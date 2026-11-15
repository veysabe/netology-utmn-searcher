import re
from pathlib import Path

import pypdf

import storage
import structures

WORD_RE = re.compile(r"\w+")


class Indexer:
    """Строит обратный индекс по документам, используя кэш частот."""

    def __init__(self, documents, storage):
        self.documents = documents
        self.storage = storage

    def count_words(self, path):
        counts = {}
        reader = pypdf.PdfReader(path)
        for page in reader.pages:
            text = (page.extract_text() or "").lower()
            for word in WORD_RE.findall(text):
                counts[word] = counts.get(word, 0) + 1
        return counts

    def build(self):
        cache = self.storage.load_cache()
        inverted_index = {}
        doc_lengths = {}

        for doc_id, path in self.documents.items():
            mtime = Path(path).stat().st_mtime
            if path in cache and cache[path]["mtime"] == mtime:
                counts = cache[path]["words"]
            else:
                try:
                    counts = self.count_words(path)
                except Exception as e:
                    print(f"Не удалось проиндексировать {path}: {e}")
                    continue
                cache[path] = {"mtime": mtime, "words": counts}

            doc_lengths[doc_id] = sum(counts.values())
            for word, count in counts.items():
                inverted_index.setdefault(word, {})[doc_id] = count

        cache = {path: cache[path] for path in self.documents.values() if path in cache}
        self.storage.save_cache(cache)
        self.storage.save_index(self.documents, inverted_index, doc_lengths)
        return inverted_index, doc_lengths


def index():
    """Строит индекс и кладёт его в глобальные словари."""
    saved = storage.current.load_index(structures.documents)
    if saved is None:
        inverted_index, doc_lengths = Indexer(structures.documents, storage.current).build()
    else:
        inverted_index, doc_lengths = saved

    structures.inverted_index.clear()
    structures.inverted_index.update(inverted_index)
    structures.doc_lengths.clear()
    structures.doc_lengths.update(doc_lengths)
