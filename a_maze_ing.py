#!/usr/bin/env python3
"""
Main entry point for the A-Maze-ing project.

This module provides a CLI interface for generating, displaying,
and interacting with a maze generator system.
"""

import sys
import random
from app import (read_config, generate_output, display_maze, toggle_perfect,
                 show_config, set_algorithm, ConfigError, RenderError)


def main() -> None:
    """
    Run the main interactive maze application.

    This function:
    - Loads configuration file from command-line argument
    - Generates initial maze
    - Provides an interactive menu for:
        - regenerating maze
        - toggling shortest path display
        - changing wall colours
        - switching day/night mode
        - switching algorithms
        - toggling perfect/non-perfect maze
        - viewing configuration
    - Handles runtime errors gracefully

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    config_file = sys.argv[1]

    wall_colors = [
        "\033[38;5;240m",
        "\033[38;5;67m",
        "\033[38;5;108m",
        "\033[38;5;137m",
        "\033[38;5;131m"]
    color_index = 0
    show_path = False
    current_wall_color = wall_colors[color_index]

    try:
        mode = "day"
        output = generate_output(config_file, current_wall_color, mode)
        while True:
            config = read_config(config_file)
            perfectness = "perfect" if config["PERFECT"] else "non-perfect"
            print("=== A-Maze-ing ===")
            print("1. Regenerate new maze")
            print("2. Show/hide shortest path from entry to exit")
            print("3. Change maze wall colours")
            print(f"4. Toggle day/night mode: {mode}")
            print(f"5. Switch algorithm: {config['ALGORITHM']}")
            print(f"6. Toggle maze loops: {perfectness}")
            print("7. Show configurations")
            print("8. Quit")
            choice = input("Choice? (1-8): ")

            if choice == "1":
                show_path = False
                output = generate_output(
                    config_file, current_wall_color, mode,
                    seed=random.randint(1, 1000))

            elif choice == "2":
                show_path = not show_path
                print("\033[2J\033[H", end="")
                display_maze(output, current_wall_color, mode,
                             show_path=show_path)

            elif choice == "3":
                color_index = (color_index + 1) % len(wall_colors)
                current_wall_color = wall_colors[color_index]
                print("\033[2J\033[H", end="")
                display_maze(output, current_wall_color, mode,
                             show_path=show_path)

            elif choice == "4":
                mode = "night" if mode == "day" else "day"
                print("\033[2J\033[H", end="")
                display_maze(output, current_wall_color, mode,
                             show_path=show_path)

            elif choice == "5":
                val = "prim" if config["ALGORITHM"] == "dfs" else "dfs"
                set_algorithm(config_file, config["ALGORITHM"], val)

                show_path = False
                output = generate_output(config_file, current_wall_color, mode)

            elif choice == "6":
                toggle_perfect(config_file)
                show_path = False
                output = generate_output(config_file, current_wall_color, mode)

            elif choice == "7":
                show_config(config_file)

            elif choice == "8":
                break

            else:
                print("Unknown command. "
                      "Please input number only between 1-8\n")

    except ConfigError as e:
        print("Configurations Error:", e)
        sys.exit()
    except RenderError as e:
        print("\033[2J\033[H", end="")
        print("Rendering Error:", e)
        sys.exit()


if __name__ == "__main__":
    main()
