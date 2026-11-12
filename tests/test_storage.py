import mongomock
import pymongo

import storage
from config.config import AppConfig
from index_storage import FileIndexStorage
from storage import MongoIndexStorage, create_storage


def make_storage():
    return MongoIndexStorage(client=mongomock.MongoClient(), db_name="test")


def test_saves_and_loads_word_cache():
    store = make_storage()
    cache = {"/docs/a.pdf": {"mtime": 1.0, "words": {"python": 2}}}

    store.save_cache(cache)

    assert store.load_cache() == cache


def test_saves_index_in_separate_collections():
    store = make_storage()

    store.save_index({1: "/docs/a.pdf"}, {"python": {1: 2}}, {1: 2})

    assert store.db.postings.count_documents({}) == 1
    assert store.db.doc_lengths.count_documents({}) == 1
    assert store.db.postings.find_one()["word"] == "python"


def test_loads_saved_index_when_files_did_not_change(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.touch()
    store = make_storage()
    store.save_cache({str(pdf): {"mtime": pdf.stat().st_mtime, "words": {"python": 1}}})
    store.save_index({1: str(pdf)}, {"python": {1: 1}}, {1: 1})

    assert store.load_index({1: str(pdf)}) == ({"python": {1: 1}}, {1: 1})


def test_does_not_load_index_when_file_changed(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.touch()
    store = make_storage()
    store.save_cache({str(pdf): {"mtime": 1.0, "words": {"python": 1}}})
    store.save_index({1: str(pdf)}, {"python": {1: 1}}, {1: 1})

    assert store.load_index({1: str(pdf)}) is None


def test_does_not_load_index_when_file_missing(tmp_path):
    store = make_storage()
    store.save_cache({str(tmp_path / "a.pdf"): {"mtime": 1.0, "words": {}}})
    store.save_index({1: str(tmp_path / "a.pdf")}, {}, {})

    assert store.load_index({1: str(tmp_path / "a.pdf")}) is None


def test_remaps_document_ids_after_order_change(tmp_path):
    first = tmp_path / "a.pdf"
    second = tmp_path / "b.pdf"
    first.touch()
    second.touch()
    store = make_storage()
    store.save_cache(
        {
            str(first): {"mtime": first.stat().st_mtime, "words": {"python": 1}},
            str(second): {"mtime": second.stat().st_mtime, "words": {"python": 1}},
        }
    )
    store.save_index(
        {1: str(first), 2: str(second)},
        {"python": {1: 3, 2: 7}},
        {1: 10, 2: 20},
    )

    inverted_index, doc_lengths = store.load_index({1: str(second), 2: str(first)})

    # Файл second теперь первый, файл first — второй.
    assert inverted_index == {"python": {1: 7, 2: 3}}
    assert doc_lengths == {1: 20, 2: 10}


class BrokenStorage:
    def __init__(self, uri, db_name):
        pass

    def check(self):
        raise RuntimeError("нет соединения")


class TimeoutStorage:
    def __init__(self, uri, db_name):
        pass

    def check(self):
        raise pymongo.errors.ServerSelectionTimeoutError("сервер не отвечает")


def test_falls_back_to_file_storage(monkeypatch):
    monkeypatch.setattr(storage, "MongoIndexStorage", BrokenStorage)
    config = AppConfig(search_paths=["docs"], storage="mongodb")

    result = create_storage(config)

    assert isinstance(result, FileIndexStorage)
    assert storage.STATUS["mode"] == "file"
    assert storage.STATUS["fallback"] is True
    assert storage.STATUS["reason"] == "нет соединения"


def test_falls_back_when_mongo_does_not_answer(monkeypatch):
    monkeypatch.setattr(storage, "MongoIndexStorage", TimeoutStorage)
    config = AppConfig(search_paths=["docs"], storage="mongodb")

    result = create_storage(config)

    assert isinstance(result, FileIndexStorage)
    assert storage.STATUS["fallback"] is True
    assert storage.STATUS["reason"] == "нет соединения с MongoDB"


def test_uses_mongo_storage_when_available(monkeypatch):
    def build(uri, db_name):
        return MongoIndexStorage(client=mongomock.MongoClient(), db_name="test")

    monkeypatch.setattr(storage, "MongoIndexStorage", build)
    config = AppConfig(search_paths=["docs"], storage="mongodb")

    result = create_storage(config)

    assert isinstance(result, MongoIndexStorage)
    assert storage.STATUS["mode"] == "mongodb"
    assert storage.STATUS["fallback"] is False


def test_uses_file_storage_from_config():
    config = AppConfig(search_paths=["docs"], storage="file")

    result = create_storage(config)

    assert isinstance(result, FileIndexStorage)
    assert storage.STATUS["mode"] == "file"
    assert storage.STATUS["fallback"] is False


def test_returns_none_when_database_is_empty():
    assert make_storage().load_index({}) is None


def test_returns_none_when_doc_id_is_missing(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.touch()
    store = make_storage()
    store.save_cache({str(pdf): {"mtime": pdf.stat().st_mtime, "words": {}}})

    assert store.load_index({1: str(pdf)}) is None


def test_returns_none_when_file_set_changed(tmp_path):
    first = tmp_path / "a.pdf"
    second = tmp_path / "b.pdf"
    first.touch()
    second.touch()
    store = make_storage()
    store.save_cache(
        {
            str(first): {"mtime": first.stat().st_mtime, "words": {}},
            str(second): {"mtime": second.stat().st_mtime, "words": {}},
        }
    )
    store.save_index({1: str(first), 2: str(second)}, {}, {})

    assert store.load_index({1: str(first)}) is None
