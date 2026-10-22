# Robin

Autonomous insurance-claims agent for small businesses. After a loss, the
business owner onboards on a website (uploads the policy PDFs, signs a mandate), then
talks to Robin on Telegram. Robin declares the loss to the insurer the same day,
collects evidence, builds a clause-cited statement of loss, emails and calls the
insurer, follows up, and presents the insurer's offer factually. The business owner
decides; Robin executes.

Built in one day for the Accel / Aiven "Data-Centric Agents" hackathon (22 October
2026) by a team of three. Product spec: `docs/prd/2026-10-22-robin-claims-agent/PRD.md`.

**Why now.** On 17–18 October 2026, at least 3,000 shops were damaged in France
(Prime Minister / Public Sénat 19/10), with insured losses estimated at €1–1.2 bn
(Morningstar DBRS via Reinsurance News) and small retailers making up 70 % of the
victims (FCD via Economie Matin). France Assureurs extended the declaration deadline to
30 days. The mandatory riot cover voted in the 2026 finance law is not in force. A
small business owner facing this has to read 70–120 pages of general conditions they
have never opened, declare within days, and build a statement of loss alone. Sources
and figures: PRD §1.1–1.2 and `data/research/08c_Real_Cases_Case_Law.md` §0.

## What Robin does and does not do

Robin is a **pure procedural layer**. It does what the business owner should be doing
themselves, faster and without forgetting anything. It never decides, advises or
accepts. Every euro it emits traces to an `evidence` row, a `client_instruction` fact,
or a cited formula whose inputs are those. A review gate enforces this in code before
any outbound message.

| Robin does | Robin never does |
|---|---|
| Declares the loss to the insurer on Day 0 with confirmed facts only | Decides or originates an amount |
| Collects evidence (photos, invoices, inventory, police receipt) with sha256 dedup | Advises, recommends, assesses "your chances" |
| Builds a living statement of loss: item → evidence → clause (page) → computation | Accepts, agrees, waives or settles anything |
| Emails and calls the insurer, requests documents, follows up at D+7 | Negotiates in its own name |
| Stores oral insurer answers as `insurer_oral` / `to_confirm` and asks for written confirmation | Lets an oral answer modify the coverage profile |
| Detects release language in an insurer offer and explains its effect factually | Collects funds (the insurer pays the business owner) |
| Presents the offer as "X € of the Y € documented", lists the generic options without weighting | Treats silence as acceptance |

**Why this matters legally.** Case law qualifies paid, personalised advice on
insurers' settlement offers as unlawful practice of legal advice: Cass. 2e civ.
9 December 2015 (n° 14-24.268), CA Nîmes 7 July 2023 (appeal dismissed), and Cass.
2e civ. 7 May 2025 as referenced in PRD §2.15. The distinction the law draws is between
*information à caractère documentaire* (documentary information), which is lawful, and
a personalised opinion contributing to the decision, which is not. Robin stays on the
documentary side, and the review gate makes that a property of the output rather than
of the marketing. Full analysis: `data/research/09c_Legal_Perimeter_Synthesis.md`.

## How it works

Single FastAPI service: HTTP (site + webhooks) and an in-process asyncio worker. All
state lives in Aiven PostgreSQL, including LangGraph checkpoints. Webhooks only insert
into `events` and return; the worker does the work.

```
 Business owner                          Insurer side
 ──────────────                          ────────────
 Web onboarding ─► Intake Agent ─► coverage_profile, contract_levers,
 (PDFs, mandate,   (LangGraph,      deadline_rules, intake_tasks
  consents)         6 nodes)
      │ /start <code>
      ▼
 Telegram ──────────┐
 AgentMail webhook ─┼─► events ─► worker ─► Claims Agent ─► review gate
 ElevenLabs webhook ┤  (pending)  (SKIP     (LangGraph,         │
 scheduler ─────────┘             LOCKED)   1 thread/claim,     │ approved
                                            PG checkpointer)    ▼
                                                            adapters
                                                   telegram / email / voice
                                                          │
                                          ┌───────────────┴──────────────┐
                                          ▼                              ▼
                                simulated insurer              live insurer
                                (LangGraph, own mailbox,       (demo: a teammate
                                 "SIMULATED INSURER" label)    answers the call)
```

The Claims Agent (`app/agents/claims/graph.py`) runs one LangGraph thread per claim
(`thread_id = claim_id`), checkpointed in Postgres with `AsyncPostgresSaver`. Each run
ends in `wait` on a typed `interrupt()`; the next event resumes it with
`Command(resume=...)`. A restart does not lose the thread.

```
 event ─► load_memory ─► triage ─► analyze ─► act ─► review ─► dispatch
            ▲           new claim?  facts,     drafts  8 controls   send,
            │           offer?      evidence,    ▲        │         schedule
            │           followup?   dedup,       │ retry  │         follow-ups
            │                       covers,      └────────┘ ≤ 3        │
            │                       offers       then: ask client      ▼
            │                                                       reflect
            │                                                       (digest)
            │                                                          │
            │   Command(resume={event})                                ▼
            └──────────────────── next event ──────────────────────  wait
                                                   interrupt({wait_type}):
                                                   awaiting_client
                                                   awaiting_insurer_email
                                                   awaiting_call_result
                                                   awaiting_followup
                                                   awaiting_signature_decision
```

Node behaviour as implemented:

- `triage` decides from the event kind and memory: no initial declaration sent yet
  → new claim, declare today (L113-2); insurer email with an amount and offer vocabulary
  → `present_offer`; `followup_due` → `act`; otherwise `update`.
- `analyze` logs client text as a `client` fact, registers uploaded documents as
  evidence (sha256 dedup, then amount + date + vendor), stores call answers as
  `insurer_oral` / `to_confirm`, records every insurer position verbatim in a ledger,
  and on an offer email inserts an `offers` row with `has_release_language`. It then
  matches each loss item to a cover of the coverage profile (`brain/covers.py`: stolen
  contents → theft cover, damaged property → riot / glass / fire cover; cap, deductible,
  clause and page come from the profile row, never from the agent). With
  `OPENAI_API_KEY` set it also reads documents (vision for images, `pdftotext` for
  PDFs) and structures the client's narrative into a neutral description and candidate
  loss items; without a key these steps degrade gracefully.
- `act` builds drafts from templates: declaration email in the insurer's language, English Day-0
  checklist, acknowledgements that state how items map to the policy (caps and gaps
  with pages), written-confirmation request after a call, D+7 follow-up, offer
  summary. Drafts never recommend or originate an amount.
- `review` runs every draft through the gate; a blocked draft is retried up to three
  times, then replaced by a factual notice to the client asking for confirmation.
- `dispatch` sends approved drafts through the adapters and schedules the insurer
  follow-up and the D+3 / D+7 offer-decision reminders.
- `reflect` updates the running claim digest (open asks and when they were asked,
  satisfied asks, insurer positions, next steps) that the next turn reads back, so the
  agent does not re-request what is already on file. Then `wait` parks the thread.

Every tool call writes a row in `actions` (`app/agents/audit.py`) with arguments,
result, tokens and latency.

## The review gate

`app/agents/review/gate.py` is the single exit for outbound text. Workstream A calls
it before any simulated-insurer email; the Claims Agent calls it on every draft. The
controls are deterministic (regex, SQL, string similarity), run before any send, and
every result is written to `review_log` with the draft, the verdict and the violations.

| # | Control | What it checks |
|---|---|---|
| 1 | Evidence | each loss item in the send has ≥ 1 `evidence` row and an existing `clause_id` |
| 2 | Citation | every (clause_id, quote) pair is verbatim in the clause body (similarity ≥ 0.9) |
| 3 | Duplicates | no evidence row counted twice, none with `duplicate_of` set |
| 4 | Traceable € | every amount in the text equals (±0.50 €) an evidence, derived or client-instruction amount |
| 5 | Promise | no "we accept", "agreed", "we waive", *pour solde de tout compte*, "full and final" |
| 6 | Advice | no "you should", "we recommend", "your chances", "legally insufficient", *vous devriez* |
| 7 | Banned words | toward insurer / police / prefect: no *organisé*, *bande*, *casseurs*, *émeutiers*, *prémédité*, "gang", "looters"… (these qualify the event as an organised group and can forfeit the State liability claim, L211-10 CSI) |
| 8 | Unconfirmed | no fact with `status != confirmed` in an external send |

French and English patterns are both checked on every draft. An LLM judge layered on
top of the deterministic controls is referenced in the code but not implemented; the
gate is currently rule-based only. Tests: `tests/test_review_gate.py` (AC-10, AC-11,
AC-12 and the allowed factual phrasings).

## Data at the core

Robin is a memory model with an agent on top. Nothing is overwritten; everything
carries its source.

**Account memory** (written by Intake, read by Claims):
- `coverage_profile` — one row per guarantee, versioned with `supersedes`; `subscribed`
  is `yes | no | unknown` and a missing page never means `no`. Each row cites
  `clause_id`, `page`, a verbatim `quote` and a confidence.
- `contract_levers` — waiver of the *règle proportionnelle*, assessor fees cover,
  single deductible, indirect losses, advances, and contractual traps, each with clause
  and page, marked `to_confirm`.
- `deadline_rules` — sourced deadline candidates extracted from the contract text.

**Claim memory** (written by Claims):
- `facts` — `source` ∈ `client | document | client_instruction | insurer_email |
  insurer_oral | agent_inference`, `status` ∈ `confirmed | to_confirm | contradicted |
  superseded`, versioned with `supersedes`. Oral answers and agent inferences default
  to `to_confirm`.
- `evidence` — linked to a `documents` row; duplicate detection on sha256 first, then
  on (amount, date, vendor); duplicates are kept but marked `duplicate_of`.
- `loss_items` — label, amount, `amount_basis` (`purchase_price | replacement_value |
  invoice | formula | client_instruction`), `evidence_ids`, `clause_id`, page, quote,
  computation, condition, status; a new version supersedes the previous one.
- `offers`, `scheduled_tasks`, `communications`, `calls`, `actions`, `review_log`.
- `claim_digest` — the agent's running summary per claim (open asks with how many
  times and since when they were asked, insurer positions verbatim and dated, next
  steps), rewritten after every turn by `reflect` and read back by `load_memory`.
- `insurer_profiles` — cross-claim observations per insurer (first-reply delay, first
  offer as a share of the documented total, documents requested, release language),
  stated to the client as observations only once two or more claims exist, never as a
  prediction.

**Execution state** — LangGraph checkpoint tables created by
`langgraph-checkpoint-postgres`; the Claims Agent thread survives restarts.

**Contract corpus.** `data/contrats/txt/` holds 12 public general conditions
and IPIDs (AXA, Allianz, Generali, Groupama, Hiscox, MAAF, MMA, Pacifica, Sogessur),
exported with `pdftotext -layout` and page-separated by `\f`. `app/ingestion` splits
them into page-local clauses (1,655 clauses locally) whose bodies are exact slices of
the source text, indexed with a `tsvector('french')` for `websearch_to_tsquery` search
(`app/ingestion/search.py`). Every coverage fact cites clause and page, and the gate
verifies the quote against the clause body before it leaves.

## Demo scenario

Case A from `data/research/08c_Real_Cases_Case_Law.md` §6 (composite and fictional):
Karim, smartphone repair and resale, Marseille city centre. Policy: MAAF general
conditions 11031 (01/2026) from the corpus plus a synthetic policy schedule
(`data/fixtures/karim_particular_conditions.pdf`: riot extension, theft capped at
€15,000, business interruption with a 3-day deductible, replacement value on equipment,
€1,000 general deductible). Workflow W1 from PRD §2.13:

- Karim onboards on the site, uploads the PDFs, signs the mandate and the three
  consents; the Intake Agent produces a coverage profile with pages; the deep link
  `/start <code>` connects his Telegram chat.
- Telegram: "My shop was looted Saturday night" + photos + invoices. The thread opens a
  claim, sends the declaration email (in French, the demo insurer's language) to the insurer on Day 0 and the Day-0
  checklist to Karim (police complaint, photos before works, boarding-up, no repairs
  without written approval).
- Karim re-sends an invoice already on file: the sha256 match marks it `duplicate_of`
  and Robin says so without counting it twice.
- The simulated insurer acknowledges with a reference and asks for the police receipt
  and the number of customer devices; Robin relays, files and transmits.
- Live call (ElevenLabs Agents + Twilio, answered by a teammate playing the insurer):
  "Does the riot extension apply to stock, or the €15,000 theft cap?" The answer is
  stored as `insurer_oral` / `to_confirm`, summarised to Karim as oral and unconfirmed,
  and a written-confirmation email goes out.
- The simulated insurer sends an offer of €20,750 with a *quittance d'indemnité pour
  solde de tout compte* (full-and-final release) PDF attached. `analyze` records the
  offer with `has_release_language = true`; Robin tells Karim what the offer covers of
  what is documented, that signing extinguishes further claims (art. 2052 C. civ.),
  and lists the options (accept, ask, contest; complaint, ombudsman, loss assessor,
  lawyer) without weighting them. The thread parks on `awaiting_signature_decision`.
- The service is restarted mid-demo; the thread resumes from the checkpointer.
- The simulated insurer is labelled "SIMULATED INSURER" in every email it sends.

## Benchmark

PRD §2.12 specifies a benchmark on cases A (Karim / MAAF), B (bakery) and C (optician)
with three variants: naive declaration, LLM alone (same model, no clauses, no
invoices), and the Claims Agent. Measures: € identified, recall of claimable items with
correct clause and page, % of correct citations, untraceable amounts emitted (must be
0), token cost and latency per event. Ground truth: `08a`/`08b` for clauses and pages,
`08c` §6 for items.

The harness is **planned, not built**: `bench/` currently contains only an empty
`__init__.py`. No figure is published until it has been measured. The research
baselines (Karim declares ≈ €38,100 alone against ≈ €89,700 of documented items; the
scenario offer is ≈ €20,750) are assumptions from `08c` §6, not benchmark results.

## Stack

- Python 3.12, FastAPI, uvicorn, psycopg 3 (async pool, `max_size = 8` for the app,
  2 for the checkpointer; Aiven PG has `max_connections = 15`).
- LangGraph + `langgraph-checkpoint-postgres` (`AsyncPostgresSaver`).
- OpenAI through `langchain-openai`, built in one place (`app/llm.py`); default model
  `gpt-4o` (`OPENAI_MODEL`, `INTAKE_MODEL`), temperature 0. Document extractions are
  cached by sha256 in `llm_extraction_cache`.
- `python-telegram-bot` (long polling in dev, webhook in prod), AgentMail (one inbox per
  account, Svix-verified inbound webhook), ElevenLabs Agents + Twilio (outbound call,
  HMAC-verified post-call webhook, browser widget fallback), ElevenLabs Scribe or
  OpenAI Whisper for Telegram voice notes.
- Jinja2 templates, Argon2 passwords, ReportLab / fpdf2 for fixture and release PDFs,
  poppler `pdftotext` in the Docker image.
- Aiven PostgreSQL 18 and Aiven Runtime. One Dockerfile, one service.

## Run locally

```sh
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r pyproject.toml
# local Postgres 16 (Homebrew) on port 5499, db "robin", user "robin", trust auth
export PATH=/opt/homebrew/opt/postgresql@16/bin:$PATH
pg_ctl -D /tmp/robin-pg -o "-p 5499 -k /tmp" -l /tmp/robin-pg.log start
.venv/bin/uvicorn app.main:app --port 8080 --reload   # reads .env (gitignored)
curl localhost:8080/health
```

Docker alternative for the database:

```sh
docker run -d --name robin-pg -e POSTGRES_USER=robin -e POSTGRES_PASSWORD=robin \
  -e POSTGRES_DB=robin -p 5499:5432 postgres:16
```

Migrations in `app/migrations/*.sql` run automatically at startup, in filename order,
once each (`schema_migrations`). They are additive only. Load the contract corpus once
with `.venv/bin/python -m app.ingestion.load_corpus`. Tests:
`.venv/bin/python -m pytest tests/`. A database-backed smoke test of the Claims Agent
thread (park on interrupt, resume on the next event) is in
`scripts/smoke_claims_graph.py`.

Environment variables (`app/config.py`; `.env.example` is partially stale and still
lists `ANTHROPIC_API_KEY`, which is not read):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres DSN; injected by the Aiven integration in production |
| `OPENAI_API_KEY`, `OPENAI_MODEL`, `INTAKE_MODEL` | the only LLM provider; without a key the graphs run in degraded, deterministic mode |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_MODE` (`polling` \| `webhook`), `TELEGRAM_BOT_USERNAME` | Telegram channel and deep link |
| `AGENTMAIL_API_KEY`, `AGENTMAIL_WEBHOOK_SECRET`, `AGENTMAIL_DOMAIN`, `AGENTMAIL_SHARED_INBOX`, `SIMULATED_INSURER_EMAIL` | email channel and demo insurer inbox |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_PHONE_NUMBER_ID`, `ELEVENLABS_WEBHOOK_SECRET` | voice channel |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `INSURER_TEST_PHONE` | telephony and the number of the teammate playing the insurer |
| `PUBLIC_BASE_URL` | webhook registration and deep links |
| `SESSION_SECRET`, `INTERNAL_API_TOKEN` | web sessions; bearer for `/internal/*` operator endpoints |
| `WORKER_ENABLED`, `WORKER_POLL_SECONDS`, `LOG_LEVEL`, `GIT_COMMIT` | worker and logging |

## Deploy

Production runs on Aiven: project `larp`, Runtime application `robin`
(`aws-eu-central-1`), PostgreSQL service `pg-3f9bc500` (`do-fra`), `DATABASE_URL`
injected by the service integration. Pushing to `main` does not deploy: redeploy from
the Aiven console (Runtime → robin → Deploy latest commit) or with the Aiven MCP
(`aiven_application_redeploy`). Secrets live in Runtime environment variables, never
in the repository or in logs. `/health` reports `db` and which integrations have keys.

## Repository layout

```
app/main.py, db.py, worker.py, config.py   shared core: FastAPI lifespan, pool, event worker
app/contracts.py                           shared types (events, facts, loss items, review)
app/llm.py                                 the one place that builds chat models (OpenAI)
app/migrations/                            additive SQL schema, applied at startup
app/ingestion/                             PDF/text -> documents/clauses (pages split on \f), search
app/agents/intake/                         Intake Agent: coverage profile, levers, traps, deadlines
app/agents/claims/                         Claims Agent graph, nodes, memory, tools, outbound
app/agents/claims/brain/                   cover matching, claim digest, insurer positions, insurer profiles
app/agents/review/                         review gate: 8 controls, rules, amounts, citations
app/agents/insurer_sim/                    simulated insurer (demo only, labelled as such)
app/agents/audit.py                        record_action(): every tool call -> `actions`
app/deadlines/                             per-claim deadline instantiation (planned, empty)
app/channels/telegram|email|voice/         adapters: python-telegram-bot, AgentMail, ElevenLabs
app/web/                                   onboarding site, mandate, consents, tracking page
bench/                                     benchmark harness (planned, empty)
scripts/                                   smoke test of the Claims Agent thread
tests/                                     pytest
data/contrats/txt/                         12 public general conditions / IPIDs
data/fixtures/                             synthetic Karim policy schedule and endorsement
data/research/                             sourced research (see below)
docs/prd/, docs/workstreams/               PRD, status tracker, the three workstream specs
```

## Research corpus

`data/research/` is the sourced base the product is built on. `08a` and `08b` extract
the relevant clauses of the 12 contracts with page numbers (riots, theft, glass,
business interruption, ancillary costs, levers, traps). `08c` collects real merchant
testimonies from October 2026, case law, and the three composite demo cases with their
item tables. `08d` covers the claims process, business model and regulation. `09a`
lists contractual traps and hard cases, `09b` the denial, appraisal and offer
playbooks, and `09c` the legal perimeter of the service and the ten capabilities the
agent needs. The product spec in `docs/prd/` consolidates them. The research files are
in French with English glosses; everything else in the repository is in English.

## Status

Derived from the Status blocks of `docs/workstreams/A-*.md`, `B-*.md`, `C-*.md` and
checked against the code on 22 October 2026.

| Area | State |
|---|---|
| FastAPI skeleton, async pool, migrations, event worker, `/health` | done, deployed on Aiven Runtime |
| Ingestion of the 12 public contracts into `documents` / `clauses` | done locally; production load pending |
| Intake Agent (coverage profile, levers, traps, deadline rules, missing documents) | implemented; validation with the real model pending |
| Onboarding site, mandate + 3 consents, deep link, tracking page | done locally; live bot pending |
| Synthetic Karim policy schedule + endorsement PDFs, `loss_catalog`, `riot_events` seeds | done |
| Claims Agent graph with Postgres checkpointer, resume on events | done (smoke-tested) |
| Review gate, 8 deterministic controls, `review_log` | done, tested; LLM judge not implemented |
| Document reading and narrative extraction with OpenAI | implemented in `nodes/llm.py` |
| Offer detection, `offers` row, release-language detection, offer summary | implemented in `graph.py` / `analyze.py` / `act.py` |
| Loss item ↔ cover matching, claim digest, insurer position ledger, insurer profiles | implemented in `brain/`, tested in `tests/test_claims_brain.py` |
| Telegram bot: linking, media, voice notes, send adapter, webhook | code ready; blocked on `TELEGRAM_BOT_TOKEN` |
| AgentMail: mailbox per account, send adapter, inbound webhook, insurer-language templates | done, tested on production |
| ElevenLabs + Twilio: agent, `start_call` adapter, post-call webhook, reconciliation | done, tested on production |
| Insurer Simulator with release PDF | done, tested end to end on production |
| Claims Agent triggering `start_call` itself | not wired; calls are started via `POST /internal/calls` |
| Statement-of-loss email with cited items, contestation transmission | planned |
| Per-claim deadline instantiation from `deadline_rules` (`app/deadlines/`) | planned |
| State liability claim module (L211-10 CSI, prefect letter) | planned (H1) |
| Benchmark harness (`bench/`) | planned |
| End-to-end W1 rehearsal on production | pending |

## Legal note

Robin is not a lawyer, a loss assessor or an insurance intermediary, and nothing it
produces is legal advice. The service perimeter is operational execution under a
written mandate: notify, collect, transmit, follow up, document, explain facts; it
excludes accepting an offer, settling, waiving, collecting funds and any
recommendation. Case-law references in this repository come mostly from commentaries
and must be checked on Légifrance before being cited externally
(`data/research/08c_Real_Cases_Case_Law.md`, header note).
