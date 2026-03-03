# JODI Multi-Channel Architecture

**Problem:** Support same user across Telegram, WhatsApp, and web form with unified state  
**Solution:** Phone-based identity + channel-agnostic state management

---

## Core Principles

1. **Phone number = universal identifier** (perfect for Indian matchmaking)
2. **Single source of truth** (users table)
3. **Channel-agnostic progress** (resume from any channel)
4. **Real-time state sync** (sessions → users table)
5. **Audit trail** (conversation_logs tracks all interactions)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    CHANNELS (Entry Points)               │
├─────────────┬─────────────┬─────────────┬──────────────┤
│  Telegram   │  WhatsApp   │  Web Form   │    Email     │
│  (bot DM)   │  (business) │  (landing)  │  (magic link)│
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬───────┘
       │             │              │             │
       │             │              │             │
       ▼             ▼              ▼             ▼
┌──────────────────────────────────────────────────────────┐
│            IDENTITY LAYER (user_channels)                 │
│  Maps channel IDs → user_id                              │
│  • telegram_id: 7207658858 → user_id: abc123             │
│  • whatsapp_phone: +971585408825 → user_id: abc123       │
│  • session_token: xyz789 → user_id: abc123               │
│  • email: nikunj.vora@gmail.com → user_id: abc123        │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│         STATE MANAGEMENT (sessions + users)               │
│                                                           │
│  ┌─────────────────┐          ┌──────────────────┐      │
│  │  sessions        │ ────────▶│  users (canonical)│     │
│  │  (ephemeral)     │  flush   │  (source of truth)│     │
│  │  • Per channel   │          │  • Profile        │     │
│  │  • Fast writes   │          │  • Progress       │     │
│  │  • Loop tracking │          │  • Tier/completeness     │
│  └─────────────────┘          └──────────────────┘      │
│                                                           │
│  ┌─────────────────────────────────────────────┐        │
│  │  conversation_logs (audit trail)            │        │
│  │  • All Q&A interactions                      │        │
│  │  • Channel metadata                          │        │
│  │  • Timestamps                                │        │
│  └─────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

---

## User Flow Examples

### Flow 1: Telegram → WhatsApp (same user)

```
Day 1: Telegram
1. User sends /start on Telegram
2. Bot: "What's your phone number?" (validates via OTP)
3. User: +971585408825
4. System:
   - Creates user: id=abc123, phone=+971585408825
   - Links: user_channels (user_id=abc123, channel_type=telegram, channel_identifier=7207658858)
5. User completes 45% (Q1-Q26)
6. User leaves

Day 2: WhatsApp
1. User sends message to WhatsApp business number
2. System checks: user_channels WHERE channel_type=whatsapp AND channel_identifier=+971585408825
   - Not found → New WhatsApp user
3. Bot: "Have you used Jodi before?"
   - User: "Yes, I started on Telegram"
4. Bot: "What's your phone number?" (or auto-detect from WhatsApp metadata)
5. User: +971585408825
6. System:
   - Lookup: users WHERE phone=+971585408825
   - Found! user_id=abc123
   - Link: user_channels (user_id=abc123, channel_type=whatsapp, channel_identifier=+971585408825)
7. Bot: "Welcome back! You're 45% complete. Let's pick up where you left off."
8. Load state: current_question=27 (next unanswered)
9. User continues from Q27 on WhatsApp
```

### Flow 2: Web Form → Telegram (same user)

```
Day 1: Web Form (email marketing campaign)
1. User clicks email link: https://jodi.com/start?ref=email_campaign
2. Landing page: "What's your phone number?" (or email)
3. User: +971585408825 (OTP verification)
4. System:
   - Creates user: id=xyz456, phone=+971585408825
   - Links: user_channels (user_id=xyz456, channel_type=web, channel_identifier=session_token_abc)
5. User completes 30% on web form (Q1-Q20)
6. User leaves

Day 2: Telegram (discovers bot)
1. User sends /start on Telegram
2. Bot: "What's your phone number?"
3. User: +971585408825
4. System:
   - Lookup: users WHERE phone=+971585408825
   - Found! user_id=xyz456
   - Link: user_channels (user_id=xyz456, channel_type=telegram, channel_identifier=7207658858)
5. Bot: "Hey! I see you started on our website. You're 30% complete. Want to continue here?"
6. User: "Yes"
7. Load state: current_question=21 (next unanswered)
8. User continues from Q21 on Telegram
```

---

## Implementation Strategy

### Phase 1: Phone-Based Identity (Week 1)

**Goal:** All users have phone numbers, enabling cross-channel linking

**Changes:**
1. Add phone collection at start of flow (Q0.5: "What's your phone number?")
2. Validate phone via OTP (Twilio Verify API)
3. Store in users.phone (UNIQUE)
4. Create user_channels record on first interaction

**Code:**
```python
async def collect_phone_number(update, context, telegram_id):
    # Ask for phone
    await update.message.reply_text(
        "Quick question first — what's your phone number?\n\n"
        "We use this to sync your profile across devices (Telegram, WhatsApp, web).\n\n"
        "Format: +971585408825"
    )
    
    # After user provides phone
    phone = validate_phone(user_input)
    
    # Get or create user
    user_id = get_or_create_user_by_phone(phone, 'telegram', telegram_id)
    
    # Check if user has existing progress
    if has_existing_progress(user_id):
        await show_resume_prompt(update, context, user_id)
    else:
        await start_fresh_onboarding(update, context, user_id)
```

### Phase 2: Session State Sync (Week 2)

**Goal:** All channels write to users table, enabling cross-channel resume

**Changes:**
1. Modify bot handlers to use user_id (not telegram_id)
2. Write answers to both sessions (fast) and users (canonical)
3. Resume logic: load from users table, skip already-answered
4. Show progress: "You're 45% complete. Let's continue..."

**Code:**
```python
async def resume_onboarding(user_id, channel_type):
    # Load canonical state from users table
    user = db.query("SELECT * FROM users WHERE id = %s", (user_id,))
    answers = load_all_answers(user_id)  # users + user_preferences + user_signals
    
    # Find next unanswered question
    next_q = find_next_unanswered_question(answers, user.current_question)
    
    # Create session for this channel
    session = {
        'user_id': user_id,
        'channel_type': channel_type,
        'current_question': next_q,
        'answers': answers,
        'asked_questions': list(range(1, next_q))  # Already asked
    }
    save_session(session)
    
    return f"Welcome back! You're {calculate_completeness(user_id)}% complete."
```

### Phase 3: WhatsApp Integration (Week 3)

**Goal:** WhatsApp business number receives messages, syncs with existing users

**Changes:**
1. WhatsApp webhook receiver (FastAPI endpoint)
2. Phone number extraction from WhatsApp metadata
3. Lookup user_channels → user_id
4. Same bot logic as Telegram (different message formatting)

**Code:**
```python
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    
    # Extract WhatsApp phone
    whatsapp_phone = data['from']  # +971585408825
    message_text = data['text']['body']
    
    # Get or create user
    user_id = get_user_id_from_channel('whatsapp', whatsapp_phone)
    
    if not user_id:
        # New WhatsApp user
        await ask_for_linking(whatsapp_phone)  # "Have you used Jodi before?"
    else:
        # Existing user
        await handle_message(user_id, 'whatsapp', message_text)
```

### Phase 4: Web Form (Week 4)

**Goal:** Web form on landing page syncs with Telegram/WhatsApp

**Changes:**
1. Next.js form with same 77 questions
2. Phone collection + OTP verification
3. Progress bar (visual equivalent of section transitions)
4. Save to same users table
5. Generate magic link for email (JWT with user_id)

---

## Database Queries (Common Patterns)

### Get user_id from any channel

```sql
-- From Telegram
SELECT user_id FROM user_channels 
WHERE channel_type = 'telegram' AND channel_identifier = '7207658858';

-- From WhatsApp
SELECT user_id FROM user_channels
WHERE channel_type = 'whatsapp' AND channel_identifier = '+971585408825';

-- From phone (any channel)
SELECT id FROM users WHERE phone = '+971585408825';
```

### Link new channel to existing user

```sql
-- User switches from Telegram to WhatsApp
INSERT INTO user_channels (user_id, channel_type, channel_identifier)
VALUES ('abc123', 'whatsapp', '+971585408825')
ON CONFLICT (channel_type, channel_identifier) DO UPDATE SET last_used = NOW();
```

### Load user state for resume

```sql
-- Get all answered questions
SELECT 
    u.id, u.phone, u.current_question, u.completeness, u.tier,
    -- All fields from users table
FROM users u
WHERE u.id = 'abc123';

-- Find next unanswered question
SELECT MIN(question_num) FROM (
    SELECT question_num FROM all_questions
    WHERE question_num NOT IN (
        SELECT question_num FROM answered_questions WHERE user_id = 'abc123'
    )
) AS unanswered;
```

---

## Edge Cases & Solutions

### 1. **User has multiple phone numbers**
- Solution: Allow multiple phones linked to same user_id
- Primary phone marked with is_primary = TRUE
- Ask: "We found 2 numbers. Which one is yours?"

### 2. **User forgot which channel they used**
- Solution: Ask for phone number
- Lookup across all channels
- Show: "I found your profile! You used [Telegram] last on [Feb 21]."

### 3. **Conflicting answers across channels**
- Solution: Last write wins (timestamp)
- Show diff: "You answered differently on Telegram vs WhatsApp. Which is correct?"

### 4. **Session expiry**
- Solution: Sessions auto-expire after 7 days
- Users table is permanent
- On return: recreate session from users table

### 5. **Privacy: sharing phone number**
- Solution: Optional (can use email or Telegram username)
- But phone strongly recommended for WhatsApp integration
- Show: "Phone helps us sync your profile across devices (optional)"

---

## Metrics to Track

1. **Cross-channel adoption:** % users who use >1 channel
2. **Resume rate:** % users who resume after leaving
3. **Preferred channel:** Which channel has highest completion rate
4. **Channel mix:** Distribution of users across channels
5. **Sync latency:** Time between channel switch and state load

---

## Security Considerations

1. **Phone verification:** OTP required before linking phone
2. **Session tokens:** JWT with short expiry (web form)
3. **Rate limiting:** Prevent phone number enumeration attacks
4. **Encryption:** Phone numbers hashed in logs
5. **GDPR:** User can delete all data across all channels

---

## Files Created

1. `/ventures/jodi/schema/12_multi_channel_identity.sql` — DB schema
2. `/ventures/jodi/MULTI_CHANNEL_ARCHITECTURE.md` — This doc

**Next steps:**
1. Apply migration to Supabase
2. Update bot handlers to use user_id (not telegram_id)
3. Add phone collection flow
4. Build resume logic
5. Test cross-channel linking
