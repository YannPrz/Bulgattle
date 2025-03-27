"""
--------------------------------------------------------------------------------
Author: Camille Solacroup
Date: 2025-03-24
Description:
    This script extracts text from EQE Paper D PDF documents and saves them as
    text files. It processes different types of documents, including questions
    and answers, while cleaning and formatting the extracted content.
--------------------------------------------------------------------------------
"""

import fitz 
import re
import os



# Input and output directories
input_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/EQE Exams/02-Paper D"
output_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/EQE Exams/02-Paper D"

# Ensure output directories exist
os.makedirs(output_folder, exist_ok=True)



def extract_text_from_pdf_PaperD_answers(pdf_path: str) -> str:
    """
    Extracts and cleans text from a given EQE Paper D answers PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        str: The cleaned and formatted extracted text.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for i, page in enumerate(doc):
        if i == 0:
            continue

        page_text = page.get_text("text")

        #2024
        page_text = re.sub(r"Question (\d+)\s*\(\d+\s*marks\)", r"Question \1", page_text)
        page_text = re.sub(r"\s*\n?", '• ', page_text)

        #2023
        page_text = re.sub(r'(?m)^\s+\n', '', page_text)
        page_text = re.sub(r"^\d+ \n", '', page_text) 
        page_text = re.sub(r"(\n\d+\.)\s*\n+", r"\1 ", page_text)  
        page_text = re.sub(r"(Answer to Question \d+):\s*", r"\1\n", page_text)
        page_text = re.sub(r"(Question \d+)\.\s*", r"\1\n", page_text)
        page_text = re.sub(r"Possible Solution – Paper D \d{4}, Part [IVXLCDM]+\s*\n", "", page_text)


        #2021
        page_text = re.sub(r"- \d+ - ", r"", page_text)  

        full_text += page_text 

    # Extract questions and answers separately for better readability
    pattern = r'(?m)Question \d+\s*.*?(?=\nQuestion \d+|\Z)'
    questions = re.findall(pattern, full_text, flags=re.DOTALL)

    pattern_bis = r'(?m)^\s*Answer to Question \d+\s*.*?(?=\nAnswer to Question \d+|\Z)'
    answers = re.findall(pattern_bis, full_text, flags=re.DOTALL)
    
    full_text = "\n\n\n\n".join(questions + answers)

    #2024
    full_text = re.sub(r"-\s*\n", "- ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"→\s*\n", "→ ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"(Question \d) ([a-zA-Z]) ", r"\1\n\2", full_text, flags=re.DOTALL)
    full_text = re.sub(r"\b([a-zA-Z])\)\n", r"\1) ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"Examiners’ Report – Paper D \d{4}, Part (I{1,3}|IV|V|VI{0,3}|X)\s*\n", "", full_text, flags=re.DOTALL)
    
    #2023
    full_text = re.sub(r"\(([a-zA-Z])\)\s*\n", r"(\1) ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"(?<!\n{3})(\nAnswer to Question \d+)", r"\n\n\n\1", full_text, flags=re.DOTALL)
    full_text = re.sub(r"(?<!\n{3})(\nQuestion \d+\s*\n)", r"\n\n\n\1", full_text, flags=re.DOTALL)

    #2022
    full_text = re.sub(r'1\nD1-1 \nMax \nAwarded.*?.*', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r"([a-zA-Z&&[^IVXLCDM]])\s*\n([a-zA-Z&&[^IVXLCDM]])", r"\1 \2", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([a-zA-Z],)\s*\n([a-zA-Z])", r"\1 \2", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([a-zA-Z])\s*\n([a-z])", r"\1 \2", full_text, flags=re.DOTALL)

    #2021
    full_text = re.sub(r' Examination Committee III: Paper D - Marking Details - Candidate No \n?.*', '', full_text, flags=re.DOTALL)

    return full_text



def extract_text_from_pdf_PaperD_questions(pdf_path: str) -> str:
    """
    Extracts and cleans text from a given EQE Paper D questions PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        str: The cleaned and formatted extracted text.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for i, page in enumerate(doc):
        
        page_text = page.get_text("text")

        #2024
        page_text = re.sub(r"\s*\n?", '• ', page_text)
        page_text = re.sub(r"Paper D2\s*\nThis paper comprises:", '', page_text)   
        page_text = re.sub(r"\(\d+\s*marks\)", r"", page_text)
        page_text = re.sub(r"Part II: Legal Opinion\s*\n", r"", page_text)
        
        #2023
        page_text = re.sub(r"\(\d+\s*points\)", r"", page_text)
        page_text = re.sub(r"\n\d-\d", r"", page_text)
        page_text = re.sub(r"\d{4}/D/EN/\d+\n", '', page_text)
        page_text = re.sub(r"━\s*\n?", '- ', page_text)
        page_text = re.sub(r"^Questions:\s*\n", '', page_text)
        page_text = re.sub(r"\n(\d+)\)", r'\n\1.', page_text)
        page_text = re.sub(r"\n\((\d+)\)", r'\n\1.', page_text)

        #2022
        page_text = re.sub(r"\d{4}/D/EN\n", '', page_text)

        #2021
        page_text = re.sub(r"• (Questions 1-4)\s*50 points", r"\1", page_text)
        page_text = re.sub(r"\d{4}/D2/EN\n", '', page_text)
        page_text = re.sub(r"\d{4}/D2/EN/\d+\n", '', page_text)
        
        full_text += page_text 

    #2024
    full_text = re.sub(r'EN\nEUROPEAN QUALIFYING EXAMINATION \d{4}\s*\n', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r"(\n\d+\.)\s*", r"\n\1 ", full_text, flags=re.DOTALL)

    #2022
    full_text = re.sub(r"\(([a-zA-Z])\)\n", r"(\1) ", full_text, flags=re.DOTALL)
    
    return full_text



def extract_text_from_pdf_PaperD_questions_D11_D12(pdf_path: str) -> str:
    """
    Extracts and cleans text from a given EQE Paper D1-1 and D1-2 questions PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        str: The cleaned and formatted extracted text.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for i, page in enumerate(doc):
        
        page_text = page.get_text("text")

        #2024D1-1
        page_text = re.sub(r"QUESTION (\d+)\n\s*\(\d+\s*MARKS\)", r"Question \1", page_text)

        #2023D1-1
        page_text = re.sub(r"\s*\n?", '', page_text)

        #2023D1-2
        page_text = re.sub(r"\d{4}/D/EN/\d+\n", '', page_text)

        #2022D1-1
        page_text = re.sub(r"(\n\d+\.)\s*\n+", r"\1 ", page_text)  

        #2021D1-1
        page_text = re.sub(r"QUESTION (\d+) \n\s*\n\s*\(\d+\s*MARKS\)", r"Question \1", page_text)
        page_text = re.sub(r"QUESTION (\d+) \n\s*\(\d+\s*MARKS\)", r"Question \1", page_text)
        page_text = re.sub(r"\d{4}/D1-1/EN/\d+\n", '', page_text)

        #2021D1-2
        page_text = re.sub(r"\d{4}/D1-2/EN/\d+\n", '', page_text)
        page_text = re.sub(r"\n\((\d+)\)", r'\n\1.', page_text)

        full_text += page_text 
            
    pattern = r'(?m)Question \d+\s*$.*?(?=\nQuestion \d+|\Z)'
    questions = re.findall(pattern, full_text, flags=re.DOTALL)
    full_text = "\n\n\n\n".join(questions)

    #2021D1-2
    full_text = re.sub(r"(\n\([a-z]\))\s*\n", r"\n\1 ", full_text, flags=re.DOTALL)
    
    #2021D1-1
    full_text = re.sub(r"(\n\d+\.)\s*", r"\n\1 ", full_text, flags=re.DOTALL)

    #2021D1-2
    full_text = re.sub(r"(?<!\n)(\n\([a-z]\))", r"\n\1", full_text, flags=re.DOTALL)
    
    return full_text



for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)

    if filename.endswith("_PaperD_Answers.pdf") | filename.endswith("_PaperD_answers_EN.pdf") | filename.endswith("_PaperD_answers.pdf") | filename.endswith("_PaperD_Answers.pdf"):
        extracted_text = extract_text_from_pdf_PaperD_answers(file_path)
    elif filename.endswith("_PaperD2_questions_EN.pdf"):
        extracted_text = extract_text_from_pdf_PaperD_questions(file_path)
    elif filename.endswith("_PaperD1-1_questions_EN.pdf")|filename.endswith("_PaperD1-2_questions_EN.pdf"):
        extracted_text = extract_text_from_pdf_PaperD_questions_D11_D12(file_path)
    else:
        continue 

    output_filename = filename.replace(".pdf", ".txt").replace(".html", ".txt")
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(extracted_text)

    print(f"Extraction completed for: {filename} → {output_filename}")

print("Extraction completed for all files.")