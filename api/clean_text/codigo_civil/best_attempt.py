import re
import json

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
    # Читаем весь текст
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Создаем словарь для хранения текстов секций
    sections_text = {}
    
    # Получаем список секций, отсортированный по позиции в тексте
    sorted_sections = sorted(sections.items(), key=lambda x: x[1])
    
    # Извлекаем текст каждой секции
    for i, (section_name, start_pos) in enumerate(sorted_sections):
        # Если это последняя секция, берем текст до конца
        if i == len(sorted_sections) - 1:
            sections_text[section_name] = text[start_pos:]
        else:
            # Иначе берем текст до начала следующей секции
            next_section_pos = sorted_sections[i + 1][1]
            sections_text[section_name] = text[start_pos:next_section_pos]
    
    # Выводим информацию о найденных секциях
    print("\nИзвлечены тексты следующих секций:")
    for section, content in sections_text.items():
        print(f"- {section}: {len(content)} символов")
    
    return sections_text

def find_subsections(sections_text: dict) -> dict:
    """
    Находит подразделы внутри основных секций:
    - TÍTULO внутри LIBRO
    - CAPÍTULO внутри TÍTULO
    - Статьи с номерами
    
    Args:
        sections_text (dict): словарь с текстами основных секций
    
    Returns:
        dict: иерархическая структура всего документа
    """
    # Создаем структуру для хранения иерархии документа
    structure = {}
    
    # Обрабатываем каждую секцию
    for section_name, section_text in sections_text.items():
        print(f"\nWorking on section: {section_name}")
        structure[section_name] = {}
        
        # Для TÍTULO PRELIMINAR ищем CAPÍTULO и статьи
        if section_name == 'TÍTULO PRELIMINAR':
            # Ищем все CAPÍTULO
            capitulos = list(re.finditer(r'CAPÍTULO\s+(?:PRIMERO|[IVX]+)', section_text))
            
            for i, capitulo_match in enumerate(capitulos):
                capitulo_name = capitulo_match.group()
                capitulo_start = capitulo_match.start()
                
                # Определяем где заканчивается этот CAPÍTULO
                if i < len(capitulos) - 1:
                    capitulo_end = capitulos[i+1].start()
                else:
                    capitulo_end = len(section_text)
                
                capitulo_text = section_text[capitulo_start:capitulo_end]
                print(f"  Capitulo found: {capitulo_name}")
                
                # Сохраняем текст CAPÍTULO
                structure[section_name][capitulo_name] = {
                    "text": capitulo_text,
                    "articles": {}  # Здесь будут статьи
                }
        
        # Для остальных (LIBRO) ищем TÍTULO, CAPÍTULO и статьи
        else:
            # Ищем все TÍTULO
            titulos = list(re.finditer(r'TÍTULO\s+(?:PRIMERO|[IVX]+)', section_text))
            
            for i, titulo_match in enumerate(titulos):
                titulo_name = titulo_match.group()
                titulo_start = titulo_match.start()
                
                # Определяем где заканчивается этот TÍTULO
                if i < len(titulos) - 1:
                    titulo_end = titulos[i+1].start()
                else:
                    titulo_end = len(section_text)
                
                titulo_text = section_text[titulo_start:titulo_end]
                print(f"  Titulo found: {titulo_name}")
                
                # Создаем структуру для этого TÍTULO
                structure[section_name][titulo_name] = {
                    "text": titulo_text,
                    "capitulos": {}
                }
                
                # Ищем все CAPÍTULO внутри этого TÍTULO
                capitulos = list(re.finditer(r'CAPÍTULO\s+(?:PRIMERO|[IVX]+)', titulo_text))
                
                for j, capitulo_match in enumerate(capitulos):
                    capitulo_name = capitulo_match.group()
                    capitulo_start = capitulo_match.start()
                    
                    # Определяем где заканчивается этот CAPÍTULO
                    if j < len(capitulos) - 1:
                        capitulo_end = capitulos[j+1].start()
                    else:
                        capitulo_end = len(titulo_text)
                    
                    capitulo_text = titulo_text[capitulo_start:capitulo_end]
                    print(f"    Capitulo found: {capitulo_name}")
                    
                    # Сохраняем текст CAPÍTULO
                    structure[section_name][titulo_name]["capitulos"][capitulo_name] = {
                        "text": capitulo_text,
                        "articles": {}  # Здесь будут статьи
                    }
    
    return structure

def improved_find_articles(structure: dict) -> dict:
    """
    Улучшенный алгоритм поиска и извлечения статей с обработкой особых случаев
    
    Args:
        structure (dict): иерархическая структура документа
    
    Returns:
        dict: структура со всеми корректно выделенными статьями
    """
    print("\nПоиск статей с улучшенным алгоритмом...")
    article_count = 0
    article_lengths = []
    
    # Паттерн для заголовков секций
    section_header_pattern = r'^Secci[óo]n\s+\d+\.?a?\s+'
    
    # Перебираем все секции
    for section_name, section_data in structure.items():
        print(f"Поиск статей в: {section_name}")
        
        # Для TÍTULO PRELIMINAR обрабатываем CAPÍTULO напрямую
        if section_name == 'TÍTULO PRELIMINAR':
            for capitulo_name, capitulo_data in section_data.items():
                capitulo_text = capitulo_data["text"]
                
                # Обрабатываем главу
                process_capitulo_for_articles(
                    capitulo_text,
                    structure[section_name][capitulo_name]["articles"],
                    section_header_pattern,
                    article_lengths
                )
                article_count += len(structure[section_name][capitulo_name]["articles"])
        
        # Для LIBRO обрабатываем вложенные TÍTULO и CAPÍTULO
        else:
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    capitulo_text = capitulo_data["text"]
                    
                    # Обрабатываем главу
                    process_capitulo_for_articles(
                        capitulo_text,
                        structure[section_name][titulo_name]["capitulos"][capitulo_name]["articles"],
                        section_header_pattern,
                        article_lengths
                    )
                    article_count += len(structure[section_name][titulo_name]["capitulos"][capitulo_name]["articles"])
    
    # Выводим статистику по статьям
    if article_lengths:
        avg_length = sum(article_lengths) / len(article_lengths)
        min_length = min(article_lengths)
        max_length = max(article_lengths)
        print(f"Всего найдено статей: {article_count}")
        print(f"Средняя длина статьи: {avg_length:.2f} символов")
        print(f"Минимальная длина: {min_length} символов")
        print(f"Максимальная длина: {max_length} символов")
    else:
        print("Статьи не найдены!")
    
    return structure

def process_capitulo_for_articles(capitulo_text, articles_dict, section_header_pattern, article_lengths):
    """
    Обрабатывает текст главы для извлечения статей с учетом особых случаев
    
    Args:
        capitulo_text (str): текст главы
        articles_dict (dict): словарь для хранения статей
        section_header_pattern (str): паттерн для заголовков секций
        article_lengths (list): список для хранения длин статей
    """
    # Регулярное выражение для поиска статей 
    article_matches = list(re.finditer(r'(\d+)\.\s+([^\n]+(?:\n(?!\d+\.)[^\n]+)*)', capitulo_text))
    
    for i, article_match in enumerate(article_matches):
        article_num = article_match.group(1)
        article_text = article_match.group(2).strip()
        
        # Пропускаем заголовки секций
        if re.match(section_header_pattern, article_text):
            continue
            
        # Пропускаем "плохие" статьи
        if re.match(r'^\[\…….+\]\s*\d*\.*$', article_text):
            continue
            
        # Если статья заканчивается двоеточием, попробуем найти пункты
        if article_text.endswith(':'):
            # Находим положение конца текущей статьи
            current_end = article_match.end()
            
            # Определяем начало следующей статьи (если есть)
            next_start = len(capitulo_text)
            if i < len(article_matches) - 1:
                next_start = article_matches[i+1].start()
                
            # Извлекаем текст между этой статьей и следующей
            points_text = capitulo_text[current_end:next_start].strip()
            
            # Ищем пронумерованные пункты
            points = re.findall(r'\d+\.º\s+([^\n]+(?:\n(?!\d+\.º)[^\n]+)*)', points_text)
            
            # Если нашли пункты, добавляем их к тексту статьи
            if points:
                article_text += "\n" + "\n".join([f"{i+1}. {point.strip()}" for i, point in enumerate(points)])
        
        # Сохраняем статью и длину
        articles_dict[article_num] = article_text
        article_lengths.append(len(article_text))

def create_flat_articles_list(structure: dict) -> list:
    """
    Создает плоский список статей с метаданными для эмбеддингов
    
    Args:
        structure (dict): иерархическая структура документа
    
    Returns:
        list: список статей с метаданными
    """
    articles_list = []
    
    # Перебираем все секции
    for section_name, section_data in structure.items():
        
        # Для TÍTULO PRELIMINAR
        if section_name == 'TÍTULO PRELIMINAR':
            for capitulo_name, capitulo_data in section_data.items():
                for article_num, article_text in capitulo_data["articles"].items():
                    articles_list.append({
                        "libro": section_name,
                        "titulo": "",
                        "capitulo": capitulo_name,
                        "article": article_num,
                        "text": article_text
                    })
        
        # Для LIBRO
        else:
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    for article_num, article_text in capitulo_data["articles"].items():
                        articles_list.append({
                            "libro": section_name,
                            "titulo": titulo_name,
                            "capitulo": capitulo_name,
                            "article": article_num,
                            "text": article_text
                        })
    
    print(f"Создан плоский список из {len(articles_list)} статей для эмбеддингов")
    return articles_list

def save_articles_to_json(articles_list: list, output_file: str):
    """
    Сохраняет список статей в JSON-файл
    
    Args:
        articles_list (list): список статей с метаданными
        output_file (str): путь для сохранения
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles_list, f, ensure_ascii=False, indent=2)
    
    print(f"Статьи сохранены в файл: {output_file}")

def check_short_articles(structure, min_length=50):
    """
    Выводит список слишком коротких статей для проверки
    
    Args:
        structure (dict): иерархическая структура документа
        min_length (int): минимальная ожидаемая длина статьи
    """
    print(f"\nСтатьи короче {min_length} символов:")
    found = 0
    
    # Перебираем все секции
    for section_name, section_data in structure.items():
        
        # Для TÍTULO PRELIMINAR
        if section_name == 'TÍTULO PRELIMINAR':
            for capitulo_name, capitulo_data in section_data.items():
                for article_num, article_text in capitulo_data["articles"].items():
                    if len(article_text) < min_length:
                        print(f"\nСтатья {article_num} ({len(article_text)} символов):")
                        print(f"Раздел: {section_name}, Глава: {capitulo_name}")
                        print(f"Текст: '{article_text}'")
                        found += 1
        
        # Для LIBRO
        else:
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    for article_num, article_text in capitulo_data["articles"].items():
                        if len(article_text) < min_length:
                            print(f"\nСтатья {article_num} ({len(article_text)} символов):")
                            print(f"Раздел: {section_name}, Título: {titulo_name}, Глава: {capitulo_name}")
                            print(f"Текст: '{article_text}'")
                            found += 1
    
    if found == 0:
        print("Коротких статей не найдено.")
    else:
        print(f"\nВсего найдено {found} коротких статей.")

# Основная функция запуска
def main():
    print("Запуск улучшенного алгоритма обработки юридического текста...")
    
    # Шаг 1: Находим основные секции
    sections = find_main_sections(cleaned_text_file)
    
    # Шаг 2: Извлекаем текст каждой секции
    sections_text = extract_sections_text(cleaned_text_file, sections)
    
    # Шаг 3: Находим подразделы (TÍTULO, CAPÍTULO)
    structure = find_subsections(sections_text)
    
    # Шаг 4: Улучшенный поиск статей
    structure = improved_find_articles(structure)
    
    # Шаг 5: Создаем плоский список статей для эмбеддингов
    articles_list = create_flat_articles_list(structure)
    
    # Шаг 6: Сохраняем статьи в JSON
    save_articles_to_json(articles_list, 'articles_for_embeddings.json')
    
    # Проверка коротких статей
    check_short_articles(structure, min_length=30)
    
    print("\nОбработка завершена. Результаты готовы для создания эмбеддингов.")

if __name__ == "__main__":
    main() 