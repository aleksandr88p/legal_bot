import fitz  # PyMuPDF
import json
import re

# 1. Пути к файлам
pdf_path = '../../DATA/codigo_penal.pdf'
output_path = 'structure_with_text_penal.json'

# 2. Описание стилей для поиска
STYLE_LIBRO = {"font": "AvenirLTStd-Roman", "size": 10.5}
STYLE_TITULO = {"font": "AvenirLTStd-Heavy", "size": 9.5}
STYLE_CAPITULO = {"font": "AvenirLTStd-Roman", "size": 9.5}

# 3. Сравнение стиля
def match_style(span, style):
    return span['font'] == style['font'] and abs(span['size'] - style['size']) < 0.2

# 4. Поиск артиклов по penal
def is_articulo(span):
    text = span['text'].strip()
    # "Artículo 14" или "ARTÍCULO 14"
    if (
        span['font'] == "AvenirLTStd-Heavy"
        and abs(span['size'] - 9.5) < 0.2
        and re.match(r"^(Artículo|ARTÍCULO)\s+\d+", text)
    ):
        return True
    return False

# 5. Основной парсер
def extract_structure_with_text(pdf_path):
    doc = fitz.open(pdf_path)
    structure = []
    current = {
        "book_name": "codigo penal",
        "libro": None,
        "titulo": None,
        "capitulo": None,
        "articulo": None,
        "text": ""
    }

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span['text'].strip()
                    # LIBRO
                    if match_style(span, STYLE_LIBRO) and text.startswith("LIBRO"):
                        if current["articulo"]:
                            structure.append(current.copy())
                        current["libro"] = text
                        current["titulo"] = None
                        current["capitulo"] = None
                        current["articulo"] = None
                        current["text"] = ""
                    # TITULO
                    elif match_style(span, STYLE_TITULO) and text.startswith("TÍTULO"):
                        if current["articulo"]:
                            structure.append(current.copy())
                        current["titulo"] = text
                        current["capitulo"] = None
                        current["articulo"] = None
                        current["text"] = ""
                    # CAPITULO
                    elif match_style(span, STYLE_CAPITULO) and text.startswith("CAPÍTULO"):
                        if current["articulo"]:
                            structure.append(current.copy())
                        current["capitulo"] = text
                        current["articulo"] = None
                        current["text"] = ""
                    # ARTICULO
                    elif is_articulo(span):
                        if current["articulo"]:
                            structure.append(current.copy())
                        current["articulo"] = text
                        current["text"] = ""
                    # Добавляем текст к текущей статье
                    elif current["articulo"]:
                        current["text"] += (text + " ")

    # Добавляем последний артикул
    if current["articulo"]:
        structure.append(current.copy())

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"Структура сохранена в {output_path}")

# 6. Запуск парсера
if __name__ == "__main__":
    extract_structure_with_text(pdf_path)