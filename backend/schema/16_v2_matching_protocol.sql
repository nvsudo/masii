-- Migration 16: V2 Matching Protocol Schema Changes
-- Aligns database to the v2 matching protocol (docs/question_matching_protocol.md)
--
-- What changed in v2:
--   - Every data question now has an explicit partner preference question
--   - 14 new partner preference fields needed in user_preferences
--   - 6 questions removed (sect, family values, family involvement, gotra, property, financial contribution)
--   - "Hometown" reframed to "Where did you grow up?" (raised_in)
--   - Medical conditions and disability split into separate fields
--   - Mother tongue preference is now a hard gate
--   - Marital status preference is now multi-select (array)
--
-- Run against: Supabase (PostgreSQL 15+)
-- Date: March 2026

BEGIN;

-- ============================================================================
-- PART 1: USERS TABLE — Rename hometown → raised_in
-- Q3 reframed from "Where is your family originally from?" to "Where did you grow up?"
-- ============================================================================

-- Rename existing hometown columns to raised_in
ALTER TABLE users RENAME COLUMN hometown_state TO raised_in_state;
ALTER TABLE users RENAME COLUMN hometown_city TO raised_in_city;

-- Add country-level field for "India" vs "Outside India" + specific country
ALTER TABLE users ADD COLUMN IF NOT EXISTS raised_in_country VARCHAR(100);

COMMENT ON COLUMN users.raised_in_state IS 'State where user grew up — if raised in India (Q3)';
COMMENT ON COLUMN users.raised_in_city IS 'City where user grew up (Q3)';
COMMENT ON COLUMN users.raised_in_country IS 'Country where user grew up — "India" or specific country if abroad (Q3)';

-- ============================================================================
-- PART 2: USERS TABLE — Split disability from medical conditions
-- Q51 split into: medical conditions (known_conditions) + disability (new)
-- ============================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS disability VARCHAR(50);

COMMENT ON COLUMN users.known_conditions IS 'Known medical conditions — diabetes, asthma, thyroid, etc. (Q51)';
COMMENT ON COLUMN users.disability IS 'Physical disability — No / Yes / Prefer not to say (Q51-disability)';

-- ============================================================================
-- PART 3: USER_PREFERENCES TABLE — Add 12 new partner preference columns
-- These are the explicit partner preferences added in v2.
-- Each follows a data question with "what do you want in a partner?"
-- ============================================================================

-- Q2-pref: Where should your partner currently live?
-- Hard gate. Options: Same city / Same state / Same country / Anywhere / Specific countries
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_current_location VARCHAR(100);
COMMENT ON COLUMN user_preferences.pref_current_location IS 'Partner current location preference — hard gate (Q2-pref)';

-- Q3-pref: Where should your partner have been raised?
-- Hard gate. Options vary by user location (India vs abroad)
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_raised_in VARCHAR(100);
COMMENT ON COLUMN user_preferences.pref_raised_in IS 'Partner raised-in preference — hard gate (Q3-pref)';

-- Q6-pref: What marital status are you open to in a partner?
-- Hard gate. Multi-select: Never married / Divorced / Widowed / Awaiting divorce / Any
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_marital_status TEXT[];
COMMENT ON COLUMN user_preferences.pref_marital_status IS 'Accepted partner marital statuses — hard gate, multi-select array (Q6-pref)';

-- Q6a-pref: Are you open to a partner who has children?
-- Hard gate. Options: Yes / Only if they don't live with them / No
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_children_existing VARCHAR(50);
COMMENT ON COLUMN user_preferences.pref_children_existing IS 'Partner existing children preference — hard gate (Q6a-pref)';

-- Q17-pref: Partner education field preference?
-- Scored. Options: Same as mine / Doesn't matter
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_education_field VARCHAR(100);
COMMENT ON COLUMN user_preferences.pref_education_field IS 'Partner education field preference — scored (Q17-pref)';

-- Q27-pref: Partner siblings preference?
-- Scored. Options: Must have siblings / Single child is fine / Doesn't matter
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_siblings VARCHAR(50);
COMMENT ON COLUMN user_preferences.pref_siblings IS 'Partner siblings preference — scored (Q27-pref)';

-- Q37a-pref: Partner children timeline preference?
-- Scored. Options: Soon after marriage / After 2-3 years / After 4+ years / Doesn't matter
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_children_timeline VARCHAR(50);
COMMENT ON COLUMN user_preferences.pref_children_timeline IS 'Partner children timeline preference — scored (Q37a-pref)';

-- Q38-pref: Partner living arrangement preference?
-- Scored. Options: With parents / Near parents / Independent / Open / Doesn't matter
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_living_arrangement VARCHAR(100);
COMMENT ON COLUMN user_preferences.pref_living_arrangement IS 'Partner living arrangement preference — scored (Q38-pref)';

-- Q42M-pref: How often do you need your partner to cook? (men only)
-- Scored (WOW 1.5 when above expectations). Options: Regularly / Sometimes / Rarely / Never
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_partner_cooking_freq VARCHAR(100);
COMMENT ON COLUMN user_preferences.pref_partner_cooking_freq IS 'Partner cooking frequency expectation — men only, WOW factor (Q42M-pref)';

-- Q42F-pref: Do you need your partner to know how to cook? (men only, about women)
-- Scored. Options: Yes must cook regularly / Some cooking is enough / Doesn't matter
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_partner_can_cook VARCHAR(50);
COMMENT ON COLUMN user_preferences.pref_partner_can_cook IS 'Partner cooking ability requirement — men only (Q42F-pref)';

-- Q39a: Countries willing to relocate to (follow-up to relocation question)
-- Multi-select array
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS relocation_countries TEXT[];
COMMENT ON COLUMN user_preferences.relocation_countries IS 'Specific countries willing to relocate to — multi-select array (Q39a)';

-- Q51a-disability: Are you open to a partner with a disability?
-- Hard gate. Options: Yes / Depends / No
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS pref_disability VARCHAR(50);
COMMENT ON COLUMN user_preferences.pref_disability IS 'Partner disability preference — hard gate (Q51a-disability)';

-- NOTE: pref_family_type already exists from migration 13 (no action needed)
-- It now stores: Same as mine / Doesn't matter (Q22-pref)

-- ============================================================================
-- PART 4: USER_PREFERENCES TABLE — Drop deprecated columns (v2 skipped questions)
-- These questions are removed from the free-tier intake flow.
-- Data is NOT deleted — columns are dropped. If you need to preserve data,
-- back up first.
-- ============================================================================

-- Q11 (sect/denomination) — removed: not enough data to tree properly
ALTER TABLE user_preferences DROP COLUMN IF EXISTS sect_denomination;

-- Q28 (family involvement) — removed: if on Masii, family is involved
ALTER TABLE user_preferences DROP COLUMN IF EXISTS family_involvement;

-- Q48a (gotra exclude list) — removed: gotra questions skipped in v2
ALTER TABLE user_preferences DROP COLUMN IF EXISTS pref_gotra_exclude;

-- ============================================================================
-- PART 5: USER_SIGNALS TABLE — Drop deprecated columns (v2 skipped questions)
-- ============================================================================

-- Q48 (gotra) — removed: can match later, future premium
ALTER TABLE user_signals DROP COLUMN IF EXISTS gotra;

-- Q24 (family values) — removed: self-assessment unreliable
ALTER TABLE user_signals DROP COLUMN IF EXISTS family_values;

-- Q49 (family property) — removed: covered by updated family wealth tiers (Q23)
ALTER TABLE user_signals DROP COLUMN IF EXISTS family_property;

-- Q47F (women's financial contribution view) — removed: Q46 already covers this
ALTER TABLE user_signals DROP COLUMN IF EXISTS financial_contribution;

-- ============================================================================
-- PART 6: Update comments on existing columns that changed behavior in v2
-- ============================================================================

-- Mother tongue preference is now a HARD GATE (was soft filter)
COMMENT ON COLUMN user_preferences.pref_mother_tongue IS 'Partner mother tongue preference — NOW A HARD GATE in v2 (Q15)';

-- Height preference is now a HARD GATE (was ignored)
COMMENT ON COLUMN user_preferences.pref_height_min IS 'Partner minimum height in cm — NOW A HARD GATE in v2 (Q41)';
COMMENT ON COLUMN user_preferences.pref_height_max IS 'Partner maximum height in cm — NOW A HARD GATE in v2 (Q41)';

-- Marital status on users is now used as a HARD GATE (was stub)
COMMENT ON COLUMN users.marital_status IS 'Current marital status — NOW A HARD GATE in v2, matched against partner pref_marital_status (Q6)';

-- Diet preference is now a HARD GATE (was soft)
COMMENT ON COLUMN user_preferences.pref_diet IS 'Partner diet preference — NOW A HARD GATE in v2. Options: Same as mine / Any but not non-veg / Veg / Doesn''t matter (Q33)';

-- Marriage timeline is now a HARD GATE (was soft)
COMMENT ON COLUMN user_preferences.marriage_timeline IS 'How soon looking to get married — NOW A HARD GATE, must be within 1 step (Q36). Options: Within 1 year / 1-2 years / 2-3 years / Just exploring';

-- Known conditions text updated (split from disability)
COMMENT ON COLUMN user_preferences.pref_conditions IS 'Partner medical condition preference — hard gate. Split from disability in v2 (Q51a)';

-- ============================================================================
-- PART 7: Indexes for new columns used in matching filters
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_prefs_current_location ON user_preferences(pref_current_location);
CREATE INDEX IF NOT EXISTS idx_prefs_raised_in ON user_preferences(pref_raised_in);
CREATE INDEX IF NOT EXISTS idx_prefs_marital_status ON user_preferences USING gin(pref_marital_status);
CREATE INDEX IF NOT EXISTS idx_prefs_children_existing ON user_preferences(pref_children_existing);
CREATE INDEX IF NOT EXISTS idx_prefs_disability ON user_preferences(pref_disability);
CREATE INDEX IF NOT EXISTS idx_users_raised_in ON users(raised_in_country, raised_in_state);
CREATE INDEX IF NOT EXISTS idx_users_disability ON users(disability);

-- ============================================================================
-- PART 8: Update profile completeness function for v2 fields
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

    -- Count users table fields (16 core fields)
    total_fields := 16;
    IF u.full_name IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.gender IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.date_of_birth IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.city_current IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.raised_in_country IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.mother_tongue IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.marital_status IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.height_cm IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.weight_kg IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.religion IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.education_level IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.education_field IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.occupation_sector IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.annual_income IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.family_type IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    IF u.siblings IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;

    -- Count preferences fields (14 core fields including new v2 prefs)
    IF p IS NOT NULL THEN
        total_fields := total_fields + 14;
        IF p.pref_religion IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_diet IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_drinking IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_smoking IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.marriage_timeline IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.children_intent IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_age_min IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_age_max IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_current_location IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_raised_in IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_marital_status IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.living_arrangement IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_height_min IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF p.pref_mother_tongue IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
    END IF;

    -- Count signals fields (5 core fields)
    IF s IS NOT NULL THEN
        total_fields := total_fields + 5;
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
-- SUMMARY — Quick reference for the person running this migration
-- ============================================================================
--
-- USERS TABLE:
--   RENAME  hometown_state      → raised_in_state
--   RENAME  hometown_city       → raised_in_city
--   ADD     raised_in_country     VARCHAR(100)
--   ADD     disability            VARCHAR(50)
--
-- USER_PREFERENCES TABLE:
--   ADD     pref_current_location   VARCHAR(100)   -- hard gate
--   ADD     pref_raised_in          VARCHAR(100)   -- hard gate
--   ADD     pref_marital_status     TEXT[]          -- hard gate, multi-select
--   ADD     pref_children_existing  VARCHAR(50)    -- hard gate
--   ADD     pref_education_field    VARCHAR(100)   -- scored
--   ADD     pref_siblings           VARCHAR(50)    -- scored
--   ADD     pref_children_timeline  VARCHAR(50)    -- scored
--   ADD     pref_living_arrangement VARCHAR(100)   -- scored
--   ADD     pref_partner_cooking_freq VARCHAR(100) -- WOW factor (men only)
--   ADD     pref_partner_can_cook   VARCHAR(50)    -- scored (men only)
--   ADD     relocation_countries    TEXT[]          -- multi-select
--   ADD     pref_disability         VARCHAR(50)    -- hard gate
--   DROP    sect_denomination                      -- v2: question skipped
--   DROP    family_involvement                     -- v2: question skipped
--   DROP    pref_gotra_exclude                     -- v2: question skipped
--
-- USER_SIGNALS TABLE:
--   DROP    gotra                                  -- v2: question skipped
--   DROP    family_values                          -- v2: question skipped
--   DROP    family_property                        -- v2: question skipped
--   DROP    financial_contribution                  -- v2: question skipped
--
-- BEHAVIOR CHANGES (no schema change, just matching logic):
--   pref_mother_tongue    → now a HARD GATE (was soft)
--   pref_height_min/max   → now a HARD GATE (was ignored)
--   marital_status        → now a HARD GATE (was stub)
--   pref_diet             → now a HARD GATE (was soft)
--   marriage_timeline     → now a HARD GATE (was soft)
--

COMMIT;
