"""Run with python -m app.ingestion.load_corpus. Idempotent, including concurrent runs."""

import asyncio
from pathlib import Path
from psycopg.types.json import Jsonb
from app import db
from app.ingestion.pdf import sha256, split_clauses

CORPUS = Path(__file__).resolve().parents[2] / "data/contrats/txt"


async def load_corpus() -> list[dict]:
    output = []
    async with db.pool.connection() as conn:
        await conn.execute("SELECT pg_advisory_xact_lock(200001)")
        for path in sorted(CORPUS.glob("*.txt")):
            content = path.read_bytes()
            digest = sha256(content)
            exists = await (
                await conn.execute(
                    "SELECT id FROM documents WHERE account_id IS NULL AND origin='corpus' AND sha256=%s",
                    (digest,),
                )
            ).fetchone()
            if exists:
                output.append(
                    {"file": path.name, "id": str(exists[0]), "existing": True}
                )
                continue
            text = content.decode("utf-8")
            clauses = split_clauses(text)
            kind = "ipid" if "IPID" in path.name else "general_conditions"
            insurer = path.name.split("_")[0]
            if insurer == "CA":
                insurer = "Pacifica"
            if insurer == "SG":
                insurer = "Sogessur"
            row = await (
                await conn.execute(
                    """INSERT INTO documents(doc_type,origin,filename,mime_type,sha256,content,
                extracted_text,insurer_name,product_name,version_label,page_count,metadata)
                VALUES (%s,'corpus',%s,'text/plain',%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (
                        kind,
                        path.name,
                        digest,
                        content,
                        text,
                        insurer,
                        path.stem,
                        "11031 - 01/26" if insurer == "MAAF" else path.stem,
                        max(c.page for c in clauses),
                        Jsonb({"public": True, "source_format": "pdftotext -layout"}),
                    ),
                )
            ).fetchone()
            async with conn.cursor() as cur:
                await cur.executemany(
                    "INSERT INTO clauses(document_id,page,heading,body) VALUES (%s,%s,%s,%s)",
                    [(row[0], c.page, c.heading, c.body) for c in clauses],
                )
            output.append(
                {"file": path.name, "id": str(row[0]), "clauses": len(clauses)}
            )
    return output


async def main():
    if not await db.open_pool():
        raise SystemExit("DATABASE_URL is required.")
    try:
        await db.run_migrations()
        for row in await load_corpus():
            print(row)
    finally:
        await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
