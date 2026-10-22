# Benchmark — 2026-10-22 12:53 UTC

Ground truth: `bench/cases/*.json` (items and amounts from research `08c` §6, pages from `08a`/`08b`). Every figure below was produced by `bench/run.py`.

## Case A — Karim — phone repair and resale, Marseille city centre
Contract: MAAF Multirisque Professionnelle 11031 (01/2026). Ground truth: 11 items, 89 700 €. Insurer first offer in the scenario: 20 750 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 38 100 € | 4/11 (36 %) | 0/0 | — | — | — | declared from memory, no contract read |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | — | — | — | — | — | — | not run — OPENAI_API_KEY missing (narrative extraction needs the model) |

## Case B — Boulangerie Martin — window blown in and fire start, Paris 10e
Contract: AXA Atouts PME (réf. 975637 I). Ground truth: 8 items, 57 900 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 20 900 € | 4/8 (50 %) | 0/0 | — | — | — | declared from memory, no contract read |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | — | — | — | — | — | — | not run — OPENAI_API_KEY missing (narrative extraction needs the model) |

## Case C — Optique Pauline — stock looted, Marseille
Contract: Generali 100% Pro (GA5M70F, 01/2022). Ground truth: 7 items, 127 200 €. Insurer first offer in the scenario: 25 000 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 135 100 € | 4/7 (57 %) | 0/0 | — | — | — | declared at retail price — exposure to forfeiture for false declaration |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | — | — | — | — | — | — | not run — OPENAI_API_KEY missing (narrative extraction needs the model) |
