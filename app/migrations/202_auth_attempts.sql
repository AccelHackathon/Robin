CREATE TABLE IF NOT EXISTS web_auth_attempts (key text NOT NULL,created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS web_auth_attempts_key_idx ON web_auth_attempts(key,created_at);
