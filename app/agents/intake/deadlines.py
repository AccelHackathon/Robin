"""Extract sourced candidate rules, not dates. C instantiates confirmed rules per claim."""

import re
from psycopg.types.json import Jsonb

TERMS = {
    "police_report": "plainte",
    "declaration": "déclar",
    "loss_statement": "état des pertes",
    "payment": "paiement",
    "replacement_value_top_up": "deux ans",
    "prescription": "prescription",
}


async def extract_deadline_candidates(state):
    from app.agents.intake.graph import execute

    for kind, term in TERMS.items():
        for c in state["clauses"]:
            if term not in c["body"].casefold():
                continue
            lines = c["body"].splitlines()
            for i, line in enumerate(lines):
                if term not in line.casefold():
                    continue
                quote = "\n".join(lines[max(0, i - 1) : i + 3]).strip()[:600]
                if not re.search(
                    r"\b(?:\d+|deux|cinq|trente)\s+(?:jours?|heures?|ans?|mois)|au plus vite",
                    quote,
                    re.I,
                ):
                    continue
                await execute(
                    """INSERT INTO deadline_rules(account_id,document_id,kind,rule,source_clause_id,quote,page)
                  VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING""",
                    (
                        state["account_id"],
                        c["document_id"],
                        kind,
                        Jsonb(
                            {
                                "status": "to_confirm",
                                "text": quote,
                                "requires_claim_context": True,
                            }
                        ),
                        c["id"],
                        quote,
                        c["page"],
                    ),
                )
                break
