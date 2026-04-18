import sys
import os
from typing import Dict


# Box Drawing Characters
V_WALL = "┃"
H_WALL = "━━━"
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"


north, east, south, west = 1, 2, 4, 8


def get_corner(grid, x, y, width, height) -> Dict[str, bool]:
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


def render_box(filepath: str) -> None:
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    grid_lines = [l for l in lines if not l.startswith('(')]
    coord_lines = [l for l in lines if l.startswith('(')]
    if not grid_lines:
        print(f"Error: {filepath} doesn't contain a valid maze.")
        return

    width, height = len(grid_lines[0]), len(grid_lines)

    # Creates a 2D array of ints from the hex values
    grid = [[int(c, 16) for c in row] for row in grid_lines]

    # Get start and end positions, turns it into tuple of ints
    try:
        start_pos = eval(coord_lines[0])
        end_pos = eval(coord_lines[1])
    except (IndexError, SyntaxError):
        start_pos, end_pos = (0, 0), (width - 1, height - 1)

    output = []
    for y in range(height + 1):
        line = ""
        for x in range(0, width + 1):
            line += get_corner(grid, x, y, width, height)
            # Horizontal walls
            if x < width:
                has_h = False
                if y == 0:
                    has_h = (grid[0][x] & north) # Top row
                elif y == height:
                    has_h = (grid[height - 1][x] & south) # Bottom row
                else:
                    has_h = (grid[y - 1][x] & south) or (grid[y][x] & north) # Middle rows
                line += H_WALL if has_h else "   "
        output.append(line)

        if y < height:
            line = ""
            # Vertical walls
            for x in range(0, width + 1):
                has_v = False
                if x == 0:
                    has_v = (grid[y][0] & west) # Left wall
                elif x == width:
                    has_v = (grid[y][width - 1] & east) # Right wall
                else:
                    has_v = (grid[y][x - 1] & east) or (grid[y][x] & west) # Middle walls
                line += V_WALL if has_v else " "

                if x < width:
                    if (x, y) == start_pos:
                        line += f" {BOLD}{GREEN}S{RESET} "
                    elif (x, y) == end_pos:
                        line += f" {BOLD}{RED}G{RESET} "
                    else:
                        line += "   "
            output.append(line)

    print("\n".join(output))


# Testing
if __name__ == "__main__":
    render_box("../maze.txt")
