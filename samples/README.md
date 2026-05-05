# Echantillons synthétiques / Synthetic Samples

Tous les noms, coordonnées et informations médicales sont **fictifs**.
All names, contact details, and medical information are **synthetic**.

## Echantillons manuels (01–10)

| # | Fichier | Cas | Particularité |
|---|---------|-----|---------------|
| 01 | `01_irm_thoracique.txt` | Ordonnance propre pour IRM thoracique | Complet, toutes les infos présentes |
| 02 | `02_coroscanner_ambiguous.txt` | Coroscanner sans précision d'injection | Injection non spécifiée → champ manquant |
| 03 | `03_missing_prescriber.txt` | Demande scanner abdominopelvien | Contact prescripteur absent |
| 04 | `04_fax_scanner.pdf` | Fax scanné d'une demande scanner cérébral | PDF texte (pdfplumber) |
| 05 | `05_lab_result_unknown.txt` | Résultat biologique pour patient inconnu | Patient non connu du secrétariat |
| 06 | `06_urgent_diu.txt` | Demande urgente DIU | Urgence élevée, coordination nécessaire |
| 07 | `07_pediatric.txt` | Cas pédiatrique (<10 ans) | Coordination hospitalisation pédiatrique |
| 08 | `08_walkin_handwritten.txt` | Note de passage patient (style manuscrit) | Texte informel, écriture télégraphique |
| 09 | `09_blood_test_no_match.txt` | Bilan sanguin sans patient programmé | Pas de correspondance avec examen prévu |
| 10 | `10_no_signature.txt` | Email d'un service prescripteur sans signature | Aucun contact identifiable |

## Echantillons générés (011–100)

90 échantillons texte générés par `scripts/generate_samples.py` couvrant :
- Demandes complètes (toutes modalités)
- Champs manquants : DDN, téléphone, prescripteur, indication, créatinine, identité
- Examens ambigus (termes familiers/abréviations)
- Fax (format texte structuré)
- Notes d'accueil (walk-in)
- Résultats de laboratoire

## Echantillons PDF/Image pour OCR (101–105)

| # | Fichier | Format | OCR requis | Contenu |
|---|---------|--------|------------|---------|
| 101 | `101_fax_irm_lombaire.pdf` | PDF texte | Non (pdfplumber) | IRM rachis lombaire |
| 102 | `102_fax_image_echo.pdf` | PDF image | Oui (pytesseract) | Echographie thyroïdienne |
| 103 | `103_fax_image_doppler.pdf` | PDF image | Oui (pytesseract) | Doppler artériel urgent |
| 104 | `104_ordonnance_radio.png` | PNG | Oui (pytesseract) | Radio thorax |
| 105 | `105_note_walkin.png` | PNG | Oui (pytesseract) | Note d'accueil walk-in |

Générés par `scripts/generate_pdf_samples.py`.
