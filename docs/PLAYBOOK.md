# Masii — Go-to-Market Playbook

**Last updated:** 2026-03-03
**Status:** Pre-launch checklist

---

## Honest State

| Layer | Status | Notes |
|-------|--------|-------|
| Brand & docs | DONE | Vision, brand soul, 36 gunas spec, matching protocol, orchestrator |
| Website | DONE (not deployed) | Static HTML, needs hosting + domain |
| Telegram bot | DONE (deployed) | 36 gunas on Fly.io, stores to Supabase. Masii branded. |
| Web form | EXISTS (broken) | Local only, not connected to DB, not Masii-styled |
| Matching algorithm | NOT BUILT | Zero code. Protocol doc exists. |
| Double opt-in | NOT BUILT | Zero code |
| Match delivery | NOT BUILT | Zero code |
| WhatsApp | NOT STARTED | No Business API account |
| Payments | NOT BUILT | Not needed for free tier launch |
| Social (X, Insta) | NOT STARTED | No accounts |
| Domain | NOT PURCHASED | masii.co / masii.app / masii.ai |
| Safety (report/flag) | NOT BUILT | Zero code |

---

## Critical Path to Launch

### What "launch" means
People can sign up, Masii builds their profile, Masii matches them, both say yes, they connect. Free. That's the product.

### The blockers (in order)

```
1. Matching algorithm     ← without this, no product
2. Double opt-in flow     ← without this, no introductions
3. Domain + website live  ← credibility, CTA destination
4. Social presence        ← discovery, proof of life
```

---

## The Checklist

### P0 — Without these, don't launch

- [x] **Rebrand bot** — All messages say Masii. 36-guna flow with tree branching, section transitions, proxy support.
- [x] **36 gunas intake** — 36 questions across 6 sections (Niyat, Parichay, Dharam, Parivar, Jeevan Shaili, Soch). Conditional tree branching for religion/caste/practice/diet. ~10 minutes.
- [ ] **Domain** — Buy masii.co or masii.app or masii.ai
- [ ] **Deploy website** — Vercel/Netlify/Cloudflare Pages, point domain
- [ ] **Matching algorithm v1** — Hard filters (gender, age range, location, religion, marital status) → compatibility score (culture, lifestyle, values, family) → rank. Doesn't need to be perfect. Needs to produce a match with a reason.
- [ ] **Match delivery** — Masii sends match summary to Person A on Telegram. "I found someone. Here's why I think you two should meet." Shows: age, city, education, career, Masii's reasoning. No name/photo yet.
- [ ] **Double opt-in** — Person A says yes → Masii sends to Person B. Person B says yes → introduction sent. Person says no → logged, never revealed to other party. 72h timeout.
- [ ] **Introduction message** — Both said yes. Masii sends both parties: name, photo (if uploaded), a conversation starter, and each other's Telegram handle or phone.
- [ ] **Report / flag** — Button after introduction: "Report this person." Flags for Nik review. Auto-pause flagged profile. Simple is fine.
- [ ] **Match history** — User can ask "show my matches" and see past matches + status (pending, accepted, rejected, expired, introduced).

### P1 — Launch week, not day one

- [ ] **Web form rebuild** — Styled like Masii. Connected to same Supabase DB. Same 36 gunas. Phone = identity key.
- [ ] **X account** — @masiiHQ or @getmasii or @masii_app. Bio: "AI matchmaker for Indians everywhere. You deserve to meet." Pin a thread explaining the philosophy.
- [ ] **Instagram account** — @masii or @masii.app. Bio link → website. First 9 posts: brand story grid (the philosophy, the problem, cultural takes).
- [ ] **Community unlock page** — On website: "Join the [City/Community] pool. When we hit [X] profiles, matching starts." Progress bar. Invite link.
- [ ] **Basic analytics** — Track: signups/day, intake completion rate, matches made, opt-in rate. Supabase queries or simple dashboard.
- [ ] **Feedback loop** — 7 days after introduction, Masii asks: "Did you connect? How did it go?" Stores response. Feeds into matching quality.

### P2 — Month 1, prove the model

- [ ] **WhatsApp Business API** — Apply, get approved, build webhook handler. Port the 36-guna flow.
- [ ] **Verified tier** — Photo verification (live selfie match). Income verification (document upload). Badge on profile.
- [ ] **Payment integration** — Razorpay for INR. Stripe for international. Subscription for Verified tier.
- [ ] **Match explanation** — "Masii's reasoning" section with the match. "You both value family involvement. You're both Jain vegetarian. She's in Melbourne, you're in Sydney — close enough for weekends."
- [ ] **Nudge system** — Incomplete profiles get nudged at 24h, 72h, 7d. Match responses nudged at 24h, 48h.
- [ ] **Content engine** — Weekly blog post or Instagram reel. Cultural takes, anonymized match stories, dating observations.

### P3 — Month 2-3, scale

- [ ] **Premium tier** — Deep profiling, family context, active search, concierge introductions.
- [ ] **Second community unlock** — Pick next city/community based on waitlist.
- [ ] **Orchestrator agent** — Masii runs autonomously: intake follow-ups, matching runs, match delivery, feedback, stats publishing, anomaly detection. Nik gets weekly digest, not daily tasks.
- [ ] **Referral system** — "Invite 5 friends, unlock matching faster for your community."

---

## Decisions Needed Now

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Channel for launch** | WhatsApp vs Telegram | **Telegram.** WhatsApp API takes weeks to approve. Telegram is live. Ship now, port later. |
| **First community** | Gujarati? City-based? Broad? | **Pick one city where you have network.** Mumbai Gujarati? Melbourne Indian? Decide and recruit. |
| **Matching v1 scope** | Full 7-dimension scoring vs simple filters | **Simple first.** Hard filters + 3 weighted dimensions (culture, lifestyle, values). Ship in days, not weeks. |
| **Photos** | Required vs optional | **Optional at signup, required before introduction.** Don't gate intake on photos. |

---

## What "Working" Looks Like

1. Someone finds Masii (website, social, word of mouth)
2. They message Masii on Telegram
3. Masii asks 36 questions in ~10 minutes (6 sections, tree branching)
4. Profile saved to Supabase
5. Masii runs matching (every 12 hours or on-demand)
6. Match found → Masii sends summary to Person A
7. Person A says yes → Masii sends to Person B
8. Both yes → Introduction sent with contact details
9. 7 days later → Masii asks how it went
10. Feedback stored → Matching gets smarter

That's the loop. Everything else is optimization.

---

*"Ship the loop. Then make it better."*
