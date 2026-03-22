# masii Marketing Dashboard — Complete Setup & Usage Guide

**Status:** READY TO DEPLOY  
**Last Updated:** 2026-03-13  
**Owner:** A (Main Agent)

---

## What You Have

### Core Components (Python)
1. **`masii_content_generator.py`** — Opus-powered content generation
   - Ideas: 5-10 concepts per day
   - Copy: Full text for X, Instagram, Reddit
   - Brand guidelines baked in

2. **`masii_marketing_orchestrator.py`** — Master orchestrator
   - Content queue management
   - Approval gate tracking
   - Dashboard snapshots
   - Lessons logging

3. **`masii_posting_engine.py`** — Platform posting
   - X/Twitter: Direct API + randomized scheduling
   - Instagram: Buffer API integration
   - Reddit: PRAW integration

4. **`lessons.md`** — Event-driven learning log
   - What worked (and why)
   - What flopped (and why)
   - Monthly synthesis
   - Grows daily

### Documentation
- **`MARKETING_INFRASTRUCTURE.md`** — Full architecture (this file points to it)
- **`MARKETING_WORKFLOW_PLAN.md`** — High-level strategy

---

## Daily Workflow (43 Minutes Total)

### 8:00 AM — Morning Ideas (5 min)

**You don't do anything yet.** A generates ideas:

```bash
# Terminal (A's work, not yours)
python3 masii_content_generator.py generate-ideas --count=10
```

**Output:** 10 ideas across X, Instagram, Reddit

---

### 8:05 AM — User Approval: Ideas (5 min)

**Your turn.** Review ideas and pick which ones to develop.

**Action:**
1. Read the 10 ideas
2. Approve top 5-7 ideas you like
3. Tell A which ones → A writes copy

---

### 8:10 AM — Copy Writing (10 min)

**A writes** full copy for approved ideas (Opus):

```bash
python3 masii_content_generator.py write-copy --ideas=[approved_ids]
```

**Output:** Full copy ready for each platform

---

### 8:20 AM — User Approval: Copy (5 min)

**Your turn.** Review copy and approve final wording.

**Action:**
1. Read the copy for each post
2. Approve or request rewrites
3. Tell A to proceed to visuals

---

### 8:25 AM — Visual Generation (10 min)

**A generates** images/videos (Gemini, Nano, Veo):

```bash
# Gemini for images
python3 masii_visual_designer.py generate-images --posts=[approved_ids]

# Nano for short videos
python3 masii_visual_designer.py generate-videos --posts=[approved_ids] --type=nano

# (Optional) Veo for premium videos
python3 masii_visual_designer.py generate-videos --posts=[approved_ids] --type=veo
```

**Output:** Images + short videos for each post

---

### 8:35 AM — User Approval: Visuals (5 min)

**Your turn.** Review visuals and approve direction.

**Action:**
1. Review generated images/videos
2. Approve or request new visuals
3. Tell A to schedule posts

---

### 8:40 AM — Scheduling (5 min)

**A schedules** posts across platforms:

```bash
python3 masii_posting_engine.py schedule-daily-posts --posts=[approved_ids]
```

**What happens:**
- **X posts:** Scheduled for randomized times (10:00-14:00 window)
- **Instagram posts:** Scheduled in Buffer (you confirm in Buffer dashboard)
- **Reddit posts:** Posted immediately (or scheduled if you prefer)

**Output:** Confirmation that posts are queued/scheduled

---

### 8:45 AM — Confirmation (0 min)

**Done.** Posts are live or queued.

---

## Real-Time Monitoring (Throughout Day)

### Dashboard Updates (Auto)

Every 15 minutes, engagement is pulled from X/Instagram/Reddit:

```bash
# A runs this automatically
python3 masii_marketing_orchestrator.py get-dashboard-snapshot
```

**Shows:**
- Likes, shares, comments, followers
- Conversion signals (clicks, signups)
- Engagement rate by platform
- Trending content

### Lessons Logging (Event-Driven)

When a post gets traction (or flops), A logs it immediately:

```
[2026-03-13 14:23] | X | 87 likes | Diaspora identity hook works
Post: "Free matches > endless swiping..."
Context: Posted 13:47, avg X post = 24 likes
Learning: Identity-first messaging outperforms generic dating hooks.
```

---

## What You Actually Do

### Gate 1: Ideas Approval (5 min)
- **Input:** 10 ideas
- **Your call:** Pick which ones to develop (N/A if you like them all)
- **Output:** Approved list goes to copy writer

### Gate 2: Copy Approval (5 min)
- **Input:** Full copy for each approved idea
- **Your call:** "This works" or "Reword this"
- **Output:** Approved copy goes to designer

### Gate 3: Visuals Approval (5 min)
- **Input:** Images + videos (from Gemini/Nano/Veo)
- **Your call:** "Love it" or "Try again"
- **Output:** Approved visuals go to scheduler

### Gate 4: Schedule Confirmation (0-5 min)
- **Input:** Posts queued across platforms
- **Your call:** "Ship it"
- **Output:** Posts go live/scheduled

### Daily Learning Review (Optional, 10 min)
- **Read:** lessons.md entries from the day
- **Your insight:** "This pattern is worth testing" or "Kill this angle"
- **Impact:** Tomorrow's ideas build on today's learnings

---

## Setup Instructions

### 1. Buffer Account Setup (You Do This)

```
1. Sign up: https://buffer.com (free tier: 3 channels, 5 posts/queue)
2. Connect Instagram (Buffer OAuth)
3. Get API token (Buffer dashboard → API)
4. Save token to: ~/.buffer_api_token
```

### 2. X/Twitter API Setup (A Can Do This)

```
1. You have full OAuth (read + write)
2. API token already configured in moltbot.json
3. Ready to post
```

### 3. Reddit PRAW Setup (A Can Do This)

```
1. Create Reddit app (reddit.com/prefs/apps)
2. Get credentials (client_id, client_secret, user_agent)
3. Configure in masii_posting_engine.py
```

### 4. Google Gemini API Setup

```
1. Enable Gemini API (Google Cloud)
2. Get API key
3. Store in ~/.gemini_api_key
```

### 5. Optional: Nano Banana & Veo

```
# These are external APIs, pay-per-use
# Not required for MVP; can add later
```

---

## Daily Commands (Reference)

```bash
# Morning: Generate ideas
python3 masii_content_generator.py generate-ideas --count=10

# After your approval: Write copy
python3 masii_content_generator.py write-copy --ideas=1,2,3,4,5

# After your approval: Generate visuals
python3 masii_visual_designer.py generate-images --posts=1,2,3,4,5
python3 masii_visual_designer.py generate-videos --posts=1,2,3,4,5

# After your approval: Schedule posts
python3 masii_posting_engine.py schedule-daily-posts --posts=1,2,3,4,5

# Monitor engagement (auto-runs every 15 min)
python3 masii_marketing_orchestrator.py get-dashboard-snapshot

# View lessons log
cat lessons.md

# Log a learning (when a post gets traction)
python3 masii_marketing_orchestrator.py log-learning \
  --platform=X \
  --engagement=87_likes \
  --insight="Diaspora identity hook works"
```

---

## Cost & Token Budget

**Daily Token Spend:** ~9.7K tokens

| Component | Tokens | Cost |
|-----------|--------|------|
| Ideas (Opus) | 2K | $0.06 |
| Copy (Opus) | 4K | $0.12 |
| Audits (Sonnet) | 3K | $0.03 |
| Dashboard (Haiku) | 0.5K | $0.001 |
| **Daily Total** | **9.7K** | **$0.22** |

**External APIs (Pay-per-use):**
- Gemini: ~$0.01-0.02 per image
- Nano: ~$0.05-0.10 per video
- Veo: ~$0.50-1.00 per premium video (optional)

**Monthly:** ~$7-10 tokens + ~$5-20 external APIs = ~$15-30/month total

---

## Troubleshooting

### "Post didn't schedule to Buffer"
- Check Buffer API token is valid
- Verify Instagram account is connected in Buffer
- Check scheduled time is in the future

### "X post rate limit exceeded"
- We hit Twitter's 300 tweets/15min limit
- Wait 15 minutes, retry
- Monitor daily post count (we post 6-12/day, well under limit)

### "Gemini image generation failed"
- Check API key is valid
- Verify API is enabled in Google Cloud
- Try fallback: use Nano for video instead of Gemini for image

### "Reddit post rejected"
- Check subreddit rules (some have automod filters)
- Verify account has karma/age requirements
- Try different subreddit from our list

---

## Next Steps

1. **Set up Buffer** (5 min) — You need to do this
2. **Run first cycle tomorrow morning** — A generates ideas, you approve, posts ship
3. **Monitor engagement** — Check dashboard throughout day
4. **Log learnings** — Every win/failure becomes input for tomorrow's ideas
5. **Weekly synthesis** — Every Friday, review patterns and adjust strategy

---

## Questions?

Each component (`masii_content_generator.py`, etc.) has inline docs.  
Full architecture details in `MARKETING_INFRASTRUCTURE.md`.  
Strategy & brand guidelines in `MARKETING_WORKFLOW_PLAN.md`.  

Ready to launch tomorrow morning. 🚀
