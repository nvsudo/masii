# Run Log

All changes and decisions, one line each.

| Date | Change |
|------|--------|
| 2026-03-12 | Removed "Masii is listening" warm-header bar from homepage — distraction |
| 2026-03-12 | Consolidated "How it works" + "How introductions work" into single section on homepage — was repetitive, and one-cup page already covers the full flow |
| 2026-03-12 | Fixed "Not a form. A conversation" copy — product is a quiz, rewrote to reflect that |
| 2026-03-12 | Revised hero: headline → "Meet Masii — India's favourite matchmaking auntie", description split into two lines — action line + trait line |
| 2026-03-12 | Hero tagline iterated: "Culturally fluent" → "She gets the nuance" → "She knows the difference" → "Desi. Private. Global." — three words, felt not explained |
| 2026-03-12 | Reordered homepage: Hero → How It Works → Safe Space → Meet Masii → Pricing → Quote → CTA. Dropped "Why Masii" section (redundant). Trimmed Safe Space from 4 cards to 3, cut duplicate copy. |
| 2026-03-12 | Homepage pricing: expanded from thin teaser to full section — ₹151 price, 90%+ free card, 4-step payment flow, blog link |
| 2026-03-12 | pricing.html: removed two future cup tiers (Masii over Chai, Masii on a Mission) — only current ₹151 offering shown |
| 2026-03-12 | pricing.html: condensed philosophy to one paragraph, moved full argument to blog piece |
| 2026-03-12 | one-cup.html: stripped all pricing content (promise card, launch pricing, progress bar, coming soon) — now focused on quiz flow only |
| 2026-03-12 | Created blog/pricing-paradigm.html — "People matching — the new pricing paradigm" — absorbs pricing philosophy |
| 2026-03-12 | Replaced "No subscription. No monthly fee. Ever." with "No hidden fees. No gotchas." across all pages — future products may have subscriptions |
| 2026-03-12 | Replaced "say yes" / "said yes" with "interested" / "agree to be introduced" across all pages — "say yes" could imply marriage consent |
| 2026-03-12 | Replaced "the woman" / "the girl's family" with "her side" / "her family" across all pages — avoids Masii/her pronoun confusion and sounds more natural in Indian matchmaking context |
| 2026-03-12 | Added SRK Om Shanti Om quote ("kehte hain agar kisi cheez ko dil se chaaho...") to pricing-paradigm blog — 90%+ free matches section. Pop culture references to be used selectively. |
| 2026-03-12 | Removed "lower confidence matches" paragraph from pricing blog — was underselling the product. Platforms charge fees, no need to justify. |
| 2026-03-12 | Archived stories/ to archive/stories/ — stories reflect free-text product that doesn't exist yet. Removed Stories from all navs and footers (27 files). Will bring back when real matches happen. |
| 2026-03-12 | Fixed nav consistency across all blog pages: logo now includes 🪷 flower, CTA links point to one-cup.html (was start.html). Fixed know-your-masii.html CTA too. |
| 2026-03-12 | Blog brand alignment: fixed Google Fonts (was Instrument Serif/Inter/JetBrains Mono → Playfair Display/DM Sans/Caveat), nav links (Why Masii → Meet Masii, About → Pricing), css/styles.css nav-cta (dark square → terracotta pill), btn-primary (dark square → terracotta pill with shadow), nav (solid → frosted glass blur), added paper texture background. All 22 blog files updated. |
| 2026-03-12 | Created js/components.js — single source of truth for nav + footer. Replaced inline nav/footer HTML across all pages (index, pricing, one-cup, know-your-masii, 22 blog files) with `<div id="site-nav">` / `<div id="site-footer">` placeholders. Nav changes are now one-file edits. Removed duplicate mobile nav toggle code from main.js. |
