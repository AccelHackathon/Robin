# 09c — Legal perimeter of the agent and synthesis of required capabilities

> Written 22/10/2026. Two parts: (1) what French law allows or forbids an autonomous service that handles claims for retailers — the risk is real and documented in case law; (2) the synthesis of all the research (`08a`–`09b`) into concrete capabilities to build.
> Reading rule: every fact is followed by its source. **(unverified)** = hypothesis. Research synthesis, not legal advice — the characterisation of the service must be validated by a lawyer before commercial launch.

---

## Part 1 — The legal perimeter: two documented red lines

### 1.1. *Distribution d'assurance* (insurance distribution) (L511-1 / IDD) — a fine line

Art. L511-1 of the Code des assurances defines distribution as including **« contribuer à la gestion et à l'exécution des contrats d'assurance, notamment en cas de sinistre »** [contributing to the management and performance of insurance contracts, in particular in the event of a claim], for remuneration. Being a distributor ⇒ ORIAS registration (French register of insurance intermediaries), professional capacity, professional liability insurance, 15 h/year IDD training, ACPR supervision.

Key nuance set by the ACPR itself: « l'activité qui consiste **exclusivement** en la gestion, l'évaluation et le règlement des sinistres n'est pas considérée comme de la distribution » [the activity consisting exclusively of managing, assessing and settling claims is not considered distribution], but « contribuer **plus largement** à la gestion et à l'exécution des contrats » [contributing more broadly to the management and performance of contracts] falls within it. Source: [ACPR — insurance intermediaries](https://acpr.banque-france.fr/fr/professionnels/lacpr-vous-accompagne/intermediaires/intermediaires-dassurance).

- The line between « handling a claim for the policyholder » (outside distribution) and « contributing to the performance of the contract » (distribution) is not cleanly settled for a service like ours — **grey area, to be characterised by a lawyer**.
- The decisive criterion retained by legal doctrine is **remuneration linked to the activity**: a % of the indemnity may pull the model towards distribution depending on how it is structured. Source: [Deloitte Blog](https://blog.avocats.deloitte.fr/le-porteur-dune-police-dassurance-souscrite-pour-le-compte-dun-tiers-doit-il-etre-considere-comme-un-intermediaire-en-assurance/).
- If the conclusion leans « distribution »: the routes are own ORIAS registration (*courtier* — broker — on an ancillary basis?) or appointment under an existing intermediary (MIAD, R511-2). Source: [Académie Conformité](https://academieconformite.fr/courtier-soustraitance-gestion-sinistres-prestataire-externe/).

### 1.2. *Consultation juridique* (regulated legal advice) (loi 1971) — the most serious risk, direct case law

**Cass. 2e civ., 9 décembre 2015, n° 14-24.268** — an **insurance broker** (hence already ORIAS-registered) who provided, habitually and for remuneration, « un avis personnalisé sur les offres transactionnelles des assureurs, en négocie le montant » [a personalised opinion on insurers' settlement offers, negotiates their amount] and referred clients to a lawyer on failure: **unlawful practice of legal advice**, prohibition + publication. These services fell neither within the follow-up of a contract placed through the broker, nor within preparatory work for a subscription. Source: [LibreJustice](https://librejustice.fr/decision/fr/xJ63RDysOGQm).

**CA Nîmes, 7 juillet 2023** (upheld, appeal to the Cour de cassation dismissed) — a « mandataire d'assuré » [policyholder's agent] who analysed insurers' indemnity proposals and advised clients on next steps: same characterisation, prohibition under a penalty of €1,000 per breach. Source: [CNB](https://cnb.avocat.fr/actualite/le-cnb-et-l-ordre-des-avocats-de-marseille-obtiennent-la-condamnation-d-un-mandataire-d-assure-devant-la-cour-de-cassation).

**The definition that tips the balance**: legal advice is « toute prestation intellectuelle **personnalisée** qui tend à fournir un avis sur une situation soulevant des difficultés juridiques ainsi que sur la(les) voie(s) possible(s) pour les résoudre, concourant à la prise de décision du bénéficiaire » [any personalised intellectual service tending to provide an opinion on a situation raising legal difficulties and on the possible route(s) to resolve them, contributing to the beneficiary's decision-making]. What remains lawful: « **information à caractère documentaire** » [documentary information] — informing on the state of the law or case law without a personalised opinion. Source: [BACA Lyon — nullity for unlawful object](https://publications-prairial.fr/bacaly/index.php?id=1000).

**Positioning decided by Mathis (22/10/2026)**: the service is a **pure procedural layer** — it simplifies the process and does what it is supposed to do (notify, collect, transmit, follow up, document, explain factually), full stop. **The agent does not execute the payout** (the insurer pays the retailer directly — which also closes the open point « do not assume the service receives the funds ») and **decides no amount**: every figure transmitted reflects the retailer's documented losses or their explicit instruction. It does not advise, does not negotiate, does not « win » — it removes friction.

This perimeter corresponds to option A below and removes most of the « legal advice » risk — **provided it is held in what the agent produces, not only in the marketing**: case law characterises acts, not intent. Still to lock down in the outputs: no amount must ever originate from the agent (only from evidence or the retailer's instructions), and no wording must suggest a personalised legal assessment.

Operational boundary to engrave in the design:

| Removes friction (lawful under mandate) | Crosses into advice (risk) |
|---|---|
| Notify on time, transmit documents, build the *état des pertes* (statement of loss) | Assess « your chances » of winning |
| Request a status, follow up, prepare the appraisal file | Negotiate the amount with legal arguments on the client's behalf (« en négocie le montant » [negotiates the amount] was the conduct censured in Cass. 2015) |
| Detect a *quittance* (release) and explain its effect factually (« this document extinguishes future remedies on this claim ») | Say « do not accept » / « this offer is legally insufficient » |
| Quantify the gap: « the offer covers 62 % of your documented losses; items not covered: X, Y » | Formulate a weighted recommendation |
| Prepare the quantified and sourced counter-analysis; the retailer chooses the figure and the strategy; the agent executes their instruction | Choose the counter-proposal amount oneself |

**Application to our agent — the tension is head-on**: the current design provides that the agent « explains the offer and may formulate a recommendation ». A personalised recommendation « accept / refuse this offer » grounded in applicable law = the exact core of the two condemned cases. Mitigation options (product/legal decision to be made, not an implementation recommendation):

| Option | What the agent does | Residual risk |
|---|---|---|
| A. Strictly documentary | Compares the offer to the file's items/figures, cites clauses and their sources, quantifies gaps — without ever formulating an opinion on the decision | Lowest; remains the question whether the quantified comparison already constitutes an « opinion » |
| B. Bounded factual recommendation | « The offer covers 62 % of your documented statement of loss; items not covered: X, Y » + presents the generic routes (clarification, contestation, mediation, lawyer) without weighing them | Medium — the opinion/finding boundary is a question of fact |
| C. Recommendation + human escalation | The agent recommends, but any contested file or significant offer is validated by a partner policyholder's loss assessor/lawyer | Legally safer; contradicts Mathis's « zero human » constraint |
| D. Characterisation + legal structuring | Prior legal opinion, structuring (ORIAS/MIAD, possibly an in-house lawyer or partner firm), service T&Cs writing out the perimeter | Necessary whatever the option — not an alternative |

**Decisive point for the business model**: both condemnations rest on « à titre habituel et rémunéré » [habitually and for remuneration]. A service paid as a % of the indemnity that advises on offers ticks both boxes. **Legal validation is not optional before the first invoice.**

### 1.3. What is free and useful

- *Mandat* (mandate) of representation for operational steps (notify, transmit, request status, follow up): lawful — this is execution, not advice.
- The profession of ***expert d'assuré*** (policyholder's loss assessor) is not regulated (no mandatory certification; Fedexa/Ifpass voluntary); fees unregulated, observed practice **5–15 % of the indemnity** or flat fee/Upemeic scale. Sources: [L'Argus — expert d'assuré](https://www.argusdelassurance.com/juriscope/expert-d-assure-une-profession-encore-en-construction.206112), [RM 2129](https://questions.assemblee-nationale.fr/q15/15-2129QE.htm). → Price benchmark + possible structuring route (operate AS/WITH a policyholder's loss assessor).
- Results-based remuneration benchmarks confirmed abroad: public adjusters ~10 % (capped in several US States). See `09b` §5.

---

## Part 2 — Synthesis: the 10 capabilities that make an « expert-grade » agent

Cross-reading of `08a`–`08d` (policy corpus, real cases, process) and `09a`–`09b` (traps, tactics, playbooks). Credible sophistication against a human insurance expert comes down to ten capabilities; each is verifiable in the benchmark.

### C1. Coverage determination on real documents
Parse CG + CP + endorsements (*conditions générales* / *conditions particulières* — general conditions / policy schedule); as at the date of the loss (the applicable endorsement is an already-planned demo moment). Check for every denial: clause in conspicuous typeface (L112-4), « formal and limited » character (L113-1), and whether the insurer provides proof of the factual conditions. **Benchmark test**: on the corpus of 12 CG, produce for a given case the list of candidate covers + enforceable exclusions with page cited.

### C2. Deadline machine
All deadlines as tracked tasks: notification 2 d/5 d, LRAR (registered letter with acknowledgement of receipt) for increase in risk 15 d, waiting period per cover, appraisal, complaint→mediation 2 months, 2-year limitation with interrupting events (LRAR on settlement, expert appointment), replacement-as-new top-up ~2 years. **Test**: a simulated 24-month file misses no deadline.

### C3. Evidence discipline (anti-forfeiture)
Every fact carries source + verification status + author. Nothing unverified goes to the insurer. This is the capability that protects the client from the agent itself (Cass. 2026: *déchéance* — forfeiture of cover — for false statement is upheld). **Test**: inject a contradictory invoice → the agent marks it unconfirmed and asks, never asserts it.

### C4. Detection of underinsurance and derogating clauses
At onboarding: sums insured vs. value indicators → alert. On denial: check tolerance / reversibility / indexation / agreed value before conceding the proportional rule; demand proof of actual value. ~40 % of UK property claims undergo this adjustment → **the no. 1 value lever**. **Test**: `08c` case with sum insured < actual value, policy with tolerance clause → the reduction is contested and correctly quantified.

### C5. Denial dissection
Denial letter → classified ground (non-coverage / exclusion / forfeiture / reduction / suspension) → invoked clause cited → playbook countermeasure (`09b` §1) → reasoned and sourced LRAR reply. **Test**: on 5 standard letters, classification and countermeasure are 100 % correct.

### C6. Appraisal preparation and follow-up
Pre-visit checklist (quantified statement of loss, indexed photos, written positions handed over), own notes during, written observations after; « expert fees » cover extracted at onboarding; threshold for recommending a *contre-expertise* (counter-appraisal). **Test**: appraisal scenario — the file handed to the expert contains all items with clause + evidence.

### C7. Signature gate
Automatic detection of *quittance* / « solde de tout compte » [full and final settlement] / « renonciation » [waiver] / « transaction » [settlement agreement] / « définitif » [final] in any insurer document → explanation of items covered vs. given up → explicit retailer decision. Silence ≠ acceptance (already decided). **Test**: a release disguised as a « payment acknowledgement » is intercepted.

### C8. Quantified offer evaluation
Item-by-item reconciliation: covered/partial/denied/absent; depreciation vs. formula; caps; deductible; proportional rule; provisional vs. final. Restitution to the policyholder in plain language with the € gap. ⚠️ Phrase as a **quantified comparison** (cf. §1.2) — the wording « I recommend accepting/refusing » is the legal risk point to be decided.

### C9. File cadence (public adjuster playbook)
Communications logged and dated, insurer's positions verbatim with contact name, reminders scheduled at sending, insurer's deadlines tracked, every overrun exploited as leverage. This is procedural persistence — where an overwhelmed human gives up, the agent does not tire. **Test**: a simulated insurer that stalls → sequence reminder → LRAR → complaint, dated and traceable.

### C10. Clear-eyed escalation and owned perimeter
Know what cannot be won (waiting period, valid exclusion, suspension for unpaid premium) and say so quickly with the alternative remedies (liable third party, State L211-10 CSI). Know where the service stops: serious legal contestation → policyholder's loss assessor / lawyer (cf. §1.2 — this is also a legal obligation, not merely prudence). **Test**: uncovered case (loss during waiting period) → the agent detects it and pivots to alternative routes instead of fabricating a file.

---

## Honest reading for the pitch: the promise is time and money saved, not victory

The value is expressed as friction removed, measurably:

- **Time**: building the statement of loss (finding invoices, searching every clause across 70–120 pages, quantifying) — metric already planned in the benchmark (`CONTEXTE` §7); reminders and follow-up the retailer has no time to sustain.
- **Money**: claimable items the retailer is unaware of (FCA: denials come « as a shock », PE — business interruption — yields more than expected — `09b` §6); contested reductions (underinsurance: ~40 % of UK property claims adjusted — Aviva); money left on the table (replacement-as-new top-up at ~2 years; expert fees covered by the policy).
- **Errors avoided**: late notification, missing evidence, release signed too early, unverified fact transmitted — each documented as a real cause of loss (`09a`, `09b`).

The data confirms it: ~50 % of large commercial claims are disputed (Mactavish), litigation yields ~32 % for the policyholder in ~3 years — the value is not « winning », it is that the file never needs to be disputed, and that it is complete when it is.

**Pitch-ready demo**: two identical files — the naive retailer notifies late, under-quantifies items, forgets the tolerance clause and signs a release; the agent notifies on day 0, mobilises the derogating clauses, documents every exchange, quantifies the offer gap item by item. The delta in hours + € + technicalities avoided is the measure — without the agent ever « advising »: it executes and quantifies, the retailer decides.
