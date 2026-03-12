# Masii: 36-Guna / 36-Question Removal Guide

Every instance across the codebase where "36 gunas", "36 questions", or the fixed number 36 is used in relation to the question flow. Replace with flexible language.

---

## PRODUCT COPY / HOMEPAGE / FORMS

### `index.html` (homepage)
- **"Masii asks you 36 questions — like the 36 gunas, but for real life."**
  → Replace with: "Masii asks you about your values, your lifestyle, your family, your future."
- **"36 questions. 10 minutes."** (referenced in start.html)
  → Replace with: "A few minutes. An honest conversation."

### `start.html` (channel picker)
- **"36 questions. 10 minutes. Choose how you'd like to do it."**
  → Replace with: "A conversation about who you are. Choose how you'd like to do it."

### `form.html`
- **`<title>Masii — The 36 Gunas</title>`**
  → Replace with: `<title>Masii — Tell Us About You</title>`
- **"Tell Masii about yourself. 36 questions about your values, lifestyle, family, and future."**
  → Replace with: "Tell Masii about yourself. Your values, lifestyle, family, and future."

### `about.html`
- No direct "36" references. Clean.

---

## BLOG POSTS

### `blog/36-gunas-explained.html`
- **DECISION: This entire blog post is about the 36-guna concept.**
- Options:
  1. **Keep but reframe**: Change title to "What the gunas teach us about compatibility" — make it a cultural/historical essay, not a product feature description. Remove any claims that Masii uses 36 questions specifically.
  2. **Archive/remove**: If you don't want any association with the number.
- Specific lines to change if keeping:
  - Title: "The 36 gunas, explained" → "What the gunas teach us about compatibility"
  - Remove any implication Masii uses exactly 36 questions

### `blog/building-trust-with-ai.html`
- **"Why 36 questions"** (entire H2 section)
  → Rewrite section header to: "Why the right questions matter"
  → Replace: "The number isn't random. It comes from research..." with language about question design without a fixed number
- **"36 is the number where we get enough signal..."**
  → Remove or replace with: "We ask enough to match with confidence while keeping the conversation short enough that people finish it."
- **"Each question does multiple things at once."** — This is fine, keep.
- **"Don't ask 36 shallow questions. Ask 36 deep ones."**
  → Replace with: "Don't ask shallow questions. Ask deep ones."

### `blog/confidence-gap.html`
- **"She looks at 36 signals that a thoughtful auntie would care about."**
  → Replace with: "She looks at dozens of signals that a thoughtful auntie would care about."

### `blog/conversation-not-form.html`
- No "36" references. Clean.

### `blog/culture-not-checkbox.html`
- No "36" references. Clean.

### `blog/diaspora-dating.html`
- No "36" references. Clean.

### `blog/diet-dharma-dealbreakers.html`
- No "36" references. Clean.

### `blog/family-approval-solved.html`
- No "36" references. Clean.

### `blog/how-ai-reads-between-lines.html`
- No "36" references. Clean.

### `blog/long-distance-diaspora.html`
- No "36" references. Clean.

### `blog/matchmaking-is-not-dating.html`
- No "36" references. Clean.

### `blog/the-case-for-fewer-matches.html`
- No "36" references. Clean.

### `blog/the-nri-homecoming.html`
- No "36" references. Clean.

### `blog/the-proxy-problem.html`
- No "36" references. Clean.

### `blog/what-high-confidence-means.html`
- **"she looks at 36+ signals across culture, values, lifestyle, and family"** (meta description + body)
  → Replace with: "she looks at dozens of signals across culture, values, lifestyle, and family"
- **"The 36 signals"** (H2)
  → Replace with: "The signals that matter"

### `blog/what-your-masi-knew.html`
- No "36" references. Clean.

### `blog/why-free-matches.html`
- No "36" references. Clean.

### `blog/why-no-photos-first.html`
- No "36" references. Clean.

### `blog/why-we-chose-telegram.html`
- No "36" references. Clean.

### `blog/index.html` (blog listing)
- **"People trust their masi because she's known them for years. How does an AI build that trust through 36 carefully designed questions?"**
  → Replace with: "...How does an AI build that trust through carefully designed questions?"
- **"Masii doesn't match on one dimension. She looks at 36+ signals..."**
  → Replace with: "...She looks at dozens of signals..."
- **"The 36 gunas, explained"** (blog listing entry)
  → Update title to match whatever the blog post becomes
- **"What the traditional 36 gunas are, why they worked, and how Masii reimagines them"**
  → Update description to match

---

## STORIES

### `stories/index.html`
- No "36" references. Clean.

### All individual story files
- No "36" references found. Clean.

---

## JAVASCRIPT

### `js/form-config.js`
- **`const TOTAL_QUESTIONS = 60;`** — This is fine (internal logic, not user-facing)
- **`const TOTAL_GUNAS = TOTAL_QUESTIONS;`** — Rename to `TOTAL_FORM_QUESTIONS`
- **Phase names use "gunas" internally** — Optional rename for code cleanliness but not user-facing
- **Section title "The 36 Gunas"** referenced in form.html title — already covered above

### `js/form.js`
- Internal variable `currentGuna`, `showGuna()`, `renderGunaQuestion()` etc.
  → Optional code cleanup: rename to `currentQuestion`, `showQuestion()`, etc.
  → Not user-facing, so lower priority

### `js/auth.js`, `js/main.js`
- No "36" references. Clean.

---

## ONBOARDING / AUTH PAGES

### `onboarding.html`
- **"We'll ask you 36 thoughtful questions about who you are"**
  → Replace with: "We'll have a conversation about who you are"

### `login.html`, `signup.html`
- No "36" references. Clean.

---

## CSS FILES
- No "36" references. Clean.

---

## SUMMARY

**Files requiring changes:**
1. `index.html` — 1 change
2. `start.html` — 1 change
3. `form.html` — 2 changes (title + meta)
4. `onboarding.html` — 1 change
5. `blog/36-gunas-explained.html` — Full reframe or archive
6. `blog/building-trust-with-ai.html` — 3 changes
7. `blog/confidence-gap.html` — 1 change
8. `blog/what-high-confidence-means.html` — 2 changes
9. `blog/index.html` — 3 changes
10. `js/form-config.js` — 1 rename (TOTAL_GUNAS → TOTAL_FORM_QUESTIONS)

**Files clean (no changes needed):** All other blog posts, stories, CSS, auth pages.
