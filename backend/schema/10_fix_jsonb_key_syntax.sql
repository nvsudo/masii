-- ============================================================================
-- JODI Schema Fix: Fix JSONB key counting syntax in calculate_tier_completion
-- Error: column "key" does not exist
-- Fix: Use proper lateral join syntax for jsonb_object_keys
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_tier_completion(
  p_user_id BIGINT,
  p_tier INT
)
RETURNS DECIMAL AS $$
DECLARE
  total_fields INT;
  populated_fields INT;
  completion DECIMAL;
BEGIN
  CASE p_tier
    WHEN 1 THEN
      -- Tier 1: 17 required hard filter columns
      total_fields := 17;
      
      -- Count populated fields
      SELECT 
        (CASE WHEN first_name IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN last_name IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN full_name IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN date_of_birth IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN age IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN gender_identity IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN sexual_orientation IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN city_current IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN nationality IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN religion IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN children_intent IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN marital_status IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN smoking IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN drinking IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN relationship_intent IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN relationship_timeline IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN diet IS NOT NULL THEN 1 ELSE 0 END)
      INTO populated_fields
      FROM users WHERE id = p_user_id;
      
    WHEN 2 THEN
      -- Tier 2: 33 fields (lifestyle 13 + values 10 + relationship_style 10)
      total_fields := 33;
      
      -- Count JSONB fields with confidence >= 0.70
      -- ✅ FIXED: Use proper lateral join syntax
      SELECT COALESCE(
        (SELECT COUNT(*) 
         FROM user_signals us, 
         LATERAL jsonb_each(COALESCE(us.lifestyle, '{}'::jsonb)) AS lifestyle_entry
         WHERE us.user_id = p_user_id 
         AND (lifestyle_entry.value->>'confidence')::decimal >= 0.70),
        0
      ) +
      COALESCE(
        (SELECT COUNT(*) 
         FROM user_signals us, 
         LATERAL jsonb_each(COALESCE(us.values, '{}'::jsonb)) AS values_entry
         WHERE us.user_id = p_user_id 
         AND (values_entry.value->>'confidence')::decimal >= 0.70),
        0
      ) +
      COALESCE(
        (SELECT COUNT(*) 
         FROM user_signals us, 
         LATERAL jsonb_each(COALESCE(us.relationship_style, '{}'::jsonb)) AS rel_entry
         WHERE us.user_id = p_user_id 
         AND (rel_entry.value->>'confidence')::decimal >= 0.70),
        0
      )
      INTO populated_fields;
      
    WHEN 3 THEN
      -- Tier 3: 30 fields (personality 14 + family_background 8 + media_signals 8)
      total_fields := 30;
      
      -- ✅ FIXED: Use proper lateral join syntax
      SELECT COALESCE(
        (SELECT COUNT(*) 
         FROM user_signals us, 
         LATERAL jsonb_each(COALESCE(us.personality, '{}'::jsonb)) AS personality_entry
         WHERE us.user_id = p_user_id 
         AND (personality_entry.value->>'confidence')::decimal >= 0.70),
        0
      ) +
      COALESCE(
        (SELECT COUNT(*) 
         FROM user_signals us, 
         LATERAL jsonb_each(COALESCE(us.family_background, '{}'::jsonb)) AS family_entry
         WHERE us.user_id = p_user_id 
         AND (family_entry.value->>'confidence')::decimal >= 0.70),
        0
      ) +
      COALESCE(
        (SELECT COUNT(*) 
         FROM user_signals us, 
         LATERAL jsonb_each(COALESCE(us.media_signals, '{}'::jsonb)) AS media_entry
         WHERE us.user_id = p_user_id 
         AND (media_entry.value->>'confidence')::decimal >= 0.70),
        0
      )
      INTO populated_fields;
      
    ELSE
      RETURN 0;
  END CASE;
  
  IF total_fields = 0 THEN
    RETURN 0;
  END IF;
  
  completion := (populated_fields::decimal / total_fields::decimal) * 100;
  RETURN ROUND(completion, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_tier_completion IS 
'Calculate tier completion percentage based on populated fields with confidence >= 0.70 (FIXED: proper JSONB lateral join syntax)';
