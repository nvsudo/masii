-- ============================================================================
-- JODI Schema Fix: Update calculate_tier_completion to use renamed columns
-- Fix references to: city → city_current, marital_history → marital_status, dietary_restrictions → diet
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
      -- Tier 1: 17 required hard filter columns (includes 3 name fields: first_name, last_name, full_name)
      SELECT COUNT(*) INTO total_fields FROM (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name IN (
          'first_name', 'last_name', 'full_name', 'date_of_birth', 'age', 'gender_identity', 'sexual_orientation',
          'city_current', 'nationality', 'religion', 'children_intent', 'marital_status',
          'smoking', 'drinking', 'relationship_intent', 'relationship_timeline', 'diet'
        )
      ) AS t1;
      
      -- Count populated fields (alias is optional, not counted)
      -- ✅ FIXED: Updated column names to match renamed schema
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
      SELECT (
        (SELECT COUNT(*) FROM jsonb_object_keys(COALESCE(lifestyle, '{}'::jsonb)) 
         WHERE (lifestyle->key->>'confidence')::decimal >= 0.70) +
        (SELECT COUNT(*) FROM jsonb_object_keys(COALESCE(values, '{}'::jsonb))
         WHERE (values->key->>'confidence')::decimal >= 0.70) +
        (SELECT COUNT(*) FROM jsonb_object_keys(COALESCE(relationship_style, '{}'::jsonb))
         WHERE (relationship_style->key->>'confidence')::decimal >= 0.70)
      ) INTO populated_fields
      FROM user_signals WHERE user_id = p_user_id;
      
    WHEN 3 THEN
      -- Tier 3: 26 fields (personality 14 + family_background 8 + media_signals 8)
      total_fields := 30;
      
      SELECT (
        (SELECT COUNT(*) FROM jsonb_object_keys(COALESCE(personality, '{}'::jsonb))
         WHERE (personality->key->>'confidence')::decimal >= 0.70) +
        (SELECT COUNT(*) FROM jsonb_object_keys(COALESCE(family_background, '{}'::jsonb))
         WHERE (family_background->key->>'confidence')::decimal >= 0.70) +
        (SELECT COUNT(*) FROM jsonb_object_keys(COALESCE(media_signals, '{}'::jsonb))
         WHERE (media_signals->key->>'confidence')::decimal >= 0.70)
      ) INTO populated_fields
      FROM user_signals WHERE user_id = p_user_id;
      
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
'Calculate tier completion percentage based on populated fields with confidence >= 0.70 (FIXED: uses renamed columns)';
