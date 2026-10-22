"""Workstream A — simulated insurer scenario logic (no network)."""

from app.agents.insurer_sim.scenarios import KARIM_DEFAULT, classify, pick_step


def test_classify_declaration():
    assert classify("Déclaration de sinistre – Karim", "nous vous déclarons") == "declaration"


def test_classify_contest_inflections():
    assert classify("Objet: contestation", "nous contestons la proposition") == "contest"


def test_scenario_progresses_without_repeating_steps():
    played: set[str] = set()
    sequence = ["declaration", "loss_statement", "written_confirmation", "complements", "contest"]
    keys = []
    for intent in sequence:
        step = pick_step(KARIM_DEFAULT, intent, played)
        assert step is not None, intent
        played.add(step.key)
        keys.append(step.key)
    assert keys == ["ack_declaration", "ask_invoices", "confirm_theft_cap", "offer_with_release", "contest_to_expert"]


def test_offer_step_attaches_release_pdf():
    step = pick_step(KARIM_DEFAULT, "complements", set())
    assert step.attach_release_pdf is True


def test_step_is_played_once():
    played = {"ack_declaration"}
    assert pick_step(KARIM_DEFAULT, "declaration", played) is None


def test_release_pdf_contains_settlement_language():
    from app.agents.insurer_sim.release_pdf import build_release_pdf
    import subprocess, tempfile

    pdf = build_release_pdf(business_name="Karim", signer="M. K.", amount=20750.0,
                            loss_date="17/10/2026", ref="SIN-2026-104201", policy_number="MRP-1")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(pdf)
        f.flush()
        text = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True).stdout.decode()
    assert "SOLDE DE TOUT COMPTE" in text
    assert "RENONCE" in text
