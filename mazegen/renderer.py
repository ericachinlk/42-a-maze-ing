import time
from typing import Any


# Box Drawing Characters
V_WALL = "┃"
H_WALL = "━━━"
RESET = "\033[0m"  # Resets all ANSI formatting

wall_colors_rotation = [
    "\033[38;5;240m",  # Dark gray
    "\033[38;5;67m",   # Medium blue
    "\033[38;5;108m",  # Soft green
    "\033[38;5;137m",  # Brown
    "\033[38;5;131m"   # Muted red
]

north, east, south, west = 1, 2, 4, 8

THEMES = {
    "day": {
        "start": "\033[38;5;78m",    # Bright green
        "goal": "\033[38;5;203m",    # Pink
        "path": "\033[38;5;222m",    # Light beige
        "pattern": "\033[48;5;230m"  # Light cream
    },
    "night": {
        "start": "\033[38;5;117m",   # Light sky blue
        "goal": "\033[38;5;215m",    # Soft orange
        "path": "\033[38;5;246m",    # Medium gray
        "pattern": "\033[48;5;236m"  # Dark gray-blue
    }
}


class RenderError(Exception):
    """
    Exception raised when maze rendering fails.

    Used when:
    - file is missing
    - maze format is invalid
    - parsing of maze data fails
    """
    pass


class CLIRenderer:
    """
    Renderer implementation for CLI application.

    This class acts as a bridge between the reusable `MazeGenerator`
    module and the application-specific rendering logic.

    It delegates rendering responsibilities to functions defined
    in the app layer, keeping the core maze generator independent
    from any UI or display concerns.

    Methods:
        pre_render: Renders intermediate frames during maze generation.
        display_maze: Renders the final maze output.
    """
    def __init__(self, maze_info: dict[str, Any]) -> None:
        if not isinstance(maze_info, dict):
            raise RenderError("maze_info must be a dict")
        try:
            self.grid = maze_info["grid"]
            self.entry = maze_info["entry"]
            self.exit = maze_info["exit"]
            self.width = maze_info["width"]
            self.height = maze_info["height"]
        except KeyError as e:
            raise RenderError("Unable to retrieve maze_info. "
                              f"Missing key: {e}")

        self.mode = "day"
        self.wall_color = "\033[38;5;240m"
        self.color_index = 0
        self.path: str = ""

    def toggle_mode(self) -> None:
        self.mode = "night" if self.mode == "day" else "day"

    def rotate_wall_color(self) -> None:
        self.color_index = (self.color_index + 1) % len(wall_colors_rotation)
        self.wall_color = wall_colors_rotation[self.color_index]

    def render_maze(self, show_path: bool, final: bool) -> str:
        """
        Render a maze from a saved output file into a string representation.

        This function:
        - Reads maze file
        - Parses grid, entry/exit, and path
        - Converts bitmask grid into ASCII/Unicode maze
        - Optionally overlays shortest path and UI decorations

        Args:
            filepath (str): Path to maze output file.
            color (str): Wall color escape code.
            show_path (bool): Whether to display shortest path.
            final: Whether this is final render (shows start/goal/pattern).
            mode (str): Display theme mode ("day" or "night").

        Returns:
            str: Fully rendered maze as a string.

        Raises:
            RenderError: If file is missing or maze format is invalid.
        """

        grid = self.grid
        entry = self.entry
        exit = self.exit
        width = self.width
        height = self.height
        path_line = self.path

        if not grid:
            raise RenderError("Maze is invalid.")

        path_cells = set()
        path_cells = self._build_path_cells(entry, path_line)

        theme = THEMES.get(self.mode, THEMES["day"])
        wall_color = self.wall_color

        output = []
        for y in range(height + 1):
            line = ""
            for x in range(width + 1):
                corners = self._get_corner(grid, x, y, width, height)
                line += f"{wall_color}{corners}{RESET}"

                if x < width:
                    if y == 0:
                        has_h = grid[0][x] & north
                    elif y == height:
                        has_h = grid[height - 1][x] & south
                    else:
                        has_h = ((grid[y - 1][x] & south)
                                 or (grid[y][x] & north))

                    line += f"{wall_color}{H_WALL}{RESET}" if has_h else "   "
            output.append(line)

            if y < height:
                line = ""
                for x in range(width + 1):
                    if x == 0:
                        has_v = grid[y][0] & west
                    elif x == width:
                        has_v = grid[y][width - 1] & east
                    else:
                        has_v = (grid[y][x - 1] & east) or (grid[y][x] & west)

                    line += f"{wall_color}{V_WALL}{RESET}" if has_v else " "

                    if x < width:
                        if (x, y) == entry and final:
                            line += f" \033[1m{theme['start']}S{RESET} "
                        elif (x, y) == exit and final:
                            line += f" \033[1m{theme['goal']}G{RESET} "
                        elif (x, y) in path_cells:
                            if show_path:
                                line += f" {theme['path']}·{RESET} "
                            else:
                                line += f"  {RESET} "
                        elif grid[y][x] == 15 and final:
                            line += f"{theme['pattern']}   {RESET}"
                        else:
                            line += "   "
                output.append(line)

        return ("\n".join(output))

    def pre_render(self) -> None:
        """
        Render an intermediate frame of the maze during generation.

        This method is typically called repeatedly by the maze generator
        to visualize the step-by-step carving process.

        Args:
            config (dict[str, Any]): Configuration dictionary containing
                runtime settings (e.g. output file, dimensions).
            maze (MazeGenerator): The current maze generator instance,
                providing access to the grid state.
            mode (str): Display mode (e.g. "day" or "night").
            color (str, optional): ANSI color code for rendering walls.
                Defaults to "".

        Returns:
            None
        """
        self.display_maze(show_path=False, final=False)
        time.sleep(0.03)

    def display_maze(
            self,
            show_path: bool = True,
            final: bool = True
    ) -> None:
        """
        Render the maze to the terminal or output display.

        This method is used to display the final maze, and optionally
        the solution path.

        Args:
            filename (str): Path to the maze output file.
            color (str): ANSI color code for rendering walls.
            mode (str): Display mode (e.g. "day" or "night").
            show_path (bool, optional): Whether to overlay the shortest
                path on the maze. Defaults to False.
            final (bool, optional): Indicates whether this is the final
                render (affects formatting or animation behavior).
                Defaults to True.

        Returns:
            None
        """
        print("\033[H\033[J", end="")
        print(self.render_maze(show_path=show_path, final=final))

    def _get_corner(
            self,
            grid: list[list[int]],
            x: int,
            y: int,
            width: int,
            height: int
    ) -> str:
        """
        Compute the correct Unicode box-drawing character for a grid corner.

        This function determines how walls connect at a specific
        grid intersection by checking surrounding cells.

        Args:
            grid (list[list[int]]): Maze grid encoded with bitmask walls.
            x (int): X-coordinate of the corner.
            y (int): Y-coordinate of the corner.
            width (int): Maze width.
            height (int): Maze height.

        Returns:
            str: Unicode character representing wall junction.
        """
        # Checks corners of cell (x, y)
        nw = grid[y - 1][x - 1] if y > 0 and x > 0 else 0
        ne = grid[y - 1][x] if y > 0 and x < width else 0
        sw = grid[y][x - 1] if y < height and x > 0 else 0
        se = grid[y][x] if y < height and x < width else 0

        # Wall exists if statement resolves to TRUE
        up = bool((nw & east) or (ne & west))  # East of nw or West of ne
        down = bool((sw & east) or (se & west))  # East of sw or West of se
        # South of nw or North of sw
        left = bool((nw & south) or (sw & north))
        # South of ne or North of se
        right = bool((ne & south) or (se & north))

        # Checks up, down, left, right walls
        # and picks the corresponding symbol
        res = {
            (True, True, True, True): "╋",
            (True, True, True, False): "┫",
            (True, True, False, True): "┣",
            (True, True, False, False): "┃",
            (True, False, True, True): "┻",
            (True, False, True, False): "┛",
            (True, False, False, True): "┗",
            (True, False, False, False): "┃",
            (False, True, True, True): "┳",
            (False, True, True, False): "┓",
            (False, True, False, True): "┏",
            (False, True, False, False): "┃",
            (False, False, True, True): "━",
            (False, False, True, False): "━",
            (False, False, False, True): "━",
            (False, False, False, False): " "
        }
        return res.get((up, down, left, right), " ")

    def _build_path_cells(
            self,
            start: tuple[int, int],
            path_str: str
    ) -> set[tuple[int, int]]:
        """
        Convert a path string into a set of visited coordinates.

        Args:
            start (tuple[int, int]): Starting coordinate.
            path_str (str): Path encoded as directions (N, E, S, W).

        Returns:
            set[tuple[int, int]]: Set of coordinates visited along path.
        """
        x, y = start
        cells = {(x, y)}
        moves = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

        for step in path_str:
            dx, dy = moves.get(step, (0, 0))
            x += dx
            y += dy
            cells.add((x, y))

        return cells
