import sqlite3
import joblib
import warnings
import os
from scipy.sparse import hstack, csr_matrix

# On importe nos modules (assure-toi que les fichiers n'ont pas de tirets dans leurs noms)
from data_forge import generer_usine_monde_reel
from nexus_prime import charger_donnees, entrainer_modeles

warnings.filterwarnings("ignore")

DB_PATH = "nexus_bionexus.db"


def rechercher_client(nom_partiel: str):
    """Retrouve un ID client à partir d'un nom (UX friendly)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Recherche souple (non sensible à la casse)
            query = "SELECT id_client, nom_organisation FROM clients WHERE nom_organisation LIKE ?"
            cursor.execute(query, (f"%{nom_partiel}%",))
            results = cursor.fetchall()
            return results
    except sqlite3.Error:
        return []


def run_pipeline_complet():
    print("\n" + "═" * 60)
    print(" 🔥 NEXUS SYSTEM - PIPELINE D'AUTO-ENTRAÎNEMENT")
    print("═" * 60)

    # ÉTAPE 1 : La Forge (Data Generation)
    generer_usine_monde_reel()

    # ÉTAPE 2 : Nexus Prime (Entraînement)
    print("\n🧠 Ré-entraînement du cerveau en cours...")
    df = charger_donnees()
    vectorizer, domain_model, score_model = entrainer_modeles(df)

    # ÉTAPE 3 : L'Interface
    print("\n" + "═" * 60)
    print(" 🚀 INTERFACE DÉCISIONNELLE PRÊTE")
    print("═" * 60)

    while True:
        print("\n" + "-" * 60)
        ticket_text = input("📝 Description du problème : ").strip()
        if ticket_text.lower() == 'exit': break

        # UX : Recherche du client par nom au lieu d'ID
        recherche = input("👤 Nom du client (ou ID) : ").strip()
        clients_trouves = rechercher_client(recherche)

        if len(clients_trouves) == 1:
            client_id = clients_trouves[0][0]
            print(f"✅ Client identifié : {clients_trouves[0][1]} ({client_id})")
        elif len(clients_trouves) > 1:
            print("❓ Plusieurs clients trouvés :")
            for c in clients_trouves: print(f"  - {c[0]} : {c[1]}")
            client_id = input("Tapez l'ID exact : ").strip()
        else:
            print("⚠️ Aucun client trouvé, utilisation d'un profil standard.")
            client_id = "CLI-GENERIC"

        urgency_input = input("🚨 Urgence déclarée (1-5) : ").strip()
        urgency_level = int(urgency_input) if urgency_input.isdigit() else 3

        # --- INFÉRENCE ---
        X_text = vectorizer.transform([ticket_text])
        etat_num = 1 if urgency_level >= 4 else 0
        X_metadata = csr_matrix([[urgency_level, etat_num]])
        X_final = hstack([X_text, X_metadata])

        predicted_domain = domain_model.predict(X_text)[0]
        raw_score = score_model.predict(X_final)[0]
        final_score = round(raw_score, 1)

        print(f"\n[ RÉSULTAT ] Domaine: {predicted_domain} | Score: {final_score}/10")

        # Log SQL
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    INSERT INTO prediction_logs (texte_ticket, id_client, domaine_predit, score_brut_ia)
                    VALUES (?, ?, ?, ?)
                """, (ticket_text, client_id, predicted_domain, float(raw_score)))
        except:
            pass


if __name__ == "__main__":
    run_pipeline_complet()
