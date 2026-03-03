-- Migration 13: Align schema to master question flow (docs/question-flow.md)
-- The question flow is the single source of truth for all intake questions.
-- This migration adds missing columns, renames fields to match, changes types,
-- moves fields to correct tables, and drops unused columns.
--
-- Run against: Supabase (PostgreSQL 15+)
-- Date: March 2026

BEGIN;

-- ============================================================================
-- PART 1: USERS TABLE — Renames
-- ============================================================================

ALTER TABLE users RENAME COLUMN gender_identity TO gender;
ALTER TABLE users RENAME COLUMN disability_status TO known_conditions;
ALTER TABLE users RENAME COLUMN family_financial_status TO family_status;
ALTER TABLE users RENAME COLUMN occupation TO occupation_sector;

-- ============================================================================
-- PART 2: USERS TABLE — Add missing columns
-- ============================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS weight_kg INT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS education_field VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS mother_occupation VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS hometown_city VARCHAR(255);

-- Change languages_spoken from TEXT to TEXT[] (array for multi-select)
-- First copy data, then alter
ALTER TABLE users ADD COLUMN IF NOT EXISTS languages_spoken_arr TEXT[];
UPDATE users SET languages_spoken_arr = CASE
    WHEN languages_spoken IS NOT NULL AND languages_spoken != '' THEN ARRAY[languages_spoken]
    ELSE NULL
END;
ALTER TABLE users DROP COLUMN IF EXISTS languages_spoken;
ALTER TABLE users RENAME COLUMN languages_spoken_arr TO languages_spoken;

-- ============================================================================
-- PART 3: USERS TABLE — Drop unused columns

DROP TRIGGER IF EXISTS update_users_full_name ON users;
DROP TRIGGER IF EXISTS update_completeness_on_user_change ON users;
-- ============================================================================
-- These fields are not in the question flow and were part of the old
-- generic Western matchmaking framework.

ALTER TABLE users DROP COLUMN IF EXISTS first_name;
ALTER TABLE users DROP COLUMN IF EXISTS last_name;
ALTER TABLE users DROP COLUMN IF EXISTS alias;
ALTER TABLE users DROP COLUMN IF EXISTS sexual_orientation;
ALTER TABLE users DROP COLUMN IF EXISTS nationality;
ALTER TABLE users DROP COLUMN IF EXISTS ethnicity;
ALTER TABLE users DROP COLUMN IF EXISTS native_languages;
ALTER TABLE users DROP COLUMN IF EXISTS relationship_intent;
ALTER TABLE users DROP COLUMN IF EXISTS relationship_timeline;
ALTER TABLE users DROP COLUMN IF EXISTS work_industry;
ALTER TABLE users DROP COLUMN IF EXISTS looking_for_gender;
ALTER TABLE users DROP COLUMN IF EXISTS body_type;
ALTER TABLE users DROP COLUMN IF EXISTS complexion;
ALTER TABLE users DROP COLUMN IF EXISTS residency_type;
-- KEEP state_india — used by Q2 location tree (India → state → city)
ALTER TABLE users DROP COLUMN IF EXISTS sub_caste;
ALTER TABLE users DROP COLUMN IF EXISTS education_institute_tier;
ALTER TABLE users DROP COLUMN IF EXISTS employment_status;
ALTER TABLE users DROP COLUMN IF EXISTS career_ambition;
ALTER TABLE users DROP COLUMN IF EXISTS income_currency;
ALTER TABLE users DROP COLUMN IF EXISTS net_worth_range;
ALTER TABLE users DROP COLUMN IF EXISTS property_ownership;
ALTER TABLE users DROP COLUMN IF EXISTS financial_dependents;
ALTER TABLE users DROP COLUMN IF EXISTS living_with_parents_post_marriage;
ALTER TABLE users DROP COLUMN IF EXISTS family_involvement_search;
ALTER TABLE users DROP COLUMN IF EXISTS weekend_style;
ALTER TABLE users DROP COLUMN IF EXISTS pet_ownership;
ALTER TABLE users DROP COLUMN IF EXISTS sleep_schedule;
ALTER TABLE users DROP COLUMN IF EXISTS gender_roles_household;
ALTER TABLE users DROP COLUMN IF EXISTS financial_management;
ALTER TABLE users DROP COLUMN IF EXISTS political_leaning;
ALTER TABLE users DROP COLUMN IF EXISTS astrology_belief;
ALTER TABLE users DROP COLUMN IF EXISTS interfaith_intercaste_openness;
ALTER TABLE users DROP COLUMN IF EXISTS settling_country;
ALTER TABLE users DROP COLUMN IF EXISTS willing_to_relocate;

-- ============================================================================
-- PART 4: USERS TABLE — Move fields to correct tables
-- These columns exist on users but belong elsewhere per question flow.
-- We'll add them to the right table first, migrate data, then drop from users.
-- ============================================================================

-- Fields moving to user_preferences:
-- religious_practice, sect_denomination, caste_community, children_intent, children_timeline

-- Fields moving to user_signals (as flat columns):
-- smoking, drinking, diet, fitness_frequency, social_style, family_values, manglik_status

-- (Data migration happens after the target columns are created in Parts 5 & 6)

-- ============================================================================
-- PART 5: USER_PREFERENCES TABLE — Renames
-- ============================================================================

ALTER TABLE user_preferences RENAME COLUMN partner_diet_pref TO pref_diet;
ALTER TABLE user_preferences RENAME COLUMN smoking_partner_ok TO pref_smoking;
ALTER TABLE user_preferences RENAME COLUMN drinking_partner_ok TO pref_drinking;
ALTER TABLE user_preferences RENAME COLUMN pref_disability_ok TO pref_conditions;
ALTER TABLE user_preferences RENAME COLUMN pref_working_spouse TO partner_working;
ALTER TABLE user_preferences RENAME COLUMN age_min TO pref_age_min;
ALTER TABLE user_preferences RENAME COLUMN age_max TO pref_age_max;

-- ============================================================================
-- PART 6: USER_PREFERENCES TABLE — Add missing columns
-- ============================================================================

-- From Phase 2 (Background) — moved from users
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS religious_practice VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS sect_denomination VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS caste_community VARCHAR(100);

-- From Phase 3 (Partner Background Preferences)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_religion VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_religion_exclude TEXT[];
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_caste VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_caste_exclude TEXT[];
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_mother_tongue VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_income_min VARCHAR(100);

-- From Phase 7 (Marriage & Living) — moved from users
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS marriage_timeline VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS children_intent VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS children_timeline VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS living_arrangement VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS relocation_willingness VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS family_involvement VARCHAR(100);

-- From Phase 8 (Partner Physical Preferences)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_height_min INT;
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_height_max INT;

-- From Phase 10 (Sensitive)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_manglik VARCHAR(50);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_gotra_exclude TEXT[];
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_family_status VARCHAR(50);

-- From Phase 9 (Household — Women only)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_partner_cooking VARCHAR(100);
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_partner_household VARCHAR(100);

-- ============================================================================
-- PART 7: USER_PREFERENCES TABLE — Drop unused columns
-- ============================================================================

ALTER TABLE user_preferences DROP COLUMN IF EXISTS gender_preference;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS location_preference;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS max_distance_km;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS religion_preference;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS religion_importance;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_children_ok;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS soft_preferences;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS dealbreakers;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS green_flags;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS partner_location_pref;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS partner_religion_pref;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_complexion;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_marital_status;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_age_range;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_height;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_income_range;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS db_divorced_ok;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS db_widowed_ok;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS db_children_ok;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS db_nri_ok;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS db_age_gap_max;

-- Change open_to_relocation from BOOLEAN to VARCHAR (4 options)
ALTER TABLE user_preferences DROP COLUMN IF EXISTS open_to_relocation;
-- relocation_willingness already added above as VARCHAR(100)

-- ============================================================================
-- PART 8: USER_SIGNALS TABLE — Add flat columns
-- The JSONB blobs (lifestyle, values, etc.) are kept for future AI-inferred
-- signals. New flat columns are for explicit user answers from the intake.
-- ============================================================================

ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS diet VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS drinking VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS smoking VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS fitness_frequency VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS social_style VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS conflict_style VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS family_values VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS manglik_status VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS gotra VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS family_property VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS financial_planning VARCHAR(100);

-- Gender-forked: Men
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS cooking_contribution VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS household_contribution VARCHAR(100);

-- Gender-forked: Women
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS do_you_cook VARCHAR(50);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS career_after_marriage VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS financial_contribution VARCHAR(100);
ALTER TABLE user_signals ADD COLUMN IF NOT EXISTS live_with_inlaws VARCHAR(100);

-- ============================================================================
-- PART 9: Migrate data from users to correct tables
-- Copy existing values before dropping from users.
-- ============================================================================

-- Move to user_preferences (only if data exists)
UPDATE user_preferences p
SET
    religious_practice = COALESCE(p.religious_practice, u.religious_practice),
    sect_denomination = COALESCE(p.sect_denomination, u.sect_denomination),
    caste_community = COALESCE(p.caste_community, u.caste_community),
    children_intent = COALESCE(p.children_intent, u.children_intent),
    children_timeline = COALESCE(p.children_timeline, u.children_timeline)
FROM users u
WHERE p.user_id = u.id
AND (u.religious_practice IS NOT NULL
     OR u.sect_denomination IS NOT NULL
     OR u.caste_community IS NOT NULL
     OR u.children_intent IS NOT NULL
     OR u.children_timeline IS NOT NULL);

-- Move to user_signals (only if data exists)
UPDATE user_signals s
SET
    diet = COALESCE(s.diet, u.diet),
    drinking = COALESCE(s.drinking, u.drinking),
    smoking = COALESCE(s.smoking, u.smoking),
    fitness_frequency = COALESCE(s.fitness_frequency, u.fitness_frequency),
    social_style = COALESCE(s.social_style, u.social_style),
    family_values = COALESCE(s.family_values, u.family_values),
    manglik_status = COALESCE(s.manglik_status, u.manglik_status)
FROM users u
WHERE s.user_id = u.id
AND (u.diet IS NOT NULL
     OR u.drinking IS NOT NULL
     OR u.smoking IS NOT NULL
     OR u.fitness_frequency IS NOT NULL
     OR u.social_style IS NOT NULL
     OR u.family_values IS NOT NULL
     OR u.manglik_status IS NOT NULL);

-- Now drop the moved columns from users
ALTER TABLE users DROP COLUMN IF EXISTS religious_practice;
ALTER TABLE users DROP COLUMN IF EXISTS sect_denomination;
ALTER TABLE users DROP COLUMN IF EXISTS caste_community;
ALTER TABLE users DROP COLUMN IF EXISTS children_intent;
ALTER TABLE users DROP COLUMN IF EXISTS children_timeline;
ALTER TABLE users DROP COLUMN IF EXISTS diet;
ALTER TABLE users DROP COLUMN IF EXISTS drinking;
ALTER TABLE users DROP COLUMN IF EXISTS smoking;
ALTER TABLE users DROP COLUMN IF EXISTS fitness_frequency;
ALTER TABLE users DROP COLUMN IF EXISTS social_style;
ALTER TABLE users DROP COLUMN IF EXISTS family_values;
ALTER TABLE users DROP COLUMN IF EXISTS manglik_status;

-- ============================================================================
-- PART 10: USER_CHANNELS TABLE — Renames for consistency
-- ============================================================================

-- ALTER TABLE user_channels RENAME COLUMN channel_type TO channel;
-- ALTER TABLE user_channels RENAME COLUMN channel_identifier TO channel_id;

-- ============================================================================
-- PART 11: Update indexes for renamed columns
-- ============================================================================

-- Drop old indexes that reference renamed/dropped columns
DROP INDEX IF EXISTS idx_users_gender;
DROP INDEX IF EXISTS idx_users_gender_identity;
DROP INDEX IF EXISTS idx_users_location;
DROP INDEX IF EXISTS idx_users_religion_practice;

-- Create new indexes on frequently filtered columns
CREATE INDEX IF NOT EXISTS idx_users_gender ON users(gender);
CREATE INDEX IF NOT EXISTS idx_users_religion ON users(religion);
CREATE INDEX IF NOT EXISTS idx_users_current_location ON users(city_current, country_current);
CREATE INDEX IF NOT EXISTS idx_users_mother_tongue ON users(mother_tongue);
CREATE INDEX IF NOT EXISTS idx_users_marital_status ON users(marital_status);
CREATE INDEX IF NOT EXISTS idx_users_height_weight ON users(height_cm, weight_kg);
CREATE INDEX IF NOT EXISTS idx_users_income ON users(annual_income);
CREATE INDEX IF NOT EXISTS idx_users_education ON users(education_level, education_field);

-- Preferences indexes for matching queries
CREATE INDEX IF NOT EXISTS idx_prefs_religion ON user_preferences(pref_religion);
CREATE INDEX IF NOT EXISTS idx_prefs_caste ON user_preferences(pref_caste);
CREATE INDEX IF NOT EXISTS idx_prefs_timeline ON user_preferences(marriage_timeline);

-- Signals indexes
CREATE INDEX IF NOT EXISTS idx_signals_diet ON user_signals(diet);
CREATE INDEX IF NOT EXISTS idx_signals_drinking ON user_signals(drinking);
CREATE INDEX IF NOT EXISTS idx_signals_smoking ON user_signals(smoking);

-- ============================================================================
-- PART 12: Update sessions table to match new question flow
-- The sessions table stores in-progress intake state.
-- ============================================================================

-- No structural changes needed — sessions.answers is JSONB (flexible)
-- and sessions.current_question / current_section are generic.

-- ============================================================================
-- PART 13: Drop or update functions that reference old column names
-- ============================================================================

-- Drop old trigger that references first_name/last_name
DROP TRIGGER IF EXISTS trigger_generate_full_name ON users;
DROP FUNCTION IF EXISTS generate_full_name();

-- Drop old completeness functions (they reference dropped/renamed columns)
DROP FUNCTION IF EXISTS calculate_tier_completion(BIGINT);
DROP FUNCTION IF EXISTS calculate_tier_completion(UUID);
DROP FUNCTION IF EXISTS calculate_weighted_completeness(BIGINT);
DROP FUNCTION IF EXISTS calculate_weighted_completeness(UUID);
DROP FUNCTION IF EXISTS check_mvp_activation(BIGINT);
DROP FUNCTION IF EXISTS check_mvp_activation(UUID);
DROP FUNCTION IF EXISTS export_user_profile(BIGINT);
DROP FUNCTION IF EXISTS export_user_profile(UUID);

-- Drop completeness trigger (references old functions)
DROP TRIGGER IF EXISTS trigger_recalculate_completeness ON users;
DROP TRIGGER IF EXISTS trigger_recalculate_completeness ON user_signals;

-- ============================================================================
-- PART 14: New completeness function aligned to question flow
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_profile_completeness(p_user_id UUID)
RETURNS DECIMAL AS $$
DECLARE
    total_fields INT := 0;
    filled_fields INT := 0;
    u RECORD;
    p RECORD;
    s RECORD;
BEGIN
    SELECT * INTO u FROM users WHERE id = p_user_id;
    SELECT * INTO p FROM user_preferences WHERE user_id = p_user_id;
    SELECT * INTO s FROM user_signals WHERE user_id = p_user_id;

    IF u IS NULL THEN RETURN 0; END IF;

    -- Count users table fields
    total_fields := 15; -- full_name, gender, date_of_birth, city_current, hometown_state, hometown_city, mother_tongue, marital_status, height_cm, weight_kg, religion, education_level, education_field, occupation_sector, annual_income
    IF u.full_name IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.gender IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.date_of_birth IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.city_current IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.hometown_state IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.hometown_city IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.mother_tongue IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.marital_status IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.height_cm IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.weight_kg IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.religion IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.education_level IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.education_field IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.occupation_sector IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.annual_income IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;

    -- Count preferences fields (if row exists)
    IF p IS NOT NULL THEN
        total_fields := total_fields + 10; -- pref_religion, pref_diet, pref_drinking, pref_smoking, marriage_timeline, children_intent, pref_age_min, pref_age_max, family_involvement, living_arrangement
        IF p.pref_religion IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_diet IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_drinking IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_smoking IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.marriage_timeline IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.children_intent IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_age_min IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_age_max IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.family_involvement IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.living_arrangement IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    END IF;

    -- Count signals fields (if row exists)
    IF s IS NOT NULL THEN
        total_fields := total_fields + 5; -- diet, drinking, smoking, fitness_frequency, financial_planning
        IF s.diet IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF s.drinking IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF s.smoking IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF s.fitness_frequency IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF s.financial_planning IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    END IF;

    IF total_fields = 0 THEN RETURN 0; END IF;
    RETURN ROUND((filled_fields::DECIMAL / total_fields) * 100, 1);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PART 15: Comments documenting the new schema
-- ============================================================================

COMMENT ON TABLE users IS 'Facts about the person — identity, demographics, education, family. Source: question-flow.md';
COMMENT ON TABLE user_preferences IS 'What they want in a partner + life preferences (marriage timeline, living arrangement). Source: question-flow.md';
COMMENT ON TABLE user_signals IS 'Behavioral and lifestyle signals — diet, habits, household expectations, personality. Flat columns for intake answers; JSONB blobs for future AI-inferred signals. Source: question-flow.md';

COMMENT ON COLUMN users.gender IS 'Male or Female (question flow Q0.3)';
COMMENT ON COLUMN users.weight_kg IS 'Gender-specific buckets stored as midpoint kg (Q8)';
COMMENT ON COLUMN users.known_conditions IS 'Any known medical conditions or disabilities (Q51, sensitive section)';
COMMENT ON COLUMN users.languages_spoken IS 'Array of languages spoken besides mother tongue (Q5, multi-select)';
COMMENT ON COLUMN users.education_field IS 'Field of study: Engineering, Medicine, Business, etc. (Q17)';
COMMENT ON COLUMN users.occupation_sector IS 'Public/Private/Professional/Business/Startup/Student/Other (Q18)';

COMMENT ON COLUMN user_preferences.pref_religion_exclude IS 'Do-not-match religion list (Q13a, multi-select array)';
COMMENT ON COLUMN user_preferences.pref_caste_exclude IS 'Do-not-match caste list (Q14a, multi-select array)';
COMMENT ON COLUMN user_preferences.pref_gotra_exclude IS 'Gotra exclusion list (Q48a, sensitive section, multi-select array)';
COMMENT ON COLUMN user_preferences.pref_partner_cooking IS 'How often partner should cook — women only (Q44F)';
COMMENT ON COLUMN user_preferences.pref_partner_household IS 'How much partner should contribute to chores — women only (Q45F)';

COMMENT ON COLUMN user_signals.cooking_contribution IS 'Meals per week willing to cook — both genders (Q42M/43F)';
COMMENT ON COLUMN user_signals.do_you_cook IS 'Do you know how to cook — women only (Q42F)';
COMMENT ON COLUMN user_signals.live_with_inlaws IS 'OK living with his parents — women only (Q48F)';
COMMENT ON COLUMN user_signals.gotra IS 'User gotra — sensitive section (Q48)';
COMMENT ON COLUMN user_signals.family_property IS 'Family property ownership — sensitive section (Q49)';

COMMIT;
