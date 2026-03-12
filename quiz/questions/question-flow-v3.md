# Masii — Master Question Flow v3

> Single source of truth. Telegram bot, web form, and DB schema all derive from this document.
> Last updated: March 2026 (v3 — full audit upgrade from v2)

---

## What Changed from v2

### Architecture Changes
- **State-first context**: Q3 (raised in) now drives downstream options for caste, language suggestions, diet defaults, and income brackets
- **Sensitive gate removed**: Every previously-gated question now has "Prefer not to say" individually. Privacy reassurance is a section intro, not a gate.
- **New Personality section**: Social style, conflict style, plus 2 new personality questions (weekend style, communication style) in a standalone section
- **Preference questions grouped with parents**: Each "about you" question is immediately followed by its "about your partner" preference. No more split phases.
- **Company name added**: Free text input after occupation sector
- **Religious practice examples**: Every religion gets contextual examples per practice level
- **Name split**: Full name (for records) + preferred name (for personalization). All `{name}` uses preferred name.
- **Caste include/exclude state-contextualized**: Q14/Q14a caste preference lists now driven by raised_in_state, matching Q12.
- **Column layout directives**: Any question with 8+ options specifies `columns: 2/3/4` to reduce scrolling.
- **Intro reduced**: 3 screens → 1 screen. Form-focused, not service-focused.

### Questions Added (net new)
- Q0.2a: `preferred_name` — "What should I call you?"
- Q18a: `company_name` — free text company name
- Q_personality_3: Weekend style (new WOW factor)
- Q_personality_4: Communication style (new WOW factor)
- All 14 v2 preference questions now implemented (were spec-only before)

### Questions Removed
- Q11 (sect/denomination) — deferred to premium
- Q24 (family values) — unreliable self-assessment
- Q28 (family involvement) — redundant
- Q47F (financial contribution, women) — covered by Q46
- Q48/Q48a (gotra) — deferred to premium
- Q49 (family property) — covered by Q23
- Sensitive gate question itself — replaced by per-question "Prefer not to say"

### Questions Rewritten
- Q3: "Where did you grow up?" — now full location tree (India/Outside India)
- Q10: Religious practice — now includes examples per level per religion
- Q22: Family type — options expanded from 3 to 4 with clear definitions
- Q25/Q26: "Not alive" → "Late"
- Q29: Diet — switched to universal options (not religion-specific)
- Q36: Marriage timeline — aligned to spec
- Q42/Q43: Cooking — reframed from "15 meals" to natural frequency
- Q44M: Partner working — reframed
- Q42F: "Do you know how to cook?" → "How's your cooking?"
- Q49F (career after marriage) — reframed
- Q52/Q53: Social/conflict style — reframed, rescored
- All "Partner's X preference?" questions rewritten as natural sentences
- All section transitions rewritten in Masii's voice

---

## Flow Architecture

```
                    ┌─────────────┐
                    │  question-   │
                    │  flow.md     │  ← YOU ARE HERE (source of truth, v3)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Telegram │ │ Web Form │ │ WhatsApp │
        │ bot      │ │ JS       │ │ (future) │
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │  Supabase    │
                    │  (users,     │
                    │  preferences,│
                    │  signals)    │
                    └──────────────┘
```

### Key Rules
- Every question must enable filtering/matching. No "get to know you" fluff (that's premium).
- Free text fields are premium only, except: name, city, company name.
- State-first architecture: Q3 (raised_in_state) drives downstream options for caste, language, diet, and income.
- "Prefer not to say" available on every sensitive question. No gates.
- Preference questions immediately follow their parent question.
- Male/Female question variants where expectations genuinely differ.
- "Do not match" lists (multi-select) for religion and caste — negative filters are real in India. Caste lists are state-contextualized.
- Full name asked upfront for records. Preferred name asked for personalization — all `{name}` references use preferred_name.
- **Column layout**: Any question with 8+ options must specify `columns: 2/3/4` in the config. Reduces scrolling on mobile. Rule of thumb: 8-12 options → 2 columns. 13-18 → 3 columns. 19+ → 3-4 columns or searchable dropdown.
- Auto-save at end of each section (Wave 3 implementation).

### Proxy Flow
- Separate, shorter flow for people filling on behalf of someone else.
- Collects basics only, then sends the actual person a message (via phone number) to complete.
- See [Proxy Flow](#proxy-flow) section at the end.

---

## Section Transitions (v3 — Masii's Voice)

All transitions use `{name}`. Each is ≤2 lines. Tone: warm auntie, not form wizard.

| Section | Transition |
|---------|-----------|
| Basics (Parichay) | "{name}, let's start simple. The stuff any masi would ask first." |
| Background (Dharam) | "{name}, I need to understand where you come from. Not to judge — to find someone who fits." |
| Partner Background | "Now the other side — what matters to you in their background, {name}?" |
| Education & Career (Vidya) | "Work and education, {name}. What you do and what you studied." |
| Family (Parivar) | "Family. You know this is the part I care about most, {name}." |
| Lifestyle (Jeevan Shaili) | "How you live, {name}. The everyday stuff that makes or breaks it." |
| Marriage & Living (Shaadi) | "The big picture, {name}. What does married life actually look like for you?" |
| Partner Physical | "A few preferences, {name}. Be honest — I don't judge." |
| Household & Expectations | "Real talk, {name}. Who cooks. Who cleans. How money works. No right answers — just honest ones." |
| Sensitive (Traditional) | "A few questions that traditional matchmakers ask. If any don't apply, just say 'Prefer not to say.' Your answers are never shared — not even with your match." |
| Personality | "Last stretch, {name}. A few about the kind of person you are — not what you do, but how you are." |
| Close | See Close section |

---

## Question Flow — Self (Primary)

### Phase 0: Setup

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 0.1 | `intent` | Are you filling this for yourself or someone else? | single | `For myself` / `For someone else` | meta | If "Someone else" → jump to Proxy Flow |
| 0.2 | `full_name` | What's your full name? | text | — | users | For records. Placeholder: "First and last name" |
| 0.2a | `preferred_name` | What should I call you? | text | — | users | Used as `{name}` throughout. Placeholder: "e.g. Nik, Priya, Ravi". Auto-fill first word of full_name. |
| 0.3 | `gender` | Are you male or female? | single | `Male` / `Female` | users | Gates gendered question variants. Small text below options: "More options coming soon — we see you." |

---

### Phase 1: Basics (Parichay)

> "{name}, let's start simple. The stuff any masi would ask first."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 1 | `date_of_birth` | When were you born? | two_step | Step 1: Year (2006–1970) / Step 2: Month | users | |
| 2 | `current_location` | Where do you live right now? | location_tree | Step 1: India / Outside India → Step 2: State or Country → Step 3: City (text) | users | Sets `_location_type` and `_location_country` for downstream logic |
| 2-pref | `pref_current_location` | Where should your partner currently live? | single + multi | `Same city as me` / `Same state as me` / `Same country as me` / `Anywhere` / `Specific countries...` (multi-select dropdown of top countries) | preferences | Hard gate. Immediately follows Q2. |
| 3 | `raised_in` | Where did you grow up? | location_tree | Step 1: India / Outside India → Step 2: If India: State → City (text). If outside: Country → City (text) | users | **KEY CONTEXT NODE.** `raised_in_state` drives downstream: caste list, language suggestions, diet defaults, income context. |
| 3-pref | `pref_raised_in` | Where should your partner have been raised? | single | **If user outside India:** `Same country as me` / `Raised abroad (any country)` / `Raised in India is fine too` / `Doesn't matter` | preferences | Hard gate. Options vary by user location. |
| | | | | **If user in India:** `Same state` / `Nearby states` / `Any state in India` / `Abroad is fine too` / `Doesn't matter` | | |
| 4 | `mother_tongue` | What is your mother tongue? | single | `Hindi` / `Gujarati` / `Marathi` / `Tamil` / `Telugu` / `Kannada` / `Malayalam` / `Bengali` / `Punjabi` / `Urdu` / `Odia` / `Assamese` / `Sindhi` / `Konkani` / `Tulu` / `Rajasthani` / `Bhojpuri` / `Maithili` / `Dogri` / `Kashmiri` / `Other` | users | **Expanded list. columns: 3.** Auto-suggest based on Q3 `raised_in_state`. E.g., if state = Tamil Nadu, surface Tamil first. |
| 5 | `languages_spoken` | What other languages do you speak? | multi | Same list as Q4 (minus their mother tongue) + `English` | users | Multi-select. Helps cross-regional matching |
| 6 | `marital_status` | What's your current marital status? | single | `Never married` / `Divorced` / `Widowed` / `Awaiting divorce` | users | Hard gate for matching |
| 6-pref | `pref_marital_status` | What marital status are you open to in a partner? | multi | `Never married` / `Divorced` / `Widowed` / `Awaiting divorce` / `Any` | preferences | Hard gate. Immediately follows Q6. |
| 6a | `children_existing` | Do you have children? | single | `No` / `Yes, they live with me` / `Yes, they don't live with me` | users | **Skip if** marital_status = "Never married" |
| 6a-pref | `pref_children_existing` | Are you open to a partner who has children? | single | `Yes` / `Only if they don't live with them` / `No` | preferences | Hard gate. **Skip if** Q6a not shown. |
| 7 | `height_cm` | How tall are you? | single | **Women:** `Below 5'2" (157 cm)` / `5'2" (157 cm)` / `5'3" (160 cm)` / `5'4" (163 cm)` / `5'5" (165 cm)` / `5'6" (168 cm)` / `5'7" (170 cm)` / `Above 5'7" (173 cm)` | users | Dual display: feet + cm. Store cm. columns: 2. |
| | | | | **Men:** `Below 5'5" (165 cm)` / `5'5" (165 cm)` / `5'6" (168 cm)` / `5'7" (170 cm)` / `5'8" (173 cm)` / `5'9" (175 cm)` / `5'10" (178 cm)` / `5'11" (180 cm)` / `6'0" (183 cm)` / `6'1" (185 cm)` / `6'2" (188 cm)` / `6'3" (191 cm)` / `Above 6'3" (193 cm)` | | |
| 8 | `weight_kg` | What is your weight? | single | **Women:** `Below 45 kg (99 lbs)` / `45-50 kg (99-110 lbs)` / `50-55 kg (110-121 lbs)` / `55-60 kg (121-132 lbs)` / `60-65 kg (132-143 lbs)` / `65-70 kg (143-154 lbs)` / `70-75 kg (154-165 lbs)` / `75-80 kg (165-176 lbs)` / `Above 80 kg (176 lbs)` | users | Dual display: kg + lbs. Store kg. columns: 2. |
| | | | | **Men:** `Below 60 kg (132 lbs)` / `60-65 kg (132-143 lbs)` / `65-70 kg (143-154 lbs)` / `70-75 kg (154-165 lbs)` / `75-80 kg (165-176 lbs)` / `80-85 kg (176-187 lbs)` / `85-90 kg (187-198 lbs)` / `90-100 kg (198-220 lbs)` / `Above 100 kg (220 lbs)` | | |

---

### Phase 2: Background (Dharam)

> "{name}, I need to understand where you come from. Not to judge — to find someone who fits."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 9 | `religion` | What is your religion? | single | `Hindu` / `Muslim` / `Sikh` / `Jain` / `Christian` / `Buddhist` / `Parsi` / `No religion` / `Other` | users | Gates downstream questions. columns: 2. |
| 10 | `religious_practice` | How would you describe your religious practice? | single | **See Practice Levels table below** | preferences | **Skip if** religion = Buddhist, No religion, Other. Now includes examples per level. |
| 12 | `caste_community` | What is your caste or community? | single | **State-contextualized.** Top castes for `raised_in_state` shown first, then remaining castes for their religion, then `Other` / `Prefer not to say`. See Caste Lists appendix. columns: 3. | preferences | **Skip if** religion has no caste system (Muslim, Christian, Buddhist, Parsi, No religion, Other). |
| 12a | `caste_importance` | How important is caste in your partner? | single | `Must be same caste` / `Prefer same, open to others` / `Doesn't matter` | preferences | **Skip if** caste = "Prefer not to say" |

#### Religious Practice Levels (Q10) — with examples

| Religion | Level 1 | Level 2 | Level 3 | Level 4 |
|----------|---------|---------|---------|---------|
| **Hindu** | Very religious — "Daily puja, regular fasting, temple every week" | Religious — "Puja most days, major festivals, temple visits" | Moderately religious — "Festivals and family rituals, occasional temple" | Not religious — "Cultural Hindu, don't practice actively" |
| **Muslim** | Very religious — "Five daily prayers, Ramadan, regular mosque" | Religious — "Friday prayers, Ramadan, Eid celebrations" | Moderately religious — "Eid and major occasions, occasional prayer" | Not religious — "Cultural Muslim, don't practice actively" |
| **Sikh** | Very religious (Amritdhari) — "Amrit chhaka, 5 Ks, daily Nitnem" | Religious (Keshdhari) — "Unshorn hair, regular Gurdwara, Nitnem" | Moderate (Sahajdhari) — "Gurdwara on occasions, flexible on 5 Ks" | Not religious — "Cultural Sikh, don't practice actively" |
| **Jain** | Very religious — "Strict dietary rules, regular temple, Paryushana fasting" | Religious — "Temple regularly, dietary discipline, major festivals" | Moderately religious — "Festivals and family rituals, flexible on diet" | Not religious — "Cultural Jain, don't practice actively" |
| **Christian** | Very religious — "Church every Sunday, Bible study, active in parish" | Religious — "Regular church, Christmas/Easter, prayer life" | Moderately religious — "Church on occasions, celebrates festivals" | Not religious — "Cultural Christian, don't practice actively" |

---

### Phase 3: Partner Background Preferences

> "Now the other side — what matters to you in their background, {name}?"

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 13 | `pref_religion` | Does your partner's religion matter to you? | single | `Same religion only` / `Open to all` / `Open, but not...` | preferences | Hard gate. Rewritten from "Partner's religion preference?" |
| 13a | `pref_religion_exclude` | Which religions would you NOT want to match with? | **multi** | `Hindu` / `Muslim` / `Sikh` / `Jain` / `Christian` / `Buddhist` / `Parsi` / `No religion` | preferences | **Only if** Q13 = "Open, but not..." |
| 14 | `pref_caste` | What about caste — does it matter? | single | `Same caste only` / `Same community, any caste` / `Open to all` / `Open, but not...` | preferences | **Skip if** religion has no caste. Hard gate. |
| 14a | `pref_caste_exclude` | Which castes would you NOT want to match with? | **multi** | **State-contextualized.** Same list as Q12 for their religion + raised_in_state. Top castes for user's state shown first. columns: 3. | preferences | **Only if** Q14 = "Open, but not...". Multi-select with "Done ✓". |
| 15 | `pref_mother_tongue` | Does language matter? Should they speak your mother tongue? | single | `Same language only` / `Same or Hindi` / `Doesn't matter` | preferences | Hard gate. |

---

### Phase 4: Education & Career (Vidya)

> "Work and education, {name}. What you do and what you studied."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 16 | `education_level` | What is your highest education? | single | `High school` / `Diploma` / `Bachelor's` / `Master's` / `Doctorate / PhD` / `Professional (CA, CS, MBBS, LLB)` | users | |
| 17 | `education_field` | What did you study? | single | `Engineering / IT` / `Medicine / Healthcare` / `Business / MBA` / `Law` / `Finance / CA / CS` / `Arts / Humanities` / `Science` / `Design / Architecture` / `Government / Civil Services` / `Other` | users | Rewritten from "What field?". columns: 2. |
| 17-pref | `pref_education_field` | Does your partner's field of study matter? | single + multi | `Same as mine` / `Doesn't matter` / `Specific fields...` (multi-select from Q17 list) | preferences | Scored. |
| 18 | `occupation_sector` | What sector do you work in? | single | `Tech / IT` / `Finance / Banking` / `Consulting` / `Healthcare` / `Manufacturing` / `Media / Entertainment` / `Education` / `Government / Public sector` / `Professional (Doctor, Lawyer, CA)` / `Business / Self-employed` / `Startup` / `Retail / Hospitality` / `Not working` / `Student` / `Other` | users | **Expanded from 8 to 15 sectors. columns: 3.** |
| 18a | `company_name` | Which company? | text | — | users | **NEW.** Free text. Placeholder: "e.g. TCS, Infosys, family business..." **Skip if** Q18 = "Not working" or "Student". |
| 19 | `annual_income` | What is your annual income? This is only used for matching — never displayed. | single | **State/location-contextualized.** See Income Brackets appendix. columns: 2. | users | Metro vs non-metro tiers for India. Currency auto-detected from Q2 location. |
| 20 | `pref_education_min` | Minimum education you'd want in a partner? | single | `Doesn't matter` / `At least Bachelor's` / `At least Master's` / `At least Professional degree` | preferences | |
| 21 | `pref_income_min` | Minimum income you'd want in a partner? | single | Same brackets as Q19 + `Doesn't matter` | preferences | |

#### Income Brackets (Q19) — by location

All brackets are **annual income**.

**India (INR):**
`Under ₹5 lakh/year` / `₹5-10 lakh/year` / `₹10-20 lakh/year` / `₹20-35 lakh/year` / `₹35-50 lakh/year` / `₹50-75 lakh/year` / `₹75 lakh - ₹1 crore/year` / `₹1-2 crore/year` / `Above ₹2 crore/year` / `Prefer not to say`

**USA (USD):**
`Under $30K/year` / `$30-50K/year` / `$50-75K/year` / `$75-100K/year` / `$100-150K/year` / `$150-250K/year` / `Above $250K/year` / `Prefer not to say`

**UK (GBP):**
`Under £25K/year` / `£25-40K/year` / `£40-60K/year` / `£60-80K/year` / `£80-120K/year` / `£120-200K/year` / `Above £200K/year` / `Prefer not to say`

**Canada (CAD):**
`Under C$40K/year` / `C$40-60K/year` / `C$60-90K/year` / `C$90-120K/year` / `C$120-180K/year` / `C$180-300K/year` / `Above C$300K/year` / `Prefer not to say`

**UAE (AED):**
`Under AED 100K/year` / `AED 100-200K/year` / `AED 200-350K/year` / `AED 350-500K/year` / `AED 500-750K/year` / `AED 750K-1M/year` / `Above AED 1M/year` / `Prefer not to say`

**Singapore (SGD):**
`Under S$40K/year` / `S$40-70K/year` / `S$70-100K/year` / `S$100-150K/year` / `S$150-250K/year` / `S$250-400K/year` / `Above S$400K/year` / `Prefer not to say`

**Other countries:** Default to USD brackets.

---

### Phase 5: Family (Parivar)

> "Family. You know this is the part I care about most, {name}."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 22 | `family_type` | What kind of family setup did you grow up in? | single | `Nuclear (parents live separately from extended family)` / `Joint (everyone under one roof)` / `Extended (same building or compound, separate households)` / `Parents nearby (same city, separate homes)` | users | **Expanded from 3 to 4 options** with clear definitions. |
| 22-pref | `pref_family_type` | Do you prefer your partner to be from a similar family setup? | single | `Same as mine` / `Doesn't matter` | preferences | Scored. |
| 23 | `family_status` | How would you describe your family's financial status? | single | **India:** `Less than ₹10 lakh annual income` / `₹10-30 lakh annual income + some assets` / `₹30-70 lakh annual income + assets` / `₹70 lakh+ annual income + significant assets` / `Assets over ₹10 crore` / `Prefer not to say` | users | **Aligned to spec tiers (6 options).** Outside India: country-specific (TBD, default to broad 4-tier). |
| 25 | `father_occupation` | Father's occupation? | single | `Business / Self-employed` / `Service / Salaried` / `Professional (Doctor, Lawyer, CA)` / `Government` / `Retired` / `Late` / `Prefer not to say` | users | **"Not alive" → "Late"** |
| 26 | `mother_occupation` | Mother's occupation? | single | `Homemaker` / `Working professional` / `Business` / `Government` / `Retired` / `Late` / `Prefer not to say` | users | **"Not alive" → "Late"** |
| 27 | `siblings` | Do you have siblings? | single | `Only child` / `1 sibling` / `2 siblings` / `3+ siblings` | users | |
| 27-pref | `pref_siblings` | Do you have a preference about your partner's siblings? | single | `Must have siblings` / `Single child is fine` / `Doesn't matter` | preferences | Scored. |

---

### Phase 6: Lifestyle (Jeevan Shaili)

> "How you live, {name}. The everyday stuff that makes or breaks it."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 29 | `diet` | What is your diet? | single | `Strict vegetarian (no onion/garlic)` / `Vegetarian` / `Eggetarian` / `Occasionally non-veg` / `Non-veg` / `Vegan` / `Jain` / `Halal only` / `Other` | users | **Universal options.** No longer religion-specific. "Halal only" added for Muslim users. columns: 2. |
| 30 | `drinking` | Do you drink alcohol? | single | `Never` / `Socially / Occasionally` / `Regularly` | users | |
| 31 | `smoking` | Do you smoke? | single | `Never` / `Socially / Occasionally` / `Regularly` | users | |
| 32 | `fitness_frequency` | How often do you exercise or play sports? | single | `Daily` / `3-5 times a week` / `1-2 times a week` / `Rarely` / `Never` | users | |
| 33 | `pref_diet` | How important is diet in your partner? | single | `Same as mine` / `Any vegetarian (no non-veg)` / `Vegetarian only` / `Doesn't matter` | preferences | **Rewritten question. 4 options (up from 3).** Hard gate. |
| 34 | `pref_drinking` | Is drinking a dealbreaker for you? | single | `Must not drink` / `Social drinking OK` / `Doesn't matter` | preferences | **Rewritten question.** Hard gate. |
| 35 | `pref_smoking` | Is smoking a dealbreaker? | single | `Must not smoke` / `Social smoking OK` / `Doesn't matter` | preferences | **Rewritten question.** Hard gate. |

---

### Phase 7: Marriage & Living (Shaadi)

> "The big picture, {name}. What does married life actually look like for you?"

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 36 | `marriage_timeline` | How soon are you looking to get married? | single | `Within 1 year` / `1-2 years` / `2-3 years` / `Just exploring` | preferences | **Aligned to spec.** Hard gate: within 1 step. |
| 37 | `children_intent` | Do you want children? | single | `Yes` / `Maybe / Open to it` / `No` | preferences | Hard gate: Yes vs No = eliminated |
| 37a | `children_timeline` | When would you want children? | single | `Soon after marriage` / `After 2-3 years` / `After 4+ years` | preferences | **Skip if** Q37 = "No" |
| 37a-pref | `pref_children_timeline` | When would you want your partner to be open to having children? | single | `Soon after marriage` / `After 2-3 years` / `After 4+ years` / `Doesn't matter` | preferences | Scored. **Skip if** Q37 = "No". |
| 38 | `living_arrangement` | After marriage, where would you want to live? | single | `With parents (joint family)` / `Near parents but separate` / `Independent — wherever life takes us` / `Open to discussion` | preferences | |
| 38-pref | `pref_living_arrangement` | What living arrangement would you need your partner to be open to? | single | Same as Q38 + `Doesn't matter` | preferences | Scored. |
| 39 | `relocation_willingness` | Would you relocate for the right match? | single | `Yes, anywhere` / `Yes, within India` / `Yes, within my state/country` / `Only abroad` / `No, I'm settled where I am` | preferences | **"Only abroad" added.** |
| 39a | `relocation_countries` | Which countries? | multi | Top countries list (multi-select) | preferences | **Only if** Q39 = "Only abroad" or "Yes, anywhere". |

---

### Phase 8: Partner Preferences — Physical

> "A few preferences, {name}. Be honest — I don't judge."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 40 | `pref_age_range` | What age range are you looking for? | two_step | Step 1: Min age (18-50) / Step 2: Max age (min-55) | preferences | Hard gate |
| 41 | `pref_height_range` | Any height preference? | two_step_same_screen | Min and max dropdowns shown side by side on same screen. Opposite gender scale from Q7. + `Doesn't matter` button above the dropdowns. | preferences | Hard gate. **Same-screen layout: two dropdowns side by side.** |

---

### Phase 9: Household & Expectations (Gender-forked)

> "Real talk, {name}. Who cooks. Who cleans. How money works. No right answers — just honest ones."

**For Men:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 42M | `cooking_contribution` | How often are you willing to cook? | single | `Most days (10+ meals/week)` / `A few times a week (4-7 meals)` / `Occasionally (1-3 meals)` / `Rarely or never` | signals | **Reframed from "15 meals" math.** |
| 42M-pref | `pref_partner_cooking_freq` | How often would you want your partner to cook? | single | `Most days` / `A few times a week` / `Occasionally` / `Doesn't matter — we'll figure it out` | preferences | Scored. Matched against her Q43F. |
| 42F-pref | `pref_partner_can_cook` | Is it important that your partner knows how to cook? | single | `Yes, regularly` / `Some cooking is enough` / `Doesn't matter` | preferences | Scored. Asked to men, matched against her Q42F. |
| 43M | `household_contribution` | How do you see household responsibilities? | single | `Shared equally` / `Mostly outsourced (cook/maid)` / `Flexible — whatever works` / `She would handle most of it` | signals | **Reordered: "Shared equally" first.** |
| 44M | `partner_working` | What's your view on your partner working? | single | `A career is important to me` / `I'm flexible — whatever she wants` / `I'd prefer a homemaker` | preferences | **Reframed from prescriptive language.** |

**For Women:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 42F | `do_you_cook` | How's your cooking? | single | `I cook often` / `Sometimes` / `Learning` / `Not my thing` | signals | **Reframed from "Do you know how to cook?"** |
| 43F | `cooking_contribution` | How often are you willing to cook? | single | `Most days (10+ meals/week)` / `A few times a week (4-7 meals)` / `Occasionally (1-3 meals)` / `Rarely or never` | signals | Same scale as men. |
| 44F | `pref_partner_cooking` | How often would you want your partner to cook? | single | `Most days` / `A few times a week` / `Occasionally` / `Doesn't matter — we'll figure it out` | preferences | Matched against his cooking_contribution |
| 45F | `pref_partner_household` | How much do you need your partner to contribute at home? | single | `Equal share` / `Significant help` / `Some help` / `Not needed — I'll manage or outsource` | preferences | Matched against his household_contribution |
| 46F | `career_after_marriage` | What does your career look like after marriage? | single | `Full steam ahead` / `Open to a pause for family` / `Still figuring it out` / `Prefer to focus on home` | signals | **Reframed.** |
| 48F | `live_with_inlaws` | Would you be OK living with his parents? | single | `Yes, happy to` / `For some time, not permanently` / `Prefer not to` / `Depends on the situation` | signals | |

**For Both:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 46 | `financial_planning` | How should finances work in a marriage? | single | `Fully joint` / `Joint for household, separate for personal` / `Mostly separate` | signals | |

---

### Phase 10: Sensitive (No Gate — Per-Question "Prefer not to say")

> "A few questions that traditional matchmakers ask. If any don't apply, just say 'Prefer not to say.' Your answers are never shared — not even with your match."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 47 | `manglik_status` | Are you Manglik? | single | `Yes` / `No` / `Don't know` / `Not applicable` / `Prefer not to say` | signals | **Only shown if** Hindu or Jain. "Prefer not to say" added. |
| 47a | `pref_manglik` | Is Manglik status important in your partner? | single | `Must match` / `Prefer, but flexible` / `Doesn't matter` | preferences | **Only if** Q47 = Yes or No. |
| 50 | `pref_family_status` | Does your partner's family financial status matter? | single | `Same or higher` / `Doesn't matter` | preferences | Scored against Q23. **Rewritten question.** |
| 51 | `known_conditions` | Do you have any known medical conditions? (e.g. diabetes, asthma, thyroid) | single | `No` / `Yes` / `Prefer not to say` | users | |
| 51-disability | `disability` | Do you have a disability? | single | `No` / `Yes` / `Prefer not to say` | users | Separate question. |
| 51a | `pref_conditions` | Are you open to a partner with a medical condition? | single | `Yes` / `Depends on the condition` / `No` | preferences | Hard gate: "No" + candidate has condition = eliminated. |
| 51a-disability | `pref_disability` | Are you open to a partner with a disability? | single | `Yes` / `Depends` / `No` | preferences | Hard gate. |

---

### Phase 11: Personality (NEW standalone section)

> "Last stretch, {name}. A few about the kind of person you are — not what you do, but how you are."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 52 | `social_style` | How social are you? | single | `Love big gatherings — the more people the better` / `Enjoy going out but need my downtime` / `Prefer small groups and close friends` / `Homebody — happiest at home` | signals | WOW factor. |
| 53 | `conflict_style` | How do you handle disagreements? | single | `Address it right away` / `Give it a day, then talk` / `Let most things go` / `Need time alone before I can discuss` | signals | **Reframed as full question. Rescored as matrix (see matching protocol).** |
| 54 | `weekend_style` | What does your ideal weekend look like? | single | `Out and about — restaurants, events, travel` / `Mix of plans and downtime` / `Quiet at home — cook, read, recharge` / `Depends on the week` | signals | **NEW. WOW factor.** Lifestyle alignment signal. |
| 55 | `communication_style` | How do you stay connected with people you care about? | single | `Talk or call often — daily check-ins` / `Regular texts and voice notes` / `Quality time over quantity — less frequent but deeper` / `I'm not great at staying in touch but I show up when it matters` | signals | **NEW. WOW factor.** Relationship maintenance signal. |

---

### Close

> "{name}, that's everything. You've been honest, and that's exactly what I need.
>
> I'm going to work on this. When I find someone worth your time — someone who actually fits — I'll tell you why I think so.
>
> Sit tight. Good things take a little time.
>
> — Masii"

→ Collect phone number (if not already known from channel)
→ Submit all answers

---

## Proxy Flow

When `intent` = "Someone else":

### Step 1: Proxy basics

| # | Field | Question | Type | Options |
|---|-------|----------|------|---------|
| P1 | `proxy_relation` | What's your relationship to them? | single | `Parent` / `Sibling` / `Relative` / `Friend` |
| P2 | `person_name` | What's their name? | text | — |
| P3 | `person_gender` | Male or female? | single | `Male` / `Female` |
| P4 | `person_phone` | What's their phone number? (I'll send them a message to complete their profile.) | phone | — |
| P5 | `person_age` | How old are they? | single | Year list (2006-1970) |
| P6 | `person_location` | Where do they live? | location_tree | Same as Q2 |
| P7 | `person_religion` | What's their religion? | single | Same as Q9 |
| P8 | `person_caste` | What's their caste/community? | single | Same as Q12 (conditional on religion) |
| P9 | `person_marital_status` | Marital status? | single | Same as Q6 |
| P10 | `person_education` | Highest education? | single | Same as Q16 |
| P11 | `person_occupation` | What do they do? | single | Same as Q18 |

### Step 2: Close

> "Thanks! I'll send {person_name} a message at their number to complete the rest. Their answers will be private — you won't see them. I'll let you know when their profile is ready.
>
> — Masii"

→ System sends invite to `person_phone` via WhatsApp/Telegram
→ When they click, they get the full self-flow (Phase 0-11) with their name pre-filled

---

## Question Count Summary (v3)

| Section | Questions | Notes |
|---------|-----------|-------|
| Setup | 4 | Intent, full name, preferred name, gender |
| Basics | 8 + 5 pref/sub | DOB, location, location-pref, raised-in, raised-in-pref, mother tongue, languages, marital, marital-pref, children-existing, children-existing-pref, height, weight |
| Background | 2 + 1 sub | Religion, practice (with examples), caste, caste importance |
| Partner Background | 3 + 2 sub | Religion pref, religion exclude, caste pref, caste exclude, mother tongue pref |
| Education & Career | 6 + 1 pref + 1 new | Education, field, field-pref, sector (expanded), **company name (new)**, income, education-min-pref, income-min-pref |
| Family | 5 + 2 pref | Family type (expanded), family-type-pref, family status (aligned), father occ, mother occ, siblings, siblings-pref |
| Lifestyle | 7 | Diet (universal), drinking, smoking, fitness, diet-pref (4 options), drinking-pref, smoking-pref |
| Marriage & Living | 5 + 3 pref + 1 sub | Timeline (aligned), children intent, children timeline, children-timeline-pref, living arrangement, living-arrangement-pref, relocation (with "Only abroad"), relocation countries |
| Partner Physical | 2 | Age range, height range |
| Household (gendered) | M: 5, F: 6, Both: 1 | All reframed |
| Sensitive (no gate) | 3 + 4 sub | Manglik, manglik-pref, family-status-pref, medical, disability, medical-pref, disability-pref |
| Personality (NEW) | 4 | Social style, conflict style, **weekend style (new)**, **communication style (new)** |
| **Total** | **M: ~59 + ~16 pref/sub (~75 clicks), F: ~60 + ~15 pref/sub (~75 clicks)** | Net: +9 from v2, but 7 removed + rebalanced. Cleaner, more signal per question. |

---

## DB Schema Mapping (v3)

### `users` table (facts about the person)
`full_name`, `preferred_name`, `gender`, `date_of_birth`, `current_location`, `raised_in`, `raised_in_state`, `mother_tongue`, `languages_spoken` (array), `marital_status`, `children_existing`, `height_cm`, `weight_kg`, `religion`, `education_level`, `education_field`, `occupation_sector`, `company_name`, `annual_income`, `family_type`, `family_status`, `father_occupation`, `mother_occupation`, `siblings`, `known_conditions`, `disability`

### `preferences` table (what they want in a partner)
`religious_practice`, `caste_community`, `caste_importance`, `pref_religion`, `pref_religion_exclude` (array), `pref_caste`, `pref_caste_exclude` (array), `pref_mother_tongue`, `pref_current_location`, `pref_raised_in`, `pref_marital_status` (array), `pref_children_existing`, `pref_education_min`, `pref_education_field`, `pref_income_min`, `pref_family_type`, `pref_siblings`, `pref_diet`, `pref_drinking`, `pref_smoking`, `pref_age_min`, `pref_age_max`, `pref_height_min`, `pref_height_max`, `pref_manglik`, `pref_family_status`, `pref_conditions`, `pref_disability`, `pref_children_timeline`, `pref_living_arrangement`, `pref_partner_cooking_freq` (M), `pref_partner_can_cook` (M), `pref_partner_cooking` (F), `pref_partner_household` (F), `marriage_timeline`, `children_intent`, `children_timeline`, `living_arrangement`, `relocation_willingness`, `relocation_countries` (array), `partner_working` (M only)

### `signals` table (behavioral/personality signals)
`diet`, `drinking`, `smoking`, `fitness_frequency`, `social_style`, `conflict_style`, `weekend_style`, `communication_style`, `cooking_contribution` (both), `household_contribution` (M), `do_you_cook` (F), `career_after_marriage` (F), `live_with_inlaws` (F), `financial_planning`, `manglik_status`

### `user_channels` table
`user_id`, `channel` (telegram/web/whatsapp), `channel_id`, `phone`

---

## Error Messages (v3 — no emojis)

```
button_expected: "Just tap one of the options above."
sticker_during_buttons: "Save that energy — just pick an option for now."
invalid_input: "That doesn't look right. Please try again."
network_error: "Something went wrong on my end. Let me try that again."
```

---

## Resume Messages (v3)

```
Hey {name}, we were getting through your profile — want to pick up where we left off?

Progress: {section_name} • {current} of {total} questions
```

Buttons: `Resume` / `Start over`

---

## Intro Message (v3 — single screen, form-focused)

**Screen 1 (only screen):**
```
This takes about 10 minutes.

I'll ask about your life, your values, your
family, and what you're looking for.

Be honest — the better I know you,
the better the match.

Everything stays between us.
```
Button: "Let's go →"

*Note: The homepage already explains who Masii is, how it works, and pricing. The form intro only needs to set expectations for the form itself.*

---

## On Hold / Future

- **Complexion** (self + preference) — waiting on photo upload. Regional bias makes self-reported complexion tricky.
- **Body type preference** — weight + height gives us BMI. No need for self-reported "slim/athletic/heavy."
- **Free text fields** (hobbies, about me, what you're looking for) — premium feature, not part of free matching flow.
- **Deep personality questions** (love language, attachment style, values essays) — premium tier.
- **Sect/Denomination (old Q11)** — removed from free tier. Revisit for premium.
- **Gotra (old Q48/Q48a)** — removed from free tier. Revisit for premium.
- **Non-binary gender** — acknowledged in v3 with "More options coming soon" text. Full implementation pending matching logic design.
- **Form colors** — Current form does not use brand colors. Wave 3: align to brand design system (cream backgrounds, terracotta accents, earth text, no pure white/black).
- **Multi-select tick indicators** — Multi-select answers don't show visual tick marks. Wave 3 form UI fix.
- **Back navigation** — Wave 3. At minimum, allow back within current section.
- **Auto-save** — Wave 3. Save at end of each section.
- **Mid-form save point** — Wave 3. After Phase 4 (~30 questions), offer "I can start looking now, or you can continue for better matches."

---

## Appendix: State-Contextualized Caste Lists

The `raised_in_state` from Q3 determines which castes appear first in the Q12 dropdown. Every list includes `Other` and `Prefer not to say` at the bottom.

### Hindu Castes by State (Top castes shown first)

| State | Priority Castes |
|-------|----------------|
| Tamil Nadu | Brahmin (Iyer, Iyengar), Nadar, Thevar, Gounder, Mudaliar, Pillai, Vanniyar, Chettiar, Scheduled Caste, Scheduled Tribe |
| Kerala | Nair, Namboodiri, Menon, Ezhava, Syrian Christian*, Pulaya, Scheduled Caste, Scheduled Tribe |
| Karnataka | Brahmin, Lingayat, Vokkaliga, Gowda, Reddy, Scheduled Caste, Scheduled Tribe |
| Andhra Pradesh / Telangana | Reddy, Kamma, Kapu, Brahmin, Velama, Naidu, Vysya, Scheduled Caste, Scheduled Tribe |
| Maharashtra | Maratha, Brahmin (Chitpavan, Deshastha), Kunbi, Mali, Scheduled Caste, Scheduled Tribe |
| Gujarat | Patel, Brahmin, Baniya, Jain*, Rajput, Lohana, Scheduled Caste, Scheduled Tribe |
| Rajasthan | Rajput, Brahmin, Marwari, Jat, Agarwal, Meena, Gurjar, Scheduled Caste, Scheduled Tribe |
| Punjab / Haryana | Jat, Khatri, Arora, Brahmin, Yadav, Saini, Scheduled Caste |
| Uttar Pradesh / Bihar | Brahmin, Yadav, Rajput, Bhumihar, Kayastha, Kurmi, Baniya, Scheduled Caste, Scheduled Tribe |
| West Bengal | Brahmin, Kayastha, Baidya, Mahishya, Scheduled Caste, Scheduled Tribe |
| Delhi NCR | Brahmin, Agarwal, Baniya, Jat, Khatri, Arora, Yadav, Gupta, Kayastha, Rajput |
| Other / Outside India | Brahmin, Agarwal, Baniya, Jat, Kayastha, Kshatriya, Maratha, Patel, Rajput, Reddy, Nair, Iyer, Iyengar, Gupta, Khatri, Arora, Sindhi, Lingayat (full national list) |

*Note: Syrian Christian and Jain appear in state lists where they are culturally significant, even though they technically cross religion lines. The Q9 religion filter still applies — these only show if religion = Hindu.*

### Jain Castes (national, no state context needed)
`Agarwal` / `Baniya` / `Oswal` / `Porwal` / `Shrimal` / `Khandelwal` / `Other` / `Prefer not to say`

### Sikh Castes (national)
`Jat Sikh` / `Khatri Sikh` / `Arora Sikh` / `Ramgarhia` / `Saini` / `Ravidasia` / `Other` / `Prefer not to say`
