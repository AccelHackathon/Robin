"""French email templates for the insurer side (workstream A). Rendered text goes through review()."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"), undefined=StrictUndefined,
                   trim_blocks=True, lstrip_blocks=True, autoescape=False)

INSURER_DOCUMENT_REQUESTS = {
    "CG_signed": "une copie des conditions générales applicables au contrat, dans leur version remise à l'assuré, avec la preuve de cette remise",
    "CP_signed": "une copie des conditions particulières signées par l'assuré, ainsi que de tout avenant en vigueur à la date du sinistre",
    "delivery_proof": "la preuve de la remise à l'assuré des documents contractuels (date et modalité)",
    "expert_report": "le rapport d'expertise établi à la suite de la visite de votre expert",
}


def render(name: str, **ctx) -> tuple[str, str]:
    """Returns (subject, body). The first line of every template is the subject."""
    text = _env.get_template(f"{name}.txt.j2").render(**ctx).strip()
    first, _, rest = text.partition("\n")
    subject = first.removeprefix("Objet :").strip()
    return subject, rest.strip()
