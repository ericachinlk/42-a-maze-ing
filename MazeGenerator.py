import random
from collections import deque


N = 1  # North
E = 2  # East
S = 4  # South
W = 8  # West


class MazeGenerator:
    """
    A grid-based maze generated using a randomized
    Depth-First Search (DFS) algorithm with backtracking,
    which guarantees full connectivity.

    Each cell stores wall information using
    bitwise encoding (N, E, S, W), allowing efficient storage
    and fast wall checks during generation and pathfinding.
    """
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int],
            exit: tuple[int],
            seed: int
    ) -> None:
        """
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

        if not (self.is_valid(entry[0], entry[1], width, height) and
                self.is_valid(exit[0], exit[1], width, height)):
            raise SystemExit(f"Error: Entry {entry} and exit {exit} coordinates are out of bounds"
                             f" for maze of size {width}x{height}")

        if entry == exit:
            raise SystemExit("Error: Entry and exit coordinates are the same")

        if width <= 0 or height <= 0:
            raise SystemExit("Error: Width and height must be positive")
        
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid: list[list[int]] = []

        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(15)
            self.grid.append(row)

        random.seed(seed)

    def generate(self) -> None:
        """
        The function starts at one cell, randomly moves around,
        removing walls to create paths.
        """
        visited: list[list[bool]] = []

        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(False)
            visited.append(row)

        def dfs(x: int, y: int) -> None:
            """
            A recursive function that:
            - mark current cell as visited
            - shuffle directions
            -- each tuple means dx, dy, wall to remove, opposite wall
            -- example: (1, 0, E, W) means move to the right,
            remove E wall of current cell, & remove W wall of cell to the right
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
            - backtracks to dfs[0,1] -> example if function finishes too here
            - backtracks to dfs[0,0] -> dfs[1,0] -> explore possible moves
            - From (1,0): explore, go deeper if possible, otherwise return.
            Eventually everything is visited.
            So when dfs fully done, all visited[y][x] = True
            """
            visited[y][x] = True

            directions = [
                (0, -1, N, S), (1, 0, E, W), (0, 1, S, N), (-1, 0, W, E)]
            random.shuffle(directions)

            for dx, dy, wall, opposite in directions:
                nx, ny = x + dx, y + dy

                # recursion stops when there is no unvisited cell
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not visited[ny][nx]
                ):
                    self.grid[y][x] ^= wall
                    self.grid[ny][nx] ^= opposite

                    # move to next cell and repeat
                    dfs(nx, ny)

        # start running dfs from given start coordinates
        start_x, start_y = self.entry
        dfs(start_x, start_y)

    def to_hex(self) -> list[str]:
        """
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

    @staticmethod
    def is_valid(x: int, y: int, width: int, height: int) -> bool:
        return 0 <= x < width and 0 <= y < height
    
    def apply_42_pattern(self) -> None:
        """
        Draws a '42' using fully closed cells (value = 15)
        """

        # minimum size check
        if self.width < 6 or self.height < 5:
            print("Warning: Maze too small for '42' pattern")
            return

        # starting position (top-left offset)
        start_x = self.width // 4
        start_y = self.height // 3

        # --- DRAW "4" ---
        four_coords = [
            (0, 0), (0, 1), (0, 2),        # left vertical
            (1, 2),                        # middle bar
            (2, 0), (2, 1), (2, 2), (2, 3) # right vertical
        ]

        # --- DRAW "2" ---
        two_coords = [
            (4, 0), (5, 0), (6, 0),        # top
            (6, 1),
            (4, 2), (5, 2), (6, 2),        # middle
            (4, 3),
            (4, 4), (5, 4), (6, 4)         # bottom
        ]

        # helper to safely close a cell
        def close_cell(x, y):
            if (x, y) == self.entry or (x, y) == self.exit:
                return

            self.grid[y][x] = 15

            # fix neighbors
            neighbors = [
                (0, -1, N, S),
                (1, 0, E, W),
                (0, 1, S, N),
                (-1, 0, W, E)
            ]

            for dx, dy, wall, opposite in neighbors:
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] |= opposite  # ensure neighbor has matching wall

    def find_shortest_path(self) -> str:
        """
        Returns the shortest path from entry to exit
        as a string of N,E,S,W
        """

        directions = [
            (0, -1, N, "N"),
            (1, 0, E, "E"),
            (0, 1, S, "S"),
            (-1, 0, W, "W")
        ]

        queue = deque()
        queue.append((self.entry[0], self.entry[1], ""))

        visited = set()
        visited.add(self.entry)

        while queue:
            x, y, path = queue.popleft()

            if (x, y) == self.exit:
                return path

            for dx, dy, wall, letter in directions:
                nx, ny = x + dx, y + dy

                # check bounds
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue

                # check if wall is OPEN (bit = 0)
                if self.grid[y][x] & wall != 0:
                    continue

                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + letter))

        return ""  # should never happen if maze is valid
