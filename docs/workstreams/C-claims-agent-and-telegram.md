# Workstream C — Claims Agent & Telegram

**Owner:** teammate 2. **PRD sections:** 2.3 (Claims Agent), 2.4 (living loss statement), 2.5 (deadline machine per claim), 2.6 (provenance), 2.7 (review gate), 2.9 (offer presentation), 2.12 (benchmark), 2.13 workflows, 3.2 rows `agents/claims`, `agents/review`, `deadlines`, `channels/telegram`, `bench`; AC-3, AC-4, AC-5, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15.

## Status

- [ ] Telegram bot created (BotFather) and token set on Runtime
- [ ] Linking `/start <code>` → `telegram_links`, welcome message
- [ ] Claims Agent graph with Postgres checkpointer; resume on events
- [ ] Tools implemented (12)
- [ ] Review gate (8 controls) + `review_log`
- [ ] Deadline instantiation per claim
- [ ] Offer presentation + release-language detection
- [ ] Benchmark A/B/C × 3 variants

## Owned paths

```
app/agents/claims/         graph.py, state.py, nodes/*.py, tools.py (implement the stubs), prompts.py, memory.py, handlers.py
app/agents/review/         gate.py (review()), rules.py (banned/allowed phrases FR+EN), amounts.py (traceability), citations.py
app/deadlines/             instantiate.py (per claim, from B's rules), followups.py
app/channels/telegram/     bot.py (python-telegram-bot, long polling in dev), routes.py (webhook in prod), send.py (adapter), media.py, transcribe.py, handlers.py
bench/                     run.py, cases/{a_karim,b_bakery,c_optician}.json, variants/{naive,llm_only,agent}.py, report.md (generated)
app/migrations/3xx_*.sql
app/main.py, app/db.py, app/worker.py, app/config.py, app/contracts.py   (shared core — you are the gatekeeper; apply others' requests quickly)
tests/test_claims_*.py, tests/test_review_*.py, tests/test_telegram_*.py, tests/test_bench_*.py
```

## Deliverables

### C1. Telegram channel (first — it is the client's screen)

1. Create the bot with @BotFather (name suggestion: `RobinClaimsBot`), set `TELEGRAM_BOT_TOKEN` locally and on Runtime (Aiven MCP, full variable list), and `TELEGRAM_BOT_USERNAME` (B's deep link needs it).
2. `bot.py`: `python-telegram-bot` application. Dev: long polling started in `main.py` lifespan when `TELEGRAM_MODE=polling`. Prod: webhook `POST /webhooks/telegram/<token>` (`routes.py`), set with `setWebhook` at startup when `PUBLIC_BASE_URL` is set. Either way the handler only **enqueues** (`telegram`/`message` or `document`) and returns.
3. `/start <code>`: consume `link_codes` (unexpired, unused) → insert `telegram_links` → send the welcome message built from B's `write_welcome_brief` (English, covers + caps + deductibles + page refs). `/start` without a valid code → explain how to link from the website. Never link on a phone number alone.
4. `media.py`: photos, documents, voice → `getFile` → `documents` (`origin = telegram`, `sha256`, `mime_type`); voice `.oga` → `transcribe.py` (ElevenLabs Scribe with `ELEVENLABS_API_KEY`, or OpenAI Whisper with `OPENAI_API_KEY`) → text stored on the document and passed as the message text.
5. `send.py` adapter `send_telegram(...)` (README signature): sends text/documents to the account's chat, writes `communications`, returns id. Rate limit 30 messages / chat / 10 min.

### C2. Claims Agent (LangGraph)

- `state.py`: typed state (claim id, account id, inbound event, memory snapshot, drafts, pending wait type).
- `graph.py`: nodes `load_memory → triage → analyze → act → review → wait → present_offer` exactly as PRD 2.3; `langgraph-checkpoint-postgres` `AsyncPostgresSaver` on the same `DATABASE_URL` (call `.setup()` once at startup, it creates its tables); `thread_id = claim_id`.
- `handlers.py`: route events into the graph:
  - `telegram/message|document` with no open claim → `triage` decides: question about the contract (answer from memory, no claim) or new loss → create `claims` row, start a thread.
  - any event for an account with an open claim whose thread is interrupted → `Command(resume={"wait_type": ..., "event": ...})`.
  - `agentmail/email_received` (mailbox role `agent`), `elevenlabs/call_ended`, `scheduler/followup_due` → resume the matching claim thread.
- `triage` rule (AC-3): a new loss triggers the **initial declaration email the same day, before any evidence request**. Minimum content: date, place, nature of the loss, policy number, mandate attached, "detailed loss statement to follow". Language French (insurer). Through `review()`.
- `analyze`: vision extraction via `read_document` (Claude; cache by sha256), facts with `source_kind`, evidence rows with duplicate detection (`sha256`, then `(amount, date, vendor)`) → `duplicate_of` + message to the client (AC-4); loss items versioned, each with evidence ids + clause id + page + quote + computation; walk B's `loss_catalog` and B's `coverage_profile`; ventilate by cover (theft vs damage vs BI); recompute stock at purchase price when the client gives retail prices, citing the clause (AC-13).
- **Derived amounts rule**: an amount is traceable if it is on an evidence, is a `client_instruction` fact, or is computed by a formula whose every input is one of those and whose clause is cited (`computation_detail`). This is how business interruption passes the gate.
- `act`: tool selection with Claude tool-use; each tool writes `actions` via `app.agents.audit`.
- `wait`: `interrupt()` typed (`WaitType` in contracts). Set `claims.status` accordingly.
- `present_offer` (AC-9): item-by-item comparison, nature (advance/provisional/final), **release-language detection** on the offer email and attachments ("quittance", "solde de tout compte", "renonciation", "transaction", "définitif", "pour solde") → `offers.has_release_language`, factual explanation of the effect, then `awaiting_signature_decision`. No answer is never acceptance; reminders at J+3 and J+7. Decisions: `accept` → payment tracking + replacement-value top-up task; `contest` → the client gives items and figures, Robin transmits; `ask` → details.
- Tools (`tools.py`): implement all 12 stubs. `send_email`/`start_call` call A's adapters; `ask_client` calls `send_telegram` after `review()`.
- Memory: read the tables directly (no LangGraph Store needed); `get_claim_memory` returns one dict used by prompts.

### C3. Review gate (`app/agents/review/gate.py`)

`review(draft, ctx) -> ReviewResult`, the 8 controls of PRD 2.7, deterministic checks first, LLM judge second:
1. evidence: each loss item sent has ≥ 1 evidence and 1 existing clause;
2. citation: `verify_quote` (B's `app.ingestion.search.verify_quote`, normalised similarity ≥ 0.9);
3. duplicates: none counted;
4. **traceable amounts**: every number in `draft.amounts_eur` ∈ evidence ∪ derived ∪ client_instruction (tolerance 0.5 €);
5. no promise/acceptance (regex FR+EN + judge);
6. no personalised advice (judge, with an **allowed phrasing list** in `rules.py`: "The offer covers X of Y documented", "Your policy provides…", "You can accept, ask for details, or contest", "Options that exist: …");
7. banned words FR+EN (`rules.py`) → rewrite into plain facts;
8. no unconfirmed facts in external sends.
Every call writes `review_log`. Failures return to `analyze` with the violations; the third failure on the same draft → ask the client.

### C4. Deadlines per claim (`app/deadlines/`)

From B's deadline rules and the `riot_events` match (`claims.riot_event_id`), instantiate `scheduled_tasks` for the claim: police report, declaration (30 days for the 17–18/10 event), loss statement, insurer follow-up J+7 after each request, payment 30 days after agreement, replacement-value top-up J+700, prescription alert J-90, State recourse 2030-12-31, client reminders J+3/J+7 on the offer. `kind`, `source_clause_id`/`legal_basis`, `missed_at` when passed (continue, inform factually — PRD 2.5 failure mode). The worker already fires due tasks as `followup_due` events.

### C5. Benchmark (`bench/`)

Cases A (Karim / MAAF), B (bakery / AXA Atouts PME), C (optician / Generali 100% Pro) from `data/research/08c` §6, ground truth from `08a/08b` (clause + page) and `08c` §6 (items). Variants: `naive` (the "declared alone" column), `llm_only` (same model, same narrative, no clauses, no invoices), `agent` (the Claims Agent with the ingested contract and fixture evidence). Metrics: € identified, recall of claimable items, % correct citations (page exists and `verify_quote` passes), untraceable amounts (must be 0), tokens, latency. Output `bench/report.md` with a table for the slide. **No number on the slide that was not produced by this script.**

## Acceptance

AC-3, AC-4, AC-5 (≥ 90 % of case A items with evidence + clause + page), AC-7 (restart the service mid-wait on production, send the next message, the thread resumes, no action replayed), AC-8 (call result → `insurer_oral`/`to_confirm`, profile unchanged, written confirmation email sent), AC-9, AC-10, AC-11, AC-12, AC-13, AC-15.

## Order of work

1. Bot + linking + welcome (needs B's `link_codes` and brief; stub the brief until then). 2. Graph skeleton with checkpointer + resume on a Telegram message (AC-7 early). 3. `read_document`, `search_clauses`, `update_loss_statement`, `analyze` on seeded Karim evidence. 4. Review gate deterministic controls. 5. Initial declaration + `ask_client` + dedup (AC-3, AC-4). 6. Email/call events → facts (AC-8), offer presentation (AC-9). 7. Deadlines. 8. Benchmark. 9. LLM judge controls, allowed phrasing, polish.

## Config you own

`TELEGRAM_BOT_TOKEN`, `TELEGRAM_MODE` (`polling|webhook`), `PUBLIC_BASE_URL`, `ANTHROPIC_API_KEY` (shared with B).
