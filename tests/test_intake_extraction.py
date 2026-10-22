from app.agents.intake.graph import amount_in_source, fixture_fact


def test_amounts_must_exist_in_source():
    assert amount_in_source(15000, "Plafond : 15 000 EUR")
    assert amount_in_source(15.5, "Franchise : 15,5 %")
    assert not amount_in_source(30000, "Plafond : 15 000 EUR")
    assert not amount_in_source(1000, "11000 euros")


def test_fixture_parser_never_applies_to_real_documents():
    clause = {
        "body": "Vol, tentative de vol et vandalisme   Souscrit - plafond stock : 15 000 EUR",
        "metadata": {},
    }
    assert fixture_fact("theft_vandalism", clause) is None
    clause["metadata"]["synthetic"] = True
    assert fixture_fact("theft_vandalism", clause)["ceiling"]["amount"] == 15000
