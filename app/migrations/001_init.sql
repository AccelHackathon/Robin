CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Event queue consumed by the in-process worker (SELECT ... FOR UPDATE SKIP LOCKED)
CREATE TABLE IF NOT EXISTS events (
    id            bigserial PRIMARY KEY,
    source        text NOT NULL,              -- telegram | agentmail | elevenlabs | scheduler | web
    kind          text NOT NULL,              -- message | document | email_received | call_ended | followup_due | onboarding_done
    account_id    uuid,
    claim_id      uuid,
    payload       jsonb NOT NULL DEFAULT '{}'::jsonb,
    status        text NOT NULL DEFAULT 'pending',  -- pending | processing | done | failed
    attempts      int NOT NULL DEFAULT 0,
    error         text,
    created_at    timestamptz NOT NULL DEFAULT now(),
    processed_at  timestamptz
);
CREATE INDEX IF NOT EXISTS events_pending_idx ON events (status, created_at) WHERE status = 'pending';

-- Identity and onboarding
CREATE TABLE IF NOT EXISTS accounts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email         text UNIQUE NOT NULL,
    password_hash text NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS businesses (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    name          text NOT NULL,
    siret         text,
    address       text,
    activity      text,
    representative_name text,
    representative_role text,
    phone         text,
    insurer_name  text,
    insurer_contact_email text,
    broker_name   text,
    tenant_or_owner text,
    vat_recoverable boolean,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mandates (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    version       text NOT NULL,
    scope         jsonb NOT NULL,
    signer_name   text NOT NULL,
    signer_role   text,
    signed_at     timestamptz NOT NULL DEFAULT now(),
    proof         jsonb NOT NULL DEFAULT '{}'::jsonb,
    revoked_at    timestamptz
);

CREATE TABLE IF NOT EXISTS consents (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    purpose       text NOT NULL,              -- mandate | telegram | data_processing
    granted_at    timestamptz NOT NULL DEFAULT now(),
    revoked_at    timestamptz
);

CREATE TABLE IF NOT EXISTS mailboxes (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid REFERENCES accounts(id),
    address       text UNIQUE NOT NULL,
    provider_id   text,
    role          text NOT NULL DEFAULT 'agent',  -- agent | simulated_insurer
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS link_codes (
    code          text PRIMARY KEY,
    account_id    uuid NOT NULL REFERENCES accounts(id),
    created_at    timestamptz NOT NULL DEFAULT now(),
    used_at       timestamptz
);

CREATE TABLE IF NOT EXISTS telegram_links (
    chat_id       bigint PRIMARY KEY,
    account_id    uuid NOT NULL REFERENCES accounts(id),
    username      text,
    linked_at     timestamptz NOT NULL DEFAULT now()
);

-- Documents and contract knowledge
CREATE TABLE IF NOT EXISTS documents (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid REFERENCES accounts(id),   -- NULL for public corpus (general conditions)
    claim_id      uuid,
    doc_type      text NOT NULL,              -- general_conditions | particular_conditions | endorsement | ipid | invoice | photo | police_report | correspondence | other
    origin        text NOT NULL,              -- web_upload | telegram | email | corpus
    filename      text,
    mime_type     text,
    sha256        text NOT NULL,
    content       bytea,
    extracted_text text,
    document_date date,
    version_label text,
    insurer_name  text,
    product_name  text,
    page_count    int,
    metadata      jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS documents_account_idx ON documents (account_id);
CREATE INDEX IF NOT EXISTS documents_claim_idx ON documents (claim_id);
CREATE INDEX IF NOT EXISTS documents_sha_idx ON documents (account_id, sha256);

CREATE TABLE IF NOT EXISTS clauses (
    id            bigserial PRIMARY KEY,
    document_id   uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page          int NOT NULL,
    heading       text,
    body          text NOT NULL,
    tsv           tsvector GENERATED ALWAYS AS (to_tsvector('french', coalesce(heading, '') || ' ' || body)) STORED
);
CREATE INDEX IF NOT EXISTS clauses_tsv_idx ON clauses USING gin (tsv);
CREATE INDEX IF NOT EXISTS clauses_doc_page_idx ON clauses (document_id, page);

CREATE TABLE IF NOT EXISTS coverage_profile (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    guarantee     text NOT NULL,
    subscribed    boolean,                    -- NULL = unknown, never inferred from a missing page
    ceiling_eur   numeric,
    deductible    text,
    conditions    text,
    source_clause_id bigint REFERENCES clauses(id),
    source_document_id uuid REFERENCES documents(id),
    confidence    text NOT NULL DEFAULT 'extracted',  -- extracted | confirmed | assumed
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- Claims
CREATE TABLE IF NOT EXISTS claims (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    status        text NOT NULL DEFAULT 'open',  -- open | declared | awaiting_client | awaiting_insurer | offer_received | accepted | contested | closed
    loss_date     date,
    loss_type     text,
    summary       text,
    insurer_reference text,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS facts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    statement     text NOT NULL,
    source        text NOT NULL,              -- client_message | document:<id> | call:<id> | email:<id> | inference
    confidence    text NOT NULL DEFAULT 'reported',  -- reported | documented | oral_unconfirmed | confirmed_written | disputed
    status        text NOT NULL DEFAULT 'active',    -- active | superseded | retracted
    supersedes    uuid REFERENCES facts(id),
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    document_id   uuid NOT NULL REFERENCES documents(id),
    evidence_type text NOT NULL,              -- invoice | photo | quote | inventory | police_report | bank_statement | other
    amount_eur    numeric,
    currency      text DEFAULT 'EUR',
    issued_on     date,
    vendor        text,
    description   text,
    extracted     jsonb NOT NULL DEFAULT '{}'::jsonb,
    duplicate_of  uuid REFERENCES evidence(id),
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS loss_items (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    label         text NOT NULL,
    category      text,
    amount_claimed_eur numeric,
    computation   text,
    evidence_ids  uuid[] NOT NULL DEFAULT '{}',
    clause_id     bigint REFERENCES clauses(id),
    clause_page   int,
    clause_quote  text,
    condition_note text,
    status        text NOT NULL DEFAULT 'draft',  -- draft | supported | missing_evidence | submitted | accepted | rejected
    version       int NOT NULL DEFAULT 1,
    supersedes    uuid REFERENCES loss_items(id),
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS communications (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    claim_id      uuid REFERENCES claims(id),
    channel       text NOT NULL,              -- telegram | email | phone
    direction     text NOT NULL,              -- inbound | outbound
    counterpart   text,
    subject       text,
    body          text,
    attachments   uuid[] NOT NULL DEFAULT '{}',
    provider_ref  text,
    delivery_status text,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS calls (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    goal          text NOT NULL,
    questions     jsonb NOT NULL DEFAULT '[]'::jsonb,
    provider_ref  text,
    transcript    text,
    result        jsonb,
    status        text NOT NULL DEFAULT 'requested',  -- requested | in_progress | completed | failed
    created_at    timestamptz NOT NULL DEFAULT now(),
    ended_at      timestamptz
);

CREATE TABLE IF NOT EXISTS actions (
    id            bigserial PRIMARY KEY,
    claim_id      uuid REFERENCES claims(id),
    account_id    uuid REFERENCES accounts(id),
    agent         text NOT NULL,              -- intake | claims | insurer_sim
    tool          text NOT NULL,
    arguments     jsonb NOT NULL DEFAULT '{}'::jsonb,
    result        jsonb,
    ok            boolean,
    trigger_event_id bigint REFERENCES events(id),
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    due_at        timestamptz NOT NULL,
    reason        text NOT NULL,
    status        text NOT NULL DEFAULT 'pending',  -- pending | fired | cancelled
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS scheduled_tasks_due_idx ON scheduled_tasks (due_at) WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS offers (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id      uuid NOT NULL REFERENCES claims(id),
    source_communication_id uuid REFERENCES communications(id),
    total_eur     numeric,
    breakdown     jsonb NOT NULL DEFAULT '[]'::jsonb,
    gap_analysis  jsonb,
    client_decision text,                     -- NULL (no answer is never acceptance) | accept | contest | ask_detail
    decided_at    timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);
