# Workstream D — Risk Sentinel (continuous monitoring)

**Owner:** Emile. **Why:** the system reacted only to the client's messages; the Sentinel makes Robin proactive. It watches external risks for each business (protests, riots, weather vigilance, nearby fires, access strikes, burglary waves, insurer/government measures), alerts the client on Telegram with sourced facts and the policy's own terms, and turns those alerts into evidence when a loss follows.

## Status

- [x] Keenable HTTP client (`search`, `fetch` with extraction prompt), usage recorded in `actions`
- [x] Migration 110: `risk_profiles`, `watch_queries`, `alerts`, `alert_sources`, `sentinel_sweeps`
- [x] Risk taxonomy → covers, query templates, practical measures (`risks.py`); risk profile from B's tables (`profile.py`)
- [x] LangGraph sweep: profile → plan → search → triage → fetch → assess → dedupe → compose → gate → notify → persist
- [x] Scheduler (every minute, due accounts → `sentinel/sweep_due`), arming on `onboarding_done`, alert↔claim linking
- [x] Operator endpoints `/internal/sentinel/sweep`, `/internal/sentinel/alerts`
- [x] Real sweeps verified locally for a Marseille account (floods in Bouches-du-Rhône 19–20 Oct, protest bans) — alerts pass the review gate
- [ ] Real Telegram notification (needs a valid `TELEGRAM_BOT_TOKEN` on Runtime; the one provided is rejected by Telegram)
- [ ] Tracking page: show alerts (B's page could read `alerts` + `alert_sources`)

## Owned paths

```
app/agents/sentinel/       graph.py, profile.py, risks.py, handlers.py, scheduler.py, routes.py
app/channels/web_search/   keenable.py
app/migrations/11x_*.sql
tests/test_sentinel.py
```

## How it behaves

- **Profile**: address → city/department (postcode), activity → vehicles, latest `coverage_profile` facts, `deadline_rules`. A cover that is `unknown` is still watched (never assume "no").
- **Queries**: ≤ 2 per risk, ≤ 10 per sweep, French, localised (`{city}`, `{department}`, `{street}`), `published_after = 48h` so only fresh pages count. Each query is stored in `watch_queries` with its last hit count.
- **Triage** (gpt-4o, one call for all hits): keeps concrete, dated, local events; drops opinion and other cities. **Fetch** with a Keenable extraction prompt (place, window, issuer, verbatim French sentence). **Assess** (gpt-4o per candidate): relevance, severity (critical/high/medium/low), `event_phase` upcoming/ongoing/past, best risk key, cover concerned, official source flag.
- **Dedupe** on `sha1(risk_key | normalised place | date)`: five newspapers covering one protest = one alert; new sources are attached to the existing alert.
- **Message** (English, to the client): facts + source URL (+ "official"), the policy's cover status with page references and caps, contractual conditions with pages, general precautions explicitly labelled "not contractual, not advice on a claim", the declaration deadline (from `deadline_rules` or L113-2 / 30-day France Assureurs measure). Past events ask whether damage occurred instead of giving precautions.
- **Gate**: every alert goes through `app.agents.review.gate.review()` (deterministic controls); blocked alerts are stored with `status = review_blocked`.
- **Notify**: `send_telegram()` when the account has a linked chat and severity ≥ `SENTINEL_MIN_SEVERITY_TO_NOTIFY` (default medium). Otherwise stored as `new` / `below_threshold`.
- **Evidence loop**: when a claim appears for the account, `link_alerts_to_claim()` attaches alerts whose window (± 2 days) covers the loss date, so their sources document the external event (cause for art. 1733, riot-event match for the State recourse).

## Events and interfaces

| source | kind | emitted by | consumed by | payload |
|---|---|---|---|---|
| `sentinel` | `sweep_due` | scheduler (`scheduler.py`) | D (`handlers.py`, background task) | `{account_id, provider_ref}` |
| `web` | `onboarding_done` | B | D arms monitoring (first sweep +3 min) | — |
| `telegram` | `message` / `document` | C | D links alerts to the newest claim | — |

Reads: `businesses`, `coverage_profile`, `deadline_rules`, `telegram_links`, `claims`. Writes: its own tables + `actions`, `review_log` (via gate). Calls: `review()` (C), `send_telegram()` (C), Keenable, OpenAI.

## Config

`KEENABLE_API_KEY` (set on Runtime), `KEENABLE_SEARCH_MODE` (realtime), `SENTINEL_ENABLED`, `SENTINEL_INTERVAL_MINUTES` (15), `SENTINEL_LOOKBACK_HOURS` (48), `SENTINEL_MIN_SEVERITY_TO_NOTIFY` (medium). Cost per sweep: ~10 Keenable realtime searches + ≤ 4 fetches (1 credit each) + ~5 gpt-4o calls.

## Demo

`POST /internal/sentinel/sweep {"account_id": ...}` on the Thibault demo account (`thibault@robin-demo.fr`, Marseille, account `c83fab57-aec9-4611-9dec-4dfd1631ee46`) returns live alerts in ~30 s; with Telegram linked the alert lands in the client's chat. Then declare a loss in the same window: the alert is linked to the claim as evidence.
