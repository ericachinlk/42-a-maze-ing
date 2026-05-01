from mazegen import MazeGenerator, CLIRenderer

print("\033[2J\033[H", end="")
maze = MazeGenerator(
        width=10,
        height=10,
        entry=(0,0),
        exit=(6,5),
        seed=42,
        perfect=True,
        algorithm="dfs"
)
renderer = CLIRenderer(maze.get_maze_info())
maze.generate(renderer=renderer)
renderer.display_maze()

print(maze.perfect)
print(maze.grid)
print(maze.find_shortest_path())

