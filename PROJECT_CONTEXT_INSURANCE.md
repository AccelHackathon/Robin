# Context — Autonomous claims agent for small businesses

Updated on **22 October 2026**, Paris time.

This document serves as context for resuming the design and building the product in another session. It consolidates the discussions, the hackathon brief, the hand-drawn diagram IMG_1211 and the official Aiven research from 22 October 2026. It distinguishes Mathis's decisions, recommendations and capabilities that have actually been verified. **The product is not yet implemented in this repository.**

> **Update of 22 October, noon — read this first.** Three changes relative to sections 1 to 13:
> 1. **Telegram replaces WhatsApp** as the merchant's channel (team decision: the WhatsApp Cloud API cannot be made to work within the time available). Wherever the sections below say "WhatsApp", read "Telegram". The WhatsApp constraints (24-hour window, templates, phone number verification) **disappear**.
> 2. **Aiven is provisioned**: organisation with an active trial ($50 of credits, 30 days), project `larp`, PostgreSQL `pg-3f9bc500` (Developer-1 plan, 1 CPU / 1 GB / 8 GB, DigitalOcean `fra`) running. Runtime is available in the project. The GitHub → Runtime link is still to be done and requires the organisation admin role.
> 3. **Stack and architecture settled**: Python / FastAPI / **LangGraph** with Postgres checkpointer, single service on Runtime. The details, the demo scenario and the build order are in **section 14**, which takes precedence in case of contradiction with the rest of the document.

## 1. Objective and vision

Build an assistant that takes over a small business's insurance file after a loss event. The experience has **two blocks: a website to create and configure the account, then WhatsApp to use the agent day to day**.

On the website, the merchant enters their phone number, uploads their contracts and documents, describes their business and history, then grants a *mandat* (mandate/power of attorney). A chatbot asks for any missing information. After onboarding, the service sends them a welcome message on WhatsApp.

The business owner explains the facts, sends photos, voice messages and documents. The agent reads the contract, identifies the relevant steps, collects missing evidence, contacts the insurer, assembles the claim, submits it and follows up on the exchanges.

The objective is to **assemble the most complete and best-substantiated compensation claim possible in light of the actual damage and the contract**. An amount claimed is not a reimbursement obtained. No promise of guaranteed reimbursement has been adopted.

Example input: "Someone smashed my shop window. Here are the photos. What should I do?"

Proposed working tagline: **"Your policy, your evidence, your claim — handled by your agent."** No brand name has been settled.

The initial context notably mentions shops damaged or vandalised on the fringes of demonstrations. This is an example use case, not a definitive limitation of the product.

**Pitch hook (current events, "why now"):**
- On **17 and 18 October 2026**, approximately **3,000 shops** were damaged or looted in France. This figure is provisional; it is cited by the Prime Minister and by Serge Papin ([Public Sénat, 19/10](https://www.publicsenat.fr/actualites/economie/pillages-au-moins-3-000-commerces-touchees-pour-des-centaines-de-millions-deuros-de-degats)), and confirmed by Bercy ([press release of 20/10](https://presse.economie.gouv.fr/le-gouvernement-met-en-place-des-mesures-de-soutien-aux-commerces-touches-par-les-degradations-du-samedi-17-et-dimanche-18-octobre-2026/)).
- Insured damage is estimated at between **€1 and 1.2 billion** ([Morningstar DBRS via Reinsurance News](https://www.reinsurancene.ws/france-riots-put-srcc-accumulation-risk-in-focus-for-re-insurers-morningstar-dbrs/)).
- As a precedent, the 2023 riots gave rise to 16,400 claims for €793M ([Sénat](https://www.senat.fr/rap/r23-521/r23-52117.html)).
- The market is not limited to riots: roughly 110 claims per 1,000 merchant policies per year ([France Assureurs 2024](https://www.franceassureurs.fr/wp-content/uploads/lassurance-de-dommages-aux-biens-des-professionnels-en-2024-1.pdf)).

## 2. Decisions expressed by Mathis

### Users and scope

- Target **small businesses in France**, with small retailers as the priority.
- The business owner is the intended user.
- Do not impose a commercial threshold on claim amount or loss category at this stage.
- Large problems seem particularly interesting to Mathis.
- A specific case can illustrate the demo without limiting the commercial ambition of the service.

### Autonomy

- The product must be **genuinely autonomous**, with no human team processing files behind the scenes in the intended operation.
- The agent must take the initiative on research, document requests, calls, submissions and follow-ups.
- Do not impose a human review of every intermediate action.
- It may ask the merchant for facts, documents or photos when information is missing.
- When a compensation offer arrives, it **notifies the merchant**, explains it and may make a recommendation.
- **Accepting an offer remains the merchant's decision.**
- No systematic mechanism for escalating to an internal human expert has been accepted: Mathis favours the agent's independence.
- This does not remove the need to handle uncertainty, tool limitations and blocked situations. The exact behaviour in those cases remains to be designed.

### Interface and document retrieval

- **Most recent decision: an account on our website and a web onboarding before moving to WhatsApp.**
- WhatsApp for exchanges, photos, documents and voice messages after that setup.
- The merchant can send their contract within the conversation.
- If they cannot find it, the agent must be able to request a copy from the insurer, within an authorised framework.
- A connection to **the insurer's customer portal** was also explored. It remains a separate avenue from the account created on our own website, which is now confirmed.
- Retrieving documents from that portal depends on a delegation mechanism that is accepted and technically available; it has not been verified.
- An authorisation to represent and technical access to the account are two distinct matters.
- A tracking page reachable via a link from WhatsApp was **recommended by the assistant, not yet chosen by Mathis**.

The attached diagram also shows a feedback loop from the tools back to the memory built during onboarding, and an intervention by the merchant at the time of the proposal. It confirms continuity between the two blocks, not two isolated assistants.

### Product language

- **Explicit decision by Mathis: the bot speaks English.** The onboarding chatbot's replies and the WhatsApp messages are therefore in English. The agent also uses English by default in its generated exchanges; adapting to French for an insurer-side contact would remain to be specified.
- The working context and exchanges with Mathis remain in French, concrete and with little jargon.
- French contracts and documents keep their original language and exact quotations; an explanation in English does not replace the source.
- The language of the website's static elements has not been settled separately; do not confuse this point with the bot's language.

### Calls

- The voice agent would use **ElevenLabs** to contact the insurer.
- Calls must clarify questions useful to the file: expected documents, procedure, contractual point or blocker.
- The answers obtained must feed the claim memory and change the next actions where necessary.
- No real call to an insurer has been made or tested.
- **Call language: English**, like the rest of the bot. The demo call is in English, which allows the jury to understand it.

### Remuneration — provisional

- Mathis is considering a **percentage at the time of compensation**.
- Rate, calculation base, caps and terms remain "to be determined".
- Do not assume the service would directly collect the insurer's funds.
- Mathis explicitly asked to **focus on the product rather than the business**. Do not resume a long interview on pricing, acquisition or distribution unless asked.

## 3. Block 1 — Account creation and onboarding on the website

### Requested journey

1. **Create an account.** Access the site, sign up/log in, and be able to resume an interrupted onboarding.
2. **Configure the phone number.** Enter the phone number that will be used on WhatsApp and link that number to the right customer account.
3. **Upload what you have.** Contracts, *conditions particulières / CP* (policy schedule), endorsements, any incident reports and useful history. The hand-drawn diagram mentions contracts; Mathis also mentions incident reports. Keep both types.
4. **Fill in the profile.** Business persona, company, contact person and shop context.
5. **Grant a mandate.** Authorise the service to carry out the defined steps and keep proof of that authorisation.
6. **Complete with the chatbot.** The agent reads the documents and asks only for the information still needed.
7. **Move to WhatsApp.** The account is saved, the initial memory is available and a welcome message is sent once the channel is operational.

### Interpretation of the profile/persona — recommendation to adapt

The persona here means a **business profile useful to the file**, not invented psychological traits:

- identity and capacity of the representative;
- company and activity, SIREN/SIRET where relevant;
- address of the premises and tenant/owner status;
- insurer, broker and contacts already known;
- tax situation relevant to the valuation, notably VAT, when established;
- practical contact preferences and history of claims or existing proceedings.

These fields are a proposed model. Do not require all of them before allowing sign-up. Data present in a document does not need to be retyped, but an uncertain extraction must be confirmed.

### What the onboarding chatbot does

- Identify and classify the uploaded documents; keep the originals.
- Extract information along with its sources and degree of confirmation.
- Spot a missing policy schedule, an outdated document or an applicable endorsement.
- Ask a targeted question in English: "Is this the insured business address?", "Could you upload the policy schedule showing your selected cover?"
- Request the representation details needed for the mandate.
- Never infer that an option is not subscribed because its page has not been received yet.
- Keep missing documents as tasks; an account can be created with a still-incomplete profile.

Creating an account must be able to prepare for future use. If a claim is already under way, open its record and resume the procedure without waiting for the full history to be completed. Do not delay an urgent declaration in order to finish onboarding.

### Mandate and consents

The mandate must name the entity operating the service and the person authorised to grant power on behalf of the company. Proposed scope: obtain documents, submit confirmed facts and supporting documents, contact insurer/broker, request a status or additional information, and follow up.

Keep version, scope, signatory, declared/verified capacity, date, proof of acceptance and revocation. The signature mechanism remains to be chosen. Do not present mere account opening as a general authorisation.

Accepting an offer, a settlement or a waiver does not follow from the intended operational mandate. The merchant keeps the decision on the proposal. The legal characterisation of the commercial service and the powers actually accepted by the insurer remain to be validated.

Separate the **mandate of representation**, the **consent to receive WhatsApp communications** and the **information on data processing**. A single undifferentiated button does not properly describe these purposes.

### Welcome message and linking to the phone number

Proposed text, not yet sent:

> Hi! Your account is ready. You can message us here whenever you need help, and send photos or documents about your claim.

The transition from the website is a service-initiated send: plan for the recipient's consent and an approved template. An alternative is a button to WhatsApp that has the merchant send the first message. The twenty-four-hour service window starts with the user's message; creating the web account alone does not open it. [WhatsApp policy](https://whatsappbusiness.com/policy/).

Implementation recommendation: verify ownership of the number, normalise it and associate the WhatsApp conversation identifier with the authenticated business. Do not merge files on the sole basis of an unverified number entry.

Distinguish **account created**, **profile partially completed**, **mandate recorded**, **WhatsApp linked**, **welcome sent/delivered/failed**. If sending fails, the account remains created; the site offers a retry instead of displaying a fictitious success.

### Expected outcome at the end of block 1

A durable customer identity, a business profile, a linked number, the documents received and their versions, the mandate, the missing information and the history make up the initial memory. The second block reuses this memory from the very first message.

## 4. Block 2 — WhatsApp agent, tools and customer memory

### User experience

The merchant writes naturally, sends a voice message, photos or a document. The agent finds the relevant business and file, reads their current state, chooses the relevant action, uses its tools and informs the merchant of the result or the blocker.

The recommended flow is: **incoming event → memory read → analysis → action → verified result → memory update → next step**. A reply received by email or after a call must be able to trigger the next step without a new prompt from the merchant.

### Requested tools

- **WhatsApp messages:** receive and send, fetch media, identify the conversation, keep acknowledgements and failures.
- **Emails:** prepare and send a declaration, a document request, supporting documents or a follow-up; receive replies and attach them to the right file. **Chosen provider: AgentMail** (see §13). Do not assume access to the merchant's personal mailbox.
- **Phone:** call via ElevenLabs and compatible telephony, navigate a switchboard if possible, ask for clarifications and retrieve a structured result. A transcript is not proof that the file has been opened.
- **Customer memory:** read and update facts, contracts, documents, exchanges, actions, offers and settlements over time.

The name "customer memory" is validated as a concept. Functions such as `get_customer_context`, `store_evidence`, `send_email`, `start_phone_call` or `schedule_followup` would be proposed technical interfaces, not tools already available.

### What is memorised

**At the business level:** profile, representatives, verified numbers, mandates, contacts, contracts and confirmed preferences.

**At the claim level:** known or presumed facts, documents and versions, damage, *état des pertes* (statement of loss), rules applied, communications, deadlines, actions taken, pending tasks and proposals.

A correction must not silently erase the previous value. An oral answer keeps its provenance; an offer and a payment keep their own proofs. The web chatbot, WhatsApp and the tools use the same file, with separation between customers and between claims.

### Autonomy and merchant intervention

The agent handles the routine steps provided for in its mandate, without systematic human validation. It calls on the merchant when information or evidence is missing, when an access requires their intervention, or when a decision exceeds the delegated powers.

At the offer stage, it explains the amounts, gaps and conditions. The merchant decides to accept, ask for clarification or contest. **Silence is never acceptance.** After the authorised decision, the agent tracks the payment and any supplements.

### Operational journey of the file

1. Identify the loss event and the emergencies; preserve evidence.
2. Prepare and submit the initial declaration through a recognised channel, without waiting for all documents.
3. Read the applicable contractual documents and establish the candidate covers.
4. Build the statement of loss: each item links a piece of evidence, a clause, a calculation and any condition.
5. Request missing information and use email/phone to resolve a specific question.
6. Submit supplements, keep acknowledgements and follow any loss adjustment.
7. Present the proposal to the merchant for decision.
8. Track advances, direct payment to the repairer, compensation received and conditional supplement.

Requests, offers and funds received are distinct objects. An action is only marked as done once its result is observed. A refusal, a wait or an outage must remain visible.

## 5. Access and available documents

- No complete real commercial claim file has been provided.
- **A corpus of 12 real public general conditions is available in `data/contrats/txt/`** (details and usage in §13.2): Generali, AXA ×2, Allianz, Sogessur, Groupama, MAAF, MMA, Hiscox ×3, Pacifica. Added to these are the per-contract clause sheets (with pages) and 3 sourced, quantified cases in `data/research/`.
- Mathis may try to obtain one; he also asked to search for public documents available on the Internet.
- Access to a personal/family insurance policy was mentioned. The name heard, "MAF" or "MAAF", remains to be confirmed.
- An insurance account for his company may exist under the president's access. No access, contract or test agreement is confirmed.
- Do not infer an authorisation to connect, collect or publish from this mere mention.
- No credentials have been provided.
- Public general conditions and insurer guides have been found. A policyholder's policy schedule remains necessary to determine the covers they actually subscribed.
- The diagram **IMG_1211.HEIC** has been read: account with phone, contracts, persona and history; WhatsApp message; mailbox/customer memory/phone tools; intervention on the proposal.
- Mathis plans to grant Aiven access via **API, MCP or CLI** to build and deploy. None of these accesses had been configured while this document was being written.
- **Most recent technical preference: use the Aiven API first; MCP and CLI remain alternatives.**

## 6. Hackathon — latest brief provided by Mathis

**Future Founders: Data-Centric Agents — From Prompt to Production Data.** Accel AI Innovate Paris hackathon, **22 October 2026**.

The latest brief is more precise than the page initially discussed. It asks for:

- A working product for a specific user and problem.
- Agents that reason and act on real, evolving, sometimes stale or contradictory data.
- A data layer that is central to the product's usefulness.
- **Deployment of the application on Aiven Runtime**; use of its data services where relevant.
- A complete end-to-end user journey.
- A demonstration of the data flow: sources, storage, movement and effects on decisions.
- Measured evidence: before/after, benchmark or comparison with a naive/data-free version.
- A slide stating the user, the current reason for existing and a path to the first users.
- Publicly shareable data; explicit separation between live execution and recorded or simulated scenarios.

### The five judging criteria

1. **Customer Problem & Product Value**: real problem, clear user, plausible adoption.
2. **Agent Capability**: multi-step reasoning, autonomy, collaboration or learning beyond a single model call.
3. **Data at the Core**: freshness, relevant volume, grounding in sources and/or memory that is genuinely useful.
4. **Evidence It Works**: measured result, e.g. accuracy, cost, latency, success or time.
5. **Execution & Pitch**: understandable and polished demo, clear differentiation, credible path to the first users.

A **separate Aiven prize** rewards the best use of its platform. The brief does not ask to artificially multiply services nor to implement every inspiration track.

The PDF provided by Mathis, **Future Founder Challenge_ Data-Centric Agents (1) (1).pdf**, has been read and confirms these requirements, notably Aiven Runtime, the measured comparison and the distinction between live and recorded scenario.

### Translating the criteria into our demo

- **Value:** a merchant creates an account, uploads documents and receives a usable file and understandable tracking.
- **Agent:** an insurer reply or a new piece of evidence causes a new action to be chosen and executed, without a hidden scenario driven by the presenter.
- **Data:** the memory created on the website is found again on WhatsApp; contract version, documents and history change the conclusions.
- **Evidence:** measure errors, duplicates, repeated questions and resolved checks across several variants, against a baseline using the same model and the same documents.
- **Execution:** short onboarding, real transition to WhatsApp, visible tool status and explicit decision on the proposal; a single slide with target, current reason for existing and the first intended field validation.

Demo accounts and claims must be public or synthetic. A test endpoint may simulate the insurer, but must be named as such; actions actually executed and simulated results must remain distinguishable.

The public agenda consulted earlier announces a 9 am start, pitches by the eight best teams at 4 pm and results at 5 pm. The individual pitch duration and the rules on code prepared in advance have not been verified.

## 7. Proposed product/data articulation — not yet built

Recommended guiding thread: **an evolving file in which new documents change the agent's decisions and actions**.

After web onboarding, intended journey:

1. Message, photos and the merchant's account of events on WhatsApp.
2. Ingestion of the contract, the policy schedule and the available supporting documents.
3. Identification of established facts, uncertainties and missing documents.
4. Targeted question or call to the insurer.
5. Receipt of a new document or reply.
6. Update of the analysis, the substantiated valuation and the action plan.
7. Check of sources, inconsistencies and calculations.
8. Submission and tracking of the file.
9. Offer received, explained and presented to the merchant for decision.

### Data to keep and link

- Documents: type, origin, version, document date, validity period relevant to the claim, link to the content.
- Facts: source, verification status, contradictions and corrections.
- Damage and claimed items: supporting documents, relevant clauses, calculations, applicable deductibles/caps when established.
- Exchanges: messages, written replies, call transcripts, points still to be confirmed.
- Actions: reason, elements used, result, next step, document requests already made.
- Offers: content, amounts, items covered, gaps and the merchant's decision.

An oral answer from a contact must not be automatically treated as a modification of the contract. The agent must keep the origin of the information and its level of confirmation.

### Recommended demo moments

- An endorsement applicable at the date of loss is added: the agent identifies the changes and revises the affected elements.
- An invoice is sent twice: the amount is not counted twice.
- A new document substantiates a previously incomplete item: the file evolves with a visible justification.
- A session resumes: the agent finds the claim memory and the requests already handled.
- An incoming call or message creates a new relevant task, without depending on an additional instruction from the presenter.

### Recommended experimental evidence

Prepare several controlled variants of a file: complete case, missing document, old version, duplicate and contradiction. Define the expected checks and their sources before the test.

Compare against a simple call to the **same model with the same available documents**. Measure checks correctly resolved, grounding of amounts in evidence and update time. No result has been measured yet; do not invent reimbursement gains or hours saved.

**Metrics added to the benchmark:**

- **Recall of claimable items.** For each case × contract pair, the ground truth lists the claimable items with their clause and page (source: `data/research/08a_*`, `08b_*`). We measure how many are found.
- **Correct citations.** We measure the percentage of items whose cited page exists and actually says what is asserted.
- **€ identified.** We compare three amounts: the merchant's naive declaration, the LLM without contract search, and our agent. The cases come from `data/research/08c_*`.
- **Time to assemble the file.** The clock runs from photos and invoices received on WhatsApp to the complete file: text extracted from images by OCR, documents attached, items quantified and cited. It is compared with the time of a manual assembly: finding each invoice, copying out the amounts, searching for each clause across 70 to 120 pages. The manual time must be measured on a real timed case, not estimated.
- **Cost per file** (tokens/API) and **latency**.

The checks already planned (duplicates, endorsement, contradictions, session resumption) remain in the benchmark.

## 8. Recommended minimal architecture

- **Website on Aiven Runtime**: sign-up, onboarding, documents, profile, mandate and completion chatbot.
- **Backend on Aiven Runtime**: event reception, tools, orchestration and agent execution. A single application service for the first build is a recommendation for simplicity, not a requirement from Mathis.
- **Aiven PostgreSQL**: file state, referenced documents, versions, facts, exchanges, actions and test traces.
- **WhatsApp**: merchant interface; integration and terms of use to be verified before implementation.
- **Inbound/outbound emails**: provider to be chosen, API and tracking events to be integrated.
- **ElevenLabs + compatible telephony**: calls; account, number and configuration not available at this stage.
- **Original documents**: durable protected storage to be chosen. Do not assume the container's disk acts as a persistent archive. For a very limited prototype, storage in the database can be considered; for large volumes, plan for suitable object storage.
- **Durable asynchronous tasks**: keep requests and attempts in the database; process long operations outside the webhook response and resume after restart. The execution mechanism and its limits on the chosen plan must be tested.
- A handling agent and possibly a distinct review agent. The number of agents is not an end in itself.
- No choice of framework, model, file storage provider or insurer connection mechanism has been settled.

This architecture is a recommendation, not a validated technical decision nor proof that it works. Do not add Kafka, OpenSearch, ClickHouse or Valkey just to tick the sponsors' logos.

The Aiven administrative credentials used to deploy belong to the build tooling. **They must not become tools of the merchants' chatbot.** The application uses its own data and provider credentials.

## 9. Aiven — technical research to prepare the build

Official sources consulted on **22 October 2026**. This section describes what the documentation allows; it does not prove that the project's account already has the corresponding rights, credits or services.

### 9.1. Deployment constraint

**Management console: [console.aiven.io](https://console.aiven.io/). Required hosting: Aiven Runtime.** Using only Aiven PostgreSQL with the website hosted elsewhere would not, on its own, satisfy the brief's Runtime requirement.

Runtime runs containerised applications within the Aiven project. The documented path starts from a connected GitHub repository. Plan for a `Dockerfile`/`Containerfile`, and possibly a Compose file to describe the application and services. [Runtime overview](https://aiven.io/docs/products/runtime), [manifests](https://aiven.io/docs/products/runtime/manifest-files/manifests).

The GitHub link requires the administrator role of the Aiven organisation; a GitHub organisation also requires adequate permissions to install the Aiven Platform application. Its installation can be limited to selected repositories. A single GitHub account cannot be connected to several Aiven organisations according to the current documentation. [GitHub connection](https://aiven.io/docs/products/runtime/connect-github-account).

### 9.2. Aiven API first — Mathis's decision

**The main path for building and deploying is the Aiven REST API.** MCP and CLI remain available as alternatives; configuring them is not a prerequisite for moving forward if API access suffices.

Base: **`https://api.aiven.io/v1`**. The reference documents an `aivenv1` token scheme; the Runtime examples also use `Bearer`. Check the scheme suited to the provided token and the endpoint, without displaying the secret. [Official API reference](https://api.aiven.io/doc/).

Administration path to automate, subject to the account's rights:

1. Read the project, the existing services and the available configuration.
2. Check the `application` schema and the plans with `GET /project/{project}/service-types/application` and `GET /project/{project}/service-types/application/plans`.
3. Resolve the GitHub account and repository via `GET /organization/{organization_id}/application/vcs-integrations` and its sub-path `/{integration_id}/repositories`.
4. Create PostgreSQL then the application with `POST /project/{project}/service`, types `pg` and `application`; use the actual parameters for region, plan, repository, branch, Dockerfile, port and variables.
5. Link the database via the integration API described in 9.4.
6. Track state and logs; record the commit actually deployed.
7. After a code change, use `POST /project/{project}/service/{service_name}/application/redeploy`, checking its current schema.

Plan, configuration and redeploy operations are in the [official REST reference](https://rest.aiven.io/doc/). Runtime creation templates are in the [deployment guide](https://aiven.io/docs/products/runtime/deploy-apps). No authenticated call has been executed yet.

Deploying requires `project:services:write`, a project manager or project admin role. **A GitHub push does not automatically trigger deployment.** The initial GitHub installation remains a dependency to resolve; having a token does not prove the repository is already linked.

Personal tokens are created in the console, under the user section then Tokens. Application users exist for automation; the choice will depend on the access provided. [Create a token](https://aiven.io/docs/platform/howto/create_authentication_token), [application users](https://aiven.io/docs/platform/concepts/application-users).

CLI alternative: **`avn`**, package `aiven-client`, installable notably via `pip install aiven-client`. The documentation describes token login and JSON outputs. The command was not found in this session's PATH; no installation was done. [Official CLI](https://aiven.io/docs/tools/cli).

Useful documented commands if this alternative is chosen:

```sh
avn --version
avn user login EMAIL_ADDRESS --token
avn project switch PROJECT_NAME
avn service list --project PROJECT_NAME
avn service get APPLICATION_NAME --project PROJECT_NAME
avn service logs APPLICATION_NAME --project PROJECT_NAME
```

### 9.3. Official MCP alternative

Official hosted endpoint: **`https://mcp.aiven.live/mcp`**.

The organisation must allow MCP connections. Remote authentication uses OAuth 2.0 with PKCE. The MCP can inspect resources, manage services and deploy applications; a read-only mode is therefore not enough to build the resources. Effective permissions remain those of the account and the organisation. [Official MCP documentation](https://aiven.io/docs/tools/mcp-server).

The official repository documents in particular:

- `aiven_vcs_integration_list` and `aiven_vcs_integration_initialize`: linked GitHub accounts or connection to initiate;
- `aiven_vcs_integration_repository_list` and `aiven_vcs_integration_repository_scan_container_manifest`: repository and manifest;
- `aiven_application_create`: creation and first deployment of an application;
- `aiven_application_redeploy`: rebuild of an existing application;
- `aiven_service_get` and `aiven_project_get_service_logs`: state and diagnostics.

Names and parameters must be re-read in the tools actually exposed after connection. Documented scopes include `application`, `pg`, `integrations` and `core`. [Official MCP README](https://github.com/Aiven-Open/mcp-aiven/blob/main/README.md).

**Distinction:** this OAuth concerns the build tool's access to Aiven. It authenticates neither the merchant on our website nor the service with their insurer.

### 9.4. Packaging and database

Prepare an application that listens on an interface reachable inside the container, with the port explicitly declared, e.g. `8080`. Runtime detects ports from `EXPOSE`. [Containerfiles and Dockerfiles](https://aiven.io/docs/products/runtime/manifest-files/containerfiles).

Compose can describe an application built from the repository and the recognised data services. Runtime does not deploy an application directly from the `image` property alone: use a build/Dockerfile. The detected managed service does not necessarily follow the version stated in the image; check its effective version. [Compose on Runtime](https://aiven.io/docs/products/runtime/manifest-files/compose-files).

Link PostgreSQL to the application with the **`application_service_credential`** integration; the connection string can be exposed as `DATABASE_URL`. The corresponding command is `avn service integration-create`, and the API uses `POST /project/{project}/integration`.

Runtime does not automatically provide a pre-deploy migration command or one-off task. Choose migrations at startup or in CI; for several instances, plan for their coordination. When updating variables via API/CLI, check whether the existing list is replaced so as to preserve the other values. [Connecting services and migrations](https://aiven.io/docs/products/runtime/connect-services-to-apps).

### 9.5. Networking and product authentication

The public entry point is HTTPS on port 443; Aiven terminates TLS then forwards HTTP to the container's port. Exposed application ports are HTTP, with no announced support for TCP, gRPC or HTTP/2. Some outbound ports are blocked, notably 25 and 465: **plan for an HTTPS email API**. WebSocket support and the duration/volume limits needed for the project remain to be tested; do not infer their availability from the mere presence of HTTP. [Runtime ports](https://aiven.io/docs/products/runtime/ports).

Applications are publicly reachable by default. Runtime offers Aiven Identity, tied to the organisation's users/groups, or an OIDC provider. **These mechanisms do not automatically constitute merchant sign-up.** [Runtime authentication](https://aiven.io/docs/products/runtime/authentication/apps-authentication-overview).

Recommendation: authentication and customer separation inside the application; callback endpoints reachable by providers with validation of their signatures. Check that any global Runtime protection does not block the WhatsApp, email or voice webhooks.

### 9.6. Secrets, logs and operations

Store provider keys in variables marked as secret; connections of linked services can be exposed via integration. A change to variables redeploys the previously deployed commit, not necessarily the latest in the repository. [Runtime variables and secrets](https://aiven.io/docs/products/runtime/secrets-and-variables).

Build and run have separate logs. The API documents `POST /project/{project}/service/{service}/logs` with `log_type: application-build` or `application-run`. The announced native retention is twenty-four hours. **The customer's business history must be kept in our durable data, not in these logs.** [Runtime logs](https://aiven.io/docs/products/runtime/runtime-logs).

Changing the application's plan does not automatically adjust the plans of connected services. No price, region, credit amount or Runtime quota of the account has been confirmed. [Application plans](https://aiven.io/docs/products/runtime/scale-apps).

### 9.7. Recommended order once access is provided

1. Identify organisation, project, permissions, region and existing resources; record the credits/plans actually available.
2. Check the token and the necessary API operations first. Use MCP or CLI as an alternative if useful; do not wait for all three paths to be configured.
3. Link the appropriate GitHub repository via the authorised path and record branch/manifest.
4. Deploy a minimal application on Runtime very early and check its URL, port and commit.
5. Connect PostgreSQL, apply migrations and verify a test write/read as well as recovery after restart.
6. Add sign-up, profile, mandate and documents; validate the isolation of two demo accounts.
7. Hook up a WhatsApp channel that is actually available, then the compliant welcome message and memory resumption.
8. Add email/voice with authorised test counterparts, reply events and failure tracking.
9. Run the evidence cases and the demo; keep the observed results and the origin of the data.

These are proposed steps for the future build. Persistent file support, upload volumes, long-running task behaviour, any PostgreSQL extensions and provider access have not been validated on the account.

## 10. Business sources already identified

Sources consulted during the conversation; no functional verification of insurer portals has been done.

- [Official Accel/BuilderBase event](https://luma.com/0v3c010v).
- [MAAF — Multirisque Professionnelle general conditions, January 2026 edition, accessible version](https://handicapzero.maaf.fr/mon-activite-professionnelle/multirisque-professionnelle/conditions-generales-multirisque-professionnelle).
- [MAAF — premises and contents: subscribed covers specified in the policy schedule](https://handicapzero.maaf.fr/mon-activite-professionnelle/multirisque-professionnelle/conditions-generales-multirisque-professionnelle/vos-locaux-et-leur-contenu).
- [AXA — professional glass breakage declaration](https://www.axa.fr/professionnels/demarches/declaration-bris-glace.html).
- [CCI Paris Île-de-France — merchants affected by loss events](https://www.entreprises.cci-paris-idf.fr/commercants-sinistres).
- [France Assureurs — property damage linked to urban violence](https://www.franceassureurs.fr/lassurance-protege-finance-et-emploie/lassurance-protege/les-demarches-en-cas-de-sinistre/indemnisation-degats-materiels-provoques-violences-urbaines/).
- [Code civil, article 1984 — principle of the mandate](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006445236/).
- [CNIL — exercising the right of access through a representative](https://www.cnil.fr/fr/repondre-une-demande-de-droit-dacces). This topic concerns personal data; on its own it does not prove that a complete commercial file can be retrieved instantly.
- [Aiven Runtime — deploying an application](https://aiven.io/docs/products/runtime/deploy-apps).
- [Aiven Runtime — connecting data services](https://aiven.io/docs/products/runtime/connect-services-to-apps).
- [ElevenLabs — inbound/outbound Twilio telephony](https://elevenlabs.io/docs/eleven-agents/phone-numbers/twilio-integration/native-integration/).

## 11. Actual state of the work and requested next steps

The workspace contains research and reports on AI agents and solar files. It does not yet contain a claims-handling prototype, a WhatsApp/insurer connection, a configured voice agent or an executed benchmark.

The other ideas explored — personal brain, portable memory and solar file supplements — are historical context. **The active project is small-business insurance.**

Previous documents:

- [Research on AI agents](recherche-agents-ia.html).
- [Study of solar files](etude-dossiers-solaires.html).

The documentary research on the workflow was carried out in three parallel strands, then consolidated: [full workflow and sources](recherche-workflow-sinistres-commercants.md). It provides the details of clauses and fictional cases; the present document is the reference for the updated two-block product journey.

Main results to preserve, which do not constitute new decisions by Mathis:

- Declare quickly without waiting for all documents, then complete the file and keep proof of receipt.
- The recommended core is a **living statement of loss**: each item links actual damage, evidence, clause, calculation and next action.
- The MAAF January 2026 *conditions générales / CG* (general conditions) provide verified examples: displayed goods damaged by the breakage, boarding-up/security guard costs under conditions, VAT/deductibles and supplement after replacement. They do not transpose to all contracts.
- An accepted offer is not a payment received: track advances, direct payment to the repairer and any supplements separately.
- No universal delegated access to customer portals has been established. Credential-sharing restrictions and authentication must be handled per channel and per insurer; a mandate on its own does not provide technical access.
- WhatsApp imposes constraints on reply window, templates and sensitive identifiers. A protected upload area is recommended for a bank account statement (RIB) or identity document requested by the insurer.
- Twilio trial accounts limit recipients; telephony and WhatsApp media must be tested on the accounts actually available.
- Do not hard-code a universal clock. Rules differ according to the nature of the loss, the contract and the regime. The applicability of the decree planned for the new article L121-18 was not established in this research.

Two entirely fictional test cases are described: supplementary evidence after a shopfront breakage, and conditional supplement after equipment replacement. No real claim, insurer call, deployment or compensation result has been obtained.

**Mathis's latest request: this context Markdown, incorporating the onboarding website, the WhatsApp block and the in-depth Aiven research.** The next piece of work would be building and verifying the prototype once access is available; no cloud resource has been created at this stage.

## 12. Collaboration preferences to preserve

- Reply in French, concretely, with little jargon.
- This preference concerns our exchanges with Mathis: **the product's bot speaks English**.
- To build and deploy on Aiven, **API first**; MCP and CLI are alternative solutions.
- Priority to the product, the demo and the agent's operation.
- Do not impose a narrow commercial niche or an amount limit already refused by Mathis.
- Preserve the desired autonomy; do not reintroduce systematic human validation or a hidden team.
- Distinguish Mathis's decisions, the assistant's suggestions and things actually tested.
- Mathis invoked the **grill-me** skill: if the design interview resumes, ask one question at a time, with a recommendation; examine directly what can be examined rather than asking for facts already accessible.
- Requests for research, synthesis or files must be handled before resuming the interview.

## 13. Build decisions (22 October 2026, morning)

### 13.1. Chosen stack

| Component | Choice | Why / notes |
|---|---|---|
| **Merchant channel** | ~~WhatsApp Cloud API~~ → **Telegram Bot API** (noon decision, see §14) | Bot created via `@BotFather` in two minutes, no verification. Text, photos, documents, voice messages (`.oga`) via `getFile`. Long polling in dev, webhook in prod. Unrestricted outbound messages after `/start`. |
| **Email** | **AgentMail**: one mailbox per customer or file, sending and receiving via API, webhook on every received email | Free tier: 3 mailboxes, 100 emails/day, addresses on `@agentmail.to`. Sending goes over HTTPS, which works around the blocking of ports 25/465 on Runtime (§9.5). No access to the merchant's mailbox. |
| **Calls** | **ElevenLabs Agents**, with the file injected at call start (dynamic variables) | Free plan A: the call via the ElevenLabs **web widget** (browser), without a phone number. "Real phone" option: a **Twilio trial** number (free, no credit card; verified numbers only, 10 min max, a "trial" message read at the start of the call). Use the ElevenLabs credits from the Builders Pack. |
| **LLM + OCR** | **Claude**: agent loop with tools, and vision to extract text from photos, invoices and police reports into structured JSON | Extraction from images is at the heart of the "the agent does everything" promise. |
| **Data** | **Aiven PostgreSQL**: accounts, contracts split into clauses with page, files, documents, facts, exchanges, actions, memory | Clauses are searched by full text, and/or with pgvector if the extension is available. |
| **Hosting** | **Aiven Runtime** (brief requirement) | GitHub must be linked first (admin role required, §9.1). |

### 13.2. Real data corpus (in this repo)

- **`data/contrats/txt/`**: 12 **public** contractual documents for commercial multi-risk insurance, extracted with `pdftotext -layout`. Original sources:
  - Generali 100% Pro GA5M70F (72 pp.): https://www.air-assurances.com/pdf_doc/hangar_2022/CG_GA5M70F.pdf
  - AXA Atouts PME (88 pp.): https://media.axa.fr/content/dam/axa-fr/image/pro/documents-informations/pdf-assurance-atout-pro-pme-cg.pdf
  - AXA Mon Pack Entrepreneur (108 pp.): https://media.axa.fr/content/dam/axa-fr/image/pro/documents-informations/pdf-mon-pack-entrepreneur-cg.pdf
  - Allianz Actif Pro (124 pp.; services and liberal professions contract, not the merchant contract, which is not published): https://www.gpm.fr/wp-content/uploads/2026/06/CG-MRP-ALLIANZ.pdf
  - Sogessur / Société Générale, Commerçants Artisans (2016): https://static.societegenerale.fr/pro/PRO/Repertoire_par_type_de_contenus/Fichier_a_telecharger/Fiches_numeriques/cg-commercants-artisants.pdf
  - Groupama, common provisions only (the text of the covers is not available): https://www.coover.fr/wp-content/uploads/2019/10/conditions-generales-responsabilite-civile-professionnelle-groupama.pdf
  - MAAF Multirisque Pro 11031 (01/2026): https://www.maaf.fr/fr/files/live/sites/maaf/files/DOCUMENTS/Professionnels/CG/MAAF_Conditions_generales_Multirisque_pro_11031.pdf
  - MMA Pro-PME 352 pp. (04/2021): https://philtr.fr/static/pdf/insurance/mrp/mma_mrp.pdf
  - Hiscox (CG, Special Conventions MRP0623, IPID): https://www.hiscox.fr/courtage/sites/courtage/files/documents/MRP0623%20-%20Conventions%20Speciales%20Multirisques%20Dommages%20aux%20Biens%20Professionnels%20.pdf
  - Pacifica / Crédit Agricole (IPID only): https://www.credit-agricole.fr/content/dam/assetsca/master/public/commun/documents/7197A.36_IPA_doc%20info_M9_PRO-122020-BD.pdf
- **`data/research/08a_*` and `08b_*`**: for each contract, the clauses useful after looting or vandalism, with a short quotation and page, plus a cross-table of "often-forgotten items". Examples **verified in the text**:
  - **MMA** reimburses the *expert d'assuré* (policyholder's loss assessor) chosen by the insured up to 10% of the compensation, capped at €40,000, if the option was subscribed.
  - **Generali** applies a loss assessor fee scale of 5% up to €350,000.
  - **Sogessur** excludes « les vols ou tentatives de vol, survenus lors d'émeutes » (thefts or attempted thefts occurring during riots).
- **`data/research/08c_*`**: real testimonies (2023 and October 2026), case law (numbers to be checked on Légifrance before display) and **3 quantified composite cases** (smartphone repairer, bakery, optician) which serve as the basis for the benchmark.
- **`data/research/08d_*`**: the claims process, compensation calculation, regulation (mandate, legal advice, ORIAS), competition, market size and 10 answers to a VC partner's questions.

### 13.3. What the benchmark must show

The benchmark is detailed in §7. Key figures to display on the slide:

- the **recall of claimable items**, with the correct page;
- the **€ identified** in three versions: naive declaration, LLM alone, our agent;
- the **time to assemble the file**, agent versus manual: photos and invoices read automatically, documents attached, each item quantified and cited;
- the **cost per file**.

## 14. Chosen architecture and build plan (22 October 2026, noon)

This section supersedes any points in the previous sections that it contradicts. It results from a scoping session with the team on the day of the hackathon. The choices below are **decisions**, unless marked "to verify".

### 14.1. What we are building, in one sentence

An **agentic system** that, for each merchant, instantiates an agent with its own memory, its own mailbox and its own tools; this agent runs in **its own loop** per claim file, from the declaration to a compensation proposal, handling the back-and-forth itself (documents from the customer, emails and calls to the insurer, reviews, follow-ups), and only hands back to the merchant at the time of the offer.

### 14.2. Decisions taken during scoping

| Topic | Decision | Why |
|---|---|---|
| Merchant channel | **Telegram** (Bot API) | WhatsApp Cloud API takes too long to obtain. Telegram: immediate token, long polling without a public URL, unrestricted outbound messages, deep link to link the web account. Pitch narrative: "the channel layer is 200 lines; WhatsApp as soon as Meta approves". |
| Onboarding | **Stays on the website** (block 1 confirmed): account, phone, contracts, identity, **signed mandate**, history, then Telegram linking | Explicit team decision. This is when the agent is created, receives its mailbox and builds its initial memory. |
| Insurer side | **Emails: simulated insurer** via a second agent. **Voice call: a team member plays the insurer** live | Emails must be reproducible during a 5-minute pitch; the call is the "live" moment. The simulator is named as such in front of the jury. |
| Language | **Python 3.12** | PDF/page processing, Anthropic SDK, `python-telegram-bot`, native LangGraph. |
| Agent framework | **LangGraph** (+ `langchain-anthropic`), explicitly written graphs, no generic ReAct agent | Team decision. Good fit: the **Postgres checkpointer** persists each file's state in Aiven PG, `interrupt()` natively models waits (document from the customer, email reply, decision on the offer). |
| Topology | **A single FastAPI service** on Runtime: website + webhooks + worker in the same process | One Dockerfile, one deployment, all state in the database. Two services would be cleaner, not today. |
| Demo case | **Case A "Karim"** (smartphones, Marseille) on **MAAF CG 11031 (01/2026)** + synthetic policy schedule | Most recent contract in the corpus, clauses already verified, most striking gap (€38,100 declared alone vs ≈ €89,700 defensible, `08c` §6). |
| Model | Claude (text + vision) via `langchain-anthropic` | Vision for invoices, photos, police reports. |
| LangSmith | Optional, bonus to show traces | Not a dependency. |

### 14.3. The agents and their memory

Three distinct LangGraph agents, which communicate only through the database and the real channels (email), never by direct call:

**A. Intake Agent** — runs once at the end of web onboarding, then on every new document.
Input: the uploaded PDFs. Output: the business's **initial memory**. It classifies each document (CG, CP, endorsement, IPID, incident report, correspondence), splits it into **paginated clauses**, extracts the coverage profile (subscribed covers, caps, deductibles, options, notable exclusions) **with source page and confidence level**, spots missing documents (e.g. CP missing → task), and prepares the welcome message. It never infers that an option is not subscribed because the page is missing.

**B. Claims Agent** — one **LangGraph thread per file** (`thread_id = claim_id`). This is the main loop.
Nodes:
1. `load_memory` — loads the business profile, the coverage profile, the current file (facts, documents, statement of loss, actions, exchanges).
2. `triage` — qualifies the incoming event (new document, email reply, call result, customer question, scheduled follow-up) and decides: reply, update, act, or wait.
3. `analyze` — updates the facts and **the statement of loss**: each item = evidence + clause (page) + calculation + any condition. Deduplicates documents (hash + amount/date/supplier). Flags contradictions and missing documents.
4. `act` — chooses and executes one or more tools (below).
5. `review` — separate control node: checks that every item has evidence and an existing clause, that the cited pages actually contain what is asserted, that no amount is counted twice, and that no outbound email promises or accepts anything. Sends back to `analyze` on failure.
6. `wait` — typed `interrupt()`: `awaiting_client`, `awaiting_insurer_email`, `awaiting_call_result`, `awaiting_followup`. The graph is persisted; a webhook or the scheduler issues `Command(resume=payload)`.
7. `present_offer` — end of loop: summarises the offer, the gap versus the statement of loss, the levers, and puts the question to the merchant. **Silence is never acceptance.** After the decision: `contest` restarts the loop, `accept` moves the file to payment tracking.

Claims Agent tools (Python `@tool` functions, each writing a row to `actions`):
`get_claim_memory`, `search_clauses(contract_id, query)`, `read_document(doc_id)` (vision → structured JSON), `update_loss_statement(items)`, `ask_client(text, requested_items)`, `send_email(to, subject, body, attachment_ids)`, `start_call(goal, questions)`, `schedule_followup(when, reason)`, `log_fact(fact, source, confidence)`, `present_offer(offer_id)`.

**C. Insurer Simulator Agent** — a separate graph, with its own AgentMail mailbox (`sinistres-demo@agentmail.to` or equivalent), **labelled "simulated insurer"** in the UI and the pitch.
It reads received emails, follows a script configurable per scenario (acknowledgement → document request → capped offer) and replies after a short delay. It **never** sees the Claims Agent's memory: it only has the emails. It allows the demo to be replayed identically.

**Memory, two levels:**
- **Durable memory (our PG tables)**: business, representatives, mandate, mailbox, contracts and clauses, files, documents, facts, statement of loss, exchanges, actions, offers. This is the source of truth, readable by the jury. A correction creates a new version; it does not overwrite.
- **Execution state (LangGraph checkpointer in the same database)**: where each thread is, what it is waiting on. Enables recovery after restart and pause/resume on external events. The LangGraph Store can be used for cross-thread memory (business profile), **to verify** depending on the installed version; otherwise read the tables directly.

### 14.4. Data model (Aiven PostgreSQL)

Main tables, all with `id`, `created_at`, and `account_id` for isolation between customers:

- `accounts` (email, password hash), `businesses` (name, SIRET, address, owner, phone, insurer, broker), `mandates` (version, scope, signatory, timestamp, proof, revocation), `consents` (mandate / Telegram / data, separate).
- `mailboxes` (AgentMail address, identifier, role `agent` or `simulated_insurer`).
- `telegram_links` (chat_id, linking code, state), `link_codes` (single-use deep link code).
- `documents` (type, origin, version, document date, hash, `bytea` content for today, extracted text), `clauses` (document_id, page, title, text, `tsvector`).
- `coverage_profile` (cover, subscribed?, cap, deductible, conditions, source clause_id, confidence).
- `claims` (status, date of loss, nature, summary), `facts` (text, source, confidence, status, `supersedes`), `evidence` (document_id, type, amount, date, supplier, hash, `duplicate_of`), `loss_items` (item, amount claimed, evidence_ids, clause_id, calculation, condition, status), `communications` (channel, direction, recipient, content, acknowledgement, failure), `calls` (goal, questions, transcript, structured result, confidence), `actions` (tool, arguments, result, triggering event), `scheduled_tasks` (when, reason, state), `offers` (amounts per item, gap, customer decision, timestamp).
- `events` (source, raw payload, state `pending/processing/done/failed`): queue consumed by the worker with `SELECT … FOR UPDATE SKIP LOCKED`.
- LangGraph checkpointer tables (created by the library).

Clause search: Postgres full-text (`tsvector`, `french` dictionary). pgvector only if time allows; 12 contracts do not need it.

### 14.5. Event flow

```
Telegram update ─┐
AgentMail webhook ─┼─> INSERT events ─> worker (asyncio, same process)
ElevenLabs post-call ┤                      │
scheduler (follow-ups) ┘                    ├─ existing thread waiting? ─> Command(resume=…)
                                            └─ otherwise ─> new graph run
                                                        │
                                            tools ─> PG (actions, communications, …) ─> Telegram / AgentMail / ElevenLabs
```

- Webhooks respond in under one second; all long work happens in the worker.
- Each action is only marked as done once the result is observed (AgentMail acknowledgement, Telegram `message_id`, end of call).
- AgentMail/ElevenLabs webhook signatures are verified; the Telegram token serves as the URL secret if we switch to webhook mode.

### 14.6. External integrations

- **Telegram**: `python-telegram-bot`. Long polling while developing; webhook on the Runtime URL once deployed. Media downloaded via `getFile`, stored in `documents`. **Voice messages**: `.oga` Opus → transcription by ElevenLabs Scribe (Builders Pack credits) or Whisper; Claude does not process audio.
- **AgentMail**: one mailbox created per account at the end of onboarding (free tier limit: 3 mailboxes → one for Karim, one for the simulated insurer, one spare). "Message received" webhook → `events`. Sending over HTTPS, Runtime-compatible.
- **ElevenLabs Agents**: outbound call to the verified number of the teammate playing the insurer (Twilio trial); dynamic variables = goal, questions, file summary; **post-call webhook** with transcript and structured result → `events`. Fallback if telephony fails: ElevenLabs web widget projected on screen. Every oral answer is stored with provenance "oral, unconfirmed" and triggers a request for written confirmation.
- **Claude** via `langchain-anthropic`; vision for invoices/photos/police reports; structured outputs for facts and items.

### 14.7. Demo scenario (≈ 5 minutes)

Persona: Karim, smartphone repair and resale, Marseille city centre. Contract: MAAF CG 11031 (01/2026) + **one-page synthetic CP**: riots and civil commotion extension, theft capped at €15,000, *perte d'exploitation / PE* (business interruption) subscribed with a 3-day *franchise* (deductible), *valeur à neuf* (replacement-as-new value) for equipment, general deductible €1,000.

**Block 1 — website (≈ 1 min 30)**
1. Account (email + password).
2. Shop: name, SIRET, address, owner, phone, insurer.
3. Upload: MAAF CG, Karim's CP, an old piece of correspondence (optional).
4. Mandate displayed, three separate checkboxes (mandate, Telegram, data), typed name + timestamp.
5. Validation → AgentMail mailbox created, Intake Agent starts ingestion, coverage profile displayed with source pages.
6. "Open Telegram" button (deep link). `/start` links the chat; the agent says hello **in English** and summarises what it understood from the contract.

**Block 2 — Telegram (≈ 3 min)**
7. Karim: "My shop was looted Saturday night" + 3 photos + 2 supplier invoices.
8. The agent opens the file, extracts facts and amounts, **sends the initial declaration by email** to the simulated insurer, requests the missing documents (inventory, till export, customer devices under repair, police complaint).
9. Karim re-sends an invoice already sent → **no duplicate**, the agent says so.
10. The simulated insurer replies: asks for the number of customer devices and the complaint. The agent relays to Karim, updates the file.
11. **ElevenLabs call to the insurer (played by the team)**: "Does the riot extension apply to stock, or the €15,000 theft cap?". The answer enters memory with oral provenance; the agent requests written confirmation by email.
12. The simulated insurer sends an offer of ≈ €20,750. The agent **stops and hands back**: offer, amount supported by the statement of loss, main gap (stock capped under theft instead of riots), proposal to contest or to see the details. Karim decides.

**"Data" moments to show**: the rejected duplicate; the endorsement/CP that changes a cap; session resumption (restart the service during the demo and show that the thread resumes); the oral answer that does not modify the contract until it is in writing.

### 14.8. Benchmark (evidence slide)

`bench/` script run on the 3 composite cases of `08c` §6 (A Karim, B Boulangerie Martin, C Optique Pauline), each crossed with its contract:

| Variant | Input | What we measure |
|---|---|---|
| Naive declaration | the "declared alone" column of `08c` | € declared |
| LLM alone | same model, same account of events, **without** access to clauses or invoices | € identified, items found, fabricated citations |
| Claims Agent | account of events + documents + contract via tools | € identified, **recall of claimable items**, **% of correct citations** (page exists and says what is asserted), token cost, latency |

Ground truth: `08a_*`, `08b_*` (clauses and pages) and `08c` §6 (items). The "timed manual time" from §7 is **removed** from today's benchmark: not honestly feasible in one day. No figure is displayed before it has been measured.

### 14.9. Aiven deployment

- Project `larp`, PG `pg-3f9bc500` already running. Create the Runtime application from the GitHub repository (prerequisites: Aiven organisation admin + GitHub app installation), `Dockerfile` at the root, `EXPOSE 8080`, `application_service_credential` integration → `DATABASE_URL`.
- Migrations at startup (single instance). Secrets (Anthropic, Telegram, AgentMail, ElevenLabs) in variables marked as secret.
- Deployment is not automatic on push: `redeploy` via API after each change.
- Runtime logs retained 24 h: business history is in the database, not in the logs.

### 14.10. Build order

1. **Skeleton + Aiven** (blocking, do first): FastAPI "hello", Dockerfile, Runtime deployment, PG linked, test migration, read/write verified. If the GitHub link blocks, we know before noon.
2. **Ingestion**: splitting the 12 CG into paginated clauses (`\f` from `pdftotext -layout`), full-text, Intake Agent on MAAF + Karim's CP, coverage profile with pages.
3. **Minimal Claims Agent**: `load_memory → analyze → review → present` graph on a seeded file, tools `search_clauses`, `read_document`, `update_loss_statement`. Statement of loss cited page by page. **This is the core; everything else can be degraded, not this.**
4. **Telegram**: deep link linking, incoming text/photos/documents, `ask_client`, `interrupt`/`resume` on customer reply, deduplication.
5. **Benchmark**: script, 3 cases, figures for the slide.
6. **AgentMail**: mailbox per account, `send_email`, inbound webhook, Insurer Simulator Agent.
7. **Onboarding website**: 4 steps, mandate, consents, Intake Agent trigger, final screen with deep link.
8. **ElevenLabs**: outbound call, post-call webhook, oral provenance.
9. **Telegram voice messages** (transcription), demonstrated recovery after restart, pitch polish.

If time runs short: 8 becomes a web widget or a slide; 9 is skipped; 7 can be reduced to a single page. 1 to 5 are non-negotiable.

### 14.11. What remains open

- Who on the team has the Aiven organisation admin role for the GitHub link.
- Verified Twilio trial number for the call; ElevenLabs credits actually available.
- Telegram bot name and product name (none settled).
- LangGraph Store for cross-thread memory vs direct table reads: decide at installation depending on the version.
- Mandate signature mechanism: checkbox + typed name + timestamp for the demo; qualified electronic signature later.
