-- ============================================================================
-- JODI Schema Upgrade: User Preferences Table
-- What they're looking for in a partner (hard filters + soft preferences)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  
  -- ===========================================================================
  -- HARD FILTER PREFERENCES (Must match for elimination)
  -- ===========================================================================
  age_min INT NOT NULL DEFAULT 18,
  age_max INT NOT NULL DEFAULT 99,
  gender_preference TEXT[], -- Array: ["Male", "Female", "Non-binary"]
  
  location_preference TEXT[], -- Cities/countries open to: ["Dubai", "Mumbai", "New York"]
  max_distance_km INT, -- For location-based matching
  open_to_relocation BOOLEAN DEFAULT FALSE,
  
  religion_preference TEXT[], -- ["Same religion", "Open to all", "Muslim", "Hindu", ...]
  religion_importance VARCHAR(50), -- "Must match" | "Prefer same" | "Open"
  
  children_preference VARCHAR(100), -- "OK with existing kids" | "No existing kids" | "Flexible"
  education_minimum VARCHAR(100), -- "Bachelor's" | "Master's" | "PhD" | "No preference"
  
  -- ===========================================================================
  -- SOFT PREFERENCES WITH WEIGHTS (Scoring, not elimination)
  -- ===========================================================================
  soft_preferences JSONB DEFAULT '{}'::jsonb,
  /*
  Schema per preference:
  {
    "preference_name": {
      "values": [<array of acceptable values>],
      "weight": <0.0-1.0>,  -- How important (1.0 = critical, 0.3 = nice-to-have)
      "type": "exact_match" | "range" | "compatibility_score"
    }
  }
  
  Example fields:
  - height_range: {min: 165, max: 190, weight: 0.5, type: "range"}
  - dietary_compatibility: {values: ["Vegetarian", "Vegan"], weight: 0.7, type: "exact_match"}
  - family_involvement: {value: "Moderate", weight: 0.6, type: "compatibility_score"}
  - political_alignment: {value: "Progressive", weight: 0.8, type: "compatibility_score"}
  - ambition_level: {value: "Driven", weight: 0.9, type: "compatibility_score"}
  - social_energy_match: {value: "Similar", weight: 0.6, type: "compatibility_score"}
  - religious_practice_level: {value: "Similar", weight: 0.8, type: "compatibility_score"}
  - lifestyle_compatibility: {areas: ["fitness", "travel", "social"], weight: 0.7}
  */
  
  -- ===========================================================================
  -- EXPLICIT DEALBREAKERS (Instant elimination)
  -- ===========================================================================
  dealbreakers TEXT[], -- ["Smoking", "Wants kids when I don't", "Different religion", ...]
  
  -- ===========================================================================
  -- GREEN FLAGS (What excites them in a partner)
  -- ===========================================================================
  green_flags TEXT[], -- ["Emotionally intelligent", "Ambitious", "Family-oriented", ...]
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT user_preferences_user_id_unique UNIQUE(user_id),
  CONSTRAINT age_range_valid CHECK (age_min < age_max)
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_soft_preferences_gin ON user_preferences USING gin(soft_preferences jsonb_path_ops);

-- Add updated_at trigger
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_preferences IS 'Partner requirements: hard filters (elimination) + soft preferences (scoring)';
COMMENT ON COLUMN user_preferences.soft_preferences IS 'Weighted preferences for compatibility scoring, not elimination';
COMMENT ON COLUMN user_preferences.dealbreakers IS 'Explicit dealbreakers that cause instant match rejection';
COMMENT ON COLUMN user_preferences.green_flags IS 'Positive traits that increase match appeal';
