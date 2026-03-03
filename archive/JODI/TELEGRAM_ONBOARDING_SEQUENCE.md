# JODI Telegram Onboarding — Complete User Experience Sequence

**From first /start to end of structured intake**  
**Total time: ~10-12 minutes | ~37 screens | Zero LLM calls**

---

## 🎬 INTRO (2-3 minutes)

### Message 1
```
Hey! 👋 I'm Jodi.

I help people find real, lasting relationships.
No swiping. No algorithms optimized to keep you scrolling.

Just one great introduction at a time.
```
**Button:** `[ Tell me more → ]`

---

### Message 2
```
Before we start — something important.

This is your space. Whatever you share here is between
us. It doesn't go on a profile. It doesn't go on a form.
Your parents won't see it. Your friends won't see it.
No one sees anything unless you approve it.

You can tell me things here that you might not say
out loud — what you actually want, what you've been
through, what matters to you when no one's watching.

I'm not here to judge. I'm here to find you
the right person. The more honest you are with me,
the better I can do that.
```
**Button:** `[ I like that. Keep going → ]`

---

### Message 3 
```
One thing we do differently — photos come at the end
of our process, not the beginning.

We know not everyone photographs well. And honestly,
AI filters have made photos pretty unreliable anyway.

I'd rather understand who you are first — your values,
your energy, what makes you laugh, what you need in
a partner. That's what actually predicts a great match.

Photos matter, but they're not the whole story.
And they're definitely not the first chapter.
```
**Button:** `[ That's refreshing → ]`

---
### Message 4
```
Here's how I find people for you:

I start with your basics and deal-breakers to filter
out anyone who clearly isn't right.

Then I go deeper — personality, values, lifestyle,
the stuff that actually makes two people click.

When I find someone promising, I'll introduce you.
One person at a time, with context on why I think
you'd work well together.
```
**Button:** `[ And then? → ]`

---
### Message 5
```
The best part — I learn as we go.

When I show you a match, your reaction teaches me
something. What excited you. What felt off.
What surprised you.

Even the matches that don't work out make the
next one better. Think of it like a friend who sets you up —
except I remember everything and never stop trying.
```
**Button:** `[ Makes sense → ]`

### Message 6
```
Okay, here's the plan:

First, I'll ask some quick-tap questions —
deal-breakers, lifestyle, the structured stuff.
Takes about 8 minutes. No typing, just tapping.

After that, we switch to real conversation.
I'll ask you questions a good friend would ask
if they were setting you up. Answer whenever
you feel like it — no rush, no pressure.

And if you ever want to change an answer,
just tell me later during our chats. Nothing is locked in.
```
**Button:** `[ Let's start → ]`

---

### Message 7
```
Last thing — your privacy.

🔒 Your data is encrypted and never sold
🔒 Matches only see what you approve
🔒 You can delete everything at any time
🔒 I'll always ask before sharing anything

This only works if we trust each other.
I take that seriously.
```
**Button:** `[ Got it, let's go → ]`

---

## 🔥 PHASE 1: TOP FILTERS (2-3 minutes)


### F1: Relationship Intent
```
What are you looking for?
```
**Buttons:**
```
[ Marriage                ]
[ Long-term relationship  ]
[ Open to either          ]
```

---

### F2: Religion
```
What's your religion or faith?
```
**Buttons (2 columns):**
```
[ ☪️ Islam        ]  [ 🕉️ Hinduism     ]
[ ✝️ Christianity ]  [ ✡️ Judaism      ]
[ ☬ Sikhism      ]  [ ☸️ Buddhism     ]
[ 🔮 Spiritual    ]  [ 🚫 Not religious]
[ 💬 Other →      ]
```

---

### F3: Religion Practice (conditional)
*Shows if not "Spiritual" or "Not religious"*
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

---

### F4: Partner Religion Match
```
Does your partner's religion matter?
```
**Buttons:**
```
[ Must be same as mine          ]
[ Prefer same, open to others   ]
[ Open to others except some    ]
[ Doesn't matter                ]
```
*If "Open except some": Follow-up text input for religions not open to*

---

### F5: Children Intent
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

---

### F6: Existing Children
```
Do you have children already?
```
**Buttons:**
```
[ No                           ]
[ Yes, they live with me       ]
[ Yes, they don't live with me ]
```

---

### F7: Smoking
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

---

### F8: Drinking
```
Do you drink alcohol?
```
**Buttons:**
```
[ Never              ]
[ Socially           ]
[ Regularly          ]
[ Prefer not to say  ]
```

---

### F9: Dietary Preferences
```
Any dietary preferences?

(Matters more than people think — shared meals are a big part of life together)
```
**Buttons (2 columns):**
```
[ No restrictions ]  [ Halal            ]
[ Vegetarian      ]  [ Kosher           ]
[ Vegan           ]  [ Jain vegetarian  ]
[ Other →         ]
```

---

### F10: Marital History
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

---

### F11: Timeline
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

---

### F12: Education Preference
```
Does your partner's education level matter?
```
**Buttons:**
```
[ Must have a degree       ]
[ Postgraduate preferred   ]
[ Doesn't matter           ]
```

---

## 👤 PHASE 2: IDENTITY & DEMOGRAPHICS (2 minutes)

### Transition
```
Those are the big ones ✓

Now a few quick ones about you.
```

---

### I1: First Name
```
What should I call you?
```
**Input:** Text reply (force_reply)  
**Placeholder:** "Your first name..."

**Response:**
```
Nice to meet you, {name} 👋
```

---

### I2: Gender
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

---

### I3: Orientation
```
Who are you looking to meet?
```
**Buttons:**
```
[ Men    ]  [ Women ]
[ Both   ]  [ Other → ]
```

---

### I4: Date of Birth
```
When were you born? (DD/MM/YYYY)

I keep your exact date private — only your age shows to matches.
```
**Input:** Text reply  
**Placeholder:** "DD/MM/YYYY"

**Response:**
```
{age} — got it ✓
```

---

### I5: Country
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

---

### I6: City (dynamic by country)
```
Which city?
```
**Example for UAE:**
```
[ Dubai      ]  [ Abu Dhabi ]
[ Sharjah    ]  [ Other →   ]
```
**Example for India:**
```
[ Mumbai      ]  [ Delhi NCR   ]
[ Bangalore   ]  [ Hyderabad   ]
[ Chennai     ]  [ Pune        ]
[ Kolkata     ]  [ Other →     ]
```

---

### I7: Nationality / Ethnicity
```
What's your nationality or ethnicity?
```
**Input:** Text reply  
**Placeholder:** "e.g. Indian, Pakistani-American, British-Arab..."

---

## 🏃 PHASE 3: LIFESTYLE & PREFERENCES (3 minutes)

### Transition
```
Almost there, {name} — you're flying through this ✓

A few more about your lifestyle and preferences,
then we switch to the good stuff.
```

---

### L1: Work Style
```
What's your work situation?
```
**Buttons (2 columns):**
```
[ Corporate / MNC     ]  [ Startup           ]
[ Own business        ]  [ Freelance         ]
[ Government          ]  [ Student           ]
[ Between jobs        ]  [ Prefer not to say ]
```

---

### L2: Education Level
```
Highest education?
```
**Buttons:**
```
[ High school                      ]
[ Bachelor's degree                ]
[ Master's degree                  ]
[ PhD / Doctorate                  ]
[ Professional (MD, JD, CA, etc.)  ]
[ Other                            ]
```

---

### L3: Income Bracket
```
Roughly what's your annual income range?

(This stays completely private — never shown to matches.
It helps me understand lifestyle compatibility.)
```
**Buttons (USD/AED/GBP markets):**
```
[ Under $50K        ]  [ $50K–$100K    ]
[ $100K–$200K       ]  [ $200K–$500K   ]
[ $500K+            ]  [ Prefer not to say ]
```
**Buttons (INR market):**
```
[ Under ₹10L        ]  [ ₹10L–₹25L    ]
[ ₹25L–₹50L        ]  [ ₹50L–₹1Cr    ]
[ ₹1Cr+             ]  [ Prefer not to say ]
```

---

### L4: Living Situation
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

---

### L5: Exercise / Fitness
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

---

### L6: Social Energy
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

---

### L7: Travel
```
How much do you travel?
```
**Buttons:**
```
[ Homebody — love being home        ]
[ A few trips a year                ]
[ Travel frequently                 ]
[ Digital nomad / constantly moving ]
```

---

### L8: Pets
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

---

### L9: Substance Use
```
Any recreational substance use? (Cannabis, etc.)
```
**Buttons:**
```
[ Never              ]
[ Occasionally       ]
[ Regularly          ]
[ Prefer not to say  ]
```

---

### L10: Height
```
How tall are you? (Optional)
```
**Buttons (2 columns):**
```
[ Under 5'2" / <157cm      ]  [ 5'2"–5'5" / 157–165cm   ]
[ 5'5"–5'8" / 165–173cm    ]  [ 5'8"–5'11" / 173–180cm  ]
[ 5'11"–6'1" / 180–185cm   ]  [ 6'1"+ / 185cm+          ]
[ Skip                      ]
```

---

### L11: Partner Age Range (2-step)
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
**Buttons:**
```
[ 30 ] [ 32 ] [ 34 ] [ 36 ] [ 38 ] [ 40+ ]
```

---

### L12: Location Flexibility
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

---

### L13: Caste / Community (conditional — India/Pakistan/Bangladesh + Hindu/Muslim/Sikh/Jain)
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
**Input:** Text reply  
**Placeholder:** "e.g. Brahmin, Patel, Sunni, Rajput..."

---

### L14: Family Involvement (conditional — South Asia/Gulf countries or Islam/Hinduism/Sikhism)
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

---

## 📸 PHASE 4: PHOTO + CLOSE (1 minute)

### Transition
```
That's all the quick questions done, {name} ✓

One last thing before we switch to conversation mode —
```

---

### P1: Photo Upload
```
I need at least one recent photo of you.

It stays private — only shared when I introduce you
to a match, and only with your approval.

Send me a clear photo where your face is visible 📸
```
**Input:** Photo message

**After upload:**
```
Great photo ✓ Want to add more? Better photos = better first impressions.
```
**Buttons:**
```
[ Add another photo ]  [ That's enough ]
```

---

### P2: Quick Summary
```
Here's a quick snapshot:

{name}, {age} · {city}, {country}
{religion} ({practice_level}) · Looking for {intent}
{orientation} · {partner_age_min}–{partner_age_max}

If anything looks off, just tell me later in chat
and I'll fix it instantly.
```
**Button:**
```
[ Looks good → ]
```

---

### P3: The Transition 🎯
**This is the MOST IMPORTANT message — the bridge from form-mode to relationship-mode**
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

---

## 🗣️ CONVERSATIONAL MODE BEGINS (LLM-driven from here)

**If user taps "Ask me something":**

### First LLM Question (example)
```
Okay {name}, here's one I love asking —

Describe your ideal Saturday. Not the Instagram
version — the real one. What does a genuinely
great day off look like for you?
```
**Input:** Free-form text reply (no buttons)

**From here:** All subsequent interactions are LLM-driven conversational depth-building using the conversational state controller.

---

## 📊 SUMMARY

| Phase | Fields Captured | Screens | Time | Cost |
|-------|----------------|---------|------|------|
| Intro | 0 | 7 | 2-3 min | $0 |
| Phase 1: Top Filters | 12 | 12 | 2-3 min | $0 |
| Phase 2: Identity | 7 | 7 | 2 min | $0 |
| Phase 3: Lifestyle | 14 | 12-14 | 3 min | $0 |
| Phase 4: Photo + Close | 1 | 3 | 1 min | $0 |
| **TOTAL BUTTON PHASE** | **34-36 fields** | **~37 screens** | **~10-12 min** | **$0.00** |
| Conversational Mode | Ongoing | — | Weeks | ~$0.02-0.05/session |

---

## ⚙️ ERROR HANDLING

| User Action | Bot Response |
|-------------|-------------|
| Sends text when button expected | "Just tap one of the options above 👆" |
| Sends sticker/GIF during buttons | "😄 Save that energy — just tap a button for now, we'll chat properly soon." |
| Goes idle >5 min during buttons | No action. Resume where they left off when they return. |
| Goes idle >24 hours during buttons | "Hey {name}, we were getting through the quick questions — want to pick up where we left off?" + [ Resume → ] |
| Wants to change an answer mid-flow | "No worries — once we finish the quick questions, you can tell me in chat and I'll update anything." |
| Sends `/start` again after partial completion | Resume from last incomplete screen, never restart |

---

## 🎯 KEY DESIGN PRINCIPLES

1. **Filters before identity** — Signal that matching quality matters more than profile building
2. **No correction flow during buttons** — Changes happen conversationally later (reduces friction)
3. **Momentum is everything** — Complete button phase in one sitting (8-10 min max)
4. **The transition message (P3) is critical** — Shifts mental model from form-filling to relationship-building
5. **Zero LLM cost for structured data** — Save API spend for high-value conversational depth

---

**Status:** Ready for Blitz to implement  
**Schema:** ✅ Deployed to Supabase  
**Button configs:** ✅ Available in `/JODI/telegram_button_flows.ts`  
**Next:** Blitz integrates button handler + conversational controller
