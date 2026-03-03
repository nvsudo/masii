-- Migration 15: Double opt-in support for matches table
--
-- Adds index for new match statuses used by the delivery engine:
--   pending → offered_a → accepted_a → offered_b → accepted → introduced
--   Also: declined_a, declined_b, expired_a, expired_b, almost
--
-- The status column is VARCHAR so no ALTER needed for new values.

-- Index for delivery engine queries (offered/accepted states)
CREATE INDEX IF NOT EXISTS idx_matches_delivery_status
    ON matches(status, updated_at)
    WHERE status IN ('pending', 'offered_a', 'offered_b', 'accepted_a', 'almost');

-- Track who was offered first (for analytics)
ALTER TABLE matches ADD COLUMN IF NOT EXISTS offered_first VARCHAR(10);
COMMENT ON COLUMN matches.offered_first IS 'Who was offered first: a=user_id, b=matched_user_id';

-- Track offer timestamps
ALTER TABLE matches ADD COLUMN IF NOT EXISTS offered_a_at TIMESTAMPTZ;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS offered_b_at TIMESTAMPTZ;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS introduced_at TIMESTAMPTZ;
