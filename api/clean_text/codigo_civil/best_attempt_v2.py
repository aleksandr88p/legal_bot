import re
import json
from typing import Dict, List, Tuple

# Путь к очищенному файлу
cleaned_text_file = 'cleaned_text.txt'

def find_main_sections(input_file: str) -> dict:
    """
    Находит основные секции в тексте закона:
    - TÍTULO PRELIMINAR
    - LIBRO PRIMERO
    - LIBRO II
    - LIBRO III
    - LIBRO IV
    
    Args:
        input_file (str): путь к очищенному файлу с текстом
        
    Returns:
        dict: словарь с найденными секциями и их позициями
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    sections = {}

    # TÍTULO PRELIMINAR
    titulo_prel = re.search(r'TÍTULO PRELIMINAR', text)
    if titulo_prel:
        sections['TÍTULO PRELIMINAR'] = titulo_prel.start()

    # LIBROS
    libro_patterns = [
        r'LIBRO PRIMERO',
        r'LIBRO II\b', 
        r'LIBRO III\b',
        r'LIBRO IV\b'
    ]
    for pattern in libro_patterns:
        match = re.search(pattern, text)
        if match:
            sections[match.group()] = match.start()
    
    print("\nНайдены следующие секции:")
    for section, pos in sorted(sections.items(), key=lambda x: x[1]):
        print(f"- {section}")
    
    return sections

def extract_sections_text(input_file: str, sections: dict) -> dict:
    """
    Извлекает текст каждой секции, используя найденные позиции
    
    Args:
        input_file (str): путь к файлу с текстом
        sections (dict): словарь с позициями секций
    
    Returns:
        dict: словарь с текстами секций
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    sections_text = {}
    sorted_sections = sorted(sections.items(), key=lambda x: x[1])
    
    for i, (section_name, start_pos) in enumerate(sorted_sections):
        if i == len(sorted_sections) - 1:
            sections_text[section_name] = text[start_pos:]
        else:
            next_section_pos = sorted_sections[i + 1][1]
            sections_text[section_name] = text[start_pos:next_section_pos]
    
    print("\nИзвлечены тексты следующих секций:")
    for section, content in sections_text.items():
        print(f"- {section}: {len(content)} символов")
    
    return sections_text

def find_capitulos(sections_text: dict) -> dict:
    """
    Находит все CAPÍTULO в тексте и создает структуру документа.
    Для TÍTULO PRELIMINAR ищет CAPÍTULO напрямую,
    для LIBRO ищет TÍTULO, а затем CAPÍTULO внутри них.
    
    Args:
        sections_text (dict): словарь с текстами основных секций
    
    Returns:
        dict: иерархическая структура документа
    """
    structure = {}
    
    for section_name, section_text in sections_text.items():
        print(f"\nОбработка секции: {section_name}")
        structure[section_name] = {}
        
        # Для TÍTULO PRELIMINAR ищем CAPÍTULO напрямую
        if section_name == 'TÍTULO PRELIMINAR':
            capitulos = list(re.finditer(r'CAPÍTULO\s+(?:PRIMERO|[IVX]+)', section_text))
            
            for i, capitulo_match in enumerate(capitulos):
                capitulo_name = capitulo_match.group()
                capitulo_start = capitulo_match.start()
                
                if i < len(capitulos) - 1:
                    capitulo_end = capitulos[i+1].start()
                else:
                    capitulo_end = len(section_text)
                
                capitulo_text = section_text[capitulo_start:capitulo_end]
                print(f"  Найдена глава: {capitulo_name}")
                
                structure[section_name][capitulo_name] = {
                    "text": capitulo_text,
                    "chunks": []  # Здесь будут чанки текста
                }
        
        # Для LIBRO ищем TÍTULO, а затем CAPÍTULO
        else:
            titulos = list(re.finditer(r'TÍTULO\s+(?:PRIMERO|[IVX]+)', section_text))
            
            for i, titulo_match in enumerate(titulos):
                titulo_name = titulo_match.group()
                titulo_start = titulo_match.start()
                
                if i < len(titulos) - 1:
                    titulo_end = titulos[i+1].start()
                else:
                    titulo_end = len(section_text)
                
                titulo_text = section_text[titulo_start:titulo_end]
                print(f"  Найден раздел: {titulo_name}")
                
                structure[section_name][titulo_name] = {
                    "text": titulo_text,
                    "capitulos": {}
                }
                
                # Ищем CAPÍTULO внутри TÍTULO
                capitulos = list(re.finditer(r'CAPÍTULO\s+(?:PRIMERO|[IVX]+)', titulo_text))
                
                for j, capitulo_match in enumerate(capitulos):
                    capitulo_name = capitulo_match.group()
                    capitulo_start = capitulo_match.start()
                    
                    if j < len(capitulos) - 1:
                        capitulo_end = capitulos[j+1].start()
                    else:
                        capitulo_end = len(titulo_text)
                    
                    capitulo_text = titulo_text[capitulo_start:capitulo_end]
                    print(f"    Найдена глава: {capitulo_name}")
                    
                    structure[section_name][titulo_name]["capitulos"][capitulo_name] = {
                        "text": capitulo_text,
                        "chunks": []  # Здесь будут чанки текста
                    }
    
    return structure

def split_into_chunks(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Разбивает текст на чанки с перекрытием.
    Перекрытие (overlap) нужно для сохранения контекста между чанками.
    
    Args:
        text (str): текст для разбиения
        max_chunk_size (int): максимальный размер чанка
        overlap (int): размер перекрытия между чанками
    
    Returns:
        List[str]: список чанков текста
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Определяем конец текущего чанка
        end = start + max_chunk_size
        
        if end >= len(text):
            # Если это последний чанк, берем весь оставшийся текст
            chunks.append(text[start:])
            break
        
        # Ищем ближайший конец параграфа или предложения
        # чтобы не разрезать текст посередине
        next_period = text.find('.', end - 100, end + 100)
        if next_period != -1:
            end = next_period + 1
        
        chunks.append(text[start:end])
        
        # Учитываем перекрытие при определении начала следующего чанка
        start = end - overlap
    
    return chunks

def process_structure_for_chunks(structure: dict, max_chunk_size: int = 1000, overlap: int = 100) -> dict:
    """
    Обрабатывает структуру документа и разбивает текст глав на чанки.
    
    Args:
        structure (dict): иерархическая структура документа
        max_chunk_size (int): максимальный размер чанка
        overlap (int): размер перекрытия между чанками
    
    Returns:
        dict: структура с чанками текста
    """
    print("\nРазбиение текста на чанки...")
    
    for section_name, section_data in structure.items():
        if section_name == 'TÍTULO PRELIMINAR':
            for capitulo_name, capitulo_data in section_data.items():
                chunks = split_into_chunks(
                    capitulo_data["text"],
                    max_chunk_size,
                    overlap
                )
                capitulo_data["chunks"] = chunks
                print(f"  {capitulo_name}: разбит на {len(chunks)} чанков")
        else:
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    chunks = split_into_chunks(
                        capitulo_data["text"],
                        max_chunk_size,
                        overlap
                    )
                    capitulo_data["chunks"] = chunks
                    print(f"  {capitulo_name}: разбит на {len(chunks)} чанков")
    
    return structure

def create_flat_chunks_list(structure: dict) -> list:
    """
    Создает плоский список чанков с метаданными для эмбеддингов.
    Каждый чанк содержит информацию о его расположении в структуре документа.
    
    Args:
        structure (dict): иерархическая структура документа
    
    Returns:
        list: список чанков с метаданными
    """
    chunks_list = []
    
    for section_name, section_data in structure.items():
        if section_name == 'TÍTULO PRELIMINAR':
            for capitulo_name, capitulo_data in section_data.items():
                for i, chunk_text in enumerate(capitulo_data["chunks"]):
                    chunks_list.append({
                        "libro": section_name,
                        "titulo": "",
                        "capitulo": capitulo_name,
                        "chunk_index": i,
                        "total_chunks": len(capitulo_data["chunks"]),
                        "text": chunk_text
                    })
        else:
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    for i, chunk_text in enumerate(capitulo_data["chunks"]):
                        chunks_list.append({
                            "libro": section_name,
                            "titulo": titulo_name,
                            "capitulo": capitulo_name,
                            "chunk_index": i,
                            "total_chunks": len(capitulo_data["chunks"]),
                            "text": chunk_text
                        })
    
    print(f"\nСоздан плоский список из {len(chunks_list)} чанков для эмбеддингов")
    return chunks_list

def save_chunks_to_json(chunks_list: list, output_file: str):
    """
    Сохраняет список чанков в JSON-файл.
    
    Args:
        chunks_list (list): список чанков с метаданными
        output_file (str): путь для сохранения
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_list, f, ensure_ascii=False, indent=2)
    
    print(f"Чанки сохранены в файл: {output_file}")

def main():
    print("Запуск улучшенного алгоритма обработки юридического текста (V2)...")
    
    # Шаг 1: Находим основные секции
    sections = find_main_sections(cleaned_text_file)
    
    # Шаг 2: Извлекаем текст каждой секции
    sections_text = extract_sections_text(cleaned_text_file, sections)
    
    # Шаг 3: Находим все CAPÍTULO и создаем структуру
    structure = find_capitulos(sections_text)
    
    # Шаг 4: Разбиваем текст глав на чанки
    structure = process_structure_for_chunks(structure)
    
    # Шаг 5: Создаем плоский список чанков для эмбеддингов
    chunks_list = create_flat_chunks_list(structure)
    
    # Шаг 6: Сохраняем чанки в JSON
    save_chunks_to_json(chunks_list, 'chunks_for_embeddings.json')
    
    print("\nОбработка завершена. Результаты готовы для создания эмбеддингов.")

if __name__ == "__main__":
    main() 