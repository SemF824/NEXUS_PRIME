# executives/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from main import NexusAgenticSystem

app = FastAPI(title="NEXUS Prime API", description="Moteur de triage d'urgence Cloud", version="35.0")
nexus = NexusAgenticSystem()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TicketRequest(BaseModel):
    texte: str

@app.post("/api/evaluer")
async def evaluer_ticket_api(request: TicketRequest):
    # 1. Évaluation via ton moteur de qualification
    domaine, score, friction = nexus.evaluator.evaluer_ticket(request.texte)
    niveau = "🔴 CRITIQUE" if score >= 8 else "🟠 HAUTE" if score >= 5 else "🟢 BASSE"

    # 2. Vérification si le ticket est complet
    if friction != "COMPLET":
        # Génération asynchrone de la question par le LLM
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
        # Fin de l'appel, on log en base de données
        nexus.logger.log(request.texte, domaine, [], score, statut="CLOS")
        return {
            "statut": "COMPLET",
            "resultat": {
                "domaine_final": domaine,
                "score_sur_10": score,
                "niveau_alerte": niveau
            }
        }