import fitz  # PyMuPDF
import json
import re

pdf_path = '../../DATA/Codigo_Civil.pdf'
output_path = 'structure_with_text.json'

STYLE_LIBRO = {"font": "AvenirLTStd-Roman", "size": 10.5}
STYLE_TITULO = {"font": "AvenirLTStd-Heavy", "size": 9.5}
STYLE_CAPITULO = {"font": "AvenirLTStd-Roman", "size": 9.5}

def match_style(span, style):
    return span['font'] == style['font'] and abs(span['size'] - style['size']) < 0.2

def is_articulo(span):
    text = span['text'].strip()
    if span['font'] == "AvenirLTStd-Heavy" and abs(span['size'] - 9.5) < 0.2 and re.match(r"^\d+\.", text):
        return True
    if span['font'] == "AvenirLTStd-Heavy" and 9.5 < span['size'] <= 9.75 and re.match(r"^\d+\.", text):
        return True
    return False

def extract_structure_with_text(pdf_path):
    doc = fitz.open(pdf_path)
    result = []
    current = {
        "book_name": "codigo civil",
        "libro": None,
        "titulo": None,
        "capitulo": None,
        "articulo": None,
        "texto": ""
    }
    current_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()

                    # LIBRO
                    if match_style(span, STYLE_LIBRO) and text.startswith("LIBRO"):
                        # Сохраняем предыдущую статью, если была
                        if current["articulo"] is not None:
                            current["texto"] = " ".join(current_text).strip()
                            result.append(current.copy())
                            current_text = []
                            current["articulo"] = None
                        current["libro"] = text
                        current["titulo"] = None
                        current["capitulo"] = None
                        continue

                    # TÍTULO
                    if match_style(span, STYLE_TITULO) and text.startswith("TÍTULO"):
                        if current["articulo"] is not None:
                            current["texto"] = " ".join(current_text).strip()
                            result.append(current.copy())
                            current_text = []
                            current["articulo"] = None
                        current["titulo"] = text
                        current["capitulo"] = None
                        continue

                    # CAPÍTULO
                    if match_style(span, STYLE_CAPITULO) and text.startswith("CAPÍTULO"):
                        if current["articulo"] is not None:
                            current["texto"] = " ".join(current_text).strip()
                            result.append(current.copy())
                            current_text = []
                            current["articulo"] = None
                        current["capitulo"] = text
                        continue

                    # ARTICULO
                    if is_articulo(span):
                        if current["articulo"] is not None:
                            current["texto"] = " ".join(current_text).strip()
                            result.append(current.copy())
                            current_text = []
                        current["articulo"] = text
                        continue

                    # Всё остальное — текст статьи
                    if current["articulo"] is not None:
                        if text:
                            current_text.append(text)

    # Сохраняем последнюю статью, если была
    if current["articulo"] is not None:
        current["texto"] = " ".join(current_text).strip()
        result.append(current.copy())

    return result

if __name__ == "__main__":
    structure = extract_structure_with_text(pdf_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Структура с текстами статей сохранена в {output_path}")