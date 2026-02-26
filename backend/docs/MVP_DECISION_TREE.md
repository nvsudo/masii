# Jodi MVP Onboarding - Decision Tree

## Visual Flow Map (77 Questions with Conditional Branching)

```
START: Jodi Onboarding
│
├─ A. IDENTITY & BASICS (9 questions)
│  ├─ Q1: Gender identity (Male/Female/Non-binary)
│  ├─ Q2: Looking for (Men/Women/Either)
│  ├─ Q3: Date of birth
│  ├─ Q4: Marital status
│  │   └─ IF marital_status ≠ "Never married"
│  │       └─ Q5: Do you have children? ⚠️ CONDITIONAL
│  ├─ Q6: Height
│  ├─ Q7: Body type
│  ├─ Q8: Complexion
│  └─ Q9: Disability status
│
├─ B. LOCATION & MOBILITY (8 questions)
│  ├─ Q10: Residency status (Indian citizen / NRI / OCI / Foreign national)
│  │   ├─ IF residency_type ≠ "Indian citizen (in India)"
│  │   │   ├─ Q11: Country you live in ⚠️ CONDITIONAL (NRI-only)
│  │   │   └─ Q17: Where do you plan to settle long-term? ⚠️ CONDITIONAL (NRI-only)
│  │   └─ IF residency_type = "Indian citizen (in India)"
│  │       └─ Q12: State (India) ⚠️ CONDITIONAL (India-only)
│  ├─ Q13: City (current)
│  ├─ Q14: Hometown state
│  ├─ Q15: Willing to relocate?
│  └─ Q16: Partner location preference
│
├─ C. RELIGION, CASTE & CULTURE (10 questions)
│  ├─ Q18: Your religion
│  │   └─ BRANCHES BY RELIGION:
│  │       ├─ IF Hindu → Q21: Sect (Shaivite/Vaishnavite/Arya Samaj/etc.)
│  │       ├─ IF Muslim → Q21: Sect (Sunni/Shia/Sufi/Ahmadiyya) ⚠️ MUSLIM BRANCH
│  │       │   └─ [Food: Halal only appears in diet Q45]
│  │       ├─ IF Christian → Q21: Sect (Catholic/Protestant/Orthodox/Evangelical)
│  │       ├─ IF Sikh → Q21: Sect (Amritdhari/Keshdhari/Sehajdhari)
│  │       └─ IF Jain/Buddhist/Hindu → Caste questions appear
│  ├─ Q19: How religious are you?
│  ├─ Q20: Partner's religion preference
│  ├─ Q21: Sect/denomination ⚠️ CONDITIONAL (dropdown changes by religion)
│  │   └─ IF religion = Hindu/Jain/Sikh/Buddhist
│  │       ├─ Q22: Caste/community ⚠️ CONDITIONAL (Hindu/Jain/Sikh only)
│  │       │   └─ IF caste_community answered
│  │       │       └─ Q23: Sub-caste/gotra ⚠️ CONDITIONAL (nested)
│  │       ├─ Q24: Caste importance
│  │       └─ Q27: Manglik status ⚠️ CONDITIONAL (Hindu/Jain only)
│  ├─ Q25: Mother tongue
│  └─ Q26: Languages spoken
│
├─ D. EDUCATION & CAREER (5 questions)
│  ├─ Q28: Highest education
│  ├─ Q29: Institute tier (IIT/IIM vs State vs Abroad)
│  ├─ Q30: Employment status
│  ├─ Q31: Industry/field
│  └─ Q32: Career priority
│
├─ E. FINANCIAL PROFILE 🔒 (4 questions - PRIVATE)
│  ├─ Q33: Annual income (range)
│  │   └─ IF residency_type ≠ "Indian citizen"
│  │       └─ Q34: Income currency ⚠️ CONDITIONAL (NRI-only)
│  ├─ Q35: Net worth range
│  ├─ Q36: Own property?
│  └─ Q37: Financial dependents?
│
├─ F. FAMILY BACKGROUND (7 questions)
│  ├─ Q38: Family type (Nuclear/Joint/Extended joint)
│  ├─ Q39: Family financial status
│  ├─ Q40: Father's occupation
│  ├─ Q41: Family values (Traditional/Moderate/Liberal)
│  ├─ Q42: Live with parents post-marriage?
│  ├─ Q43: Family involvement in search
│  └─ Q44: Siblings
│
├─ G. LIFESTYLE & HABITS (11 questions)
│  ├─ Q45: Your diet
│  ├─ Q46: Partner's diet preference
│  ├─ Q47: Smoking
│  ├─ Q48: Smoking partner OK?
│  ├─ Q49: Drinking
│  ├─ Q50: Drinking partner OK?
│  ├─ Q51: Fitness frequency
│  ├─ Q52: Social style (Outgoing/Homebody)
│  ├─ Q53: Weekend style
│  ├─ Q54: Pet ownership
│  └─ Q55: Sleep schedule
│
├─ H. PARTNER PREFERENCES (9 questions)
│  ├─ Q56: Partner age range
│  ├─ Q57: Partner height
│  ├─ Q58: Partner complexion
│  ├─ Q59: Partner education (min)
│  ├─ Q60: Partner income expectation
│  ├─ Q61: Partner marital status OK?
│  ├─ Q62: Partner having children OK?
│  ├─ Q63: Partner with disability OK?
│  └─ Q64: Want a working partner?
│
├─ I. VALUES & RELATIONSHIP STYLE (8 questions)
│  ├─ Q65: Relationship intent (timeline)
│  ├─ Q66: Want children?
│  │   └─ IF children_intent ≠ "Definitely not"
│  │       └─ Q67: Children timeline ⚠️ CONDITIONAL
│  ├─ Q68: Gender roles / household responsibilities
│  ├─ Q69: Financial management in marriage
│  ├─ Q70: Political leaning
│  ├─ Q71: Kundli/astrology importance
│  └─ Q72: Open to inter-faith/inter-caste?
│
└─ J. HARD DEALBREAKER CHECKBOXES (5 questions)
   ├─ Q73: OK with divorced partner?
   ├─ Q74: OK with widowed partner?
   ├─ Q75: OK with partner who has children?
   ├─ Q76: OK with NRI partner?
   └─ Q77: Maximum age gap acceptable
```

---

## Key Conditional Branches

### 1. **Marital Status Branch** (Q4 → Q5)
```
Q4: Marital status
├─ Never married → Skip Q5 (no children)
└─ Divorced/Widowed/Separated/Annulled → Q5: Do you have children?
```

### 2. **Residency Branch** (Q10 → Q11, Q12, Q17, Q34)
```
Q10: Residency status
├─ Indian citizen (in India)
│  └─ Q12: State (India)
└─ NRI / OCI / Foreign national
   ├─ Q11: Country you live in
   ├─ Q17: Where do you plan to settle long-term?
   └─ Q34: Income currency (in Financial section)
```

### 3. **Religion Branch** (Q18 → Q21 sect options)
```
Q18: Your religion
├─ Hindu → Q21: Sect (Shaivite/Vaishnavite/Arya Samaj/etc.)
│  ├─ Q22: Caste (Brahmin/Kshatriya/SC/ST/OBC/etc.)
│  │  └─ Q23: Sub-caste/gotra (if Q22 answered)
│  ├─ Q24: Caste importance
│  └─ Q27: Manglik status
│
├─ Muslim → Q21: Sect (Sunni/Shia/Sufi/Ahmadiyya)
│  └─ [No caste questions]
│  └─ [Q45 Diet: Halal only option appears]
│
├─ Christian → Q21: Sect (Catholic/Protestant/Orthodox/Evangelical)
│  └─ [No caste questions]
│
├─ Sikh → Q21: Sect (Amritdhari/Keshdhari/Sehajdhari)
│  ├─ Q22: Caste (Jat/Khatri/Ramgarhia/etc.)
│  │  └─ Q23: Sub-caste (if Q22 answered)
│  └─ Q24: Caste importance
│
├─ Jain → Q21: Sect (Digambar/Shwetambar/etc.)
│  ├─ Q22: Caste/community
│  │  └─ Q23: Sub-caste (if Q22 answered)
│  ├─ Q24: Caste importance
│  ├─ Q27: Manglik status
│  └─ [Q45 Diet: Jain food option (no root veg, no onion/garlic)]
│
├─ Buddhist → Q22: Caste (if applicable)
│  └─ Q23: Sub-caste (if Q22 answered)
│
└─ No religion/Atheist/Spiritual/Jewish/Parsi/Other
   └─ [Skip caste questions Q22-Q24]
   └─ [Skip Q27 Manglik]
```

### 4. **Caste Branch** (Q22 → Q23)
```
Q22: Caste/community (shown only for Hindu/Jain/Sikh/Buddhist)
├─ Answered → Q23: Sub-caste/gotra (optional)
└─ "Prefer not to say" → Skip Q23
```

### 5. **Children Intent Branch** (Q66 → Q67)
```
Q66: Want children?
├─ Definitely not → Skip Q67
└─ Yes/Probably/Open → Q67: Children timeline
```

---

## Summary: Total Questions by User Path

| User Profile | Base Questions | Conditional Questions | **Total** |
|-------------|----------------|---------------------|----------|
| **Standard Indian (Hindu/Jain/Sikh, never married, in India)** | 69 | +6 (State, Caste, Sub-caste, Manglik, Children timeline) | **75** |
| **NRI Hindu (never married, living abroad)** | 69 | +6 (Country, Settling plan, Currency, Caste, Sub-caste, Manglik) | **75** |
| **Muslim (never married, in India)** | 69 | +2 (State, Children timeline) | **71** |
| **Divorced Hindu (in India, has children)** | 69 | +7 (Children existing, State, Caste, Sub-caste, Manglik, Children timeline) | **76** |
| **Christian NRI (never married)** | 69 | +4 (Country, Settling plan, Currency, Children timeline) | **73** |
| **Atheist/No religion (never married, in India)** | 69 | +2 (State, Children timeline) | **71** |

**Minimum path:** 71 questions (Muslim/Atheist, never married, no children wanted)  
**Maximum path:** 77 questions (Divorced Hindu NRI with children, wants more kids)

---

## Hard Filters (Instant Match Elimination)

These questions use **binary yes/no logic** to eliminate incompatible matches:

1. Gender identity + Looking for gender (Q1, Q2)
2. Age (Q3) → filtered by partner age range (Q56)
3. Marital status (Q4) ↔ Partner marital status OK (Q61)
4. Children existing (Q5) ↔ Partner children OK (Q62, Q75)
5. Disability (Q9) ↔ Partner disability OK (Q63)
6. Residency type (Q10) ↔ NRI OK (Q76)
7. Religion (Q18) ↔ Partner religion pref (Q20)
8. Caste (Q22, if shown) ↔ Caste importance (Q24)
9. Willing to relocate (Q15) ↔ Partner location pref (Q16)
10. Diet (Q45) ↔ Partner diet pref (Q46)
11. Smoking (Q47) ↔ Smoking partner OK (Q48)
12. Drinking (Q49) ↔ Drinking partner OK (Q50)
13. Children intent (Q66)
14. Relationship timeline (Q65)
15. Age gap max (Q77)

**Two-way filters:** Both users must pass each other's filters.

---

## Soft Filters & Algo Weights

These influence **match score** but don't eliminate:

- Height (Q6, Q7) ↔ Partner height pref (Q57)
- Complexion (Q8) ↔ Partner complexion pref (Q58)
- State/City (Q12, Q13)
- Education (Q28, Q29) ↔ Partner education min (Q59)
- Income (Q33) ↔ Partner income expectation (Q60)
- Family type (Q38), values (Q41)
- Lifestyle habits (Q51-Q55)
- Political leaning (Q70)
- Astrology belief (Q71)

---

## Implementation Notes

### Phase 1: Collect Hard Filters First
Tier 1 = Questions 1-27 (Identity + Location + Religion/Culture)
- Get dealbreakers early
- Reduce drop-off on long forms
- Enable early match preview ("X compatible profiles exist")

### Phase 2: Lifestyle + Preferences
Tier 2 = Questions 28-64 (Education, Career, Family, Lifestyle, Prefs)
- Now that they're invested, go deeper
- Private financial section (🔒 reassure: "Never shown to matches")

### Phase 3: Values + Dealbreakers
Tier 3 = Questions 65-77 (Values, Relationship style, Final dealbreakers)
- Philosophical alignment
- Binary yes/no dealbreaker checkboxes at end

### Conditional Logic Implementation
```python
# Example: Marital status → Children question
if user_answer['marital_status'] != 'Never married':
    show_question('children_existing')

# Example: Religion → Caste questions
if user_answer['religion'] in ['Hindu', 'Jain', 'Sikh', 'Buddhist']:
    show_question('caste_community')
    if user_answer['caste_community'] is not None:
        show_question('sub_caste')  # Optional follow-up
    show_question('caste_importance')
    if user_answer['religion'] in ['Hindu', 'Jain']:
        show_question('manglik_status')

# Example: NRI → Geography questions
if user_answer['residency_type'] != 'Indian citizen (in India)':
    show_question('country_current')
    show_question('settling_country')
    show_question('income_currency')  # Later in Financial section
else:
    show_question('state_india')
```

---

## UX Considerations

1. **Progress bar:** "32 of ~73 questions" (dynamic based on path)
2. **Save & resume:** Store partial answers, let users come back
3. **Skip logic transparency:** "Based on your answer, we'll ask/skip X"
4. **Privacy callouts:** 🔒 icon for private financial questions
5. **Cultural sensitivity:** "Prefer not to say" option for complexion, caste
6. **Mobile-first:** Dropdowns, sliders, multi-select optimized for Telegram

---

*Decision tree created: 2026-02-20*  
*Based on: "Updated MVP questions" tab in Jodi schema sheet*
