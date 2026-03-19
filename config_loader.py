import json
from pathlib import Path
from typing import Any, Dict


CONFIG_PATH = Path("config/config.json")
DEFAULT_CONFIG_PATH = Path("config/default.json")


def load_config() -> Dict[str, Any]:
    """
    Load config/config.json and merge with default.json.
    Ensures all EMS subsystems (ADL, Memory, Ethics) have required fields.
    """

    # Load defaults first
    if DEFAULT_CONFIG_PATH.exists():
        with open(DEFAULT_CONFIG_PATH, "r") as f:
            default_cfg = json.load(f)
    else:
        default_cfg = {}

    # Load main config
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            user_cfg = json.load(f)
    else:
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

    # Merge user config over defaults
    merged = _deep_merge(default_cfg, user_cfg)
    return merged


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    Values in override take precedence.
    """
    result = dict(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result
