# executives/ui.py
import gradio as gr
import asyncio
from main import NexusAgenticSystem

# Initialisation du noyau dur
nexus = NexusAgenticSystem()

async def interaction_nexus(message, history):
    if not nexus.llm_en_ligne:
        await nexus.prechauffer_cerveau()

    # Analyse du message via Scikit-Learn
    domaine, score, friction = nexus.evaluator.evaluer_ticket(message)

    # Si le ticket n'est pas parfait
    if friction != "COMPLET":
        statut, question_bot = await nexus.generer_question_bot(
            transcript=f"Client: {message}",
            texte_utilisateur=message,
            domaine=domaine,
            score_actuel=score
        )
        return f"🚨 [Analyse: {domaine} | Urgence: {score}/10]\nNEXUS: {question_bot}"
    
    # Si le dossier est validé
    else:
        niveau = "🔴 CRITIQUE" if score >= 8 else "🟠 HAUTE" if score >= 5 else "🟢 BASSE"
        nexus.logger.log(message, domaine, [], score, statut="CLOS")
        return f"✅ TICKET CLOS ET TRANSMIS.\nDomaine : {domaine}\nNiveau Alerte : {niveau}\nLes unités sont en route."

# Définition de l'interface graphique (Style Chat)
app = gr.ChatInterface(
    fn=interaction_nexus,
    title="NEXUS Prime - Centre de Commandement",
    description="Entrez la situation d'urgence. Moteur hybride tactique (Scikit-Learn + Llama 3.3 / Gemma 4).",
    fill_height=True
)

if __name__ == "__main__":
    # Lancement sur le port 7860 ouvert sur ton pare-feu GCP
    app.launch(server_name="0.0.0.0", server_port=7860)