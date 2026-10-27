from pathlib import Path

import os

import index
import search
from config.config import load_config
from server import run_server
from document_reader import load_documents

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.yaml"

if __name__ == '__main__':
    config = load_config(CONFIG_PATH)
    load_documents(config.search_paths)
    print(config.search_paths)
    index.index()

    run_server(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8008)),
    )
