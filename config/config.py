from dataclasses import dataclass

import yaml


@dataclass
class AppConfig:
    search_paths: list[str]
    storage: str = "file"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "pdf_search"


# Метод инита конфига
def load_config(path: str) -> AppConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if "search_paths" not in raw or not raw["search_paths"]:
        raise ValueError("config.yml: 'search_paths' обязателен")

    storage = raw.get("storage", "file")
    if storage not in ("file", "mongodb"):
        raise ValueError("config.yml: 'storage' может быть 'file' или 'mongodb'")

    return AppConfig(
        search_paths=raw["search_paths"],
        storage=storage,
        mongo_uri=raw.get("mongo_uri", "mongodb://localhost:27017"),
        mongo_db=raw.get("mongo_db", "pdf_search"),
    )
