-- ============================================================================
-- JODI Schema Fix: Align Database to Bot Code (77-Field MVP)
-- Bot is source of truth. Schema must match bot expectations.
-- Execution: 2026-02-21 (P0 blocker fix)
-- ============================================================================

-- ===========================================================================
-- PART 1: FIX TRIGGER (IMMEDIATE BLOCKER)
-- ===========================================================================

-- Fix trigger function: NEW.user_id → NEW.id
CREATE OR REPLACE FUNCTION trigger_recalculate_completeness()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM calculate_weighted_completeness(NEW.id);  -- ✅ FIXED
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION trigger_recalculate_completeness IS 
'Auto-recalculate completeness score on users table updates (FIXED: uses NEW.id not NEW.user_id)';

-- ===========================================================================
-- PART 2: RENAME MISMATCHED COLUMNS IN USERS TABLE
-- ===========================================================================

-- 1. marital_history → marital_status
ALTER TABLE users RENAME COLUMN marital_history TO marital_status;

-- 2. country → country_current
ALTER TABLE users RENAME COLUMN country TO country_current;

-- 3. city → city_current
ALTER TABLE users RENAME COLUMN city TO city_current;

-- 4. religious_practice_level → religious_practice
ALTER TABLE users RENAME COLUMN religious_practice_level TO religious_practice;

-- 5. industry → work_industry
ALTER TABLE users RENAME COLUMN industry TO work_industry;

-- 6. dietary_restrictions → diet
ALTER TABLE users RENAME COLUMN dietary_restrictions TO diet;

-- 7. native_languages (array) → keep as is, will map mother_tongue separately
-- (native_languages can stay for other use cases, add mother_tongue as separate column)

-- ===========================================================================
-- PART 3: ADD MISSING COLUMNS TO USERS TABLE (35 fields)
-- ===========================================================================

-- Identity & Basics (Section A)
ALTER TABLE users ADD COLUMN IF NOT EXISTS looking_for_gender VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS children_existing VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS body_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS complexion VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS disability_status VARCHAR(50);

-- Location & Mobility (Section B)
ALTER TABLE users ADD COLUMN IF NOT EXISTS residency_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS state_india VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS hometown_state VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS willing_to_relocate VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS settling_country VARCHAR(100);

-- Religion & Culture (Section C)
ALTER TABLE users ADD COLUMN IF NOT EXISTS sect_denomination VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS sub_caste VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS mother_tongue VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS languages_spoken TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS manglik_status VARCHAR(50);

-- Education & Career (Section D)
ALTER TABLE users ADD COLUMN IF NOT EXISTS education_institute_tier VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS employment_status VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS career_ambition VARCHAR(50);

-- Financial (Section E)
ALTER TABLE users ADD COLUMN IF NOT EXISTS annual_income VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS income_currency VARCHAR(10);
ALTER TABLE users ADD COLUMN IF NOT EXISTS net_worth_range VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS property_ownership VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS financial_dependents VARCHAR(100);

-- Family (Section F)
ALTER TABLE users ADD COLUMN IF NOT EXISTS family_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS family_financial_status VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS father_occupation VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS family_values VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS living_with_parents_post_marriage VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS family_involvement_search VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS siblings VARCHAR(100);

-- Lifestyle (Section G)
ALTER TABLE users ADD COLUMN IF NOT EXISTS fitness_frequency VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS social_style VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS weekend_style VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS pet_ownership VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS sleep_schedule VARCHAR(50);

-- Values (Section I)
ALTER TABLE users ADD COLUMN IF NOT EXISTS children_timeline VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS gender_roles_household VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS financial_management VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS political_leaning VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS astrology_belief VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS interfaith_intercaste_openness VARCHAR(50);

-- ===========================================================================
-- PART 4: RENAME MISMATCHED COLUMNS IN USER_PREFERENCES TABLE
-- ===========================================================================

-- 1. location_preference → keep as array (bot can adapt)
-- 2. religion_preference → keep as array (bot can adapt)
-- 3. education_minimum → pref_education_min
ALTER TABLE user_preferences RENAME COLUMN education_minimum TO pref_education_min;

-- 4. children_preference → pref_children_ok
ALTER TABLE user_preferences RENAME COLUMN children_preference TO pref_children_ok;

-- ===========================================================================
-- PART 5: ADD MISSING COLUMNS TO USER_PREFERENCES TABLE (14 fields)
-- ===========================================================================

-- Partner preferences (Section H)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS partner_location_pref TEXT;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS partner_religion_pref TEXT;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS caste_importance VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS partner_diet_pref VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS smoking_partner_ok VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS drinking_partner_ok VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_age_range VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_height VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_complexion VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_income_range VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_marital_status VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_disability_ok VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_working_spouse VARCHAR(50);

-- Dealbreakers (Section J)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS db_divorced_ok BOOLEAN;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS db_widowed_ok BOOLEAN;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS db_children_ok BOOLEAN;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS db_nri_ok BOOLEAN;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS db_age_gap_max INT;

-- ===========================================================================
-- PART 6: UPDATE INDEXES TO MATCH RENAMED COLUMNS
-- ===========================================================================

-- Drop old indexes on renamed columns
DROP INDEX IF EXISTS idx_users_location;
DROP INDEX IF EXISTS idx_users_religion;

-- Create new indexes with correct column names
CREATE INDEX IF NOT EXISTS idx_users_location ON users(city_current, country_current);
CREATE INDEX IF NOT EXISTS idx_users_marital_status ON users(marital_status);
CREATE INDEX IF NOT EXISTS idx_users_work_industry ON users(work_industry);
CREATE INDEX IF NOT EXISTS idx_users_diet ON users(diet);

-- ===========================================================================
-- PART 7: UPDATE COMMENTS TO REFLECT NEW COLUMN NAMES
-- ===========================================================================

COMMENT ON COLUMN users.marital_status IS 'Marital history: Never/Divorced/Widowed (renamed from marital_history)';
COMMENT ON COLUMN users.country_current IS 'Current country of residence (renamed from country)';
COMMENT ON COLUMN users.city_current IS 'Current city of residence (renamed from city)';
COMMENT ON COLUMN users.religious_practice IS 'Religious practice level: Devout/Cultural/Spiritual/Secular (renamed from religious_practice_level)';
COMMENT ON COLUMN users.work_industry IS 'Work industry/sector (renamed from industry)';
COMMENT ON COLUMN users.diet IS 'Dietary restrictions/preferences (renamed from dietary_restrictions)';

COMMENT ON COLUMN user_preferences.pref_education_min IS 'Minimum education level preference (renamed from education_minimum)';
COMMENT ON COLUMN user_preferences.pref_children_ok IS 'OK with partner having existing children (renamed from children_preference)';

-- ===========================================================================
-- PART 8: UPDATE HELPER FUNCTIONS TO USE NEW COLUMN NAMES
-- ===========================================================================

-- Update export_user_profile function to use new column names
CREATE OR REPLACE FUNCTION export_user_profile(p_user_id BIGINT)
RETURNS JSONB AS $$
DECLARE
  profile JSONB;
  tier1_data JSONB;
  tier2_data JSONB;
  tier3_data JSONB;
  preferences_data JSONB;
BEGIN
  -- Tier 1: Users table hard filters (UPDATED COLUMN NAMES)
  SELECT jsonb_build_object(
    'first_name', first_name,
    'last_name', last_name,
    'full_name', full_name,
    'alias', alias,
    'date_of_birth', date_of_birth,
    'age', age,
    'gender_identity', gender_identity,
    'sexual_orientation', sexual_orientation,
    'city_current', city_current,
    'country_current', country_current,
    'nationality', nationality,
    'ethnicity', ethnicity,
    'native_languages', native_languages,
    'religion', religion,
    'children_intent', children_intent,
    'marital_status', marital_status,
    'smoking', smoking,
    'drinking', drinking,
    'diet', diet,
    'relationship_intent', relationship_intent,
    'relationship_timeline', relationship_timeline,
    'occupation', occupation,
    'work_industry', work_industry,
    'education_level', education_level,
    'height_cm', height_cm,
    'tier_level', tier_level,
    'profile_active', profile_active,
    'completeness_score', completeness_score
  ) INTO tier1_data
  FROM users WHERE id = p_user_id;
  
  -- Preferences (UPDATED COLUMN NAMES)
  SELECT jsonb_build_object(
    'age_min', age_min,
    'age_max', age_max,
    'gender_preference', gender_preference,
    'location_preference', location_preference,
    'open_to_relocation', open_to_relocation,
    'religion_preference', religion_preference,
    'pref_children_ok', pref_children_ok,
    'pref_education_min', pref_education_min,
    'soft_preferences', soft_preferences,
    'dealbreakers', dealbreakers,
    'green_flags', green_flags
  ) INTO preferences_data
  FROM user_preferences WHERE user_id = p_user_id;
  
  -- Tier 2-3: All signals
  SELECT jsonb_build_object(
    'lifestyle', lifestyle,
    'values', values,
    'relationship_style', relationship_style,
    'personality', personality,
    'family_background', family_background,
    'media_signals', media_signals,
    'match_learnings', match_learnings
  ) INTO tier2_data
  FROM user_signals WHERE user_id = p_user_id;
  
  -- Combine all
  profile := jsonb_build_object(
    'user_id', p_user_id,
    'tier1', tier1_data,
    'preferences', preferences_data,
    'signals', tier2_data,
    'exported_at', NOW()
  );
  
  RETURN profile;
END;
$$ LANGUAGE plpgsql;

-- Update trigger to check renamed columns
DROP TRIGGER IF EXISTS update_completeness_on_user_change ON users;
CREATE TRIGGER update_completeness_on_user_change
  AFTER UPDATE ON users
  FOR EACH ROW
  WHEN (
    OLD.first_name IS DISTINCT FROM NEW.first_name OR
    OLD.last_name IS DISTINCT FROM NEW.last_name OR
    OLD.full_name IS DISTINCT FROM NEW.full_name OR
    OLD.date_of_birth IS DISTINCT FROM NEW.date_of_birth OR
    OLD.gender_identity IS DISTINCT FROM NEW.gender_identity OR
    OLD.religion IS DISTINCT FROM NEW.religion OR
    OLD.children_intent IS DISTINCT FROM NEW.children_intent OR
    OLD.marital_status IS DISTINCT FROM NEW.marital_status OR
    OLD.diet IS DISTINCT FROM NEW.diet OR
    OLD.smoking IS DISTINCT FROM NEW.smoking OR
    OLD.drinking IS DISTINCT FROM NEW.drinking
  )
  EXECUTE FUNCTION trigger_recalculate_completeness();

COMMENT ON TRIGGER update_completeness_on_user_change ON users IS 
'Auto-recalculate completeness score when Tier 1 fields are updated (UPDATED for renamed columns)';

-- ===========================================================================
-- VERIFICATION QUERIES
-- ===========================================================================

-- Run these to verify migration success:
/*
-- 1. Check all columns exist in users table
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- 2. Check all columns exist in user_preferences table
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'user_preferences' 
ORDER BY ordinal_position;

-- 3. Verify trigger function
SELECT pg_get_functiondef(oid)
FROM pg_proc
WHERE proname = 'trigger_recalculate_completeness';

-- 4. Test trigger doesn't crash
UPDATE users SET gender_identity = 'Male' WHERE telegram_id = 7207658858;
*/
