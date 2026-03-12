# Question Matching Protocol — v3 Update

> Addendum to v2 matching protocol. Covers new questions, rescored questions,
> and changed gate logic. All other v2 scoring rules remain unchanged.
>
> Source of truth for question definitions: masii-questions.yaml
> This document covers SCORING RULES ONLY.

---

## Summary of Changes

| Change | Detail |
|--------|--------|
| 2 new WOW questions | Weekend style (Q54), Communication style (Q55) |
| 1 rescored question | Conflict style (Q53) — ordinal → matrix |
| Diet gate updated | 4 options (was 3), universal diet values (was religion-specific) |
| Income matching | Cross-currency tier system enables India ↔ NRI matching |
| Cooking questions | Reframed options — new value strings need mapping |
| Career/household | Reframed options — new value strings need mapping |

---

## NEW: Q54 — Weekend Style [WOW FACTOR]

**Question:** What does your ideal weekend look like?
**Options:** `Out and about` / `Mix` / `Quiet at home` / `Depends`

**Scoring (WOW factor):**
- Same style = 1.5
- One step apart = 1.0
- "Depends" = 1.0 with anything (flexible person, no penalty)
- Two steps apart = 0.5
- "Out and about" + "Quiet at home" = 0.0

**Ordinal scale:** Out and about → Mix → Quiet at home. "Depends" is a wildcard.

**Why WOW:** Two homebodies finding each other is a genuine lifestyle bonus. Two social people who want to be out every weekend — same. This is the daily-life-compatibility signal that religion and caste can't capture.

---

## NEW: Q55 — Communication Style [WOW FACTOR]

**Question:** How do you stay connected with people you care about?
**Options:** `Daily check-ins` / `Regular texts` / `Quality over quantity` / `Show up when it matters`

**Scoring (WOW factor):**
- Same style = 1.5
- One step apart = 1.0
- Two steps apart = 0.5
- Extremes ("Daily check-ins" + "Show up when it matters") = 0.0

**Ordinal scale:** Daily check-ins → Regular texts → Quality over quantity → Show up when it matters.

**Why WOW:** Communication frequency mismatch is one of the top relationship complaints. A person who needs daily check-ins paired with someone who goes quiet for days — that's a real problem, not a preference.

---

## RESCORED: Q53 — Conflict Style [WOW FACTOR, NOW MATRIX]

**Question:** How do you handle disagreements?
**Options:** `Address immediately` / `Give it time` / `Let it go` / `Need space`

**Old scoring (v2):** Ordinal proximity. Same = 1.5, one step = 1.0, two+ steps = 0.5.

**Problem with ordinal:** "Get heated, then cool down" (old) and "Avoid conflict" (old) were treated as adjacent on a spectrum. They're not. Someone who needs to talk immediately and someone who avoids conflict entirely are deeply incompatible — but someone who needs time and someone who needs space are very compatible (both need processing time).

**New scoring (v3): Compatibility matrix.**

|  | Address immediately | Give it time | Let it go | Need space |
|--|:--:|:--:|:--:|:--:|
| **Address immediately** | **1.5** | 1.0 | 0.5 | 0.5 |
| **Give it time** | 1.0 | **1.5** | 1.0 | 1.0 |
| **Let it go** | 0.5 | 1.0 | **1.5** | 1.0 |
| **Need space** | 0.5 | 1.0 | 1.0 | **1.5** |

**Key insight:** "Give it time" and "Need space" are highly compatible (both need processing before discussion — score 1.0). "Let it go" and "Need space" are also compatible (neither escalates — score 1.0). "Address immediately" is only truly compatible with itself and "Give it time" (both want resolution, just different timing).

**Implementation:** Store the matrix as a 2D lookup. Score = `CONFLICT_MATRIX[user_a_style][user_b_style]`.

---

## UPDATED: Q33 — Diet Preference Gate

**Old options (v2 code):** `Same as mine` / `Vegetarian or above` / `Doesn't matter`
**New options (v3):** `Same as mine` / `Any vegetarian (no non-veg)` / `Vegetarian only` / `Doesn't matter`

**Gate logic (updated):**

| Preference | Allows | Eliminates |
|-----------|--------|------------|
| Same as mine | Must match candidate's Q29 exactly | Everything else |
| Any vegetarian | Strict veg, Veg, Eggetarian, Vegan, Jain | Non-veg, Occasionally non-veg, Halal only |
| Vegetarian only | Strict veg, Veg, Vegan, Jain | Everything else (including Eggetarian) |
| Doesn't matter | All | None |

**Why the split:** "Any vegetarian" allows eggetarian (eggs are fine in many vegetarian households). "Vegetarian only" does not. This distinction matters — a Jain family that says "vegetarian only" means no eggs. A Punjabi family that says "any vegetarian" might be fine with eggs.

**CRITICAL: Universal diet values.** The old code used religion-specific strings (e.g., "Jain vegetarian" vs "Vegetarian" vs "Halal only"). The v3 diet question uses universal values. All comparisons use the same string set. No cross-religion normalization needed.

---

## UPDATED: Income Matching — Cross-Currency Tiers

**Problem:** A user in India earning ₹20-35 lakh/year and a user in the US earning $75-100K/year are roughly equivalent in purchasing power and lifestyle. But the old system couldn't compare INR and USD brackets.

**Solution:** Every income bracket has a `tier` number (1-9). The tier is the unit of comparison, not the currency amount.

| Tier | India (INR) | USA (USD) | UAE (AED) | UK (GBP) |
|------|------------|-----------|-----------|----------|
| 1 | Under ₹5L | Under $30K | Under AED 100K | Under £25K |
| 2 | ₹5-10L | $30-50K | AED 100-200K | £25-40K |
| 3 | ₹10-20L | $50-75K | AED 200-350K | £40-60K |
| 4 | ₹20-35L | $75-100K | AED 350-500K | £60-80K |
| 5 | ₹35-50L | $100-150K | AED 500-750K | £80-120K |
| 7 | ₹75L-1Cr | $150-250K | AED 750K-1M | £120-200K |
| 9 | Above ₹2Cr | Above $250K | Above AED 1M | Above £200K |

**Q21 gate logic:** "Minimum income" preference compares tiers. Candidate's tier ≥ preference tier = pass (1.0). Candidate's tier < preference tier = fail (0.0). "Doesn't matter" = 1.0 always. "Prefer not to say" = skip, no penalty.

**Note:** India has tiers 6 and 8 (₹50-75L and ₹1-2Cr) that other currencies skip. This is intentional — India's income distribution has more granularity at the top. Cross-currency comparison still works because the tier numbers align at the key thresholds.

---

## UPDATED: Cooking Questions — Value String Mapping

The cooking questions were reframed from "15 meals a week" to natural frequency. The scoring logic is the same, but the value strings changed.

**Old → New value mapping:**

| Old value (v2) | New value (v3) | Ordinal |
|---------------|---------------|---------|
| 0 | Rarely or never | 1 |
| 1-3 | Occasionally | 2 |
| 4-7 | A few times a week | 3 |
| 8-10 | (merged into above) | 3 |
| More than 10 | Most days | 4 |

**Scoring unchanged:** Cross-match her cooking_contribution against his pref_partner_cooking_freq (and vice versa). Meets or exceeds = 1.0. Exceeds by 2+ levels = 1.5 (WOW). Below = 0.0.

---

## UPDATED: Career/Household — Value String Mapping

**Q42F (do_you_cook) — Women:**

| Old value | New value |
|-----------|-----------|
| Yes, I cook regularly | I cook often |
| Yes, but I don't cook often | Sometimes |
| No, but I'm willing to learn | Learning |
| No | Not my thing |

**Q43M (household_contribution) — Men:**

| Old value | New value |
|-----------|-----------|
| Mostly her | Mostly her (now last option, relabeled "She would handle most of it") |
| Shared equally | Shared equally (now first option) |
| Mostly outsourced (cook/maid) | Mostly outsourced |
| Flexible — whatever works | Flexible |

**Q44M (partner_working) — Men:**

| Old value | New value |
|-----------|-----------|
| Yes, she should have a career | Career important |
| Her choice | Her choice |
| Prefer she focuses on home | Prefer homemaker |

**Q46F (career_after_marriage) — Women:**

| Old value | New value |
|-----------|-----------|
| Yes, definitely | Full steam ahead |
| Yes, but open to a break for kids | Open to a pause |
| Undecided | Undecided |
| No, prefer homemaking | Prefer homemaking |

**Cross-matching rules unchanged.** The semantic mapping is 1:1. Just update the string comparisons.

---

## SCORING MODEL — Updated Totals

**With v3 additions:**
- Hard gates: 23 (eliminates pair before scoring)
- Scored questions: ~55-60 (depending on gender and skip logic)
- WOW factors: 7 (was 5, added weekend_style and communication_style)

**Max possible score with WOW:** ~62-65 points
- ~55 scored questions at 1.0 each = 55
- 7 WOW questions at 1.5 each = 10.5
- Total max ≈ 65.5

**Score tiers (unchanged):**
- 75%+ = strong match, free introduction
- 60-74% = decent match, free introduction
- Below 60% = not shown in free tier

**What 75% means now:** With max ~65, threshold is ~49 points. A pair needs to match on most of the important stuff (religion, caste, location, age, diet, lifestyle, family) AND have some personality alignment to clear easily. The 2 new WOW factors make personality alignment more rewarding without raising the bar on the fundamentals.

---

## Data Migration Notes

If you have v2 data in the database, these fields need value remapping:

| Field | Old values | New values | Action |
|-------|-----------|-----------|--------|
| diet | Religion-specific strings | Universal strings | Migration script needed |
| cooking_contribution | "0", "1-3", "4-7", "8-10", "More than 10" | "Rarely or never", "Occasionally", "A few times a week", "Most days" | Migration script needed |
| do_you_cook | "Yes, I cook regularly" etc. | "I cook often" etc. | Migration script needed |
| household_contribution | "Mostly her" etc. | "Mostly her" etc. (minor changes) | Migration script needed |
| partner_working | "Prefer she focuses on home" | "Prefer homemaker" | Migration script needed |
| career_after_marriage | "Yes, definitely" etc. | "Full steam ahead" etc. | Migration script needed |
| conflict_style | "Talk it out immediately" etc. | "Address immediately" etc. | Migration script needed |
| marriage_timeline | "Within 6 months" / "In the next 1 year" | "Within 1 year" / "1-2 years" | Migration script needed |
| family_status | "Middle class" etc. | "tier_1" through "tier_5" | Migration script needed |
| annual_income | "Under ₹5 lakh" etc. | "INR_1" etc. (tiered) | Migration script needed |

**New fields (no migration, just add columns):**
`preferred_name`, `company_name`, `weekend_style`, `communication_style`, `disability`, `raised_in_state`, `pref_current_location`, `pref_raised_in`, `pref_marital_status`, `pref_children_existing`, `pref_education_field`, `pref_family_type`, `pref_siblings`, `pref_children_timeline`, `pref_living_arrangement`, `pref_partner_cooking_freq`, `pref_partner_can_cook`, `pref_disability`, `relocation_countries`
