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
    val = value.lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    raise SystemExit(f"{name} must be true/false")


def parse_algo(value: str, name: str) -> str:
    val = value.lower()
    if val == "dfs" or val == "prim":
        return val
    else:
        raise SystemExit(f"{name} must be dfs or prim")


def read_config(filename: str) -> dict[str, Any]:
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
                raw[key.strip()] = value.strip()
    except FileNotFoundError:
        raise SystemExit("Error: Config file not found")

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT", "SEED", "ALGORITHM"]
    for key in required:
        if key not in raw:
            raise SystemExit(f"Missing required config: {key}")

    width = parse_int(raw["WIDTH"], "WIDTH")
    height = parse_int(raw["HEIGHT"], "HEIGHT")
    entry = parse_tuple(raw["ENTRY"], "ENTRY")
    exit = parse_tuple(raw["EXIT"], "EXIT")
    seed = parse_int(raw["SEED"], "SEED")
    perfect = parse_bool(raw["PERFECT"], "PERFECT")
    algorithm = parse_algo(raw["ALGORITHM"], "ALGORITHM")
    output_file = raw["OUTPUT_FILE"]

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
