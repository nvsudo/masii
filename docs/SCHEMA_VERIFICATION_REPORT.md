# JODI Schema Verification Report

**Date:** 2026-02-21  
**Issue:** Database trigger error causing bot crash after Q1 (gender selection)

---

## 🚨 CRITICAL BUG FOUND

### Root Cause
Trigger function `trigger_recalculate_completeness()` references `NEW.user_id` but `users` table doesn't have a `user_id` column.

**Error:**
```
Database query failed: record "new" has no field "user_id"
CONTEXT: SQL statement "SELECT calculate_weighted_completeness(NEW.user_id)"
PL/pgSQL function trigger_recalculate_completeness() line 3 at PERFORM
```

**Location:** `/schema/07_helper_functions.sql` line 227-231

**Current (WRONG):**
```sql
CREATE OR REPLACE FUNCTION trigger_recalculate_completeness()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM calculate_weighted_completeness(NEW.user_id);  -- ❌ NO user_id COLUMN
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Fix Required:**
```sql
CREATE OR REPLACE FUNCTION trigger_recalculate_completeness()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM calculate_weighted_completeness(NEW.id);  -- ✅ Use id (primary key)
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 📋 FULL FIELD VERIFICATION

### Bot Expectations vs Schema Reality

#### **USERS Table** (53 fields expected by bot)

| Q# | Bot Field | Schema Column | Status | Notes |
|----|-----------|---------------|--------|-------|
| 1 | gender_identity | gender_identity | ✅ MATCH | |
| 2 | looking_for_gender | ❌ MISSING | ❌ MISMATCH | Schema doesn't have this field |
| 3 | date_of_birth | date_of_birth | ✅ MATCH | |
| 4 | marital_status | marital_history | ⚠️ NAME DIFF | Bot: marital_status, Schema: marital_history |
| 5 | children_existing | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 6 | height_cm | height_cm | ✅ MATCH | |
| 7 | body_type | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 8 | complexion | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 9 | disability_status | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 10 | residency_type | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 11 | country_current | country | ⚠️ NAME DIFF | Bot: country_current, Schema: country |
| 12 | state_india | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 13 | city_current | city | ⚠️ NAME DIFF | Bot: city_current, Schema: city |
| 14 | hometown_state | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 15 | willing_to_relocate | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 17 | settling_country | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 18 | religion | religion | ✅ MATCH | |
| 19 | religious_practice | religious_practice_level | ⚠️ NAME DIFF | Bot: religious_practice, Schema: religious_practice_level |
| 21 | sect_denomination | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 22 | caste_community | caste_community | ✅ MATCH | |
| 23 | sub_caste | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 25 | mother_tongue | native_languages | ⚠️ NAME DIFF | Bot: mother_tongue (single), Schema: native_languages (array) |
| 26 | languages_spoken | ❌ MISSING | ❌ MISMATCH | Not in schema (native_languages exists but different) |
| 27 | manglik_status | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 28 | education_level | education_level | ✅ MATCH | |
| 29 | education_institute_tier | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 30 | employment_status | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 31 | work_industry | industry | ⚠️ NAME DIFF | Bot: work_industry, Schema: industry |
| 32 | career_ambition | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 33 | annual_income | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 34 | income_currency | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 35 | net_worth_range | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 36 | property_ownership | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 37 | financial_dependents | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 38 | family_type | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 39 | family_financial_status | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 40 | father_occupation | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 41 | family_values | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 42 | living_with_parents_post_marriage | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 43 | family_involvement_search | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 44 | siblings | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 45 | diet | dietary_restrictions | ⚠️ NAME DIFF | Bot: diet, Schema: dietary_restrictions |
| 47 | smoking | smoking | ✅ MATCH | |
| 49 | drinking | drinking | ✅ MATCH | |
| 51 | fitness_frequency | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 52 | social_style | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 53 | weekend_style | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 54 | pet_ownership | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 55 | sleep_schedule | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 65 | relationship_intent | relationship_intent | ✅ MATCH | |
| 66 | children_intent | children_intent | ✅ MATCH | |
| 67 | children_timeline | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 68 | gender_roles_household | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 69 | financial_management | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 70 | political_leaning | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 71 | astrology_belief | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 72 | interfaith_intercaste_openness | ❌ MISSING | ❌ MISMATCH | Not in schema |

**Summary (USERS table):**
- ✅ Exact match: 11/53 fields (21%)
- ⚠️ Name mismatch: 7/53 fields (13%)
- ❌ Missing: 35/53 fields (66%)

---

#### **PREFERENCES Table** (24 fields expected by bot)

| Q# | Bot Field | Schema Column | Status | Notes |
|----|-----------|---------------|--------|-------|
| 16 | partner_location_pref | location_preference | ⚠️ NAME DIFF | Bot: partner_location_pref (single), Schema: location_preference (array) |
| 20 | partner_religion_pref | religion_preference | ⚠️ NAME DIFF | Bot: partner_religion_pref (single), Schema: religion_preference (array) |
| 24 | caste_importance | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 46 | partner_diet_pref | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 48 | smoking_partner_ok | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 50 | drinking_partner_ok | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 56 | pref_age_range | age_min + age_max | ⚠️ STRUCTURE | Bot: single field, Schema: two separate columns |
| 57 | pref_height | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 58 | pref_complexion | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 59 | pref_education_min | education_minimum | ⚠️ NAME DIFF | Bot: pref_education_min, Schema: education_minimum |
| 60 | pref_income_range | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 61 | pref_marital_status | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 62 | pref_children_ok | children_preference | ⚠️ NAME DIFF | Bot: pref_children_ok, Schema: children_preference |
| 63 | pref_disability_ok | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 64 | pref_working_spouse | ❌ MISSING | ❌ MISMATCH | Not in schema |
| 73 | db_divorced_ok | ❌ MISSING | ❌ MISMATCH | Not in schema (dealbreakers array exists) |
| 74 | db_widowed_ok | ❌ MISSING | ❌ MISMATCH | Not in schema (dealbreakers array exists) |
| 75 | db_children_ok | ❌ MISSING | ❌ MISMATCH | Not in schema (dealbreakers array exists) |
| 76 | db_nri_ok | ❌ MISSING | ❌ MISMATCH | Not in schema (dealbreakers array exists) |
| 77 | db_age_gap_max | ❌ MISSING | ❌ MISMATCH | Not in schema |

**Summary (PREFERENCES table):**
- ✅ Exact match: 0/20 fields (0%)
- ⚠️ Name/structure mismatch: 6/20 fields (30%)
- ❌ Missing: 14/20 fields (70%)

---

## 📌 RECOMMENDATIONS

### Immediate (P0 - Blocks Onboarding)

1. **Fix trigger function** (schema/07_helper_functions.sql):
   ```sql
   -- Change NEW.user_id → NEW.id
   CREATE OR REPLACE FUNCTION trigger_recalculate_completeness()
   RETURNS TRIGGER AS $$
   BEGIN
     PERFORM calculate_weighted_completeness(NEW.id);  -- ✅ FIX
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

2. **Add missing USERS table columns** (35 fields):
   - Follow the 77-field MVP spec from TELEGRAM_ONBOARDING_SEQUENCE.md
   - Add columns as VARCHAR/TEXT (safe default):
     ```sql
     ALTER TABLE users ADD COLUMN IF NOT EXISTS looking_for_gender VARCHAR(50);
     ALTER TABLE users ADD COLUMN IF NOT EXISTS children_existing VARCHAR(50);
     ALTER TABLE users ADD COLUMN IF NOT EXISTS body_type VARCHAR(50);
     -- ... (32 more)
     ```

3. **Add missing PREFERENCES table columns** (14 fields):
   ```sql
   ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS caste_importance VARCHAR(50);
   ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS partner_diet_pref VARCHAR(100);
   -- ... (12 more)
   ```

4. **Rename mismatched columns** OR **update bot code**:
   - Option A: Rename schema columns to match bot (7 in users, 6 in preferences)
   - Option B: Update bot field mappings to match schema (simpler, less risky)

### Prioritization per N's Mandate

**"Where there is a mismatch, prioritize the 77-field MVP schema I gave in the MVP and 100+ data point document"**

✅ **Action:** Bot code is correct (reflects MVP spec). Schema needs to be updated to match bot expectations.

---

## 📝 NEXT STEPS

1. **Blitz:** Apply trigger fix + add missing columns (migration script)
2. **DevOps:** Apply migration to Supabase, restart bot
3. **Test:** Verify Q1 (gender) → Q2 (looking_for_gender) works
4. **Full test:** Run through all 77 questions to verify schema completeness

**ETA:** <2 hours (migration + deployment)
