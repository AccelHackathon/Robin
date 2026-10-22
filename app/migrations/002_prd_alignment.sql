-- Aligns the schema with docs/prd/2026-10-22-robin-claims-agent/PRD.md §3.4. Additive only.

-- Contract levers and traps detected by the Intake Agent (PRD 2.2 steps 5-6)
CREATE TABLE IF NOT EXISTS contract_levers (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid REFERENCES accounts(id),       -- NULL for public corpus documents
    document_id   uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    kind          text NOT NULL,   -- no_proportional_rule | assessor_fees | single_deductible | indirect_losses_10pct | bi_advances | trap.<name>
    present       boolean,
    detail        jsonb NOT NULL DEFAULT '{}'::jsonb,
    clause_id     bigint REFERENCES clauses(id),
    page          int,
    quote         text,
    confidence    text NOT NULL DEFAULT 'extracted',
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS contract_levers_doc_idx ON contract_levers (document_id);

-- Coverage profile: PRD wants versioning, structured ceiling/deductible and verbatim quote
ALTER TABLE coverage_profile
    ADD COLUMN IF NOT EXISTS version int NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS ceiling jsonb,
    ADD COLUMN IF NOT EXISTS deductible_detail jsonb,
    ADD COLUMN IF NOT EXISTS exclusions jsonb NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS quote text,
    ADD COLUMN IF NOT EXISTS page int,
    ADD COLUMN IF NOT EXISTS supersedes uuid REFERENCES coverage_profile(id);

-- Documents: validity window and readability flag (PRD 2.2 failure mode)
ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS valid_from date,
    ADD COLUMN IF NOT EXISTS valid_to date,
    ADD COLUMN IF NOT EXISTS readable boolean NOT NULL DEFAULT true;

-- Review gate log (PRD 2.7)
CREATE TABLE IF NOT EXISTS review_log (
    id            bigserial PRIMARY KEY,
    account_id    uuid REFERENCES accounts(id),
    claim_id      uuid REFERENCES claims(id),
    channel       text NOT NULL,                      -- telegram | email | phone_brief | prefect_letter
    draft         text NOT NULL,
    passed        boolean NOT NULL,
    violations    jsonb NOT NULL DEFAULT '[]'::jsonb,
    rewrite       text,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS review_log_claim_idx ON review_log (claim_id);

-- Payments tracked separately from offers (an accepted offer is not money received)
CREATE TABLE IF NOT EXISTS payments (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    offer_id      uuid REFERENCES offers(id),
    amount_eur    numeric NOT NULL,
    kind          text NOT NULL,                      -- advance | direct_to_repairer | indemnity | replacement_value_top_up
    received_at   timestamptz,
    evidence_document_id uuid REFERENCES documents(id),
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- Known riot / unrest events enabling the State recourse module (PRD 2.10)
CREATE TABLE IF NOT EXISTS riot_events (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name          text NOT NULL,
    started_at    timestamptz NOT NULL,
    ended_at      timestamptz,
    cities        text[] NOT NULL DEFAULT '{}',
    declaration_deadline_days int,                    -- e.g. 30 announced by France Assureurs for 17-18/10/2026
    state_claim_deadline date,                        -- L211-10 CSI four-year prescription
    sources        jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at    timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE claims ADD COLUMN IF NOT EXISTS riot_event_id uuid REFERENCES riot_events(id);

-- Catalogue of claimable items the agent walks through for every claim (PRD 2.4)
CREATE TABLE IF NOT EXISTS loss_catalog (
    key           text PRIMARY KEY,                   -- e.g. stock, bailed_goods, shopfront_glass, security_guarding
    label_en      text NOT NULL,
    label_fr      text NOT NULL,
    category      text NOT NULL,                      -- property | contents | fees | business_interruption | recourse
    typical_evidence text[] NOT NULL DEFAULT '{}',
    often_forgotten boolean NOT NULL DEFAULT false,
    notes         text,
    source_ref    text                                -- research file + section
);

-- Offers: nature and release-language detection (PRD 2.9)
ALTER TABLE offers
    ADD COLUMN IF NOT EXISTS received_at timestamptz,
    ADD COLUMN IF NOT EXISTS nature text,             -- advance | provisional | final
    ADD COLUMN IF NOT EXISTS has_release_language boolean,
    ADD COLUMN IF NOT EXISTS release_terms text,
    ADD COLUMN IF NOT EXISTS source_document_id uuid REFERENCES documents(id);

-- Facts: PRD source vocabulary
ALTER TABLE facts ADD COLUMN IF NOT EXISTS source_kind text;
-- source_kind: document | client | client_instruction | insurer_email | insurer_oral | agent_inference

-- Loss items: basis of the amount and structured computation
ALTER TABLE loss_items
    ADD COLUMN IF NOT EXISTS amount_basis text,       -- purchase_price | replacement_value | invoice | formula
    ADD COLUMN IF NOT EXISTS computation_detail jsonb,
    ADD COLUMN IF NOT EXISTS catalog_key text REFERENCES loss_catalog(key);

-- Actions: cost and latency for the benchmark and observability
ALTER TABLE actions
    ADD COLUMN IF NOT EXISTS tokens_in int,
    ADD COLUMN IF NOT EXISTS tokens_out int,
    ADD COLUMN IF NOT EXISTS latency_ms int,
    ADD COLUMN IF NOT EXISTS model text;

-- Scheduled tasks: deadline machine (PRD 2.5)
ALTER TABLE scheduled_tasks
    ADD COLUMN IF NOT EXISTS kind text,               -- police_report | declaration | loss_statement | insurer_followup | payment | replacement_value_top_up | prescription_alert | state_recourse | client_reminder
    ADD COLUMN IF NOT EXISTS source_clause_id bigint REFERENCES clauses(id),
    ADD COLUMN IF NOT EXISTS legal_basis text,
    ADD COLUMN IF NOT EXISTS missed_at timestamptz;

-- Communications: delivery and the insurer's verbatim position
ALTER TABLE communications
    ADD COLUMN IF NOT EXISTS failed_reason text,
    ADD COLUMN IF NOT EXISTS insurer_position_verbatim text,
    ADD COLUMN IF NOT EXISTS language text;           -- en | fr

-- Link codes expire
ALTER TABLE link_codes ADD COLUMN IF NOT EXISTS expires_at timestamptz;

-- Idempotency for inbound provider events
CREATE UNIQUE INDEX IF NOT EXISTS events_provider_ref_idx ON events ((payload->>'provider_ref')) WHERE payload ? 'provider_ref';
