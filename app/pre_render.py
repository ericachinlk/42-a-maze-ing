from mazegen import MazeGenerator
from typing import Dict, Any
import os
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

    output = render_box(config["OUTPUT_FILE"], color, final=False)
    # os.system('clear')
    # print(output)
    # time.sleep(0.03)
    print("\033[H", end="")   # move cursor to top-left
    print(output)  # removed flush because there wasn't a need
    time.sleep(0.03)