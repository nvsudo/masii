# IMP-001 through IMP-006 — Implementation Plan

**Goal:** Implement all 6 improvements recursively

---

## Changes Required

### IMP-001: DOB Two-Step Button Selection

**Current:** Q3 = text input (DD/MM/YYYY)

**New:** 
- Q3a: Birth year (button grid 1980-2006)
- Q3b: Birth month (button grid Jan-Dec)
- Skip day (assume 15th for age calculation)

**Files:**
- `config.py`: Split Q3 into two questions with button grids
- `onboarding_handler.py`: Handle two-step flow
- `db_adapter.py`: Store birth_year, birth_month, calculate DOB

---

### IMP-002: Body Type & Complexion Softer + Paired Preferences

**Current:** 
- Q7: "Body type?" [Slim/Average/Athletic/Curvy/Heavy]
- Q8: "Skin tone?" [Fair/Wheatish/Dusky/Dark]

**New:**
- Q7: "How would you describe your fitness level?" [Not active / Occasionally active / Regularly active / Very athletic]
- Q7a: "What fitness level would you prefer in a partner?" [same options + No preference]
- Q7b: "Any fitness dealbreakers?" [optional multi-select or skip]
- Q8: Softer complexion framing (emoji-based or indirect)
- Q8a: Partner complexion preference
- Q8b: Dealbreakers

**Files:**
- `config.py`: Update Q7-Q8 text + options, add Q7a/7b, Q8a/8b
- Total questions increases: 77 → 81 (add 4 questions)

---

### IMP-003: NRI Location Hierarchical Drill-Down

**Current:** Q11 = single country dropdown (messy)

**New:**
- Q11a: "Where are you based?" [USA / UK / EU / AU / Singapore / UAE / Others]
- Q11b: IF EU → [Germany / France / Netherlands / Spain / Italy / Switzerland / Belgium / Others]
- Q11c: IF Others → [Canada / NZ / Middle East / South Africa / Type your country]

**Files:**
- `config.py`: Split Q11 into conditional multi-step
- `conditional_logic.py`: Add hierarchical logic

---

### IMP-004: Partner Religion Expectation Setting

**Current:** Q20 = "Partner's religion:" (abrupt after Q19 your religion)

**New:** Add transition message before Q20

**Files:**
- `config.py`: Add `pre_question_message` field to Q20
- `onboarding_handler.py`: Send message before Q20

---

### IMP-005: Sect/Caste Cultural Terminology

**Current:** 
- Hindu sects: Shaivite, Vaishnavite, Arya Samaj, Smartha
- Hindu castes: (too English, too direct)

**New:**
- Research Shaadi.com / Jeevansathi terminology
- Update to culturally authentic terms
- Consider bilingual: "Vaishnava (वैष्णव)"

**Files:**
- `conditional_logic.py`: Update `get_conditional_options()` for Q21, Q22

---

### IMP-006: Conversational Warmth & Empathy

**Changes:**
1. Add acknowledgment responses after sensitive questions (Q5, Q9, Q33-Q37, Q72)
2. Add progress milestones (25%, 50%, 75%)
3. Add empathy before difficult sections (financial, dealbreakers)
4. Add humor/lightness (Q53 weekends, Q54 pets)
5. Warmer section transitions (already done in IMP-007, enhance further)

**Files:**
- `config.py`: Add `response_template` to questions
- `onboarding_handler.py`: Send acknowledgments after answers, check progress milestones

---

## Implementation Order

1. ✅ **IMP-001** (DOB buttons) — Simplest, quick win
2. ✅ **IMP-004** (Religion framing) — Just add transition message
3. ✅ **IMP-005** (Cultural terminology) — Update option labels
4. ✅ **IMP-003** (NRI location) — Medium complexity (conditional logic)
5. ✅ **IMP-002** (Body/Complexion paired prefs) — Most complex (adds 4 questions)
6. ✅ **IMP-006** (Warmth) — Add throughout

---

## Question Number Changes

**Before:** 77 questions

**After:** 
- IMP-002 adds 4 questions (Q7a, Q7b, Q8a, Q8b)
- IMP-003 might add 1-2 questions (hierarchical drill-down)
- **New total:** ~82-83 questions

**Note:** All question numbers after Q8 shift by +4

---

## Testing Strategy

After each IMP:
1. Deploy to staging
2. Test specific user path (Hindu, never married, India)
3. Verify no loops, correct skip logic
4. Check tone/warmth in messages

---

**Starting implementation now...**
