"""Scripted behaviour of the simulated insurer (demo only, PRD 2.11).

A scenario is an ordered list of steps. Each inbound email is classified into an intent; the
simulator picks the first step whose `trigger` matches and that has not been played yet (or
falls back to a generic acknowledgement). Replies are French, insurer tone, and every reply
carries the "SIMULATED INSURER" label. The script never reads the Claims Agent's memory.
"""

from dataclasses import dataclass, field
import re

SIGNATURE = (
    "\n\nService Indemnisation Professionnels\n"
    "Assurances Démo — SIMULATED INSURER (hackathon demo, not a real insurer)\n"
    "sinistres-demo-assureur@agentmail.to"
)

# --- intent classification --------------------------------------------------------------------

INTENT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("contest", re.compile(r"\b(contest\w*|désaccord|desaccord|réclamation|reclamation)\b", re.I)),
    ("written_confirmation", re.compile(r"\b(confirmation écrite|confirmation ecrite|échange téléphonique|echange telephonique|confirmer par écrit)\b", re.I)),
    ("document_request", re.compile(r"\b(communication de pièces|communiquer|conditions (générales|particulières)|rapport d'expertise|preuve de (la )?remise)\b", re.I)),
    ("loss_statement", re.compile(r"\b(état des pertes|etat des pertes|récapitulatif des dommages|chiffrage|montant total)\b", re.I)),
    ("complements", re.compile(r"\b(compl[ée]ment|pièces? jointes?|ci-joint|factures?|inventaire|dépôt de plainte|récépissé)\b", re.I)),
    ("declaration", re.compile(r"\b(déclaration de sinistre|declaration de sinistre|déclarons|nous vous déclarons)\b", re.I)),
]


def classify(subject: str, body: str) -> str:
    text = f"{subject}\n{body}"
    for intent, pat in INTENT_PATTERNS:
        if pat.search(text):
            return intent
    return "other"


# --- scenario definition ----------------------------------------------------------------------

@dataclass
class Step:
    key: str
    trigger: set[str]
    subject: str
    body: str
    delay_seconds: int = 15
    attach_release_pdf: bool = False
    once: bool = True


@dataclass
class Scenario:
    name: str
    steps: list[Step] = field(default_factory=list)
    fallback_subject: str = "Re: {subject}"
    fallback_body: str = (
        "Madame, Monsieur,\n\nNous accusons réception de votre message, qui a été joint au dossier {ref}. "
        "Il sera traité dans les meilleurs délais par le gestionnaire en charge.\n\nCordialement,"
    )


def _ref(n: int) -> str:
    return f"SIN-2026-{104200 + n:06d}"


KARIM_DEFAULT = Scenario(
    name="karim_default",
    steps=[
        Step(
            key="ack_declaration", trigger={"declaration"},
            subject="Re: {subject} — Accusé de réception — dossier {ref}",
            body=(
                "Madame, Monsieur,\n\n"
                "Nous accusons réception de votre déclaration de sinistre pour le compte de {business_name}, contrat n° {policy_number}. "
                "Votre dossier est enregistré sous la référence {ref}, à rappeler dans toute correspondance.\n\n"
                "Afin de poursuivre l'instruction, nous vous remercions de nous transmettre :\n"
                "- le récépissé de dépôt de plainte ;\n"
                "- un état des pertes chiffré accompagné des justificatifs (factures d'achat, dernier inventaire, export de caisse) ;\n"
                "- le nombre et la valeur des appareils appartenant à des clients qui se trouvaient dans la boutique au moment des faits, le cas échéant ;\n"
                "- des photographies des dommages avant toute remise en état.\n\n"
                "Nous vous rappelons qu'aucune réparation définitive ne doit être engagée sans notre accord écrit, à l'exception des mesures conservatoires.\n\n"
                "Un expert pourra être missionné selon le montant des dommages déclarés.\n\nCordialement,"
            ),
            delay_seconds=20,
        ),
        Step(
            key="ask_invoices", trigger={"loss_statement"},
            subject="Re: {subject} — dossier {ref} — pièces complémentaires",
            body=(
                "Madame, Monsieur,\n\n"
                "Nous avons bien reçu l'état des pertes relatif au dossier {ref}.\n\n"
                "Pour l'évaluation du poste « marchandises », nous vous remercions de nous adresser les factures d'achat fournisseurs correspondantes ainsi que le dernier inventaire. "
                "Nous attirons votre attention sur le fait que les marchandises dérobées relèvent de la garantie Vol, dont le plafond contractuel s'applique.\n\n"
                "La perte d'exploitation ne pourra être examinée qu'au vu des éléments comptables (chiffre d'affaires mensuel N-1 et N-2, charges variables).\n\n"
                "Cordialement,"
            ),
            delay_seconds=25,
        ),
        Step(
            key="confirm_theft_cap", trigger={"written_confirmation"},
            subject="Re: {subject} — dossier {ref}",
            body=(
                "Madame, Monsieur,\n\n"
                "Nous confirmons les éléments évoqués lors de notre échange téléphonique : les marchandises dérobées lors des événements du 17 octobre 2026 sont traitées, "
                "en l'état du dossier, au titre de la garantie Vol du contrat, dans la limite du plafond prévu aux conditions particulières, soit 15 000 €. "
                "Cette position est émise sous réserve des conclusions de l'expertise et de l'examen des conditions particulières.\n\n"
                "Les pièces à transmettre pour la valorisation du stock sont les factures d'achat fournisseurs et le dernier inventaire.\n\nCordialement,"
            ),
            delay_seconds=20,
        ),
        Step(
            key="offer_with_release", trigger={"complements"},
            subject="Re: {subject} — dossier {ref} — proposition d'indemnisation",
            body=(
                "Madame, Monsieur,\n\n"
                "Après examen des pièces transmises pour le dossier {ref}, nous sommes en mesure de vous adresser la proposition d'indemnisation suivante :\n\n"
                "- Marchandises (garantie Vol, plafond contractuel) : 15 000,00 €\n"
                "- Vitrine (bris de glace, valeur à neuf) : 3 600,00 €\n"
                "- Rideau métallique et caisse enregistreuse, après application d'une vétusté de 30 % : 3 150,00 €\n"
                "- Franchise contractuelle : - 1 000,00 €\n"
                "Total proposé : 20 750,00 €\n\n"
                "Les autres postes déclarés ne sont pas retenus en l'état (absence de justificatifs ou hors garantie).\n\n"
                "Vous trouverez ci-joint la quittance d'indemnité à nous retourner signée pour permettre le règlement. "
                "Le versement interviendra sous 30 jours à compter de la réception de la quittance signée.\n\nCordialement,"
            ),
            delay_seconds=30,
            attach_release_pdf=True,
        ),
        Step(
            key="contest_to_expert", trigger={"contest"},
            subject="Re: {subject} — dossier {ref} — transmission à l'expert",
            body=(
                "Madame, Monsieur,\n\n"
                "Nous prenons note de votre contestation et des éléments complémentaires transmis. Le dossier {ref} est transmis à notre expert pour un nouvel examen "
                "des postes contestés, notamment la qualification de la garantie applicable aux marchandises.\n\n"
                "Nous reviendrons vers vous à l'issue de cet examen, dans un délai indicatif de quinze jours.\n\nCordialement,"
            ),
            delay_seconds=20,
        ),
        Step(
            key="documents_sent", trigger={"document_request"},
            subject="Re: {subject} — dossier {ref} — communication de pièces",
            body=(
                "Madame, Monsieur,\n\n"
                "Nous accusons réception de votre demande de communication de pièces pour le dossier {ref}. "
                "Les documents contractuels sollicités vous seront adressés par le service gestion des contrats sous dix jours ouvrés.\n\nCordialement,"
            ),
            delay_seconds=20,
        ),
    ],
)

SCENARIOS = {s.name: s for s in [KARIM_DEFAULT]}


def pick_step(scenario: Scenario, intent: str, played: set[str]) -> Step | None:
    for step in scenario.steps:
        if intent in step.trigger and (not step.once or step.key not in played):
            return step
    return None


def make_reference(seq: int) -> str:
    return _ref(seq)
