"""The Claims Agent's brain: memory that is read back for reasoning.

- covers.py    loss item ↔ cover matching (cap, deductible, clause) — where the research becomes behaviour
- digest.py    running per-claim digest (narrative, open asks, insurer positions, next steps)
- positions.py insurer position ledger (verbatim, dated, attributed)
- profiles.py  cross-claim memory about insurers (delays, first-offer ratio, documents they ask for)
"""
