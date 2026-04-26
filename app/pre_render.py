from mazegen import MazeGenerator
from typing import Dict, Any
import time


def pre_render(config: Dict[str, Any],
               maze: MazeGenerator,
               mode: str,
               color: str = "") -> None:
    from .generate_maze import write_output, display_maze

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    display_maze(config["OUTPUT_FILE"], color, mode, final=False)
    time.sleep(0.03)
