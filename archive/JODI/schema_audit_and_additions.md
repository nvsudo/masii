# JODI Schema Audit & Missing Fields

## Executive Summary
**Current state:** ~85 of 100+ data points covered in schema  
**Missing:** ~15-20 fields across Tiers 1-3  
**Action:** Add missing columns + enhance JSONB schema + validation

---

## TIER 1 AUDIT: THE BASICS (25 total fields)

### 1A. Identity & Demographics (9 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Full name / alias | `users.full_name` | ✅ EXISTS | None |
| Date of birth | `users.date_of_birth` | ✅ EXISTS | Add validation (18-80) |
| Age | `users.age` | ✅ EXISTS | Auto-calc from DOB |
| Gender identity | `users.gender_identity` | ✅ EXISTS | None |
| Sexual orientation | `users.sexual_orientation` | ✅ EXISTS | None |
| City / Location | `users.city` | ✅ EXISTS | None |
| Nationality | `users.nationality` | ✅ EXISTS | None |
| Ethnicity / Race | `users.ethnicity` | ✅ EXISTS | None |
| Native languages | `users.native_languages` | ✅ EXISTS | None |
| Photo(s) | Object storage | ⚠️ SKIPPED | Per N approval |

### 1B. Hard Deal-Breakers (10 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Religion / Faith | `users.religion` | ✅ EXISTS | None |
| Partner religion req. | `user_preferences.religion_preference` | ✅ EXISTS | None |
| Children intent | `users.children_intent` | ✅ EXISTS | None |
| Partner children req. | `user_preferences.children_preference` | ✅ EXISTS | None |
| Marital history | `users.marital_history` | ✅ EXISTS | None |
| Smoking | `users.smoking` | ✅ EXISTS | Use Telegram buttons |
| Drinking | `users.drinking` | ✅ EXISTS | Use Telegram buttons |
| Dietary restrictions | `users.dietary_restrictions` | ✅ EXISTS | None |
| Relationship intent | `users.relationship_intent` | ✅ EXISTS | None |
| Timeline | `users.relationship_timeline` | ✅ EXISTS | None |

### 1C. Basic Preferences (6 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Age range preference | `user_preferences.age_min/max` | ✅ EXISTS | None |
| Location preference | `user_preferences.location_preference` | ✅ EXISTS | None |
| Open to distance? | `user_preferences.open_to_relocation` | ✅ EXISTS | None |
| Height | `users.height_cm` | ✅ EXISTS | None |
| Height preference | `user_preferences.soft_preferences.height_range` | ✅ EXISTS | None |
| Education minimum | `user_preferences.education_minimum` | ✅ EXISTS | None |
| Caste / Community | `users.caste_community` | ✅ EXISTS | None |
| Family involvement | `user_preferences.soft_preferences.family_involvement` | ✅ EXISTS | None |

**TIER 1 STATUS: ✅ 100% COVERED** (minus photo validation, per N)

---

## TIER 2 AUDIT: READY (33 fields)

### 2A. Lifestyle & Daily Life (13 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Occupation / Industry | `users.occupation`, `users.industry` | ✅ EXISTS | None |
| Work style | `user_signals.lifestyle.work_style` | ✅ EXISTS | None |
| Work-life balance | `user_signals.lifestyle.work_life_balance` | ✅ EXISTS | None |
| Income bracket | `user_signals.lifestyle.income_bracket` | ✅ EXISTS | None |
| Financial style | `user_signals.lifestyle.financial_style` | ✅ EXISTS | None |
| Living situation | `user_signals.lifestyle.living_situation` | ✅ EXISTS | None |
| Exercise / Fitness | `user_signals.lifestyle.exercise_fitness` | ✅ EXISTS | None |
| Diet / Food culture | `user_signals.lifestyle.diet_food_culture` | ✅ EXISTS | None |
| Travel frequency | `user_signals.lifestyle.travel_frequency` | ✅ EXISTS | None |
| Social energy | `user_signals.lifestyle.social_energy` | ✅ EXISTS | None |
| Weekend pattern | `user_signals.lifestyle.weekend_pattern` | ✅ EXISTS | None |
| Pet ownership | `user_signals.lifestyle.pet_ownership` | ✅ EXISTS | None |
| Substance use | `user_signals.lifestyle.substance_use` | ✅ EXISTS | None |

### 2B. Values & Worldview (10 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Political orientation | `user_signals.values.political_orientation` | ✅ EXISTS | None |
| Religious practice level | `user_signals.values.religious_practice_level` | ⚠️ MISSING | **ADD to JSONB** |
| Family values | `user_signals.values.family_values` | ✅ EXISTS | None |
| Gender role views | `user_signals.values.gender_role_views` | ✅ EXISTS | None |
| Cultural identity strength | `user_signals.values.cultural_identity_strength` | ✅ EXISTS | None |
| Ambition level | `user_signals.values.ambition_level` | ✅ EXISTS | None |
| Philanthropy / Giving | `user_signals.values.philanthropy_giving` | ✅ EXISTS | None |
| Environmental views | `user_signals.values.environmental_views` | ✅ EXISTS | None |
| Education importance | `user_signals.values.education_importance` | ✅ EXISTS | None |
| Stance on key issues | `user_signals.values.key_issue_stances` | ✅ EXISTS | None |

### 2C. Relationship Expectations (10 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Love language | `user_signals.relationship_style.love_language` | ✅ EXISTS | None |
| Conflict style | `user_signals.relationship_style.conflict_style` | ✅ EXISTS | None |
| Independence needs | `user_signals.relationship_style.independence_needs` | ✅ EXISTS | None |
| Past relationship count | `user_signals.relationship_style.past_relationship_count` | ✅ EXISTS | None |
| Reason last ended | `user_signals.relationship_style.reason_last_ended` | ✅ EXISTS | None |
| Green flags sought | `user_signals.relationship_style.green_flags_sought` | ✅ EXISTS | None |
| Red flags cited | `user_signals.relationship_style.red_flags_cited` | ✅ EXISTS | None |
| Physical type preference | `user_signals.relationship_style.physical_type_preference` | ✅ EXISTS | None |
| Intellectual match pref. | `user_signals.relationship_style.intellectual_match_preference` | ✅ EXISTS | None |
| Shared activities pref. | `user_signals.relationship_style.shared_activities_preference` | ✅ EXISTS | None |

**TIER 2 STATUS: 32/33 fields (97%)**  
**MISSING:** `religious_practice_level` (moved from Tier 1 column to inferred signal)

---

## TIER 3 AUDIT: DEEP PROFILE (26 fields)

### 3A. Psychological Profile (10 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Attachment style | `user_signals.personality.attachment_style` | ✅ EXISTS | None |
| Big 5: Openness | `user_signals.personality.big5_openness` | ✅ EXISTS | None |
| Big 5: Conscientiousness | `user_signals.personality.big5_conscientiousness` | ✅ EXISTS | None |
| Big 5: Extraversion | `user_signals.personality.big5_extraversion` | ✅ EXISTS | None |
| Big 5: Agreeableness | `user_signals.personality.big5_agreeableness` | ✅ EXISTS | None |
| Big 5: Neuroticism | `user_signals.personality.big5_neuroticism` | ✅ EXISTS | None |
| Emotional intelligence | `user_signals.personality.emotional_intelligence` | ✅ EXISTS | None |
| Communication style | `user_signals.personality.communication_style` | ✅ EXISTS | None |
| Humor style | `user_signals.personality.humor_style` | ✅ EXISTS | None |
| Decision-making style | `user_signals.personality.decision_making_style` | ✅ EXISTS | None |
| Stress response | `user_signals.personality.stress_response` | ✅ EXISTS | None |
| Optimism spectrum | `user_signals.personality.optimism_spectrum` | ✅ EXISTS | None |
| Need for novelty | `user_signals.personality.novelty_seeking` | ✅ EXISTS | None |
| Self-awareness level | `user_signals.personality.self_awareness_level` | ✅ EXISTS | None |

### 3B. Family & Background Depth (8 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Family structure | `user_signals.family_background.family_structure` | ✅ EXISTS | None |
| Family of origin dynamics | `user_signals.family_background.family_of_origin_dynamics` | ✅ EXISTS | None |
| Parenting philosophy | `user_signals.family_background.parenting_philosophy` | ✅ EXISTS | None |
| Extended family expectations | `user_signals.family_background.extended_family_expectations` | ✅ EXISTS | None |
| Financial background | `user_signals.family_background.financial_background` | ✅ EXISTS | None |
| Immigration story | `user_signals.family_background.immigration_story` | ✅ EXISTS | None |
| Relationship with parents | `user_signals.family_background.relationship_with_parents` | ✅ EXISTS | None |
| Community ties | `user_signals.family_background.community_ties` | ✅ EXISTS | None |

### 3C. Rich Media Signals (8 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Voice tone / Energy | `user_signals.media_signals.voice_tone_energy` | ✅ EXISTS | None |
| Vocabulary sophistication | `user_signals.media_signals.vocabulary_sophistication` | ✅ EXISTS | None |
| Emoji / Expression style | `user_signals.media_signals.emoji_expression_style` | ✅ EXISTS | None |
| Response latency patterns | `user_signals.media_signals.response_latency_pattern` | ✅ EXISTS | None |
| Message length patterns | `user_signals.media_signals.message_length_pattern` | ✅ EXISTS | None |
| Topic initiation patterns | `user_signals.media_signals.topic_initiation_patterns` | ✅ EXISTS | None |
| Emotional disclosure depth | `user_signals.media_signals.emotional_disclosure_depth` | ✅ EXISTS | None |
| Consistency over time | `user_signals.media_signals.consistency_over_time` | ✅ EXISTS | None |

**TIER 3 STATUS: ✅ 100% COVERED**

---

## TIER 4 AUDIT: CALIBRATED (16 fields)

### 4A. Match Reaction Data (8 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| First impression reaction | `matches.user_first_impression` | ⚠️ MISSING | **ADD to matches table** |
| Photo reaction | `matches.user_photo_reaction` | ⚠️ MISSING | **ADD to matches table** |
| Profile reaction | `matches.user_profile_notes` | ⚠️ MISSING | **ADD to matches table** |
| Date willingness | `matches.date_willingness` | ⚠️ MISSING | **ADD to matches table** |
| Post-date feedback | `matches.date_feedback` | ⚠️ MISSING | **ADD to matches table** |
| Surprise learnings | `matches.surprise_learnings` | ⚠️ MISSING | **ADD to matches table** |
| Revealed preferences | `matches.revealed_preferences` | ⚠️ MISSING | **ADD to matches table** |

### 4B. Behavioral Calibration (8 fields)
| Field | Current Schema | Status | Action |
|-------|---------------|--------|--------|
| Stated vs revealed gaps | `user_signals.match_learnings.stated_vs_revealed_gaps` | ✅ EXISTS | None |
| Surprise preferences | `user_signals.match_learnings.surprise_preferences` | ⚠️ MISSING | **ADD to JSONB** |
| Updated deal-breakers | `user_signals.match_learnings.evolved_dealbreakers` | ✅ EXISTS | None |
| Coaching receptiveness | `user_signals.match_learnings.coaching_receptiveness` | ✅ EXISTS | None |
| Preference drift | `user_signals.match_learnings.preference_drift_patterns` | ✅ EXISTS | None |
| Response speed to matches | `user_signals.media_signals.response_speed_to_matches` | ⚠️ MISSING | **ADD to JSONB** |
| Question patterns | `user_signals.personality.question_patterns_about_matches` | ⚠️ MISSING | **ADD to JSONB** |
| Rejection reasons evolution | `user_signals.personality.rejection_reasons_evolution` | ⚠️ MISSING | **ADD to JSONB** |
| Engagement depth variance | `user_signals.media_signals.engagement_depth_variance` | ⚠️ MISSING | **ADD to JSONB** |
| Return rate after rejection | `user_signals.media_signals.return_rate_after_rejection` | ⚠️ MISSING | **ADD to JSONB** |
| Self-narrative evolution | `user_signals.personality.self_narrative_evolution` | ⚠️ MISSING | **ADD to JSONB** |

**TIER 4 STATUS: 60% covered**  
**MISSING:** 7 match table columns + 7 JSONB fields

---

## SUMMARY: MISSING FIELDS TO ADD

### 1. `matches` table additions (7 new JSONB columns):
```sql
ALTER TABLE matches ADD COLUMN user_first_impression JSONB;
ALTER TABLE matches ADD COLUMN user_photo_reaction JSONB;
ALTER TABLE matches ADD COLUMN user_profile_notes TEXT;
ALTER TABLE matches ADD COLUMN date_willingness VARCHAR(50);
ALTER TABLE matches ADD COLUMN date_feedback JSONB;
ALTER TABLE matches ADD COLUMN surprise_learnings TEXT[];
ALTER TABLE matches ADD COLUMN revealed_preferences JSONB;
```

### 2. `user_signals.values` JSONB addition:
- `religious_practice_level` (with confidence + source tracking)

### 3. `user_signals.match_learnings` JSONB additions:
- `surprise_preferences`

### 4. `user_signals.media_signals` JSONB additions:
- `response_speed_to_matches`
- `engagement_depth_variance`
- `return_rate_after_rejection`

### 5. `user_signals.personality` JSONB additions:
- `question_patterns_about_matches`
- `rejection_reasons_evolution`
- `self_narrative_evolution`

### 6. Age validation (already exists, just enforce):
- Update trigger to validate age 18-80 on DOB change
- Add CHECK constraint on `users.age`

---

## NEXT STEPS

1. ✅ Run SQL migration to add missing fields
2. ✅ Update extraction pipeline to route new fields
3. ✅ Implement Telegram button flows for categorical fields
4. ✅ Add age validation in DOB parsing logic
5. ✅ Update DATA_FIELD_MAPPING.md with new fields
6. ✅ Test CRUD operations via conversation agent

**Timeline:** Ship ASAP (N approved)
