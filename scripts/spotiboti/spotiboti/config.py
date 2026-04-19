import json
import os
from pathlib import Path

def get_config_dir() -> Path:
    config_dir = Path.home() / ".config" / "spotiboti"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_config() -> dict:
    config_file = get_config_dir() / "config.json"
    if not config_file.exists():
        return {}
    with open(config_file, "r") as f:
        return json.load(f)

def save_config(config: dict) -> None:
    config_file = get_config_dir() / "config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

def get_catalog_cache_path() -> str:
    return str(get_config_dir() / "catalog_token_cache")

def get_library_cache_path() -> str:
    return str(get_config_dir() / "library_token_cache")

def get_market() -> str | None:
    config = load_config()
    return config.get("market")

DEFAULT_REDIRECT_URI = "http://127.0.0.1:9100"
