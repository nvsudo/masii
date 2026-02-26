-- ============================================================================
-- JODI Schema Upgrade: Matches Table
-- Tier 4 Calibration: Post-match reactions and revealed preferences
-- ============================================================================

-- Drop existing matches table if empty (safe upgrade)
DROP TABLE IF EXISTS matches CASCADE;

CREATE TABLE matches (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  matched_user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  
  -- ===========================================================================
  -- MATCH METADATA
  -- ===========================================================================
  match_score DECIMAL(5,2), -- 0.00-100.00 compatibility score
  match_explanation JSONB, -- Why they were matched (for transparency)
  /*
  Example structure:
  {
    "hard_filters_matched": ["Age range", "Location", "Religion", "Children intent"],
    "top_compatibility_signals": [
      {"signal": "Ambition level", "score": 0.95},
      {"signal": "Family values", "score": 0.88},
      {"signal": "Lifestyle compatibility", "score": 0.82}
    ],
    "potential_concerns": ["Different political views"],
    "overall_reasoning": "Strong values alignment and lifestyle compatibility..."
  }
  */
  
  -- ===========================================================================
  -- TIER 4: FIRST IMPRESSION REACTIONS (Immediately after match reveal)
  -- ===========================================================================
  user_first_impression VARCHAR(50), -- "Excited" | "Neutral" | "Disappointed" | "Surprised"
  user_photo_reaction VARCHAR(50), -- "Attracted" | "Not attracted" | "Neutral"
  user_profile_notes TEXT, -- What stood out (positive or negative)
  
  date_willingness VARCHAR(50), -- "Eager" | "Willing" | "Reluctant" | "Declined"
  date_willingness_reason TEXT, -- Why eager/declined
  
  -- ===========================================================================
  -- TIER 4: POST-DATE FEEDBACK (If date happened)
  -- ===========================================================================
  date_happened BOOLEAN DEFAULT FALSE,
  date_scheduled_at TIMESTAMPTZ,
  date_completed_at TIMESTAMPTZ,
  
  date_feedback JSONB,
  /*
  Example structure:
  {
    "chemistry": 7,        // 1-10 scale
    "conversation": 8,     // 1-10 scale
    "attraction": 6,       // 1-10 scale
    "energy_match": 9,     // 1-10 scale
    "notes": "Great conversation but didn't feel romantic spark",
    "want_second_date": false,
    "what_worked": ["Easy to talk to", "Shared interests"],
    "what_didnt": ["No physical chemistry", "Different sense of humor"]
  }
  */
  
  -- ===========================================================================
  -- TIER 4: CALIBRATION LEARNINGS (System-inferred from reactions)
  -- ===========================================================================
  surprise_learnings TEXT[], -- What they liked that they didn't expect
  revealed_preferences JSONB, -- Stated vs. revealed preference gaps
  /*
  Example structure:
  {
    "gaps": [
      {
        "stated": "Prefer someone extroverted",
        "revealed": "Reacted very positively to introverted match",
        "confidence": 0.85
      },
      {
        "stated": "Height matters (6ft+)",
        "revealed": "Was attracted to 5'9\" match",
        "confidence": 0.78
      }
    ],
    "new_preferences_discovered": [
      "Values dry humor (didn't state this explicitly)",
      "Attracted to nerdy personality (stated 'athletic' preference)"
    ]
  }
  */
  
  -- ===========================================================================
  -- MATCH STATUS
  -- ===========================================================================
  status VARCHAR(50) DEFAULT 'pending', -- "pending" | "accepted" | "declined" | "date_scheduled" | "date_completed" | "ghosted"
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  feedback_at TIMESTAMPTZ, -- When user provided feedback
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT no_self_match CHECK (user_id != matched_user_id),
  CONSTRAINT unique_match_pair UNIQUE(user_id, matched_user_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_user_id ON matches(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status);
CREATE INDEX IF NOT EXISTS idx_matches_feedback ON matches(user_id) WHERE date_happened;
CREATE INDEX IF NOT EXISTS idx_match_explanation_gin ON matches USING gin(match_explanation jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_revealed_preferences_gin ON matches USING gin(revealed_preferences jsonb_path_ops);

-- Add updated_at trigger
DROP TRIGGER IF EXISTS update_matches_updated_at ON matches;
CREATE TRIGGER update_matches_updated_at
    BEFORE UPDATE ON matches
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================================================
-- HELPER FUNCTION: Extract stated vs revealed preference gaps for a user
-- ===========================================================================
CREATE OR REPLACE FUNCTION get_revealed_preference_gaps(p_user_id BIGINT)
RETURNS TABLE(
  stated TEXT,
  revealed TEXT,
  confidence DECIMAL(3,2),
  match_count INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    (jsonb_array_elements(revealed_preferences->'gaps')->>'stated')::TEXT,
    (jsonb_array_elements(revealed_preferences->'gaps')->>'revealed')::TEXT,
    (jsonb_array_elements(revealed_preferences->'gaps')->>'confidence')::DECIMAL(3,2),
    COUNT(*)::INT
  FROM matches
  WHERE user_id = p_user_id
    AND revealed_preferences IS NOT NULL
  GROUP BY 1, 2, 3
  ORDER BY 4 DESC, 3 DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE matches IS 'Match history with Tier 4 calibration data (reactions, feedback, revealed preferences)';
COMMENT ON COLUMN matches.match_explanation IS 'Transparent explanation of why they were matched';
COMMENT ON COLUMN matches.user_first_impression IS 'Immediate reaction: Excited/Neutral/Disappointed/Surprised';
COMMENT ON COLUMN matches.date_feedback IS 'Structured feedback after date (chemistry, conversation, attraction scores)';
COMMENT ON COLUMN matches.revealed_preferences IS 'Tier 4 gold: Stated preferences vs. actual reactions (calibration data)';
COMMENT ON FUNCTION get_revealed_preference_gaps IS 'Aggregates stated vs revealed gaps across all matches for a user';
