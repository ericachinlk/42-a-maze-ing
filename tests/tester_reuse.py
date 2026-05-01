from mazegen import MazeGenerator, MazeError, RenderError, CLIRenderer
import sys


def demo_1(maze: MazeGenerator) -> None:
    print("\n======= DEMO 1 (WITHOUT DISPLAY) =======")
    maze.generate()

    print("Print the grid in hex format:")
    grid_lines = maze.to_hex()
    for line in grid_lines:
        print(line)

    print("\nPrint shortest_path:", maze.find_shortest_path())

    filename = "output_test.txt"
    print(f"\nExport grid data to '{filename}'")
    maze.write_output(filename)

def demo_2(maze: MazeGenerator) -> None:
    renderer = CLIRenderer(maze.get_maze_info())
    maze.generate(renderer=renderer)
    renderer.display_maze()
    print("\n======= DEMO 2 (WITH DISPLAY) =======")
    print("Default maze display: path shown, day mode, grey wall color")

    print("\nHide path in maze display")
    renderer.display_maze(show_path=False, clear_screen=False)

    print("\nToggle day/night mode")
    renderer.toggle_mode()
    renderer.display_maze(clear_screen=False)

    print("\nRotate maze wall colors")
    renderer.rotate_wall_color()
    renderer.display_maze(clear_screen=False)


def demo_3(maze: MazeGenerator) -> None:
    renderer = CLIRenderer(maze.get_maze_info())
    maze.generate(renderer=renderer, use_pattern=False)
    renderer.display_maze()
    print("\n======= DEMO 3 (DISPLAY WITHOUT PATTERN) =======")
    print("Default maze display: path shown, day mode, grey wall color")


def main() -> None:
    try:
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

        if sys.argv[1] == "demo1":
            demo_1(maze)
        elif sys.argv[1] == "demo2":
            print("\033[2J\033[H", end="")
            demo_2(maze)
        elif sys.argv[1] == "demo3":
            print("\033[2J\033[H", end="")
            demo_3(maze)
        else:
            print("Unknown argument.")

    except (MazeError, RenderError) as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
