import os

from structures import documents

def load_documents(search_paths):
    documents.clear()
    document_id = 1

    for folder_path in search_paths:
        if not os.path.isdir(folder_path):
            continue
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
                documents[document_id] = file_path
                document_id += 1
    return documents