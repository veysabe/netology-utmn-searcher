import structures
import pypdf

def index():
    for doc_id, path in structures.documents.items():
        reader = pypdf.PdfReader(path)
        for page in reader.pages:
            text = page.extract_text().lower().replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
            for word in text.split():
                if word not in structures.inverted_index:
                    structures.inverted_index[word] = {
                        doc_id: 1
                    }
                else:
                    if doc_id not in structures.inverted_index[word]:
                        structures.inverted_index[word][doc_id] = 1
                    else:
                        structures.inverted_index[word][doc_id] += 1
