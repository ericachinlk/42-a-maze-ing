from mazegen import MazeGenerator, MazeError, RenderError, CLIRenderer


def main():

    display = input("Display the maze? (y/n): ")

    try:
        maze = MazeGenerator(
            width=20,
            height=10,
            entry=(0, 0),
            exit=(19, 9),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )

        if display == "y":
            renderer = CLIRenderer(maze.get_maze_info())
            maze.generate(use_pattern=True, renderer=renderer)
            renderer.path = maze.find_shortest_path()
            renderer.display_maze(show_path=True)

            renderer.toggle_mode()
            renderer.rotate_wall_color()

            print(maze.grid)
            print(maze.find_shortest_path())
            maze.write_output("output_test.txt")
        
        elif display == "n":
            maze.generate()
            print(maze.grid)
            print(maze.find_shortest_path())
            maze.write_output("output_test.txt")
        
        else:
            print("Unknown command. Please enter only 'y' or 'n'\n")

    except (MazeError, RenderError) as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
