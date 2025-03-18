import fitz  # PyMuPDF pour extraire le texte des PDF
import re  # Module pour manipuler les expressions régulières
import mysql.connector  # Pour interagir avec MySQL
from mysql.connector import Error  # Gestion des erreurs SQL
import os


# Chemin du fichier PDF
mcq_pdf_path = "./../EPAC_Exams/2022 - EPAC_exam_mcq_en_Part1.pdf"
solution_pdf_path = "./../EPAC_Exams/2022 - EPAC_Solution_mcq&open.pdf"


def is_file_already_processed(conn, pdf_path):
    """
    Vérifie si un fichier PDF a déjà été traité en base de données.
    """
    cursor = conn.cursor()
    source_file = os.path.basename(pdf_path)  # Extrait le nom du fichier
    sql = "SELECT COUNT(*) FROM Question WHERE source_file = %s"
    cursor.execute(sql, (source_file,))
    count = cursor.fetchone()[0]
    
    return count > 0  # Retourne True si des données existent déjà


# === FONCTION DE NETTOYAGE DU TEXTE ===
def clean_text(text):
    """
    Remplace les retours à la ligne et séquences d'espaces par un seul espace.
    """
    return re.sub(r"\s+", " ", text).strip()



def connect_to_db():
    """
    Établit une connexion à la base de données MySQL.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Remplace par ton vrai mot de passe MySQL
            database="quiz_db"
        )
        if conn.is_connected():
            print("Connexion à la base MySQL réussie.")
            return conn
    except Error as e:
        print(f"Erreur de connexion à MySQL : {e}")
        return None

def insert_question(conn, question_text, question_type, annee, pdf_path):
    """
    Insère une question en stockant automatiquement le nom du fichier source.
    """
    cursor = conn.cursor()
    source_file = os.path.basename(pdf_path)  # Extrait le nom du fichier source
    sql = "INSERT INTO Question (question_text, question_type, annee, source_file) VALUES (%s, %s, %s, %s)"
    values = (clean_text(question_text), question_type, annee, source_file)
    cursor.execute(sql, values)
    conn.commit()
    return cursor.lastrowid  # Retourne l'ID de la question insérée

def insert_answer(conn, reponse_text, pdf_path):
    """
    Insère une réponse en stockant automatiquement le nom du fichier source.
    """
    cursor = conn.cursor()
    source_file = os.path.basename(pdf_path)  # Extrait le nom du fichier source
    sql = "INSERT INTO Reponse (reponse_text, source_file) VALUES (%s, %s)"
    values = (clean_text(reponse_text), source_file)
    cursor.execute(sql, values)
    conn.commit()
    return cursor.lastrowid  # Retourne l'ID de la réponse insérée



def link_question_answer(conn, question_id, reponse_id, is_correct):
    """
    Associe une question à une réponse en indiquant si elle est correcte.
    """
    cursor = conn.cursor()
    sql = "INSERT INTO Question_Reponse (question_id, reponse_id, is_correct) VALUES (%s, %s, %s)"
    cursor.execute(sql, (question_id, reponse_id, is_correct))
    conn.commit()


# === FONCTIONS POUR EXTRAIRE LE TEXTE DES PDF ===
def extract_text_from_pdf(pdf_path):
    """
    Extrait le texte d'un fichier PDF et retourne son contenu sous forme de chaîne de caractères.
    """
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text


# === FONCTION POUR EXTRAIRE LES QUESTIONS QCM ET LEURS CHOIX ===
def extract_mcq_questions(text):
    """
    Extrait les questions QCM ainsi que leurs choix de réponse (A., B., C., D.).
    """

    # Nouvelle regex améliorée : capture la question jusqu'au "?" suivi d'une ligne vide, puis le choix A.
    pattern = r"(\d+\.)\s(.+?\?)\s*\n(A\..+?)\n(B\..+?)\n(C\..+?)\n(D\..*?)(?=\n\d+\.|$)"


    r"""
    (\d+\.)        # Capture un numéro de question, qui commence par un ou plusieurs chiffres (\d+), suivis d’un point (.)
    \s            # Capture un espace après le numéro de la question.
    (.+?\?)       # Capture le texte de la question jusqu'à un "?" (le +? signifie capture non-greedy).
    \n\s*\n       # Capture un saut de ligne + une ligne vide (garantit qu'on est bien à la fin de la question).
    (A\..+?)      # Capture la réponse A., qui commence par "A." suivi de son texte.
    \n(B\..+?)    # Capture la réponse B., qui commence par "B." suivi de son texte.
    \n(C\..+?)    # Capture la réponse C., qui commence par "C." suivi de son texte.
    \n(D\..+?)    # Capture la réponse D., qui commence par "D." suivi de son texte.
    (?=\n|$)      # Capture D. suivi de tout texte jusqu'à un saut de ligne (\n) ou la fin du texte ($).
    """

    matches = re.findall(pattern, text, re.DOTALL)

    mcq_list = []

    for match in matches:
        question_number = match[0].strip()  # Numéro de la question
        question_text = match[1].strip()  # Texte de la question

        # Extraction des choix (A, B, C, D)
        choices = [clean_text(match[2]),
                   clean_text(match[3]),
                   clean_text(match[4]),
                   clean_text(match[5])]

        mcq_list.append({"question": question_text, "choices": choices})

    return mcq_list

# === FONCTION POUR EXTRAIRE LES SOLUTIONS QCM ===
def extract_mcq_solutions(text):
    """
    Extrait les réponses correctes des QCM depuis le fichier de correction.
    """
    pattern = r"Question\s+(\d+):\s+([A-D])"
    matches = re.findall(pattern, text)

    # Stocke les solutions sous forme de dictionnaire {numéro_question: bonne réponse}
    solutions = {int(num): answer for num, answer in matches}
    return solutions


def insert_justification(conn, question_id, texte):
    """
    Insère une justification dans la table Justification.
    """
    cursor = conn.cursor()
    sql = "INSERT INTO Justification (question_id, texte) VALUES (%s, %s)"
    values = (question_id, clean_text(texte))
    cursor.execute(sql, values)
    conn.commit()
    return cursor.lastrowid  # Retourne l'ID de la justification insérée


def insert_article(conn, reference, texte, lien):
    """
    Insère un article de loi.
    """
    cursor = conn.cursor()
    sql = "INSERT INTO Article (reference, texte, lien) VALUES (%s, %s, %s)"
    values = (reference, texte, lien)
    cursor.execute(sql, values)
    conn.commit()
    return cursor.lastrowid

def link_justification_article(conn, justification_id, article_id):
    """
    Lie une justification à un article juridique.
    """
    cursor = conn.cursor()
    sql = "INSERT INTO Justification_Article (justification_id, article_id) VALUES (%s, %s)"
    cursor.execute(sql, (justification_id, article_id))
    conn.commit()


def extract_justifications(text):
    """
    Extrait les justifications et articles pour chaque question.
    """
    pattern = r"Question\s+(\d+):\s+\w\n(.*?)\nLegal basis\s*\n(.*?)(?=\nQuestion\s+\d+:|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)

    justifications = {}
    for match in matches:
        question_number = int(match[0])
        justification_text = clean_text(match[2])
        justifications[question_number] = justification_text

    return justifications  # Retourne un dictionnaire {numéro_question: justification}


def extract_articles(justification_text):
    """
    Extrait uniquement les références légales d'une justification spécifique.
    """
    pattern = r"(Rule|Article|Decision) \d+(?:\(\d+\))? EPC"
    matches = re.findall(pattern, justification_text)

    return list(set(matches))  # Supprime les doublons et retourne une liste propre



# Extraction du texte
mcq_text = extract_text_from_pdf(mcq_pdf_path)
solution_text = extract_text_from_pdf(solution_pdf_path)

# Normalisation
mcq_text = re.sub(r"\n{2,}", "\n", mcq_text)

# Extraction des données
mcq_questions = extract_mcq_questions(mcq_text)
mcq_solutions = extract_mcq_solutions(solution_text)
justifications = extract_justifications(solution_text)

# Connexion et insertion dans la base
# Connexion à la base
conn = connect_to_db()

if conn:
    # Vérifier si le fichier PDF a déjà été traité
    if is_file_already_processed(conn, mcq_pdf_path):
        print(f"⚠️ Le fichier '{os.path.basename(mcq_pdf_path)}' a déjà été traité. Aucune action.")
    else:
        print(f"✅ Traitement du fichier '{os.path.basename(mcq_pdf_path)}' en cours...")

        # Extraction du texte
        mcq_text = extract_text_from_pdf(mcq_pdf_path)
        solution_text = extract_text_from_pdf(solution_pdf_path)

        # Normalisation des sauts de ligne
        mcq_text = re.sub(r"\n{2,}", "\n", mcq_text)

        # Extraction des données
        mcq_questions = extract_mcq_questions(mcq_text)
        mcq_solutions = extract_mcq_solutions(solution_text)
        justifications = extract_justifications(solution_text)

        # Insérer les données dans la base
        for i, question in enumerate(mcq_questions):
            question_id = insert_question(conn, question["question"], 1, 2022, mcq_pdf_path)
            for choice in question["choices"]:
                reponse_id = insert_answer(conn, choice, mcq_pdf_path)
                is_correct = (choice[0] == mcq_solutions.get(i + 1, "X"))
                link_question_answer(conn, question_id, reponse_id, is_correct)

            # Insérer les justifications et les articles
            if i + 1 in justifications:
                justification_id = insert_justification(conn, question_id, justifications[i + 1])
                for article in extract_articles(justifications[i + 1]):
                    article_id = insert_article(conn, article, "", "")
                    link_justification_article(conn, justification_id, article_id)

        print("✅ Données insérées avec succès.")

    # Fermeture de la connexion
    conn.close()
else:
    print("❌ Connexion MySQL impossible.")
