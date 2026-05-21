*This project has been created as part of the 42 curriculum by lchin, nichoo.*

---

# Maze Generator (mazegen)

## Description

This project is a **configurable maze generation system written in Python**.  
It generates 2D mazes using classical algorithms and provides tools to **render, export, and solve** them.

The system is designed with a **clear separation between core logic and application layer**, making the maze engine reusable in other projects.

---

## Architecture Overview
```
root/
├── a_maze_ing.py        # CLI entry point
├── pyproject.toml       # Packaging configuration
├── Makefile             # Automation commands
├── mazegen/             # Reusable library
│   ├── maze_generator.py
│   ├── renderer.py
│   └── __init__.py
└── app/                 # Application layer
    ├── config.py
    ├── generate_maze.py
    └── __init__.py
```

---

## Core Components

### mazegen (Reusable Library)

- **MazeGenerator**
  - DFS & Prim maze generation
  - Pattern constraints ("42 pattern")
  - Loop control (perfect / non-perfect)
  - BFS shortest path solver
  - Hex export

- **CLIRenderer**
  - Terminal rendering
  - Animation support
  - Theme switching (day/night)
  - Wall color rotation

---

### app (Application Layer)

- **config.py**
  - Config parsing and validation

- **generate_maze.py**
  - Orchestration between config, generator, and renderer

---

### CLI

- **a_maze_ing.py**
  - Interactive interface
  - Runtime controls (toggle path, theme, algorithm, etc.)

---

## Maze Representation

Each cell encodes walls using 4 bits:

- N = 1  
- E = 2  
- S = 4  
- W = 8  

### Examples

- `15`: all walls closed (`1111`)
- `0`: all walls open (`0000`)

---

## Algorithms

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
- DFS & Prim algorithms
- Perfect / non-perfect maze modes
- Loop generation
- Embedded **"42" pattern constraint**
- BFS shortest path solver
- Hex export format
- CLI rendering with:
  - Animation
  - Day/night themes
  - Wall color rotation

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

### Fields

| Key            | Description        |
|----------------|--------------------|
| WIDTH / HEIGHT | Maze dimensions    |
| ENTRY / EXIT   | Coordinates `(x,y)`|
| OUTPUT_FILE    | Output file (.txt) |
| PERFECT        | True = no loops    |
| SEED           | Random seed        |
| ALGORITHM      | `dfs` or `prim`    |

---

## Makefile Usage

The project uses a `Makefile` to simplify development and execution.

### Quick Start
```bash
make install
make run
```

---

## Instructions

### 1. Setup environment
```bash
make install
```
- Creates virtual environment (`venv/`)
- Installs `flake8` and `mypy`

---

### 2. Run program
```bash
make run
```
- Runs program with `config.txt`

---

### 3. Debug mode
```bash
make debug
```
- Runs with debug mode (`DEBUG=1`)
- Displays internal maze data

---

### 4. Build package (for reuse)
```bash
make dev-tools
```
- Installs `build` package

```bash
make build
```
Creates:
```
dist/
  mazegen-1.0.0-py3-none-any.whl
  mazegen-1.0.0.tar.gz
```

---

### 5. Code Quality
```bash
make lint
```
- Runs flake8 + mypy (moderate strictness)

```bash
make lint-strict
```
- Runs stricter type checking

---

### 6. Cleanup
```bash
make clean
```
- Removes cache files

```bash
make uninstall
```
- Deletes virtual environment

---

## CLI Features

Interactive menu allows:

- Regenerate maze (new seed)
- Toggle shortest path
- Change wall colors
- Toggle day/night mode
- Switch algorithm (DFS and Prim)
- Toggle perfect/non-perfect maze
- View configuration

---

## Output Format

Generated `.txt` file:
```
<hex grid>

entry_x,entry_y
exit_x,exit_y
<path>
```

---

## Reusability

You can use the core generator independently:

```python
from mazegen import MazeGenerator

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

print(maze.grid)
print(maze.find_shortest_path())
```

CLI rendering is optional and can be plugged in when needed:

```python
from mazegen import MazeGenerator, CLIRenderer

maze = MazeGenerator(
    width=20,
    height=10,
    entry=(0, 0),
    exit=(19, 9),
    seed=42,
    perfect=True,
    algorithm="dfs"
)

renderer = CLIRenderer(maze.get_maze_info())
maze.generate(renderer=renderer)

print(maze.grid)
print(maze.find_shortest_path())
```

### Reusable components:

* MazeGenerator (core logic)
* BFS path solver
* Grid representation (bitmask system)
* Hex export (to_hex())
* Output report generation
* Pluggable renderer system

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

* Seed-based reproducibility
* Modular structure
* Clean separation of concerns
* Reusable core logic

### What could be improved

* Support more algorithm
* Allow randomized maze sizes
* Add more edge-case tests
* Further refine configuration handling
* Refine 3×3 open-space validation to better support imperfect maze representations

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
* Google-style docstring: https://google.github.io/styleguide/pyguide.html
