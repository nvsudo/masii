-- ============================================================================
-- JODI Schema Upgrade: Users Table
-- Adds 100+ data fields from Matchmaking Data Capture Framework v1
-- Type: Iterative upgrade (adds columns to existing users table)
-- ============================================================================

-- Name fields (Tier 1 - Required)
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS alias VARCHAR(100);

-- Add NOT NULL constraints for name fields (allows existing NULLs during migration)
-- These will be enforced by the application layer for new records

-- Add new Tier 1 columns (hard filters - indexed)
ALTER TABLE users ADD COLUMN IF NOT EXISTS date_of_birth DATE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS age INT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS gender_identity VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS sexual_orientation VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS nationality VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS native_languages TEXT[]; -- Array of languages
ALTER TABLE users ADD COLUMN IF NOT EXISTS ethnicity VARCHAR(100);

-- Tier 1: Hard Deal-Breakers (indexed columns)
ALTER TABLE users ADD COLUMN IF NOT EXISTS religion VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS religious_practice_level VARCHAR(50); -- Devout/Cultural/Spiritual/Secular
ALTER TABLE users ADD COLUMN IF NOT EXISTS children_intent VARCHAR(50); -- Want/Don't/Already have
ALTER TABLE users ADD COLUMN IF NOT EXISTS marital_history VARCHAR(50); -- Never/Divorced/Widowed
ALTER TABLE users ADD COLUMN IF NOT EXISTS smoking VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS drinking VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS dietary_restrictions VARCHAR(100); -- Halal/Kosher/Vegan/None
ALTER TABLE users ADD COLUMN IF NOT EXISTS relationship_intent VARCHAR(100); -- Marriage/Long-term
ALTER TABLE users ADD COLUMN IF NOT EXISTS relationship_timeline VARCHAR(50); -- Ready now/1-2 years/Exploring

-- Tier 2: Lifestyle basics (indexed for common filters)
ALTER TABLE users ADD COLUMN IF NOT EXISTS occupation VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS education_level VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS caste_community VARCHAR(100); -- Indian/Jewish/etc cultures
ALTER TABLE users ADD COLUMN IF NOT EXISTS height_cm INT; -- Optional height in cm

-- Profile status & tier tracking
ALTER TABLE users ADD COLUMN IF NOT EXISTS tier_level INT DEFAULT 1 CHECK (tier_level BETWEEN 1 AND 4);
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_active BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS completeness_score DECIMAL(5,2) DEFAULT 0.0; -- 0.00-100.00
ALTER TABLE users ADD COLUMN IF NOT EXISTS priority_score DECIMAL(5,2) DEFAULT 0.0; -- For matching queue
ALTER TABLE users ADD COLUMN IF NOT EXISTS matching_activated_at TIMESTAMPTZ;

-- Add check constraint for age (drop first if exists)
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_age_check;
ALTER TABLE users ADD CONSTRAINT users_age_check CHECK (age IS NULL OR (age >= 18 AND age <= 100));

-- Create indexes for hard filters (used in matching elimination)
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
CREATE INDEX IF NOT EXISTS idx_users_gender ON users(gender_identity);
CREATE INDEX IF NOT EXISTS idx_users_location ON users(city, country);
CREATE INDEX IF NOT EXISTS idx_users_religion ON users(religion);
CREATE INDEX IF NOT EXISTS idx_users_children_intent ON users(children_intent);
CREATE INDEX IF NOT EXISTS idx_users_relationship_intent ON users(relationship_intent);
CREATE INDEX IF NOT EXISTS idx_users_active_priority ON users(profile_active, priority_score DESC);

-- Add updated_at trigger if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate age from date_of_birth
CREATE OR REPLACE FUNCTION calculate_age_from_dob()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date_of_birth IS NOT NULL THEN
        NEW.age = EXTRACT(YEAR FROM AGE(NEW.date_of_birth));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update age when date_of_birth changes
DROP TRIGGER IF EXISTS update_users_age ON users;
CREATE TRIGGER update_users_age
    BEFORE INSERT OR UPDATE OF date_of_birth ON users
    FOR EACH ROW
    EXECUTE FUNCTION calculate_age_from_dob();

-- Function to auto-generate full_name from first_name + last_name
CREATE OR REPLACE FUNCTION generate_full_name()
RETURNS TRIGGER AS $$
BEGIN
    -- Only auto-generate if first_name or last_name changed and full_name is not explicitly set
    IF (TG_OP = 'INSERT' OR 
        OLD.first_name IS DISTINCT FROM NEW.first_name OR 
        OLD.last_name IS DISTINCT FROM NEW.last_name) THEN
        
        -- Auto-generate if first_name and last_name exist but full_name is empty
        IF NEW.first_name IS NOT NULL AND NEW.last_name IS NOT NULL THEN
            IF NEW.full_name IS NULL OR NEW.full_name = '' THEN
                NEW.full_name = TRIM(NEW.first_name || ' ' || NEW.last_name);
            END IF;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate full_name when first_name or last_name changes
DROP TRIGGER IF EXISTS update_users_full_name ON users;
CREATE TRIGGER update_users_full_name
    BEFORE INSERT OR UPDATE OF first_name, last_name ON users
    FOR EACH ROW
    EXECUTE FUNCTION generate_full_name();

COMMENT ON TABLE users IS 'Core user profiles with hard filters (indexed columns) for elimination matching';
COMMENT ON COLUMN users.first_name IS 'First name (required) - extracted by LLM or user input';
COMMENT ON COLUMN users.last_name IS 'Last name (required) - extracted by LLM or user input';
COMMENT ON COLUMN users.full_name IS 'Full name (auto-generated from first + last, or user override)';
COMMENT ON COLUMN users.alias IS 'Preferred nickname or alias (optional)';
COMMENT ON COLUMN users.tier_level IS 'Current tier: 1=Basics, 2=Ready, 3=Deep Profile, 4=Calibrated';
COMMENT ON COLUMN users.profile_active IS 'TRUE when MVP threshold met (100% T1 + 70% T2 + 2 sessions + 45% total)';
COMMENT ON COLUMN users.completeness_score IS 'Weighted completion across all tiers (0-100)';
COMMENT ON COLUMN users.priority_score IS 'Matching priority = completeness + recency boost';
