import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Читаем текст из файла
with open("extracted_laws.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Исправляем основные структурные элементы
def fix_main_structure(text):
    # Исправляем TÍTULO PRELIMINAR
    text = re.sub(r'TÍT[Uu\s\n]*LO\s+PRELIMINAR', 'TÍTULO PRELIMINAR', text)
    
    # Исправляем LIBRO с разными номерами
    text = re.sub(r'LI[Bb\s\n]*RO\s+PRIMERO', 'LIBRO PRIMERO', text)
    text = re.sub(r'LI[Bb\s\n]*RO\s+II', 'LIBRO II', text)
    text = re.sub(r'LI[Bb\s\n]*RO\s+III', 'LIBRO III', text)
    text = re.sub(r'LI[Bb\s\n]*RO\s+IV', 'LIBRO IV', text)
    
    # Исправляем TÍTULO (общий шаблон)
    text = re.sub(r'TÍT[Uu\s\n]*LO', 'TÍTULO', text)
    
    # Исправляем CAPÍTULO (общий шаблон)
    text = re.sub(r'CAPÍT[Uu\s\n]*LO', 'CAPÍTULO', text)
    
    return text

# Исправляем переносы и пробелы в словах
def fix_word_breaks(text):
    # Убираем перенос с дефисом (например, "com- pleta" → "completa")
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Убираем лишние пробелы между частями слова (например, "costumbr e" → "costumbre")
    text = re.sub(r'(\w{2,})\s+(\w{1,3})\b', r'\1\2', text)
    
    # Объединяем куски слов, разбитые переносом строки
    text = re.sub(r'(\w{2,})\s*\n\s*(\w{1,3})\b', r'\1\2', text)
    
    return text

# Исправляем нумерацию статей
def fix_article_numbering(text):
    # Соединяем номера статей, разорванные разрывами строк
    text = re.sub(r'(\d+)\.\s*\n\s*', r'\1. ', text)
    
    # Исправляем случаи, когда номер и текст разделены переносом строки
    text = re.sub(r'(\d+\.\s*)\n(\w+)', r'\1 \2', text)
    
    return text

# Нормализуем регистр для подзаголовков
def normalize_subheader_case(text):
    # Находим подзаголовки между CAPÍTULO и номерами статей и приводим их к верхнему регистру
    def uppercase_headers(match):
        return match.group(1) + match.group(2).upper() + match.group(3)
    
    # Шаблон: CAPÍTULO + любой текст + до первого номера статьи
    text = re.sub(r'(CAPÍTULO [IVX]+\s*\n\s*)([a-zñáéíóúü\s]+)(\n\s*\d+\.)', 
                  uppercase_headers, text, flags=re.IGNORECASE)
    
    return text

def process_legal_text(text):
    print("Начало обработки текста...")
    
    # Шаг 1: Исправляем основную структуру
    text = fix_main_structure(text)
    print("Структурные заголовки исправлены")
    
    # Шаг 2: Исправляем переносы и пробелы в словах
    text = fix_word_breaks(text)
    print("Переносы и пробелы в словах исправлены")
    
    # Шаг 3: Исправляем нумерацию статей
    text = fix_article_numbering(text)
    print("Нумерация статей исправлена")
    
    # Шаг 4: Нормализуем регистр для подзаголовков
    text = normalize_subheader_case(text)
    print("Регистр подзаголовков нормализован")
    
    # Шаг 5: Общая очистка
    text = text.replace('\r', '')  # Удаляем возможные символы возврата каретки
    text = re.sub(r'\n{3,}', '\n\n', text)  # Убираем избыточные пустые строки
    print("Общая очистка завершена")
    
    return text

processed_text = process_legal_text(text)
with open("processed_laws.txt", "w", encoding="utf-8") as f:
    f.write(processed_text)

print("Обработка закончена. Результат сохранен в processed_laws.txt")