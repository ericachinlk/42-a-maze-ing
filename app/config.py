from typing import Any


class ConfigError(Exception):
    pass


def parse_int(value: str, name: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ConfigError(f"{name} must be an integer")


def parse_tuple(value: str, name: str) -> tuple[int, int]:
    try:
        x, y = map(int, value.split(","))
        return x, y
    except (TypeError, ValueError):
        raise ConfigError(f"{name} must be in format 'x,y'")


def parse_bool(value: str, name: str) -> bool:
    if not value:
        return True
    val = value.lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    raise ConfigError(f"{name} must be true/false")


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
        raise ConfigError(f"{name} must be dfs or prim")


def parse_output(value: str, name: str) -> str:
    if not value.endswith(".txt"):
        raise ConfigError(f"{name} must be a txt file")
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
                    raise ConfigError(f"Invalid line (missing '=') - {line}")
                key, value = line.split("=", 1)
                raw[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        raise ConfigError(f"Config file {filename} not found")

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT"]
    for key in required:
        if key not in raw:
            raise ConfigError(f"Missing required config - {key}")
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
        raise ConfigError("WIDTH and HEIGHT must be positive")

    if entry == exit:
        raise ConfigError("ENTRY and EXIT cannot be the same")

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError("ENTRY is out of bounds")

    if not (0 <= exit[0] < width and 0 <= exit[1] < height):
        raise ConfigError("EXIT is out of bounds")

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
    print("\n=== Current Configurations ===")
    for k, v in config.items():
        print(f"* {k}: {v}")
    print()


def set_config(filename: str, current_algorithm: str, toggle_algorithm: str) -> None:
    raw = file_validator(filename)
    if "ALGORITHM" in raw.keys():
            with open(filename, "r") as f:
                lines = f.readlines()
            found = False
            for i, line in enumerate(lines):
                if line.startswith("ALGORITHM="):
                    value = line.split("=", 1)[1]
                    if (
                        value.strip().lower() == current_algorithm.lower()
                        or value.strip() == ""
                    ):
                        lines[i] = f"ALGORITHM={toggle_algorithm}\n"
                        found = True
                        break
            if found:
                with open(filename, "w") as f:
                    f.writelines(lines)
    else:
        with open(filename, "a") as f:
            f.write(f"\nALGORITHM={toggle_algorithm}")

