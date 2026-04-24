#!/usr/bin/env python3

import sys
from app import read_config, generate_maze, display_maze, show_config, set_config

"""Note: need to add docstrings for all functions"""


# ANSI escape sequences for color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
WHITE = "\033[37m"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    config_file = sys.argv[1]

    colors = [WHITE, RED, GREEN, YELLOW, BLUE]
    color_index = 0
    show_path = False
    current_color = colors[color_index]
    config = read_config(config_file)
    output = generate_maze(config_file, current_color)

    # if config["DISPLAY"] == "static":
    display_maze(output, current_color, show_path, True)

    while True:
        print("=== A-Maze-ing ===")
        print("1. Regenerate new maze")
        print("2. Show/hide path from entry to exit")
        print("3. Rotate maze colours")
        print("4. Display current configurations")
        print("5. Modify configurations")
        print("6. Quit")
        choice = input("Choice? (1-6): ")
        if choice == "1":
            import random

            output = generate_maze(config_file, current_color, seed=random.randint(1, 1000))
            # if config["DISPLAY"] == "static":
            display_maze(output, current_color, show_path, True)

        elif choice == "2":
            show_path = not show_path
            # if config["DISPLAY"] == "static":
            display_maze(output, current_color, show_path, True)

        elif choice == "3":
            color_index = (color_index + 1) % len(colors)
            current_color = colors[color_index]
            # if config["DISPLAY"] == "static":
            display_maze(output, current_color, show_path, True)
        
        elif choice == "4":
            show_config("../config.txt")
        
        # this is not working as it should... it keeps saying cannot find the keyword, will fix
        elif choice == "5":
            mod = input("Usage: KEY VALUE, e.g. 'ALGORITHM prim': ").split()
            if len(mod) != 2:
                print("Usage: KEY VALUE")
                sys.exit(1)
            key = mod[0]
            value = mod[1]
            set_config("../config.txt", key, value)

        elif choice == "6":
            break


if __name__ == "__main__":
    main()
