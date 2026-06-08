"""
Maze generation engine supporting DFS and Prim algorithms.

This module provides:
    MazeGenerator: Core maze generation and solving logic.
    MazeError: Custom exception for maze-related failures.

The generator is independent of any UI or rendering layer and can be
used as a standalone library.
"""

import random
from collections import deque
from typing import Optional, Any
from mazegen.renderer import CLIRenderer

# Bitmask directions used for wall encoding in each cell
N, E, S, W = 1, 2, 4, 8


class MazeError(Exception):
    """
    Base exception for maze-related errors.

    Raised when invalid inputs, configuration issues,
    or illegal states occur during maze generation or processing.
    """
    pass


class MazeGenerator:
    """
    Reusable maze generation engine supporting multiple
    algorithms and features.

    This class generates and solves mazes using different algorithms and
    provides access to both the raw maze structure and the computed
    solution path.

    Supported features:
        DFS (Depth-First Search) maze generation
        Prim's algorithm maze generation
        Perfect and non-perfect maze generation
        Optional fixed pattern embedding ("42" pattern constraint)
        Shortest path extraction using BFS

    Maze representation:
        The maze is stored as a 2D grid of integers:

            self.grid[y][x]

        Each cell uses a 4-bit wall encoding:
            N = 1, E = 2, S = 4, W = 8

        Example values:
            15 -> all walls present (1111)
             0 -> no walls present (0000)

    Basic usage example:

        from mazegen import MazeGenerator

        maze = MazeGenerator(
            width=20,
            height=10,
            entry=(0, 0),
            exit=(19, 9),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )

        maze.generate()

        print(maze.grid)
        print(maze.find_shortest_path())
    """
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exit: tuple[int, int],
            seed: Optional[int] = None,
            perfect: bool = True,
            algorithm: str = "dfs"
    ) -> None:
        """
        Initializes a MazeGenerator instance.

        Args:
            width (int): Width of the maze in cells.
            height (int): Height of the maze in cells.
            entry (tuple[int, int]): Entry coordinate (x, y).
            exit (tuple[int, int]): Exit coordinate (x, y).
            seed (Optional[int]): Random seed for reproducibility.
                If None, a random seed is generated.
            perfect (bool): If True, generates a perfect maze (no loops).
            algorithm (str): Generation algorithm ("dfs" or "prim").

        Raises:
            MazeError: If any parameter is invalid.
        """
        self._validate(width, height, entry, exit, algorithm, seed)

        if seed is None:
            seed = random.randint(1, 1000)

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed
        self.perfect = perfect
        self.algorithm = algorithm
        self.pattern_cells: set[tuple[int, int]] = set()

        self.rng = random.Random(self.seed)

        # Initialize grid (all walls closed = 15)
        self.grid: list[list[int]] = []
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(15)
            self.grid.append(row)

    def _validate(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        algorithm: str,
        seed: int | None
    ) -> None:
        """
        Validates initialization parameters.

        Args:
            width (int): Maze width.
            height (int): Maze height.
            entry (tuple[int, int]): Entry coordinate.
            exit (tuple[int, int]): Exit coordinate.
            algorithm (str): Algorithm name.
            seed (int | None): Random seed.

        Raises:
            MazeError: If any parameter is invalid.
        """
        if not isinstance(width, int) or width <= 0:
            raise MazeError("Width must be positive integer")

        if not isinstance(height, int) or height <= 0:
            raise MazeError("Height must be positive integer")

        if algorithm not in ("dfs", "prim"):
            raise MazeError("Algorithm must be 'dfs' or 'prim'")

        if (
            not isinstance(entry, tuple)
            or not isinstance(exit, tuple)
            or len(entry) != 2
            or len(exit) != 2
        ):
            raise MazeError("Entry and exit must be (x, y) tuples")

        # Allow entry == exit for trivial maze (e.g. 1x1)
        if entry == exit and not (width == 1 and height == 1):
            raise MazeError("Entry and exit cannot be the same "
                            "for non-trivial maze")

        if width > 1000 or height > 1000:
            raise MazeError("Maze dimensions too large")

        ex, ey = entry
        xx, xy = exit

        if not all(isinstance(v, int) for v in (ex, ey, xx, xy)):
            raise MazeError("Entry and exit coordinates must be integers")
        if not (0 <= ex < width and 0 <= ey < height):
            raise MazeError("Entry out of bounds")
        if not (0 <= xx < width and 0 <= xy < height):
            raise MazeError("Exit out of bounds")

        if seed is not None and not isinstance(seed, int):
            raise MazeError("Seed must be an integer or None")

    def apply_42_pattern(self, visited: list[list[bool]]) -> None:
        """
        Applies a fixed "42" obstacle pattern to the maze.

        The pattern blocks specific cells and are marked as visited
        as well as stored in maze's attribute pattern_cells,
        ensuring the generator route paths around the pattern blocks.

        Args:
            visited (list[list[bool]]): Visited grid used
                during generation.

        Raises:
            MazeError: If the maze is too small or
                entry/exit overlaps the pattern.
        """
        # check if maze is big enough to display '42' pattern
        if self.width < 8 or self.height < 6:
            raise MazeError("Maze too small to apply pattern")

        # list of coordinates that form shapes of '4' and '2' (y, x)
        # this will take up max 5 rows (height) and 7 columns (width)
        p4 = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2),
              (0, 2), (1, 2), (3, 2), (4, 2)]
        p2 = [(0, 4), (0, 5), (0, 6), (1, 6), (2, 6), (2, 5),
              (2, 4), (3, 4), (4, 4), (4, 5), (4, 6)]

        # center the pattern in the maze
        # // divide gives integer, / divide gives float
        offset_y = (self.height - 5) // 2
        offset_x = (self.width - 7) // 2

        pattern_cells = set()
        for dy, dx in p4 + p2:
            py, px = offset_y + dy, offset_x + dx
            pattern_cells.add((px, py))

        if self.entry in pattern_cells or self.exit in pattern_cells:
            raise MazeError("Entry/exit overlap pattern region")

        for dy, dx in p4 + p2:
            py, px = offset_y + dy, offset_x + dx
            self.grid[py][px] = 15
            visited[py][px] = True
            self.pattern_cells.add((px, py))

    def generate(
            self,
            renderer: CLIRenderer | None = None,
            use_pattern: bool = True,
            color: str | None = None,
            mode: str | None = None
    ) -> None:
        """
        Generates the maze using the selected algorithm.

        Optionally applies the "42" pattern and loop creation.

        Args:
            renderer (CLIRenderer | None): Optional renderer for visualization.
            use_pattern (bool): Whether to apply the "42" pattern.
        """
        visited: list[list[bool]] = []

        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(False)
            visited.append(row)

        warning_message: str | None = None
        try:
            if use_pattern:
                self.apply_42_pattern(visited)
        except MazeError as e:
            warning_message = f"\n[WARNING] '42' pattern skipped: {str(e)}"

        if self.algorithm == "dfs":
            self._generate_dfs(visited, renderer=renderer, color=color)
        elif self.algorithm == "prim":
            self._generate_prim(visited, renderer=renderer, color=color)

        # handle PERFECT=False (multiple paths instead of just one)
        if not self.perfect:
            self._add_loops(renderer=renderer)

        # print final frame
        if renderer:
            renderer.path = self.find_shortest_path()
            renderer.pattern_error = warning_message
            renderer.display_maze(color=color, mode=mode)
        else:
            if warning_message:
                print(warning_message)

    def _generate_dfs(
            self,
            visited: list[list[bool]],
            renderer: CLIRenderer | None = None,
            color: str | None = None
    ) -> None:
        """
        Generates the maze using Depth-First Search (DFS).

        Args:
            visited (list[list[bool]]): Visited grid.
            renderer (CLIRenderer | None): Optional renderer.
        """
        def dfs(x: int, y: int) -> None:
            """
            Recursive DFS backtracking function.

            Visits cells, removes walls, and explores neighbors randomly.

            Args:
                x (int): Current x-coordinate.
                y (int): Current y-coordinate.
            """
            visited[y][x] = True

            directions = [
                (0, -1, N, S), (1, 0, E, W), (0, 1, S, N), (-1, 0, W, E)]
            self.rng.shuffle(directions)

            for dx, dy, wall, opposite in directions:
                nx, ny = x + dx, y + dy

                if (nx, ny) in self.pattern_cells:
                    continue

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not visited[ny][nx]
                ):
                    self.grid[y][x] ^= wall
                    self.grid[ny][nx] ^= opposite

                    if renderer:
                        renderer.pre_render(color=color)

                    dfs(nx, ny)

        start_x = self.rng.randint(0, self.width - 1)
        start_y = self.rng.randint(0, self.height - 1)
        dfs(start_x, start_y)

    def _generate_prim(
            self,
            visited: list[list[bool]],
            renderer: CLIRenderer | None = None,
            color: str | None = None
    ) -> None:
        """
        Generates the maze using Prim's algorithm.

        Args:
            visited (list[list[bool]]): Visited grid.
            renderer (CLIRenderer | None): Optional renderer.
        """
        start_x = self.rng.randint(0, self.width - 1)
        start_y = self.rng.randint(0, self.height - 1)
        visited[start_y][start_x] = True
        walls: list[tuple[int, int, int, int, int, int]] = []

        def add_walls(x: int, y: int) -> None:
            """
            Adds frontier walls of the current cell to the candidate list.

            This supports Prim's algorithm by expanding the maze frontier.

            Args:
                x (int): Current x-coordinate.
                y (int): Current y-coordinate.
            """
            directions = [
                (0, -1, N, S), (1, 0, E, W), (0, 1, S, N), (-1, 0, W, E)]

            for dx, dy, wall, opposite in directions:
                nx, ny = x + dx, y + dy

                if (nx, ny) in self.pattern_cells:
                    continue

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not visited[ny][nx]
                ):
                    walls.append((x, y, nx, ny, wall, opposite))

        add_walls(start_x, start_y)

        while walls:
            idx = self.rng.randint(0, len(walls) - 1)
            x, y, nx, ny, wall, opposite = walls.pop(idx)

            if not visited[ny][nx]:
                self.grid[y][x] ^= wall
                self.grid[ny][nx] ^= opposite

                if renderer:
                    renderer.pre_render(color=color)

                visited[ny][nx] = True
                add_walls(nx, ny)

    def _add_loops(self, renderer: CLIRenderer | None = None) -> None:
        """
        Adds random loops to create a non-perfect maze.

        Args:
            renderer (CLIRenderer | None): Optional renderer.
        """
        # remove walls of up to 5% of the maze cells
        extra_removals = (self.width * self.height) // 20
        attempts = 0
        removed = 0

        # repeat until enough walls removed or too many failed attempts
        while removed < extra_removals and attempts < 1000:
            attempts += 1
            # pick a random cell not on the edges
            x = self.rng.randint(1, self.width - 2)
            y = self.rng.randint(1, self.height - 2)

            if (x, y) in self.pattern_cells:
                continue

            # Pick a wall to remove (East or South)
            # e.g. (E, W, 1, 0) means removing E wall, W wall of opposite cell
            # and move to the right
            wall, opp, dx, dy = self.rng.choice([(E, W, 1, 0), (S, N, 0, 1)])

            # skip cells if the neighbouring cells are the '42' pattern cells
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.pattern_cells:
                continue

            # check if the wall exist in the cell, if yes, remove walls
            if self.grid[y][x] & wall:
                # check if will create 3x3 open area before removing wall
                if not self._creates_3x3_open_area(x, y, wall, dx, dy):
                    self.grid[y][x] ^= wall
                    self.grid[y + dy][x + dx] ^= opp
                    removed += 1

                    if renderer:
                        renderer.pre_render()

    def _creates_3x3_open_area(
            self,
            x: int,
            y: int,
            wall: int,
            dx: int,
            dy: int
    ) -> bool:
        """
        Checks whether removing a specific wall would create
        a fully open 3x3 area.

        This method simulates the wall removal, checks for resulting
        3x3 fully-open regions, then reverts the change. This ensures
        accuracy by evaluating the maze state AFTER the wall removal.

        Args:
            x (int): X-coordinate of the cell losing a wall.
            y (int): Y-coordinate of the cell losing a wall.
            wall (int): Wall direction being removed (N, E, S, or W).
            dx (int): X direction of neighbor cell
                (1 for E, -1 for W, 0 for vertical).
            dy (int): Y direction of neighbor cell
                (1 for S, -1 for N, 0 for horizontal).

        Returns:
            bool: True if removing the wall would create a 3x3 fully open area,
                False otherwise.
        """
        # Get the neighbor cell coordinates
        nx, ny = x + dx, y + dy

        # Determine opposite wall using a mapping
        opposite_wall = {N: S, S: N, E: W, W: E}[wall]

        # Simulate the wall removal (XOR toggles the wall bit)
        self.grid[y][x] ^= wall
        self.grid[ny][nx] ^= opposite_wall

        # Check all possible 3x3 blocks that could be affected
        # The affected region spans around both modified cells
        min_y = min(y, ny)
        max_y = max(y, ny)
        min_x = min(x, nx)
        max_x = max(x, nx)

        # Check 3x3 blocks that include the modified cells
        # A 3x3 block starting at (sx,sy) includes (x,y) if:
        # sx <= x <= sx+2 and sy <= y <= sy+2
        # Which means: x-2 <= sx <= x and y-2 <= sy <= y
        # For both cells: min(x,nx)-2 <= sx <= max(x,nx)
        # and min(y,ny)-2 <= sy <= max(y,ny)
        for check_y in range(
            max(0, min_y - 2), min(self.height - 2, max_y + 1)
        ):
            for check_x in range(
                max(0, min_x - 2), min(self.width - 2, max_x + 1)
            ):
                open_count = 0
                # Count cells in this 3x3 block that are
                # COMPLETELY open (all walls removed)
                for yy in range(check_y, check_y + 3):
                    for xx in range(check_x, check_x + 3):
                        # A cell is "completely open" only
                        # if it has NO walls (value == 0)
                        if self.grid[yy][xx] == 0:
                            open_count += 1

                # If all 9 cells in the 3x3 block are completely open,
                # revert and return True
                if open_count == 9:
                    self.grid[y][x] ^= wall
                    self.grid[ny][nx] ^= opposite_wall
                    return True

        # No 3x3 fully open area would be created; revert simulation
        self.grid[y][x] ^= wall
        self.grid[ny][nx] ^= opposite_wall
        return False

    def to_hex(self) -> list[str]:
        """
        Converts the maze grid into hexadecimal string representation.

        Returns:
            list[str]: List of strings, one per row of the maze.
        """
        lines: list[str] = []
        for row in self.grid:
            line = ""
            for cell in row:
                # hex() converts an integer into a hex string.
                # [2:] removes the prefix '0x'
                hex_value = hex(cell)[2:].upper()
                line += hex_value
            lines.append(line)
        return lines

    def find_shortest_path(self) -> str:
        """
        Finds the shortest path from entry to exit using BFS.

        Returns:
            str: Path as a sequence of directions ("N", "E", "S", "W").
                Returns an empty string if no path exists.
        """
        # each tuple means (dx, dy, wall to check, letter to add to path)
        # e.g. (1, 0, E, "E") means move right, check East wall, record "E"
        directions = [
            (0, -1, N, "N"),
            (1, 0, E, "E"),
            (0, 1, S, "S"),
            (-1, 0, W, "W")
        ]

        queue: deque[tuple[int, int, str]] = deque()
        # store entry x, y position, path so far (empty at start)
        queue.append((self.entry[0], self.entry[1], ""))

        # start position marked as visited
        visited = set()
        visited.add(self.entry)

        # keep running as long as there are positions to explore
        while queue:
            # takes the oldest item from the queue
            x, y, path = queue.popleft()

            # if current position is the exit, return path immediately
            if (x, y) == self.exit:
                return path

            # loop through N, E, S, W and move in that direction
            for dx, dy, wall, letter in directions:
                nx, ny = x + dx, y + dy

                # check bounds, skip if outside grid / invalid position
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue

                if (nx, ny) in self.pattern_cells:
                    continue

                # check if wall is OPEN
                # & bit by bit comparison at the same position
                # e.g cell is 1111(all walls), wall is 0100 (check S wall)
                # the comparison will be 0100 (if same, result is 1, else 0)
                # 0100 is not 0, so means there is a wall, do not proceed
                if self.grid[y][x] & wall != 0:
                    continue

                # if not visited, mark as visited, add position to queue
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + letter))

        return ""

    def write_output(self, filename: str) -> None:
        """
        Writes the maze and metadata to a file.

        Output format:
            - Hex grid
            - Entry coordinates
            - Exit coordinates
            - Shortest path

        Args:
            filename (str): Output file path.

        Raises:
            MazeError: If the file cannot be written.
        """
        path = self.find_shortest_path()
        try:
            with open(filename, "w") as f:
                for line in self.to_hex():
                    f.write(line + "\n")

                f.write("\n")
                f.write(f"{self.entry[0]},{self.entry[1]}\n")
                f.write(f"{self.exit[0]},{self.exit[1]}\n")
                f.write(f"{path}\n")
        except OSError as e:
            raise MazeError(f"Failed to write output file: {e}")

    def get_maze_info(self) -> dict[str, Any]:
        """
        Returns basic maze metadata.

        Returns:
            dict[str, Any]: Dictionary containing grid, entry, exit,
                width, and height.
        """
        return {
            "grid": self.grid,
            "entry": self.entry,
            "exit": self.exit,
            "width": self.width,
            "height": self.height
        }
