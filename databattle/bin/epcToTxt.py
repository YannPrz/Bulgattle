# Goal extract the english part of rule from the epc files, write it in a txt files and store all the data in a SQL database
# Author Thomas Beaussart
# Date 2021-05-26
# Version 1.0
# package : pymupdf pour lire les fichiers pdf et les convertir en texte

import fitz # pymupdf
import re

# Function to convert the epc file into text
# Each paragraph = 1 line 
# Each article = [n° article] + [space] + [name of the article] 
# If the article is divided into part the line start with [n°(or letter) of the section]  
# Parameters:
# - pdf_path : str : path to the pdf file
# - txt_output : str : path to the txt file
# - nStart : int : page number to start the extraction
# - nEnd : int : page number to end the extraction
def extract_EPC_txt(pdf_path: str, txt_output: str, nStart: int, nEnd: int):
    doc = fitz.open(pdf_path)
    text_extract = []
    c=1
    for num_page in range(nStart, nEnd, 2):  # Only take the odd pages
        page = doc[num_page]
        width, height = page.rect.width, page.rect.height

        # Extract the English part from the right side of the page
        english_part = page.get_text("blocks", clip=fitz.Rect(width / 2, 0, width, height))
        
        page_text = []
        for paragraph in english_part:
            text = paragraph[4].strip()
            if text and not text[0].isdigit():  # Exclude paragraphs starting with a digit
                # Replace newlines within paragraphs with spaces
                
                tmp = text 
                text = re.sub(r'Article .*\n', str(c)+" ", text)
                if tmp!= text :
                    c+=1
                
                text = text.replace("European Patent Convention","")
                text = text.replace("\n\n","")
                text = text.replace("", "")
                text = text.replace("-\n", "")
                text = text.replace("\n", " ")
                text = re.sub(r'PART .*',"", text)
                text = re.sub(r'Chapter .*',"", text)
                page_text.append(text)
        if page_text:
            # Join paragraphs with double newline for separation
            text_extract.append("\n".join(page_text))

    # Save the text in a txt file
    with open(txt_output, "w") as f:
        f.write("\n\n".join(text_extract))  # Separate each page's text with double newline

# A rajouter pour le moment :
# - fin de ligne
#  enlever textes useless (European Patent Convention)
#  enlever les indices surtout pour les articles 

pdfFile = "/home/cytech/databattle/Bulgattle/databattle/ressources/1-EPC_17th_edition_2020_en.pdf"
txtFile = "/home/cytech/databattle/Bulgattle/databattle/ressources/EPC2.txt"
extract_EPC_txt(pdfFile, txtFile, 47, 101) 
				


