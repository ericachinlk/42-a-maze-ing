from mazegen import MazeGenerator
from typing import Any
import time


def pre_render(config: dict[str, Any],
               maze: MazeGenerator,
               mode: str,
               color: str = "") -> None:
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
    from .generate_maze import write_output, display_maze

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    display_maze(config["OUTPUT_FILE"], color, mode, final=False)
    time.sleep(0.03)
