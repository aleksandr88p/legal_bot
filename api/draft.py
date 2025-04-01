import pdfplumber
import time


def extract_text_with_pdfplumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            if i < 19:
                continue
            # for page in pdf.pages:
            text += page.extract_text().lower() + "\n"
            print(text)
            if i == 21:
                break
    return text

pdf_path = "Codigo_Civil.pdf"  # Укажи путь к твоему PDF
text = extract_text_with_pdfplumber(pdf_path)

# with open("extracted_laws_cleaned.txt", "w", encoding="utf-8") as f:
#     f.write(text)

print("Текст извлечён и сохранён в extracted_laws_cleaned.txt")