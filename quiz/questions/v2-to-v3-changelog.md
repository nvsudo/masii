# Masii Question Flow — v2 → v3 Changelog

> Quick reference for what changed, what was added, what was removed, and why.

---

## Questions Removed (6)

| Old # | Question | Reason |
|-------|----------|--------|
| Q11 | Sect / Denomination | Deferred to premium. Not enough data to tree properly. |
| Q24 | Family Values | Self-assessment unreliable. Everyone says "moderate." |
| Q28 | Family Involvement | Redundant. If you're on Masii, your family is involved. |
| Q47F | Financial Contribution (Women) | Covered by Q46 (financial planning, both genders). |
| Q48/Q48a | Gotra | Deferred to premium. |
| Q49 | Family Property | Covered by Q23 family status tiers. |
| — | Sensitive gate question | Replaced by per-question "Prefer not to say." |

## Questions Added (4 net new + 14 preference questions implemented)

| New # | Field | Question | Type | Why |
|-------|-------|----------|------|-----|
| 0.2a | `preferred_name` | What should I call you? | text | Personalization. All {name} references use this. Full name kept for records. |
| 18a | `company_name` | Which company? | text | Signal for matching. Shows career level without income. |
| 54 | `weekend_style` | What does your ideal weekend look like? | single | New WOW factor. Lifestyle alignment. |
| 55 | `communication_style` | How do you stay connected with people you care about? | single | New WOW factor. Relationship maintenance signal. |

**14 preference questions now implemented** (were in v2 spec but missing from code):
Q2-pref, Q3-pref, Q6-pref, Q6a-pref, Q17-pref, Q22-pref, Q27-pref, Q37a, Q37a-pref, Q38-pref, Q39a, Q42M-pref, Q42F-pref, Q51-disability, Q51a-disability

---

## Questions Rewritten (copy, options, or both)

| # | What Changed | Old | New |
|---|-------------|-----|-----|
| Q3 | Full rebuild | "Where is your family originally from? (State)" — India-only picker | "Where did you grow up?" — India/Outside India location tree. KEY CONTEXT NODE for downstream. |
| Q7/Q8 | Dual units | Feet only / kg only | "5'6" (168 cm)" / "70 kg (154 lbs)" |
| Q10 | Examples added | "Very religious / Religious / Moderate / Not religious" | Each level now has a one-line example per religion. E.g., Hindu Very religious: "Daily puja, regular fasting, temple every week" |
| Q10 (Muslim) | Label fix | "Liberal" as lowest option | "Not religious" — consistent with all other religions |
| Q13 | Copy | "Partner's religion preference?" | "Does your partner's religion matter to you?" |
| Q14 | Copy | "Partner's caste preference?" | "What about caste — does it matter?" |
| Q15 | Copy | "Partner's mother tongue preference?" | "Does language matter? Should they speak your mother tongue?" |
| Q17 | Copy | "What field?" | "What did you study?" |
| Q18 | Options expanded | 8 sectors | 15 sectors (Tech/IT, Finance/Banking, Consulting, Healthcare, Manufacturing, Media, Education, Govt, Professional, Business, Startup, Retail/Hospitality, Not working, Student, Other) |
| Q22 | Options expanded | Nuclear / Joint / Semi-joint | 4 options with definitions: Nuclear / Joint / Extended / Parents nearby |
| Q23 | Options aligned | Middle class / Upper middle / Affluent / Prefer not to say | 6 income-based tiers per spec |
| Q25/Q26 | Label fix | "Not alive" | "Late" |
| Q29 | Options rebuilt | Religion-specific diet lists | Universal: Strict veg / Veg / Eggetarian / Occasionally non-veg / Non-veg / Vegan / Jain / Halal only / Other |
| Q33 | Copy + options | "Partner's diet preference?" — 3 options | "How important is diet in your partner?" — 4 options |
| Q34 | Copy | "Partner's drinking — dealbreaker?" | "Is drinking a dealbreaker for you?" |
| Q35 | Copy | "Partner's smoking — dealbreaker?" | "Is smoking a dealbreaker?" |
| Q36 | Options aligned | Within 6 months / 1 year / 2-3 years / Exploring | Within 1 year / 1-2 years / 2-3 years / Exploring |
| Q39 | Option added | 4 options | 5 options: "Only abroad" added |
| Q41 | Copy | "Partner's height preference?" | "Any height preference?" |
| Q42M/43F | Reframed | "Out of 15 meals in a week..." | "How often are you willing to cook?" — natural frequency labels |
| Q42F | Reframed | "Do you know how to cook?" | "How's your cooking?" — Options: "I cook often / Sometimes / Learning / Not my thing" |
| Q43M | Reordered | "Mostly her" was first option | "Shared equally" is first. "Mostly her" → "She would handle most of it" (last). |
| Q44M | Reframed | "Prefer she focuses on home" | "I'd prefer a homemaker" — same meaning, less prescriptive |
| Q46F | Reframed | "Do you plan to continue working after marriage?" | "What does your career look like after marriage?" — Options rewritten |
| Q50 | Copy | "Partner's family financial status preference?" | "Does your partner's family financial status matter?" |
| Q52 | Options rewritten | Dashes in labels | Natural sentences without dashes |
| Q53 | Full rewrite | "When there's a disagreement, you tend to..." | "How do you handle disagreements?" — New ordinal-clean options |

---

## Structural Changes

| Change | Detail |
|--------|--------|
| **State-first architecture** | Q3 `raised_in_state` now drives: caste list order (Q12), language auto-suggest (Q4), income bracket context (Q19) |
| **Sensitive gate removed** | Every sensitive question gets "Prefer not to say" individually. Section intro replaces the gate. |
| **Personality is its own section** | Q52-55 are now Phase 11: Personality. 2 existing + 2 new questions. |
| **Preference questions grouped** | Each pref question immediately follows its parent (e.g., Q6 → Q6-pref → Q6a → Q6a-pref) |
| **Currency brackets added** | Q19/Q21: USD, GBP, CAD, AED, SGD brackets. Auto-detected from Q2 location. All labeled "/year". |
| **Section transitions rewritten** | All 10+ transitions rewritten in Masii's voice. |
| **Close message rewritten** | Warmer, more rewarding close after 75 questions. |
| **Intro reduced** | 3 screens → 1 screen. Form-focused only (service intro is on homepage). |
| **Error messages de-emojied** | All emojis removed per brand guidelines. |
| **Gender acknowledgment** | Q0.3 adds "More options coming soon — we see you" text below Male/Female. |
| **Name split** | Full name (Q0.2) for records + preferred name (Q0.2a) for personalization. Auto-fills first word. |
| **Caste include/exclude state-contextualized** | Q14/Q14a caste preference and exclude lists now driven by raised_in_state, matching Q12. |
| **Column layout directives** | All questions with 8+ options specify columns: 2/3/4 to reduce mobile scrolling. |
| **Height pref same-screen** | Q41 partner height shows min and max dropdowns side by side on one screen. |
| **Form colors** | Parked to Wave 3: align form to brand design system colors (cream, terracotta, earth). |
| **Multi-select ticks** | Parked to Wave 3: add visual tick indicators on multi-select answers. |
| **Question count** | v2: ~66 clicks → v3: ~75 clicks. +9 net (4 new + 14 pref implemented - 7 removed - 1 gate) |

---

## Implementation Waves (unchanged from audit)

**Wave 1: Spec Alignment** — Implement the 14 missing pref questions, remove 6 dead questions, rebuild Q3, switch to universal diet, align marriage timeline, add currency brackets.

**Wave 2: Copy & Options** — Rewrite all question copy, transitions, error messages. Expand sectors, castes, languages. Add company name. Add practice examples.

**Wave 3: Structural** — Auto-save per section. Back navigation within sections. Mid-form save point. Non-binary gender implementation. Form brand colors. Multi-select tick indicators.
