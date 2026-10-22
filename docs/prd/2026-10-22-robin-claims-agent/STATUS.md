# STATUS — Robin claims agent

PRD: `PRD.md` (same folder). Updated: 2026-10-22.

## Current phase

- [ ] H0 — hackathon demo (pitch 4 pm, results 5 pm)
- [ ] H1 — first real users
- [ ] H2 — launch

## Blockers

| # | Blocker | Impact | Owner | State |
|---|---|---|---|---|
| B1 | Aiven organisation admin role for GitHub → Runtime link | H0 deployment | ? | **Open** |
| B2 | ElevenLabs credits + verified Twilio number | Step 8 (degradable) | ? | Open |
| B3 | Benchmark contracts B/C not assigned | Step 5 | ? | Open |

## H0 tasks

| # | Task | Depends on | Unblocks | State |
|---|---|---|---|---|
| 1 | FastAPI skeleton + Dockerfile + Runtime + PG + test migration | — | everything | Ready |
| 2 | Ingestion of 12 CG + Intake (MAAF + Karim CP) → profile, levers, deadlines | 1 | 3, 5 | Blocked by 1 |
| 3 | Minimal Claims Agent + **review node (8 checks)** | 1 | 4, 5, 6 | Blocked by 1 |
| 4 | Telegram: deep link, media, ask_client, interrupt/resume, deduplication, resume test | 3 | 7 | Blocked by 3 |
| 5 | `bench/` 3 cases × 3 variants | 2, 3 | slide | Blocked by 2, 3 |
| 6 | AgentMail + Insurer Simulator (with release) | 3 | 7 | Blocked by 3 |
| 7 | Reduced onboarding site + mandate + 3 consents | 2 | demo | Blocked by 2 |
| 8 | ElevenLabs call + post-call + oral provenance | 6 | demo | Blocked by 6 (degradable → widget) |
| 9 | Telegram voice notes, resume demonstrated, pitch | 4, 6 | — | Blocked |

Parallelism: 2 ‖ 3 · 4 ‖ 6 · 7 ‖ 8. **1–5 non-negotiable.**

## Acceptance criteria to tick before the pitch

- [ ] AC-1 MAAF coverage profile with pages
- [ ] AC-3 Day-0 declaration before any document request
- [ ] AC-4 duplicate refused
- [ ] AC-6 endorsement changes the ceiling
- [ ] AC-7 resume after restart
- [ ] AC-8 oral answer `to_confirm`
- [ ] AC-9 release detected, no implicit acceptance
- [ ] AC-11/12 review blocks advice and unsourced amount
- [ ] AC-15 bench measured (no unmeasured figure on the slide)
- [ ] AC-16 two-account isolation

## Open questions (see PRD §6)

Q1 Aiven admin · Q3 voice · Q4 language to insurer · Q6/Q7 legal advice + compensation · Q8 verify case-law reference numbers on Légifrance before display · Q9 contracts B/C.

## Log

| Date | Event |
|---|---|
| 2026-10-22 | PRD v1 written from CONTEXTE §1–14, 08a–08d, 09a–09c |
