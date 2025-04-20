import json

input_path = "structure_with_text.json"
output_path = "codigo_civil.ndjson"

with open(input_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

with open(output_path, "w", encoding="utf-8") as f:
    for article in articles:
        f.write(json.dumps(article, ensure_ascii=False) + "\n")

print(f"NDJSON для эластика сохранён в {output_path}")