#!/bin/bash

export PYTHONUNBUFFERED=1

echo "🔥 [1/3] Démarrage du daemon Ollama natif CUDA..."
ollama serve > /var/log/ollama_engine.log 2>&1 &

echo "⏳ En attente de l'hyperviseur matérielle..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 2
done

echo "📥 [2/3] Chargement du modèle LLM local gemma4:e4b..."
ollama pull gemma4:e4b

echo "⚙️ [2.5/3] Alignement structurel : Protection du binaire ML..."
# ANCHOR : On ne lance plus nexus_audit_expert.py ici pour éviter de générer un micro-dataset asymétrique.
echo "✅ Modèle statistique figé préservé."

echo "🚀 [3/3] Démarrage du Centre de Commandement..."
cd executives
python3 ui.py