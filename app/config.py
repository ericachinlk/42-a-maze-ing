from typing import Any

"""
Configuration parsing and validation utilities.

Provides functions to read a config file, validate its structure,
and convert raw string values into typed Python values.
"""


class ConfigError(Exception):
    """
    Custom exception raised when configuration parsing fails.

    Used throughout the config system to signal invalid or missing
    configuration values.
    """
    pass


def parse_int(value: str, name: str) -> int:
    """
    Parse a string into an integer.

    Args:
        value (str): Value to parse.
        name (str): Field name used in error messages.

    Returns:
        int: Parsed integer.

    Raises:
        ConfigError: If the value is not a valid integer.
    """
    try:
        return int(value)
    except ValueError:
        raise ConfigError(f"{name} must be an integer")


def parse_tuple(value: str, name: str) -> tuple[int, int]:
    """
    Parse a string into an (x, y) integer tuple.

    Expected format: "x,y"

    Args:
        value (str): Input string.
        name (str): Field name used in error messages.

    Returns:
        tuple[int, int]: Parsed coordinate tuple.

    Raises:
        ConfigError: If format is invalid or values are not integers.
    """
    cleaned = value.replace(" ", "")
    parts = cleaned.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{name} must contain exactly two values")
    try:
        x, y = map(int, parts)
        return x, y
    except ValueError:
        raise ConfigError(f"{name} must be in format 'x,y'")


def parse_bool(value: str, name: str) -> bool:
    """
    Parse a boolean string.

    Accepted values: true/false, 1/0, yes/no (case-insensitive).

    Args:
        value (str): Input string.
        name (str): Field name used in error messages.

    Returns:
        bool: Parsed boolean value.

    Raises:
        ConfigError: If value is not a valid boolean.
    """
    if value is None or value == "":
        raise ConfigError(f"{name} must be true/false")
    val = value.strip().lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    raise ConfigError(f"{name} must be true/false")


def parse_seed(value: str | None, name: str) -> int | None:
    """
    Parse an optional integer seed value.

    Args:
        value (str): Seed string or None.
        name (str): Field name used in error messages.

    Returns:
        int | None: Parsed integer seed, or None if not provided.
    """
    if value is None or value == "":
        return None
    else:
        return parse_int(value, name)


def parse_algo(value: str | None, name: str) -> str:
    """
    Parse maze generation algorithm.

    Args:
        value (str): Algorithm name ("dfs" or "prim").
        name (str): Field name used in error messages.

    Returns:
        str: Normalized algorithm name.

    Raises:
        ConfigError: If algorithm is invalid.
    """
    if value is None or value == "":
        return "dfs"
    val = value.strip().lower()
    if val in ("dfs", "prim"):
        return val
    else:
        raise ConfigError(f"{name} must be dfs or prim")


def parse_output(value: str, name: str) -> str:
    """
    Validate output filename.

    Args:
        value (str): Output filename.
        name (str): Field name used in error messages.

    Returns:
        str: Validated filename.

    Raises:
        ConfigError: If filename does not end with .txt.
    """
    if not value.endswith(".txt"):
        raise ConfigError(f"{name} must be a txt file")
    return value


def file_validator(filename: str) -> dict[str, str]:
    """
    Validate and parse a configuration file.

    Performs:
        - Comment removal
        - Duplicate key detection
        - Required key validation
        - Unknown key detection

    Args:
        filename (str): Path to config file.

    Returns:
        dict[str, str]: Raw configuration key-value pairs.

    Raises:
        ConfigError: If file is invalid or missing required fields.
    """
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
                key_clean = key.strip().upper()
                if key_clean in raw:
                    raise ConfigError(f"Duplicate config key: {key_clean}")
                raw[key_clean] = value.strip()
    except FileNotFoundError:
        raise ConfigError(f"Config file {filename} not found")
    except OSError:
        raise ConfigError(f"Failed to read config file {filename}")

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT"]
    for key in required:
        if key not in raw:
            raise ConfigError(f"Missing required config - {key}")

    allowed = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
               "OUTPUT_FILE", "PERFECT", "SEED", "ALGORITHM"}
    for key in raw:
        if key not in allowed:
            raise ConfigError(f"Unknown config key: {key}")
    return raw


def read_config(filename: str) -> dict[str, Any]:
    """
    Parse configuration file into typed values.

    Args:
        filename (str): Path to config file.

    Returns:
        dict[str, Any]: Parsed configuration dictionary.
    """
    raw = file_validator(filename)

    width = parse_int(raw["WIDTH"], "WIDTH")
    height = parse_int(raw["HEIGHT"], "HEIGHT")
    entry = parse_tuple(raw["ENTRY"], "ENTRY")
    exit = parse_tuple(raw["EXIT"], "EXIT")
    perfect = parse_bool(raw["PERFECT"], "PERFECT")
    seed = parse_seed(raw.get("SEED"), "SEED")
    algorithm = parse_algo(raw.get("ALGORITHM"), "ALGORITHM")
    output_file = parse_output(raw["OUTPUT_FILE"], "OUTPUT FILE")

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


def set_algorithm(
        filename: str,
        current_algorithm: str,
        toggle_algorithm: str
) -> None:
    """
    Update maze generation algorithm in config file.

    Args:
        filename (str): Path to config file.
        current_algorithm (str): Current algorithm name.
        toggle_algorithm (str): New algorithm value.

    Raises:
        ConfigError: If file update fails.
    """
    raw = file_validator(filename)
    try:
        if "ALGORITHM" in raw.keys():
            with open(filename, "r") as f:
                lines = f.readlines()
            found = False
            for i, line in enumerate(lines):
                if line.strip().startswith("ALGORITHM="):
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
    except OSError:
        raise ConfigError("Failed to update ALGORITHM in config file")


def toggle_perfect(filename: str) -> None:
    """
    Toggle PERFECT flag in configuration file.

    Args:
        filename (str): Path to config file.

    Raises:
        ConfigError: If file update fails.
    """
    _ = file_validator(filename)
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("PERFECT="):
                value = line.split("=", 1)[1]
                if value.strip().lower() == "true":
                    lines[i] = "PERFECT=False\n"
                else:
                    lines[i] = "PERFECT=True\n"
                break
        with open(filename, "w") as f:
            f.writelines(lines)
    except OSError:
        raise ConfigError("Failed to update PERFECT in config file")
