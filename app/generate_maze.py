from mazegen import MazeGenerator, MazeError
from typing import Optional
import time


def generate_output(
        config_file: str,
        color: str = "",
        mode: str = "day",
        seed: Optional[int] = None,
) -> MazeGenerator:
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
    from app.config import read_config
    config = read_config(config_file)
    seed_value = seed if seed is not None else config["SEED"]

    print("\033[2J\033[H", end="")

    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        config["ENTRY"],
        config["EXIT"],
        seed=seed_value,
        perfect=config["PERFECT"],
        algorithm=config["ALGORITHM"]
    )
    from app.app_renderer import AppRenderer
    renderer = AppRenderer()

    maze.generate(
        color=color,
        mode=mode,
        use_pattern=True,
        renderer=renderer)

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )
    return maze


def display_maze(
        maze: MazeGenerator,
        color: str,
        mode: str,
        show_path: bool = False,
        final: bool = True
) -> None:
    """
    Render a maze file to the terminal.

    This function reads a generated maze file and displays it using
    the rendering system. It supports optional path visualization and
    different display modes.

    Args:
        filename (str): Path to the maze output file.
        color (str): ANSI escape code used for wall coloring.
        mode (str): Display mode ("day" or "night").
        show_path (bool, optional): If True, overlays the shortest path
            onto the maze. Defaults to False.
        final (bool, optional): Indicates whether this is the final frame
            of rendering (affects formatting/animation behavior).
            Defaults to True.

    Returns:
        None
    """
    from app.render import render_maze
    print("\033[H\033[J", end="")
    print(render_maze(maze, color, show_path, final, mode))


def write_output(
        filename: str,
        maze: MazeGenerator,
        entry: tuple[int, int],
        exit: tuple[int, int]
) -> None:
    """
    Write the generated maze and metadata to a file.

    The output file contains:
        - Hexadecimal maze grid representation
        - Entry coordinate
        - Exit coordinate
        - Shortest path string (if exists)

    File format example:
        <hex grid lines>

        (entry_x, entry_y)
        (exit_x, exit_y)
        <path string>

    Args:
        filename (str): Output file path.
        maze (MazeGenerator): Generated maze instance.
        entry (tuple[int, int]): Entry coordinate (x, y).
        exit (tuple[int, int]): Exit coordinate (x, y).

    Returns:
        None
    """
    path = maze.find_shortest_path()
    try:
        with open(filename, "w") as f:
            for line in maze.to_hex():
                f.write(line + "\n")

            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")
            f.write(f"{path}\n")
    except OSError as e:
        raise MazeError(f"Failed to write output file: {e}")


def pre_render(
        maze: MazeGenerator,
        mode: str,
        color: str = ""
) -> None:
    """
    Render an intermediate animation frame of the maze generation process.

    This function is called during maze generation to:
    - Write current maze state to output file
    - Display it in the terminal
    - Pause briefly to create animation effect

    Args:
        config (Dict[str, Any]):
            Configuration dictionary containing maze settings.
        maze (MazeGenerator): Current maze object being generated.
        mode (str): Display mode ("day" or "night").
        color (str): Wall color escape code for rendering.

    Returns:
        None
    """
    display_maze(maze, color, mode, final=False)
    time.sleep(0.03)
