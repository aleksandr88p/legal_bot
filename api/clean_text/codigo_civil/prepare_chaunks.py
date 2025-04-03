import re
from typing import Dict

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


def find_capitulos(sections: Dict[str, str]) -> Dict[str, any]:
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
                # print(capitulo_name, len(capitulo_text))
        else:
            print('Working on section:', section_name)
            titulos = list(re.finditer(r'TÍTULO\s+[IVX]+|TÍTULO\s+PRIMERO', section_text))
            for i, titulo_match in enumerate(titulos):
                titulo_name = titulo_match.group()
                # print(titulo_name)
                titulo_start = titulo_match.end()
                if i < len(titulos) - 1:
                    titulo_end = titulos[i + 1].start()
                else:
                    titulo_end = len(section_text)
                titulo_text = section_text[titulo_start:titulo_end].strip()
                # print(titulo_name, len(titulo_text))
                structure[section_name][titulo_name] = {}

                capitulos = list(re.finditer(r'CAPÍTULO\s+[IVX]+|CAPÍTULO\s+PRIMERO', titulo_text))
                for j, capitulo_match in enumerate(capitulos):
                    capitulo_name = capitulo_match.group()
                    # print(capitulo_name)
                    capitulo_start = capitulo_match.end()
                    if j < len(capitulos) - 1:
                        capitulo_end = capitulos[j + 1].start()
                    else:
                        capitulo_end = len(titulo_text)
                    capitulo_text = titulo_text[capitulo_start:capitulo_end].strip()
                    print(capitulo_name, len(capitulo_text))

    return structure



structure = find_capitulos(sections)

