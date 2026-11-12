import pytest

import structures
from search import Searcher, search


def make_searcher(limit=10):
    documents = {1: "a.pdf", 2: "b.pdf", 3: "c.pdf"}
    inverted_index = {
        "python": {1: 2, 2: 1},
        "search": {1: 1, 3: 5},
    }
    doc_lengths = {1: 10, 2: 10, 3: 10}
    return Searcher(documents, inverted_index, doc_lengths, limit)


def test_ranks_by_tf_idf():
    results = make_searcher().search("python")

    assert [result["id"] for result in results] == [1, 2]


def test_query_is_case_insensitive():
    searcher = make_searcher()

    assert searcher.search("PYTHON") == searcher.search("python")


def test_sums_scores_for_multiple_words():
    results = make_searcher().search("python search")

    assert [result["id"] for result in results] == [3, 1, 2]


def test_returns_at_most_limit():
    documents = {doc_id: f"{doc_id}.pdf" for doc_id in range(1, 13)}
    inverted_index = {"python": {doc_id: 1 for doc_id in documents}}
    doc_lengths = {doc_id: 10 for doc_id in documents}

    results = Searcher(documents, inverted_index, doc_lengths).search("python")

    assert len(results) == 10


def test_unknown_word_returns_nothing():
    assert make_searcher().search("banana") == []


def test_global_search_uses_structures():
    structures.documents.clear()
    structures.documents.update({1: "a.pdf"})
    structures.inverted_index.clear()
    structures.inverted_index.update({"python": {1: 1}})
    structures.doc_lengths.clear()
    structures.doc_lengths.update({1: 1})

    assert search("python") == [{"id": 1, "path": "a.pdf"}]
