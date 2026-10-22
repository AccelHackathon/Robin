# Benchmark — 2026-10-22 13:01 UTC

Ground truth: `bench/cases/*.json` (items and amounts from research `08c` §6, pages from `08a`/`08b`). Every figure below was produced by `bench/run.py`.

## Case A — Karim — phone repair and resale, Marseille city centre
Contract: MAAF Multirisque Professionnelle 11031 (01/2026). Ground truth: 11 items, 89 700 €. Insurer first offer in the scenario: 20 750 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 38 100 € | 4/11 (36 %) | 0/0 | — | — | — | declared from memory, no contract read |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | 85 950 € | 10/11 (91 %) | 10/10 (100 %) | 0 | 0 | 150 ms | 10 items, 10 supported by evidence; deterministic pipeline only (no model key: narrative not structured) |

<details><summary>Agent statement of loss</summary>

| Item | Key | Amount | Status | Page | Cover |
|---|---|---|---|---|---|
| Business interruption (loss of gross margin) | business_interruption | 11 250 | supported | 41 | covered |
| Customers' goods held in the shop | bailed_goods | 7 500 | supported | 22 | covered |
| Professional equipment | equipment | 4 500 | supported | 19 | covered |
| Spare parts and accessories | spare_parts | 6 000 | supported | 19 | covered |
| Stock (goods for resale) | stock | 39 600 | supported | 19 | capped |
| Cleaning and debris removal | debris_cleaning | 800 | supported | 24 | covered |
| Guarding and boarding-up | guarding_boarding | 1 200 | supported | 14 | covered |
| Metal shutter | shutter | 3 500 | supported | 14 | covered |
| Shop window and glazing | shopfront_glass | 3 600 | supported | 14 | covered |
| Tenant fit-out and furniture | tenant_fit_out | 8 000 | supported | 15 | covered |

</details>

## Case B — Boulangerie Martin — window blown in and fire start, Paris 10e
Contract: AXA Atouts PME (réf. 975637 I). Ground truth: 8 items, 57 900 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 20 900 € | 4/8 (50 %) | 0/0 | — | — | — | declared from memory, no contract read |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | 53 200 € | 7/8 (88 %) | 7/7 (100 %) | 0 | 0 | 79 ms | 7 items, 7 supported by evidence; deterministic pipeline only (no model key: narrative not structured) |

<details><summary>Agent statement of loss</summary>

| Item | Key | Amount | Status | Page | Cover |
|---|---|---|---|---|---|
| Business interruption (loss of gross margin) | business_interruption | 18 900 | supported | 27 | covered |
| Stock (goods for resale) | stock | 2 500 | supported | 6 | covered |
| Cleaning and debris removal | debris_cleaning | 5 000 | supported | 37 | covered |
| Extra operating costs | extra_operating_costs | 2 000 | supported | 27 | covered |
| Guarding and boarding-up | guarding_boarding | 900 | supported | 38 | covered |
| Shop window and glazing | shopfront_glass | 11 900 | supported | 20 | covered |
| Tenant fit-out and furniture | tenant_fit_out | 12 000 | supported | 35 | covered |

</details>

## Case C — Optique Pauline — stock looted, Marseille
Contract: Generali 100% Pro (GA5M70F, 01/2022). Ground truth: 7 items, 127 200 €. Insurer first offer in the scenario: 25 000 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 135 100 € | 4/7 (57 %) | 0/0 | — | — | — | declared at retail price — exposure to forfeiture for false declaration |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | 111 600 € | 6/7 (86 %) | 7/7 (100 %) | 0 | 0 | 75 ms | 7 items, 7 supported by evidence; deterministic pipeline only (no model key: narrative not structured) |

<details><summary>Agent statement of loss</summary>

| Item | Key | Amount | Status | Page | Cover |
|---|---|---|---|---|---|
| Business interruption (loss of gross margin) | business_interruption | 21 000 | supported | 28 | covered |
| Customers' goods held in the shop | bailed_goods | 9 000 | supported | 17 | covered |
| Professional equipment | equipment | 3 000 | supported | 17 | covered |
| Stock (goods for resale) | stock | 54 000 | supported | 17 | capped |
| Extra operating costs | extra_operating_costs | 2 500 | supported | 28 | covered |
| Metal shutter | shutter | 7 100 | supported | 20 | covered |
| Tenant fit-out and furniture | tenant_fit_out | 15 000 | supported | 12 | covered |

</details>
