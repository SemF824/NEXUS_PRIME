# Dockerfile
# Base Python légère
FROM python:3.10-slim

# Éviter que Python ne stocke des logs en mémoire tampon (idéal pour voir les crashs en direct)
ENV PYTHONUNBUFFERED=1

# 1. Installer curl (requis pour installer Ollama) et dépendances système
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*

# 2. Installer le moteur Ollama dans le conteneur
RUN curl -fsSL https://ollama.com/install.sh | sh

# 3. Définir le dossier de travail
WORKDIR /app

# 4. Copier les dépendances Python et les installer
COPY executives/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier l'intégralité du projet dans le conteneur
COPY . /app

# 6. Rendre le script de démarrage exécutable
RUN chmod +x /app/start.sh

# 7. Exposer le port de l'API Web (8000) et d'Ollama (11434)
EXPOSE 8000 11434

# 8. Commande de lancement (Le chef d'orchestre)
CMD ["/app/start.sh"]