# executives/nexus_inference.py
import os
import ollama
from google import genai
from google.genai import types
import nexus_config

class NexusInference:
    def __init__(self):
        # Moteur principal Cloud
        self.gemini_disponible = True
        if not nexus_config.GEMINI_API_KEY:
            print("⚠️ [WARN] Clé GEMINI_API_KEY manquante. Mode dégradé (100% Local Ollama) activé.")
            self.gemini_disponible = False
        else:
            self.client_cloud = genai.Client(api_key=nexus_config.GEMINI_API_KEY)
        
        self.model_cloud = nexus_config.MODEL_CLOUD
        self.model_local = nexus_config.MODEL_LOCAL

    def _construire_prompt(self, transcript: str, domaine: str, friction: str) -> str:
        return f"""Rôle : Régulateur SAMU/112/NEXUS.
Nature de l'urgence détectée : {domaine}
Information manquante essentielle (Friction) : {friction}
Transcription de l'échange : "{transcript}"

OBJECTIF STRICT : Pose une unique question chirurgicale pour obtenir l'information manquante ({friction.lower()}).
RÈGLES DE PRODUCTION :
1. Pas de bonjour, pas de présentation ("Ici le 112"). Va droit au but.
2. Sois incisif, direct et rassurant.
3. Ta réponse doit faire moins de 15 mots.
4. Réponds exclusivement en Français.
Question :"""

    def generer_relance_urgence(self, transcript: str, domaine: str, friction: str) -> str:
        prompt = self._construire_prompt(transcript, domaine, friction)
        
        # --- STRATÉGIE 1 : TENTATIVE VIA GOOGLE GEMINI (CLOUD) ---
        if self.gemini_disponible:
            try:
                response = self.client_cloud.models.generate_content(
                    model=self.model_cloud,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=50
                    )
                )
                print("📡 [INFÉRENCE] Relance générée via Gemini Cloud API.")
                return response.text.strip()
            except Exception as e:
                print(f"🚨 [FAILOVER] Incident sur l'API Gemini : {e}. Bascule immédiate sur le moteur local...")
        
        # --- STRATÉGIE 2 : SECOURS VIA OLLAMA (LOCAL) ---
        try:
            response = ollama.generate(
                model=self.model_local,
                prompt=prompt,
                options={"temperature": 0.1, "num_predict": 50}
            )
            print(f"🔌 [INFÉRENCE] Relance générée via Ollama Local ({self.model_local}).")
            return response['response'].strip()
        except Exception as local_err:
            print(f"❌ [CRITICAL] Échec des deux moteurs d'IA : {local_err}")
            # Ultime barrière de sécurité si tout est détruit
            return f"NEXUS : Précisez votre demande concernant le domaine {domaine}. Quel est votre {friction.lower()} ?"