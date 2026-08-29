DROP INDEX IF EXISTS core.idx_outbox_pending;
DROP TABLE IF EXISTS core.outbox_messages;
DROP INDEX IF EXISTS core.idx_jobs_lease_expiry;
DROP INDEX IF EXISTS core.idx_jobs_runnable;
ALTER TABLE core.jobs DROP CONSTRAINT IF EXISTS ck_job_operation_fingerprint;
ALTER TABLE core.jobs DROP COLUMN IF EXISTS operation_fingerprint;
