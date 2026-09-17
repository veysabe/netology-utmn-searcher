from config.config import load_config
from server import run_server
from document_reader import load_documents

if __name__ == '__main__':
    config = load_config('./config/config.yaml')
    load_documents(config.search_paths)
    print(config.search_paths)

    run_server()
    pass