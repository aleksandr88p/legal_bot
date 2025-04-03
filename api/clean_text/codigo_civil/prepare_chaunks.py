import re
import json
from typing import Dict, List, Any

def find_main_sections(text: str) -> Dict[str, str]:
    """
    Находит основные секции в тексте и извлекает их.
    
    Args:
        text (str): Очищенный текст всего документа.
    
    Returns:
        Dict[str, str]: Словарь с названиями секций и их текстами.
    """
    sections = {}
    with open(text, 'r', encoding='utf-8') as f:
        text = f.read() 
    # Определяем шаблоны для поиска секций
    section_patterns = [
        r'TÍTULO PRELIMINAR',
        r'LIBRO PRIMERO',
        r'LIBRO II\b',
        r'LIBRO III\b',
        r'LIBRO IV\b'
    ]
    
    # Находим позиции каждой секции
    positions = [(match.start(), match.group()) for pattern in section_patterns for match in re.finditer(pattern, text)]
    positions.sort()  # Сортируем по начальной позиции
    
    # Извлекаем текст каждой секции
    for i, (start_pos, section_name) in enumerate(positions):
        if i < len(positions) - 1:
            end_pos = positions[i + 1][0]
        else:
            end_pos = len(text)
        
        sections[section_name] = text[start_pos:end_pos].strip()
    
    return sections 

cleaned_text_file = 'cleaned_text.txt'

sections = find_main_sections(cleaned_text_file)


def find_capitulos(sections: Dict[str, str]) -> Dict[str, Any]:
    """
    Находит все CAPÍTULO в тексте и создает структуру.
    
    Args:
        sections (Dict[str, str]): Словарь с названиями секций и их текстами.
    
    Returns:
        Dict[str, Any]: Словарь с названиями секций и их текстами.
    """
    structure = {}
    for section_name, section_text in sections.items():
        
        structure[section_name] = {}
        if section_name == 'TÍTULO PRELIMINAR':
            print('Working on section:', section_name)
            # находим все CAPÍTULO в тексте может быть римская цирфра или слова PRIMERO
            capitulos = list(re.finditer(r'CAPÍTULO\s+[IVX]+|CAPÍTULO\s+PRIMERO', section_text))
            for i, capitulo_match in enumerate(capitulos):
                capitulo_name = capitulo_match.group()
                capitulo_start = capitulo_match.end()
                if i < len(capitulos) - 1:
                    capitulo_end = capitulos[i + 1].start()
                else:
                    capitulo_end = len(section_text)
                capitulo_text = section_text[capitulo_start:capitulo_end].strip()
                structure[section_name][capitulo_name] = capitulo_text
                print(f"{capitulo_name}: {len(capitulo_text)} символов")
        else:
            print('Working on section:', section_name)
            titulos = list(re.finditer(r'TÍTULO\s+[IVX]+|TÍTULO\s+PRIMERO', section_text))
            for i, titulo_match in enumerate(titulos):
                titulo_name = titulo_match.group()
                titulo_start = titulo_match.end()
                if i < len(titulos) - 1:
                    titulo_end = titulos[i + 1].start()
                else:
                    titulo_end = len(section_text)
                titulo_text = section_text[titulo_start:titulo_end].strip()
                structure[section_name][titulo_name] = {}

                capitulos = list(re.finditer(r'CAPÍTULO\s+[IVX]+|CAPÍTULO\s+PRIMERO', titulo_text))
                for j, capitulo_match in enumerate(capitulos):
                    capitulo_name = capitulo_match.group()
                    capitulo_start = capitulo_match.end()
                    if j < len(capitulos) - 1:
                        capitulo_end = capitulos[j + 1].start()
                    else:
                        capitulo_end = len(titulo_text)
                    capitulo_text = titulo_text[capitulo_start:capitulo_end].strip()
                    structure[section_name][titulo_name][capitulo_name] = capitulo_text
                    print(f"{capitulo_name}: {len(capitulo_text)} символов")

    return structure


def split_into_chunks(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Разбивает текст на чанки с перекрытием, учитывая списки.
    
    Args:
        text (str): Текст для разбиения.
        max_chunk_size (int): Максимальный размер чанка.
        overlap (int): Размер перекрытия между чанками.
    
    Returns:
        List[str]: Список чанков текста.
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + max_chunk_size, text_length)
        
        # Ищем конец последнего полного слова в диапазоне
        last_space = text.rfind(' ', start, end)
        if last_space != -1:
            end = last_space
        
        # Ищем ближайший конец предложения
        last_period = max(text.rfind('.', start, end), text.rfind('!', start, end), text.rfind('?', start, end))
        if last_period != -1 and (end - last_period) < 100:
            end = last_period + 1
        
        # Проверяем, не разрываем ли мы список
        if ':' in text[start:end]:
            list_start = text.find(':', start, end)
            list_end = text.find('\n', list_start, end)
            if list_end != -1:
                end = list_end + 1
        
        chunks.append(text[start:end].strip())
        
        # Начинаем следующий чанк с учетом перекрытия
        start = end - overlap
    
    return chunks


def create_chunks_for_structure(structure: Dict[str, Any], max_chunk_size: int = 1000, overlap: int = 100) -> Dict[str, Any]:
    """
    Создает чанки для каждой главы в структуре и добавляет их в структуру.
    
    Args:
        structure (Dict[str, Any]): Иерархическая структура документа.
        max_chunk_size (int): Максимальный размер чанка.
        overlap (int): Размер перекрытия между чанками.
    
    Returns:
        Dict[str, Any]: Структура с чанками текста.
    """
    structure_with_chunks = {}
    
    for section_name, section_data in structure.items():
        structure_with_chunks[section_name] = {}
        
        if section_name == 'TÍTULO PRELIMINAR':
            # Обработка структуры TÍTULO PRELIMINAR => CAPÍTULO
            for capitulo_name, capitulo_text in section_data.items():
                chunks = split_into_chunks(capitulo_text, max_chunk_size, overlap)
                structure_with_chunks[section_name][capitulo_name] = {
                    "text": capitulo_text,
                    "chunks": chunks,
                    "total_chunks": len(chunks)
                }
                print(f"{capitulo_name}: разбит на {len(chunks)} чанков")
        else:
            # Обработка структуры LIBRO => TÍTULO => CAPÍTULO
            for titulo_name, titulo_data in section_data.items():
                structure_with_chunks[section_name][titulo_name] = {}
                
                for capitulo_name, capitulo_text in titulo_data.items():
                    chunks = split_into_chunks(capitulo_text, max_chunk_size, overlap)
                    structure_with_chunks[section_name][titulo_name][capitulo_name] = {
                        "text": capitulo_text,
                        "chunks": chunks,
                        "total_chunks": len(chunks)
                    }
                    print(f"{capitulo_name}: разбит на {len(chunks)} чанков")
    
    return structure_with_chunks


def create_flat_chunks_list(structure_with_chunks: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Создает плоский список чанков с метаданными.
    
    Args:
        structure_with_chunks (Dict[str, Any]): Структура документа с чанками.
    
    Returns:
        List[Dict[str, Any]]: Плоский список чанков с метаданными.
    """
    flat_chunks = []
    
    for section_name, section_data in structure_with_chunks.items():
        if section_name == 'TÍTULO PRELIMINAR':
            # Обработка структуры TÍTULO PRELIMINAR => CAPÍTULO
            for capitulo_name, capitulo_data in section_data.items():
                for chunk_index, chunk_text in enumerate(capitulo_data["chunks"]):
                    flat_chunks.append({
                        "section": section_name,
                        "titulo": "",  # У TÍTULO PRELIMINAR нет подразделов TÍTULO
                        "capitulo": capitulo_name,
                        "chunk_index": chunk_index,
                        "total_chunks": capitulo_data["total_chunks"],
                        "text": chunk_text
                    })
        else:
            # Обработка структуры LIBRO => TÍTULO => CAPÍTULO
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data.items():
                    for chunk_index, chunk_text in enumerate(capitulo_data["chunks"]):
                        flat_chunks.append({
                            "section": section_name,
                            "titulo": titulo_name,
                            "capitulo": capitulo_name,
                            "chunk_index": chunk_index,
                            "total_chunks": capitulo_data["total_chunks"],
                            "text": chunk_text
                        })
    
    print(f"\nСоздан плоский список из {len(flat_chunks)} чанков с метаданными")
    return flat_chunks


def save_chunks_to_json(flat_chunks: List[Dict[str, Any]], output_file: str) -> None:
    """
    Сохраняет плоский список чанков с метаданными в JSON файл.
    
    Args:
        flat_chunks (List[Dict[str, Any]]): Плоский список чанков с метаданными.
        output_file (str): Имя выходного файла.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flat_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"Чанки с метаданными сохранены в файл: {output_file}")


def main():
    """
    Основная функция для выполнения всего процесса.
    """
    # Шаг 1: Находим основные секции
    sections = find_main_sections(cleaned_text_file)
    
    # Шаг 2: Находим главы в каждой секции
    structure = find_capitulos(sections)
    
    # Шаг 3: Разбиваем текст каждой главы на чанки
    structure_with_chunks = create_chunks_for_structure(structure)
    
    # Шаг 4: Создаем плоский список чанков с метаданными
    flat_chunks = create_flat_chunks_list(structure_with_chunks)
    
    # Шаг 5: Сохраняем чанки с метаданными в JSON файл
    save_chunks_to_json(flat_chunks, 'chunks_with_metadata.json')
    
    print("\nОбработка завершена. Результаты готовы для создания эмбеддингов.")


if __name__ == "__main__":
    main()


