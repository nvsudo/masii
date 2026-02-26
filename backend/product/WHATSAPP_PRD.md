# JODI WhatsApp PRD — Product Requirements Document

**Date:** 2026-02-22  
**Owner:** Seema  
**Status:** Draft for Review  
**Target Launch:** Q1 2026

---

## 🎯 Executive Summary

**What:** WhatsApp Business integration for Jodi's matchmaking onboarding, enabling users to complete profile-building via WhatsApp instead of (or in addition to) Telegram.

**Why:** 
- **Reach:** WhatsApp has 2B+ global users, 500M+ in India alone (vs Telegram's 55M India users)
- **Trust:** In South Asian/Middle Eastern markets, WhatsApp is the primary family communication channel
- **Convenience:** Phone number = identity (no separate signup), native to users' daily habits
- **Market fit:** Our demographic (25-40, diaspora, marriage-focused) lives on WhatsApp

**How:** Adapt existing Telegram onboarding flow to WhatsApp Business API constraints, leverage multi-channel architecture for cross-platform continuity.

**Success Metrics:**
- 50% of new signups via WhatsApp within 3 months of launch
- 65%+ button-phase completion rate (vs 60% target on Telegram)
- 30%+ cross-channel usage (users who switch Telegram ↔ WhatsApp)
- Sub-2-hour response time for conversational phase

---

## 🧩 Problem Statement

### Current State
- Jodi onboarding exists on Telegram only
- Telegram penetration is lower in our target markets (UAE, Saudi, India tier-2 cities)
- Family members (who often influence matchmaking decisions) don't use Telegram
- Users can't easily switch devices mid-flow

### Desired State
- User starts on WhatsApp (their primary messaging app)
- Family members can verify it's a "real" business (blue checkmark matters)
- Seamless cross-channel experience (start on WhatsApp, continue on Telegram, or vice versa)
- Higher trust signal due to WhatsApp's business verification

---

## 👥 Target Audience

### Primary Users
- **Age:** 25-40
- **Location:** UAE, Saudi Arabia, India (metros + tier-2 cities), UK, US
- **Demographic:** Indian/Pakistani/Bangladeshi diaspora + locals in Gulf
- **Psychographic:** Marriage-focused, family-oriented, values trust/privacy
- **Tech comfort:** Medium (comfortable with WhatsApp, may not use Telegram)

### Key Insights
1. **WhatsApp = Trust:** "If it's on WhatsApp, it's real" (especially for 30+ demographic)
2. **Family involvement:** Parents/siblings often involved in matchmaking process — WhatsApp easier to show/explain
3. **Device switching:** Users often use WhatsApp on phone, Telegram on desktop — want flexibility
4. **Regional preference:** Gulf users strongly prefer WhatsApp over Telegram

---

## 🔧 Technical Architecture

### WhatsApp Business API Setup

**Provider:** Meta Cloud API (recommended) or Twilio WhatsApp Business  
**Phone Number:** Dedicated business number with green checkmark verification  
**Business Profile:**
- Name: Jodi
- Category: Matchmaking Service
- Description: "AI-powered matchmaking for serious relationships. Private, thoughtful, one great match at a time."
- Website: https://jodi.com
- Support hours: 24/7 (automated) + human escalation

### Integration Points

```
┌─────────────────────────────────────────────────────┐
│                  WhatsApp Business API               │
│         (Meta Cloud API or Twilio Wrapper)          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            FastAPI Webhook Receiver                  │
│   POST /webhooks/whatsapp                           │
│   - Validates signature                             │
│   - Extracts phone + message                        │
│   - Routes to conversation handler                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         Multi-Channel Identity Layer                 │
│   get_user_id_from_channel('whatsapp', phone)       │
│   - Lookup in user_channels table                   │
│   - Create if new, link if existing                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│           Conversation State Controller              │
│   (Shared logic with Telegram)                      │
│   - Load user state from users table                │
│   - Determine next question                         │
│   - Format response for WhatsApp                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         WhatsApp Message Formatter                   │
│   - Converts button arrays to WhatsApp format       │
│   - Handles media differently (image/video)         │
│   - Respects 3-button / 10-list-item limits         │
└─────────────────────────────────────────────────────┘
```

### Database Schema (Already Exists)

**No new tables needed!** Multi-channel architecture already supports WhatsApp:

```sql
-- user_channels table (existing)
INSERT INTO user_channels (user_id, channel_type, channel_identifier, is_verified)
VALUES ('abc123', 'whatsapp', '+971585408825', TRUE);

-- users table (existing)
-- All profile data stored here, channel-agnostic

-- conversation_logs table (existing)
-- Tracks all interactions with channel metadata
```

---

## 🎨 UX Design & Flow Adaptation

### WhatsApp Constraints vs Telegram

| Feature | Telegram | WhatsApp | Adaptation |
|---------|----------|----------|------------|
| **Inline buttons** | Unlimited, multi-column | Max 3 per message | Split into multiple messages or use Lists |
| **Button labels** | 64 chars | 20 chars | Shorten labels |
| **List messages** | Not available | Up to 10 items | Use for multi-option questions |
| **Media captions** | 1024 chars | 1024 chars | Same |
| **Message threading** | Yes (reply markup) | No | Use context in text |
| **Markdown** | Full support | Limited (bold/italic only) | Simplify formatting |
| **Read receipts** | Optional | Always on | Users see "read" status |
| **Typing indicator** | Controllable | Auto (5s max) | Simulate human pacing |

### Flow Adaptations

#### **Multi-Choice Questions (>3 options)**

**Telegram approach:**
```
[ ☪️ Islam ] [ 🕉️ Hinduism ] [ ✝️ Christianity ]
[ ✡️ Judaism ] [ ☬ Sikhism ] [ ☸️ Buddhism ]
[ 🔮 Spiritual ] [ 🚫 Not religious ]
```

**WhatsApp approach (List Message):**
```
What's your religion or faith? 👇

Tap below to choose from 8 options
```
**List button:** `[ Select Religion ]`

**List content:**
```
☪️ Islam
🕉️ Hinduism
✝️ Christianity
✡️ Judaism
☬ Sikhism
☸️ Buddhism
🔮 Spiritual / Other
🚫 Not religious
```

#### **Binary/Ternary Questions (≤3 options)**

**No change needed** — WhatsApp supports up to 3 reply buttons:

```
Do you smoke?

[ Never ] [ Socially ] [ Regularly ]
```

#### **Text Input Questions**

**Telegram:** Uses `force_reply` markup  
**WhatsApp:** No special markup needed (just wait for text reply)

**Approach:**
```
What should I call you?

Just type your first name and send it to me 👇
```

---

## 📱 User Journey (WhatsApp-Specific)

### Entry Points

1. **Direct message to business number**
   - User saves `+971-XX-JODI-XXX` and sends "Hi"
   - Triggers welcome flow

2. **Click-to-WhatsApp link** (primary acquisition)
   - Landing page CTA: `[ Message us on WhatsApp ]`
   - URL: `https://wa.me/971XXXXXXX?text=Hi`
   - Pre-fills "Hi" message, user just hits send

3. **QR Code** (offline marketing)
   - Posters, business cards, events
   - Scans → Opens WhatsApp chat

4. **WhatsApp Business Directory**
   - Organic discovery via WhatsApp search
   - Category: "Dating & Relationships" or "Consulting"

### First-Time User Flow

**Message 1 (Welcome):**
```
Hey! 👋 I'm Jodi.

I help people find real, lasting relationships.
No swiping. No algorithms. Just one great introduction at a time.

Ready to start?

[ Yes, tell me more ] [ Not now ]
```

**If "Yes, tell me more":**
→ Same intro sequence as Telegram (7-message privacy/philosophy intro)

**If "Not now":**
```
No worries! Message me whenever you're ready 😊

I'll be here.
```
*Conversation ends. User can restart anytime by messaging.*

### Returning User Flow (Cross-Channel)

**Scenario:** User started on Telegram, now messages on WhatsApp

**Bot detects:** Phone number matches existing user in `user_channels`

**Message:**
```
Hey {name}! 👋

I see you started with me on Telegram.
You're {completeness}% complete.

Want to pick up where you left off?

[ Yes, continue ] [ Start fresh ]
```

**If "Yes, continue":**
→ Load state from `users` table, resume from last unanswered question

**If "Start fresh":**
→ Confirm: "This will reset your progress. Are you sure?" → Proceed or cancel

---

## 🗂️ Complete Question Flow (WhatsApp Format)

### Phase 1: Top Filters (12 questions)

**F1: Relationship Intent** (3 buttons)
```
What are you looking for?

[ Marriage ] [ Long-term ] [ Either ]
```

**F2: Religion** (List message, 8 options)
```
What's your religion or faith? 👇

[ Select from list ]
```

**F3: Religion Practice** (3 buttons, conditional)
```
How would you describe your practice?

[ Very practicing ] [ Practicing ] [ Cultural ]
```
*Note: "Not very practicing" removed to fit 3-button limit; merged into "Cultural"*

**F4: Partner Religion** (3 buttons + conditional text)
```
Does your partner's religion matter?

[ Must be same ] [ Prefer same ] [ Doesn't matter ]
```
*If "Prefer same": Follow-up text input for exceptions*

**F5: Children Intent** (List message, 5 options)
```
Do you want children in the future? 👇

[ Select option ]
```
List:
```
Definitely yes
Probably yes
Open to it
Probably not
Definitely not
```

**F6: Existing Children** (3 buttons)
```
Do you have children already?

[ No ] [ Yes, with me ] [ Yes, not with me ]
```

**F7: Smoking** (3 buttons)
```
Do you smoke?

[ Never ] [ Socially ] [ Regularly ]
```
*"Quitting" removed to fit limit; users can clarify in conversation*

**F8: Drinking** (3 buttons)
```
Do you drink alcohol?

[ Never ] [ Socially ] [ Prefer not to say ]
```
*"Regularly" removed (covered by "Socially" for matchmaking purposes)*

**F9: Dietary Preferences** (List message, 7 options)
```
Any dietary preferences?

(Shared meals are a big part of life together)

[ Select preference ]
```
List:
```
No restrictions
Vegetarian
Vegan
Halal
Kosher
Jain vegetarian
Other
```

**F10: Marital History** (3 buttons)
```
Have you been married before?

[ Never married ] [ Divorced ] [ Widowed ]
```
*"Separated" merged into "Divorced" for simplicity*

**F11: Timeline** (3 buttons)
```
How soon are you looking to find someone?

[ Ready now ] [ Within a year ] [ Just exploring ]
```
*"1-2 years" merged into "Within a year"*

**F12: Education Preference** (3 buttons)
```
Does your partner's education level matter?

[ Must have degree ] [ Postgrad preferred ] [ Doesn't matter ]
```

---

### Phase 2: Identity (7 questions)

**Transition message:**
```
Those are the big ones ✓

Now a few quick ones about you.
```

**I1: First Name** (text input)
```
What should I call you?

Just type your first name and hit send 👇
```

**I2: Gender** (3 buttons)
```
How do you identify?

[ Man ] [ Woman ] [ Non-binary ]
```

**I3: Orientation** (3 buttons)
```
Who are you looking to meet?

[ Men ] [ Women ] [ Both ]
```

**I4: Date of Birth** (text input)
```
When were you born? (DD/MM/YYYY)

I keep your exact date private — only your age shows to matches.
```

**I5: Country** (List message, 10+ options)
```
Where are you based? 👇

[ Select country ]
```
Top 10:
```
🇮🇳 India
🇦🇪 UAE
🇺🇸 USA
🇬🇧 UK
🇸🇬 Singapore
🇸🇦 Saudi Arabia
🇶🇦 Qatar
🇧🇭 Bahrain
🇰🇼 Kuwait
🇵🇰 Pakistan
+ Other (type it)
```

**I6: City** (dynamic list by country)
```
Which city? 👇

[ Select city ]
```
Example for UAE:
```
Dubai
Abu Dhabi
Sharjah
Ajman
Other (type it)
```

**I7: Ethnicity** (text input)
```
What's your nationality or ethnicity?

e.g. Indian, Pakistani-American, British-Arab...
```

---

### Phase 3: Lifestyle (14 questions)

**Transition:**
```
Almost there, {name} — you're flying through this ✓

A few more about your lifestyle and preferences.
```

**L1: Work Style** (List message, 8 options)
```
What's your work situation? 👇

[ Select option ]
```

**L2: Education Level** (List message, 6 options)
```
Highest education? 👇

[ Select level ]
```

**L3: Income Bracket** (List message, 6 options)
```
Roughly what's your annual income range?

(Completely private — helps with lifestyle compatibility)

[ Select range ]
```

**L4: Living Situation** (3 buttons)
```
Current living situation?

[ Live alone ] [ With roommates ] [ With family ]
```

**L5: Exercise** (3 buttons)
```
How active are you?

[ Very active ] [ Active ] [ Not very active ]
```

**L6: Social Energy** (3 buttons)
```
At a party, you're more likely to...

[ Work the room ] [ Stick with friends ] [ Deep 1-on-1 convo ]
```

**L7: Travel** (3 buttons)
```
How much do you travel?

[ Homebody ] [ Few trips/year ] [ Travel frequently ]
```

**L8: Pets** (3 buttons)
```
Pets?

[ Have pets 🐾 ] [ Want pets ] [ No pets ]
```

**L9: Substance Use** (3 buttons)
```
Any recreational substance use? (Cannabis, etc.)

[ Never ] [ Occasionally ] [ Prefer not to say ]
```

**L10: Height** (List message, 6 options + skip)
```
How tall are you? (Optional) 👇

[ Select height ]
```

**L11: Partner Age Range** (2-step, 3 buttons each)
```
What age range works for you in a partner?

Youngest:

[ 22-25 ] [ 26-29 ] [ 30-33 ]
```
Then:
```
Oldest:

[ 30-33 ] [ 34-37 ] [ 38+ ]
```

**L12: Location Flexibility** (3 buttons)
```
Does your partner need to be in {city}?

[ Same city ] [ Same country ] [ Open to distance ]
```

**L13: Community** (conditional, 3 buttons + text)
```
Does community matter for your match?

[ Must be same ] [ Prefer same ] [ Doesn't matter ]
```
If "Must" or "Prefer":
```
What's your community?

e.g. Brahmin, Patel, Sunni, Rajput...
```

**L14: Family Involvement** (conditional, 3 buttons)
```
Is your family involved in your search?

[ Yes, actively ] [ They know ] [ Keeping private ]
```

---

### Phase 4: Photo + Close (3 messages)

**Transition:**
```
That's all the quick questions done, {name} ✓

One last thing before we switch to conversation mode —
```

**P1: Photo Upload**
```
I need at least one recent photo of you.

It stays private — only shared when I introduce you to a match, with your approval.

Send me a clear photo where your face is visible 📸
```

**After upload:**
```
Great photo ✓ Want to add more?

[ Add another ] [ That's enough ]
```

**P2: Quick Summary**
```
Here's a quick snapshot:

{name}, {age} · {city}, {country}
{religion} ({practice}) · Looking for {intent}
Seeking {orientation} · Age {min}–{max}

If anything looks off, just tell me later and I'll fix it.

[ Looks good ]
```

**P3: The Transition** 🎯
```
You're in, {name} ✓

I now know your basics and filters. That's ~25% of what I need to find someone great.

The quick-tap stuff tells me who to filter OUT.
The conversation tells me who to filter IN.

From now on, I'll ask real questions — the kind a good friend would ask. Answer in your own words, whenever you feel like it.

No rush. The more I understand you, the better your first introduction will be.

Ready?

[ Ask me something ] [ I'll come back later ]
```

---

## 🛠️ Technical Implementation

### WhatsApp Business API Setup

**Step 1: Get Business Number**
- Register with Meta Business Manager
- Request WhatsApp Business API access
- Verify business (expect 1-2 weeks for green checkmark)
- Alternative: Use Twilio's WhatsApp Business API (faster setup, higher cost)

**Step 2: Configure Webhooks**
```python
# FastAPI webhook receiver
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Receives messages from WhatsApp Business API
    """
    # Verify webhook signature (Meta signature validation)
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(await request.body(), signature):
        raise HTTPException(status_code=403)
    
    data = await request.json()
    
    # Extract message details
    if data['entry'][0]['changes'][0]['value'].get('messages'):
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        phone = message['from']  # +971585408825
        msg_type = message['type']  # text, button, list, image, etc.
        
        if msg_type == 'text':
            text = message['text']['body']
            await handle_text_message(phone, text)
        elif msg_type == 'button':
            button_id = message['button']['payload']
            await handle_button_click(phone, button_id)
        elif msg_type == 'list':
            list_id = message['list_reply']['id']
            await handle_list_selection(phone, list_id)
        elif msg_type == 'image':
            image_id = message['image']['id']
            await handle_image_upload(phone, image_id)
    
    return {"status": "ok"}

@app.get("/webhooks/whatsapp")
async def verify_webhook(request: Request):
    """
    Webhook verification (Meta requirement)
    """
    mode = request.query_params.get('hub.mode')
    token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')
    
    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    else:
        raise HTTPException(status_code=403)
```

**Step 3: Message Sending**
```python
import httpx

async def send_whatsapp_message(phone: str, message_data: dict):
    """
    Send message via WhatsApp Business API
    """
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        **message_data
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()

# Example: Send text with buttons
await send_whatsapp_message("+971585408825", {
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {"text": "Do you smoke?"},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": "smoke_never", "title": "Never"}},
                {"type": "reply", "reply": {"id": "smoke_social", "title": "Socially"}},
                {"type": "reply", "reply": {"id": "smoke_regular", "title": "Regularly"}}
            ]
        }
    }
})

# Example: Send list message
await send_whatsapp_message("+971585408825", {
    "type": "interactive",
    "interactive": {
        "type": "list",
        "body": {"text": "What's your religion or faith? 👇"},
        "action": {
            "button": "Select Religion",
            "sections": [
                {
                    "rows": [
                        {"id": "religion_islam", "title": "☪️ Islam"},
                        {"id": "religion_hindu", "title": "🕉️ Hinduism"},
                        {"id": "religion_christian", "title": "✝️ Christianity"},
                        {"id": "religion_jewish", "title": "✡️ Judaism"},
                        {"id": "religion_sikh", "title": "☬ Sikhism"},
                        {"id": "religion_buddhist", "title": "☸️ Buddhism"},
                        {"id": "religion_spiritual", "title": "🔮 Spiritual"},
                        {"id": "religion_none", "title": "🚫 Not religious"}
                    ]
                }
            ]
        }
    }
})
```

### Identity Layer Integration

```python
async def get_or_create_user_from_whatsapp(phone: str) -> str:
    """
    Get existing user_id or create new user for WhatsApp channel
    
    Flow:
    1. Check user_channels for existing WhatsApp link
    2. If not found, check users table for phone number
    3. If found, link WhatsApp channel to existing user
    4. If not found, create new user
    """
    # Check if WhatsApp channel already linked
    existing = db.query(
        "SELECT user_id FROM user_channels WHERE channel_type='whatsapp' AND channel_identifier=%s",
        (phone,)
    ).fetchone()
    
    if existing:
        return existing['user_id']
    
    # Check if phone exists in users table (from other channel)
    user = db.query(
        "SELECT id FROM users WHERE phone=%s",
        (phone,)
    ).fetchone()
    
    if user:
        # Link WhatsApp to existing user
        db.execute(
            "INSERT INTO user_channels (user_id, channel_type, channel_identifier, is_verified) "
            "VALUES (%s, 'whatsapp', %s, TRUE)",
            (user['id'], phone)
        )
        return user['id']
    
    # Create new user
    user_id = generate_user_id()
    db.execute(
        "INSERT INTO users (id, phone, created_at, channel_source) "
        "VALUES (%s, %s, NOW(), 'whatsapp')",
        (user_id, phone)
    )
    
    # Link WhatsApp channel
    db.execute(
        "INSERT INTO user_channels (user_id, channel_type, channel_identifier, is_verified) "
        "VALUES (%s, 'whatsapp', %s, TRUE)",
        (user_id, phone)
    )
    
    return user_id
```

### Conversation State Controller (Shared with Telegram)

```python
async def handle_whatsapp_message(phone: str, message_content: str):
    """
    Main message handler for WhatsApp
    """
    # Get or create user
    user_id = await get_or_create_user_from_whatsapp(phone)
    
    # Load session state
    session = load_or_create_session(user_id, 'whatsapp')
    
    # Determine next action
    next_action = await determine_next_action(session, message_content)
    
    if next_action['type'] == 'button_question':
        # Send WhatsApp button message
        await send_button_question_whatsapp(phone, next_action)
    elif next_action['type'] == 'list_question':
        # Send WhatsApp list message
        await send_list_question_whatsapp(phone, next_action)
    elif next_action['type'] == 'text_question':
        # Send text prompt
        await send_text_question_whatsapp(phone, next_action)
    elif next_action['type'] == 'conversational':
        # LLM-driven conversation
        await send_conversational_message_whatsapp(phone, next_action)
    
    # Log interaction
    log_conversation(user_id, 'whatsapp', message_content, next_action)
```

---

## 📊 Success Metrics & KPIs

### Primary Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Signup conversion** | 70%+ start onboarding after first message | (Users who answer Q1) / (Users who send first message) |
| **Button phase completion** | 65%+ complete all 34 questions | (Users who finish P4) / (Users who start F1) |
| **Photo upload rate** | 80%+ upload at least 1 photo | (Users with photo) / (Users who finish P3) |
| **Cross-channel usage** | 30%+ switch between Telegram/WhatsApp | (Users in both channels) / (Total users) |
| **Response time** | <2 hours median for conversational phase | Time between user message and bot reply |

### Secondary Metrics

- **Channel preference:** % of new users choosing WhatsApp vs Telegram
- **Completion time:** Median time to finish button phase (target: 10-12 min)
- **Drop-off points:** Which questions have highest abandonment
- **Family referrals:** % of users who mention "my mom/dad sent me this"
- **Business verification impact:** Conversion lift after green checkmark approval

---

## 🚀 Go-to-Market & Launch Plan

### Phase 1: Soft Launch (Week 1-2)

**Audience:** Existing Telegram users (cross-channel linking test)

**Goals:**
- Validate WhatsApp integration works
- Test cross-channel state sync
- Identify UX friction points

**Tactics:**
- Send Telegram broadcast: "Now on WhatsApp! Try it: [link]"
- Track: How many switch? Do they resume correctly?

### Phase 2: Private Beta (Week 3-4)

**Audience:** 100 hand-picked users (friends, referrals, warm leads)

**Goals:**
- Get qualitative feedback on WhatsApp UX
- Validate button/list message design
- Test family involvement flows

**Tactics:**
- Personal outreach: "Hey, we're testing WhatsApp — want early access?"
- WhatsApp group: "Jodi Beta Testers" for feedback
- Weekly check-ins: "How's the experience so far?"

### Phase 3: Public Launch (Week 5+)

**Audience:** Open to all via marketing channels

**Goals:**
- Drive 1000+ WhatsApp signups in first month
- Achieve 50% WhatsApp:Telegram ratio
- Collect 5-star reviews on WhatsApp Business directory

**Tactics:**
- **Paid ads:** Instagram/Facebook → WhatsApp click-to-chat
- **Landing page:** Primary CTA = "Message us on WhatsApp"
- **Offline:** QR codes at diaspora events (weddings, cultural festivals)
- **Word of mouth:** "Send this to your single friend" viral mechanic

### Marketing Messaging

**Hook:** "Now on WhatsApp — the app you actually use every day"

**Benefits:**
- ✅ No new app to download
- ✅ Verified business (green checkmark = trust)
- ✅ Privacy you can trust (end-to-end encrypted)
- ✅ Start/stop anytime (conversations, not forms)

**Call-to-action:** `[ Message Jodi on WhatsApp ]`

---

## 🔒 Privacy & Compliance

### GDPR / Data Protection

- **Consent:** First message asks: "By continuing, you agree to our [Privacy Policy]"
- **Right to delete:** Command: "Delete my data" → Immediate purge from all tables
- **Data portability:** Command: "Export my data" → JSON file sent via WhatsApp
- **Opt-out:** Command: "Stop" → Unsubscribes from all messages

### WhatsApp Business Policy Compliance

**Allowed:**
- Onboarding conversations (user-initiated)
- Match introductions (with user consent)
- Profile updates (user-requested)

**Not allowed:**
- Promotional broadcasts (unless user opted in)
- Marketing to non-users
- Sharing user data with third parties

**Message windows:**
- **24-hour window:** Free messages within 24h of user's last message
- **After 24h:** Requires approved message template (e.g., "Your match is ready")

### Security

- **Phone verification:** Auto-verified via WhatsApp (no OTP needed)
- **Webhook signature:** Validate all incoming messages (prevent spoofing)
- **Data encryption:** TLS in transit, encrypted at rest (Supabase default)
- **Access logs:** Track all data access (audit trail)

---

## 🐛 Edge Cases & Error Handling

### User Behaviors

| Scenario | Bot Response |
|----------|-------------|
| Sends text when button/list expected | "Just tap one of the options above 👆" |
| Sends random emoji/sticker during button phase | "😄 Hold that thought — tap a button for now, we'll chat properly soon." |
| Stops mid-flow, returns after 24h | "Hey {name}! Want to pick up where we left off?" + [Resume] button |
| Stops mid-flow, returns after 7 days | "Hey {name}! It's been a while. Let's continue from where we were." + [Resume] |
| Wants to change an answer | "No problem! Which question? I'll ask it again." → Reruns that question |
| Accidentally sends photo too early | "Nice pic! 😊 Hold onto it for now — I'll ask for photos in a bit." |
| Sends voice note | "I can't listen to voice notes yet — can you type it instead?" |
| Asks "How does this work?" mid-flow | Pause flow → Send explainer → Resume |

### Technical Issues

| Issue | Mitigation |
|-------|-----------|
| WhatsApp API downtime | Queue messages, retry with exponential backoff |
| Webhook fails to receive message | Alert monitoring (PagerDuty), manual intervention |
| User's phone number changes | Support flow: "New number? DM us from old number first to verify" |
| Duplicate messages (WhatsApp bug) | Dedupe by message_id within 1-minute window |
| Image upload fails | "Hmm, that didn't work. Try again? Or send a different photo." |

---

## 🔧 Development Checklist

### Backend

- [ ] Set up WhatsApp Business API account (Meta or Twilio)
- [ ] Configure webhook endpoints (`POST /webhooks/whatsapp`, `GET /webhooks/whatsapp`)
- [ ] Implement signature verification
- [ ] Build message parsers (text, button, list, image)
- [ ] Create message senders (text, button, list, media)
- [ ] Integrate with existing identity layer (`get_or_create_user_from_whatsapp`)
- [ ] Test cross-channel state sync (Telegram → WhatsApp, WhatsApp → Telegram)
- [ ] Implement 24-hour message window tracking
- [ ] Set up message templates for >24h scenarios
- [ ] Add conversation logging with WhatsApp metadata

### Frontend (Bot UX)

- [ ] Adapt all 37 questions to WhatsApp format (buttons/lists)
- [ ] Write WhatsApp-specific copy (shorter labels, emojis for clarity)
- [ ] Design list message structures (8-10 items max)
- [ ] Create fallback flows for unsupported media types
- [ ] Implement typing indicators (5s delay before sending)
- [ ] Add read receipt handling (don't overwhelm users)
- [ ] Build cross-channel resume prompts

### Testing

- [ ] Unit tests: Message parsing, button/list generation
- [ ] Integration tests: Webhook → Database → Response
- [ ] E2E tests: Full onboarding flow (button phase + conversational)
- [ ] Cross-channel tests: Start Telegram, continue WhatsApp (and vice versa)
- [ ] Load tests: 1000 concurrent users
- [ ] Error tests: Invalid phone, missing fields, duplicate messages

### DevOps

- [ ] Deploy webhook receiver to production (Fly.io or similar)
- [ ] Configure SSL cert for webhook URL
- [ ] Set up monitoring (Sentry for errors, Datadog for metrics)
- [ ] Create runbooks for common issues (API downtime, webhook failures)
- [ ] Set up alerts (PagerDuty for critical failures)

### Compliance

- [ ] Draft WhatsApp-specific privacy policy addendum
- [ ] Implement "Delete my data" command
- [ ] Implement "Export my data" command
- [ ] Get legal review of message templates
- [ ] Submit message templates for WhatsApp approval (3-5 day turnaround)

---

## 💰 Cost Analysis

### WhatsApp Business API Pricing (Meta Cloud API)

| Message Type | Cost (per message) | Volume (Month 1) | Monthly Cost |
|--------------|-------------------|------------------|--------------|
| **Business-initiated** (first 1000/month) | Free | 1000 | $0 |
| **Business-initiated** (after 1000) | $0.005 - $0.03 (varies by country) | 500 | $2.50 - $15 |
| **User-initiated** (within 24h) | Free | 5000 | $0 |
| **Service conversations** | $0.01 - $0.05 | 2000 | $20 - $100 |
| **TOTAL** | — | — | **$22.50 - $115** |

**Key insight:** Stay within 24-hour windows = near-zero cost (same as Telegram)

### Alternative: Twilio WhatsApp API

- **Higher cost:** $0.005/message minimum (no free tier)
- **Faster setup:** 2-3 days vs 1-2 weeks for Meta verification
- **Month 1 estimate:** ~$150-200

**Recommendation:** Start with Twilio (speed), migrate to Meta Cloud API after verification (cost optimization)

---

## 🎯 Success Criteria (Launch +3 Months)

### Must-Have
- ✅ 1000+ WhatsApp signups
- ✅ 60%+ button-phase completion rate
- ✅ <5% error rate (webhook failures, message delivery)
- ✅ Cross-channel sync works (no data loss when switching)

### Nice-to-Have
- ✅ 50% of signups via WhatsApp (vs Telegram)
- ✅ 30% cross-channel usage
- ✅ Green checkmark verification approved
- ✅ 4.5+ star rating on WhatsApp Business directory

### Red Flags (Pivot Signals)
- ❌ <40% button-phase completion (worse than Telegram)
- ❌ High drop-off at photo upload (privacy concerns?)
- ❌ <20% WhatsApp adoption (users prefer Telegram)
- ❌ Family involvement causing friction (parents messaging bot, confusion)

---

## 📅 Timeline

| Phase | Duration | Key Milestones |
|-------|----------|----------------|
| **Setup** | Week 1 | WhatsApp Business account approved, webhook deployed |
| **Development** | Week 2-3 | Backend integration complete, button/list flows built |
| **Testing** | Week 4 | Cross-channel sync tested, edge cases handled |
| **Soft Launch** | Week 5 | 50 Telegram users test WhatsApp, feedback collected |
| **Private Beta** | Week 6-7 | 100 new users via referrals, UX refinements |
| **Public Launch** | Week 8 | Marketing campaign live, open to all |
| **Optimization** | Week 9-12 | Iterate based on metrics, hit 1000 users |

---

## 🤔 Open Questions for Review

1. **Business verification timing:** Start with Twilio (fast) or wait for Meta green checkmark (trust)?
2. **Photo upload flow:** Should we allow multiple photos at once, or force 1-at-a-time?
3. **Family involvement:** Should we build a "parent mode" (simpler language, more context)?
4. **Pricing disclosure:** Should we mention "free" in marketing, or avoid pricing talk entirely?
5. **Multi-language:** India market needs Hindi/Tamil/Telugu support — Phase 2 or MVP?
6. **Broadcast strategy:** Can we send weekly "check-in" messages, or does that violate WhatsApp policy?
7. **Voice notes:** High demand in Gulf markets — worth building voice-to-text?
8. **Group chats:** Some users want family group chat for match approval — support this?

---

## 📎 Appendices

### A. WhatsApp vs Telegram Feature Comparison

| Feature | WhatsApp | Telegram | Winner |
|---------|----------|----------|--------|
| **Global users** | 2B+ | 900M | WhatsApp |
| **India penetration** | 500M | 55M | WhatsApp |
| **Business features** | Native (verified checkmark) | Third-party bots | WhatsApp |
| **Button flexibility** | 3 max | Unlimited | Telegram |
| **List messages** | Up to 10 items | Not available | WhatsApp |
| **Message formatting** | Limited (bold/italic) | Full markdown | Telegram |
| **Media handling** | Images, videos, docs | Same + stickers, animations | Tie |
| **Read receipts** | Always on | Optional | Telegram (privacy) |
| **Family trust** | High (default comm channel) | Low (perceived as "tech-y") | WhatsApp |
| **API cost** | $0 (within 24h window) | $0 (always free) | Tie |

### B. Sample Message Templates (for >24h scenarios)

**Template 1: Match Ready**
```
Template name: match_ready_notification
Category: ACCOUNT_UPDATE
Language: English

Body:
Hey {{1}}, great news! I found someone I think you'll really like. Reply to see their profile 😊

Variables:
{{1}} = User's first name

Status: PENDING_APPROVAL
```

**Template 2: Profile Incomplete**
```
Template name: profile_reminder
Category: ACCOUNT_UPDATE
Language: English

Body:
Hi {{1}}, you're {{2}}% complete! Finish your profile to see your first match. Reply "continue" to pick up where you left off.

Variables:
{{1}} = User's first name
{{2}} = Completeness percentage

Status: PENDING_APPROVAL
```

### C. References & Resources

- **WhatsApp Business API Docs:** https://developers.facebook.com/docs/whatsapp
- **Meta Cloud API Pricing:** https://developers.facebook.com/docs/whatsapp/pricing
- **Twilio WhatsApp API:** https://www.twilio.com/docs/whatsapp
- **Message Templates Guide:** https://developers.facebook.com/docs/whatsapp/message-templates
- **WhatsApp Business Policy:** https://www.whatsapp.com/legal/business-policy

---

**Status:** Draft for Review  
**Next Steps:**
1. Review with N
2. Address open questions
3. Get Kavi's technical review (backend feasibility)
4. Finalize go-to-market timeline
5. Post to Google Docs for team visibility

---

*Created by Seema · 2026-02-22*
