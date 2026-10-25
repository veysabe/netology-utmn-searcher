import re

import structures
import pypdf

WORD_RE = re.compile(r"\w+")

def index():
    for doc_id, path in structures.documents.items():
        counts: dict[str, int] = {}
        try:
            reader = pypdf.PdfReader(path)
            for page in reader.pages:
                text = (page.extract_text() or "").lower()
                for word in WORD_RE.findall(text):
                    counts[word] = counts.get(word, 0) + 1
        except Exception as e:
            print(f"Не удалось проиндексировать {path}: {e}")
            continue

        structures.doc_lengths[doc_id] = sum(counts.values())
        for word, count in counts.items():
            structures.inverted_index.setdefault(word, {})[doc_id] = count
