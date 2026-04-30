from mazegen import MazeGenerator, CLIRenderer
from typing import Optional, Any


def generate_maze(
        config: dict[str, Any],
        seed: Optional[int] = None,
        display: bool = False
) -> tuple[MazeGenerator, CLIRenderer | None]:
    """
    Generate a maze from a configuration file and write the result to disk.

    This function serves as the main orchestration layer of the application.
    It reads the configuration, initializes the maze generator, runs the
    generation process, and writes the final output to a file.

    Workflow:
        1. Load configuration from file
        2. Determine random seed (override if provided)
        3. Initialize MazeGenerator instance
        4. Generate maze using selected algorithm
        5. Render via AppRenderer (optional animation)
        6. Write final maze output to file

    Args:
        config_file (str): Path to the configuration file containing maze
            parameters such as width, height, entry, exit, algorithm, etc.
        color (str, optional): ANSI escape code used for wall coloring.
            Defaults to "".
        mode (str, optional): Display mode for rendering ("day" or "night").
            Defaults to "day".
        seed (Optional[int], optional): Overrides the configuration seed
            for deterministic generation. If None, uses config seed.

    Returns:
        str: The output filename where the generated maze is written.
    """
    seed_value = seed if seed is not None else config["SEED"]

    print("\033[2J\033[H", end="")

    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        config["ENTRY"],
        config["EXIT"],
        seed=seed_value,
        perfect=config["PERFECT"],
        algorithm=config["ALGORITHM"],
    )

    maze_info = maze.get_maze_info()
    if display:
        renderer = CLIRenderer(maze_info)
        maze.generate(renderer=renderer)
    else:
        renderer = None
        maze.generate()

    maze.write_output(config["OUTPUT_FILE"])

    return maze, renderer
