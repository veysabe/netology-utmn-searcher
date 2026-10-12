from pathlib import Path

from structures import documents

ROOT_PATH = Path(__file__).resolve().parent

def load_documents(search_paths):
    documents.clear()
    document_id = 1

    for folder_path in search_paths:
        folder_path = ROOT_PATH / folder_path.lstrip("/\\")
        if not folder_path.is_dir():
            continue
        for file_path in sorted(folder_path.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() == ".pdf":
                documents[document_id] = str(file_path)
                document_id += 1
    return documents
