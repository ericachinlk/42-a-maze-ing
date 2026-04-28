# Box Drawing Characters
V_WALL = "┃"
H_WALL = "━━━"
RESET = "\033[0m"  # Resets all ANSI formatting

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


def get_corner(
        grid: list[list[int]],
        x: int, y: int, width: int, height: int) -> str:
    """
    Compute the correct Unicode box-drawing character for a grid corner.

    This function determines how walls connect at a specific grid intersection
    by checking surrounding cells.

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
    left = bool((nw & south) or (sw & north))  # South of nw or North of sw
    right = bool((ne & south) or (se & north))  # South of ne or North of se

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


def build_path_cells(
        start: tuple[int, int], path_str: str) -> set[tuple[int, int]]:
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


def parse_tuple(s: str) -> tuple[int, int]:
    """
    Parse a coordinate string into a tuple.

    Expected format: "(x,y)"

    Args:
        s (str): Coordinate string.

    Returns:
        tuple[int, int]: Parsed (x, y) coordinate.
    """
    s = s.strip("()")
    x, y = s.split(",")
    return int(x), int(y)


def render_maze(
        filepath: str,
        color: str = "",
        show_path: bool = False,
        final: bool = False,
        mode: str = "day"
) -> str:
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
        final (bool): Whether this is final render (shows start/goal/pattern).
        mode (str): Display theme mode ("day" or "night").

    Returns:
        str: Fully rendered maze as a string.

    Raises:
        RenderError: If file is missing or maze format is invalid.
    """
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        raise RenderError(f"{filepath} not found.")

    grid_lines = []
    coord_lines = []
    path_line = ""

    for line in lines:
        if line.startswith("("):
            coord_lines.append(line)
        elif all(c in "0123456789ABCDEF" for c in line):
            grid_lines.append(line)
        else:
            path_line = line

    if not grid_lines:
        raise RenderError(f"{filepath} doesn't contain a valid maze.")

    width, height = len(grid_lines[0]), len(grid_lines)
    grid = [[int(c, 16) for c in row] for row in grid_lines]

    try:
        start_pos = parse_tuple(coord_lines[0])
        end_pos = parse_tuple(coord_lines[1])
    except (IndexError, ValueError):
        start_pos, end_pos = (0, 0), (width - 1, height - 1)

    path_cells = set()
    if show_path and path_line:
        path_cells = build_path_cells(start_pos, path_line)

    theme = THEMES.get(mode, THEMES["day"])

    output = []
    for y in range(height + 1):
        line = ""
        for x in range(width + 1):
            line += f"{color}{get_corner(grid, x, y, width, height)}{RESET}"

            if x < width:
                if y == 0:
                    has_h = grid[0][x] & north
                elif y == height:
                    has_h = grid[height - 1][x] & south
                else:
                    has_h = (grid[y - 1][x] & south) or (grid[y][x] & north)

                line += f"{color}{H_WALL}{RESET}" if has_h else "   "
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

                line += f"{color}{V_WALL}{RESET}" if has_v else " "

                if x < width:
                    if (x, y) == start_pos and final:
                        line += f" \033[1m{theme['start']}S{RESET} "
                    elif (x, y) == end_pos and final:
                        line += f" \033[1m{theme['goal']}G{RESET} "
                    elif (x, y) in path_cells:
                        line += f" {theme['path']}·{RESET} "
                    elif grid[y][x] == 15 and final:
                        line += f"{theme['pattern']}   {RESET}"
                    else:
                        line += "   "
            output.append(line)

    return ("\n".join(output))
