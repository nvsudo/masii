# Masii — Master Question Flow

> Single source of truth. Telegram bot, web form, and DB schema all derive from this document.
> Last updated: March 2026

---

## Flow Architecture

```
                    ┌─────────────┐
                    │  question-   │
                    │  flow.md     │  ← YOU ARE HERE (source of truth)
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
- Free text fields are premium only. Free tier = structured options.
- Questions use market-standard Indian matrimonial terminology (Shaadi.com / BharatMatrimony reference).
- Sensitive questions go behind an opt-in gate with privacy reassurance.
- Male/Female question variants where expectations genuinely differ.
- "Do not match" lists (multi-select) for religion and caste — negative filters are real in India.
- Name asked upfront so all subsequent questions can personalize with `{name}`.

### Proxy Flow
- Separate, shorter flow for people filling on behalf of someone else.
- Collects basics only, then sends the actual person a message (via phone number) to complete.
- See [Proxy Flow](#proxy-flow) section at the end.

---

## Question Flow — Self (Primary)

### Phase 0: Setup

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 0.1 | `intent` | Are you filling this for yourself or someone else? | single | `Self` / `Someone else` | meta | If "Someone else" → jump to Proxy Flow |
| 0.2 | `full_name` | What's your name? | text | — | users | Used as `{name}` throughout |
| 0.3 | `gender` | Are you male or female? | single | `Male` / `Female` | users | Gates gendered question variants |

---

### Phase 1: Basics (Parichay)

> "Let's start with the basics, {name}."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 1 | `date_of_birth` | When were you born? | two_step | Step 1: Year (2006–1970) / Step 2: Month | users | |
| 2 | `current_location` | Where do you live right now? | location_tree | Step 1: India / Outside India → Step 2: State or Country → Step 3: City | users | |
| 3 | `hometown` | Where is your family originally from? | two_step | Step 1: State (Indian states list) → Step 2: City/Town | users | State + town — helps match cultural roots and regional identity |
| 4 | `mother_tongue` | What is your mother tongue? | single | `Hindi` / `Gujarati` / `Marathi` / `Tamil` / `Telugu` / `Kannada` / `Malayalam` / `Bengali` / `Punjabi` / `Urdu` / `Odia` / `Assamese` / `Sindhi` / `Konkani` / `Tulu` / `Other` | users | Big matching signal |
| 5 | `languages_spoken` | What other languages do you speak? | multi | Same list as Q4 (minus their mother tongue) + `English` | users | Multi-select. Helps cross-regional matching |
| 6 | `marital_status` | What's your current marital status? | single | `Never married` / `Divorced` / `Widowed` / `Awaiting divorce` | users | |
| 6a | `children_existing` | Do you have children? | single | `No` / `Yes, they live with me` / `Yes, they don't live with me` | users | **Skip if** marital_status = "Never married" |
| 7 | `height_cm` | How tall are you? | single | **Women:** `Below 5'2"` / `5'2"` / `5'3"` / `5'4"` / `5'5"` / `5'6"` / `5'7"` / `Above 5'7"` | users | Gender-specific ranges. Store cm. |
| | | | | **Men:** `Below 5'5"` / `5'5"` / `5'6"` / `5'7"` / `5'8"` / `5'9"` / `5'10"` / `5'11"` / `6'0"` / `6'1"` / `6'2"` / `6'3"` / `Above 6'3"` | | |
| 8 | `weight_kg` | What is your weight? | single | **Women:** `Below 45 kg` / `45-50 kg` / `50-55 kg` / `55-60 kg` / `60-65 kg` / `65-70 kg` / `70-75 kg` / `75-80 kg` / `Above 80 kg` | users | Gender-specific buckets. We calc BMI from height + weight. |
| | | | | **Men:** `Below 60 kg` / `60-65 kg` / `65-70 kg` / `70-75 kg` / `75-80 kg` / `80-85 kg` / `85-90 kg` / `90-100 kg` / `Above 100 kg` | | |

<!-- HOLD: Complexion
| X | `complexion` | What is your complexion? | single | `Very fair` / `Fair` / `Wheatish` / `Wheatish brown` / `Dark` | users | BharatMatrimony standard terms |
Holding this — photo will go a long way. Regional bias makes this tricky (Andhra vs Punjab norms differ). Revisit when photo upload is live.
-->

---

### Phase 2: Background (Dharam)

> "Now a bit about your background, {name}. This helps me find people from compatible communities."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 9 | `religion` | What is your religion? | single | `Hindu` / `Muslim` / `Sikh` / `Jain` / `Christian` / `Buddhist` / `Parsi` / `No religion` / `Other` | users | Gates many downstream questions |
| 10 | `religious_practice` | How would you describe your religious practice? | single | **Hindu:** `Very religious` / `Religious` / `Moderately religious` / `Not religious` | preferences | **Skip if** religion has no practice options (Buddhist, No religion, Other) |
| | | | | **Muslim:** `Very religious` / `Religious` / `Moderately religious` / `Liberal` | | |
| | | | | **Sikh:** `Very religious (Amritdhari)` / `Religious (Keshdhari)` / `Moderate (Sahajdhari)` / `Not religious` | | |
| | | | | **Jain:** `Very religious` / `Religious` / `Moderately religious` / `Not religious` | | |
| | | | | **Christian:** `Very religious` / `Religious` / `Moderately religious` / `Not religious` | | |
| 11 | `sect_denomination` | What is your sect or denomination? | single | **Hindu:** `Vaishnav` / `Shaiv` / `Arya Samaji` / `Smartha` / `ISKCON` / `None / Other` | preferences | **Skip if** religion has no sects |
| | | | | **Muslim:** `Sunni` / `Shia` / `Sufi` / `Ahmadiyya` / `None / Other` | | |
| | | | | **Jain:** `Digambar` / `Shwetambar` / `Other` | | BharatMatrimony standard |
| | | | | **Christian:** `Catholic` / `Protestant` / `Orthodox` / `Evangelical` / `Other` | | |
| 12 | `caste_community` | What is your caste or community? | single | **Hindu (major):** `Brahmin` / `Agarwal` / `Baniya` / `Jat` / `Kayastha` / `Kshatriya` / `Maratha` / `Patel` / `Rajput` / `Reddy` / `Nair` / `Iyer` / `Iyengar` / `Gupta` / `Khatri` / `Arora` / `Sindhi` / `Lingayat` / `Scheduled Caste` / `Scheduled Tribe` / `Other` / `Prefer not to say` | preferences | **Skip if** religion has no caste system |
| | | | | **Jain:** `Agarwal` / `Baniya` / `Oswal` / `Porwal` / `Shrimal` / `Khandelwal` / `Other` / `Prefer not to say` | | |
| | | | | **Sikh:** `Jat Sikh` / `Khatri Sikh` / `Arora Sikh` / `Ramgarhia` / `Saini` / `Ravidasia` / `Other` / `Prefer not to say` | | |
| 12a | `caste_importance` | How important is caste in your partner? | single | `Must be same caste` / `Prefer same, open to others` / `Doesn't matter` | preferences | **Skip if** caste = "Prefer not to say" |

---

### Phase 3: Partner Background Preferences

> "Now let's talk about what you're looking for in a partner's background."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 13 | `pref_religion` | Partner's religion preference? | single | `Same religion only` / `Open to all` / `Open, but not...` | preferences | |
| 13a | `pref_religion_exclude` | Which religions would you NOT want to match with? | **multi** | `Hindu` / `Muslim` / `Sikh` / `Jain` / `Christian` / `Buddhist` / `Parsi` / `No religion` | preferences | **Only if** Q13 = "Open, but not..." — the "do not match" list. Multi-select. |
| 14 | `pref_caste` | Partner's caste preference? | single | `Same caste only` / `Same community, any caste` / `Open to all` / `Open, but not...` | preferences | **Skip if** religion has no caste |
| 14a | `pref_caste_exclude` | Which castes would you NOT want to match with? | **multi** | [Same caste list as Q12 for their religion] | preferences | **Only if** Q14 = "Open, but not..." — multi-select |
| 15 | `pref_mother_tongue` | Partner's mother tongue preference? | single | `Same language only` / `Same or Hindi` / `Doesn't matter` | preferences | |

---

### Phase 4: Education & Career (Vidya)

> "Let's talk about education and career, {name}."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 16 | `education_level` | What is your highest education? | single | `High school` / `Diploma` / `Bachelor's` / `Master's` / `Doctorate / PhD` / `Professional (CA, CS, MBBS, LLB)` | users | |
| 17 | `education_field` | What field? | single | `Engineering / IT` / `Medicine / Healthcare` / `Business / MBA` / `Law` / `Finance / CA / CS` / `Arts / Humanities` / `Science` / `Design / Architecture` / `Government / Civil Services` / `Other` | users | |
| 18 | `occupation_sector` | What sector do you work in? | single | `Public / Government` / `Private` / `Professional (Doctor, Lawyer, CA)` / `Business / Self-employed` / `Startup` / `Not working` / `Student` / `Other` | users | Simplified: Public, Private, Professional, Business, Startup, Not working, Student, Other |
| 19 | `annual_income` | What is your annual income? (This is only used for matching, never displayed.) | single | `Under ₹5 lakh` / `₹5-10 lakh` / `₹10-20 lakh` / `₹20-35 lakh` / `₹35-50 lakh` / `₹50-75 lakh` / `₹75 lakh - ₹1 crore` / `₹1-2 crore` / `Above ₹2 crore` / `Prefer not to say` | users | Reassurance text. For NRIs: `Under $30K` / `$30-50K` / `$50-75K` / `$75-100K` / `$100-150K` / `$150-250K` / `Above $250K` — detect from location |
| 20 | `pref_education_min` | Minimum education you'd want in a partner? | single | `Doesn't matter` / `At least Bachelor's` / `At least Master's` / `At least Professional degree` | preferences | |
| 21 | `pref_income_min` | Minimum income range you'd want in a partner? | single | Same brackets as Q19 + `Doesn't matter` | preferences | |

---

### Phase 5: Family (Parivar)

> "Family matters in Indian matchmaking. Let's cover that, {name}."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 22 | `family_type` | What type of family do you come from? | single | `Nuclear` / `Joint` / `Semi-joint` | users | |
| 23 | `family_status` | How would you describe your family's financial status? | single | `Middle class` / `Upper middle class` / `Affluent` / `Prefer not to say` | users | |
| 24 | `family_values` | How would you describe your family's values? | single | `Traditional` / `Moderate` / `Liberal` | users | |
| 25 | `father_occupation` | Father's occupation? | single | `Business / Self-employed` / `Service / Salaried` / `Professional (Doctor, Lawyer, CA)` / `Government` / `Retired` / `Not alive` / `Prefer not to say` | users | |
| 26 | `mother_occupation` | Mother's occupation? | single | `Homemaker` / `Working professional` / `Business` / `Government` / `Retired` / `Not alive` / `Prefer not to say` | users | |
| 27 | `siblings` | Do you have siblings? | single | `Only child` / `1 sibling` / `2 siblings` / `3+ siblings` | users | |
| 28 | `family_involvement` | How involved will your family be in the decision? | single | `Very — their approval matters` / `Moderate — I'll decide but they have input` / `Independent — my decision entirely` | preferences | |

---

### Phase 6: Lifestyle (Jeevan Shaili)

> "Almost there, {name}. A few questions about how you live day to day."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 29 | `diet` | What is your diet? | single | **Jain:** `Strict Jain (no onion/garlic)` / `Jain vegetarian` / `Flexible` | users | Options depend on religion |
| | | | | **Hindu:** `Pure vegetarian (no onion/garlic)` / `Vegetarian` / `Eggetarian` / `Non-vegetarian` / `Flexible` | | |
| | | | | **Muslim:** `Halal only` / `Non-vegetarian` / `Flexible` | | |
| | | | | **Sikh:** `Vegetarian` / `Non-vegetarian` / `Flexible` | | |
| | | | | **Default:** `Vegetarian` / `Vegan` / `Eggetarian` / `Non-vegetarian` / `Flexible` | | |
| 30 | `drinking` | Do you drink alcohol? | single | `Never` / `Socially / Occasionally` / `Regularly` | users | |
| 31 | `smoking` | Do you smoke? | single | `Never` / `Socially / Occasionally` / `Regularly` | users | |
| 32 | `fitness_frequency` | How often do you exercise or play sports? | single | `Daily` / `3-5 times a week` / `1-2 times a week` / `Rarely` / `Never` | users | |
| 33 | `pref_diet` | Partner's diet preference? | single | `Same as mine` / `Vegetarian or above` / `Doesn't matter` | preferences | |
| 34 | `pref_drinking` | Partner's drinking — dealbreaker? | single | `Must not drink` / `Social drinking OK` / `Doesn't matter` | preferences | |
| 35 | `pref_smoking` | Partner's smoking — dealbreaker? | single | `Must not smoke` / `Social smoking OK` / `Doesn't matter` | preferences | |

---

### Phase 7: Marriage & Living (Shaadi)

> "Let's talk about what married life looks like for you, {name}."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 36 | `marriage_timeline` | How soon are you looking to get married? | single | `Within 6 months` / `In the next 1 year` / `In the next 2-3 years` / `Just exploring` | preferences | |
| 37 | `children_intent` | Do you want children? | single | `Yes` / `Maybe / Open to it` / `No` | preferences | |
| 37a | `children_timeline` | When would you want children? | single | `Soon after marriage` / `After 2-3 years` / `After 4+ years` | preferences | **Skip if** Q37 = "No" |
| 38 | `living_arrangement` | After marriage, where would you want to live? | single | `With parents (joint family)` / `Near parents but separate` / `Independent — wherever life takes us` / `Open to discussion` | preferences | |
| 39 | `relocation_willingness` | Would you relocate for the right match? | single | `Yes, anywhere` / `Yes, within India` / `Yes, within my state/country` / `No, I'm settled where I am` | preferences | |

---

### Phase 8: Partner Preferences — Physical

> "A few preferences about your partner, {name}."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 40 | `pref_age_range` | Partner's age range? | two_step | Step 1: Min age (18-45) / Step 2: Max age (min-50) | preferences | |
| 41 | `pref_height_range` | Partner's height preference? | two_step | Step 1: Min height / Step 2: Max height (opposite gender scale from Q7) + `Doesn't matter` | preferences | Men see women's range, women see men's range |

<!-- HOLD: Complexion & build preferences — waiting on photo upload feature
| X | `pref_complexion` | Partner's complexion preference? | single | `Fair` / `Fair to wheatish` / `Doesn't matter` | preferences | |
| X | `pref_body_type` | Partner's build preference? | single | `Slim or athletic` / `Average` / `Doesn't matter` | preferences | |
-->

---

### Phase 9: Household & Expectations (Gender-forked)

> "The next few are about how you see daily life in a marriage. No right answers — just honest ones."

**For Men:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 42M | `cooking_contribution` | Out of 15 meals in a week, how many are you willing to cook? | single | `0` / `1-3` / `4-7` / `8-10` / `More than 10` | signals | |
| 43M | `household_contribution` | How do you see household responsibilities? | single | `Mostly her` / `Shared equally` / `Mostly outsourced (cook/maid)` / `Flexible — whatever works` | signals | |
| 44M | `partner_working` | Do you want your partner to work? | single | `Yes, she should have a career` / `Her choice` / `Prefer she focuses on home` | preferences | |

**For Women:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 42F | `do_you_cook` | Do you know how to cook? | single | `Yes, I cook regularly` / `Yes, but I don't cook often` / `No, but I'm willing to learn` / `No` | signals | |
| 43F | `cooking_contribution` | Out of 15 meals in a week, how many are you willing to cook? | single | `0` / `1-3` / `4-7` / `8-10` / `More than 10` | signals | Same scale as men — enables matching |
| 44F | `pref_partner_cooking` | How often do you need your partner to cook? | single | `Regularly (7+ meals a week)` / `Sometimes (3-6 meals)` / `Rarely (1-2 meals)` / `Never — I'll handle it or we'll outsource` | preferences | Matchable against his cooking_contribution |
| 45F | `pref_partner_household` | How much do you need your partner to contribute to household chores? | single | `Equal share` / `Significant help` / `Some help` / `Not needed — I'll manage or outsource` | preferences | Matchable against his household_contribution |
| 46F | `career_after_marriage` | Do you plan to continue working after marriage? | single | `Yes, definitely` / `Yes, but open to a break for kids` / `Undecided` / `No, prefer homemaking` | signals | |
| 47F | `financial_contribution` | How do you see financial contribution in a marriage? | single | `Equal partnership` / `I'll contribute, he leads` / `His responsibility primarily` / `Flexible — depends on situation` | signals | |
| 48F | `live_with_inlaws` | Would you be OK living with his parents? | single | `Yes, happy to` / `For some time, not permanently` / `Prefer not to` / `Depends on the situation` | signals | |

**For Both:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 46 | `financial_planning` | How should finances work in a marriage? | single | `Fully joint` / `Joint for household, separate for personal` / `Mostly separate` | signals | |

---

### Phase 10: Sensitive Section (Opt-in Gate)

> **Gate message:** "The next few questions cover criteria that traditional matchmakers ask. Some families consider these important. Your answers are **only used for matching and never published or shared** with anyone — not even your match. Skip this section if you'd rather not answer."
>
> `Would you like to answer these?` → `Yes` / `No, skip`

**If Yes:**

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 47 | `manglik_status` | Are you Manglik? | single | `Yes` / `No` / `Don't know` / `Not applicable` | signals | Only for Hindu, Jain |
| 47a | `pref_manglik` | Is Manglik status important in your partner? | single | `Must match` / `Prefer, but flexible` / `Doesn't matter` | preferences | **Only if** Q47 ≠ "Not applicable" |
| 48 | `gotra` | What is your gotra? | single | `[Common gotras by religion]` + `Don't know` + `Not applicable` | preferences | Only for Hindu, Jain, Sikh |
| 48a | `pref_gotra_exclude` | Any gotras you cannot match with? | **multi** | `[Common gotras]` + `None / Doesn't matter` | preferences | Multi-select. Some families have gotra restrictions. |
| 49 | `family_property` | Does your family own property? | single | `Rented home` / `Own flat/apartment` / `Own independent house` / `Own bungalow/villa` / `Agricultural land` / `Multiple properties` / `Prefer not to say` | signals | |
| 50 | `pref_family_status` | Partner's family financial status preference? | single | `Same or higher` / `Doesn't matter` | preferences | |
| 51 | `known_conditions` | Do you have any known medical conditions or disabilities? | single | `No` / `Yes` / `Prefer not to say` | users | Sensitive but real. Traditional matchmakers always ask. Framed broadly — covers physical, medical, mental health. |
| 51a | `pref_conditions` | Would you be open to a partner with a medical condition or disability? | single | `Yes` / `Depends on the condition` / `No` | preferences | |

---

### Phase 11: Social & Personality

> "Last stretch, {name}. A few about how you are socially."

| # | Field | Question | Type | Options | DB Table | Notes |
|---|-------|----------|------|---------|----------|-------|
| 52 | `social_style` | How social are you? | single | `Very social — love big gatherings` / `Social — enjoy going out but need downtime` / `Introverted — prefer small groups` / `Very introverted — homebody` | signals | |
| 53 | `conflict_style` | When there's a disagreement, you tend to... | single | `Talk it out immediately` / `Take some time, then discuss` / `Avoid conflict` / `Get heated, then cool down` | signals | |

---

### Close

> "Done, {name}! I have everything I need. I'll start searching for your match and message you when I find someone worth your time. Sit tight.
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
| P4 | `person_phone` | What's their phone number? (We'll send them a message to complete their profile.) | phone | — |
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

## Question Count Summary

| Section | Questions | Notes |
|---------|-----------|-------|
| Setup | 3 | Name, gender, intent |
| Basics | 8 + 1 sub | DOB, location, hometown (state+town), mother tongue, languages, marital, height, weight |
| Background | 4 + 1 sub | Religion, practice, sect, caste |
| Partner background | 3 + 2 sub | Do-not-match lists (multi-select) |
| Education & Career | 6 | Sector simplified, income brackets |
| Family | 7 | |
| Lifestyle | 7 | Diet, drinking, smoking, fitness |
| Marriage & Living | 4 + 1 sub | Timeline, children, relocation |
| Partner physical | 2 | Age range, height range (complexion/build on hold) |
| Household (gendered) | M: 3, F: 7 | M: cook, household, partner working / F: can you cook, cook contribution, pref partner cook, pref partner household, career, financial, in-laws |
| Sensitive (opt-in) | 5 + 3 sub | Manglik, gotra, property, conditions |
| Social | 2 | |
| **Total** | **M: ~55 + subs (~60 clicks), F: ~59 + subs (~65 clicks)** | Women have more household matching questions |

---

## DB Schema Mapping

### `users` table (facts about the person)
`full_name`, `gender`, `date_of_birth`, `current_location`, `hometown_state`, `hometown_city`, `mother_tongue`, `languages_spoken` (array), `marital_status`, `children_existing`, `height_cm`, `weight_kg`, `religion`, `education_level`, `education_field`, `occupation_sector`, `annual_income`, `family_type`, `family_status`, `father_occupation`, `mother_occupation`, `siblings`, `known_conditions`

### `preferences` table (what they want in a partner)
`religious_practice`, `sect_denomination`, `caste_community`, `caste_importance`, `pref_religion`, `pref_religion_exclude` (array), `pref_caste`, `pref_caste_exclude` (array), `pref_mother_tongue`, `pref_education_min`, `pref_income_min`, `pref_diet`, `pref_drinking`, `pref_smoking`, `pref_age_min`, `pref_age_max`, `pref_height_min`, `pref_height_max`, `pref_manglik`, `pref_gotra_exclude` (array), `pref_family_status`, `pref_conditions`, `pref_partner_cooking` (F), `pref_partner_household` (F), `marriage_timeline`, `children_intent`, `children_timeline`, `living_arrangement`, `relocation_willingness`, `family_involvement`, `partner_working` (M only)

### `signals` table (behavioral/personality signals)
`diet`, `drinking`, `smoking`, `fitness_frequency`, `social_style`, `conflict_style`, `cooking_contribution` (both), `household_contribution` (M), `do_you_cook` (F), `career_after_marriage` (F), `financial_contribution` (F), `live_with_inlaws` (F), `financial_planning`, `manglik_status`, `gotra`, `family_property`, `family_values`

### `user_channels` table
`user_id`, `channel` (telegram/web/whatsapp), `channel_id`, `phone`

---

## On Hold / Future

- **Complexion** (self + preference) — waiting on photo upload. Regional bias makes self-reported complexion tricky.
- **Body type preference** — weight + height gives us BMI. No need for self-reported "slim/athletic/heavy."
- **Free text fields** (hobbies, about me, what you're looking for) — premium feature, not part of free matching flow.
- **Deep personality questions** (love language, communication style, values essays) — premium tier.
