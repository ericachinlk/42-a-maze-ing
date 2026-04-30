#!/usr/bin/env python3
"""
Main entry point for the A-Maze-ing project.

This module provides a CLI interface for generating, displaying,
and interacting with a maze generator system.
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
    config["ACTIVE_SEED"] = seed_val
    print("\n┌────── Active Configurations ──────┐")
    for k, v in config.items():
        print(f"│ {k:<12} : {str(v):<18} │")
    print("└───────────────────────────────────┘\n")


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

    try:
        config = read_config(config_file)
        show_path = True
        maze, renderer = generate_maze(config, display=True)
        seed_val = maze.seed
        show_config_status = False

        while True and renderer:
            config = read_config(config_file)
            perfectness = "perfect" if config["PERFECT"] else "non-perfect"

            if not show_config_status:
                renderer.display_maze(show_path=show_path)
                if maze.pattern_error:
                    print("\n[WARNING] '42' pattern skipped: "
                          f"{maze.pattern_error}")
            else:
                show_config(config, seed_val)
                print("\033[2J\033[H", end="")
                show_config_status = False

            print("=== A-Maze-ing ===")
            print("1. Regenerate new maze")
            print("2. Show/hide shortest path from entry to exit")
            print("3. Change maze wall colours")
            print(f"4. Toggle day/night mode: {renderer.mode}")
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
                maze, renderer = generate_maze(
                    config, seed=seed_val, display=True)

            elif choice == "2":
                show_path = not show_path
                print("\033[2J\033[H", end="")

            elif choice == "3":
                renderer.rotate_wall_color()
                print("\033[2J\033[H", end="")

            elif choice == "4":
                renderer.toggle_mode()
                print("\033[2J\033[H", end="")

            elif choice == "5":
                val = "prim" if config["ALGORITHM"] == "dfs" else "dfs"
                set_algorithm(config_file, config["ALGORITHM"], val)
                maze, renderer = generate_maze(
                    config, seed=seed_val, display=True)

            elif choice == "6":
                toggle_perfect(config_file)
                maze, renderer = generate_maze(
                    config, seed=seed_val, display=True)

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
