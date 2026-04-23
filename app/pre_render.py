from mazegen import MazeGenerator
from typing import Dict, Any
import os
import time


def pre_render(config: Dict[str, Any],
               maze: MazeGenerator,
               color: str = "") -> None:
    from .render import render_box
    from a_maze_ing import write_output

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )

    
    output = render_box(config["OUTPUT_FILE"], color)
    os.system('clear')
    print(output)
    time.sleep(0.03)