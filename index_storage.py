import json

def load_cache():
    try:
        with open('index_cache.json', encoding='utf-8') as f:
            raw = json.load(f)
        return raw
    except Exception as e:
        print(f"Кэш не удалось прочитать :( {e}")
        return {}

def save_cache(data):
    with open('index_cache.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)