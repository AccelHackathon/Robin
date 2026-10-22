-- B: durable onboarding, private sessions and Intake handoffs. Additive only.
CREATE TABLE IF NOT EXISTS web_sessions (
    token_hash text PRIMARY KEY,
    account_id uuid NOT NULL REFERENCES accounts(id),
    csrf_token text NOT NULL,
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS web_sessions_account_idx ON web_sessions(account_id);
CREATE TABLE IF NOT EXISTS onboarding (
    account_id uuid PRIMARY KEY REFERENCES accounts(id),
    step text NOT NULL DEFAULT 'business',
    urgent boolean NOT NULL DEFAULT false,
    incident text,
    completed_at timestamptz,
    intake_status text NOT NULL DEFAULT 'pending',
    intake_error text,
    welcome_brief text,
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS account_contracts (
    account_id uuid NOT NULL REFERENCES accounts(id),
    document_id uuid NOT NULL REFERENCES documents(id),
    PRIMARY KEY(account_id, document_id)
);
CREATE TABLE IF NOT EXISTS intake_tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id uuid NOT NULL REFERENCES accounts(id),
    key text NOT NULL,
    description text NOT NULL,
    resolved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(account_id, key)
);
CREATE TABLE IF NOT EXISTS deadline_rules (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id uuid NOT NULL REFERENCES accounts(id),
    document_id uuid NOT NULL REFERENCES documents(id),
    kind text NOT NULL,
    rule jsonb NOT NULL,
    source_clause_id bigint NOT NULL REFERENCES clauses(id),
    quote text NOT NULL,
    page int NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(account_id, source_clause_id, kind)
);
CREATE TABLE IF NOT EXISTS intake_cache (
    cache_key text PRIMARY KEY,
    result jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE consents ADD COLUMN IF NOT EXISTS version text;
ALTER TABLE claims ADD COLUMN IF NOT EXISTS tracking_token_hash text;
CREATE UNIQUE INDEX IF NOT EXISTS claims_tracking_token_idx ON claims(tracking_token_hash) WHERE tracking_token_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS coverage_account_guarantee_idx ON coverage_profile(account_id, guarantee, version DESC);
-- The shared worker dispatches a single handler per source/kind. Fan out transactionally:
-- A retains web/onboarding_done; B consumes web/document_added for both entry points.
CREATE OR REPLACE FUNCTION b_enqueue_onboarding_intake() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF NEW.source = 'web' AND NEW.kind = 'onboarding_done' THEN
    INSERT INTO events(source,kind,account_id,payload)
    VALUES ('web','document_added',NEW.account_id,jsonb_build_object(
      'account_id',NEW.account_id,'reason','onboarding_done','provider_ref','b-intake-onboarding-' || NEW.id));
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER b_onboarding_intake AFTER INSERT ON events FOR EACH ROW EXECUTE FUNCTION b_enqueue_onboarding_intake();
