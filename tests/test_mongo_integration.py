"""Проверка хранилища на настоящей MongoDB.

Тест запускается только в CI, где поднят сервис-контейнер MongoDB:
локально без переменной MONGO_URI он пропускается.
"""

import os

import pytest

from storage import MongoIndexStorage

MONGO_URI = os.environ.get("MONGO_URI")

pytestmark = pytest.mark.skipif(not MONGO_URI, reason="нужна настоящая MongoDB (MONGO_URI)")


def make_storage():
    store = MongoIndexStorage(MONGO_URI, "pdf_search_ci")
    store.db.client.drop_database("pdf_search_ci")
    return store


def test_saves_and_reloads_index(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.touch()
    store = make_storage()
    store.save_cache({str(pdf): {"mtime": pdf.stat().st_mtime, "words": {"python": 1}}})

    store.save_index({1: str(pdf)}, {"python": {1: 1}}, {1: 1})

    assert store.load_index({1: str(pdf)}) == ({"python": {1: 1}}, {1: 1})
    assert store.db.postings.count_documents({}) == 1
    assert store.db.doc_lengths.count_documents({}) == 1
