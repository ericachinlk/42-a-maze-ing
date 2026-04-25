from typing import Any


def parse_int(value: str, name: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"{name} must be an integer")


def parse_tuple(value: str, name: str) -> tuple[int, int]:
    try:
        x, y = map(int, value.split(","))
        return x, y
    except Exception:
        raise SystemExit(f"{name} must be in format 'x,y'")


def parse_bool(value: str, name: str) -> bool:
    if not value:
        return True
    val = value.lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    raise SystemExit(f"{name} must be true/false")


def parse_seed(value: Any, name: str) -> Any:
    if not value:
        return value
    else:
        return parse_int(value, name)


def parse_algo(value: Any, name: str) -> str:
    if not value:
        return "dfs"
    val = value.lower()
    if val == "dfs" or val == "prim":
        return val
    else:
        raise SystemExit(f"{name} must be dfs or prim")


def parse_output(value: str, name: str) -> str:
    if not value.endswith(".txt"):
        raise SystemExit(f"{name} must be a txt file")
    else:
        return value


def file_validator(filename: str) -> dict[str, str]:
    raw: dict[str, str] = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise SystemExit(f"Invalid line (missing '='): {line}")
                key, value = line.split("=", 1)
                raw[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        raise SystemExit("Error: Config file not found")

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT"]
    for key in required:
        if key not in raw:
            raise SystemExit(f"Missing required config: {key}")
    return raw


def read_config(filename: str) -> dict[str, Any]:
    raw = file_validator(filename)

    width = parse_int(raw["WIDTH"], "WIDTH")
    height = parse_int(raw["HEIGHT"], "HEIGHT")
    entry = parse_tuple(raw["ENTRY"], "ENTRY")
    exit = parse_tuple(raw["EXIT"], "EXIT")
    perfect = parse_bool(raw["PERFECT"], "PERFECT")
    seed = parse_seed(raw.get("SEED"), "SEED")
    algorithm = parse_algo(raw.get("ALGORITHM"), "ALGORITHM")
    output_file = parse_output(raw["OUTPUT_FILE"], "OUTPUT FILE")

    # validation for valid maze
    if width <= 0 or height <= 0:
        raise SystemExit("WIDTH and HEIGHT must be positive")

    if entry == exit:
        raise SystemExit("ENTRY and EXIT cannot be the same")

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise SystemExit("ENTRY is out of bounds")

    if not (0 <= exit[0] < width and 0 <= exit[1] < height):
        raise SystemExit("EXIT is out of bounds")

    return {
        "WIDTH": width,
        "HEIGHT": height,
        "ENTRY": entry,
        "EXIT": exit,
        "OUTPUT_FILE": output_file,
        "PERFECT": perfect,
        "SEED": seed,
        "ALGORITHM": algorithm
    }


def show_config(filename: str):
    config = read_config(filename)
    print("\n=== CONFIG ===")
    for k, v in config.items():
        print(f"{k}: {v}")


def set_config(filename: str, key: str, value: str):
    raw = file_validator(filename)
    key = key.upper()
    if key in raw.keys():
        lines = []
        with open(filename, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == key:
                        lines.append(f"{key}={value}\n")
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

        with open(filename, "w") as f:
            f.writelines(lines)
        print(f"{key} updated to {value}")
    else:
        print(f"{key} is not found.")


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if not args:
        print("Commands:")
        print("  show")
        print("  set KEY VALUE")
        sys.exit(1)

    command = args[0]
    config_file = "../config.txt"

    if command == "show":
        show_config(config_file)
    elif command == "set":
        if len(args) != 3:
            print("Usage: set KEY VALUE")
            sys.exit(1)
        key = args[1]
        value = args[2]
        set_config(config_file, key, value)
        show_config(config_file)
    else:
        print("Unknown command:", command)
