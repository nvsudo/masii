-- ============================================================================
-- JODI Schema Upgrade: Tier Progress Tracking
-- Tracks user progress through 4-tier onboarding + MVP activation
-- ============================================================================

CREATE TABLE IF NOT EXISTS tier_progress (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  
  -- ===========================================================================
  -- TIER COMPLETION PERCENTAGES (0.00-100.00)
  -- ===========================================================================
  tier1_completion DECIMAL(5,2) DEFAULT 0.0, -- "The Basics" (Hard filters)
  tier2_completion DECIMAL(5,2) DEFAULT 0.0, -- "Ready" (Lifestyle + values)
  tier3_completion DECIMAL(5,2) DEFAULT 0.0, -- "Deep Profile" (Psychological depth)
  tier4_completion DECIMAL(5,2) DEFAULT 0.0, -- "Calibrated" (Post-match learning)
  
  -- ===========================================================================
  -- FIELD-LEVEL TRACKING (What's been populated)
  -- ===========================================================================
  completed_fields JSONB DEFAULT '{
    "tier1": [],
    "tier2": [],
    "tier3": [],
    "tier4": []
  }'::jsonb,
  /*
  Example structure:
  {
    "tier1": ["full_name", "date_of_birth", "gender_identity", "religion", "children_intent", ...],
    "tier2": ["occupation", "work_style", "love_language", "political_orientation", ...],
    "tier3": ["attachment_style", "big5_openness", "emotional_intelligence", ...],
    "tier4": ["match_reaction_1", "stated_vs_revealed_gap_1", ...]
  }
  */
  
  -- ===========================================================================
  -- OPEN-ENDED RESPONSE TRACKING (Required for MVP)
  -- ===========================================================================
  open_ended_count INT DEFAULT 0,
  open_ended_responses JSONB DEFAULT '[]'::jsonb,
  /*
  Example structure:
  [
    {
      "question": "What excites you in a partner?",
      "response": "Someone who challenges me intellectually...",
      "signals_extracted": 5,
      "asked_at": "2026-02-11T10:30:00Z"
    },
    {
      "question": "Describe your typical weekend",
      "response": "I usually hit the gym, then brunch with friends...",
      "signals_extracted": 3,
      "asked_at": "2026-02-12T09:15:00Z"
    }
  ]
  */
  
  -- ===========================================================================
  -- SESSION TRACKING (Required for MVP activation)
  -- ===========================================================================
  session_count INT DEFAULT 0,
  first_session_at TIMESTAMPTZ,
  last_session_at TIMESTAMPTZ,
  total_messages_sent INT DEFAULT 0,
  total_messages_received INT DEFAULT 0,
  
  -- ===========================================================================
  -- MVP ACTIVATION STATUS
  -- ===========================================================================
  mvp_achieved BOOLEAN DEFAULT FALSE,
  mvp_achieved_at TIMESTAMPTZ,
  mvp_blocked_reasons TEXT[], -- ["Need 30% more Tier 2", "Need 1 more open-ended", ...]
  
  /*
  MVP Activation Rules:
  - 100% Tier 1 completion
  - 70%+ Tier 2 completion
  - 2+ open-ended responses with meaningful signals
  - 45%+ total completeness score
  - 2+ sessions (prevents rushed single-session signups)
  */
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT tier_progress_user_id_unique UNIQUE(user_id),
  CONSTRAINT tier1_completion_range CHECK (tier1_completion BETWEEN 0 AND 100),
  CONSTRAINT tier2_completion_range CHECK (tier2_completion BETWEEN 0 AND 100),
  CONSTRAINT tier3_completion_range CHECK (tier3_completion BETWEEN 0 AND 100),
  CONSTRAINT tier4_completion_range CHECK (tier4_completion BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_tier_progress_user_id ON tier_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_tier_progress_mvp ON tier_progress(mvp_achieved, tier2_completion);
CREATE INDEX IF NOT EXISTS idx_tier_progress_completed_fields_gin ON tier_progress USING gin(completed_fields jsonb_path_ops);

-- Add updated_at trigger
DROP TRIGGER IF EXISTS update_tier_progress_updated_at ON tier_progress;
CREATE TRIGGER update_tier_progress_updated_at
    BEFORE UPDATE ON tier_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================================================
-- HELPER FUNCTION: Calculate weighted completeness across all tiers
-- ===========================================================================
DROP FUNCTION IF EXISTS calculate_total_completeness(BIGINT);
CREATE OR REPLACE FUNCTION calculate_total_completeness(p_user_id BIGINT)
RETURNS DECIMAL(5,2) AS $$
DECLARE
  v_tier1 DECIMAL(5,2);
  v_tier2 DECIMAL(5,2);
  v_tier3 DECIMAL(5,2);
  v_tier4 DECIMAL(5,2);
  v_total DECIMAL(5,2);
BEGIN
  SELECT 
    tier1_completion,
    tier2_completion,
    tier3_completion,
    tier4_completion
  INTO v_tier1, v_tier2, v_tier3, v_tier4
  FROM tier_progress
  WHERE user_id = p_user_id;
  
  -- Weighted: T1=40%, T2=35%, T3=20%, T4=5%
  v_total := (v_tier1 * 0.40) + (v_tier2 * 0.35) + (v_tier3 * 0.20) + (v_tier4 * 0.05);
  
  RETURN ROUND(v_total, 2);
END;
$$ LANGUAGE plpgsql;

-- ===========================================================================
-- HELPER FUNCTION: Check if user meets MVP activation criteria
-- ===========================================================================
DROP FUNCTION IF EXISTS check_mvp_activation(BIGINT);
CREATE OR REPLACE FUNCTION check_mvp_activation(p_user_id BIGINT)
RETURNS TABLE(
  meets_mvp BOOLEAN,
  blocked_reasons TEXT[]
) AS $$
DECLARE
  v_tier1 DECIMAL(5,2);
  v_tier2 DECIMAL(5,2);
  v_open_ended INT;
  v_session_count INT;
  v_total_completeness DECIMAL(5,2);
  v_reasons TEXT[] := '{}';
BEGIN
  SELECT 
    tier1_completion,
    tier2_completion,
    open_ended_count,
    session_count
  INTO v_tier1, v_tier2, v_open_ended, v_session_count
  FROM tier_progress
  WHERE user_id = p_user_id;
  
  v_total_completeness := calculate_total_completeness(p_user_id);
  
  -- Check each MVP requirement
  IF v_tier1 < 100 THEN
    v_reasons := array_append(v_reasons, 'Need to complete Tier 1 (currently ' || v_tier1 || '%)');
  END IF;
  
  IF v_tier2 < 70 THEN
    v_reasons := array_append(v_reasons, 'Need 70% Tier 2 completion (currently ' || v_tier2 || '%)');
  END IF;
  
  IF v_open_ended < 2 THEN
    v_reasons := array_append(v_reasons, 'Need ' || (2 - v_open_ended) || ' more open-ended response(s)');
  END IF;
  
  IF v_total_completeness < 45 THEN
    v_reasons := array_append(v_reasons, 'Need 45% total completeness (currently ' || v_total_completeness || '%)');
  END IF;
  
  IF v_session_count < 2 THEN
    v_reasons := array_append(v_reasons, 'Need ' || (2 - v_session_count) || ' more session(s)');
  END IF;
  
  -- Return results
  RETURN QUERY SELECT (array_length(v_reasons, 1) IS NULL OR array_length(v_reasons, 1) = 0), v_reasons;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE tier_progress IS 'Tracks user progress through 4-tier onboarding and MVP activation status';
COMMENT ON COLUMN tier_progress.mvp_achieved IS 'TRUE when all MVP criteria met: 100% T1 + 70% T2 + 2 open-ended + 45% total + 2 sessions';
COMMENT ON COLUMN tier_progress.mvp_blocked_reasons IS 'Human-readable list of what is blocking MVP activation';
COMMENT ON FUNCTION calculate_total_completeness IS 'Returns weighted completeness: T1=40%, T2=35%, T3=20%, T4=5%';
COMMENT ON FUNCTION check_mvp_activation IS 'Checks all MVP criteria and returns blockers if any';
