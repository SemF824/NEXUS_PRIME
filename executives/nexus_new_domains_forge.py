# nexus_new_domains_forge.py
# Génère 100 000 tickets par domaine pour les nouveaux domaines
# Format : Sujets | Demande | Domaine | Niveau de priorité
import pandas as pd
import random
import csv
import os

TICKETS_PAR_DOMAINE = 100_000
DOSSIER_SORTIE = "../datasets/"

# ===========================================================
# UTILITAIRES COMMUNS
# ===========================================================
ADRESSES = [
    f"au {n} rue {r}, {v}"
    for n in range(1, 300)
    for r in ["Victor Hugo", "de la République", "Jean Jaurès", "Pasteur", "des Fleurs",
              "de la Gare", "du Port", "des Lilas", "du Château", "de Paris",
              "de Lyon", "de Marseille", "Gambetta", "Leclerc", "Foch", "Bellevue"]
    for v in ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Nantes",
              "Strasbourg", "Lille", "Rennes", "Montpellier", "Nice", "Grenoble"]
]
NUMEROS_TEL = [f"06 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}" for _ in range(1000)]
NOMS_APP = ["SAP", "Salesforce", "SharePoint", "Outlook", "Teams", "Intranet", "ERP", "CRM", "SIRH", "Jira", "Confluence"]
NOMS_MACHINES = [f"PC-{random.randint(1000,9999)}" for _ in range(500)] + [f"LAPTOP-{random.randint(100,999)}" for _ in range(300)]
DEPARTEMENTS = ["Comptabilité", "RH", "IT", "Marketing", "Logistique", "Ventes", "Direction", "Accueil", "Sécurité", "Support", "Juridique", "Finance", "Production"]


def _adresse():
    return random.choice(ADRESSES)

def _tel():
    return random.choice(NUMEROS_TEL)

def _app():
    return random.choice(NOMS_APP)

def _machine():
    return random.choice(NOMS_MACHINES)

def _dept():
    return random.choice(DEPARTEMENTS)


# ===========================================================
# 1. INFRA — Serveurs, Réseau, Datacenter, Sécurité IT
# ===========================================================
INFRA_INTENTS = {
    "Infra_Serveur_Crash": {
        "domaine": "Infra - Serveurs & Datacenter",
        "sujets": [
            "Crash de l'hyperviseur", "Serveur de prod HS", "BSOD sur serveur",
            "Serveur inaccessible", "Redémarrage intempestif", "Disque dur serveur mort",
            "Panne RAID critique", "Serveur muet au ping", "Surchauffe CPU serveur",
            "Alimentation serveur défaillante", "Mémoire RAM serveur corrompue", "Partition système pleine"
        ],
        "salutations": ["Bonjour l'équipe infra,", "Urgence datacenter,", "Alerte critique,", "Bonjour,", ""],
        "problemes": [
            "le serveur de production {machine} a planté brutalement et ne répond plus au ping. Tous les utilisateurs du service {dept} sont bloqués.",
            "notre hyperviseur principal est en erreur critique depuis {temps}. Les 12 VMs hébergées sont inaccessibles.",
            "le serveur de fichiers {machine} redémarre en boucle sans raison apparente, les logs montrent un BSOD code 0x0000007E.",
            "le disque RAID du serveur {machine} indique une panne sur 2 des 4 disques. Risque de perte de données imminent.",
            "la baie de stockage SAN ne répond plus, toutes les applications critiques du département {dept} sont en erreur.",
            "le serveur de base de données tombe toutes les 30 minutes, impossible de travailler correctement.",
            "la température CPU du serveur {machine} dépasse 90°C depuis ce matin, risque d'arrêt d'urgence.",
            "le service Active Directory est tombé, personne ne peut se connecter au domaine dans les bureaux."
        ],
        "contextes": [
            "C'est critique pour notre activité, merci d'intervenir en urgence.",
            "Le ticket de maintenance est {ticket_id}.",
            "Le contrat SLA exige une reprise sous 4 heures maximum.",
            "Les utilisateurs impactés sont au nombre de {nb_users}.",
            "J'ai déjà tenté un redémarrage manuel sans succès.",
            "Le dernier backup date d'hier soir, merci de le vérifier."
        ],
        "priorites": ["Haute", "Haute", "Haute", "Moyenne"]
    },
    "Infra_Reseau_Panne": {
        "domaine": "Infra - Réseau & Connectivité",
        "sujets": [
            "Réseau coupé bâtiment", "VPN instable", "WiFi hors service", "Perte de connectivité",
            "Bande passante saturée", "Switch de coeur en panne", "Lenteurs réseau critiques",
            "Firewall qui bloque tout", "DNS ne répond plus", "Routeur défaillant",
            "Coupure internet totale", "Accès NAS impossible"
        ],
        "salutations": ["Bonjour l'équipe réseau,", "Urgence réseau,", "Problème de connectivité,", "Bonjour,"],
        "problemes": [
            "l'ensemble du réseau du bâtiment principal est coupé depuis {temps}. Aucun poste n'accède à internet ni aux ressources internes.",
            "le VPN d'accès distant se déconnecte toutes les 10 minutes, rendant le télétravail impossible pour le département {dept}.",
            "le WiFi du plateau {dept} ne fonctionne plus du tout, environ {nb_users} personnes sont impactées.",
            "la bande passante internet est saturée à 100%, toutes les applications cloud sont inutilisables.",
            "le switch de cœur de réseau {machine} est tombé en panne, coupant 3 étages entiers du réseau.",
            "notre pare-feu bloque toutes les connexions sortantes depuis ce matin après la mise à jour de règles.",
            "le serveur DNS interne ne répond plus, causant des délais de connexion de 30+ secondes sur toutes les applications.",
            "le débit réseau est tombé à moins de 1 Mbps alors qu'on devrait avoir 1 Gbps, cela bloque tout le monde."
        ],
        "contextes": [
            "Merci d'intervenir rapidement, c'est bloquant pour toute la production.",
            "Le monitoring Nagios indique l'alerte depuis {temps}.",
            "Nous avons un pic d'activité prévu dans 2 heures.",
            "Les logs du firewall sont disponibles sur demande.",
            "Le fournisseur ISP a été contacté et dit que leur côté est OK."
        ],
        "priorites": ["Haute", "Haute", "Moyenne", "Basse"]
    },
    "Infra_Securite_IT": {
        "domaine": "Infra - Sécurité Informatique",
        "sujets": [
            "Suspicion ransomware", "Tentative d'intrusion détectée", "Alerte antivirus critique",
            "Phishing réussi signalé", "Fuite de données suspectée", "Cyberattaque en cours",
            "Compte admin compromis", "Exfiltration de données", "Malware détecté poste",
            "Alerte SIEM critique", "Connexion suspecte détectée", "Violation de politique sécurité"
        ],
        "salutations": ["URGENT - Sécurité,", "Alerte RSSI,", "Incident de sécurité,", "Bonjour,"],
        "problemes": [
            "plusieurs postes du département {dept} affichent un message de ransomware demandant une rançon. Les fichiers semblent chiffrés.",
            "notre SIEM a déclenché une alerte critique : tentative d'intrusion depuis une IP externe sur le port 22 du serveur {machine}.",
            "un collaborateur a cliqué sur un lien de phishing et a saisi ses identifiants. Son compte {machine} est potentiellement compromis.",
            "l'antivirus a détecté un malware de type trojan sur {nb_users} postes du parc informatique. La quarantaine a été lancée.",
            "des transferts de données inhabituels vers une IP externe inconnue ont été détectés depuis le serveur {machine} cette nuit.",
            "le compte administrateur principal a été utilisé depuis une adresse IP géolocalisée à l'étranger à 3h du matin.",
            "un salarié a connecté une clé USB non autorisée, déclenchant une alerte DLP. Des données confidentielles ont peut-être été copiées.",
            "nous avons détecté une scan réseau interne suspect provenant du poste {machine}, possible mouvement latéral."
        ],
        "contextes": [
            "J'ai immédiatement isolé les machines du réseau.",
            "Merci d'activer le plan de réponse aux incidents.",
            "Le RSSI a été informé et demande un rapport d'incident.",
            "Toutes les preuves numériques sont préservées.",
            "La direction est informée et attend votre intervention."
        ],
        "priorites": ["Haute", "Haute", "Haute", "Moyenne"]
    }
}

# ===========================================================
# 2. MATÉRIEL — Bureautique, Téléphonie, Périphériques
# ===========================================================
MATERIEL_INTENTS = {
    "Materiel_PC_Panne": {
        "domaine": "Matériel - PC & Ordinateurs",
        "sujets": [
            "PC ne démarre plus", "Écran noir au démarrage", "BSOD répété",
            "Ordinateur très lent", "Ventilateur bruyant", "Batterie laptop ne charge plus",
            "Clavier défaillant", "Souris ne répond plus", "PC surchauffe et s'éteint",
            "Port USB HS", "Carte graphique en panne", "Disque dur clique"
        ],
        "salutations": ["Bonjour le support,", "Bonjour,", "Besoin d'aide,", ""],
        "problemes": [
            "mon ordinateur {machine} ne démarre plus du tout ce matin. L'écran reste noir malgré le bouton power.",
            "j'ai des écrans bleus BSOD répétés toutes les heures sur mon poste {machine}, code d'erreur : KERNEL_DATA_INPAGE_ERROR.",
            "mon PC est devenu extrêmement lent depuis la mise à jour Windows d'hier. Il met 15 minutes à démarrer.",
            "le ventilateur de mon laptop fait un bruit terrible et la machine s'éteint au bout de 20 minutes.",
            "la batterie de mon ordinateur portable ne se charge plus du tout. Je dois rester branché en permanence.",
            "la moitié des touches de mon clavier ne répondent plus, notamment les chiffres et certaines lettres.",
            "mon PC s'éteint brutalement en plein travail, apparemment par surchauffe. La pièce est pourtant bien ventilée.",
            "le disque dur de mon poste {machine} fait des bruits de cliquetis inquiétants. Je crains une perte de données."
        ],
        "contextes": [
            "Mon nom d'utilisateur est {acc_num} et je suis au département {dept}.",
            "Le numéro de série du matériel est {machine}.",
            "J'ai des données importantes non sauvegardées, merci d'intervenir rapidement.",
            "Je peux déposer le matériel au helpdesk si nécessaire.",
            "Ce poste est utilisé pour des applications critiques métier."
        ],
        "priorites": ["Haute", "Moyenne", "Basse", "Basse"]
    },
    "Materiel_Impression": {
        "domaine": "Matériel - Impression & Bureautique",
        "sujets": [
            "Imprimante hors service", "Bourrage papier copieur", "Imprimante ne reçoit pas les travaux",
            "Cartouche encre vide", "Scanner défaillant", "Photocopieuse en erreur",
            "Qualité impression dégradée", "Imprimante réseau introuvable", "Télécopieur en panne",
            "Imprimante fait des traînées", "Plus de papier", "Imprimante offline"
        ],
        "salutations": ["Bonjour,", "Besoin d'une intervention,", ""],
        "problemes": [
            "l'imprimante multifonction du département {dept} est totalement hors service depuis ce matin.",
            "le copieur de l'étage indique un bourrage papier mais je n'arrive pas à localiser le blocage.",
            "les travaux d'impression n'arrivent plus à l'imprimante réseau depuis la mise à jour du driver.",
            "la cartouche toner de l'imprimante principale est vide, impossible d'imprimer. Besoin d'un remplacement urgent.",
            "le scanner du service {dept} ne transfère plus les documents scannés vers le serveur.",
            "la qualité d'impression est déplorable : les pages sont striées et illisibles.",
            "l'imprimante n'apparaît plus dans la liste des imprimantes disponibles depuis ce matin.",
            "la photocopieuse affiche une erreur C-3200 et refuse de fonctionner."
        ],
        "contextes": [
            "L'imprimante se trouve au {dept}, numéro d'inventaire {machine}.",
            "Nous devons imprimer des documents urgents pour une réunion cet après-midi.",
            "Il n'y a plus de consommables en stock pour cette imprimante.",
            "La dernière maintenance date de {temps}."
        ],
        "priorites": ["Moyenne", "Haute", "Basse", "Basse"]
    },
    "Materiel_Telephonie": {
        "domaine": "Matériel - Téléphonie & Mobilité",
        "sujets": [
            "Téléphone fixe sans tonalité", "Smartphone professionnel cassé", "Oreillette défaillante",
            "Messagerie vocale inaccessible", "Téléphone ne reçoit pas les appels", "Batterie téléphone gonflée",
            "Écran téléphone fissuré", "MDM bloqué sur mobile", "SIM pro non reconnue",
            "Conférence téléphonique impossible", "Renvoi d'appel bloqué", "Qualité audio très mauvaise"
        ],
        "salutations": ["Bonjour,", "Bonjour le support téléphonie,", ""],
        "problemes": [
            "mon téléphone fixe de bureau n'a plus de tonalité depuis ce matin, je ne peux ni recevoir ni passer d'appels.",
            "mon smartphone professionnel est tombé et l'écran est fissuré. Il ne répond plus aux touches.",
            "la messagerie vocale de mon poste téléphonique est pleine et je ne peux pas la vider.",
            "mon téléphone professionnel ne reçoit plus les appels entrants, ils vont directement en messagerie.",
            "la batterie de mon smartphone pro a gonflé et le téléphone est inutilisable, c'est dangereux.",
            "le MDM a bloqué mon téléphone après une tentative de mise à jour, je n'ai plus accès à mes applications.",
            "ma carte SIM professionnelle n'est plus reconnue par le téléphone depuis ce week-end.",
            "la qualité audio lors des conférences téléphoniques est catastrophique depuis la migration Teams."
        ],
        "contextes": [
            "Mon poste téléphonique est le {acc_num}.",
            "Je travaille au département {dept} et j'attends des appels importants.",
            "Pouvez-vous me fournir un téléphone de remplacement en attendant la réparation ?",
            "Le numéro de serie du mobile est {machine}."
        ],
        "priorites": ["Moyenne", "Haute", "Basse", "Basse"]
    }
}

# ===========================================================
# 3. ACCÈS — Authentification, Comptes, VPN, Droits
# ===========================================================
ACCES_INTENTS = {
    "Acces_MDP_Compte": {
        "domaine": "Accès - Authentification & Mots de passe",
        "sujets": [
            "Mot de passe oublié", "Compte verrouillé", "Réinitialisation MDP urgente",
            "Échec authentification multifacteur", "Code MFA non reçu", "Compte expiré",
            "Impossible de changer le mot de passe", "Session expirée en boucle",
            "Authentification SSO défaillante", "Windows Hello ne reconnaît plus",
            "Certificat client expiré", "Compte désactivé par erreur"
        ],
        "salutations": ["Hello le helpdesk,", "Bonjour,", "Urgence connexion,", ""],
        "problemes": [
            "je ne me souviens plus de mon mot de passe de session Windows. Mon identifiant est {acc_num}.",
            "mon compte est verrouillé après trop de tentatives de connexion. Je dois accéder à {app_name} de toute urgence.",
            "je ne reçois plus le SMS avec le code à 6 chiffres pour la double authentification sur {app_name}.",
            "mon compte a expiré après mes congés et je ne peux plus me connecter à aucune application.",
            "je n'arrive pas à changer mon mot de passe : le système dit qu'il ne respecte pas la politique mais ne précise pas pourquoi.",
            "ma session se ferme toutes les 5 minutes et me demande de me reconnecter, c'est insupportable.",
            "l'authentification SSO de {app_name} ne fonctionne plus depuis la migration vers le nouveau portail.",
            "Windows Hello (reconnaissance faciale) ne me reconnaît plus depuis que j'ai changé de bureau."
        ],
        "contextes": [
            "Mon nom d'utilisateur est {acc_num}.",
            "Je reviens de congés et j'ai besoin d'accès urgent pour une réunion dans 1 heure.",
            "J'ai essayé la procédure de réinitialisation en libre-service sans succès.",
            "Mon responsable {dept} peut confirmer mon identité si nécessaire.",
            "Mon numéro de téléphone de secours est le {tel_num}."
        ],
        "priorites": ["Haute", "Moyenne", "Basse", "Basse"]
    },
    "Acces_Droits_Applications": {
        "domaine": "Accès - Droits & Applications",
        "sujets": [
            "Accès refusé à une application", "Demande de droits nouveaux", "Perte de droits après migration",
            "Accès dossier réseau refusé", "Permissions SharePoint manquantes", "Licence logicielle expirée",
            "Profil utilisateur corrompu", "Accès VPN non autorisé", "Droits impression retirés",
            "Boîte mail partagée inaccessible", "Délégation Outlook supprimée", "Accès BI bloqué"
        ],
        "salutations": ["Bonjour,", "Bonjour le support,", ""],
        "problemes": [
            "j'ai besoin d'accéder à {app_name} pour ma nouvelle mission mais le système m'affiche 'Accès refusé'.",
            "depuis la migration des serveurs, je n'ai plus accès au dossier partagé \\\\serveur\\{dept}.",
            "mes permissions sur SharePoint ont disparu après la mise à jour de vendredi dernier.",
            "ma licence {app_name} a expiré et je ne peux plus ouvrir l'application. J'en ai besoin pour livrer un projet.",
            "mon profil Windows est corrompu : je perds mes paramètres et mes raccourcis à chaque redémarrage.",
            "je n'arrive plus à me connecter au VPN depuis chez moi. L'erreur indique 'utilisateur non autorisé'.",
            "mes droits d'impression ont été retirés sans raison, je ne peux plus rien imprimer.",
            "je n'arrive plus à accéder à la boîte mail partagée {dept} depuis la migration Exchange."
        ],
        "contextes": [
            "Mon manager {dept} a approuvé cette demande d'accès.",
            "La demande de droits référence le ticket {ticket_id}.",
            "J'ai besoin de cet accès pour un projet urgent livrable cette semaine.",
            "Mon identifiant est {acc_num}, je suis au département {dept}."
        ],
        "priorites": ["Haute", "Moyenne", "Basse", "Basse"]
    },
    "Acces_Gestion_Comptes": {
        "domaine": "Gestion des Comptes & Droits",
        "sujets": [
            "Création compte nouvel arrivant", "Suppression compte départ salarié", "Changement de nom utilisateur",
            "Transfert de droits entre collègues", "Audit droits utilisateurs", "Compte de service à créer",
            "Réactivation compte inactif", "Modification groupe AD", "Attribution licence Microsoft 365",
            "Création boîte mail fonctionnelle", "Onboarding nouveau collaborateur", "Révision des droits d'accès"
        ],
        "salutations": ["Bonjour l'équipe IT,", "Bonjour,", "Demande RH validée,", ""],
        "problemes": [
            "nous avons un nouveau collaborateur qui arrive lundi dans le département {dept}. Merci de créer son compte et ses accès.",
            "un salarié du service {dept} quitte l'entreprise vendredi. Merci de désactiver son compte et d'archiver sa boîte mail.",
            "suite à son mariage, la collaboratrice {acc_num} souhaite changer son nom d'utilisateur dans l'AD.",
            "nous avons besoin d'un compte de service pour l'application {app_name} avec des droits en lecture sur la base de données.",
            "le compte de {acc_num} est inactif depuis 6 mois. Le manager {dept} demande sa réactivation.",
            "merci d'ajouter {acc_num} au groupe AD 'Finance-Reporting' pour lui donner accès aux tableaux de bord.",
            "nous avons besoin d'une licence Microsoft 365 E3 pour la nouvelle collaboratrice du département {dept}.",
            "créer une boîte mail fonctionnelle contact.{dept}@entreprise.fr avec partage vers 3 personnes."
        ],
        "contextes": [
            "La demande a été approuvée par le responsable {dept}.",
            "Le formulaire RH est joint à ce ticket.",
            "Date d'effet souhaitée : lundi prochain.",
            "Merci de confirmer la création par retour de mail."
        ],
        "priorites": ["Haute", "Moyenne", "Basse", "Basse"]
    }
}

# ===========================================================
# 4. POMPIER — Incendie, Secours, Accident, Fuite gaz
# ===========================================================
POMPIER_INTENTS = {
    "Pompier_Incendie": {
        "domaine": "Pompier - Incendie",
        "sujets": [
            "Incendie d'appartement", "Feu de cuisine", "Incendie de voiture", "Départ de feu sous-sol",
            "Incendie entrepôt", "Feu de forêt proche habitation", "Fumée importante bâtiment",
            "Incendie de poubelles", "Feu de cabanon", "Incendie école", "Embrasement toiture",
            "Feu de terrasse", "Incendie camping-car", "Feu dans une cave"
        ],
        "salutations": ["Allô les pompiers,", "Vite, au secours,", "Urgence, ", "Bonjour,", ""],
        "problemes": [
            "il y a un incendie dans l'appartement au 3ème étage {adresse}. Les flammes sortent par la fenêtre et ça se propage.",
            "la cuisine de mon appartement {adresse} a pris feu, je n'arrive pas à éteindre avec l'extincteur.",
            "une voiture est en feu sur le parking {adresse}, les flammes risquent de se propager aux voitures voisines.",
            "il y a de la fumée épaisse qui sort du sous-sol de l'immeuble {adresse}, ça sent le plastique brûlé.",
            "un entrepôt brûle {adresse}, les flammes sont très hautes et il y a peut-être des bonbonnes de gaz à l'intérieur.",
            "un feu de broussailles s'approche dangereusement des habitations {adresse}, le vent souffle fort.",
            "je vois de la fumée noire sortir du toit de l'immeuble {adresse}, les voisins n'ont pas l'air au courant.",
            "des poubelles devant l'immeuble {adresse} sont en feu, les flammes touchent le mur de l'entrée."
        ],
        "contextes": [
            "Des personnes sont peut-être encore à l'intérieur.",
            "J'ai prévenu mes voisins et tout le monde est sorti.",
            "Il y a des personnes à mobilité réduite à l'étage.",
            "Les enfants de l'école jouent dans la cour juste à côté.",
            "Mon numéro est le {tel_num}, je reste à l'extérieur.",
            "Je suis {adresse}, venez vite s'il vous plaît."
        ],
        "priorites": ["Haute", "Haute", "Haute", "Haute"]
    },
    "Pompier_Fuite_Gaz": {
        "domaine": "Pompier - Fuite & Risque Chimique",
        "sujets": [
            "Forte odeur de gaz", "Fuite de gaz signalée", "Odeur chimique suspecte",
            "Fuite bonbonne propane", "Camion citerne accident", "Nuage de fumée toxique",
            "Explosion imminente gaz", "Gaz carbonique cave", "Chlore piscine accidentel",
            "Fuite ammoniac entrepôt", "Produit chimique renversé", "CO détecteur déclenché"
        ],
        "salutations": ["Allô les pompiers,", "Urgence,", "Vite, ", ""],
        "problemes": [
            "il y a une très forte odeur de gaz dans tout mon immeuble {adresse}. J'ai coupé le gaz mais ça sent encore très fort.",
            "une bonbonne de gaz propane fuit dans le garage {adresse}. J'entends un sifflement et ça sent fort.",
            "un camion citerne a eu un accident {adresse} et un liquide inconnu se répand sur la chaussée, ça fume.",
            "le détecteur de monoxyde de carbone de mon appartement sonne depuis 10 minutes {adresse}.",
            "il y a une odeur chimique très forte et des yeux qui piquent dans tout le bâtiment {adresse}.",
            "de la fumée jaunâtre sort d'un conduit de l'entrepôt {adresse}, les employés ont été évacués.",
            "j'ai renversé accidentellement un produit chimique dans le labo {adresse}, vapeurs irritantes, quelqu'un tousse.",
            "la salle de chloration de la piscine {adresse} a une fuite, les nageurs ont été évacués en urgence."
        ],
        "contextes": [
            "J'ai évacué tout le monde du bâtiment.",
            "J'ai coupé l'alimentation électrique pour éviter une étincelle.",
            "Il ne faut surtout pas sonner, ça pourrait provoquer une explosion.",
            "Mon numéro est le {tel_num}.",
            "Nous attendons dehors {adresse}."
        ],
        "priorites": ["Haute", "Haute", "Haute", "Moyenne"]
    },
    "Pompier_Secours_Personne": {
        "domaine": "Pompier - Secours & Accidents",
        "sujets": [
            "Accident de voiture avec blessés", "Personne coincée dans un ascenseur", "Chute de hauteur",
            "Noyade en cours", "Personne coincée sous décombres", "Accident de travail grave",
            "Crue soudaine personnes isolées", "Effondrement partiel structure", "Personne tombée dans un puits",
            "Avalanche avec ensevelis", "Accident de moto grave", "Randonneur blessé inaccessible"
        ],
        "salutations": ["Allô les pompiers,", "Urgence secours,", "Vite, ", "Au secours, ", ""],
        "problemes": [
            "grave accident de voiture {adresse}. Deux véhicules sont impliqués, il y a au moins 2 blessés coincés dans les débris.",
            "une personne est coincée depuis 30 minutes dans l'ascenseur de l'immeuble {adresse}. Elle commence à paniquer.",
            "un ouvrier est tombé d'un échafaudage de 5 mètres {adresse}. Il est conscient mais ne peut plus bouger ses jambes.",
            "quelqu'un est en train de se noyer dans la rivière {adresse}. Je n'arrive pas à l'atteindre depuis la berge.",
            "un pan de mur s'est effondré {adresse}, il y aurait une personne coincée sous les décombres.",
            "un chantier a eu un accident grave {adresse}, un ouvrier est blessé et coincé sous une poutre.",
            "des inondations ont coupé l'accès, 3 personnes sont isolées sur un toit {adresse}, l'eau monte encore.",
            "un randonneur a glissé et est blessé dans une zone escarpée. Il a réussi à nous appeler au {tel_num}."
        ],
        "contextes": [
            "J'ai appelé le 15 aussi pour le SAMU, ils arrivent.",
            "La victime est consciente et me parle.",
            "Il n'y a pas d'autre accès possible par la route.",
            "Le nombre de blessés n'est pas encore connu.",
            "Je suis sur place et j'attends, mon numéro est le {tel_num}."
        ],
        "priorites": ["Haute", "Haute", "Haute", "Moyenne"]
    },
    "Pompier_Operations_Diverses": {
        "domaine": "Pompier - Opérations Diverses",
        "sujets": [
            "Nid de frelons dangereux", "Animal dangereux signalé", "Inondation cave",
            "Arbre tombé sur route", "Toiture endommagée tempête", "Portail bloqué véhicule coincé",
            "Objet bloqué dans une gorge", "Assistance personne isolée", "Tempête dégâts imminents",
            "Ligne électrique tombée", "Désincarcération non urgente", "Déversement carburant route"
        ],
        "salutations": ["Bonjour les pompiers,", "Bonjour,", ""],
        "problemes": [
            "il y a un énorme nid de frelons asiatiques dans la cour {adresse}. Les enfants ne peuvent plus sortir.",
            "ma cave est inondée suite aux pluies de cette nuit {adresse}. L'eau monte encore, j'ai le compteur électrique là-dedans.",
            "un arbre vient de tomber sur la route {adresse} suite aux vents. Il bloque complètement la circulation.",
            "la tempête a arraché des tuiles de mon toit {adresse}. La charpente est exposée, il pleut à l'intérieur.",
            "une ligne électrique est tombée sur la chaussée {adresse} suite au vent. Des fils pendent très bas.",
            "du carburant s'est répandu sur une grande surface de la route {adresse} suite à un accident de camion.",
            "mon voisin âgé de 85 ans ne répond plus depuis 2 jours {adresse}. Je crains pour sa santé.",
            "un chat est coincé en haut d'un arbre depuis hier {adresse} et ne peut plus descendre."
        ],
        "contextes": [
            "Merci de venir dès que possible.",
            "La zone est sécurisée, personne n'approche.",
            "Quand pouvez-vous intervenir ?",
            "Mon numéro est le {tel_num}."
        ],
        "priorites": ["Moyenne", "Basse", "Basse", "Basse"]
    }
}

# ===========================================================
# 5. POLICE NATIONALE — Sécurité, Infractions, Urgences
# ===========================================================
POLICE_INTENTS = {
    "Police_Urgence_Violence": {
        "domaine": "Police - Violence & Urgence",
        "sujets": [
            "Agression physique en cours", "Violences conjugales", "Braquage signalé",
            "Menaces de mort proférées", "Bagarre avec arme blanche", "Tirs entendus",
            "Prise d'otage", "Tentative de meurtre", "Personne en danger immédiat",
            "Séquestration signalée", "Règlement de comptes", "Violence à enfant"
        ],
        "salutations": ["Police secours,", "Au secours,", "Urgence,", "Je panique,", "Venez vite,"],
        "problemes": [
            "une femme se fait frapper par son conjoint {adresse}. On entend des cris depuis 10 minutes.",
            "un braquage est en cours dans la boutique {adresse}. Les voleurs ont des armes et retiennent le gérant.",
            "quelqu'un vient de me menacer de mort avec un couteau {adresse}. Il est encore sur place.",
            "des tirs ont été entendus {adresse}. Au moins 2 coups de feu, les gens fuient dans tous les sens.",
            "une bagarre a dégénéré {adresse}. Un homme a sorti un couteau et quelqu'un est blessé.",
            "mon ex-conjoint m'a séquestrée {adresse}. Je me suis enfermée dans la salle de bain et j'appelle discrètement.",
            "j'entends mon voisin battre ses enfants {adresse}. Des cris d'enfants depuis 20 minutes.",
            "un homme armé menace les clients d'un restaurant {adresse}."
        ],
        "contextes": [
            "Je suis caché, venez discrètement.",
            "L'agresseur est encore sur place.",
            "Il y a des blessés qui ont besoin du SAMU aussi.",
            "Mon numéro est le {tel_num}, je reste en ligne.",
            "J'ai filmé la scène, je vous transmets les images."
        ],
        "priorites": ["Haute", "Haute", "Haute", "Haute"]
    },
    "Police_Cambriolage_Vol": {
        "domaine": "Police - Cambriolage & Vol",
        "sujets": [
            "Cambriolage en cours", "Vol à la tire signalé", "Effraction de véhicule",
            "Vol de voiture", "Cambriolage découvert", "Pickpocket dans les transports",
            "Vol avec violence", "Sac à main arraché", "Escroquerie signalée",
            "Vol en réunion", "Fraude bancaire signalée", "Vol de colis"
        ],
        "salutations": ["Bonjour la police,", "Allô,", "Je veux signaler,", ""],
        "problemes": [
            "je suis en train d'entendre du bruit dans mon appartement du dessous {adresse}. Je pense que c'est un cambriolage.",
            "on vient de m'arracher mon sac à main {adresse}. L'auteur est parti en courant direction la rue Victor Hugo.",
            "ma voiture a été fracturée cette nuit {adresse}. La vitre avant est cassée et mon GPS a été volé.",
            "ma voiture a été volée cette nuit. Elle était garée {adresse}. C'est une Renault Clio noire, plaque {acc_num}.",
            "je viens de rentrer chez moi et je constate que j'ai été cambriolé {adresse}. La porte a été forcée.",
            "on m'a volé mon téléphone dans le métro. L'auteur est sorti à la station suivante.",
            "j'ai été victime d'une escroquerie en ligne. J'ai virée {nb_users}€ à une personne qui se faisait passer pour mon banquier.",
            "quelqu'un a volé des colis devant ma porte d'entrée {adresse}. J'ai les images de la caméra."
        ],
        "contextes": [
            "Je peux fournir un signalement précis de l'auteur.",
            "J'ai les images de vidéosurveillance.",
            "Je veux déposer une plainte.",
            "Mon numéro est le {tel_num}.",
            "Les auteurs sont peut-être encore dans le secteur."
        ],
        "priorites": ["Haute", "Moyenne", "Basse", "Basse"]
    },
    "Police_Securite_Routiere": {
        "domaine": "Sécurité Routière & Circulation",
        "sujets": [
            "Chauffard signalé", "Rodéo urbain", "Conducteur ivre sur route",
            "Accident de la route", "Refus d'obtempérer", "Véhicule abandonné suspect",
            "Course poursuite illégale", "Deux-roues dangereux", "Obstacle sur autoroute",
            "Conducteur endormi au volant", "Excès de vitesse dangereux", "Stationnement gênant pompiers"
        ],
        "salutations": ["Bonjour,", "Je veux signaler,", "Allô,", ""],
        "problemes": [
            "des motos font des rodéos urbains {adresse} à toute vitesse en grillant les feux rouges depuis une heure.",
            "je suis derrière un conducteur qui roule très dangereusement sur l'A{nb_users}. Il fait des zigzags et semble ivre.",
            "un accident vient de se produire {adresse}, deux voitures impliquées. Il semble y avoir des blessés.",
            "un conducteur refuse d'obtempérer au contrôle de police et prend la fuite direction {adresse}.",
            "un véhicule est abandonné depuis 3 jours {adresse}, il bloque le passage des pompiers.",
            "un conducteur semble s'être endormi au volant, son véhicule dérive lentement sur la file de gauche de l'autoroute.",
            "une voiture fait des courses illégales avec une autre {adresse}. Ils roulent à plus de 100 km/h en ville.",
            "un cyclomoteur sans plaque fait des tonneaux devant les piétons {adresse}."
        ],
        "contextes": [
            "J'ai pris des photos des plaques d'immatriculation.",
            "Le conducteur fonce vers le centre-ville.",
            "Des piétons ont failli être renversés.",
            "Je suis en sécurité et je vous appelle depuis un arrêt.",
            "Mon numéro est le {tel_num}."
        ],
        "priorites": ["Haute", "Moyenne", "Basse", "Basse"]
    },
    "Police_Troubles_Ordre_Public": {
        "domaine": "Police - Ordre Public & Incivilités",
        "sujets": [
            "Tapage nocturne", "Groupe menaçant", "Dégradation de bien public",
            "Personne suspecte qui rôde", "Trafic de stupéfiants visible", "Incivilité grave",
            "Occupation illégale d'espace", "Attroupement menaçant", "Graffitis en cours",
            "Bruit de voisinage persistant", "Mendicité agressive", "Comportement bizarre danger"
        ],
        "salutations": ["Bonjour,", "Je souhaite signaler,", ""],
        "problemes": [
            "mes voisins font une soirée extrêmement bruyante depuis minuit {adresse}. J'ai frappé à leur porte sans succès.",
            "un groupe de jeunes stationne depuis plusieurs heures devant mon immeuble {adresse} et intimide les résidents.",
            "des individus sont en train de taguer les murs de l'école {adresse}. Je les observe depuis ma fenêtre.",
            "une personne tourne autour des voitures garées dans ma rue {adresse} depuis une heure, ça semble suspect.",
            "il y a un deal de drogue ouvert dans le hall de mon immeuble {adresse} depuis plusieurs semaines.",
            "un sans-abri agressif demande de l'argent aux clients devant la pharmacie {adresse} et les bouscule.",
            "un squat s'est installé dans le bâtiment vacant {adresse}. On entend du bruit la nuit et ça craint.",
            "une bagarre entre voisins s'est produite dans la cour {adresse}, des insultes et des bousculades."
        ],
        "contextes": [
            "Je ne souhaite pas porter plainte mais juste signaler.",
            "La situation dure depuis plusieurs semaines.",
            "Quand vous aurez le temps, ce n'est pas urgent.",
            "Je suis disponible au {tel_num} si vous avez besoin d'informations."
        ],
        "priorites": ["Moyenne", "Basse", "Basse", "Basse"]
    }
}

# ===========================================================
# MOTEUR DE GÉNÉRATION GÉNÉRIQUE
# ===========================================================
def _remplir(texte: str) -> str:
    return (texte
            .replace("{adresse}", _adresse())
            .replace("{tel_num}", _tel())
            .replace("{app_name}", _app())
            .replace("{machine}", _machine())
            .replace("{dept}", _dept())
            .replace("{acc_num}", f"USR{random.randint(10000, 99999)}")
            .replace("{ticket_id}", f"TKT-{random.randint(100000, 999999)}")
            .replace("{nb_users}", str(random.randint(2, 500)))
            .replace("{temps}", random.choice(["ce matin", "hier soir", "il y a 2 heures", "depuis 30 minutes", "depuis midi"]))
            )


def generer_tickets_pour_domaine(intents_dict: dict, nb_tickets: int) -> pd.DataFrame:
    lignes = []
    cles = list(intents_dict.keys())
    i = 0
    while len(lignes) < nb_tickets:
        intent_key = cles[i % len(cles)]
        intent = intents_dict[intent_key]
        sujet = random.choice(intent["sujets"])
        salutation = random.choice(intent["salutations"])
        probleme = _remplir(random.choice(intent["problemes"]))
        contexte = _remplir(random.choice(intent["contextes"]))
        demande = f"{salutation} {probleme} {contexte}".strip()
        priorite = random.choice(intent["priorites"])
        lignes.append({
            "Sujets": sujet,
            "Demande": demande,
            "Domaine": intent["domaine"],
            "Niveau de priorité": priorite
        })
        i += 1
    return pd.DataFrame(lignes[:nb_tickets])


# ===========================================================
# LANCEMENT PRINCIPAL
# ===========================================================
def run():
    os.makedirs(DOSSIER_SORTIE, exist_ok=True)

    taches = [
        ("INFRA", INFRA_INTENTS, "dataset_tickets_Infra_100k.csv"),
        ("MATÉRIEL", MATERIEL_INTENTS, "dataset_tickets_Materiel_100k.csv"),
        ("ACCÈS", ACCES_INTENTS, "dataset_tickets_Acces_100k.csv"),
        ("POMPIER", POMPIER_INTENTS, "dataset_tickets_Pompiers_100k.csv"),
        ("POLICE", POLICE_INTENTS, "dataset_tickets_Police_100k.csv"),
    ]

    for nom, intents_dict, fichier in taches:
        print(f"  -> Génération {TICKETS_PAR_DOMAINE:,} tickets [{nom}]...")
        df = generer_tickets_pour_domaine(intents_dict, TICKETS_PAR_DOMAINE)
        chemin = os.path.join(DOSSIER_SORTIE, fichier)
        df.to_csv(chemin, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")
        print(f"     [OK] {len(df):,} tickets -> {chemin}")

    print("\n[OK] Generation terminee : 5 domaines x 100 000 tickets.")


if __name__ == "__main__":
    print(f"[START] FORGE NOUVEAUX DOMAINES - Objectif : {TICKETS_PAR_DOMAINE:,} tickets par domaine")
    run()
