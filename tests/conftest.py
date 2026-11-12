import pytest

import storage
import structures
from index_storage import FileIndexStorage


@pytest.fixture(autouse=True)
def reset_global_state():
    """Сбрасывает глобальные словари, чтобы тесты не зависели от порядка."""
    structures.documents.clear()
    structures.inverted_index.clear()
    structures.doc_lengths.clear()
    storage.current = FileIndexStorage()
    storage.STATUS.update(mode="file", fallback=False, reason=None)
    yield
