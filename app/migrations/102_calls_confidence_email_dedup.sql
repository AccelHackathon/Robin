-- Workstream A fixes found in review.

-- PRD 3.4 `calls.confidence` (oral answers are provisional); missing from 001.
ALTER TABLE calls ADD COLUMN IF NOT EXISTS confidence text;

-- The same provider message id legitimately appears twice in the internal demo loop:
-- once as the agent mailbox's outbound row and once as the simulated insurer's inbound row.
-- Uniqueness must be per direction and mailbox, not global.
DROP INDEX IF EXISTS communications_provider_ref_idx;
CREATE UNIQUE INDEX IF NOT EXISTS communications_email_inbound_idx
    ON communications (mailbox_id, provider_ref) WHERE channel = 'email' AND direction = 'inbound' AND provider_ref IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS communications_email_outbound_idx
    ON communications (mailbox_id, provider_ref) WHERE channel = 'email' AND direction = 'outbound' AND provider_ref IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS communications_phone_idx
    ON communications (direction, provider_ref) WHERE channel = 'phone' AND provider_ref IS NOT NULL;
