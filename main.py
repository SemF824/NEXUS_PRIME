# executives/main.py
import asyncio
import sqlite3
import datetime
import warnings
import sys
import re
import textwrap
import os
from ollama import AsyncClient
from groq import AsyncGroq
import nexus_config
from nexus_qualification import QualificationEngine
from nexus_matrix import DOMAINES

warnings.filterwarnings("ignore")

# =====================================================================
# MODULE 1 : BASE DE DONNÉES & LOGGING (MUTLI-THREAD)
# =====================================================================
class ShadowLogger:
    def __init__(self):
        self.conn = sqlite3.connect(nexus_config.DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS interactions_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date_log TEXT, ticket_complet TEXT,
            domaine_principal TEXT, domaines_secondaires TEXT, score REAL, statut TEXT)''')
        self.conn.commit()

    def log(self, ticket_final, domaine_principal, sec_list, score, statut="CLOS"):
        date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sec_str = ", ".join(sec_list) if sec_list else "AUCUN"
        try:
            self.cursor.execute('''INSERT INTO interactions_log (date_log, ticket_complet, domaine_principal, domaines_secondaires, score, statut)
                VALUES (?, ?, ?, ?, ?, ?)''', (date_now, ticket_final, domaine_principal, sec_str, score, statut))
            self.conn.commit()
        except sqlite3.OperationalError:
            self.cursor.execute('DROP TABLE IF EXISTS interactions_log')
            self.cursor.execute('''CREATE TABLE interactions_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date_log TEXT, ticket_complet TEXT,
                domaine_principal TEXT, domaines_secondaires TEXT, score REAL, statut TEXT)''')
            self.cursor.execute('''INSERT INTO interactions_log (date_log, ticket_complet, domaine_principal, domaines_secondaires, score, statut)
                VALUES (?, ?, ?, ?, ?, ?)''', (date_now, ticket_final, domaine_principal, sec_str, score, statut))
            self.conn.commit()

        print("\n" + "📊 " + "=" * 25 + " DATABASE COMMIT OVERSIGHT " + "=" * 25)
        print(f" 📅 Horodatage : {date_now}")
        print(f" 📂 Statut Log : {statut}")
        print(f" 🎯 Domaine Maître : {domaine_principal} | Urgence Score : {score}/10")
        print(f" 🚨 Renforts Unit  : {sec_str}")
        print(f" 📝 Transcript Final Reconstitué :\n    {ticket_final}")
        print("=" * 78 + "\n")

# =====================================================================
# MODULE 2 : EXÉCUTION TACTIQUE
# =====================================================================
class TaskExecutor:
    @staticmethod
    def declencher_protocoles(domaines_impliques, niveau_urgence, resume_ticket, motif_cloture="STANDARD"):
        print("\n   ⚡ DÉCLENCHEMENT DES TÂCHES OPÉRATIONNELLES (MULTI-SERVICES) :")
        if motif_cloture == "SILENCE_CRITIQUE":
            print("      [ALERTE] 🚨 RUPTURE DE LIAISON DÉTECTÉE - PROTOCOLE D'URGENCE ABSOLUE ACTIVÉ")
        elif motif_cloture == "CRI_DETECTE":
            print("      [ALERTE] 🚨 PANIQUE ACOUSTIQUE DÉTECTÉE - INTERVENTION MAXIMUM IMMÉDIATE")
        if niveau_urgence == "🔴 CRITIQUE":
            print("      [API] 📡 Broadcast SMS d'alerte aux superviseurs d'astreinte -> ENVOYÉ")
        for domaine in domaines_impliques:
            print(f"\n      --- Unité En Alerte : {domaine} ---")
            if domaine == "POMPIER":
                print("      [WEBHOOK] 🚒 Transmission au SDIS local (Code Rouge) -> OK")
                print("      [TASK] 🗺️ Extraction des coordonnées GPS pour les engins -> EN COURS")
            elif domaine == "POLICE":
                print("      [WEBHOOK] 🚓 Alerte patrouille secteur en cours (Sécurisation) -> OK")
            elif domaine == "ÉNERGIE & INFRASTRUCTURES" or domaine == "CYBERSÉCURITÉ":
                print("      [WEBHOOK] ⚡ Alerte Cellule de Crise Infrastructure -> OK")
            elif domaine == "MÉDICAL":
                print("      [WEBHOOK] 🚑 Transmission du bilan au SAMU (Régulation 15) -> OK")
            elif domaine == "EN_ATTENTE":
                print("      [DISPATCH] 🗑️ Appel fantôme / Erreur de ligne -> ARCHIVÉ SANS SUITE")
            else:
                print(f"      [DISPATCH] 📨 Transmission standard au centre {domaine} -> OK")

# =====================================================================
# MODULE 3 : MOTEUR COGNITIF HYBRIDE
# =====================================================================
class NexusAgenticSystem:
    def __init__(self):
        print(f"🧠 Initialisation NEXUS V_ULTIME (Cloud & Local {nexus_config.MODEL_LOCAL})...")
        self.logger = ShadowLogger()
        self.evaluator = QualificationEngine()
        self.executor = TaskExecutor()

        # Moteur local (Gemma 4 Edge branché sur ton runtime CUDA interne)
        self.client_llm = AsyncClient()
        self.local_model = nexus_config.MODEL_LOCAL
        self.llm_en_ligne = False

        # Moteur Cloud secondaire (Groq) - Clé obsolète gérée en failover transparent
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_disponible = bool(self.groq_key)
        if self.groq_disponible:
            self.client_groq = AsyncGroq(api_key=self.groq_key)
            print("🌐 [CLOUD] Client Groq initialisé.")
        else:
            print("⚠️ [WARN] Clé GROQ_API_KEY introuvable ou révoquée. Souveraineté locale exclusive.")

    async def prechauffer_cerveau(self):
        print(f"🔥 Pré-chauffage du bouclier local {self.local_model} en cours...")
        try:
            await self.client_llm.chat(model=self.local_model, messages=[{'role': 'user', 'content': 'ping'}],
                                       options={'num_predict': 1})
            self.llm_en_ligne = True
            print(f"✅ Moteur local {self.local_model} paré et monté en RAM.")
        except Exception as e:
            self.llm_en_ligne = False
            print(f"⚠️ ERREUR CRITIQUE LOCAL : Impossible de joindre Ollama. {e}")
        
        if self.groq_disponible:
            print(f"📡 Vérification du pipeline Groq Cloud ({nexus_config.MODEL_CLOUD})...")
            try:
                await self.client_groq.chat.completions.create(
                    model=nexus_config.MODEL_CLOUD,
                    messages=[{'role': 'user', 'content': 'ping'}],
                    max_tokens=1,
                    timeout=5.0
                )
                print(f"✅ [STATUS] Inférence Cloud active ({nexus_config.MODEL_CLOUD}).")
            except Exception as e:
                self.groq_disponible = False
                print(f"🚨 [LOG API GROQ] Échec du canal de communication Cloud : {e}")

    def est_salutation_basique(self, texte):
        t_clean = texte.strip().lower()
        t_clean = re.sub(r'[^\w\s]', '', t_clean)
        return t_clean in ["bonjour", "salut", "allo", "allô", "bonsoir", "oui", "non", "ok"]

    def detecter_choc_acoustique(self, texte):
        t = texte.upper()
        mots_chocs = ["AU SECOURS", "AIDEZ-MOI", "ÇA EXPLOSE", "AU FEU", "JE MEURS", "AAAA", "VITE VITE"]
        if any(mot in t for mot in mots_chocs):
            return True
        if len(t) > 5 and sum(1 for c in texte if c.isupper()) / len(texte) > 0.6:
            return True
        return False

    def verifier_presence_localisation(self, texte):
        t = texte.lower()
        indicateurs_forts = ["gare", "aéroport", "hôpital", "clinique", "mairie", "préfecture", "super u"]
        if any(ind in t for ind in indicateurs_forts): return True
        voirie = r'\b(rue|avenue|boulevard|impasse|allée|chemin|route|place|square|pont)\b'
        if re.search(voirie, t): return True
        if re.search(r'\b\d{5}\b', t): return True
        return False

    async def generer_question_bot(self, transcript, texte_utilisateur, domaine, score_actuel):
        """
        Rôle d'Ollama / Gemma 4 : Gérer l'interaction, piloter les relances de friction
        et analyser si de nouvelles infos permettent de DÉQUALIFIER la sévérité du ticket.
        """
        if self.est_salutation_basique(texte_utilisateur):
            return "EN_COURS", "Ici les urgences. Quel est votre problème et où vous trouvez-vous ?"
            
        if not self.groq_disponible and not self.llm_en_ligne:
            return "EN_COURS", "Décrivez votre urgence et votre adresse exacte."

        prompt_base = f"""Rôle : Régulateur intelligent et expert de crise (Froid, analytique, direct).
        Domaine d'urgence identifié en amont : {domaine}
        Criticité actuelle estimée : {score_actuel}/10

        HISTORIQUE DE L'ÉCHANGE :
        {transcript}

        Dernier message reçu de l'appelant : "{texte_utilisateur}"

        DIRECTIVES AGENTIQUES CRITIQUES :
        1. RE-EVALUATION / DEQUALIFICATION : Analyse l'échange. Si l'appelant apporte des éléments contradictoires, rassurants ou minimisants ("c'est une blague", "fausse alerte", "je regarde un film"), tu as le pouvoir de DÉQUALIFIER la situation.
        2. STRATÉGIE DE RELANCE : Si une localisation (adresse ou repère majeur comme "Super U", "Gare de Rennes") manque pour déclencher les secours, pose UNE SEULE question chirurgicale. Moins de 12 mots. Pas de politesse.
        3. CONDITION DE CLÔTURE : Si le danger est caractérisé ET qu'une localisation valide figure dans le transcript, réponds EXCLUSIVEMENT par le token : ###CLOS###

        Génère ta réponse finale :"""

        contenu = ""

        # Trajectoire Cloud si configurée
        if self.groq_disponible:
            try:
                response = await self.client_groq.chat.completions.create(
                    model=nexus_config.MODEL_CLOUD,
                    messages=[{'role': 'system', 'content': prompt_base}],
                    temperature=0.0,
                    max_tokens=30,
                    timeout=5.0
                )
                contenu = response.choices[0].message.content.strip()
            except Exception:
                self.groq_disponible = False

        # Trajectoire Locale Souveraine : Gemma 4 en action
        if not contenu and self.llm_en_ligne:
            prompt_local = "<|think|>\n" + prompt_base
            try:
                reponse = await asyncio.wait_for(
                    self.client_llm.chat(model=self.local_model, messages=[{'role': 'user', 'content': prompt_local}],
                                         options={'temperature': 0.0}), timeout=60.0
                )
                contenu = reponse['message']['content'].strip()
                contenu = re.sub(r'<think>.*?</think>', '', contenu, flags=re.DOTALL | re.IGNORECASE).strip()
            except asyncio.TimeoutError:
                return "EN_COURS", "Liaison instable. Répétez votre position s'il vous plaît."
            except Exception:
                return "EN_COURS", "Je vous entends mal. Pouvez-vous répéter où vous vous trouvez ?"

        if not contenu:
            return "EN_COURS", "Liaison instable. Veuillez préciser votre localisation."

        # Interception de la clôture
        if "###CLOS###" in contenu:
            if domaine in ["MÉDICAL", "POLICE", "POMPIER"]:
                if not self.verifier_presence_localisation(texte_utilisateur) and "Rennes" not in transcript and "Super U" not in transcript:
                    return "EN_COURS", "Donnez-moi un repère visuel précis ou une rue pour envoyer les secours."
            return "COMPLET", ""

        contenu = contenu.replace("###CLOS###", "").strip()
        contenu = re.sub(r'^(Régulateur\s*:|Client\s*:|Ta réponse\s*:|Réponse\s*:|:\s*|"\s*)', '', contenu, flags=re.IGNORECASE).strip('" ')
        return "EN_COURS", contenu

    async def extraire_domaines_secondaires(self, texte_utilisateur, domaine_principal):
        if domaine_principal in ["NON_URGENT", "EN_ATTENTE"]: return []
        prompt = f"Analyse : '{texte_utilisateur}'. Principal : {domaine_principal}. Besoins de renforts ? Choix : {', '.join(DOMAINES)}. Règles : Pas le principal. Si rien : AUCUN. Si plusieurs, sépare par virgules. Aucun autre texte."
        res = ""
        
        if self.groq_disponible:
            try:
                response = await self.client_groq.chat.completions.create(
                    model=nexus_config.MODEL_CLOUD,
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=0.0, timeout=3.0
                )
                res = response.choices[0].message.content.strip().upper()
            except:
                pass

        if not res and self.llm_en_ligne:
            try:
                reponse = await asyncio.wait_for(
                    self.client_llm.chat(model=self.local_model, messages=[{'role': 'user', 'content': prompt}],
                                         options={'temperature': 0.0}), timeout=30.0)
                res = reponse['message']['content'].strip().upper()
                res = re.sub(r'<think>.*?</think>', '', res, flags=re.DOTALL | re.IGNORECASE).strip()
            except Exception:
                pass

        if not res or "AUCUN" in res: return []
        return list(set([d.strip() for d in res.split(',') if d.strip() in DOMAINES and d.strip() != domaine_principal]))

# =====================================================================
# SOUS-ROUTINE ASYNCHRONE OPTIMISÉE
# =====================================================================
async def async_input(prompt: str, timeout: float):
    loop = asyncio.get_event_loop()
    print(prompt, end="", flush=True)
    queue = asyncio.Queue()
    def got_input():
        line = sys.stdin.readline()
        loop.call_soon_threadsafe(queue.put_nowait, line)
    loop.add_reader(sys.stdin.fileno(), got_input)
    try:
        ligne = await asyncio.wait_for(queue.get(), timeout)
        return ligne.strip()
    except asyncio.TimeoutError:
        print()
        return ""
    finally:
        loop.remove_reader(sys.stdin.fileno())

# =====================================================================
# BOUCLE PRINCIPALE
# =====================================================================
async def run_terminal():
    nexus = NexusAgenticSystem()
    await nexus.prechauffer_cerveau()
    print("\n" + "=" * 70)
    print(f"🚀 NEXUS COMMAND CENTER — PIPELINE TEMPS RÉEL")
    print("=" * 70 + "\n")

    while True:
        raw = await async_input("📝 Client (Début d'appel) : ", timeout=86400)
        if raw.lower() in {"exit", "q", "quit"}: break
        if not raw: continue

        ticket_final = raw
        transcript = f"Client : {raw}\n"
        ticket_complet = False
        silence_count = 0
        motif_fermeture = "STANDARD"
        skip_generation = False

        if nexus.est_salutation_basique(ticket_final):
            domaine_maitre, score_maitre = "EN_ATTENTE", 0.0
        else:
            domaine_maitre, score_maitre, _ = nexus.evaluator.evaluer_ticket(ticket_final)

        while not ticket_complet:
            if nexus.detecter_choc_acoustique(ticket_final):
                print("   [ALERTE] 💥 PANIQUE DÉTECTÉE - BASCULE MULTI-FORCES")
                domaine_maitre = "MÉDICAL"
                score_maitre = 10.0
                motif_fermeture = "CRI_DETECTE"
                if silence_count > 0:
                    ticket_complet = True
                    break

            # Détection dynamique de déqualification conversationnelle
            if "fausse alerte" in ticket_final.lower() or "je rigolais" in ticket_final.lower() or "un film" in ticket_final.lower():
                print("   [INFO] 📉 Alerte identifiée comme nulle ou annulée. Ajustement de la sévérité.")
                score_maitre = max(1.0, score_maitre - 6.0)
                if score_maitre <= 3.0:
                    domaine_maitre = "DIGITAL SUPPORT"

            if not nexus.est_salutation_basique(ticket_final) and "fausse alerte" not in ticket_final.lower():
                domaine_courant, score_courant, friction = nexus.evaluator.evaluer_ticket(ticket_final)
                if score_courant > score_maitre:
                    score_maitre = score_courant
                    domaine_maitre = domaine_courant

            if not skip_generation:
                statut, question_bot = await nexus.generer_question_bot(transcript, ticket_final, domaine_maitre, score_maitre)
                if statut == "COMPLET":
                    ticket_complet = True
                    break
                wrapped_bot = textwrap.fill(
                    f"🤖 NEXUS ({domaine_maitre} | Score: {score_maitre}/10) : {question_bot}",
                    width=70, initial_indent="   ", subsequent_indent="      "
                )
                print(wrapped_bot)

            skip_generation = False
            complement = await async_input("   💬 Client : ", timeout=20.0)

            if complement == "":
                silence_count += 1
                if domaine_maitre in ["MÉDICAL", "POLICE", "POMPIER"]:
                    if silence_count == 1:
                        print("   🤖 NEXUS (RELANCE URGENCE) : Allô ? Répondez-moi si vous m'entendez !")
                        skip_generation = True
                        continue
                    else:
                        motif_fermeture = "SILENCE_CRITIQUE"
                        ticket_complet = True
                        break
                else:
                    print("   ⚠️ APPEL ABANDONNÉ PAR L'UTILISATEUR.")
                    nexus.logger.log(ticket_final, domaine_maitre, [], score_maitre, statut="ABANDON")
                    break

            silence_count = 0
            if complement.lower() in {"exit", "q", "quit"}:
                ticket_final = "exit"
                break

            ticket_final += " " + complement
            transcript += f"Régulateur : {question_bot}\nClient : {complement}\n"

        if ticket_final == "exit": break

        niveau = "🔴 CRITIQUE" if score_maitre >= 8 else "🟠 HAUTE" if score_maitre >= 5 else "🟢 BASSE"
        print(f"\n   ✅ APPEL CLOS — TRANSMISSION AUX UNITÉS")
        print(f"   🎯 Service Principal : {domaine_maitre}  |  🔢 Score Tactique : {score_maitre}/10  →  {niveau}")

        domaines_secondaires = await nexus.extraire_domaines_secondaires(ticket_final, domaine_maitre)
        if motif_fermeture == "CRI_DETECTE":
            domaines_secondaires = list(set(domaines_secondaires + ["POLICE", "POMPIER"]))
            domaines_secondaires = [d for d in domaines_secondaires if d != domaine_maitre]
            
        if domaines_secondaires:
            print(f"   🚨 Renforts requis identifiés : {', '.join(domaines_secondaires)}")

        domaines_impliques = [domaine_maitre] + domaines_secondaires
        nexus.executor.declencher_protocoles(domaines_impliques, niveau, ticket_final, motif_fermeture)
        nexus.logger.log(ticket_final, domaine_maitre, domaines_secondaires, score_maitre, statut=motif_fermeture)
        print("-" * 70 + "\n📝 En attente du prochain appelant...\n")

if __name__ == "__main__":
    asyncio.run(run_terminal())