# JODI Data Field Mapping
**For Conversation Orchestrator: Real-Time Extraction → Schema Routing**

This document maps every data point from the Matchmaking Data Capture Framework to its storage location in the Supabase schema. The conversation orchestrator uses this to route extracted values during live conversation.

---

## **TIER 1: THE BASICS** (5-7 min, required before profile creation)

### 1A. Identity & Demographics (Explicit → `users` table columns)

| Field | Storage | Extraction Method | Example Values |
|-------|---------|-------------------|----------------|
| Full name / alias | `users.full_name` | Direct ask | "Sarah Khan" |
| Date of birth | `users.date_of_birth` | Direct ask | 1995-03-15 |
| Age | `users.age` | Auto-calculated | 29 |
| Gender identity | `users.gender_identity` | Direct ask | Male / Female / Non-binary |
| Sexual orientation | `users.sexual_orientation` | Direct ask | Heterosexual / Gay / Bi / Other |
| City / Location | `users.city`, `users.country` | Direct ask | "Dubai", "UAE" |
| Nationality | `users.nationality` | Direct ask | "Indian", "American" |
| Ethnicity | `users.ethnicity` | Direct ask (optional) | "South Asian", "Hispanic" |
| Native languages | `users.native_languages` | Direct ask | ["English", "Hindi", "Urdu"] |
| Photo(s) | Object storage → URL | Upload prompt | https://... |

**Extraction Prompt:**  
_"Let me get to know you! What's your name? When were you born? Where are you based?"_

---

### 1B. Hard Deal-Breakers (Explicit → `users` table columns, indexed)

| Field | Storage | Extraction Method | Example Values |
|-------|---------|-------------------|----------------|
| Religion / Faith | `users.religion` | Direct ask | "Muslim", "Hindu", "Christian", "Jewish", "Atheist" |
| Partner religion req. | `user_preferences.religion_preference` | Direct ask | ["Same religion", "Open to all"] |
| Children intent | `users.children_intent` | Direct ask | "Want kids", "Don't want", "Already have" |
| Partner children req. | `user_preferences.children_preference` | Direct ask | "OK with existing kids", "No existing kids" |
| Marital history | `users.marital_history` | Direct ask | "Never married", "Divorced", "Widowed" |
| Smoking | `users.smoking` | Direct ask | "Current smoker", "Never", "Socially" |
| Drinking | `users.drinking` | Direct ask | "Regularly", "Socially", "Never" |
| Dietary restrictions | `users.dietary_restrictions` | Direct ask | "Halal", "Kosher", "Vegan", "None" |
| Relationship intent | `users.relationship_intent` | Direct ask | "Marriage", "Long-term committed" |
| Timeline | `users.relationship_timeline` | Direct ask | "Ready now", "1-2 years", "Exploring" |

**Extraction Prompt:**  
_"A few important things: Do you practice a religion? Do you want kids? Have you been married before? How do you feel about smoking/drinking?"_

---

### 1C. Basic Preferences (Mix → `users` columns + `user_preferences` JSONB)

| Field | Storage | Extraction Method | Example Values |
|-------|---------|-------------------|----------------|
| Age range preference | `user_preferences.age_min/max` | Direct ask | 25-35 |
| Location preference | `user_preferences.location_preference` | Direct ask | ["Dubai", "Mumbai", "NYC"] |
| Open to distance? | `user_preferences.open_to_relocation` | Direct ask | TRUE / FALSE |
| Height | `users.height_cm` | Direct ask (optional) | 175 cm |
| Height preference | `user_preferences.soft_preferences.height_range` | Direct ask | {min: 165, max: 185, weight: 0.5} |
| Education minimum | `user_preferences.education_minimum` | Direct ask | "Bachelor's", "Master's", "No preference" |
| Caste / Community | `users.caste_community` | Direct ask (if relevant) | "Brahmin", "Ashkenazi", "None" |
| Family involvement | `user_preferences.soft_preferences.family_involvement` | Direct ask | {value: "Moderate", weight: 0.6} |

**Extraction Prompt:**  
_"What age range works for you? Are you open to long-distance? Does education level matter to you?"_

---

## **TIER 2: READY** (3-7 days, 70%+ completion activates matching)

### 2A. Lifestyle & Daily Life (Mix → `user_signals.lifestyle` JSONB)

| Field | Storage | Extraction Method | Example Values | Confidence |
|-------|---------|-------------------|----------------|------------|
| Occupation / Industry | `users.occupation`, `users.industry` | Direct ask + infer | "Software Engineer", "Tech" | 1.0 / 0.85 |
| Work style | `lifestyle.work_style` | Infer from descriptions | "Startup", "Corporate", "Freelance" | 0.80 |
| Work-life balance | `lifestyle.work_life_balance` | Infer from schedule | "Flexible", "9-5", "Workaholic" | 0.70 |
| Income bracket | `lifestyle.income_bracket` | Direct ask (gated) | "$100k-150k", "$150k-250k" | 1.0 |
| Financial style | `lifestyle.financial_style` | Infer from money talk | "Saver", "Investor", "Spender" | 0.65 |
| Living situation | `lifestyle.living_situation` | Direct ask | "Alone", "Roommates", "Family" | 1.0 |
| Exercise / Fitness | `lifestyle.exercise_fitness` | Infer from routine | "Gym 4x/week", "Active", "Sedentary" | 0.85 |
| Diet / Food culture | `lifestyle.diet_food_culture` | Infer from food talk | "Foodie", "Health-focused", "Cook at home" | 0.75 |
| Travel frequency | `lifestyle.travel_frequency` | Infer from stories | "Frequent traveler", "Occasional", "Homebody" | 0.80 |
| Social energy | `lifestyle.social_energy` | Infer from descriptions | "Introvert", "Extrovert", "Ambivert" | 0.70 |
| Weekend pattern | `lifestyle.weekend_pattern` | Open-ended question | "Gym → brunch → hiking" | 1.0 |
| Pet ownership | `lifestyle.pet_ownership` | Direct ask | "Has dogs", "Wants pets", "Allergic" | 1.0 |
| Substance use | `lifestyle.substance_use` | Direct ask (gated) | "Cannabis occasional", "None" | 1.0 |

**Extraction Prompts:**  
_"What do you do for work? How's your work-life balance?  
Tell me about your typical weekend.  
Are you a gym person? How often do you travel?  
Do you have pets or want them?"_

**JSONB Schema per field:**
```json
{
  "work_style": {
    "value": "Startup",
    "confidence": 0.85,
    "source": "inferred",
    "updated_at": "2026-02-11T10:30:00Z"
  }
}
```

---

### 2B. Values & Worldview (Inferred → `user_signals.values` JSONB)

| Field | Storage | Extraction Method | Example Values | Confidence |
|-------|---------|-------------------|----------------|------------|
| Political orientation | `values.political_orientation` | Infer from views | "Progressive", "Moderate", "Conservative" | 0.75 |
| Religious practice level | `values.religious_practice_level` | Infer from T1 + talk | "Devout", "Cultural", "Secular" | 0.80 |
| Family values | `values.family_values` | Infer from family talk | "Traditional", "Modern", "Blended" | 0.70 |
| Gender role views | `values.gender_role_views` | Infer from context | "Egalitarian", "Traditional" | 0.75 |
| Cultural identity strength | `values.cultural_identity_strength` | Infer from heritage talk | "Strong", "Moderate", "Assimilated" | 0.80 |
| Ambition level | `values.ambition_level` | Infer from career goals | "Driven", "Balanced", "Laid-back" | 0.85 |
| Philanthropy / Giving | `values.philanthropy_giving` | Infer from activities | "Active volunteer", "Occasional donor" | 0.70 |
| Environmental views | `values.environmental_views` | Infer from lifestyle | "Climate-conscious", "Not priority" | 0.65 |
| Education importance | `values.education_importance` | Infer + direct | "Critical", "Important", "Not priority" | 0.80 |
| Stance on key issues | `values.key_issue_stances` | Infer from free text | {abortion: "Pro-choice", ...} | 0.70 |

**Extraction Prompts:**  
_Let natural conversation reveal values. Don't directly ask "What's your political orientation?"  
Instead: "What causes do you care about?" "How was your relationship with your family growing up?"  
System extracts values from their stories._

---

### 2C. Relationship Expectations (Mix → `user_signals.relationship_style` JSONB)

| Field | Storage | Extraction Method | Example Values | Confidence |
|-------|---------|-------------------|----------------|------------|
| Love language | `relationship_style.love_language` | Open question + infer | "Quality Time", "Physical Touch" | 0.85 |
| Conflict style | `relationship_style.conflict_style` | Infer from stories | "Communicator", "Avoider", "Confronter" | 0.75 |
| Independence needs | `relationship_style.independence_needs` | Infer from lifestyle | "High", "Moderate", "Low" | 0.70 |
| Past relationship count | `relationship_style.past_relationship_count` | Direct ask (gated) | 3 | 1.0 |
| Reason last ended | `relationship_style.reason_last_ended` | Open-ended question | "Different life goals" | 1.0 |
| Green flags sought | `relationship_style.green_flags_sought` | Open-ended question | ["Emotional intelligence", "Ambition"] | 1.0 |
| Red flags cited | `relationship_style.red_flags_cited` | Open-ended question | ["Dishonesty", "Lack of ambition"] | 1.0 |
| Physical type preference | `relationship_style.physical_type_preference` | Direct ask (gated, optional) | "Fit, tall, dark hair" | 1.0 |
| Intellectual match pref. | `relationship_style.intellectual_match_preference` | Infer from convo depth | "Equal", "Stimulating" | 0.80 |
| Shared activities pref. | `relationship_style.shared_activities_preference` | Infer from lifestyle | "Balanced", "Independent lives" | 0.75 |

**Extraction Prompts:**  
_"How do you feel loved? What matters most in a relationship?  
What happened with your last relationship? What did you learn?  
What excites you when you meet someone new? Any dealbreakers?"_

---

## **TIER 3: DEEP PROFILE** (Weeks 2-4, ongoing)

### 3A. Psychological Profile (Inferred → `user_signals.personality` JSONB)

| Field | Storage | Extraction Method | Confidence |
|-------|---------|-------------------|------------|
| Attachment style | `personality.attachment_style` | Infer from relationship stories | 0.70 |
| Big 5: Openness | `personality.big5_openness` | Infer from conversation patterns | 0.75 |
| Big 5: Conscientiousness | `personality.big5_conscientiousness` | Infer from organization/planning | 0.75 |
| Big 5: Extraversion | `personality.big5_extraversion` | Infer from social energy | 0.80 |
| Big 5: Agreeableness | `personality.big5_agreeableness` | Infer from how they talk about others | 0.70 |
| Big 5: Neuroticism | `personality.big5_neuroticism` | Infer from stress/emotion talk | 0.65 |
| Emotional intelligence | `personality.emotional_intelligence` | Infer from empathy/self-awareness | 0.70 |
| Communication style | `personality.communication_style` | Infer from message patterns | 0.85 |
| Humor style | `personality.humor_style` | Infer from jokes/reactions | 0.80 |
| Decision-making style | `personality.decision_making_style` | Infer from how they describe choices | 0.75 |
| Stress response | `personality.stress_response` | Infer from pressure stories | 0.70 |
| Optimism spectrum | `personality.optimism_spectrum` | Infer from tone analysis | 0.75 |
| Need for novelty | `personality.novelty_seeking` | Infer from lifestyle + travel | 0.80 |
| Self-awareness level | `personality.self_awareness_level` | Infer from contradictions | 0.65 |

**Extraction Method:**  
Deep psychological signals emerge over time from sustained conversation. LLM analyzes:
- How they describe past relationships → attachment style
- How they talk about stress → coping mechanisms
- Message length, tone, emoji use → communication style
- Stories about decision-making → analytical vs intuitive

---

### 3B. Family & Background Depth (Mix → `user_signals.family_background` JSONB)

| Field | Storage | Extraction Method | Confidence |
|-------|---------|-------------------|------------|
| Family structure | `family_background.family_structure` | Conversational exploration | 0.80 |
| Family of origin dynamics | `family_background.family_of_origin_dynamics` | Infer from family talk | 0.75 |
| Parenting philosophy | `family_background.parenting_philosophy` | Open-ended question | 0.70 |
| Extended family expectations | `family_background.extended_family_expectations` | Culturally gated question | 0.75 |
| Financial background | `family_background.financial_background` | Infer from stories | 0.70 |
| Immigration story | `family_background.immigration_story` | Infer from background convo | 1.0 |
| Relationship with parents | `family_background.relationship_with_parents` | Infer from family conversations | 0.80 |
| Community ties | `family_background.community_ties` | Infer from social descriptions | 0.85 |

**Extraction Prompts:**  
_"Tell me about your family. Are you close with them?  
How was growing up for you?  
If you want kids someday, what kind of parent do you think you'd be?"_

---

### 3C. Rich Media Signals (Inferred → `user_signals.media_signals` JSONB)

| Field | Storage | Extraction Method | Confidence |
|-------|---------|-------------------|------------|
| Voice tone / Energy | `media_signals.voice_tone_energy` | Voice note analysis (Telegram) | 0.80 |
| Vocabulary sophistication | `media_signals.vocabulary_sophistication` | NLP analysis of messages | 0.85 |
| Emoji / Expression style | `media_signals.emoji_expression_style` | Pattern analysis | 0.90 |
| Response latency patterns | `media_signals.response_latency_pattern` | Behavioral tracking | 0.95 |
| Message length patterns | `media_signals.message_length_pattern` | Behavioral tracking | 0.90 |
| Topic initiation patterns | `media_signals.topic_initiation_patterns` | Conversation analysis | 0.85 |
| Emotional disclosure depth | `media_signals.emotional_disclosure_depth` | Conversation analysis | 0.70 |
| Consistency over time | `media_signals.consistency_over_time` | Longitudinal comparison | 0.75 |

**Extraction Method:**  
Behavioral patterns tracked automatically:
- Average response time
- Message length distribution
- Emoji frequency
- Voice note usage
- Topics they bring up unprompted

---

## **TIER 4: CALIBRATED** (Post-match learning, ongoing)

### 4A. Match Reaction Data (Post-Match → `matches` table)

| Field | Storage | Extraction Method |
|-------|---------|-------------------|
| First impression reaction | `matches.user_first_impression` | Direct ask after reveal |
| Photo reaction | `matches.user_photo_reaction` | Direct ask |
| Profile reaction | `matches.user_profile_notes` | Open-ended feedback |
| Date willingness | `matches.date_willingness` | Direct ask |
| Post-date feedback | `matches.date_feedback` | Structured feedback |
| Surprise learnings | `matches.surprise_learnings` | Open-ended question |
| Revealed preferences | `matches.revealed_preferences` | System-computed |

**Extraction Prompts:**  
_After match reveal:  
"What's your first impression? What stood out to you (positive or negative)?  
Would you like to meet them?"_

_After date:  
"How'd it go? Chemistry? Conversation? Attraction? What worked? What didn't?"_

---

### 4B. Behavioral Calibration (System-Inferred → `user_signals.match_learnings` JSONB)

| Field | Storage | Extraction Method |
|-------|---------|-------------------|
| Stated vs revealed gaps | `match_learnings.stated_vs_revealed_gaps` | Computed from matches |
| Updated deal-breakers | `match_learnings.evolved_dealbreakers` | Inferred from feedback patterns |
| Coaching receptiveness | `match_learnings.coaching_receptiveness` | Tracked through conversation |
| Preference drift | `match_learnings.preference_drift_patterns` | Longitudinal comparison |

**Extraction Method:**  
System compares:
- What they said they want (Tier 2 preferences)
- Who they actually react positively to (Tier 4 matches)
- Gaps = calibration gold

---

## **EXTRACTION ROUTING LOGIC**

### Real-Time Extraction Flow

```
1. User sends message
   ↓
2. LLM analyzes message + recent context
   ↓
3. Extract signals with confidence scores
   ↓
4. Route to schema:
   
   IF hard filter (Tier 1):
     → Update users table column
     → Mark tier_progress.completed_fields
   
   IF soft signal (Tier 2-3):
     → Merge into user_signals JSONB
     → Update if confidence > existing OR first time
     → Track in tier_progress.completed_fields
   
   IF partner preference:
     → Update user_preferences table
   
   IF match feedback (Tier 4):
     → Write to matches table
     → Update user_signals.match_learnings
   
5. Recalculate tier completion %
   ↓
6. Check MVP activation rules
   ↓
7. If MVP met → Set users.profile_active = TRUE
```

---

## **CONFIDENCE THRESHOLDS**

- **Store signal if:** `confidence >= 0.70`
- **Update existing signal if:** `new_confidence > existing_confidence`
- **Mark "stable" if:** Same value observed 3+ times
- **Flag contradiction if:** Conflicting values with high confidence

---

## **TIER COMPLETION CALCULATION**

### Tier 1 (15 required fields):
- Full name, DOB, gender, orientation, city, nationality, religion, children_intent, marital_history, smoking, drinking, relationship_intent
- **Completion = (populated_count / 15) × 100**

### Tier 2 (40 target fields):
- 13 lifestyle + 10 values + 10 relationship_style + 7 preferences
- **Completion = (populated_count / 40) × 100**
- **Weight only signals with confidence >= 0.70**

### Tier 3 (30 target fields):
- 14 personality + 8 family_background + 8 media_signals
- **Completion = (populated_count / 30) × 100**

### Tier 4 (Ongoing):
- Completion = matches with feedback / total matches

---

## **MVP ACTIVATION CHECKLIST**

```sql
SELECT 
  tier1_completion = 100 AS tier1_complete,
  tier2_completion >= 70 AS tier2_ready,
  open_ended_count >= 2 AS enough_open_ended,
  calculate_total_completeness(user_id) >= 45 AS total_complete,
  session_count >= 2 AS multiple_sessions,
  -- All must be TRUE
  (tier1_completion = 100 AND 
   tier2_completion >= 70 AND 
   open_ended_count >= 2 AND 
   calculate_total_completeness(user_id) >= 45 AND 
   session_count >= 2) AS mvp_achieved
FROM tier_progress
WHERE user_id = $1;
```

When **all criteria TRUE** → Activate matching!

---

**For Blitz:** This document is your reference for implementing extraction logic in the conversation orchestrator.  
**For N/Xing:** Review and confirm field priorities + MVP rules.
