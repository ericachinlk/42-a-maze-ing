#!/usr/bin/env python3

import sys
from app import read_config, generate_maze, display_maze, show_config, set_config, ConfigError, RenderError

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

    # colors = [WHITE, RED, GREEN, YELLOW, BLUE]
    wall_colors = [
    "\033[38;5;240m",  # gray
    "\033[38;5;67m",   # soft blue
    "\033[38;5;108m",  # soft green
    "\033[38;5;137m",  # muted amber
    "\033[38;5;131m",  # dusty red
]
    color_index = 0
    show_path = False
    # current_color = colors[color_index]
    current_wall_color = wall_colors[color_index]
    try:
        output = generate_maze(config_file, current_wall_color)
        mode = "day"
        while True:
            config = read_config(config_file)
            print("=== A-Maze-ing ===")
            print("1. Regenerate new maze")
            print("2. Show/hide path from entry to exit")
            print("3. Rotate maze colours")
            print(f"4. Day/Night mode: {mode}")
            print(f"5. Algorithm: {config['ALGORITHM']}")
            print("6. Show configurations")
            print("7. Quit")
            choice = input("Choice? (1-7): ")
            if choice == "1":
                show_path = False
                import random

                output = generate_maze(config_file, current_wall_color, seed=random.randint(1, 1000))

            elif choice == "2":
                show_path = not show_path
                display_maze(output, current_wall_color, show_path, mode=mode)

            elif choice == "3":
                color_index = (color_index + 1) % len(wall_colors)
                current_wall_color = wall_colors[color_index]
                display_maze(output, current_wall_color, show_path, mode=mode)
            
            elif choice == "4":
                mode = "night" if mode == "day" else "day"
                display_maze(output, current_wall_color, show_path, mode=mode)
            
            elif choice == "5":
                val = "prim" if config["ALGORITHM"] == "dfs" else "dfs"
                set_config(config_file, config["ALGORITHM"], val)

                show_path = False
                output = generate_maze(config_file, current_wall_color)
            
            elif choice == "6":
                show_config(config_file)

            elif choice == "7":
                break
    
    except ConfigError as e:
        print("Configurations Error:", e)
        sys.exit()
    except RenderError as e:
        print("Rendering Error:", e)
        sys.exit()


if __name__ == "__main__":
    main()
