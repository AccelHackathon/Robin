# Robin — agent instructions

Autonomous insurance-claims agent for French small businesses. Product spec: `docs/prd/2026-10-22-robin-claims-agent/PRD.md` (authoritative). Architecture decisions: `CONTEXTE_PROJET_ASSURANCE.md` §14 (historical). Status tracker: `docs/prd/2026-10-22-robin-claims-agent/STATUS.md`.

## Start here

The work is split into three parallel workstreams, each owned by one person and their agents. **Before writing any code, read `docs/workstreams/README.md`** (rules, interfaces, what is already done), then the spec of the stream you were assigned:

- **A — Voice & insurer side** → `docs/workstreams/A-voice-and-insurer.md`
- **B — Onboarding & Intake** → `docs/workstreams/B-onboarding-and-intake.md`
- **C — Claims Agent & Telegram** → `docs/workstreams/C-claims-agent-and-telegram.md`

Your spec lists the paths you own, the deliverables, the acceptance criteria and the order of work. Work only inside your owned paths; follow the git cadence in the README (small commits, `git pull --rebase` before every push); update the Status block at the top of your spec when you finish an item. If you were not told which stream you are on, stop and ask.

## Language

Everything in the repo is in English: code, comments, docs, commit messages, prompts. Exceptions: verbatim quotes from French insurance contracts (never translate a cited clause), outbound emails to French insurers, and the French research files under `data/research/`.

## Stack

Python 3.12, FastAPI, psycopg 3 (async pool), LangGraph + `langgraph-checkpoint-postgres`, `langchain-openai`, `python-telegram-bot`, Jinja2. Single service: HTTP + webhooks + in-process worker. Aiven PostgreSQL 18 (`max_connections = 15`: keep pools small). Deployed on Aiven Runtime.

## Run locally

```sh
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r pyproject.toml
# local Postgres 16 (Homebrew) on port 5499, db "robin", user "robin", trust auth
export PATH=/opt/homebrew/opt/postgresql@16/bin:$PATH
pg_ctl -D /tmp/robin-pg -o "-p 5499 -k /tmp" -l /tmp/robin-pg.log start
.venv/bin/uvicorn app.main:app --port 8080 --reload   # reads .env (gitignored)
curl localhost:8080/health
```

Migrations in `app/migrations/*.sql` run automatically at startup, in filename order, once each (`schema_migrations`). They are **additive only**: never `DROP`, never rename; add a new numbered file.

## Deploy

Production: Aiven project `larp`, application `robin` (Runtime, `aws-eu-central-1`), database `pg-3f9bc500` (`do-fra`), `DATABASE_URL` injected by the service integration. Pushing to `main` does **not** deploy. Redeploy via the Aiven MCP (`aiven_application_redeploy`) or console → Runtime → robin → Deploy latest commit. Secrets live in Runtime environment variables; never in the repo, never in logs.

## Layout and ownership

```
app/main.py, db.py, worker.py, config.py   shared core (announce changes)
app/contracts.py                           shared types (PRD §5) — changing these is a cross-team change
app/migrations/                            schema (additive)
app/ingestion/                             PDF -> documents/clauses (pages split on \f)
app/agents/intake/                         Intake Agent: coverage profile, levers, traps, deadlines
app/agents/claims/                         Claims Agent graph + tools (tools.py = contract)
app/agents/review/                         review gate (PRD 2.7) — every outbound text passes here
app/agents/insurer_sim/                    simulated insurer (demo only, labelled as such)
app/agents/audit.py                        record_action(): every tool call writes to `actions`
app/deadlines/                             deadline machine (PRD 2.5) -> scheduled_tasks
app/channels/telegram|email|voice/         Telegram, AgentMail, ElevenLabs adapters -> `events`
app/web/                                   onboarding site, mandate, consents, tracking page
bench/                                     benchmark: naive / LLM-only / agent on cases A, B, C
tests/                                     pytest
data/contrats/txt/                         12 public general conditions (\f = page break)
data/research/                             sourced research: clauses+pages (08a/08b), cases (08c), legal (09c)
```

Work inside your directory. Cross-cutting needs (new table, new event kind, new tool) go through `contracts.py` / a new migration and a short note in the commit message.

## Non-negotiable rules (from the PRD)

- Robin is a **pure procedural layer**: it never decides an amount, never advises, never accepts or waives anything. It documents, transmits, asks, follows up, explains facts.
- Every euro emitted comes from an `evidence` row, a `client_instruction` fact, or a formula whose every input is one of those and whose clause is cited.
- Every outbound message (Telegram, email, call brief, prefect letter) passes `app.agents.review` first and is logged in `review_log`.
- Every tool call writes a row in `actions` (`app.agents.audit`).
- Every date comes from a clause or a legal article (`source_clause_id` / `legal_basis`), never a universal clock.
- Never infer that a cover is not subscribed because a page is missing: `subscribed = unknown`.
- Facts and loss items are versioned (`supersedes`), never overwritten. Oral answers from an insurer are `insurer_oral` / `to_confirm` and never modify the coverage profile.
- No response from the client is never an acceptance.
- Banned words toward insurer / police / prefect (both languages): organised, gang, came on purpose, rioters, looters, premeditated — organisé(s), bande, venus exprès, casseurs, émeutiers, prémédité. Rewrite as plain facts (time, place, count).
- Webhooks answer in < 1 s: insert into `events`, return 200, let the worker do the work. Idempotency on `payload.provider_ref`.
- Isolation: every query filters by `account_id`.
- The simulated insurer is always labelled "simulated insurer" in UI and pitch. Do not add data services for logos.

## Verification

`.venv/bin/python -m pytest tests/` and a local run of `/health` with `db: ok` before pushing. For agent changes, run the relevant case in `bench/` and check `review_log` for false positives.
