# Chatbot Bulgattle

Ce projet implémente un chatbot basé sur Flask, utilisant une interface web pour interagir avec les utilisateurs. Il est développé dans le cadre de l'application **Bulgattle**.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants :

- [Docker](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/downloads/)

## Installation

### 1. Cloner le dépôt

Commencez par cloner le dépôt GitHub du projet sur votre machine locale :

```bash
git clone https://github.com/YannPrz/Bulgattle.git
cd Bulgattle
```

### 2. Ajouter votre utilisateur au groupe Docker

Avant de pouvoir exécuter Docker sans utiliser sudo, vous devez ajouter votre utilisateur au groupe Docker. Exécutez les commandes suivantes :

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Ajouter la clef API Scaleway

Une fois dans le répertoire, il faut ajouter la clef API Scaleway dans le fichier rag.py

```bash
SCW_API_KEY = os.getenv("SCW_API_KEY") or "Your API key"
```

### 4. Construire l'image Docker

Puis construisez l'image Docker avec la commande suivante :

```bash
docker build -t epac-chatbot .
```

### 5. Lancer l'application Docker

Ensuite, lancez le conteneur Docker en exposant le port 5000 :

```bash
docker run -p 5000:5000 --name epac-container epac-chatbot
```

### 6. Accéder à l'interface web

Double-cliquez sur le fichier chatbot.html dans le dossier static pour ouvrir l'interface du chatbot dans votre navigateur.

## Arrêter et relancer le conteneur Docker

### Arrêter le conteneur

Si vous souhaitez arrêter le conteneur en cours d'exécution, utilisez la commande suivante :

```bash
docker stop epac-container
```

### Relancer le conteneur

Pour relancer le conteneur arrêté, exécutez cette commande :

```bash
docker start -a epac-container
```
Cela redémarrera le conteneur et vous permettra de continuer à interagir avec l'application.


## Structure du projet

Voici un aperçu de la structure des fichiers du projet :

```bash
Bulgattle/
├── Dockerfile               # Définition de l'image Docker
├── donnees/                 # Dossier contenant les données utilisées par le chatbot
├── extractionDonnees        # Dossier contenant les codes ayant permis l'extraction des données fournis
├── rag.py                   # Code principal du chatbot avec Flask
├── requirements.txt         # Dépendances Python nécessaires
├── static/                  # Fichiers statiques (HTML, CSS, JS)
└── README.md                # Documentation du projet
```

## Dépendances

Le projet repose sur certaines dépendances Python qui sont listées dans le fichier requirements.txt.

```bash
flask
flask-cors
requests
chromadb
scikit-learn
sentence-transformers
langchain
langchain-community
langchain-huggingface
langchain-chroma
sentencepiece
sacremoses
```

## Auteurs

Camille Solacroup
Thomas Beaussart
Mattéo Reyne
Yann Perez-Ferron
Julien Gitton