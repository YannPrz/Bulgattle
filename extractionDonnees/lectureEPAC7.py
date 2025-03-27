import fitz  # PyMuPDF pour extraire le texte des PDF
import spacy
import json

nlp = spacy.load("en_core_web_sm")
import re  # Module pour manipuler les expressions régulières
import mysql.connector  # Pour interagir avec MySQL
from mysql.connector import Error  # Gestion des erreurs SQL
import os



# === 📌 Nettoyage du texte ===
def clean_text(text):
    return re.sub(r"\s+", " ", text).strip() if text else ""



# === 📌 Extraction du texte depuis un PDF ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text("text") for page in doc)


# === 📌 Extraction des Questions QCM ===
def extract_mcq_questions(text):
    pattern = r"(\d+\.)\s(.+?\?)\s*\n(A\..+?)\n(B\..+?)\n(C\..+?)\n(D\..*?)(?=\n\d+\.|$)"
    matches = re.findall(pattern, text, re.DOTALL)

    mcq_list = []
    for match in matches:
        question_text = clean_text(match[1])
        choix_A = clean_text(match[2])
        choix_B = clean_text(match[3])
        choix_C = clean_text(match[4])
        choix_D = clean_text(match[5])

        mcq_list.append({
            "question": question_text,
            "choix_A": choix_A,
            "choix_B": choix_B,
            "choix_C": choix_C,
            "choix_D": choix_D
        })

    return mcq_list


# === 📌 Extraction des Solutions QCM ===
def extract_mcq_solutions(text):
    pattern = r"Question\s+(\d+):\s+([A-D])"
    matches = re.findall(pattern, text)
    return {int(num): answer for num, answer in matches}  # Associe numéro -> solution


def clean_text_advanced(text):
    """Nettoie le texte en supprimant les espaces inutiles et les sauts de ligne superflus."""
    return re.sub(r"\s+", " ", text).strip()

def extract_questions_ouvertes(text):
    """
    Étape 1 : Extrait les "questions ouvertes" en bloc (contexte + questions associées).
    """
    pattern_questions_ouvertes = r"(\d+\.\s\(\d+\s+points\))\s*(.*?)(?=\s*\d+\.\s\(|\Z)"
    
    matches = re.findall(pattern_questions_ouvertes, text, re.DOTALL)

    # Liste des blocs de questions ouvertes complètes
    questions_ouvertes = []
    
    #print(matches, "fin latches ")

    for match in matches:
        #bloc_complet = clean_text_advanced(match)  # Nettoyage du bloc complet
        #print(match[1], "\n\n\n\n")
        questions_ouvertes.append(match[1])
    #print("\n\n\n\n\nquetsions complètes  : ", questions_ouvertes, "\n\n\n\n\n")

    return questions_ouvertes


def extract_contexte_et_questions(bloc):
    """
    Sépare le contexte et les sous-questions d’un bloc structuré.
    Chaque sous-question commence par un chiffre suivi d’un point : 1., 2., 3., etc.
    """
    lignes = bloc.split("\n")
    contexte_lignes = []
    questions = []
    current_question = ""

    is_question_started = False

    for line in lignes:
        line = line.strip()
        if re.match(r"^\d+\.\s", line):
            # Nouvelle question détectée
            if current_question:
                questions.append(current_question.strip())
            current_question = line  # Commence nouvelle question
            is_question_started = True
        elif is_question_started:
            # Ajout à la question en cours
            current_question += " " + line
        else:
            # Partie contexte
            contexte_lignes.append(line)

    # Dernière question
    if current_question:
        questions.append(current_question.strip())

    contexte = clean_text_advanced(" ".join(contexte_lignes))
    return contexte, questions


def extract_open_answers(text):
    """
    Extrait les réponses aux questions ouvertes depuis le texte extrait.
    Chaque réponse est associée à son numéro de question.
    """
    pattern = r"Question\s+(\d+):\s*(.*?)(?=\nQuestion\s+\d+:|\Z)"  # Capture les réponses
    matches = re.findall(pattern, text, re.DOTALL)
    #print("matches : ", matches)
    solutions = {}
    for match in matches:
        question_number = int(match[0])
        solution_text = match[1].strip()
        #print("match[1] : ", match[1])
        solutions[question_number] = solution_text

    return solutions



def detect_questions(text):
    """
    Identifie les phrases interrogatives dans un bloc de texte.
    """
    doc = nlp(text)
    questions = []
    contexte = []

    for sent in doc.sents:
        if "?" in sent.text or sent.text.strip().lower().startswith(("what", "why", "how", "when", "where", "who", 
                                                                        "is", "does", "do", "can", "should", "please", 
                                                                        "you should", "you must", "explain", "could", "would", 
                                                                        "shall", "may", "must", "did", "will", "which", 
                                                                        "whom", "whose", "might", "provide", "describe", 
                                                                        "give an example", "tell me", "demonstrate", "justify", "show", "list")
                                                                        ):
            questions.append(sent.text.strip())
        else:
            contexte.append(sent.text.strip())

    return " ".join(contexte), questions


def is_structured_block(bloc):
    """
    Détermine si un bloc est structuré (avec a./b./1./A./etc.) suivi d'une question.
    Un bloc structuré contient au moins deux sous-questions numérotées ou lettrées.
    """
    print("bloc dans is structured ", bloc, "\n\n\n\n\n")
    pattern = r"^\s*([a-zA-Z0-9])\.\s+"
    matches = re.findall(pattern, bloc, re.MULTILINE)
    return len(matches) >= 2



def split_block_into_subanswers(block_text):
    parts = re.split(r"(?:^|\n)\s*\d+\.\s+", block_text)
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) == 1:
        paragraphs = re.split(r"\n\s*\n", block_text)
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 10]
        if len(paragraphs) > 1:
            parts = paragraphs
    
    return parts


def split_block_into_subanswers(text):
    """
    Sépare un bloc de réponse en sous-réponses, en prenant en compte les listes à puces et les paragraphes.
    Retourne une liste de sous-réponses.
    """
    lines = text.strip().splitlines()
    subanswers = []
    current = ""

    bullet_pattern = re.compile(r"^\s*([•\-–—o*])\s+|^\s*(\uf0a7|\u2022|\u00a7|\d+\.)\s+")  # liste de puces classiques

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if bullet_pattern.match(line):
            # Si on a un bloc déjà en cours, on le termine
            if current:
                subanswers.append(current.strip())
            current = line  # Nouvelle entrée de puce
        else:
            # Si on est déjà dans une entrée, on continue
            if current:
                current += " " + line
            else:
                current = line  # Commencer une nouvelle ligne normale

    if current:
        subanswers.append(current.strip())

    return subanswers if subanswers else [text.strip()]

def detect_open_answers_from_blocks_listed(answer_blocks):
    """
    Prend une liste de blocs de réponses (une par question) et les découpe en sous-réponses si nécessaire.
    Retourne un dictionnaire {num_question: [sous_réponses]}.
    """
    answers = {}
    for i, block in enumerate(answer_blocks, start=1):
        cleaned_block = block.strip()
        sub_answers = split_block_into_subanswers(cleaned_block)
        answers[i] = sub_answers
    return answers


def detect_open_answers_from_blocks_listed(answer_blocks):
    answers = {}
    for i, block in enumerate(answer_blocks, start=1):
        cleaned_block = block.strip()
        sub_answers = split_block_into_subanswers(cleaned_block)
        answers[i] = sub_answers
    return answers

def split_answers_by_question(text):
    """
    Sépare le texte complet en blocs de réponse individuels en se basant sur "Question X".
    """
    pattern = r"Question\s+\d+\s*(.*?)(?=(?:\nQuestion\s+\d+)|\Z)"
    return re.findall(pattern, text, re.DOTALL)


def detect_open_answers_from_blocks(answer_blocks):
    """
    Extrait les réponses depuis une liste de blocs de texte (chaque bloc étant une réponse complète à une question ouverte).
    Retourne un dictionnaire {numéro_question: texte_réponse}.
    """
    answers = {}
    question_number = 1

    for block in answer_blocks:
        cleaned = clean_text_advanced(block)
        answers[question_number] = cleaned
        question_number += 1

    return answers



def export_open_questions_to_jsonl_simple(contexte_list, questions_list, answers_dict, output_path):
    """
    Exporte les questions ouvertes (contexte, question, réponse) dans un fichier JSONL.
    Matching simple : question[i] <-> réponse[i] pour chaque bloc.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for bloc_index in range(len(contexte_list)):
            contexte = contexte_list[bloc_index]
            questions = questions_list[bloc_index]
            reponses = answers_dict.get(bloc_index + 1, [])

            for i in range(len(questions)):
                question = questions[i]
                reponse = reponses[i] if i < len(reponses) else "Aucune réponse disponible"

                data = {
                    "contexte": contexte,
                    "question": question,
                    "reponse": reponse
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

def export_open_questions_to_jsonl(contexte_list, questions_list, answers_dict, output_path):
    """
    Exporte proprement les données question/contexte/réponse même en cas de déséquilibre.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for bloc_index in range(len(contexte_list)):
            contexte = contexte_list[bloc_index]
            questions = questions_list[bloc_index]
            reponses = answers_dict.get(bloc_index + 1, [])

            q_count = len(questions)
            r_count = len(reponses)

            if r_count == 0:
                # Aucune réponse : on met "Aucune réponse disponible" pour chaque question
                for question in questions:
                    f.write(json.dumps({
                        "contexte": contexte,
                        "question": question,
                        "reponse": "Aucune réponse disponible"
                    }, ensure_ascii=False) + "\n")

            elif q_count == r_count:
                # Match 1:1
                for q, r in zip(questions, reponses):
                    f.write(json.dumps({
                        "contexte": contexte,
                        "question": q,
                        "reponse": r
                    }, ensure_ascii=False) + "\n")

            elif q_count > r_count:
                # Plus de questions → on répartit les réponses
                group_size = q_count // r_count
                extra = q_count % r_count

                i = 0
                for r_index, r in enumerate(reponses):
                    nb_q = group_size + (1 if r_index < extra else 0)
                    for _ in range(nb_q):
                        if i < q_count:
                            f.write(json.dumps({
                                "contexte": contexte,
                                "question": questions[i],
                                "reponse": r
                            }, ensure_ascii=False) + "\n")
                            i += 1

            else:
                # Plus de réponses que de questions → on ignore les réponses en trop
                for i in range(q_count):
                    f.write(json.dumps({
                        "contexte": contexte,
                        "question": questions[i],
                        "reponse": reponses[i]
                    }, ensure_ascii=False) + "\n")













# === 🎯 Traitement Principal ===
mode = "open"  # Choisir "qcm" ou "open"

if mode == "qcm":
    pdf_path = "./../EPAC_Exams/2022 - EPAC_exam_mcq_en_Part1.pdf"
    solution_pdf_path = "./../EPAC_Exams/2022 - EPAC_Solution_mcq&open.pdf"
elif mode == "open":
    pdf_path = "./../EPAC_Exams/2024 - EPAC_exam_open.pdf"
    solution_pdf_path_2022 = "./../EPAC_Exams/2022 - EPAC_Solution_mcq&open.pdf"
    solution_pdf_path_open_2024 = "./../EPAC_Exams/2024 - EPAC_solution_open.pdf"
    pdf_question_open_2023 = "./../EPAC_Exams/2023 - EPAC_exam_open_EN.pdf"
    pdf_solution_open_2023 = "./../EPAC_Exams/2023 - EPAC_solution_open.pdf"
    
else:
    print("❌ Mode inconnu. Utilisez 'qcm' ou 'open'.")
    exit()



#if is_file_already_processed(conn, pdf_path):
if (False):
    print(f"⚠️ Le fichier '{os.path.basename(pdf_path)}' a déjà été traité.")
else:
    text = extract_text_from_pdf(pdf_path)
    text_solution = extract_text_from_pdf(solution_pdf_path_open_2024)
    #print("text_solution : ", text_solution)
    if mode == "qcm":
        # Extraction des QCM
        questions = extract_mcq_questions(text)
        solutions = extract_mcq_solutions(text_solution)
        print("solutions : ",solutions)

    elif mode == "open":
        # Extraction des questions ouvertes en blocs
        blocs_ouvertes = extract_questions_ouvertes(text)

        # Extraction des contextes et des sous-questions
        contexte = []
        questions = []

        for bloc in blocs_ouvertes:
            if is_structured_block(bloc):
                c, q = extract_contexte_et_questions(bloc)
            else:
                c, q = detect_questions(bloc)

            contexte.append(c)
            questions.append(q)

        # Extraction des blocs de réponses depuis le PDF de solutions
        answer_blocks = split_answers_by_question(text_solution)

        # Application du découpage intelligent (puces + paragraphes)
        open_answers = detect_open_answers_from_blocks_listed(answer_blocks)

        # Export JSONL basique (match index sans forcer)
        output_json_path = "questions_ouvertes.jsonl"
        export_open_questions_to_jsonl_simple(contexte, questions, open_answers, output_json_path)

        print("✅ Données insérées avec succès.")

