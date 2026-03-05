# Masii — Go-to-Market Playbook

**Last updated:** 2026-03-04
**Status:** Pre-launch. Core engine done. Need to wire it up and deploy.

---

## Honest State

| Layer | Status | Notes |
|-------|--------|-------|
| Brand & docs | DONE | Vision, brand soul, question flow (60 Qs), v2 matching protocol, orchestrator spec |
| Website | DONE (local) | Static HTML — landing, about, start, form, 23 blog posts, 12 match stories. Not deployed. |
| Domain | SECURED | masii.co + masii.app — both owned. Need to point to hosting. |
| Telegram bot | DONE (staging) | v2 60-question flow on Fly.io (`jodi-bot-staging`), webhook-based, Supabase-connected. @masiiapp on Telegram. Tests passing. |
| Web form | DONE (local) | Full 77-field intake with conditional logic. Not connected to Supabase. Runs on localhost only. |
| Question flow | DONE (v2) | 60 questions, conditional branching, synced across bot config, web form schema, and DB schema. |
| Database schema | DONE (v2) | 16 migrations on Supabase. All v2 partner preference columns deployed. Multi-channel identity layer in place. |
| Matching engine | DONE (v2) | Hard filters (17 gates) + per-question scoring (35 scorers) + bidirectional min. 28 tests passing. Not deployed. |
| Double opt-in | DONE (code) | Full state machine: pending → offered_a → accepted_a → offered_b → accepted → introduced. 72h timeout. Email intro. Bot callbacks wired. |
| Cron / scheduler | DONE (code) | `cron.py` with --match, --deliver, --dry-run modes. Not deployed — no scheduled job running. |
| Match delivery | DONE (code) | Telegram notifications + email introductions. SMTP-ready. Not tested end-to-end with real data. |
| MCP server | NOT BUILT | Expose profile creation as a tool. Anyone on ChatGPT or Claude can create a Masii profile mid-conversation. |
| Identity (OTP/SSO) | NOT BUILT | No phone verification or SSO. Web form is open. Data quality risk. |
| WhatsApp | NOT BUILT | PRD exists. Identity layer ready. No webhook handler, no Meta/Twilio account. |
| Safety (report/flag) | NOT BUILT | Zero code. Needed before public launch. |
| Social (X, Insta) | PARTIAL | @masiiapp on X secured. Instagram not started. |
| Payments | NOT BUILT | Not needed for free tier launch |

---

## What's Actually Working Right Now

1. Telegram bot can onboard a user through 60 questions with conditional branching
2. Data saves to Supabase (users, user_preferences, user_signals tables)
3. Matching engine finds compatible pairs — 28 test scenarios all pass, including NRI cross-country, 2nd gen, cross-religion rejection, strict diet gates
4. Double opt-in code handles the full lifecycle from match creation to email introduction
5. Cron script ties matching + delivery together
6. Multi-channel identity layer maps phone → Telegram → WhatsApp → email

## What's Not Working Yet

1. **No scheduled job running.** Matching and delivery code exists but nothing executes it. No cron on Fly.io, no external scheduler.
2. **Web form not deployed or DB-connected.** Works locally, stores to `.ndjson` file, not Supabase.
3. **Website not deployed.** HTML exists, domains secured (masii.co + masii.app), but not pointed to any hosting yet.
4. **End-to-end flow never tested with real profiles.** Bot → DB → matching run → Telegram offer → accept → email intro. Each piece works in isolation; the chain hasn't run.
5. **No safety/reporting.** A user can't flag or report a match.
6. **Social presence partial.** @masiiapp on X + Telegram secured. No posts. No Instagram yet.

---

## Critical Path to Launch

### What "launch" means
People can sign up via Telegram, Masii builds their profile, matching runs daily, both say yes, they get introduced. Free. That's the product.

### The blockers (in order)

```
1. Deploy cron job (matching + delivery)   ← the system starts producing matches
2. End-to-end test with real profiles      ← proves the chain works
3. Deploy website to masii.co              ← credibility, sign-up CTA (domain secured)
4. Safety / report mechanism               ← can't launch without this
5. First posts on @masiiapp X              ← discovery, proof of life (handle secured)
```

---

## The Checklist

### P0 — Without these, don't launch

- [x] **Rebrand bot** — All messages say Masii. v2 question flow with tree branching, section transitions, proxy support.
- [x] **v2 question flow** — 60 questions across intake phases. Conditional branching for religion/caste/practice/diet/gender.
- [x] **Matching engine v2** — 17 hard gates + 35 per-question scorers. Bidirectional. NRI, 2nd gen, cross-religion, diet strictness all tested. 75%+ = free intro, 60-74% = decent match.
- [x] **Double opt-in flow** — Girl-first offering. 72h timeout. State machine in delivery.py. Bot callbacks wired.
- [x] **Cron orchestrator** — match + deliver modes, dry-run, CLI flags. Ready to schedule.
- [x] **DB schema v2** — 16 migrations. All partner preference columns. Multi-channel identity.
- [x] **Domain** — masii.co + masii.app secured.
- [ ] **Deploy website** — Cloudflare Pages / Vercel / Netlify, point masii.co
- [ ] **Deploy cron job** — Schedule on Fly.io (daily matching at 2am IST, hourly delivery check). Or use external cron (Railway, Render cron, GitHub Actions).
- [ ] **End-to-end test** — Create 2 test profiles via Telegram bot → run matching → verify offer arrives → accept → verify intro email. Do this before going public.
- [ ] **Proxy flow test** — Create a profile on behalf of someone else (parent filling for child). Verify proxy fields save correctly, matching treats proxy profiles the same.
- [ ] **Identity verification** — OTP or Google SSO on web form. Without this, anyone can submit garbage profiles. (See decision below.)
- [ ] **Report / flag** — Button after introduction: "Report this person." Flags for Nik review. Auto-pause flagged profile.
- [ ] **Match history** — User asks "show my matches" → see past matches + status.

### P1 — Launch week, not day one

- [ ] **Deploy web form** — Vercel/Netlify. Wire to Supabase via API. Same 60 questions.
- [ ] **MCP server** — Expose Masii profile creation as a tool. Anyone on ChatGPT or Claude can say "find me a match" and Masii walks them through intake mid-conversation. Server handles: create profile, check match status, update preferences. Phone is the identity key — same profile regardless of channel.
- [ ] **Claude/ChatGPT skill** — Package the MCP server as a published skill/GPT action. "Create a Masii profile" as a one-click install. Distribution channel that costs nothing.
- [ ] **X account** — @masiiapp secured. Pin thread explaining the philosophy.
- [ ] **Instagram account** — @masii. Bio link → website. First 9 posts: brand story grid.
- [ ] **Community unlock page** — "Join the [City] pool. When we hit X profiles, matching starts."
- [ ] **Basic analytics** — Signups/day, intake completion rate, matches made, opt-in rate.
- [ ] **Feedback loop** — 7 days after introduction, Masii asks: "Did you connect?" Stores response.
- [ ] **chatgpt, claude apps** 
- [ ] ** voice based conversations** 
--  highest premium tier.
-- coaching 
-- post meeting feedback 
-- on going calibration 


#module to think about. calibration.. once you share your feedback, why helps us. 
- First paid tier feature 
- Nuanced profiles, data science + vector embeddings 
- Sexual preferences, boundaries, looks, etc : can we really do this 
- verified health reports, lab partners 
- credit score integration 

#physical world extensions
- First meet and great. looks, conversations, etc. stretch idea  

# premium clients
- bespoke service 
- get matched to the top families 
- in depth personalities, pictures, family background etc ( looking for a rich husband play )

#niche hits 
-- i have money, i need hot girl 
-- high ambition guy high ambition girl 
-- so rich, so rich, international lifestyle 



### P2 — Month 1, prove the model

- [ ] **WhatsApp Business API** — Apply, get approved, build webhook handler. Port the 60-question flow.
- [ ] **Verified tier** — Photo verification (live selfie match). Income verification (document upload). Badge on profile.
- [ ] **Payment integration** — Razorpay (INR) + Stripe (international). Subscription for Verified tier.
- [ ] **Nudge system** — Incomplete profiles nudged at 24h, 72h, 7d. Match responses nudged at 24h, 48h.
- [ ] **Content engine** — Weekly blog post or Instagram reel. Cultural takes, anonymized match stories.

### P3 — Month 2-3, scale

- [ ] **Premium tier** — Deep profiling, family context, active search, concierge introductions.
- [ ] **Second community unlock** — Pick next city/community based on waitlist.
- [ ] **Orchestrator agent** — Masii runs autonomously: intake follow-ups, matching runs, delivery, feedback, stats. Nik gets weekly digest.
- [ ] **Referral system** — "Invite 5 friends, unlock matching faster for your community."

---

## Decisions Needed Now

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Cron hosting** | Fly.io scheduled machine vs external cron (Railway, GitHub Actions) | **Fly.io.** Bot is already there. Keep infra together. |
| **First community** | Gujarati? City-based? Broad? | **Pick one city where you have network.** Mumbai Gujarati? Melbourne Indian? |
| **Domain routing** | masii.co as primary, masii.app redirect? | **masii.co primary.** Point masii.app → masii.co redirect. |
| **Website hosting** | Vercel / Netlify / Cloudflare Pages | **Cloudflare Pages.** Free, fast, custom domain. |
| **Telegram bot username** | @masiiapp (secured) | **Already done.** Update bot username on Fly.io if not already @masiiapp. |
| **Web form identity** | OTP vs Google SSO vs plain form | See analysis below. |

### Web Form Identity: OTP vs Google SSO vs Plain Form

**The problem:** A blank web form with no verification invites garbage data. Fake profiles poison the matching pool. On Telegram, identity is implicit (phone-linked account). On a web form, it's not.

| Approach | Effort | Data quality | Friction | Notes |
|----------|--------|-------------|----------|-------|
| **Phone OTP** | Medium (need SMS provider: Twilio/MSG91/Supabase Auth) | HIGH — phone = real person, matches Telegram identity model | Medium — extra step, but Indians are used to OTP | Phone is already the universal identity key in the DB. OTP confirms it's real. Works for both India (MSG91 cheap) and international (Twilio). Supabase has built-in phone auth. |
| **Google SSO** | Low (Supabase has it built-in, few lines of code) | MEDIUM — proves a Google account exists, not a phone number | Low — one click | Doesn't give you a phone number. You'd still need to ask for phone separately (for Telegram/WhatsApp linking). Two identity systems to reconcile. Good for NRI/2nd gen who expect SSO. |
| **Plain form** | Zero | LOW — anyone can submit anything | Zero | Only works if you manually review every profile before matching. Doesn't scale past 50 profiles. |
| **OTP + Google SSO** | Medium-High | HIGHEST — either path confirms identity | User's choice | Best UX: "Sign in with Google" OR "Verify your phone." Both paths eventually collect phone for matching. Supabase Auth supports both. |

**Recommendation:** Start with **Phone OTP via Supabase Auth**. Reasons:
1. Phone is already the identity key — OTP confirms it, zero reconciliation needed
2. Supabase Auth has phone OTP built-in (just enable it + add Twilio/MessageBird creds)
3. Prevents garbage profiles from day one
4. Add Google SSO later as a second option (easy to layer on)

**Cost:** Twilio SMS ~$0.05/OTP (international), MSG91 ~₹0.15/OTP (India). At 100 signups, that's $5 or ₹15. Irrelevant.

---

## Architecture as of Today

```
Telegram Bot (Fly.io staging)
    │
    ▼
Supabase (AP South 1 — Mumbai)
    ├── users (100+ columns, v2)
    ├── user_preferences (14 partner pref columns, v2)
    ├── user_signals (lifestyle signals)
    ├── matches (double opt-in status lifecycle)
    └── user_channels (phone/telegram/whatsapp/email)
    │
    ▼
Matching Engine (local, not deployed)
    ├── filters.py — 17 hard gates
    ├── scoring.py — 35 per-question scorers
    ├── matcher.py — pair identification + ranking
    ├── delivery.py — double opt-in + email intro
    └── cron.py — scheduler (--match, --deliver, --dry-run)
    │
    ▼
Notifications
    ├── Telegram (match offers via bot)
    └── Email (introductions via SMTP)
```

---

## What "Working" Looks Like

1. Someone finds Masii (website, social, word of mouth)
2. They message Masii on Telegram
3. Masii asks 60 questions in ~12 minutes (conditional branching)
4. Profile saved to Supabase
5. Cron runs matching daily at 2am IST
6. Match found (75%+) → Masii sends summary to Person A via Telegram
7. Person A says yes → Masii sends to Person B (72h timeout each)
8. Both yes → Email introduction with names, details, conversation starter
9. 7 days later → Masii asks how it went
10. Feedback stored → Matching improves

That's the loop. Everything else is optimization.

---

## Uncommitted Work (as of Mar 4)

11 files changed across v2 matching rewrite + intake alignment:
- `backend/matching/` — filters, scoring, matcher, tests (v2 rewrite, 28 test scenarios)
- `backend/bot/` — config.py, conditional_logic.py (v2 question alignment)
- `webform-intake/` — app.js, schema.json (v2 question alignment)
- `docs/question-flow.md` — v2 updates

This work needs to be committed and pushed.

---

*"Ship the loop. Then make it better."*
