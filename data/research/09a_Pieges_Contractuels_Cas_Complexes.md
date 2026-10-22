# 09a — Pièges contractuels et cas complexes : ce qui fait perdre un dossier MRP

> Rédigé le 22/10/2026. Complète `08d` (processus) : ici, les mécanismes qui réduisent ou annulent une indemnisation, avec le levier juridique qui y répond et le comportement attendu de l'agent.
> Règle de lecture : chaque fait est suivi de sa source. **(non vérifié)** = hypothèse de travail. Ceci est une synthèse de recherche, pas un avis juridique.

---

## 0. Pourquoi ce fichier

Un dossier de sinistre « simple » se gère de gré à gré. La valeur de l'agent se joue sur les cas où l'assureur invoque un mécanisme de réduction ou d'exclusion. Ce fichier liste les mécanismes, dans l'ordre de fréquence estimée pour un commerçant en MRP.

---

## 1. Règle proportionnelle de capitaux (sous-assurance) — le cas n°1 à l'échelle

**Mécanisme.** Art. L121-5 C. assur. : si la valeur réelle de la chose assurée au jour du sinistre excède la somme garantie, l'assuré « supporte une part proportionnelle du dommage, sauf convention contraire ». Formule : `indemnité = dommages × (somme assurée / valeur réelle)`. S'applique de plein droit, sinistre partiel ou total, indépendamment de la bonne foi de l'assuré. Sources : [Juriblio L121-5](https://juriblio.fr/codes/code-des-assurances/partie-legislative/livre-ier/titre-ii/chapitre-ier/article-l121-5), [Index Habitation](https://www.index-habitation.fr/multirisque/sinistres/regle-proportionnelle-de-capitaux).

**Ampleur.** Aviva estime ~33 % des PME sous-assurées sur leurs bâtiments, et ~40 % des sinistres immobiliers ajustés à la baisse pour sous-assurance (données assureur UK, ordre de grandeur transposable). Source : [Aviva Broker Underinsurance](https://connect.avivab2b.co.uk/broker/resources/product-support/Underinsurance/).

**Les contres, dans l'ordre où l'agent les vérifie** ([Ariane Gire — 6 points clés](https://www.arianegire.fr/publications/les-six-points-clefs-de-la-regle-proportionnelle-de-capitaux)) :

1. **Clause de tolérance** : seuil (ex. 15 %) en deçà duquel la règle ne joue pas.
2. **Clause de réversibilité / report d'excédent** : la valeur de l'ensemble des biens est prise en compte, pas celle du seul bien sinistré.
3. **Clause d'indexation** : la valeur assurée suit un indice — la sous-assurance peut ne pas exister au jour du sinistre.
4. **Clause de première assurance / valeur agréée** : indemnité déterminée à l'avance, écarte la règle.
5. **Charge de la preuve** : c'est à l'assureur d'établir la valeur réelle au jour du sinistre. Contester son estimation est légitime.

**Agent** : à l'onboarding, comparer sommes assurées vs. éléments de valorisation disponibles et signaler un risque de sous-assurance (alerte, pas conseil). Au sinistre : avant de concéder une réduction, vérifier les 4 clauses dérogatoires dans les CG/CP ; exiger la preuve de la valeur réelle retenue par l'assureur.

## 2. Règle proportionnelle de prime (déclaration inexacte à la souscription)

**Mécanisme.** Art. L113-9 C. assur. : si l'omission ou la déclaration inexacte n'est pas intentionnelle, l'indemnité est réduite dans la proportion du taux de prime payé vs. prime qui aurait dû l'être. Si intentionnelle → nullité possible (L113-8). Source : [Le Codex](https://www.avocats-juridiques.fr/assurance-multirisque-pro-comment-gerer-un-refus-dindemnisation/).

**Nuance clé.** L'assuré ne répond que des questions posées par l'assureur (L113-2, 2° : le questionnaire). Une omission sur un point jamais demandé ne peut pas être opposée. La mauvaise foi / l'intentionnalité est à prouver par l'assureur.

**Temporalité** : sinistre avant que l'assureur n'ait choisi résiliation ou nouvelle prime → traité comme une inexactitude découverte après sinistre (règle proportionnelle applicable, Cass. 2e civ., 2 mars 2017, n° 15-27831). Source : [Krajeski, U. Toulouse](https://publications.ut-capitole.fr/id/eprint/23892/1/23892_Krajeski.pdf).

**Agent** : conserver la déclaration de risque initiale et les questionnaires ; si l'assureur invoque L113-9, vérifier (a) que la question existait, (b) la base du calcul de proportion, (c) contester l'intentionnalité si nullité invoquée.

## 3. Aggravation du risque non déclarée

**Mécanisme.** L113-2, 3° : déclarer en 15 jours (LRAR) les circonstances nouvelles aggravant le risque. L113-4 : l'assureur peut résilier ou proposer un nouveau taux ; non-déclaration → garantie mise en jeu.

**Contre important.** L'assureur ne peut plus se prévaloir de l'aggravation s'il en a été informé « de quelque manière que ce soit » et a continué à encaisser les primes ou payé une indemnité (L113-4, dernier al.). **La preuve de ce que l'assureur savait est donc un actif du dossier.**

**Agent** : traiter tout changement d'activité, travaux, stockage de nouvelles marchandises comme un événement déclenchable (« Should this be declared to your insurer? ») ; archiver tous les échanges montrant la connaissance de l'assureur.

## 4. Déchéance pour déclaration tardive

**Mécanisme.** Délais : 2 jours ouvrés (vol), 5 jours ouvrés (général), contractuels au-delà. L113-2 : la déchéance n'est opposable que si (a) clause contractuelle la prévoit, (b) l'assureur prouve un préjudice causé par le retard, (c) pas de cas fortuit/force majeure. Rappelé en jurisprudence : Cass. com., 7 mars 2018. Sources : [Legifrance L113-2](https://www.legifrance.gouv.fr/codes/id/LEGISCTA000006157200), [Journal Actu](https://www.avocat-journalactu.fr/comment-contester-le-refus-dindemnisation-de-votre-assurance-multirisque-entreprise/).

**Agent** : envoyer la déclaration immédiatement, même incomplète — une déclaration n'est pas un dossier chiffré ; tracker les délais comme des tâches ; documenter toute force majeure ; si déchéance opposée, exiger la preuve du préjudice.

## 5. Déchéance pour fausse déclaration sur le sinistre — risque existentiel pour un agent

**Mécanisme.** Clauses type : « toute fausse déclaration sur la nature, les causes, les circonstances ainsi que les conséquences du sinistre […] vous prive de tout droit à garantie ». Validité : caractères très apparents (L112-4) + **l'assureur doit établir la mauvaise foi de l'assuré**. Jurisprudence constante : Cass. 2e civ., 5 juil. 2018, n° 17-20.491 ; 15 déc. 2022, n° 20-22.836 ; **12 fév. 2026, n° 24-18.594** (la déchéance n'est pas une sanction disproportionnée ; l'assuré qui a menti sur les conséquences perd sa garantie). Sources : [Doctrine Cass. 2026](https://www.doctrine.fr/d/CASS/2026/CASSP88C53E2C8DA6189276CB), [LibreJustice](https://librejustice.fr/decision/fr/tAwtgaai1cKK).

**Conséquence produit** : toute exagération, arrondi ou fait non vérifié envoyé à l'assureur expose le commerçant à perdre TOUTE la garantie du sinistre — y compris les postes légitimes. Un agent qui « aide trop » détruit le dossier. Corollaire : la provenance et le statut de vérification de chaque fait (déjà prévu dans la mémoire du projet) n'est pas un luxe, c'est la protection principale du client.

## 6. Exclusions de garantie

**Règle.** L113-1 : les exclusions doivent être **formelles et limitées** — claires, précises, sans besoin d'interprétation, et ne peuvent vider la garantie de sa substance. L112-4 : nullités, déchéances, exclusions en caractères très apparents. Charge de la preuve des conditions de fait de l'exclusion : à l'assureur, non réversible par le contrat (Cass. 2e civ., 2 avr. 1997). Interprétation contra proferentem (C. civ. 1190, contrat d'adhésion contre le rédacteur). Sources : [Gdroit charge de la preuve](https://gdroit.fr/droit-des-assurances/sinistre-dans-le-cadre-du-contrat-dassurance-la-charge-de-la-preuve/), [Cass. 21-15.392 (COVID, perte d'exploitation)](https://www.courdecassation.fr/en/decision/638852d601d0fb05d44b0982), [Cass. 23-14.482 (exclusion mal rédigée)](https://www.doctrine.fr/d/CASS/2025/CASSPA93FD78E859BAF922DD3).

**Pratique abusive documentée** : qualification erronée du sinistre pour le faire entrer dans une exclusion ; interprétation extensive ; mélange garanties/exclusions dans une même clause (risqué pour l'assureur, cf. Trillat). Sources : [Journal Actu](https://www.avocat-journalactu.fr/comment-contester-le-refus-dindemnisation-de-votre-assurance-multirisque-entreprise/), [Trillat & Associés](https://www.trillatassocies.com/data/Actualite/Exclusions-contractuelles-et-charge-de-la-preuve.pdf).

**Agent** — checklist quand une exclusion est invoquée : (a) la clause est-elle en caractères très apparents ? (b) sa lecture exige-t-elle une interprétation ? → argument « non formelle » ; (c) vide-t-elle la garantie de sa substance ? (d) quelle preuve l'assureur apporte-t-il des conditions de fait ?

## 7. Émeutes / mouvements populaires (le cas d'usage du projet)

Rappel `08d` : L121-8 — l'assureur ne couvre pas émeutes/mouvements populaires **sauf clause contraire**, et c'est à lui de prouver la qualification en émeute. Point pratique : la qualification du fait (pillage isolé, vandalisme, émeute) détermine la garantie mobilisée — vol, vandalisme, bris de glace, ou clause émeute expresse. L'agent doit construire la qualification la plus favorable supportée par les preuves, pas accepter celle de l'assureur.

## 8. Délai de carence

Les MRP prévoient des carences par garantie : repères ~15 j (incendie), ~30 j (vol), 30-90 j (perte d'exploitation) ; la garantie optionnelle « protection fiscale » MAAF en a une. Sources : [Assur-life](https://www.assur-life.com/assurance-professionnelle-quels-delais-de-carence-prevoir-pour-etre-couvert/), [CG MAAF §28](https://handicapzero.maaf.fr/mon-activite-professionnelle/multirisque-professionnelle/conditions-generales-multirisque-professionnelle/la-vie-du-contrat/28-la-vie-du-contrat-conclusion-prise-deffet-resiliation). **Un sinistre pendant la carence est légitimement non couvert** — cas où « gagner » est impossible ; le rôle de l'agent est de le dire vite et de basculer sur les autres recours (responsable tiers, État).

## 9. Obligations de prévention / mesures de sécurité

Alarme fonctionnelle, rideau métallique, contrôle électrique annuel (type APAVE), conservation des preuves avant travaux : les CG les posent ; leur violation ouvre exclusion ou réduction. Dans l'affaire Cass. 2017 citée plus haut, le défaut de transmission des rapports annuels a justifié la règle proportionnelle. **Agent** : extraire les obligations de prévention à l'onboarding en checklist datée ; au sinistre, vérifier l'état de conformité AVANT l'assureur (alarme en service la nuit du vol, etc.) ; si manquement, préparer la réponse (préjudice causal requis ? proportionnalité ?).

## 10. Perte d'exploitation — le plus gros poste, le plus technique

- Ne joue que si (a) garantie PE souscrite (CP), (b) causée par un dommage matériel garanti sur le « lieu de risque » (cf. CG type IME : événements garantis → dommages matériels directs → PE). Source : [CG IME Pertes d'exploitation](https://imentreprises.fr/ime/services-en-ligne/doc/CG/CG_PERTES-EXPLOITATION.pdf).
- Calcul : perte de **marge brute** (CA − charges variables) sur la période d'indemnisation souscrite (12/18/24 mois), + frais supplémentaires ; clause d'ajustement d'assiette ~20 % courante. Source : [Matmut](https://www.matmut.fr/pro/assurance-activite/conseils/calcul-indemnisation-perte-exploitation).
- La période d'indemnisation n'est pas affectée par une résiliation post-sinistre (CG IME art. 2) — point à vérifier si l'assureur menace de résilier en cours de dossier.
- Contentieux de référence : fermetures administratives COVID — bataille entière sur le caractère « formel et limité » des exclusions (Cass. 21-15.392).
- **Agent** : collecter tôt liasse fiscale, CA mensuel N et N-1, charges variables ; construire le modèle de marge brute avec l'expert-comptable du commerçant ; documenter la chaîne causale dommage → interruption.

## 11. Cumul de contrats et répartition

L121-4 : plusieurs assurances sur le même risque → obligation de les déclarer entre elles ; chacun paie dans la limite de sa garantie ; total ≤ dommage réel (L121-1). Le cumul dolosif est sanctionné, le cumul innocent ne l'est pas. Cas fréquent : MRP + bris de glace séparé + garantie carte pro. **Agent** : recenser tous les contrats à l'onboarding ; répartir les postes sur les contrats les plus favorables ; déclarer les cumuls proprement (LRAR si requis).

## 12. Locataire / propriétaire et recours

- Risques locatifs : le commerçant locataire garantit les dommages locatifs au bailleur ; son MRP couvre son contenu et sa responsabilité — deux flux de réclamation distincts, ne pas les mélanger.
- Responsable tiers : si un tiers a causé le sinistre, l'assureur indemnise puis est subrogé (L121-12) ; le commerçant ne doit rien signer qui prive l'assureur (ou lui-même) du recours.
- Émeutes : recours contre l'État, art. L211-10 CSI — préfet puis TA, prescription 4 ans ; limite CE 28/10/2022 (actes prémédités de groupe organisé). Déjà noté en `08d` ; l'agent doit le garder comme piste parallèle quand la garantie échoue.

## 13. Vétusté différée et valeur à neuf — argent laissé sur la table

Le complément « valeur à neuf » n'est versé qu'après remplacement effectif, sur factures, sous ~2 ans. Un commerçant qui ne sait pas qu'il doit réclamer ce complément le perd. **Agent** : à la clôture de tout dossier avec vétusté, créer la tâche long terme « complément valeur à neuf » avec échéance contractuelle et factures attendues.

## 14. Prime impayée / suspension de garantie

L113-3 : garantie suspendue 30 jours après mise en demeure restée sans effet ; sinistre pendant suspension = pas de couverture. **Agent** : au premier contact sinistre, vérifier l'état des primes (question directe au commerçant + demande d'attestation à l'assureur) avant de promettre quoi que ce soit.

---

## Cartographie rapide → ce que l'agent doit savoir faire

| Piège | Signal à détecter | Levier |
|---|---|---|
| Sous-assurance | Sommes assurées < valeur probable | Clauses tolérance/réversibilité/indexation ; preuve valeur réelle à la charge de l'assureur |
| Inexactitude souscription | Refus invoquant L113-8/9 | Question jamais posée = non opposable ; intentionnalité à prouver |
| Aggravation non déclarée | Changement d'activité/travaux | Preuve de connaissance de l'assureur + primes encaissées |
| Déclaration tardive | Refus sur délai | Préjudice à prouver + force majeure |
| Fausse déclaration sinistre | Tout fait non vérifié | Ne jamais affirmer non sourcé — protection en amont |
| Exclusion | Refus sur clause | L112-4 forme + « formelle et limitée » + preuve à l'assureur |
| Carence | Sinistre < X jours après effet | Recours alternatifs (tiers, État) |
| Prévention | Alarme/sécurité requise | Conformité vérifiée avant l'assureur |
| PE | Interruption d'activité | Marge brute + causalité + période d'indemnisation |
| Cumul | Plusieurs contrats | Répartition postes + déclaration croisée |
| Vétusté | Indemnité en 2 temps | Tâche complément valeur à neuf à ~2 ans |
| Prime impayée | Suspension possible | Statut prime vérifié en tout premier |
