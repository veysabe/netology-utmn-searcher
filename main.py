from config.config import load_config

if __name__ == '__main__':
    config = load_config('./config/config.yaml')
    print(config.search_paths)
    pass