from pathlib import Path

from structures import documents

ROOT_PATH = Path(__file__).resolve().parent


class DocumentReader:
    """Собирает PDF-файлы из директорий конфигурации."""

    def __init__(self, root_path=ROOT_PATH):
        self.root_path = Path(root_path)

    def load(self, search_paths):
        found = {}
        document_id = 1

        for folder_path in search_paths:
            folder_path = Path(folder_path)
            if not folder_path.is_absolute():
                folder_path = self.root_path / folder_path
            if not folder_path.is_dir():
                continue
            for file_path in sorted(folder_path.iterdir()):
                if file_path.is_file() and file_path.suffix.lower() == ".pdf":
                    found[document_id] = str(file_path)
                    document_id += 1
        return found


def load_documents(search_paths):
    """Обновляет глобальный список документов и возвращает его."""
    documents.clear()
    documents.update(DocumentReader().load(search_paths))
    return documents
