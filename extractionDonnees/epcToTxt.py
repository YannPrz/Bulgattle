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
# - nEnd : int : page number to end the extraction$


def suppEntete(text: str, banList: list):
	for ban in banList:
		if text.startswith(ban):
			text = text.replace(ban,"")
	return text

def extract_EPC_txt(pdf_path: str, txt_output: str, nStart: int, nEnd: int):
	banList = ["European Patent Convention","Implementing Regulations","Rules relating to Fees","Rules of Procedure of the Enlarged Board of Appeal","Rules of Procedure of the Boards of Appeal","Protocol on Interpretation","Protocol on Centralisation","Protocol on Recognition","Protocol on Privileges and Immunities","Act revising the EPC","Transitional provisions"] ## Liste des entêtes
	doc = fitz.open(pdf_path)
	text_extract = []
	c=1
	b= True
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
				
				if (text.startswith("Article")and not text.startswith("Articles"))or text.startswith("Rule"):
					if text.startswith("Article"):
						text = text[len("Article")+1:]
					else:
						text = text[len("Rule")+1:]
						b=False

					match = re.search(r'^[^a-zA-Z\n]*[a-zA-Z]', text)
					if match != None:

						text = match.group(1)
						
					else:
						text = re.sub(r'^.*?\n', str(c) + " ", text, count=1)
					
						text = re.sub(r'\n', " ", text)
						
						if b and c==158 :  ## In the only time where we have 
							c= 164
						else :
							c+=1	

				text = suppEntete(text, banList)
				text = text.replace("\n\n","")
				text = text.replace("", "")
				text = text.replace("-\n", "")
				text = text.replace("\n", " ")
				text = text.replace(" r\n","")
				text = re.sub(r'PART .*',"", text)
				text = re.sub(r'Chapter .*',"", text)
				page_text.append(text)
			##Prend aussi en compte les "commentaires"
			else : 
				if (len(text)>=2 and text[0].isdigit()):
					tmp =""
					nbrDigit=0
					while ( text[nbrDigit].isdigit()):
						nbrDigit+=1
					
					if text[nbrDigit] == "." or (text[nbrDigit].isalpha() and text[nbrDigit+1] == ".") :
						
						if text[nbrDigit] == "." :
							tmp = text[:nbrDigit] + ". " 
						elif text[nbrDigit].isalpha() and text[nbrDigit+1] == ".":
							tmp = text[:nbrDigit+1] + ". "
				
						match = re.search(r'\s(.*)', text)
						if match != None:
							text = tmp + match.group(1)
						page_text.append(text)
					else : 
						
						break	


		if page_text:
			# Join paragraphs with double newline for separation
			text_extract.append("\n".join(page_text))

	# Save the text in a txt file
	with open(txt_output, "w") as f:
		f.write("".join(text_extract))  # Separate each page's text with double newline


def extract_EPC_SECTION_txt(pdf_path: str, txt_output: str, nStart: int, nEnd: int):
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
				
				if text.startswith("Section") or text.startswith("Rule"):
					
					text = str(c)
					c+=1	

				text = text.replace("Protocol on Centralisation","")
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
		f.write("\n".join(text_extract))  # Separate each page's text with double newline


pdfFile =""  #Parth to the EPC file
txtFileRepo =""  ##Path to the txt Repository

extract_EPC_txt(pdfFile, txtFileRepo+"ART_conventionOnGrandEuroPatent.txt", 47, 271) #Ok
extract_EPC_txt(pdfFile, txtFileRepo+"RULE_implementingRegulation.txt", 303, 603) #Ok

extract_EPC_txt(pdfFile, txtFileRepo+"ART_rule_Fees.txt", 607, 649) #Ok 

extract_EPC_txt(pdfFile, txtFileRepo+"ART_RuleProcedureEnlargedBoardAppeal.txt", 653, 677) #Ok
extract_EPC_txt(pdfFile, txtFileRepo+"ART_RuleProcedureBoardOfAppeal.txt", 681,719)

extract_EPC_txt(pdfFile, txtFileRepo+"ART_ProtocoleInterpretationArt69.txt", 721, 722) #Ok
extract_EPC_SECTION_txt(pdfFile, txtFileRepo+"SECTION_ProtocoleCentralisation.txt", 725, 743) #Ok

extract_EPC_txt(pdfFile,txtFileRepo+"ART_ProtocolJuridictionRecognitionDecisionInRespectRightGrantEuropean.txt",745,753)

extract_EPC_txt(pdfFile,txtFileRepo+"ART_ProtocolPrivilegeImmunitesEuropeanPatentOrganisation.txt",755,779)
extract_EPC_txt(pdfFile,txtFileRepo+"ART_ActRevisingConventionGrantEuropeanPatents.txt",785,795) 
extract_EPC_txt(pdfFile,txtFileRepo+"ART_DecisionAdministrativeCouncil.txt",799,803)		
