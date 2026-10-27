import re

import structures
import pypdf

from pathlib import Path
import index_storage

WORD_RE = re.compile(r"\w+")

def index():
    cache = index_storage.load_cache()
    for doc_id, path in structures.documents.items():
        counts: dict[str, int] = {}
        mtime = Path(path).stat().st_mtime
        if path in cache and cache[path]["mtime"] == mtime:
            counts = cache[path]["words"]
        else:
            try:
                reader = pypdf.PdfReader(path)
                for page in reader.pages:
                    text = (page.extract_text() or "").lower()
                    for word in WORD_RE.findall(text):
                        counts[word] = counts.get(word, 0) + 1
            except Exception as e:
                print(f"Не удалось проиндексировать {path}: {e}")
                continue
            cache[path] = {"mtime": mtime, "words": counts}
        structures.doc_lengths[doc_id] = sum(counts.values())
        for word, count in counts.items():
            structures.inverted_index.setdefault(word, {})[doc_id] = count
    index_storage.save_cache(cache)
