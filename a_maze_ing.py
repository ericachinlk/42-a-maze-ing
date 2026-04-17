#!/usr/bin/env python3

import sys
from MazeGenerator import MazeGenerator
from typing import Any

"""Note: need to add docstrings for all functions"""


def read_config(filename: str) -> dict[str, Any]:
    raw: dict[str, str] = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Invalid line: {line}")
                key, value = line.split("=", 1)
                raw[key.strip()] = value.strip()
    except FileNotFoundError:
        raise SystemExit("Error: Config file not found")

    # Validate required fields
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT", "SEED"]
    for key in required:
        if key not in raw:
            raise SystemExit(f"Missing required config: {key}")

    # Convert types
    config: dict[str, Any] = {
        "WIDTH": int(raw["WIDTH"]),
        "HEIGHT": int(raw["HEIGHT"]),
        "ENTRY": tuple(map(int, raw["ENTRY"].split(","))),
        "EXIT": tuple(map(int, raw["EXIT"].split(","))),
        "OUTPUT_FILE": raw["OUTPUT_FILE"],
        "PERFECT": raw["PERFECT"] == "True",
        "SEED": int(raw["SEED"])}
    return config


def write_output(
        filename: str, maze: MazeGenerator, entry: tuple, exit_: tuple
) -> None:
    with open(filename, "w") as f:
        for line in maze.to_hex():
            f.write(line + "\n")

        f.write("\n")

        # need add this method in MazeGenerator
        # path = maze.find_path(entry, exit_)

        f.write(f"{entry}\n")
        f.write(f"{exit_}\n")
        # f.write(f"{path}\n")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        config = read_config(sys.argv[1])
        maze = MazeGenerator(config["WIDTH"], config["HEIGHT"], config["SEED"])
        maze.generate()

        # need to add this method in MazeGenerator
        # if not config["PERFECT"]:
        #     maze.add_loops()

        write_output(
            config["OUTPUT_FILE"],
            maze,
            config["ENTRY"],
            config["EXIT"]
        )
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
