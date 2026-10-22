# 08b — Contrats Batch B : MAAF, MMA, Hiscox, Pacifica (Crédit Agricole)

> Objectif : pour un commerçant vandalisé/pillé lors des émeutes du 17-18 octobre 2026, identifier dans de **vrais** contrats multirisque pro tout ce qui peut être légitimement réclamé.
> Règles de lecture :
> - **Page** = numéro de page **du fichier PDF** (pour MAAF, le numéro imprimé en bas de page = page PDF − 1 ; pour MMA et Hiscox, page PDF = page imprimée).
> - Les citations sont **verbatim** (raccourcies avec « […] » si besoin). Rien n'est inventé : si une clause n'existe pas dans le document, c'est écrit **« absent »**.
> - Les montants « CP » renvoient aux **Conditions particulières** du client (plafonds/franchises propres à chaque contrat) : l'agent devra les lire en plus des CG.
> - Fichiers extraits (texte) : `contrats/txt/` — PDF d'origine : `contrats/pdf/`.

## Documents collectés

| Assureur | Document | Réf./version | Pages | Source | Fichier local |
|---|---|---|---|---|---|
| **MAAF** (Covéa) | Conditions générales Multirisque Professionnelle | Réf. 11031 - 01/26 | 90 | https://www.maaf.fr/fr/files/live/sites/maaf/files/DOCUMENTS/Professionnels/CG/MAAF_Conditions_generales_Multirisque_pro_11031.pdf (site officiel) | `contrats/pdf/MAAF_MRP_CG_11031-0126.pdf` / `contrats/txt/MAAF_MRP_CG_11031-0126.txt` |
| **MMA** (Covéa) | Contrat MMA PRO-PME — Conditions Générales | CG n° 352 p, édition avril 2021 | 104 | https://philtr.fr/static/pdf/insurance/mrp/mma_mrp.pdf (copie hébergée par un comparateur ; pas trouvée sur mma.fr) | `contrats/pdf/MMA_ProPME_CG_352p_2021-04.pdf` / `contrats/txt/MMA_ProPME_CG_352p_2021-04.txt` |
| **Hiscox** (offre courtage) | Conventions Spéciales Multirisques Dommages aux Biens Professionnels | n° MRP0623 | 51 | https://www.hiscox.fr/courtage/sites/courtage/files/documents/MRP0623%20-%20Conventions%20Speciales%20Multirisques%20Dommages%20aux%20Biens%20Professionnels%20.pdf | `contrats/pdf/HISCOX_MRP_CS_DommagesBiens_MRP0623.pdf` / `.txt` |
| Hiscox (complément) | PRO by Hiscox — Conditions Générales (version antérieure) | n° MRP0918 (19215 11/18) | 46 | https://www.hiscox.fr/courtage/courtage/sites/courtage/files/documents/CG%20Pro%20by%20Hiscox.pdf | `contrats/pdf/HISCOX_MRP_CG_ProByHiscox.pdf` / `.txt` |
| Hiscox (complément) | IPID PRO by Hiscox | MRP0820 | 2 | https://www.hiscox.fr/courtage/sites/courtage/files/documents/IPID_Pro%20by%20Hiscox%20-%20MRP0820.pdf | `contrats/pdf/HISCOX_MRP_IPID_MRP0820.pdf` / `.txt` |
| **Pacifica** (Crédit Agricole, bancassureur) | Document d'information (IPID) Assurance Multirisque Professionnelle avec ou sans local | 7197A.36 (2020.12) | 3 | https://www.credit-agricole.fr/content/dam/assetsca/master/public/commun/documents/7197A.36_IPA_doc%20info_M9_PRO-122020-BD.pdf | `contrats/pdf/CA_Pacifica_MRP_IPID_7197A36-122020.pdf` / `.txt` |

**Non trouvés (à signaler honnêtement)** : CG multirisque pro **MACIF** et **MAIF** (non publiées en PDF accessible ; les comparateurs indiquent que MACIF ne les diffuse pas) ; CG complètes **Pacifica** et **ACM/Crédit Mutuel** (seuls IPID/mémos/flyers trouvés). Le PDF MMA officiel n'est pas sur mma.fr : la version utilisée (avril 2021) est une copie tierce, potentiellement remplacée par une édition plus récente.

> Attention Hiscox : l'IPID précise que PRO by Hiscox vise les « entreprises prestataires de conseils et services » (bureaux). C'est un bon exemple de contrat « courtier » mais moins représentatif d'une boutique.

---

## 1. MAAF — Multirisque Professionnelle, CG Réf. 11031 - 01/26

- Source : maaf.fr (officiel). Local : `contrats/pdf/MAAF_MRP_CG_11031-0126.pdf`.
- Structure : garanties de base « Vos locaux et leur contenu » + options (Vol/vandalisme, Bris de matériel) + « Tranquillité financière » (pertes d'exploitation, perte de valeur vénale du fonds) en option.

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| Émeutes — garantie | « nous garantissons les dommages matériels* directs causés aux biens immobiliers et mobiliers assurés résultant d'émeutes* ou mouvements populaires*. » | 15 | Garantie émeutes **incluse** dans « Vos locaux et leur contenu ». |
| Émeutes — périmètre | « Ces émeutes* et mouvements populaires* sont couverts s'ils sont à l'origine des dommages garantis au titre de : l'incendie […] le bris des vitres, vitrines et enseignes, les garanties optionnelles : - la garantie vol, tentative de vol et vandalisme […] » | 15 | Le pillage/la casse liés à l'émeute ne sont indemnisés que via les garanties **souscrites** (incendie, bris de vitres, vol-vandalisme si option prise). Vérifier les CP : sans option Vol/vandalisme, le pillage n'est pas couvert. |
| Émeutes — espèces | Tableau : espèces, titres et valeurs « À concurrence de 10 % de la somme assurée au titre du contenu […] avec un maximum de 16 000 € » | 15 | La caisse volée lors d'une émeute est réclamable dans cette limite. |
| Définition émeutes | « Soulèvements populaires violents contre l'autorité publique pour obtenir la réalisation de revendication économique, sociale, ou politique et troublant la sécurité et l'ordre public. » | 82 | Qualification à documenter (articles de presse, arrêtés préfectoraux). |
| Définition mouvements populaires | « Actions violentes de la foule troublant la sécurité et l'ordre public. » | 83 | Définition large, facile à remplir pour le 17-18 octobre. |
| Vol — conditions | Vol garanti « Suite à introduction dans les bâtiments* assurés : • avec effraction • sans effraction - Suite à agression » | 19 | L'effraction est la porte d'entrée habituelle d'un pillage (rideau forcé, vitrine cassée). |
| Vol — vitrines | « Vol de vos marchandises exposées dans les vitrines - Suite à un bris de vitres sans introduction dans les bâtiments* assurés » | 19 | Vol « à travers la vitrine » couvert même sans entrer dans la boutique. |
| Vol — définition effraction | « Avec effraction : tout forcement, dégradation ou destruction de tout dispositif de fermeture* ou de tout élément de clos ou de couvert » | 19 | Photographier les traces de forcement (rideau, serrure, vitre). |
| Vol — protections exigées | « En cas de non-respect de ces obligations, la garantie ne sera pas acquise. » (fermeture à clé, alarme activée, pas de cadenas classe 1-3) | 21 | Point d'attaque probable de l'assureur : prouver que les protections étaient en place et actives. |
| Vandalisme | « Nous garantissons les conséquences des détériorations, dégradations ou destructions volontaires de vos biens, commises par autrui » | 22 | Couvre bâtiments, agencements, mobilier, marchandises, biens confiés (option Vol/vandalisme). |
| Tags / graffitis | « Les dommages causés par les inscriptions telles que graffitis et tags sur les murs et vitrines de vos bâtiments* assurés » | 23 | **Nettoyage de tags réclamable** (souvent oublié). |
| Bris de glace | Biens assurés : « la devanture, la clôture […] portes, vitrines […] les enseignes dès lors qu'elles sont fixées aux bâtiments* assurés » | 14 | Vitrine + enseigne cassées couvertes. |
| Bris de glace — extensions | « le bris des produits non verriers constituant la façade […] (y compris le bris des dispositifs de protection tels que les rideaux métalliques et les encadrements) » | 14 | **Rideau métallique** endommagé en même temps que la vitrine : réclamable. |
| Bris — marchandises exposées | « Vos marchandises exposées et détériorées par le bris » : « À concurrence de 20 % de la somme assurée au titre du contenu » | 14 | Marchandises abîmées par les éclats de vitrine. |
| Bris — auvents, stores | « Par extension, sont garantis les auvents, bannes, stores et corbeilles dès lors qu'ils sont fixés aux bâtiments* assurés. » | 14 | Store/banne arraché : réclamable. |
| Clôture provisoire / gardiennage | « les frais de clôture et de gardiennage engagés avec notre accord » — plafond « 6 600 € » | 14, 19, 23 | Planches, contreplaqué, vigile après le pillage : jusqu'à 6 600 € (bris, vol, vandalisme). **Obtenir l'accord** de l'assureur. |
| Obligation de clôture | « vous vous engagez à faire poser immédiatement une clôture provisoire dans le cas où celle-ci s'avérerait nécessaire. » | 14, 18 | Obligation de l'assuré : la respecter et la facturer. |
| Assistance gardiennage | « le gardiennage des locaux pendant 72 heures : afin de préserver vos biens contre le vol à la suite d'un acte de vandalisme » | 58 | Service gratuit en plus des 6 600 €. Délais d'intervention allongés en cas d'émeutes (p. 58). |
| Serrures | « Le remplacement à l'identique des serrures » — « 3 000 € » | 19 | Changement de serrures réclamable. |
| Frais de récupération | « Les frais exposés pour la récupération des objets assurés volés » — « Sans limitation de somme » | 19 | Frais pour récupérer de la marchandise retrouvée. |
| Mise en conformité | « 500 € par m² de superficie développée de vos locaux professionnels » | 25 | Travaux imposés par les normes lors de la remise en état. |
| Déplacement / garde-meuble | « Frais exposés avec un maximum de 6 400 € pour frais de garde-meuble » | 25 | Stockage du stock rescapé pendant les travaux. |
| Mesures de sauvetage | « À concurrence de 5 % de l'indemnité versée au titre des dommages aux biens assurés » | 25 | Frais pour limiter le sinistre. |
| Relogement | « Frais exposés pendant 2 ans » (loyer d'une réinstallation temporaire) | 25 | Local provisoire pour continuer à vendre. |
| Démolition / déblais | « les frais de démolition et de déblais des biens assurés, ainsi que les frais exposés à la suite des mesures conservatoires* imposées par décision administrative » | 24 | Évacuation des gravats et des débris. Plafond non chiffré dans le tableau des garanties complémentaires. |
| Honoraires architecte / décorateur | « À concurrence de 5 % de l'indemnité versée au titre des biens immobiliers » | 25 | Honoraires de décorateur/architecte pour refaire la boutique. |
| **Pertes indirectes** | « À concurrence de 10 % de l'indemnité versée au titre des dommages aux biens assurés » — « Sans franchise » | 25 | **+10 %** sur justificatifs (courriers, démarches). |
| Limite des pertes indirectes | « ne peut en aucun cas servir à prendre en charge des honoraires […] d'experts d'assuré, ni à compenser […] une franchise*, d'une vétusté* » | 25 | Les 10 % ne peuvent **pas** financer l'expert d'assuré. |
| Honoraires expert d'assuré | « Chacun de nous prendra en charge les frais et honoraires de son expert et, le cas échéant, la moitié de ceux du troisième. » | 78 | **Absent** comme garantie : l'expert d'assuré reste à la charge du commerçant. |
| Cotisation dommages-ouvrage | « À concurrence de 5 % de l'indemnité versée au titre des bâtiments* sinistrés » | 25 | Si gros travaux. |
| Matériel en leasing | « l'indemnité de résiliation incluant les loyers restant dus que nous versons à la société propriétaire du matériel » | 23 | Option bris de matériel : solde de leasing d'un TPE/ordinateur détruit. |
| Marchandises — évaluation | « évaluées au prix d'achat calculé au cours du jour* à la date du sinistre […] et majoré des frais accessoires de transport. » | 79 | Réclamer le **prix d'achat du jour** + transport (pas le prix de vente). |
| Mobilier/matériel — rachat de vétusté | « la vétusté* déduite […] vous sera remboursée sur présentation des factures à hauteur de 33 % maximum, dès lors que le remplacement s'effectue dans les deux ans » | 79 | Racheter = récupérer jusqu'à 33 % de vétusté. |
| Informatique < 2 ans | « Le matériel informatique de moins de 2 ans est évalué en valeur à neuf*, sans aucune déduction de vétusté*. » | 79 | Caisse, PC, tablette récents : **valeur à neuf**. |
| Bâtiments — vétusté | « remboursée sur présentation des factures à hauteur de 33% maximum » (reconstruction dans les 2 ans, même usage) | 78 | Pour propriétaire des murs / aménagements. |
| Règle proportionnelle | « La règle proportionnelle de capitaux […] n'est pas applicable au présent contrat. » | 78 | Pas de réduction pour sous-assurance des capitaux. |
| Pertes d'exploitation — base | « la perte de votre marge brute sur chiffre d'affaires ou sur recettes, honoraires, commissions. » + frais supplémentaires d'exploitation | 41 | Option « Tranquillité financière » à vérifier dans les CP. |
| PE — émeutes | Événements déclencheurs « (y compris s'ils surviennent à l'occasion d'émeutes* ou mouvements populaires*) » ; « si l'option vol, tentative de vol et vandalisme est souscrite » | 41 | La fermeture après pillage est indemnisable si l'option PE (et l'option Vol/vandalisme) sont souscrites. |
| PE — après vol | PE suite à vol : « 2 jours ouvrés » de franchise, plafond « indemnité journalière forfaitaire […] multipliée par 60 jours ouvrés » | 43 | Après pillage : **forfait journalier**, au plus 60 jours ouvrés. |
| PE — au réel / forfait | Au réel : période de 12, 18 ou 24 mois ; forfait : 100 % du forfait journalier si arrêt total, 50 % si partiel | 42 | Distinguer fermeture totale et réouverture partielle. |
| PE — exclusion | Exclues les PE résultant « de l'impossibilité d'accès à votre outil de production résultant d'émeutes et mouvements populaires* » | 43 | Une boutique **non** touchée mais fermée par les émeutes alentour : **pas couverte**. |
| PE — terrorisme | Franchise légale « trois jours ouvrés, avec un minimum de 1 140 euros » | 57 | Seulement en cas de qualification terroriste. |
| Perte de valeur vénale du fonds | Indemnise la perte de « droit au bail, pas-de-porte, clientèle, achalandage » ; déclencheurs : incendie, dégâts des eaux, climatiques, choc de véhicules | 43 | Applicable si une boutique **incendiée** pendant l'émeute ne peut plus rouvrir (bail résilié, refus du bailleur de reconstruire). |
| Déclaration | « dans les 2 jours ouvrés* en cas de vol, tentative de vol ou vandalisme » ; 5 jours ouvrés sinon | 76 | **Délai critique : 2 jours ouvrés**. |
| Plainte | « Prévenez la police ou la gendarmerie locale au plus vite et déposez plainte. Remettez-nous […] le certificat de dépôt de plainte accompagné d'un état estimatif » | 76 | Plainte + état estimatif des biens = pièces clés. |
| Déchéance | Refus si retard « si ce retard nous a causé un préjudice » ; déchéance totale en cas de fausse déclaration de mauvaise foi | 76-77 | La déchéance pour retard suppose un préjudice démontré par l'assureur. |
| **Franchise unique** | « Lorsque plusieurs garanties sont mises en jeu à l'occasion d'un même sinistre*, vous conservez à votre charge uniquement la plus élevée des franchises* applicables. » (mais les franchises PE et dommages se cumulent) | 80 | Vitrine + vol + vandalisme = **une seule franchise**, à vérifier dans le décompte de l'assureur. |
| TVA | « Si l'assuré* est assujetti à la taxe sur la valeur ajoutée (TVA), celle-ci est exclue du calcul des indemnités. » | 80 | Chiffrer les dommages HT si l'assuré récupère la TVA. |
| Expertise | « Vous pouvez également faire appel à un expert de votre choix. Nous désignerons alors le nôtre. Si ces deux experts ne parviennent pas à un accord, ils feront appel à un troisième. » | 78 | Expertise contradictoire possible, mais à vos frais. |
| Justificatifs | Justifier « par tous les moyens et documents […] dans le délai de prescription de deux ans. » | 78 | Factures, photos, inventaire, relevés de caisse. |

---

## 2. MMA — Contrat MMA PRO-PME, CG n° 352 p (avril 2021)

- Source : copie publique (philtr.fr) ; assureurs MMA IARD / MMA IARD Assurances Mutuelles. Local : `contrats/pdf/MMA_ProPME_CG_352p_2021-04.pdf`.
- Particularité clé : les **émeutes** sont un événement de la garantie « **Incendie et risques annexes** » (et aussi de « Dégâts des eaux », « Liquides », « Bris de machines »). La garantie Vandalisme exclut les dommages relevant de ces autres garanties.

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| Émeutes — garantie | Dommages matériels causés par : « des émeutes, mouvements populaires, actes de sabotage » (garantie Incendie et risques annexes) | 20 | Les dégâts matériels d'émeute relèvent de la garantie **Incendie et risques annexes** (franchise/plafond de cette garantie). |
| Émeutes — autres garanties | Même événement dans Dégâts des eaux (p. 21), Liquides (p. 22), Bris de machines « Cause externe […] émeutes, mouvements populaires, actes de sabotage » (p. 32) | 21, 22, 32 | Machine ou vitrine réfrigérée cassée par les émeutiers : aussi via Bris de machines. |
| Vol pendant une émeute | « Nous* couvrons également […] le vol ou la tentative de vol commis à l'occasion d'émeutes, mouvements populaires, actes de sabotage » | 28 | **Pillage couvert** au titre du Vol, dans les mêmes conditions (effraction, etc.). |
| Vol — conditions | Commis « par effraction ou escalade directe […] par forcement des serrures […] par agression » | 28 | Prouver l'effraction (photos, constat). |
| Vol — biens couverts | Biens mobiliers « qui vous* sont confiés* […] empruntés […] avec clause de réserve de propriété […] sous contrat de location » | 28 | **Biens confiés** (dépôt-vente, réparations clients) et matériel loué couverts. |
| Vol — moyens de fermeture | « Les moyens de fermeture ou de protection de vos* locaux* » | 28 | Rideau, serrures, grilles détériorés : réclamables. |
| Vol — protections | Si protections déclarées non mises en œuvre et sinistre facilité : « l'indemnité sera réduite de moitié » ; chèques/facturettes non répertoriés : réduite de moitié | 29 | Sanction : **−50 %**, pas un refus total. Vérifier les répertoires de chèques. |
| Vol — inoccupation | Suspension si fermeture cumulée « excède 45 jours » dans l'année ; valeurs : 4 jours consécutifs | 29 | À vérifier si la boutique était fermée avant les émeutes. |
| Vandalisme — définition | « Toute dégradation ou destruction volontaire commise par autrui* (ex : casse, graffiti, saccage). » | 5 | « Saccage » est expressément visé. |
| Vandalisme — biens | Biens immobiliers, agencements, aménagements, embellissements, mobilier (y compris confiés) | 30 | Couvre les aménagements du locataire. |
| Vandalisme — articulation | Exclus : dommages causés par les événements « Incendie, dégâts des eaux […] », « Vol », « Bris des glaces »… « que vous ayez ou non souscrit ces assurances » | 31 | Le dommage d'émeute passe par l'**Incendie et risques annexes** (où l'émeute est un événement), pas par le Vandalisme. |
| Bris des glaces | « vitrines, façades […] devantures […] enseignes, panneaux publicitaires » + « films anti-effraction » | 31 | Vitrine, enseigne, film anti-effraction. |
| Bris — extensions | « les détériorations des biens mobiliers d'exploitation* et des agencements […] les frais de gardiennage et de clôture provisoire » | 31 | Marchandises abîmées par la vitrine cassée + clôture provisoire. |
| Clôture / gardiennage | « les frais de gardiennage et de clôture provisoire consécutifs à un sinistre* garanti et visant à protéger les locaux* » | 12, 29 | Inclus dans les « frais et pertes ». |
| Assistance gardiennage | Gardien ou vigile pris en charge « au maximum pendant 120 heures » | 69 | **5 jours** de gardiennage via MMA Assistance. |
| Frais et pertes — locataire | « La perte financière résultant des frais engagés pour réaliser des agencements, aménagements, embellissements* […] devenus la propriété du bailleur » | 11 | Si le bail est résilié ou si le bailleur refuse de refaire : les travaux du locataire sont indemnisés. |
| Frais et pertes — perte d'usage | « la perte d'usage représentant tout ou partie de la valeur locative des locaux* » | 12 | **Loyer payé pour une boutique inutilisable** : réclamable. |
| Déplacement / relogement | « frais de déplacement et de réinstallation […] les frais de stockage » ; loyer d'une réinstallation temporaire | 12 | Garde-meuble, local provisoire. |
| Démolition / déblais / nettoyage | « les frais de démolition, de déblais ou de nettoyage » + « frais de désamiantage* » | 12 | Nettoyage après saccage réclamable. |
| Honoraires décorateur / BET | « les honoraires : - de décorateurs, de bureaux d'études et de contrôle technique et d'ingénierie » | 12 | Décorateur pour refaire la boutique. |
| Intérêts d'emprunt TVA | « remboursement des intérêts de l'emprunt contracté […] pour compenser la différence entre l'indemnité […] TVA exclue et […] TVA comprise » | 12 | Pour assuré non récupérateur de TVA. |
| Mise en conformité / pertes de loyers | Mise en conformité ; « la perte des loyers » (propriétaire) ; cotisation dommages-ouvrage | 12 | Si propriétaire des murs. |
| **Honoraires d'expert d'assuré** | « nous vous remboursons, sur justificatif, les honoraires de l'expert que vous aurez choisi » ; maximum « 10 % de l'indemnité […] 40 000 € par sinistre » | 69 | **Garantie distincte « Honoraires d'expert »** : l'expert d'assuré financé jusqu'à 10 % / 40 000 €. Vérifier dans les CP qu'elle est souscrite. |
| Expertise PE | « Les honoraires de l'expert choisi par vous* vous* seront remboursés selon les modalités […] « honoraires d'expert » si vous l'avez souscrite. » | 41 | Même chose pour les litiges de pertes d'exploitation. |
| Expertise — règle générale | « chacune des parties peut choisir un expert […] Chaque partie paie les honoraires de son expert et la moitié de ceux du troisième. » | 85 | Sans l'option, l'expert d'assuré est à vos frais. |
| Règle proportionnelle | « La règle proportionnelle de capitaux […] n'est pas applicable au présent contrat. » | 85 | Pas de réduction pour sous-assurance des capitaux (mais elle existe pour le CA/la marge brute en PE, p. 44). |
| Biens confiés | Garantis « dans la mesure où ils ne sont pas assurés par leur propriétaire » (assurance pour compte) | 85 | Biens de clients volés : réclamables. |
| Valeur à neuf matériel | « votre* matériel* de moins de 3 ans est indemnisé au prix du neuf » (option « valeur de rééquipement à neuf ») | 88 | Option à vérifier ; formule « PLUS » : neuf jusqu'à 6 ans. |
| Rééquipement à neuf | Matériel de 3 à 10 ans : valeur à neuf moins vétusté, « majoré de 33 % » ; factures « dans les 2 ans » | 89 | Racheter dans les 2 ans. |
| Vétusté matériel | Minimum « 10 % » par an, maximum « 50 % » ou « 80 % » selon le cas | 88 | Contester les taux de vétusté excessifs. |
| Frais annexes matériel | Vétusté « ne s'applique pas sur les frais d'emballages, de transport, dépose, pose, essai, installation » | 88 | Frais d'installation remboursés **sans vétusté**. |
| Bâtiments / agencements | 2ᵉ indemnité = vétusté « limitée […] au quart de la valeur de réparation » si travaux dans les 2 ans, même zone d'achalandage | 86 | Reconstruire dans les 2 ans = récupérer une partie de la vétusté. |
| Marchandises | « Prix d'achat au dernier cours précédant le sinistre*, frais de transport et de manutention compris » ; vendues non livrées : « Prix de vente convenu » | 90 | Les **commandes déjà vendues** volées sont indemnisées au **prix de vente**. |
| Archives / données | Coût de reconstitution, sur factures « dans les deux ans » | 90 | Reconstitution de la comptabilité et des fichiers clients. |
| PE — déclencheurs | Dommages couverts par « Incendie* et risques annexes… » (dont émeutes) **et** « votre* assurance Vol, vandalisme* » → « Pertes d'exploitation après vol, vandalisme* » | 41 | Option PE à vérifier pour chaque type d'événement souscrit. |
| PE — impossibilité d'accès | Dommages matériels « à moins de 1 000 mètres » qui « auraient été couverts au titre de votre* assurance Incendie* et risques annexes » | 42 | **Argument à faire valoir** : l'émeute étant un événement de la garantie Incendie et risques annexes, des dégâts à moins de 1 km pourraient ouvrir la PE même si la boutique est intacte. Seule l'exclusion terrorisme est explicite (p. 43). Formulation contestable : à confirmer avec l'expert. |
| PE — formules | Forfait : montant journalier × jours (max « 365 jours ») ; au réel : perte de marge brute + frais supplémentaires − charges épargnées | 43-44 | Jusqu'à 1 an au forfait. |
| PE — piège du CA déclaré | Si le CA réel dépasse le CA déclaré de plus de 20 % : indemnité réduite (cotisation payée / cotisation due) | 44 | Vérifier le CA déclaré dans les CP. |
| PE — après vol | Exclues les PE résultant « d'un vol des valeurs* » ou « d'une agression* » | 43 | PE après pillage de **marchandises** OK, PE après vol de caisse non. |
| Valeur vénale du fonds | Perte totale/partielle consécutive à un événement de « Incendie* et risques annexes… » | 47 | Émeute = événement de cette garantie : boutique incendiée ou saccagée qui ne peut rouvrir → indemnisation du fonds. |
| Déclaration | Vol : « 2 jours ouvrés » ; autres : « 5 jours ouvrés » ; autorités : « dans les 2 jours » pour vols, vandalisme | 81 | **Plainte sous 2 jours**. |
| Délai de paiement | Vol : « Au plus tôt 30 jours après la date de déclaration du sinistre* » ; autres sinistres : « Au plus tard 30 jours après la date : - d'accord entre les parties » | 92 | Paiement au plus tard 30 jours après l'accord : le relancer dès J+30. |
| État des pertes | « nous* fournir, dans un délai de 30 jours, un état des pertes […] certifié sincère et véritable » | 81 | **Délai de 30 jours** souvent oublié : l'agent doit le produire. |
| Plainte | « aviser immédiatement les autorités locales de police ou de gendarmerie et y déposer une plainte » | 82 | Obligation. |
| Biens retrouvés | Avant indemnisation : reprendre les biens retrouvés dans les 30 jours ; l'assureur paie « les frais nécessaires à cette récupération » | 82 | Frais de récupération réclamables. |
| Déchéance | Retard : déchéance « si nous* établissons que le retard nous* a causé un préjudice » ; fausse déclaration : déchéance | 82 | La charge du préjudice pèse sur l'assureur. |
| Exclusion RC | Exclus en RC : dommages « par des émeutes, mouvements populaires » | 71 | Sans incidence sur les dommages aux biens propres. |

---

## 3. Hiscox — Conventions Spéciales Multirisques Dommages aux Biens Professionnels n° MRP0623

- Source : hiscox.fr (espace courtage). Local : `contrats/pdf/HISCOX_MRP_CS_DommagesBiens_MRP0623.pdf`. Complété par la CG PRO by Hiscox MRP0918 (2018) et l'IPID MRP0820.

| Thème | Ce que dit le contrat (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| Émeutes — garantie | « Les dommages matériels causés par les émeutes et les mouvements populaires. » | 8 | Garantie émeutes incluse (dommages matériels). |
| Émeutes — articulation État | « s'exerce à défaut ou en complément de l'article L. 2216-3 du Code général des collectivités territoriales relatif à la responsabilité de l'État » | 8 | **Recours contre l'État** pour ce que l'assureur ne paie pas (franchise, PE…). Rare de le voir écrit dans un contrat. |
| Émeutes — exclusion générale | Exclusion 8 « Conflits sociaux et mouvements populaires » ; la garantie émeutes n'y déroge que « partielle[ment] » | 8, 28 | Seuls les **dommages matériels** sont repris ; les pertes financières sans dommage matériel restent exclues. |
| Vol et vandalisme — plainte | Sous réserve « que l'assuré dépose immédiatement une plainte, qui ne pourra être retirée qu'avec l'accord écrit préalable de l'assureur » | 9 | Plainte immédiate obligatoire. |
| Vol — conditions | « par effraction ou escalade ayant laissé des traces apparentes, par usage de fausses clés, par introduction clandestine, avec violence » | 9 | Photographier les **traces apparentes**. |
| Vol — détériorations | « Sont également couvertes les détériorations mobilières/immobilières […] consécutives à un vol ou une tentative de vol » | 10 | Porte/rideau forcés couverts au titre du vol. |
| Vol — exclusions | Exclus les vols « pendant une occupation […] dans le cadre d'un conflit du travail », « après abandon des bâtiments à la suite d'évacuation ou de réquisition », biens « en plein air » | 9-10 | Si la police a fait évacuer : risque d'exclusion à contester. |
| Vol caisse | Espèces en tiroir-caisse : vol « par effraction ou enlèvement desdits tiroirs-caisses » ou avec violence | 10 | Caisse arrachée pendant le pillage : couverte. |
| Vandalisme | « Les dommages matériels résultant d'actes de vandalisme. » | 11 | Couvert. |
| Bris de glace | « bris accidentels de verres, glaces et vitres incorporés aux bâtiments assurés, des enseignes lumineuses » | 9 | Vitrine + enseigne lumineuse. |
| Paiement / intérêts | Provision sous « 2 (deux) mois » et indemnité sous « 3 (trois) mois » après l'état estimatif ; au-delà, intérêts au taux légal (> 4 000 €) | 8 | Ces délais figurent dans la clause émeutes/catnat : **réclamer les intérêts de retard**. Règlement sous 10/15 jours ouvrés après accord, sinon intérêts (p. 15). |
| Bâtiments — vétusté | Vétusté « minimum de 10 (dix) % par an sans pouvoir excéder 70 (soixante-dix) % » ; solde versé si travaux réceptionnés sous 24 mois | 12 | Rachat de vétusté si travaux sous 24 mois. |
| Bâtiments non reconstruits | « valeur vénale des bâtiments sinistrés majorée de 20 (vingt) % » | 13 | Pour les propriétaires des murs. |
| Matériel / mobilier | Achat neuf « au cours de l'année précédant » le sinistre : « valeur de remplacement à neuf » | 13 | Matériel de moins d'un an : valeur à neuf. |
| Marchandises | Prix d'achat du jour + transport ; déjà vendues non livrées : « prix de vente convenu, déduction faite des frais épargnés […] et de la marge » | 14 | Commandes clients volées. |
| Vol par introduction clandestine | Dépôt de plainte « circonstancié » : « date et créneau horaire précis ; description des faits […] avis de témoins » | 14 | Modèle de plainte à suivre à la lettre. |
| **Honoraires expert d'assuré** | « remboursement des frais et honoraires de tout autre expert que vous aurez mandaté […] dans la limite de 5 (cinq) % de l'indemnité valorisée par notre expert. » | 14 | Expert d'assuré financé jusqu'à **5 %** (garantie « Frais et pertes additionnels », à souscrire). |
| Tiers expert | « En cas de divergence […] ils seront départagés par un troisième expert […] par voie judiciaire. » | 14 | Procédure contradictoire. |
| PE — déclencheurs | Perte de marge brute après dommage « au titre des événements Incendie et risques annexes, Événements climatiques, Catastrophes naturelles, Dégât des eaux ou Attentats » | 15 | Ni les **émeutes** ni le **vol/vandalisme** ne sont listés : PE **absente** après pillage (sauf incendie). |
| Frais supplémentaires d'exploitation | Loyers de réinstallation, réparations provisoires, travaux hors heures, transport express, reconstitution des archives | 16 | Mêmes déclencheurs que la PE (pas l'émeute). |
| **Frais et pertes additionnels** | « directement consécutifs à un dommage matériel garanti au titre de la 2e partie, section 1 « Dommages Matériels » » | 16 | Déclenchés par **tout** dommage matériel garanti, **émeutes et vandalisme compris**. |
| FPA — perte d'usage | « tout ou partie de la valeur locative des bâtiments assurés et occupés par l'assuré en cas d'impossibilité […] de les utiliser » | 17 | Loyer d'une boutique inutilisable. |
| FPA — crédit-bail | « le montant des annuités de crédit-bail […] qui […] resteraient à la charge de l'assuré » | 17 | Leasing du matériel détruit. |
| FPA — aménagements locataire | Perte « des aménagements qu'il avait réalisés […] devenus la propriété du bailleur » | 17 | Travaux du locataire perdus. |
| FPA — nettoyage, déblai, honoraires | « frais de nettoyage, déblai, démolition » ; « honoraires des architectes […] décorateurs » ; mise en conformité | 17 | Nettoyage après saccage, décorateur. |
| FPA — clôture | « les frais de bâchage, de clôture provisoire et de gardiennage » | 17 | Planches et vigile. |
| **FPA — trésorerie** | « intérêts des emprunts […] jusqu'au versement de l'indemnité » ; « le montant des découverts bancaires » | 17 | **Agios et découverts** pendant l'attente : rarement réclamés. |
| **FPA — fournisseurs** | « le coût d'achat des matières premières et autres approvisionnements que l'assuré serait contraint de continuer à régler » ; « frais d'annulation de commande » | 17 | Commandes fournisseurs payées malgré la fermeture, pénalités d'annulation. |
| Valeur vénale du fonds | Déclencheurs : Incendie, climatiques, catnat, dégâts des eaux ; exclue en zone PPR | 18 | Seulement si la boutique a été **incendiée**. |
| Impossibilité d'accès / désaffection | Mêmes déclencheurs (pas d'émeutes) | 18-19 | **Absent** pour l'émeute. |
| Règle proportionnelle | « nous renonçons à appliquer la règle proportionnelle » | 32 | Pas de réduction pour sous-assurance. |
| Déclaration | Dommages : « 5 (cinq) jours » ; vol : « 48 (quarante-huit) heures » | 31-32 | **48 h pour le vol** (plus court que MAAF/MMA). |
| Plainte | « déposer perte dans les 72 (soixante-douze) heures […] et nous communiquer la copie de votre dépôt de plainte » | 32 | Plainte sous 72 h. |
| Déchéance | Retard : déchéance « si ce manquement nous a causé un préjudice » ; fausse déclaration : déchéance totale | 32 | — |
| Assistance | Gardiennage par agent de sécurité « pour une durée de 72 (soixante-douze) heures maximums » | 47 | Gratuit. |
| CG 2018 (MRP0918) | Expert d'assuré : « dans la limite de cinq (5) % de l'indemnité initialement valorisée par notre expert » ; exclusion « émeutes et mouvements populaires » (guerres et assimilés) avec garantie émeutes en dérogation | 27, 45, 22 | Même logique dans l'ancienne version. |

---

## 4. Pacifica (Crédit Agricole) — IPID Multirisque Professionnelle 7197A.36 (2020.12)

- Document d'information de 3 pages seulement (pas les CG complètes, non trouvées). À utiliser comme **indice** à confirmer dans les CG et CP du client.

| Thème | Ce que dit le document (citation courte) | Page | Ce que ça veut dire pour le commerçant pillé |
|---|---|---|---|
| Émeutes | « Attentats, actes de terrorisme, émeutes, mouvements populaires » (garantie systématique) | 1 | Incluse dans tous les contrats avec local. |
| Vol et vandalisme | « Vol et vandalisme : valeur du capital vol de 2 000 € à 300 000 € » | 1 | Plafond selon les CP. |
| Enseignes et stores | « à concurrence de 20 000 € » | 1 | Enseigne arrachée. |
| **Pertes indirectes** | « frais annexes justifiés à la suite d'un sinistre garanti : frais réels limités à 10 % de l'indemnité versée » | 1 | +10 % sur justificatifs. |
| Démolition / déblais | « 25 % de l'indemnité versée pour les dommages aux biens » | 1 | Évacuation des débris. |
| **Mensualités de prêt** | « jusqu'à 12 mensualités du prêt en cours limitées à 500 € par mois » (prêt immobilier, rénovation ou achat du fonds) | 1 | **Jusqu'à 6 000 €** de remboursement d'échéances : rarement réclamé. |
| Investissements du locataire | « Pertes des investissements réalisés par un locataire : à concurrence des frais réels. » | 1 | Aménagements perdus. |
| Locaux provisoires | Garantie aux deux adresses en cas de « locaux provisoires suite à sinistre […] limitée à 2 ans » | 1 | Stock déplacé dans un local temporaire : assuré. |
| Option rééquipement à neuf | « coût de remplacement dans la limite du rééquipement à neuf » | 1 | À vérifier dans les CP. |
| Graffitis | Exclus : « Les graffitis, inscriptions, salissures, affichages à l'extérieur des locaux. » | 1 | Tags extérieurs **non** couverts (contrairement à la MAAF). |
| Prévention | « Le non-respect des mesures de prévention exigées entraîne une prise en charge à hauteur de 70 % » | 1 | Réduction de 30 %, pas un refus total. |
| Franchises | Générales de 150 € à 1 200 € ; bris de glace et enseignes : franchise « réduite de moitié » | 1 | — |
| **PE — impossibilité d'accès pour émeute** | « une impossibilité d'accès au local assuré du fait d'une émeute ou d'un mouvement populaire : […] indemnité forfaitaire journalière de 15 € à 8 000 € » | 2 | **Seul contrat du lot couvrant la fermeture forcée sans dommage**, si l'option est souscrite. |
| PE émeute — limites | « durée d'indemnisation de 7 jours consécutifs ou non par année d'assurance et un seuil d'intervention de 3 jours » | 2 | Au plus 7 jours, après 3 jours de fermeture. |
| PE — dommage direct | « durée d'indemnisation de 18 mois consécutifs et un seuil d'intervention de 3 jours » | 2 | Boutique pillée : PE jusqu'à 18 mois. |
| PE — exclusion | Exclues les pertes « qui résulteraient d'une grève, d'un lock-out, d'un mouvement de foule dans violence volontaire. » (texte tel quel ; « dans » est probablement une coquille pour « sans ») | 2 | Si on lit « sans » : seule la foule non violente est exclue, et les émeutes violentes du 17-18 octobre restent couvertes. À confirmer dans les CG. |
| Valeur vénale du fonds | Perte « en cas d'impossibilité complète et définitive de continuer l'exploitation » — plafond de 10 000 € à 3 000 000 € | 2 | — |
| Déclaration | Délais non chiffrés dans l'IPID (« dans les conditions et délais impartis ») | 3 | **Absent** de l'IPID : à lire dans les CG. |
| Honoraires expert d'assuré | Non mentionnés | — | **Absent** de l'IPID. |

---

## 5. Tableau croisé — « Postes souvent oubliés et récupérables »

Légende : ✅ = clause présente (page) · ❌ = absente ou exclue · ? = non vérifiable dans le document disponible (IPID seulement).

| Poste récupérable | MAAF 11031-01/26 | MMA PRO-PME 352p | Hiscox MRP0623 | Pacifica (IPID) | Plafond type relevé |
|---|---|---|---|---|---|
| **Honoraires de l'expert d'assuré** | ❌ chacun paie son expert (p78) ; exclu des pertes indirectes (p25) | ✅ garantie « Honoraires d'expert » (p69) | ✅ via FPA (p14) | ? | MMA : 10 % de l'indemnité, max 40 000 € ; Hiscox : 5 % de l'indemnité chiffrée par l'expert de l'assureur |
| **Pertes indirectes forfaitaires** | ✅ (p25) | ❌ pas de forfait (frais et pertes listés) | ❌ (FPA détaillés à la place) | ✅ (p1) | 10 % de l'indemnité dommages (MAAF, Pacifica) |
| Clôture provisoire / gardiennage | ✅ (p14, 19, 23) | ✅ (p12, 28, 31) | ✅ (p17) | ? | MAAF 6 600 € ; autres : CP |
| Gardiennage par l'assistance (gratuit) | ✅ 72 h (p58) | ✅ 120 h (p69) | ✅ 72 h (p47) | ? | 72 à 120 heures |
| Nettoyage de tags / graffitis | ✅ (p23) | ✅ (« graffiti » dans la définition du vandalisme, p5) | ✅ vandalisme (p11) | ❌ exclu à l'extérieur (p1) | CP |
| Rideau métallique / moyens de fermeture | ✅ (p14) | ✅ (p28) | ✅ détériorations après vol (p10) | ? | CP |
| Store / banne / enseigne | ✅ (p14) | ✅ enseignes (p31) | ✅ enseignes lumineuses (p9) | ✅ (p1) | Pacifica 20 000 € |
| Remplacement des serrures | ✅ (p19) | ✅ moyens de fermeture (p28) | ✅ détériorations (p10) | ? | MAAF 3 000 € |
| Démolition / déblais / nettoyage | ✅ (p24) | ✅ (p12) | ✅ (p17) | ✅ (p1) | Pacifica 25 % ; autres : frais réels ou CP |
| Honoraires d'architecte / décorateur | ✅ (p25) | ✅ (p12) | ✅ (p17) | ? | MAAF 5 % de l'indemnité immobilière |
| Mise en conformité | ✅ (p25) | ✅ (p12) | ✅ (p17) | ? | MAAF 500 €/m² |
| Garde-meuble / déménagement | ✅ (p25) | ✅ (p12) | ? | ? | MAAF 6 400 € pour le garde-meuble |
| Relogement / local provisoire | ✅ 2 ans (p25) | ✅ (p12) | ✅ FSE (p16, déclencheurs restreints) | ✅ 2 ans (p1) | — |
| Perte d'usage (loyer d'un local inutilisable) | ❌ absent en tant que tel | ✅ (p12) | ✅ (p17) | ? | — |
| Aménagements du locataire perdus | ❌ absent | ✅ (p11) | ✅ (p17) | ✅ (p1) | Frais réels (Pacifica) |
| Crédit-bail / leasing restant dû | ✅ option bris de matériel (p23) | ✅ perte financière, contrat de financement (p89) | ✅ annuités (p17) | ? | CP |
| Mensualités de prêt pendant les travaux | ❌ | ❌ | ❌ | ✅ (p1) | 12 × 500 € |
| Intérêts d'emprunt / découvert bancaire | ❌ | ✅ intérêts liés à la TVA uniquement (p12) | ✅ (p17) | ❌ | — |
| Achats fournisseurs à payer / annulation de commandes | ❌ | ❌ | ✅ (p17) | ❌ | — |
| Marchandises vendues non livrées au prix de vente | ❌ (prix d'achat, p79) | ✅ (p90) | ✅ marge déduite (p14) | ? | — |
| Biens confiés (clients, dépôt-vente) | ✅ (p19, 22) | ✅ (p28, 85) | ? | ? | CP |
| Espèces / caisse | ✅ 10 % du contenu, max 16 000 € (p15) | ✅ valeurs (p28) | ✅ tiroir-caisse (p10) | ❌ hors meuble fermé (p1) | MAAF 16 000 € |
| Rachat de vétusté (remplacement sous 2 ans) | ✅ 33 % max (p78-79) | ✅ +33 % ou ¼ de la valeur (p86, 89) | ✅ solde sous 24 mois (p12) | ✅ option (p1) | — |
| Valeur à neuf du matériel récent | ✅ informatique < 2 ans (p79) | ✅ option < 3 ans (< 6 ans en PLUS) (p88-89) | ✅ < 1 an (p13) | ✅ option (p1) | — |
| Frais d'installation/transport sans vétusté | ? | ✅ (p88) | ✅ frais accessoires (p17) | ? | — |
| Reconstitution d'archives / données | ❌ exclue après vol (p21, 23) | ✅ (p90) | ✅ FSE (p16) | ? | — |
| PE après pillage (dommage direct) | ✅ forfait, 60 jours ouvrés (p43) | ✅ option « PE après vol, vandalisme » (p41) | ❌ (p15) | ✅ 18 mois (p2) | — |
| PE pour fermeture forcée **sans dommage** (émeute alentour) | ❌ exclue (p43) | ? argument possible (< 1 000 m, p42) | ❌ (p18) | ✅ 7 jours, forfait 15 à 8 000 €/jour (p2) | — |
| Frais supplémentaires d'exploitation | ✅ (p41) | ✅ (p12, 43-44) | ✅ (p16, sans les émeutes) | ✅ (p2) | — |
| Perte de valeur vénale du fonds | ✅ si incendie (p43) | ✅ incendie et risques annexes, dont émeutes (p47) | ✅ si incendie (p18) | ✅ (p2) | Pacifica 10 k€ à 3 M€ |
| Intérêts de retard de l'assureur | ❌ ni délai ni intérêts dans l'art. 38 (p80) | ❌ pas d'intérêts, mais paiement au plus tard 30 jours après l'accord (p92) | ✅ taux légal > 4 000 € (p8, 15) | ? | — |
| Franchise unique en cas de garanties cumulées | ✅ la plus élevée seulement (p80) | ? non trouvé | ? non trouvé | ? | — |
| Recours contre l'État (L.2216-3 CGCT) mentionné | ❌ | ❌ | ✅ (p8) | ❌ | Hors contrat |
| Pas de règle proportionnelle de capitaux | ✅ (p78) | ✅ (p85) | ✅ (p32) | ? | — |

### Délais impératifs (pour l'agent)

| | MAAF | MMA | Hiscox | Pacifica (IPID) |
|---|---|---|---|---|
| Déclaration vol / vandalisme | 2 jours ouvrés (p76) | 2 jours ouvrés (p81) | 48 heures pour le vol (p32) | Non chiffré |
| Déclaration autres dommages | 5 jours ouvrés | 5 jours ouvrés | 5 jours | Non chiffré |
| Plainte | « au plus vite » (p76) | Aux autorités sous 2 jours (p81) | Sous 72 h (p32), immédiate pour vol et vandalisme (p9) | Non chiffré |
| État des pertes | « dès que possible » (p76) | **30 jours** (p81) | Base des délais de paiement (p8) | Non chiffré |
| Remplacement pour le rachat de vétusté | 2 ans | 2 ans | 24 mois | Non chiffré |

### Enseignements clés pour le pitch
1. Le contrat ne paie que ce qui est **demandé et justifié** : chaque contrat comporte 10 à 20 postes annexes (clôture, nettoyage, honoraires, perte d'usage, intérêts, vétusté rachetable) que le commerçant ignore.
2. Les clauses **diffèrent fortement** d'un contrat à l'autre. Exemples : expert d'assuré financé chez MMA (10 %, plafond 40 k€) et Hiscox (5 %) mais pas chez MAAF ; fermeture sans dommage couverte uniquement chez Pacifica (7 jours) ; tags couverts chez MAAF mais exclus à l'extérieur chez Pacifica. L'agent doit donc lire **le contrat du client**.
3. Les **délais sont courts** (48 h à 2 jours ouvrés, 30 jours pour l'état des pertes chez MMA). L'agent doit produire une checklist dès J+0.
