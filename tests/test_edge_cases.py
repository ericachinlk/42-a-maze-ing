import pytest
from mazegen import MazeGenerator, MazeError


# -------------------------
# INVALID ENTRY / EXIT
# -------------------------

def test_entry_equals_exit():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry=(0, 0),
            exit=(0, 0),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


def test_entry_out_of_bounds():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry=(5, 0),  # invalid
            exit=(4, 4),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


def test_exit_out_of_bounds():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry=(0, 0),
            exit=(10, 10),  # invalid
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


def test_negative_coordinates():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry=(-1, 0),
            exit=(4, 4),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


def test_non_tuple_entry():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry="0,0",  # wrong type
            exit=(4, 4),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


# -------------------------
# INVALID DIMENSIONS
# -------------------------

def test_zero_dimensions():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=0,
            height=5,
            entry=(0, 0),
            exit=(0, 4),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


def test_negative_dimensions():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=-5,
            height=5,
            entry=(0, 0),
            exit=(4, 4),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )


# -------------------------
# INVALID ALGORITHM
# -------------------------

def test_invalid_algorithm():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry=(0, 0),
            exit=(4, 4),
            seed=42,
            perfect=True,
            algorithm="random"  # invalid
        )


# -------------------------
# PATTERN EDGE CASES
# -------------------------

def test_pattern_too_small_maze():
    """
    Pattern should NOT crash even if maze too small.
    """
    maze = MazeGenerator(
        width=5,
        height=5,
        entry=(0, 0),
        exit=(4, 4),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    # should not crash
    maze.generate(use_pattern=True)

    path = maze.find_shortest_path()
    assert path != ""


def test_pattern_does_not_block_entry_exit():
    """
    Pattern must never overwrite entry/exit.
    """
    maze = MazeGenerator(
        width=10,
        height=10,
        entry=(5, 5),
        exit=(9, 9),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    maze.generate(use_pattern=True)

    # entry and exit must still be reachable
    path = maze.find_shortest_path()
    assert path != ""


def test_pattern_connectivity_not_broken():
    """
    Even with pattern, maze should still be solvable.
    """
    maze = MazeGenerator(
        width=12,
        height=12,
        entry=(0, 0),
        exit=(11, 11),
        seed=42,
        perfect=True,
        algorithm="dfs"
    )

    maze.generate(use_pattern=True)

    path = maze.find_shortest_path()
    assert path != ""


# -------------------------
# STRESS: RANDOM ENTRY/EXIT VALIDITY
# -------------------------

@pytest.mark.parametrize("entry,exit", [
    ((0, 0), (9, 9)),
    ((9, 0), (0, 9)),
    ((5, 5), (0, 0)),
    ((3, 7), (8, 2)),
])
def test_various_entry_exit_positions(entry, exit):
    maze = MazeGenerator(
        width=10,
        height=10,
        entry=entry,
        exit=exit,
        seed=42,
        perfect=True,
        algorithm="prim"
    )

    maze.generate()

    path = maze.find_shortest_path()
    assert path != "", f"No path from {entry} to {exit}"


# -------------------------
# INVALID SEED TYPE
# -------------------------

def test_invalid_seed_type():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5,
            height=5,
            entry=(0, 0),
            exit=(4, 4),
            seed="abc",  # invalid
            perfect=True,
            algorithm="dfs"
        )


# -------------------------
# EXTREME SIZE LIMIT (if you enforce it)
# -------------------------

def test_excessive_size():
    with pytest.raises(MazeError):
        MazeGenerator(
            width=5000,
            height=5000,
            entry=(0, 0),
            exit=(4999, 4999),
            seed=42,
            perfect=True,
            algorithm="dfs"
        )
