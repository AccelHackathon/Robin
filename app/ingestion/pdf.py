"""Page-preserving ingestion. Clause bodies are exact slices of the original text."""
from __future__ import annotations
import asyncio
import hashlib
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 20 * 1024 * 1024

@dataclass(frozen=True)
class PageClause:
    page: int
    heading: str | None
    body: str


def split_clauses(text: str) -> list[PageClause]:
    result = []
    for page_no, page in enumerate(text.split('\f'), 1):
        if not page.strip():
            continue
        # Small page-local chunks, preserving whitespace and exact source offsets.
        chunks = re.split(r'(?<=\n)(?=\s*\n)', page)
        pending = ''
        for chunk in chunks:
            if pending and len(pending) + len(chunk) > 2800:
                result.append(_clause(page_no, pending))
                pending = ''
            pending += chunk
        if pending.strip():
            result.append(_clause(page_no, pending))
    return result


def _clause(page: int, body: str) -> PageClause:
    lines = [x.strip() for x in body.splitlines() if x.strip()]
    heading = next((x for x in lines[:4] if x.isupper() or re.match(r'^\d+[.) ]', x)), None)
    return PageClause(page, heading, body)


def sniff_type(content: bytes) -> str:
    if content.startswith(b'%PDF-'): return 'application/pdf'
    if content.startswith(b'\xff\xd8\xff'): return 'image/jpeg'
    if content.startswith(b'\x89PNG\r\n\x1a\n'): return 'image/png'
    if len(content) > 12 and content[4:8] == b'ftyp' and content[8:12] in (b'heic', b'heix', b'hevc', b'mif1'):
        return 'image/heic'
    raise ValueError('Choose a PDF, JPG, PNG or HEIC file.')


async def pdf_text(content: bytes) -> str:
    if len(content) > MAX_BYTES: raise ValueError('Files must be 20 MB or smaller.')
    with tempfile.TemporaryDirectory(prefix='robin-pdf-') as folder:
        path = Path(folder) / 'input.pdf'
        path.write_bytes(content)
        proc = await asyncio.create_subprocess_exec('pdftotext', '-layout', str(path), '-',
                                                   stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), 45)
        except (TimeoutError, asyncio.CancelledError):
            proc.kill(); await proc.wait(); raise
        if proc.returncode: raise ValueError('This PDF could not be read. Please upload an unlocked copy.')
        return stdout.decode('utf-8', errors='replace')


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
