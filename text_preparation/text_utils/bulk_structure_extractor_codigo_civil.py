import fitz  # PyMuPDF
import json
import re
import os

from text_extraction import extract_text_from_pdf

# === НАСТРОЙКИ ===
pdf_path = '../../DATA/Codigo_Civil.pdf'  # путь к PDF
book_name = "codigo civil"                # название книги
output_ndjson = "codigo_civil.ndjson"     # итоговый NDJSON-файл

pdf_document = fitz.open(pdf_path)
page_count = pdf_document.page_count



def is_libro(text):
    return text.upper().startswith('LIBRO')

def is_titulo(text):
    return text.upper().startswith('TÍTULO')

def is_capitulo(text):
    return text.upper().startswith('CAPÍTULO')

def is_articulo_bold(text, font, size):
    # Только жирный номер артикула, например "17."
    return (
        font == "AvenirLTStd-Heavy"
        and abs(size - 9.5) < 0.3
        and re.match(r'^\d+\.', text.strip())
    )

def get_articulo_num(text):
    m = re.match(r'^(?:art[íi]?culo\s*)?(\d+\.)', text.strip(), re.IGNORECASE)
    if m:
        return m.group(1)
    return text.strip()

def font_ok(font):
    return "AvenirLTStd" in font

doc = fitz.open(pdf_path)
page_count = doc.page_count

current_libro = None
current_titulo = None
current_capitulo = None
current_articulo = None
current_text = []

with open(output_ndjson, "w", encoding="utf-8") as fout:
    for page_num in range(page_count):
        print(f"Обрабатываем страницу {page_num+1} из {page_count}")
        blocks = extract_text_from_pdf(pdf_path, page_num)

        for block in blocks:
            text = block['text'].strip()
            font = block['font']
            size = block['size']

            # LIBRO
            if is_libro(text) and font_ok(font) and 9.0 <= size <= 11.0:
                current_libro = text.strip()
                current_titulo = None
                current_capitulo = None
                current_articulo = None
                current_text = []
                continue

            # TITULO
            if is_titulo(text) and font_ok(font) and 9.0 <= size <= 10.0:
                current_titulo = text.strip()
                current_capitulo = None
                current_articulo = None
                current_text = []
                continue

            # CAPITULO
            if is_capitulo(text) and font_ok(font) and 9.0 <= size <= 10.0:
                current_capitulo = text.strip()
                current_articulo = None
                current_text = []
                continue

            # ARTICULO только по жирному номеру
            if is_articulo_bold(text, font, size):
                # Сохраняем предыдущий артикул
                if current_articulo is not None and current_text:
                    fout.write(json.dumps({
                        "book_name": book_name,
                        "libro": current_libro,
                        "titulo": current_titulo,
                        "capitulo": current_capitulo,
                        "articulo": current_articulo,
                        "texto": " ".join(current_text).strip()
                    }, ensure_ascii=False) + "\n")
                current_articulo = get_articulo_num(text)
                current_text = []
                continue

            # Всё остальное — часть текущего артикула
            if current_articulo is not None:
                current_text.append(text)

        # После каждой страницы сохраняем последний артикул, если он есть
        if current_articulo is not None and current_text:
            fout.write(json.dumps({
                "book_name": book_name,
                "libro": current_libro,
                "titulo": current_titulo,
                "capitulo": current_capitulo,
                "articulo": current_articulo,
                "texto": " ".join(current_text).strip()
            }, ensure_ascii=False) + "\n")
            current_text = []

print("Готово! Все данные записаны в codigo_civil.ndjson")