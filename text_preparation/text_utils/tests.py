import json
import re

# Путь к файлу с результатом структуры
structure_path = "structure_with_text.json"

def extract_article_number(articulo):
    """Извлекает номер статьи как int (например, '115.' -> 115)"""
    if articulo is None:
        return None
    match = re.match(r"(\d+)", articulo)
    if match:
        return int(match.group(1))
    return None

def find_article_gaps(structure):
    last_num = None
    last_info = None
    gaps = []

    for entry in structure:
        articulo = entry.get("articulo")
        num = extract_article_number(articulo)
        if num is not None:
            if last_num is not None and num != last_num + 1:
                gaps.append({
                    "prev_articulo": last_num,
                    "next_articulo": num,
                    "missed_count": num - last_num - 1,
                    "context": {
                        "libro": entry.get("libro"),
                        "titulo": entry.get("titulo"),
                        "capitulo": entry.get("capitulo"),
                    }
                })
            last_num = num
            last_info = entry
    return gaps

if __name__ == "__main__":
    with open(structure_path, "r", encoding="utf-8") as f:
        structure = json.load(f)
    gaps = find_article_gaps(structure)
    if gaps:
        print("Обнаружены пропуски статей:")
        for gap in gaps:
            print(
                f"После статьи {gap['prev_articulo']} сразу идет {gap['next_articulo']} "
                f"(пропущено {gap['missed_count']}) "
                f"в LIBRO: {gap['context']['libro']}, "
                f"TITULO: {gap['context']['titulo']}, "
                f"CAPITULO: {gap['context']['capitulo']}"
            )
    else:
        print("Пропусков статей не найдено.")