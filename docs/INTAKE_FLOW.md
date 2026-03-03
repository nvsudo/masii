# Masii — Unified Intake Flow

**Last updated:** 2026-03-03
**Status:** v2 — Revised (Masii brand, all-Indians positioning)

---

## Overview

Intake is how people enter Masii. Three channels, one profile. The experience differs by channel, but the data collected is the same and the profile they build is unified.

**Primary**: WhatsApp (not set up yet — design for it, ship Telegram for now)
**Secondary**: Web form (built, needs deployment + DB sync)
**Tertiary**: Telegram (current, becomes fallback)

---

## Core Principle: Progressive Disclosure

**Don't ask 77 questions.** Not on any channel.

The current Telegram bot asks 77 questions in sequence. That's an interrogation, not a conversation. The unified intake reverses this:

1. **Get to matching fast** — minimum viable profile in 5-7 minutes
2. **Deepen over time** — Masii asks follow-up questions after each match interaction
3. **Infer what you can** — 60% of signals should be AI-inferred from conversation and behavior

### Tier System (Unchanged)

| Tier | What | When | Matching Impact |
|------|------|------|-----------------|
| T1: Basics | Hard filters — gender, age, location, religion, marital status | Required before profile creation | Must be 100% |
| T2: Ready | Lifestyle, values, preferences — diet, education, family | Matching activates at 70% | Scored matching begins |
| T3: Deep | Personality, communication style, attachment, dealbreakers | Optional, improves match quality | Priority in queue |
| T4: Calibrated | Post-match learning — revealed preferences, feedback | Passive, from match interactions | Algorithm improves |

### Minimum Viable Profile (MVP)
- 100% Tier 1
- 70% Tier 2
- At least 2 open-ended responses
- 45% total completeness
- At least 2 sessions (proves commitment)

---

## Channel-Specific Flows

### WhatsApp (Primary)

**Why WhatsApp:**
- 500M+ users in India. It's the default communication channel.
- Families already use WhatsApp groups. Cultural fit.
- Business API supports buttons, lists, media.
- Phone number = identity (perfect for cross-channel linking).

**Flow:**

```
User sends message to Masii's WhatsApp number
(from website CTA, Instagram bio, or word of mouth)
    │
    ▼
WELCOME MESSAGE
    "Hey! I'm Masii, your AI matchmaker.
     I help Indians everywhere find their
     person — no swiping, no browsing,
     just thoughtful matching.

     Ready to get started?
     [Yes, let's go]  [Tell me more first]"
    │
    ▼
ENTRY GATE
    "Quick question first —
     Are you filling this for yourself
     or someone else?

     [For myself]
     [For a family member or friend]"
    │
    ├─ IF PROXY:
    │   "How are you connected to them?"
    │   [Parent] [Sibling] [Friend] [Relative]
    │
    │   "Do they know you're doing this?"
    │   [Yes, they asked me to]
    │   [Yes, they're okay with it]
    │   [Not yet, I'll tell them]
    │
    │   IF no consent → "No worries. You can fill
    │   everything out. We won't start matching
    │   until they say yes."
    │
    ▼
RETURNING USER CHECK
    "Have you started a profile with
     Masii before?

     [I'm new]
     [I've been here before]"
    │
    ├─ IF RETURNING:
    │   "What's your phone number?"
    │   → Lookup users.phone
    │   → IF FOUND: "Welcome back! You're [X]%
    │     done. Let's pick up where we left off."
    │   → IF NOT FOUND: "Hmm, I can't find that
    │     number. Let's start fresh — it's quick."
    │
    ▼
TIER 1: THE BASICS (5-7 minutes)
    Masii asks these conversationally:

    1. Gender → Button: [Male] [Female] [Non-binary]
    2. Name → Text input
    3. Date of birth → Text (validates 18-80)
    4. Where are you based? → Button: [Country list]
       → IF NRI: City? → Text
       → IF India: State + City → Buttons + Text
    5. Religion → Button: [Hindu] [Muslim] [Christian] [Sikh] [Jain] [Buddhist] [Other] [None]
    6. Marital status → Button: [Never married] [Divorced] [Widowed] [Separated]
       → IF not "Never married": Children from previous? → [Yes] [No]
    7. Looking for → Button: [Male] [Female]

    "Great! That's the basics. I already have
     enough to start looking for you. But the
     more I know, the better the match.

     Want to keep going? It takes about
     5 more minutes.

     [Keep going]  [That's enough for now]"
    │
    ├─ IF "enough for now":
    │   Save as T1 complete. Queue for matching
    │   with T1-only data. Masii follows up in
    │   24 hours to continue.
    │
    ▼
TIER 2: GETTING TO KNOW YOU (5-8 minutes)
    8. Education → Button: [options]
    9. Career field → Button: [options]
    10. Diet → Button: [Veg] [Non-veg] [Vegan] [Jain] [Flexible]
    11. Smoking → Button: [Never] [Social] [Regular]
    12. Drinking → Button: [Never] [Social] [Regular]
    13. Family type → Button: [Nuclear] [Joint] [Extended]
    14. Mother tongue → Button: [Gujarati] [Hindi] [Tamil] [etc.]
    15. Want kids? → Button: [Yes] [No] [Already have] [Open]
    16. What matters most in a partner?
        → Text (open-ended — this is gold for AI inference)
    17. Anything that's a dealbreaker?
        → Text (open-ended)

    "You're 70% there! That's enough for me to
     start finding quality matches.

     I'll message you when I find someone.
     In the meantime — want to add a photo?
     It's optional but matches with photos
     get 3x more responses.

     [Add photo]  [Maybe later]"
    │
    ▼
PROFILE SAVED. MATCHING ACTIVATED.
Masii sends first match when available.

TIER 3 happens organically:
    - After first match: "Before I show you the next one,
      can I ask a couple more questions?"
    - After a date: "How was it? What did you like?"
    - Monthly check-in: "Anything changed? New city? New priorities?"
```

**WhatsApp-Specific Constraints:**
- Max 3 buttons per message (WhatsApp API limit)
- Use List messages for >3 options (up to 10 items)
- Keep messages short — WhatsApp = quick reads
- Use emojis sparingly but naturally
- Voice messages possible for T3 deep profiling (future)

---

### Web Form (Secondary)

**Purpose:** For people who prefer filling out a form over chatting. Also useful for proxy submissions (parents filling for children).

**Design:**
- Clean, minimal form (Polsia-inspired)
- Progressive: shows one section at a time
- Progress bar at top
- Save & resume (via phone number or email)
- Same questions as WhatsApp, structured as form fields

**Flow:**

```
Website → "Create your profile" CTA
    │
    ▼
ENTRY PAGE
    "Are you creating this profile for
     yourself or someone else?"
    ○ For myself
    ○ For a family member or friend
    │
    ├─ IF PROXY: relationship + consent form
    │
    ▼
PHONE / EMAIL
    "Enter your phone number or email.
     We'll use this to save your progress
     and send you matches."
    │
    → Check if returning user
    → IF YES: load existing data, show summary
    → IF NO: proceed to form
    │
    ▼
SECTION 1: THE BASICS
    [Gender] [Name] [DOB] [Location]
    [Religion] [Marital status]
    [Looking for]

    → Progress: 30%
    → [Save & Continue Later] always visible
    │
    ▼
SECTION 2: LIFESTYLE & PREFERENCES
    [Education] [Career] [Diet]
    [Smoking] [Drinking] [Family type]
    [Mother tongue] [Children intent]

    → Progress: 60%
    │
    ▼
SECTION 3: WHAT MATTERS
    [Open-ended: What matters most in a partner?]
    [Open-ended: Dealbreakers?]
    [Photo upload (optional)]

    → Progress: 85%
    │
    ▼
REVIEW & SUBMIT
    Summary of all answers
    [Edit] buttons per section
    [Submit profile]
    │
    ▼
CONFIRMATION
    "Your profile is live! Masii is looking
     for your match.

     We'll message you on WhatsApp when
     we find someone.

     Want to improve your match quality?
     [Continue on WhatsApp with Masii]
     → Deep link to WhatsApp bot"
```

**Web Form connects to same database:**
- Phone = identity key (same as WhatsApp/Telegram)
- Answers sync to `users` + `user_preferences` + `user_signals`
- Session state stored in `sessions` table (channel_type = 'web')
- If user later messages on WhatsApp, Masii sees their web profile

---

### Telegram (Fallback)

Telegram keeps the existing 77-question flow but with the new entry gate (self/proxy + returning user check). It becomes the "power user" channel — people who want the full deep conversation.

**Changes from current:**
1. Add entry gate (same as WhatsApp)
2. Add "save & resume" with phone number
3. Progressive: stop at T2 (70%) and say "that's enough to start"
4. T3 questions become optional follow-ups, not mandatory sequence

---

## Data Architecture: One Profile, Three Channels

```
┌───────────────────────────────────────────────┐
│                   SUPABASE                     │
│                                                │
│  users (canonical profile)                     │
│  ├── phone (UNIQUE) ← universal identity       │
│  ├── email (UNIQUE)                            │
│  ├── Tier 1 fields (hard filters)              │
│  ├── Tier 2 fields (lifestyle)                 │
│  ├── completeness_score                        │
│  ├── tier_level (1-4)                          │
│  ├── profile_active                            │
│  └── preferred_channel                         │
│                                                │
│  user_channels (identity mapping)              │
│  ├── user_id → users.id                        │
│  ├── channel_type (telegram/whatsapp/web)      │
│  ├── channel_identifier (chat_id/phone/token)  │
│  └── linked_at                                 │
│                                                │
│  sessions (per-channel ephemeral state)        │
│  ├── user_id → users.id                        │
│  ├── channel_type                              │
│  ├── current_question                          │
│  ├── answers (JSONB)                           │
│  ├── asked_questions                           │
│  └── expires_at (7 days)                       │
│                                                │
│  user_signals (JSONB — deep profile data)      │
│  ├── lifestyle, values, personality            │
│  └── media_signals, match_learnings            │
│                                                │
│  user_preferences (partner requirements)       │
│  ├── pref_age_range, pref_height, etc.         │
│  └── dealbreaker flags                         │
│                                                │
│  matches (match records)                       │
│  ├── user_a_id, user_b_id                      │
│  ├── match_score, match_explanation            │
│  ├── opt_in_a, opt_in_b                        │
│  └── feedback fields                           │
└───────────────────────────────────────────────┘

CROSS-CHANNEL FLOW:
  Web form (phone: +91-98765-43210)
      → Creates users row + user_channels(web)
      → Saves T1 + T2 answers

  User messages WhatsApp bot
      → Bot asks phone number
      → Finds existing user by phone
      → Links user_channels(whatsapp)
      → Loads existing profile
      → "Welcome back! I see you already filled
         out the basics. Let me ask a few more
         to find you better matches."
```

---

## Intake Questions: Unified Set

### Reduced from 77 to ~25 (with optional deep dive)

The current 77-question flow is too long. The unified intake reduces the mandatory questions and makes the rest optional/progressive.

**Tier 1: Required (8 questions, 5-7 min)**
1. Gender
2. Name
3. Date of birth
4. Location (country → city)
5. Religion
6. Marital status (+ children if applicable)
7. Looking for (gender)
8. Phone number (for identity)

**Tier 2: Recommended (9 questions, 5-8 min)**
9. Education level
10. Career field
11. Diet preference
12. Smoking habits
13. Drinking habits
14. Family type
15. Mother tongue
16. Children intent
17. What matters most in a partner? (open-ended)

**Tier 2b: Important (4 questions, 3 min)**
18. Caste/community (if applicable)
19. Relocation willingness
20. Partner age preference
21. Dealbreakers (open-ended)

**Tier 3: Deep (asked progressively, over multiple sessions)**
22. Religious practice level
23. Income range
24. Family values
25. Attachment style
26. Conflict resolution style
27. Emotional availability
28. Love language
29. Long-term goals
30. Partner education/income preferences
... (remaining questions from current 77, asked as follow-ups)

---

## Masii's Intake Personality

### Voice Rules (WhatsApp/Telegram)

```
DO:
- Warm, encouraging, slightly playful
- Use simple language (no jargon)
- Acknowledge sensitive questions before asking
- Celebrate milestones ("You're halfway there!")
- Reference cultural context naturally
- Short messages (WhatsApp = quick reads)

DON'T:
- Sound like a form ("Question 14 of 77")
- Use corporate language ("Please provide your...")
- Rush through sensitive topics
- Ask back-to-back questions without breathing room
- Use English words when Hinglish is more natural

EXAMPLES:
  Bad:  "What is your dietary preference?"
  Good: "Veg or non-veg? (No judgment either way!)"

  Bad:  "Please select your marital status."
  Good: "Have you been married before?"

  Bad:  "What is your annual income range?"
  Good: "This next one's about finances — totally
         optional and stays private. What's your
         rough income range?"
```

### Section Transitions

```
After T1 basics:
  "Okay, I have the essentials. Already thinking
   about who might be a good fit for you.

   Want to help me narrow it down? A few more
   questions about your lifestyle — takes about
   5 minutes."

After T2 lifestyle:
  "This is great. I have enough to start
   matching you with real people.

   I'll message you when I find someone
   worth your time. No spam, just quality."

Before sensitive questions (income, caste):
  "Quick heads up — the next question is
   personal. You can always skip it. Your
   answer stays private unless you choose
   to share it."

After profile complete:
  "You're all set! Your profile is live.

   I'm already looking through the community
   for your match. I'll reach out when I
   find someone special.

   One last thing — want to add a photo?
   Profiles with photos get 3x more responses."
```

---

## Proxy Flow (Parents/Family)

Critical for Indian context. Many parents fill profiles for their children.

```
PROXY IDENTIFIED
    │
    "Who are you filling this for?"
    → Captures proxy name + relationship
    │
    "Do they know about this?"
    [Yes, they asked me to]     → Full access, matching active
    [Yes, they're okay with it] → Full access, matching active
    [Not yet]                   → Can fill form, matching paused
    │
    IF matching paused:
    "No problem! Fill everything out and we'll
     save it. When they're ready, they can
     message us on WhatsApp and we'll activate
     their profile. Just have them say
     'I'm [Name], my [parent/sibling] created
     my profile.'"
    │
    THROUGHOUT PROXY FLOW:
    - "What is THEIR [field]?" (not "your")
    - "How would THEY describe themselves?"
    - "What are THEY looking for?"
    │
    CONSENT ACTIVATION:
    - Candidate messages Masii's WhatsApp
    - Verifies identity (name + phone)
    - Reviews profile summary
    - "Does this look right?" → Edit opportunity
    - "Activate matching?" → [Yes] → Matching begins
```

---

## Analytics: Intake Funnel

Track these to optimize:

```
Funnel Stage                    Target
─────────────────────────────── ──────
Website visit                   100%
Click "Start on WhatsApp"       40%
Send first message              30%
Complete T1 (basics)            20%
Complete T2 (lifestyle)         15%
Profile activated for matching  12%
First match received            10%
First mutual opt-in             5%
```

Key drop-off points to watch:
- Website → WhatsApp click (is the CTA compelling?)
- First message → T1 complete (is the intro too long?)
- T1 → T2 (is the break point clear? "Keep going" vs "that's enough")
- Profile → First match (how long do they wait?)
