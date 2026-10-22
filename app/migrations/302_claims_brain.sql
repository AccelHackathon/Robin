-- Workstream C. Memory that is read back for reasoning, not only written for audit.

-- One running digest per claim: what happened, what is pending, what the insurer said, next steps.
-- Replaces truncating communications/actions in the prompt; makes "do not ask twice" trivial.
CREATE TABLE IF NOT EXISTS claim_digest (
    claim_id            uuid PRIMARY KEY REFERENCES claims(id) ON DELETE CASCADE,
    narrative           text,                               -- 5-10 lines, plain facts, no advice
    open_asks           jsonb NOT NULL DEFAULT '[]'::jsonb, -- [{item, asked_at, times, satisfied_at}]
    insurer_positions   jsonb NOT NULL DEFAULT '[]'::jsonb, -- [{at, channel, who, position_verbatim, topic, status}]
    next_steps          jsonb NOT NULL DEFAULT '[]'::jsonb, -- [{step, due, source}]
    turn_count          int  NOT NULL DEFAULT 0,
    updated_at          timestamptz NOT NULL DEFAULT now()
);

-- Cross-claim memory about insurers: what Robin has observed across all files with the same insurer.
CREATE TABLE IF NOT EXISTS insurer_profiles (
    insurer_name            text PRIMARY KEY,
    claims_count            int  NOT NULL DEFAULT 0,
    first_reply_hours_sum   numeric NOT NULL DEFAULT 0,  -- sum over claims with a measured first reply
    first_reply_count       int  NOT NULL DEFAULT 0,
    first_offer_ratio_sum   numeric NOT NULL DEFAULT 0,  -- sum of (first offer / documented total)
    first_offer_count       int  NOT NULL DEFAULT 0,
    documents_requested     jsonb NOT NULL DEFAULT '{}'::jsonb, -- {"police_report": 7, "inventory": 5, ...}
    release_language_count  int  NOT NULL DEFAULT 0,  -- offers that came with a release/quittance
    updated_at              timestamptz NOT NULL DEFAULT now()
);

-- Which claims already contributed to which profile metric (idempotent updates on replays).
CREATE TABLE IF NOT EXISTS insurer_profile_marks (
    claim_id    uuid NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    metric      text NOT NULL,                              -- first_reply | first_offer | documents
    PRIMARY KEY (claim_id, metric)
);
