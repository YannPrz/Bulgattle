import json
import re 

def prexToToJsonOption(destTxt,destjsonl):
	with open (destTxt,"r",encoding="utf-8")as f:
		numQuestion=0
		numChoix =0
		contenue = ""
		type = 0   ## 0 pour question 1 pour choix 2 pour réponse
		d ={}
		listeDictionnaire=[]
		c=0
		##pas oublié dico
		for ligne in f :
			c+=1
			matchNum =re.search(r'\d+\.\d+ (.*)', ligne)
			if ligne.startswith("Option") or ligne.startswith("Question") or ligne.startswith("TRUE") or ligne.startswith("FALSE") or matchNum  :
				#procedure Enregistrement dictionnaire
				numAChoisir = numQuestion if type ==0 else numChoix
				ecritDict(d,contenue,type,numAChoisir) ##pas bon encore
				contenue=""
				if ligne.startswith("Option") :
					numChoix+=1
					type = 1
					contenue +=ligne.split(": ", 1)[1].strip() if ":" in ligne else "" ## Prend tout le texte après ": "
				if ligne.startswith("TRUE") or ligne.startswith("FALSE") :
					type = 2
					##match =re.search(r'\w+\s–\s+(.*)', ligne)
					contenue += ligne
					"""if match : 
						contenue += match.group(1)
						
	
					else :
						contenue+= ligne"""""

				if matchNum :
					contenue += matchNum.group(1)
					numChoix+=1
					type = 1

					

				if ligne.startswith("Question"): ## à faire à la fin
					if numQuestion>0 :
						listeDictionnaire.append(d)
					d={}
					numQuestion+=1
					numChoix= 0
					type=0
				
 
			else :
				if ligne!="\n" :
					contenue+= ligne
		listeDictionnaire.append(d)
		with open(destjsonl,"w",encoding="utf-8") as fjason :
			for donnee in listeDictionnaire:
				fjason.write(json.dumps(donnee, ensure_ascii=False) + "\n")
## Je ne sais plus si ce truc sert à quelque chose 

def prexToToJsonNum(destTxt,destjsonl):
	with open (destTxt,"r",encoding="utf-8")as f:
		numQuestion=0
		numChoix =0
		contenue = ""
		type = False
		d ={}
		listeDictionnaire=[]
		nLigne=1
		##pas oublié dico
		for ligne in f :
			nLigne+=1
			if ligne[0].isdigit() or ligne.startswith("Question")  :
				#procedure Enregistrement dictionnaire
				numAChoisir = numChoix if type else numQuestion
				
				ecritDict(d,contenue,type,numAChoisir)
				contenue=""
				##
				##if ligne.startswith("Option") :
				##	numChoix+=1
				##	type = True
				##	contenue +=ligne.split(": ", 1)[1].strip() if ":" in ligne else "" ## Prend tout le texte après ": "
				

				if ligne[0].isdigit() :
					numChoix +=1
					type = True
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
						type=False
				
 
			else :
				if ligne!="\n" :
					contenue+= ligne
		listeDictionnaire.append(d)
		with open(destjsonl,"w",encoding="utf-8") as fjason :
			for donnee in listeDictionnaire:
				fjason.write(json.dumps(donnee, ensure_ascii=False) + "\n")

def ecritDict(dictionnaire,text,type,num):
	if type == 0 :
		s = "Question"
		
	elif type == 1 :
		s="Choix"
	else :
		s="Answer"
	dictionnaire[s+str(num)]=text

def ArtTxtToJson(destTxt,destjsonl):
	with open (destTxt,"r",encoding="utf-8")as f:
		numArticle=""
		numSsArticle =0
		NumSsSsArticle = chr(ord('a')-1)	
		isSsArticle = False
		isSsSsArticle = False
		contenue=""
		d ={}
		listeDictionnaire=[]
		c=0
		for ligne in f :
			
			##matchArticle = re.search(r'^\d+(.*)', ligne)
			matchSsArticle =re.search(r'^\(\d+\)(.*)', ligne)
			matchSsSsArticle = re.search(r'^\([a-zA-Z]+\)(.*)', ligne)
			c+=1 
			if ligne[0].isdigit() or matchSsArticle or matchSsSsArticle :
				
				
				#procedure Enregistrement dictionnaire
				ecritDictArt(d,contenue,numArticle,isSsArticle,numSsArticle,isSsSsArticle,NumSsSsArticle)
				contenue=""
				if matchSsSsArticle :
					
					NumSsSsArticle = chr(ord(NumSsSsArticle)+1)	
					isSsSsArticle = True
					contenue += matchSsSsArticle.group(1)
				else :
					isSsSsArticle = False
					
					NumSsSsArticle = chr(ord('a')-1)
					if matchSsArticle :
						numSsArticle+=1
						isSsArticle = True
						contenue += matchSsArticle.group(1)
					else :
						matchArticle = re.search(r'^(\S+)\s+(.*)', ligne)
						if numArticle!="" and d!={} :
							
							listeDictionnaire.append(d)
						d={}
						isSsArticle = False
						numSsArticle = 0
						numArticle=""
						numArticle+= matchArticle.group(1)
						contenue += matchArticle.group(2)

			else : 
				if ligne!="\n" :
					print(ligne)
					contenue+= ligne
		listeDictionnaire.append(d)
		with open(destjsonl,"w",encoding="utf-8") as fjason :
			for donnee in listeDictionnaire:
				fjason.write(json.dumps(donnee, ensure_ascii=False) + "\n")	

def ecritDictArt(dictionnaire,text,numArticle,isSsArticle,NumSsArticle,isSsSsArticle,NumSsSsArticle):
	if not text.startswith("(deleted)\n") :
		
		
		if isSsSsArticle :
			
			dictionnaire["ssRules"+ str(NumSsArticle) + NumSsSsArticle]=text

		elif isSsArticle :
			dictionnaire["ssRules"+ str(NumSsArticle)]  =text

		else :
			dictionnaire["numRules"]=numArticle
			dictionnaire["nameRules"]=text

dest= "/home/cytech/databattle/Bulgattle/databattle/ressources/EPC/"
name = "RULE_implementingRegulation"
#prexToToJsonOption(dest+name+".txt",dest+name+".jsonl")

ArtTxtToJson(dest+name+".txt",dest+name+".jsonl")

