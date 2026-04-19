import sys
from MazeGenerator import MazeGenerator
from render import render_box
from a_maze_ing import read_config, write_output

def generate_maze() -> str:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        config = read_config(sys.argv[1])
        maze = MazeGenerator(config["WIDTH"],
                             config["HEIGHT"],
                             config["ENTRY"],
                             config["EXIT"],
                             config["SEED"])
        maze.generate()

        # need to add this method in MazeGenerator
        # if not config["PERFECT"]:
        #     maze.add_loops()

        write_output(
            config["OUTPUT_FILE"],
            maze,
            config["ENTRY"],
            config["EXIT"]
        )

    except Exception as e:
        print(f"Error: {e}")

    print(config["OUTPUT_FILE"])
    return config["OUTPUT_FILE"]


# ANSI escape sequences for color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"


def main() -> None:
    colors = [RED, GREEN, YELLOW, BLUE]
    color_index = 0

    output = generate_maze()
    render_box(output)
    while True:
        print("=== A-Maze-ing ===")
        print("1. Regenerate new maze")
        print("2. Show/hide path from entry to exit")
        print("3. Rotate maze colours")
        print("4. Quit")
        choice = input("Choice? (1-4): ")
        if choice == "1":
            import random

            rand_seed = random.randint(1, 1000)
            print(rand_seed)

            config = read_config("config.txt")
            maze = MazeGenerator(config["WIDTH"],
                                 config["HEIGHT"],
                                 config["ENTRY"],
                                 config["EXIT"],
                                 rand_seed)
            maze.generate()

            write_output(
            config["OUTPUT_FILE"],
            maze,
            config["ENTRY"],
            config["EXIT"]
            )

            render_box(output)

            # TODO: Tidy up

            pass
        if choice == "2":
            print("TODO: implement pathfindig")
            # TODO: Implement pathfinding
            pass
        if choice == "3":
            render_box(output, colors[color_index])
            color_index = (color_index + 1) % len(colors)
        if choice == "4":
            break

if __name__ == "__main__":
    main()
