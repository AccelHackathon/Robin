"""Generates the 'quittance d'indemnité pour solde de tout compte' PDF attached to the demo offer.

Its only purpose is to exercise the Claims Agent's release-language detection (PRD 2.9, AC-9).
"""

from datetime import date

from fpdf import FPDF

RELEASE_TEXT = (
    "Je soussigné(e), {signer}, agissant pour le compte de {business_name}, reconnais avoir reçu de "
    "Assurances Démo la somme de {amount} euros ({amount_words}) en règlement du sinistre survenu le {loss_date}, "
    "dossier {ref}, contrat n° {policy_number}.\n\n"
    "Cette somme est acceptée POUR SOLDE DE TOUT COMPTE. Par la signature de la présente quittance, l'assuré déclare "
    "être intégralement indemnisé de l'ensemble des dommages résultant de ce sinistre et RENONCE à toute réclamation "
    "ultérieure, présente ou future, à quelque titre que ce soit, en relation avec cet événement. La présente "
    "quittance vaut TRANSACTION au sens des articles 2044 et suivants du Code civil et met fin définitivement au dossier."
)


def build_release_pdf(*, business_name: str, signer: str, amount: float, loss_date: str, ref: str, policy_number: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "ASSURANCES DEMO - Service Indemnisation", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(160, 0, 0)
    pdf.cell(0, 6, "SIMULATED INSURER - document generated for a hackathon demo, no legal effect", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "QUITTANCE D'INDEMNITE POUR SOLDE DE TOUT COMPTE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    amount_str = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    text = RELEASE_TEXT.format(signer=signer, business_name=business_name, amount=amount_str,
                               amount_words="vingt mille sept cent cinquante", loss_date=loss_date, ref=ref, policy_number=policy_number)
    pdf.multi_cell(0, 6, text)
    pdf.ln(10)
    pdf.cell(0, 8, f"Fait à Marseille, le {date.today():%d/%m/%Y}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.cell(0, 8, "Signature de l'assuré, précédée de la mention « Bon pour quittance et renonciation » :", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.cell(0, 8, "____________________________________________", new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
