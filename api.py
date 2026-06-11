# executives/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from main import NexusAgenticSystem

# 1. Initialisation de l'application Web et de l'IA Agentique
app = FastAPI(title="NEXUS Prime API", description="Moteur de triage d'urgence 100% Local (Mistral)", version="35.0")
nexus = NexusAgenticSystem()

# 2. Configuration du Middleware CORS pour ton futur Front-End
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Déclenchement automatique du pré-chauffage de Mistral à l'allumage du serveur
@app.on_event("startup")
async def startup_event():
    print("🔥 [STARTUP] Activation de l'écoute asynchrone du LLM (Mistral 7B)...")
    await nexus.prechauffer_cerveau()

# 4. Schéma des données d'entrée attendues
class TicketRequest(BaseModel):
    texte: str

# 5. Route principale de routage tactique
@app.post("/api/evaluer")
async def evaluer_ticket_api(request: TicketRequest):
    # Évaluation en temps réel via ton moteur Scikit-Learn / Formule logique
    domaine, score, friction = nexus.evaluator.evaluer_ticket(request.texte)
    niveau = "🔴 CRITIQUE" if score >= 8 else "🟠 HAUTE" if score >= 5 else "🟢 BASSE"

    # Si des données vitales manquent (comme la localisation)
    if friction != "COMPLET":
        # Génération chirurgicale de la relance par Mistral
        statut, question_bot = await nexus.generer_question_bot(
            transcript=f"Client: {request.texte}", 
            texte_utilisateur=request.texte, 
            domaine=domaine, 
            score_actuel=score
        )
        return {
            "statut": "INCOMPLET",
            "domaine_pressenti": domaine,
            "question_ia": question_bot,
            "friction_detectee": friction
        }
    else:
        # Si le dossier est complet, enregistrement en BDD et clôture
        nexus.logger.log(request.texte, domaine, [], score, statut="CLOS")
        return {
            "statut": "COMPLET",
            "resultat": {
                "domaine_final": domaine,
                "score_sur_10": score,
                "niveau_alerte": niveau
            }
        }