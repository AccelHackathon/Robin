# Workstream A — Voice & insurer side

**Owner:** Emile. **PRD sections:** 2.8 (expertise), 2.11 (Insurer Simulator), 3.2 rows `channels/voice`, `channels/email`, `agents/insurer_sim`; AC-8, AC-9 (release detection input), 7.2 (call failure messages).

## Status (updated 11:10)

- [x] Twilio trial number `+1 573 538 3826` imported into ElevenLabs (`phnum_0301m5hhx7rvfv7rftfxav8hc6ts`); outbound call reaches `+33 6 47 50 23 84` (press any key at the Twilio trial prompt)
- [x] Production agent `agent_1101m5hj0xtfftsa51r6tr0g3wjy` configured (procedural-layer prompt, data-collection for the structured result), provisioning script `app/channels/voice/agent.py`
- [x] Post-call webhook (`/webhooks/elevenlabs`, HMAC-verified) → `calls` + `call_ended` event; widget fallback `/voice/widget/{call_id}`
- [x] `start_call` adapter (`app/channels/voice/call.py`)
- [x] AgentMail: mailbox per account (on `onboarding_done`), `send_email` adapter, inbound webhook (Svix-verified) → documents + `email_received`, French templates
- [x] Insurer Simulator Agent — **tested end to end on production**: declaration → ack with reference + document requests; offer step attaches the "solde de tout compte" release PDF
- [x] Simulated insurer inbox `sinistres-demo-assureur@agentmail.to`; AgentMail webhook registered
- [x] Live post-call webhook **tested twice on production** (commit `1275f7c` deployed): HMAC verified, `reached_human`, structured answers with rationale when the insurer does not answer, `call_ended` emitted and consumed by C's handler (0 failed events)
- [x] Reconciliation watcher for calls without webhook (Twilio check at 90 s / 240 s, 8-minute timeout, startup sweep) — code deployed, real no-answer run not yet exercised (both test calls were answered)
- [x] French language preset + `language_detection` tool on the agent
- [x] `POST /internal/calls` (bearer `INTERNAL_API_TOKEN`) to start a call on a claim during rehearsals; rehearsal claim `800cdd2d-7130-4722-a804-d6afdf1817d4` (account `demo-karim@robin.local`) exists in production; the live demo account is `thibault@robin-demo.fr` (Thibault Phone Repair, Marseille)
- [ ] Optional: one real "let it ring" call to watch the `voicemail_or_no_answer` path

Integration notes for the merge: `call_ended` payload = `{call_id, transcript, structured_result{reached_human, answers[{question_index, answered, answer_summary, answer_verbatim, rationale, confidence}], insurer_reference, documents_requested, summary}, status, finalized_by}`; `email_received` payload carries `mailbox_role` (`agent` → C, `simulated_insurer` → A). Secrets on Runtime: all of stream A's are set; still missing globally: `TELEGRAM_BOT_TOKEN`. LLM provider is OpenAI only (`app/llm.py`).

## Owned paths

```
app/channels/voice/        routes.py (webhooks), call.py (start_call adapter), agent.py (ElevenLabs agent config), handlers.py
app/channels/email/        routes.py (webhook), send.py (send_email adapter), mailboxes.py (create per account), handlers.py
app/agents/insurer_sim/    graph.py (LangGraph), scenarios.py (scripts), handlers.py
app/migrations/1xx_*.sql
tests/test_voice_*.py, tests/test_email_*.py, tests/test_insurer_sim_*.py
```

## Deliverables

### A1. Voice — ElevenLabs Agents + Twilio

1. **`start_call` adapter** (`app/channels/voice/call.py`, signature in README): builds the dynamic variables from the brief, calls `POST /v1/convai/twilio/outbound-call`, inserts a `calls` row (`status = requested`, `provider_ref = conversation_id`), writes `communications` (channel `phone`, direction `outbound`), records the action. Reads `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_PHONE_NUMBER_ID`, `INSURER_TEST_PHONE` from settings (add them to `app/config.py`).
2. **Agent configuration** (`agent.py`): one production agent, created/updated by a script. Prompt rules (PRD principle): Robin is a procedural assistant under a written mandate; asks the listed questions one at a time; never negotiates, accepts, waives, gives opinions; states that every answer will be confirmed in writing; ends politely. Language: English for the demo; a `language` dynamic variable to switch to French later. Dynamic variables: `business_name`, `policy_number`, `claim_ref`, `loss_date`, `loss_summary`, `call_goal`, `questions`, `insurer_name`.
3. **Post-call webhook** (`routes.py`, `POST /webhooks/elevenlabs`): verify the HMAC signature (ElevenLabs `xi-signature` header, secret in `ELEVENLABS_WEBHOOK_SECRET`), answer 200 in < 1 s, enqueue `("elevenlabs", "call_ended")` with `account_id`, `claim_id`, `call_id`, transcript, `structured_result`. Configure the webhook URL in ElevenLabs to `https://<runtime-url>/webhooks/elevenlabs`.
4. **Structured result**: use the agent's data-collection / analysis feature to produce, per question, `{question, answer_verbatim, answer_summary, confidence}` plus `{reached_human: bool, callback_requested: bool, insurer_reference: str|null}`. Store in `calls.structured_result`, set `calls.status = completed`, `ended_at`, `transcript`.
5. **Provenance rule**: the webhook handler never touches `coverage_profile` or `facts`. C turns the result into `facts` with `source_kind = insurer_oral`, `status = to_confirm` (AC-8). Your job is to deliver the structured result reliably.
6. **Failure modes**: no answer / busy / voicemail → `calls.status = failed`, enqueue `call_ended` with `structured_result = {reached_human: false, reason}` so C can fall back to email (PRD 7.2). Twilio trial "press any key" prompt: documented in the README; the live "insurer" presses a key.
7. **Fallback**: ElevenLabs web widget page at `GET /voice/widget/{call_id}` (served by your router) with the same agent and dynamic variables, for a demo without telephony.

### A2. Email — AgentMail

1. **Mailbox per account** (`mailboxes.py`): on `("web", "onboarding_done")` — register a handler in `app/channels/email/handlers.py` — create an AgentMail inbox (e.g. `robin-<slug>@agentmail.to`), insert into `mailboxes` (`role = agent`). Free tier: 3 inboxes. Create the `simulated_insurer` inbox once (seed/CLI).
2. **`send_email` adapter** (`send.py`, signature in README): fetch attachments from `documents.content`, send through the AgentMail API, insert `communications` (channel `email`, direction `outbound`, `provider_ref` = message id, `language`), record the action. Retry 3× with backoff on 5xx; on final failure write `failed_reason` and return the communication id anyway (C decides what to tell the client).
3. **Inbound webhook** (`routes.py`, `POST /webhooks/agentmail`): verify signature, answer 200 fast, store attachments as `documents` (`origin = email`, `doc_type = correspondence|other`, `sha256`), insert `communications` (inbound), enqueue `("agentmail", "email_received")` with the mailbox role so the worker routes it to C (role `agent`) or to the simulator (role `simulated_insurer`). Resolve `claim_id` from the subject tag `[RB-<claim short id>]` that outbound emails always carry.
4. **Insurer document requests**: template bodies (French) for `request_insurer_document(kind)` — signed CG/CP, proof of delivery, expert report (PRD 2.8). C calls `send_email` with them; you provide the templates in `app/channels/email/templates/*.j2`.

### A3. Insurer Simulator Agent (demo only, always labelled "simulated insurer")

1. Separate LangGraph (`graph.py`) with its own Postgres checkpointer thread per inbound email thread. Input: the inbound email only — it never reads Claims Agent memory (`claims`, `facts`, `loss_items` are off limits; enforce in code by only querying `communications` of the simulator mailbox).
2. **Scenario script** (`scenarios.py`, "karim_default"):
   1. First declaration received → acknowledgement with a claim reference `SIN-2026-xxxx`, request for the police report and the number of customer devices in repair.
   2. Loss statement received → asks for supplier invoices for the stock and the last inventory; mentions the theft cover cap.
   3. Written confirmation request after the call → replies that stock stolen during riots is handled under the theft cover, 15 000 € cap, "sous réserve de l'expertise".
   4. Complements received → **offer** ≈ 20 750 € (stock at the 15 000 € theft cap, shopfront 3 600 €, shutter and till after 30 % depreciation 3 150 €, minus 1 000 € deductible) **with an attached PDF "quittance d'indemnité pour solde de tout compte"** (generate it) so C's release-language detection (AC-9) fires.
   5. Contest received → "transmis à l'expert", delay.
3. Replies are in **French**, realistic insurer tone, delay 10–30 s (asyncio sleep in the handler, or a `scheduled_tasks` row), signed "Service Indemnisation — SIMULATED INSURER (demo)".
4. Every reply goes through `review()` too (it must not contain banned words either) and is logged.

## Acceptance

- A-1: `start_call` from a seeded claim rings the verified phone; the post-call webhook creates a `call_ended` event with a non-empty `structured_result` within 30 s of hang-up.
- A-2: An email sent via `send_email` from Karim's mailbox lands in the simulator mailbox; the simulator replies; the reply appears as an `email_received` event with `account_id` and `claim_id` resolved.
- A-3: The offer email carries the release PDF; `documents` has it with `doc_type = correspondence`.
- A-4: No simulator code path reads `claims`/`facts`/`loss_items` (grep in tests).

## Order of work

1. `start_call` + post-call webhook + `call_ended` event (unblocks C's AC-8). 2. AgentMail send + inbound webhook (unblocks C's email tools). 3. Mailbox-per-account handler. 4. Simulator scenario steps 1–4. 5. Widget fallback. 6. Production prompt polish, French variant.

## Secrets / config you own

`ELEVENLABS_API_KEY` (set), `ELEVENLABS_AGENT_ID`, `ELEVENLABS_PHONE_NUMBER_ID`, `ELEVENLABS_WEBHOOK_SECRET`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `INSURER_TEST_PHONE`, `AGENTMAIL_API_KEY` (set), `AGENTMAIL_WEBHOOK_SECRET`, `SIMULATED_INSURER_EMAIL`. Local values are in `.env`; push them to Runtime with the Aiven MCP.
