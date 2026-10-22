"""Benchmark metrics: item-level precision/recall/F1, amount error on matched items, citation precision."""

from __future__ import annotations

from typing import Any


def item_metrics(produced: list[dict[str, Any]], ground_truth: list[dict[str, Any]]) -> dict[str, Any]:
    """Match on catalog key. Amount error = |produced − truth| / truth over matched items with both amounts."""
    gt = {g["catalog_key"]: g for g in ground_truth}
    pr = {}
    for p in produced:
        k = p.get("catalog_key") or p.get("key")
        if k and k not in pr:
            pr[k] = p
    tp = set(gt) & set(pr)
    fp = set(pr) - set(gt)
    fn = set(gt) - set(pr)
    precision = len(tp) / len(pr) if pr else 0.0
    recall = len(tp) / len(gt) if gt else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    errs = []
    for k in tp:
        a, b = pr[k].get("amount_eur", pr[k].get("amount")), gt[k].get("amount_eur")
        if a is not None and b:
            errs.append(abs(float(a) - float(b)) / float(b))
    mape = sum(errs) / len(errs) if errs else None
    within10 = sum(1 for e in errs if e <= 0.10)
    return {"tp": len(tp), "fp": len(fp), "fn": len(fn), "precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3),
            "amount_mape": (round(mape, 3) if mape is not None else None), "amounts_within_10pct": f"{within10}/{len(errs)}",
            "missed": sorted(fn), "spurious": sorted(fp)}


def eur_summary(produced_total: float | None, truth_total: float, naive_total: float | None) -> dict[str, Any]:
    out = {"truth_eur": round(truth_total), "produced_eur": (round(produced_total) if produced_total is not None else None)}
    if produced_total is not None:
        out["coverage_of_truth_pct"] = round(100 * produced_total / truth_total) if truth_total else None
        out["over_declared_eur"] = round(max(0.0, produced_total - truth_total))
    if naive_total is not None and produced_total is not None:
        out["delta_vs_naive_eur"] = round(produced_total - naive_total)
    return out
