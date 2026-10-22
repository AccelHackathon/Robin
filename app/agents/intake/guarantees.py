"""Stable canonical keys used in coverage_profile and the Claims Agent."""

GUARANTEES = {
    "fire": ("Fire", "incendie", 11),
    "riot_civil_commotion": (
        "Riots and civil commotion",
        "émeutes mouvements populaires",
        15,
    ),
    "theft_vandalism": ("Theft and vandalism", "vol vandalisme", 19),
    "glass": ("Glass breakage", "bris vitres vitrines", 14),
    "water": ("Water damage", "dégâts eaux", 16),
    "business_interruption": ("Business interruption", "perte exploitation", 41),
    "bailed_goods": ("Customers’ goods", "biens confiés", 22),
    "tenant_fit_out": ("Tenant fit-out", "aménagements", 8),
    "equipment_replacement_value": (
        "Equipment replacement value",
        "matériel informatique neuf",
        79,
    ),
    "guarding_boarding": ("Guarding and boarding", "gardiennage clôture", 14),
    "debris": ("Debris removal", "démolition déblais", 24),
    "graffiti": ("Graffiti", "graffitis tags", 23),
    "cash": ("Cash", "espèces fonds valeurs", 15),
    "locks": ("Locks", "serrures", 19),
    "assessor_fees": ("Policyholder assessor fees", "honoraires expert", 78),
    "indirect_losses": ("Indirect losses", "pertes indirectes", 25),
    "legal_protection": ("Legal protection", "protection juridique", 54),
    "assistance": ("Assistance", "assistance", 58),
}
PC_LABELS = {
    "fire": "Incendie",
    "riot_civil_commotion": "Émeutes et mouvements populaires",
    "theft_vandalism": "Vol, tentative de vol et vandalisme",
    "glass": "Bris de glace",
    "water": "Dégâts des eaux",
    "business_interruption": "Perte d’exploitation",
    "bailed_goods": "Biens confiés",
    "tenant_fit_out": "Aménagements du locataire",
    "equipment_replacement_value": "Matériel en valeur à neuf",
}
