# Research Note #1: Double Opt-In Introduction Patterns

**Topic:** Progressive Disclosure Models (Haystack, Jodi, Professional Matching)  
**Date:** February 14, 2026  
**Compiled by:** A

---

## Core Principle: Mutual Consent > Forced Exposure

The fundamental insight: **Introducing two parties without both consenting is deploying their time on your behalf without permission.**

---

## What Double Opt-In Means (Professional Context)

**Definition:** A third party connects two people **only after both have agreed** to be connected, with the option to decline before introductions happen.

**Why it works:**
- Respects both parties' time and boundaries
- Reduces inbox resentment ("don't make me the asshole for saying no")
- Creates higher-quality connections (both parties actually want it)
- Signals trust and professionalism from the connector

---

## The Email Pattern (from beehiiv)

### ❌ **Single Opt-In (BAD):**

> "Hey [Person A], meet [Person B]! You both love paint. I think you should chat."

**Problems:**
- Person A never consented
- Forced into 3 bad choices: ignore (look like a jerk), decline (look like a jerk), or waste time
- Connector is showing off their access to Person A's time

---

### ✅ **Double Opt-In (GOOD):**

**Step 1: Ask both parties separately**

> "Hey [Person A], I know someone ([Person B]) who's doing [specific relevant thing]. Would you be open to a short intro? Here's why I think it could be valuable: [1-2 sentences]. Totally fine if now's not the right time."

> "Hey [Person B], I know [Person A] who might be able to help with [specific problem]. Would you be interested in an intro? No worries if you're slammed."

**Step 2: Only connect if both say yes**

> "Great! Connecting you both. [Person A], meet [Person B] — [context]. [Person B], [Person A] is [context]. I'll let you two take it from here. Feel free to ignore if this ends up not being useful."

**Why this works:**
- Acknowledges the value and time of **both** people
- Tells both parties **exactly** who the other person is and why it might be helpful
- Creates a norm that allows recipients to ignore it without guilt

---

## Progressive Disclosure in Matching Platforms

### BetterHelp (Therapist Matching)

**How it works:**
1. **Initial questionnaire:** User fills out needs, preferences, schedule, therapist gender preference
2. **Algorithm processes inputs:** Matches user with licensed therapist based on proprietary algorithm
3. **48-hour window:** Algorithm sends query to all providers whose profile buzzwords match; at least one provider responds in 99% of cases
4. **User gets matched therapist:** Can switch therapists anytime for free

**Key privacy insight:**
- BetterHelp's privacy policy: "We process some data to personalize your experience. For example, if you identify as religious and prefer a therapist who utilizes faith-based practices, we process that information to match you with an appropriate therapist."
- **Progressive trust:** Start with basic preferences → refine over time → never expose raw profile to directory browsing

---

### Keeper.ai (Dating Matchmaking)

**Tier-based onboarding:**
- **Tier 1:** Basics (age, location, non-negotiables)
- **Tier 2:** Preferences (what you want, lifestyle basics)
- **Tier 3:** Deep profile (signals, family context, lifestyle details)
- **Tier 4:** Calibrated (after initial matches, refine preferences)

**Critical lesson:** Don't rush incomplete profiles into matching. 70%+ Tier 2 completion required before matching activates. Why? Poor early matches = blame the service.

**Progressive disclosure model:**
- Users never see raw profiles
- Matchmaker controls what gets shared, when
- Introduction only happens when both profiles are "ready" (completeness thresholds met)
- Double opt-in at match stage: both parties must agree to intro

---

## Anti-Pattern: LinkedIn / Dating App "Directory Browsing"

**Problem with directories:**
- All-or-nothing disclosure: either your full profile is visible or you're invisible
- No progressive trust building
- Leads to:
  - Incomplete profiles (users protect privacy by withholding)
  - Comparison shopping (reduces humans to specs)
  - Asymmetric information (one party knows way more before first contact)

**Why progressive disclosure wins:**
- **Control:** Platform controls what gets shared, when
- **Context:** Each reveal is tied to a specific stage (e.g., "we think you're a match, here's why")
- **Trust ladder:** Small reveals → mutual interest → deeper context → introduction
- **Protection:** Bad actors can't scrape/browse/stalk

---

## Application to HAYSTACK (Talent Matching)

**Current model (email-first):**
- Candidates email talent.haystack@gmail.com with resume + quota docs
- Companies email talent.haystack@gmail.com with JD + business email (verification)
- AI extracts signals, matches candidates to JDs
- **Morning emails (8 AM):** Companies get "why this match" narrative + anonymized performance summary

**Missing layer: Double opt-in**

**Proposed flow:**
1. **Candidate submits** → AI extracts signals, verifies performance
2. **Match identified** → AI scores fit (0.4 performance + 0.3 context + 0.2 relative strength + 0.1 trajectory)
3. **Ask candidate first:** "We have a [role type] at [company strength tier, e.g., 'growth-stage B2B SaaS, $20M ARR']. Interested in an intro?"
4. **If yes, ask company:** "We have a candidate who [performance summary, anonymized]. Fits your JD because [LLM narrative]. Want an intro?"
5. **If both yes → connect:** Full profiles exchanged, intro email with context

**Why this matters for HAYSTACK:**
- **Protects candidates:** No spamming their info to companies that won't engage
- **Protects companies:** No wasting time on candidates who aren't interested
- **Higher conversion:** Both parties are pre-qualified and consenting
- **Trust signal:** "We respect your time" = premium positioning

---

## Application to JODI (Matchmaking)

**Current onboarding:**
- 7-message intro (privacy reassurance, photos-at-end philosophy, emotionally safe space)
- 4 phases, 37 screens, 34-36 fields captured
- Tier-based progress (Tier 1 → 2 → 3 → 4)
- Matching only activates at **Tier 2 70%+ completion**

**Double opt-in layer:**
1. **Match identified:** AI scores compatibility based on 100+ data points (40% explicit, 60% inferred)
2. **Soft intro to both parties:** "We think we found someone who might be a great match. Here's why [1-2 sentences, anonymized]. Interested in learning more?"
3. **If both say yes:** "Great! Here's a bit more context [photo + 3-4 key compatibility signals]. Want to meet?"
4. **If both say yes again → full intro:** Exchange full profiles, set up first date logistics

**Why this wins:**
- **Emotionally safe:** No one gets rejected *after* seeing full profile (rejection happens at anonymized stage)
- **Higher engagement:** Both parties are pre-qualified and excited
- **Protects brand:** Bad matches don't happen because one party wasn't actually interested
- **Differentiation:** Most dating apps force "swipe on full profile" — this is concierge-level curation

---

## Key Quotes

**From beehiiv article:**
> "Don't (metaphorically) ding-dong ditch people's inboxes and leave bags of flaming, smelly substance for them to deal with. Ask for permission, it's the right thing to do."

**From BetterHelp users (Reddit):**
> "In reality, it's an algorithm and whatever research they've done shows that within 48 hours, at least one provider has responded to the query, sent out to all the providers whose profile buzzwords match yours, in 99% of cases."

---

## Bottom Line

**Progressive disclosure + double opt-in = trust at scale.**

- Start with minimal information exchange
- Increase revelation only when mutual interest is confirmed
- Never force exposure without consent
- Respect asymmetry: candidates/daters have more to lose than companies/matchers

**This is the moat.** Anyone can build a directory. Building a trust ladder requires UX restraint and AI orchestration.

---

**Sources:**
- beehiiv: "Nail Email Etiquette: Use the Double Opt-In Introduction" (https://www.beehiiv.com/blog/how-to-use-the-double-opt-in-introduction)
- BetterHelp privacy policy + user experiences (therapyhelpers.com, Reddit)
- Keeper.ai tier model (from N's JODI data framework)
- Andrew Chen marketplace thinking (applied to matching context)
