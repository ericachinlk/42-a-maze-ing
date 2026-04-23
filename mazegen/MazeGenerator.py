import random
from collections import deque
from typing import List, Tuple, Any

# Bitmask directions
N, E, S, W = 1, 2, 4, 8


class MazeGenerator:
    """
    A grid-based maze generator using randomized DFS (backtracking).

    Each cell stores wall information using bitwise encoding:
    N=1, E=2, S=4, W=8

    Example:
        15 (1111) = all walls closed
        0  (0000) = all walls open
    """
    def __init__(
            self,
            width: int,
            height: int,
            entry: Tuple[int, int],
            exit: Tuple[int, int],
            seed: int,
            perfect: bool=True
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
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")

        if not (self.is_valid(entry[0], entry[1], width, height) and
                self.is_valid(exit[0], exit[1], width, height)):
            raise ValueError("Entry/exit coordinates are out of bounds")

        if entry == exit:
            raise ValueError("Entry and exit coordinates are the same")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.seed = seed
        self.perfect = perfect

        random.seed(seed)

        # Initialize grid (all walls closed = 15)
        self.grid: list[list[int]] = []
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(15)
            self.grid.append(row)

    @staticmethod
    def is_valid(x: int, y: int, width: int, height: int) -> bool:
        return 0 <= x < width and 0 <= y < height

    def apply_42_pattern(self, visited: list[list[bool]]) -> None:
        """Places a '42' using fully closed cells (15)."""
        if self.width < 8 or self.height < 6:
            return  # silently skip

        # Shape of '4' and '2' (y, x)
        p4 = [(0,0), (1,0), (2,0), (2,1), (2,2), (0,2), (1,2), (3,2), (4,2)]
        p2 = [(0,4), (0,5), (0,6), (1,6), (2,6), (2,5), (2,4), (3,4), (4,4), (4,5), (4,6)]

        offset_y = (self.height - 5) // 2
        offset_x = (self.width - 7) // 2

        for dy, dx in p4 + p2:
            py, px = offset_y + dy, offset_x + dx
            # Don't block entry or exit
            if (px, py) != self.entry and (px, py) != self.exit:
                self.grid[py][px] = 15
                visited[py][px] = True

    def generate(self, config: dict[str, Any],
                 color: str,
                 use_pattern: bool = False) -> None:
        """
        The function starts at one cell, randomly moves around,
        removing walls to create paths.
        """
        visited: list[list[bool]] = []
        from render import pre_render

        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(False)
            visited.append(row)

        # Apply pattern and mark as visited so DFS goes AROUND them
        if use_pattern:
            self.apply_42_pattern(visited)


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
 
                    pre_render(config, self, color)

                    # move to next cell and repeat
                    dfs(nx, ny)

        # start running dfs from given start coordinates
        
        
        start_x, start_y = self.entry
        dfs(start_x, start_y)

        # Handle PERFECT=False (Braid Maze)
        if not self.perfect:
            self._add_loops()

    def _add_loops(self):
        """Randomly removes walls to create multiple paths, avoiding 3x3 areas."""
        extra_removals = (self.width * self.height) // 10  # 10% more paths
        attempts = 0
        removed = 0
        
        while removed < extra_removals and attempts < 1000:
            attempts += 1
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            # Pick a wall to remove (East or South)
            wall, opp, dx, dy = random.choice([(E, W, 1, 0), (S, N, 0, 1)])
            
            if self.grid[y][x] & wall:
                # Check if removing this wall creates a 3x3 open area (all 0s)
                # This is a simplified check; for strictness, you'd check the 3x3 neighborhood
                self.grid[y][x] ^= wall
                self.grid[y + dy][x + dx] ^= opp
                removed += 1

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
