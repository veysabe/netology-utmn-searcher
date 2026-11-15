import os
from pathlib import Path

import index
from config.config import load_config
from document_reader import load_documents
from server import run_server
from storage import create_storage

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.yaml"

if __name__ == '__main__':
    config = load_config(CONFIG_PATH)
    load_documents(config.search_paths)
    create_storage(config)
    index.index()

    run_server(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8008)),
    )
