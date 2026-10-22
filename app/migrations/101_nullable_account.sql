-- Insurer-side communications (inbound insurer mail, simulated insurer outbound) have no account.
-- Relax the NOT NULL so the email channel and the simulator can store them. Additive/relaxing only.
ALTER TABLE communications ALTER COLUMN account_id DROP NOT NULL;
