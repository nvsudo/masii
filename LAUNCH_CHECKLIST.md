# masii Launch Checklist — Finishing Touches

Created: 2026-03-06 01:15 AM Dubai

## ✅ DONE

### Infrastructure
- [x] Domain: masii.co + masii.app configured
- [x] DNS: Cloudflare pointing to Pages + Fly.io
- [x] Frontend: Deployed on Cloudflare Pages from `nvsudo/masii` main branch
- [x] Backend: Fly.io apps exist (`jodi-matchmaker`, `jodi-bot-staging`)
- [x] Database: Supabase connected (herqdldjaxmfusjjpwdg)

### Auth System
- [x] Supabase email auth configured
- [x] signup.html created
- [x] login.html created  
- [x] onboarding.html created
- [x] auth.js wrapped in DOMContentLoaded

## 🚧 NEEDS ATTENTION

### 1. Email Auth Flow - END-TO-END TEST
**Status:** Code deployed, but not tested end-to-end  
**Test Steps:**
- [ ] Create test account at masii.co/signup.html
- [ ] Check email arrives (confirm Supabase email template is configured)
- [ ] Click confirmation link
- [ ] Verify redirect to /onboarding.html
- [ ] Check session persists

**Blockers:**
- Need to verify Supabase email provider is enabled
- Need to check email template is customized (currently default)

### 2. Telegram Bot Link
**Current:** Placeholder `https://t.me/your_masii_bot`  
**Needs:** Real bot username

**Action Required:**
- [ ] Find/confirm Telegram bot username (check Fly secrets or create new bot)
- [ ] Update `website/onboarding.html` line ~68
- [ ] Commit + push to trigger Cloudflare redeploy

**Backend Status:**
- ✅ `TELEGRAM_BOT_TOKEN` is set in Fly secrets
- ✅ Bot code exists in `/backend/bot/`
- ❓ Not sure if this is the production bot or staging

### 3. Backend Rebrand Updates
**Current App Name:** `jodi-matchmaker` (not rebranded)  
**Issues:**
- Fly app names still reference "jodi"
- May have old env vars or domain refs

**Options:**
1. **Keep it** - Internal naming doesn't matter, just update DNS
2. **Rename** - Create `masii-bot` and migrate
3. **Deploy fresh** - New Fly app from scratch

**Recommendation:** Keep `jodi-matchmaker` running, just update:
- [ ] Verify Supabase connection string is current
- [ ] Check ANTHROPIC_API_KEY is valid
- [ ] Test bot responds to /start

### 4. User Flow - CRITICAL PATH TEST
**The Golden Path:**
1. User visits masii.co
2. Clicks "Start" → masii.co/signup.html
3. Signs up with email
4. Receives confirmation email
5. Clicks link → masii.co/onboarding.html
6. Clicks "Start Conversation on Telegram"
7. Opens Telegram bot
8. Bot says hello, starts 36-question flow
9. Bot stores answers in Supabase
10. Matching runs (manual or cron)

**Test Status:**
- [ ] Steps 1-2: ✅ (website is live)
- [ ] Steps 3-6: ⚠️ (code exists, not tested)
- [ ] Steps 7-10: ❓ (backend deployed, not verified)

### 5. Supabase Configuration
**Dashboard:** https://supabase.com/dashboard/project/herqdldjaxmfusjjpwdg

**Settings to verify:**
- [ ] Authentication → Providers → Email: **ENABLED**
- [ ] Authentication → Providers → Email: **Confirm email = ON**
- [ ] Authentication → URL Configuration → Site URL: `https://masii.co`
- [ ] Authentication → URL Configuration → Redirect URLs: `https://masii.co/onboarding.html`
- [ ] Authentication → Email Templates → Confirm signup: **Customized** (optional but nice)

### 6. Backend Health Check
**Apps:**
- `jodi-matchmaker` (production)
- `jodi-bot-staging` (staging)

**Status:**
- Last deployed: Feb 19, 2026 (production is OLD)
- May need fresh deployment with latest code

**Health Checks:**
- [ ] `curl https://jodi-matchmaker.fly.dev/health` (or equivalent endpoint)
- [ ] Check Fly logs: `fly logs -a jodi-matchmaker`
- [ ] Verify bot webhook is set up correctly

## 🎯 TOMORROW'S PLAN (Priority Order)

### Phase 1: Verify & Fix (30 min)
1. **Get Telegram bot username** (ask N or check @BotFather)
2. **Update onboarding.html** with real bot link
3. **Test Supabase settings** (email provider, redirects)
4. **Deploy backend** if needed (may be outdated)

### Phase 2: End-to-End Test (30 min)
5. **Test signup flow** with real email
6. **Verify email delivery** and confirmation
7. **Test Telegram bot** responds to /start
8. **Check Supabase data** is written correctly

### Phase 3: Polish (30 min)
9. **Update email templates** in Supabase (branding)
10. **Add monitoring** (error alerts, usage tracking)
11. **Document** the working flow for future reference

## ❓ QUESTIONS FOR N

1. **Telegram Bot:** What's the bot username? (e.g., `@masii_bot`)
   - If it doesn't exist, should I create a new one via @BotFather?
   
2. **Backend Deployment:** Should I redeploy `jodi-matchmaker` with latest code?
   - Last deploy was Feb 19 (2+ weeks ago)
   
3. **Email Branding:** Want me to customize the Supabase confirmation email template?
   - Default template is plain, could add masii branding
   
4. **Monitoring:** Set up error alerts for the bot? (e.g., Telegram group for failures)

## 📝 NOTES

- Frontend is solid (Cloudflare Pages auto-deploys from GitHub)
- Auth code looks good (fixed race conditions tonight)
- Backend is the biggest unknown (deployed 2 weeks ago, may need refresh)
- Need to verify the full loop: signup → email → Telegram → Supabase

---

**Next Steps:** Answer the 4 questions above, then I'll execute the 3-phase plan.
