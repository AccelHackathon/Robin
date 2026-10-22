-- Workstream D: Risk Sentinel — continuous monitoring of external risks per account. Additive only.

-- What the agent watches for an account, derived from business + coverage profile (re-derived on each sweep).
CREATE TABLE IF NOT EXISTS risk_profiles (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL UNIQUE REFERENCES accounts(id),
    city          text,
    department    text,                                  -- e.g. "Bouches-du-Rhône" / "13"
    region        text,
    address       text,
    activity      text,
    has_vehicles  boolean NOT NULL DEFAULT false,
    has_shopfront boolean NOT NULL DEFAULT true,
    risk_keys     text[] NOT NULL DEFAULT '{}',           -- civil_unrest | hail | storm | flood | fire_nearby | strike_access | theft_wave | heatwave_power | regulatory
    covers        jsonb NOT NULL DEFAULT '{}'::jsonb,    -- {risk_key: {guarantee, subscribed, clause_id, page, prevention: [...], deadline: ...}}
    watch_enabled boolean NOT NULL DEFAULT true,
    sweep_interval_minutes int NOT NULL DEFAULT 15,
    last_sweep_at timestamptz,
    next_sweep_at timestamptz NOT NULL DEFAULT now(),
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS risk_profiles_due_idx ON risk_profiles (next_sweep_at) WHERE watch_enabled;

-- Concrete search queries planned for a sweep (kept for auditability and cost control).
CREATE TABLE IF NOT EXISTS watch_queries (
    id            bigserial PRIMARY KEY,
    account_id    uuid NOT NULL REFERENCES accounts(id),
    risk_key      text NOT NULL,
    query         text NOT NULL,
    site          text,
    published_after text,
    last_run_at   timestamptz,
    last_hits     int,
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (account_id, risk_key, query)
);

-- One alert = one assessed external event relevant to the account. Deduplicated by fingerprint.
CREATE TABLE IF NOT EXISTS alerts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id    uuid NOT NULL REFERENCES accounts(id),
    claim_id      uuid REFERENCES claims(id),            -- set when a later claim is linked to this event
    risk_key      text NOT NULL,
    fingerprint   text NOT NULL,                         -- sha1(risk_key|place|date) for dedup
    severity      text NOT NULL,                         -- low | medium | high | critical
    title         text NOT NULL,
    event_summary text NOT NULL,                         -- plain facts: what, where, when, perimeter
    event_starts_at timestamptz,
    event_ends_at timestamptz,
    place         text,
    distance_hint text,                                  -- "same street", "same city", "department"
    guarantee     text,                                  -- canonical cover key concerned
    clause_id     bigint REFERENCES clauses(id),
    clause_page   int,
    prevention_items jsonb NOT NULL DEFAULT '[]'::jsonb,  -- contractual/practical measures, each with source
    deadline_note text,                                  -- e.g. "declare within 2 working days (L113-2)"
    assessment    jsonb NOT NULL DEFAULT '{}'::jsonb,    -- full model output
    message_en    text,                                  -- what was sent to the client (after review)
    review_passed boolean,
    communication_id uuid REFERENCES communications(id),
    status        text NOT NULL DEFAULT 'new',           -- new | notified | suppressed_duplicate | below_threshold | review_blocked | expired
    notified_at   timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (account_id, fingerprint)
);
CREATE INDEX IF NOT EXISTS alerts_account_idx ON alerts (account_id, created_at DESC);

-- Sources behind an alert (every alert must have at least one URL).
CREATE TABLE IF NOT EXISTS alert_sources (
    id            bigserial PRIMARY KEY,
    alert_id      uuid NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    url           text NOT NULL,
    title         text,
    site          text,
    published_at  timestamptz,
    excerpt       text,
    official      boolean NOT NULL DEFAULT false,        -- prefecture, Météo-France, ministry, insurer
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- Sweep log for observability and the pitch slide (cost per sweep, hits, alerts).
CREATE TABLE IF NOT EXISTS sentinel_sweeps (
    id            bigserial PRIMARY KEY,
    account_id    uuid NOT NULL REFERENCES accounts(id),
    started_at    timestamptz NOT NULL DEFAULT now(),
    finished_at   timestamptz,
    queries_run   int NOT NULL DEFAULT 0,
    hits          int NOT NULL DEFAULT 0,
    pages_fetched int NOT NULL DEFAULT 0,
    candidates    int NOT NULL DEFAULT 0,
    alerts_created int NOT NULL DEFAULT 0,
    alerts_notified int NOT NULL DEFAULT 0,
    credits_used  numeric,
    error         text
);
