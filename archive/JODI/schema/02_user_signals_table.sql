-- ============================================================================
-- JODI Schema Upgrade: User Signals Table
-- Stores all inferred + soft explicit signals in JSONB (Tier 2-4 data)
-- Type: New table for compatibility scoring (not elimination filtering)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_signals (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  
  -- ===========================================================================
  -- TIER 2: LIFESTYLE & DAILY LIFE (Mix of Explicit + Inferred)
  -- ===========================================================================
  lifestyle JSONB DEFAULT '{}'::jsonb,
  /*
  Schema per field:
  {
    "field_name": {
      "value": <any>,              -- The actual value
      "confidence": <0.0-1.0>,     -- Confidence score (1.0 = explicit)
      "source": "explicit|inferred", -- How captured
      "updated_at": <timestamp>    -- Last update
    }
  }
  
  Example fields:
  - work_style: "Corporate" | "Startup" | "Freelance" | "Government"
  - work_life_balance: "Workaholic" | "9-5" | "Flexible" | "Balanced"
  - income_bracket: "$50k-100k" | "$100k-150k" | "$150k-250k" | "$250k+"
  - financial_style: "Saver" | "Spender" | "Investor" | "Balanced"
  - living_situation: "Alone" | "Roommates" | "Family" | "Owns"
  - exercise_fitness: "Gym regular" | "Sports" | "Active lifestyle" | "Sedentary"
  - diet_food_culture: "Foodie" | "Cook at home" | "Health-focused" | "Casual"
  - travel_frequency: "Frequent traveler" | "Occasional" | "Homebody"
  - social_energy: "Introvert" | "Extrovert" | "Ambivert"
  - weekend_pattern: <free text describing typical weekend>
  - pet_ownership: "Has dogs" | "Has cats" | "Wants pets" | "No pets" | "Allergic"
  - substance_use: "Cannabis occasional" | "None" | "Social"
  */
  
  -- ===========================================================================
  -- TIER 2: VALUES & WORLDVIEW (Primarily Inferred)
  -- ===========================================================================
  values JSONB DEFAULT '{}'::jsonb,
  /*
  Example fields:
  - political_orientation: "Progressive" | "Moderate" | "Conservative" | "Apolitical"
  - family_values: "Traditional" | "Modern" | "Blended"
  - gender_role_views: "Egalitarian" | "Traditional" | "Complementarian"
  - cultural_identity_strength: "Strong" | "Moderate" | "Assimilated" | "Fluid"
  - ambition_level: "Driven" | "Balanced" | "Laid-back"
  - philanthropy_giving: "Active volunteer" | "Monthly donations" | "Occasional" | "Not priority"
  - environmental_views: "Climate-conscious" | "Sustainable living" | "Not priority"
  - education_importance: "Critical" | "Important" | "Moderate" | "Not priority"
  - key_issue_stances: {abortion: "Pro-choice", guns: "Reform", immigration: "Open", ...}
  */
  
  -- ===========================================================================
  -- TIER 2: RELATIONSHIP EXPECTATIONS (Explicit + Inferred)
  -- ===========================================================================
  relationship_style JSONB DEFAULT '{}'::jsonb,
  /*
  Example fields:
  - love_language: "Acts of Service" | "Words of Affirmation" | "Physical Touch" | "Gifts" | "Quality Time"
  - conflict_style: "Avoider" | "Confronter" | "Communicator" | "Withdrawer"
  - independence_needs: "High" | "Moderate" | "Low" | "Codependent"
  - past_relationship_count: <number>
  - reason_last_ended: <free text>
  - green_flags_sought: [<array of desired traits>]
  - red_flags_cited: [<array of dealbreakers>]
  - physical_type_preference: <free text, optional>
  - intellectual_match_preference: "Equal" | "Complementary" | "Stimulating" | "Not priority"
  - shared_activities_preference: "Do everything together" | "Balanced" | "Independent lives"
  */
  
  -- ===========================================================================
  -- TIER 3: PSYCHOLOGICAL PROFILE (Primarily Inferred)
  -- ===========================================================================
  personality JSONB DEFAULT '{}'::jsonb,
  /*
  Example fields:
  - attachment_style: "Secure" | "Anxious" | "Avoidant" | "Disorganized"
  - big5_openness: <0.0-1.0 score>
  - big5_conscientiousness: <0.0-1.0 score>
  - big5_extraversion: <0.0-1.0 score>
  - big5_agreeableness: <0.0-1.0 score>
  - big5_neuroticism: <0.0-1.0 score>
  - emotional_intelligence: "High" | "Moderate" | "Low"
  - communication_style: "Direct" | "Indirect" | "Verbose" | "Concise"
  - humor_style: "Dry" | "Sarcastic" | "Warm" | "Slapstick" | "Dark"
  - decision_making_style: "Analytical" | "Intuitive" | "Impulsive" | "Deliberate"
  - stress_response: "Problem-solver" | "Emotional processor" | "Avoider" | "Seeker of support"
  - optimism_spectrum: "Optimist" | "Realist" | "Pessimist"
  - novelty_seeking: "High" | "Moderate" | "Low" | "Routine-loving"
  - self_awareness_level: "High" | "Moderate" | "Low"
  */
  
  -- ===========================================================================
  -- TIER 3: FAMILY & BACKGROUND DEPTH (Mix of Explicit + Inferred)
  -- ===========================================================================
  family_background JSONB DEFAULT '{}'::jsonb,
  /*
  Example fields:
  - family_structure: "Close-knit" | "Distant" | "Complicated" | "Chosen family"
  - family_of_origin_dynamics: "Warm" | "Distant" | "Complicated" | "Abusive"
  - parenting_philosophy: "Strict" | "Free-range" | "Balanced" | "Attachment-based"
  - extended_family_expectations: "High involvement" | "Moderate" | "Low" | "No contact"
  - financial_background: "Wealthy" | "Upper middle" | "Middle" | "Modest" | "Struggled"
  - immigration_story: "First gen" | "Second gen" | "Diaspora" | "Multicultural" | "Not applicable"
  - relationship_with_parents: "Close" | "Strained" | "Distant" | "No contact"
  - community_ties: "Active in religious community" | "Cultural community" | "None"
  */
  
  -- ===========================================================================
  -- TIER 3: RICH MEDIA SIGNALS (Inferred from Behavior)
  -- ===========================================================================
  media_signals JSONB DEFAULT '{}'::jsonb,
  /*
  Example fields:
  - voice_tone_energy: "Warm" | "Reserved" | "High-energy" | "Calm" (from voice notes)
  - vocabulary_sophistication: "Casual" | "Articulate" | "Academic"
  - emoji_expression_style: "Expressive" | "Minimal" | "None"
  - response_latency_pattern: "Quick responder" | "Thoughtful pauser" | "Delayed"
  - message_length_pattern: "Brief texter" | "Essay writer" | "Balanced"
  - topic_initiation_patterns: [<topics user brings up unprompted>]
  - emotional_disclosure_depth: "Surface-level" | "Moderate" | "Vulnerable"
  - consistency_over_time: "Stable" | "Evolving" | "Contradictory"
  */
  
  -- ===========================================================================
  -- TIER 4: MATCH CALIBRATION (Post-Match Learning)
  -- ===========================================================================
  match_learnings JSONB DEFAULT '{}'::jsonb,
  /*
  Example fields:
  - stated_vs_revealed_gaps: [
      {
        "stated": "Wants outdoorsy partner",
        "revealed": "Reacts positively to homebodies",
        "confidence": 0.85,
        "match_id": <uuid>
      }
    ]
  - surprise_preferences: [<array of unexpected attractions>]
  - evolved_dealbreakers: [<things that matter more/less than stated>]
  - coaching_receptiveness: "High" | "Moderate" | "Resistant"
  - preference_drift_patterns: {<field>: {from: <old>, to: <new>, date: <timestamp>}}
  */
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT user_signals_user_id_unique UNIQUE(user_id)
);

-- Create indexes for JSONB queries (GIN indexes for flexible querying)
CREATE INDEX IF NOT EXISTS idx_user_signals_lifestyle_gin ON user_signals USING gin(lifestyle jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_user_signals_values_gin ON user_signals USING gin(values jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_user_signals_personality_gin ON user_signals USING gin(personality jsonb_path_ops);

-- Add updated_at trigger
DROP TRIGGER IF EXISTS update_user_signals_updated_at ON user_signals;
CREATE TRIGGER update_user_signals_updated_at
    BEFORE UPDATE ON user_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE user_signals IS 'All inferred and soft preference signals for compatibility scoring (not hard filters)';
COMMENT ON COLUMN user_signals.lifestyle IS 'Tier 2: Lifestyle patterns, work, exercise, travel, social energy';
COMMENT ON COLUMN user_signals.values IS 'Tier 2: Political, family values, cultural identity, ambition';
COMMENT ON COLUMN user_signals.relationship_style IS 'Tier 2: Love language, conflict style, green/red flags';
COMMENT ON COLUMN user_signals.personality IS 'Tier 3: Big 5, attachment style, humor, decision-making, emotional intelligence';
COMMENT ON COLUMN user_signals.family_background IS 'Tier 3: Family dynamics, parenting philosophy, financial background';
COMMENT ON COLUMN user_signals.media_signals IS 'Tier 3: Voice tone, vocabulary, message patterns, consistency';
COMMENT ON COLUMN user_signals.match_learnings IS 'Tier 4: Post-match calibration, stated vs revealed preferences';
