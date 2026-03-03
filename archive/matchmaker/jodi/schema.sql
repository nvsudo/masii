-- Jodi Platform PostgreSQL schema (v1)
-- Location: /Users/nikunjvora/clawd/matchmaker/jodi/schema.sql

-- Enable pgvector extension for embedding vectors
CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================================
-- users: core authentication and account fields
-- ==========================================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    last_login TIMESTAMPTZ
);

COMMENT ON TABLE users IS 'Core user accounts (auth). Separate from profile data.';

-- ==========================================================
-- profiles: user-visible attributes, preferences and embeddings
-- Hybrid approach: hard-filter columns (indexed) + JSONB for flexible data + vector for embeddings
-- ==========================================================
CREATE TABLE IF NOT EXISTS profiles (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name TEXT,
    dob DATE,
    gender TEXT,
    location GEOGRAPHY(POINT, 4326), -- stores lat/lon; indexable via PostGIS if available; fallback to TEXT if PostGIS not desired
    location_text TEXT,
    religion TEXT,
    relationship_intent TEXT,
    smoking TEXT,
    drinking TEXT,
    wants_children BOOLEAN,
    education_level TEXT,
    height_cm INTEGER,

    -- JSONB columns for flexible or evolving data
    preferences JSONB DEFAULT '{}'::jsonb,
    personality_data JSONB DEFAULT '{}'::jsonb,
    media_signals JSONB DEFAULT '{}'::jsonb,

    -- Vector column for similarity search (pgvector)
    embedding vector(1536), -- dimension should match model used (example: 1536)

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE profiles IS 'Profile information separated from auth (users). Hard filter columns are duplicated here for fast querying; additional flexible attributes live in JSONB.';

-- Indexes on hard filter columns (for fast filtering)
CREATE INDEX IF NOT EXISTS idx_profiles_dob ON profiles(dob);
CREATE INDEX IF NOT EXISTS idx_profiles_gender ON profiles(gender);
CREATE INDEX IF NOT EXISTS idx_profiles_location_text ON profiles(location_text);
CREATE INDEX IF NOT EXISTS idx_profiles_religion ON profiles(religion);
CREATE INDEX IF NOT EXISTS idx_profiles_relationship_intent ON profiles(relationship_intent);
CREATE INDEX IF NOT EXISTS idx_profiles_smoking ON profiles(smoking);
CREATE INDEX IF NOT EXISTS idx_profiles_drinking ON profiles(drinking);
CREATE INDEX IF NOT EXISTS idx_profiles_wants_children ON profiles(wants_children);
CREATE INDEX IF NOT EXISTS idx_profiles_education_level ON profiles(education_level);
CREATE INDEX IF NOT EXISTS idx_profiles_height_cm ON profiles(height_cm);

-- GIN indexes on JSONB columns for efficient containment/key queries
CREATE INDEX IF NOT EXISTS gin_profiles_preferences ON profiles USING GIN (preferences);
CREATE INDEX IF NOT EXISTS gin_profiles_personality_data ON profiles USING GIN (personality_data);
CREATE INDEX IF NOT EXISTS gin_profiles_media_signals ON profiles USING GIN (media_signals);

-- Index for embedding vector (ivfflat recommended for pgvector if many rows)
-- Note: CREATE INDEX ... USING ivfflat requires specifying lists and the table to be ANALYZED; adjust as needed for production.
-- Example (uncomment and tune):
-- CREATE INDEX IF NOT EXISTS idx_profiles_embedding ON profiles USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- ==========================================================
-- interactions: append-only event log (separate from profiles)
-- Append-only: records all likes, messages, views, swipes, etc.
-- ==========================================================
CREATE TABLE IF NOT EXISTS interactions (
    id BIGSERIAL PRIMARY KEY,
    actor_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- e.g., 'like', 'superlike', 'message', 'view'
    payload JSONB DEFAULT '{}'::jsonb, -- event-specific data (message text, metadata)
    created_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE interactions IS 'Append-only interaction log. Kept separate from profiles to optimize writes and retain audit history.';

-- Indexes to support queries: recent interactions by actor/target
CREATE INDEX IF NOT EXISTS idx_interactions_actor ON interactions(actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_target ON interactions(target_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(type);
CREATE INDEX IF NOT EXISTS gin_interactions_payload ON interactions USING GIN (payload);

-- ==========================================================
-- matches: derived/matching state between users (can be rebuilt from interactions)
-- Stores active matches and metadata
-- ==========================================================
CREATE TABLE IF NOT EXISTS matches (
    id BIGSERIAL PRIMARY KEY,
    user_a BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_b BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matched_at TIMESTAMPTZ DEFAULT now(),
    status TEXT DEFAULT 'active', -- active, blocked, unmatched
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(user_a, user_b)
);

COMMENT ON TABLE matches IS 'Materialized matches derived from interactions. Can be rebuilt if lost.';

-- Indexes to find matches for a user quickly
CREATE INDEX IF NOT EXISTS idx_matches_user_a ON matches(user_a);
CREATE INDEX IF NOT EXISTS idx_matches_user_b ON matches(user_b);

-- ==========================================================
-- Notes on location: If PostGIS is not available, location can be stored as text or separate lat/lon floats.
-- If you prefer lat/lon without PostGIS change the location column to: location_lat DOUBLE PRECISION, location_lon DOUBLE PRECISION
-- ==========================================================

-- End of schema.sql
