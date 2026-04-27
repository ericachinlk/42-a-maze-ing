from mazegen import MazeGenerator
from app import read_config, render_maze
from typing import Optional, Any


def generate_output(
        config_file: str,
        color: str = "",
        mode: str = "day",
        seed: Optional[int] = None,
) -> Any:
    """
    Generate a maze based on configuration and write it to output file.

    This function:
    - Reads configuration file
    - Creates MazeGenerator instance
    - Generates maze using selected algorithm
    - Writes final maze output to file

    Args:
        config_file (str): Path to configuration file.
        color (str): Wall color escape code.
        mode (str): Display mode ("day" or "night").
        seed (Optional[int]): Override seed for deterministic generation.

    Returns:
        Any: Output filename where maze is saved.
    """
    config = read_config(config_file)
    seed_value = seed if seed is not None else config["SEED"]

    print("\033[2J\033[H", end="")

    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        config["ENTRY"],
        config["EXIT"],
        seed_value,
        config["PERFECT"],
        config["ALGORITHM"]
    )
    maze.generate(config, color, mode, use_pattern=True)

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    return config["OUTPUT_FILE"]


def display_maze(
        filename: str,
        color: str,
        mode: str,
        show_path: bool = False,
        final: bool = True
) -> None:
    """
    Render maze output in terminal.

    Args:
        filename (str): Maze output file.
        color (str): Wall color scheme.
        mode (str): Display mode ("day" or "night").
        show_path (bool): Whether to display shortest path.
        final (bool): Whether this is final render or animation frame.
    """
    print("\033[H\033[J", end="")
    print(render_maze(filename, color, show_path, final, mode))


def write_output(
        filename: str,
        maze: MazeGenerator,
        entry: tuple[int, int],
        exit: tuple[int, int]
) -> None:
    """
    Write maze data and metadata to output file.

    File format:
    - Hex grid representation
    - Entry coordinates
    - Exit coordinates
    - Shortest path string

    Args:
        filename (str): Output file path.
        maze (MazeGenerator): Generated maze object.
        entry (tuple[int, int]): Entry coordinate.
        exit (tuple[int, int]): Exit coordinate.
    """
    path = maze.find_shortest_path()

    with open(filename, "w") as f:
        for line in maze.to_hex():
            f.write(line + "\n")

        f.write("\n")
        f.write(f"{entry}\n")
        f.write(f"{exit}\n")
        f.write(f"{path}\n")
