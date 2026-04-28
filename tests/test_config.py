import pytest
from app.config import (
    read_config,
    file_validator,
    parse_int,
    parse_tuple,
    parse_bool,
    parse_seed,
    parse_algo,
    parse_output,
    ConfigError,
)


# -------------------------
# Helper to create temp files
# -------------------------
def write_config(tmp_path, content: str):
    file = tmp_path / "config.txt"
    file.write_text(content)
    return str(file)


# -------------------------
# VALID CONFIG TEST
# -------------------------
def test_valid_config(tmp_path):
    config_file = write_config(tmp_path, """
    WIDTH=10
    HEIGHT=5
    ENTRY=0,0
    EXIT=9,4
    OUTPUT_FILE=maze.txt
    PERFECT=true
    SEED=42
    ALGORITHM=dfs
    """)

    config = read_config(config_file)

    assert config["WIDTH"] == 10
    assert config["HEIGHT"] == 5
    assert config["ENTRY"] == (0, 0)
    assert config["EXIT"] == (9, 4)
    assert config["OUTPUT_FILE"] == "maze.txt"
    assert config["PERFECT"] is True
    assert config["SEED"] == 42
    assert config["ALGORITHM"] == "dfs"


# -------------------------
# MISSING REQUIRED FIELD
# -------------------------
def test_missing_required(tmp_path):
    config_file = write_config(tmp_path, """
    WIDTH=10
    HEIGHT=5
    ENTRY=0,0
    OUTPUT_FILE=maze.txt
    PERFECT=true
    """)

    with pytest.raises(ConfigError):
        read_config(config_file)


# -------------------------
# DUPLICATE KEYS
# -------------------------
def test_duplicate_keys(tmp_path):
    config_file = write_config(tmp_path, """
    WIDTH=10
    WIDTH=20
    HEIGHT=5
    ENTRY=0,0
    EXIT=9,4
    OUTPUT_FILE=maze.txt
    PERFECT=true
    """)

    with pytest.raises(ConfigError):
        file_validator(config_file)


# -------------------------
# UNKNOWN KEY
# -------------------------
def test_unknown_key(tmp_path):
    config_file = write_config(tmp_path, """
    WIDTH=10
    HEIGHT=5
    ENTRY=0,0
    EXIT=9,4
    OUTPUT_FILE=maze.txt
    PERFECT=true
    RANDOM=123
    """)

    with pytest.raises(ConfigError):
        file_validator(config_file)


# -------------------------
# INVALID INT
# -------------------------
def test_invalid_int():
    with pytest.raises(ConfigError):
        parse_int("abc", "WIDTH")


# -------------------------
# INVALID TUPLE FORMAT
# -------------------------
def test_invalid_tuple_format():
    with pytest.raises(ConfigError):
        parse_tuple("1,2,3", "ENTRY")


def test_invalid_tuple_non_int():
    with pytest.raises(ConfigError):
        parse_tuple("1,a", "ENTRY")


# -------------------------
# INVALID BOOL
# -------------------------
def test_invalid_bool():
    with pytest.raises(ConfigError):
        parse_bool("maybe", "PERFECT")


# -------------------------
# BOOLEAN VARIANTS
# -------------------------
@pytest.mark.parametrize("val,expected", [
    ("true", True),
    ("false", False),
    ("1", True),
    ("0", False),
    ("yes", True),
    ("no", False),
])
def test_parse_bool_variants(val, expected):
    assert parse_bool(val, "PERFECT") == expected


# -------------------------
# SEED PARSING
# -------------------------
def test_parse_seed_none():
    assert parse_seed(None, "SEED") is None
    assert parse_seed("", "SEED") is None


def test_parse_seed_valid():
    assert parse_seed("123", "SEED") == 123


# -------------------------
# ALGORITHM PARSING
# -------------------------
def test_parse_algo_default():
    assert parse_algo(None, "ALGORITHM") == "dfs"


def test_parse_algo_valid():
    assert parse_algo("prim", "ALGORITHM") == "prim"


def test_parse_algo_invalid():
    with pytest.raises(ConfigError):
        parse_algo("random", "ALGORITHM")


# -------------------------
# OUTPUT FILE VALIDATION
# -------------------------
def test_parse_output_valid():
    assert parse_output("maze.txt", "OUTPUT_FILE") == "maze.txt"


def test_parse_output_invalid():
    with pytest.raises(ConfigError):
        parse_output("maze.csv", "OUTPUT_FILE")


# -------------------------
# FILE NOT FOUND
# -------------------------
def test_file_not_found():
    with pytest.raises(ConfigError):
        file_validator("non_existent.txt")


# -------------------------
# INVALID LINE FORMAT
# -------------------------
def test_invalid_line_format(tmp_path):
    config_file = write_config(tmp_path, """
    WIDTH 10
    HEIGHT=5
    ENTRY=0,0
    EXIT=9,4
    OUTPUT_FILE=maze.txt
    PERFECT=true
    """)

    with pytest.raises(ConfigError):
        file_validator(config_file)
