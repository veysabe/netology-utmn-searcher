import pytest

from config.config import load_config


def write_config(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_search_paths(tmp_path):
    path = write_config(tmp_path, "search_paths:\n  - demo_docs\n")

    config = load_config(path)

    assert config.search_paths == ["demo_docs"]
    assert config.storage == "file"
    assert config.mongo_uri == "mongodb://localhost:27017"


def test_loads_storage_settings(tmp_path):
    path = write_config(
        tmp_path,
        "search_paths:\n  - docs\nstorage: mongodb\n"
        "mongo_uri: mongodb://db:27017\nmongo_db: test_db\n",
    )

    config = load_config(path)

    assert config.storage == "mongodb"
    assert config.mongo_uri == "mongodb://db:27017"
    assert config.mongo_db == "test_db"


def test_rejects_missing_search_paths(tmp_path):
    path = write_config(tmp_path, "storage: file\n")

    with pytest.raises(ValueError):
        load_config(path)


def test_rejects_empty_search_paths(tmp_path):
    path = write_config(tmp_path, "search_paths: []\n")

    with pytest.raises(ValueError):
        load_config(path)


def test_rejects_unknown_storage(tmp_path):
    path = write_config(tmp_path, "search_paths:\n  - docs\nstorage: redis\n")

    with pytest.raises(ValueError):
        load_config(path)
