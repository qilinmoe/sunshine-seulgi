import os, tomllib
from pathlib import Path

def _set_envs(mapping: dict):
    """If env exists, don't change it; Otherwise put the value in."""
    for key, value in mapping.items():
        os.environ.setdefault(key, value)
    return

def _flatten_dict(d: dict, parent_key="") -> dict:
    """Flatten a dict for usage with _set_envs()."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else str(k)
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key).items())
        elif isinstance(v, list):
            items.append((new_key, ",".join(str(i) for i in v)))
        else:
            items.append((new_key, str(v)))
    return dict(items)

def init_config():
    """Set env variables from config.toml; Only if they don't already exist."""
    file_path = Path(__file__).parent
    config_path = file_path.parent / "config.toml"
    with open(config_path, "rb") as cf:
        result = tomllib.load(cf)
    _set_envs(_flatten_dict(result))
    return
