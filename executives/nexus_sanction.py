# nexus_sanction.py
# Détection des EXAGÉRATIONS ABUSIVES (déclarations gonflées dans le seul but de
# passer en priorité) + gestion de la RÉPUTATION des émetteurs et de la RÉCIDIVE.
#
# Principe : on compare la DRAMATISATION revendiquée (vocabulaire d'urgence maximale,
# majuscules, points d'exclamation...) à la GRAVITÉ RÉELLE objective (entités de danger,
# symptômes sévères, impact/urgence jugés par le modèle). Une forte dramatisation SANS
# aucun fait grave = forçage de priorité => avertissement gradué + journalisation.
import sqlite3
import re
import datetime

from nexus_config import (
    DB_PATH, MOTS_EXAGERATION, SEUIL_DRAMATISATION,
    MOTS_GRAVES, SYMPTOMES_SEVERES, MOTS_DELITS, MOTS_SINISTRES,
    CORPS_SENSIBLES, MOTS_BENINS,
)


# ============================================================================
# 1. DÉTECTEUR D'EXAGÉRATION (dissonance dramatisation vs réalité)
# ============================================================================
class ExaggerationDetector:

    @staticmethod
    def mesurer_dramatisation(texte_brut: str, texte_propre: str):
        """Score de PRESSION D'URGENCE revendiquée. 0 = neutre, plus c'est haut plus ça dramatise."""
        score = 0
        details = []
        t = texte_propre.replace("’", "'")  # apostrophe typographique -> droite

        # 1. Marqueurs lexicaux de forçage de priorité (les plus parlants)
        for expr in MOTS_EXAGERATION:
            if expr in t:
                score += 2
                details.append(f"« {expr} »")

        # 2. Points d'exclamation en rafale
        nb_excl = texte_brut.count("!")
        if nb_excl >= 3:
            score += 2
            details.append(f"{nb_excl} points d'exclamation")
        elif nb_excl == 2:
            score += 1

        # 3. Cris en MAJUSCULES (mots de +3 lettres tout en capitales)
        mots_caps = [m for m in texte_brut.split() if m.isupper() and len(m) > 3]
        if len(mots_caps) >= 2:
            score += 2
            details.append(f"{len(mots_caps)} mots en capitales")

        # 4. Allongement expressif (« urgentttt », « viiite »)
        if re.search(r"(.)\1{2,}", texte_brut):
            score += 1
            details.append("lettres répétées (cri)")

        # 5. Martèlement du registre d'urgence
        nb_urgent = len(re.findall(r"\b(urgent|urgence|vite)\b", t))
        if nb_urgent >= 2:
            score += 1
            details.append(f"insistance « urgent/vite » x{nb_urgent}")

        return score, details

    @staticmethod
    def a_gravite_reelle(texte_propre: str, doc, impact: int, urgence: int, corps_trouves):
        """True s'il existe au moins UN fait objectivement grave (≠ simple vocabulaire)."""
        raisons = []

        if doc is not None and any(ent.label_ in ("ARME", "ALERTE_VITALE") for ent in doc.ents):
            raisons.append("entité de danger réelle (arme / alerte vitale)")
        if any(m in texte_propre for m in MOTS_GRAVES):
            raisons.append("mot grave factuel")
        if any(m in texte_propre for m in SYMPTOMES_SEVERES):
            raisons.append("symptôme sévère")
        if any(m in texte_propre for m in MOTS_DELITS):
            raisons.append("délit signalé")
        if any(m in texte_propre for m in MOTS_SINISTRES):
            raisons.append("sinistre signalé")
        if corps_trouves and any(c in corps_trouves for c in CORPS_SENSIBLES):
            raisons.append("partie du corps sensible touchée")
        if impact >= 3 or urgence >= 3:
            raisons.append(f"notation modèle élevée ({impact}/{urgence})")

        return (len(raisons) > 0), raisons

    def detecter(self, texte_brut, texte_propre, doc, impact, urgence, corps_trouves):
        """
        Renvoie (est_exagere: bool, niveau: int, rapport: dict).
        Exagération abusive = dramatisation >= SEUIL ET aucune gravité réelle.
        """
        score_drama, details_drama = self.mesurer_dramatisation(texte_brut, texte_propre)

        # La gravité réelle ne doit PAS être déduite des mots d'hyperbole eux-mêmes
        # (ex. « catastrophe » est à la fois hyperbole ET sinistre). On retire donc les
        # expressions de dramatisation avant de juger la gravité factuelle.
        texte_factuel = texte_propre.replace("’", "'")
        for expr in MOTS_EXAGERATION:
            if expr in texte_factuel:
                texte_factuel = texte_factuel.replace(expr, " ")

        a_grave, raisons_grave = self.a_gravite_reelle(texte_factuel, doc, impact, urgence, corps_trouves)
        benin_explicite = any(m in texte_propre for m in MOTS_BENINS)

        est_exagere = (score_drama >= SEUIL_DRAMATISATION) and (not a_grave)
        # niveau de certitude : dramatisation + bonus si le ticket est explicitement bénin
        niveau = score_drama + (2 if benin_explicite else 0)

        rapport = {
            "score_dramatisation": score_drama,
            "details_dramatisation": details_drama,
            "gravite_reelle": a_grave,
            "raisons_gravite": raisons_grave,
            "benin_explicite": benin_explicite,
        }
        return est_exagere, niveau, rapport


# ============================================================================
# 2. GESTIONNAIRE DE RÉPUTATION (récidive + sanctions graduées)
# ============================================================================
class ReputationManager:

    def __init__(self, db_path: str = DB_PATH):
        # check_same_thread=False : l'API FastAPI peut être multi-thread.
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reputation_emetteurs (
                emetteur_id        TEXT PRIMARY KEY,
                nb_exagerations    INTEGER DEFAULT 0,
                premiere_infraction TEXT,
                derniere_infraction TEXT,
                score_confiance    REAL DEFAULT 1.0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sanctions_log (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                date_log          TEXT,
                emetteur_id       TEXT,
                ticket            TEXT,
                niveau_dissonance INTEGER,
                details           TEXT,
                sanction          TEXT
            )
        """)
        self.conn.commit()

    @staticmethod
    def _confiance(nb: int) -> float:
        """Score de confiance qui se dégrade à chaque récidive (plancher à 0)."""
        return round(max(0.0, 1.0 - 0.2 * nb), 2)

    def get_reputation(self, emetteur_id: str):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT nb_exagerations, score_confiance FROM reputation_emetteurs WHERE emetteur_id = ?",
            (emetteur_id,),
        )
        row = cur.fetchone()
        return (row[0], row[1]) if row else (0, 1.0)

    def enregistrer_infraction(self, emetteur_id: str) -> int:
        """Incrémente le compteur d'exagérations de l'émetteur et renvoie le nouveau total."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()
        cur.execute(
            "SELECT nb_exagerations FROM reputation_emetteurs WHERE emetteur_id = ?",
            (emetteur_id,),
        )
        row = cur.fetchone()
        if row is None:
            nb = 1
            cur.execute(
                "INSERT INTO reputation_emetteurs "
                "(emetteur_id, nb_exagerations, premiere_infraction, derniere_infraction, score_confiance) "
                "VALUES (?, ?, ?, ?, ?)",
                (emetteur_id, nb, now, now, self._confiance(nb)),
            )
        else:
            nb = row[0] + 1
            cur.execute(
                "UPDATE reputation_emetteurs "
                "SET nb_exagerations = ?, derniere_infraction = ?, score_confiance = ? "
                "WHERE emetteur_id = ?",
                (nb, now, self._confiance(nb), emetteur_id),
            )
        self.conn.commit()
        return nb

    def journaliser_sanction(self, emetteur_id, ticket, niveau, rapport, message):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO sanctions_log "
            "(date_log, emetteur_id, ticket, niveau_dissonance, details, sanction) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (now, emetteur_id, ticket, niveau,
             " ; ".join(rapport.get("details_dramatisation", [])), message),
        )
        self.conn.commit()

    @staticmethod
    def message_avertissement(nb_infractions: int, rapport: dict) -> str:
        """Avertissement GRADUÉ selon le nombre de récidives de l'émetteur."""
        details = ", ".join(rapport.get("details_dramatisation", [])[:3]) or "ton dramatisé"

        if nb_infractions <= 1:
            return (
                "⚠️ AVERTISSEMENT — Votre message emploie un registre d'urgence maximale "
                f"({details}) sans aucun élément factuel grave. La priorité est attribuée selon "
                "les FAITS, jamais selon le ton. Décrivez la situation objectivement."
            )
        if nb_infractions == 2:
            return (
                "⚠️⚠️ 2ᵉ AVERTISSEMENT — Nouvelle exagération détectée "
                f"({details}). Gonfler artificiellement l'urgence détourne les ressources des "
                "vraies urgences. Cette récidive est consignée à votre dossier."
            )
        return (
            f"🚫 ABUS RÉPÉTÉ ({nb_infractions}ᵉ infraction) — Tendance confirmée à dramatiser "
            f"sans fondement ({details}). Votre score de confiance est dégradé "
            f"({rapport.get('score_dramatisation', '?')} pts de dramatisation). Les signalements "
            "abusifs répétés exposent à un déclassement automatique de vos prochains tickets."
        )

    # --- Orchestrateur pratique : enregistre + journalise + renvoie le message ---
    def sanctionner(self, emetteur_id, ticket, niveau, rapport) -> str:
        nb = self.enregistrer_infraction(emetteur_id)
        message = self.message_avertissement(nb, rapport)
        self.journaliser_sanction(emetteur_id, ticket, niveau, rapport, message)
        return message


# ============================================================================
# 3. AUTOTEST RAPIDE (python nexus_sanction.py)
# ============================================================================
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # consoles Windows en cp1252
    except Exception:
        pass

    det = ExaggerationDetector()

    cas = [
        # (texte_brut, texte_propre_normalise, impact, urgence, corps)
        ("URGENCE ABSOLUE !!! Je veux etre traite en priorite IMMEDIATEMENT pour mon mot de passe",
         "urgence absolue je veux etre traite en priorite immediatement pour mon mot de passe", 1, 1, []),
        ("VENEZ VITE, IL Y A UNE FUSILLADE !!!",
         "venez vite il y a une fusillade", 4, 4, []),
        ("Bonjour, mon imprimante est en panne, pouvez-vous regarder svp",
         "bonjour mon imprimante est en panne pouvez-vous regarder svp", 1, 1, []),
        ("C'EST UNE CATASTROPHE ABSOLUE, GRAVISSIME !!!! je vais mourir si vous ne reparez pas mon ecran",
         "c'est une catastrophe absolue gravissime je vais mourir si vous ne reparez pas mon ecran", 1, 1, []),
    ]

    print("=" * 70)
    print("AUTOTEST — Détecteur d'exagération")
    print("=" * 70)
    for brut, propre, imp, urg, corps in cas:
        est, niv, rap = det.detecter(brut, propre, None, imp, urg, corps)
        verdict = "🚫 EXAGÉRATION" if est else "✅ OK"
        print(f"\n{verdict} (drama={rap['score_dramatisation']}, grave={rap['gravite_reelle']})")
        print(f"   Texte   : {brut[:65]}")
        if rap["details_dramatisation"]:
            print(f"   Signaux : {', '.join(rap['details_dramatisation'])}")
        if rap["raisons_gravite"]:
            print(f"   Gravité : {', '.join(rap['raisons_gravite'])}")
