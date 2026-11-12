from pathlib import Path

import mongomock

import index
import storage
import structures
from index import Indexer
from index_storage import FileIndexStorage
from storage import MongoIndexStorage

DEMO_PDF = Path(__file__).resolve().parent.parent / "demo_docs" / "01_python_basics.pdf"


class SavedIndexStorage:
    def __init__(self, saved):
        self.saved = saved

    def load_index(self, documents):
        return self.saved

    def load_cache(self):
        raise AssertionError("кэш не должен читаться, если индекс уже сохранён")


class EmptyStorage:
    def load_index(self, documents):
        return None

    def load_cache(self):
        return {}

    def save_cache(self, data):
        pass

    def save_index(self, documents, inverted_index, doc_lengths):
        pass


def test_index_uses_saved_index(monkeypatch):
    monkeypatch.setattr(storage, "current", SavedIndexStorage(({"python": {1: 1}}, {1: 1})))
    structures.documents.clear()
    structures.documents[1] = "/docs/a.pdf"

    index.index()

    assert structures.inverted_index == {"python": {1: 1}}
    assert structures.doc_lengths == {1: 1}


def test_index_builds_when_nothing_saved(monkeypatch):
    monkeypatch.setattr(storage, "current", EmptyStorage())
    structures.documents.clear()
    structures.documents[1] = str(DEMO_PDF)

    index.index()

    assert structures.inverted_index["python"] == {1: 3}
    assert structures.doc_lengths[1] > 0


def test_indexer_reads_text_from_pdf(tmp_path):
    store = FileIndexStorage(str(tmp_path / "cache.json"))

    inverted_index, doc_lengths = Indexer({1: str(DEMO_PDF)}, store).build()

    assert inverted_index["python"] == {1: 3}
    assert doc_lengths[1] > 0


def test_broken_pdf_is_skipped(tmp_path):
    broken = tmp_path / "broken.pdf"
    broken.write_bytes(b"not a pdf")
    store = MongoIndexStorage(client=mongomock.MongoClient(), db_name="test")

    inverted_index, doc_lengths = Indexer({1: str(broken)}, store).build()

    assert inverted_index == {}
    assert doc_lengths == {}


def test_pdf_without_text_is_indexed_as_empty(tmp_path):
    from pypdf import PdfWriter

    path = tmp_path / "empty.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with open(path, "wb") as f:
        writer.write(f)
    store = FileIndexStorage(str(tmp_path / "cache.json"))

    inverted_index, doc_lengths = Indexer({1: str(path)}, store).build()

    assert inverted_index == {}
    assert doc_lengths == {1: 0}


def test_file_storage_saves_and_loads_cache(tmp_path):
    store = FileIndexStorage(str(tmp_path / "cache.json"))
    cache = {"/docs/a.pdf": {"mtime": 1.0, "words": {"python": 1}}}

    store.save_cache(cache)

    assert store.load_cache() == cache
    assert store.load_index({}) is None


def test_file_storage_returns_empty_cache_on_error(tmp_path):
    store = FileIndexStorage(str(tmp_path / "missing.json"))

    assert store.load_cache() == {}
