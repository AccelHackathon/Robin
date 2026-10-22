"""Risk profile of an account: where it is, what it does, what it is covered for, and what the
contract requires (prevention conditions, declaration deadlines). Everything comes from the
tables filled by workstream B; nothing is guessed about the contract.
"""

from __future__ import annotations

import json
import re

from psycopg.rows import dict_row

from app import db
from app.agents.sentinel.risks import risks_for

DEPARTMENTS = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence", "05": "Hautes-Alpes", "06": "Alpes-Maritimes",
    "07": "Ardèche", "08": "Ardennes", "09": "Ariège", "10": "Aube", "11": "Aude", "12": "Aveyron", "13": "Bouches-du-Rhône",
    "14": "Calvados", "15": "Cantal", "16": "Charente", "17": "Charente-Maritime", "18": "Cher", "19": "Corrèze", "21": "Côte-d'Or",
    "22": "Côtes-d'Armor", "23": "Creuse", "24": "Dordogne", "25": "Doubs", "26": "Drôme", "27": "Eure", "28": "Eure-et-Loir",
    "29": "Finistère", "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde", "34": "Hérault", "35": "Ille-et-Vilaine",
    "36": "Indre", "37": "Indre-et-Loire", "38": "Isère", "39": "Jura", "40": "Landes", "41": "Loir-et-Cher", "42": "Loire",
    "43": "Haute-Loire", "44": "Loire-Atlantique", "45": "Loiret", "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozère",
    "49": "Maine-et-Loire", "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne", "54": "Meurthe-et-Moselle",
    "55": "Meuse", "56": "Morbihan", "57": "Moselle", "58": "Nièvre", "59": "Nord", "60": "Oise", "61": "Orne", "62": "Pas-de-Calais",
    "63": "Puy-de-Dôme", "64": "Pyrénées-Atlantiques", "65": "Hautes-Pyrénées", "66": "Pyrénées-Orientales", "67": "Bas-Rhin",
    "68": "Haut-Rhin", "69": "Rhône", "70": "Haute-Saône", "71": "Saône-et-Loire", "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie",
    "75": "Paris", "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines", "79": "Deux-Sèvres", "80": "Somme", "81": "Tarn",
    "82": "Tarn-et-Garonne", "83": "Var", "84": "Vaucluse", "85": "Vendée", "86": "Vienne", "87": "Haute-Vienne", "88": "Vosges",
    "89": "Yonne", "90": "Territoire de Belfort", "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne", "95": "Val-d'Oise",
}

VEHICLE_WORDS = re.compile(r"\b(camion|camionnette|utilitaire|véhicule|vehicule|livraison|food[- ]?truck|transport|taxi|vtc|ambulan)", re.I)


def parse_address(address: str | None) -> dict:
    """Best-effort split of a French address into street / postcode / city / department."""
    address = (address or "").strip()
    m = re.search(r"\b(\d{5})\b\s*([^,]+)?", address)
    postcode = m.group(1) if m else None
    city = (m.group(2) or "").strip() if m else None
    street = address.split(",")[0].strip() if "," in address else None
    if street:
        street = re.sub(r"^\d+\s*(bis|ter)?\s*", "", street, flags=re.I).strip()
    dept_code = None
    if postcode:
        dept_code = "20" if postcode.startswith("20") else postcode[:2]
        if postcode.startswith("97"):
            dept_code = postcode[:3]
    department = DEPARTMENTS.get(dept_code or "", dept_code)
    return {"street": street or None, "postcode": postcode, "city": city or None, "department": department, "dept_code": dept_code}


async def build_profile(account_id: str) -> dict:
    """Read business + latest coverage facts + deadline rules, upsert `risk_profiles`, return the profile."""
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM businesses WHERE account_id = %s ORDER BY created_at DESC LIMIT 1", (account_id,))
            biz = await cur.fetchone() or {}
            await cur.execute(
                """
                SELECT DISTINCT ON (guarantee) guarantee, subscribed, ceiling, ceiling_eur, deductible, deductible_detail,
                       conditions, exclusions, quote, source_clause_id, page, confidence
                FROM coverage_profile WHERE account_id = %s ORDER BY guarantee, version DESC, created_at DESC
                """,
                (account_id,),
            )
            facts = await cur.fetchall()
            await cur.execute("SELECT kind, rule, quote, page, source_clause_id FROM deadline_rules WHERE account_id = %s", (account_id,))
            deadlines = await cur.fetchall()
            await cur.execute("SELECT chat_id FROM telegram_links WHERE account_id = %s LIMIT 1", (account_id,))
            tg = await cur.fetchone()

    def _sub(v):
        if v is True:
            return "yes"
        if v is False:
            return "no"
        return v if isinstance(v, str) else "unknown"

    covers: dict[str, dict] = {}
    for f in facts:
        conds = f["conditions"]
        if isinstance(conds, str):
            try:
                conds = json.loads(conds)
            except Exception:
                conds = [conds]
        covers[f["guarantee"]] = {
            "guarantee": f["guarantee"], "subscribed": _sub(f["subscribed"]),
            "ceiling": f["ceiling"] or ({"amount": float(f["ceiling_eur"])} if f["ceiling_eur"] is not None else None),
            "deductible": f["deductible_detail"] or f["deductible"],
            "conditions": conds or [], "quote": f["quote"], "clause_id": f["source_clause_id"], "page": f["page"],
            "confidence": f["confidence"],
        }

    addr = parse_address(biz.get("address"))
    activity = f"{biz.get('activity') or ''} {biz.get('name') or ''}"
    has_vehicles = bool(VEHICLE_WORDS.search(activity))
    profile = {
        "account_id": str(account_id),
        "business_name": biz.get("name"),
        "activity": biz.get("activity"),
        "address": biz.get("address"),
        "street": addr["street"], "postcode": addr["postcode"], "city": addr["city"] or "France",
        "department": addr["department"] or "", "dept_code": addr["dept_code"],
        "tenant_or_owner": biz.get("tenant_or_owner"),
        "insurer_name": biz.get("insurer_name"),
        "has_vehicles": has_vehicles,
        "has_shopfront": True,
        "covers": covers,
        "deadlines": [{"kind": d["kind"], "rule": d["rule"], "quote": d["quote"], "page": d["page"], "clause_id": d["source_clause_id"]} for d in deadlines],
        "telegram_linked": bool(tg),
    }
    profile["risk_keys"] = [r.key for r in risks_for(has_vehicles=has_vehicles, has_shopfront=True, covers=covers)]

    async with db.pool.connection() as conn:
        await conn.execute(
            """
            INSERT INTO risk_profiles (account_id, city, department, address, activity, has_vehicles, has_shopfront, risk_keys, covers, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            ON CONFLICT (account_id) DO UPDATE SET city = EXCLUDED.city, department = EXCLUDED.department, address = EXCLUDED.address,
                activity = EXCLUDED.activity, has_vehicles = EXCLUDED.has_vehicles, risk_keys = EXCLUDED.risk_keys,
                covers = EXCLUDED.covers, updated_at = now()
            """,
            (account_id, profile["city"], profile["department"], profile["address"], profile["activity"], has_vehicles, True,
             profile["risk_keys"], json.dumps({k: {"subscribed": v["subscribed"], "page": v["page"], "clause_id": v["clause_id"]} for k, v in covers.items()})),
        )
        await conn.commit()
    return profile
