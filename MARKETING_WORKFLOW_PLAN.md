# masii Marketing Workflow — Architecture Plan

**Status:** Ready to build (awaiting approval)  
**Last Updated:** 2026-03-13 16:17 GMT+4  
**Owner:** A (Main Agent)

---

## Core Stack

### Copy & Ideas
- **Opus** — Generate copy, creative angles, content variations
- **Sonnet** — Quality checks, tone inspection, brand alignment audits

### Visual Content
- **Google Gemini 2.0 Flash** — Fast image generation (posters, graphics, social)
- **Google Imagen 3** — High-quality images (fallback: Gemini Flash)
- **Google Nano Banana** — Short-form video generation

### Posting & Automation
| Channel | Method | Automation Level |
|---------|--------|-----------------|
| **X/Twitter** | Direct API | Fully automated (A posts) |
| **Instagram** | Buffer API scheduling | Semi-automated (A schedules, Buffer posts) |
| **Reddit** | Direct API | Fully automated (A posts) |

---

## Full Workflow

### 1. MORNING GENERATION
```
Opus: Generate 5-10 content ideas
  ↓ (masii brand guidelines injected)
Sonnet: Quality check + brand alignment
  ↓
[YOU APPROVE IDEAS] ← Gate 1
  ↓
Opus: Write full copy for approved ideas
  ↓
Sonnet: Tone check, readability, masii fit
  ↓
[YOU APPROVE COPY] ← Gate 2
```

### 2. VISUAL GENERATION (Instagram + Visual X Posts)
```
Gemini 2.0 Flash: Generate images/graphics
Nano Banana: Generate short video clips
  ↓
[YOU APPROVE VISUALS] ← Gate 3
```

### 3. POSTING

**X/Twitter:**
- A posts directly via Twitter API
- Immediate live
- Non-repetition rules enforced (5-day cooldown per mention)

**Instagram:**
- A schedules via Buffer API
- Posts at scheduled time (auto)
- Visual approval required before scheduling

**Reddit:**
- A posts directly via PRAW API
- Immediate live
- Subreddit rules compliance checked by Sonnet

### 4. REAL-TIME ENGAGEMENT TRACKING
```
Dashboard auto-pulls:
  - Likes, shares, comments, saves
  - Follower growth
  - Click-through rates (via UTM tracking)
  - Conversion signals (if trackable)
```

### 5. EVENT-DRIVEN LEARNING
```
ON EACH WIN/FAILURE: Log to lessons.md immediately

Format:
[TIMESTAMP] | [CHANNEL] | [OUTCOME] | [INSIGHT]

Examples:
2026-03-13 13:45 | X | 2K likes | Hook "Real intent over swiping" works
2026-03-13 14:12 | Instagram | 50 likes | Reel length too long?
2026-03-13 15:30 | Reddit | 40 comments | Q&A format drives engagement
```

### 6. LEARNING LOOP
```
Daily:
  - You review lessons.md
  - Extract patterns (what resonates, what flops)
  - Feed insights back to Opus for next day's ideas

Weekly:
  - Compile performance summary
  - Document wins for DevMkt playbook
  - Identify new hooks/angles to test
```

---

## Approval Gates (Your Control Points)

1. **Ideas Approval** — Opus generates, you approve direction
2. **Copy Approval** — Opus writes, you approve messaging
3. **Visual Approval** — Gemini/Nano generates, you approve creative
4. **Lessons Review** — You read lessons.md daily, provide feedback

Everything else is automated.

---

## Daily Token Cost Estimate

| Task | Model | Cost |
|------|-------|------|
| Copy + Ideas (5-10 posts) | Opus | ~8K tokens |
| Quality Checks | Sonnet | ~3K tokens |
| Scheduling + Dashboard | Haiku | ~200 tokens |
| **DAILY TOTAL** | — | **~11.2K tokens** |

*External APIs (Gemini, Nano Banana) are pay-per-use, not token-based.*

---

## Channels & Cadence

**X/Twitter:**
- 6-12 posts/day (randomized times within 10:00-14:00 window)
- Observations, tips, diaspora insights, community engagement

**Instagram:**
- 1-2 reels/day + 2-3 carousel posts
- Lifestyle, onboarding stories, community highlights
- Scheduled via Buffer

**Reddit:**
- 2-3 threads/week in niche communities (r/diaspora, r/immigration, etc.)
- AMAs, help threads, genuine discussions

---

## Brand Guidelines Integration

From `masii-brand-design-system.md`:
- **Tone:** Warm, inclusive, honest about diaspora complexities
- **Voice:** First-person, storytelling, not corporate
- **Visual:** Warm colors (amber, earth tones), human-focused photography
- **Key Hooks:** 
  - "Free matches" (vs. paid dating apps)
  - "For diaspora" (identity-first)
  - "Real intent" (no swiping fatigue)
  - "Built by diaspora, for diaspora"

All Opus prompts injected with these guidelines.

---

## Dependencies & Prerequisites

- ✅ masii repo pulled (`/ventures/masii/`)
- ✅ Brand guidelines extracted
- ✅ Buffer API credentials needed (for Instagram scheduling)
- ✅ X/Twitter OAuth configured
- ✅ Reddit API credentials needed (if posting programmatically)
- ✅ Google Gemini/Nano Banana API access needed

---

## Next Steps (When Approved)

1. Wire up Opus → Sonnet → Gemini pipeline
2. Set up Buffer API integration (Instagram)
3. Set up X/Twitter direct posting
4. Set up Reddit direct posting
5. Create lessons.md template (event-driven)
6. Build engagement dashboard
7. Inject brand guidelines into all prompts
8. **THEN:** Start content generation (awaiting your daily approvals)

---

**Status:** READY TO BUILD
