from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import random
import re
import requests
from transformers import pipeline
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURATION API ---
SCW_API_KEY = os.getenv("SCW_API_KEY") or "" # API key for Scaleway here
SCW_ENDPOINT = "https://api.scaleway.ai/1138408b-5317-4d40-83b1-24ebe6b8ed96/v1/chat/completions"
MODEL_NAME = "mistral-nemo-instruct-2407"

# --- SYSTEM PROMPT ---
system_prompt = """You are a legal assistant specialising in European patent law.

Your task is to answer questions solely on the basis of the documents provided (context injected via RAG). 
You can use the data and rephrase it but please do not add any new information.

You must :
Be factual, structured, concise and legally rigorous
Never generate repetition: avoid answering with similar questions or identical wording that is not necessary in an answer
do not generate multiple questions and answers in your response

If the question is off-topic, nonsensical, or contains characters or words not related to the context given (RAG), respond:
'I cannot answer this question with certainty because the documents provided do not cover this point sufficiently.'

If the question is too short or contains random characters (e.g., 'sifzrfh'), also respond:
'I cannot answer this question with certainty because the documents provided do not cover this point sufficiently.'

You are evaluated for your ability to:
Use only the documents provided
Be legally accurate
Not generate unnecessary repetitions or hallucinations
"""

# --- INITIALISATION DES PIPELINES DE TRADUCTION ---
translator_fr = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
translator_en = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

def traduire(text, target="fr", chunk_size=450):
    # Utilisation du pipeline déjà initialisé pour la traduction
    if target == "fr":
        translator = translator_fr
    else:
        translator = translator_en

    # Découpe du texte en morceaux si nécessaire
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    translated = []

    # Traduction par morceaux
    for chunk in chunks:
        translated_text = translator(chunk, max_length=512)[0]["translation_text"]
        translated.append(translated_text)

    return " ".join(translated)


# === CHARGEMENT DES DOCUMENTS POUR LE RAG ===  (en fonction des fichiers sources, les jsonl n'ont pas été formatés avec les même mot clés et de la même façon d'ou le grand nombre de fonction pour extraire les données)
def load_jsonl_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def extract_rules(paths):
    docs = []
    for path in paths:
        for data in load_jsonl_lines(path):
            rnum = data.get("numRule", "")
            rname = data.get("nameRule", "").strip()
            if rnum and rname:
                docs.append(f"Rule {rnum}: {rname}")
            for key, val in data.items():
                if key.startswith("ssRule") and isinstance(val, str):
                    docs.append(f"Implementing Regulation - Rule {rnum}: {val.strip()}")
    return docs

def extract_legislation(paths):
    docs = []
    def recurse(sec, title=""):
        if isinstance(sec, dict):
            for k, v in sec.items():
                if isinstance(v, dict):
                    recurse(v, v.get("title", k))
                elif isinstance(v, str) and v.strip():
                    docs.append(f"{title}: {v.strip()}")
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for chap, content in data.items():
                recurse(content, chap)
    return docs

def extract_paperD_questions(path):
    return [
        re.sub(r"(Human|AI|Question\s*\d+:?)", "", d.get("question", "").strip())
        for d in load_jsonl_lines(path)
        if len(d.get("question", "")) > 50
    ]

def extract_articles(path):
    return [
        f"{d['Article']}: {d['Title']}\n\n{d['Description']}"
        for d in load_jsonl_lines(path)
        if d.get("Article") and d.get("Title") and d.get("Description")
    ]

def extract_rules_json(path):
    return [
        f"Article: {d['Article']}\nTitle: {d['Title']}\nContent: {d['Description']}"
        for d in load_jsonl_lines(path)
        if d.get("Article") and d.get("Title") and d.get("Description")
    ]

def extract_open_questions(path):
    return [
        f"Contexte: {d['contexte']}\n\nQuestion: {d['question']}\n\nRéponse: {d['reponse']}"
        for d in load_jsonl_lines(path)
        if d.get("contexte") and d.get("question") and d.get("reponse")
    ]

def extract_pre_exam(path):
    return [
        f"Contexte: {d['contexte']}\n\nQuestion: {d['question']}\n\nRéponse: {d['answer']}\n\nExplication: {d['explanation']}"
        for d in load_jsonl_lines(path)
        if d.get("contexte") and d.get("question") and d.get("answer")
    ]

def load_all_docs():
    docs = []
    docs += extract_rules([
        "./donnees/legislatif/ART_conventionOnGrandEuroPatent.jsonl",
        "./donnees/legislatif/RULE_implementingRegulation.jsonl"
    ])
    docs += extract_legislation([f"./donnees/legislatif/Part_{x}.jsonl" for x in "ABCDEFGH"])
    docs += extract_paperD_questions("./donnees/paperD_output.jsonl")
    docs += extract_articles("./donnees/PCT_articles.jsonl")
    docs += extract_rules_json("./donnees/resteEPC.jsonl")
    docs += extract_rules_json("./donnees/pct_rules.jsonl")
    docs += extract_open_questions("./donnees/EPAC_open_output.jsonl")
    docs += extract_pre_exam("./donnees/Pre-Exam_output.jsonl")
    return docs

# Texte parasite dans les réponses du modèle à certain moment. On a pas eu le temps de vérifier si cela venait plus de notre découpage des réponses ou du modèle lui même. Solution temporaire pour nettoyer les réponses par manque de temps.
def nettoyer_reponse_ia(texte):
    match = re.search(r"(Answer:|Comment:)", texte, re.IGNORECASE)
    if match:
        return texte[match.start():].strip()
    return texte.strip()

print("Chargement des documents...")
context_chunks = load_all_docs()
print(f"{len(context_chunks)} documents chargés.")

print("Création des embeddings...")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#utilisation d'une bdd vectorielle pour stocker nos données et rendre les recherches plus rapides. Stockage persistant pour ne pas avoir à recharger les données à chaque fois
vectordb = Chroma.from_texts(context_chunks, embedding=embedding_model, persist_directory="epac_chroma_db")
retriever = vectordb.as_retriever() #transforme notre bdd en un objet retriever permettant de faire des recherches de documents en fonction de la question posée cherchant les documents les plus proches de la question posée
print("Base vectorielle prête.")

app = Flask(__name__, static_folder="static") #initialisation de l'application flask
CORS(app) 

def appeler_llm(prompt):
    # Appel de l'API Scaleway qui héberge notre modèle de langage
    headers = {
        "Authorization": f"Bearer {SCW_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 512
    }
    response = requests.post(SCW_ENDPOINT, headers=headers, json=payload)
    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e} – {response.text}"

# Fonction pour récupérer le contexte des documents les plus proches de la question posée
def get_context(question):
    docs = retriever.invoke(question)
    return "\n\n".join(d.page_content for d in docs)

# Fonction pour poser une question à notre modèle de langage en associant le contexte des documents les plus proches de la question posée
def rag_with_llm(question):
    context = get_context(question)
    full_prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
    return appeler_llm(full_prompt)

def charger_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f]

qcm_questions = charger_questions("./donnees/EPAC_qcm_output.jsonl")

def justifier_par_rag(q_text, correct_ans, choices):
    p = f"""
Here is a multiple-choice question from an EPAC exam.

Question: {q_text}

Choices:
A. {choices.get("A")}
B. {choices.get("B")}
C. {choices.get("C")}
D. {choices.get("D")}

The correct answer is: {correct_ans}

Can you explain why this answer is correct? Support your explanation with legal reasoning if possible.
"""
    return rag_with_llm(p)

# on récupère une question aléatoire dans notre base de questions et on la traduit si besoin
@app.route("/training", methods=["GET"])
def training():
    lang = request.args.get("lang", "en")
    q = random.choice(qcm_questions)
    question_text = q["question"]
    choices = q["choices"]

    if lang == "fr":
        question_text = traduire(question_text, target="fr")
        choices = {k: traduire(v, target="fr") for k, v in choices.items()}

    return jsonify({
        "question_id": qcm_questions.index(q),
        "question": question_text,
        "choices": choices
    })

# on récupère la réponse à la question posée par l'utilisateur et on vérifie si elle est correcte ou non et fournir une explication
@app.route("/training_answer", methods=["POST"])
def training_answer():
    data = request.json
    qid = data.get("question_id")
    rep = data.get("answer", "").upper()
    lang = data.get("lang", "en")

    if qid is None or rep not in "ABCD":
        return jsonify({"error": "Invalid data"}), 400

    q = qcm_questions[int(qid)]
    correct = (rep == q["answer"].upper())
    explanation_en = justifier_par_rag(q["question"], q["answer"], q["choices"])
    explanation = traduire(explanation_en, target="fr") if lang == "fr" else explanation_en

    return jsonify({
        "correct": correct,
        "correct_answer": q["answer"],
        "explanation": explanation
    })

# on pose une question à notre modèle de langage et on récupère la réponse
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    lang = data.get("lang", "en")

    if not question:
        return jsonify({"error": "Missing question"}), 400

    if lang == "fr":
        question = traduire(question, target="en")

    reponse = rag_with_llm(question)
    reponse_nettoyee = nettoyer_reponse_ia(reponse)

    if lang == "fr":
        reponse_nettoyee = traduire(reponse_nettoyee, target="fr")

    return jsonify({"response": reponse_nettoyee})

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "chatbot.html")

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")