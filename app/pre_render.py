from mazegen import MazeGenerator
from typing import Dict, Any
import time


def pre_render(config: Dict[str, Any],
               maze: MazeGenerator,
               color: str = "") -> None:
    from .render import render_box
    from .generate_maze import write_output

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    print("\033[H", end="")   # move cursor to top-left
    print(render_box(config["OUTPUT_FILE"], color, final=False))
    time.sleep(0.03)