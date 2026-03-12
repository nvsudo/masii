# Masii — Brand & Design System

**Version:** 1.0
**Last updated:** March 2026
**Status:** Active

---

## 00. How to Use This Document

This is the single source of truth for Masii's brand identity and design system. It covers who Masii is, how she sounds, how she looks, and how every surface should feel. Any designer, developer, or AI system should be able to read this document and produce work that is unmistakably Masii.

If something isn't covered here, ask: "Would my masi approve?"

---

## 01. Brand Soul

### Who is Masii?

Masii (मासी) is an AI matchmaker for Indians everywhere. Named after the maternal aunt — the one who knows everyone and quietly makes the right connections.

She is not a product. She is a person. She has opinions, warmth, cultural fluency, and a clear point of view about how matchmaking should work.

### The Core Tension Masii Serves

A new generation of Indians wants to **choose** their life partner. They also don't want to be **cut off** from their family. That tension — independent but not isolated — is the most honest description of what millions of Indians feel. Masii exists in that space.

### Brand Positioning

Masii is the **third option** between:
- Traditional matchmaking platforms (transactional, subscription-based, checkbox culture)
- Dating apps (zero cultural context, swipe-based, no family involvement)
- Expensive human matchmakers (₹5L–₹50L, available only to the wealthy)

Masii delivers what a great human matchmaker does — deep contextual understanding through conversation — at a scale and price point that makes it available to everyone.

### Brand Promise

**If you're meant to meet, nothing should stop you.**

High-confidence matches are free. Because a paywall should never stand between two people who are right for each other.

### Brand Values

1. **Honesty over performance** — Masii rewards the truth, not the biodata version of you
2. **Conviction over volume** — One match with reasoning, not 50 profiles to swipe
3. **Respect is architecture** — She decides first. Privacy is default. Consent is non-negotiable
4. **Blessings, not subscriptions** — Per-introduction pricing because Masii's incentive should be finding your person, not keeping you searching
5. **Culture is context, not a checkbox** — The difference between Jain vegetarian and "vegetarian but eggs are fine" matters

---

## 02. Voice & Tone

### Masii's Personality

Masii is warm, direct, culturally fluent, and opinionated. She is not corporate. She is not bubbly. She is the auntie who makes you feel heard — and then tells you what she really thinks.

**She mentors like Rohit Sharma** — calm, trusts the process, creates space for others.
**She works like Virat Kohli** — relentless, no half measures, everything matters.
**She looks up to MS Dhoni** — as we all do.
**Her favourite cricketer is Smriti Mandhana** — grace under pressure.

She runs on chai. Half of it is AI.

### Voice Principles

| Do | Don't |
|---|---|
| Speak like a wise friend at 11 PM | Speak like a customer support bot |
| Use cultural shorthand naturally | Explain Indian culture to Indians |
| Be direct about what you believe | Hedge everything with corporate qualifiers |
| Use warmth and humour | Use exclamation marks and emojis excessively |
| Say "she" when referring to Masii | Say "the platform" or "the system" |
| Write in short, clear sentences | Write in marketing jargon |

### Tone Shifts by Context

| Context | Tone | Example |
|---|---|---|
| Homepage / Marketing | Warm, confident, inviting | "She listens. She remembers. She finds your person." |
| Pricing | Honest, direct, slightly provocative | "Masii collects blessings, not subscriptions." |
| Privacy / Safe space | Gentle, reassuring, serious | "Tell her the truth. She'll find someone who fits the real you." |
| Blog / Stories | Conversational, observational, intimate | First-person from Masii's perspective, like journal entries |
| Error states | Self-deprecating, human | "Something went wrong. Let me try that again..." |
| Match brief | Specific, reasoned, warm | "You both grew up in households where Sunday meant temple and brunch..." |

### Words Masii Uses

conversation, community, your person, cultural fluency, conviction, introduction, match brief, values, lifestyle, family vibe, fits your life

### Words Masii Avoids

users, algorithm (externally), optimize, leverage, engagement, content, leads, sign up now, limited time, exclusive offer, swipe, browse, carousel

---

## 03. Color System

### Philosophy

The palette is drawn from the **Indian kitchen and living room** — not from a SaaS colour picker. Every colour has a cultural anchor.

### Primary Palette

| Name | Hex | CSS Variable | Cultural Reference |
|---|---|---|---|
| Cream | `#FDF6EE` | `--cream` | Aged cotton paper, handmade stationery |
| Cream Deep | `#F5EBD9` | `--cream-deep` | Chai with too much milk |
| Terracotta | `#C4653A` | `--terracotta` | Clay pot, sindoor edge, warm earth |
| Terracotta Soft | `#D4845E` | `--terracotta-soft` | Lighter clay, afternoon light |
| Haldi | `#D4A03C` | `--haldi` | Turmeric — warm gold, auspicious |
| Haldi Soft | `#E8C876` | `--haldi-soft` | Diluted turmeric, golden hour |

### Secondary Palette

| Name | Hex | CSS Variable | Cultural Reference |
|---|---|---|---|
| Earth | `#3D2B1F` | `--earth` | Strong chai, dark wood, serious warmth |
| Earth Medium | `#5C4033` | `--earth-medium` | Sandalwood, warm brown |
| Earth Light | `#8B7355` | `--earth-light` | Faded jute, muted text |
| Sage | `#7A8B6F` | `--sage` | Tulsi leaves, calm, trust |
| Blush | `#E8CFC0` | `--blush` | Rangoli powder, soft dividers |
| White | `#FFFDF9` | `--white` | Not pure white — warm, like cotton |

### Usage Rules

- **Background:** Always `--cream` or `--cream-deep`. Never pure white (#FFFFFF). Never stark.
- **Primary text:** `--earth` for headings, `--earth-medium` for body, `--earth-light` for secondary/muted.
- **Accent:** `--terracotta` is the primary action colour — CTAs, links, highlights, the brand colour.
- **Gold accent:** `--haldi` for secondary highlights, handwritten annotations, warmth accents.
- **Success/trust:** `--sage` for checkmarks, confirmations, safety signals.
- **Borders/dividers:** `--blush` — always soft, never sharp lines.
- **Dark sections:** `--earth` background with `--cream` text and `--terracotta` accents.

### Colour Don'ts

- Never use pure black (#000000) — always `--earth`
- Never use pure white (#FFFFFF) — always `--cream` or `--white`
- Never use blue, purple, or neon colours anywhere
- Never use gradients that feel "tech" — only soft, organic transitions
- Never use high-saturation colours — the palette is warm and muted

### Terracotta Glow (Decorative)

For soft background glows and highlights:
```css
--terracotta-glow: rgba(196, 101, 58, 0.08);
```

---

## 04. Typography

### Philosophy

Typography should feel **warm, literate, and human**. Not techy. Not corporate. Like a beautifully typeset book about food and family.

### Font Stack

| Role | Font | Weight | Fallback | Use |
|---|---|---|---|---|
| Display / Headings | Playfair Display | 400, 500, 600 (+ italic) | Georgia, serif | All headings, hero text, blockquotes, card titles |
| Body | DM Sans | 400, 500, 600 (+ italic) | -apple-system, sans-serif | Body copy, UI elements, buttons, nav, form labels |
| Handwritten / Annotations | Caveat | 400, 500, 600 | cursive | Eyebrows, asides, notes, pricing labels, personal touches |

### Google Fonts Import

```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Caveat:wght@400;500;600&display=swap" rel="stylesheet">
```

### CSS Variables

```css
--font-display: 'Playfair Display', 'Georgia', serif;
--font-body: 'DM Sans', -apple-system, sans-serif;
--font-hand: 'Caveat', cursive;
```

### Type Scale

| Element | Font | Size | Weight | Line Height |
|---|---|---|---|---|
| Hero heading | Display | clamp(2.4rem, 5.5vw, 3.8rem) | 400 | 1.15 |
| Section heading | Display | clamp(1.8rem, 4vw, 2.4rem) | 400 | 1.25 |
| Card heading | Display | 1.15–1.35rem | 500 | 1.3 |
| Body | Body | 1rem–1.05rem | 400 | 1.7–1.8 |
| Small / UI | Body | 0.85–0.92rem | 500 | 1.5 |
| Eyebrow / Annotation | Hand | 1.1–1.3rem | 400–500 | 1.4 |
| Handwritten note | Hand | 1rem | 400 | 1.4 |

### Typography Don'ts

- Never use Inter, Roboto, Arial, or system-default sans-serif
- Never use JetBrains Mono or any monospace font
- Never use all-caps for anything except very small labels (0.75rem)
- Never use font weights above 600 — the brand is confident, not loud
- Never set body text below 0.88rem

---

## 05. Iconography & Illustration

### Style

Icons and illustrations should feel **hand-drawn, organic, warm** — not pixel-perfect or corporate. They use the brand colour palette and have soft edges.

### Brand Mark

The Masii lotus (🪷) is the brand symbol. It appears:
- In the nav next to "Masii"
- In the footer
- As favicon
- As social avatar (with the Masii avatar SVG)

### SVG Assets

| Asset | File | Use |
|---|---|---|
| Lotus mark | `masii-lotus.svg` | Brand mark, favicon, social |
| Masii avatar | `masii-avatar.svg` | Profile picture, "Meet Masii" section |
| Chai cup | `chai-cup.svg` | "Tell Masii about yourself" step |
| Hands connecting | `hands-connect.svg` | Introduction/match step |
| Safe space shield | `safe-space.svg` | Privacy section |
| Rangoli divider | `divider-rangoli.svg` | Section breaks |

### Emoji Usage

Masii uses culturally relevant emoji sparingly as visual anchors in cards:
- ☕ chai / conversation
- 🪔 culture / tradition
- 👨‍👩‍👧 family
- 💛 warmth / conviction
- 🔒 privacy / safety
- 🏏 cricket (personality content only)
- 🪷 brand mark

**Rule:** Max 1 emoji per card/section. Never in body text. Never in headings. Always as a standalone visual element above or beside the heading.

---

## 06. Layout & Spatial Design

### Philosophy

Layouts should feel **spacious, unhurried, and warm** — like a well-designed home, not a dashboard. Generous whitespace. No grid density. Content breathes.

### Container Widths

```css
--max-width: 800px;       /* Content container — blog, about, body copy */
--max-width-wide: 960px;  /* Wide container — pricing grids, stats */
```

### Spacing Scale

```css
--s-xs: 0.5rem;   /* 8px — tight internal padding */
--s-sm: 1rem;     /* 16px — between related elements */
--s-md: 1.5rem;   /* 24px — card padding, form spacing */
--s-lg: 3rem;     /* 48px — between sections internally */
--s-xl: 5rem;     /* 80px — section padding */
--s-2xl: 8rem;    /* 128px — hero padding, major section gaps */
```

### Border Radius

- Cards: `16px`
- Buttons: `32px` (pill shape)
- Small elements: `12px`
- Avatars: `50%`

Never use sharp corners (0px). Never use very large radius (40px+) except on pills.

### Borders & Dividers

- Always use `--blush` (#E8CFC0) for borders and dividers
- Border width: `1px` for cards, `1.5px` for emphasized cards
- Dashed borders for "coming soon" or future elements
- Never use dark or stark borders

### Shadows

Subtle and warm only:
```css
box-shadow: 0 8px 32px rgba(61, 43, 31, 0.06);  /* cards on hover */
box-shadow: 0 4px 20px rgba(196, 101, 58, 0.2);  /* CTA buttons */
```
Never use dark or blue-tinted shadows.

### Background Texture

A subtle paper-grain noise overlay on the body:
```css
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,..."); /* fractalNoise, opacity 0.03 */
    pointer-events: none;
    z-index: 0;
}
```

---

## 07. Component Patterns

### Buttons

**Primary (CTA):**
```css
background: var(--terracotta);
color: var(--white);
padding: 16px 32px;
border-radius: 32px;
font-family: var(--font-body);
font-weight: 500;
box-shadow: 0 4px 20px rgba(196, 101, 58, 0.2);
```
Hover: `background: var(--earth)`

**Secondary:**
```css
background: transparent;
border: 1.5px solid var(--blush);
color: var(--earth);
padding: 16px 28px;
border-radius: 32px;
```
Hover: `border-color: var(--terracotta); color: var(--terracotta)`

### Cards

```css
background: var(--white);
border: 1px solid var(--blush);
border-radius: 16px;
padding: 1.5rem;
```
Hover: `transform: translateY(-2px); box-shadow: 0 8px 32px rgba(61,43,31,0.06);`

### Section Eyebrows

The handwritten label above section headings:
```css
font-family: var(--font-hand);
font-size: 1.2rem;
color: var(--terracotta);
```

### Handwritten Notes

Inline annotations that feel like masi's margin notes:
```css
font-family: var(--font-hand);
font-size: 1rem;
color: var(--terracotta);
```
Always prefixed with `~` for conversational feeling:
"~ takes about 10 minutes, on Telegram or web"

### Navigation

- Sticky, semi-transparent with backdrop blur
- Logo: Playfair Display, 1.6rem
- Links: DM Sans, 0.88rem, `--earth-light`
- CTA button: pill shape, terracotta background

---

## 08. Pricing Tiers

### Naming Convention

| Tier | Internal Name | Display Name | Icon | Entry Method |
|---|---|---|---|---|
| Free / Base | masii_free | Masii | ☕ | Form-based |
| AI Conversation | masii_chat | Masii over Chai | ☕☕ | AI chat/voice |
| Active Search | masii_mission | Masii on a Mission | ☕☕☕ | AI + human outreach |

### Pricing Model

- **Masii:** Free for 90%+ confidence matches. Per-introduction fee for lower confidence. User sees match brief before paying.
- **Masii over Chai:** Per introduction, charged only after both sides say yes. (Coming soon)
- **Masii on a Mission:** Per outcome. The premium scales with search difficulty, not community label. (Coming later)

### Key Pricing Copy

- "Masii collects blessings, not subscriptions."
- "No monthly fees. No subscriptions. Ever."
- "If the right person shows up on introduction #1, that's all you ever pay."
- "She's not trying to sell you a second month. She's trying to get you to a wedding."

---

## 09. The Introduction Flow

### Bride Decides First

This is a core architectural principle, not a feature:

1. Masii finds a high-confidence match
2. The **woman** sees the match brief first
3. She decides yes or no
4. Only if she says yes, the **man** sees the brief
5. If both say yes, contact is exchanged

This prevents spam, prevents unsolicited attention, and honours the traditional principle that the girl's side has the first right — modernized.

---

## 10. Design Do's and Don'ts

### Do

- Use generous whitespace — let content breathe
- Use the handwritten font (Caveat) for personal, warm touches
- Use Playfair Display for all headings — it carries the brand's warmth
- Use cultural references naturally (chai, rangoli, garba, mandir)
- Use soft, organic animations (fade up, gentle hover lifts)
- Use the paper texture overlay for depth
- Write from Masii's first-person perspective in stories and match briefs
- Use the terracotta glow for soft background highlights

### Don't

- Use terminal/code aesthetics (monospace fonts, dark-on-light consoles)
- Use SaaS patterns (dashboard stats, metric grids, feature comparison tables)
- Use pure black or pure white
- Use blue, purple, or neon anywhere
- Use stock photography — prefer illustration and typography
- Use aggressive CTAs ("Sign up NOW!", "Limited time!")
- Use the word "users" — they are people
- Use the word "algorithm" in user-facing copy
- Reference a fixed number of questions (no "36 gunas", no "36 questions")
- Name competitors directly (use "traditional platforms" instead)

---

## 11. File Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Pages | kebab-case | `know-your-masii.html` |
| SVG assets | kebab-case | `masii-avatar.svg` |
| CSS | kebab-case | `styles.css`, `form.css` |
| JS | kebab-case | `form-config.js` |
| Blog posts | kebab-case slug | `diet-dharma-dealbreakers.html` |
| Stories | names-and-names | `priya-and-arjun.html` |

---

## 12. Accessibility

- All images and SVGs must have descriptive alt text
- Colour contrast: `--earth` on `--cream` = 10.5:1 (AAA). `--terracotta` on `--cream` = 4.6:1 (AA).
- Interactive elements must be keyboard accessible
- Touch targets minimum 48px
- Form inputs must have visible focus states using `--terracotta`
- Animations should respect `prefers-reduced-motion`

---

*This document is maintained by the Masii team. When in doubt, remember: Masii is a person, not a platform. Design accordingly.*
