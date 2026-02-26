# JODI Improvements Backlog

**Purpose:** Track incremental improvements and polish items for JODI. No immediate execution — prioritize and batch later.

**Status:** Parked for post-MVP

---

## Backlog

### Infrastructure & Ops

**1. Schema Fix: Add `full_name` column to users table**
- **Issue:** Code tries to write `full_name` but column doesn't exist in database
- **Impact:** Extraction fails with `column "full_name" of relation "users" does not exist`
- **Fix:** Add migration: `ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);`
- **Priority:** HIGH (blocking data capture)
- **Discovered:** 2026-02-12 (via logging)

---

### User Experience & Flow

**1. Interactive button-based onboarding (Tier 1)** ⭐
- **Goal:** Use Telegram inline buttons for fast, tap-friendly data collection
- **What works:** Conditional flows ✅, Dynamic invocation ✅, Hybrid button+text ✅
- **What doesn't:** Native date pickers ❌, Native multi-select ❌ (but can fake both)
- **Recommended:** Buttons for structured (gender, religion, yes/no), text for open-ended (name, city if "Other")
- **Benefits:** 10x faster (tap vs type), cleaner data (no typos), higher engagement, lower drop-off
- **Example flow:** 13 questions in ~60 seconds (vs 5-7 minutes typing)
- **Design:** See `/JODI/Telegram_Interactive_Onboarding_Options.md`
- **Priority:** HIGH (major UX win, reduces friction)
- **Discovered:** 2026-02-12

**2. Email intake option for premium tier (future)**
- **Idea:** One daily email vs real-time chat for "executive matchmaking"
- **Target:** Older demographics (40+), premium pricing tier
- **Benefits:** More thoughtful responses, professional tone accepted, can send examples/guides
- **Trade-offs:** Higher cost (~2x tokens), feels less intimate, higher drop-off risk
- **Analysis:** See `/JODI/Email_vs_Chat_Intake_Analysis.md`
- **Priority:** LOW (post-MVP, premium feature)
- **Discovered:** 2026-02-12

---

### Data & Matching

*(No items yet)*

---

### Performance & Scale

*(No items yet)*

---

### Content & Messaging

*(No items yet)*

---

## Completed / Shipped

*(Items move here once implemented)*

---

**Last Updated:** 2026-02-12  
**Maintained By:** A
