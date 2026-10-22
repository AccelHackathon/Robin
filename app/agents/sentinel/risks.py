"""Risk taxonomy of the Sentinel: which external events matter for which cover, what to search,
and which prevention / deadline facts to attach. Everything the agent says about the contract
comes from `coverage_profile` / `clauses` at runtime; this file only maps risks to covers and
query templates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Guarantee keys follow workstream B's canonical vocabulary (app/agents/intake/guarantees.py).


@dataclass(frozen=True)
class Risk:
    key: str
    label_en: str
    guarantees: tuple[str, ...]              # covers concerned, first = primary
    queries: tuple[str, ...]                 # templates; {city}, {department}, {street} are filled per account
    official_sites: tuple[str, ...] = ()     # sites that count as official sources
    practical_measures: tuple[str, ...] = () # non-contractual, common-sense measures (always labelled as such)
    applies_if: str = "always"               # always | has_vehicles | has_shopfront
    default_severity: str = "medium"


RISKS: dict[str, Risk] = {
    r.key: r
    for r in [
        Risk(
            key="civil_unrest", label_en="Protest, riot or civil unrest",
            guarantees=("riot_civil_commotion", "theft_vandalism", "glass", "business_interruption"),
            queries=(
                "manifestation {city} préfecture arrêté parcours",
                "manifestation {city} samedi cortège centre-ville",
                "émeutes pillages {city} commerces",
                "interdiction de manifester couvre-feu {city}",
            ),
            official_sites=("bouches-du-rhone.gouv.fr", "prefectures-regions.gouv.fr", "interieur.gouv.fr", "gouvernement.fr"),
            practical_measures=(
                "Lower the shutter and remove high-value stock from the window before the start time.",
                "Photograph the shopfront and the stock before the event so you have a dated 'before' state.",
                "Keep invoices and the latest inventory at hand.",
            ),
            applies_if="has_shopfront", default_severity="high",
        ),
        Risk(
            key="hail", label_en="Hail",
            guarantees=("storm_hail_snow", "equipment_replacement_value", "glass"),
            queries=("vigilance orange orages grêle {department}", "alerte grêle {city} Météo-France", "orages violents grêle {department} prévision"),
            official_sites=("vigilance.meteofrance.fr", "meteofrance.com"),
            practical_measures=("Move vehicles under cover.", "Close awnings and secure outdoor displays.", "Photograph vehicles and glass surfaces before the storm."),
            applies_if="always", default_severity="medium",
        ),
        Risk(
            key="storm", label_en="Storm / high winds",
            guarantees=("storm_hail_snow", "glass", "business_interruption"),
            queries=("vigilance orange vent violent {department}", "tempête {city} rafales alerte", "vigilance rouge tempête {department}"),
            official_sites=("vigilance.meteofrance.fr", "meteofrance.com"),
            practical_measures=("Retract awnings and signs that can be torn off.", "Secure outdoor furniture and displays."),
            default_severity="medium",
        ),
        Risk(
            key="flood", label_en="Flood / heavy rain",
            guarantees=("water", "natural_disaster", "business_interruption"),
            queries=("vigilance orange pluie inondation {department}", "crue {city} alerte inondation", "épisode méditerranéen {department} vigilance"),
            official_sites=("vigilance.meteofrance.fr", "vigicrues.gouv.fr"),
            practical_measures=("Raise stock and equipment off the floor.", "Photograph the premises before the episode."),
            default_severity="medium",
        ),
        Risk(
            key="fire_nearby", label_en="Fire in the immediate surroundings",
            guarantees=("fire", "business_interruption"),
            queries=("incendie {street} {city}", "incendie commerce {city} centre-ville pompiers"),
            practical_measures=("Check smoke damage inside the premises and photograph it before cleaning.",),
            default_severity="high",
        ),
        Risk(
            key="strike_access", label_en="Strike or blockade affecting access",
            guarantees=("business_interruption",),
            queries=("grève blocage {city} commerces accès centre-ville", "blocage {city} manifestation transports fermeture"),
            practical_measures=("Keep daily sales records: an access-denial loss needs a documented before/after.",),
            default_severity="low",
        ),
        Risk(
            key="theft_wave", label_en="Burglary wave in the area",
            guarantees=("theft_vandalism",),
            queries=("série de cambriolages commerces {city}", "vague de vols {city} commerçants police"),
            practical_measures=("Check that alarm and locks match what the policy requires.",),
            default_severity="low",
        ),
        Risk(
            key="regulatory", label_en="Regulatory or insurer measure affecting the claim",
            guarantees=("riot_civil_commotion", "theft_vandalism", "business_interruption"),
            queries=(
                "France Assureurs délai déclaration sinistre commerçants mesures exceptionnelles",
                "assureurs franchise supprimée commerçants dégradations manifestations",
                "fonds de soutien commerçants dégradations Bercy aide",
            ),
            official_sites=("franceassureurs.fr", "economie.gouv.fr", "presse.economie.gouv.fr"),
            default_severity="medium",
        ),
    ]
}

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def risks_for(*, has_vehicles: bool, has_shopfront: bool, covers: dict[str, dict]) -> list[Risk]:
    """Risks worth watching for an account: a cover is subscribed or unknown (never assume 'no')."""
    out = []
    for r in RISKS.values():
        if r.applies_if == "has_vehicles" and not has_vehicles:
            continue
        if r.applies_if == "has_shopfront" and not has_shopfront:
            continue
        if r.key == "regulatory":
            out.append(r)
            continue
        if any((covers.get(g) or {}).get("subscribed") in ("yes", "unknown", None) for g in r.guarantees):
            out.append(r)
    return out
