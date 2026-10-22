# Benchmark — 2026-10-22 13:06 UTC

Ground truth: `bench/cases/*.json` (items and amounts from research `08c` §6, pages from `08a`/`08b`). Every figure below was produced by `bench/run.py`.

## Case A — Karim — phone repair and resale, Marseille city centre
Contract: MAAF Multirisque Professionnelle 11031 (01/2026). Ground truth: 11 items, 89 700 €. Insurer first offer in the scenario: 20 750 €.

| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |
|---|---|---|---|---|---|---|---|
| naive | 38 100 € | 4/11 (36 %) | 0/0 | — | — | — | declared from memory, no contract read |
| llm_only | — | — | — | — | — | — | not run — OPENAI_API_KEY missing |
| agent | 85 950 € | 10/11 (91 %) | 10/10 (100 %) | 0 | 0 | 290 ms | 10 items, 10 supported by evidence; deterministic pipeline only (no model key: narrative not structured) |

Item-level: precision 1.0, recall 0.909, F1 0.952; amount error on matched items (MAPE) 0.017; within ±10 %: 9/10. Missed: extra_operating_costs.

**Ablations** — what each data layer contributes (same inputs, one component removed):

| Pipeline | € | Recall | F1 | Citations | Untraceable | MAPE |
|---|---|---|---|---|---|---|
| full | 85 950 | 10/11 | 0.952 | 10/10 | 0 | 0.017 |
| no_coverage | 85 950 | 10/11 | 0.952 | 10/10 | 0 | 0.017 |
| no_recompute | 85 950 | 10/11 | 0.952 | 10/10 | 0 | 0.017 |
| no_evidence_items | 11 250 | 1/11 | 0.167 | 1/1 | 0 | 0.167 |
| no_bi | 74 700 | 10/11 | 0.952 | 10/10 | 0 | 0.0 |

Reading the ablations without a model key: `no_evidence_items` removes item creation from documents and the statement collapses to the formula-based BI line — the evidence layer is where the euros come from. `no_bi` removes the only computed item. `no_coverage` and `no_recompute` are identical to `full` here because cover matching also runs inside item creation and recomputation only acts on client-stated items, which the narrative step (model) produces; their contribution is measured when the model variant runs.

**Perturbations** — robustness checks with stated expectations:

| Perturbation | Expected | Observed | Result |
|---|---|---|---|
| duplicate invoice | flagged as duplicate; € unchanged | 1 duplicate(s); 85950 € vs 85950 € | PASS |
| endorsement: theft cap 15 000 → 30 000 € | the cap applied to the stock item follows the new schedule version | cap 15000.0 → 30000.0 €; status capped → capped | PASS |
| policy schedule missing (all covers unknown) | no item concluded 'not covered'; covers reported unknown | 0 item(s) wrongly concluded not covered; statuses ['unknown'] | PASS |
| qualifying words about the perpetrators | none in outbound insurer text | 0 hit(s) in 0 email(s) — not exercised: the bench path does not run the graph's outbound step; covered by the gate suite below | N/A |

**Deadlines** — 7 dated tasks, all sourced: True: police_report 2026-10-19; declaration 2026-11-16; loss_statement 2026-11-16; replacement_value_top_up 2028-09-16; prescription_alert 2028-07-18; prescription 2028-10-16; state_recourse 2030-10-02

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
| agent | 53 200 € | 7/8 (88 %) | 7/7 (100 %) | 0 | 0 | 60 ms | 7 items, 7 supported by evidence; deterministic pipeline only (no model key: narrative not structured) |

Item-level: precision 1.0, recall 0.875, F1 0.933; amount error on matched items (MAPE) 0.321; within ±10 %: 5/7. Missed: equipment.

**Ablations** — what each data layer contributes (same inputs, one component removed):

| Pipeline | € | Recall | F1 | Citations | Untraceable | MAPE |
|---|---|---|---|---|---|---|
| full | 53 200 | 7/8 | 0.933 | 7/7 | 0 | 0.321 |
| no_coverage | 53 200 | 7/8 | 0.933 | 7/7 | 0 | 0.321 |
| no_recompute | 53 200 | 7/8 | 0.933 | 7/7 | 0 | 0.321 |
| no_evidence_items | 18 900 | 1/8 | 0.222 | 1/1 | 0 | 0.199 |
| no_bi | 34 300 | 7/8 | 0.933 | 7/7 | 0 | 0.342 |

Reading the ablations without a model key: `no_evidence_items` removes item creation from documents and the statement collapses to the formula-based BI line — the evidence layer is where the euros come from. `no_bi` removes the only computed item. `no_coverage` and `no_recompute` are identical to `full` here because cover matching also runs inside item creation and recomputation only acts on client-stated items, which the narrative step (model) produces; their contribution is measured when the model variant runs.

**Perturbations** — robustness checks with stated expectations:

| Perturbation | Expected | Observed | Result |
|---|---|---|---|
| duplicate invoice | flagged as duplicate; € unchanged | 1 duplicate(s); 53200 € vs 53200 € | PASS |
| policy schedule missing (all covers unknown) | no item concluded 'not covered'; covers reported unknown | 0 item(s) wrongly concluded not covered; statuses ['unknown'] | PASS |
| qualifying words about the perpetrators | none in outbound insurer text | 0 hit(s) in 0 email(s) — not exercised: the bench path does not run the graph's outbound step; covered by the gate suite below | N/A |

**Deadlines** — 7 dated tasks, all sourced: True: police_report 2026-10-19; declaration 2026-11-16; loss_statement 2026-11-16; replacement_value_top_up 2028-09-16; prescription_alert 2028-07-18; prescription 2028-10-16; state_recourse 2030-10-02

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
| agent | 111 600 € | 6/7 (86 %) | 7/7 (100 %) | 0 | 0 | 64 ms | 7 items, 7 supported by evidence; deterministic pipeline only (no model key: narrative not structured) |

Item-level: precision 0.857, recall 0.857, F1 0.857; amount error on matched items (MAPE) 0.041; within ±10 %: 5/6. Missed: shopfront_glass. Spurious: shutter.

**Ablations** — what each data layer contributes (same inputs, one component removed):

| Pipeline | € | Recall | F1 | Citations | Untraceable | MAPE |
|---|---|---|---|---|---|---|
| full | 111 600 | 6/7 | 0.857 | 7/7 | 0 | 0.041 |
| no_coverage | 111 600 | 6/7 | 0.857 | 7/7 | 0 | 0.041 |
| no_recompute | 111 600 | 6/7 | 0.857 | 7/7 | 0 | 0.041 |
| no_evidence_items | 21 000 | 1/7 | 0.25 | 1/1 | 0 | 0.028 |
| no_bi | 90 600 | 6/7 | 0.857 | 7/7 | 0 | 0.043 |

Reading the ablations without a model key: `no_evidence_items` removes item creation from documents and the statement collapses to the formula-based BI line — the evidence layer is where the euros come from. `no_bi` removes the only computed item. `no_coverage` and `no_recompute` are identical to `full` here because cover matching also runs inside item creation and recomputation only acts on client-stated items, which the narrative step (model) produces; their contribution is measured when the model variant runs.

**Perturbations** — robustness checks with stated expectations:

| Perturbation | Expected | Observed | Result |
|---|---|---|---|
| duplicate invoice | flagged as duplicate; € unchanged | 1 duplicate(s); 111600 € vs 111600 € | PASS |
| endorsement: theft cap 20 000 → 40 000 € | the cap applied to the stock item follows the new schedule version | cap 20000.0 → 40000.0 €; status capped → capped | PASS |
| policy schedule missing (all covers unknown) | no item concluded 'not covered'; covers reported unknown | 0 item(s) wrongly concluded not covered; statuses ['unknown'] | PASS |
| client states 120 000 € (retail) | stock from invoices at purchase price, not the stated figure | stock = 54000.0 | PASS |
| qualifying words about the perpetrators | none in outbound insurer text | 0 hit(s) in 0 email(s) — not exercised: the bench path does not run the graph's outbound step; covered by the gate suite below | N/A |

**Deadlines** — 7 dated tasks, all sourced: True: police_report 2026-10-19; declaration 2026-11-16; loss_statement 2026-11-16; replacement_value_top_up 2028-09-16; prescription_alert 2028-07-18; prescription 2028-10-16; state_recourse 2030-10-02

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

## Review gate — adversarial suite

Drafts that must be blocked: 20/20 blocked (100 %). Legitimate factual drafts: 12/12 passed (false positives 0 %).

| Control | Blocked drafts |
|---|---|
| personalised_advice | 7 |
| promise_or_acceptance | 5 |
| untraceable_amount | 3 |
| banned_word | 5 |
| unconfirmed_fact | 1 |

## Method

Deterministic runs on a local PostgreSQL with the 12 public general conditions ingested (1 655 clauses). The agent column is the production pipeline minus the model step (narrative structuring) when no key is configured; it is labelled accordingly in each row. Ground-truth amounts are research assumptions (`08c` §6) and the three cases are composite and fictional. Citations are verified against the ingested clause text (whitespace-normalised similarity ≥ 0.9). Untraceable amounts use the same rule as the production review gate.
