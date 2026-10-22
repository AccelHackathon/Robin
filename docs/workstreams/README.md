# Workstreams — how three people (and their agents) build Robin in parallel

Product spec: `docs/prd/2026-10-22-robin-claims-agent/PRD.md` (authoritative). Conventions: `AGENTS.md`. This folder splits the PRD into three independent workstreams with explicit interfaces so nobody blocks anybody.

| Stream | Owner | Scope | Spec |
|---|---|---|---|
| **A — Voice & insurer side** | Emile | ElevenLabs calls (Twilio), AgentMail email channel, Insurer Simulator Agent | `A-voice-and-insurer.md` |
| **B — Onboarding & Intake** | teammate 1 | Web onboarding site, contract ingestion (12 CG), Intake Agent (coverage profile, levers, traps, deadlines), seeds | `B-onboarding-and-intake.md` |
| **C — Claims Agent & Telegram** | teammate 2 | LangGraph Claims Agent, tools, review gate, Telegram channel, benchmark | `C-claims-agent-and-telegram.md` |

## What is already done (do not redo)

- FastAPI skeleton, async psycopg pool, SQL migrations at startup, in-process event worker (`app/worker.py`), `/health`.
- Schema: migrations `001` + `002` (26 tables aligned with PRD §3.4).
- Shared types: `app/contracts.py` (PRD §5). Tool contract: `app/agents/claims/tools.py`. Audit helper: `app/agents/audit.py`.
- Routers and handler modules for every stream are **already registered in `app/main.py`** (empty). You fill your own files; you never edit `main.py`.
- Production: Aiven Runtime app `robin` + PostgreSQL `pg-3f9bc500`, `/health` returns `db: ok`. Secrets set: `AGENTMAIL_API_KEY`, `ELEVENLABS_API_KEY`, `OPENAI_API_KEY` (the only LLM provider; see `app/llm.py`). Missing: `TELEGRAM_BOT_TOKEN`.
- Voice test passed: Twilio number `+1 573 538 3826` imported in ElevenLabs (`phnum_0301m5hhx7rvfv7rftfxav8hc6ts`), test agent `agent_1101m5hj0xtfftsa51r6tr0g3wjy`, outbound call reaches the verified phone. Twilio trial plays "press any key" before connecting.

## Git rules (the whole point is not stepping on each other)

1. Everyone works on `main`. No long-lived branches: integration pain grows with branch age.
2. **Commit every 20–30 minutes**, small and green (`import app.main` must succeed, `/health` must answer).
3. Before every push: `git pull --rebase origin main`, re-run the import check, then `git push`. Never `--force`.
4. **Only touch your own paths** (listed in each spec). Shared files have one owner:

   | File | Owner | How others request changes |
   |---|---|---|
   | `app/main.py`, `app/db.py`, `app/worker.py`, `app/config.py` | C | Post the needed change in the team chat; C applies it within minutes. New settings: add to `app/config.py` yourself, one line, and say so. |
   | `app/contracts.py` | C | Additive only (new fields with defaults, new Literal values). Say so in the commit message. |
   | `app/migrations/` | each stream has its own number range: **A = 1xx, B = 2xx, C = 3xx** | Never edit an applied migration. Additive only. |
   | `docs/workstreams/*.md` | each owner | Keep "Status" at the top of your spec current; it is how the others know where you are. |

5. Commit messages in English, imperative, with the stream letter: `[A] Add ElevenLabs post-call webhook`.
6. Deploy: pushing does not deploy. Any owner can redeploy with the Aiven MCP (`aiven_application_redeploy`, project `larp`, service `robin`) or the console. Redeploy after each meaningful green push; check `/health`.
7. Secrets go in Runtime environment variables (via Aiven MCP `aiven_service_update`, re-sending the **whole** list) and in the local `.env` (gitignored). Never in git.

## Interfaces between streams

Everything crosses stream boundaries through **the database** and **the event queue**, never through direct function calls into another stream's internals, except for the three adapter functions listed below.

### Event queue (`events` table, `app.worker.enqueue`)

| source | kind | emitted by | consumed by | payload |
|---|---|---|---|---|
| `web` | `onboarding_done` | B (site) | B (Intake handler) | `{account_id}` |
| `web` | `document_added` | B (site) | B (Intake handler) | `{account_id, document_id}` |
| `telegram` | `message` | C (bot) | C (claims handler) | `{account_id, chat_id, text, provider_ref}` |
| `telegram` | `document` | C (bot) | C (claims handler) | `{account_id, chat_id, document_id, mime_type, caption, provider_ref}` |
| `agentmail` | `email_received` | A (webhook) | C (claims handler) if the mailbox role is `agent`; A (insurer_sim handler) if role is `simulated_insurer` | `{account_id, mailbox_id, communication_id, from, subject, body_text, attachment_document_ids, provider_ref}` |
| `elevenlabs` | `call_ended` | A (webhook) | C (claims handler) | `{account_id, claim_id, call_id, transcript, structured_result, provider_ref}` |
| `scheduler` | `followup_due` | worker (already implemented) | C (claims handler) | `{task_id, reason}` + `claim_id` column |

`account_id` and `claim_id` are columns on `events`; set them when known. `payload.provider_ref` must be unique per provider message (idempotency index exists).

### Adapter functions (the only cross-stream imports)

Implemented by **A**, called by **C**'s tools:

```python
# app/channels/email/send.py
async def send_email(*, account_id: str, claim_id: str | None, to: str, subject: str, body: str,
                     attachment_document_ids: list[str], language: str) -> str:
    """Sends from the account's agent mailbox. Writes `communications`. Returns communication_id."""

# app/channels/voice/call.py
async def start_call(*, account_id: str, claim_id: str, to_number: str, goal: str,
                     questions: list[str], brief: dict) -> str:
    """Starts an ElevenLabs outbound call. Writes `calls` (status requested). Returns call_id.
    The result arrives later as an ("elevenlabs", "call_ended") event."""
```

Implemented by **C**, called by **A**'s simulator and by **B**'s site:

```python
# app/channels/telegram/send.py
async def send_telegram(*, account_id: str, text: str, document_ids: list[str] = ()) -> str:
    """Sends to the account's linked chat. Writes `communications`. Returns communication_id."""
```

Implemented by **C** (review gate), called by **A** before any simulated-insurer email and by **B** for any outbound text:

```python
# app/agents/review/gate.py
async def review(draft: OutboundDraft, ctx: ReviewContext) -> ReviewResult
```

### Database handoffs

| Table | Written by | Read by | Notes |
|---|---|---|---|
| `accounts`, `businesses`, `mandates`, `consents` | B | C (memory), A (email identity, call brief) | |
| `link_codes` | B (creates on onboarding end) | C (`/start <code>` consumes, writes `telegram_links`) | 15-minute expiry |
| `mailboxes` | A (creates on `onboarding_done`, role `agent`) | C (`send_email` picks the account mailbox) | A also owns the `simulated_insurer` mailbox |
| `documents`, `clauses` | B (contracts, web uploads), C (Telegram uploads), A (email attachments) | everyone | `doc_type` from `app.contracts.DocType`; `sha256` always set |
| `coverage_profile`, `contract_levers`, `loss_catalog`, `riot_events` | B | C | versioned; `subscribed = unknown` when not established |
| `scheduled_tasks` (contract deadlines) | B (Intake extracts), C (follow-ups) | worker fires → C | `kind`, `source_clause_id`, `legal_basis` |
| `claims`, `facts`, `evidence`, `loss_items`, `offers`, `payments` | C | A (call brief), B (tracking page) | |
| `communications` | A (email), C (Telegram), A (calls summary) | everyone | |
| `calls` | A | C | `structured_result` schema in spec A |
| `actions`, `review_log` | everyone via helpers | bench, observability | |
| LangGraph checkpoint tables | C | — | created by the library |

### Demo scenario (shared, PRD 2.13 W1)

Karim, phone repair shop, Marseille. MAAF general conditions 11031 (01/2026) + synthetic particular conditions (B produces the PDF: riot extension, theft capped 15 000 €, business interruption with a 3-day deductible, replacement value on equipment, 1 000 € general deductible). The simulated insurer (A) answers emails; the live call (A) is answered by Emile. Telegram (C) is the client's screen. The site (B) is the opening minute.

## Rhythm

- Each owner updates the **Status** block at the top of their spec with every push.
- Integration checkpoint: once A, B and C each have their first acceptance item green, run workflow W1 end to end on production, then rehearse the demo.
