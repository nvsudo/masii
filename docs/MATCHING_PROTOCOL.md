# Masii — Matching Protocol

**Last updated:** 2026-03-03
**Status:** Draft v1

---

## Overview

The matching protocol is Masii's core engine. It determines who sees whom, when, and why. It runs autonomously — no human in the loop for standard matches.

The goal is not "give them options." The goal is "find the right person." Fewer, better matches. Conviction, not volume.

---

## Matching Philosophy

### 1. Fewer matches, higher conviction
Traditional apps: "Here are 50 profiles. Good luck."
Masii: "Here's one person. Here's why. Both of you said yes."

### 2. Hard filters are non-negotiable
If someone says "Hindu only" — that's absolute. No "but they're great otherwise." Respecting dealbreakers builds trust.

### 3. Soft signals are where the magic is
Two people who are both vegetarian, value family time over nightlife, want kids in 2-3 years, and speak Gujarati at home — that's compatibility that no checkbox captures.

### 4. Context beats demographics
A 32-year-old doctor in Melbourne and a 29-year-old engineer in Sydney — the algorithm shouldn't care about the 3-year age gap if everything else aligns. Context > numbers.

### 5. The algorithm gets smarter
Every "yes" and every "no" after a match teaches the system. Revealed preferences > stated preferences over time.

---

## Architecture

```
Profile A                           Profile B
    │                                   │
    ▼                                   ▼
┌─────────────────────────────────────────────┐
│           STAGE 1: HARD FILTERS             │
│                                             │
│  Eliminate impossible matches.              │
│  Binary pass/fail. No scoring.              │
│                                             │
│  - Gender/orientation alignment             │
│  - Age within preference range (±2 buffer)  │
│  - Location compatibility                   │
│  - Religion (if dealbreaker)                │
│  - Marital status (if dealbreaker)          │
│  - Children (if dealbreaker)                │
│  - Diet (if dealbreaker)                    │
│  - Smoking/drinking (if dealbreaker)        │
│                                             │
│  Result: PASS or ELIMINATE                  │
└──────────────────┬──────────────────────────┘
                   │
                   │ Passed hard filters
                   ▼
┌─────────────────────────────────────────────┐
│           STAGE 2: COMPATIBILITY SCORE      │
│                                             │
│  Weighted scoring across dimensions.        │
│  0-100 scale. Each dimension 0-10.          │
│                                             │
│  Dimensions (see scoring below)             │
└──────────────────┬──────────────────────────┘
                   │
                   │ Score calculated
                   ▼
┌─────────────────────────────────────────────┐
│           STAGE 3: CONFIDENCE CHECK         │
│                                             │
│  Is the score reliable?                     │
│                                             │
│  - Both profiles >45% complete?             │
│  - Score based on >5 data points?           │
│  - No conflicting signals?                  │
│                                             │
│  High confidence: present match             │
│  Low confidence: hold for more data         │
└──────────────────┬──────────────────────────┘
                   │
                   │ High confidence + score ≥ 75
                   ▼
┌─────────────────────────────────────────────┐
│           STAGE 4: MATCH QUEUE              │
│                                             │
│  Ranked by score. Rate-limited.             │
│  Max 1 match per week (free tier).          │
│  Max 3 matches per week (verified/premium). │
│                                             │
│  Score ≥ 87: Free introduction              │
│  Score 75-86: Free introduction             │
│  Score 60-74: Shown to paid tiers only      │
│  Score <60: Not shown                       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
            DOUBLE OPT-IN
         (see flow below)
```

---

## Scoring Dimensions

### Dimension Weights

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Cultural Alignment | 20% | Religion, caste importance, language, family values |
| Lifestyle Match | 18% | Diet, habits, social style, fitness, pets |
| Life Stage | 15% | Age proximity, marriage timeline, children intent |
| Location Compatibility | 12% | Same city/country, relocation willingness |
| Education & Career | 10% | Education level, ambition alignment |
| Values & Personality | 15% | Conflict style, emotional availability, politics |
| Family Dynamics | 10% | Family type, parent involvement, living situation |

**Total: 100%**

### Scoring Rules

#### Cultural Alignment (0-10, weight 20%)

```
Same religion + same importance level     → 10
Same religion, different practice level   → 7
Different religion, both "open"           → 5
Different religion, one strict            → 2
Dealbreaker conflict                      → ELIMINATE (Stage 1)

Same caste + caste matters to both        → +2 bonus
Same mother tongue                        → +1 bonus
Same sub-community (e.g., Patel)          → +1 bonus
```

#### Lifestyle Match (0-10, weight 18%)

```
Same diet                                 → 3/3
Compatible diet (one flexible)            → 2/3
Incompatible diet (veg + non-veg strict)  → 0/3

Same smoking/drinking habits              → 2/2
One tolerant of other's habits            → 1/2
Both strict, opposite habits              → ELIMINATE

Similar social style                      → 2/2
Similar weekend preferences               → 1.5/1.5
Similar fitness level                     → 1.5/1.5
```

#### Life Stage (0-10, weight 15%)

```
Age within preference range               → 3/3
Age within ±2 buffer                      → 2/3
Age outside range                         → 0/3

Same children intent                      → 4/4
One flexible on children                  → 2/4
Opposite children intent                  → ELIMINATE

Similar marriage timeline                 → 3/3
Different but overlapping timeline        → 1.5/3
Incompatible timeline                     → 0/3
```

#### Location Compatibility (0-10, weight 12%)

```
Same city                                 → 10
Same country, different city              → 7
Different country, one willing to relocate→ 5
Different country, both open              → 4
Different country, neither relocates      → 1
```

#### Education & Career (0-10, weight 10%)

```
Both meet each other's education min      → 5/5
One below other's preference              → 3/5
Both below each other's preference        → 1/5

Similar ambition level                    → 5/5
One ambitious, one balanced               → 3/5
Opposite ambition levels                  → 1/5
```

#### Values & Personality (0-10, weight 15%)

```
Same conflict resolution style            → 3/3
Compatible styles                         → 2/3
Opposite styles (avoidant + confronter)   → 1/3

Similar emotional availability            → 3/3
Similar love language (top 2 overlap)     → 2/2
Similar political alignment               → 2/2
```

#### Family Dynamics (0-10, weight 10%)

```
Compatible family involvement pref        → 4/4
One flexible on family involvement        → 2/4
Incompatible (wants family + wants none)  → 0/4

Compatible living situation               → 3/3
One flexible on living with parents       → 2/3

Similar family financial status           → 3/3
Different but within 1 level              → 2/3
Very different                            → 1/3
```

---

## Composite Score Calculation

```python
def calculate_match_score(profile_a, profile_b):
    scores = {}

    # Stage 1: Hard filters (binary elimination)
    if not pass_hard_filters(profile_a, profile_b):
        return None  # Eliminated

    # Stage 2: Dimension scoring
    scores['cultural']   = score_cultural(a, b)    # 0-10
    scores['lifestyle']  = score_lifestyle(a, b)   # 0-10
    scores['life_stage'] = score_life_stage(a, b)  # 0-10
    scores['location']   = score_location(a, b)    # 0-10
    scores['education']  = score_education(a, b)   # 0-10
    scores['values']     = score_values(a, b)      # 0-10
    scores['family']     = score_family(a, b)      # 0-10

    # Weighted composite
    weights = {
        'cultural': 0.20, 'lifestyle': 0.18, 'life_stage': 0.15,
        'location': 0.12, 'education': 0.10, 'values': 0.15,
        'family': 0.10
    }

    composite = sum(scores[d] * weights[d] for d in scores)

    # Scale to 0-100
    match_score = round(composite * 10, 1)

    # Stage 3: Confidence check
    confidence = calculate_confidence(profile_a, profile_b, scores)

    return {
        'score': match_score,
        'confidence': confidence,  # 'high', 'medium', 'low'
        'dimensions': scores,
        'explanation': generate_explanation(scores, weights)
    }
```

### Confidence Calculation

```python
def calculate_confidence(a, b, scores):
    # How many dimensions had sufficient data?
    data_points_a = count_answered_fields(a)
    data_points_b = count_answered_fields(b)

    # Minimum: both profiles must be 45%+ complete
    if min(a.completeness, b.completeness) < 0.45:
        return 'low'

    # Count dimensions with actual data (not defaults)
    dimensions_with_data = sum(
        1 for d in scores
        if has_real_data(a, d) and has_real_data(b, d)
    )

    if dimensions_with_data >= 6:
        return 'high'
    elif dimensions_with_data >= 4:
        return 'medium'
    else:
        return 'low'
```

---

## Double Opt-In Flow

This is the core experience. Both people must say yes before an introduction happens.

```
MATCH FOUND (score ≥ 75, confidence high)
    │
    ▼
┌─────────────────────────────────────┐
│  PERSON A receives message:         │
│                                     │
│  "Masii found someone for you.      │
│                                     │
│   Name: [First name only]           │
│   Age: [Age]                        │
│   Location: [City, Country]         │
│   Match strength: 89%               │
│                                     │
│   Why Masii thinks you'd click:     │
│   - Both value family time          │
│   - Both Gujarati speakers          │
│   - Similar career ambition         │
│   - Both want kids in 2-3 years     │
│                                     │
│   Want to meet them?                │
│   [Yes, I'm interested]             │
│   [Not this time]                   │
│   [Tell me more first]"             │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
   YES    NOT NOW    TELL MORE
    │         │          │
    │         │          └→ Show 2-3 more details
    │         │             (education, diet, lifestyle)
    │         │             Then ask again: Yes/No
    │         │
    │         └→ Log rejection reason (optional)
    │            "What didn't appeal?"
    │            → Feed into revealed preferences
    │
    ▼
┌─────────────────────────────────────┐
│  PERSON B receives same message     │
│  (with Person A's details)          │
│                                     │
│  Same options: Yes / Not now /      │
│  Tell me more                       │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
   YES     NOT NOW    TELL MORE
    │         │
    │         └→ Log reason, don't notify A
    │            (never reveal rejection)
    │
    ▼
BOTH SAID YES
    │
    ▼
┌─────────────────────────────────────┐
│  INTRODUCTION                       │
│                                     │
│  "Great news! You both said yes.    │
│                                     │
│   [Name] is excited to meet you.    │
│                                     │
│   Here's their full profile:        │
│   [Expanded details]                │
│                                     │
│   Their WhatsApp: [number]          │
│   (or) We'll connect you in a       │
│   group chat.                       │
│                                     │
│   Masii's tip: Ask about [shared    │
│   interest]. That's what makes      │
│   you two a great match."           │
└──────────────┬──────────────────────┘
               │
               ▼
         FEEDBACK LOOP
         (7 days later)
```

### Timing Rules

- Person A is contacted first (randomly selected)
- Person A has 72 hours to respond
- If Person A says yes, Person B is contacted within 1 hour
- Person B has 72 hours to respond
- If both say yes, introduction sent within 1 hour
- If either says no, the other is never told (no rejection signal)
- "Not now" ≠ "never" — the match stays in queue, resurfaces in 30 days

### What's Shown vs Hidden

**Before opt-in (summary only):**
- First name
- Age
- City, Country
- Match score
- 3-4 compatibility highlights
- General education level
- General career field

**After mutual opt-in (full profile):**
- Full name
- Photos (if uploaded)
- Detailed profile
- Contact info (WhatsApp number)
- Masii's conversation starter suggestion

**Never shown:**
- Income (unless both Verified tier)
- Rejection reasons
- Other matches they were shown
- Score breakdown details

---

## Feedback Loop

### Post-Introduction Check-In (Day 7)

```
"Hey [Name]! It's been a week since I connected you with [Match].

How's it going?

[We've been talking - it's going well]
[We connected but no spark]
[We haven't connected yet]
[Prefer not to say]"
```

### Post-Date Feedback (If they report a date)

```
"How was meeting [Match] in person?

Chemistry:  [1-5 stars]
Conversation: [1-5 stars]
Would you meet again? [Yes / Maybe / No]

Anything Masii should know for future matches?"
```

### How Feedback Improves Matching

```python
# Revealed preference learning
if user_said_yes_to_match and date_went_well:
    # Strengthen similar dimension weights for this user
    boost_weights(user, match.high_scoring_dimensions)

if user_said_no_to_match:
    # Analyze which dimensions were low
    weak_dims = get_low_dimensions(user, rejected_match)
    # Increase weight of those dimensions for this user
    adjust_weights(user, weak_dims, direction='up')

if user_said_yes_but_date_was_bad:
    # Profile looked good on paper, didn't work in person
    # This is the most valuable signal
    # Something the algorithm missed — personality? Chemistry?
    flag_for_analysis(user, match, feedback)
```

---

## Match Presentation: What Masii Says

### The Explanation Template

Masii doesn't just say "87% match." She tells a story:

```
"I think you two would really get along. Here's why:

You're both Gujarati speakers who grew up abroad but stayed
connected to the culture. [Name] is a [profession] in [city]
— similar career drive to yours.

What stood out: you both said family time is more important
than nightlife, you both want kids in the next 2-3 years,
and you're both vegetarian. That alignment on the daily
stuff is what makes relationships work.

One thing that's different: [Name] grew up in [country] while
you grew up in [country]. But you're both open to relocation,
so geography isn't a barrier.

Match strength: 89%"
```

### Explanation Generation Rules

1. **Lead with commonality** — what they share
2. **Be specific** — "both vegetarian" not "lifestyle match"
3. **Acknowledge differences honestly** — "one thing that's different"
4. **Frame differences positively** — "but you're both open to..."
5. **End with conviction** — the score, stated confidently
6. **Cultural context** — reference shared cultural signals

---

## Edge Cases

### Asymmetric Matches
Person A scores Person B at 90%. Person B scores Person A at 72%.
- Use the lower score as the match score (conservative)
- Require both directions to pass threshold

### Small Pool
Early days: may not have enough profiles for high-confidence matches.
- Lower threshold to 70% for first 100 profiles
- Be transparent: "Masii is still building the community. Fewer matches, but they'll be meaningful."
- Never pad with low-quality matches just to show activity

### Repeated Rejections
User has rejected 5+ matches in a row.
- Masii checks in: "I notice the last few matches haven't felt right. Can you help me understand what I'm missing?"
- Trigger a mini re-profiling conversation
- Adjust weights based on rejection patterns

### No Matches Available
- Don't ghost the user. Masii messages: "I haven't found the right match yet. I'm looking. I'll reach out when I find someone worth your time."
- Weekly "still searching" update if >2 weeks without a match

---

## Algorithm Evolution

### V1 (Launch)
- Hard filters + weighted scoring (as described above)
- Rule-based dimension scores
- Static weights per dimension

### V2 (Month 3)
- Per-user weight adjustment based on feedback
- Revealed preference learning
- Cluster analysis (find "types" that match well)

### V3 (Month 6)
- LLM-powered compatibility analysis
- Conversation analysis (how they answered, not just what)
- Semantic matching on open-ended responses (values, goals, dealbreakers)

### V4 (Year 1)
- Full Tier 4 calibration loop
- Matchmaker agent consultation for premium
- Cross-community matching (Gujarati-Marathi, etc.)
