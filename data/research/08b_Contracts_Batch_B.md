# 08b — Policies Batch B: MAAF, MMA, Hiscox, Pacifica (Crédit Agricole)

> Objective: for a merchant vandalised/looted during the riots of 17-18 October 2026, identify in **real** commercial multi-risk policies everything that can legitimately be claimed.
> Reading rules:
> - **Page** = page number **of the PDF file** (for MAAF, the number printed at the bottom of the page = PDF page − 1; for MMA and Hiscox, PDF page = printed page).
> - Quotes are **verbatim** (shortened with « […] » where needed). Nothing is invented: if a clause does not exist in the document, it is marked **« absent »**.
> - « CP » amounts refer to the client's *conditions particulières / CP* (policy schedule) (ceilings/*franchises* — deductibles — specific to each policy): the agent will have to read them in addition to the *conditions générales / CG* (general conditions).
> - Extracted files (text): `contrats/txt/` — original PDFs: `contrats/pdf/`.

## Documents collected

| Insurer | Document | Ref./version | Pages | Source | Local file |
|---|---|---|---|---|---|
| **MAAF** (Covéa) | Conditions générales Multirisque Professionnelle | Ref. 11031 - 01/26 | 90 | https://www.maaf.fr/fr/files/live/sites/maaf/files/DOCUMENTS/Professionnels/CG/MAAF_Conditions_generales_Multirisque_pro_11031.pdf (official site) | `contrats/pdf/MAAF_MRP_CG_11031-0126.pdf` / `contrats/txt/MAAF_MRP_CG_11031-0126.txt` |
| **MMA** (Covéa) | Contrat MMA PRO-PME — Conditions Générales | CG n° 352 p, April 2021 edition | 104 | https://philtr.fr/static/pdf/insurance/mrp/mma_mrp.pdf (copy hosted by a comparison site; not found on mma.fr) | `contrats/pdf/MMA_ProPME_CG_352p_2021-04.pdf` / `contrats/txt/MMA_ProPME_CG_352p_2021-04.txt` |
| **Hiscox** (broker offering) | Conventions Spéciales Multirisques Dommages aux Biens Professionnels | n° MRP0623 | 51 | https://www.hiscox.fr/courtage/sites/courtage/files/documents/MRP0623%20-%20Conventions%20Speciales%20Multirisques%20Dommages%20aux%20Biens%20Professionnels%20.pdf | `contrats/pdf/HISCOX_MRP_CS_DommagesBiens_MRP0623.pdf` / `.txt` |
| Hiscox (supplement) | PRO by Hiscox — Conditions Générales (earlier version) | n° MRP0918 (19215 11/18) | 46 | https://www.hiscox.fr/courtage/courtage/sites/courtage/files/documents/CG%20Pro%20by%20Hiscox.pdf | `contrats/pdf/HISCOX_MRP_CG_ProByHiscox.pdf` / `.txt` |
| Hiscox (supplement) | IPID PRO by Hiscox | MRP0820 | 2 | https://www.hiscox.fr/courtage/sites/courtage/files/documents/IPID_Pro%20by%20Hiscox%20-%20MRP0820.pdf | `contrats/pdf/HISCOX_MRP_IPID_MRP0820.pdf` / `.txt` |
| **Pacifica** (Crédit Agricole, bancassurer) | Information document (IPID) Assurance Multirisque Professionnelle avec ou sans local | 7197A.36 (2020.12) | 3 | https://www.credit-agricole.fr/content/dam/assetsca/master/public/commun/documents/7197A.36_IPA_doc%20info_M9_PRO-122020-BD.pdf | `contrats/pdf/CA_Pacifica_MRP_IPID_7197A36-122020.pdf` / `.txt` |

**Not found (to be reported honestly)**: commercial multi-risk CG for **MACIF** and **MAIF** (not published as an accessible PDF; comparison sites indicate that MACIF does not release them); complete CG for **Pacifica** and **ACM/Crédit Mutuel** (only IPIDs/memos/flyers found). The official MMA PDF is not on mma.fr: the version used (April 2021) is a third-party copy, potentially superseded by a more recent edition.

> Hiscox caveat: the IPID states that PRO by Hiscox targets « entreprises prestataires de conseils et services » [consulting and service companies] (offices). It is a good example of a « courtier » [broker] policy but less representative of a shop.

---

## 1. MAAF — Multirisque Professionnelle, CG Ref. 11031 - 01/26

- Source: maaf.fr (official). Local: `contrats/pdf/MAAF_MRP_CG_11031-0126.pdf`.
- Structure: base covers « Vos locaux et leur contenu » [your premises and their contents] + options (Theft/vandalism, Equipment breakdown) + « Tranquillité financière » [financial peace of mind] (*perte d'exploitation / PE* — business interruption —, loss of goodwill value) as an option.

| Topic | What the policy says (short verbatim quote) | Page | What this means for the looted merchant |
|---|---|---|---|
| Riots — cover | « nous garantissons les dommages matériels* directs causés aux biens immobiliers et mobiliers assurés résultant d'émeutes* ou mouvements populaires*. » | 15 | *Émeutes et mouvements populaires* (riots and civil commotion) cover **included** in « Vos locaux et leur contenu ». |
| Riots — scope | « Ces émeutes* et mouvements populaires* sont couverts s'ils sont à l'origine des dommages garantis au titre de : l'incendie […] le bris des vitres, vitrines et enseignes, les garanties optionnelles : - la garantie vol, tentative de vol et vandalisme […] » | 15 | Riot-related looting/breakage is only indemnified via the covers **taken out** (fire, glass breakage, theft-vandalism if the option is taken). Check the CP: without the Theft/vandalism option, looting is not covered. |
| Riots — cash | Table: cash, securities and valuables « À concurrence de 10 % de la somme assurée au titre du contenu […] avec un maximum de 16 000 € » | 15 | The till stolen during a riot can be claimed within this limit. |
| Definition of riots | « Soulèvements populaires violents contre l'autorité publique pour obtenir la réalisation de revendication économique, sociale, ou politique et troublant la sécurité et l'ordre public. » | 82 | Characterisation to be documented (press articles, prefectoral orders). |
| Definition of civil commotion | « Actions violentes de la foule troublant la sécurité et l'ordre public. » | 83 | Broad definition, easy to meet for 17-18 October. |
| Theft — conditions | Theft covered « Suite à introduction dans les bâtiments* assurés : • avec effraction • sans effraction - Suite à agression » | 19 | Break-in is the usual entry point for looting (forced shutter, broken window). |
| Theft — shop windows | « Vol de vos marchandises exposées dans les vitrines - Suite à un bris de vitres sans introduction dans les bâtiments* assurés » | 19 | Theft « à travers la vitrine » [through the window] covered even without entering the shop. |
| Theft — definition of break-in | « Avec effraction : tout forcement, dégradation ou destruction de tout dispositif de fermeture* ou de tout élément de clos ou de couvert » | 19 | Photograph the traces of forcing (shutter, lock, glass). |
| Theft — required protections | « En cas de non-respect de ces obligations, la garantie ne sera pas acquise. » (locked up, alarm activated, no class 1-3 padlocks) | 21 | Likely line of attack for the insurer: prove the protections were in place and active. |
| Vandalism | « Nous garantissons les conséquences des détériorations, dégradations ou destructions volontaires de vos biens, commises par autrui » | 22 | Covers buildings, fittings, furniture, stock, *biens confiés* (customers' goods held in custody) (Theft/vandalism option). |
| Tags / graffiti | « Les dommages causés par les inscriptions telles que graffitis et tags sur les murs et vitrines de vos bâtiments* assurés » | 23 | **Tag removal claimable** (often forgotten). |
| *Bris de glace* (glass breakage) | Insured property: « la devanture, la clôture […] portes, vitrines […] les enseignes dès lors qu'elles sont fixées aux bâtiments* assurés » | 14 | Broken window + sign covered. |
| Glass breakage — extensions | « le bris des produits non verriers constituant la façade […] (y compris le bris des dispositifs de protection tels que les rideaux métalliques et les encadrements) » | 14 | **Metal shutter** damaged at the same time as the window: claimable. |
| Breakage — displayed goods | « Vos marchandises exposées et détériorées par le bris » : « À concurrence de 20 % de la somme assurée au titre du contenu » | 14 | Goods damaged by window shards. |
| Breakage — awnings, blinds | « Par extension, sont garantis les auvents, bannes, stores et corbeilles dès lors qu'ils sont fixés aux bâtiments* assurés. » | 14 | Torn-off blind/awning: claimable. |
| *Clôture provisoire* (temporary boarding-up) / *gardiennage* (security guarding) | « les frais de clôture et de gardiennage engagés avec notre accord » — ceiling « 6 600 € » | 14, 19, 23 | Boards, plywood, security guard after the looting: up to €6,600 (breakage, theft, vandalism). **Obtain the insurer's consent**. |
| Boarding-up obligation | « vous vous engagez à faire poser immédiatement une clôture provisoire dans le cas où celle-ci s'avérerait nécessaire. » | 14, 18 | Insured's obligation: comply with it and invoice it. |
| Assistance — security guarding | « le gardiennage des locaux pendant 72 heures : afin de préserver vos biens contre le vol à la suite d'un acte de vandalisme » | 58 | Free service on top of the €6,600. Longer response times in case of riots (p. 58). |
| Locks | « Le remplacement à l'identique des serrures » — « 3 000 € » | 19 | Lock replacement claimable. |
| Recovery costs | « Les frais exposés pour la récupération des objets assurés volés » — « Sans limitation de somme » | 19 | Costs to recover goods that are found. |
| Compliance upgrade | « 500 € par m² de superficie développée de vos locaux professionnels » | 25 | Works imposed by regulations during reinstatement. |
| Removal / storage | « Frais exposés avec un maximum de 6 400 € pour frais de garde-meuble » | 25 | Storage of surviving stock during works. |
| Salvage measures | « À concurrence de 5 % de l'indemnité versée au titre des dommages aux biens assurés » | 25 | Costs to limit the loss. |
| Rehousing | « Frais exposés pendant 2 ans » (rent for temporary relocation) | 25 | Temporary premises to keep trading. |
| Demolition / debris removal | « les frais de démolition et de déblais des biens assurés, ainsi que les frais exposés à la suite des mesures conservatoires* imposées par décision administrative » | 24 | Removal of rubble and debris. Ceiling not quantified in the table of supplementary covers. |
| Architect / designer fees | « À concurrence de 5 % de l'indemnité versée au titre des biens immobiliers » | 25 | Designer/architect fees to redo the shop. |
| ***Pertes indirectes*** (indirect losses) | « À concurrence de 10 % de l'indemnité versée au titre des dommages aux biens assurés » — « Sans franchise » | 25 | **+10%** against supporting documents (correspondence, formalities). |
| Limit on indirect losses | « ne peut en aucun cas servir à prendre en charge des honoraires […] d'experts d'assuré, ni à compenser […] une franchise*, d'une vétusté* » | 25 | The 10% can **not** fund the *expert d'assuré* (policyholder's loss assessor). |
| Policyholder's loss-assessor fees | « Chacun de nous prendra en charge les frais et honoraires de son expert et, le cas échéant, la moitié de ceux du troisième. » | 78 | **Absent** as a cover: the policyholder's loss assessor remains at the merchant's expense. |
| Construction-insurance premium | « À concurrence de 5 % de l'indemnité versée au titre des bâtiments* sinistrés » | 25 | If major works. |
| Leased equipment | « l'indemnité de résiliation incluant les loyers restant dus que nous versons à la société propriétaire du matériel » | 23 | Equipment breakdown option: lease balance on a destroyed card terminal/computer. |
| Stock — valuation | « évaluées au prix d'achat calculé au cours du jour* à la date du sinistre […] et majoré des frais accessoires de transport. » | 79 | Claim the **current purchase price** + transport (not the selling price). |
| Furniture/equipment — *rachat de vétusté* (depreciation buy-back) | « la vétusté* déduite […] vous sera remboursée sur présentation des factures à hauteur de 33 % maximum, dès lors que le remplacement s'effectue dans les deux ans » | 79 | Buying back = recovering up to 33% of *vétusté* (depreciation). |
| IT < 2 years | « Le matériel informatique de moins de 2 ans est évalué en valeur à neuf*, sans aucune déduction de vétusté*. » | 79 | Recent till, PC, tablet: *valeur à neuf* (replacement-as-new). |
| Buildings — depreciation | « remboursée sur présentation des factures à hauteur de 33% maximum » (rebuilding within 2 years, same use) | 78 | For owners of the walls / fit-out. |
| *Règle proportionnelle de capitaux* (underinsurance averaging) | « La règle proportionnelle de capitaux […] n'est pas applicable au présent contrat. » | 78 | No reduction for underinsurance of sums insured. |
| Business interruption — basis | « la perte de votre marge brute sur chiffre d'affaires ou sur recettes, honoraires, commissions. » + additional operating expenses | 41 | Loss of *marge brute* (gross margin). « Tranquillité financière » option to be checked in the CP. |
| BI — riots | Triggering events « (y compris s'ils surviennent à l'occasion d'émeutes* ou mouvements populaires*) » ; « si l'option vol, tentative de vol et vandalisme est souscrite » | 41 | Closure after looting is indemnifiable if the BI option (and the Theft/vandalism option) are taken out. |
| BI — after theft | BI following theft: « 2 jours ouvrés » [2 business days] waiting period, ceiling « indemnité journalière forfaitaire […] multipliée par 60 jours ouvrés » | 43 | After looting: **flat daily rate**, at most 60 business days. |
| BI — actual / flat rate | Actual basis: period of 12, 18 or 24 months; flat rate: 100% of the daily flat rate if total stoppage, 50% if partial | 42 | Distinguish total closure from partial reopening. |
| BI — exclusion | Excluded: BI resulting « de l'impossibilité d'accès à votre outil de production résultant d'émeutes et mouvements populaires* » | 43 | A shop **not** damaged but closed because of surrounding riots: **not covered**. |
| BI — terrorism | Statutory waiting period « trois jours ouvrés, avec un minimum de 1 140 euros » | 57 | Only if the events are characterised as terrorism. |
| Loss of goodwill value | Indemnifies the loss of « droit au bail, pas-de-porte, clientèle, achalandage » [leasehold right, key money, customer base, goodwill]; triggers: fire, water damage, weather, vehicle impact | 43 | Applicable if a shop **set on fire** during the riot can no longer reopen (lease terminated, landlord refuses to rebuild). |
| Notification | « dans les 2 jours ouvrés* en cas de vol, tentative de vol ou vandalisme » ; 5 business days otherwise | 76 | **Critical deadline: 2 business days**. |
| Police report | « Prévenez la police ou la gendarmerie locale au plus vite et déposez plainte. Remettez-nous […] le certificat de dépôt de plainte accompagné d'un état estimatif » | 76 | Police report + estimated statement of property = key documents. |
| *Déchéance* (forfeiture) | Refusal for delay « si ce retard nous a causé un préjudice » [if the delay caused us prejudice]; total forfeiture in case of a bad-faith false declaration | 76-77 | Forfeiture for delay requires prejudice demonstrated by the insurer. |
| **Single deductible** | « Lorsque plusieurs garanties sont mises en jeu à l'occasion d'un même sinistre*, vous conservez à votre charge uniquement la plus élevée des franchises* applicables. » (but BI and property deductibles are cumulative) | 80 | Window + theft + vandalism = **a single deductible**, to be checked in the insurer's settlement statement. |
| VAT | « Si l'assuré* est assujetti à la taxe sur la valeur ajoutée (TVA), celle-ci est exclue du calcul des indemnités. » | 80 | Quantify damage excl. VAT if the insured recovers VAT. |
| Loss adjustment | « Vous pouvez également faire appel à un expert de votre choix. Nous désignerons alors le nôtre. Si ces deux experts ne parviennent pas à un accord, ils feront appel à un troisième. » | 78 | Joint loss adjustment possible, but at your own expense. |
| Supporting evidence | Prove « par tous les moyens et documents […] dans le délai de prescription de deux ans. » | 78 | Invoices, photos, inventory, till records. |

---

## 2. MMA — Contrat MMA PRO-PME, CG n° 352 p (April 2021)

- Source: public copy (philtr.fr); insurers MMA IARD / MMA IARD Assurances Mutuelles. Local: `contrats/pdf/MMA_ProPME_CG_352p_2021-04.pdf`.
- Key feature: **riots** are an event of the « **Incendie et risques annexes** » [fire and related risks] cover (and also of « Dégâts des eaux » [water damage], « Liquides » [liquids], « Bris de machines » [machinery breakdown]). The Vandalism cover excludes damage falling under those other covers.

| Topic | What the policy says (short verbatim quote) | Page | What this means for the looted merchant |
|---|---|---|---|
| Riots — cover | Property damage caused by: « des émeutes, mouvements populaires, actes de sabotage » (Fire and related risks cover) | 20 | Riot property damage falls under the **Fire and related risks** cover (that cover's deductible/ceiling). |
| Riots — other covers | Same event in Water damage (p. 21), Liquids (p. 22), Machinery breakdown « Cause externe […] émeutes, mouvements populaires, actes de sabotage » (p. 32) | 21, 22, 32 | Machine or refrigerated display broken by rioters: also via Machinery breakdown. |
| Theft during a riot | « Nous* couvrons également […] le vol ou la tentative de vol commis à l'occasion d'émeutes, mouvements populaires, actes de sabotage » | 28 | **Looting covered** under Theft, on the same conditions (break-in, etc.). |
| Theft — conditions | Committed « par effraction ou escalade directe […] par forcement des serrures […] par agression » | 28 | Prove the break-in (photos, report). |
| Theft — property covered | Movable property « qui vous* sont confiés* […] empruntés […] avec clause de réserve de propriété […] sous contrat de location » | 28 | ***Biens confiés*** (customers' goods held in custody) (consignment, customer repairs) and hired equipment covered. |
| Theft — means of closure | « Les moyens de fermeture ou de protection de vos* locaux* » | 28 | Damaged shutter, locks, grilles: claimable. |
| Theft — protections | If declared protections not implemented and loss facilitated: « l'indemnité sera réduite de moitié » ; unrecorded cheques/card slips: reduced by half | 29 | Sanction: **−50%**, not outright refusal. Check the cheque registers. |
| Theft — unoccupancy | Suspension if cumulative closure « excède 45 jours » [exceeds 45 days] in the year; valuables: 4 consecutive days | 29 | To be checked if the shop was closed before the riots. |
| Vandalism — definition | « Toute dégradation ou destruction volontaire commise par autrui* (ex : casse, graffiti, saccage). » | 5 | « Saccage » [ransacking] is expressly named. |
| Vandalism — property | Buildings, fittings, fit-out, *embellissements* (tenant's fit-out), furniture (including goods held in custody) | 30 | Covers the tenant's fit-out. |
| Vandalism — interplay | Excluded: damage caused by the events « Incendie, dégâts des eaux […] », « Vol », « Bris des glaces »… « que vous ayez ou non souscrit ces assurances » | 31 | Riot damage goes through **Fire and related risks** (where riots are an event), not Vandalism. |
| Glass breakage | « vitrines, façades […] devantures […] enseignes, panneaux publicitaires » + « films anti-effraction » | 31 | Shop window, sign, anti-burglary film. |
| Breakage — extensions | « les détériorations des biens mobiliers d'exploitation* et des agencements […] les frais de gardiennage et de clôture provisoire » | 31 | Goods damaged by the broken window + temporary boarding-up. |
| Boarding-up / security guarding | « les frais de gardiennage et de clôture provisoire consécutifs à un sinistre* garanti et visant à protéger les locaux* » | 12, 29 | Included in « frais et pertes » [expenses and losses]. |
| Assistance — security guarding | Caretaker or security guard covered « au maximum pendant 120 heures » | 69 | **5 days** of security guarding via MMA Assistance. |
| Expenses and losses — tenant | « La perte financière résultant des frais engagés pour réaliser des agencements, aménagements, embellissements* […] devenus la propriété du bailleur » | 11 | If the lease is terminated or the landlord refuses to redo: the tenant's works are indemnified. |
| Expenses and losses — loss of use | « la perte d'usage représentant tout ou partie de la valeur locative des locaux* » | 12 | **Rent paid for an unusable shop**: claimable. |
| Removal / rehousing | « frais de déplacement et de réinstallation […] les frais de stockage » ; rent for temporary relocation | 12 | Storage, temporary premises. |
| Demolition / debris removal / cleaning | « les frais de démolition, de déblais ou de nettoyage » + « frais de désamiantage* » | 12 | Cleaning after ransacking claimable. |
| Designer / engineering fees | « les honoraires : - de décorateurs, de bureaux d'études et de contrôle technique et d'ingénierie » | 12 | Designer to redo the shop. |
| VAT loan interest | « remboursement des intérêts de l'emprunt contracté […] pour compenser la différence entre l'indemnité […] TVA exclue et […] TVA comprise » | 12 | For an insured who does not recover VAT. |
| Compliance upgrade / loss of rent | Compliance upgrade; « la perte des loyers » [loss of rent] (owner); construction-insurance premium | 12 | If owner of the walls. |
| **Policyholder's loss-assessor fees** | « nous vous remboursons, sur justificatif, les honoraires de l'expert que vous aurez choisi » ; maximum « 10 % de l'indemnité […] 40 000 € par sinistre » | 69 | **Separate « Honoraires d'expert » [loss-assessor fees] cover**: the policyholder's loss assessor funded up to 10% / €40,000. Check in the CP that it is taken out. |
| BI loss adjustment | « Les honoraires de l'expert choisi par vous* vous* seront remboursés selon les modalités […] « honoraires d'expert » si vous l'avez souscrite. » | 41 | Same for business-interruption disputes. |
| Loss adjustment — general rule | « chacune des parties peut choisir un expert […] Chaque partie paie les honoraires de son expert et la moitié de ceux du troisième. » | 85 | Without the option, the policyholder's loss assessor is at your expense. |
| Underinsurance averaging | « La règle proportionnelle de capitaux […] n'est pas applicable au présent contrat. » | 85 | No reduction for underinsurance of sums insured (but it does exist for turnover/gross margin in BI, p. 44). |
| Goods held in custody | Covered « dans la mesure où ils ne sont pas assurés par leur propriétaire » [insofar as they are not insured by their owner] (insurance on behalf of others) | 85 | Stolen customers' goods: claimable. |
| Replacement-as-new equipment | « votre* matériel* de moins de 3 ans est indemnisé au prix du neuf » (« valeur de rééquipement à neuf » [re-equipment-as-new value] option) | 88 | Option to be checked; « PLUS » formula: new value up to 6 years. |
| Re-equipment as new | Equipment 3 to 10 years old: new value less depreciation, « majoré de 33 % » [increased by 33%]; invoices « dans les 2 ans » [within 2 years] | 89 | Buy back within 2 years. |
| Equipment depreciation | Minimum « 10 % » per year, maximum « 50 % » or « 80 % » depending on the case | 88 | Challenge excessive depreciation rates. |
| Ancillary equipment costs | Depreciation « ne s'applique pas sur les frais d'emballages, de transport, dépose, pose, essai, installation » | 88 | Installation costs reimbursed **without depreciation**. |
| Buildings / fittings | 2nd indemnity = depreciation « limitée […] au quart de la valeur de réparation » [limited to a quarter of the repair value] if works within 2 years, same catchment area | 86 | Rebuilding within 2 years = recovering part of the depreciation. |
| Stock | « Prix d'achat au dernier cours précédant le sinistre*, frais de transport et de manutention compris » ; sold but not delivered: « Prix de vente convenu » [agreed selling price] | 90 | Stolen **orders already sold** are indemnified at **selling price**. |
| Records / data | Reconstitution cost, against invoices « dans les deux ans » [within two years] | 90 | Reconstitution of accounts and customer files. |
| BI — triggers | Damage covered by « Incendie* et risques annexes… » (including riots) **and** « votre* assurance Vol, vandalisme* » → « Pertes d'exploitation après vol, vandalisme* » | 41 | BI option to be checked for each type of event taken out. |
| BI — denial of access | Property damage « à moins de 1 000 mètres » [within 1,000 metres] that « auraient été couverts au titre de votre* assurance Incendie* et risques annexes » | 42 | **Argument to put forward**: since riots are an event of the Fire and related risks cover, damage within 1 km could trigger BI even if the shop is intact. Only the terrorism exclusion is explicit (p. 43). Contestable wording: to be confirmed with the loss assessor. |
| BI — formulas | Flat rate: daily amount × days (max « 365 jours »); actual basis: loss of gross margin + additional expenses − saved costs | 43-44 | Up to 1 year on the flat-rate basis. |
| BI — declared-turnover trap | If actual turnover exceeds declared turnover by more than 20%: indemnity reduced (premium paid / premium due) | 44 | Check the declared turnover in the CP. |
| BI — after theft | Excluded: BI resulting « d'un vol des valeurs* » or « d'une agression* » | 43 | BI after looting of **stock** OK, BI after theft of the till not. |
| Goodwill value | Total/partial loss following an event of « Incendie* et risques annexes… » | 47 | Riot = event of this cover: a burnt or ransacked shop that cannot reopen → goodwill indemnified. |
| Notification | Theft: « 2 jours ouvrés » ; others: « 5 jours ouvrés » ; authorities: « dans les 2 jours » for theft, vandalism | 81 | **Police report within 2 days**. |
| Payment deadline | Theft: « Au plus tôt 30 jours après la date de déclaration du sinistre* » ; other losses: « Au plus tard 30 jours après la date : - d'accord entre les parties » | 92 | Payment no later than 30 days after agreement: chase from D+30. |
| Statement of loss | « nous* fournir, dans un délai de 30 jours, un état des pertes […] certifié sincère et véritable » | 81 | **30-day deadline** often forgotten: the agent must produce it. |
| Police report | « aviser immédiatement les autorités locales de police ou de gendarmerie et y déposer une plainte » | 82 | Obligation. |
| Recovered property | Before indemnification: take back recovered property within 30 days; the insurer pays « les frais nécessaires à cette récupération » | 82 | Recovery costs claimable. |
| Forfeiture | Delay: forfeiture « si nous* établissons que le retard nous* a causé un préjudice » ; false declaration: forfeiture | 82 | The burden of proving prejudice lies with the insurer. |
| Liability exclusion | Excluded under liability: damage « par des émeutes, mouvements populaires » | 71 | No impact on damage to own property. |

---

## 3. Hiscox — Conventions Spéciales Multirisques Dommages aux Biens Professionnels n° MRP0623

- Source: hiscox.fr (broker area). Local: `contrats/pdf/HISCOX_MRP_CS_DommagesBiens_MRP0623.pdf`. Supplemented by the PRO by Hiscox CG MRP0918 (2018) and the IPID MRP0820.

| Topic | What the policy says (short verbatim quote) | Page | What this means for the looted merchant |
|---|---|---|---|
| Riots — cover | « Les dommages matériels causés par les émeutes et les mouvements populaires. » | 8 | Riot cover included (property damage). |
| Riots — interplay with the State | « s'exerce à défaut ou en complément de l'article L. 2216-3 du Code général des collectivités territoriales relatif à la responsabilité de l'État » | 8 | **Recourse against the State** for what the insurer does not pay (deductible, BI…). Rare to see it written into a policy. |
| Riots — general exclusion | Exclusion 8 « Conflits sociaux et mouvements populaires » ; the riot cover derogates from it only « partielle[ment] » [partially] | 8, 28 | Only **property damage** is brought back in; financial losses without property damage remain excluded. |
| Theft and vandalism — police report | Subject to « que l'assuré dépose immédiatement une plainte, qui ne pourra être retirée qu'avec l'accord écrit préalable de l'assureur » | 9 | Immediate police report mandatory. |
| Theft — conditions | « par effraction ou escalade ayant laissé des traces apparentes, par usage de fausses clés, par introduction clandestine, avec violence » | 9 | Photograph the **visible traces**. |
| Theft — damage | « Sont également couvertes les détériorations mobilières/immobilières […] consécutives à un vol ou une tentative de vol » | 10 | Forced door/shutter covered under theft. |
| Theft — exclusions | Excluded: thefts « pendant une occupation […] dans le cadre d'un conflit du travail », « après abandon des bâtiments à la suite d'évacuation ou de réquisition », property « en plein air » [in the open air] | 9-10 | If the police ordered an evacuation: risk of exclusion to be challenged. |
| Till theft | Cash in till drawer: theft « par effraction ou enlèvement desdits tiroirs-caisses » or with violence | 10 | Till ripped out during looting: covered. |
| Vandalism | « Les dommages matériels résultant d'actes de vandalisme. » | 11 | Covered. |
| Glass breakage | « bris accidentels de verres, glaces et vitres incorporés aux bâtiments assurés, des enseignes lumineuses » | 9 | Shop window + illuminated sign. |
| Payment / interest | Provisional payment within « 2 (deux) mois » and indemnity within « 3 (trois) mois » after the estimated statement; beyond that, interest at the statutory rate (> €4,000) | 8 | These deadlines are in the riots/natural-disaster clause: **claim late-payment interest**. Settlement within 10/15 business days after agreement, otherwise interest (p. 15). |
| Buildings — depreciation | Depreciation « minimum de 10 (dix) % par an sans pouvoir excéder 70 (soixante-dix) % » ; balance paid if works accepted within 24 months | 12 | Depreciation buy-back if works within 24 months. |
| Buildings not rebuilt | « valeur vénale des bâtiments sinistrés majorée de 20 (vingt) % » | 13 | For owners of the walls. |
| Equipment / furniture | Bought new « au cours de l'année précédant » [in the year preceding] the loss: « valeur de remplacement à neuf » | 13 | Equipment less than one year old: replacement-as-new value. |
| Stock | Current purchase price + transport; already sold but not delivered: « prix de vente convenu, déduction faite des frais épargnés […] et de la marge » | 14 | Stolen customer orders. |
| Theft by clandestine entry | « circonstancié » [detailed] police report: « date et créneau horaire précis ; description des faits […] avis de témoins » | 14 | Police-report template to follow to the letter. |
| **Policyholder's loss-assessor fees** | « remboursement des frais et honoraires de tout autre expert que vous aurez mandaté […] dans la limite de 5 (cinq) % de l'indemnité valorisée par notre expert. » | 14 | Policyholder's loss assessor funded up to **5%** (« Frais et pertes additionnels » [additional expenses and losses] cover, to be taken out). |
| Third expert | « En cas de divergence […] ils seront départagés par un troisième expert […] par voie judiciaire. » | 14 | Joint loss-adjustment procedure. |
| BI — triggers | Loss of gross margin after damage « au titre des événements Incendie et risques annexes, Événements climatiques, Catastrophes naturelles, Dégât des eaux ou Attentats » | 15 | Neither **riots** nor **theft/vandalism** are listed: BI **absent** after looting (unless fire). |
| Additional operating expenses | Relocation rent, temporary repairs, out-of-hours works, express transport, reconstitution of records | 16 | Same triggers as BI (not riots). |
| **Additional expenses and losses** | « directement consécutifs à un dommage matériel garanti au titre de la 2e partie, section 1 « Dommages Matériels » » | 16 | Triggered by **any** covered property damage, **riots and vandalism included**. |
| FPA — loss of use | « tout ou partie de la valeur locative des bâtiments assurés et occupés par l'assuré en cas d'impossibilité […] de les utiliser » | 17 | Rent for an unusable shop. |
| FPA — finance lease | « le montant des annuités de crédit-bail […] qui […] resteraient à la charge de l'assuré » | 17 | Lease on destroyed equipment. |
| FPA — tenant's fit-out | Loss « des aménagements qu'il avait réalisés […] devenus la propriété du bailleur » | 17 | Tenant's works lost. |
| FPA — cleaning, debris removal, fees | « frais de nettoyage, déblai, démolition » ; « honoraires des architectes […] décorateurs » ; compliance upgrade | 17 | Cleaning after ransacking, designer. |
| FPA — boarding-up | « les frais de bâchage, de clôture provisoire et de gardiennage » | 17 | Boards and security guard. |
| **FPA — cash flow** | « intérêts des emprunts […] jusqu'au versement de l'indemnité » ; « le montant des découverts bancaires » | 17 | **Bank charges and overdrafts** while waiting: rarely claimed. |
| **FPA — suppliers** | « le coût d'achat des matières premières et autres approvisionnements que l'assuré serait contraint de continuer à régler » ; « frais d'annulation de commande » | 17 | Supplier orders paid despite closure, cancellation penalties. |
| Goodwill value | Triggers: Fire, weather, natural disaster, water damage; excluded in risk-prevention-plan zones | 18 | Only if the shop was **set on fire**. |
| Denial of access / loss of custom | Same triggers (no riots) | 18-19 | **Absent** for riots. |
| Underinsurance averaging | « nous renonçons à appliquer la règle proportionnelle » | 32 | No reduction for underinsurance. |
| Notification | Damage: « 5 (cinq) jours » ; theft: « 48 (quarante-huit) heures » | 31-32 | **48 h for theft** (shorter than MAAF/MMA). |
| Police report | « déposer perte dans les 72 (soixante-douze) heures […] et nous communiquer la copie de votre dépôt de plainte » | 32 | Police report within 72 h. |
| Forfeiture | Delay: forfeiture « si ce manquement nous a causé un préjudice » ; false declaration: total forfeiture | 32 | — |
| Assistance | Security guarding by a security guard « pour une durée de 72 (soixante-douze) heures maximums » | 47 | Free. |
| CG 2018 (MRP0918) | Policyholder's loss assessor: « dans la limite de cinq (5) % de l'indemnité initialement valorisée par notre expert » ; exclusion « émeutes et mouvements populaires » (war and similar) with riot cover as a derogation | 27, 45, 22 | Same logic in the earlier version. |

---

## 4. Pacifica (Crédit Agricole) — IPID Multirisque Professionnelle 7197A.36 (2020.12)

- Information document of only 3 pages (not the complete CG, which were not found). To be used as an **indication** to be confirmed in the client's CG and CP.

| Topic | What the document says (short verbatim quote) | Page | What this means for the looted merchant |
|---|---|---|---|
| Riots | « Attentats, actes de terrorisme, émeutes, mouvements populaires » (standard cover) | 1 | Included in all policies with premises. |
| Theft and vandalism | « Vol et vandalisme : valeur du capital vol de 2 000 € à 300 000 € » | 1 | Ceiling per the CP. |
| Signs and blinds | « à concurrence de 20 000 € » | 1 | Torn-off sign. |
| **Indirect losses** | « frais annexes justifiés à la suite d'un sinistre garanti : frais réels limités à 10 % de l'indemnité versée » | 1 | +10% against supporting documents. |
| Demolition / debris removal | « 25 % de l'indemnité versée pour les dommages aux biens » | 1 | Debris removal. |
| **Loan instalments** | « jusqu'à 12 mensualités du prêt en cours limitées à 500 € par mois » (property, renovation or goodwill-purchase loan) | 1 | **Up to €6,000** of instalment reimbursement: rarely claimed. |
| Tenant's investments | « Pertes des investissements réalisés par un locataire : à concurrence des frais réels. » | 1 | Lost fit-out. |
| Temporary premises | Cover at both addresses in case of « locaux provisoires suite à sinistre […] limitée à 2 ans » | 1 | Stock moved to temporary premises: insured. |
| Re-equipment-as-new option | « coût de remplacement dans la limite du rééquipement à neuf » | 1 | To be checked in the CP. |
| Graffiti | Excluded: « Les graffitis, inscriptions, salissures, affichages à l'extérieur des locaux. » | 1 | Exterior tags **not** covered (unlike MAAF). |
| Prevention | « Le non-respect des mesures de prévention exigées entraîne une prise en charge à hauteur de 70 % » | 1 | 30% reduction, not outright refusal. |
| Deductibles | General: €150 to €1,200; glass breakage and signs: deductible « réduite de moitié » [halved] | 1 | — |
| **BI — denial of access due to riot** | « une impossibilité d'accès au local assuré du fait d'une émeute ou d'un mouvement populaire : […] indemnité forfaitaire journalière de 15 € à 8 000 € » | 2 | **The only policy in the batch covering forced closure without damage**, if the option is taken out. |
| Riot BI — limits | « durée d'indemnisation de 7 jours consécutifs ou non par année d'assurance et un seuil d'intervention de 3 jours » | 2 | At most 7 days, after 3 days of closure. |
| BI — direct damage | « durée d'indemnisation de 18 mois consécutifs et un seuil d'intervention de 3 jours » | 2 | Looted shop: BI up to 18 months. |
| BI — exclusion | Excluded: losses « qui résulteraient d'une grève, d'un lock-out, d'un mouvement de foule dans violence volontaire. » (text as is; « dans » is probably a typo for « sans » [without]) | 2 | If read as « sans »: only a non-violent crowd is excluded, and the violent riots of 17-18 October remain covered. To be confirmed in the CG. |
| Goodwill value | Loss « en cas d'impossibilité complète et définitive de continuer l'exploitation » — ceiling €10,000 to €3,000,000 | 2 | — |
| Notification | Deadlines not quantified in the IPID (« dans les conditions et délais impartis » [within the conditions and deadlines set]) | 3 | **Absent** from the IPID: to be read in the CG. |
| Policyholder's loss-assessor fees | Not mentioned | — | **Absent** from the IPID. |

---

## 5. Cross-reference table — « Postes souvent oubliés et récupérables » [often-forgotten recoverable items]

Legend: ✅ = clause present (page) · ❌ = absent or excluded · ? = not verifiable in the available document (IPID only).

| Recoverable item | MAAF 11031-01/26 | MMA PRO-PME 352p | Hiscox MRP0623 | Pacifica (IPID) | Typical ceiling noted |
|---|---|---|---|---|---|
| **Policyholder's loss-assessor fees** | ❌ each pays its own expert (p78); excluded from indirect losses (p25) | ✅ « Honoraires d'expert » cover (p69) | ✅ via FPA (p14) | ? | MMA: 10% of the indemnity, max €40,000; Hiscox: 5% of the indemnity quantified by the insurer's expert |
| **Flat-rate indirect losses** | ✅ (p25) | ❌ no flat rate (itemised expenses and losses) | ❌ (itemised FPA instead) | ✅ (p1) | 10% of the property indemnity (MAAF, Pacifica) |
| Temporary boarding-up / security guarding | ✅ (p14, 19, 23) | ✅ (p12, 28, 31) | ✅ (p17) | ? | MAAF €6,600; others: CP |
| Security guarding via assistance (free) | ✅ 72 h (p58) | ✅ 120 h (p69) | ✅ 72 h (p47) | ? | 72 to 120 hours |
| Tag / graffiti removal | ✅ (p23) | ✅ (« graffiti » in the definition of vandalism, p5) | ✅ vandalism (p11) | ❌ excluded outside (p1) | CP |
| Metal shutter / means of closure | ✅ (p14) | ✅ (p28) | ✅ damage after theft (p10) | ? | CP |
| Blind / awning / sign | ✅ (p14) | ✅ signs (p31) | ✅ illuminated signs (p9) | ✅ (p1) | Pacifica €20,000 |
| Lock replacement | ✅ (p19) | ✅ means of closure (p28) | ✅ damage (p10) | ? | MAAF €3,000 |
| Demolition / debris removal / cleaning | ✅ (p24) | ✅ (p12) | ✅ (p17) | ✅ (p1) | Pacifica 25%; others: actual costs or CP |
| Architect / designer fees | ✅ (p25) | ✅ (p12) | ✅ (p17) | ? | MAAF 5% of the building indemnity |
| Compliance upgrade | ✅ (p25) | ✅ (p12) | ✅ (p17) | ? | MAAF €500/m² |
| Storage / removal | ✅ (p25) | ✅ (p12) | ? | ? | MAAF €6,400 for storage |
| Rehousing / temporary premises | ✅ 2 years (p25) | ✅ (p12) | ✅ FSE (p16, restricted triggers) | ✅ 2 years (p1) | — |
| Loss of use (rent on unusable premises) | ❌ absent as such | ✅ (p12) | ✅ (p17) | ? | — |
| Tenant's fit-out lost | ❌ absent | ✅ (p11) | ✅ (p17) | ✅ (p1) | Actual costs (Pacifica) |
| Outstanding finance lease / leasing | ✅ equipment breakdown option (p23) | ✅ financial loss, financing contract (p89) | ✅ annual instalments (p17) | ? | CP |
| Loan instalments during works | ❌ | ❌ | ❌ | ✅ (p1) | 12 × €500 |
| Loan interest / bank overdraft | ❌ | ✅ VAT-related interest only (p12) | ✅ (p17) | ❌ | — |
| Supplier purchases still payable / order cancellation | ❌ | ❌ | ✅ (p17) | ❌ | — |
| Goods sold but not delivered at selling price | ❌ (purchase price, p79) | ✅ (p90) | ✅ margin deducted (p14) | ? | — |
| Goods held in custody (customers, consignment) | ✅ (p19, 22) | ✅ (p28, 85) | ? | ? | CP |
| Cash / till | ✅ 10% of contents, max €16,000 (p15) | ✅ valuables (p28) | ✅ till drawer (p10) | ❌ outside a locked cabinet (p1) | MAAF €16,000 |
| Depreciation buy-back (replacement within 2 years) | ✅ 33% max (p78-79) | ✅ +33% or ¼ of the value (p86, 89) | ✅ balance within 24 months (p12) | ✅ option (p1) | — |
| Replacement-as-new for recent equipment | ✅ IT < 2 years (p79) | ✅ option < 3 years (< 6 years in PLUS) (p88-89) | ✅ < 1 year (p13) | ✅ option (p1) | — |
| Installation/transport costs without depreciation | ? | ✅ (p88) | ✅ ancillary costs (p17) | ? | — |
| Reconstitution of records / data | ❌ excluded after theft (p21, 23) | ✅ (p90) | ✅ FSE (p16) | ? | — |
| BI after looting (direct damage) | ✅ flat rate, 60 business days (p43) | ✅ « PE après vol, vandalisme » option (p41) | ❌ (p15) | ✅ 18 months (p2) | — |
| BI for forced closure **without damage** (surrounding riot) | ❌ excluded (p43) | ? possible argument (< 1,000 m, p42) | ❌ (p18) | ✅ 7 days, flat rate €15 to €8,000/day (p2) | — |
| Additional operating expenses | ✅ (p41) | ✅ (p12, 43-44) | ✅ (p16, excluding riots) | ✅ (p2) | — |
| Loss of goodwill value | ✅ if fire (p43) | ✅ fire and related risks, including riots (p47) | ✅ if fire (p18) | ✅ (p2) | Pacifica €10k to €3M |
| Insurer's late-payment interest | ❌ neither deadline nor interest in art. 38 (p80) | ❌ no interest, but payment no later than 30 days after agreement (p92) | ✅ statutory rate > €4,000 (p8, 15) | ? | — |
| Single deductible when covers are combined | ✅ highest only (p80) | ? not found | ? not found | ? | — |
| Recourse against the State (L.2216-3 CGCT) mentioned | ❌ | ❌ | ✅ (p8) | ❌ | Outside the policy |
| No underinsurance averaging | ✅ (p78) | ✅ (p85) | ✅ (p32) | ? | — |

### Mandatory deadlines (for the agent)

| | MAAF | MMA | Hiscox | Pacifica (IPID) |
|---|---|---|---|---|
| Notification of theft / vandalism | 2 business days (p76) | 2 business days (p81) | 48 hours for theft (p32) | Not quantified |
| Notification of other damage | 5 business days | 5 business days | 5 days | Not quantified |
| Police report | « au plus vite » [as soon as possible] (p76) | To the authorities within 2 days (p81) | Within 72 h (p32), immediate for theft and vandalism (p9) | Not quantified |
| Statement of loss | « dès que possible » [as soon as possible] (p76) | **30 days** (p81) | Basis for payment deadlines (p8) | Not quantified |
| Replacement for depreciation buy-back | 2 years | 2 years | 24 months | Not quantified |

### Key takeaways for the pitch
1. The policy only pays what is **claimed and substantiated**: each policy contains 10 to 20 ancillary items (boarding-up, cleaning, fees, loss of use, interest, recoverable depreciation) that the merchant is unaware of.
2. Clauses **differ strongly** from one policy to another. Examples: policyholder's loss assessor funded at MMA (10%, €40k cap) and Hiscox (5%) but not at MAAF; closure without damage covered only at Pacifica (7 days); tags covered at MAAF but excluded outside at Pacifica. The agent must therefore read **the client's policy**.
3. **Deadlines are short** (48 h to 2 business days, 30 days for the statement of loss at MMA). The agent must produce a checklist from D+0.
