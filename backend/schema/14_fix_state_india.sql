-- Migration 14: Re-add state_india column
--
-- Migration 13 mistakenly dropped state_india, but our code still uses it.
-- The Q2 location tree writes: _location_type → state_india → city
-- This migration re-adds it if it was dropped.

ALTER TABLE users ADD COLUMN IF NOT EXISTS state_india VARCHAR(100);
