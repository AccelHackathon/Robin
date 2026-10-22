# Contexte — Agent autonome de sinistre pour petites entreprises

Mis à jour le **22 octobre 2026**, heure de Paris.

Ce document sert de contexte pour reprendre la conception et construire le produit dans une autre session. Il consolide les échanges, le brief du hackathon, le schéma manuscrit IMG_1211 et la recherche officielle Aiven du 22 octobre 2026. Il distingue les décisions de Mathis, les recommandations et les capacités effectivement vérifiées. **Le produit n’est pas encore implémenté dans cet espace de travail ; les accès Aiven et fournisseurs restent à fournir/configurer.**

## 1. Objectif et vision

Construire un assistant qui prend en charge le dossier d’assurance d’une petite entreprise après un sinistre. L’expérience comporte **deux blocs : un site pour créer et configurer son compte, puis WhatsApp pour utiliser l’agent au quotidien**.

Sur le site, le commerçant renseigne son téléphone, dépose ses contrats et documents, décrit son entreprise et son historique, puis donne un mandat. Un chatbot demande les informations manquantes. Après l’onboarding, le service lui adresse un message de bienvenue sur WhatsApp.

Le dirigeant explique les faits, envoie des photos, des messages vocaux et ses documents. L’agent lit le contrat, identifie les démarches pertinentes, collecte les preuves manquantes, contacte l’assureur, constitue la demande, la transmet et suit les échanges.

L’objectif est de **constituer la demande d’indemnisation la plus complète et la mieux justifiée possible au regard des dommages réels et du contrat**. Un montant demandé n’est pas un remboursement obtenu. Aucune promesse de remboursement garanti n’a été retenue.

Exemple d’entrée : « On a cassé la vitrine de ma boutique. Voici les photos. Que dois-je faire ? »

Promesse de travail proposée : **“Your policy, your evidence, your claim — handled by your agent.”** Aucun nom de marque n’a été arrêté.

Le contexte initial évoque notamment les commerces dégradés ou vandalisés en marge de manifestations. Cela constitue un exemple d’usage, pas une limitation définitive du produit.

**Hook du pitch (actualité, « why now ») :**
- Les **17 et 18 octobre 2026**, environ **3 000 commerces** ont été dégradés ou pillés en France. Ce chiffre est provisoire ; il est cité par le Premier ministre et par Serge Papin ([Public Sénat, 19/10](https://www.publicsenat.fr/actualites/economie/pillages-au-moins-3-000-commerces-touchees-pour-des-centaines-de-millions-deuros-de-degats)), et confirmé par Bercy ([communiqué du 20/10](https://presse.economie.gouv.fr/le-gouvernement-met-en-place-des-mesures-de-soutien-aux-commerces-touches-par-les-degradations-du-samedi-17-et-dimanche-18-octobre-2026/)).
- Les dommages assurés sont estimés entre **1 et 1,2 Md€** ([Morningstar DBRS via Reinsurance News](https://www.reinsurancene.ws/france-riots-put-srcc-accumulation-risk-in-focus-for-re-insurers-morningstar-dbrs/)).
- Comme précédent, les émeutes de 2023 ont donné lieu à 16 400 sinistres pour 793 M€ ([Sénat](https://www.senat.fr/rap/r23-521/r23-52117.html)).
- Le marché ne s’arrête pas aux émeutes : environ 110 sinistres pour 1 000 contrats de commerçants par an ([France Assureurs 2024](https://www.franceassureurs.fr/wp-content/uploads/lassurance-de-dommages-aux-biens-des-professionnels-en-2024-1.pdf)).

## 2. Décisions exprimées par Mathis

### Utilisateurs et périmètre

- Viser les **petites entreprises en France**, en priorité les petits commerçants.
- Le dirigeant est l’utilisateur envisagé.
- Ne pas imposer de seuil commercial de montant ou de catégorie de sinistre à ce stade.
- Les problèmes importants semblent particulièrement intéressants à Mathis.
- Un cas précis peut illustrer la démonstration sans limiter l’ambition commerciale du service.

### Autonomie

- Le produit doit être **réellement autonome**, sans équipe humaine qui traite les dossiers en coulisses dans le fonctionnement envisagé.
- L’agent doit prendre l’initiative des recherches, demandes de pièces, appels, transmissions et relances.
- Ne pas imposer une relecture humaine de chaque action intermédiaire.
- Il peut demander des faits, documents ou photos au commerçant lorsque les informations manquent.
- Lorsqu’une offre d’indemnisation arrive, il **notifie le commerçant**, l’explique et peut formuler une recommandation.
- **L’acceptation d’une offre reste une décision du commerçant.**
- Aucun mécanisme systématique de recours à un expert humain interne n’a été accepté : Mathis privilégie l’indépendance de l’agent.
- Cela ne dispense pas de traiter les incertitudes, limites des outils et situations bloquées. Le comportement exact dans ces cas reste à concevoir.

### Interface et récupération des documents

- **Décision la plus récente : un compte sur notre site et un onboarding web avant le passage à WhatsApp.**
- WhatsApp pour les échanges, photos, documents et vocaux après cette configuration.
- Le commerçant peut transmettre son contrat dans la conversation.
- S’il ne le retrouve pas, l’agent doit pouvoir en demander une copie à l’assureur, dans un cadre autorisé.
- Une connexion à **l’espace client de l’assureur** a aussi été explorée. Elle reste une piste distincte du compte créé sur notre propre site, désormais confirmé.
- La récupération des documents depuis cet espace dépend d’un mécanisme de délégation accepté et techniquement disponible ; il n’est pas vérifié.
- Une autorisation de représentation et un accès technique au compte sont deux sujets distincts.
- Une page de suivi accessible par lien depuis WhatsApp a été **recommandée par l’assistant, pas encore choisie par Mathis**.

Le schéma joint montre également un retour des outils vers la mémoire issue de l’onboarding et une intervention du commerçant au moment de la proposition. Il confirme la continuité entre les deux blocs, pas deux assistants isolés.

### Langue du produit

- **Décision explicite de Mathis : le bot parle anglais.** Les réponses du chatbot d’onboarding et les messages WhatsApp sont donc en anglais. L’agent utilise également l’anglais par défaut dans ses échanges générés ; une adaptation au français d’un interlocuteur assureur resterait à préciser.
- Le contexte de travail et les échanges avec Mathis restent en français, concrets et avec peu de jargon.
- Les contrats et pièces françaises conservent leur langue d’origine et leurs citations exactes ; une explication en anglais ne remplace pas la source.
- La langue de tous les éléments statiques du site n’a pas été arrêtée séparément ; ne pas confondre ce point avec la langue du bot.

### Appels

- L’agent vocal utiliserait **ElevenLabs** pour contacter l’assurance.
- Les appels doivent clarifier les questions utiles au dossier : pièces attendues, procédure, point contractuel ou blocage.
- Les réponses obtenues doivent alimenter la mémoire du sinistre et modifier les prochaines actions lorsque nécessaire.
- Aucun appel réel à un assureur n’a été effectué ou testé.
- **Langue des appels : anglais**, comme le reste du bot. L’appel de démo se fait en anglais, ce qui permet au jury de le comprendre.

### Rémunération — provisoire

- Mathis envisage un **pourcentage au moment de l’indemnisation**.
- Taux, base de calcul, plafonds et modalités restent « to be determined ».
- Ne pas supposer que le service encaisserait directement les fonds de l’assurance.
- Mathis a explicitement demandé de **se concentrer sur le produit plutôt que sur le business**. Ne pas reprendre une longue interview sur prix, acquisition ou distribution sans demande.

## 3. Bloc 1 — Création du compte et onboarding sur le site

### Parcours demandé

1. **Créer son compte.** Accès au site, inscription/connexion et reprise possible d’un onboarding interrompu.
2. **Configurer son numéro.** Renseigner le téléphone qui sera utilisé sur WhatsApp et relier ce numéro au bon compte client.
3. **Déposer ce qu’on possède.** Contrats, conditions particulières, avenants, constats éventuels et historique utile. Le schéma manuscrit mentionne les contrats ; Mathis évoque aussi les constats. Conserver les deux types.
4. **Renseigner son profil.** Persona métier, entreprise, interlocuteur et contexte du commerce.
5. **Donner un mandat.** Autoriser le service à accomplir les démarches définies et conserver la preuve de cette autorisation.
6. **Compléter avec le chatbot.** L’agent lit les documents et demande uniquement les informations encore nécessaires.
7. **Passer à WhatsApp.** Le compte est enregistré, la mémoire initiale est disponible et un message de bienvenue est envoyé lorsque le canal est opérationnel.

### Interprétation du profil/persona — recommandation à adapter

Le persona désigne ici un **profil métier utile au dossier**, pas des traits psychologiques inventés :

- identité et qualité du représentant ;
- entreprise et activité, SIREN/SIRET lorsque pertinent ;
- adresse des locaux et statut locataire/propriétaire ;
- assureur, courtier et contacts déjà connus ;
- situation fiscale utile au chiffrage, notamment TVA, lorsqu’elle est établie ;
- préférences pratiques de contact et historique de sinistres ou démarches existantes.

Ces champs constituent un modèle proposé. Ne pas tous les imposer avant de permettre l’inscription. Une donnée présente dans un document n’a pas à être retapée, mais une extraction incertaine doit être confirmée.

### Ce que fait le chatbot d’onboarding

- Identifier et classer les documents déposés ; conserver les originaux.
- Extraire les informations avec leurs sources et leur degré de confirmation.
- Repérer une condition particulière absente, un document ancien ou un avenant applicable.
- Poser une question ciblée en anglais : “Is this the insured business address?”, “Could you upload the policy schedule showing your selected cover?”
- Demander les informations de représentation nécessaires au mandat.
- Ne pas déduire qu’une option n’est pas souscrite parce que sa page n’a pas encore été reçue.
- Conserver les documents manquants comme des tâches ; un compte peut être créé avec un profil encore incomplet.

La création d’un compte doit pouvoir préparer un usage futur. Si un sinistre est déjà en cours, ouvrir sa fiche et reprendre la procédure sans attendre que tout l’historique soit complété. Ne pas retarder une déclaration urgente pour terminer l’onboarding.

### Mandat et consentements

Le mandat doit désigner l’entité qui exploite le service et la personne habilitée à donner pouvoir pour l’entreprise. Périmètre proposé : obtenir des documents, transmettre les faits confirmés et les pièces, contacter assureur/courtier, demander un statut ou un complément et relancer.

Conserver version, périmètre, signataire, qualité déclarée/vérifiée, date, preuve d’acceptation et révocation. Le mécanisme de signature reste à choisir. Ne pas présenter la simple ouverture du compte comme une autorisation générale.

L’acceptation d’une offre, une transaction ou une renonciation ne découlent pas du mandat opérationnel envisagé. Le commerçant garde la décision sur la proposition. La qualification juridique du service commercial et les pouvoirs effectivement acceptés par l’assureur restent à valider.

Séparer **mandat de représentation**, **accord pour recevoir des communications WhatsApp** et **information sur les traitements de données**. Un seul bouton indistinct ne décrit pas correctement ces finalités.

### Message de bienvenue et liaison au numéro

Texte proposé, pas encore envoyé :

> Hi! Your account is ready. You can message us here whenever you need help, and send photos or documents about your claim.

Le passage depuis le site constitue un envoi initié par le service : prévoir l’accord du destinataire et un modèle approuvé. Une alternative est un bouton vers WhatsApp faisant envoyer le premier message par le commerçant. La fenêtre de service de vingt-quatre heures démarre avec le message utilisateur ; la seule création du compte web ne l’ouvre pas. [Politique WhatsApp](https://whatsappbusiness.com/policy/).

Recommandation d’implémentation : vérifier la possession du numéro, le normaliser et associer l’identifiant de conversation WhatsApp à l’entreprise authentifiée. Ne pas fusionner des dossiers sur la seule saisie d’un numéro non vérifié.

Distinguer **compte créé**, **profil partiellement complété**, **mandat enregistré**, **WhatsApp relié**, **bienvenue envoyée/livrée/échouée**. Si l’envoi échoue, le compte reste créé ; le site propose une reprise au lieu d’afficher une réussite fictive.

### Résultat attendu à la fin du bloc 1

Une identité client durable, un profil d’entreprise, un numéro relié, les documents reçus et leurs versions, le mandat, les informations manquantes et l’historique constituent la mémoire initiale. Le second bloc réutilise cette mémoire dès le premier message.

## 4. Bloc 2 — Agent WhatsApp, outils et mémoire client

### Expérience utilisateur

Le commerçant écrit naturellement, envoie un vocal, des photos ou un document. L’agent retrouve l’entreprise et le dossier concernés, lit leur état actuel, choisit l’action pertinente, utilise ses outils et informe le commerçant du résultat ou du blocage.

Le flux recommandé est : **événement entrant → lecture de la mémoire → analyse → action → résultat vérifié → mise à jour de la mémoire → prochaine étape**. Une réponse reçue par mail ou après un appel doit pouvoir déclencher la suite sans nouveau prompt du commerçant.

### Outils demandés

- **Messages WhatsApp :** recevoir et envoyer, récupérer les médias, identifier la conversation, conserver les accusés et échecs.
- **Emails :** préparer et envoyer une déclaration, une demande de document, des justificatifs ou une relance ; recevoir les réponses et les rattacher au bon dossier. **Fournisseur retenu : AgentMail** (voir §13). Ne pas supposer un accès à la boîte personnelle du commerçant.
- **Téléphone :** appeler via ElevenLabs et une téléphonie compatible, naviguer dans un standard si possible, demander des précisions et récupérer un résultat structuré. Une transcription n’est pas une preuve que le dossier a été ouvert.
- **Mémoire client :** lire et mettre à jour les faits, contrats, pièces, échanges, actions, offres et règlements dans la durée.

Le nom « mémoire client » est validé comme concept. Des fonctions telles que `get_customer_context`, `store_evidence`, `send_email`, `start_phone_call` ou `schedule_followup` seraient des interfaces techniques proposées, pas des outils déjà disponibles.

### Ce qui est mémorisé

**Au niveau de l’entreprise :** profil, représentants, numéros vérifiés, mandats, contacts, contrats et préférences confirmées.

**Au niveau du sinistre :** faits connus ou présumés, pièces et versions, dommages, état des pertes, règles utilisées, communications, échéances, actions effectuées, tâches en attente et propositions.

Une correction ne doit pas effacer silencieusement la valeur précédente. Une réponse orale garde sa provenance ; une offre et un versement gardent leurs preuves propres. Le chatbot web, WhatsApp et les outils utilisent le même dossier, avec séparation entre clients et entre sinistres.

### Autonomie et intervention du commerçant

L’agent prend en charge les démarches courantes prévues dans son mandat, sans validation humaine systématique. Il sollicite le commerçant lorsqu’une information ou une preuve manque, lorsqu’un accès exige son intervention ou lorsqu’une décision dépasse les pouvoirs délégués.

Lors de l’offre, il explique les montants, écarts et conditions. Le commerçant décide d’accepter, demander une précision ou contester. **Une absence de réponse n’est jamais une acceptation.** Après la décision autorisée, l’agent suit le paiement et les éventuels compléments.

### Parcours opérationnel du dossier

1. Identifier le sinistre et les urgences ; préserver les preuves.
2. Préparer et transmettre la déclaration initiale par un canal reconnu, sans attendre toutes les pièces.
3. Lire le jeu contractuel applicable et établir les garanties candidates.
4. Construire l’état des pertes : chaque poste relie une preuve, une clause, un calcul et une condition éventuelle.
5. Demander les informations manquantes et utiliser mail/téléphone pour résoudre une question précise.
6. Transmettre les compléments, conserver les accusés et suivre l’expertise éventuelle.
7. Présenter la proposition au commerçant pour décision.
8. Suivre acomptes, paiement direct au réparateur, indemnité reçue et complément conditionnel.

Les demandes, offres et fonds reçus sont des objets distincts. Une action n’est marquée effectuée que lorsque son résultat est constaté. Un refus, une attente ou une panne doivent rester visibles.

## 5. Accès et documents disponibles

- Aucun dossier réel complet de sinistre commercial n’a été fourni.
- **Un corpus de 12 conditions générales publiques réelles est disponible dans `data/contrats/txt/`** (détail et usage au §13.2) : Generali, AXA ×2, Allianz, Sogessur, Groupama, MAAF, MMA, Hiscox ×3, Pacifica. S’y ajoutent les fiches clauses par contrat (avec pages) et 3 cas chiffrés sourcés dans `data/research/`.
- Mathis peut essayer d’en obtenir un ; il a également demandé de rechercher les documents publics disponibles sur Internet.
- Un accès à une assurance personnelle/familiale a été évoqué. Le nom entendu « MAF » ou « MAAF » reste à confirmer.
- Un compte d’assurance de son entreprise existe peut-être sous l’accès du président. Aucun accès, contrat ou accord de test n’est confirmé.
- Ne pas déduire une autorisation de connexion, de collecte ou de publication à partir de cette simple évocation.
- Aucun identifiant n’a été fourni.
- Des conditions générales publiques et guides assureurs ont été trouvés. Les conditions particulières d’un assuré restent nécessaires pour déterminer ses garanties effectivement souscrites.
- Le schéma **IMG_1211.HEIC** a été lu : compte avec téléphone, contrats, persona et historique ; message WhatsApp ; outils boîte mail/mémoire client/téléphone ; intervention sur la proposition.
- Mathis prévoit de donner un accès Aiven par **API, MCP ou CLI** pour construire et déployer. Aucun de ces accès n’a été configuré pendant la rédaction de ce document.
- **Préférence technique la plus récente : utiliser l’API Aiven en priorité ; MCP et CLI restent des alternatives.**

## 6. Hackathon — dernier brief fourni par Mathis

**Future Founders: Data-Centric Agents — From Prompt to Production Data.** Hackathon Accel AI Innovate Paris, le **22 octobre 2026**.

Le dernier brief est plus précis que la page initialement discutée. Il demande :

- Un produit fonctionnel pour un utilisateur et un problème précis.
- Des agents qui raisonnent et agissent sur des données réelles, évolutives, parfois périmées ou contradictoires.
- Une couche de données centrale dans l’utilité du produit.
- **Déploiement de l’application sur Aiven Runtime** ; usage de ses services de données là où ils sont pertinents.
- Un parcours utilisateur complet de bout en bout.
- Une démonstration du flux de données : sources, stockage, circulation et effets sur les décisions.
- Une preuve mesurée : avant/après, benchmark ou comparaison avec une version naïve/sans données.
- Une slide indiquant utilisateur, raison d’être actuelle et piste pour les premiers utilisateurs.
- Des données partageables publiquement ; séparation explicite entre exécution en direct et scénarios enregistrés ou simulés.

### Les cinq critères de jugement

1. **Customer Problem & Product Value** : problème réel, utilisateur clair, adoption plausible.
2. **Agent Capability** : raisonnement multiétape, autonomie, collaboration ou apprentissage au-delà d’un appel unique au modèle.
3. **Data at the Core** : fraîcheur, volume pertinent, ancrage dans les sources et/ou mémoire réellement utiles.
4. **Evidence It Works** : résultat mesuré, par exemple exactitude, coût, latence, réussite ou temps.
5. **Execution & Pitch** : démonstration compréhensible et soignée, différence claire, chemin crédible vers les premiers utilisateurs.

Un **prix Aiven séparé** récompense le meilleur usage de sa plateforme. Le brief ne demande pas de multiplier artificiellement les services ni de réaliser toutes les pistes d’inspiration.

Le PDF fourni par Mathis, **Future Founder Challenge_ Data-Centric Agents (1) (1).pdf**, a été lu et confirme ces exigences, notamment Aiven Runtime, la comparaison mesurée et la distinction entre direct et scénario enregistré.

### Traduction des critères dans notre démonstration

- **Valeur :** un commerçant crée son compte, dépose ses pièces et reçoit un dossier utilisable et un suivi compréhensible.
- **Agent :** une réponse d’assurance ou une nouvelle preuve fait choisir et exécuter une nouvelle action, sans scénario caché piloté par le présentateur.
- **Données :** la mémoire créée sur le site est retrouvée sur WhatsApp ; version du contrat, pièces et historique modifient les conclusions.
- **Preuve :** mesurer les erreurs, doublons, questions répétées et contrôles résolus sur plusieurs variantes, avec une référence au même modèle et aux mêmes documents.
- **Exécution :** onboarding court, transition réelle vers WhatsApp, statut des outils visible et décision explicite sur la proposition ; slide unique avec cible, raison d’être actuelle et première validation terrain envisagée.

Les comptes et sinistres de démonstration doivent être publics ou synthétiques. Un endpoint de test peut simuler l’assureur, mais doit être nommé comme tel ; les actions réellement exécutées et les résultats simulés doivent rester distinguables.

L’agenda public précédemment consulté annonce démarrage à 9 h, pitch des huit meilleures équipes à 16 h et résultats à 17 h. La durée individuelle des pitches et les règles sur le code préparé en amont n’ont pas été vérifiées.

## 7. Articulation produit/données proposée — pas encore construite

Fil conducteur recommandé : **un dossier évolutif dont les nouvelles pièces changent les décisions et les actions de l’agent**.

Après l’onboarding web, parcours envisagé :

1. Message, photos et récit du commerçant sur WhatsApp.
2. Ingestion du contrat, des conditions particulières et des justificatifs disponibles.
3. Identification des faits établis, incertitudes et pièces manquantes.
4. Question ciblée ou appel à l’assureur.
5. Réception d’une pièce ou réponse nouvelle.
6. Mise à jour de l’analyse, du chiffrage justifié et du plan d’action.
7. Contrôle des sources, des incohérences et des calculs.
8. Transmission et suivi du dossier.
9. Offre reçue, expliquée et présentée au commerçant pour décision.

### Données à conserver et relier

- Documents : type, origine, version, date du document, période de validité pertinente pour le sinistre, lien vers le contenu.
- Faits : source, statut de vérification, contradictions et corrections.
- Dommages et postes demandés : justificatifs, clauses pertinentes, calculs, franchises/plafonds applicables lorsqu’ils sont établis.
- Échanges : messages, réponses écrites, transcriptions d’appels, points restant à confirmer.
- Actions : motif, éléments utilisés, résultat, prochaine étape, demandes de pièces déjà faites.
- Offres : contenu, montants, postes couverts, écarts et décision du commerçant.

Une réponse orale d’un interlocuteur ne doit pas être traitée automatiquement comme une modification du contrat. L’agent doit conserver l’origine de l’information et son niveau de confirmation.

### Moments de démonstration recommandés

- Un avenant applicable à la date du sinistre est ajouté : l’agent identifie les changements et révise les éléments concernés.
- Une facture est envoyée deux fois : le montant n’est pas compté deux fois.
- Une nouvelle pièce étaye un poste jusque-là incomplet : le dossier évolue avec une justification visible.
- Une session reprend : l’agent retrouve la mémoire du sinistre et les demandes déjà traitées.
- Un appel ou message entrant crée une nouvelle tâche pertinente, sans dépendre d’une consigne supplémentaire du présentateur.

### Preuve expérimentale recommandée

Préparer plusieurs variantes contrôlées d’un dossier : cas complet, pièce manquante, ancienne version, doublon et contradiction. Définir avant le test les contrôles attendus et leurs sources.

Comparer à un appel simple au **même modèle avec les mêmes documents disponibles**. Mesurer les contrôles correctement résolus, l’ancrage des montants dans les preuves et le temps de mise à jour. Aucun résultat n’a encore été mesuré ; ne pas inventer de gains de remboursement ou d’heures économisées.

**Métriques ajoutées au benchmark :**

- **Rappel des postes réclamables.** Pour chaque couple cas × contrat, la vérité terrain liste les postes réclamables avec leur clause et leur page (source : `data/research/08a_*`, `08b_*`). On mesure combien sont trouvés.
- **Citations correctes.** On mesure le pourcentage de postes dont la page citée existe et dit bien ce qui est affirmé.
- **€ identifiés.** On compare trois montants : la déclaration naïve du commerçant, le LLM sans recherche dans le contrat, et notre agent. Les cas viennent de `data/research/08c_*`.
- **Temps de constitution du dossier.** Le chrono va des photos et factures reçues sur WhatsApp au dossier complet : texte extrait des images par OCR, pièces rattachées, postes chiffrés et cités. On le compare au temps d’une constitution manuelle : retrouver chaque facture, recopier les montants, chercher chaque clause dans 70 à 120 pages. Le temps manuel doit être mesuré sur un cas réel chronométré, pas estimé.
- **Coût par dossier** (tokens/API) et **latence**.

Les contrôles déjà prévus (doublons, avenant, contradictions, reprise de session) restent dans le benchmark.

## 8. Architecture minimale recommandée

- **Site web sur Aiven Runtime** : inscription, onboarding, documents, profil, mandat et chatbot de complément.
- **Backend sur Aiven Runtime** : réception des événements, outils, orchestration et exécution des agents. Un seul service applicatif pour le premier build est une recommandation de simplicité, pas une exigence de Mathis.
- **Aiven PostgreSQL** : état du dossier, pièces référencées, versions, faits, échanges, actions et traces de test.
- **WhatsApp** : interface du commerçant ; intégration et conditions d’usage à vérifier avant implémentation.
- **Emails entrants/sortants** : fournisseur à choisir, API et événements de suivi à intégrer.
- **ElevenLabs + téléphonie compatible** : appels ; compte, numéro et configuration non disponibles à ce stade.
- **Documents originaux** : stockage durable protégé à choisir. Ne pas présumer que le disque du conteneur fait office d’archive persistante. Pour un prototype très limité, une conservation en base peut être étudiée ; pour des volumes importants, prévoir un stockage objet adapté.
- **Tâches asynchrones durables** : conserver les demandes et tentatives en base ; traiter les opérations longues hors de la réponse au webhook et reprendre après redémarrage. Le mécanisme d’exécution et ses limites sur le plan choisi doivent être testés.
- Un agent gestionnaire et éventuellement un agent de contrôle distinct. Le nombre d’agents n’est pas une fin en soi.
- Aucun choix de framework, modèle, fournisseur de stockage des fichiers ou mécanisme de connexion assureur n’a été arrêté.

Cette architecture est une recommandation, pas une décision technique validée ni une preuve de fonctionnement. Ne pas ajouter Kafka, OpenSearch, ClickHouse ou Valkey uniquement pour cocher les logos des sponsors.

Les accès administratifs Aiven utilisés pour déployer appartiennent à l’outillage de construction. **Ils ne doivent pas devenir des outils du chatbot des commerçants.** L’application utilise ses propres accès de données et fournisseurs.

## 9. Aiven — recherche technique pour préparer le build

Sources officielles consultées le **22 octobre 2026**. Cette section décrit ce que la documentation permet ; elle ne prouve pas que le compte du projet a déjà les droits, crédits ou services correspondants.

### 9.1. Contrainte de déploiement

**Console de gestion : [console.aiven.io](https://console.aiven.io/). Hébergement demandé : Aiven Runtime.** Utiliser uniquement PostgreSQL Aiven avec le site hébergé ailleurs ne satisferait pas à lui seul l’exigence Runtime du brief.

Runtime exécute des applications conteneurisées dans le projet Aiven. Le parcours documenté part d’un dépôt GitHub connecté. Prévoir un `Dockerfile`/`Containerfile`, éventuellement un fichier Compose pour décrire application et services. [Présentation Runtime](https://aiven.io/docs/products/runtime), [manifestes](https://aiven.io/docs/products/runtime/manifest-files/manifests).

Le lien GitHub nécessite le rôle administrateur de l’organisation Aiven ; une organisation GitHub exige également les pouvoirs adéquats pour installer l’application Aiven Platform. On peut limiter son installation aux dépôts choisis. Un même compte GitHub ne peut pas être connecté à plusieurs organisations Aiven selon la documentation actuelle. [Connexion GitHub](https://aiven.io/docs/products/runtime/connect-github-account).

### 9.2. API Aiven en priorité — décision de Mathis

**La voie principale de construction et de déploiement est l’API REST Aiven.** MCP et CLI restent disponibles en alternatives ; leur configuration n’est pas un prérequis pour avancer si l’accès API suffit.

Base : **`https://api.aiven.io/v1`**. La référence documente un schéma de token `aivenv1` ; les exemples Runtime utilisent aussi `Bearer`. Vérifier le schéma adapté au token fourni et à l’endpoint, sans afficher le secret. [Référence API officielle](https://api.aiven.io/doc/).

Parcours d’administration à automatiser, sous réserve des droits du compte :

1. Lire le projet, les services existants et la configuration disponible.
2. Vérifier le schéma `application` et les plans avec `GET /project/{project}/service-types/application` et `GET /project/{project}/service-types/application/plans`.
3. Résoudre le compte GitHub et le dépôt via `GET /organization/{organization_id}/application/vcs-integrations` et son sous-chemin `/{integration_id}/repositories`.
4. Créer PostgreSQL puis l’application avec `POST /project/{project}/service`, types `pg` et `application` ; utiliser les paramètres réels de région, plan, dépôt, branche, Dockerfile, port et variables.
5. Relier la base via l’API d’intégration décrite en 9.4.
6. Suivre l’état et les logs ; relever le commit effectivement déployé.
7. Après changement du code, utiliser `POST /project/{project}/service/{service_name}/application/redeploy`, en vérifiant son schéma courant.

Les opérations de plans, configuration et redéploiement figurent dans la [référence REST officielle](https://rest.aiven.io/doc/). Les modèles de création Runtime sont dans le [guide de déploiement](https://aiven.io/docs/products/runtime/deploy-apps). Aucun appel authentifié n’a encore été exécuté.

Il faut `project:services:write`, un rôle project manager ou project admin pour déployer. **Un push GitHub ne déclenche pas automatiquement le déploiement.** L’installation GitHub initiale reste une dépendance à résoudre ; disposer d’un token ne prouve pas que le dépôt est déjà relié.

Les tokens personnels se créent dans la console, rubrique utilisateur puis Tokens. Des utilisateurs applicatifs existent pour l’automatisation ; le choix dépendra de l’accès fourni. [Créer un token](https://aiven.io/docs/platform/howto/create_authentication_token), [utilisateurs applicatifs](https://aiven.io/docs/platform/concepts/application-users).

Alternative CLI : **`avn`**, paquet `aiven-client`, installable notamment par `pip install aiven-client`. La documentation décrit connexion par token et sorties JSON. La commande n’a pas été trouvée dans le PATH de cette session ; aucune installation n’a été faite. [CLI officielle](https://aiven.io/docs/tools/cli).

Commandes documentées utiles si cette alternative est choisie :

```sh
avn --version
avn user login EMAIL_ADDRESS --token
avn project switch PROJECT_NAME
avn service list --project PROJECT_NAME
avn service get APPLICATION_NAME --project PROJECT_NAME
avn service logs APPLICATION_NAME --project PROJECT_NAME
```

### 9.3. Alternative MCP officielle

Endpoint officiel hébergé : **`https://mcp.aiven.live/mcp`**.

L’organisation doit autoriser les connexions MCP. L’authentification distante utilise OAuth 2.0 avec PKCE. Le MCP peut inspecter les ressources, gérer des services et déployer des applications ; un mode lecture seule ne suffit donc pas à construire les ressources. Les permissions effectives restent celles du compte et de l’organisation. [Documentation MCP officielle](https://aiven.io/docs/tools/mcp-server).

Le dépôt officiel documente notamment :

- `aiven_vcs_integration_list` et `aiven_vcs_integration_initialize` : comptes GitHub reliés ou connexion à initier ;
- `aiven_vcs_integration_repository_list` et `aiven_vcs_integration_repository_scan_container_manifest` : dépôt et manifeste ;
- `aiven_application_create` : création et premier déploiement d’une application ;
- `aiven_application_redeploy` : reconstruction d’une application existante ;
- `aiven_service_get` et `aiven_project_get_service_logs` : état et diagnostic.

Les noms et paramètres doivent être relus dans les outils réellement exposés après connexion. Les scopes documentés incluent `application`, `pg`, `integrations` et `core`. [README officiel du MCP](https://github.com/Aiven-Open/mcp-aiven/blob/main/README.md).

**Distinction :** cet OAuth concerne l’accès de l’outil de construction à Aiven. Il n’authentifie ni le commerçant dans notre site, ni le service auprès de son assureur.

### 9.4. Packaging et base de données

Préparer une application qui écoute sur une interface accessible dans le conteneur, avec le port explicitement déclaré, par exemple `8080`. Runtime détecte les ports à partir de `EXPOSE`. [Containerfiles et Dockerfiles](https://aiven.io/docs/products/runtime/manifest-files/containerfiles).

Compose peut décrire une application construite depuis le dépôt et les services de données reconnus. Runtime ne déploie pas directement une application à partir de la seule propriété `image` : utiliser un build/Dockerfile. Le service managé détecté ne suit pas forcément la version indiquée dans l’image ; vérifier sa version effective. [Compose sur Runtime](https://aiven.io/docs/products/runtime/manifest-files/compose-files).

Relier PostgreSQL à l’application avec l’intégration **`application_service_credential`** ; la chaîne de connexion peut être exposée en `DATABASE_URL`. La commande correspondante est `avn service integration-create`, et l’API utilise `POST /project/{project}/integration`.

Runtime ne fournit pas automatiquement de commande de migration avant déploiement ni de tâche ponctuelle. Choisir des migrations au démarrage ou en CI ; pour plusieurs instances, prévoir leur coordination. Lors d’une mise à jour de variables par API/CLI, vérifier si la liste existante est remplacée afin de préserver les autres valeurs. [Connexion des services et migrations](https://aiven.io/docs/products/runtime/connect-services-to-apps).

### 9.5. Réseau et authentification du produit

Le point d’entrée public est HTTPS sur le port 443 ; Aiven termine TLS puis transmet en HTTP au port du conteneur. Les ports applicatifs exposés sont HTTP, sans support annoncé de TCP, gRPC ou HTTP/2. Certains ports sortants sont bloqués, notamment 25 et 465 : **prévoir une API email en HTTPS**. Le support WebSocket et les limites de durée/volume nécessaires au projet restent à tester ; ne pas déduire leur disponibilité de la seule présence d’HTTP. [Ports Runtime](https://aiven.io/docs/products/runtime/ports).

Les applications sont accessibles publiquement par défaut. Runtime propose Aiven Identity, lié aux utilisateurs/groupes de l’organisation, ou un fournisseur OIDC. **Ces mécanismes ne constituent pas automatiquement l’inscription des commerçants.** [Authentification Runtime](https://aiven.io/docs/products/runtime/authentication/apps-authentication-overview).

Recommandation : authentification et séparation des clients dans l’application ; endpoints de callbacks accessibles aux fournisseurs avec validation de leurs signatures. Vérifier qu’une éventuelle protection globale Runtime ne bloque pas les webhooks WhatsApp, email ou voix.

### 9.6. Secrets, logs et exploitation

Stocker les clés fournisseurs dans les variables marquées secrètes ; les connexions des services reliés peuvent être exposées par intégration. Une modification des variables redéploie le commit précédemment déployé, pas nécessairement le dernier du dépôt. [Variables et secrets Runtime](https://aiven.io/docs/products/runtime/secrets-and-variables).

Build et exécution possèdent des logs distincts. L’API documente `POST /project/{project}/service/{service}/logs` avec `log_type: application-build` ou `application-run`. La rétention native annoncée est de vingt-quatre heures. **L’historique métier du client doit être conservé dans nos données durables, pas dans ces logs.** [Logs Runtime](https://aiven.io/docs/products/runtime/runtime-logs).

Changer le plan de l’application n’ajuste pas automatiquement les plans des services connectés. Aucun prix, région, montant de crédit ni quota Runtime du compte n’a été confirmé. [Plans d’application](https://aiven.io/docs/products/runtime/scale-apps).

### 9.7. Ordre recommandé une fois les accès fournis

1. Identifier organisation, projet, permissions, région et ressources existantes ; relever les crédits/plans réellement disponibles.
2. Vérifier en priorité le token et les opérations API nécessaires. Utiliser MCP ou CLI en alternative si utile ; ne pas attendre que les trois voies soient configurées.
3. Relier le dépôt GitHub adéquat via le parcours autorisé et relever branche/manifeste.
4. Déployer très tôt une application minimale sur Runtime et vérifier son URL, son port et son commit.
5. Connecter PostgreSQL, appliquer les migrations et vérifier une écriture/lecture de test ainsi que la reprise après redémarrage.
6. Ajouter inscription, profil, mandat et documents ; valider l’isolement de deux comptes de démonstration.
7. Brancher un canal WhatsApp réellement disponible, puis le message de bienvenue conforme et la reprise de la mémoire.
8. Ajouter mail/voix avec interlocuteurs de test autorisés, événements de réponse et suivi des échecs.
9. Exécuter les cas de preuve et la démo ; conserver les résultats observés et l’origine des données.

Ce sont des étapes proposées pour la construction future. Le support des fichiers persistants, les volumes d’upload, le fonctionnement des tâches longues, les extensions PostgreSQL éventuelles et les accès aux fournisseurs n’ont pas été validés sur le compte.

## 10. Sources métier déjà repérées

Sources consultées pendant la conversation ; aucune vérification fonctionnelle des espaces assureurs n’a été faite.

- [Événement officiel Accel/BuilderBase](https://luma.com/0v3c010v).
- [MAAF — conditions générales Multirisque Professionnelle, édition janvier 2026, version accessible](https://handicapzero.maaf.fr/mon-activite-professionnelle/multirisque-professionnelle/conditions-generales-multirisque-professionnelle).
- [MAAF — locaux et contenu : garanties souscrites précisées dans les conditions particulières](https://handicapzero.maaf.fr/mon-activite-professionnelle/multirisque-professionnelle/conditions-generales-multirisque-professionnelle/vos-locaux-et-leur-contenu).
- [AXA — déclaration de bris de glace professionnel](https://www.axa.fr/professionnels/demarches/declaration-bris-glace.html).
- [CCI Paris Île-de-France — commerçants sinistrés](https://www.entreprises.cci-paris-idf.fr/commercants-sinistres).
- [France Assureurs — dégâts matériels liés aux violences urbaines](https://www.franceassureurs.fr/lassurance-protege-finance-et-emploie/lassurance-protege/les-demarches-en-cas-de-sinistre/indemnisation-degats-materiels-provoques-violences-urbaines/).
- [Code civil, article 1984 — principe du mandat](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006445236/).
- [CNIL — exercice du droit d’accès par un mandataire](https://www.cnil.fr/fr/repondre-une-demande-de-droit-dacces). Ce sujet concerne les données personnelles ; il ne prouve pas à lui seul qu’un dossier commercial complet est récupérable instantanément.
- [Aiven Runtime — déploiement d’une application](https://aiven.io/docs/products/runtime/deploy-apps).
- [Aiven Runtime — connexion des services de données](https://aiven.io/docs/products/runtime/connect-services-to-apps).
- [ElevenLabs — téléphonie Twilio entrante/sortante](https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration/).

## 11. État réel du travail et suite demandée

L’espace de travail contient des recherches et rapports sur les agents IA et les dossiers solaires. Il ne contient pas encore de prototype de gestion de sinistre, de connexion WhatsApp/assureur, d’agent vocal configuré ou de benchmark exécuté.

Les autres idées explorées — cerveau personnel, mémoire portable et compléments de dossiers solaires — sont du contexte historique. **Le projet actif est l’assurance des petites entreprises.**

Documents précédents :

- [Recherche sur les agents IA](recherche-agents-ia.html).
- [Étude des dossiers solaires](etude-dossiers-solaires.html).

La recherche documentaire sur le workflow a été réalisée en trois volets parallèles, puis consolidée : [workflow complet et sources](recherche-workflow-sinistres-commercants.md). Elle fournit le détail des clauses et cas fictifs ; le présent document fait référence pour le parcours produit actualisé en deux blocs.

Principaux résultats à préserver, qui ne constituent pas de nouvelles décisions de Mathis :

- Déclarer rapidement sans attendre toutes les pièces, puis compléter le dossier et conserver les preuves de réception.
- Le cœur recommandé est un **état des pertes vivant** : chaque poste relie dommages réels, preuves, clause, calcul et prochaine action.
- Les CG MAAF janvier 2026 fournissent des exemples vérifiés : marchandises exposées abîmées par le bris, frais de clôture/gardiennage sous conditions, TVA/franchises et complément après remplacement. Ils ne se transposent pas à tous les contrats.
- Une offre acceptée n’est pas un règlement reçu : suivre acomptes, paiement direct au réparateur et compléments éventuels séparément.
- Aucun accès délégué universel aux espaces clients n’a été établi. Les restrictions de partage des identifiants et l’authentification doivent être traitées par canal et assureur ; un mandat ne fournit pas à lui seul un accès technique.
- WhatsApp impose des contraintes de fenêtre de réponse, de modèles et d’identifiants sensibles. Un dépôt protégé est recommandé pour un RIB ou une pièce d’identité demandés par l’assureur.
- Les comptes Twilio d’essai limitent les destinataires ; la téléphonie et les médias WhatsApp doivent être testés sur les comptes réellement disponibles.
- Ne pas coder une horloge universelle. Les règles diffèrent selon nature du sinistre, contrat et régime. L’applicabilité du décret prévu pour le nouvel article L121-18 n’a pas été établie dans cette recherche.

Deux cas de test entièrement fictifs sont décrits : complément de preuves après bris de devanture et complément conditionnel après remplacement de matériel. Aucun sinistre réel, appel assureur, déploiement ou résultat d’indemnisation n’a été obtenu.

**Dernière demande de Mathis : ce Markdown de contexte, intégrant le site d’onboarding, le bloc WhatsApp et la recherche approfondie Aiven.** Le travail suivant serait la construction et la vérification du prototype lorsque les accès seront disponibles ; aucune ressource cloud n’a été créée à ce stade.

## 12. Préférences de collaboration à préserver

- Répondre en français, concrètement, avec peu de jargon.
- Cette préférence concerne nos échanges avec Mathis : **le bot du produit parle anglais**.
- Pour construire et déployer sur Aiven, **priorité à l’API** ; MCP et CLI sont des solutions alternatives.
- Priorité au produit, à la démonstration et au fonctionnement de l’agent.
- Ne pas imposer une niche commerciale étroite ou une limite de montant déjà refusée par Mathis.
- Préserver l’autonomie souhaitée ; ne pas réintroduire une validation humaine systématique ou une équipe cachée.
- Distinguer décisions de Mathis, suggestions de l’assistant et choses réellement testées.
- Mathis a invoqué le skill **grill-me** : si l’entretien de conception reprend, poser une seule question à la fois, avec une recommandation ; examiner ce qui peut l’être directement plutôt que demander des faits déjà accessibles.
- Les demandes de recherche, de synthèse ou de fichier doivent être traitées avant de reprendre l’interview.

## 13. Décisions de build (22 octobre 2026, matin)

### 13.1. Stack retenue

| Brique | Choix | Pourquoi / notes |
|---|---|---|
| **WhatsApp** | **Compte WhatsApp Business** créé par l'équipe, branché via l'**API WhatsApp Cloud (Meta)** | C'est le canal principal du commerçant : texte, photos, documents, vocaux. Les médias arrivent par webhook et sont téléchargés côté backend. |
| **Email** | **AgentMail** : une boîte par client ou dossier, envoi et réception par API, webhook à chaque email reçu | Offre gratuite : 3 boîtes, 100 emails/jour, adresses en `@agentmail.to`. L'envoi passe par HTTPS, ce qui contourne le blocage des ports 25/465 sur Runtime (§9.5). Aucun accès à la boîte du commerçant. |
| **Appels** | **ElevenLabs Agents**, avec le dossier injecté au démarrage de l'appel (variables dynamiques) | Plan A gratuit : l'appel par le **widget web** ElevenLabs (navigateur), sans numéro. Option « vrai téléphone » : un numéro **Twilio trial** (gratuit, sans CB ; numéros vérifiés uniquement, 10 min max, message « trial » lu en début d'appel). Utiliser les crédits ElevenLabs du Builders Pack. |
| **LLM + OCR** | **Claude** : boucle d'agent avec outils, et vision pour extraire le texte des photos, factures et PV en JSON structuré | L'extraction depuis les images est au cœur de la promesse « l'agent fait tout ». |
| **Données** | **Aiven PostgreSQL** : comptes, contrats découpés en clauses avec page, dossiers, pièces, faits, échanges, actions, mémoire | Les clauses sont cherchées en plein texte, et/ou avec pgvector si l'extension est disponible. |
| **Hébergement** | **Aiven Runtime** (exigence du brief) | Il faut d'abord relier le GitHub (rôle admin requis, §9.1). |

### 13.2. Corpus de données réelles (dans ce repo)

- **`data/contrats/txt/`** : 12 documents contractuels **publics** de multirisque professionnelle, extraits avec `pdftotext -layout`. Sources originales :
  - Generali 100% Pro GA5M70F (72 p.) : https://www.air-assurances.com/pdf_doc/hangar_2022/CG_GA5M70F.pdf
  - AXA Atouts PME (88 p.) : https://media.axa.fr/content/dam/axa-fr/image/pro/documents-informations/pdf-assurance-atout-pro-pme-cg.pdf
  - AXA Mon Pack Entrepreneur (108 p.) : https://media.axa.fr/content/dam/axa-fr/image/pro/documents-informations/pdf-mon-pack-entrepreneur-cg.pdf
  - Allianz Actif Pro (124 p. ; contrat services et professions libérales, pas le contrat commerçant, qui n'est pas publié) : https://www.gpm.fr/wp-content/uploads/2026/06/CG-MRP-ALLIANZ.pdf
  - Sogessur / Société Générale, Commerçants Artisans (2016) : https://static.societegenerale.fr/pro/PRO/Repertoire_par_type_de_contenus/Fichier_a_telecharger/Fiches_numeriques/cg-commercants-artisants.pdf
  - Groupama, dispositions communes uniquement (le texte des garanties n'est pas disponible) : https://www.coover.fr/wp-content/uploads/2019/10/conditions-generales-responsabilite-civile-professionnelle-groupama.pdf
  - MAAF Multirisque Pro 11031 (01/2026) : https://www.maaf.fr/fr/files/live/sites/maaf/files/DOCUMENTS/Professionnels/CG/MAAF_Conditions_generales_Multirisque_pro_11031.pdf
  - MMA Pro-PME 352 p (04/2021) : https://philtr.fr/static/pdf/insurance/mrp/mma_mrp.pdf
  - Hiscox (CG, Conventions spéciales MRP0623, IPID) : https://www.hiscox.fr/courtage/sites/courtage/files/documents/MRP0623%20-%20Conventions%20Speciales%20Multirisques%20Dommages%20aux%20Biens%20Professionnels%20.pdf
  - Pacifica / Crédit Agricole (IPID seul) : https://www.credit-agricole.fr/content/dam/assetsca/master/public/commun/documents/7197A.36_IPA_doc%20info_M9_PRO-122020-BD.pdf
- **`data/research/08a_*` et `08b_*`** : pour chaque contrat, les clauses utiles après pillage ou vandalisme, avec citation courte et page, plus un tableau croisé des « postes souvent oubliés ». Exemples **vérifiés dans le texte** :
  - **MMA** rembourse l'expert choisi par l'assuré jusqu'à 10 % de l'indemnité, dans la limite de 40 000 €, s'il a souscrit l'option.
  - **Generali** applique un barème d'honoraires d'expert de 5 % jusqu'à 350 000 €.
  - **Sogessur** exclut « les vols ou tentatives de vol, survenus lors d'émeutes ».
- **`data/research/08c_*`** : des témoignages réels (2023 et octobre 2026), la jurisprudence (n° à vérifier sur Légifrance avant affichage) et **3 cas composites chiffrés** (réparateur smartphones, boulangerie, opticien) qui servent de base au benchmark.
- **`data/research/08d_*`** : le process sinistre, le calcul des indemnités, la réglementation (mandat, consultation juridique, ORIAS), la concurrence, la taille du marché et 10 réponses aux questions d'un partner VC.

### 13.3. Ce que le benchmark doit montrer

Le benchmark est détaillé au §7. Les chiffres clés à afficher sur la slide :

- le **rappel des postes réclamables**, avec la page correcte ;
- les **€ identifiés** dans trois versions : déclaration naïve, LLM seul, notre agent ;
- le **temps de constitution du dossier**, de l'agent comparé au manuel : photos et factures lues automatiquement, pièces rattachées, chaque poste chiffré et cité ;
- le **coût par dossier**.
