# JODI Schema Upgrade Summary
**Matchmaking Data Capture Framework v1 → Supabase Implementation**

---

## What Changed

### **Before (Old System):**
- ~30 data fields
- Basic user profile + preferences
- Simple matching logic

### **After (New Framework):**
- **100+ data fields** across 4 tiers
- **Hard filters** (indexed columns) vs **Signals** (JSONB scoring)
- **Explicit vs Inferred** architecture (40% stated, 60% AI-extracted)
- **Progressive disclosure** (Tier 1 → Tier 2 → Tier 3 → Tier 4)
- **MVP activation gates** (don't match until ready)
- **Tier 4 calibration** (stated vs revealed preferences)

---

## Database Changes

### **Tables Modified:**
1. **`users`** — Added 20+ hard filter columns (age, religion, children_intent, etc.)
2. **`user_signals`** (NEW) — JSONB storage for all inferred/soft signals
3. **`user_preferences`** (NEW) — Partner requirements (hard + soft with weights)
4. **`tier_progress`** (NEW) — Tracks completion % and MVP activation
5. **`matches`** (NEW) — Match history + Tier 4 calibration data

### **Key Schema Decisions:**

#### **Hard Filters → Indexed Postgres Columns**
Used for **elimination** (not scoring). Must be fast for filtering.

Examples:
- `users.age` (indexed)
- `users.religion` (indexed)
- `users.city` (indexed)
- `users.children_intent` (indexed)

**Why:** Matching queries like `WHERE age BETWEEN 25 AND 35 AND religion = 'Muslim'` need indexes.

---

#### **Signals → JSONB with Confidence Scores**
Used for **scoring** (not elimination). Flexible schema for AI-inferred data.

Examples:
```json
// user_signals.lifestyle
{
  "work_style": {
    "value": "Startup",
    "confidence": 0.85,
    "source": "inferred",
    "updated_at": "2026-02-11T10:30:00Z"
  },
  "ambition_level": {
    "value": "Driven",
    "confidence": 0.90,
    "source": "inferred",
    "updated_at": "2026-02-11T10:32:15Z"
  }
}
```

**Why:** Inferred signals have confidence scores. Store everything as JSONB so schema can evolve without migrations.

---

#### **Tier Progress Tracking**
Tracks completion % for each tier + MVP activation status.

Key fields:
- `tier1_completion` (0.00-100.00)
- `tier2_completion` (0.00-100.00)
- `mvp_achieved` (BOOLEAN)
- `mvp_blocked_reasons` (TEXT[])

**MVP Activation Rules:**
- ✅ 100% Tier 1 (all hard filters)
- ✅ 70%+ Tier 2 (lifestyle + values)
- ✅ 2+ open-ended responses
- ✅ 45%+ total completeness
- ✅ 2+ sessions (prevents rushed signups)

**When all TRUE:** `users.profile_active = TRUE` → matching begins

---

## What DIDN'T Change

### **System Architecture (Kept As-Is):**
✅ Real-time conversational extraction (no batch delays)  
✅ LLM extracts signals during live chat  
✅ Conversation orchestrator manages question flow  
✅ All extraction happens in conversation loop  

**No policy shift — just expanded the data model.**

---

## For Blitz: Implementation Checklist

### **1. Run Schema Migrations**
```bash
cd /Users/nikunjvora/clawd/JODI/schema
export SUPABASE_DB_URL='postgresql://...'  # Get from Supabase dashboard
chmod +x 00_run_migrations.sh
./00_run_migrations.sh
```

This creates/upgrades all tables.

---

### **2. Update Conversation Orchestrator**

The orchestrator needs to:

#### **A. Extract Signals with Confidence Scores**
When LLM analyzes a message, output JSON like:
```json
{
  "signals": [
    {
      "field": "work_style",
      "value": "Startup",
      "confidence": 0.85,
      "tier": 2,
      "category": "lifestyle",
      "source": "inferred"
    },
    {
      "field": "ambition_level",
      "value": "Driven",
      "confidence": 0.90,
      "tier": 2,
      "category": "values",
      "source": "inferred"
    }
  ]
}
```

#### **B. Route Extracted Values to Schema**
Use the mapping in `DATA_FIELD_MAPPING.md`:

```python
def route_signal(signal):
    if signal['category'] in ['users', 'hard_filter']:
        # Update users table column
        update_user_column(signal['field'], signal['value'])
    
    elif signal['category'] in ['lifestyle', 'values', 'personality', 'family', 'media']:
        # Merge into user_signals JSONB
        merge_signal_to_jsonb(
            table='user_signals',
            column=signal['category'],
            field=signal['field'],
            value={
                'value': signal['value'],
                'confidence': signal['confidence'],
                'source': signal['source'],
                'updated_at': datetime.utcnow()
            }
        )
    
    elif signal['category'] == 'preferences':
        # Update user_preferences
        update_user_preferences(signal['field'], signal['value'])
```

#### **C. Track Tier Progress**
After each extraction:
```python
# 1. Mark field as completed
add_to_completed_fields(user_id, tier=signal['tier'], field=signal['field'])

# 2. Recalculate tier completion %
tier_completion = calculate_tier_completion(user_id, tier=signal['tier'])
update_tier_progress(user_id, f'tier{signal["tier"]}_completion', tier_completion)

# 3. Update total completeness
total = calculate_total_completeness(user_id)
update_user_completeness(user_id, total)

# 4. Check MVP activation
if check_mvp_criteria(user_id):
    activate_user_for_matching(user_id)
```

---

### **3. Update LLM Extraction Prompts**

**System Prompt Addition:**
```
You are extracting matchmaking signals from conversation. For each message, identify:
1. Explicit statements (confidence = 1.0)
2. Inferred signals (confidence = 0.0-1.0 based on strength of evidence)

Output JSON with:
- field: Name from DATA_FIELD_MAPPING.md
- value: Extracted value
- confidence: 0.0-1.0 (how certain you are)
- tier: 1-4 (from framework)
- category: lifestyle/values/personality/etc
- source: "explicit" or "inferred"

Only extract signals with confidence >= 0.70.
```

**Extraction Context:**
Pass last 10 messages + user's current signals to LLM for context.

---

### **4. Implement MVP Gating**

When user tries to see matches but MVP not met:

```python
mvp_status = check_mvp_activation(user_id)

if not mvp_status['meets_mvp']:
    blockers = mvp_status['blocked_reasons']
    
    # Show friendly message
    return f"""
    I'm still learning about you! I need a little more to find great matches.
    
    What's missing:
    {format_blockers(blockers)}
    
    Chat with me for a few more minutes and we'll get there. 😊
    
    Quick question: {next_question_for_tier2()}
    """
```

---

### **5. Add Progress UI**

Show completion % to users:
```python
completeness = get_user_completeness(user_id)

return f"""
Your profile is {completeness}% complete.
The more I know, the better your matches! 🎯

Current tier: {get_current_tier_name(user_id)}
"""
```

Tier names (user-facing):
- Tier 1: "The Basics"
- Tier 2: "Ready"
- Tier 3: "Deep Profile"
- Tier 4: "Calibrated"

---

## Testing Checklist

### **Schema Validation:**
- [ ] All migrations run successfully
- [ ] Indexes created (check with `\d+ users`)
- [ ] JSONB structure works (test insert/query)
- [ ] Helper functions work (`calculate_total_completeness`, `check_mvp_activation`)

### **Extraction Pipeline:**
- [ ] LLM extracts signals with confidence scores
- [ ] Signals route to correct schema locations
- [ ] Tier progress updates after each extraction
- [ ] MVP activation triggers when criteria met

### **User Flow:**
- [ ] New user completes Tier 1 → profile created
- [ ] Continues chatting → Tier 2 builds
- [ ] Hits 70% Tier 2 → matching activates
- [ ] Below MVP → sees "building your profile" message
- [ ] Above MVP → sees "you're in, searching..." message

---

## SQL Helper Queries

### Check user's tier progress:
```sql
SELECT 
  u.full_name,
  u.tier_level,
  u.profile_active,
  u.completeness_score,
  tp.tier1_completion,
  tp.tier2_completion,
  tp.tier3_completion,
  tp.open_ended_count,
  tp.session_count,
  tp.mvp_achieved
FROM users u
JOIN tier_progress tp ON u.id = tp.user_id
WHERE u.id = '<user_id>';
```

### Check what's blocking MVP:
```sql
SELECT * FROM check_mvp_activation('<user_id>');
```

### View user's signals:
```sql
SELECT 
  lifestyle,
  values,
  personality
FROM user_signals
WHERE user_id = '<user_id>';
```

### See match calibration data:
```sql
SELECT 
  match_score,
  user_first_impression,
  date_feedback,
  revealed_preferences
FROM matches
WHERE user_id = '<user_id>'
ORDER BY created_at DESC;
```

---

## Next Steps

1. **Kavi:** Run migrations on dev Supabase instance
2. **Blitz:** Update conversation orchestrator with extraction routing
3. **Blitz:** Implement tier progress tracking
4. **Blitz:** Add MVP gating to matching flow
5. **Blitz:** Test full Tier 1 → Tier 2 → MVP activation flow
6. **N/Xing:** Review progress UI copy + tier names

---

## Questions?

- **Schema design:** Kavi
- **Implementation:** Blitz (with Kavi support)
- **Product/UX:** Xing + N

**Docs:** All files in `/Users/nikunjvora/clawd/JODI/schema/`
