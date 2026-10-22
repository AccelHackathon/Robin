-- Workstream A: voice (ElevenLabs/Twilio) and email (AgentMail). Additive only.

ALTER TABLE calls
    ADD COLUMN IF NOT EXISTS account_id uuid REFERENCES accounts(id),
    ADD COLUMN IF NOT EXISTS to_number text,
    ADD COLUMN IF NOT EXISTS from_number text,
    ADD COLUMN IF NOT EXISTS twilio_call_sid text,
    ADD COLUMN IF NOT EXISTS brief jsonb NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS duration_secs int,
    ADD COLUMN IF NOT EXISTS summary text,
    ADD COLUMN IF NOT EXISTS failure_reason text;
CREATE UNIQUE INDEX IF NOT EXISTS calls_provider_ref_idx ON calls (provider_ref) WHERE provider_ref IS NOT NULL;

ALTER TABLE mailboxes
    ADD COLUMN IF NOT EXISTS display_name text,
    ADD COLUMN IF NOT EXISTS webhook_id text,
    ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE communications
    ADD COLUMN IF NOT EXISTS mailbox_id uuid REFERENCES mailboxes(id),
    ADD COLUMN IF NOT EXISTS thread_ref text,            -- provider thread id (AgentMail thread_id)
    ADD COLUMN IF NOT EXISTS in_reply_to text,           -- provider message id this replies to
    ADD COLUMN IF NOT EXISTS from_address text,
    ADD COLUMN IF NOT EXISTS to_addresses text[] NOT NULL DEFAULT '{}';
CREATE INDEX IF NOT EXISTS communications_thread_idx ON communications (thread_ref);
CREATE UNIQUE INDEX IF NOT EXISTS communications_provider_ref_idx ON communications (channel, provider_ref) WHERE provider_ref IS NOT NULL;

-- Simulated insurer: one scripted thread per claim (demo only)
CREATE TABLE IF NOT EXISTS insurer_sim_threads (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_ref    text UNIQUE,                           -- AgentMail thread id on the simulated_insurer mailbox
    claim_tag     text,                                  -- [RB-xxxxxxxx] tag parsed from the subject
    scenario      text NOT NULL DEFAULT 'karim_default',
    step          int NOT NULL DEFAULT 0,
    insurer_reference text,
    history       jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now()
);
