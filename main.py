from config.config import load_config
from app import run_server

if __name__ == '__main__':
    config = load_config('./config/config.yaml')
    print(config.search_paths)

    run_server()
    pass