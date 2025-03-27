"""
--------------------------------------------------------------------------------
Author: Camille Solacroup
Date: 2025-03-25
Description:
    This script extracts specific parts of a PDF document (PCT Guidelines) 
    and saves each part as a separate text file.
--------------------------------------------------------------------------------
"""

import fitz # PyMuPDF for PDF text extraction
import re # Regular expressions for text cleaning
import os # File handling

def extract_PCT_guidelines_txt(pdf_path: str, begin: int, end: int) -> str:
    """
    Extracts and cleans text from a given range of pages in a PCT Guidelines PDF.

    Args:
        pdf_path (str): Path to the input PDF file.
        begin (int): Start page (inclusive, 1-based indexing).
        end (int): End page (inclusive, 1-based indexing).

    Returns:
        str: Cleaned extracted text.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for i, page in enumerate(doc):

        if i < begin + 1 or i > end - 1:
            continue
    
        width,height = page.rect.width , page.rect.height

        # Handle two-column layout by extracting different regions on odd/even pages
        if (i % 2 == 0) :
            page_text = page.get_text("text",clip = fitz.Rect(0,0,(1-0.28)*width,height))
        else:
            page_text = page.get_text("text",clip = fitz.Rect((0.28)*width,0,width,height))

        # Remove unwanted headers and formatting issues
        page_text = re.sub(r'March 2024\s*\n', '', page_text)
        page_text = re.sub(r'Guidelines for Examination in the EPO\s*\n', '', page_text)
        page_text = re.sub(r"(\n\d+\.)\s*\n+", r"\1 ", page_text) 

        full_text += page_text 
        
        if i%50==0 :
            print(f"Processing page {i + 1}...")

    # Extract text based on chapter structure if present
    pattern = r'(?m)^Chapter [IVXLCDM].*?(?=\nChapter [IVXLCDM]|\Z)'
    chapter = re.findall(pattern, full_text, flags=re.DOTALL)
    full_text = "\n\n\n\n".join(chapter)

    # Additional text formatting cleanup
    full_text = re.sub(r"\(([ivxlcdm]+)\)\s*\n", r"(\1) ", full_text, flags=re.DOTALL)
    full_text = re.sub(r'^\s*\n+', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r"\(([a-zA-Z])\)\s*\n", r"(\1) ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"-\s*\n", "- ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"–\s*\n", "- ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"\b([a-zA-Z])\)\n", r"\1) ", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([a-zA-Z],)\s*\n([a-zA-Z])", r"\1 \2", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([a-zA-Z])\s*\n([a-zA-Z])", r"\1 \2", full_text, flags=re.DOTALL)
    full_text = re.sub(r"([;,])\s*\n([a-zA-Z])", r"\1 \2", full_text, flags=re.DOTALL)
    full_text = re.sub(r"(\n\d+\. )", r"\n\n\1", full_text, flags=re.DOTALL)

    return full_text


# Define input and output paths
input_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/3-en-epc-guidelines-2024-hyperlinked.pdf"
output_folder ="/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT_guidelines"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Define the page ranges for each part
parts = [
    (41, 190),  
    (203, 282), 
    (293, 360), 
    (371, 434), 
    (449, 596), 
    (607, 716),  
    (725, 848), 
    (859, 924) 
]

# Extract and save each part
for i, (begin_page, end_page) in enumerate(parts):
    extracted_text = extract_PCT_guidelines_txt(
        input_folder,
        begin=begin_page,
        end=end_page
    )
    
    part_letter = chr(65 + i) 
    # Generate output file path dynamically
    output_path = f"/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT_guidelines/Part_{part_letter}.txt"

    with open(output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(extracted_text)

    print(f"Extracted Part {part_letter} (Pages {begin_page} to {end_page if end_page else 'end'}) → Saved as {output_path}")
    print("Extraction completed.")

