# PRD — Robin: autonomous claims-file agent for small businesses

| Field | Value |
|---|---|
| Status | Draft v1 — to be approved by the team |
| Priority | P0 |
| Date | 2026-10-22 |
| Horizons | **H0** = hackathon demo (today, 4 pm) · **H1** = first real users (4–8 weeks) · **H2** = launched product (3–6 months) |
| Consolidated sources | `PROJECT_CONTEXT_INSURANCE.md` §1–14 · `data/research/08a–08d` · `data/research/09a–09c` · corpus `data/contrats/txt/` (12 CG) |
| Reference in case of conflict | This PRD > `CONTEXTE` §14 > rest of `CONTEXTE` |

> **Guiding principle (Mathis's decision, 22/10)**: Robin is a **pure procedural layer**. It simplifies the process and does what the business owner should be doing themselves: declare, collect, transmit, follow up, document, explain factually. It **does not execute the payout**, **does not decide any amount**, **does not advise**. It removes friction. Everything that follows derives from this principle.

---

## 0. What does not exist yet (greenfield)

No product code in the repository. This PRD creates everything. External dependencies whose state is known at the time of writing:

- **Aiven**: project `larp`, PostgreSQL `pg-3f9bc500` being provisioned; Runtime available; **GitHub → Runtime link not done** (organisation admin required). Blocking for H0.
- **Telegram**: bot to be created via @BotFather (2 min). Non-blocking.
- **AgentMail**: free tier 3 mailboxes / 100 emails/day. Sufficient for H0, insufficient for H1.
- **ElevenLabs**: Builders Pack credits to be confirmed; Twilio trial for a verified number. Can degrade to a web widget.
- **Claude**: API key to be stored as a Runtime secret.

---

## 1. Problem, target, success

### 1.1. Problem

After a loss event, a small French business owner has 2 business days to declare, file a *plainte* (police complaint), put up a *clôture provisoire* (temporary boarding-up), then build an *état des pertes* (statement of loss) by reading 70 to 120 pages of *conditions générales / CG* (general conditions) they have never opened. They don't know what is claimable: each contract contains **10 to 20 ancillary items** (*gardiennage* (security guarding), debris removal, fees, loss of use, graffiti, locks, *rachat de vétusté* (depreciation buy-back), *pertes indirectes* (indirect losses) 10 %) that nobody points out to them (`08b` §5). They declare from memory, forget *perte d'exploitation / PE* (business interruption) (only 53 % of business owners know about it, `08c` §1.2), value their stock at retail price and expose themselves to total *déchéance* (forfeiture) for misrepresentation (Cass. 2e civ., 12/02/2026, `09a` §5). Then they wait: there is **no statutory settlement deadline** for MRP policies (`08d` §1, LMA 2023), nobody follows up, and they sign the first *quittance* (release).

Documented outcome: a tobacconist with €200,000 of damage received €55,000 in 2023 (`08c` §1.2); *experts d'assuré* (policyholder's loss assessors) claim +15 to +40 % over the initial offer (`08c` §3); ~40 % of UK property claims are adjusted downward for underinsurance (Aviva, `09a` §1). Refusals come "as a shock" because the policyholder was unaware of their policy's conditions (FCA, `09b` §6).

### 1.2. Why now

- **17–18 October 2026**: ~3,000 shops damaged, €1–1.2 bn in insured losses, 70 % small business owners; declaration deadline extended to 30 days by France Assureurs (`08c` §0). Window of action open until mid-November.
- **No public safety net**: the mandatory riot cover (LFI 2026, art. 171) has been voted but is **not in force** (`08c` §5).
- **Category validated in the US**: Finch ($4.5M, 09/2026, Aglaé Ventures on the cap table), Tugboat ($3M, 06/2026). **No policyholder-side AI tool in France or Europe** (`08d` §4).
- Accel/Aiven hackathon today: Runtime deployment required, measured proof required.

### 1.3. Who

| Persona | Pain | What Robin removes |
|---|---|---|
| **Small retail business owner** (H0/H1 target: looted shopkeeper, 17/10) | No time, no skills, panic; declares late and incomplete | Day-0 declaration, guided collection, complete and cited statement of loss, follow-ups |
| Small business owner, routine loss (H2: 110 claims / 1,000 contracts / year) | Broken shopfront, water damage, simple theft; "small" but time-consuming file | Same pipeline; value = time |
| The business owner's accountant (H1 channel) | Asked for PE figures with no framework | Receives a structured document request (N-1/N-2 tax returns, monthly revenue) |
| Hackathon jury (H0) | Wants to see data that changes decisions | Duplicate refused, endorsement that changes a ceiling, resume after restart, unconfirmed oral answer |

### 1.4. Success metrics

| Metric | Baseline (naive) | Target | Method |
|---|---|---|---|
| **Recall of claimable items** (correct clause + page) | Naive declaration: 3–5 items / case | ≥ 90 % of ground-truth items `08c` §6 | `bench/` on cases A/B/C × contract |
| **Correct citations** (page exists and says what is asserted) | LLM alone: invented citations | ≥ 95 % | Automatic page/text check + proofreading |
| **€ identified** | A: €38,100 / B: €20,900 / C: inflated €135,100 | A: ≈ €89,700 / B: ≈ €57,900 / C: ≈ €127,200 **without a single unsourced amount** | `bench/` 3 variants |
| **Untraceable amounts emitted by the agent** | — | **0** | Review node, test AC-12 |
| **Missed deadlines** on a simulated 24-month file | — | 0 | Deadline-engine test |
| **Duplicates counted** | — | 0 | AC-5 |
| **Cost / file** (tokens) and latency per event | — | measured, displayed | `actions` logs |
| H1: business owner time per file | not measured | measured on 5 real files | Action log |
| H1: satisfaction / NPS of first 5 customers | — | collected | Interview |

---

## 2. Features

Complex sub-features follow the 7-part format (goal, sources, steps, prompt, schema, failure mode, consumers).

### 2.1. Web onboarding (Block 1)

**Goal**: create the durable identity, the profile, the *mandat* (mandate) and the initial memory, then link Telegram.

**Steps** (`CONTEXTE` §3, §14.7):
1. Account (email + password); resume of an interrupted onboarding.
2. Business: name, SIRET, address, manager, phone, insurer, broker, tenant/owner status, VAT registration (impacts net/gross valuation — MAAF p. 80).
3. Upload: CG, *conditions particulières / CP* (policy schedule), endorsements, IPID, reports, correspondence. Originals retained.
4. **Mandate + separate consents** (3 distinct checkboxes: representation mandate, Telegram channel, data processing). Version, scope, signatory, capacity, timestamp, proof. The mandate covers: obtaining documents, transmitting confirmed facts and supporting documents, contacting insurer/broker/adjuster, requesting a status, following up. It **excludes**: accepting an offer, settling, waiving, collecting funds.
5. Trigger the Intake Agent → coverage profile displayed with pages.
6. Telegram deep link → `/start` links the `chat_id` to the account → welcome message in English with a contract summary.

**Rules**: an account can be created with an incomplete profile; **an urgent loss must never wait for onboarding to finish** (open the file, declare, complete later). Distinct statuses: account created / partial profile / mandate recorded / Telegram linked / welcome sent-delivered-failed.

**Failure mode**: Telegram send failure → account remains created, site offers "resume", no false success.

### 2.2. Intake Agent — coverage profile

**Goal**: turn the client's PDFs into structured memory, clause by clause, with page and confidence.

**Sources**: uploaded documents; `data/contrats/txt/` corpus to pre-fill if the CG is recognised (hash / publisher reference, e.g. "11031 - 01/26" MAAF).

**Steps**:
1. Classify each document: `general_conditions | policy_schedule | endorsement | ipid | report | police_complaint | correspondence | invoice | other`, with document date and validity period.
2. Split into paginated clauses (`\f` from `pdftotext -layout`), index as `tsvector` (`french` dictionary).
3. Extract the **coverage profile**: for each candidate guarantee (fire-vandalism, riots, theft, glass breakage, PE, goods in custody, ancillary costs…) → `subscribed: yes|no|unknown`, ceiling, *franchise* (deductible), conditions (required protections, prior approval), notable exclusions, source `clause_id`, confidence.
4. Extract the contract's **deadline engine** (see 2.5): declaration deadline theft / other, complaint deadline (24 h Generali/Allianz, 48 h AXA, « au plus vite » MAAF), statement of loss (30 days MMA), depreciation buy-back (2 years), payment after agreement (30 days).
5. Extract the **contractual levers**: waiver of the *règle proportionnelle* (underinsurance averaging) (yes at Generali p. 54, AXA p. 55, Allianz p. 57, MAAF p. 78, MMA p. 85, Hiscox p. 32), assessor fees cover (MMA 10 % max €40k; Generali 5 %; Hiscox 5 %; **absent** MAAF, AXA Mon Pack), single deductible when guarantees are combined (MAAF p. 80, Generali p. 54), indirect losses 10 %, PE advances (Generali p. 52), 50 % advance (Allianz p. 61).
6. Detect **contractual traps** (`09a`, `08a` §traps): theft excluded during riots (Sogessur p. 19), theft excluded from riot cover → split (AXA p. 7), PE for denial of access excluded (AXA p. 29, MAAF p. 43), assistance excluded during riots (Generali p. 60), repairs without written approval prohibited (Generali p. 45), stock capped at €3,000 when the policy schedule (DP) is silent (Allianz p. 66).
7. List **missing documents** as tasks (CP absent → "Could you upload the policy schedule showing your selected cover?"). **Never infer that an option is not subscribed because its page is missing.**

**Prompt (extraction, per candidate clause)**:
```
You are extracting insurance coverage facts from a French commercial property policy.
Document: {doc_type} "{doc_title}", page {page}.
Clause text (verbatim, French): """{clause_text}"""
Task: for the guarantee "{guarantee_name}", return ONLY what this clause states. Do not infer
from other pages. If the clause does not address the field, return null.
Return JSON matching the schema. Keep `quote` as an exact short verbatim excerpt (≤ 200 chars).
```

**Output schema**:
```json
{
  "guarantee": "string — canonical key, e.g. theft, riot, glass, business_interruption",
  "subscribed": "yes | no | unknown",
  "ceiling": {"amount": "number|null", "unit": "EUR|percent_of_content|days", "basis": "string|null"},
  "deductible": {"amount": "number|null", "unit": "EUR|days|percent"},
  "conditions": ["string"],
  "exclusions": ["string"],
  "quote": "string — verbatim excerpt",
  "clause_id": "uuid",
  "page": "int",
  "confidence": "high | medium | low"
}
```

**Failure mode**: unreadable OCR → document flagged `unreadable`, task "please re-upload page X"; `low` confidence extraction → field shown with a "to confirm" badge, never used in a message to the insurer without the business owner's confirmation.

**Consumers**: Claims Agent (`load_memory`, `analyze`), deadline engine, coverage-profile UI, benchmark (ground truth = `08a/08b`).

### 2.3. Claims Agent — main loop (Block 2)

**Goal**: one LangGraph thread per file that moves the claim forward from declaration to offer presentation, autonomously, and only hands back control at defined moments.

**Nodes** (aligned with `CONTEXTE` §14.3, enriched):

| Node | Role | Enrichment from research |
|---|---|---|
| `load_memory` | Loads business, coverage profile, file, facts, evidence, statement of loss, actions, communications, deadlines | — |
| `triage` | Qualifies the inbound event; decides reply / update / act / wait | **Day-0 urgency**: if new loss → immediately trigger `declare_initial` without waiting for documents (L113-2; 2 business days for theft) |
| `analyze` | Updates facts + statement of loss (item = evidence + clause + computation + condition); deduplicates; flags contradictions and gaps | **Split** by guarantee (theft vs damage vs PE); **factual qualification** of the event without banned words; underinsurance and derogatory-clause detection; **causal chain** material damage → PE |
| `act` | Executes the tools | — |
| `review` | Check before any send | See 2.7 — **legal + evidence + figures gate** |
| `wait` | Typed `interrupt()` | `awaiting_client`, `awaiting_insurer_email`, `awaiting_call_result`, `awaiting_followup`, `awaiting_signature_decision` |
| `present_offer` | End of loop | Item-by-item quantified comparison, **release/settlement detection**, business owner's decision |

**Tools** (`@tool`, each writes to `actions`):
`get_claim_memory`, `search_clauses(contract_id, query)`, `read_document(doc_id)`, `update_loss_statement(items)`, `ask_client(text, requested_items)`, `send_email(to, subject, body, attachment_ids)`, `start_call(goal, questions)`, `schedule_followup(when, reason)`, `log_fact(fact, source, confidence)`, `register_deadline(kind, due_at, source_clause_id)`, `present_offer(offer_id)`, `request_insurer_document(kind)` (signed CG/CP + proof of delivery, adjuster's report — `08c` §4.7).

**Operational journey** (`CONTEXTE` §4) enriched:
1. Identify the loss and the urgencies; **Day-0 checklist** generated from the contract: police complaint (contractual deadline), temporary boarding-up (MAAF obligation p. 14/18 — and billable €6,600), photos before works, no repairs without written approval except protective measures.
2. **Initial declaration by email on Day 0** with confirmed facts only; acknowledgement retained.
3. Read the contract set as at the loss date (applicable endorsement) → candidate guarantees.
4. Build the living statement of loss; systematic **"subject to further additions"** (`09b` §5).
5. Request missing documents (client / accountant for PE: N-1, N-2 tax returns, monthly revenue, variable costs); email/call to the insurer for a specific question.
6. Transmit additions; follow the loss adjustment (2.8).
7. Present the offer (2.9).
8. Track advances, payment, **replacement-as-new top-up at 2 years**, and the **recours État** (State liability claim) in parallel (2.10).

### 2.4. Living statement of loss

**Goal**: the core of the product. Each item links damage → evidence → clause (page) → computation → condition → status.

**Item catalogue** (extracted from `08b` §5 and `08c` §3.2 — the agent walks this catalogue for each file and checks applicability to the contract):
stock (current purchase price + non-recoverable transport/handling/taxes), parts/accessories, **goods in custody** (customers' devices), shopfront (no depreciation at AXA p. 56) + window graphics/lettering, roller shutter, sign/awning/canopy, locks (MAAF €3,000), tenant's fixtures and fittings, equipment (*valeur à neuf* (replacement-as-new) if < 2/3/5 years depending on contract), **security guarding/boarding-up** (MAAF €6,600, Generali €14,000), debris removal/cleaning/decontamination, **graffiti**, cash (MAAF 10 % of contents max €16,000), records reconstitution, storage/removal, relocation/temporary premises, architect/designer fees, compliance upgrades, **indirect losses 10 %**, **PE (*marge brute* (gross margin), period, deductible in days, advances)**, additional operating costs (prior approval), seals extending the PE (AXA p. 28), loss of goodwill value, outstanding lease payments, policyholder's loss assessor fees (if covered), **deferred depreciation buy-back**, **residual claimable from the State**.

**Computation rules**: net of VAT if VAT-registered; a single deductible if a "single deductible" clause exists; *vétusté* (depreciation) per the contractual formula (never invented); PE = revenue loss × gross margin rate − saved costs + additional costs, with N-1 and N-2 (TJ Saint-Étienne 2025: a drop that follows the prior trend is rejected); **public aid of a different nature not deductible** from PE (TAE Marseille 29/01/2026) but short-time work compensation is deductible.

**`loss_items` schema**: see §3.4.

**Failure mode**: item without evidence → `status = unsupported`, excluded from any send, collection task; item without clause → `status = no_cover_found`, visible to the business owner, candidate for the State liability claim.

### 2.5. Deadline engine

**Goal**: zero missed deadlines. All dates are persisted tasks (`scheduled_tasks`) derived from the contract or the law, with the source clause.

| Deadline | Source | Behaviour |
|---|---|---|
| Police complaint | 24 h (Generali p. 45, Allianz p. 56) / 48 h (AXA p. 54) / « au plus vite » (MAAF p. 76) | Day-0 task, client reminder |
| Theft/vandalism declaration | 2 business days (L113-2; all contracts); **30 days** for 17/10 (France Assureurs) | Declaration sent on Day 0 no matter what |
| Other declaration | 5 business days | same |
| Statement of loss | 30 days (MMA p. 81), "as soon as possible" (MAAF) | Internal follow-up; send "subject to additions" |
| Aggravation of risk | 15 days by *LRAR* (registered letter) (L113-2 3°) | Triggered by a detected change of activity |
| Reply to the insurer | Each insurer request logged with due date on the day of receipt | Client reminder D-2 |
| Insurer follow-up | Set when each request is sent (D+7 by default) | follow-up → LRAR → complaint → mediation (if eligible) |
| Complaint → mediation | 2 months without reply | Factual information to the business owner |
| Payment after agreement | 30 days (Generali p. 54, MMA p. 92) | Follow-up |
| **Depreciation buy-back** | 2 years (all) | Task D+700, replacement invoices |
| Insurer *prescription* (limitation period) | 2 years (L114-1); interrupted by LRAR about settlement / adjuster appointment (L114-2) | Alert D-90; check the contract restates it (R112-1) otherwise unenforceable |
| **State liability claim** | 4 years → **31/12/2030** for 17/10 (L211-10 CSI, prior application to the prefect R421-1 CJA) | Long-term task |

**Failure mode**: if a deadline has passed → mark `missed`, inform factually ("the contractual deadline for X was DATE; late declaration can only be opposed if the insurer proves prejudice — L113-2"), continue.

### 2.6. Evidence discipline and provenance

- Each `fact` carries `source` (document / client / insurer oral / insurer email), `confidence`, `status` (`confirmed | to_confirm | contradicted`), `supersedes`.
- **Oral answer ≠ contract**: a call answer is stored as `source=oral, status=to_confirm` and triggers a request for written confirmation; it never modifies the coverage profile.
- **Duplicates**: file hash + (amount, date, supplier) → `duplicate_of`; the agent tells the business owner.
- **Correction**: new version, never overwrite.
- **Evidence preservation**: Day-0 reminder "photos before works; keep all invoices" (LMA 2020 case 1.11: works before loss adjustment lead to cover being refused).

### 2.7. Review node — the gate before any send

**Goal**: nothing goes out without passing these checks. This protects the business owner **and** legally protects the service (`09c`).

| Check | Rule | Failure → |
|---|---|---|
| Evidence | each item sent has ≥ 1 `evidence` and 1 existing `clause_id` | back to `analyze` |
| Citation | the cited page contains the asserted text (verbatim match of `quote`) | back to `analyze` |
| Duplicate | no `evidence.duplicate_of` counted | back to `analyze` |
| **Traceable amount** | **every € emitted comes from an `evidence` or an explicit instruction from the business owner (`facts.source = client_instruction`)** — never from the agent | blocked |
| **No promise / acceptance** | regex + LLM: no "we accept", "agreed", "waive", "final" | blocked |
| **No personalised legal advice** | no "you should", "we recommend accepting/refusing", "your chances", "legally insufficient"; allowed: factual findings, citations, quantified gaps, statement of generic avenues | rewrite |
| **Banned words** (State liability claim, `08c` §4.3) | « organisé(s) », « bande », « venus exprès », « casseurs », « émeutiers », « prémédité » (French terms to detect) in any text to insurer / complaint / prefect | rewrite as facts (time, place, number, link to the march) |
| Unconfirmed fact | no `fact.status != confirmed` in an external send | removal or question to the client |
| Language | English to the business owner; **French to a French insurer** (decision pending, cf. Q4) | — |

**Prompt (review)**:
```
You are the compliance reviewer for outbound messages of a claims-handling assistant in France.
The assistant is a PURE PROCEDURAL LAYER: it transmits documented facts and amounts, cites policy
clauses, asks for documents, follows up. It must NEVER: state an amount not present in the evidence
list; accept, agree, waive or settle anything; give personalised legal advice or recommendations;
use the words {banned_words} when describing the event.
Message: """{draft}"""
Evidence amounts: {evidence_amounts}
Client instructions: {client_instructions}
Return JSON: {"pass": bool, "violations": [{"type": "...", "span": "...", "fix": "..."}], "rewrite": "string|null"}
```

### 2.8. Loss adjustment handling

- Request in writing: the insurer's adjuster report, **signed** CG/CP + proof of delivery before accepting an exclusion (`08c` §4.7).
- Before the visit: hand the adjuster the written file (statement of loss, indexed photos, invoices) — traceable; afterwards: send written observations immediately (no countersignature required by law, `09b` §3).
- Extract from the contract the existence and ceiling of the "assessor fees" cover and **display it factually** to the business owner ("your policy covers an assessor of your choice up to 10 % / 40 000 € — MMA p. 69"); the decision to appoint a policyholder's loss assessor is theirs. Robin does not recommend, it informs.
- Appointing an adjuster interrupts the limitation period → record the date.

### 2.9. Offer presentation and signature gate

**Goal**: the business owner decides with full knowledge; Robin compares and explains, does not recommend.

**Steps**:
1. Item-by-item reconciliation: `covered | partial | refused | absent`; parameters applied (depreciation vs contractual formula, ceiling, deductible — single?, underinsurance averaging — waived in the contract?).
2. Nature: advance / provisional / final; document attached?
3. **Detection** in any insurer document: « quittance », « solde de tout compte », « renonciation », « transaction », « définitif », « pour solde » → `awaiting_signature_decision` with a factual explanation of the effect ("this document extinguishes further claims on this loss — art. 2052 C. civ.; there is no 15-day withdrawal for property claims").
4. Feedback: "The offer covers X € of the Y € documented in your loss statement (Z %). Not covered: [items]. Applied: 30 % depreciation on shutter (policy formula: p. 79); theft ceiling 15 000 € applied to stock (your schedule shows a riot extension — p. CP). You can: accept, ask for details, contest." Then a list of generic avenues (written complaint, mediation if eligible, policyholder's loss assessor, lawyer) **without weighting**.
5. Business owner's decision → `accept` (payment + depreciation tracking) / `contest` (they indicate the items and the figure; Robin transmits) / `ask`.

**Absolute rule**: no reply ≠ acceptance.

### 2.10. "State liability claim" module (L211-10 CSI) — H1

**Goal**: the residual not paid by the insurer (deductible, depreciation, ceilings, uncovered PE) is claimable from the State for damage caused by *attroupements* (unlawful assemblies) — an item **almost always forgotten** (`08c` §3.2 no. 9).

- Triggered if the loss is dated to a known unlawful-assembly event (`riot_events` table: 17–18/10/2026…).
- Builds the **quantified prior application to the prefect** (R421-1 CJA) with the same statement of loss, the insurer's settlement breakdown, and a timestamped factual description **without banned words**.
- Tracks the four-year limitation period (31/12/2030).
- Failure mode: if the facts described by the client contain "organised / equipped" → Robin rephrases as raw facts and asks for confirmation; never qualifies.

### 2.11. Insurer Simulator Agent (H0)

Separate graph, dedicated AgentMail mailbox, **labelled "simulated insurer"** in the UI and the pitch. Script parameterisable per scenario: acknowledgement → document request (police complaint, number of customer devices) → capped offer (≈ €20,750 for Karim) → late follow-up → **full and final settlement release** attached to the offer (to trigger the signature gate in the demo). Never sees the Claims Agent's memory.

### 2.12. Benchmark (H0, proof slide)

`bench/` script on cases A/B/C from `08c` §6 × contract (A: MAAF 11031 + synthetic CP; B/C: to be assigned — AXA Atouts PME, Generali 100% Pro). Three variants: naive declaration, LLM alone (same model, same narrative, no clauses or invoices), Claims Agent. Measures: € identified, item recall, % correct citations, untraceable amounts (must be 0), token cost, latency. Ground truth: `08a/08b` (clauses + pages), `08c` §6 (items). **No figure displayed before it has been measured.** Timed manual effort is removed from the H0 benchmark (not honestly feasible in one day).

### 2.13. User workflows

**W1 — New loss (Karim)**
1. Telegram: "My shop was looted Saturday night" + 3 photos + 2 invoices.
2. `triage` → new file → Day-0 checklist (complaint, boarding-up, photos before works) → **initial declaration sent on Day 0** → acknowledgement.
3. `analyze`: facts extracted (vision), initial items, candidate guarantees (riots included MAAF p. 15; theft/vandalism = option → CP), missing documents → `ask_client`.
4a. Karim re-sends an invoice already sent → duplicate detected, stated.
4b. Karim sends the inventory → items updated, statement of loss transmitted "subject to further additions".
5. Simulated insurer requests the police complaint → relayed → received → transmitted.
6. ElevenLabs call: "Does the riot extension apply to stock, or the €15 000 theft cap?" → oral answer `to_confirm` → written confirmation email requested.
7. Offer ≈ €20,750 + release → `present_offer` → signature gate → Karim decides.
8. If `contest`: Karim indicates items and figures; Robin transmits the quantified, sourced contestation. If `accept`: 30-day payment tracking, depreciation task D+700, State module.

**W2 — Resume after restart**: service restarted during the demo → thread resumed from the checkpointer → same state, same tasks.

**W3 — Endorsement added**: new CP with theft ceiling €30,000 → Intake re-runs → versioned profile → `analyze` recomputes → delta visible.

### 2.14. Edge cases

| # | Case | Behaviour |
|---|---|---|
| 1 | CP absent | Guarantees `unknown`, never `no`; upload task; `request_insurer_document(CP)` |
| 2 | Loss during waiting period | Detected from CP; stated factually; pivot to alternative remedies |
| 3 | Unpaid premium / suspension L113-3 | Day-0 question + certificate request; no send while unknown |
| 4 | Client declares stock at retail price | Robin resets to purchase price **with the clause** (MAAF p. 79) and explains the factual risk (forfeiture for misrepresentation); does not send the inflated figure |
| 5 | Client writes "organised looters" | Factual rephrasing proposed; confirmation before sending |
| 6 | Invoice / inventory contradiction | Both facts `contradicted`; targeted question; neither is sent |
| 7 | Oral answer contradicts the contract | Stored `to_confirm`; profile unchanged; written confirmation requested |
| 8 | Two contracts on the same risk | L121-4: cross-declaration; allocation per item; total ≤ damage |
| 9 | Tenant + fire | Art. 1733 C. civ.: document the external origin (timestamps, video); two streams (landlord / MRP) |
| 10 | Insurer silent for 60 days | follow-up → LRAR (interrupts limitation period) → complaint → mediation info |
| 11 | Business owner does not respond to the offer | Reminder D+3, D+7; never implicit acceptance |
| 12 | Insurer document contains « solde de tout compte » hidden in a "settlement acknowledgement" | Detection → signature gate |
| 13 | Out-of-scope message ("should I sue?") | Documentary reply: existing avenues, no advice; referral to lawyer/policyholder's loss assessor as an option |
| 14 | Mandate revoked | All tasks suspended; no send; file exportable |

### 2.15. Out of scope

- **NO recommendation** to accept/refuse, no assessment of "chances", no negotiation in its own name (Cass. 2e civ. 9/12/2015; CA Nîmes 7/07/2023; Cass. 2e civ. 7/05/2025 — `09c` §1.2, `08d` §3).
- **NO collection** of funds; the insurer pays the business owner.
- **NO sale or recommendation of contracts** (ORIAS trigger, L511-1).
- NO access to insurers' customer portals (not technically verified, `CONTEXTE` §2).
- NO WhatsApp in H0 (Telegram); WhatsApp in H1 after Meta validation.
- NO field canvassing ("vulture" risk, Gironde prefecture 2023).
- NO hidden human team; professionals (policyholder's loss assessor, lawyer) are **presented as options** to the business owner, never engaged behind the scenes.

---

## 3. Architecture

### 3.1. Overview

```mermaid
graph TD
  subgraph Client["Business owner"]
    W[Onboarding site] 
    T[Telegram]
  end
  subgraph Runtime["Aiven Runtime — single FastAPI service"]
    API[HTTP: site + webhooks]
    EV[(events queue PG)]
    WK[Worker asyncio]
    IA[Intake Agent]
    CA[Claims Agent<br/>1 thread / claim]
    RV[Review node]
    SIM[Insurer Simulator<br/>'simulated insurer']
  end
  PG[(Aiven PostgreSQL<br/>durable memory + checkpointer)]
  AM[AgentMail]
  EL[ElevenLabs Agents]
  CL[Claude text+vision]
  W --> API --> IA --> PG
  T --> API --> EV --> WK --> CA
  AM --> API
  EL --> API
  CA <--> PG
  CA --> RV --> AM
  CA --> RV --> T
  CA --> EL
  IA --> CL
  CA --> CL
  AM --> SIM --> AM
```

### 3.2. Components

| Component | Responsibility | H0 | H1+ |
|---|---|---|---|
| `app/web` | 6-step onboarding, mandate, consents, coverage profile, tracking page via link | Minimal (can be 1 page) | Complete |
| `app/channels/telegram` | Long polling dev / webhook prod; media via `getFile`; voice notes → transcription | Yes | + WhatsApp |
| `app/channels/email` | AgentMail: 1 mailbox / account; inbound webhook → `events` | Yes | Own domain, volume |
| `app/channels/voice` | ElevenLabs: outbound call, dynamic variables, post-call webhook | Degradable to widget | Twilio prod |
| `app/agents/intake` | 2.2 | Yes | — |
| `app/agents/claims` | 2.3–2.9 | Core | + 2.10 |
| `app/agents/review` | 2.7 | Yes | + continuous eval |
| `app/agents/insurer_sim` | 2.11 | Yes | Removed in real prod |
| `app/deadlines` | 2.5 scheduler | Yes | — |
| `app/ingestion` | pdftotext → clauses → tsvector | Yes | pgvector if useful |
| `bench/` | 2.12 | Yes | Nightly CI |
| `migrations/` | Alembic at startup | Yes | — |

### 3.3. Technical decisions

| Decision | Options | Choice | Why |
|---|---|---|---|
| Channel | WhatsApp Cloud / Telegram | **Telegram** (H0) | Immediate token, no 24 h window; WhatsApp H1 |
| Agent framework | Generic ReAct / explicit LangGraph | **LangGraph** | PG checkpointer, native `interrupt()` for long waits |
| Topology | 1 service / 2 services | **1 service** | 1 Dockerfile, all state in the database |
| Clause search | tsvector / pgvector | **tsvector `french`** | 12 contracts; pgvector optional |
| LLM | Claude | **Claude** | Vision for invoices/police reports; structured outputs |
| Document storage | bytea / object | **bytea** H0 | Prototype; S3-compatible object storage H1 |
| Bot language | EN / FR | **EN to business owner** (Mathis's decision); **FR to insurer** to be decided (Q4) | English-speaking jury; real French insurer |
| Mandate signature | checkbox + name + timestamp / eIDAS | **checkbox + timestamp** H0; eIDAS H1 | — |
| Human in the loop | yes / no | **No** (Mathis's decision); professionals = presented options | Autonomy + legal scope |

### 3.4. Data model (Aiven PostgreSQL)

All tables: `id uuid pk`, `account_id uuid not null` (isolation), `created_at timestamptz default now()`.

```sql
-- Identity & mandate
create table accounts (email text unique not null, password_hash text not null);
create table businesses (name text, siret text, address text, manager_name text, phone text,
  insurer text, broker text, tenant_or_owner text check (tenant_or_owner in ('tenant','owner','unknown')),
  vat_registered boolean);                                   -- null = unknown (3 states)
create table mandates (version int, scope jsonb, signer_name text, signer_role text,
  accepted_at timestamptz, proof jsonb, revoked_at timestamptz);
create table consents (kind text check (kind in ('mandate','channel','data')), accepted_at timestamptz, version text);
create table mailboxes (address text unique, provider_id text, role text check (role in ('agent','simulated_insurer')));
create table telegram_links (chat_id bigint unique, state text, linked_at timestamptz);
create table link_codes (code text unique, expires_at timestamptz, used_at timestamptz);

-- Documents & contract
create table documents (doc_type text, origin text, version text, doc_date date, valid_from date, valid_to date,
  sha256 text, content bytea, extracted_text text, readable boolean);
create table clauses (document_id uuid references documents, page int, title text, body text,
  tsv tsvector generated always as (to_tsvector('french', coalesce(title,'')||' '||body)) stored);
create index clauses_tsv on clauses using gin(tsv);
create table coverage_profile (version int, guarantee text, subscribed text check (subscribed in ('yes','no','unknown')),
  ceiling jsonb, deductible jsonb, conditions jsonb, exclusions jsonb, quote text,
  clause_id uuid references clauses, page int, confidence text, supersedes uuid);
create table contract_levers (kind text, present boolean, detail jsonb, clause_id uuid references clauses);
  -- kind: no_proportional_rule | assessor_fees | single_deductible | indirect_losses_10pct | bi_advances | traps.*

-- Claim
create table claims (status text, loss_date timestamptz, nature text, summary text, riot_event_id uuid);
create table facts (claim_id uuid references claims, text text, source text
  check (source in ('document','client','client_instruction','insurer_email','insurer_oral','agent_inference')),
  confidence text, status text check (status in ('confirmed','to_confirm','contradicted','superseded')), supersedes uuid);
create table evidence (claim_id uuid, document_id uuid references documents, kind text, amount numeric, currency text default 'EUR',
  evidence_date date, supplier text, sha256 text, duplicate_of uuid references evidence);
create table loss_items (claim_id uuid, category text, label text, amount_claimed numeric, amount_basis text,
  evidence_ids uuid[], clause_id uuid references clauses, computation jsonb, condition text,
  status text check (status in ('supported','unsupported','no_cover_found','sent','accepted','refused','partial')),
  version int, supersedes uuid);
create table communications (claim_id uuid, channel text, direction text, counterpart text, subject text, body text,
  attachments uuid[], provider_message_id text, delivered boolean, failed_reason text, insurer_position_verbatim text);
create table calls (claim_id uuid, goal text, questions jsonb, transcript text, structured_result jsonb, confidence text);
create table actions (claim_id uuid, tool text, args jsonb, result jsonb, trigger_event_id uuid, tokens_in int, tokens_out int, latency_ms int);
create table scheduled_tasks (claim_id uuid, kind text, due_at timestamptz, reason text, source_clause_id uuid,
  state text check (state in ('pending','done','missed','cancelled')));
create table offers (claim_id uuid, received_at timestamptz, items jsonb, total numeric, nature text
  check (nature in ('advance','provisional','final')), has_release_language boolean, release_terms text,
  comparison jsonb, client_decision text check (client_decision in ('accept','contest','ask')), decided_at timestamptz);
create table payments (claim_id uuid, offer_id uuid, amount numeric, received_at timestamptz, kind text);
create table riot_events (name text, started_at timestamptz, ended_at timestamptz, cities text[], state_claim_deadline date);

-- Event queue & review
create table events (source text, payload jsonb, state text check (state in ('pending','processing','done','failed')),
  claim_id uuid, attempts int default 0);
create table review_log (claim_id uuid, draft text, passed boolean, violations jsonb, rewrite text);
-- + LangGraph checkpointer tables (created by the library)
```

### 3.5. Event flow

```
Telegram update ─┐
AgentMail webhook ┼─> INSERT events (pending) ─> worker: SELECT … FOR UPDATE SKIP LOCKED
ElevenLabs post-call ┤                                 ├─ thread waiting? → Command(resume=payload)
scheduler (deadlines) ┘                                └─ otherwise → new run
Webhook replies < 1 s. Action marked done only on an observed result (message_id, acknowledgement, call ended).
```

---

## 4. Dependencies

| Service / package | Usage | Risk | Fallback |
|---|---|---|---|
| Aiven Runtime + PG | Hosting, state | **GitHub link = blocking for H0** (org admin) | Identify the admin now; deploy a hello world by 1 pm |
| `langgraph`, `langgraph-checkpoint-postgres`, `langchain-anthropic` | Agents | Cross-thread Store version to verify | Direct table reads |
| `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `psycopg[binary]` | App | Low | — |
| `python-telegram-bot` | Channel | Low | — |
| AgentMail API | Email | 3 free mailboxes | 1 Karim + 1 simulator + 1 spare |
| ElevenLabs Agents + Twilio trial | Calls | Credits / verified number | Projected web widget |
| Anthropic API | LLM + vision | Cost / latency | Extraction cache by sha256 |
| `pdftotext` (poppler) | Ingestion | In the Docker image | — |
| ElevenLabs Scribe / Whisper | Telegram voice notes | Optional H0 | Skipped (step 9) |

Order: Aiven skeleton → ingestion → minimal Claims Agent → Telegram → benchmark → AgentMail + simulator → site → voice → voice notes (`CONTEXTE` §14.10; 1–5 non-negotiable).

---

## 5. Interface contracts

```python
# Normalised event (all sources)
class InboundEvent(TypedDict):
    source: Literal["telegram","agentmail","elevenlabs","scheduler","web"]
    account_id: str; claim_id: str | None
    kind: Literal["message","document","email","call_result","deadline","onboarding_done"]
    payload: dict; received_at: datetime

# Resuming a waiting thread
Command(resume={"wait_type": "awaiting_client", "event": InboundEvent})

# Tool signatures (each call → one `actions` row)
def search_clauses(contract_id: str, query: str, k: int = 8) -> list[Clause]  # Clause{id,page,title,body}
def read_document(doc_id: str) -> DocExtract  # {doc_type, facts: [...], amounts: [...], confidence}
def update_loss_statement(items: list[LossItemInput]) -> list[LossItem]
def ask_client(text_en: str, requested_items: list[str]) -> CommId
def send_email(to: str, subject: str, body: str, attachment_ids: list[str]) -> CommId  # goes through review
def start_call(goal: str, questions: list[str]) -> CallId
def schedule_followup(when: datetime, reason: str, source_clause_id: str | None) -> TaskId
def register_deadline(kind: str, due_at: datetime, source_clause_id: str | None) -> TaskId
def log_fact(text: str, source: FactSource, confidence: str) -> FactId
def request_insurer_document(kind: Literal["CG_signed","CP_signed","delivery_proof","expert_report"]) -> CommId
def present_offer(offer_id: str) -> None  # interrupt awaiting_signature_decision

# Review
def review(draft: OutboundDraft, ctx: ReviewContext) -> ReviewResult  # {pass, violations[], rewrite}

# HTTP
POST /webhooks/telegram        # secret = token in the URL
POST /webhooks/agentmail       # signature verified
POST /webhooks/elevenlabs      # signature verified
POST /onboarding/*             # session cookie
GET  /claims/{id}/track?token= # tracking page via link (read-only)
GET  /healthz
```

---

## 6. Open questions and spikes

| # | Question | Current assumption | Spike | Blocks |
|---|---|---|---|---|
| Q1 | Who holds the Aiven organisation admin role? | A team member | Ask now; otherwise deploy elsewhere and document | H0 deployment |
| Q2 | LangGraph Store for cross-thread memory? | Not needed | Check installed version | No |
| Q3 | ElevenLabs credits + verified Twilio number | Available | Call test at 2 pm | Step 8 |
| Q4 | **Language of emails/calls to a French insurer** | EN for the demo (jury) | Mathis's decision; recommendation: **FR to a real insurer in H1**, EN kept for the demo | H1 |
| Q5 | Eligibility of professionals to the Médiation de l'Assurance | Uncertain ("consumer" charter) | Check per insurer / LMA charter | H1 wording |
| Q6 | **Legal qualification of the service** (loi 1971 / L511-1) with the "procedural layer" scope | Outside legal consultation and outside distribution | **Lawyer's opinion before the first invoice** | H1 launch |
| Q7 | Compensation model compatible with Q6 | % of the indemnity (benchmark 5–10 % policyholder's loss assessors, ~10 % public adjusters) | Lawyer: does a success-based % reinforce the "advice" qualification? Alternatives: subscription, flat fee per file | H1 |
| Q8 | Case-law references displayed | From secondary sources | Verify on Légifrance before any on-screen display | H0 slide |
| Q9 | Benchmark contracts B and C | AXA Atouts PME / Generali 100% Pro | Assign and verify the synthetic CP | H0 bench |
| Q10 | GDPR: DPA, EU hosting, police complaint reports (sensitive data) | Aiven `fra` = EU | Processing register, supplier DPAs | H1 |

---

## 7. Failure modes

### 7.1. Risks

| Risk | Prob. | Impact | Mitigation |
|---|---|---|---|
| GitHub Runtime link impossible in time | Med. | **Critical H0** | Hello world deployed first; plan B hosting + honest explanation to the jury |
| The agent emits an unsourced amount or an opinion | Med. | Critical (legal + trust) | Blocking review node + `review_log` + test AC-12; eval on 50 drafts before the demo |
| Unverified fact sent → client forfeiture | Low | Critical | `facts.status` gate; vision confidence; question to the client |
| Clause / page hallucination | Med. | High | Citation verified verbatim against `clauses.body` |
| Duplicate counted | Low | Medium | sha256 + triple key |
| Webhook > 1 s → retry storm | Med. | Medium | Insert + immediate 200; idempotence on `provider_message_id` |
| Incompatible checkpointer | Low | High | Resume test from step 3 |
| LLM cost | Med. | Medium | Extraction cache by sha256; $ cap per file; smaller model for triage |
| Demo: simulated insurer perceived as cheating | Med. | High for pitch | "simulated insurer" label everywhere; real live call |
| "Vulture" reputation | Low H0 | High H1 | GTM via referrers (accountants, CCI, brokers), never canvassing |
| Legal requalification of the service | Med. | **Critical H1** | Q6/Q7; scope hard-coded in the review node and the terms of service |

### 7.2. Business-owner-side errors (Telegram, EN)

| Error | Message | Recovery |
|---|---|---|
| Unreadable document | "I couldn't read this file. Could you send a clearer photo of page X?" | Upload task |
| Email send failed | "The email to your insurer failed to send (provider error). I'll retry in 10 minutes." | Retry 3× then alert |
| Call not completed | "I couldn't reach the insurer by phone. I've sent the same questions by email." | Fall back to email |
| Deadline passed | "The contractual deadline for X was DATE. Late declaration can only be opposed if the insurer proves prejudice (art. L113-2). I've sent it now." | Continue |
| Out of scope | "I can't advise on that decision. Here are the options that exist: …" | Documentary |

### 7.3. Rollback

Single service: `redeploy` of the previous commit via the Aiven API; additive migrations only (never `drop` in H0/H1); file state in PG, nothing in logs.

---

## 8. Tests and acceptance criteria

| # | Given | When | Then | Priority |
|---|---|---|---|---|
| AC-1 | MAAF CG + Karim CP uploaded | Intake runs | Coverage profile with ≥ 15 guarantees, each row has `clause_id` + existing page; theft/vandalism = `yes` (CP), PE = `yes` | Must |
| AC-2 | CP absent | Intake runs | All options = `unknown`, never `no`; "upload CP" task | Must |
| AC-3 | Message "looted Saturday night" + photos | triage | File created; initial declaration sent **before** any document request; acknowledgement logged | Must |
| AC-4 | Invoice X sent 2× | analyze | Only 1 `evidence` counted; `duplicate_of`; message to the client | Must |
| AC-5 | Inventory + invoices + N-1/N-2 revenue | analyze | Statement of loss ≥ 90 % of items `08c` §6 case A; each item has evidence + clause + page | Must |
| AC-6 | Theft ceiling €30k endorsement added | Intake + analyze | Versioned profile; stock item recomputed; delta displayed | Must |
| AC-7 | Service restarted while waiting | event arrives | Thread resumed; no action replayed | Must |
| AC-8 | Oral answer "riot extension applies" | post-call | Fact `insurer_oral/to_confirm`; profile unchanged; confirmation email sent | Must |
| AC-9 | Offer + « pour solde de tout compte » document | present_offer | `has_release_language = true`; factual explanation; `awaiting_signature_decision`; no implicit acceptance after 7 days | Must |
| AC-10 | Client writes "organised looters" | review | Factual rephrasing; word absent from any external send | Must |
| AC-11 | Draft contains "we recommend you refuse" | review | Blocked, rewritten as a quantified comparison | Must |
| AC-12 | Draft contains a € absent from `evidence` and client instructions | review | **Blocked**; `review_log` | Must |
| AC-13 | Client declares stock at retail price | analyze | Reset to purchase price with clause; risk explained; retail price not sent | Must |
| AC-14 | Simulated 24-month file | scheduler | Tasks: complaint, declaration, statement of loss, follow-ups, 30-day payment, depreciation D+700, limitation D-90, State 31/12/2030 — all created, none missed | Should |
| AC-15 | Bench A/B/C | `bench/` | 3 variants measured; agent > LLM alone > naive in recall and €, 0 untraceable amounts | Must (slide) |
| AC-16 | Two demo accounts | isolation | No cross-`account_id` leak (filtered queries, tests) | Must |

**Unit tests**: deduplication, PE computation, single deductible, banned-word detection, release detection, deadline extraction per contract (12 CG). **Integration**: webhook → events → resume; AgentMail round trip; checkpointer resume. **E2E**: W1, W2, W3.

---

## 9. Security and compliance

| Requirement | Threshold | Reason |
|---|---|---|
| Multi-tenant isolation | `account_id` on all tables, filtered in every query; test AC-16 | Financial and criminal data (police reports) |
| Site authentication | HttpOnly/SameSite session cookie; argon2 passwords | — |
| Telegram linking | Single-use code, expires in 15 min; `chat_id` verified; never merge on phone number alone | Anti-impersonation |
| Webhooks | AgentMail / ElevenLabs signature verified; Telegram token as URL secret; `provider_message_id` idempotence | — |
| Secrets | Runtime variables marked secret; never in database or logs; Aiven admin credentials **are not** bot tools | — |
| Rate limiting | 30 messages / chat / 10 min; 20 uploads / account / h | Abuse, cost |
| Input validation | Allowed MIME types (pdf, jpg, png, heic, oga); size ≤ 20 MB; antivirus H1 | — |
| Sensitive data | Police complaint reports, bank details, ID documents: encrypted at rest (Aiven PG); **protected upload** rather than Telegram for bank details/ID (`CONTEXTE` §11 recommendation) | GDPR |
| Audit log | `actions`, `communications`, `review_log`, `mandates`: append-only | Proof of what was done on the client's behalf |
| Retention | File kept ≥ limitation period (2 years insurer, 4 years State) + 1 year; export on request; deletion on revocation + statutory delay | — |
| Business compliance | Mandate distinct from consents; terms of service spelling out the "procedural" scope; "does not constitute legal advice" notice; lawyer's opinion Q6 before invoicing | Loi 1971, L511-1 |
| Demo transparency | "simulated insurer" label; distinction between real execution / scripted scenario | Hackathon brief |

---

## 10. Performance, costs, observability

| Metric | Target |
|---|---|
| Webhook → 200 | < 1 s |
| Event → first Telegram reply | < 20 s (p95) |
| Intake of 100 pages | < 3 min |
| LLM cost per typical file (A) | measured; $5 cap H0; $20/day alert |
| Concurrency | 1 instance H0; asyncio worker; `SKIP LOCKED` ready for N instances |

**Provider resilience**: 429 → exponential backoff 3×; AgentMail down → retry 10 min then client alert; ElevenLabs down → fall back to email; Claude timeout 60 s / step, 5 min / run.

**Observability**: `actions` table (tool, tokens, latency), `events` (depth, failures), `review_log` (block rate by type), `scheduled_tasks` (missed = 0). LangSmith optional.

---

## 11. Context for AI agents (developers)

| Path | Content | Why |
|---|---|---|
| `PROJECT_CONTEXT_INSURANCE.md` §14 | Today's architecture decisions | Stack reference |
| `data/contrats/txt/*.txt` | 12 real CG (`\f` = page) | Ingestion + ground truth |
| `data/research/08a`, `08b` | Clauses + pages per contract; "forgotten items" table; deadlines | **Item catalogue** (2.4) and **deadline engine** (2.5) |
| `data/research/08c` §6 | Quantified cases A/B/C | Benchmark + fixtures |
| `data/research/08c` §4.3 | Banned words, State liability claim | Review node, State module |
| `data/research/09a` | Contractual traps → signals + levers | Detection in Intake/analyze |
| `data/research/09b` §5 | Public adjuster file discipline | `communications` cadence + follow-ups |
| `data/research/09c` §1.2 | Lawful boundary / advice | **Review node rules** |

**Patterns**: every external send goes through `review`; every tool writes to `actions`; every date comes from a clause or the law with `source_clause_id`; every € comes from an `evidence` or a `client_instruction`.
**Anti-patterns**: do not code "a universal clock" (deadlines vary per contract); do not infer an unsubscribed option from a missing page; do not overwrite a fact; do not let the agent pick a figure; do not add Kafka/OpenSearch/Valkey for the logos.

---

## 12. Execution phases

### H0 — today (order per `CONTEXTE` §14.10, enriched)

| # | Task | Files | Blocks |
|---|---|---|---|
| 1 | FastAPI hello + Dockerfile `EXPOSE 8080` + Runtime deployment + PG connected + test migration | `app/main.py`, `Dockerfile`, `migrations/` | everything |
| 2 | Ingestion of 12 CG → `documents`/`clauses`; Intake on MAAF + Karim CP → `coverage_profile`, `contract_levers`, deadlines | `app/ingestion/`, `app/agents/intake/` | 3,5 |
| 3 | Minimal Claims Agent `load_memory → analyze → review → present` on a seeded file; tools `search_clauses`, `read_document`, `update_loss_statement`; **review node with the 8 checks** | `app/agents/claims/`, `app/agents/review/` | 4,5,6 |
| 4 | Telegram: deep link, media, `ask_client`, interrupt/resume, deduplication; resume-after-restart test | `app/channels/telegram/` | 7 |
| 5 | `bench/`: 3 cases × 3 variants; figures for the slide | `bench/` | slide |
| 6 | AgentMail: mailbox/account, `send_email`, webhook, **Insurer Simulator** with release | `app/channels/email/`, `app/agents/insurer_sim/` | 7 |
| 7 | Site: 6 steps reduced to 1–2 pages, mandate + 3 consents, Intake, deep link | `app/web/` | demo |
| 8 | ElevenLabs: outbound call, post-call, oral provenance | `app/channels/voice/` | demo (degradable) |
| 9 | Telegram voice notes; resume demonstrated; pitch | — | — |

Parallelism: 2 ‖ 3 (after 1); 4 ‖ 6 (after 3); 5 as soon as 3 produces a statement of loss; 7 ‖ 8.

### H1 — first users (4–8 weeks)

- **Legal**: lawyer's opinion (Q6/Q7); terms of service; non-advice notice; GDPR register + DPA.
- **Channels**: WhatsApp Cloud (Meta validation); own email domain; object storage.
- **Product**: State liability claim module (2.10); full 24-month deadline engine; tracking page via link; PDF file export (statement of loss + documents + log); multi-contract L121-4.
- **Coverage**: extend the corpus (Groupama booklets, Allianz retailers, Pacifica CG); per-insurer profiles.
- **Distribution** (never canvassing): accountants (hold the PE tax returns), CCI / trade associations (post-17/10 emergency units), brokers, **policyholder's loss assessors** (white-label tool — they are "small, fragmented and under-tooled", `08d` §4).
- **Measurement**: 5 real files tracked; business owner time; € identified vs initial declaration; deadlines met.

### H2 — launch (3–6 months)

- Compensation validated (Q7); possible structuring (partner policyholder's loss assessor / MIAD if required).
- All routine MRP claims (110 / 1,000 contracts / year), not just riots; event seasonality anticipated (summer 2026 fires: 3,000 business claims).
- Monitor **LFI 2026 art. 171** (mandatory riot cover, 2-month advance, BCT): adapt deadlines on entry into force.
- Continuous eval of the review node (block rate, false positives); nightly benchmark on extended corpus.
- Security: upload antivirus, pentest, eIDAS mandate.

---

## 13. Decision log

| Date | Who | Topic | Decision |
|---|---|---|---|
| 2026-10-22 morning | Mathis | Bot in English; autonomy without human; acceptance = business owner; % of indemnity (TBD) | Decisions |
| 2026-10-22 midday | Team (Emile) | Telegram, LangGraph, single service, Karim/MAAF case, simulated insurer | Decisions (§14) |
| 2026-10-22 | Mathis | **Robin = pure procedural layer**: does not execute the payout, does not decide any amount, does not advise; removes friction | **Decision — guiding principle** |
| 2026-10-22 | Research (09c) | Cass. 2015 / CA Nîmes 2023 / Cass. 2025: paid advice on offers = unlawful legal consultation | Review node = safeguard; lawyer's opinion before invoicing (Q6) |
| 2026-10-22 | This PRD | Language to insurer (Q4), compensation (Q7), mediation for professionals (Q5) | **Open** |

## Approval

| Role | Name | Date | Status |
|---|---|---|---|
| Author | — | 2026-10-22 | Submitted |
| Product | Mathis | | Pending |
| Engineering | Emile | | Pending |

**PRD status: [ ] APPROVED FOR EXECUTION**
