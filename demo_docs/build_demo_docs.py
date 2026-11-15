"""Пересобирает демонстрационный корпус PDF.

Запуск: python demo_docs/build_demo_docs.py
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS = {
    "01_python_basics.pdf": [
        "Python is a popular programming language.",
        "Python is used for web development, data analysis and automation.",
        "This document describes Python basics.",
    ],
    "02_search_engines.pdf": [
        "A search engine finds documents by keywords.",
        "Search engines build an inverted index.",
        "The index maps every word to documents.",
        "Search quality depends on ranking.",
    ],
    "03_pdf_and_text.pdf": [
        "PDF is a format for documents.",
        "A PDF file can contain text.",
        "Python can read PDF files and extract text for search.",
    ],
    "04_tf_idf_ranking.pdf": [
        "TF-IDF is a ranking method for search.",
        "TF-IDF uses word frequency and document frequency.",
        "The inverted index stores word frequency for each document.",
    ],
}


def escape_pdf_string(text):
    """Экранирует символы, которые в PDF имеют специальный смысл."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(path, lines):
    """Создаёт простой одностраничный PDF с текстом."""
    content = "BT\n/F1 12 Tf\n72 720 Td\n16 TL\n"
    for line in lines:
        content += f"({escape_pdf_string(line)}) Tj\nT*\n"
    content += "ET\n"

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content)} >>\nstream\n{content}endstream",
    ]

    pdf = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{number} 0 obj\n{obj}\nendobj\n"

    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n"
    pdf += "0000000000 65535 f \n"
    for offset in offsets:
        pdf += f"{offset:010d} 00000 n \n"
    pdf += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )

    path.write_bytes(pdf.encode("latin-1"))


def main():
    for filename, lines in DOCUMENTS.items():
        make_pdf(BASE_DIR / filename, lines)
        print(f"Создан {filename}")


if __name__ == "__main__":
    main()
