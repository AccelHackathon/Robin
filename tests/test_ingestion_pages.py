from pathlib import Path
from app.ingestion.pdf import split_clauses,sniff_type
from app.ingestion.search import quote_matches
import pytest

def test_pages_and_verbatim_are_preserved():
    text='TITLE\n A  sentence.\n\nAnother sentence.\f\f3. Heading\nLast page.\f'
    clauses=split_clauses(text)
    assert [c.page for c in clauses]==[1,3]
    assert clauses[0].body==text.split('\f')[0]
    assert clauses[0].heading=='TITLE'

def test_quote_validation():
    assert quote_matches('Clause: le gardiennage des locaux pendant 72 heures.','le gardiennage des locaux pendant 72 heures')
    assert not quote_matches('Le plafond applicable est de 15 000 euros.','La garantie couvre 900 000 euros sans plafond.')
    assert not quote_matches('Theft option','Theft')

def test_magic_bytes():
    assert sniff_type(b'%PDF-1.4\n')=='application/pdf'
    with pytest.raises(ValueError):sniff_type(b'<script>not an image</script>')

def test_corpus_page_numbers():
    path=Path('data/contrats/txt/MAAF_MRP_CG_11031-0126.txt')
    clauses=split_clauses(path.read_text())
    assert max(c.page for c in clauses)==90
    assert any(c.page==58 and '72 heures' in c.body for c in clauses)
