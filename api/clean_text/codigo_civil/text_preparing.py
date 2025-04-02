import re
import logging


input_file = 'extracted_laws_fitz2.txt'
cleaned_text = 'cleaned_text.txt'


def clean_basic_text(input_file: str, output_file: str) -> None:
    '''
    Очищает текст от лишних символов и форматирует его для удобочитаемости.    
    ''' 
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # заменю перенос строки, знаки равенства и еще один перенос строки, на просто перенос строки
    text = re.sub(r'\n=+\n', '\n', text)
    
    # заменю три и более переноса строки, на два переноса строки
    text = re.sub(r'\n\n\n+', '\n\n', text)

    # замею два и более пробела, на один пробел
    text = re.sub(r'\s{2,}', ' ', text)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    logging.info(f'Text cleaned and saved to {output_file}')
    
    

# clean_basic_text(input_file, cleaned_text)

# найду начало и конец основных секций  
def find_main_sections(input_file:str) -> dict:
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

    #LIBROS
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

def check_capitulo_text_length(structure):
    """
    Выводит информацию о длине текста в каждой главе (CAPÍTULO)
    """
    print("\nДлина текста в каждой главе:")
    
    # Для TÍTULO PRELIMINAR
    print("\nTÍTULO PRELIMINAR:")
    for capitulo_name, capitulo_data in structure['TÍTULO PRELIMINAR'].items():
        capitulo_text = capitulo_data["text"]
        print(f"  {capitulo_name}: {len(capitulo_text)} символов")
    
    # Для каждой LIBRO
    for section_name in structure:
        if section_name != 'TÍTULO PRELIMINAR':
            print(f"\n{section_name}:")
            for titulo_name, titulo_data in structure[section_name].items():
                print(f"  {titulo_name}:")
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    capitulo_text = capitulo_data["text"]
                    print(f"    {capitulo_name}: {len(capitulo_text)} символов")



# def find_articles(structure: dict) -> dict:
#     """
#     Находит и извлекает статьи внутри каждой главы (CAPÍTULO)
    
#     Args:
#         structure (dict): иерархическая структура документа
    
#     Returns:
#         dict: структура со всеми статьями
#     """
#     print("\nПоиск статей...")
#     article_count = 0
#     article_lengths = []
    
#     # Перебираем все секции
#     for section_name, section_data in structure.items():
#         print(f"Поиск статей в: {section_name}")
        
#         # Для TÍTULO PRELIMINAR обрабатываем CAPÍTULO напрямую
#         if section_name == 'TÍTULO PRELIMINAR':
#             for capitulo_name, capitulo_data in section_data.items():
#                 capitulo_text = capitulo_data["text"]
                
#                 # Ищем статьи - числа за которыми следует точка и текст
#                 articles = re.finditer(r'(\d+)\.\s+([^\n]+(?:\n[^\d\n][^\n]+)*)', capitulo_text)
                
#                 for article_match in articles:
#                     article_num = article_match.group(1)
#                     article_text = article_match.group(2).strip()
                    
#                     structure[section_name][capitulo_name]["articles"][article_num] = article_text
#                     article_count += 1
#                     article_lengths.append(len(article_text))
        
#         # Для LIBRO обрабатываем вложенные TÍTULO и CAPÍTULO
#         else:
#             for titulo_name, titulo_data in section_data.items():
#                 for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
#                     capitulo_text = capitulo_data["text"]
                    
#                     # Ищем статьи
#                     articles = re.finditer(r'(\d+)\.\s+([^\n]+(?:\n[^\d\n][^\n]+)*)', capitulo_text)
                    
#                     for article_match in articles:
#                         article_num = article_match.group(1)
#                         article_text = article_match.group(2).strip()
                        
#                         structure[section_name][titulo_name]["capitulos"][capitulo_name]["articles"][article_num] = article_text
#                         article_count += 1
#                         article_lengths.append(len(article_text))
    
#     # Выводим статистику по статьям
#     if article_lengths:
#         avg_length = sum(article_lengths) / len(article_lengths)
#         min_length = min(article_lengths)
#         max_length = max(article_lengths)
#         print(f"Всего найдено статей: {article_count}")
#         print(f"Средняя длина статьи: {avg_length:.2f} символов")
#         print(f"Минимальная длина: {min_length} символов")
#         print(f"Максимальная длина: {max_length} символов")
#     else:
#         print("Статьи не найдены!")
    
#     return structure


def find_articles(structure: dict) -> dict:
    """
    Находит и извлекает статьи внутри каждой главы (CAPÍTULO)
    """
    print("\nПоиск статей...")
    article_count = 0
    article_lengths = []
    
    # Регулярное выражение для поиска статей
    # Старое выражение: r'(\d+)\.\s+([^\n]+(?:\n[^\d\n][^\n]+)*)'
    # Новое улучшенное выражение:
    article_pattern = r'(\d+)\.\s+([^\n]+(?:\n[^\d\n][^\n]+)*?)(?=\n\d+\.\s+|\Z)'
    
    # Дополнительное регулярное выражение для фильтрации плохих статей
    bad_article_pattern = r'^\[\…….+\]\s*\d*\.*$'
    
    # Перебираем все секции
    for section_name, section_data in structure.items():
        print(f"Поиск статей в: {section_name}")
        
        # Для TÍTULO PRELIMINAR обрабатываем CAPÍTULO напрямую
        if section_name == 'TÍTULO PRELIMINAR':
            for capitulo_name, capitulo_data in section_data.items():
                capitulo_text = capitulo_data["text"]
                
                # Ищем статьи с улучшенным шаблоном
                articles = re.finditer(article_pattern, capitulo_text)
                
                for article_match in articles:
                    article_num = article_match.group(1)
                    article_text = article_match.group(2).strip()
                    
                    # Фильтруем статьи с [......]
                    if re.match(bad_article_pattern, article_text):
                        continue
                    
                    structure[section_name][capitulo_name]["articles"][article_num] = article_text
                    article_count += 1
                    article_lengths.append(len(article_text))
        
        # Для LIBRO обрабатываем вложенные TÍTULO и CAPÍTULO
        else:
            for titulo_name, titulo_data in section_data.items():
                for capitulo_name, capitulo_data in titulo_data["capitulos"].items():
                    capitulo_text = capitulo_data["text"]
                    
                    # Ищем статьи с улучшенным шаблоном
                    articles = re.finditer(article_pattern, capitulo_text)
                    
                    for article_match in articles:
                        article_num = article_match.group(1)
                        article_text = article_match.group(2).strip()
                        
                        # Фильтруем статьи с [......]
                        if re.match(bad_article_pattern, article_text):
                            continue
                            
                        structure[section_name][titulo_name]["capitulos"][capitulo_name]["articles"][article_num] = article_text
                        article_count += 1
                        article_lengths.append(len(article_text))
    
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



sections = find_main_sections(cleaned_text)
sections_text = extract_sections_text('cleaned_text.txt', sections)
structure = find_subsections(sections_text)
articles = find_articles(structure)


# Использование
check_short_articles(structure, min_length=50)  # Показать статьи короче 30 символов


