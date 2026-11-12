import heapq
import math

import structures
from index import WORD_RE


class Searcher:
    """Ранжирует документы по TF-IDF."""

    def __init__(self, documents, inverted_index, doc_lengths, limit=10):
        self.documents = documents
        self.inverted_index = inverted_index
        self.doc_lengths = doc_lengths
        self.limit = limit

    def search(self, query):
        words = set(WORD_RE.findall(query.lower()))
        total_docs = len(self.documents)

        scores = {}  # ID документа -> релевантность

        for word in words:
            postings = self.inverted_index.get(word)
            if not postings:
                continue
            # tf = count / длина документа, idf = log(N / df)
            idf = math.log(total_docs / len(postings))
            for doc_id, count in postings.items():
                tf = count / self.doc_lengths[doc_id]
                scores[doc_id] = scores.get(doc_id, 0.0) + tf * idf

        ranked = heapq.nlargest(self.limit, scores, key=scores.get)

        return [
            {
                "id": doc_id,
                "path": self.documents[doc_id],
            }
            for doc_id in ranked
        ]


def search(query, limit=10):
    """Ищет по глобальному индексу."""
    searcher = Searcher(
        structures.documents,
        structures.inverted_index,
        structures.doc_lengths,
        limit,
    )
    return searcher.search(query)
