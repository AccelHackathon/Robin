"""Benchmark (PRD 2.12, AC-5, AC-15): naive declaration vs LLM-only vs Claims Agent on cases A/B/C.

    PYTHONPATH=. .venv/bin/python bench/run.py            # all cases, writes bench/report.md
    PYTHONPATH=. .venv/bin/python bench/run.py --case A

Needs DATABASE_URL with the 12 contracts ingested (app.ingestion.load_corpus) and OPENAI_API_KEY for
the two model-backed variants. Without a key those variants are reported as "not run" — no number
is ever invented. Ground truth: bench/cases/*.json (items from research 08c §6, pages from 08a/08b).

Metrics per variant:
  eur_identified        sum of amounts in the produced statement
  recall                ground-truth items found (by catalog key)
  citations_correct     items citing a page that exists in the contract and whose quote is verbatim in it
  untraceable_amounts   amounts not equal to an evidence amount, a client-stated amount, or a sum of those  (agent target: 0)
  tokens / latency_ms   from the `actions` table (agent) or the model response (llm_only)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.agents.claims import handlers as H
from app.agents.claims import memory as M
from app.agents.claims import tools_impl as T
from app.agents.claims.brain import covers, recompute
from app.agents.review import amounts as A
from app.agents.review.citations import quote_in_body
from app.config import settings

CASES = Path(__file__).parent / "cases"
REPORT = Path(__file__).parent / "report.md"


# --- helpers -------------------------------------------------------------------------------------

async def _corpus_doc(product_name: str) -> dict[str, Any]:
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT id, page_count FROM documents WHERE origin = 'corpus' AND product_name = %s", (product_name,))
        row = await cur.fetchone()
    if not row:
        raise SystemExit(f"contract {product_name} not ingested; run app.ingestion.load_corpus first")
    return dict(row)


async def _clause_on_page(doc_id: str, page: int | None, hint: str = "") -> dict[str, Any] | None:
    if page is None:
        return None
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT id, page, body FROM clauses WHERE document_id = %s AND page = %s ORDER BY id LIMIT 1", (doc_id, page))
        row = await cur.fetchone()
    return dict(row) if row else None


async def _page_exists(doc_id: str, page: int | None) -> bool:
    if page is None:
        return False
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT 1 FROM clauses WHERE document_id = %s AND page = %s LIMIT 1", (doc_id, page))).fetchone()
    return row is not None


def _recall(found_keys: set[str], gt: list[dict[str, Any]]) -> tuple[int, int]:
    keys = {g["catalog_key"] for g in gt}
    return len(keys & found_keys), len(keys)


def _traceable_pool(case: dict[str, Any]) -> list[float]:
    ev = [float(e["amount_eur"]) for e in case["evidence"] if e.get("amount_eur") is not None]
    stated = A.extract_amounts_eur(case["narrative"])
    return ev + stated


def _untraceable(amounts: list[float], case: dict[str, Any], extra_allowed: list[float] = ()) -> list[float]:
    pool = _traceable_pool(case) + list(extra_allowed)
    # sums of evidence are traceable too (a stock item from two invoices)
    ev = [float(e["amount_eur"]) for e in case["evidence"] if e.get("amount_eur") is not None]
    sums = set()
    for i in range(len(ev)):
        for j in range(i + 1, len(ev)):
            sums.add(round(ev[i] + ev[j], 2))
    return A.untraceable(amounts, pool + sorted(sums))


# --- variants ------------------------------------------------------------------------------------

def run_naive(case: dict[str, Any]) -> dict[str, Any]:
    found = set(case.get("naive_items", []))
    r, n = _recall(found, case["ground_truth"])
    return {"variant": "naive", "eur_identified": case["naive_declared_eur"], "recall": f"{r}/{n}", "recall_pct": round(100 * r / n),
            "citations_correct": "0/0", "citations_pct": None, "untraceable_amounts": None, "tokens": None, "latency_ms": None,
            "note": case.get("naive_note") or "declared from memory, no contract read"}


LLM_ONLY_SYSTEM = """A small-business owner describes an insured loss. Produce their statement of loss for the insurer under the policy named below.
Return ONLY JSON: {"items": [{"label": str, "catalog_key": one of {keys}, "amount_eur": number|null, "page": int|null, "quote": "short verbatim quote from the policy or null"}]}
You have no access to the policy text or to invoices; do your best from the description."""


async def run_llm_only(case: dict[str, Any], doc: dict[str, Any], catalog_keys: list[str]) -> dict[str, Any]:
    if not settings.openai_api_key:
        return {"variant": "llm_only", "note": "not run — OPENAI_API_KEY missing"}
    from app.agents.claims.nodes import llm

    started = time.perf_counter()
    system = LLM_ONLY_SYSTEM.replace("{keys}", ", ".join(catalog_keys))
    res = await llm.complete_json(system, [{"type": "text", "text": f"Policy: {case['contract']['label']}.\n\n{case['narrative']}"}], claim_id=None, tool="bench_llm_only")
    latency = int((time.perf_counter() - started) * 1000)
    items = res.get("items") or []
    amounts = [float(i["amount_eur"]) for i in items if i.get("amount_eur") is not None]
    cited = [i for i in items if i.get("page") is not None]
    ok = 0
    for i in cited:
        cl = await _clause_on_page(str(doc["id"]), i["page"])
        if cl and i.get("quote") and quote_in_body(i["quote"], cl["body"]):
            ok += 1
    r, n = _recall({i.get("catalog_key") for i in items}, case["ground_truth"])
    async with db.pool.connection() as conn:
        tok = await (await conn.execute("SELECT tokens_in, tokens_out FROM actions WHERE tool = 'bench_llm_only' ORDER BY created_at DESC LIMIT 1")).fetchone()
    return {"variant": "llm_only", "eur_identified": round(sum(amounts)), "recall": f"{r}/{n}", "recall_pct": round(100 * r / n),
            "citations_correct": f"{ok}/{len(cited)}", "citations_pct": (round(100 * ok / len(cited)) if cited else None),
            "untraceable_amounts": len(_untraceable(amounts, case)), "tokens": (tok[0] or 0) + (tok[1] or 0) if tok else None, "latency_ms": latency,
            "note": f"{len(items)} items; pages cited without the text: {len(cited)}", "items": items}


async def run_agent(case: dict[str, Any], doc: dict[str, Any]) -> dict[str, Any]:
    """Seed an account with the case's coverage profile, feed the narrative and the evidence through the agent's own pipeline.

    With a model key the narrative is structured by the model. Without one, the deterministic path runs alone:
    narrative logged as a fact, closure period taken as the client's statement, items created from the documents,
    purchase-price recomputation, cover matching, business interruption from the accounting export. Labelled as such.
    """
    acct = str(uuid.uuid4())
    started = time.perf_counter()
    async with db.pool.connection() as conn:
        await conn.execute("INSERT INTO accounts (id, email, password_hash) VALUES (%s, %s, 'bench')", (acct, f"bench-{case['id']}-{acct[:6]}@example.com"))
        await conn.execute(
            "INSERT INTO businesses (account_id, name, insurer_name, vat_recoverable, insurer_contact_email) VALUES (%s, %s, %s, %s, 'bench@example.com')",
            (acct, case["name"].split(" — ")[0], case["contract"]["insurer_name"], case.get("vat_recoverable")))
        for cov in case["coverage"]:
            cl = await _clause_on_page(str(doc["id"]), cov.get("page"))
            await conn.execute(
                """INSERT INTO coverage_profile (account_id, guarantee, subscribed, ceiling, deductible_detail, source_clause_id, source_document_id, page, quote, confidence)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'bench')""",
                (acct, cov["guarantee"], {"yes": True, "no": False}.get(cov["subscribed"]), json.dumps(cov.get("ceiling")) if cov.get("ceiling") else None,
                 json.dumps(cov.get("deductible")) if cov.get("deductible") else None, cl["id"] if cl else None, doc["id"], cov.get("page"), (cl["body"][:200] if cl else None)))
        await conn.commit()
    claim_id = await H.create_claim(acct, case["narrative"], loss_date=date.fromisoformat(case["loss_date"]), loss_type=case["loss_type"])
    from app.agents.claims.brain import evidence_items
    from app.agents.claims.nodes import analyze as AN

    with_model = bool(settings.openai_api_key)
    if with_model:
        state = {"claim_id": claim_id, "event": {"kind": "message", "payload": {"text": case["narrative"]}}, "memory": await M.get_claim_memory(claim_id), "triage": {}}
        await AN.run(state)
    else:
        await T.log_fact(claim_id, case["narrative"], "client", "medium")
        mem = await M.get_claim_memory(claim_id)
        bi = covers.ensure_bi_item(mem, case.get("closure_days"))
        if bi:
            from app.contracts import LossItemInput
            await T.update_loss_statement(claim_id, [LossItemInput(**bi)])

    new_ids = []
    async with db.pool.connection() as conn:
        for e in case["evidence"]:
            d = await (await conn.execute(
                "INSERT INTO documents (account_id, claim_id, doc_type, origin, filename, sha256) VALUES (%s,%s,%s,'bench',%s,%s) RETURNING id",
                (acct, claim_id, e["type"] if e["type"] in ("invoice", "quote", "inventory", "accounting") else "other", e["document"], f"bench-{uuid.uuid4()}"))).fetchone()
            await conn.commit()
            row = await T.add_evidence(claim_id, document_id=str(d[0]), evidence_type=e["type"], amount_eur=e.get("amount_eur"), issued_on=e.get("date"),
                                       vendor=e.get("vendor"), description=e["description"], extracted={"facts": [e["description"]]}, sha256=None)
            new_ids.append(str(row["id"]))
    mem = await M.get_claim_memory(claim_id)
    await recompute.recompute_from_evidence(claim_id, mem, new_ids)
    mem = await M.get_claim_memory(claim_id)
    await evidence_items.create_items_from_evidence(claim_id, mem, new_ids)
    mem = await M.get_claim_memory(claim_id)
    await evidence_items.compute_business_interruption(claim_id, mem, case.get("closure_days"))
    mem = await M.get_claim_memory(claim_id)
    await covers.match_claim(claim_id, mem)
    mem = await M.get_claim_memory(claim_id)
    latency = int((time.perf_counter() - started) * 1000)

    items = mem["loss_items"]
    amounts = [float(li["amount_claimed_eur"]) for li in items if li.get("amount_claimed_eur") is not None]
    found = {li.get("catalog_key") for li in items if li.get("catalog_key")}
    r, n = _recall(found, case["ground_truth"])
    cited = [li for li in items if li.get("clause_page") is not None]
    ok = 0
    for li in cited:
        cl = await _clause_on_page(str(doc["id"]), li["clause_page"])
        if cl and li.get("clause_quote") and quote_in_body(li["clause_quote"], cl["body"]):
            ok += 1
    buckets = M.amounts_for_review(mem)
    untr = A.untraceable(amounts, buckets["evidence"] + buckets["derived"] + buckets["client_instruction"])
    async with db.pool.connection() as conn:
        tok = await (await conn.execute("SELECT coalesce(sum(tokens_in),0) + coalesce(sum(tokens_out),0) FROM actions WHERE claim_id = %s", (claim_id,))).fetchone()
    supported = sum(1 for li in items if li.get("status") in ("supported", "sent"))
    mode = "model + deterministic pipeline" if with_model else "deterministic pipeline only (no model key: narrative not structured)"
    return {"variant": "agent", "eur_identified": round(sum(amounts)), "recall": f"{r}/{n}", "recall_pct": round(100 * r / n),
            "citations_correct": f"{ok}/{len(cited)}", "citations_pct": (round(100 * ok / len(cited)) if cited else None),
            "untraceable_amounts": len(untr), "tokens": int(tok[0]) if tok else 0, "latency_ms": latency,
            "note": f"{len(items)} items, {supported} supported by evidence; {mode}",
            "items": [{"label": li["label"], "key": li.get("catalog_key"), "amount": li.get("amount_claimed_eur") and float(li["amount_claimed_eur"]), "status": li.get("status"),
                       "page": li.get("clause_page"), "cover": ((li.get("computation_detail") or {}).get("cover") or {}).get("status")} for li in items]}


# --- report --------------------------------------------------------------------------------------

def _fmt(v, suffix=""):
    return "—" if v is None else f"{v:,}{suffix}".replace(",", " ")


def render(results: list[dict[str, Any]]) -> str:
    out = [f"# Benchmark — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "",
           "Ground truth: `bench/cases/*.json` (items and amounts from research `08c` §6, pages from `08a`/`08b`). Every figure below was produced by `bench/run.py`.", ""]
    for case_res in results:
        c = case_res["case"]
        gt_total = sum(g["amount_eur"] for g in c["ground_truth"])
        out += [f"## Case {c['id']} — {c['name']}", f"Contract: {c['contract']['label']}. Ground truth: {len(c['ground_truth'])} items, {_fmt(gt_total)} €."
                + (f" Insurer first offer in the scenario: {_fmt(c['insurer_first_offer_eur'])} €." if c.get("insurer_first_offer_eur") else ""), "",
                "| Variant | € identified | Recall (items) | Citations correct | Untraceable amounts | Tokens | Latency | Note |", "|---|---|---|---|---|---|---|---|"]
        for v in case_res["variants"]:
            if "eur_identified" not in v:
                out.append(f"| {v['variant']} | — | — | — | — | — | — | {v['note']} |")
                continue
            out.append(f"| {v['variant']} | {_fmt(v['eur_identified'])} € | {v['recall']} ({v['recall_pct']} %) | {v['citations_correct']}"
                       + (f" ({v['citations_pct']} %)" if v.get("citations_pct") is not None else "")
                       + f" | {_fmt(v['untraceable_amounts'])} | {_fmt(v['tokens'])} | {_fmt(v['latency_ms'], ' ms')} | {v['note']} |")
        out.append("")
        agent = next((v for v in case_res["variants"] if v["variant"] == "agent" and v.get("items")), None)
        if agent:
            out += ["<details><summary>Agent statement of loss</summary>", "", "| Item | Key | Amount | Status | Page | Cover |", "|---|---|---|---|---|---|"]
            out += [f"| {i['label']} | {i['key'] or '—'} | {_fmt(round(i['amount']) if i['amount'] is not None else None)} | {i['status']} | {i['page'] or '—'} | {i['cover'] or '—'} |" for i in agent["items"]]
            out += ["", "</details>", ""]
    return "\n".join(out)


async def main(only: str | None) -> None:
    await db.open_pool()
    await db.run_migrations()
    from app.agents.claims import graph as G
    await G.setup()
    async with db.pool.connection() as conn:
        catalog_keys = [r[0] for r in await (await conn.execute("SELECT key FROM loss_catalog ORDER BY key")).fetchall()]
    results = []
    for path in sorted(CASES.glob("*.json")):
        case = json.loads(path.read_text())
        if only and case["id"].upper() != only.upper():
            continue
        doc = await _corpus_doc(case["contract"]["product_name"])
        variants = [run_naive(case), await run_llm_only(case, doc, catalog_keys), await run_agent(case, doc)]
        results.append({"case": case, "variants": variants})
        print(f"case {case['id']}: " + " | ".join(f"{v['variant']}={v.get('eur_identified', 'n/a')}" for v in variants))
    REPORT.write_text(render(results))
    print(f"report → {REPORT}")
    await G.teardown()
    await db.close_pool()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case")
    asyncio.run(main(p.parse_args().case))
