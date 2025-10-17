"""Конфигурация"""

from typing import Any
from yaml import safe_load

def load_yaml_config(config_path: str) -> dict[str, Any]:
    """Загружает конфиг из YAML

    Args:
        config_path: путь до конфига.

    Returns:
        словарь с конфигурацией.
    """
    try:
        with open(
            config_path,
            "r", encoding="utf-8"
        ) as f:
            config = safe_load(f)

        return config
    except FileNotFoundError as err:
        raise RuntimeError(f"Файл конфигурации {config_path} не найден") \
            from err

prompts = load_yaml_config("config/prompts.yaml")["prompts"]
models_params = load_yaml_config("config/model_params.yaml")
