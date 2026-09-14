import yaml
from dataclasses import dataclass

@dataclass
class AppConfig:
    search_paths: list[str]

# Метод инита конфига
def load_config(path: str) -> AppConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if "search_paths" not in raw or not raw["search_paths"]:
        raise ValueError("config.yml: 'search_paths' обязателен")

    return AppConfig(
        search_paths=raw["search_paths"],
    )