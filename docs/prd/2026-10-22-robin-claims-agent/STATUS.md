# STATUS — Robin claims agent

PRD : `PRD.md` (même dossier). Mis à jour : 2026-10-22.

## Phase courante

- [ ] H0 — démo hackathon (pitch 16 h, résultats 17 h)
- [ ] H1 — premiers utilisateurs réels
- [ ] H2 — lancement

## Bloqueurs

| # | Bloqueur | Impact | Owner | État |
|---|---|---|---|---|
| B1 | Rôle admin organisation Aiven pour lien GitHub → Runtime | Déploiement H0 | ? | **Ouvert** |
| B2 | Crédits ElevenLabs + numéro Twilio vérifié | Étape 8 (dégradable) | ? | Ouvert |
| B3 | Contrats B/C du benchmark non affectés | Étape 5 | ? | Ouvert |

## Tâches H0

| # | Tâche | Dépend de | Débloque | État |
|---|---|---|---|---|
| 1 | Squelette FastAPI + Dockerfile + Runtime + PG + migration test | — | tout | Ready |
| 2 | Ingestion 12 CG + Intake (MAAF + CP Karim) → profil, leviers, deadlines | 1 | 3, 5 | Blocked by 1 |
| 3 | Claims Agent minimal + **review node (8 contrôles)** | 1 | 4, 5, 6 | Blocked by 1 |
| 4 | Telegram : deep link, médias, ask_client, interrupt/resume, dédoublonnage, test reprise | 3 | 7 | Blocked by 3 |
| 5 | `bench/` 3 cas × 3 variantes | 2, 3 | slide | Blocked by 2, 3 |
| 6 | AgentMail + Insurer Simulator (avec quittance) | 3 | 7 | Blocked by 3 |
| 7 | Site onboarding réduit + mandat + 3 consentements | 2 | démo | Blocked by 2 |
| 8 | ElevenLabs appel + post-call + provenance orale | 6 | démo | Blocked by 6 (dégradable → widget) |
| 9 | Vocaux Telegram, reprise démontrée, pitch | 4, 6 | — | Blocked |

Parallélisme : 2 ‖ 3 · 4 ‖ 6 · 7 ‖ 8. **1–5 non négociables.**

## Critères d'acceptation à cocher avant le pitch

- [ ] AC-1 profil de garanties MAAF avec pages
- [ ] AC-3 déclaration J0 avant toute demande de pièce
- [ ] AC-4 doublon refusé
- [ ] AC-6 avenant change le plafond
- [ ] AC-7 reprise après redémarrage
- [ ] AC-8 réponse orale `to_confirm`
- [ ] AC-9 quittance détectée, pas d'acceptation implicite
- [ ] AC-11/12 review bloque avis et montant non sourcé
- [ ] AC-15 bench mesuré (aucun chiffre non mesuré sur la slide)
- [ ] AC-16 isolation deux comptes

## Questions ouvertes (voir PRD §6)

Q1 admin Aiven · Q3 voix · Q4 langue vers assureur · Q6/Q7 avis juridique + rémunération · Q8 vérifier n° de jurisprudence sur Légifrance avant affichage · Q9 contrats B/C.

## Journal

| Date | Événement |
|---|---|
| 2026-10-22 | PRD v1 rédigé à partir de CONTEXTE §1–14, 08a–08d, 09a–09c |
