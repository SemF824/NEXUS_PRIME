#!/bin/bash

echo "🔥 [1/3] Démarrage du moteur Ollama en arrière-plan..."
ollama serve &

# Laisser 5 secondes à Ollama pour s'initialiser
sleep 5

echo "📥 [2/3] Chargement des modèles IA (Mistral)..."
# Modifie "mistral" par "codestral" ici si tu veux utiliser le gros modèle
ollama pull mistral

echo "🚀 [3/3] Démarrage de l'API NEXUS (FastAPI)..."
cd executives
# On lance le serveur web Uvicorn
uvicorn api:app --host 0.0.0.0 --port 7860