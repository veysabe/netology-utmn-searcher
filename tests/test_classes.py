from pathlib import Path

from document_reader import DocumentReader
from index import Indexer
from search import Searcher


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


def make_searcher():
    documents = {1: "a.pdf", 2: "b.pdf", 3: "c.pdf"}
    inverted_index = {
        "python": {1: 2, 2: 1},
        "search": {1: 1, 3: 5},
    }
    doc_lengths = {1: 10, 2: 10, 3: 10}
    return Searcher(documents, inverted_index, doc_lengths)


def test_searcher_ranks_by_tf_idf():
    results = make_searcher().search("python")

    assert [result["id"] for result in results] == [1, 2]


def test_searcher_ignores_case():
    searcher = make_searcher()

    assert searcher.search("PYTHON") == searcher.search("python")


def test_searcher_returns_at_most_ten_results():
    documents = {doc_id: f"{doc_id}.pdf" for doc_id in range(1, 13)}
    inverted_index = {"python": {doc_id: 1 for doc_id in documents}}
    doc_lengths = {doc_id: 10 for doc_id in documents}
    searcher = Searcher(documents, inverted_index, doc_lengths)

    assert len(searcher.search("python")) == 10


def test_searcher_skips_unknown_word():
    assert make_searcher().search("banana") == []
