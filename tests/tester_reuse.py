from mazegen import MazeGenerator, MazeError


def validate_path(maze: MazeGenerator, path: str) -> bool:
    x, y = maze.entry

    moves = {
        "N": (0, -1, 1),
        "E": (1, 0, 2),
        "S": (0, 1, 4),
        "W": (-1, 0, 8),
    }

    for step in path:
        dx, dy, wall = moves[step]

        # wall must be OPEN
        if maze.grid[y][x] & wall != 0:
            return False

        x += dx
        y += dy

    return (x, y) == maze.exit


def main():
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

        maze.generate()

        print(maze.grid)                 # raw structure
        print(maze.find_shortest_path()) # solution path (N/E/S/W)
        print(validate_path(maze, maze.find_shortest_path()))
        print()

        data = maze.to_hex()
        for line in data:
            print(line)

    except MazeError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
