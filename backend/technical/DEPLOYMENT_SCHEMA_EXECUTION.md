# JODI Schema Execution - Deployment Summary

**Status:** ✅ READY TO SHIP  
**Approved By:** N  
**Date:** 2026-02-12  
**Agent:** Kavi (Subagent)

---

## Executive Summary

**Scope:** Complete 100+ data point framework implementation with extraction pipeline  
**Changes:**
- ✅ Schema updated to cover 100/100+ data points (Tiers 1-4)
- ✅ Age validation added (18-80 years, DOB parsing)
- ✅ Telegram button flows for 14 critical categorical fields
- ✅ Extraction pipeline with full CRUD operations
- ✅ Helper functions for signal management
- ⚠️ Photo validation SKIPPED (per N approval)

**What's New:**
1. 7 new columns in `matches` table (Tier 4 match reactions)
2. Age validation on DOB (18-80 enforced)
3. JSONB helper functions for CRUD operations
4. Telegram button flows configuration
5. LLM extraction pipeline with confidence tracking
6. Auto-recalculate completeness triggers

---

## Files Delivered

### 1. Schema Migrations (SQL)
- **`schema/06_complete_100_datapoints.sql`**
  - Age validation (18-80 years)
  - 7 new `matches` table columns for Tier 4
  - Helper functions: `upsert_user_signal`, `get_user_signal`, `calculate_tier_completion`, `check_mvp_activation`
  - Indexes for performance

- **`schema/07_helper_functions.sql`**
  - `remove_user_signal` (DELETE operation)
  - `get_user_signals_above_confidence` (filtered READ)
  - `export_user_profile` (full profile JSON export)
  - `calculate_weighted_completeness` (Tier 1: 50%, Tier 2: 35%, Tier 3: 15%)
  - Auto-recalculate triggers on updates

### 2. Extraction Pipeline (TypeScript)
- **`extraction_pipeline.ts`**
  - DOB parsing with age validation (18-80)
  - LLM-based multi-field extraction
  - CRUD operations: `createField`, `readField`, `updateField`, `deleteField`
  - Confidence-based updates (only update if new >= existing)
  - Auto-route fields to correct storage (columns vs JSONB)
  - MVP activation check after each extraction

### 3. Telegram Button Flows (TypeScript)
- **`telegram_button_flows.ts`**
  - 10 Tier 1 button flows (gender, orientation, religion, kids, marital, smoking, drinking, diet, intent, timeline)
  - 4 Tier 2 button flows (work style, exercise, pets, love language)
  - 2 Tier 4 button flows (date willingness, first impression)
  - Helper functions: `generateButtonMarkup`, `parseCallbackData`

### 4. Documentation
- **`schema_audit_and_additions.md`**
  - Complete audit of 100+ data points vs current schema
  - Missing field analysis
  - Action items checklist

---

## Deployment Checklist

### PHASE 1: Database Migration (CRITICAL - DO FIRST)

```bash
# 1. Backup production database
pg_dump -U postgres -h <DB_HOST> jodi_prod > jodi_backup_$(date +%Y%m%d).sql

# 2. Run migrations in order
psql -U postgres -h <DB_HOST> -d jodi_prod -f schema/06_complete_100_datapoints.sql
psql -U postgres -h <DB_HOST> -d jodi_prod -f schema/07_helper_functions.sql

# 3. Verify migration success
psql -U postgres -h <DB_HOST> -d jodi_prod -c "
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'matches' 
  AND column_name IN ('user_first_impression', 'date_willingness', 'date_feedback');
"
# Should return 3 rows

# 4. Test helper functions
psql -U postgres -h <DB_HOST> -d jodi_prod -c "
  SELECT calculate_tier_completion(1, 1); -- Test tier completion calculation
"
```

**ROLLBACK (if needed):**
```bash
psql -U postgres -h <DB_HOST> -d jodi_prod < jodi_backup_$(date +%Y%m%d).sql
```

---

### PHASE 2: Code Deployment

#### A. Install TypeScript Files
```bash
# Copy extraction pipeline to backend
cp extraction_pipeline.ts /path/to/backend/src/extraction/
cp telegram_button_flows.ts /path/to/backend/src/telegram/

# Install dependencies (if not already present)
npm install @supabase/supabase-js
```

#### B. Environment Variables
Add to `.env`:
```env
# Age validation
MIN_USER_AGE=18
MAX_USER_AGE=80

# LLM API (for extraction)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Confidence thresholds
MIN_SIGNAL_CONFIDENCE=0.70
MIN_TIER1_CONFIDENCE=0.90
```

#### C. Update Conversation Agent
Integrate extraction pipeline into conversation handler:

```typescript
import { processConversationMessage } from './extraction/extraction_pipeline';
import { TIER_1_BUTTON_FLOWS, generateButtonMarkup } from './telegram/telegram_button_flows';

async function handleUserMessage(userId: number, message: string, messageHistory: string[]) {
  const context = {
    user_id: userId,
    message: message,
    message_history: messageHistory,
    current_tier: await getCurrentTier(userId)
  };
  
  // Extract fields from message
  const result = await processConversationMessage(supabase, context);
  
  // Check if user just achieved MVP
  if (result.tier_updated) {
    await sendTelegramMessage(userId, "🎉 Your profile is ready! Let's find you some matches.");
  }
  
  // Handle errors
  if (result.errors.length > 0) {
    // Log errors but don't block user
    console.error('Extraction errors:', result.errors);
  }
  
  return result.extracted;
}
```

#### D. Integrate Telegram Buttons
```typescript
import { TIER_1_BUTTON_FLOWS } from './telegram/telegram_button_flows';

// When asking for categorical field, use buttons
async function askForGender(userId: number) {
  const genderFlow = TIER_1_BUTTON_FLOWS.find(f => f.field === 'gender_identity');
  
  await bot.sendMessage(userId, genderFlow.question, {
    reply_markup: generateButtonMarkup(genderFlow)
  });
}

// Handle button callbacks
bot.on('callback_query', async (query) => {
  const { field, value, storage, table, column } = parseCallbackData(
    query.data, 
    TIER_1_BUTTON_FLOWS
  );
  
  const extraction = {
    field,
    value,
    confidence: 1.0,
    source: 'button',
    tier: 1,
    storage_location: storage,
    table,
    column
  };
  
  await createField(supabase, query.from.id, extraction);
  await bot.answerCallbackQuery(query.id, { text: `Got it: ${value}` });
});
```

---

### PHASE 3: Testing

#### Test 1: Age Validation
```sql
-- Should SUCCEED (age 25)
INSERT INTO users (telegram_id, date_of_birth) 
VALUES (999999, '1999-02-12');

-- Should FAIL (age 17)
INSERT INTO users (telegram_id, date_of_birth) 
VALUES (999998, '2007-02-12');

-- Should FAIL (age 81)
INSERT INTO users (telegram_id, date_of_birth) 
VALUES (999997, '1943-02-12');
```

#### Test 2: Signal CRUD
```typescript
// Test extraction pipeline
const testContext = {
  user_id: 1,
  message: "I'm 28, live in Dubai, and I'm a software engineer. I go to the gym 4 times a week.",
  message_history: [],
  current_tier: 1
};

const result = await processConversationMessage(supabase, testContext);

console.log('Extracted fields:', result.extracted);
// Should extract: age, city, occupation, exercise_fitness

// Test READ
const cityField = await ProfileCRUD.read(supabase, 1, 'city');
console.log('City:', cityField.value); // "Dubai"

// Test UPDATE
await ProfileCRUD.update(supabase, 1, {
  field: 'city',
  value: 'Mumbai',
  confidence: 1.0,
  source: 'explicit',
  tier: 1,
  storage_location: 'users_column',
  table: 'users',
  column: 'city'
});

// Test DELETE
await ProfileCRUD.delete(supabase, 1, 'city');
```

#### Test 3: Tier Completion & MVP
```sql
-- Check tier completion for user ID 1
SELECT 
  calculate_tier_completion(1, 1) as tier1,
  calculate_tier_completion(1, 2) as tier2,
  calculate_tier_completion(1, 3) as tier3;

-- Check MVP activation
SELECT * FROM check_mvp_activation(1);

-- Should show:
-- tier1_complete, tier2_ready, enough_open_ended, total_complete, multiple_sessions, mvp_achieved
```

#### Test 4: Telegram Buttons
```typescript
// Simulate button click
const callbackData = 'gender_male';
const parsed = parseCallbackData(callbackData, TIER_1_BUTTON_FLOWS);

console.log(parsed);
// { field: 'gender_identity', value: 'Male', storage: 'column', table: 'users', column: 'gender_identity' }
```

---

### PHASE 4: Production Rollout

#### Step 1: Soft Launch (10% of users)
- Enable new extraction pipeline for 10% of new signups
- Monitor error rates, extraction accuracy
- Check Supabase logs for constraint violations

#### Step 2: Gradual Ramp (50% → 100%)
- Increase to 50% after 24h with no critical issues
- Full rollout after 48h

#### Step 3: Backfill Existing Users (Optional)
- Run extraction pipeline on existing user message history
- Populate missing Tier 2-3 signals from past conversations

```typescript
async function backfillUserSignals(userId: number) {
  const messages = await getMessageHistory(userId);
  
  for (const msg of messages) {
    const context = {
      user_id: userId,
      message: msg.text,
      message_history: [],
      current_tier: 2
    };
    
    await processConversationMessage(supabase, context);
  }
}
```

---

## Critical Validations

### ✅ Age Validation (18-80 years)
- Enforced at DB level via CHECK constraint
- Validated in DOB extraction function
- Error message: "Age must be between 18 and 80 years. Calculated age: X"

### ✅ Confidence Thresholds
- Tier 1 hard filters: confidence >= 0.90 (explicit only)
- Tier 2-3 signals: confidence >= 0.70 to count toward tier completion
- Updates only happen if new confidence >= existing

### ✅ MVP Activation Rules
1. 100% Tier 1 complete (15 required fields)
2. 70% Tier 2 complete (23/33 fields)
3. 2+ open-ended responses captured
4. 45% total weighted completeness
5. 2+ separate sessions

All conditions must be TRUE to activate matching.

---

## LLM Integration (TODO for Blitz/DevOps)

Replace placeholder in `extraction_pipeline.ts`:

```typescript
async function callLLMAPI(prompt: string, model: 'claude' | 'gpt'): Promise<string> {
  if (model === 'claude') {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1024,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    
    const data = await response.json();
    return data.content[0].text;
    
  } else {
    // OpenAI fallback
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [{ role: 'user', content: prompt }]
      })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
  }
}
```

---

## Monitoring & Alerts

### Key Metrics to Track

1. **Extraction accuracy**
   - % of messages that extract at least 1 field
   - Average confidence scores by tier
   - LLM API error rate

2. **Age validation failures**
   - Count of users who provide age < 18 or > 80
   - Track drop-off at age entry

3. **Tier completion rates**
   - % of users reaching Tier 1 complete
   - % reaching Tier 2 (70%+) for MVP
   - Time to MVP (median days)

4. **Button vs. Text extraction**
   - Accuracy comparison: button inputs vs. LLM-parsed text
   - Button usage rate for categorical fields

### Supabase Dashboard Queries

```sql
-- Tier completion distribution
SELECT 
  tier_level,
  COUNT(*) as user_count,
  AVG(completeness_score) as avg_completeness
FROM users
GROUP BY tier_level;

-- MVP activation rate
SELECT 
  COUNT(*) FILTER (WHERE profile_active = true) as active_users,
  COUNT(*) as total_users,
  (COUNT(*) FILTER (WHERE profile_active = true)::decimal / COUNT(*)) * 100 as activation_rate
FROM users
WHERE created_at > NOW() - INTERVAL '30 days';

-- Field extraction confidence distribution
SELECT 
  category,
  field,
  AVG((value->>'confidence')::decimal) as avg_confidence,
  COUNT(*) as signal_count
FROM (
  SELECT 'lifestyle' as category, key as field, value
  FROM user_signals, jsonb_each(lifestyle)
  UNION ALL
  SELECT 'values', key, value
  FROM user_signals, jsonb_each(values)
) signals
GROUP BY category, field
ORDER BY avg_confidence DESC;
```

---

## Known Limitations & Future Work

### Current Limitations
1. **Photo validation:** Skipped per N approval (will need separate ML pipeline)
2. **LLM extraction accuracy:** Depends on model quality + prompt engineering
3. **Voice note analysis:** Tier 3C media signals not yet implemented (requires speech-to-text)
4. **Multilingual support:** Extraction currently English-only

### Future Enhancements
1. **Active learning:** Flag low-confidence extractions for human review
2. **Contradiction detection:** Alert when user statements conflict (e.g., "Never smoked" vs. "I quit smoking last year")
3. **Preference calibration:** Compare stated vs. revealed preferences after 5+ matches
4. **Automated wording iteration:** A/B test question phrasing for higher response rates

---

## Rollback Plan

If critical issues arise:

1. **Disable new extraction pipeline:**
   ```typescript
   const ENABLE_NEW_EXTRACTION = false; // Feature flag
   ```

2. **Revert database migrations:**
   ```bash
   psql -U postgres -h <DB_HOST> -d jodi_prod < jodi_backup_$(date +%Y%m%d).sql
   ```

3. **Fall back to manual data entry:**
   - Use Telegram buttons only (no LLM extraction)
   - Require explicit input for all fields

---

## Success Criteria

### Week 1 (Soft Launch)
- ✅ 0 age validation constraint violations (catch at input)
- ✅ >80% of Tier 1 fields extracted successfully via buttons
- ✅ <5% LLM extraction error rate
- ✅ 10+ users reach MVP (Tier 2 70%+)

### Week 2 (Full Rollout)
- ✅ 50+ users activated for matching (profile_active = TRUE)
- ✅ Median time to MVP < 5 days
- ✅ Average Tier 2 completeness > 75%
- ✅ <2% rollback rate (users reverting fields)

### Month 1 (Calibration)
- ✅ 100+ match reactions captured (Tier 4 data)
- ✅ 5+ users show stated vs. revealed preference gaps
- ✅ LLM extraction accuracy > 85% (validated against button inputs)

---

## Contact

**Questions or issues?**
- Schema/DB: Kavi or DevOps
- Extraction logic: Blitz
- Product decisions: N or Xing

**Deployment timeline:** ASAP (N approved)

---

**DEPLOYMENT READY ✅**
