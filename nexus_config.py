# executives/nexus_config.py
import os

# Chemins des bases de données et modèles ML
DB_PATH = "../nexus_bionexus.db"

# Ton modèle Kaggle
MODEL_UNIFIED_PATH = "../pickle_result/nexus_modele_final_V35.pkl"

# Configurations des Modèles LLM (Ollama Local & Cloud)
MODEL_EVALUATOR = "qwen2.5-coder"
MODEL_LOCAL = "gemma4:e4b"         # Modèle local unique pour le failover
MODEL_CLOUD = "llama-3.3-70b-versatile"

CONFIDENCE_THRESHOLD = 0.50