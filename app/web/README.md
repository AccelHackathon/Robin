# B — Onboarding and Intake

The site adapts the supplied `Front` prototype to server-rendered FastAPI/Jinja2 pages. Assets and the original blue sky / sun design are bundled locally; no CDN is required.

## Run

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r pyproject.toml pytest pytest-asyncio
# Set DATABASE_URL in .env. Use a dedicated local database for development.
.venv/bin/python -m app.ingestion.load_corpus
.venv/bin/uvicorn app.main:app --port 8080 --reload
```

Migrations run at startup. The corpus CLI is idempotent and loads all 12 public documents (including the two IPIDs; they are not mislabelled as general conditions), 1,655 clauses. Clause bodies are verbatim, page-local text slices. Public corpus clauses have `account_id = NULL`; client documents always belong to their account.

Settings: `DATABASE_URL`, `OPENAI_API_KEY`, `INTAKE_MODEL` (default `gpt-4o`), `TELEGRAM_BOT_USERNAME`, `PUBLIC_BASE_URL`. Production must use HTTPS (`PUBLIC_BASE_URL=https://…`) so session cookies are Secure. Sessions are random opaque values stored only as hashes; no signing secret is needed. Passwords use Argon2, following the authoritative PRD section 9.

Without the model key, ingestion, uploads and onboarding still work. Candidate coverage stays `unknown` / low confidence. Only the explicitly labelled synthetic Karim schedule uses a deterministic fixture parser. No outbound messages are sent by B and no model result is fabricated. HEIC originals are accepted and retained; they currently require a PDF/JPG/PNG replacement for reading. Image OCR uses Claude when available.

## Integration with A and C

- `web/onboarding_done` is emitted exactly once after the mandate transaction. A owns its mailbox handler. Migration 200 transactionally fans it out into `web/document_added`, which B consumes. The shared worker now supports multiple handlers; B retains this separate queued event so intake and mailbox provisioning can complete independently.
- Uploads emit `web/document_added` transactionally with their document row. Duplicate uploads do not create a duplicate event.
- B writes `account_contracts`, `coverage_profile`, `contract_levers`, `deadline_rules`, `intake_tasks`, and `onboarding.welcome_brief`. The welcome brief is an **unsent draft**: C must review it before sending it through Telegram.
- SQL `coverage_profile.subscribed` stays boolean/NULL; the web API serializes yes/no/unknown. `source_clause_id` is bigint. Private `search_clauses` and `verify_quote` calls must pass `account_id=`; two-argument calls only access public corpus clauses.
- `deadline_rules.rule` includes `status`, `amount`, `unit`, `trigger`, `conditions`, and `requires_claim_context` for extracted rules. Candidate-only rules include their source text and `status=to_confirm`; C must not instantiate these as established deadlines. No universal deadline is inferred.
- `link_codes` are single-use 15-minute codes for C to consume atomically. B's renewal expires earlier unused codes. B polls actual `telegram_links` and communication delivery status; clicking a link never counts as connected.
- Urgent onboarding skips documents. Its narrative is saved in `onboarding.incident` and included in `onboarding_done`. **C still needs to consume the urgent narrative for claim triage**; B deliberately does not write C's claims/facts or pretend a declaration was sent.
- Tracking is read-only. Account owners can mint or rotate a private bearer link with `POST /claims/{id}/tracking-link` (CSRF required). Only its SHA-256 is stored in `claims.tracking_token_hash`. Rotating invalidates the previous link. Link holders can view that one claim, not download private originals or access other claims.
- The shared worker currently leaves crashed `processing` events unrecovered. C owns retry/recovery changes. B's stored writes and cached extractions are idempotent on replay and account-level advisory locking serializes versions.

## Fixtures and verification

```sh
.venv/bin/python data/fixtures/generate_karim.py
.venv/bin/python data/fixtures/generate_karim.py --ceiling 30000
ROBIN_TEST_DATABASE_URL=postgresql://…/robin_b_tests .venv/bin/python -m pytest tests/
```

Tests use a dedicated database and never send to external providers. They cover page preservation, citation/amount checks, session invalidation, CSRF, upload validation/deduplication, account isolation, missing-schedule unknowns, mandate idempotence, event fan-out, link expiry, urgent routing and endorsement versioning. Real OpenAI/Telegram/AgentMail execution and production loading are separate integration checks requiring the team's configuration.

## Important scope details

The mandate record includes its exact scope, version, typed name, capacity, timestamp, and account identity. No offer acceptance, waiver, settlement or fund collection is delegated. The operating legal entity and launch privacy/retention texts still need the team's H1 details before use with real customers.

No production deployment is performed by running the site or test suite. Use the repository's Aiven deployment workflow after production credentials and cross-stream handlers are configured.
