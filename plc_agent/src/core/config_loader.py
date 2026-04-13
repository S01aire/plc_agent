from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from models import Config
from settings import EnvSettings


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a dict at top level: {path}")
    return data

@lru_cache
def get_settings() -> EnvSettings:
    env_settings = EnvSettings()
    return env_settings

@lru_cache
def get_config() -> Config:
    config_dir = Path(__file__).parent.parent / "config"
    yaml_config = load_yaml_file(config_dir / "config.yaml")

    return Config(**yaml_config)


if __name__ == "__main__":
    config = get_config()
    print(config.llm.model)