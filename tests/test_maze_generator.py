import pytest
from mazegen import MazeGenerator


# -------------------------
# Helpers
# -------------------------

DIRS = {
    "N": (0, -1, 1),  # (dx, dy, wall bit)
    "E": (1, 0, 2),
    "S": (0, 1, 4),
    "W": (-1, 0, 8),
}


def is_valid_move(maze, x, y, direction):
    dx, dy, wall = DIRS[direction]
    nx, ny = x + dx, y + dy

    # within bounds
    if not (0 <= nx < maze.width and 0 <= ny < maze.height):
        return False

    # wall must be open (bit NOT set)
    if maze.grid[y][x] & wall != 0:
        return False

    return True


def traverse_path(maze, path):
    x, y = maze.entry
    for step in path:
        assert step in DIRS, f"Invalid direction: {step}"
        assert is_valid_move(maze, x, y, step), f"Illegal move {step} from {(x, y)}"

        dx, dy, _ = DIRS[step]
        x += dx
        y += dy

    return (x, y)


def bfs_reachable_count(maze):
    from collections import deque

    visited = set()
    queue = deque([maze.entry])
    visited.add(maze.entry)

    while queue:
        x, y = queue.popleft()

        for d, (dx, dy, wall) in DIRS.items():
            nx, ny = x + dx, y + dy

            if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                continue

            if maze.grid[y][x] & wall != 0:
                continue

            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    return len(visited)


# -------------------------
# TEST: Path validity
# -------------------------
def test_shortest_path_validity():
    maze = MazeGenerator(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    maze.generate()

    path = maze.find_shortest_path()

    assert path != "", "Path should exist"

    final_pos = traverse_path(maze, path)

    assert final_pos == maze.exit, "Path does not end at exit"


# -------------------------
# TEST: Connectivity (perfect maze)
# -------------------------
def test_perfect_maze_connectivity():
    maze = MazeGenerator(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    maze.generate()

    reachable = bfs_reachable_count(maze)

    assert reachable == maze.width * maze.height, "Maze is not fully connected"


# -------------------------
# TEST: Connectivity (Prim)
# -------------------------
def test_prim_maze_connectivity():
    maze = MazeGenerator(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        seed=42,
        perfect=True,
        algorithm="prim"
    )

    maze.generate()

    reachable = bfs_reachable_count(maze)

    assert reachable == maze.width * maze.height


# -------------------------
# TEST: Seed determinism
# -------------------------
def test_seed_determinism():
    maze1 = MazeGenerator(
        10, 10, (0, 0), (9, 9),
        seed=123,
        perfect=True,
        algorithm="dfs"
    )
    maze2 = MazeGenerator(
        10, 10, (0, 0), (9, 9),
        seed=123,
        perfect=True,
        algorithm="dfs"
    )

    maze1.generate()
    maze2.generate()

    assert maze1.grid == maze2.grid, "Same seed should produce identical mazes"


# -------------------------
# TEST: Different seeds → different mazes
# -------------------------
def test_seed_variation():
    maze1 = MazeGenerator(10, 10, (0, 0), (9, 9), seed=1, perfect=True, algorithm="dfs")
    maze2 = MazeGenerator(10, 10, (0, 0), (9, 9), seed=2, perfect=True, algorithm="dfs")

    maze1.generate()
    maze2.generate()

    assert maze1.grid != maze2.grid, "Different seeds should produce different mazes"


# -------------------------
# TEST: Non-perfect maze still solvable
# -------------------------
def test_non_perfect_maze_has_path():
    maze = MazeGenerator(
        10, 10, (0, 0), (9, 9),
        seed=42,
        perfect=False,
        algorithm="dfs"
    )

    maze.generate()

    path = maze.find_shortest_path()

    assert path != "", "Non-perfect maze should still have a solution"


# -------------------------
# TEST: Small maze edge case
# -------------------------
def test_small_maze():
    maze = MazeGenerator(
        1, 1, (0, 0), (0, 0),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    maze.generate()

    path = maze.find_shortest_path()

    assert path == "", "1x1 maze should have empty path"