import fitz  # Для работы с PDF
import json
import os
import re

# Можно импортировать свою функцию, если нужно:
from text_extraction import extract_text_from_pdf

# Пример: анализ одной страницы PDF
pdf_path = '../../DATA/Codigo_Civil.pdf'
page_num = 66

# Получаем текст и стили
blocks = extract_text_from_pdf(pdf_path, page_num)


# Сохраняем результат
with open(f'civil{page_num}.json', 'w', encoding='utf-8') as f:
    json.dump(blocks, f, ensure_ascii=False, indent=2)