-- ============================================================================
-- JODI Helper Functions for Extraction Pipeline
-- CRUD operations for JSONB signals
-- ============================================================================

-- Function to remove a specific field from JSONB signals
CREATE OR REPLACE FUNCTION remove_user_signal(
  p_user_id BIGINT,
  p_signal_category TEXT,
  p_field_name TEXT
)
RETURNS VOID AS $$
BEGIN
  EXECUTE format(
    'UPDATE user_signals SET %I = %I - %L WHERE user_id = $1',
    p_signal_category,
    p_signal_category,
    p_field_name
  ) USING p_user_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION remove_user_signal IS 
'Remove a specific field from JSONB signal category (used for DELETE operations)';

-- Function to get all signals for a user with confidence >= threshold
CREATE OR REPLACE FUNCTION get_user_signals_above_confidence(
  p_user_id BIGINT,
  p_confidence_threshold DECIMAL DEFAULT 0.70
)
RETURNS TABLE(
  category TEXT,
  field TEXT,
  value JSONB,
  confidence DECIMAL,
  source TEXT,
  updated_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    'lifestyle' AS category,
    key AS field,
    value->'value' AS value,
    (value->>'confidence')::decimal AS confidence,
    value->>'source' AS source,
    (value->>'updated_at')::timestamptz AS updated_at
  FROM user_signals, jsonb_each(lifestyle)
  WHERE user_id = p_user_id
    AND (value->>'confidence')::decimal >= p_confidence_threshold
  
  UNION ALL
  
  SELECT 
    'values' AS category,
    key AS field,
    value->'value' AS value,
    (value->>'confidence')::decimal AS confidence,
    value->>'source' AS source,
    (value->>'updated_at')::timestamptz AS updated_at
  FROM user_signals, jsonb_each(values)
  WHERE user_id = p_user_id
    AND (value->>'confidence')::decimal >= p_confidence_threshold
  
  UNION ALL
  
  SELECT 
    'relationship_style' AS category,
    key AS field,
    value->'value' AS value,
    (value->>'confidence')::decimal AS confidence,
    value->>'source' AS source,
    (value->>'updated_at')::timestamptz AS updated_at
  FROM user_signals, jsonb_each(relationship_style)
  WHERE user_id = p_user_id
    AND (value->>'confidence')::decimal >= p_confidence_threshold
  
  UNION ALL
  
  SELECT 
    'personality' AS category,
    key AS field,
    value->'value' AS value,
    (value->>'confidence')::decimal AS confidence,
    value->>'source' AS source,
    (value->>'updated_at')::timestamptz AS updated_at
  FROM user_signals, jsonb_each(personality)
  WHERE user_id = p_user_id
    AND (value->>'confidence')::decimal >= p_confidence_threshold
  
  UNION ALL
  
  SELECT 
    'family_background' AS category,
    key AS field,
    value->'value' AS value,
    (value->>'confidence')::decimal AS confidence,
    value->>'source' AS source,
    (value->>'updated_at')::timestamptz AS updated_at
  FROM user_signals, jsonb_each(family_background)
  WHERE user_id = p_user_id
    AND (value->>'confidence')::decimal >= p_confidence_threshold
  
  UNION ALL
  
  SELECT 
    'media_signals' AS category,
    key AS field,
    value->'value' AS value,
    (value->>'confidence')::decimal AS confidence,
    value->>'source' AS source,
    (value->>'updated_at')::timestamptz AS updated_at
  FROM user_signals, jsonb_each(media_signals)
  WHERE user_id = p_user_id
    AND (value->>'confidence')::decimal >= p_confidence_threshold;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_signals_above_confidence IS 
'Get all user signals across all JSONB categories with confidence >= threshold';

-- Function to export full user profile as JSON
CREATE OR REPLACE FUNCTION export_user_profile(p_user_id BIGINT)
RETURNS JSONB AS $$
DECLARE
  profile JSONB;
  tier1_data JSONB;
  tier2_data JSONB;
  tier3_data JSONB;
  preferences_data JSONB;
BEGIN
  -- Tier 1: Users table hard filters
  SELECT jsonb_build_object(
    'first_name', first_name,
    'last_name', last_name,
    'full_name', full_name,
    'alias', alias,
    'date_of_birth', date_of_birth,
    'age', age,
    'gender_identity', gender_identity,
    'sexual_orientation', sexual_orientation,
    'city', city,
    'country', country,
    'nationality', nationality,
    'ethnicity', ethnicity,
    'native_languages', native_languages,
    'religion', religion,
    'children_intent', children_intent,
    'marital_history', marital_history,
    'smoking', smoking,
    'drinking', drinking,
    'dietary_restrictions', dietary_restrictions,
    'relationship_intent', relationship_intent,
    'relationship_timeline', relationship_timeline,
    'occupation', occupation,
    'industry', industry,
    'education_level', education_level,
    'height_cm', height_cm,
    'tier_level', tier_level,
    'profile_active', profile_active,
    'completeness_score', completeness_score
  ) INTO tier1_data
  FROM users WHERE id = p_user_id;
  
  -- Preferences
  SELECT jsonb_build_object(
    'age_min', age_min,
    'age_max', age_max,
    'gender_preference', gender_preference,
    'location_preference', location_preference,
    'open_to_relocation', open_to_relocation,
    'religion_preference', religion_preference,
    'children_preference', children_preference,
    'education_minimum', education_minimum,
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

COMMENT ON FUNCTION export_user_profile IS 
'Export complete user profile as structured JSON (for AI context or debugging)';

-- Function to calculate weighted completeness score
CREATE OR REPLACE FUNCTION calculate_weighted_completeness(p_user_id BIGINT)
RETURNS DECIMAL AS $$
DECLARE
  t1_completion DECIMAL;
  t2_completion DECIMAL;
  t3_completion DECIMAL;
  weighted_score DECIMAL;
BEGIN
  t1_completion := calculate_tier_completion(p_user_id, 1);
  t2_completion := calculate_tier_completion(p_user_id, 2);
  t3_completion := calculate_tier_completion(p_user_id, 3);
  
  -- Weighted: T1 (50%), T2 (35%), T3 (15%)
  weighted_score := (t1_completion * 0.50) + (t2_completion * 0.35) + (t3_completion * 0.15);
  
  -- Update users table
  UPDATE users 
  SET completeness_score = ROUND(weighted_score, 2)
  WHERE id = p_user_id;
  
  RETURN ROUND(weighted_score, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_weighted_completeness IS 
'Calculate weighted completeness score (T1=50%, T2=35%, T3=15%) and update users table';

-- Trigger to auto-recalculate completeness on signal updates
CREATE OR REPLACE FUNCTION trigger_recalculate_completeness()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM calculate_weighted_completeness(NEW.user_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_completeness_on_signal_change ON user_signals;
CREATE TRIGGER update_completeness_on_signal_change
  AFTER INSERT OR UPDATE ON user_signals
  FOR EACH ROW
  EXECUTE FUNCTION trigger_recalculate_completeness();

COMMENT ON TRIGGER update_completeness_on_signal_change ON user_signals IS 
'Auto-recalculate completeness score when signals are updated';

-- Trigger to auto-recalculate completeness on users table updates
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
    OLD.children_intent IS DISTINCT FROM NEW.children_intent
  )
  EXECUTE FUNCTION trigger_recalculate_completeness();

COMMENT ON TRIGGER update_completeness_on_user_change ON users IS 
'Auto-recalculate completeness score when Tier 1 fields are updated';
