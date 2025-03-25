import json
import re 

def prexToToJsonOption(destTxt,destjsonl):
	with open (destTxt,"r",encoding="utf-8")as f:
		numQuestion=0
		numChoix =0
		contenue = ""
		isChoix = False   ## 0 pour question 1 pour choix 2 pour réponse
		d ={}
		listeDictionnaire=[]
		##pas oublié dico
		for ligne in f :

			if ligne.startswith("Option") or ligne[0].isdigit() or ligne.startswith("Question") or ligne.startswith("TRUE") or ligne.startswith("FALSE") :
				#procedure Enregistrement dictionnaire
				numAChoisir = numChoix if isChoix else numQuestion
				
				ecritDict(d,contenue,isChoix,numAChoisir)
				contenue=""
				if ligne.startswith("Option") :
					numChoix+=1
					isChoix = True
					contenue +=ligne.split(": ", 1)[1].strip() if ":" in ligne else "" ## Prend tout le texte après ": "


				if ligne[0].isdigit() :
					numChoix +=1

				if ligne.startswith("Question"): ## à faire à la fin
					if numQuestion>0 :
						listeDictionnaire.append(d)
					d={}
					numQuestion+=1
					numChoix= 0
					isChoix=False
				
 
			else :
				if ligne!="\n" :
					contenue+= ligne
		listeDictionnaire.append(d)
		with open(destjsonl,"w",encoding="utf-8") as fjason :
			for donnee in listeDictionnaire:
				fjason.write(json.dumps(donnee, ensure_ascii=False) + "\n")

def prexToToJsonNum(destTxt,destjsonl):
	with open (destTxt,"r",encoding="utf-8")as f:
		numQuestion=0
		numChoix =0
		contenue = ""
		isChoix = False
		d ={}
		listeDictionnaire=[]
		nLigne=1
		##pas oublié dico
		for ligne in f :
			nLigne+=1
			if ligne[0].isdigit() or ligne.startswith("Question")  :
				#procedure Enregistrement dictionnaire
				numAChoisir = numChoix if isChoix else numQuestion
				
				ecritDict(d,contenue,isChoix,numAChoisir)
				contenue=""
				##
				##if ligne.startswith("Option") :
				##	numChoix+=1
				##	isChoix = True
				##	contenue +=ligne.split(": ", 1)[1].strip() if ":" in ligne else "" ## Prend tout le texte après ": "
				

				if ligne[0].isdigit() :
					numChoix +=1
					isChoix = True
					match =re.search(r'\d+\.\d+ (.*)', ligne)
					if match : 
						contenue += match.group(1)
						
					else :
						contenue+= ligne
				if ligne.startswith("Question"): ## à faire à la fin
					if not ligne.startswith("Question "+str(numQuestion+1)) :
						contenue+= ligne
					else :
						if numQuestion>0 :
							listeDictionnaire.append(d)
						d={}
						numQuestion+=1
						numChoix= 0
						isChoix=False
				
 
			else :
				if ligne!="\n" :
					contenue+= ligne
		listeDictionnaire.append(d)
		with open(destjsonl,"w",encoding="utf-8") as fjason :
			for donnee in listeDictionnaire:
				fjason.write(json.dumps(donnee, ensure_ascii=False) + "\n")


def ecritDict(dictionnaire,text,isChoix,num):
	if isChoix : 
		s="Choix"
	else :
		s = "Question"
	dictionnaire[s+str(num)]=text

def 

dest= "/home/cytech/databattle/Bulgattle/databattle/ressources/"
name = "2022_PreEx_questions_EN"
prexToToJsonNum(dest+name+".txt",dest+name+".jsonl")

