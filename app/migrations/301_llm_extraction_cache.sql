-- Workstream C. Cache of model extractions keyed by document hash and task, so re-reading the same
-- invoice (benchmark re-runs, duplicate uploads) costs nothing.
CREATE TABLE IF NOT EXISTS llm_extraction_cache (
    sha256      text NOT NULL,
    task        text NOT NULL,          -- read_document | extract_narrative | ...
    model       text NOT NULL,
    result      jsonb NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (sha256, task)
);
