documents: dict[int, str] = {} # ID документа -> путь
inverted_index: dict[str, dict[int, int]] = {} # Слово -> {ID документа -> количество повторений слова в документе}
doc_lengths: dict[int, int] = {} # ID документа -> общее количество слов в документе
