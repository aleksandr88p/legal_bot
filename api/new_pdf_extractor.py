import pdfplumber

def extract_text_with_pdfplumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

pdf_path = "Codigo_Civil.pdf"  # Укажи путь к твоему PDF
text = extract_text_with_pdfplumber(pdf_path)

with open("extracted_laws_cleaned.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Текст извлечён и сохранён в extracted_laws_cleaned.txt")