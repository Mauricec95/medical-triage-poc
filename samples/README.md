# Echantillons synthétiques / Synthetic Samples

Tous les noms, coordonnées et informations médicales sont **fictifs**.
All names, contact details, and medical information are **synthetic**.

| # | Fichier | Cas | Particularité |
|---|---------|-----|---------------|
| 01 | `01_irm_thoracique.txt` | Ordonnance propre pour IRM thoracique | Complet, toutes les infos présentes |
| 02 | `02_coroscanner_ambiguous.txt` | Coroscanner sans précision d'injection | Injection non spécifiée → champ manquant |
| 03 | `03_missing_prescriber.txt` | Demande scanner abdominopelvien | Contact prescripteur absent |
| 04 | `04_fax_scanner.pdf` | Fax scanné d'une demande scanner | Nécessite OCR (simulated as text for POC) |
| 05 | `05_lab_result_unknown.txt` | Résultat biologique pour patient inconnu | Patient non connu du secrétariat |
| 06 | `06_urgent_diu.txt` | Demande urgente DIU | Urgence élevée, coordination nécessaire |
| 07 | `07_pediatric.txt` | Cas pédiatrique (<10 ans) | Coordination hospitalisation pédiatrique |
| 08 | `08_walkin_handwritten.txt` | Note de passage patient (style manuscrit) | Texte informel, écriture télégraphique |
| 09 | `09_blood_test_no_match.txt` | Bilan sanguin sans patient programmé | Pas de correspondance avec examen prévu |
| 10 | `10_no_signature.txt` | Email d'un service prescripteur sans signature | Aucun contact identifiable |
