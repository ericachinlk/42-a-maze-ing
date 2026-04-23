from mazegen.MazeGenerator import MazeGenerator
from typing import Dict, Any


def pre_render(config: Dict[str, Any],
               maze: MazeGenerator,
               color: str = "") -> None:
    from .render_maze import render_box
    from a_maze_ing import write_output

    write_output(
        config["OUTPUT_FILE"],
        maze,
        config["ENTRY"],
        config["EXIT"]
    )
    render_box(config["OUTPUT_FILE"], color)