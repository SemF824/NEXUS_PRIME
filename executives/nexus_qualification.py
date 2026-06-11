# executives/nexus_qualification.py
import joblib
import os
import numpy as np
import pandas as pd
from nexus_config import MODEL_UNIFIED_PATH

class QualificationEngine:
    def __init__(self):
        self.model = None
        self.mode = "LOCAL_LLM"
        
        # Chargement strict et isolé du modèle statistique unifié V35
        if os.path.exists(MODEL_UNIFIED_PATH):
            try:
                # Chargement du pipeline complet (TF-IDF + RandomForest unifiés)
                loaded_pipeline = joblib.load(MODEL_UNIFIED_PATH)
                
                # Vérification de la présence des composants essentiels pour valider l'alignement
                if hasattr(loaded_pipeline, 'named_steps') and 'tfidf' in loaded_pipeline.named_steps:
                    self.model = loaded_pipeline
                    self.mode = "ML"
                    vocab_size = len(loaded_pipeline.named_steps['tfidf'].vocabulary_)
                    print(f"🔌 Cerveau Unifié ML couplé avec succès. Vecteurs alignés ({vocab_size} dimensions) : {MODEL_UNIFIED_PATH}")
                else:
                    self.model = loaded_pipeline
                    self.mode = "ML"
                    print(f"🔌 Checkpoint ML chargé (structure brute) : {MODEL_UNIFIED_PATH}")
            except Exception as e:
                print(f"⚠️ Alerte alignement : Le fichier .pkl existant présente un conflit de version binaire ({e}).")
                self.model = None
                self.mode = "LOCAL_LLM"
        else:
            print("💡 Aucun checkpoint .pkl détecté à l'emplacement nominal. Mode Local LLM actif.")

    def calculer_score_logique(self, severite, impact, cible):
        """Formule stratégique d'urgence Nexus."""
        try:
            sev = float(severite)
            imp = float(impact)
            cib = float(cible)
            score_base = ((sev * 2) + imp + cib) / 2
            
            if sev >= 4:
                return max(score_base, 8.5)
            elif sev >= 3:
                return max(score_base, 6.0)
            return round(score_base, 1)
        except (ValueError, TypeError):
            return 5.0

    def evaluer_ticket(self, texte):
        """Triage statistique instantané via le premier rideau sémantique."""
        if self.mode == "ML" and self.model is not None:
            try:
                # L'inférence applique automatiquement la transformation TF-IDF d'origine
                prediction = self.model.predict([texte])[0]
                
                if len(prediction) == 5:
                    domaine = str(prediction[0])
                    severite = int(float(prediction[1]))
                    impact = int(float(prediction[2]))
                    cible = int(float(prediction[3]))
                    friction = str(prediction[4])
                    
                    score = self.calculer_score_logique(severite, impact, cible)
                    return domaine, score, friction
            except Exception as e:
                print(f"❌ Décalage de vecteurs intercepté lors de l'inférence : {e}")
        
        # Fallback sémantique léger en cas de rupture complète du binaire
        domaine = "MÉDICAL" if any(w in texte.lower() for w in ["sang", "coeur", "respires", "accident"]) else "DIGITAL SUPPORT"
        return domaine, 2.5, "MANQUE_LIEU"