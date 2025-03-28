"""
--------------------------------------------------------------------------------
Author: Camille Solacroup
Date: 2025-03-23
Description: 
    This script extracts and cleans text from PDF and HTML files containing 
    EQE Pre-Exam questions and answers. The extracted text is saved in a 
    structured format for further processing.
--------------------------------------------------------------------------------
"""

import fitz 
import re
import os
from bs4 import BeautifulSoup



# Define input and output folders
input_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/EQE Exams/01-Pre-Examen"
output_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/EQE Exams/01-Pre-Examen"

os.makedirs(output_folder, exist_ok=True)



def extract_text_from_pdf_PreEx_answers(pdf_path: str) -> str:
    """
    Extracts and cleans text from a Pre-Exam answers PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        str: Extracted and cleaned text.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        
        page_text = page.get_text("text")

        # Cleaning patterns for different years
        #2024
        page_text = re.sub(r'(?m)^\s+\n', '', page_text)
        page_text = re.sub(r"^\d+ \n", '', page_text)    
        page_text = re.sub(r"^Examiners’ Report Pre-examination \d{4} \n", '', page_text)
        page_text = re.sub(r"PART \d+\s*\n", '', page_text)    
        page_text = re.sub(r"(\n\d+\.\d+)\s*\n+", r"\1 ", page_text)
        page_text = re.sub(r"(\n\d+\.\d+) \s*", r"\n\1 ", page_text)
        page_text = re.sub(r"(\n\d+\.\d+)\s*-\s*", r"\1 ", page_text)
        page_text = re.sub(r"(\n\d+\.\d+)\s*–\s*", r"\1 ", page_text)

        #2023
        page_text = re.sub(r"(TRUE:)\s*\n", r"\1 ", page_text)
        page_text = re.sub(r"(FALSE:)\s*\n", r"\1 ", page_text)

        #2018
        page_text = re.sub(r"Page \d+ of \d+\n", '', page_text)   
        page_text = re.sub(r"\n\d+/\d+\n", '', page_text)   

        #2019
        page_text = re.sub(r"\d+ of \d+\n", '', page_text)  
        page_text = re.sub(r"(?<![\n])(Question \d+)\s*", r"\n\1\n", page_text)   
        page_text = re.sub(r"QUESTION (\d+)\s*\n", r"Question \1 \n", page_text)   
        page_text = re.sub(r"QUESTION (\d+):\s*\n", r"Question \1 \n", page_text)   

        page_text = re.sub(r"- \d+ -\s*\n", "", page_text)   

        full_text += page_text 
        
    # Extract questions
    pattern = r'(?m)Question \d+\s*\n.*?(?=\nQuestion \d+\s*\n|\Z)'
    questions = re.findall(pattern, full_text, flags=re.DOTALL)
    full_text = "\n\n\n\n".join(questions)

    # Additional cleaning
    #2024
    full_text = re.sub(r'EN\nEUROPEAN QUALIFYING EXAMINATION \d{4}.*', '', full_text, flags=re.DOTALL)
    
    #2023
    full_text = re.sub(r'WAHR:.*?(\n\d+\.\d+|\n\n\nQuestion \d+ )', r'\1', full_text, flags=re.DOTALL)
    full_text = re.sub(r'FALSCH:.*?(\n\d+\.\d+|\n\n\nQuestion \d+ )', r'\1', full_text, flags=re.DOTALL)
    full_text = re.sub(r'WAHR:.*?.*', '', full_text, flags=re.DOTALL)

    full_text = re.sub(r"(\n\d+\.\d+)\s*\n+", r"\1 ", full_text, flags=re.DOTALL)
    

    return full_text



def extract_text_from_pdf_PreEx_questions(pdf_path: str) -> str:
    """
    Extracts and cleans text from a Pre-Exam questions PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        str: Extracted and cleaned text.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        
        page_text = page.get_text("text")

        # Cleaning patterns for different years
        #2022
        page_text = re.sub(r"(\nQuestion \d+):", r"\1", page_text)   

        page_text = re.sub(r'(?m)^\s+\n', '', page_text)
        page_text = re.sub(r"^\d+ \n", '', page_text)    
        page_text = re.sub(r"\d{4}/P/EN\n", '', page_text)
        page_text = re.sub(r"Page \d+ of \d+\n", '', page_text) 
        page_text = re.sub(r"(\n\d+\.\d+)\s*\n+", r"\1 ", page_text)
        page_text = re.sub(r"Part \d+\s*\n", '', page_text)
        page_text = re.sub(r"-\n", r"", page_text)
        
        #2021
        page_text = re.sub(r"\d{4}/P/EN/\d+\s*\n", '', page_text)
        

        #2019
        page_text = re.sub(r"Legal questions\s*\n", "", page_text)
        page_text = re.sub(r"\n\d{4}/P/EN/\d+", '', page_text)
        page_text = re.sub(r"^Claims analysis\s*\n", "", page_text)
        page_text = re.sub(r"^Claim analysis\s*\n", "", page_text)


        #2016
        page_text = re.sub(r"Page \d+ of \d+ \n", '', page_text) 
        page_text = re.sub(r"\d{4}/PE/EN \n", '', page_text)

        #2015
        page_text = re.sub(r"QUESTION (\d+)\s*\n", r"Question \1 \n", page_text) 

        full_text += page_text 
        
    # Extract questions
    pattern = r'(?m)Question \d+\s*\n.*?(?=\nQuestion \d+\s*\n|\Z)'
    questions = re.findall(pattern, full_text, flags=re.DOTALL)
    full_text = "\n\n\n\n".join(questions)

    # Additional cleaning
    #2022
    full_text = re.sub(r"(\n\d+\.\d+)\s*", r"\n\1 ", full_text, flags=re.DOTALL)
    
    #2021
    full_text = re.sub(r"(?<!\n)(For each of the statements)", r"\n\1", full_text, flags=re.DOTALL)
    
    #2019
    full_text = re.sub(r"\(([a-zA-Z])\)\s*\n", r"(\1) ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([IVXLCDM]+\.\d+)\n", r"\1 ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([IVXLCDM]-\d+\.)\s*\n", r"\1 ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([IVXLCDM]-\d+\.)\s*", r"\1 ", full_text, flags=re.DOTALL)
    full_text = re.sub(r'\bAnnexes?\b\n?.*', '', full_text, flags=re.DOTALL)

    #2018
    full_text = re.sub(r'Annex 1*\n?.*', '', full_text, flags=re.DOTALL)

    #2016
    full_text = re.sub(r"- \n", "- ", full_text, flags=re.DOTALL)

    #2015
    full_text = re.sub(r"([IVXLCDM]+\.\d+\.) \n", r"\1 ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"(\n[a-zA-Z]\))\s*\n", r"\1 ", full_text, flags=re.DOTALL)

    #2014
    full_text = re.sub(r"([IVXLCDM]+\.\d+) \n", r"\1 ", full_text, flags=re.DOTALL)

    full_text = re.sub(r"(\n\d+\.)\s*\n", r"\n\1 ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"(?<!\n)(\n\d+\.\d+)\s*", r"\n\1 ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"QUESTIONS (14-20)", r"\n\n\nQuestions \1 ", full_text, flags=re.DOTALL)

    return full_text



def extract_text_from_html_PreEx_questions_2024(html_path: str) -> str:
    """
    Extracts text from a Pre-Exam 2024 questions HTML file.

    Args:
        html_path (str): Path to the input HTML file.

    Returns:
        str: Extracted and formatted text.
    """
    with open(file_path, "rb") as file: 
        raw_data = file.read()
        decoded_data = raw_data.decode("utf-8", errors="replace")  
        soup = BeautifulSoup(decoded_data, "html.parser")

    extracted_text = ""

    for question_block in soup.find_all("div", class_="question-block"):
        question_title = question_block.find("div", class_="question-title").get_text(strip=True)
        extracted_text += f"{question_title}\n"

        for lang_section in question_block.find_all("div", class_="language-page"):
            lang_header = lang_section.find("h4")
            if lang_header and lang_header.get_text(strip=True) == "English":
                extracted_text += lang_section.find("p").get_text(strip=True) + "\n"

        instructions = question_block.find("div", class_="instructions")
        if instructions:
            instruction_paragraphs = instructions.find_all("p")
            extracted_text += f"For each of the statements, indicate whether the statement is true (T) or false (F):\n"

        for option in question_block.find_all("div", class_="option-item"):
            option_number = option.find("strong").get_text(strip=True) if option.find("strong") else ""
            option_texts = option.find_all("p")
            if option_texts:
                option_text = option_texts[1].get_text(strip=True)
                extracted_text += f"\n{option_number} {option_text}\n"
        
        extracted_text += "\n\n\n"
    return extracted_text



def extract_text_from_html_PreEx_questions_2023(html_path: str) -> str:
    """
    Extracts text from a Pre-Exam 2023 questions HTML file.

    Args:
        html_path (str): Path to the input HTML file.

    Returns:
        str: Extracted and formatted text.
    """
    with open(file_path, "rb") as file: 
        raw_data = file.read()
        decoded_data = raw_data.decode("utf-8", errors="replace")  
        soup = BeautifulSoup(decoded_data, "html.parser")


    extracted_text = ""
    question_count = 0
    for question_block in soup.find_all("div", class_="question-block"):
        question_count += 1
        question_title = question_block.find("div", class_="question-title").get_text(strip=True)
        extracted_text += f"{question_title}\n"

        if question_count >= 11:
            html_content = str(question_block)  
            
            pattern = r'<h4>English</h4>(.*?)<h4>.*?</h4>'
            match = re.search(pattern, html_content, re.DOTALL)

            if match:
                english_text = match.group(1)
                english_text = re.sub(r'<p[^>]*lang="[^"]*">.*?</p>', '', english_text)

                clean_text = re.sub(r'<[^>]+>', '', english_text)
                clean_text = re.sub(r'Claim set I', '', clean_text)
                
                extracted_text += clean_text + "\n"

        for lang_section in question_block.find_all("div", class_="language-page"):
            lang_header = lang_section.find("h4")
            if lang_header and lang_header.get_text(strip=True) == "English":
                extracted_text += lang_section.find("p").get_text(strip=True) + "\n"

        instructions = question_block.find("div", class_="instructions")
        if instructions:
            paragraphs = instructions.find_all("p")
            if len(paragraphs) >= 3:
                if question_count >= 11:
                    english_text = paragraphs[2].get_text(strip=True) 
                else:
                    english_text = paragraphs[1].get_text(strip=True)  
                extracted_text += f"{english_text}\n"

        for option in question_block.find_all("div", class_="option-item"):
            option_number = option.find("strong").get_text(strip=True) if option.find("strong") else ""
            option_texts = option.find_all("p")
            if option_texts:
                option_text = option_texts[1].get_text(strip=True)
                extracted_text += f"\n{option_number} {option_text}\n"
        
        extracted_text += "\n\n\n"            

        claim_set_pattern = re.compile(r"Claim set I", re.IGNORECASE)
        extracted_text = claim_set_pattern.sub("", extracted_text) 
        extracted_text = re.sub(r"(Question \d+)\n{2,}", r"\1\n", extracted_text)
    return extracted_text



# Process all files in the input folder
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)

    if filename.endswith("_PreEx_Answers.pdf") | filename.endswith("_PreEx_answers_EN.pdf") | filename.endswith("_PreEx_answers.pdf") | filename.endswith("_PreEx_Answers.pdf"):
        extracted_text = extract_text_from_pdf_PreEx_answers(file_path)
    elif filename.endswith("_PreEx_questions_EN.pdf") | filename.endswith("_PreEx_questions_en.pdf") | filename.endswith("_PreEx_Questions.pdf") | filename.endswith("_PreEx_questions.pdf"):
        extracted_text = extract_text_from_pdf_PreEx_questions(file_path)
    elif filename.endswith("2024_PreEx_questions.html"): 
        extracted_text = extract_text_from_html_PreEx_questions_2024(file_path)
    elif filename.endswith("2023_PreEx_questions.html"): 
        extracted_text = extract_text_from_html_PreEx_questions_2023(file_path)
    else:
        continue 

    output_filename = filename.replace(".pdf", ".txt").replace(".html", ".txt")
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(extracted_text)

    print(f"Extraction completed for: {filename} → {output_filename}")

print("Extraction completed for all files.")
