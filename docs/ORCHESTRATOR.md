# Masii — Orchestrator Agent

**Last updated:** 2026-03-03
**Status:** v2 — Revised (Masii brand, all-Indians positioning)

---

## Overview

Masii is the autonomous agent that runs Masii. She's not a chatbot — she's an orchestrator that manages the entire matchmaking pipeline: intake, matching, introductions, feedback, and community engagement. She runs 24/7 without human intervention.

Nik doesn't run Masii. Masii does.

---

## Identity

- **Name:** Masii
- **Archetype:** The matchmaker masi — cultural confidant with a database brain. AI, transparent about it, available to everyone (not just the wealthy)
- **Personality:** Warm, culturally fluent, perceptive, confident in her matches but humble about what she doesn't know. Celebrates connections. Never judgmental.
- **Voice:** Hinglish-natural. "I found someone for you" not "A match has been identified." Family-oriented but modern. Respects tradition without imposing it.

---

## Responsibilities

### 1. Intake Management
- Welcome new users on any channel (WhatsApp, Telegram, Web)
- Conduct progressive profiling (T1 → T2 → T3)
- Handle proxy flows (parents filling for children)
- Manage returning users (load state, resume)
- Cross-channel identity linking (phone = universal key)
- Follow up with incomplete profiles (24h, 72h, 7d nudges)

### 2. Matching Engine
- Run matching algorithm on eligible profiles (MVP threshold met)
- Score all valid pairs, rank by composite score
- Manage match queue (rate-limit: 1/week free, 3/week paid)
- Handle edge cases (small pool, repeated rejections, no matches)
- Present matches with explanations (Masii's reasoning)

### 3. Double Opt-In
- Send match summaries to both parties
- Manage response windows (72h timeout)
- Handle "tell me more" requests
- Execute introductions when both say yes
- Never reveal rejections to the other party

### 4. Feedback Collection
- 7-day post-introduction check-in
- Post-date feedback (if they report a date)
- Monthly check-ins with active users
- Feed feedback into matching algorithm (revealed preferences)

### 5. Community Engagement
- Publish anonymized stats to website (profiles, matches, activity)
- Generate blog content ideas (success patterns, cultural insights)
- Trigger Instagram content via devMKT factory
- Send weekly community digest (opt-in newsletter)

### 6. Payment & Tier Management
- Track user tier (Free, Verified, Premium)
- Trigger verification flows (income, photos)
- Process tier upgrades
- Manage payment collection (Razorpay/Stripe integration)

### 7. Anomaly Detection
- Flag suspicious profiles (fake names, inconsistent answers)
- Detect spam (same message to multiple profiles)
- Monitor for harassment signals
- Escalate to Nik for edge cases

---

## Autonomous Loops

Masii runs several concurrent loops without human intervention:

### Loop 1: Intake Follow-Up (Runs every 6 hours)

```python
async def intake_followup_loop():
    """Nudge users who started but didn't finish."""

    incomplete = get_incomplete_profiles()

    for user in incomplete:
        hours_since_last = hours_since(user.last_activity)

        if hours_since_last > 24 and user.nudge_count == 0:
            send_message(user, NUDGE_24H)
            # "Hey! You were telling me about yourself
            #  yesterday. Want to pick up where we left off?
            #  You're [X]% done."

        elif hours_since_last > 72 and user.nudge_count == 1:
            send_message(user, NUDGE_72H)
            # "Just checking in — your profile is [X]%
            #  complete. A few more answers and I can
            #  start finding matches for you."

        elif hours_since_last > 168 and user.nudge_count == 2:
            send_message(user, NUDGE_7D)
            # "It's been a week! No pressure, but I've
            #  got [N] people in the community who might
            #  be a great fit. Finish your profile whenever
            #  you're ready."

        elif hours_since_last > 720:  # 30 days
            mark_dormant(user)
            # No more nudges. Reactivate if they return.
```

### Loop 2: Matching Run (Runs every 12 hours)

```python
async def matching_loop():
    """Find new matches for all eligible profiles."""

    eligible = get_eligible_profiles()  # MVP threshold met

    for user in eligible:
        # Get all profiles that pass hard filters
        candidates = hard_filter(user, eligible)

        # Score each candidate
        scored = []
        for candidate in candidates:
            if already_matched(user, candidate):
                continue
            if already_rejected(user, candidate):
                continue

            score = calculate_match_score(user, candidate)
            if score and score['confidence'] == 'high' and score['score'] >= 75:
                scored.append((candidate, score))

        # Sort by score, take top match
        scored.sort(key=lambda x: x[1]['score'], reverse=True)

        if scored:
            top_match, top_score = scored[0]

            # Check rate limit
            if matches_this_week(user) < user.match_limit:
                queue_match(user, top_match, top_score)
```

### Loop 3: Match Delivery (Runs every hour)

```python
async def match_delivery_loop():
    """Send queued matches to users."""

    queued = get_queued_matches()

    for match in queued:
        if match.status == 'queued':
            # Send to Person A first
            send_match_summary(match.user_a, match)
            match.status = 'awaiting_a'
            match.sent_to_a_at = now()

        elif match.status == 'awaiting_a':
            if match.response_a == 'yes':
                # Person A said yes, send to Person B
                send_match_summary(match.user_b, match)
                match.status = 'awaiting_b'
                match.sent_to_b_at = now()

            elif match.response_a == 'no':
                match.status = 'rejected_by_a'
                log_rejection(match.user_a, match, match.rejection_reason_a)

            elif hours_since(match.sent_to_a_at) > 72:
                match.status = 'expired_a'
                send_message(match.user_a, MATCH_EXPIRED)

        elif match.status == 'awaiting_b':
            if match.response_b == 'yes':
                # Both said yes! Make the introduction
                send_introduction(match)
                match.status = 'introduced'
                match.introduced_at = now()

                # Schedule feedback check-in
                schedule_feedback(match, days=7)

            elif match.response_b == 'no':
                match.status = 'rejected_by_b'
                log_rejection(match.user_b, match, match.rejection_reason_b)
                # Don't tell Person A about the rejection

            elif hours_since(match.sent_to_b_at) > 72:
                match.status = 'expired_b'
                # Don't tell Person A
```

### Loop 4: Feedback Collection (Runs daily)

```python
async def feedback_loop():
    """Check in on introduced matches."""

    due_feedbacks = get_feedback_due()

    for match in due_feedbacks:
        days_since_intro = days_since(match.introduced_at)

        if days_since_intro == 7 and not match.feedback_7d:
            # First check-in
            send_feedback_request(match.user_a, match, '7d')
            send_feedback_request(match.user_b, match, '7d')

        elif days_since_intro == 30 and not match.feedback_30d:
            # Monthly check-in
            send_feedback_request(match.user_a, match, '30d')
```

### Loop 5: Website Stats Publisher (Runs every 6 hours)

```python
async def stats_publisher_loop():
    """Publish anonymized stats to the website."""

    stats = {
        'total_profiles': count_active_profiles(),
        'matches_this_month': count_matches(period='month'),
        'introductions_this_month': count_introductions(period='month'),
        'cities_represented': count_unique_cities(),
        'avg_match_score': avg_match_score(),
        'top_cities': get_top_cities(limit=5),
        'newest_milestone': get_latest_milestone(),
        # e.g., "100th profile created!" or "First match in London!"
    }

    # Write to a public JSON endpoint that the website reads
    publish_stats(stats)

    # Check for blog-worthy events
    if stats['matches_this_month'] % 10 == 0:
        trigger_blog_draft(
            f"Masii made {stats['matches_this_month']} matches this month"
        )
```

### Loop 6: Anomaly Detection (Runs daily)

```python
async def anomaly_detection_loop():
    """Flag suspicious activity."""

    # Check for duplicate profiles (same phone, different names)
    duplicates = find_duplicate_phones()

    # Check for incomplete profiles older than 30 days
    stale = find_stale_profiles(days=30)

    # Check for users who rejected 5+ matches
    serial_rejecters = find_serial_rejecters(threshold=5)

    # Check for rapid profile creation (bot/spam signal)
    rapid_creation = find_rapid_creation(threshold=5, period='1h')

    for anomaly in [*duplicates, *stale, *serial_rejecters, *rapid_creation]:
        create_alert(anomaly)
        if anomaly.severity == 'high':
            notify_nik(anomaly)
```

---

## State Machine

Masii tracks every user through a state machine:

```
                    ┌─────────┐
                    │  NEW     │ User sent first message
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ INTAKE   │ Answering questions
                    │ IN       │ (T1 in progress)
                    │ PROGRESS │
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼────┐ ┌──▼───┐ ┌───▼────┐
         │ T1      │ │PAUSED│ │DORMANT │
         │ COMPLETE│ │      │ │(30d    │
         │         │ │      │ │ idle)  │
         └────┬────┘ └──────┘ └────────┘
              │
         ┌────▼────┐
         │ T2      │ Matching eligible
         │ READY   │ (MVP threshold met)
         └────┬────┘
              │
         ┌────▼──────┐
         │ MATCHING   │ In the matching pool
         │ ACTIVE     │ Masii is looking
         └────┬───────┘
              │
    ┌─────────┼──────────┐
    │         │          │
┌───▼───┐ ┌──▼───┐ ┌───▼────┐
│MATCH  │ │NO    │ │WAITING │
│FOUND  │ │MATCH │ │        │
│       │ │YET   │ │(pool   │
│       │ │      │ │ too    │
│       │ │      │ │ small) │
└───┬───┘ └──────┘ └────────┘
    │
┌───▼──────┐
│AWAITING  │ Match sent, waiting for response
│OPT-IN   │
└───┬──────┘
    │
┌───▼──────┐
│INTRODUCED│ Both said yes, connected
└───┬──────┘
    │
┌───▼──────┐
│FEEDBACK  │ Post-intro check-in
│PENDING   │
└───┬──────┘
    │
┌───▼──────┐
│ACTIVE    │ Ongoing, looking for next match
│(repeat)  │
└──────────┘
```

---

## Communication Schedule

### What Masii sends and when:

| Trigger | Message | Channel |
|---------|---------|---------|
| User starts | Welcome + intake | WhatsApp/Telegram |
| 24h incomplete | Nudge 1 | Same channel |
| 72h incomplete | Nudge 2 | Same channel |
| 7d incomplete | Nudge 3 (final) | Same channel |
| Profile complete | Confirmation + photo prompt | Same channel |
| Match found | Match summary + opt-in request | Preferred channel |
| Both opt-in | Introduction + conversation starter | Both users |
| 7d post-intro | Feedback check-in | Both users |
| 30d post-intro | Long-term check-in | Both users |
| No match (7d) | "Still looking" update | Preferred channel |
| No match (30d) | "Expand your preferences?" suggestion | Preferred channel |
| New milestone | Community announcement | Website + Instagram |
| Weekly | Community digest (opt-in) | Email |

### Message Limits (Anti-Spam)
- Max 1 unsolicited message per day
- Max 3 nudges total for incomplete profiles
- Match messages don't count toward limit
- User can mute Masii for 7/30/forever

---

## Integration Points

### With Website
- Masii publishes stats → website reads from JSON API
- Website sends new signups → Masii picks up on WhatsApp
- Blog ideas generated by Masii → drafted by devMKT content factory

### With Instagram (via devMKT factory)
- Masii flags milestones → trigger reel/post creation
- Content themes: match stories (anonymized), cultural insights, dating advice
- Inbound from Instagram → website → WhatsApp → Masii intake

### With Payment (Future)
- Masii prompts Verified tier after free match success
- Payment link sent via WhatsApp (Razorpay/Stripe)
- Tier upgraded in real-time upon payment confirmation
- Premium: Masii's behavior changes (more proactive, deeper profiling)

---

## Escalation to Nik

Masii handles 95% autonomously. She escalates when:

1. **Anomaly detected** — suspicious profile, spam, harassment
2. **Premium engagement** — new Premium signup needs human matchmaker assignment
3. **Edge case** — user reports issue Masii can't resolve
4. **System error** — database issue, API failure, message delivery failure
5. **Weekly digest** — summary of key metrics, notable events, decisions needed

### Escalation Channel
- Telegram DM to Nik (or a dedicated #jodi-alerts channel)
- Weekly email digest (automated)
- Dashboard (future) for real-time monitoring

---

## Technical Implementation

### Option A: LangGraph (Recommended)

```python
from langgraph.graph import StateGraph

# State
class AgentState(TypedDict):
    user_id: str
    user_state: str  # state machine position
    profile: dict
    current_match: Optional[dict]
    pending_actions: list

# Nodes
graph = StateGraph(AgentState)
graph.add_node("intake", intake_node)
graph.add_node("matching", matching_node)
graph.add_node("opt_in", opt_in_node)
graph.add_node("introduction", introduction_node)
graph.add_node("feedback", feedback_node)
graph.add_node("stats", stats_publisher_node)
graph.add_node("anomaly", anomaly_detection_node)

# Edges (conditional routing based on state)
graph.add_conditional_edges("intake", route_after_intake)
graph.add_conditional_edges("matching", route_after_matching)
# ... etc

# Compile
app = graph.compile()
```

### Option B: Cron + Event-Driven

```
┌─────────────────────────────────────────┐
│  CRON SCHEDULER (Railway/Fly.io)        │
│                                         │
│  Every 1h:  match_delivery_loop()       │
│  Every 6h:  intake_followup_loop()      │
│  Every 6h:  stats_publisher_loop()      │
│  Every 12h: matching_loop()             │
│  Every 24h: feedback_loop()             │
│  Every 24h: anomaly_detection_loop()    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  EVENT HANDLERS (Webhook-driven)        │
│                                         │
│  on_message:   route to intake handler  │
│  on_button:    process opt-in response  │
│  on_photo:     save + moderate          │
│  on_payment:   upgrade tier             │
└─────────────────────────────────────────┘
```

**Recommendation:** Start with Option B (simpler, battle-tested). Migrate to LangGraph when the orchestration complexity justifies it.

---

## Masii's Personality Guide

### How Masii talks:

```
MATCH FOUND:
  "I've been thinking about your profile, and I found
   someone I'm excited about. Can I tell you about them?"

BOTH SAID YES:
  "I love when this happens. You both said yes.
   [Name], meet [Name]. I have a feeling about you two."

FEEDBACK (good):
  "That makes me so happy to hear! This is why I do
   what I do. Keep me posted?"

FEEDBACK (bad):
  "Thanks for being honest. That helps me find someone
   better next time. I'm already looking."

NO MATCH YET:
  "I haven't found the right person yet — and I'd rather
   wait than send you someone who isn't right. I'm looking."

REJECTION (to rejector only):
  "Got it. No need to explain. I'll keep looking."

NUDGE:
  "Hey! Your profile is [X]% done. A few more answers
   and I can start the real work — finding your person."
```

### What Masii never says:
- "Sorry for the delay" (she's not sorry, she's thorough)
- "Unfortunately" (too corporate)
- "As per your preferences" (too formal)
- "No matches available at this time" (too robotic)
- Anything that reveals another person's rejection
