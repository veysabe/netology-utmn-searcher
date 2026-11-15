from document_reader import DocumentReader
from index import Indexer


class MemoryStorage:
    """Хранилище в памяти для тестов."""

    def __init__(self, cache=None):
        self.cache = cache or {}
        self.saved_index = None

    def load_cache(self):
        return self.cache

    def save_cache(self, data):
        self.cache = data

    def save_index(self, documents, inverted_index, doc_lengths):
        self.saved_index = (documents, inverted_index, doc_lengths)


def test_reader_resolves_relative_path_from_given_root(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "a.pdf").touch()

    found = DocumentReader(root_path=tmp_path).load(["docs"])

    assert found == {1: str(folder / "a.pdf")}


def test_indexer_takes_words_from_cache_without_parsing_pdf(tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"not a real pdf")
    cache = {str(pdf): {"mtime": pdf.stat().st_mtime, "words": {"python": 2}}}
    storage = MemoryStorage(cache)
    documents = {1: str(pdf)}

    inverted_index, doc_lengths = Indexer(documents, storage).build()

    assert inverted_index == {"python": {1: 2}}
    assert doc_lengths == {1: 2}
    assert storage.saved_index == (documents, inverted_index, doc_lengths)


def test_indexer_drops_cache_entries_for_missing_files(tmp_path):
    present = tmp_path / "present.pdf"
    present.touch()
    cache = {
        str(present): {"mtime": present.stat().st_mtime, "words": {}},
        str(tmp_path / "deleted.pdf"): {"mtime": 1.0, "words": {"old": 1}},
    }
    storage = MemoryStorage(cache)

    Indexer({1: str(present)}, storage).build()

    assert list(storage.cache) == [str(present)]
