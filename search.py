import heapq
import math

import structures
from index import WORD_RE

def search(query, limit=10):
    words = set(WORD_RE.findall(query.lower()))
    total_docs = len(structures.documents)

    scores: dict[int, float] = {} # ID документа -> релевантность

    for word in words:
        postings = structures.inverted_index.get(word)
        if not postings:
            continue
        # tf = count / длина документа, idf = log(N / df)
        idf = math.log(total_docs / len(postings))
        for doc_id, count in postings.items():
            tf = count / structures.doc_lengths[doc_id]
            scores[doc_id] = scores.get(doc_id, 0.0) + tf * idf

    ranked = heapq.nlargest(limit, scores, key=scores.get)

    return [
        {
            "id": doc_id,
            "path": structures.documents[doc_id],
            # "score": round(scores[doc_id], 4),
        }
        for doc_id in ranked
    ]
