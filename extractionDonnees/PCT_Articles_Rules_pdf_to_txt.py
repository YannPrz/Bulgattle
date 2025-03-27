"""
--------------------------------------------------------------------------------
Author: Camille Solacroup
Date: 2025-03-19
Description: 
    This script extracts articles and rules from a given PCT PDF document and 
    saves them as text files. It processes specific page ranges and removes 
    unnecessary elements such as headers, footers, and editorial notes.
--------------------------------------------------------------------------------
"""

import fitz # PyMuPDF
import re



def extract_PCT_articles_txt(pdf_path: str, txt_output: str, nStart: int, nEnd: int):
    """
    Extracts PCT articles from a specified range of pages in a PDF.

    Args:
        pdf_path (str): Path to the input PDF file.
        txt_output (str): Path to save the extracted text file.
        nStart (int): Start page number (0-based index).
        nEnd (int): End page number (exclusive).

    Returns:
        None
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for num_page in range(nStart, nEnd):
        page = doc[num_page]
        full_text += page.get_text("text")

    # Clean text by removing unnecessary elements
    full_text = re.sub(r'Patent Cooperation Treaty', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'(?m)^\s*\d+\s*$', '', full_text)  # Remove page numbers
    full_text = re.sub(r'(?m)^CHAPTER\s+[IVXLCDM]+\b.*$', '', full_text)  # Remove chapter headers
    full_text = re.sub(r'(?m)^[A-Z ]{5,}$', '', full_text)  # Remove uppercase headers
    full_text = re.sub(r'\n\s*\n', '\n', full_text)  # Remove excessive new lines

    # Extract articles using regex
    pattern = r'(?m)^Article \d+ .*?(?=\nArticle \d+ \n|\Z)'
    articles = re.findall(pattern, full_text, flags=re.DOTALL)

    with open(txt_output, "w", encoding="utf-8") as f:
        f.write("\n\n".join(articles))



def extract_PCT_rules_txt(pdf_path: str, txt_output: str, nStart: int, nEnd: int):
    """
    Extracts PCT rules from a specified range of pages in a PDF.

    Args:
        pdf_path (str): Path to the input PDF file.
        txt_output (str): Path to save the extracted text file.
        nStart (int): Start page number (0-based index).
        nEnd (int): End page number (exclusive).

    Returns:
        None
    """    
    doc = fitz.open(pdf_path)
    full_text = ""

    for num_page in range(nStart, nEnd):
        page = doc[num_page]
        full_text += page.get_text("text")

    # Clean text by removing unnecessary elements
    full_text = re.sub(r'(?s)\n?\d*\s*Editor’s Note:.*?(?=\n\d+|\nRule \d|\n\s*\n|\Z)', '', full_text)
    full_text = re.sub(r'Regulations under the PCT', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'(?m)^CHAPTER\s+[IVXLCDM]+\b.*$', '', full_text)  # Remove chapter headers
    full_text = re.sub(r'(?m)^[A-Z ]{5,}$', '', full_text)  # Remove uppercase headers
    full_text = re.sub(r'(?m)^\s*\d+\s*$', '', full_text)  # Remove page numbers
    full_text = re.sub(r'\n\s*\n', '\n', full_text)  # Remove excessive new lines
    
    # Extract rules using regex
    pattern = r'(?m)^Rule \d+(?:bis)?\s{2,3}.*?(?=\nRule \d+(?:bis)?\s{2,3}\n|\Z)'
    articles = re.findall(pattern, full_text, flags=re.DOTALL)

    # Save extracted rules to a text file
    with open(txt_output, "w", encoding="utf-8") as f:
        f.write("\n\n".join(articles))



# Source file path
input_file = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/2-PCT_wipo-pub-274-2024-en-patent-cooperation-treaty.pdf"

# Extract and save articles
output_articles = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT/PCT_articles.txt"
extract_PCT_articles_txt(input_file, output_articles, 8, 54)

# Extract and save rules
output_rules = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT/PCT_rules.txt"
extract_PCT_rules_txt(input_file, output_rules, 72, 238)
print("Extraction completed for both files.")