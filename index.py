import re

import structures
import pypdf

WORD_RE = re.compile(r"\w+")

def index():
    for doc_id, path in structures.documents.items():
        reader = pypdf.PdfReader(path)
        for page in reader.pages:
            text = (page.extract_text() or "").lower()
            for word in WORD_RE.findall(text):
                if word not in structures.inverted_index:
                    structures.inverted_index[word] = {
                        doc_id: 1
                    }
                else:
                    if doc_id not in structures.inverted_index[word]:
                        structures.inverted_index[word][doc_id] = 1
                    else:
                        structures.inverted_index[word][doc_id] += 1
