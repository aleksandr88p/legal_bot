import fitz  # PyMuPDF
import json
import re
import os

from text_extraction import extract_text_from_pdf

# === НАСТРОЙКИ ===
pdf_path = '../../DATA/Codigo_Penal.pdf'  # путь к PDF Código Penal
book_name = "codigo penal"                # название книги
output_ndjson = "codigo_penal.ndjson"     # временный NDJSON-файл

# Узнаём количество страниц
pdf_document = fitz.open(pdf_path)
page_count = pdf_document.page_count

# Контекст для иерархии
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
            if text.startswith('LIBRO') and font == "AvenirLTStd-Roman" and abs(size - 10.5) < 0.2:
                if current_articulo is not None:
                    fout.write(json.dumps({
                        "book_name": book_name,
                        "libro": current_libro,
                        "titulo": current_titulo,
                        "capitulo": current_capitulo,
                        "articulo": current_articulo,
                        "texto": " ".join(current_text).strip()
                    }, ensure_ascii=False) + "\n")
                    current_articulo = None
                    current_text = []
                current_libro = text
                continue

            # TITULO
            if text.startswith('TÍTULO') and font == "AvenirLTStd-Heavy" and abs(size - 9.5) < 0.2:
                if current_articulo is not None:
                    fout.write(json.dumps({
                        "book_name": book_name,
                        "libro": current_libro,
                        "titulo": current_titulo,
                        "capitulo": current_capitulo,
                        "articulo": current_articulo,
                        "texto": " ".join(current_text).strip()
                    }, ensure_ascii=False) + "\n")
                    current_articulo = None
                    current_text = []
                current_titulo = text
                continue

            # CAPITULO
            if text.startswith('CAPÍTULO') and font == "AvenirLTStd-Roman" and abs(size - 9.5) < 0.2:
                if current_articulo is not None:
                    fout.write(json.dumps({
                        "book_name": book_name,
                        "libro": current_libro,
                        "titulo": current_titulo,
                        "capitulo": current_capitulo,
                        "articulo": current_articulo,
                        "texto": " ".join(current_text).strip()
                    }, ensure_ascii=False) + "\n")
                    current_articulo = None
                    current_text = []
                current_capitulo = text
                continue

            # ARTICULO
            if text.startswith('Artículo') and font == "AvenirLTStd-Heavy" and abs(size - 9.5) < 0.2:
                # Извлекаем только номер (например, "Artículo 10 " -> "10")
                match = re.match(r"Artículo\s+(\d+)", text)
                articulo_num = match.group(1) + "." if match else text
                if current_articulo is not None:
                    fout.write(json.dumps({
                        "book_name": book_name,
                        "libro": current_libro,
                        "titulo": current_titulo,
                        "capitulo": current_capitulo,
                        "articulo": current_articulo,
                        "texto": " ".join(current_text).strip()
                    }, ensure_ascii=False) + "\n")
                current_articulo = articulo_num
                current_text = []
                continue

            # Собираем текст для текущего артикула
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
            current_articulo = None
            current_text = []

print(f"Готово! Все данные записаны в {output_ndjson}")