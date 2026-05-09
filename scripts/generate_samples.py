#!/usr/bin/env python3
"""Generate 90 additional synthetic French medical samples (11-100)."""

import random
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

random.seed(42)

# --- Data pools ---

FIRST_NAMES_M = [
    "Jean", "Pierre", "Michel", "André", "Philippe", "Jacques", "Bernard",
    "Alain", "François", "René", "Louis", "Henri", "Claude", "Yves", "Daniel",
    "Patrick", "Thierry", "Marc", "Éric", "Christophe", "Laurent", "Stéphane",
    "Nicolas", "Frédéric", "Olivier", "Sébastien", "David", "Julien", "Antoine",
    "Maxime", "Hugo", "Théo", "Lucas", "Léo", "Nathan", "Karim", "Mourad",
    "Samir", "Mohamed", "Youssef", "Ibrahim", "Mamadou", "Oumar",
]

FIRST_NAMES_F = [
    "Marie", "Françoise", "Monique", "Catherine", "Nathalie", "Isabelle",
    "Sylvie", "Anne", "Martine", "Christine", "Sophie", "Véronique", "Brigitte",
    "Hélène", "Sandrine", "Valérie", "Céline", "Émilie", "Julie", "Camille",
    "Léa", "Manon", "Chloé", "Emma", "Jade", "Louise", "Fatima", "Aïcha",
    "Amina", "Khadija", "Aminata", "Mariam",
]

LAST_NAMES = [
    "MARTIN", "BERNARD", "THOMAS", "PETIT", "ROBERT", "RICHARD", "DURAND",
    "DUBOIS", "MOREAU", "LAURENT", "SIMON", "MICHEL", "LEFEBVRE", "LEROY",
    "ROUX", "DAVID", "BERTRAND", "MOREL", "FOURNIER", "GIRARD", "BONNET",
    "DUPONT", "LAMBERT", "FONTAINE", "ROUSSEAU", "VINCENT", "MULLER", "LEFEVRE",
    "FAURE", "ANDRE", "MERCIER", "BLANC", "GUERIN", "BOYER", "GARNIER",
    "CHEVALIER", "FRANÇOIS", "LEGRAND", "GAUTHIER", "GARCIA", "PERRIN",
    "ROBIN", "CLEMENT", "MORIN", "NICOLAS", "HENRY", "ROUSSEL", "MATHIEU",
    "GAUTIER", "MASSON", "MARCHAND", "DUVAL", "DENIS", "DUMONT", "MARIE",
    "LEMAIRE", "NOEL", "MEYER", "DUFOUR", "MEUNIER", "BRUN", "BLANCHARD",
    "GIRAUD", "JOLY", "RIVIERE", "LUCAS", "BRUNET", "GAILLARD", "BARBIER",
    "ARNAUD", "MARTINEZ", "NGUYEN", "CHEN", "TRAORE", "DIALLO", "COULIBALY",
    "DIOP", "NDIAYE", "BA", "KAMARA", "KONÉ",
]

DR_FIRST_NAMES = [
    "Sophie", "Pierre", "Jean-Marc", "Nadia", "Philippe", "Catherine",
    "François", "Isabelle", "Éric", "Marie", "Laurent", "Sandrine",
    "Christophe", "Anne", "Olivier", "Valérie", "Nicolas", "Hélène",
    "Stéphane", "Caroline", "Antoine", "Delphine", "Julien", "Pascale",
    "David", "Béatrice", "Thierry", "Sylvie", "Marc", "Émilie",
]

DR_LAST_NAMES = [
    "BERGER", "MOREL", "LEFÈVRE", "HAMMADI", "MOREAU", "DUPONT", "SIMON",
    "LAURENT", "RICHARD", "FONTAINE", "BLANC", "MERCIER", "BOYER", "PERRIN",
    "FAURE", "GIRARD", "LAMBERT", "ROUSSEAU", "VINCENT", "GAUTHIER",
    "DELACROIX", "CHEVALIER", "DUMAS", "RENARD", "PICARD", "BARBIER",
    "LECLERC", "MARECHAL", "BENOIT", "COLLET",
]

SPECIALTIES = [
    "Médecine générale", "Cardiologie", "Pneumologie", "Neurologie",
    "Gastro-entérologie", "Orthopédie", "Rhumatologie", "Urologie",
    "Gynécologie", "ORL", "Dermatologie", "Endocrinologie",
    "Chirurgie digestive", "Chirurgie orthopédique", "Chirurgie vasculaire",
    "Oncologie", "Hématologie", "Néphrologie", "Médecine interne",
    "Pédiatrie", "Gériatrie", "Médecine du sport",
]

HOSPITALS = [
    "CHU Lyon", "Hôpital de la Croix-Rousse", "Clinique Saint-Joseph",
    "Hôpital Édouard Herriot", "CHU Saint-Étienne", "Clinique du Parc",
    "Clinique Mutualiste", "Hôpital Femme Mère Enfant", "CHU Grenoble",
    "Clinique du Tonkin", "Centre Hospitalier de Villefranche",
    "Hôpital Lyon Sud", "Clinique de la Sauvegarde", "CH Bourg-en-Bresse",
    "Clinique du Val d'Ouest", "Hôpital Nord-Ouest",
]

SERVICES = [
    "Service de médecine", "Service de chirurgie", "Service des urgences",
    "Consultation externe", "Hôpital de jour", "Service de réanimation",
    None, None, None,
]

EMAIL_DOMAINS = [
    "orange.fr", "free.fr", "gmail.com", "outlook.fr", "wanadoo.fr",
    "sfr.fr", "laposte.net", "hotmail.fr", "yahoo.fr",
]

HOSP_EMAIL_DOMAINS = [
    "chu-lyon.fr", "hopital-croix-rousse.fr", "clinique-sj.fr",
    "ch-villefranche.fr", "chu-grenoble.fr", "chu-st-etienne.fr",
    "clinique-mutualiste.fr", "hopital-edouard-herriot.fr",
]

# Exam scenarios
EXAM_SCENARIOS = [
    # (modality, region_fr, injection, indication_fr, urgency, attachments_needed)
    ("scanner", "thoracique", True, "Bilan de nodule pulmonaire", "routine", ["ordonnance", "créatinine"]),
    ("scanner", "abdomino-pelvien", True, "Douleurs abdominales chroniques, amaigrissement", "routine", ["ordonnance", "créatinine"]),
    ("scanner", "cérébral", False, "Céphalées inhabituelles", "urgent", ["ordonnance"]),
    ("scanner", "thoraco-abdomino-pelvien", True, "Bilan d'extension néoplasique", "prioritaire", ["ordonnance", "créatinine"]),
    ("scanner", "rachis lombaire", False, "Lombalgies chroniques résistantes au traitement", "routine", ["ordonnance"]),
    ("scanner", "des sinus", False, "Sinusite chronique résistante", "routine", ["ordonnance"]),
    ("scanner", "coronaire (coroscanner)", True, "Douleur thoracique atypique", "prioritaire", ["ordonnance", "créatinine"]),
    ("scanner", "membres inférieurs", True, "Suspicion de thrombose veineuse profonde", "urgent", ["ordonnance", "créatinine"]),
    ("IRM", "cérébrale", False, "Céphalées chroniques avec signes neurologiques focaux", "prioritaire", ["ordonnance"]),
    ("IRM", "cérébrale", True, "Suspicion de tumeur cérébrale", "urgent", ["ordonnance", "créatinine"]),
    ("IRM", "du rachis cervical", False, "Cervicalgies avec névralgie cervico-brachiale", "routine", ["ordonnance"]),
    ("IRM", "du rachis lombaire", False, "Sciatalgie L5 gauche rebelle", "routine", ["ordonnance"]),
    ("IRM", "du genou droit", False, "Suspicion de rupture du LCA post-traumatique", "prioritaire", ["ordonnance"]),
    ("IRM", "du genou gauche", False, "Douleur méniscale chronique", "routine", ["ordonnance"]),
    ("IRM", "de l'épaule droite", False, "Suspicion de rupture de la coiffe des rotateurs", "routine", ["ordonnance"]),
    ("IRM", "de l'épaule gauche", True, "Instabilité récidivante de l'épaule", "routine", ["ordonnance"]),
    ("IRM", "pelvienne", False, "Douleurs pelviennes chroniques", "routine", ["ordonnance"]),
    ("IRM", "hépatique", True, "Caractérisation de lésion hépatique", "prioritaire", ["ordonnance", "créatinine"]),
    ("IRM", "mammaire", True, "Bilan complémentaire après mammographie ACR4", "prioritaire", ["ordonnance"]),
    ("IRM", "cardiaque", True, "Bilan de cardiomyopathie", "prioritaire", ["ordonnance", "créatinine"]),
    ("IRM", "de la cheville", False, "Entorse grave avec suspicion de lésion ostéochondrale", "routine", ["ordonnance"]),
    ("IRM", "du poignet", False, "Douleur chronique du poignet, suspicion TFCC", "routine", ["ordonnance"]),
    ("doppler", "des troncs supra-aortiques", None, "AIT hémisphérique gauche", "urgent", ["ordonnance"]),
    ("doppler", "artériel des membres inférieurs", None, "Claudication intermittente stade II", "routine", ["ordonnance"]),
    ("doppler", "veineux des membres inférieurs", None, "Suspicion de TVP", "urgent", ["ordonnance"]),
    ("doppler", "rénal", None, "HTA résistante, suspicion de sténose artérielle rénale", "prioritaire", ["ordonnance"]),
    ("echo", "abdominale", None, "Hépatomégalie à l'examen clinique", "routine", ["ordonnance"]),
    ("echo", "pelvienne", None, "Métrorragies post-ménopausiques", "prioritaire", ["ordonnance"]),
    ("echo", "thyroïdienne", None, "Nodule thyroïdien palpable", "routine", ["ordonnance"]),
    ("echo", "des parties molles (avant-bras)", None, "Tuméfaction sous-cutanée d'apparition récente", "routine", ["ordonnance"]),
    ("echo", "mammaire", None, "Masse palpable sein gauche", "prioritaire", ["ordonnance"]),
    ("echo", "scrotale", None, "Douleur testiculaire aiguë", "urgent", ["ordonnance"]),
    ("radio", "thorax face + profil", None, "Toux chronique, bilan pneumologique", "routine", ["ordonnance"]),
    ("radio", "du bassin face", None, "Douleur de hanche droite", "routine", ["ordonnance"]),
    ("radio", "du genou droit face + profil", None, "Gonalgie post-traumatique", "routine", ["ordonnance"]),
    ("radio", "de la main droite face + 3/4", None, "Traumatisme de la main", "routine", ["ordonnance"]),
    ("radio", "du pied gauche face + profil", None, "Douleur métatarsienne chronique", "routine", ["ordonnance"]),
    ("radio", "du rachis cervical", None, "Cervicalgies post-traumatiques (AVP)", "urgent", ["ordonnance"]),
    ("radio", "panoramique dentaire", None, "Bilan pré-implantaire", "routine", ["ordonnance"]),
    ("autre", "arthrographie du genou", True, "Bilan pré-arthroscopique", "routine", ["ordonnance", "créatinine"]),
]

# Missing info patterns
MISSING_PATTERNS = [
    "complete",
    "missing_patient_dob",
    "missing_patient_phone",
    "missing_prescriber_contact",
    "missing_prescriber_name",
    "missing_injection_info",
    "missing_indication",
    "missing_creatinine",
    "missing_patient_identity",
    "ambiguous_exam",
]

# Channel templates
def gen_phone():
    return f"0{random.choice(['6','7'])} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"

def gen_hosp_phone():
    return f"04 {random.randint(20,99)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"

def gen_date(year_min=1940, year_max=2010):
    y = random.randint(year_min, year_max)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return f"{d:02d}/{m:02d}/{y}"

def gen_creat():
    return random.randint(45, 180)

def gen_email(first, last):
    first_clean = first.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e").replace("ï", "i").replace("î", "i").replace("ô", "o").replace("ü", "u").replace("û", "u").replace("à", "a").replace("â", "a").replace("ç", "c").replace("ù", "u")
    last_clean = last.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e").replace("ï", "i").replace("î", "i").replace("ô", "o").replace("ü", "u").replace("û", "u").replace("à", "a").replace("â", "a").replace("ç", "c").replace("ù", "u")
    return f"{first_clean[0]}.{last_clean}@{random.choice(EMAIL_DOMAINS)}"

def gen_dr_email(first, last):
    first_clean = first.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e").replace("-", "").replace("ï", "i").replace("î", "i").replace("ô", "o").replace("ü", "u").replace("û", "u").replace("à", "a").replace("â", "a").replace("ç", "c").replace("ù", "u")
    last_clean = last.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e").replace("ï", "i").replace("î", "i").replace("ô", "o").replace("ü", "u").replace("û", "u").replace("à", "a").replace("â", "a").replace("ç", "c").replace("ù", "u")
    return f"dr.{first_clean}.{last_clean}@{random.choice(HOSP_EMAIL_DOMAINS)}"

# --- Template generators ---

def make_email_complete(idx, scenario, patient_first, patient_last, sex, dob,
                        dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    patient_phone = gen_phone()
    patient_email = gen_email(patient_first, patient_last)
    dr_phone = gen_hosp_phone()
    dr_email = gen_dr_email(dr_first, dr_last)
    service = random.choice(SERVICES)

    inj_str = ""
    if injection is True:
        inj_str = " avec injection de produit de contraste"
    elif injection is False:
        inj_str = " sans injection"

    urgency_str = ""
    if urgency == "urgent":
        urgency_str = "\n\nDEMANDE URGENTE — Merci de programmer dans les meilleurs délais.\n"
    elif urgency == "prioritaire":
        urgency_str = "\nMerci de programmer rapidement.\n"

    creat_line = ""
    if "créatinine" in attachments and injection:
        creat = gen_creat()
        creat_line = f"\nCréatinine : {creat} µmol/L (résultat du {gen_date(2025,2025).replace('/2025', '/04/2025').split('/')[0]}/04/2025).\n"

    allergy_line = random.choice([
        "Pas d'allergie connue.",
        "Allergie : pénicilline (pas d'allergie à l'iode).",
        "Allergies : aucune.",
        "",
    ])

    pj_list = ", ".join([a.capitalize() for a in attachments])

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : Demande {mod.upper() if mod in ('IRM',) else mod} {region} — {"M." if sex == "M" else "Mme"} {patient_last}
{urgency_str}
Bonjour,

Je vous adresse {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob}, pour {"un" if mod != "IRM" else "une"} {mod} {region}{inj_str}.

Indication clinique : {indication}.
{creat_line}
{allergy_line}

Coordonnées du patient :
- Tél : {patient_phone}
- Email : {patient_email}

Merci de me confirmer la date du rendez-vous.

Cordialement,

Dr {dr_first} {dr_last}
{specialty}{f" — {service}" if service else ""} — {hospital}
Tél secrétariat : {dr_phone}
Email : {dr_email}

PJ : {pj_list}
"""
    return text.strip()


def make_email_missing_dob(idx, scenario, patient_first, patient_last, sex, dob,
                           dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    dr_email = gen_dr_email(dr_first, dr_last)
    patient_phone = gen_phone()

    inj_str = ""
    if injection is True:
        inj_str = " avec injection"
    elif injection is False:
        inj_str = " sans injection"

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : {mod} {region} pour {"M." if sex == "M" else "Mme"} {patient_last}

Bonjour,

Pourriez-vous programmer {"un" if mod != "IRM" else "une"} {mod} {region}{inj_str} pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last} ?

Motif : {indication}.

Le patient est joignable au {patient_phone}.

Merci,

Dr {dr_first} {dr_last}
{specialty} — {hospital}
Tél : {gen_hosp_phone()}
"""
    return text.strip()


def make_email_missing_phone(idx, scenario, patient_first, patient_last, sex, dob,
                             dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    dr_email = gen_dr_email(dr_first, dr_last)

    inj_str = ""
    if injection is True:
        inj_str = " avec injection"
    elif injection is False:
        inj_str = " sans injection"

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : Demande {mod} {region}

Bonjour,

Demande de {mod} {region}{inj_str} pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob}.

Indication : {indication}.

Ordonnance en pièce jointe.

Bien cordialement,
Dr {dr_first} {dr_last}
{specialty} — {hospital}
Email : {dr_email}
"""
    return text.strip()


def make_email_missing_prescriber(idx, scenario, patient_first, patient_last, sex, dob,
                                  dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    patient_phone = gen_phone()

    inj_str = ""
    if injection is True:
        inj_str = " avec injection"
    elif injection is False:
        inj_str = " sans injection"

    text = f"""De : noreply@messagerie-pro.fr
À : secretariat.radio@clinique-montchat.fr
Objet : {mod} {region}

Bonjour,

Merci de prévoir {"un" if mod != "IRM" else "une"} {mod} {region}{inj_str} pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob}.

{indication}.

Tél patient : {patient_phone}

Ordonnance jointe.

Cordialement
"""
    return text.strip()


def make_email_missing_prescriber_name(idx, scenario, patient_first, patient_last, sex, dob,
                                       dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    patient_phone = gen_phone()

    text = f"""De : secretariat@{random.choice(HOSP_EMAIL_DOMAINS)}
À : secretariat.radio@clinique-montchat.fr
Objet : Demande d'examen

Bonjour,

Un de nos médecins souhaite programmer {"un" if mod != "IRM" else "une"} {mod} {region} pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last} (né{"e" if sex == "F" else ""} le {dob}).

Motif : {indication}.

Patient joignable au {patient_phone}.

Merci
Secrétariat {specialty}
{hospital}
"""
    return text.strip()


def make_email_missing_injection(idx, scenario, patient_first, patient_last, sex, dob,
                                 dr_first, dr_last, specialty, hospital):
    mod, region, _, indication, urgency, attachments = scenario
    dr_email = gen_dr_email(dr_first, dr_last)
    patient_phone = gen_phone()

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : {mod} {region} — {"M." if sex == "M" else "Mme"} {patient_last}

Bonjour,

Je souhaite programmer {"un" if mod != "IRM" else "une"} {mod} {region} pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob}.

Indication : {indication}.

Contact patient : {patient_phone}

Cordialement,
Dr {dr_first} {dr_last}
{specialty} — {hospital}
Tél : {gen_hosp_phone()}
Email : {dr_email}
"""
    return text.strip()


def make_email_missing_indication(idx, scenario, patient_first, patient_last, sex, dob,
                                  dr_first, dr_last, specialty, hospital):
    mod, region, injection, _, urgency, attachments = scenario
    dr_email = gen_dr_email(dr_first, dr_last)
    patient_phone = gen_phone()

    inj_str = ""
    if injection is True:
        inj_str = " avec injection"
    elif injection is False:
        inj_str = " sans injection"

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : RDV {mod}

Bonjour,

Merci de donner un RDV pour {"un" if mod != "IRM" else "une"} {mod} {region}{inj_str} à {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob}.

Tél : {patient_phone}

Dr {dr_first} {dr_last}
{specialty} — {hospital}
"""
    return text.strip()


def make_email_missing_creatinine(idx, scenario, patient_first, patient_last, sex, dob,
                                  dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    dr_email = gen_dr_email(dr_first, dr_last)
    patient_phone = gen_phone()

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : {mod} {region} avec injection — {"M." if sex == "M" else "Mme"} {patient_last}

Bonjour,

Je vous adresse {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob}, pour {"un" if mod != "IRM" else "une"} {mod} {region} avec injection.

Indication clinique : {indication}.

Contact patient : {patient_phone}
Pas d'allergie connue.

Cordialement,
Dr {dr_first} {dr_last}
{specialty} — {hospital}
Tél : {gen_hosp_phone()}
Email : {dr_email}

PJ : Ordonnance
"""
    return text.strip()


def make_email_missing_identity(idx, scenario, patient_first, patient_last, sex, dob,
                                dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    dr_email = gen_dr_email(dr_first, dr_last)

    inj_str = ""
    if injection is True:
        inj_str = " avec injection"
    elif injection is False:
        inj_str = " sans injection"

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : Demande d'examen pour un patient

Bonjour,

J'aurais besoin de programmer {"un" if mod != "IRM" else "une"} {mod} {region}{inj_str} pour un de mes patients.

{indication}. Examen {"urgent" if urgency == "urgent" else "à programmer"}.

Je vous rappellerai avec les coordonnées du patient.

Dr {dr_first} {dr_last}
{specialty} — {hospital}
"""
    return text.strip()


def make_fax(idx, scenario, patient_first, patient_last, sex, dob,
             dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario
    dr_phone = gen_hosp_phone()

    inj_str = "NON PRÉCISÉ"
    if injection is True:
        inj_str = "OUI"
    elif injection is False:
        inj_str = "NON"

    creat_line = "Non fournie"
    if "créatinine" in attachments and injection:
        creat_line = f"{gen_creat()} µmol/L"

    text = f"""========================================
      FAX — {hospital.upper()}
      {specialty}
========================================

DATE : {random.randint(1,28):02d}/04/2025
DESTINATAIRE : Service de Radiologie — Clinique Montchat

DEMANDE D'EXAMEN

Patient : {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}
Né{"e" if sex == "F" else ""} le : {dob}
Sexe : {sex}

Examen demandé : {mod} {region}
Avec injection : {inj_str}

Indication clinique :
{indication}

Créatinine : {creat_line}
Allergies : {random.choice(["AUCUNE", "Non renseigné", "Pénicilline"])}

Prescripteur : Dr {dr_first} {dr_last}
Service : {specialty}
{hospital}
Tél : {dr_phone}

========================================
"""
    return text.strip()


def make_walkin(idx, scenario, patient_first, patient_last, sex, dob,
                dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario

    notes = random.choice([
        "Patient a une ordonnance mais pas de pièce d'identité.",
        "Patient sans RDV, se présente avec ordonnance.",
        "Patient pressé, demande si c'est possible aujourd'hui.",
        "Accompagné par un proche qui traduit (patient ne parle pas français).",
        "Patient âgé, accompagné par sa fille.",
    ])

    text = f"""Note accueil — {random.randint(1,28):02d}/04/2025 {random.randint(8,17)}h{random.randint(0,59):02d}

Patient se présente au guichet.

{"M." if sex == "M" else "Mme"} {patient_first} {patient_last}
{"Né" if sex == "M" else "Née"} le {dob}

Ordonnance pour : {mod} {region}
Prescripteur : Dr {dr_last} (tampon {random.choice(["lisible", "peu lisible", "illisible"])})

Motif évoqué : {indication}

{notes}

Tél : {gen_phone() if random.random() > 0.4 else "non communiqué"}
"""
    return text.strip()


def make_ambiguous(idx, scenario, patient_first, patient_last, sex, dob,
                   dr_first, dr_last, specialty, hospital):
    mod, region, injection, indication, urgency, attachments = scenario

    ambiguous_terms = {
        "scanner": random.choice(["scann", "TDM", "scan", "tomodensito"]),
        "IRM": random.choice(["remnance", "RMN", "imagerie magnétique", "irm"]),
        "doppler": random.choice(["doppler", "écho-doppler", "ED"]),
        "echo": random.choice(["écho", "échographie", "US"]),
        "radio": random.choice(["rx", "radio", "radiographie"]),
        "autre": "examen",
    }

    exam_term = ambiguous_terms.get(mod, mod)
    patient_phone = gen_phone()
    dr_email = gen_dr_email(dr_first, dr_last)

    text = f"""De : {dr_email}
À : secretariat.radio@clinique-montchat.fr
Objet : examen pour {"M." if sex == "M" else "Mme"} {patient_last}

Bonjour,

Pourriez-vous faire un {exam_term} pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last} ({dob}) ?

{indication}.

Tel patient : {patient_phone}

Merci
Dr {dr_last}
"""
    return text.strip()


def make_lab_result(idx, scenario, patient_first, patient_last, sex, dob,
                    dr_first, dr_last, specialty, hospital):
    creat = gen_creat()
    dfg = random.randint(30, 120)
    alert = ""
    if creat > 110:
        alert = "\nATTENTION : Créatinine élevée. Injection de produit de contraste à discuter.\n"

    text = f"""De : resultats@labo-{random.choice(["confluence", "biomedicis", "cerba", "biogroup"])}.fr
À : secretariat.radio@clinique-montchat.fr
Objet : Résultats biologiques — {"M." if sex == "M" else "Mme"} {patient_last} {patient_first}

Bonjour,

Résultats pour {"M." if sex == "M" else "Mme"} {patient_first} {patient_last}, né{"e" if sex == "F" else ""} le {dob} :

- Créatinine : {creat} µmol/L
- DFG estimé : {dfg} mL/min
- Hémoglobine : {round(random.uniform(10.5, 16.5), 1)} g/dL
- Plaquettes : {random.randint(150, 400)} G/L
{alert}
Prélèvement du {random.randint(15,28):02d}/04/2025.

Cordialement,
Laboratoire
"""
    return text.strip()


GENERATORS = {
    "complete": make_email_complete,
    "missing_patient_dob": make_email_missing_dob,
    "missing_patient_phone": make_email_missing_phone,
    "missing_prescriber_contact": make_email_missing_prescriber,
    "missing_prescriber_name": make_email_missing_prescriber_name,
    "missing_injection_info": make_email_missing_injection,
    "missing_indication": make_email_missing_indication,
    "missing_creatinine": make_email_missing_creatinine,
    "missing_patient_identity": make_email_missing_identity,
    "ambiguous_exam": make_ambiguous,
}

# Additional special templates
SPECIAL_TEMPLATES = ["fax", "walkin", "lab_result"]


def generate_sample(idx):
    """Generate one sample."""
    # Pick random patient
    sex = random.choice(["M", "F"])
    if sex == "M":
        patient_first = random.choice(FIRST_NAMES_M)
    else:
        patient_first = random.choice(FIRST_NAMES_F)
    patient_last = random.choice(LAST_NAMES)
    dob = gen_date(1940, 2015)

    # Pick random doctor
    dr_first = random.choice(DR_FIRST_NAMES)
    dr_last = random.choice(DR_LAST_NAMES)
    specialty = random.choice(SPECIALTIES)
    hospital = random.choice(HOSPITALS)

    # Pick random scenario
    scenario = random.choice(EXAM_SCENARIOS)

    # Pick pattern — weighted to have variety
    r = random.random()
    if r < 0.30:
        pattern = "complete"
    elif r < 0.40:
        # Special templates
        special = random.choice(SPECIAL_TEMPLATES)
        if special == "fax":
            return make_fax(idx, scenario, patient_first, patient_last, sex, dob,
                           dr_first, dr_last, specialty, hospital)
        elif special == "walkin":
            return make_walkin(idx, scenario, patient_first, patient_last, sex, dob,
                              dr_first, dr_last, specialty, hospital)
        else:
            return make_lab_result(idx, scenario, patient_first, patient_last, sex, dob,
                                  dr_first, dr_last, specialty, hospital)
    else:
        pattern = random.choice([p for p in MISSING_PATTERNS if p != "complete"])

    # For missing_injection_info, only use scanner/IRM scenarios
    if pattern == "missing_injection_info":
        candidates = [s for s in EXAM_SCENARIOS if s[0] in ("scanner", "IRM") and s[2] is not None]
        scenario = random.choice(candidates) if candidates else scenario

    # For missing_creatinine, only use scenarios with injection
    if pattern == "missing_creatinine":
        candidates = [s for s in EXAM_SCENARIOS if s[2] is True]
        scenario = random.choice(candidates) if candidates else scenario

    gen_func = GENERATORS.get(pattern, make_email_complete)
    return gen_func(idx, scenario, patient_first, patient_last, sex, dob,
                    dr_first, dr_last, specialty, hospital)


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(11, 101):
        content = generate_sample(i)
        filename = f"{i:03d}_sample.txt"
        (SAMPLES_DIR / filename).write_text(content, encoding="utf-8")
        print(f"Generated {filename}")

    print(f"\nGenerated 90 samples (011-100) in {SAMPLES_DIR}")


if __name__ == "__main__":
    main()
