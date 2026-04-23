#!/usr/bin/env python3

import sys
from typing import Optional
from mazegen import MazeGenerator
from app import read_config, render_box

"""Note: need to add docstrings for all functions"""

def generate_maze(config_file: str,
                  color: str = "",
                  seed: Optional[int] = None) -> str:
    config = read_config(config_file)
    seed_value = seed if seed is not None else config["SEED"]

    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        config["ENTRY"],
        config["EXIT"],
        seed_value,
        perfect=config["PERFECT"]
    )
    maze.generate(config, color, True)

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    return config["OUTPUT_FILE"]


def write_output(
        filename: str, maze: MazeGenerator, entry: tuple, exit: tuple
) -> None:
    path = maze.find_shortest_path()

    with open(filename, "w") as f:
        for line in maze.to_hex():
            f.write(line + "\n")

        f.write("\n")
        f.write(f"{entry}\n")
        f.write(f"{exit}\n")
        f.write(f"{path}\n")


# ANSI escape sequences for color
WHITE = "\033[097m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    config_file = sys.argv[1]

    colors = [WHITE, RED, GREEN, YELLOW, BLUE]
    color_index = 0
    show_path = False

    current_color = colors[color_index]
    output = generate_maze(config_file, current_color)
    render_box(output, current_color, show_path=show_path)

    while True:
        print("=== A-Maze-ing ===")
        print("1. Regenerate new maze")
        print("2. Show/hide path from entry to exit")
        print("3. Rotate maze colours")
        print("4. Quit")
        choice = input("Choice? (1-4): ")
        if choice == "1":
            import random

            output = generate_maze(config_file, current_color, seed=random.randint(1, 1000))
            render_box(output, current_color, show_path=show_path)

        elif choice == "2":
            show_path = not show_path
            render_box(output, current_color, show_path=show_path)

        elif choice == "3":
            color_index = (color_index + 1) % len(colors)
            current_color = colors[color_index]
            render_box(output, current_color, show_path=show_path)

        elif choice == "4":
            break


if __name__ == "__main__":
    main()
