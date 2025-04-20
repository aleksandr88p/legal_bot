import fitz  # PyMuPDF
import json
import os
import re

pdf_path = '../../DATA/Codigo_Civil.pdf'
output_path = 'structure_with_text.json'

# Описания стилей для поиска
STYLE_LIBRO = {"font": "AvenirLTStd-Roman", "size": 10.5}
STYLE_TITULO = {"font": "AvenirLTStd-Heavy", "size": 9.5}
STYLE_CAPITULO = {"font": "AvenirLTStd-Roman", "size": 9.5}

def match_style(span, style):
    return span['font'] == style['font'] and abs(span['size'] - style['size']) < 0.2

def is_articulo(span):
    text = span['text'].strip()
    # Строгое совпадение 9.5
    if span['font'] == "AvenirLTStd-Heavy" and abs(span['size'] - 9.5) < 0.2 and re.match(r"^\d+\.", text):
        return True
    # Если не найдено — ищем в диапазоне 9.5 < size <= 9.75
    if span['font'] == "AvenirLTStd-Heavy" and 9.5 < span['size'] <= 9.75 and re.match(r"^\d+\.", text):
        return True
    return False

def extract_structure(pdf_path):
    doc = fitz.open(pdf_path)
    structure = []
    current = {
        "book_name": "codigo civil",
        "libro": None,
        "titulo": None,
        "capitulo": None,
        "articulo": None
    }

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    # LIBRO
                    if match_style(span, STYLE_LIBRO) and text.startswith("LIBRO"):
                        current["libro"] = text
                        current["titulo"] = None
                        current["capitulo"] = None
                        current["articulo"] = None
                        structure.append(current.copy())
                    # TÍTULO
                    elif match_style(span, STYLE_TITULO) and text.startswith("TÍTULO"):
                        current["titulo"] = text
                        current["capitulo"] = None
                        current["articulo"] = None
                        structure.append(current.copy())
                    # CAPÍTULO
                    elif match_style(span, STYLE_CAPITULO) and text.startswith("CAPÍTULO"):
                        current["capitulo"] = text
                        current["articulo"] = None
                        structure.append(current.copy())
                    # ARTICULO — теперь через is_articulo
                    elif is_articulo(span):
                        current["articulo"] = text
                        structure.append(current.copy())
    return structure

if __name__ == "__main__":
    structure = extract_structure(pdf_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Структура сохранена в {output_path}")