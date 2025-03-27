import fitz  # PyMuPDF pour extraire le texte des PDF
import re  # Module pour manipuler les expressions régulières

# === FONCTIONS POUR EXTRAIRE LE TEXTE DES PDF ===
def extract_text_from_pdf(pdf_path):
    """
    Extrait le texte d'un fichier PDF et retourne son contenu sous forme de chaîne de caractères.
    """
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text


# === FONCTION DE NETTOYAGE DU TEXTE ===
def clean_text(text):
    """
    Remplace les retours à la ligne et séquences d'espaces par un seul espace.
    """
    return re.sub(r"\s+", " ", text).strip()



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


mcq_text = extract_text_from_pdf("./../EPAC_Exams/2022 - EPAC_exam_mcq_en_Part1.pdf")
solution_text = extract_text_from_pdf("./../EPAC_Exams/2022 - EPAC_Solution_mcq&open.pdf")

# === NORMALISATION DES SAUTS DE LIGNE ===
mcq_text = re.sub(r"\n{2,}", "\n", mcq_text)  # Remplace plusieurs sauts de ligne consécutifs par un seul

# === LANCEMENT DE L'EXTRACTION ===
mcq_questions = extract_mcq_questions(mcq_text)
mcq_solutions = extract_mcq_solutions(solution_text)

# === ASSOCIATION DES RÉPONSES AUX QUESTIONS ===
for i, question in enumerate(mcq_questions):
    question_number = i + 1  # Les questions sont numérotées à partir de 1
    question["solution"] = mcq_solutions.get(question_number, "Non disponible")  # Ajoute la réponse correcte si disponible

# === AFFICHAGE DES RÉSULTATS POUR VÉRIFICATION ===
print("\nExemple des questions extraites avec choix de réponse et solution :")
for q in mcq_questions:  # Afficher toutes les questions extraites
    print("\nQuestion :", q["question"])
    for choice in q["choices"]:
        print("  ", choice)
    print("Réponse correcte :", q["solution"])



