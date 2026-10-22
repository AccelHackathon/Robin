# 09c — Périmètre légal de l'agent et synthèse des capacités requises

> Rédigé le 22/10/2026. Deux parties : (1) ce que la loi française permet ou interdit à un service autonome qui gère des sinistres pour des commerçants — le risque est réel et documenté par la jurisprudence ; (2) la synthèse de toute la recherche (`08a`–`09b`) en capacités concrètes à construire.
> Règle de lecture : chaque fait est suivi de sa source. **(non vérifié)** = hypothèse. Synthèse de recherche, pas un avis juridique — la qualification du service doit être validée par un juriste avant lancement commercial.

---

## Partie 1 — Le périmètre légal : deux lignes rouges documentées

### 1.1. Distribution d'assurance (L511-1 / DDA) — frontière fine

L'art. L511-1 du Code des assurances définit la distribution comme incluant **« contribuer à la gestion et à l'exécution des contrats d'assurance, notamment en cas de sinistre »**, contre rémunération. Être distributeur ⇒ immatriculation ORIAS, capacité professionnelle, RC pro, formation DDA 15 h/an, contrôle ACPR.

Nuance clé posée par l'ACPR elle-même : « l'activité qui consiste **exclusivement** en la gestion, l'évaluation et le règlement des sinistres n'est pas considérée comme de la distribution », mais « contribuer **plus largement** à la gestion et à l'exécution des contrats » y entre. Source : [ACPR — intermédiaires d'assurance](https://acpr.banque-france.fr/fr/professionnels/lacpr-vous-accompagne/intermediaires/intermediaires-dassurance).

- La frontière entre « gérer un sinistre pour l'assuré » (hors distribution) et « contribuer à l'exécution du contrat » (distribution) n'est pas tranchée proprement pour un service comme le nôtre — **zone grise, à qualifier par un juriste**.
- Le critère décisif retenu par la doctrine est la **rémunération en lien avec l'activité** : un % sur l'indemnisation peut tirer le modèle vers la distribution selon sa construction. Source : [Blog Deloitte](https://blog.avocats.deloitte.fr/le-porteur-dune-police-dassurance-souscrite-pour-le-compte-dun-tiers-doit-il-etre-considere-comme-un-intermediaire-en-assurance/).
- Si la conclusion penche « distribution » : les voies sont ORIAS propre (courtier à titre accessoire ?) ou le mandatement sous un intermédiaire existant (MIAD, R511-2). Source : [Académie Conformité](https://academieconformite.fr/courtier-soustraitance-gestion-sinistres-prestataire-externe/).

### 1.2. Consultation juridique (loi 1971) — le risque le plus sérieux, jurisprudence directe

**Cass. 2e civ., 9 décembre 2015, n° 14-24.268** — un **courtier en assurance** (donc déjà ORIAS) qui fournit, à titre habituel et rémunéré, « un avis personnalisé sur les offres transactionnelles des assureurs, en négocie le montant » et oriente en cas d'échec vers un avocat : **exercice illégal de la consultation juridique**, interdiction + publicité. Ces prestations ne relevaient ni du suivi d'un contrat souscrit par son intermédiaire, ni de travaux préparatoires à une souscription. Source : [LibreJustice](https://librejustice.fr/decision/fr/xJ63RDysOGQm).

**CA Nîmes, 7 juillet 2023** (confirmé, pourvoi rejeté) — un « mandataire d'assuré » qui analysait les propositions d'indemnisation des assureurs et conseillait ses clients sur les suites : même qualification, interdiction sous astreinte de 1 000 €/infraction. Source : [CNB](https://cnb.avocat.fr/actualite/le-cnb-et-l-ordre-des-avocats-de-marseille-obtiennent-la-condamnation-d-un-mandataire-d-assure-devant-la-cour-de-cassation).

**La définition qui fait basculer** : la consultation juridique est « toute prestation intellectuelle **personnalisée** qui tend à fournir un avis sur une situation soulevant des difficultés juridiques ainsi que sur la(les) voie(s) possible(s) pour les résoudre, concourant à la prise de décision du bénéficiaire ». Ce qui reste licite : l'« **information à caractère documentaire** » — renseigner sur l'état du droit ou de la jurisprudence sans avis personnalisé. Source : [BACA Lyon — nullité pour objet illicite](https://publications-prairial.fr/bacaly/index.php?id=1000).

**Positionnement décidé par Mathis (22/10/2026)** : le service est une **couche procédurale pure** — il simplifie le processus et fait ce qu'il est censé faire (déclarer, collecter, transmettre, relancer, documenter, expliquer factuellement), point final. **L'agent n'exécute pas le remboursement** (l'assureur paie le commerçant directement — ce qui clos aussi le point ouvert « ne pas supposer que le service encaisse les fonds ») et **ne décide aucun montant** : tout chiffre transmis reflète les pertes documentées du commerçant ou son instruction explicite. Il ne conseille pas, ne négocie pas, ne « gagne » pas — il supprime la friction.

Ce périmètre correspond à l'option A ci-dessous et évacue l'essentiel du risque « consultation juridique » — **à condition qu'il soit tenu dans ce que l'agent produit, pas seulement dans le marketing** : la jurisprudence qualifie les actes, pas l'intention. Reste à verrouiller dans les sorties : aucun montant ne doit jamais provenir de l'agent (seulement de preuves ou d'instructions du commerçant), et aucune formule ne doit laisser entendre une appréciation juridique personnalisée.

Frontière opérationnelle à graver dans le design :

| Enlève la friction (licite sous mandat) | Bascule vers le conseil (risque) |
|---|---|
| Déclarer à temps, transmettre les pièces, constituer l'état des pertes | Évaluer « vos chances » de gagner |
| Demander un statut, relancer, préparer le dossier d'expertise | Négocier le montant avec argumentaire juridique en son nom (« en négocie le montant » était reproché dans Cass. 2015) |
| Détecter une quittance et expliquer factuellement son effet (« ce document éteint les recours futurs sur ce sinistre ») | Dire « n'acceptez pas » / « cette offre est insuffisante juridiquement » |
| Chiffrer l'écart : « l'offre couvre 62 % de vos pertes documentées ; postes non couverts : X, Y » | Formuler une recommandation pondérée |
| Préparer la contre-analyse chiffrée et sourcée ; le commerçant choisit le chiffre et la stratégie ; l'agent exécute son instruction | Choisir le montant de contre-proposition soi-même |

**Application à notre agent — la tension est frontale** : le design actuel prévoit que l'agent « explique l'offre et peut formuler une recommandation ». Une recommandation personnalisée « acceptez / refusez cette offre » fondée sur le droit applicable = le cœur exact des deux affaires condamnées. Options de mitigation (décision produit/juridique à trancher, pas une recommandation d'implémentation) :

| Option | Ce que fait l'agent | Risque résiduel |
|---|---|---|
| A. Documentaire strict | Compare l'offre aux postes/chiffres du dossier, cite les clauses et leurs sources, chiffre les écarts — sans jamais formuler d'avis sur la décision | Plus faible ; reste la question de savoir si la comparaison chiffrée constitue déjà un « avis » |
| B. Recommandation factuelle bornée | « L'offre couvre 62 % de votre état des pertes documenté ; postes non couverts : X, Y » + présente les voies génériques (précision, contestation, médiation, avocat) sans peser | Moyen — la frontière avis/constat est factuelle |
| C. Recommandation + escalade humaine | L'agent recommande, mais tout dossier contesté ou offre significative est validée par un expert d'assuré/avocat partenaire | Juridiquement plus sûr ; contredit la contrainte « zéro humain » de Mathis |
| D. Qualification + montage légal | Avis juridique préalable, structuration (ORIAS/MIAD, éventuel avocat salarié ou cabinet partenaire), CG du service écrivant le périmètre | Nécessaire quelle que soit l'option — pas une alternative |

**Point décisif pour le modèle économique** : les deux condamnations reposent sur « à titre habituel et rémunéré ». Un service payé au % de l'indemnisation qui conseille sur les offres coche les deux critères. **La validation juridique n'est pas optionnelle avant la première facture.**

### 1.3. Ce qui est libre et utile

- Mandat de représentation pour les démarches opérationnelles (déclarer, transmettre, demander statut, relancer) : licite — c'est de l'exécution, pas de la consultation.
- La profession d'**expert d'assuré** n'est pas réglementée (pas de certification obligatoire ; Fedexa/Ifpass volontaires) ; honoraires libres, pratique observée **5–15 % de l'indemnisation** ou forfait/barème Upemeic. Sources : [L'Argus — expert d'assuré](https://www.argusdelassurance.com/juriscope/expert-d-assure-une-profession-encore-en-construction.206112), [RM 2129](https://questions.assemblee-nationale.fr/q15/15-2129QE.htm). → Benchmark prix + voie de structuration possible (opérer COMME/AVEC un expert d'assuré).
- Benchmarks de rémunération au résultat confirmés à l'étranger : public adjusters ~10 % (plafonné dans plusieurs États US). Voir `09b` §5.

---

## Partie 2 — Synthèse : les 10 capacités qui font un agent « expert-grade »

Lecture croisée de `08a`–`08d` (corpus contrats, cas réels, processus) et `09a`–`09b` (pièges, tactiques, playbooks). Une sophistication crédible face à un expert d'assurance humain tient en dix capacités ; chacune est vérifiable dans le benchmark.

### C1. Détermination de garantie sur documents réels
Parser CG + CP + avenants ; à la date du sinistre (l'avenant applicable est un moment de démo déjà prévu). Vérifier pour chaque refus : clause en caractères apparents (L112-4), caractère « formel et limité » (L113-1), et si l'assureur apporte la preuve des conditions de fait. **Test benchmark** : sur le corpus de 12 CG, produire pour un cas donné la liste des garanties candidates + exclusions opposables avec page citée.

### C2. Machine à deadlines
Tous les délais comme tâches trackées : déclaration 2 j/5 j, LRAR aggravation 15 j, carence par garantie, expertise, réclamation→médiation 2 mois, prescription 2 ans avec événements interrupteurs (LRAR règlement, désignation expert), complément valeur à neuf ~2 ans. **Test** : un dossier simulé sur 24 mois ne perd aucune échéance.

### C3. Discipline de preuve (anti-déchéance)
Chaque fait porte source + statut de vérification + auteur. Rien de non vérifié ne part à l'assureur. C'est la capacité qui protège le client de l'agent lui-même (Cass. 2026 : la déchéance pour fausse déclaration est validée). **Test** : injecter une facture contradictoire → l'agent la marque non confirmée et questionne, jamais il ne l'affirme.

### C4. Détection de sous-assurance et des clauses dérogatoires
À l'onboarding : sommes assurées vs. indices de valeur → alerte. Au refus : vérifier tolérance / réversibilité / indexation / valeur agréée avant de concéder la règle proportionnelle ; exiger la preuve de la valeur réelle. ~40 % des sinistres immobiliers UK subissent cet ajustement → **le levier de valeur n°1**. **Test** : cas `08c` avec somme assurée < valeur réelle, contrat avec clause de tolérance → la réduction est contestée et chiffrée correctement.

### C5. Dissection de refus
Lettre de refus → motif classé (non-garantie / exclusion / déchéance / réduction / suspension) → clause invoquée citée → contre-mesure du playbook (`09b` §1) → réponse LRAR motivée et sourcée. **Test** : sur 5 lettres-types, la classification et la contre-mesure sont correctes à 100 %.

### C6. Préparation et suivi d'expertise
Checklist pré-visite (état des pertes chiffré, photos indexées, positions écrites remises), notes propres pendant, observations écrites après ; garantie « honoraires d'expert » extraite à l'onboarding ; seuil de recommandation de contre-expertise. **Test** : scénario expertise — le dossier remis à l'expert contient tous les postes avec clause + preuve.

### C7. Gate signature
Détection automatique de quittance / « solde de tout compte » / « renonciation » / « transaction » / « définitif » dans tout document de l'assureur → explication des postes couverts vs. abandonnés → décision explicite du commerçant. Absence de réponse ≠ acceptation (déjà décidé). **Test** : une quittance déguisée en « accusé de règlement » est interceptée.

### C8. Évaluation d'offre chiffrée
Rapprochement poste par poste : couvert/partiel/refusé/absent ; vétusté vs. formule ; plafonds ; franchise ; règle proportionnelle ; provisionnel vs. définitif. Restitution à l'assuré en langage clair avec écart €. ⚠️ Formuler comme **comparaison chiffrée** (cf. §1.2) — la formulation « je recommande d'accepter/refuser » est le point de risque juridique à trancher.

### C9. Cadence de dossier (playbook public adjuster)
Communications loguées datées, positions de l'assureur verbatim avec interlocuteur, relances planifiées à l'envoi, deadlines de l'assureur suivis, chaque dépassement exploité comme levier. C'est la persistance procédurale — là où un humain débordé abandonne, l'agent ne fatigue pas. **Test** : un assureur-simulé qui traîne → séquence relance → LRAR → réclamation, datée et traçable.

### C10. Escalade lucide et périmètre assumé
Savoir ce qu'on ne peut pas gagner (carence, exclusion valide, suspension pour prime impayée) et le dire vite avec les recours alternatifs (tiers responsable, État L211-10 CSI). Savoir où le service s'arrête : contestation juridique sérieuse → expert d'assuré / avocat (cf. §1.2 — c'est aussi une obligation légale, pas seulement de la prudence). **Test** : cas non couvert (sinistre en carence) → l'agent le détecte et pivote vers les voies alternatives au lieu de fabriquer un dossier.

---

## Lecture honnête pour le pitch : la promesse est le temps et l'argent sauvés, pas la victoire

La valeur se formule en friction supprimée, mesurable :

- **Temps** : constitution de l'état des pertes (retrouver factures, chercher chaque clause dans 70–120 pages, chiffrer) — métrique déjà prévue au benchmark (`CONTEXTE` §7) ; relances et suivi que le commerçant n'a pas le temps de tenir.
- **Argent** : postes réclamables que le commerçant ignore (FCA : les refus arrivent « en choc », la PE rapporte plus que prévu — `09b` §6) ; réductions contestées (sous-assurance : ~40 % des sinistres immobiliers UK ajustés — Aviva) ; argent laissé sur la table (complément valeur à neuf à ~2 ans ; honoraires d'expert garantis au contrat).
- **Erreurs évitées** : déclaration tardive, preuve manquante, quittance signée trop tôt, fait non vérifié transmis — chacune documentée comme cause réelle de perte (`09a`, `09b`).

Les données le confirment : ~50 % des gros sinistres commerciaux sont disputés (Mactavish), la voie judiciaire donne ~32 % à l'assuré en ~3 ans — la valeur n'est pas de « gagner », c'est que le dossier n'ait jamais besoin d'être disputé, et qu'il soit complet quand il l'est.

**Démo pitch-ready** : deux dossiers identiques — le commerçant naïf déclare tard, sous-chiffre les postes, oublie la clause de tolérance et signe une quittance ; l'agent déclare à J0, mobilise les clauses dérogatoires, documente chaque échange, chiffre l'écart de l'offre poste par poste. Le delta en heures + € + technicalités évitées, c'est la mesure — sans jamais que l'agent « conseille » : il exécute et chiffre, le commerçant décide.
