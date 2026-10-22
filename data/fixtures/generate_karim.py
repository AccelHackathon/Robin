"""Generate explicitly fictional policy schedules: python data/fixtures/generate_karim.py [--ceiling 30000]."""

import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).parent


def generate(ceiling=15000):
    endorsement = ceiling != 15000
    path = ROOT / (
        "karim_endorsement.pdf" if endorsement else "karim_particular_conditions.pdf"
    )
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Robin - fictional Karim policy schedule")
    c.setFillColor(HexColor("#062a66"))
    c.rect(0, 735, 595, 107, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 23)
    c.drawString(
        40, 795, "Conditions particulières" if not endorsement else "Avenant au contrat"
    )
    c.setFont("Helvetica", 11)
    c.drawString(40, 771, "Multirisque professionnelle / MAAF - scénario Karim")
    c.setFillColor(HexColor("#062a66"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, 709, "DOCUMENT FICTIF - DÉMONSTRATION ROBIN UNIQUEMENT")
    c.setFont("Helvetica", 10)
    lines = [
        "Ce document est une fixture de test, sans valeur contractuelle.",
        "Assuré : Karim Benali / Karim Mobile",
        "Activité : réparation et revente de smartphones",
        "Adresse du risque : 12 rue de la République, 13001 Marseille",
        "Police : ROBIN-DEMO-KARIM-001",
        "Conditions générales de référence : MAAF 11031 - 01/26",
        "Date du document : 2026-10-16"
        if endorsement
        else "Date du document : 2026-10-01",
        "Prise d’effet : 2026-10-16" if endorsement else "Prise d’effet : 2026-10-01",
        "Fin de validité : 2027-09-30",
    ]
    y = 684
    for line in lines:
        c.drawString(40, y, line)
        y -= 21
    rows = [
        ("Incendie", "Souscrit"),
        ("Émeutes et mouvements populaires", "Souscrit"),
        (
            "Vol, tentative de vol et vandalisme",
            f"Souscrit - plafond stock : {ceiling:,} EUR".replace(",", " "),
        ),
        ("Bris de glace", "Souscrit"),
        ("Dégâts des eaux", "Souscrit"),
        ("Perte d’exploitation", "Souscrit - franchise : 3 jours"),
        ("Biens confiés", "Souscrit"),
        ("Aménagements du locataire", "Souscrit"),
        ("Matériel en valeur à neuf", "Souscrit"),
    ]
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y - 12, "Garanties sélectionnées")
    y -= 39
    for i, (label, value) in enumerate(rows):
        if i % 2 == 0:
            c.setFillColor(HexColor("#eef5fc"))
            c.rect(35, y - 8, 525, 30, fill=1, stroke=0)
        c.setFillColor(HexColor("#062a66"))
        c.setFont("Helvetica", 9)
        c.drawString(42, y + 3, label)
        c.drawString(290, y + 3, value)
        y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y - 13, "Franchise générale : 1 000 EUR par sinistre.")
    c.setFont("Helvetica", 9)
    c.drawString(
        40,
        y - 38,
        "Les garanties restent soumises aux conditions, exclusions et limites des CG.",
    )
    if endorsement:
        c.drawString(
            40, y - 58, "Cet avenant remplace le plafond vol antérieur de 15 000 EUR."
        )
    c.setStrokeColor(HexColor("#cedbe8"))
    c.line(40, 60, 555, 60)
    c.setFont("Helvetica", 8)
    c.drawString(
        40,
        44,
        "Scénario fictif / Ne constitue ni une attestation ni une offre d’assurance.",
    )
    c.drawRightString(555, 44, "1 / 1")
    c.save()
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ceiling", type=int, default=15000)
    print(generate(parser.parse_args().ceiling))
