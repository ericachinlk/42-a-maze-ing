from mazegen import MazeGenerator, CLIRenderer
from typing import Optional, Any


def generate_maze(
        config: dict[str, Any],
        seed: Optional[int] = None,
        display: bool = False
) -> tuple[MazeGenerator, CLIRenderer | None]:
    """
    Generate a maze from configuration and optionally render it.

    Initializes a MazeGenerator using the provided configuration, runs the
    maze generation process, optionally performs live CLI rendering, and
    writes the final maze output to disk.

    Args:
        config (dict[str, Any]): Parsed configuration dictionary containing
            maze parameters such as width, height, entry, exit, algorithm,
            seed, and output file path.
        seed (Optional[int]): Overrides the configuration seed for
            deterministic generation. If None, the seed from config is used.
        display (bool): If True, enables CLI rendering during generation.

    Returns:
        tuple[MazeGenerator, CLIRenderer | None]:
            The generated MazeGenerator instance and the renderer (if display
            is enabled), otherwise None.
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
