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
1. **[BLOCKER]** Deploy `/api/intake` endpoint (Blitz task)
2. **[TEST]** End-to-end form submission
3. **[VERIFY]** Supabase receives data correctly
4. **[OPTIONAL]** Customize email templates

### Backend Decision Needed:
- Create new `masii-bot` app? Or extend `jodi-matchmaker`?
- Recommendation: New app (`masii-bot`) for clean separation

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
