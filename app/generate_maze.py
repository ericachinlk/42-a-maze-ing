from mazegen import MazeGenerator
from app import read_config, render_box
from typing import Optional


def generate_maze(
        config_file: str,
        color: str = "",
        seed: Optional[int] = None
) -> str:
    config = read_config(config_file)
    seed_value = seed if seed is not None else config["SEED"]

    # clear screen ONCE if animated
    if config["DISPLAY"] == "animated":
        print("\033[2J", end="")

    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        config["ENTRY"],
        config["EXIT"],
        seed_value,
        config["PERFECT"],
        config["ALGORITHM"],
        config["DISPLAY"]
    )
    maze.generate(config, color, True)

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    return config["OUTPUT_FILE"]


def display_maze(file, color, show_path, final):
    print("\033[2J\033[H", end="")
    print(render_box(file, color, show_path=show_path, final=True))


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

