# 09a — Contract traps and hard cases: what loses an MRP claim

> Written 22/10/2026. Complements `08d` (process): here, the mechanisms that reduce or void a payout, with the legal lever that answers each one and the behaviour expected of the agent.
> Reading rule: every fact is followed by its source. **(unverified)** = working hypothesis. This is a research synthesis, not legal advice.

---

## 0. Why this file

A « simple » claim is settled amicably. The agent's value is decided on the cases where the insurer invokes a reduction or exclusion mechanism. This file lists those mechanisms, in estimated order of frequency for a retailer on an MRP (multi-risk business) policy.

---

## 1. *Règle proportionnelle de capitaux* (underinsurance averaging rule) — the no. 1 case at scale

**Mechanism.** Art. L121-5 C. assur.: if the actual value of the insured property on the day of the loss exceeds the sum insured, the policyholder « supporte une part proportionnelle du dommage, sauf convention contraire » [bears a proportional share of the loss, unless otherwise agreed]. Formula: `indemnity = loss × (sum insured / actual value)`. Applies as of right, to partial or total losses, regardless of the policyholder's good faith. Sources: [Juriblio L121-5](https://juriblio.fr/codes/code-des-assurances/partie-legislative/livre-ier/titre-ii/chapitre-ier/article-l121-5), [Index Habitation](https://www.index-habitation.fr/multirisque/sinistres/regle-proportionnelle-de-capitaux).

**Scale.** Aviva estimates ~33 % of SMEs are underinsured on their buildings, and ~40 % of property claims are adjusted downward for underinsurance (UK insurer data, order of magnitude transposable). Source: [Aviva Broker Underinsurance](https://connect.avivab2b.co.uk/broker/resources/product-support/Underinsurance/).

**The counters, in the order the agent checks them** ([Ariane Gire — 6 key points](https://www.arianegire.fr/publications/les-six-points-clefs-de-la-regle-proportionnelle-de-capitaux)):

1. **Tolerance clause**: threshold (e.g. 15 %) below which the rule does not apply.
2. **Reversibility / surplus carry-over clause**: the value of all insured property is taken into account, not only that of the damaged item.
3. **Indexation clause**: the insured value tracks an index — the underinsurance may not exist on the day of the loss.
4. **First-loss / agreed-value clause**: indemnity fixed in advance, sets the rule aside.
5. **Burden of proof**: it is for the insurer to establish the actual value on the day of the loss. Challenging its estimate is legitimate.

**Agent**: at onboarding, compare sums insured against available valuation elements and flag an underinsurance risk (alert, not advice). At claim time: before conceding a reduction, check the 4 derogating clauses in the CG/CP (*conditions générales* / *conditions particulières* — general conditions / policy schedule); demand proof of the actual value the insurer relies on.

## 2. *Règle proportionnelle de prime* (premium-proportion reduction) (inaccurate declaration at inception)

**Mechanism.** Art. L113-9 C. assur.: if the omission or inaccurate declaration is not intentional, the indemnity is reduced in the proportion of the premium rate paid vs. the premium that should have been paid. If intentional → nullity possible (L113-8). Source: [Le Codex](https://www.avocats-juridiques.fr/assurance-multirisque-pro-comment-gerer-un-refus-dindemnisation/).

**Key nuance.** The policyholder only answers for the questions the insurer asked (L113-2, 2°: the questionnaire). An omission on a point never asked cannot be held against them. Bad faith / intent must be proven by the insurer.

**Timing**: loss occurring before the insurer has chosen between termination and a new premium → treated as an inaccuracy discovered after the loss (proportional rule applicable, Cass. 2e civ., 2 mars 2017, n° 15-27831). Source: [Krajeski, U. Toulouse](https://publications.ut-capitole.fr/id/eprint/23892/1/23892_Krajeski.pdf).

**Agent**: keep the initial risk declaration and questionnaires; if the insurer invokes L113-9, check (a) that the question existed, (b) the basis of the proportion calculation, (c) contest intent if nullity is invoked.

## 3. Undeclared *aggravation du risque* (increase in risk)

**Mechanism.** L113-2, 3°: declare within 15 days (by LRAR — registered letter with acknowledgement of receipt) any new circumstances increasing the risk. L113-4: the insurer may terminate or propose a new rate; non-declaration → cover put at stake.

**Important counter.** The insurer can no longer rely on the increase in risk if it was informed of it « de quelque manière que ce soit » [by any means whatsoever] and continued to collect premiums or paid an indemnity (L113-4, last para.). **Proof of what the insurer knew is therefore an asset of the file.**

**Agent**: treat any change of activity, works, or storage of new goods as a triggerable event (« Should this be declared to your insurer? »); archive every exchange showing the insurer's knowledge.

## 4. *Déchéance* (forfeiture of cover) for late notification

**Mechanism.** Deadlines: 2 working days (theft), 5 working days (general), contractual beyond that. L113-2: forfeiture is only enforceable if (a) a contractual clause provides for it, (b) the insurer proves a prejudice caused by the delay, (c) no fortuitous event / force majeure. Restated in case law: Cass. com., 7 mars 2018. Sources: [Legifrance L113-2](https://www.legifrance.gouv.fr/codes/id/LEGISCTA000006157200), [Journal Actu](https://www.avocat-journalactu.fr/comment-contester-le-refus-dindemnisation-de-votre-assurance-multirisque-entreprise/).

**Agent**: send the notification immediately, even if incomplete — a notification is not a quantified claim file; track deadlines as tasks; document any force majeure; if forfeiture is raised, demand proof of the prejudice.

## 5. Forfeiture for false statement about the loss — existential risk for an agent

**Mechanism.** Standard clauses: « toute fausse déclaration sur la nature, les causes, les circonstances ainsi que les conséquences du sinistre […] vous prive de tout droit à garantie » [any false statement on the nature, causes, circumstances or consequences of the loss deprives you of any right to cover]. Validity: very conspicuous typeface (L112-4) + **the insurer must establish the policyholder's bad faith**. Settled case law: Cass. 2e civ., 5 juil. 2018, n° 17-20.491; 15 déc. 2022, n° 20-22.836; **12 fév. 2026, n° 24-18.594** (forfeiture is not a disproportionate sanction; the policyholder who lied about the consequences loses cover). Sources: [Doctrine Cass. 2026](https://www.doctrine.fr/d/CASS/2026/CASSP88C53E2C8DA6189276CB), [LibreJustice](https://librejustice.fr/decision/fr/tAwtgaai1cKK).

**Product consequence**: any exaggeration, rounding or unverified fact sent to the insurer exposes the retailer to losing ALL cover for the loss — including the legitimate items. An agent that « helps too much » destroys the file. Corollary: the provenance and verification status of every fact (already planned in the project memory) is not a luxury, it is the client's primary protection.

## 6. Coverage exclusions

**Rule.** L113-1: exclusions must be **formal and limited** (*exclusion formelle et limitée*) — clear, precise, requiring no interpretation, and must not empty the cover of its substance. L112-4: nullities, forfeitures and exclusions in very conspicuous typeface. Burden of proving the factual conditions of the exclusion: on the insurer, not reversible by contract (Cass. 2e civ., 2 avr. 1997). Interpretation contra proferentem (C. civ. 1190, adhesion contract construed against the drafter). Sources: [Gdroit burden of proof](https://gdroit.fr/droit-des-assurances/sinistre-dans-le-cadre-du-contrat-dassurance-la-charge-de-la-preuve/), [Cass. 21-15.392 (COVID, business interruption)](https://www.courdecassation.fr/en/decision/638852d601d0fb05d44b0982), [Cass. 23-14.482 (poorly drafted exclusion)](https://www.doctrine.fr/d/CASS/2025/CASSPA93FD78E859BAF922DD3).

**Documented abusive practice**: mischaracterising the loss to bring it within an exclusion; extensive interpretation; mixing cover and exclusions in a single clause (risky for the insurer, cf. Trillat). Sources: [Journal Actu](https://www.avocat-journalactu.fr/comment-contester-le-refus-dindemnisation-de-votre-assurance-multirisque-entreprise/), [Trillat & Associés](https://www.trillatassocies.com/data/Actualite/Exclusions-contractuelles-et-charge-de-la-preuve.pdf).

**Agent** — checklist when an exclusion is invoked: (a) is the clause in very conspicuous typeface? (b) does reading it require interpretation? → « not formal » argument; (c) does it empty the cover of its substance? (d) what proof does the insurer provide of the factual conditions?

## 7. *Émeutes et mouvements populaires* (riots and civil commotion) (the project's use case)

Reminder from `08d`: L121-8 — the insurer does not cover riots/civil commotion **unless otherwise agreed**, and it is for the insurer to prove the characterisation as a riot. Practical point: the characterisation of the event (isolated looting, vandalism, riot) determines which cover is triggered — theft, vandalism, glass breakage, or an express riot clause. The agent must build the most favourable characterisation supported by the evidence, not accept the insurer's.

## 8. *Délai de carence* (waiting period)

MRP policies set waiting periods per cover: benchmarks ~15 d (fire), ~30 d (theft), 30-90 d (business interruption); MAAF's optional « tax protection » cover has one. Sources: [Assur-life](https://www.assur-life.com/assurance-professionnelle-quels-delais-de-carence-prevoir-pour-etre-couvert/), [CG MAAF §28](https://handicapzero.maaf.fr/mon-activite-professionnelle/multirisque-professionnelle/conditions-generales-multirisque-professionnelle/la-vie-du-contrat/28-la-vie-du-contrat-conclusion-prise-deffet-resiliation). **A loss during the waiting period is legitimately not covered** — a case where « winning » is impossible; the agent's role is to say so quickly and switch to the other remedies (liable third party, State).

## 9. Prevention obligations / security measures

Working alarm, metal shutter, annual electrical inspection (APAVE-type), preservation of evidence before works: the CG impose them; breach opens an exclusion or reduction. In the Cass. 2017 case cited above, failure to send the annual reports justified the proportional rule. **Agent**: extract prevention obligations at onboarding into a dated checklist; at claim time, check compliance status BEFORE the insurer does (alarm active on the night of the theft, etc.); if there is a breach, prepare the response (causal prejudice required? proportionality?).

## 10. *Perte d'exploitation / PE* (business interruption) — the biggest item, the most technical

- Only applies if (a) PE cover was taken out (CP), (b) caused by a covered material damage at the « lieu de risque » [insured premises] (cf. IME standard CG: covered events → direct material damage → PE). Source: [CG IME Pertes d'exploitation](https://imentreprises.fr/ime/services-en-ligne/doc/CG/CG_PERTES-EXPLOITATION.pdf).
- Calculation: loss of ***marge brute*** (gross margin: turnover − variable costs) over the indemnity period taken out (12/18/24 months), + additional costs; a ~20 % base-adjustment clause is common. Source: [Matmut](https://www.matmut.fr/pro/assurance-activite/conseils/calcul-indemnisation-perte-exploitation).
- The indemnity period is not affected by a post-loss termination (CG IME art. 2) — point to check if the insurer threatens to terminate mid-file.
- Reference litigation: COVID administrative closures — an entire battle over the « formal and limited » character of exclusions (Cass. 21-15.392).
- **Agent**: collect early the tax return bundle, monthly turnover for years N and N-1, variable costs; build the gross-margin model with the retailer's chartered accountant; document the causal chain damage → interruption.

## 11. Multiple policies and apportionment

L121-4: several insurances on the same risk → obligation to declare them to one another; each pays within the limit of its cover; total ≤ actual loss (L121-1). Fraudulent cumulation is sanctioned, innocent cumulation is not. Frequent case: MRP + separate glass-breakage policy + business-card cover. **Agent**: list all policies at onboarding; allocate items to the most favourable policies; declare cumulations properly (LRAR if required).

## 12. Tenant / landlord and recourse

- Tenant's risks: the retailer-tenant covers rental damage owed to the landlord; its MRP covers its contents and its liability — two distinct claim flows, do not mix them.
- Liable third party: if a third party caused the loss, the insurer indemnifies and is then subrogated (L121-12); the retailer must sign nothing that deprives the insurer (or itself) of the recourse.
- Riots: recourse against the State, art. L211-10 CSI — prefect then administrative court, 4-year limitation; limit set by CE 28/10/2022 (premeditated acts by an organised group). Already noted in `08d`; the agent must keep it as a parallel track when cover fails.

## 13. Deferred *vétusté* (depreciation) and *valeur à neuf* (replacement-as-new) — money left on the table

The « replacement-as-new » top-up is only paid after actual replacement, on invoices, within ~2 years. A retailer who does not know they must claim this top-up loses it. **Agent**: at closure of any file with depreciation, create the long-term task « replacement-as-new top-up » with the contractual deadline and expected invoices.

## 14. Unpaid premium / suspension of cover

L113-3: cover suspended 30 days after a *mise en demeure* (formal notice) left without effect; loss during suspension = no cover. **Agent**: at first claim contact, check premium status (direct question to the retailer + request for a certificate from the insurer) before promising anything.

---

## Quick map → what the agent must know how to do

| Trap | Signal to detect | Lever |
|---|---|---|
| Underinsurance | Sums insured < probable value | Tolerance/reversibility/indexation clauses; proof of actual value on the insurer |
| Inaccuracy at inception | Denial invoking L113-8/9 | Question never asked = not enforceable; intent to be proven |
| Undeclared increase in risk | Change of activity/works | Proof of insurer's knowledge + premiums collected |
| Late notification | Denial on deadline | Prejudice to be proven + force majeure |
| False statement on the loss | Any unverified fact | Never assert anything unsourced — upstream protection |
| Exclusion | Denial on a clause | L112-4 form + « formal and limited » + proof on the insurer |
| Waiting period | Loss < X days after inception | Alternative remedies (third party, State) |
| Prevention | Alarm/security required | Compliance checked before the insurer |
| PE | Business interruption | Gross margin + causation + indemnity period |
| Multiple policies | Several policies | Item allocation + cross-declaration |
| Depreciation | Two-stage indemnity | Replacement-as-new top-up task at ~2 years |
| Unpaid premium | Possible suspension | Premium status checked first of all |
