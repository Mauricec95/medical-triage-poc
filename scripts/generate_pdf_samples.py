#!/usr/bin/env python3
"""Generate PDF and image samples for OCR testing.

Creates:
- Text-layer PDFs (pdfplumber can read directly)
- Image-based PDFs (requires OCR via pytesseract)
- PNG image samples (requires OCR)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def create_text_pdf(filename: str, lines: list[str]) -> None:
    """Create a PDF with a text layer (readable by pdfplumber)."""
    path = SAMPLES_DIR / filename
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30 * mm, height - 25 * mm, "FAX — SERVICE DE RADIOLOGIE")
    c.line(20 * mm, height - 28 * mm, width - 20 * mm, height - 28 * mm)

    # Body
    c.setFont("Helvetica", 11)
    y = height - 40 * mm
    for line in lines:
        if y < 30 * mm:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 25 * mm
        c.drawString(25 * mm, y, line)
        y -= 6 * mm

    c.save()
    print(f"Created text PDF: {filename}")


def create_image_pdf(filename: str, lines: list[str]) -> None:
    """Create an image-based PDF (no text layer — requires OCR)."""
    # Render text to image first
    img_width, img_height = 2480, 3508  # A4 at 300 DPI
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
        font_bold = font

    # Header
    draw.text((150, 100), "FAX — SERVICE DE RADIOLOGIE", fill="black", font=font_bold)
    draw.line([(100, 170), (2380, 170)], fill="black", width=3)

    # Body
    y = 220
    for line in lines:
        draw.text((150, y), line, fill="black", font=font)
        y += 55

    # Convert to PDF (image-only, no text layer)
    path = SAMPLES_DIR / filename
    img.save(str(path), "PDF", resolution=300)
    print(f"Created image PDF: {filename}")


def create_png_image(filename: str, lines: list[str]) -> None:
    """Create a PNG image with text (requires OCR)."""
    img_width = 1200
    line_height = 32
    img_height = max(400, len(lines) * line_height + 120)
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        font = ImageFont.load_default()

    y = 40
    for line in lines:
        draw.text((40, y), line, fill="black", font=font)
        y += line_height

    path = SAMPLES_DIR / filename
    img.save(str(path))
    print(f"Created PNG: {filename}")


# --- Sample content ---

FAX_SCANNER_CEREBRAL = [
    "DATE : 22/04/2025",
    "DESTINATAIRE : Service de Radiologie",
    "",
    "DEMANDE D'EXAMEN",
    "",
    "Patient : M. Hassan EL FASSI",
    "Ne le : 14/03/1958",
    "Sexe : M",
    "",
    "Examen demande : Scanner cerebral sans injection",
    "",
    "Indication clinique :",
    "Cephalees brutales avec vomissements.",
    "Suspicion d'accident vasculaire cerebral.",
    "URGENT - a programmer en urgence.",
    "",
    "Prescripteur : Dr Nathalie VINCENT",
    "Service : Neurologie",
    "CHU Lyon",
    "Tel : 04 72 35 66 77",
    "",
    "Allergies : AUCUNE",
]

FAX_IRM_LOMBAIRE = [
    "DATE : 20/04/2025",
    "DESTINATAIRE : Service d'Imagerie Medicale",
    "",
    "DEMANDE D'IRM",
    "",
    "Patiente : Mme Sylvie ROUSSEAU",
    "Nee le : 08/11/1975",
    "Sexe : F",
    "",
    "Examen demande : IRM du rachis lombaire",
    "Sans injection",
    "",
    "Indication clinique :",
    "Lombosciatalgie L5 droite depuis 3 mois.",
    "Echec du traitement medical bien conduit.",
    "Bilan pre-chirurgical.",
    "",
    "Coordonnees patiente :",
    "Tel : 06 44 55 66 77",
    "Email : s.rousseau@gmail.com",
    "",
    "Prescripteur : Dr Marc LEBLANC",
    "Chirurgie orthopedique",
    "Clinique du Parc",
    "Tel : 04 78 22 33 44",
    "Email : dr.leblanc@clinique-parc.fr",
    "",
    "PJ : Ordonnance, CR consultation",
]

FAX_ECHO_THYROIDE = [
    "FAX MEDICAL",
    "Date : 18/04/2025",
    "",
    "A l'attention du service de radiologie",
    "Clinique Montchat",
    "",
    "Demande d'echographie thyroidienne",
    "",
    "Patient : Mme Fatima BENALI",
    "Date de naissance : 22/06/1982",
    "",
    "Motif : Nodule thyroidien decouvert",
    "a la palpation. Bilan initial.",
    "TSH normale.",
    "",
    "Tel patiente : 07 88 99 00 11",
    "",
    "Dr Antoine MERCIER",
    "Endocrinologie",
    "Hopital Edouard Herriot",
    "Tel : 04 72 11 55 66",
]

IMAGE_ORDONNANCE_RADIO = [
    "ORDONNANCE",
    "",
    "Dr Jean-Pierre MOREAU",
    "Medecine Generale",
    "15 rue de la Republique, 69001 Lyon",
    "Tel : 04 78 11 22 33",
    "",
    "Le 19/04/2025",
    "",
    "Pour : M. Georges LAMBERT",
    "Ne le 05/04/1950",
    "",
    "Radio du thorax face + profil",
    "",
    "Indication : Toux chronique depuis",
    "3 mois. Tabagisme actif 40 PA.",
    "Bilan pneumologique.",
    "",
    "Signature : Dr MOREAU",
]

IMAGE_NOTE_WALKIN = [
    "NOTE D'ACCUEIL - 21/04/2025",
    "",
    "Patiente : Mme Rosa MARTINEZ",
    "Nee le 12/07/1988",
    "",
    "Se presente avec ordonnance pour",
    "echographie pelvienne.",
    "",
    "Prescripteur : Dr FERNANDEZ",
    "(tampon peu lisible)",
    "",
    "Motif : douleurs pelviennes",
    "chroniques, bilan de fertilite.",
    "",
    "Tel : 06 33 44 55 66",
    "",
    "Pas d'allergie connue.",
]

IMAGE_FAX_DOPPLER = [
    "FAX MEDICAL - URGENT",
    "",
    "De : Service de Chirurgie Vasculaire",
    "CHU Grenoble",
    "",
    "Patient : M. Paul CHEVALIER",
    "Ne le 30/01/1945",
    "",
    "Demande : Doppler arteriel",
    "des membres inferieurs",
    "",
    "Indication : Claudication",
    "intermittente stade III.",
    "Repos douloureux nocturne.",
    "Bilan pre-operatoire urgent.",
    "",
    "Dr Isabelle RENARD",
    "Chirurgie vasculaire",
    "Tel : 04 76 55 44 33",
    "",
    "URGENT - dans les 48h SVP",
]


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    # Remove old 04_fax_scanner.txt (was a text placeholder)
    old_fax = SAMPLES_DIR / "04_fax_scanner.txt"
    if old_fax.exists():
        old_fax.unlink()
        print("Removed old 04_fax_scanner.txt")

    # Text-layer PDFs
    create_text_pdf("04_fax_scanner.pdf", FAX_SCANNER_CEREBRAL)
    create_text_pdf("101_fax_irm_lombaire.pdf", FAX_IRM_LOMBAIRE)

    # Image-based PDFs (no text layer — requires OCR)
    create_image_pdf("102_fax_image_echo.pdf", FAX_ECHO_THYROIDE)
    create_image_pdf("103_fax_image_doppler.pdf", IMAGE_FAX_DOPPLER)

    # PNG images
    create_png_image("104_ordonnance_radio.png", IMAGE_ORDONNANCE_RADIO)
    create_png_image("105_note_walkin.png", IMAGE_NOTE_WALKIN)

    print("\nDone! Created 6 PDF/image samples for OCR testing.")


if __name__ == "__main__":
    main()
