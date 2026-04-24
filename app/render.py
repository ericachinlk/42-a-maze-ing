import os
from typing import Dict


# Box Drawing Characters
V_WALL = "┃"
H_WALL = "━━━"
D_GREEN = "\033[42m"
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"

north, east, south, west = 1, 2, 4, 8


def get_corner(grid, x, y, width, height, final: bool = False) -> str:
    """
    Intersection at Top-Left of cell (x, y).
    Checks 4 adjacent cells to see which walls meet at this point.
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


def render_box(filepath: str, color: str = "", show_path: bool = False, final: bool = False) -> None:
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    grid_lines = []
    coord_lines = []
    path_line = ""

    for l in lines:
        if l.startswith("("):
            coord_lines.append(l)
        elif all(c in "0123456789ABCDEF" for c in l):
            grid_lines.append(l)
        else:
            path_line = l

    if not grid_lines:
        print(f"Error: {filepath} doesn't contain a valid maze.")
        return

    width, height = len(grid_lines[0]), len(grid_lines)
    grid = [[int(c, 16) for c in row] for row in grid_lines]

    def parse_tuple(s: str) -> tuple[int, int]:
        s = s.strip("()")
        x, y = s.split(",")
        return int(x), int(y)

    try:
        start_pos = parse_tuple(coord_lines[0])
        end_pos = parse_tuple(coord_lines[1])
    except (IndexError, ValueError):
        start_pos, end_pos = (0, 0), (width - 1, height - 1)

    def build_path_cells(start, path_str):
        x, y = start
        cells = {(x, y)}
        moves = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

        for step in path_str:
            dx, dy = moves.get(step, (0, 0))
            x += dx
            y += dy
            cells.add((x, y))

        return cells

    path_cells = set()
    if show_path and path_line:
        path_cells = build_path_cells(start_pos, path_line)

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
                    if (x, y) == start_pos:
                        line += f" {BOLD}{GREEN}S{RESET} "
                    elif (x, y) == end_pos:
                        line += f" {BOLD}{RED}G{RESET} "
                    elif (x, y) in path_cells:
                        line += f" {BOLD}{YELLOW}•{RESET} "
                    elif grid[y][x] == 15 and final:
                        line += f"{BOLD}\033[107m   {RESET}"
                    else:
                        line += "   "
            output.append(line)

    return ("\n".join(output))
