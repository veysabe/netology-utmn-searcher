import json


class FileIndexStorage:
    """Хранит частоты слов по документам в JSON-файле."""

    def __init__(self, path="index_cache.json"):
        self.path = path

    def load_cache(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Кэш не удалось прочитать :( {e}")
            return {}

    def save_cache(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def save_index(self, documents, inverted_index, doc_lengths):
        """Файловому кэшу достаточно сохранённых частот слов."""

    def load_index(self, documents):
        """Готовый индекс собирается из кэша слов при запуске."""
        return None
