from mazegen import MazeGenerator, CLIRenderer


def main() -> None:
    print("\033[2J\033[H", end="")

    maze = MazeGenerator(
        width=20,
        height=10,
        entry=(0, 0),
        exit=(19, 9),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    maze_info = maze.get_maze_info()
    renderer = CLIRenderer(maze_info)
    maze.generate(renderer=renderer)
    renderer.display_maze()


if __name__ == "__main__":
    main()
