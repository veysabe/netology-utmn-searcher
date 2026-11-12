documents: dict[int, str] = {}  # ID документа -> путь
# Слово -> {ID документа -> количество повторений слова в документе}
inverted_index: dict[str, dict[int, int]] = {}
doc_lengths: dict[int, int] = {}  # ID документа -> общее количество слов
