import fitz   
import re  

doc = fitz.open("Codigo_Civil.pdf")

with open("extracted_laws_fitz2.txt", "w", encoding="utf-8") as output_file:
    # Начинаем с 19-й страницы (индекс 18)
    start_page = 18  
    
    for page_num in range(start_page, len(doc)):
        # Получаем страницу
        page = doc[page_num]
        
        text = page.get_text()
    
        # Удаляем номер страницы в начале (если есть)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Удаляем сноски (они обычно в конце страницы)
        # Ищем сноски, начинающиеся с определенных слов
        text = re.sub(r'\n\s*(Artículo|Redactado|Modificado).*?(octubre|diciembre|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre).*?\n', '\n', text, flags=re.DOTALL)
        
        output_file.write(text)
        
        output_file.write("\n" + "=" * 30 + "\n")
        
        print(f"Обработана страница {page_num + 1}")

doc.close()

print("Текст успешно сохранен в файл 'extracted_laws_fitz2.txt'")
