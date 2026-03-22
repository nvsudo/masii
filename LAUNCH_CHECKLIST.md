# masii Launch Checklist — Current Status

**Last Updated:** 2026-03-22 19:12 IST  
**Focus:** Web + Email only (Telegram bot @masiiapp_bot paused for later)

---

## 🔴 CRITICAL BLOCKER

### Web Form Backend — NOT WIRED

**Problem:** `form.js` submits to `https://masii-bot.fly.dev/api/intake` — **this app doesn't exist.**

**Current Fly Apps:**
| App | Status | Last Deploy | Purpose |
|-----|--------|-------------|---------|
| `jodi-matchmaker` | ✅ Running | Mar 6 | Telegram bot (webhook mode) |
| `jodi-bot-staging` | ✅ Running | Mar 8 | Staging |
| `haystack-email-poller` | ✅ Running | Mar 14 | Ignition Club |

**`jodi-matchmaker` health:** Returns `{"status": "ok", "service": "jodi-telegram-bot"}` — it's a Telegram bot, not a web API.

**Fix Required:**
- [ ] **Option A:** Deploy new `masii-bot` Fly app with `/api/intake` endpoint
- [ ] **Option B:** Add `/api/intake` route to existing `jodi-matchmaker`
- [ ] Update `form.js` API_BASE if using different URL

---

## ✅ DONE

### Frontend (Cloudflare Pages)
- [x] Domain: masii.co configured
- [x] Homepage: Live with "60+ questions" pitch
- [x] Form Engine: V3 with 81 questions, YAML-driven
- [x] Auth: Supabase OTP (email-based, no passwords)
- [x] Progress Save: LocalStorage + cloud sync
- [x] Pricing Page: ₹151/intro + "90% free" model
- [x] Blog: 22 SEO posts written
- [x] Responsive: Mobile-first design

### Database (Supabase)
- [x] Project: herqdldjaxmfusjjpwdg (Mumbai)
- [x] Schema: 11 tables deployed
- [x] Auth: Email OTP enabled

### Git
- [x] Repo synced with origin/main
- [x] Marketing files committed (2026-03-22)

---

## 🟡 NEEDS VERIFICATION

### Supabase Auth Config
- [ ] Site URL set to `https://masii.co`
- [ ] Redirect URLs include `https://masii.co/onboarding.html`
- [ ] Email templates customized (currently default)

### Form Submission Loop
- [ ] Deploy intake API endpoint
- [ ] Test form → Supabase data flow
- [ ] Verify phone number capture works

---

## 🚫 PAUSED (Not Current Focus)

### Telegram Bot (@masiiapp_bot)
- Status: Bot exists but **not in active use**
- Plan: Conversational hybrid for later phase
- Current: Web + Email only

### WhatsApp Channel
- Status: "Coming soon" on landing page
- Timeline: After web flow is validated

---

## 📋 IMMEDIATE ACTIONS

### To Ship This Week:
1. ~~**[BLOCKER]** Deploy `/api/intake` endpoint~~ ✅ DONE (2026-03-22)
2. **[TEST]** End-to-end form submission ✅ Verified — data lands in Supabase
3. **[BUILD]** Orchestrator: process `form_submissions` → `users`/`preferences` tables
4. **[OPTIONAL]** Customize email templates

---

## 🏗️ ARCHITECTURE: Cross-Device Resume & Edit Profile

**Problem:** Current localStorage approach is device-bound. User starts on phone, continues on laptop → no progress.

### Recommended: Server-Side Drafts

**Schema change to `form_submissions`:**
```sql
ALTER TABLE form_submissions ADD COLUMN user_id UUID;        -- Supabase auth ID
ALTER TABLE form_submissions ADD COLUMN current_question TEXT; -- Resume point
ALTER TABLE form_submissions ADD COLUMN status TEXT DEFAULT 'submitted'; 
-- status: 'draft' | 'submitted' | 'processed'
```

**New endpoints needed:**
- `POST /api/draft` — Save progress (called every section)
- `GET /api/draft` — Load existing draft for user_id
- `PATCH /api/intake` — Update existing submission (edit profile)

**Flow:**
1. User authenticates → get `user_id`
2. Check for existing draft (`status='draft'`) → resume or start fresh
3. Save progress server-side every section completed
4. Final submit → `status='submitted'`
5. Orchestrator processes → `status='processed'`
6. Returning user with `status='processed'` → "Edit Profile" mode

**localStorage role:** Offline cache only. Server is source of truth.

### Implementation Phases

| Phase | Scope | Effort |
|-------|-------|--------|
| **Phase 1** | Add `user_id`, `status` columns. Upsert by user_id (no duplicates). | 2 hrs |
| **Phase 2** | Draft endpoint. Save progress server-side. Cross-device resume. | 4 hrs |
| **Phase 3** | Edit profile flow. Load processed users, allow updates. | 3 hrs |

**Priority:** Phase 1 after orchestrator. Phase 2-3 before public launch.

---

## 📊 Fly.io App Status (as of 2026-03-22)

```
jodi-matchmaker        deployed   Mar 6   (Telegram bot - NOT web API)
jodi-bot-staging       deployed   Mar 8   (Staging)
haystack-email-poller  deployed   Mar 14  (Ignition Club)
```

**Health Check:**
- `jodi-matchmaker.fly.dev/` → 200 ✅
- `jodi-matchmaker.fly.dev/health` → 200 ✅
- `masii-bot.fly.dev/*` → ❌ Does not exist

---

## Notes

- Telegram bot username confirmed: `@masiiapp_bot`
- Current mode: **Web + Email only**
- Matching algorithm: Phase 2 (after intake is validated)
