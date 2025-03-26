# Étape 1 : base Python légère
FROM python:3.10-slim

# Ne pas générer de fichiers .pyc et désactiver le buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système utiles
RUN apt-get update && apt-get install -y git && apt-get clean

# Dossier de travail
WORKDIR /app

# Copier les dépendances Python
COPY requirements.txt .

# Installer les paquets Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier tous les fichiers du projet dans l'image
COPY . .

# Exposer le port de Flask
EXPOSE 5000

# Lancer l'application Flask automatiquement
CMD ["python", "rag.py"]
