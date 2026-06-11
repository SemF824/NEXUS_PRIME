# Utilisation de l'image de calcul NVIDIA officielle avec drivers de développement inclus
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

# Variables d'environnement de production pour le runtime Python et Ollama
ENV PYTHONUNBUFFERED=1
ENV TMPDIR=/tmp
ENV DEBIAN_FRONTEND=noninteractive

# Installation des outils système essentiels, Python et curl
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    curl \
    git \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Mise à niveau des outils de build Python globaux
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Installation d'Ollama en mode natif (il compilera ses kernels pour la L4 sm_89 automatiquement)
RUN curl -fsSL https://ollama.com/install.sh | sh

# Configuration de l'espace de travail
WORKDIR /app

# Gestion et isolation des dépendances Python
COPY executives/requirements.txt .

# VERROUILLAGE CHIRURGICAL : 
# 1. On installe d'abord le gros des dépendances (gradio, transformers, etc.)
# 2. On FORCE la réinstallation des versions exactes de Kaggle par-dessus pour casser les dépendances v1.7+
RUN pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir scikit-learn==1.5.2 joblib==1.4.2 numpy==1.26.4 --force-reinstall

# Copie globale du code applicatif
COPY . /app

# Droits d'exécution du script d'orchestration
RUN chmod +x /app/start.sh

# Nettoyage des entrypoints par défaut
ENTRYPOINT []

# Exposition des ports du Centre de Commandement et d'Ollama
EXPOSE 7860 11434

# Lancement du pipeline
CMD ["/app/start.sh"]