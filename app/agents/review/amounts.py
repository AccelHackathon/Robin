"""Amount traceability (PRD 2.7 control 4, AGENTS.md rule 2).

An amount in an outbound text is traceable if it equals (within tolerance) an evidence amount,
a client-instruction amount, or a derived amount whose formula inputs are those and whose
clause is cited. Everything else is untraceable: the agent never originates a number.
"""

from __future__ import annotations

import re

TOLERANCE_EUR = 0.5

# "15 000 €", "15.000,50 EUR", "€3,600", "20 750,00€", "1 000 euros" — French and English forms.
_AMOUNT_RE = re.compile(
    r"(?:€\s?(\d[\d\s.,\u202f\u00a0]*\d|\d))|(?:(\d[\d\s.,\u202f\u00a0]*\d|\d)\s?(?:€|EUR\b|euros?\b))",
    re.IGNORECASE,
)


def _to_float(raw: str) -> float | None:
    s = raw.replace("\u202f", "").replace("\u00a0", "").replace(" ", "")
    # Decide the decimal separator: the last of [.,] if followed by exactly 1–2 digits.
    m = re.search(r"[.,](\d{1,2})$", s)
    if m:
        dec = s[m.start()]
        s = s[: m.start()].replace(".", "").replace(",", "") + "." + m.group(1)
        _ = dec
    else:
        s = s.replace(".", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def extract_amounts_eur(text: str) -> list[float]:
    """All euro amounts mentioned in the text, in order, duplicates kept."""
    out: list[float] = []
    for m in _AMOUNT_RE.finditer(text):
        raw = m.group(1) or m.group(2)
        v = _to_float(raw)
        if v is not None:
            out.append(v)
    return out


def untraceable(amounts: list[float], allowed: list[float], tolerance: float = TOLERANCE_EUR) -> list[float]:
    """Amounts not matched by any allowed amount within tolerance."""
    return [a for a in amounts if not any(abs(a - b) <= tolerance for b in allowed)]
