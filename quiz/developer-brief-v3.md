# Masii v3 — Developer Implementation Brief

> Everything you need to implement the v3 question flow on web and chat.
> Read this top to bottom before writing any code.
>
> Author: Product (Nik) + AI audit
> Date: March 2026

---

## Table of Contents

1. What happened and why
2. File inventory — what to use, what to ignore
3. Architecture overview
4. How to use the YAML → JS generator
5. Web form: progress, navigation, and layout spec
6. Chat (Telegram/WhatsApp): intake funnel spec
7. Implementation checklist — priority order
8. Data migration
9. Things NOT to build yet (Wave 3)

---

## 1. What Happened and Why

The v2 question flow had significant drift between the spec (question-flow.md) and the code (form-config.js). 14 preference questions existed in the spec but weren't implemented. 6 questions the spec said to remove were still live. Diet options used different strings across religions, making matching impossible. Marriage timeline options didn't match between spec and code.

We audited the entire flow across three dimensions — tree/branching logic, option design, and copy/tone — then rebuilt everything from scratch with a YAML source of truth. The YAML now drives everything. There is no other source of truth.

Key changes:
- 81 questions (was ~60, but 7 removed, 4 added, 14 preference questions implemented)
- State-contextualized caste lists (raised_in_state drives Q12 dropdown ordering)
- Universal diet options (not religion-specific)
- 11 currency brackets for income (INR, USD, GBP, CAD, AED, SGD, SAR, QAR, AUD, EUR + default)
- Cross-currency tier system for income matching
- Sensitive gate removed — replaced with per-question "Prefer not to say"
- New Personality section (4 questions, standalone)
- All copy rewritten to match Masii brand voice
- Religious practice questions now include examples per level per religion
- Preference questions grouped with their parent via follow_ups

---

## 2. File Inventory

### Source of truth (edit these)

| File | What it is | When to edit |
|------|-----------|-------------|
| `masii-questions.yaml` | All 81 questions: IDs, copy, options, types, skip logic, gates, scoring, follow-ups, column counts | When changing any question, option, skip condition, or adding/removing questions |
| `masii-reference-data.yaml` | All dynamic option lists: castes by religion+state, income by currency, countries, states, languages, heights, weights, diets, education levels, occupation sectors | When adding a caste, country, income bracket, language, or changing any reference list |

### Generated (do not edit directly)

| File | What it is | How to regenerate |
|------|-----------|------------------|
| `form-config.generated.js` | The JS config used by the web form. All questions, options, reference data, and runtime resolver functions. | `python3 generate-form-config.py` |

### Generator script

| File | What it is |
|------|-----------|
| `generate-form-config.py` | Reads both YAMLs, outputs form-config.generated.js. Run after every YAML edit. |

### Reference documents (read-only, for context)

| File | What it is |
|------|-----------|
| `question-flow-v3.md` | Human-readable spec. Same content as the YAML but in markdown tables. Give to designers or product reviewers. |
| `v2-to-v3-changelog.md` | What changed from v2 to v3 — every question added, removed, rewritten. |
| `matching-protocol-v3-update.md` | Scoring rules for new/changed questions. Value string migration tables. |
| `masii-question-flow-audit.docx` | The original audit that led to v3. Background reading only. |
| `masii-brand-design-system.docx` | Brand colors, typography, voice guidelines. The form UI must follow this. |

### Files to retire

| File | Replace with |
|------|-------------|
| `form-config.js` (old) | `form-config.generated.js` |
| `question-flow.md` (v2) | `question-flow-v3.md` (reference) + `masii-questions.yaml` (source of truth) |
| `question_matching_protocol.md` (v2) | Keep v2 as base, apply `matching-protocol-v3-update.md` as addendum |

---

## 3. Architecture Overview

```
  masii-questions.yaml          masii-reference-data.yaml
  (questions, sections,         (castes, income, languages,
   transitions, copy)            countries, heights, etc.)
          │                              │
          └──────────┬───────────────────┘
                     │
          generate-form-config.py
                     │
                     ▼
          form-config.generated.js
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Web form    Telegram    WhatsApp
      (form.js)   bot         (future)
      CANONICAL   INTAKE      INTAKE
      75 Qs       10-12 Qs    10-12 Qs
```

**Rule: If it's not in the YAML, it doesn't exist.**

The generated JS includes runtime resolver functions:
- `getCastesByReligionAndState(religion, state)` — returns state-ordered caste list
- `getIncomeBrackets(country)` — returns currency-specific income options
- `getLanguagesSuggested(state)` — returns language list with state suggestion first
- `resolveOptions(questionId, answers)` — master resolver for any dynamic options
- `shouldSkip(questionId, answers)` — evaluates skip logic
- `getQuestionFlow(answers)` — returns full ordered question path for a user

---

## 4. How to Use the Generator

### Setup

```bash
pip install pyyaml    # one time
```

### Regenerate after any YAML edit

```bash
python3 generate-form-config.py
# or with custom paths:
python3 generate-form-config.py --questions path/to/masii-questions.yaml --reference path/to/masii-reference-data.yaml --out path/to/form-config.generated.js
```

### Workflow

1. Edit `masii-questions.yaml` or `masii-reference-data.yaml`
2. Run `python3 generate-form-config.py`
3. Test locally
4. Commit all three files (both YAMLs + generated JS) together
5. Never edit form-config.generated.js by hand

---

## 5. Web Form: Progress, Navigation, and Layout Spec

The web form is the canonical experience. All 75 questions (varies by gender/religion), full option sets, column layouts.

### 5.1 Progress Indicator

**Two-layer progress:**

```
┌─────────────────────────────────────────────────────┐
│  ● ● ● ● ◐ ○ ○ ○ ○ ○ ○ ○                          │
│  Basics  Background  Partner  Education  ...         │
│                                                      │
│  Education & Career                                  │
│  3 of 8                                              │
└─────────────────────────────────────────────────────┘
```

**Layer 1 — Section pills (top bar, always visible):**
- Horizontal row of dots/pills, one per section
- Completed sections: filled (solid dot, brand color --terracotta)
- Current section: half-filled or pulsing (--terracotta-soft)
- Upcoming sections: empty (--blush or --cream-deep border)
- Section labels below dots — use short labels: "Basics", "Background", "Partner", "Education", "Family", "Lifestyle", "Marriage", "Physical", "Household", "Sensitive", "Personality"
- 11 pills total (setup is pre-progress, doesn't show)
- Tapping a completed section pill does NOT navigate there (no random access — forward only with back for previous question)
- On mobile: pills scroll horizontally if needed, current section always centered

**Layer 2 — Within-section counter (below pills):**
- Section name in display font (Playfair Display)
- "3 of 8" in body font (DM Sans) below it
- Counter is within the current section only — not global
- Resets to "1 of N" when entering a new section
- N is dynamic — accounts for skipped questions within the section

**Implementation notes:**
- Use `getQuestionFlow(answers)` to determine total applicable questions per section
- Recalculate N whenever an answer changes skip logic downstream (e.g., marital_status changes children questions)
- Section transitions (the Masii voice text) display as a full-screen card BEFORE the first question of the new section, with the section pills visible above

### 5.2 Back Navigation

**Within-section back only (for now):**
- Left arrow or "← Back" link, top-left, below the progress pills
- Goes to the previous question within the current section
- If at the first question of a section, back goes to the last question of the previous section
- If at the very first question (intent), back is hidden
- Back does NOT clear the previously given answer — it lets the user review and change it
- If the user changes an answer that affects downstream skip logic (e.g., changes religion from Hindu to Muslim), clear all downstream answers that depend on it (caste, practice, etc.) and re-ask them

**Cross-section back is Wave 3.** For now, the section transition screen has no back button. Once you enter a new section, you can only go back within it.

### 5.3 Column Layout

Questions with 8+ options must render in multiple columns to reduce scrolling.

**Rule:** Check the `columns` property on each question in the generated config. If present, render that many columns. If absent, default to 1 column.

```
columns: 2   →  Two columns, options flow left-to-right, top-to-bottom
columns: 3   →  Three columns
columns: 4   →  Four columns (rare, only for very long lists)
```

**Mobile breakpoint:** On screens < 400px wide, columns: 3 and columns: 4 should collapse to columns: 2. Never go single-column for questions marked with columns.

**Which questions have column directives:**

| Question | Options count | Columns |
|----------|:---:|:---:|
| mother_tongue | 21 | 3 |
| languages_spoken | ~20 | 3 |
| religion | 9 | 2 |
| caste_community | 10-50 | 3 |
| pref_caste_exclude | 10-50 | 3 |
| pref_religion_exclude | 8 | 2 |
| education_level | 6 | 2 |
| education_field | 10 | 2 |
| occupation_sector | 15 | 3 |
| annual_income | 8-10 | 2 |
| pref_income_min | 8-10 | 2 |
| diet | 9 | 2 |
| height (M) | 13 | 2 |
| height (F) | 8 | 2 |
| weight | 9 | 2 |
| birth_year | 37 | 3 |

### 5.4 Question Types

| Type | Rendering | Notes |
|------|-----------|-------|
| `single_select` | Pill/chip buttons. One selectable. | Tap selects and auto-advances after brief delay (300ms). |
| `multi_select` | Pill/chip buttons with tick marks. Multiple selectable. | Show "Done ✓" button at bottom. Tick indicator on selected items (currently broken — needs fixing). |
| `text_input` | Single text field with placeholder. | Show keyboard on focus. Submit on Enter or "Next" button. |
| `phone_input` | Phone field with country code picker. | Auto-detect from Q2 location. |
| `location_tree` | Multi-step: Step 1 (India/Outside) → Step 2 (State/Country) → Step 3 (City text input). | Each step is a separate screen. |
| `two_step_date` | Step 1: Year grid (3 columns). Step 2: Month grid (2 columns). | |
| `two_step_range` | Step 1: Min selector. Step 2: Max selector (starts at min). | Two separate screens. |
| `two_step_same_screen` | Min and max dropdowns side by side on one screen. + "Doesn't matter" button above. | Used for height preference (Q41). Both dropdowns visible simultaneously. |

### 5.5 Follow-up Grouping

Questions with `followUps` in the config should display their follow-ups immediately after, before moving to the next top-level question. The flow engine (`getQuestionFlow`) already handles this ordering — the form just needs to iterate the returned array.

Example: `marital_status` has followUps: `[pref_marital_status, children_existing, pref_children_existing]`. The flow will be:
1. marital_status
2. pref_marital_status
3. children_existing (skipped if Never married)
4. pref_children_existing (skipped if Never married)
5. height (next top-level question)

### 5.6 Section Transition Screens

When the section changes between two consecutive questions in the flow:

1. Show a full-width card with:
   - Section name (Playfair Display, --earth color)
   - Masii's transition text (DM Sans, --earth-medium)
   - "Continue →" button (pill-shaped, --terracotta background)
2. The progress pills at top update to show the new current section
3. Transition screens do not count toward the within-section counter

### 5.7 Intro Screen

Single screen before the form starts. Content from `INTRO.text` and `INTRO.button` in the generated config. Full-width card, centered text, single CTA button.

### 5.8 Close Screen

After the last question, show the close message from `CLOSE_MESSAGE` in the config. Replace `{name}` with preferred_name. Then collect phone number (if not already known) and submit.

---

## 6. Chat (Telegram/WhatsApp): Intake Funnel

Chat platforms are NOT the canonical form. They are intake funnels — collect enough to register the person and the top hard gates, then send them to the web form for the full profile.

### 6.1 Why

- Telegram inline keyboards max out at ~8 buttons before UX breaks
- WhatsApp has no inline keyboards — only numbered lists (max 10) and no multi-select
- Questions like Q12 (caste, 15+ options), Q4 (21 languages), Q18 (15 sectors) cannot render well in chat
- A 75-question chat flow would take 30+ minutes and have catastrophic abandonment

### 6.2 Chat Intake Questions (10-12 questions)

These questions give Masii enough for basic matching and all critical hard gates:

| # | Field | Question | Options | Gate |
|---|-------|----------|---------|------|
| 1 | preferred_name | What should I call you? | text | — |
| 2 | gender | Male or female? | Male / Female | Hard |
| 3 | date_of_birth | What year were you born? | Year picker (paginated if needed) | — |
| 4 | current_location | Where do you live? | India / Outside India → State/Country | Hard |
| 5 | religion | What is your religion? | 8 options (fits Telegram) | — |
| 6 | marital_status | Marital status? | 4 options | Hard |
| 7 | mother_tongue | Mother tongue? | Top 8 for their state + Other | — |
| 8 | diet | What is your diet? | Top 6 options (Veg / Eggetarian / Non-veg / Occasionally non-veg / Jain / Halal only) | — |
| 9 | education_level | Highest education? | 6 options | — |
| 10 | marriage_timeline | How soon? | 4 options | Hard |
| 11 | caste_community | Caste? (if Hindu/Jain/Sikh) | Top 6 for their state + Other | — |
| 12 | pref_religion | Partner's religion? | Same only / Open to all / Open but not... | Hard |

### 6.3 Chat Close + Web Handoff

After the 10-12 questions:

```
Got it, {name}. I have enough to start looking.

But the better I know you, the better the match. 
Complete your full profile here — it takes about 8 minutes:

[Complete Profile →] {web_form_link}

I'll message you when I find someone worth your time.

— Masii
```

The web form link should:
- Pre-fill all answers from the chat intake (name, gender, DOB, location, religion, etc.)
- Start the web form at the first unanswered question (skip completed sections)
- Show a "Welcome back, {name}" screen instead of the intro

### 6.4 Chat Platform Notes

**Telegram:**
- Use inline keyboards (buttons below messages) for single_select
- Max 8 buttons per question (paginate if needed)
- For multi-select: not natively supported. Use toggle buttons + "Done" button.
- For text input: just ask and wait for text reply

**WhatsApp (future):**
- Use List Messages (max 10 items per section, max 10 sections)
- For single_select: list message with radio buttons
- No multi-select native support — use numbered replies ("Reply 1, 3, 5 to select")
- For text input: just ask and wait

---

## 7. Implementation Checklist — Priority Order

### Wave 1: Get the web form working on v3 (blocks matching)

- [ ] Run `python3 generate-form-config.py` to generate `form-config.generated.js`
- [ ] Replace old `form-config.js` with `form-config.generated.js` in the web app
- [ ] Update `form.js` to use new config structure:
  - [ ] Questions are now an array of objects (not numbered keys). Use `QUESTION_INDEX[id]` to look up by ID.
  - [ ] Use `getQuestionFlow(answers)` to get the ordered question path instead of incrementing a number
  - [ ] Use `resolveOptions(questionId, answers)` instead of the old `getConditionalOptions`
  - [ ] Use `shouldSkip(questionId, answers)` instead of the old `shouldSkipQuestion`
  - [ ] Handle new question type `two_step_same_screen` (height pref — two dropdowns side by side)
  - [ ] Handle `follow_ups` — the flow engine already orders them, just iterate
  - [ ] Handle `optionsConditional` — call `resolveOptions` which handles conditional resolution
- [ ] Implement section transition screens between sections
- [ ] Remove the sensitive gate (Q53 in old code) — no more gate, questions just appear with "Prefer not to say" options
- [ ] Remove old skipped questions from rendering (Q11, Q24, Q28, Q50/financial_contribution, Q55/gotra, Q56/property)
- [ ] Add `preferred_name` field after `full_name` in setup
- [ ] Update the intro to single screen
- [ ] Update the close message
- [ ] Update error messages (remove emojis)
- [ ] Test both gender paths end-to-end (Hindu Male, Muslim Female NRI)
- [ ] Test skip logic: religion→caste skip, marital→children skip, gender fork, manglik skip

### Wave 2: UX improvements

- [ ] Implement section-based progress pills (see section 5.1)
- [ ] Implement within-section counter (see section 5.1)
- [ ] Implement back navigation within sections (see section 5.2)
- [ ] Implement column layouts for 8+ option questions (see section 5.3)
- [ ] Fix multi-select tick indicators
- [ ] Apply brand colors to form (cream backgrounds, terracotta accents, earth text — see brand design system)
- [ ] Implement auto-save at section boundaries

### Wave 3: Chat intake + structural

- [ ] Build Telegram intake flow (10-12 questions, see section 6)
- [ ] Build web form pre-fill from chat answers
- [ ] Build "Welcome back" resume screen for web form handoff
- [ ] Cross-section back navigation
- [ ] Mid-form save point after Education section

---

## 8. Data Migration

If the database has v2 data, these fields need value remapping before v3 matching can work. See `matching-protocol-v3-update.md` for complete old→new value tables.

**Fields needing migration scripts:**

| Field | Change |
|-------|--------|
| diet | Religion-specific strings → universal strings |
| cooking_contribution | "0", "1-3", "4-7" etc. → "Rarely or never", "Occasionally" etc. |
| do_you_cook | "Yes, I cook regularly" → "I cook often" etc. |
| household_contribution | Minor relabeling |
| partner_working | "Prefer she focuses on home" → "Prefer homemaker" |
| career_after_marriage | "Yes, definitely" → "Full steam ahead" etc. |
| conflict_style | "Talk it out immediately" → "Address immediately" etc. |
| marriage_timeline | "Within 6 months" → "Within 1 year"; "In the next 1 year" → "Within 1 year" |
| family_status | "Middle class" etc. → "tier_1" through "tier_5" |
| annual_income | "Under ₹5 lakh" → "INR_1" etc. (tiered values for cross-currency matching) |

**New columns to add (no migration, just ALTER TABLE):**

`preferred_name`, `raised_in_state`, `company_name`, `disability`, `weekend_style`, `communication_style`, `pref_current_location`, `pref_raised_in`, `pref_marital_status`, `pref_children_existing`, `pref_education_field`, `pref_family_type`, `pref_siblings`, `pref_children_timeline`, `pref_living_arrangement`, `pref_partner_cooking_freq`, `pref_partner_can_cook`, `pref_disability`, `relocation_countries`

---

## 9. Things NOT to Build Yet (Wave 3+)

- **Cross-section back navigation** — Only within-section back for now
- **Non-binary gender** — "More options coming soon" helper text is in place, matching logic not designed yet
- **Complexion** — Photo-only policy. Do not add self-reported complexion questions.
- **Free text fields** (hobbies, about me) — Premium feature, not in free form
- **Sect/denomination, gotra** — Premium features
- **Mermaid flow diagrams** — Nice-to-have visualization of the question tree, not blocking
- **Admin panel / CMS** — For editing questions via UI instead of YAML. Future.

---

## Quick Reference: Key Functions in form-config.generated.js

```javascript
// Get the full question flow for a user
const flow = getQuestionFlow(answers);
// Returns: ["intent", "full_name", "preferred_name", "gender", "date_of_birth", ...]

// Look up a question by ID
const q = QUESTIONS[QUESTION_INDEX["mother_tongue"]];

// Resolve dynamic options
const options = resolveOptions("caste_community", answers);
// Returns: [{ label: "Brahmin", value: "Brahmin" }, ...]  (state-ordered)

// Check if a question should be skipped
const skip = shouldSkip("manglik_status", answers);
// Returns: true/false

// Get castes for a religion + state
const castes = getCastesByReligionAndState("Hindu", "Tamil Nadu");
// Returns: Brahmin, Iyer, Iyengar, Nadar, Thevar... (TN first, then others)

// Get income brackets for a country
const brackets = getIncomeBrackets("UAE");
// Returns: AED brackets with tier numbers for cross-currency matching

// Get suggested language for a state
const langs = getLanguagesSuggested("Kerala");
// Returns: Malayalam first, then rest of list
```
