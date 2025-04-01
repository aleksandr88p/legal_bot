import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def clean_text_with_metadata(text):
    # Убираем титульные страницы и оглавление (всё до "TÍTULO PRELIMINAR")
    start_index = text.find("TÍTULO PRELIMINAR")
    if start_index != -1:
        text = text[start_index:]

    # Убираем повторяющиеся заголовки
    text = re.sub(r'^(Código Civil|LA NORMA AL DIA|MINISTERIO DE JUSTICIA|Agencia Estatal Boletin Oficial del Estado.*)$', '', text, flags=re.MULTILINE)

    # Убираем номера страниц и "$1$"
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\$1\$$', '', text, flags=re.MULTILINE)

    # Убираем сноски (но можно сохранить их отдельно, если нужно)
    text = re.sub(r'^\d+\s*(Redactado|Apartado derogado|Título redactado).*$', '', text, flags=re.MULTILINE)

    # Убираем лишние пробелы и пустые строки
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()

    # Разбиваем на чанки и извлекаем метаданные
    lines = text.split('\n')
    chunks_with_metadata = []
    current_title = ""
    current_article = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Проверяем, является ли строка заголовком раздела (например, "TÍTULO PRELIMINAR")
        if re.match(r'^(TÍTULO|CAPÍTULO|SEC\.)', line):
            current_title = line
            continue

        # Проверяем, является ли строка началом статьи (например, "1.", "2.")
        article_match = re.match(r'^(\d+\.\s+)(.*)', line)
        if article_match:
            current_article = f"Artículo {article_match.group(1).strip()[:-1]}"  # Например, "Artículo 1"
            article_text = article_match.group(2).strip()
            chunks_with_metadata.append({
                "title": current_title,
                "article": current_article,
                "text": article_text
            })
        else:
            # Если это продолжение статьи, добавляем к последнему чанку
            if chunks_with_metadata:
                chunks_with_metadata[-1]["text"] += " " + line

    return chunks_with_metadata

# Читаем текст из файла
with open("extracted_laws.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Очищаем и извлекаем метаданные
chunks_with_metadata = clean_text_with_metadata(text)

# Создаём эмбеддинги только для текста
model = SentenceTransformer('all-MiniLM-L6-v2')
texts = [chunk["text"] for chunk in chunks_with_metadata]
embeddings = model.encode(texts)

# Сохраняем в FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))
faiss.write_index(index, 'laws_index.faiss')

# Сохраняем чанки с метаданными
with open('laws_chunks.txt', 'w', encoding='utf-8') as f:
    for chunk in chunks_with_metadata:
        f.write(f"{chunk['title']}|{chunk['article']}|{chunk['text']}\n")

print(f"Сохранено {len(chunks_with_metadata)} чанков в FAISS")