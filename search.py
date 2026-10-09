import math

import structures
from index import WORD_RE

def search(query):
    words = set(WORD_RE.findall(query.lower()))
    total_docs = len(structures.documents)

    scores: dict[int, float] = {} # ID документа -> релевантность
    matches: dict[int, dict[str, int]] = {} # ID документа -> {слово -> количество вхождений}

    for word in words:
        postings = structures.inverted_index.get(word)
        if not postings:
            continue
        # тут мы этими +1 от деления на ноль защищаемся,
        idf = math.log((total_docs + 1) / (len(postings) + 1)) + 1
        for doc_id, count in postings.items():
            scores[doc_id] = scores.get(doc_id, 0.0) + count * idf
            matches.setdefault(doc_id, {})[word] = count

    ranked = sorted(scores, key=lambda doc_id: (len(matches[doc_id]), scores[doc_id]), reverse=True)

    return [
        {
            "id": doc_id,
            "path": structures.documents[doc_id],
            # "score": round(scores[doc_id], 4),
        }
        for doc_id in ranked
    ]
