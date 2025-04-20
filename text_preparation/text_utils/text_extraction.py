import fitz
import json

civil_file = '../../DATA/Codigo_Civil.pdf'

def extract_text_from_pdf(pdf_path, page_num:int):
    """
    Extracts text from a specific page (19) of a PDF file using PyMuPDF (fitz).
    
    Args:
        pdf_path (str): The path to the PDF file.
        
    Returns:
        list: A list of dictionaries containing text and its style information.
    """
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    text_with_styles = []
    
      
    print(f"Processing page {page_num + 1} of {len(pdf_document)}")
    
    # Get the page
    page = pdf_document[page_num]
    
    # Extract text as a dictionary
    text_dict = page.get_text("dict")
    
    # Iterate over the "blocks" in the text dictionary
    for block in text_dict["blocks"]:
        # Process each line in the block
        for line in block["lines"]:
            for span in line["spans"]:
                # Each "span" contains a piece of text with its style
                text_with_styles.append({
                    "text": span["text"],             # Текст
                    "font": span["font"],             # Название шрифта
                    "size": span["size"],             # Размер шрифта
                    "color": span["color"],           # Цвет текста (RGB)
                    "bbox": span["bbox"],             # Координаты текста на странице
                })
    
    # Close the PDF document
    pdf_document.close()
    
    return text_with_styles

# page_num = 30
# Call the function for testing
# d = extract_text_from_pdf(civil_file, page_num=page_num)

# with open (f'civil{page_num}.json', 'w', encoding='utf-8') as f:
#     json.dump(d, f, indent=4, ensure_ascii=False)