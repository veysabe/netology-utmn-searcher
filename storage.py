from pathlib import Path

import pymongo

from index_storage import FileIndexStorage

# Состояние хранилища для GET /health
STATUS = {"mode": "file", "fallback": False, "reason": None}

# Хранилище, которым пользуется index.index()
current = FileIndexStorage()


class MongoIndexStorage:
    """Хранит документы, постинги и длины документов в MongoDB."""

    def __init__(self, uri="mongodb://localhost:27017", db_name="pdf_search", client=None):
        self.client = client or pymongo.MongoClient(uri, serverSelectionTimeoutMS=1000)
        self.db = self.client[db_name]

    def check(self):
        """Проверяет, что база доступна."""
        self.client.admin.command("ping")

    def load_cache(self):
        return {
            doc["path"]: {"mtime": doc["mtime"], "words": doc["words"]}
            for doc in self.db.documents.find()
        }

    def save_cache(self, data):
        self.db.documents.delete_many({})
        if data:
            self.db.documents.insert_many(
                [
                    {"path": path, "mtime": item["mtime"], "words": item["words"]}
                    for path, item in data.items()
                ]
            )

    def save_index(self, documents, inverted_index, doc_lengths):
        self.db.postings.delete_many({})
        if inverted_index:
            self.db.postings.insert_many(
                [
                    {"word": word, "docs": {str(doc_id): count for doc_id, count in docs.items()}}
                    for word, docs in inverted_index.items()
                ]
            )
        self.db.doc_lengths.delete_many({})
        if doc_lengths:
            self.db.doc_lengths.insert_many(
                [{"doc_id": doc_id, "length": length} for doc_id, length in doc_lengths.items()]
            )

    def load_index(self, documents):
        """Возвращает индекс из базы, если файлы не изменились."""
        saved_mtimes = {doc["path"]: doc["mtime"] for doc in self.db.documents.find()}
        try:
            current_mtimes = {
                path: Path(path).stat().st_mtime for path in documents.values()
            }
        except OSError:
            return None
        if not saved_mtimes or saved_mtimes != current_mtimes:
            return None

        inverted_index = {
            doc["word"]: {int(doc_id): count for doc_id, count in doc["docs"].items()}
            for doc in self.db.postings.find()
        }
        doc_lengths = {doc["doc_id"]: doc["length"] for doc in self.db.doc_lengths.find()}
        return inverted_index, doc_lengths


def create_storage(config):
    """Создаёт хранилище из конфигурации с откатом на файловый кэш."""
    global current

    if config.storage != "mongodb":
        current = FileIndexStorage()
        STATUS.update(mode="file", fallback=False, reason=None)
        return current

    try:
        storage = MongoIndexStorage(config.mongo_uri, config.mongo_db)
        storage.check()
    except pymongo.errors.ServerSelectionTimeoutError:
        print("MongoDB недоступна, использую файловый кэш")
        current = FileIndexStorage()
        STATUS.update(mode="file", fallback=True, reason="нет соединения с MongoDB")
        return current
    except Exception as e:
        print(f"MongoDB недоступна ({e}), использую файловый кэш")
        current = FileIndexStorage()
        STATUS.update(mode="file", fallback=True, reason=str(e))
        return current

    current = storage
    STATUS.update(mode="mongodb", fallback=False, reason=None)
    return current
