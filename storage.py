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
        for doc_id, path in documents.items():
            self.db.documents.update_one({"path": path}, {"$set": {"doc_id": doc_id}})

    def load_index(self, documents):
        """Возвращает индекс из базы, если файлы не изменились."""
        stored = {doc["path"]: doc for doc in self.db.documents.find()}
        if not stored:
            return None

        current_mtimes = {}
        for path in documents.values():
            try:
                current_mtimes[path] = Path(path).stat().st_mtime
            except OSError:
                return None
        if set(stored) != set(current_mtimes):
            return None
        for path, mtime in current_mtimes.items():
            if stored[path]["mtime"] != mtime or "doc_id" not in stored[path]:
                return None

        # Идентификаторы могли измениться, если поменялся порядок директорий,
        # поэтому пересчитываем их по путям.
        old_to_new = {}
        for doc_id, path in documents.items():
            old_to_new[stored[path]["doc_id"]] = doc_id

        inverted_index = {}
        for doc in self.db.postings.find():
            inverted_index[doc["word"]] = {
                old_to_new[int(old_id)]: count for old_id, count in doc["docs"].items()
            }
        doc_lengths = {
            old_to_new[doc["doc_id"]]: doc["length"] for doc in self.db.doc_lengths.find()
        }
        return inverted_index, doc_lengths


def _use_file_storage(reason):
    global current
    current = FileIndexStorage()
    STATUS.update(mode="file", fallback=True, reason=reason)
    return current


def create_storage(config):
    """Создаёт хранилище из конфигурации с откатом на файловый кэш."""
    global current

    if config.storage != "mongodb":
        current = FileIndexStorage()
        STATUS.update(mode="file", fallback=False, reason=None)
        return current

    try:
        mongo = MongoIndexStorage(config.mongo_uri, config.mongo_db)
        mongo.check()
    except pymongo.errors.ServerSelectionTimeoutError:
        print("MongoDB недоступна, использую файловый кэш")
        return _use_file_storage("нет соединения с MongoDB")
    except Exception as e:
        print(f"MongoDB недоступна ({e}), использую файловый кэш")
        return _use_file_storage(str(e))

    current = mongo
    STATUS.update(mode="mongodb", fallback=False, reason=None)
    return current
