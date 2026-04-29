from mazegen import MazeGenerator


class AppRenderer:
    """
    Renderer implementation for CLI application.

    This class acts as a bridge between the reusable `MazeGenerator`
    module and the application-specific rendering logic.

    It delegates rendering responsibilities to functions defined
    in the app layer, keeping the core maze generator independent
    from any UI or display concerns.

    Methods:
        pre_render: Renders intermediate frames during maze generation.
        display_maze: Renders the final maze output.
    """
    def pre_render(
            self,
            maze: MazeGenerator,
            mode: str,
            color: str = ""
    ) -> None:
        """
        Render an intermediate frame of the maze during generation.

        This method is typically called repeatedly by the maze generator
        to visualize the step-by-step carving process.

        Args:
            config (dict[str, Any]): Configuration dictionary containing
                runtime settings (e.g. output file, dimensions).
            maze (MazeGenerator): The current maze generator instance,
                providing access to the grid state.
            mode (str): Display mode (e.g. "day" or "night").
            color (str, optional): ANSI color code for rendering walls.
                Defaults to "".

        Returns:
            None
        """
        from .generate_maze import pre_render
        pre_render(maze, mode, color)

    def display_maze(
            self,
            maze: MazeGenerator,
            color: str,
            mode: str,
            show_path: bool = False,
            final: bool = True
    ) -> None:
        """
        Render the maze to the terminal or output display.

        This method is used to display the final maze, and optionally
        the solution path.

        Args:
            filename (str): Path to the maze output file.
            color (str): ANSI color code for rendering walls.
            mode (str): Display mode (e.g. "day" or "night").
            show_path (bool, optional): Whether to overlay the shortest
                path on the maze. Defaults to False.
            final (bool, optional): Indicates whether this is the final
                render (affects formatting or animation behavior).
                Defaults to True.

        Returns:
            None
        """
        from .generate_maze import display_maze
        display_maze(maze, color, mode, show_path, final)
