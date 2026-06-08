#!/usr/bin/env python3

"""
Entry point for the A-Maze-ing CLI application.

This module runs the interactive command-line interface for generating
and controlling the maze system, including configuration loading,
maze generation, rendering, and user interaction.
"""

import sys
import random
import os
from app import (generate_maze, read_config, toggle_perfect,
                 set_algorithm, ConfigError)
from mazegen import MazeError, RenderError
from typing import Any

DEBUG = os.getenv("DEBUG") == "1"


def show_config(config: dict[str, Any], seed_val: int) -> None:
    """
    Display the current maze configuration in a formatted box.

    Args:
        config (dict[str, Any]): Configuration dictionary.
        seed_val (int): Active seed used for maze generation.

    Returns:
        None
    """
    config["ACTIVE_SEED"] = seed_val
    print("\n┌────── Active Configurations ──────┐")
    for k, v in config.items():
        print(f"│ {k:<12} : {str(v):<18} │")
    print("└───────────────────────────────────┘\n")


def main() -> None:
    """
    Entry point for the A-Maze-ing CLI application.

    This function:
    - Loads configuration from a file provided via CLI argument
    - Generates the initial maze
    - Runs an interactive menu loop allowing the user to:
        - regenerate maze
        - toggle shortest path visibility
        - rotate wall colours
        - switch between day/night themes
        - switch maze generation algorithms
        - toggle perfect/non-perfect maze mode
        - view configuration details
        - exit the program

    The function also handles runtime errors from configuration,
    rendering, and maze generation gracefully.

    Returns:
        None
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    config_file = sys.argv[1]

    try:
        config = read_config(config_file)
        show_path = True
        maze, renderer = generate_maze(config, display=True)
        seed_val = maze.seed
        color = "\033[38;5;240m"
        mode = "day"
        show_config_status = False

        while True and renderer:
            config = read_config(config_file)
            perfectness = "perfect" if config["PERFECT"] else "non-perfect"

            if not show_config_status:
                renderer.display_maze(show_path=show_path, color=color, mode=mode)
            else:
                show_config(config, seed_val)
                print("\033[2J\033[H", end="")
                show_config_status = False

            print("=== A-Maze-ing ===")
            print("1. Regenerate new maze")
            print("2. Show/hide shortest path from entry to exit")
            print("3. Change maze wall colours")
            print(f"4. Toggle day/night mode: {mode}")
            print(f"5. Switch algorithm: {config['ALGORITHM']}")
            print(f"6. Toggle maze loops: {perfectness}")
            print("7. Show configurations")
            print("8. Quit")

            if DEBUG:
                print("\n[DEBUG MAZE]")
                print("Size:", maze.width, maze.height)
                print("Entry:", maze.entry)
                print("Exit:", maze.exit)
                print("Algorithm:", maze.algorithm)
                print("Seed:", maze.seed)
                print("\nGrid (raw):")
                for row in maze.grid:
                    print(row)
                breakpoint()

            choice = input("Choice? (1-8): ")

            if choice == "1":
                seed_val = random.randint(1, 1000)
                config = read_config(config_file)
                maze, renderer = generate_maze(
                    config, seed=seed_val, display=True, color=color)

            elif choice == "2":
                show_path = not show_path
                print("\033[2J\033[H", end="")

            elif choice == "3":
                color = renderer.rotate_wall_color()
                print("\033[2J\033[H", end="")

            elif choice == "4":
                mode = renderer.toggle_mode()
                print("\033[2J\033[H", end="")

            elif choice == "5":
                val = "prim" if config["ALGORITHM"] == "dfs" else "dfs"
                set_algorithm(config_file, config["ALGORITHM"], val)
                config = read_config(config_file)
                maze, renderer = generate_maze(
                    config, seed=seed_val, display=True, color=color)

            elif choice == "6":
                toggle_perfect(config_file)
                config = read_config(config_file)
                maze, renderer = generate_maze(
                    config, seed=seed_val, display=True, color=color)

            elif choice == "7":
                show_config_status = True

            elif choice == "8":
                break

            else:
                print("Unknown command. "
                      "Please input number only between 1-8\n")

    except ConfigError as e:
        print("Configurations Error:", e)
        return
    except RenderError as e:
        print("\033[2J\033[H", end="")
        print("Rendering Error:", e)
        return
    except MazeError as e:
        print("Maze Generation Error:", e)
        return


if __name__ == "__main__":
    main()
