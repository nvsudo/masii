# Telegram Bot: Complete Button Flow Specification
## All Structured Data Upfront → Then Conversational Mode

**Version 2.0 · February 2026**

---

## Design Philosophy v2

**The insight:** Don't split structured data capture across days. Stack every button-tappable question into one fast session (~8–10 minutes). Users are most motivated at signup — capture everything structured while momentum is high. Then transition to conversational mode for depth, personality, and nuance.

**What changed from v1:**
- Removed artificial T1/T2 boundary during button flow
- Pulled ALL button-capturable T2 fields (lifestyle, preferences) into the upfront session
- Reordered to lead with the top 10 global filters (the questions that eliminate 80% of bad matches)
- Deferred location, name, and identity to AFTER filters (counterintuitive, but filters are what matter for matching — identity is just admin)
- Clearer expectation setting upfront: "quick taps now, real conversation after"
- Edit/change anything later in chat mode, no correction flow needed during buttons

**Result:** One ~8-10 minute button session captures 35-40 structured fields. Zero LLM cost. Then every interaction after is conversational AI building depth.

---

## Flow Structure

```
INTRO (3 messages, 30 sec)
    ↓
PHASE 1: TOP FILTERS — The Big Eliminators (10 screens, ~2 min)
    Religion, Partner religion match, Children, Smoking, Drinking,
    Relationship intent, Timeline, Marital history, Diet, Education pref
    ↓
PHASE 2: IDENTITY & DEMOGRAPHICS (6 screens, ~2 min)
    Gender, Orientation, DOB, Country, City, Nationality/Ethnicity
    ↓
PHASE 3: LIFESTYLE & PREFERENCES (12 screens, ~3 min)
    Work style, Income bracket, Living situation, Exercise,
    Social energy, Travel, Pets, Substance use, Height,
    Partner age range, Location flexibility, Caste/Community
    ↓
PHASE 4: PHOTO + CLOSE (3 screens, ~1 min)
    Photo upload, Summary confirmation, Transition to conversational
    ↓
CONVERSATIONAL MODE BEGINS
    First open-ended question (LLM-driven)
```

**Total button phase: ~25-30 screens, 8-10 minutes, ZERO LLM calls**

---

## INTRO SEQUENCE

### Screen 0: Welcome

**Trigger:** User sends `/start` or taps "Start"

**Bot message:**
```
Hey! 👋 I'm [BotName].

I help serious people find serious relationships.
No swiping. No endless scrolling.

I get to know you deeply, then introduce you
to one great person at a time.
```

**Buttons:**
```
[ Tell me more → ]
```

---

### Screen 1: How It Works

**Bot message:**
```
Here's how this works:

First, I'll ask you some quick-tap questions —
things like what matters to you in a partner,
deal-breakers, lifestyle basics. Takes a few minutes.

After that, we switch to conversation mode — I'll ask
you real questions, you answer in your own words.
That's where the magic happens.

The more I know, the better your matches.
Ready?
```

**Buttons:**
```
[ Let's do it → ]
```

---

### Screen 2: Edit Policy

**Bot message:**
```
One more thing — don't overthink the quick questions.
Pick what feels right.

If you want to change anything later, just tell me
in chat. I can update anything, anytime.

Nothing is locked in. 🔓
```

**Buttons:**
```
[ Got it, start the questions → ]
```

---

## PHASE 1: TOP FILTERS — THE BIG ELIMINATORS

*These are the questions that eliminate the most bad matches, fastest. They go first because they're the highest-value structured data in the entire system. Every one of these becomes an indexed Postgres column.*

### Transition Message:

```
Let's start with what really matters to you.
These help me filter out people who aren't right — fast.
```

---

### Screen F1: Relationship Intent

**Bot message:**
```
What are you looking for?
```

**Buttons:**
```
[ Marriage                ]
[ Long-term relationship  ]
[ Open to either          ]
```

**Storage:** `profiles.relationship_intent` (VARCHAR, indexed)

**Gate:** If someone tries to indicate casual/hookup (via text), respond: *"This service is built for people looking for committed relationships. If that changes, I'm here."* Do not create profile.

---

### Screen F2: Religion

**Bot message:**
```
What's your religion or faith?
```

**Buttons (2 columns):**
```
[ Islam          ]  [ Hinduism       ]
[ Christianity   ]  [ Judaism        ]
[ Sikhism        ]  [ Buddhism       ]
[ Spiritual      ]  [ Not religious  ]
[ Other →        ]
```

**If "Other":** `force_reply` — "What's your faith?"

**Storage:** `profiles.religion` (VARCHAR, indexed)

---

### Screen F3: Religion Practice Level

**Show if:** Religion ≠ "Spiritual" or "Not religious"

**Bot message:**
```
How would you describe your practice?
```

**Buttons:**
```
[ Very practicing / Devout  ]
[ Practicing                ]
[ Cultural / Moderate       ]
[ Not very practicing       ]
```

**Storage:** `profiles.religion_practice` (VARCHAR)

---

### Screen F4: Partner Religion Match

**Bot message:**
```
Does your partner's religion matter?
```

**Buttons:**
```
[ Must be same as mine        ]
[ Prefer same, open to others ]
[ Open to others except some]
[ Doesn't matter              ]
```
**show if:** Open to others, except some -> "What are some religions you're open to?" **storage:** `profiles.preferences' JSONB -> 'partner_religion_notopen_to'` 

**Storage:** `profiles.preferences` JSONB → `partner_religion_pref`

---

### Screen F5: Children Intent

**Bot message:**
```
Do you want children in the future?
```

**Buttons:**
```
[ Definitely yes   ]
[ Probably yes     ]
[ Open to it       ]
[ Probably not     ]
[ Definitely not   ]
```

**Storage:** `profiles.children_intent` (VARCHAR, indexed)

---

### Screen F6: Existing Children

**Bot message:**
```
Do you have children already?
```

**Buttons:**
```
[ No                           ]
[ Yes, they live with me       ]
[ Yes, they don't live with me ]
```

**Storage:** `profiles.has_children` (VARCHAR)

---

### Screen F7: Smoking

**Bot message:**
```
Do you smoke?
```

**Buttons:**
```
[ Never     ]
[ Socially  ]
[ Regularly ]
[ Quitting  ]
```

**Storage:** `profiles.smoking` (VARCHAR, indexed)

---

### Screen F8: Drinking

**Bot message:**
```
Do you drink alcohol?
```

**Buttons:**
```
[ Never            ]
[ Socially         ]
[ Regularly        ]
[ Prefer not to say]
```

**Storage:** `profiles.drinking` (VARCHAR, indexed)

---

### Screen F9: Dietary Preferences

**Bot message:**
```
Any dietary preferences?

(Matters more than people think — shared meals are a big part of life together)
```

**Buttons (2 columns):**
```
[ No restrictions ]  [ Halal          ]
[ Vegetarian      ]  [ Kosher         ]
[ Vegan           ]  [ Jain vegetarian]
[ Other →         ]
```

**Storage:** `profiles.dietary` (VARCHAR)

---

### Screen F10: Marital History

**Bot message:**
```
Have you been married before?
```

**Buttons:**
```
[ Never married ]
[ Divorced      ]
[ Widowed       ]
[ Separated     ]
```

**Storage:** `profiles.marital_history` (VARCHAR, indexed)

---

### Screen F11: Timeline

**Bot message:**
```
How soon are you looking to find someone?
```

**Buttons:**
```
[ Ready now — actively looking ]
[ Within the next year         ]
[ 1-2 years, no rush          ]
[ Just starting to explore     ]
```

**Storage:** `profiles.preferences` JSONB → `timeline`

---

### Screen F12: Education Preference

**Bot message:**
```
Does your partner's education level matter?
```

**Buttons:**
```
[ Must have a degree       ]
[ Postgraduate preferred   ]
[ Doesn't matter           ]
```

**Storage:** `profiles.preferences` JSONB → `education_pref`

---

### Phase 1 → Phase 2 Transition

**Bot message:**
```
Those are the big ones ✓

Now a few quick ones about you.
```

---

## PHASE 2: IDENTITY & DEMOGRAPHICS

### Screen I1: First Name

**Bot message:**
```
What should I call you?
```

**Input type:** `force_reply` — placeholder "Your first name..."

**Validation:** Non-empty, ≤30 chars

**Storage:** `profiles.display_name` (VARCHAR)

**On success:**
```
Nice to meet you, {name} 👋
```

---

### Screen I2: Gender

**Bot message:**
```
How do you identify?
```

**Buttons:**
```
[ Man        ]
[ Woman      ]
[ Non-binary ]
[ Prefer to describe → ]
```

**If "Prefer to describe":** `force_reply`

**Storage:** `profiles.gender` (VARCHAR, indexed)

---

### Screen I3: Orientation

**Bot message:**
```
Who are you looking to meet?
```

**Buttons:**
```
[ Men    ]  [ Women ]
[ Both   ]  [ Other → ]
```

**Storage:** `profiles.orientation` (VARCHAR)

---

### Screen I4: Date of Birth

**Bot message:**
```
When were you born? (DD/MM/YYYY)

I keep your exact date private — only your age shows to matches.
```

**Input type:** `force_reply` — placeholder "DD/MM/YYYY"

**Validation:** Parse date, age 18–80

**Storage:** `profiles.date_of_birth` (DATE, indexed)

**On success:**
```
{age} — got it ✓
```

---

### Screen I5: Country

**Bot message:**
```
Where are you based?
```

**Buttons (2 columns, top markets):**
```
[ 🇮🇳 India       ]  [ 🇦🇪 UAE          ]
[ 🇺🇸 USA         ]  [ 🇬🇧 UK           ]
[ 🇸🇬 Singapore   ]  [ 🇸🇦 Saudi Arabia ]
[ 🇶🇦 Qatar       ]  [ 🇧🇭 Bahrain      ]
[ 🇰🇼 Kuwait      ]  [ 🇵🇰 Pakistan     ]
[ Other →         ]
```

**Storage:** `profiles.country` (VARCHAR, indexed)

---

### Screen I6: City

**Bot message (dynamic by country):**

*India:*
```
Which city?
```
```
[ Mumbai    ]  [ Delhi NCR  ]
[ Bangalore ]  [ Hyderabad  ]
[ Chennai   ]  [ Pune       ]
[ Kolkata   ]  [ Other →    ]
```

*UAE:*
```
[ Dubai      ]  [ Abu Dhabi ]
[ Sharjah    ]  [ Other →   ]
```

*USA:*
```
[ New York    ]  [ SF Bay Area ]
[ Los Angeles ]  [ Chicago     ]
[ Houston     ]  [ Dallas      ]
[ Other →     ]
```

*UK:*
```
[ London      ]  [ Birmingham ]
[ Manchester  ]  [ Other →    ]
```

**Storage:** `profiles.city` (VARCHAR, indexed)

---

### Screen I7: Nationality / Ethnicity

**Bot message:**
```
What's your nationality or ethnicity?
```

**Input type:** `force_reply` — placeholder "e.g. Indian, Pakistani-American, British-Arab..."

**Storage:** `profiles.nationality` (VARCHAR), `profiles.ethnicity` (VARCHAR)

---

### Phase 2 → Phase 3 Transition

**Bot message:**
```
Almost there, {name} — you're flying through this ✓

A few more about your lifestyle and preferences,
then we switch to the good stuff.
```

---

## PHASE 3: LIFESTYLE & PREFERENCES

*These are Tier 2 fields that are button-capturable. Pulling them into the upfront session means when conversational mode starts, the AI already has a rich foundation and can ask deeper, more personalized questions.*

### Screen L1: Work Style

**Bot message:**
```
What's your work situation?
```

**Buttons (2 columns):**
```
[ Corporate / MNC   ]  [ Startup         ]
[ Own business       ]  [ Freelance       ]
[ Government         ]  [ Student         ]
[ Between jobs       ]  [ Prefer not to say]
```

**Storage:** `profiles.work_style` (VARCHAR)

---

### Screen L2: Education Level

**Bot message:**
```
Highest education?
```

**Buttons:**
```
[ High school        ]
[ Bachelor's degree  ]
[ Master's degree    ]
[ PhD / Doctorate    ]
[ Professional (MD, JD, CA, etc.) ]
[ Other              ]
```

**Storage:** `profiles.education_level` (VARCHAR)

---

### Screen L3: Income Bracket

**Bot message:**
```
Roughly what's your annual income range?

(This stays completely private — never shown to matches.
It helps me understand lifestyle compatibility.)
```

**Buttons (dynamic by country/currency):**

*If USD/AED/GBP markets:*
```
[ Under $50K      ]  [ $50K–$100K    ]
[ $100K–$200K     ]  [ $200K–$500K   ]
[ $500K+          ]  [ Prefer not to say ]
```

*If INR market:*
```
[ Under ₹10L      ]  [ ₹10L–₹25L    ]
[ ₹25L–₹50L      ]  [ ₹50L–₹1Cr    ]
[ ₹1Cr+           ]  [ Prefer not to say ]
```

**Storage:** `profiles.preferences` JSONB → `income_bracket`

---

### Screen L4: Living Situation

**Bot message:**
```
Current living situation?
```

**Buttons:**
```
[ Live alone           ]
[ With roommates       ]
[ With family          ]
[ Own my place         ]
[ Other                ]
```

**Storage:** `profiles.preferences` JSONB → `living_situation`

---

### Screen L5: Exercise / Fitness

**Bot message:**
```
How active are you?
```

**Buttons:**
```
[ Very active — daily exercise  ]
[ Active — few times a week     ]
[ Moderate — occasional         ]
[ Not very active               ]
```

**Storage:** `profiles.preferences` JSONB → `fitness_level`

---

### Screen L6: Social Energy

**Bot message:**
```
At a party, you're more likely to...
```

**Buttons:**
```
[ Work the room — love meeting new people  ]
[ Stick with people I know                 ]
[ Find one person and have a deep convo    ]
[ Wonder why I came                        ]
```

**Storage:** `profiles.personality_data` JSONB → `social_energy`

*Note: This one's sneakily capturing introvert/extrovert signal through a scenario rather than a label. Better data quality than asking "are you an introvert?"*

---

### Screen L7: Travel

**Bot message:**
```
How much do you travel?
```

**Buttons:**
```
[ Homebody — love being home      ]
[ A few trips a year              ]
[ Travel frequently               ]
[ Digital nomad / constantly moving]
```

**Storage:** `profiles.personality_data` JSONB → `travel_frequency`

---

### Screen L8: Pets

**Bot message:**
```
Pets?
```

**Buttons:**
```
[ Have pets 🐾     ]
[ Want pets        ]
[ No pets, no plans]
[ Allergies 😬     ]
```

**Storage:** `profiles.preferences` JSONB → `pets`

---

### Screen L9: Substance Use

**Bot message:**
```
Any recreational substance use? (Cannabis, etc.)
```

**Buttons:**
```
[ Never            ]
[ Occasionally     ]
[ Regularly        ]
[ Prefer not to say]
```

**Storage:** `profiles.preferences` JSONB → `substance_use`

---

### Screen L10: Height

**Bot message:**
```
How tall are you? (Optional)
```

**Buttons (2 columns):**
```
[ Under 5'2" / <157cm  ]  [ 5'2"–5'5" / 157–165cm ]
[ 5'5"–5'8" / 165–173cm]  [ 5'8"–5'11" / 173–180cm]
[ 5'11"–6'1" / 180–185cm] [ 6'1"+ / 185cm+        ]
[ Skip                  ]
```

**Storage:** `profiles.height_range` (VARCHAR)

---

### Screen L11: Partner Age Range

**Bot message:**
```
What age range works for you in a partner?

Youngest:
```

**Buttons (dynamic, centered around user's age ±10):**
```
[ 22 ] [ 24 ] [ 26 ] [ 28 ] [ 30 ] [ 32 ]
```

**After selection:**
```
Oldest:
```
```
[ 30 ] [ 32 ] [ 34 ] [ 36 ] [ 38 ] [ 40+ ]
```

**Storage:** `profiles.preferences` JSONB → `partner_age_min`, `partner_age_max`

---

### Screen L12: Location Flexibility

**Bot message:**
```
Does your partner need to be in {city}?
```

**Buttons:**
```
[ Same city only        ]
[ Same country is fine  ]
[ Open to distance      ]
[ Open to relocating    ]
```

**Storage:** `profiles.preferences` JSONB → `location_flexibility`

---

### Screen L13: Caste / Community (Conditional)

**Show ONLY if:** Country = India/Pakistan/Bangladesh AND religion ∈ {Hindu, Muslim, Sikh, Jain, Buddhist}

**Bot message:**
```
Does community matter for your match?

(No judgment — just want to filter right for you)
```

**Buttons:**
```
[ Must be same community     ]
[ Prefer same, flexible      ]
[ Doesn't matter at all      ]
```

**If "Must be same" or "Prefer same":**
```
What's your community?
```
`force_reply` — placeholder "e.g. Brahmin, Patel, Sunni, Rajput..."

**Storage:** `profiles.caste_community` (VARCHAR), `profiles.preferences` JSONB → `caste_pref`

---

### Screen L14: Family Involvement (Conditional)

**Show ONLY if:** Country ∈ {India, Pakistan, Bangladesh, Saudi Arabia, UAE, Qatar, Kuwait, Bahrain} OR religion ∈ {Islam, Hinduism, Sikhism}

**Bot message:**
```
Is your family involved in your search?
```

**Buttons:**
```
[ Yes, actively helping  ]
[ They know I'm looking  ]
[ They don't know yet    ]
[ Keeping this private   ]
```

**Storage:** `profiles.preferences` JSONB → `family_involvement`

---

## PHASE 4: PHOTO + CLOSE

### Phase 3 → 4 Transition

**Bot message:**
```
That's all the quick questions done, {name} ✓

One last thing before we switch to conversation mode —
```

---

### Screen P1: Photo Upload

**Bot message:**
```
I need at least one recent photo of you.

It stays private — only shared when I introduce you
to a match, and only with your approval.

Send me a clear photo where your face is visible 📸
```

**Input:** Photo message

**Validation:** Must contain a photo (not file). Basic check. If unclear: "Could you try one with better lighting? I need to see your face clearly."

**After upload:**
```
Great photo ✓ Want to add more? Better photos = better first impressions.
```

**Buttons:**
```
[ Add another photo ]  [ That's enough ]
```

**Storage:** `profiles.photos` (ARRAY of object storage URLs)

---

### Screen P2: Quick Summary

**Bot message:**
```
Here's a quick snapshot:

{name}, {age} · {city}, {country}
{religion} ({practice_level}) · Looking for {intent}
{orientation} · {partner_age_min}–{partner_age_max}

If anything looks off, just tell me later in chat
and I'll fix it instantly.
```

**Buttons:**
```
[ Looks good → ]
```

*Note: No "fix something" flow here. They can change anything conversationally later. This reduces friction and keeps momentum toward the conversational transition.*

---

### Screen P3: The Transition 🎯

**This is the most important message in the entire flow. It's the bridge from form-mode to relationship-mode.**

**Bot message:**
```
You're in, {name} ✓

I now know your basics and your filters. That's about
25% of what I need to find you someone great.

Here's what happens next:

The quick-tap stuff tells me who to filter OUT.
The conversation tells me who to filter IN.

Starting now, I'll ask you real questions — the kind
a good friend would ask if they were setting you up.
Answer in your own words, whenever you feel like it.

There's no rush. The more I understand you,
the better your first introduction will be.

Ready for the first one?
```

**Buttons:**
```
[ Ask me something → ]  [ I'll come back later ]
```

**If "Ask me something":** Trigger first LLM-driven conversational question.

**If "Come back later":** Schedule first drip question for next day.

**Storage:** Update `users.intake_tier` = 1, `users.button_phase_completed_at` = NOW()

---

## FIRST CONVERSATIONAL QUESTION (LLM Mode Begins)

**This is the first LLM-generated message. The system prompt includes all structured data collected above. The controller's target field is "weekend pattern / lifestyle depth."**

**Example first message (LLM-generated, not template):**
```
Okay {name}, here's one I love asking —

Describe your ideal Saturday. Not the Instagram
version — the real one. What does a genuinely
great day off look like for you?
```

**From here forward:** Every interaction is LLM-driven conversational mode, using the intake controller architecture (deterministic target field selection + LLM execution) described in the conversational exposure management spec.

---

## Implementation Summary

### Complete Field Count — Button Phase

| Phase | Fields Captured | Type | Screens | Time |
|-------|----------------|------|---------|------|
| Phase 1: Top Filters | 12 | All indexed columns | 12 | ~2.5 min |
| Phase 2: Identity | 7 | All indexed columns | 7 | ~2 min |
| Phase 3: Lifestyle & Prefs | 14 | Mix of columns + JSONB | 12-14 | ~3 min |
| Phase 4: Photo + Close | 1 + summary | Object storage | 3 | ~1 min |
| **TOTAL** | **34-36 fields** | | **~30 screens** | **~8-10 min** |

### What's Left for Conversational Mode

After the button phase, the following Tier 2 fields remain for conversational capture:

| Field | Why Conversational (Not Button) |
|-------|-------------------------------|
| Weekend pattern | Open-ended, reveals personality |
| Work-life balance | Nuance — "workaholic" means different things |
| Financial style | Saver/spender is too reductive as buttons |
| Food culture | "Foodie" needs context |
| Love language | Better inferred from stories than self-labeled |
| Conflict style | Self-report is unreliable, infer from stories |
| Independence needs | Needs context |
| Past relationships | Sensitive, needs conversational trust |
| Green flags / Red flags | Rich, personal, open-ended |
| All values & worldview | Inferred from conversation, not self-labeled |
| All Tier 3 (psychological) | 100% inferred |
| All Tier 4 (calibration) | 100% post-match |

### Cost Model

| Phase | Cost per User | Latency |
|-------|--------------|---------|
| Button phase (34-36 fields) | $0.00 | <100ms per screen |
| Conversational mode (ongoing) | ~$0.02-0.05 per session | 1-3 sec per response |
| First month total (est. 15 sessions) | ~$0.30-0.75 per user | — |

### State Management

```json
{
    "current_phase": "FILTERS",
    "current_screen": "F7",
    "completed_screens": ["F1","F2","F3","F4","F5","F6"],
    "skipped_screens": [],
    "conditional_screens_shown": ["L13","L14"],
    "button_phase_complete": false,
    "conversational_mode_active": false,
    "started_at": "2026-02-12T10:30:00Z",
    "last_active": "2026-02-12T10:34:00Z"
}
```

### Error Handling

| Scenario | Response |
|----------|----------|
| Text sent when button expected | "Just tap one of the options above 👆" |
| Sticker/gif during button phase | "😄 Save that energy — just tap a button for now, we'll chat properly soon." |
| Idle >5 min during button phase | No action. Resume where they left off when they return. |
| Idle >24 hours during button phase | "Hey {name}, we were getting through the quick questions — want to pick up where we left off?" + [ Resume → ] |
| Wants to change an answer mid-flow | "No worries — once we finish the quick questions, you can tell me in chat and I'll update anything." |
| /start again after partial completion | Resume from last incomplete screen, never restart |

---

## Key Design Decisions & Rationale

### Why filters before identity?

Traditional forms ask "who are you?" first. We ask "what matters to you?" first. This signals that the service is about finding the right match, not building a dating profile. It also means if a user drops off after 5 minutes, we at least have their deal-breakers — the most valuable structured data for matching.

### Why no correction flow during buttons?

v1 had a "let me fix something" option at the summary screen that routed users back to specific screens. This creates complexity and interrupts momentum. Instead: show the summary, tell them they can change anything later in chat. The conversational AI can handle "actually, I put the wrong religion" trivially. This keeps the button phase linear and fast.

### Why pull T2 lifestyle fields into the button phase?

Fields like fitness level, social energy, travel frequency, and work style are technically Tier 2 (not hard filters) but they're perfectly capturable via buttons. Leaving them for conversational mode wastes LLM calls on questions that have 4-5 discrete answers. The rule: if a field has ≤6 possible answers, it's a button. If it needs nuance, it's conversational.

### Why the party question for social energy?

"Are you an introvert or extrovert?" gets unreliable self-reports. "At a party, you're more likely to..." captures the same signal through a scenario. People are more accurate describing behavior than labeling themselves. This principle should extend to conversational mode too — ask about situations, not self-assessments.

### The transition message matters more than any single question

Screen P3 is where the user's mental model shifts from "I'm filling out a form" to "I'm talking to someone who's getting to know me." The line *"The quick-tap stuff tells me who to filter OUT. The conversation tells me who to filter IN."* is doing real work — it explains why both phases exist and motivates engagement with the conversational phase.

---

*End of Button Flow Specification · v2.0*
