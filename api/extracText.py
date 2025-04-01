import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Укажи путь к твоему PDF
pdf_path = "Codigo_Civil.pdf"  # Замени на путь к твоему PDF
text = extract_text_from_pdf(pdf_path)

# Сохрани текст в файл
with open("extracted_laws.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Текст извлечён и сохранён в extracted_laws.txt")