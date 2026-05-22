-- Workflow Designer Database Schema

CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    dag_json TEXT NOT NULL,  -- JSON: {nodes: [...], edges: [...]}
    owner TEXT NOT NULL DEFAULT 'default',
    pipeline_type TEXT NOT NULL DEFAULT 'batch',  -- batch, streaming, inference, feature
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, active, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT  -- JSON: extra metadata
);

-- Index for filtering and searching
CREATE INDEX IF NOT EXISTS idx_workflows_owner ON workflows(owner);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_pipeline_type ON workflows(pipeline_type);
CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at DESC);

-- Trigger to update updated_at on modification
CREATE TRIGGER IF NOT EXISTS update_workflows_timestamp
AFTER UPDATE ON workflows
FOR EACH ROW
BEGIN
    UPDATE workflows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
