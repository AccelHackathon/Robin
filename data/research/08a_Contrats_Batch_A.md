# 08a — Contrats multirisque pro réels, batch A (AXA, Allianz, Generali, Groupama, Société Générale/Sogessur)

> Objectif : extraire **depuis le texte réel des Conditions Générales** tout ce qu'un commerçant pillé/vandalisé (émeutes des 17-18 octobre 2026) peut légitimement réclamer.
> Règle : chaque ligne renvoie au document local + page + citation courte **verbatim**. Si une clause n'est pas dans le document : **« absent »**. Rien n'est inventé.
> Convention de pages : « p. X » = numéro **imprimé** sur la page ; « PDF n » = numéro de page du fichier PDF quand il diffère.
> Rappel : les CG fixent le cadre. **Les montants, options (valeur à neuf, PE, vol…) et franchises réels sont dans les Conditions/Dispositions Particulières (CP/DP) du client.** L'agent doit toujours croiser CG + CP.

## Inventaire des documents (batch A)

| # | Assureur / produit | Type | Version | Pages | Fichier local (pdf / txt) |
|---|---|---|---|---|---|
| 1 | **Generali – « 100% Pro » Multirisque professionnelle des artisans, commerçants et prestataires de services** | Dispositions Générales complètes | GA5M70F – Janvier 2022 | 72 | `contrats/pdf/Generali_100Pro_CG_GA5M70F.pdf` / `contrats/txt/Generali_100Pro_CG_GA5M70F.txt` |
| 2 | **AXA France – « Atouts PME » Multirisque** | Conditions Générales complètes | Réf. 975637 I (PDF créé 07/2023) | 88 | `contrats/pdf/AXA_AtoutsPME_CG.pdf` / `contrats/txt/AXA_AtoutsPME_CG.txt` |
| 3 | **Allianz IARD – « Allianz Actif Pro »** (prestataires de services et professions libérales) | Dispositions Générales complètes | REG36387 – V06/22 | 124 | `contrats/pdf/Allianz_ActifPro_DG.pdf` / `contrats/txt/Allianz_ActifPro_DG.txt` |
| 4 | **Sogessur (Société Générale) – « La Multirisque des Pros » Commerçants Artisans** | Conditions Générales complètes | « 160201 CG MRPROS », tarif en vigueur au 01/03/2016 | 60 | `contrats/pdf/SG_Sogessur_MultirisqueDesPros_CommercantsArtisans_CG.pdf` / `contrats/txt/SG_Sogessur_MultirisqueDesPros_CommercantsArtisans_CG.txt` |
| 5 | AXA France – « Mon Pack Entrepreneur » (micro-entrepreneurs sans salarié) | Conditions Générales complètes | Réf. 981030 B – Mai 2024 | 108 | `contrats/pdf/AXA_MonPackEntrepreneur_CG.pdf` / `contrats/txt/AXA_MonPackEntrepreneur_CG.txt` |
| 6 | Groupama – « Multirisque des professionnels » (AMP) | **Dispositions Générales communes uniquement** (les garanties sont dans des « fascicules » séparés, non trouvés) | 2015 (indd 01/2016) | 24 | `contrats/pdf/Groupama_MRPro_DG.pdf` / `contrats/txt/Groupama_MRPro_DG.txt` |

**Sources (URL de téléchargement)**
1. Generali : https://www.air-assurances.com/pdf_doc/hangar_2022/CG_GA5M70F.pdf (copie hébergée par un courtier ; document Generali, référence GA5M70F)
2. AXA Atouts PME : https://media.axa.fr/content/dam/axa-fr/image/pro/documents-informations/pdf-assurance-atout-pro-pme-cg.pdf (site officiel AXA)
3. Allianz Actif Pro : https://www.gpm.fr/wp-content/uploads/2026/06/CG-MRP-ALLIANZ.pdf (copie hébergée par un courtier)
4. Sogessur / Société Générale : https://static.societegenerale.fr/pro/PRO/Repertoire_par_type_de_contenus/Fichier_a_telecharger/Fiches_numeriques/cg-commercants-artisants.pdf (site officiel SG)
5. AXA Mon Pack Entrepreneur : https://media.axa.fr/content/dam/axa-fr/image/pro/documents-informations/pdf-mon-pack-entrepreneur-cg.pdf (site officiel AXA)
6. Groupama : https://www.coover.fr/wp-content/uploads/2019/10/conditions-generales-responsabilite-civile-professionnelle-groupama.pdf (copie tierce)

**Limites honnêtes**
- Allianz : les DG « Profil Pro Artisan/Commerçant » (produit dédié commerce) ne sont pas publiées en ligne ; on a analysé **Actif Pro** (même assureur, même architecture, cible services/professions libérales). À présenter comme « contrat Allianz », pas comme « le contrat des commerçants Allianz ».
- Groupama : seul le tronc commun (procédure, délais, expertise) est disponible ; **les garanties émeutes/vol/frais ne sont pas dans ce document → « absent (fascicule non disponible) »**.
- Sogessur : version 2016, peut avoir été mise à jour depuis.
- Generali (Janvier 2022) et Allianz (06/2022) sont antérieurs à la réforme « garantie émeutes » évoquée dans la presse 2026 : ne pas présumer qu'ils reflètent un éventuel nouveau régime légal.

---

## 1. Generali — 100% Pro (GA5M70F, janvier 2022)

Fichier : `contrats/txt/Generali_100Pro_CG_GA5M70F.txt` — pages imprimées = pages PDF.

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| **Émeutes / vandalisme (garantie)** | « Les détériorations provoquées par : • des actes de vandalisme* à la condition que l'Assuré* dépose une plainte auprès des autorités compétentes dans les 24 heures […] • des émeutes et mouvements populaires » | 11 | Émeutes **et** vandalisme sont dans la garantie « Incendie, événements assimilés et vandalisme » : locaux, agencements, contenu, marchandises, espèces. **Plainte sous 24 h** pour le vandalisme. |
| Définition vandalisme | « Dégradation ou destruction volontaire d'un bien commise par un tiers* » | 10 | Pas besoin d'identifier l'auteur. |
| Exclusion tags extérieurs | « Les détériorations provoquées par les graffitis, tags, pochoirs […] autres que celles situées à l'intérieur des locaux* » | 11 | Tags **intérieurs** couverts, tags de façade non. |
| Frais et pertes après vandalisme/émeute | « Les frais et pertes mentionnés au tableau des montants maximums de garantie […] suite à un événement garanti visé ci-dessus » | 11 | Ouvre droit aux frais annexes listés p. 12 (voir ci-dessous). |
| **Vol (pillage)** | « Le vol*, la tentative de vol des : • contenu professionnel* ; • autres matériels et marchandises* […] commis : • avec effraction des bâtiments* » | 17 | Le pillage relève de la garantie **Vol : contenu** (à vérifier souscrite aux DP). Effraction = « forcement, dégradation ou destruction volontaire […] des bâtiments* » (p. 6). |
| **Vol en vitrine sans entrer** | « Le vol, la tentative de vol […] des marchandises* en vitrines fixes de devanture, commis sans pénétration dans les bâtiments* pendant les heures de fermeture à condition qu'il y ait effraction, écartement ou démontage des glaces » | 17 | Vitrine brisée et marchandise arrachée de l'extérieur = **couvert** (si heures de fermeture). |
| Dommages concomitants au vol | « Les autres dommages matériels* aux : • contenu professionnel* […] concomitants à un vol* ou à une tentative de vol garanti » | 17 | Le stock abîmé (pas volé) pendant le pillage est aussi couvert. |
| Vol – détériorations immobilières | « Les dommages matériels* causés : • aux locaux professionnels* ; • aux agencements […] ; • au système électronique d'alarme ; à l'occasion d'un vol* » | 16 | Rideau, porte, alarme détruits : couverts. Serrures/badges : plafond 2 500 € (p. 17). |
| Protections exigées / sanction | « En cas de sinistre* facilité ou aggravé par l'inobservation d'une ou plusieurs des obligations […] l'indemnité sera réduite de moitié » | 18 | Les protections déclarées (niveaux 1 à 7, p. 19) doivent avoir été **utilisées**. Réduction de 50 %, **pas** de refus total. |
| Exclusions vol | Vol « exposés dans les vitrines transportables ou amovibles placées […] à l'extérieur », « situés en plein air » ; inoccupation > 90 jours | 18 | Étals extérieurs et vitrines mobiles exclus. |
| **Bris de glaces / enseignes** | « Le bris accidentel* des : • glaces, marquises et vitres incorporées aux bâtiments* […] • enseignes et plaques professionnelles » + « Les frais de transport, de dépose et de pose » | 20 | Vitrine, enseigne, panneaux publicitaires dans un rayon de 100 m, films/inscriptions sur vitre. Évaluation : « valeur de remplacement par des éléments de caractéristiques et de qualité similaires » (p. 51). |
| Frais après bris de glace | Gardiennage/clôture provisoire 14 000 € ; déplacement/replacement 10 000 € | 20 | Pose de contreplaqué, vigile après vitrine cassée : remboursables. |
| Marchandises (évaluation) | « L'indemnité correspond à leur valeur d'achat au dernier cours précédant le sinistre*, majorée, si nécessaire, des frais de transport et de manutention, des droits de douane et des taxes non récupérables » | 50 | Ne pas oublier **transport + manutention + taxes non récupérables** dans la réclamation stock. |
| Plafond « autres matériels et marchandises » | « 10 % maximum du montant du contenu professionnel* fixé aux Dispositions Particulières » | 12, 18 | Attention : sous-limite si les marchandises ne sont pas dans « contenu professionnel ». |
| **Valeur à neuf / rachat de vétusté** (matériel) | « Si le bien est remplacé dans les deux ans du sinistre* […] Indemnité complémentaire […] différence entre l'indemnité « immédiate » et les frais réellement engagés » ; au-delà de l'ancienneté de l'option : « dans la limite de la valeur d'usage* majorée de 25 % de la valeur à neuf* » | 48 | **Argent différé** : 1er chèque = valeur d'usage ; 2e chèque sur factures de remplacement **dans les 2 ans**. À tracer dans l'agent (rappel J+700). |
| Agencements / locaux | « L'indemnité totale maximum ne pourra excéder la valeur d'usage* majorée de 33 % de la valeur à neuf* » (travaux dans les 2 ans) | 47 | Agencements du locataire : « Frais réels » (p. 12). Complément versé « corps d'état par corps d'état ». |
| **Pertes d'exploitation** | « dès le premier jour en cas de sinistre* indemnisable au titre de la garantie « Incendie, événements assimilés et vandalisme » ; dans tous les autres cas […] supérieure à trois jours » | 28-29 | **Pas de franchise en jours** quand le dommage relève de vandalisme/émeutes (garantie incendie-vandalisme). Pour un sinistre « vol » seul : > 3 jours. |
| Base PE | « perte de marge brute*, de commissions, de revenus ou d'honoraires*, justifiée et subie pendant la période où le résultat de l'entreprise assurée est affecté » | 52 | Période d'indemnisation max = DP. Tolérance +20 % sur le plafond si CA a progressé (p. 29). |
| Acomptes PE | « des acomptes seront versés périodiquement pour financer les dépenses que l'Assuré* a dû ou doit engager pour couvrir ses charges fixes » | 52 | Trésorerie : **demander des acomptes** dès le rapport préliminaire. |
| Frais supplémentaires d'exploitation | Location de matériel, local de remplacement, « frais d'information de la clientèle par voie de presse ou par voie directe » | 7, 28 | Max 12 mois ; **accord exprès préalable** de l'assureur exigé (exclusion p. 28). |
| PE impossibilité d'accès | Interdiction des autorités / difficulté d'accès du fait « d'un incendie*, d'une explosion*, d'un événement climatique ou une catastrophe naturelle » | 28 | Fermeture préfectorale « préventive » sans incendie à proximité : **non visée**. |
| **Perte de valeur vénale du fonds** | « La perte de la valeur du fonds de commerce* […] consécutive à un sinistre* indemnisable relevant de […] « Incendie, événements assimilés et vandalisme » » ; partielle si « une diminution définitive de sa clientèle » | 29-30 | Commerce qui perd durablement sa clientèle après le saccage : indemnisable (si souscrite). Restitution 2/3 ou 1/3 si réinstallation < 1 km dans les 2 ans (p. 53). |
| **Frais de gardiennage et clôture provisoire** | Plafond « 14 000 euros » | 12, 17, 20 | Contreplaqué, vigile, barrières : à réclamer sur factures. |
| Frais de démolition / déblais | « Frais réels » ; taxe d'encombrement du domaine public : « Frais réels » | 12 | Benne, évacuation des débris, occupation de trottoir. |
| Déplacement / replacement du contenu | « 10 000 euros » (y compris garde-meubles et transport) | 7, 12 | |
| Relogement / perte d'usage | Relogement : « Montant de deux années de loyers » ; perte d'usage : « Valeur locative de deux années » | 12 | |
| **« Autres honoraires »** (architecte, décorateur, BET, SPS) | « Honoraires, réellement engagés et justifiés, d'architecte, bureau d'études, contrôle technique et d'ingénierie, décorateur et coordinateur […] SPS » — plafond « 10 % de l'indemnité due au titre des dommages matériels* aux locaux […] et/ou aux agencements » | 5, 12 | Refaire la boutique avec un décorateur/architecte : jusqu'à 10 % en plus. |
| **Pertes indirectes justifiées** | « Les frais restés à la charge de l'Assuré* suite à un sinistre indemnisable […] « Incendie, événements assimilés et vandalisme » » — plafond « 10 % de l'indemnité versée au titre des dommages matériels* » | 31 | **Enveloppe de 10 %** pour frais divers non couverts ailleurs (déplacements, temps passé, courriers…), sur justificatifs. Exclut les honoraires d'expert (déjà ailleurs). |
| **Honoraires de l'expert d'assuré** | Définition : « Honoraires de l'expert que l'Assuré* a choisi, le cas échéant » ; barème : « jusqu'à 350 000 euros 5% » | 7, 51 | **L'expert d'assuré est payé par Generali** jusqu'à 5 % de l'assiette (dommages + PE + valeur vénale + frais) — garanties incendie-vandalisme et DDE (p. 11, 15, 28, 30). Au-delà : 2 % / 1 % / 0,5 %. |
| Documents / archives | Frais de reconstitution des documents informatiques et papier | 20 | Factures/registres détruits : reconstitution couverte. |
| Frais financiers crédit-bail | « 10 % de l'indemnité due au titre des dommages matériels* sur le contenu professionnel* acquis en crédit - crédit-bail » | 12 | TPE/caisse en leasing détruits : différence créance / valeur à neuf. |
| Franchises | « si plusieurs franchises […] peuvent s'appliquer à un même sinistre*, seule la franchise la plus élevée sera déduite » | 54 | Une seule franchise par sinistre (par adresse). |
| Règle proportionnelle | « L'Assureur renonce à l'application de la règle proportionnelle de capitaux* » | 54 | Sous-assurance des capitaux : pas de réduction proportionnelle (plafonds restent). |
| **Délais** | Vol/vandalisme : déclarer « Dans les 2 jours ouvrés » + éléments sous 5 jours ouvrés ; autres : 5 jours ouvrés ; « en cas de vol* ou de vandalisme*, déposer plainte dans les 24 heures » | 45 | **Plainte 24 h** (plus strict que AXA). Déchéance seulement si le retard cause un préjudice à l'assureur (p. 45). |
| Réparations | « s'abstenir de procéder ou faire procéder à des réparations sans l'accord préalable et écrit de l'Assureur » | 45 | Sauf mesures conservatoires : obtenir un **accord écrit** avant travaux. |
| Expertise contradictoire | « L'Assureur désigne un expert […] l'Assuré* pouvant également, s'il le souhaite, se faire assister d'un expert » ; tiers expert ; désignation judiciaire à défaut sous 15 jours | 46 | Procédure complète ; « Chaque partie paie les frais et honoraires de son expert sous réserve de l'application de la garantie Honoraires d'expert* ». |
| Paiement | « Dans les 30 jours suivant : • un accord amiable ; • ou une décision judiciaire exécutoire » | 54 | |
| Exclusion émeutes | Exclusion générale limitée à « la participation volontaire de l'Assuré* à des émeutes » ; guerre civile/étrangère exclue | 44 | Pas d'exclusion des émeutes subies. |
| Assistance | Exclusion : « Les demandes consécutives à : • une guerre civile ou étrangère, des émeutes, des mouvements populaires » | 60 | **Piège** : l'assistance (vigile, dépannage) n'intervient pas pour les émeutes → passer par la garantie « frais de gardiennage » (14 000 €). |
| Protection juridique | Exclut les litiges « survenus à l'occasion de faits de guerre civile ou étrangère, d'émeute, de mouvements populaires » | 41 | Pas de PJ pour attaquer l'État/l'assureur sur la base des émeutes. |

---

## 2. AXA France — Atouts PME (Réf. 975637 I)

Fichier : `contrats/txt/AXA_AtoutsPME_CG.txt` — **page PDF = page imprimée + 2**.

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| **Émeutes (garantie)** | Événements garantis : « les manifestations, émeutes, mouvements populaires et actes de sabotage ; le vandalisme » | 6 (PDF 8) | Dans la garantie « Incendie, explosion, vandalisme » : locaux + contenu. |
| Ce que la garantie émeutes **ne** couvre pas | « au titre de l'ensemble des événements : − les vols avec ou sans effraction » ; pour émeutes : « graffiti et jets de peinture », « biens en cours de transport », « frais de reconstitution des archives informatiques » | 7 (PDF 9) | **Le pillage n'est pas couvert par la garantie émeutes** : il faut la garantie **Vol** (2.11). |
| Sanction prévention incendie | « l'indemnité qui vous est due sera réduite de 20 % » | 7 (PDF 9) | |
| **Vol** | Effraction, introduction clandestine, agression ; « les vols et les dommages matériels subis par le contenu […] (y compris en vitrine dans le cas de vol par effraction sans pénétration dans les locaux) » | 16-17 (PDF 18-19) | Pillage avec effraction et vitrine arrachée : couverts au titre du Vol. |
| Exclusion vol liée aux émeutes | Exclues de la garantie Vol « les détériorations et destructions : […] – consécutives à des manifestations, émeutes, mouvements populaires et actes de sabotage » | 19 (PDF 21) | Les **dégâts** de l'émeute passent par la garantie 2.3 (émeutes), pas par Vol. Le **vol** lui-même reste en garantie Vol. L'agent doit ventiler. |
| Protections | Moyens déclarés « obligatoirement être utilisés » ; alarme « enclenchée » | 19 (PDF 21) | |
| Inoccupation | Fermeture > 3 jours = inoccupation ; > 45 jours/an : pas de garantie ; espèces suspendues > 4 jours | 20 (PDF 22) | Un commerce fermé après les émeutes : attention aux nouveaux vols après 45 jours cumulés. |
| **Bris des glaces** | Devanture, portes vitrées, enseignes (« y compris celles en bois, métal ou aluminium »), panneaux dans un rayon de 100 m, + « peinture ou application d'inscriptions, de décoration, de gravures, de lettres adhésives ou de vitrophanie » | 20 (PDF 22) | La **vitrophanie / lettrage** est remboursée en plus du verre. |
| Bris de vitrine **sans vétusté** | « l'indemnité due au titre de la garantie bris de glaces est déterminée sur la base de la valeur de remplacement à neuf, sans application de vétusté » | 56 (PDF 58) | |
| Contenu / matériel | « Pour le matériel professionnel, pendant les 5 ans suivants la date de première mise en service, l'indemnité est déterminée sur la base de la valeur de remplacement à neuf sans application de vétusté » | 56 (PDF 58) | Matériel < 5 ans : valeur à neuf intégrale. |
| **Indemnité de dépréciation (rachat de vétusté)** | « L'indemnité de dépréciation ne peut excéder 25 % de la valeur de remplacement à neuf » ; versée « à condition que les travaux ou le remplacement interviennent dans un délai de 2 ans » | 55 (PDF 57) | **Argent différé** sur factures, à réclamer dans les 2 ans. |
| Marchandises | « les marchandises sont estimées à leur cours d'achat au jour de la survenance de l'événement » | 57 (PDF 59) | Prix d'achat, pas prix de vente. |
| **Pertes d'exploitation** | PE après dommage garanti « incendie, explosion, vandalisme » et « vol (y compris les détériorations) » ; base « perte de marge brute » | 27 (PDF 29) | Couvre le saccage **et** le vol. Période max = CP. |
| Franchise PE | Exclues les pertes « d'une interruption ou d'une réduction de vos activités pendant les 3 premiers jours ouvrés consécutifs » | 30 (PDF 32) | 3 jours ouvrés à la charge du commerçant. |
| PE impossibilité d'accès | Exclut « les conséquences d'émeutes, de mouvements populaires ou de manifestations, cortèges, défilés ou rassemblement sur la voie publique » | 29 (PDF 31) | Commerce **non touché** mais fermé par la police/les barrages : **pas couvert**. |
| Exclusion générale | « les frais et pertes, et les pertes d'exploitation […] consécutifs à […] des émeutes […] dès lors qu'ils ne résultent pas d'un dommage matériel garanti aux biens assurés » | 53 (PDF 55) | Corollaire : **dès qu'il y a un dommage matériel garanti, PE et frais sont dus**. |
| Contrainte administrative | PE prolongée par « mise sous scellés pour enquêtes » liée au dommage | 28 (PDF 30) | Scellés de police après pillage : la période PE s'allonge. |
| Frais supplémentaires additionnels | Actions « afin de maintenir sur le marché les produits et/ou les services » après incendie/vandalisme | 31 (PDF 33) | Communication, maintien de clientèle. |
| **Perte de valeur du fonds** | Dépréciation imputable à « incendie, explosion, vandalisme » ; « Dans le cas d'une augmentation de votre loyer permettant de rester sur les lieux, nous la prenons en charge pour le temps qui reste à courir sur votre ancien bail » | 33-34 (PDF 35-36) | Hausse de loyer post-sinistre remboursée. |
| **Frais et pertes** (cadre) | Frais « désignés aux Conditions particulières » après incendie/vandalisme, climat, effondrement, DDE ; « limités par un montant global indiqué aux Conditions particulières » | 35 (PDF 37) | Vérifier aux CP que les frais sont souscrits et le plafond global. |
| Déplacement / relogement | Garde-meubles, réinstallation, loyer provisoire « dans la limite d'une durée d'un an » | 35 (PDF 37) | |
| Honoraires décorateur / BET / SPS | « Frais et honoraires de décorateurs, bureaux d'études, contrôle technique et ingénierie » | 35 (PDF 37) | |
| Mise en conformité | Remise aux normes lors de la réparation | 36 (PDF 38) | |
| **Intérêts d'emprunt (TVA)** | Intérêts de l'emprunt « pour compenser la différence entre la l'indemnité de sinistre calculée « TVA exclue » et l'indemnité qui aurait été due […] « TVA comprise » » (max 5 ans) | 36 (PDF 38) | Poste quasi inconnu des commerçants. |
| **Pertes indirectes** | « pertes accessoires que vous pouvez supporter à la suite d'un dommage garanti […] justifiées par la production de mémoires, factures et bulletins de salaire » | 36 (PDF 38) | **Bulletins de salaire** acceptés : temps du personnel passé au nettoyage/inventaire. Pas de % fixé dans les CG (montant aux CP). |
| Démolition / déblais | Étendus « à la suite de catastrophe naturelle, de Vol et de Bris des glaces » | 37 (PDF 39) | Couverts même après un vol. |
| Archives | Reconstitution papier et informatique ; « après un délai de 2 ans » : exclu | 37 (PDF 39) | |
| **Clôture / gardiennage** | « rendus nécessaires à la suite de vol, tentative de vol ou Bris des glaces […] La durée d'indemnisation ne saurait excéder 15 jours » | 38 (PDF 40) | Vigile/contreplaqué : 15 jours max. |
| **Honoraires de l'expert d'assuré** | « Choisi par-vous à la suite d'un sinistre garanti » ; limites : barème art. 8.2, honoraires réellement payés, montant de l'indemnité | 38 (PDF 40) | Couvert **si la garantie « Honoraires d'expert » est souscrite** (p. 55). |
| Barème expert | « Jusqu'à 39 [x l'indice] : 4,50 % » ; « De 40 à 382 : 4,50 % sur 40 et 1,0 % sur le surplus » … | 55 (PDF 57) | Barème exprimé en **multiples de l'indice** : il faut la valeur de l'indice aux CP pour convertir en euros. |
| **Délais** | « vol et marchandises transportées : 2 jours ouvrés » ; « autres cas : 5 jours ouvrés » ; « déposer une plainte […] dans les 48 heures de la découverte du vol ou du vandalisme » | 54 (PDF 56) | Plainte **48 h**. Déchéance seulement si préjudice prouvé par l'assureur. |
| Expertise | « Vous disposez de la faculté de vous faire assister d'un expert de votre choix » ; tiers expert ; honoraires du 3e « par moitié » | 55 (PDF 57) | |
| Paiement | « dans les 30 jours qui suivent l'accord amiable » | 55 (PDF 57) | |
| Règle proportionnelle | « sans application de la règle proportionnelle de capitaux » | 55 (PDF 57) | |
| **Responsabilité de l'État** | « Dans le cas où en application de la législation […] sur la réparation des conséquences d'émeutes et de mouvements populaires, vous êtes susceptible d'être indemnisé […] vous vous engagez à signer une délégation à notre profit à concurrence des sommes que nous vous aurons versées » | 58 (PDF 60) | Confirme l'existence d'un **recours contre l'État** (régime légal des attroupements) : la part **non payée** par l'assureur (franchise, plafonds dépassés, biens non assurés) reste réclamable par le commerçant lui-même. |
| Exclusion guerre | Guerre civile : « il nous appartient de prouver que le sinistre provient de la guerre civile » | 52 (PDF 54) | Charge de la preuve sur AXA. |

---

## 3. Allianz IARD — Allianz Actif Pro (REG36387 – V06/22)

Fichier : `contrats/txt/Allianz_ActifPro_DG.txt` — **page PDF = page imprimée + 2**. Produit services/professions libérales (voir limites).

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| **Émeutes** | « dans les conditions et limites prévues pour chaque garantie, les dommages matériels directs causés aux biens assurés au cours d'émeutes ou mouvements populaires » | 15 (PDF 17) | Chaque dommage d'émeute est indemnisé **selon la garantie concernée** (incendie, vol/vandalisme, bris de glaces…). |
| Franchise émeutes | « Émeutes et mouvements populaires : Mêmes montants de garanties que ceux des garanties concernées. Franchise 10 % minimum 450 € maximum 2 300 € » | 67 (PDF 69) | Franchise plafonnée à 2 300 €. |
| **Vol / vandalisme** | « les vols, les tentatives de vol et actes de vandalisme commis à l'intérieur des bâtiments assurés entièrement clos et couverts avec effraction des bâtiments ou avec violences ou menaces » | 7 (PDF 9) | Pillage avec effraction couvert. |
| Vandalisme sans effraction | « les actes de vandalisme commis : • sur les parties extérieures de vos locaux, • à l'intérieur de vos locaux sans effraction » | 7 (PDF 9) | Vandalisme extérieur : franchise 10 % min 450 € max 2 300 € (p. 67). |
| Détériorations immobilières | Destructions « y compris à l'installation d'alarme ou de vidéosurveillance (caméras...) » | 7 (PDF 9) | |
| **Rangement / reclassement** | « les frais utilement exposés […] pour le reclassement d'archives éparpillées et/ou le rangement du contenu renversé sur place et ce, même si ces biens n'ont pas subi de dommages matériels » | 8 (PDF 10) | **Poste caché** : temps/prestataire de remise en ordre après le pillage. Plafond 2 300 € (franchise 150 €) p. 67. |
| Gardiennage / clôture (vol) | « frais de gardiennage et/ou de clôture provisoire des locaux, engagés à la suite d'un vol […] pour pallier la destruction de leurs moyens de protection » | 8 (PDF 10) | Plafond 2 300 € (p. 67). |
| Serrures | Remplacement serrure/badge si vol des clés + plainte | 8 (PDF 10) | Plafond 800 €. |
| Exclusions vol | « Le bris des glaces, vitres, vitrines […] pouvant faire l'objet de la garantie Bris des glaces » | 8 (PDF 10) | La vitrine passe par Bris des glaces. |
| Prévention | « la garantie ne serait pas acquise si ce manquement a facilité le sinistre » | 9 (PDF 11) | Sanction plus dure qu'AXA/Generali (perte totale, pas réduction). Exception : « pendant les seules heures de déjeuner, vous êtes dispensé d'utiliser les grilles ». |
| Inoccupation | Garantie vol suspendue après 30 jours d'inoccupation (60 avec « Complément Plus ») | 9 (PDF 11) | |
| **Bris des glaces** | Devanture, « la façade des locaux assurés (y compris les dispositifs de protection) endommagée concomitamment à un bris de vitrages », enseignes ; + « les dommages causés par le bris des glaces aux objets placés en devanture » | 9-10 (PDF 11-12) | Façade et rideau abîmés en même temps que la vitrine : couverts. « Bris suite à un acte de vandalisme : À concurrence des dommages » (p. 67). Objets en vitrine : 3 000 €. |
| Bris : frais | « les frais de gardiennage et/ou de clôture provisoire nécessaires à la protection de vos locaux à la suite d'un bris de glaces garanti » | 10 (PDF 12) | 2 300 €. |
| **Plafond marchandises** | « Marchandises : 3 000 € sauf mention contraire aux Dispositions particulières » | 66 (PDF 68) | **Piège majeur** : sans mention aux DP, le stock est plafonné à 3 000 €. |
| Mobilier / matériel | « Valeur de remplacement à neuf […] à condition que la vétusté du bien endommagé n'excède pas 25 % et que le remplacement du bien ait lieu dans un délai de 2 ans » | 59 (PDF 61) | |
| **Option forfait +10 %** | « choisir une indemnisation en valeur de remplacement vétusté déduite, majorée d'une indemnité forfaitaire complémentaire égale à 10 % du montant de l'indemnité » | 59 (PDF 61) | Alternative pour qui **ne veut pas racheter** : +10 % immédiat sans facture. Choix à faire « au moment du sinistre ». |
| Marchandises (évaluation) | « Prix d'achat majoré des taxes non récupérables et éventuellement des frais de transport et de manutention » | 59 (PDF 61) | |
| **Pertes pécuniaires et frais** (déblais, conformité, perte d'usage, « tous autres frais divers justifiés ») | Limités aux événements « Incendie et événements assimilés, Tempête, grêle, neige, Dégâts des eaux » | 16 (PDF 18) | **Piège** : ces frais ne jouent **pas** pour un sinistre vol/vandalisme pur. Ils jouent si l'émeute a provoqué un **incendie**. |
| Autres frais divers | Exemples : « honoraires de l'expert que vous avez désigné », honoraires décorateurs/BET/SPS, frais crédit-bail, intérêts d'emprunt TVA, taxe d'encombrement — plafond « 10 % de l'indemnité due au titre des locaux professionnels et du contenu avec une sous-limitation à 5 % pour les honoraires d'expert d'assuré » | 17, 68 (PDF 19, 70) | En cas d'incendie lors des émeutes : **+10 %** (15 % avec Complément Plus), dont 5 % pour l'expert. |
| **Pertes d'exploitation** | Après « Actes de vandalisme prévus au titre de la garantie Vol/Vandalisme » (et incendie…) ; période « de 12 mois mais peut être portée à 24 mois » | 19 (PDF 21) | PE couverte après vandalisme. **Le vol seul n'est pas listé** (seul le vandalisme). Pas de franchise en jours indiquée aux DG pour ce cas (3 jours ouvrés seulement pour « autres dommages matériels » et accès, p. 68) : vérifier les DP. |
| Honoraires expert PE | « le remboursement des honoraires de l'expert ayant procédé aux opérations d'expertise pour votre compte » ; « 5 % de l'indemnité » | 19, 68 (PDF 21, 70) | **Expert d'assuré payé à 5 % sur la PE** aussi. |
| PE impossibilité d'accès | Dommages dans un rayon de 300 m, 6 mois max, 30 % du capital, franchise 3 jours ouvrés ; exclut attentat/terrorisme | 19, 68 | Émeutes non exclues ici (seul attentat/terrorisme), mais il faut un événement « Incendie […] ou de tout autre événement accidentel » ayant causé des dommages matériels à proximité. |
| **Avance de trésorerie** | « une avance de trésorerie pouvant aller jusqu'à 50 % du montant des dommages matériels » | 61 (PDF 63) | Demander l'avance tout de suite. |
| Perte de valeur vénale | Seulement après Incendie, Tempête, DDE ; honoraires expert 5 % | 20-21 (PDF 22-23) | **Non mobilisable** pour vol/vandalisme sauf incendie. |
| **Délais** | « en cas de vol, de vandalisme […] déposer plainte dans les 24 heures » ; déclarer « dans les 2 jours ouvrés en cas de vol ou de vandalisme » ; état estimatif « dans les 30 jours » | 56 (PDF 58) | Plainte **24 h**. |
| Expertise | 2 experts (un par partie), tiers expert, « honoraires du 3e expert […] pour moitié » | 57 (PDF 59) | |
| Règle proportionnelle | « non-application de l'article L121-5 du Code des assurances » | 57 (PDF 59) | |
| Assistance gardiennage | Fermetures provisoires + « agent de sécurité […] pendant 72 heures réparties sur 7 jours maximum » | 36 (PDF 38) | En plus de la garantie frais (sous réserve de l'exclusion « grèves, émeutes » des cas de force majeure de l'assistance, PDF 42). |
| Paiement | « dans les 30 jours suivant l'accord amiable » | 61 (PDF 63) | |

---

## 4. Sogessur (Société Générale) — La Multirisque des Pros, Commerçants Artisans (2016)

Fichier : `contrats/txt/SG_Sogessur_MultirisqueDesPros_CommercantsArtisans_CG.txt` — pages imprimées = pages PDF.

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| **Émeutes** | « Les dommages matériels causés aux biens assurés par des actes de sabotage et d'émeutes ou de mouvements populaires, lorsque ces dommages sont de même nature que ceux couverts au titre des garanties Incendie […] Bris de glaces et Vol » | 18 | Couverture « par ricochet » : seulement les dommages de même nature qu'une garantie souscrite. |
| **Vol pendant émeutes : EXCLU** | « Les vols ou tentatives de vol, survenus lors d'émeutes ou de mouvements populaires » | 19 | **Clause clé pour la démo** : chez Sogessur, le pillage lors des émeutes n'est **pas** couvert au titre du Vol. Contradiction apparente avec p. 18 → à contester avec un expert (interprétation en faveur de l'assuré, art. L.133-2 C. consommation / clause ambiguë), mais ne rien promettre. |
| Vitrines | « Les vols de marchandises exposées dans les vitrines » exclus | 19 | Vitrines arrachées : non couvertes au titre du Vol. Le **verre** reste couvert en Bris de glaces. |
| Autres exclusions vol | Vandalisme « commis à l'extérieur des bâtiments » ; vols lors d'« évacuation des locaux ordonnés par les autorités […] troubles civils » | 19 | |
| Protections | « réduction de moitié de l'indemnisation […] si leur absence a facilité le vol » | 19 | |
| **Bris de glaces** | « des meubles vitrés et devantures ainsi que les dommages aux marchandises qui en sont consécutifs » | 16 | Plafond 15 000 € dont 3 000 € marchandises (p. 41). |
| Plafonds vol/vandalisme | « Vol : 25 000 euros » ; « Vandalisme : 30% de la valeur du contenu » ; espèces en tiroir 1 500 € | 41 | |
| **Surcroît d'activité** | Stock « automatiquement majoré de 50% » (fleuristes, vêtements/chaussures 10 jours avant soldes, alimentaire avant fêtes) | 20 | Si option souscrite et sinistre dans la période (octobre : en général hors période). |
| Marchandises | « prix d'achat apprécié au dernier cours précédant le sinistre, frais de transport et de manutention compris » | 38 | |
| Rachat de vétusté | Bâtiment : « la vétusté que nous prenons en charge ne peut excéder 25% » (reconstruction 2 ans) ; matériel non électrique : « Nous vous réglerons la vétusté sur présentation des justificatifs si le remplacement a lieu dans les deux ans » | 37-38 | Pas pour les marchandises (p. 38). Matériel électrique : grille forfaitaire 95 % → 30 % (p. 38). |
| **Pertes d'exploitation** | Après « Incendie […] Dégât des eaux et gel, Attentats et actes de terrorisme, Catastrophes naturelles, Bris de machines » ; 12 mois | 23 | **Vol et vandalisme absents de la liste.** La clause émeutes figurant dans la rubrique « Attentats » (p. 18), la PE après émeutes est **discutable** : point à faire trancher par l'expert. |
| Franchise PE | « trois jours ouvrés, calculée en moyenne sur votre dernier exercice » | 37 | |
| Plafond PE | « dans la limite d'un an de chiffre d'affaires HT » | 42 | |
| Valeur vénale du fonds | Après incendie, tempête, DDE, attentats, CatNat ; plafond 1 000 000 € | 23, 42 | Vandalisme/vol non listés. |
| **Honoraires de l'expert d'assuré** | « Nous prenons en charge les honoraires de l'expert que vous avez mandaté avec notre accord » ; barème « Jusqu'à 143 000 euros 4,50% » | 21 | **Condition : accord de l'assureur.** Sinon 1 % au-delà de 143 k€, etc. |
| Frais annexes (enveloppe) | Honoraires expert, déplacement/relogement, démolition/déblais, DO, bureaux d'étude, conformité, perte financière sur aménagements : « pris en charge dans la limite de 15% de l'indemnité versée au titre des bâtiments et du contenu » | 41 | Enveloppe commune de 15 %. |
| **Pertes indirectes** | « A concurrence de 10% de l'indemnité versée au titre des bâtiments et du contenu garantis » (sur justificatifs) | 21, 41 | +10 % sur justificatifs. |
| Perte financière aménagements | Aménagements du locataire « devenus la propriété du bailleur » si résiliation ou refus du bailleur de les refaire | 21 | |
| Perte de loyers / usage | 2 ans max | 20-21, 41 | |
| Assistance | Gardiennage « 72 heures consécutives maximum », sécurisation « 1 500 euros TTC », nettoyage « 750 euros TTC » | 51 | Mais l'assistance exclut les cas de force majeure dont « mouvements populaires, émeutes, grèves » (p. 56). |
| **Délais** | Vol/vandalisme : « dans les 2 jours ouvrés » + plainte et certificat ; autres : 5 jours ouvrés | 36 | La page « Que faire » indique « Déposez une plainte dans les 24 heures » (p. 5). |
| Paiement | « dans les 5 jours suivant l'accord entre les parties » | 40 | Le plus rapide du batch. |
| Exclusions générales | « Les dommages résultant de rébellion, d'insurrection, de mutineries militaires ou de révolution » ; « graffitis, tags » ; « pertes d'éléments incorporels du fonds de commerce » | 35 | Si l'assureur qualifie les événements d'« insurrection » : exclusion. À surveiller. |
| Limite globale | « ne pourra en aucun cas excéder le montant non indexé de 7 500 000 euros » | 42 | |

---

## 5. AXA — Mon Pack Entrepreneur (Réf. 981030 B, mai 2024) — résumé

| Thème | Ce que dit le contrat | Page | Pour le commerçant |
|---|---|---|---|
| Émeutes | « les manifestations, émeutes, mouvements populaires et actes de sabotage ; le vandalisme » (garantie Incendie, explosion et vandalisme) | 36 | Couvert pour aménagements, matériel, marchandises. Exclut « les vols avec ou sans effraction » au titre de ces événements (p. 36). |
| Vol | Contenu « y compris le contenu en vitrine dans le cas d'un vol par effraction sans pénétration » + « frais annexes […] de clôture et de gardiennage » | 30 | |
| **Expert d'assuré : NON pris en charge** | « L'assuré dispose de la faculté de se faire assister d'un expert de son choix, les honoraires de ce dernier restant à sa charge » | 65 | Contraste avec Atouts PME / Generali. Pour un micro-entrepreneur, l'expert d'assuré doit se rémunérer au résultat. |
| Dépréciation | « L'indemnité de dépréciation ne peut excéder 25 % de la valeur de remplacement à neuf » (2 ans) ; équipements informatiques < 5 ans « Sans application de vétusté » | 66 | |
| Pertes d'exploitation | **absent** (aucune occurrence « perte d'exploitation » / « marge brute » dans le document) | — | Micro-entrepreneur : pas de PE dans ce pack. |
| Délais | Vol : 2 jours ouvrés ; plainte « dans les 48 heures de la découverte du vol » | 63 | |
| Exclusion | Frais et pertes consécutifs à des émeutes « dès lors qu'ils ne résultent pas d'un dommage matériel garanti » | 59 | |

## 6. Groupama — Multirisque des professionnels, Dispositions Générales communes (AMP) — résumé

| Thème | Ce que dit le contrat | Page | Pour le commerçant |
|---|---|---|---|
| Garanties émeutes / vol / frais / PE | **absent** de ce document (renvoi aux « fascicules d'assurance correspondants ») | 16 (PDF 18) | Impossible de conclure sur Groupama sans les fascicules. |
| Délais vol / vandalisme | « aviser immédiatement les autorités locales de police et déposer une plainte » ; déclaration « 2 jours ouvrés » ; autres sinistres 5 jours ouvrés ; état estimatif sous 20 jours | 15 (PDF 17), 14 (PDF 16) | Mêmes délais que le marché. |
| Jours ouvrés | « les jours effectivement travaillés dans l'entreprise » | PDF 6 | Définition favorable : un commerce fermé le dimanche/lundi gagne des jours. |
| Expert d'assuré | « Vous avez la possibilité de vous faire assister par un expert » ; « Chacun de nous paye les frais et honoraires de son expert » | 16 (PDF 18) | Pas de prise en charge dans le tronc commun (peut exister dans un fascicule : non vérifié). |

---

## Tableau transversal — « Postes souvent oubliés et récupérables »

Légende : G = Generali 100% Pro ; AX = AXA Atouts PME ; AXm = AXA Mon Pack Entrepreneur ; AZ = Allianz Actif Pro ; SG = Sogessur ; GR = Groupama (DG communes). « absent » = clause non trouvée dans le document analysé.

| Poste récupérable | G | AX | AXm | AZ | SG | Plafond typique / remarque |
|---|---|---|---|---|---|---|
| **Honoraires de l'expert choisi par l'assuré** | Oui, barème 5 % jusqu'à 350 k€ (p. 51) | Oui si option souscrite, barème en indice, 4,5 % sur la 1re tranche (p. 38, 55) | **Non** (« restant à sa charge », p. 65) | Oui : 5 % de l'indemnité (PE, valeur vénale, bris matériel, autres frais incendie) (p. 68) | Oui avec accord, 4,5 % jusqu'à 143 k€, dans l'enveloppe 15 % (p. 21, 41) | **~4,5 à 5 % de l'indemnité** ; GR : non dans le tronc commun |
| **Pertes indirectes / frais divers justifiés** | 10 % des dommages matériels (p. 31) | Oui, sur justificatifs y compris bulletins de salaire, montant aux CP (p. 36) | absent | 10 % (15 % Complément Plus), seulement incendie/tempête/DDE (p. 17, 68) | 10 % (p. 41) | **~10 % de l'indemnité** |
| Honoraires architecte / décorateur / BET / SPS | 10 % de l'indemnité locaux/agencements (p. 12) | Oui (p. 35) | absent | Inclus dans les « autres frais » (p. 17) | Dans l'enveloppe 15 % (p. 41) | 10 à 15 % |
| **Frais de gardiennage / clôture provisoire** | 14 000 € (p. 12, 17, 20) | Oui, 15 jours max (p. 38) | Oui (p. 30) | 2 300 € (vol, bris) + assistance 72 h (p. 67, 36) | Assistance 72 h + sécurisation 1 500 € (p. 51), sous réserve de l'exclusion émeutes de l'assistance | 2 300 à 14 000 € |
| Démolition / déblais / évacuation | Frais réels (p. 12, 17) | Oui, y compris après vol et bris (p. 37) | absent | Frais engagés (incendie/tempête/DDE) (p. 67) | Enveloppe 15 % | Frais réels |
| Taxe d'encombrement de la voie publique (benne) | Frais réels (p. 12) | absent | absent | Oui (p. 17) | absent | |
| Remise en ordre / rangement après pillage | absent | absent | absent | **2 300 €** (franchise 150 €) (p. 8, 67) | absent | Spécifique Allianz |
| Remplacement des serrures / badges | 2 500 € (p. 17) | Oui (p. 17) | Oui (p. 30) | 800 € (p. 66) | absent | |
| Inscriptions / vitrophanie / films sur vitrine | Oui (p. 20) | Oui (p. 20) | n.v. | Oui (p. 10) | absent | Avec le bris de glace |
| Marchandises abîmées par la vitrine brisée | Oui (p. 20) | Oui (« détériorations consécutives ») (p. 20) | n.v. | 3 000 € (p. 67) | 3 000 € (p. 41) | |
| Vitrine remplacée **sans vétusté** | Valeur de remplacement (p. 51) | **Oui, explicite** (p. 56) | n.v. | Valeur de remplacement (p. 60) | absent | |
| **Rachat de vétusté différé (2 ans)** | VU + 25 % / 33 % (p. 47-48) | Dépréciation ≤ 25 % VRN (p. 55) | ≤ 25 % (p. 66) | VàN si vétusté ≤ 25 %, ou forfait +10 % (p. 59) | ≤ 25 % (p. 37-38) | **Second chèque à réclamer sur factures sous 2 ans** |
| Matériel récent sans vétusté | Selon option VàN aux DP (p. 48) | Matériel < 5 ans (p. 56) | Informatique < 5 ans (p. 66) | Informatique 3-5 ans (p. 59) | Informatique 3-5 ans selon formule (p. 38) | |
| Transport/manutention/taxes non récupérables sur stock | Oui (p. 50) | absent (« cours d'achat ») | n.v. | Oui (p. 59) | Transport + manutention (p. 38) | |
| **PE sans franchise en jours** | **Oui si incendie-vandalisme** (p. 28) | Non : 3 jours ouvrés (p. 30) | Pas de PE | Non indiquée aux DG pour vandalisme (à vérifier aux DP) | Non : 3 jours ouvrés (p. 37) | |
| PE après **vol** | Oui (> 3 jours) (p. 28) | Oui (p. 27) | Pas de PE | **Non** (seul le vandalisme est listé) (p. 19) | **Non** (p. 23) | |
| Acomptes / avance de trésorerie | Acomptes PE (p. 52) | absent | absent | **Avance jusqu'à 50 %** des dommages (p. 61) | absent | |
| Frais supplémentaires d'exploitation (local provisoire, location, communication clients) | Oui, 12 mois, accord préalable (p. 7, 28) | Oui + « frais supplémentaires additionnels » (p. 31) | absent | Oui (p. 19) | Oui, accord de l'expert (p. 23) | |
| Allongement PE par scellés / contrainte administrative | absent | **Oui** (p. 28) | absent | absent | absent | |
| Perte de valeur vénale du fonds après vandalisme | Oui (p. 29) | Oui + hausse de loyer remboursée (p. 33-34) | absent | Non (incendie/tempête/DDE seulement) | Non (vandalisme non listé) | |
| Intérêts d'emprunt (indemnité HT vs TTC) | absent | **Oui** (p. 36) | absent | Oui (p. 17) | absent | |
| Frais financiers de crédit-bail | 10 % (p. 12) | Désintéressement du bailleur (p. 57) | absent | Oui (p. 17) | absent | |
| Reconstitution archives / documents | Oui (p. 20) | Oui, 2 ans (p. 37) | n.v. | 10 000 € (p. 66), 2 ans | Oui (p. 39) | |
| Perte d'usage / relogement / loyers | 2 ans (p. 12) | 1 an (p. 35, 38) | n.v. | 2 ans de valeur locative (p. 67) | 2 ans (p. 41) | |
| Mise en conformité lors de la réparation | 300 000 € (p. 12) | Oui (p. 36) | n.v. | 230 €/m² (p. 67) | Enveloppe 15 % | |
| Recharge d'extincteurs | Oui (p. 11) | Oui, sans franchise (p. 36) | n.v. | Oui (p. 17) | absent | |
| Non-application de la règle proportionnelle | Oui (p. 54) | Oui (p. 55) | n.v. | Oui (p. 57) | absent | |
| Recours contre l'État (régime des attroupements) | absent | **Mentionné** (délégation, p. 58) | absent | absent | absent | Le reste à charge reste réclamable à l'État |

n.v. = non vérifié dans ce résumé (le document peut le contenir).

### Pièges à faire détecter par l'agent (preuves dans les CG)

1. **Sogessur exclut le vol pendant les émeutes** (p. 19) et le vol des marchandises en vitrine (p. 19).
2. **Allianz Actif Pro : stock plafonné à 3 000 €** si les DP ne disent rien (p. 66) ; frais annexes réservés à incendie, tempête et DDE (p. 16).
3. **AXA : la garantie « émeutes » exclut le vol** (p. 7). Le pillage se réclame au titre du Vol, et les dégâts au titre de l'Incendie-vandalisme. Il faut ventiler.
4. **AXA : pas de PE pour simple impossibilité d'accès due aux émeutes** (p. 29). Le commerce doit avoir subi un dommage matériel.
5. **Délais de plainte différents** : 24 h chez Generali (p. 45) et Allianz (p. 56), 48 h chez AXA (p. 54). Le délai de déclaration est de 2 jours ouvrés partout. La déchéance n'est opposable que si l'assureur prouve un préjudice.
6. **L'assistance (vigile, dépannage) exclut les émeutes** chez Generali (p. 60) et, comme cas de force majeure, chez Sogessur (p. 56) et Allianz (PDF 42). Les frais de gardiennage doivent alors passer par la garantie « frais et pertes » de la police dommages.
7. **Réparations sans accord écrit** : clause « s'abstenir de procéder […] à des réparations sans l'accord préalable » (Generali p. 45, Allianz p. 56). Seules les mesures conservatoires peuvent être faites sans accord.
8. **Valeur d'usage seulement si pas de remplacement sous 2 ans** : le rachat de vétusté est perdu si le commerçant ne remplace pas ou ne garde pas les factures.
