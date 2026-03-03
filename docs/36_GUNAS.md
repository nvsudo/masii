# Masii — The 36 Gunas

Modern matchmaking, rooted in tradition. 36 gunas — not horoscope-based, but life-based.

**Marketing:** "Masii asks 36 questions — like the 36 gunas, but for real life."
**UX:** 6 sections, not 36 questions. Auntie opens the conversation, not a form.

---

## Before the Gunas: The Opening

Masii doesn't start with "What's your name?" She starts with "Let me tell you how this works."

### The Opening Sequence (4 messages, ~1 min)

```
MESSAGE 1 — Who Masii is
━━━━━━━━━━━━━━━━━━━━━━━━
Hey! I'm Masii — your AI matchmaker.

I help people find real, lasting relationships.
I ask questions, I listen, and I find your person.

Think of me as the auntie who knows everyone
and never forgets what you told her.

[Tell me more →]
```

```
MESSAGE 2 — How it works
━━━━━━━━━━━━━━━━━━━━━━━━
Here's how this works:

I'll ask you 36 questions — like the 36 gunas,
but for real life. Not your horoscope. Your values,
your lifestyle, your family, your future.

Takes about 10 minutes. Then I go to work.

When I find someone worth your time, I'll message
you with my reasoning. Both of you say yes?
I make the introduction. For free.

[Sounds good →]
```

```
MESSAGE 3 — Privacy
━━━━━━━━━━━━━━━━━━━━━━━━
One thing first:

Everything you tell me stays between us. I use
your answers to find matches, never to judge.
Some questions are personal — you can skip any
of them. But the more I know, the better the match.

Your data is never sold. Never shared without
your permission.

[Got it →]
```

```
MESSAGE 4 — Intent
━━━━━━━━━━━━━━━━━━━━━━━━
Before we start —

Are you filling this out for yourself
or for someone else?

[For myself]
[For a family member / friend]
```

### If Proxy → Family Flow

```
PROXY MESSAGE 1
━━━━━━━━━━━━━━━
That's sweet. How are you connected to them?

[I'm their parent]
[I'm their sibling]
[I'm their friend]
[Other relative]
```

```
PROXY MESSAGE 2
━━━━━━━━━━━━━━━
Do they know you're doing this?

[Yes, they asked me to]
[Yes, they're okay with it]
[Not yet, I'll tell them]
```

```
IF "Not yet":
No worries. Fill everything out — I'll save it.
But I won't start matching until they say yes.
When they're ready, have them message me and
I'll activate their profile.

[Let's start →]
```

---

## The 36 Gunas

### Section 1: Niyat (Intent) — 4 gunas
*The auntie's first question isn't "what's your name." It's "what are you looking for?"*

**Buy-in:**
```
Let's start with the important stuff —
not your name, not your age. What you
actually want. This helps me understand
what kind of match to look for.

[Let's go →]
```

| # | Guna | Question | Type |
|---|------|----------|------|
| 1 | Intent | What are you looking for? | Button: Marriage / Long-term partner / Open to both |
| 2 | Timeline | How soon? | Button: Ready now / 6 months / 1 year / No rush |
| 3 | Looking for | Looking for a... | Button: Man / Woman |
| 4 | Priority | What matters MOST in a partner? (pick one) | Button: Cultural fit / Values alignment / Lifestyle match / Family compatibility / Ambition match |

**Transition:**
```
Good. Now I know what I'm looking for on your behalf.
Let me learn about you — the basics first. Quick stuff.

[Continue →]
```

---

### Section 2: Parichay (Introduction) — 5 gunas
*The basics. Fast. Buttons only.*

| # | Guna | Question | Type |
|---|------|----------|------|
| 5 | Name | What's your name? | Text |
| 6 | Gender | Gender | Button: Male / Female / Non-binary |
| 7 | Age | When were you born? | Two-step: Year → Month |
| 8 | City | Where are you based? | Tree (see below) |
| 9 | Marital status | Have you been married before? | Button: Never / Divorced / Widowed / Separated |

**Conditional: Marital status**
- If Divorced/Widowed/Separated → "Do you have children?" → Yes (how many) / No

**Conditional: Location tree**
```
Where are you based?
├── India → Which state? → Which city?
├── Outside India → Which country? → Which city?
```

**Transition:**
```
Got it, {name}. Quick and easy ✓

Now — your faith, your culture, your roots.

Not the checkbox version. The real one.

[Let's go →]
```

---

### Section 3: Dharam (Faith & Culture) — 7 gunas
*Not the checkbox version. The real one.*

| # | Guna | Question | Type |
|---|------|----------|------|
| 10 | Religion | Your faith / religion | Button (see tree) |
| 11 | Practice | How practicing are you? | Button (conditional on religion) |
| 12 | Sect / Denomination | → Only if applicable | Button (conditional tree) |
| 13 | Caste / Community | → Only if applicable | Button (conditional tree) |
| 14 | Mother tongue | What's your mother tongue? | Button |
| 15 | Partner religion | Partner's religion — preference? | Button: Same only / Same preferred / Open / Specific |
| 16 | Partner religiosity | How important is their practice level? | Button: Must match / Somewhat important / Doesn't matter |

**Conditional: Religion → Practice level**
```
Hindu → How practicing are you?
         → Very (daily puja, temple weekly)
         → Moderate (festivals, occasional temple)
         → Cultural (identify as Hindu, not practicing)
         → Not really

Muslim → How practicing are you?
         → Very (5 daily prayers, Quran regularly)
         → Moderate (Jummah, Ramadan, Eid)
         → Cultural (identify as Muslim, not strictly practicing)
         → Not really

Sikh   → How practicing are you?
         → Amritdhari (baptized)
         → Keshdhari (keeps hair)
         → Sehajdhari (clean-shaven Sikh)
         → Cultural

Jain   → How practicing are you?
         → Strict (no onion, garlic, root vegetables)
         → Moderate (vegetarian, occasional flexibility)
         → Cultural (identify as Jain, flexible diet)

Christian → How practicing are you?
            → Regular (church weekly, prayer daily)
            → Moderate (church on occasions, holidays)
            → Cultural (identify as Christian, not practicing)

Buddhist / Other / None → Skip practice question
```

**Conditional: Religion → Sect/Denomination**
```
Hindu    → Shaiva / Vaishnava / Arya Samaji / Smartha / None / Other
Muslim   → Sunni / Shia / Sufi / Ahmadiyya / None / Other
Christian → Catholic / Protestant / Orthodox / Evangelical / Other
Sikh     → (skip — practice level covers it)
Jain     → Digambar / Shwetambar / Other
Buddhist / Other / None → Skip
```

**Conditional: Religion → Caste/Community**
```
Hindu → Brahmin / Rajput-Kshatriya / Baniya-Vaishya / Kayastha / Maratha /
        Reddy / Nair / Ezhava / Patel / Agarwal / Other / Prefer not to say
        → IF answered: "How important is caste in your partner?"
           → Very / Somewhat / Doesn't matter

Jain  → Agarwal / Oswal / Porwal / Digambar / Shwetambar / Other
        → Same follow-up

Sikh  → Jat / Khatri / Arora / Ramgarhia / Saini / Other
        → Same follow-up

Muslim    → Skip caste. No follow-up.
Christian → Skip caste. No follow-up.
Buddhist  → Skip caste. No follow-up.
Other     → Skip caste. No follow-up.
```

**Acknowledgment after section:**
```
✓ Faith & culture — done.

A Jain from Ahmedabad and a Jain from Nairobi
have different lives. I want to understand yours.
```

---

### Section 4: Parivar (Family) — 5 gunas
*Family isn't a red flag. It's a feature.*

**Buy-in:**
```
Now about your family.

You want to choose your person. You also want
your family to be happy with that choice.

I'm matching for both.

[Makes sense →]
```

| # | Guna | Question | Type |
|---|------|----------|------|
| 17 | Family type | Family structure | Button: Nuclear / Joint / Extended |
| 18 | Family involvement | How involved should family be in your search? | Button: Very / Somewhat / I'll tell them after / Not at all |
| 19 | Living situation | Open to living with/near parents? | Button: Yes / Open to it / Prefer not |
| 20 | Want kids | Do you want children? | Button: Yes / No / Already have / Open |
| 21 | Kids timeline | → If Yes: When? | Button: Soon / 2-3 years / Eventually / Not sure |

**Transition:**
```
✓ Family — done.

Now the everyday stuff. Diet, lifestyle, habits.
The things that seem small but end up mattering
a lot when you're building a life together.

[Continue →]
```

---

### Section 5: Jeevan Shaili (Lifestyle) — 7 gunas
*The practical compatibility layer.*

| # | Guna | Question | Type |
|---|------|----------|------|
| 22 | Diet | Your diet | Button (conditional — see below) |
| 23 | Drinking | Alcohol? | Button: Never / Social / Regular |
| 24 | Smoking | Smoking? | Button: Never / Social / Regular |
| 25 | Education | Highest education | Button: High school / Bachelors / Masters / PhD / Professional (MD/JD/CA) / Other |
| 26 | Career | What do you do? | Button: Tech / Finance / Medicine / Law / Business / Creative / Government / Education / Other |
| 27 | Relocation | Open to relocating for the right person? | Button: Yes / Maybe / No |
| 28 | Partner diet | Partner's diet — preference? | Button: Must match mine / Prefer similar / Flexible |

**Conditional: Religion → Diet options**
```
Jain (strict)  → Jain veg (no onion/garlic) / Jain veg (flexible) / Other
Jain (other)   → Jain veg / Vegetarian / Flexible
Hindu          → Vegetarian / Eggetarian / Non-veg / Flexible
Muslim         → Halal non-veg / Non-veg (any) / Vegetarian / Flexible
Sikh           → Vegetarian / Non-veg / Flexible
Christian      → Vegetarian / Non-veg / Flexible
Other/None     → Vegetarian / Vegan / Non-veg / Flexible
```

**Milestone:**
```
You're past the halfway mark ✓

Four more gunas about your values, then we're
done. You're doing great, {name}.
```

---

### Section 6: Soch (Values & Connection) — 8 gunas
*The depth. Mix of buttons and open text.*

**Buy-in:**
```
Last section. This is the good stuff — not what
you look like on paper, but who you actually are.

Two of these are open-ended. Take your time.
The more you write, the better your match.

[Ready →]
```

| # | Guna | Question | Type |
|---|------|----------|------|
| 29 | What matters | What matters most to you in a partner? In your own words. | Open text |
| 30 | Dealbreakers | Anything that's a dealbreaker? Be honest. | Open text |
| 31 | Financial outlook | How important is partner's financial stability? | Button: Very / Somewhat / Not important |
| 32 | Ambition | Where are you in your career? | Button: Climbing / Stable / Building something / Figuring it out |
| 33 | Social energy | You're more... | Button: Introvert / Extrovert / Depends on the day |
| 34 | Conflict | When you disagree with someone, you... | Button: Talk it out / Need space first / Avoid / Compromise fast |
| 35 | Love language | How do you show love? | Button: Words / Touch / Quality time / Gifts / Acts of service |
| 36 | The one thing | One thing Masii should know about you that no question above captured. | Open text |

---

## The Close

```
THE CLOSE — After Guna 36
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{name}, you're in. All 36 gunas — done. ✓

Here's what happens now:

I'm going to look through the community for
someone who fits — not just on paper, but in
real life. Culture, values, lifestyle, family vibe.

When I find someone I'm confident about, I'll
message you with my reasoning. No name, no photo
— just why I think you two should meet.

If you say yes, they see the same about you.
If they say yes too, I make the introduction.

It might take a few days. It might take longer.
I'd rather wait than send you someone who
isn't right.

I'll be in touch. ✓
```

---

## How the Sections Flow

```
OPENING (4 messages)
  Set expectations → Privacy → Intent → Proxy check
  │
SECTION 1: Niyat (Intent) — 4 gunas
  What are you looking for? Timeline? Priority?
  BUY-IN → "Now let me learn about you"
  │
SECTION 2: Parichay (Basics) — 5 gunas
  Name, gender, age, city, marital status
  BUY-IN → "Not the checkbox version. The real one."
  │
SECTION 3: Dharam (Faith & Culture) — 7 gunas ← TREE BRANCHING
  Religion → practice → sect → caste → mother tongue → partner prefs
  ACKNOWLEDGMENT → "Every answer is valid"
  │
SECTION 4: Parivar (Family) — 5 gunas
  BUY-IN → "Choose your person. Family happy too. Matching for both."
  Family type → involvement → living → kids
  │
SECTION 5: Jeevan Shaili (Lifestyle) — 7 gunas ← DIET TREE
  Diet (conditional on religion) → habits → education → career → relocation
  MILESTONE → "Past the halfway mark"
  │
SECTION 6: Soch (Values) — 8 gunas
  BUY-IN → "The good stuff. Who you actually are."
  Open text: what matters, dealbreakers, the one thing
  │
CLOSE
  "You're in. I'll be in touch."
```

---

## Progressive Gunas (Post-Onboarding)

These are NOT asked during initial intake. They come later:

**After first match interaction:**
- Partner age range preference
- Partner education preference
- Partner location preference

**After first introduction:**
- Long-term vision (open text)
- What does partnership look like to you? (open text)

**Monthly check-in:**
- Has anything changed? New city? New priorities?
- Feedback from matches feeds into revealed preferences

---

## Question Count Summary

| Section | Gunas | Actual Qs asked (avg) | Time |
|---------|-------|-----------------------|------|
| Opening | — | 4 messages + proxy | ~1 min |
| Niyat (Intent) | 4 | 4 | ~1 min |
| Parichay (Basics) | 5 | 5-6 (conditional) | ~1.5 min |
| Dharam (Faith) | 7 | 4-7 (tree-dependent) | ~2-3 min |
| Parivar (Family) | 5 | 4-5 (conditional) | ~1.5 min |
| Jeevan Shaili (Lifestyle) | 7 | 7 | ~2 min |
| Soch (Values) | 8 | 8 | ~3 min |
| **Total** | **36** | **28-37 (tree-dependent)** | **~10-13 min** |

A Muslim user answers ~28 questions (no caste tree).
A Hindu user answers ~34 questions (full caste + sect tree).
A Jain user answers ~33 questions (caste + strict diet tree).

Nobody answers all 36 as raw questions. The trees collapse based on context. That's the auntie — she only asks what's relevant.

---

## Matching Weight Map

| Guna | Weight | Role |
|------|--------|------|
| 1 (Intent) | Hard filter | Must align |
| 3 (Looking for) | Hard filter | Must align |
| 7 (Age) | Hard filter | Within preference range |
| 9 (Marital status) | Hard filter | Per preference |
| 10 (Religion) | Heavy | If specified as requirement |
| 11 (Practice) | Heavy | Matched to partner religiosity preference |
| 13 (Caste) | Heavy | Only if user marks as important |
| 22 (Diet) | Heavy | Especially Jain strict |
| 17 (Family type) | Medium | Joint vs nuclear compatibility |
| 18 (Family involvement) | Medium | Both should be similar |
| 25 (Education) | Medium | |
| 26 (Career) | Light | |
| 29 (What matters) | AI-inferred | NLP analysis for value alignment |
| 30 (Dealbreakers) | Hard filter | Binary elimination |
| 36 (The one thing) | AI-inferred | Personality signal |

---

*"36 gunas. 6 conversations. One right person."*
