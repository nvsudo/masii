# JODI — Diaspora Matchmaking Platform

**Co-founder:** Seema  
**Status:** Schema deployed, onboarding flow ready  
**GitHub:** https://github.com/nvsudo/jodi

---

## What is Jodi?

AI-powered matchmaking for the Indian diaspora. Tier-based onboarding (T1 → T2 → T3 → T4) with 100+ data point framework for intelligent matching.

---

## Project Structure

```
jodi/
├── backend/              # Bot & orchestration (Python + Telegram)
│   ├── bot.py           # Main bot
│   ├── onboarding/      # Tier-based flow
│   └── matching/        # Matching logic (Phase 2)
│
├── webform-intake/       # Web intake form (Phase 2)
│   └── [Next.js app]
│
├── docs/                 # Product docs & tracking
│   ├── PRODUCT_TRACKER.md
│   ├── ROADMAP_SUMMARY.md
│   └── SCHEMA_VERIFICATION_REPORT.md
│
└── README.md (this file)
```

---

## Database

**Supabase:**
- **Project ID:** herqdldjaxmfusjjpwdg
- **Region:** AP South 1 (Mumbai)
- **Schema:** 11 tables (profiles, matches, user_preferences, user_signals, conversation_logs, photos, interactions, match_feedback, tier_progress, profile_readiness, users)

**Connection:**
```
Project ID: herqdldjaxmfusjjpwdg
Database URL: postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
```

---

## Quick Start

### Run Bot Locally
```bash
cd backend/
python3 bot.py
```

### Deploy to Fly.io
```bash
cd backend/
fly deploy
```

---

## Status

**Completed:**
- ✅ Database schema (100+ data points)
- ✅ Onboarding flow (T1 → T2 → T3 → T4)
- ✅ Telegram bot integration
- ✅ Out-of-order capture logic

**Next:**
- [ ] Matching algorithm (Phase 2)
- [ ] Web intake form (Phase 2)
- [ ] Photo upload
- [ ] WhatsApp channel

---

## Team

- **Seema:** Co-founder, product owner
- **Kavi:** Backend, deployment
- **Blitz:** Bot logic, orchestration

---

## Run Log

All changes and decisions are logged as single-line entries in [`ops/run-log.md`](ops/run-log.md). Every code change or product decision made during a session gets a dated one-liner there.

---

**Let's ship.** 🚀
