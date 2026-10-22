# Workstream B — Onboarding & Intake

**Owner:** teammate 1. **PRD sections:** 2.1 (onboarding), 2.2 (Intake Agent), 2.5 (deadline extraction), 2.4 catalogue seed, 3.2 rows `web`, `ingestion`, `agents/intake`; AC-1, AC-2, AC-6, AC-16; 9 (auth, consents).

## Status

- [x] Ingestion of the 12 public documents into `documents` / `clauses` (local verified; production load pending)
- [x] Seeds: `loss_catalog`, `riot_events` (research-scenario provenance retained)
- [x] Synthetic particular conditions PDF for Karim (+ 30,000 EUR endorsement generator)
- [x] Intake Agent: coverage profile, levers, traps, deadlines, missing documents (implemented; real-provider validation pending)
- [x] Onboarding site (account + 4 visual steps), mandate + 3 consents, deep link (local verified; live bot pending)
- [x] Tracking page by private, rotatable link (local verified)

### Implementation checkpoint

- Verification: 43 integrated tests passed (including 19 B tests, with a dedicated PostgreSQL database); import check and local `/health` (`db: ok`) passed. Desktop and 390px mobile inspected in Chrome; both fixture PDFs rendered and reviewed.
- Production acceptance remains open: Runtime database access, model credentials, bot username/token, and A/C integration are not available in this checkout. See `app/web/README.md` for exact handoff contracts.

- Local PostgreSQL: 12 corpus documents / 1,655 verbatim page-local clauses; idempotent ingestion verified. Production load pending Runtime access.
- Web routes, durable sessions, Argon2 passwords (PRD section 9 takes precedence over B5 bcrypt), upload validation, consent records, link renewal, and coverage polling implemented.
- Six-node Intake graph implemented; deterministic synthetic-fixture extraction tested. Real model execution uses OpenAI (`OPENAI_API_KEY`, set on Runtime); without a key the graph produces explicitly partial results and unknown subscriptions.
- Shared additions: `TELEGRAM_BOT_USERNAME`, `SESSION_SECRET`, `INTAKE_MODEL` settings; Argon2 and ReportLab dependencies. No changes to main, worker, or shared types.
- Integration: migration 200 fans out `web/onboarding_done` into `web/document_added` transactionally. A keeps the mailbox handler; B consumes the latter event.
- C handoff: `onboarding.welcome_brief` is an unsent draft (review before sending); `deadline_rules.rule.status` distinguishes extracted vs to_confirm; `coverage_profile.subscribed` remains SQL boolean/NULL, serialized yes/no/unknown on the web. Private search/quote verification requires `account_id=`.
- C handoff: urgent incident text is in `onboarding.incident` and the `onboarding_done` payload; web does not claim a declaration has been sent. C must consume it for urgent triage.

## Owned paths

```
app/ingestion/             pdf.py (split pages on \f, headings), load_corpus.py (CLI), search.py (full-text helpers)
app/agents/intake/         graph.py (LangGraph), prompts.py, guarantees.py (canonical keys), deadlines.py, handlers.py
app/web/                   routes.py, auth.py, templates/*.html, static/
app/migrations/2xx_*.sql   (seeds included: loss_catalog, riot_events)
data/fixtures/             karim_particular_conditions.pdf (+ generator script), karim_profile.json
tests/test_ingestion_*.py, tests/test_intake_*.py, tests/test_web_*.py
```

## Deliverables

### B1. Ingestion (first — unblocks C and the benchmark)

1. `app/ingestion/pdf.py`: for each `data/contrats/txt/*.txt` (already `pdftotext -layout`, pages separated by `\f`), produce `(page, heading, body)` rows. Heading = first non-empty line in caps/numbered title when present. Keep the body verbatim (never normalise the text that will be quoted; normalise only in search).
2. `load_corpus.py` (CLI, idempotent by `sha256`): insert `documents` (`account_id = NULL`, `origin = corpus`, `doc_type = general_conditions`, `insurer_name`, `product_name`, `version_label`, `page_count`) and `clauses`. Run it against production (DATABASE_URL from Runtime) once ingestion is green locally.
3. `search.py`: `search_clauses(document_id, query, k)` using `tsv @@ websearch_to_tsquery('french', query)` ranked by `ts_rank`, plus a `verify_quote(clause_id, quote)` helper (whitespace-normalised similarity ≥ 0.9 — used by C's review gate; C imports this one function).
4. Also handle PDFs uploaded on the site: run `pdftotext -layout` (poppler is in the Docker image) → same pipeline, `account_id` set.

### B2. Seeds (migration `2xx_seeds.sql` or a Python seed run at startup, idempotent)

- `loss_catalog`: the full catalogue of PRD 2.4 (stock, spare parts, bailed goods, shopfront glass, signage lettering, shutter, sign/awning, locks, tenant fit-out, equipment, guarding/boarding, debris/cleaning/decontamination, graffiti, cash, archives, storage/relocation, temporary premises, architect fees, compliance upgrades, indirect losses 10 %, business interruption, extra operating costs, seals prolonging BI, goodwill loss, outstanding leasing, assessor fees, deferred depreciation top-up, State recourse remainder). `often_forgotten` and `source_ref` from `08b §5` / `08c §3.2`.
- `riot_events`: "17–18 October 2026 unrest", cities, `declaration_deadline_days = 30`, `state_claim_deadline = 2030-12-31`, sources.

### B3. Karim fixtures

- `data/fixtures/karim_particular_conditions.pdf`, one page, MAAF-styled "Conditions particulières": insured Karim's shop in Marseille hypercentre, policy number, riot and civil commotion extension **subscribed**, theft/vandalism option subscribed with a **15 000 € cap** on stock, business interruption subscribed with a **3-day deductible**, replacement value on equipment, general deductible 1 000 €. Plus a generator script so the "endorsement raising the theft cap to 30 000 €" variant (AC-6, W3) is one command.
- `karim_profile.json`: business fields for the onboarding demo autofill.

### B4. Intake Agent (LangGraph, `app/agents/intake/graph.py`)

Triggered by `("web", "onboarding_done")` and `("web", "document_added")` — register handlers in `handlers.py`. Nodes:

1. `classify_documents` — `doc_type`, document date, validity window, `insurer_name`, `product_name`, `readable`. Recognise corpus CGs by sha256 or editor reference ("11031 - 01/26") and link instead of re-extracting.
2. `extract_coverage` — for each canonical guarantee key in `guarantees.py` (fire, riot_civil_commotion, theft_vandalism, glass, water, business_interruption, bailed_goods, tenant_fit_out, equipment_replacement_value, guarding_boarding, debris, graffiti, cash, locks, assessor_fees, indirect_losses, legal_protection, assistance): search clauses, run the extraction prompt of PRD 2.2 **per clause**, write `coverage_profile` rows with `quote`, `clause_id`, `page`, `confidence`, `version`. Particular conditions override general conditions (`supersedes`). **Never write `subscribed = no` because a page is missing: write `unknown`.**
3. `extract_levers_and_traps` — `contract_levers` rows for: no_proportional_rule, assessor_fees, single_deductible, indirect_losses_10pct, bi_advances, and traps `trap.theft_excluded_during_riots`, `trap.theft_excluded_from_riot_cover`, `trap.bi_access_denial_excluded`, `trap.assistance_excluded_riots`, `trap.repairs_require_written_consent`, `trap.stock_cap_without_pc` (PRD 2.2 step 5–6, sources `08a`, `09a`).
4. `extract_deadlines` — `scheduled_tasks` templates for the account (not yet dated: store in `coverage_profile`-like JSON on the business or a `deadline_rules` table you add in 2xx): police report delay, declaration delay (theft / other), loss statement delay, payment delay after agreement, replacement-value top-up window (2 years), prescription (2 years). Each with `source_clause_id` or `legal_basis`. C instantiates them per claim.
5. `list_missing_documents` — tasks for the client (no particular conditions → "Could you upload the policy schedule showing your selected cover?").
6. `write_welcome_brief` — English summary used by C's welcome message: covers, caps, deductibles, with page references.

Model: OpenAI `gpt-4o` through `app.llm.chat_model()` (`OPENAI_API_KEY`); no other provider. Cache extractions by `(sha256, guarantee)` in a small table (2xx) to keep the benchmark cheap.

### B5. Onboarding site (`app/web/`, Jinja2 + Tailwind CDN, server-rendered)

1. `/signup`, `/login`, `/logout` — email + password (bcrypt), HttpOnly SameSite session cookie, resume of an unfinished onboarding.
2. `/onboarding/business` — name, SIRET, address, manager, phone, insurer, broker, tenant/owner, VAT registered (3-state).
3. `/onboarding/documents` — multi-upload (pdf, jpg, png, heic; ≤ 20 MB), stored in `documents` with `sha256`, `origin = web_upload`; shows classification once Intake ran.
4. `/onboarding/mandate` — mandate text (scope per PRD 2.1 step 4: obtain documents, transmit confirmed facts and evidence, contact insurer/broker/expert, request status, follow up; **excludes** accepting an offer, settling, waiving, collecting funds), **three separate checkboxes** (mandate, Telegram channel, data processing), typed name + role, timestamp → `mandates` + `consents`.
5. `/onboarding/done` — enqueue `("web", "onboarding_done")`, create a `link_codes` row (15-minute expiry), show the **"Open Telegram"** deep link `https://t.me/<bot>?start=<code>` (bot username from settings `TELEGRAM_BOT_USERNAME`) and the live coverage profile as it fills in (poll `/onboarding/profile.json`).
6. `/claims/{id}/track?token=` — read-only tracking page: loss statement with clause pages, timeline of `communications` and `actions`, deadlines. Token stored on the claim (add column in 2xx).
7. Every query filters by the session's `account_id` (AC-16). Language of the UI: English.

## Acceptance

- B-1 (AC-1): after onboarding with MAAF CG + Karim PC, `coverage_profile` has ≥ 15 guarantees, each with an existing `clause_id` and page; theft/vandalism `yes` from the PC, business interruption `yes`.
- B-2 (AC-2): without PC, every optional cover is `unknown`, never `no`; a missing-document task exists.
- B-3: the 12 CGs are in production `clauses` (≈ 47 000 lines of text → expect ~1 500–3 000 clause rows); `search_clauses(maaf, "gardiennage")` returns the 72 h guarding clause with its page.
- B-4 (AC-6): loading the 30 000 € endorsement creates a new `coverage_profile` version for theft with `supersedes` set.
- B-5: a second account cannot see the first account's documents or profile (test).

## Order of work

1. Ingestion + corpus loaded in production (C needs it within the hour). 2. Seeds + Karim PC. 3. Intake nodes 1–2 on MAAF. 4. Site steps 1–5 (minimal styling first). 5. Intake nodes 3–6. 6. Tracking page. 7. Polish.

## Config you own

`TELEGRAM_BOT_USERNAME`, `SESSION_SECRET`.
