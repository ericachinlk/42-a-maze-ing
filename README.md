*This project has been created as part of the 42 curriculum by lchin, nichoo.*

---

# Maze Generator (mazegen)

## Description

This project is a configurable maze generation system written in Python.  
It generates 2D mazes using classical algorithms and provides tools to export, render, and solve them.

The system is split into two main components:

- **Core generation engine (MazeGenerator)**  
  Handles maze creation, algorithms, and path solving.

- **Rendering system (AppRenderer)**  
  Handles visual display and animation of maze generation.

The goal of this project is to design a reusable maze generation module that can be imported and reused in future projects, independent of any UI or rendering system.

---

## Maze Representation

The maze is stored as a 2D grid:
```
self.grid[y][x] → integer (bitmask)
```

Each cell uses 4-bit encoding for walls:

- N = 1  
- E = 2  
- S = 4  
- W = 8  

Example:
- 15 → all walls closed (1111)
- 0 → all walls open (0000)

---

## Algorithm Used

We implemented two generation algorithms:

### 1. Depth-First Search (DFS) — primary algorithm
- Randomized recursive backtracking
- Produces long winding corridors
- Ensures full coverage of the grid

### 2. Prim’s Algorithm (alternative mode)
- Expands maze from a frontier set
- Produces more evenly distributed structure

### Why DFS was chosen as default
DFS was chosen because:
- It is simpler to implement and debug
- It produces visually interesting “long path” mazes
- It works well with recursive structure and pattern constraints

---

## Features

- Configurable maze size
- Seed-based reproducibility
- Perfect / non-perfect maze modes
- Optional loop generation
- Embedded pattern constraint system ("42 pattern")
- BFS shortest path solver
- Hex export format
- Rendering hooks (pluggable UI system)

---

## Configuration File Format

Example `config.txt`:
```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=9,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=dfs
```

### Fields:

- WIDTH / HEIGHT → maze size
- ENTRY / EXIT → coordinates (x,y)
- OUTPUT_FILE → output file name
- PERFECT → whether maze contains loops
- SEED → randomness seed
- ALGORITHM → dfs | prim

---

## Instructions

### 1. Setup environment

```bash
make install
```

### 2. Run program

```bash
make run
```

### 3. Debug mode

```bash
make debug
```

### 4. Build package (for reuse)

```bash
make dev-tools
make build
```

### 5. Generated files

```
dist/
  mazegen-1.0.0-py3-none-any.whl
  mazegen-1.0.0.tar.gz
```

---

## Reusability

The core reusable module is:
```
mazegen/maze_generator.py
```

It can be imported independently:
```
from mazegen import MazeGenerator

maze = MazeGenerator(width=20, height=10, ...)
maze.generate()
print(maze.grid)
print(maze.find_shortest_path())
```

### Reusable components:

* MazeGenerator (core logic)
* BFS path solver
* Grid representation (bitmask system)
* Hex export (to_hex())

Rendering system is fully separated and optional.

---

## Team Roles

### lchin:

* Implemented maze generation algorithms (DFS, Prim)
* Implemented BFS shortest path solver
* Designed grid representation system
* Added pattern constraint system

### nichoo:

* Implemented rendering system (terminal display)
* Added animation / visual updates
* Managed pre-render and display pipeline
* Integrated UI with generation engine

---

## Planning & Development

### Initial plan

* Start with DFS generator
* Add rendering layer
* Add configuration system

### Evolution

* Added Prim algorithm as extension
* Introduced pattern-based constraints (“42 pattern”)
* Separated rendering from core logic for modularity

### What worked well

* Clear separation between logic and UI
* Seed-based reproducibility
* Modular architecture (easy to test generator alone)

### What could be improved

* Better abstraction for rendering callbacks
* More unit tests for edge cases
* Cleaner separation of configuration parsing

---

## Tools Used

* Python 3.10+
* Makefile automation
* mypy (type checking)
* flake8 (linting)
* build (packaging tool)
* Git for version control

---

## AI Usage

### AI was used for:

* Debugging type-checking issues (mypy errors)
* Improving docstring formatting (Google style)
* Packaging structure guidance (pyproject.toml design)
* Clarifying Python module behavior (-m, build system)

All core algorithms and project architecture were designed and implemented by the team.

---

## Resources

* Wikipedia: https://en.wikipedia.org/wiki/Maze_generation_algorithm
* Visual rundown on maze generation algorithms: https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap
* Helpful video series on implementing a DFS maze generator: https://www.youtube.com/watch?v=HyK_Q5rrcr4&list=WL&index=29
* Packaging: https://packaging.python.org/en/latest/
* Python official documentation: https://docs.python.org/3/
