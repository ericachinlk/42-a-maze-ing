import random
from collections import deque
from typing import Any, Protocol, Optional

"""
Maze generation engine supporting DFS and Prim algorithms.

This module provides:
- MazeGenerator: core generation logic
- Renderer protocol: optional rendering hooks

The generator is independent of UI and can be used standalone.
"""

# Bitmask directions used for wall encoding in each cell
N, E, S, W = 1, 2, 4, 8


class Renderer(Protocol):
    """
    Protocol interface for rendering hooks used during maze generation.

    This allows external modules to inject rendering logic without
    coupling MazeGenerator to any UI or CLI system.
    """
    def pre_render(
            self,
            config: dict[str, Any],
            maze: "MazeGenerator",
            mode: str,
            color: str = ""
    ) -> None:
        """
        Called during maze generation to render intermediate states.

        Args:
            config: Configuration dictionary.
            maze: Current MazeGenerator instance.
            mode: Display mode (e.g. "day", "night").
            color: Wall color escape sequence.
        """
        ...

    def display_maze(
            self,
            filename: str,
            color: str,
            mode: str,
            show_path: bool = False,
            final: bool = True
    ) -> None:
        """
        Displays the final maze output.

        Args:
            filename: Output file containing maze data.
            color: Wall color scheme.
            mode: Display mode.
            show_path: Whether to show solution path.
            final: Whether this is final render frame.
        """
        ...


class MazeError(Exception):
    """
    Base exception for all maze-related errors in the MazeGenerator module.

    This exception is used to signal invalid inputs, configuration issues,
    or illegal states encountered during maze generation.

    It provides a unified error type so that users of the library can
    consistently catch and handle all maze-specific errors.

    Example:
        try:
            MazeGenerator(width=-1, height=10, ...)
        except MazeError as e:
            print(f"Maze error: {e}")
    """
    pass


class MazeGenerator:
    """
    MazeGenerator is a reusable maze generation engine.

    It supports:
    - Depth-First Search (DFS)
    - Prim's algorithm
    - Optional loop removal (perfect / non-perfect mazes)
    - Optional embedded pattern constraints (e.g. "42" pattern)
    - Shortest path extraction (BFS solver)

    -------------------------------------------------------------------
    MAZE REPRESENTATION
    -------------------------------------------------------------------
    The maze is stored internally as:

        self.grid[y][x] -> int (bitmask of walls)

    Each cell uses 4-bit encoding:

        N = 1
        E = 2
        S = 4
        W = 8

    Example:
        15 (1111) = all walls closed
        0  (0000) = all walls open

    -------------------------------------------------------------------
    BASIC USAGE
    -------------------------------------------------------------------

    Example:

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

        print(maze.grid)                 # raw structure
        print(maze.find_shortest_path()) # solution path (N/E/S/W)

    -------------------------------------------------------------------
    NOTES FOR REUSE (IMPORTANT)
    -------------------------------------------------------------------
    This class does NOT depend on rendering or CLI.

    You can safely:
    - ignore display_maze()
    - ignore pre_render()
    - use grid directly
    - export maze via to_hex()
    - compute solution via find_shortest_path()
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
        Initialise a maze generator instance.

        Sets up the maze dimensions, generation
        parameters, and internal grid structure.
        All parameters are validated before maze creation.

        Args:
            width (int): Maze width in cells.
            height (int): Maze height in cells.
            entry (tuple[int, int]): Starting coordinate (x, y).
            exit (tuple[int, int]): Ending coordinate (x, y).
            seed (Optional[int]): Random seed for reproducibility.
            perfect (bool): If True, generates a perfect maze (no loops).
            algorithm (str): "dfs" or "prim".

        Raises:
            MazeError: If any input parameters are invalid.

        Notes:
            self.width, self.height store size of maze
            self.grid creates the maze
            The grid is a 2D list, each number = 1 cell
            [
            [15, 15, 15],
            [15, 15, 15],
            [15, 15, 15]
            ]

            Why 15? Because binary 1111 = decimal 15
            Means all 4 walls are closed, so every cell starts fully closed
            grid[y][x] = W | S | E | N
            all walls closed - 1111 ~ 15
            all walls open - 0000 ~ 0
            if only N is closed - 0001 ~ 1
            if only E is closed - 0010 ~ 2
            if only S is closed - 0100 ~ 4
            if only W is closed - 1000 ~ 8
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
        Validates initialization parameters for MazeGenerator.

        Ensures that the maze configuration is valid before generation begins.
        This prevents runtime errors caused by invalid dimensions, coordinates,
        or unsupported algorithms.

        Args:
            width: Width of the maze in cells. Must be a positive integer.
            height: Height of the maze in cells. Must be a positive integer.
            entry: Starting coordinate (x, y).
            exit: Ending coordinate (x, y).
            algorithm: Maze generation algorithm. Must be dfs" or "prim".
            seed: Must be an integer or None.

        Raises:
            MazeError: If any parameter is invalid, out of bounds,
            or unsupported.

        Returns:
            None
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
        Inserts a fixed "42" obstacle pattern into the maze.

        The pattern marks specific cells as blocked and visited to
        force maze generation to route around it.

        Args:
            visited: Grid tracking visited cells during generation.

        Returns:
            None
        """
        # check if maze is big enough
        # the '42' pattern will take 5x7 grid
        # 1 extra of space around it to allow carve paths around
        if self.width < 8 or self.height < 6:
            raise MazeError("Maze too small to apply pattern")

        # list of coordinates that form shapes of '4' and '2' (y, x)
        # this will take up max 5 rows (height) and 7 columns (width)
        p4 = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2),
              (0, 2), (1, 2), (3, 2), (4, 2)]
        p2 = [(0, 4), (0, 5), (0, 6), (1, 6), (2, 6), (2, 5),
              (2, 4), (3, 4), (4, 4), (4, 5), (4, 6)]

        # center the pattern in the maze
        # example if maze size is height 9, width 11
        # offset_y = (9 - 5) // 2 = 2
        # (42 will take up 5 rows, leaving 4 rows blank,
        # divide by 2 to be center pos)
        # offset_x = (11 - 7) // 2 = 2
        # so the shape 42 will start at offset_y, offset_x (row 2, col 2)
        # // divide gives integer, / divide gives float
        offset_y = (self.height - 5) // 2
        offset_x = (self.width - 7) // 2

        pattern_cells = set()
        for dy, dx in p4 + p2:
            # go into the actual coord of shape 42
            py, px = offset_y + dy, offset_x + dx
            pattern_cells.add((px, py))

        if self.entry in pattern_cells or self.exit in pattern_cells:
            raise MazeError("Entry/exit overlap pattern region")

        for dy, dx in p4 + p2:
            py, px = offset_y + dy, offset_x + dx
            # make all the cells in 42 to have all walls blocked
            self.grid[py][px] = 15
            # mark these cells as visited for DFS to go around later
            visited[py][px] = True
            # explicitly track these cells with pattern_cells
            self.pattern_cells.add((px, py))

    def generate(
            self,
            config: dict[str, Any] | None = None,
            color: str = "",
            mode: str = "day",
            use_pattern: bool = False,
            renderer: Renderer | None = None
    ) -> None:
        """
        Generates the maze using the selected algorithm.

        Supports DFS or Prim's algorithm and optionally applies
        pattern constraints and loop removal.

        Args:
            config: Configuration dictionary or None
            color: Rendering color code.
            mode: Display mode (e.g. "day" or "night").
            use_pattern: If True, applies embedded pattern constraints.

        Returns:
            None
        """
        if config is None:
            config = {}

        visited: list[list[bool]] = []

        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(False)
            visited.append(row)

        warning_msg = None
        try:
            # Apply pattern and mark as visited so DFS goes AROUND them
            if use_pattern:
                self.apply_42_pattern(visited)
        except MazeError as e:
            warning_msg = str(e)

        if self.algorithm == "dfs":
            self._generate_dfs(visited, config, color, mode, renderer)
        elif self.algorithm == "prim":
            self._generate_prim(visited, config, color, mode, renderer)

        # handle PERFECT=False (multiple paths instead of just one)
        if not self.perfect:
            self._add_loops(config, color, mode, renderer)

        # print final frame
        if renderer:
            output = config.get("OUTPUT_FILE", "maze.txt")
            renderer.display_maze(output, color, mode)

        # print warning if 42 pattern not applied
        if warning_msg:
            print(f"\n[WARNING] '42' pattern skipped: {warning_msg}")

    def _generate_dfs(
            self, visited: list[list[bool]],
            config: dict[str, Any], color: str, mode: str,
            renderer: Renderer | None = None) -> None:
        """
        Generates maze using Depth-First Search algorithm.

        This method delegates to a recursive DFS function that carves
        paths by backtracking through unvisited cells.

        Args:
            visited: Grid tracking visited cells.
            config: Configuration dictionary.
            color: Rendering color code.
            mode: Display mode.
            renderer: Optional renderer for visualization.
        """
        def dfs(x: int, y: int) -> None:
            """
            Generates maze using randomized Depth-First Search.

            This is a recursive backtracking algorithm that carves
            passages by visiting unvisited neighbors.

            Args:
                visited: Grid tracking visited cells.
                config: Configuration dictionary.
                color: Rendering color.
                mode: Display mode.

            Returns:
                None

            Notes:
                A recursive function that:
                - mark current cell as visited
                - shuffle directions
                -- each tuple means dx, dy, wall to remove, opposite wall
                -- example: (1, 0, E, W) means move to the right,
                remove E wall of current cell,
                & remove W wall of cell to the right
                - try moving nx, ny = x + dx, y + dy
                - check if inside grid and not visited
                - if yes then break walls

                A XOR B = elements in A or B but not both
                XOR works internally on each bit position:
                - if bits are different, write 1
                - if bits are same, write 0
                Example:
                cell = cell ^ E   # remove wall
                cell = cell ^ E   # add it back

                Recursive remark:
                every function call is stored on a call stack,
                and when a function finishes, the program resumes
                from the previous stack frame.

                A simple visualization:
                - dfs[0,0] -> dfs[0,1] -> dfs[1,1]
                -> function finishes becoz no place to go from 1,1
                - backtracks to dfs[0,1] -> e.g. if function finishes too here
                - backtracks to dfs[0,0] -> dfs[1,0] -> explore possible moves
                - From (1,0): explore, go deeper if possible, otherwise return.
                Eventually everything is visited.
                So when dfs fully done, all visited[y][x] = True
            """
            visited[y][x] = True

            directions = [
                (0, -1, N, S), (1, 0, E, W), (0, 1, S, N), (-1, 0, W, E)]
            self.rng.shuffle(directions)

            for dx, dy, wall, opposite in directions:
                nx, ny = x + dx, y + dy

                if (nx, ny) in self.pattern_cells:
                    continue
                # recursion stops when there is no unvisited cell
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not visited[ny][nx]
                ):
                    self.grid[y][x] ^= wall
                    self.grid[ny][nx] ^= opposite

                    if renderer:
                        renderer.pre_render(config, self, mode, color)

                    # move to next cell and repeat
                    dfs(nx, ny)

        # start running dfs
        start_x = self.rng.randint(0, self.width - 1)
        start_y = self.rng.randint(0, self.height - 1)
        dfs(start_x, start_y)

    def _generate_prim(
            self, visited: list[list[bool]],
            config: dict[str, Any], color: str, mode: str,
            renderer: Renderer | None = None) -> None:
        """
        Generates maze using Prim's algorithm.

        Expands a growing region by randomly selecting frontier walls.

        Args:
            visited: Grid tracking visited cells.
            config: Configuration dictionary.
            color: Rendering color.
            mode: Display mode.

        Returns:
            None
        """
        start_x = self.rng.randint(0, self.width - 1)
        start_y = self.rng.randint(0, self.height - 1)
        visited[start_y][start_x] = True
        walls: list[tuple[int, int, int, int, int, int]] = []

        def add_walls(x: int, y: int) -> None:
            """
            Adds frontier walls of the current cell to the candidate list.

            This supports Prim's algorithm by expanding the maze frontier.
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
                    renderer.pre_render(config, self, mode, color)

                visited[ny][nx] = True
                add_walls(nx, ny)

    def _add_loops(
            self,
            config: dict[str, Any],
            color: str,
            mode: str,
            renderer: Renderer | None = None
    ) -> None:
        """
        Adds random loops to create a non-perfect maze.

        Removes walls while preventing invalid open regions.

        Args:
            config: Configuration dictionary.
            color: Rendering color.
            mode: Display mode.
            renderer: Optional renderer for visualization updates.

        Returns:
            None
        """
        # remove walls of 50% of the maze cells
        extra_removals = (self.width * self.height) // 2
        attempts = 0
        removed = 0

        # repeat until enough walls removed or too many failed attempts
        while removed < extra_removals and attempts < 1000:
            attempts += 1
            # pick a random cell not on the edges
            x = self.rng.randint(1, self.width - 2)
            y = self.rng.randint(1, self.height - 2)

            # skip cells if they are the '42' pattern cells
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
                if not self._creates_3x3_open_area(x, y):
                    self.grid[y][x] ^= wall
                    self.grid[y + dy][x + dx] ^= opp
                    removed += 1

                    if renderer:
                        renderer.pre_render(config, self, mode, color)

    def _creates_3x3_open_area(self, x: int, y: int) -> bool:
        """
        Checks whether removing a wall creates a fully open 3x3 area.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            True if a 3x3 open region would be formed, otherwise False.

        Notes:
            Only checks interior-safe 3x3 blocks; edges are skipped.
        """
        # check top-left corner of possible 3x3 blocks around (x, y)
        # -2 means look 2 cells up, -1 means look 1 cell up,
        # 0 means look at current cell
        # there could be 9 combinations for coord of top left
        # of a possible 3x3 block
        for dy in (-2, -1, 0):
            for dx in (-2, -1, 0):
                # top-left of a 3x3 block
                sx, sy = x + dx, y + dy
                # must stay inside grid
                if sx < 0 or sy < 0:
                    continue
                # x, y + 2 = last cell of the 3x3 block
                if sx + 2 >= self.width or sy + 2 >= self.height:
                    continue

                open_count = 0
                # loop through the 3x3 grid
                for yy in range(sy, sy + 3):
                    for xx in range(sx, sx + 3):
                        # a cell is not fully enclosed if not 15
                        if self.grid[yy][xx] != 15:
                            open_count += 1
                # if all 9 cells has open walls, it's a 3x3 open square
                if open_count == 9:
                    return True
        # no 3x3 open area found
        return False

    def to_hex(self) -> list[str]:
        """
        Converts the maze grid into hexadecimal string format.

        Returns:
            List of strings representing each row in hex.

        Notes:
            This function:
            - Takes each row of the maze, e.g. [15, 10, 3]
            - Converts numbers into hex digits e.g. ["F", "A", 3]
            - Joins them into a string -> "FA3"
            - Returns list of strings -> ["FA3", ...]
        """
        lines: list[str] = []
        for row in self.grid:
            line = ""
            for cell in row:
                hex_value = format(cell, "X")
                line += hex_value
            lines.append(line)
        return lines

    def find_shortest_path(self) -> str:
        """
        Finds the shortest path from entry to exit using BFS.

        Args:
            None

        Returns:
            A string representing directions (N, E, S, W).
            Returns empty string if no path exists.

        Notes:
        Returns the shortest path from entry to exit
        as a string of N,E,S,W

        Using BFS(Breadth-First Search)
        - means check all 1-step moves first
        - then all 2-step moves etc
        - uses deque (double-ended queue to add/remove items from front/back)
        - uses popleft() to remove the leftmost(oldest) item
        - the above ensure FIFO (first in first out),
        so oldest node gets explored first, while newer nodes wait in line

        Simple example to illustrate:
        - from entry position, if all 4 directions are possible,
        queue will contain:
        (x1, y1, "N")
        (x2, y2, "E")
        (x3, y3, "S")
        (x4, y4, "W")
        - pop the oldest one, means removing (x1, y1, "N") from queue,
        example it's dead end, then queue becomes:
        (x2, y2, "E")
        (x3, y3, "S")
        (x4, y4, "W")
        - pop the oldest one now (x2, y2, "E") from queue and explore,
        example we can go to W and S from here, then the queue becomes:
        (x3, y3, "S")
        (x4, y4, "W")
        (x5, y5, "EW")
        (x6, y6, "ES")
        - Say x5, y5 is the exit, then we stop at (x5, y5, "EW")
        and return the path, which is EW
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
            # this is where BFS is implemented
            x, y, path = queue.popleft()

            # if current position is the exit, return path immediately
            if (x, y) == self.exit:
                return path

            # loop through N, E, S, W and move in that direction
            # 'continue' means skip and go to the next iteration
            for dx, dy, wall, letter in directions:
                nx, ny = x + dx, y + dy

                # check bounds, skip if outside grid / invalid position
                # nx >= 0 means not left of the maze
                # nx < self.width means not past the right edge
                # ny >= 0 means not above the maze
                # ny < self.height means not below the maze
                if not (0 <= nx < self.width and 0 <= ny < self.height):
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
