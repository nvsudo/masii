# Jodi — Telegram Matchmaker Bot 💬

**Project Hub: Vision, Status, and Team Overview**

---

## Vision & Mission

### The Problem
Traditional matchmaking apps (filtering on demographics) fail for diaspora communities.

A 28-year-old NRI in Canberra might be better matched with someone in Sydney (same culture, language, family values) than with someone geographically closer but culturally disconnected. **Boolean filters miss this.**

### The Solution: Conversational Matchmaking
Talk to the bot like you'd talk to a matchmaker auntie who happens to have a database brain.

**No forms. No filters. Just conversation.**

The bot understands context, trade-offs, and what you *mean* — not just what you say. Over multiple sessions, it builds a rich profile and finds matches based on contextual reasoning, not rigid filters.

### Target Market
Gujarati diaspora (initially). Expand to other South Asian communities.

**Why Gujarati?**
- Strong diaspora (Australia, Canada, UK, USA, UAE)
- High cultural preservation values
- Existing community trust via word-of-mouth
- Language as a signal (Gujarati speakers value cultural grounding)

### Success Metric
Matches where context-driven pairing beats pure proximity/demographics.

---

## High-Level Project Details

### Architecture

```
User (Telegram)
    ↓
bot.py (Telegram handlers)
    ↓
conversation.py (multi-session conversation flow)
    ↓
Claude API (conversational understanding + profile extraction)
    ↓
db_postgres.py (Supabase Postgres storage)
    ↓
matching.py (contextual matching engine)
```

### Core Components

#### 1. **Conversation Engine** (`conversation.py`)
- Multi-session intake (4 conversations over time, not 1 form)
- Session 1: Who are you? (demographics, background)
- Session 2: What are you looking for? (preferences)
- Session 3: Deep dive (context, values, trade-offs)
- Session 4: Summary & confirmation
- Claude-powered (uses sonnet/opus for quality)

#### 2. **Database Schema** (`schema.sql`, `db_postgres.py`)
- **users table** — Telegram ID, basic metadata
- **profiles table** — Rich profile with JSONB columns:
  - `demographics` — age, location, caste, language, diet
  - `preferences` — weights for matching factors + context
  - `signals` — extracted insights from conversation (e.g., "values cultural grounding")
  - `conversation_state` — current session, progress, history
  - `conversation_history` — full transcript of all conversations

#### 3. **Matching Engine** (`matching.py`)
- Contextual scoring (not boolean filters)
- Weights and trade-offs:
  - Same location → bonus
  - Different location BUT same caste + language → cultural compensation
  - Immigration complexity → penalty
- Score range: 0–100
- Returns top N matches with reasoning

#### 4. **Data** (`seed_data.py`)
- Test profiles (includes Canberra NRI case)
- Seeded into test database for validation
- Can run locally to verify matching logic

---

## Current Status

### Deployment ✅

- **Hosting:** Fly.io (`jodi-matchmaker` app, Mumbai region)
- **Database:** Supabase Postgres (`herqdldjaxmfusjjpwdg`)
- **Telegram Bot:** Live and accepting users
- **API:** Anthropic Claude (sonnet-4 for conversations)

### Recent Fixes (2026-02-10)

1. ✅ **conversation_history column** — Added JSONB to profiles table
2. ✅ **conversation_state persistence** — Fixed db_postgres.py read/write
3. ✅ **Model name** — Updated to `claude-sonnet-4-20250514` (older model deprecated)
4. ✅ **JSON serialization** — Added datetime helper for API calls
5. ✅ **API signature alignment** — bot.py calls match db_postgres adapter

### Known Limitations (V1)

- ❌ **Payments** — Unlock model designed, not implemented
- ❌ **Identity verification** — Trust-based only (auntie network validation later)
- ❌ **Mutual matches** — Both sides must express interest manually
- ❌ **WhatsApp** — Telegram only for now
- ❌ **Photo sharing** — Text-based intake only

---

## Team Updates

### Recent Work (2026-02-10)

#### Blitz 🚀 (Code & Ship)
- Fixed API signature mismatches in bot.py ↔ db_postgres
- Debugged datetime serialization issues
- **Status:** Feature-ready, bugs squashed

#### Kavi 🔧 (Systems & Shipping)
- Fixed conversation_state persistence in db_postgres.py
- Database debugging + schema validation
- Deployed to Fly.io with Anthropic key secrets
- **Status:** Infra stable, ready for user load testing

#### Shreya 🎯 (Product & GTM)
- **✅ DELIVERED:** Conversational State Management Spec
  - 1-page spec (all 5 sections: API, schema, prompts, acceptance criteria, 2-week rollout)
  - Google Doc created and shared with nikunj.vora@gmail.com
  - Link: https://docs.google.com/document/d/1X8qztj_bZGRS4Mp5HWkbIoO8ZlN68Abj/edit
  - **Status:** Ready for Blitz implementation

#### Greg 📝 (Content & Brand)
- Feedback: Current messaging needs refinement for diaspora audience
- **To-do:** Review onboarding copy, suggest warm/conversational tweaks

#### N 🎯 (Product Lead)
- Tested bot end-to-end during first user session (2026-02-10)
- Feedback: Flow is too casual/open-ended
- **Product feedback:**
  - Add progress indicators ("3 more things needed")
  - Gap-filling nudges ("I still need your X")
  - Gating: Don't match until profile is 80%+ complete
  - Optional: Tone slider (casual ↔ structured)

### Next Steps

#### Shreya (Priority: HIGH)
- [ ] Create Conversational State Management Spec (1 page)
- [ ] Design controller API (completion map, confidence scoring)
- [ ] JSON schema + system prompt template
- [ ] 2-week rollout plan
- [ ] Share Google Doc (nikunj.vora@gmail.com)

#### Blitz (After Shreya spec)
- [ ] Implement Intake Controller (completion map + next-best-question logic)
- [ ] Enforce model usage: opus/sonnet/gpt-5 only (no cheaper)
- [ ] Integration tests for profile completeness gating

#### Kavi (Ongoing)
- [ ] Monitor Fly.io app (logs, performance)
- [ ] Database queries for analytics (user onboarding funnel)
- [ ] Prepare for user load testing

#### Greg
- [ ] Review onboarding copy
- [ ] Suggest diaspora-friendly messaging tweaks
- [ ] Create brand voice guide for bot responses

---

## Documentation

### Local Files
- **`/matchmaker/jodi/README.md`** — Product overview (this content)
- **`/matchmaker/jodi/docs/ONBOARDING_CURRENT_STATE.md`** — User flow diagram
- **`/matchmaker/jodi/docs/ONBOARDING_TECHNICAL.md`** — Technical details (DB schema, API signatures)
- **`/matchmaker/ARCHITECTURE.md`** — System-wide architecture
- **`/matchmaker/QUICKSTART.md`** — Setup & deployment guide

### Shared Google Docs
- **Jodi - User Onboarding Current State**
  - URL: https://docs.google.com/document/d/1jw89vXOHNlQAMD62MCJXEZjwzHfUdEF7f8Yk9xMVPGQ/edit
  - Shared with: nikunj.vora@gmail.com
  - Purpose: Visual onboarding flow (flowchart + decision points)

### Key Code Files
- **`bot.py`** — Telegram bot entry point (handlers for /start, /help, text messages)
- **`conversation.py`** — **THE PRODUCT** (conversation quality, multi-turn logic)
- **`matching.py`** — Contextual matching engine (scoring, trade-offs)
- **`db_postgres.py`** — Supabase Postgres adapter (profile storage, retrieval)
- **`schema.sql`** — Database schema
- **`seed_data.py`** — Test data generator

---

## Environment & Secrets

### Local Development
```bash
cd /matchmaker/jodi

# Copy .env template
cp .env.example .env

# Edit .env with:
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
ANTHROPIC_API_KEY=<your_anthropic_api_key>
DATABASE_URL=postgresql://<user>:<pass>@<host>/<db>
```

### Production (Fly.io)
```bash
# Secrets stored in Fly.io app
fly secrets set TELEGRAM_BOT_TOKEN=<token>
fly secrets set ANTHROPIC_API_KEY=<key>
fly secrets set DATABASE_URL=<postgres_url>
```

**Current Fly.io app:** `jodi-matchmaker`  
**Database:** Supabase Postgres (`herqdldjaxmfusjjpwdg`)

---

## Getting Started

### 1. Clone & Setup
```bash
cd /matchmaker/jodi
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Locally
```bash
python bot.py
```

### 4. Test with Seed Data
```bash
# Create test database with profiles
python seed_data.py

# Switch .env to use test database:
# DATABASE_PATH=jodi_test.db
```

### 5. Deploy to Fly.io
```bash
fly deploy
```

---

## 🆕 CRITICAL UPDATE: New Data Capture Framework (2026-02-11)

**Status:** N has provided comprehensive data capture framework — **this supersedes Xing's earlier tier spec.**

**Document:** `/Users/nikunjvora/clawd/JODI/Matchmaking_Data_Capture_Framework_v1.docx`

**Key Changes:**
- **100+ data points** (vs. ~30 in Xing's spec)
- **Explicit vs Inferred architecture** — 40% explicit, 60% AI-inferred from conversation
- **Hard filters vs signals** — Hard filters (age, location, religion) = Postgres indexed columns; signals (personality, values) = JSONB
- **4-tier progressive model:**
  - Tier 1: THE BASICS (hard filters, identity) — 5-7 min, required before profile creation
  - Tier 2: READY (lifestyle, values, preferences) — matching activates at 70%+ completion
  - Tier 3: DEEP PROFILE (psychological signals, family depth) — priority matching
  - Tier 4: CALIBRATED (post-match learning, revealed preferences)
- **Minimum Viable Profile (MVP) for matching:**
  - 100% Tier 1 + 70% Tier 2 + at least 2 open-ended responses + 45% total completeness + 2+ sessions
- **Priority scoring:** Higher completeness = earlier/better matches
- **Keeper.ai lesson:** Don't rush users into matching with incomplete profiles

**Action Items:**
- **Kavi:** Review framework, design DB schema (hard filters as columns, signals as JSONB), plan implementation architecture
- **Xing:** Study framework deeply, understand why it's more comprehensive than your earlier spec, prepare to support implementation
- **Blitz:** (On hold until Kavi + Xing review) — will implement based on finalized architecture

**Timeline:** Immediate priority. This is the new foundation for JODI's data model.

---

## Open Questions & Decisions

### 1. Profile Completeness Gating ✅ RESOLVED
- **Current:** No gating. Bot suggests matches even if profile is partial.
- **N's feedback:** Don't match until profile is 80%+ complete.
- **Resolution:** New framework defines MVP activation rules (see above). Matching activates only when Tier 2 reaches 70%+ and overall completeness ≥ 45%.

### 2. Conversation Tone Control
- **Current:** Fixed (casual, open-ended)
- **N's suggestion:** Optional tone slider (casual ↔ structured)
- **Decision pending:** Is this MVP or post-MVP?

### 3. Identity Verification
- **Current:** Trust-based (no verification)
- **Future:** Auntie network validation (mutual vouching) or government ID check
- **For V1:** Accept trust-based with community moderation

### 4. Expansion Beyond Gujarati
- **Current:** Gujarati only
- **Plan:** Clone for other communities (Marathi, Punjabi, etc.)
- **Timeline:** Post-MVP (after Gujarati validation)

---

## Success Metrics (Alpha/Beta)

1. **Adoption:** 100 active users within 3 months
2. **Engagement:** 50%+ users complete full 4-session intake
3. **Matching:** 30%+ of matches result in conversation between users
4. **Satisfaction:** 4.0+ rating (Telegram reviews)
5. **Retention:** 25%+ weekly active users (DAU/MAU ratio)

---

## Resources & Links

| Resource | Link | Owner |
|----------|------|-------|
| Code repo | `/matchmaker/jodi/` | Blitz |
| Telegram bot | @jodi-matchmaker-bot | N |
| Fly.io app | jodi-matchmaker | Kavi |
| Database | Supabase (herqdldjaxmfusjjpwdg) | Kavi |
| Google Doc (onboarding) | [Link](https://docs.google.com/document/d/1jw89vXOHNlQAMD62MCJXEZjwzHfUdEF7f8Yk9xMVPGQ/edit) | Shreya |
| Anthropic API key | Fly.io secrets | Kavi |

---

## Notes for Agents

### Kavi 🔧
- **Role:** Infra owner. Monitor Fly.io app, database health, secrets.
- **Know:** Postgres schema, Supabase dashboard, Fly.io CLI
- **Deliverables:** Deployment readiness, database optimization, uptime monitoring

### Shreya 🎯
- **Role:** Product owner. Define completeness gating, conversation specs.
- **Know:** User onboarding flow, product requirements, testing criteria
- **Action:** Produce State Management Spec (HIGH priority, end of week)

### Blitz ⚡
- **Role:** Ship engineer. Implement features, fix bugs, integrate Shreya's spec.
- **Know:** bot.py, conversation.py, integration points
- **Upcoming:** Implement completeness gating after spec is ready

### Greg 📝
- **Role:** Brand voice. Ensure bot tone matches diaspora audience.
- **Know:** Community context, messaging tone
- **Action:** Review onboarding copy, suggest warmth tweaks

### N 🎯
- **Role:** Product lead. Make decisions, test end-to-end, set priorities.
- **Know:** What good matchmaking feels like
- **Feedback:** Currently too casual; add progress indicators and nudges

---

**Project Lead:** N  
**Tech Lead:** Kavi  
**Product Lead:** Shreya  
**Shipping:** Blitz  
**Content:** Greg  

**Created:** 2026-02-11  
**Last Updated:** 2026-02-11 10:05 GMT+4

*Share this with your team: `/JODI_PROJECT.md`*
