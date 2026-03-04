# Question Matching Protocol — v2

> The matching spec for Masii's FREE introductions.
> This is the hook to get supply going. Nuanced/warm matching is premium.
>
> **Scoring rules:**
> - Per question: 1.0 (match), 0.8, 0.5, 0.25, 0.0 (no match)
> - WOW factor: 1.5 or 2.0 (exceptionally good alignment)
> - Hard gates: pair eliminated, never shown, regardless of overall score
> - Soft 0.0: still considered if overall score is high
> - Most questions: ask user's data, then ask explicit partner preference, then binary match
> - No range assumptions, no weighted dimensions, no data science guessing
>
> **New questions marked with [NEW]**
> **Skipped questions marked with [SKIP]**

---

# PART 1: HARD GATES

Pair eliminated. Never shown. No matter how high the overall score.

---

## Q0.3 — Gender

**Question:** Are you male or female?
**Options:** `Male` / `Female`

**Gate logic:** Must be opposite gender. Male only matches Female, Female only matches Male.

---

## Q13 — Partner Religion Preference

**Question:** Partner's religion preference?
**Options:** `Same religion only` / `Open to all` / `Open, but not...`

**Gate logic:** If "Same religion only" — candidate must share your exact religion (Q9). If "Open, but not..." — triggers the exclude list (Q13a). "Open to all" passes everyone. Checked bidirectionally.

---

## Q13a — Religion Exclude List

**Question:** Which religions would you NOT want to match with?
**Options (multi-select):** `Hindu` / `Muslim` / `Sikh` / `Jain` / `Christian` / `Buddhist` / `Parsi` / `No religion`
**Only shown if:** Q13 = "Open, but not..."

**Gate logic:** If the candidate's religion (Q9) appears in your exclude list, pair eliminated.

---

## Q14 — Partner Caste Preference

**Question:** Partner's caste preference?
**Options:** `Same caste only` / `Same community, any caste` / `Open to all` / `Open, but not...`
**Only shown if:** religion has caste system

**Gate logic:** If "Same caste only" or caste_importance (Q12a) = "Must be same caste" — candidate's caste must exactly match yours. If "Open, but not..." — triggers the exclude list (Q14a). "Open to all" passes everyone.

---

## Q14a — Caste Exclude List

**Question:** Which castes would you NOT want to match with?
**Options (multi-select):** Caste list varies by religion + state (see Q12 for lists)
**Only shown if:** Q14 = "Open, but not..."

**Gate logic:** If the candidate's caste (Q12) appears in your exclude list, pair eliminated.

---

## Q40 — Partner Age Range

**Question:** What age range are you looking for in a partner?
**Options:** Step 1: Min age (18-50) / Step 2: Max age (min-55)

**Gate logic:** Candidate's age (from Q1) must fall within the stated range. In range = pass. Outside range = eliminated. No buffer, no guessing.

---

## Q33 — Partner Diet Preference [UPDATED]

**Question:** Partner's diet preference?
**Options:** `Same as mine` / `Any but not non-veg` / `Veg` / `Doesn't matter`

**Gate logic:** Compare candidate's diet (Q29) against this preference. "Same as mine" = must match exactly. "Any but not non-veg" = eliminates non-veg and occasionally non-veg. "Veg" = must be vegetarian or stricter. "Doesn't matter" = passes everyone.

---

## Q34 — Partner Drinking Preference

**Question:** Partner's drinking — dealbreaker?
**Options:** `Must not drink` / `Social drinking OK` / `Doesn't matter`

**Gate logic:** "Must not drink" + candidate drinks "Regularly" = eliminated. Social drinkers pass through "Must not drink." "Doesn't matter" passes everyone.

---

## Q35 — Partner Smoking Preference

**Question:** Partner's smoking — dealbreaker?
**Options:** `Must not smoke` / `Social smoking OK` / `Doesn't matter`

**Gate logic:** "Must not smoke" + candidate smokes "Regularly" = eliminated. Same logic as drinking.

---

## Q37 — Children Intent

**Question:** Do you want children?
**Options:** `Yes` / `Maybe / Open to it` / `No`

**Gate logic:** "Yes" vs "No" = eliminated. "Maybe / Open to it" is compatible with both. Checked bidirectionally.

---

## Q36 — Marriage Timeline [UPDATED]

**Question:** How soon are you looking to get married?
**Options:** `Within 1 year` / `1-2 years` / `2-3 years` / `Just exploring`

**Gate logic:** Must be within 1 step. "Within 1 year" + "2-3 years" = eliminated. "Within 1 year" + "Just exploring" = eliminated. Adjacent steps pass.

---

## Q6 — Marital Status [NOW A HARD GATE]

**Question:** What's your current marital status?
**Options:** `Never married` / `Divorced` / `Widowed` / `Awaiting divorce`

**Flow:** If "Never married" → skip Q6a (children existing). After Q6, immediately ask Q6-pref and Q6a-pref.

---

## Q6-pref — Partner Marital Status Preference [NEW]

**Question:** What marital status are you open to in a partner?
**Options (multi-select):** `Never married` / `Divorced` / `Widowed` / `Awaiting divorce` / `Any`

**Gate logic:** If candidate's marital status (Q6) is not in your accepted list, pair eliminated. "Any" passes everyone.

---

## Q6a — Children Existing

**Question:** Do you have children?
**Options:** `No` / `Yes, they live with me` / `Yes, they don't live with me`
**Only shown if:** Q6 ≠ "Never married"

---

## Q6a-pref — Partner's Existing Children Preference [NEW]

**Question:** Are you open to a partner who has children?
**Options:** `Yes` / `Only if they don't live with them` / `No`
**Only shown if:** makes sense to ask (i.e., user is open to divorced/widowed partners)

**Gate logic:** "No" + candidate has children = eliminated. "Only if they don't live with them" + candidate's kids live with them = eliminated. "Yes" passes everyone.

---

## Q3 — Where Did You Grow Up [REFRAMED]

**Question:** Where did you grow up?
**Options:** Step 1: `India` / `Outside India` → Step 2: If India: State → City. If outside: Country → City

This replaces the old "hometown" question. It captures where they were raised, not just family roots.

---

## Q3-pref — Partner Raised-In Preference [NEW]

**Question:** Where should your partner have been raised?
**Options:**
- If user is outside India: `Same country as me` / `Raised abroad (any country)` / `Raised in India is fine too` / `Doesn't matter`
- If user is in India: `Same state` / `Nearby states` / `Any state in India` / `Abroad is fine too` / `Doesn't matter`

**Gate logic:** Hard gate. If user says "Same country as me" and candidate grew up in a different country = eliminated. If user says "Same state" and candidate grew up in different state = eliminated. "Doesn't matter" passes everyone. An American Indian who doesn't want someone raised in India — that's respected, pair killed.

---

## Q2-pref — Partner Current Location Preference [NEW]

**Question:** Where should your partner currently live?
**Options:** `Same city as me` / `Same state as me` / `Same country as me` / `Anywhere` / `Specific countries...` (multi-select dropdown of top countries)

**Gate logic:** Hard gate. Candidate's current location (Q2) must match the stated preference. "Anywhere" passes everyone. "Specific countries" = candidate must be in one of the selected countries.

---

## Q39 — Relocation Willingness [UPDATED]

**Question:** Would you relocate for the right match?
**Options:** `Yes, anywhere` / `Yes, within India` / `Yes, within my state/country` / `Only abroad` / `No, I'm settled where I am`

**Follow-up if "Only abroad" or "Yes, anywhere":** Which countries? (multi-select: top countries list)

**Gate logic:** Only triggers elimination when BOTH people say "No, I'm settled" AND they're in different countries. If at least one person is willing to relocate, pair passes. Same-country pairs always pass.

---

## Q15 — Partner Mother Tongue Preference [NOW A HARD GATE]

**Question:** Partner's mother tongue preference?
**Options:** `Same language only` / `Same or Hindi` / `Doesn't matter`

**Gate logic:** Hard gate. "Same language only" + candidate's mother tongue (Q4) doesn't match = eliminated. "Same or Hindi" + candidate speaks neither your language nor Hindi = eliminated. "Doesn't matter" passes everyone.

---

## Q41 + Q7 — Height Preference [NOW A HARD GATE]

Q7 collects their height. Q41 collects their partner height preference (min/max range or "Doesn't matter").

**Gate logic:** Hard gate. If candidate's height (Q7) falls outside the stated min/max range = eliminated. "Doesn't matter" passes everyone. No buffer.

---

## Q47a — Manglik Preference

**Question:** Is Manglik status important in your partner?
**Options:** `Must match` / `Prefer, but flexible` / `Doesn't matter`
**Only shown if:** Q47 ≠ "Not applicable"

**Gate logic:** "Must match" = candidate's manglik status (Q47) must be same as yours. "Prefer, but flexible" and "Doesn't matter" pass everyone.

---

## Q51a — Medical Conditions Preference [UPDATED — SPLIT INTO TWO]

Old question combined medical conditions and disability. Split them.

**Q51 — Medical Conditions**
**Question:** Do you have any known medical conditions? (e.g. diabetes, asthma, thyroid)
**Options:** `No` / `Yes` / `Prefer not to say`

**Q51-disability — Disability [NEW]**
**Question:** Do you have a disability?
**Options:** `No` / `Yes` / `Prefer not to say`

**Q51a — Partner Medical Conditions Preference**
**Question:** Are you open to a partner with a medical condition?
**Options:** `Yes` / `Depends on the condition` / `No`

**Q51a-disability — Partner Disability Preference [NEW]**
**Question:** Are you open to a partner with a disability?
**Options:** `Yes` / `Depends` / `No`

**Gate logic:** "No" + candidate has condition/disability = eliminated. Separate gates for medical and disability.

---

# PART 2: SCORED QUESTIONS

These are soft scores. 0.0 is still considered if overall score is high. Total score = sum of all question scores. ~75 questions → max score ~75. Match quality = total score / max possible.

---

## Q9 — Religion

**Question:** What is your religion?
**Options:** `Hindu` / `Muslim` / `Sikh` / `Jain` / `Christian` / `Buddhist` / `Parsi` / `No religion` / `Other`

**Scoring:** Same religion = 1.0. Different religion = 0.0. The hard gate (Q13 do-not-match list) already handles elimination — this score is just a bonus signal. Don't overweight.

---

## Q10 — Religious Practice Level

**Question:** How would you describe your religious practice?
**Options vary by religion:**
- Hindu: `Very religious` / `Religious` / `Moderately religious` / `Not religious`
- Muslim: `Very religious` / `Religious` / `Moderately religious` / `Liberal`
- Sikh: `Very religious (Amritdhari)` / `Religious (Keshdhari)` / `Moderate (Sahajdhari)` / `Not religious`
- Jain: `Very religious` / `Religious` / `Moderately religious` / `Not religious`
- Christian: `Very religious` / `Religious` / `Moderately religious` / `Not religious`

**Scoring:** Treat independently from religion. This is a lifestyle signal, not a religion signal.
- Same practice level = 1.0
- One step apart = 0.5
- Two steps apart = 0.25
- Opposite ends (Very religious + Not religious) = 0.0

Key insight: Two people of different religions who are both "not religious" might match well. Two people of different religions who are both "very religious" will clash. Score practice intensity on its own.

---

## Q12 — Caste / Community

**Question:** What is your caste or community?
**Options:** Built per state. Start with top 5 castes per state + `Other` (free text). Caste list maintained as a reference schema (state → religion → castes).

**Scoring:** Scoring driven by Q12a (caste importance). The caste field itself is just data — it's Q12a that determines the score.

---

## Q12a — Caste Importance

**Question:** How important is caste in your partner?
**Options:** `Must be same caste` / `Prefer same, open to others` / `Doesn't matter`

**Scoring:**
- "Must be same caste" + same caste = 1.0 (also a hard gate if different)
- "Doesn't matter" = 1.0 (always full marks — they don't care)
- "Prefer same, open to others" + same caste = 1.0
- "Prefer same, open to others" + different caste = 0.5

---

## Q1 — Date of Birth

**Question:** When were you born?
**Options:** Step 1: Year (2006–1970) / Step 2: Month

**Scoring:** Age calculated, compared against partner's explicit age range (Q40). Within range = 1.0. Outside range = 0.0. No buffer, no proximity scoring. (Q40 is a hard gate, so if they're outside range they're already eliminated — this score is redundant but included for completeness.)

---

## Q2 — Current Location

**Question:** Where do you live right now?
**Options:** Step 1: `India` / `Outside India` → Step 2: State or Country → Step 3: City

**Scoring:** Matched against partner's explicit location preference (Q2-pref, hard gate). Since Q2-pref is a hard gate, if they pass the gate they get 1.0. Don't penalize relocation willingness — some people actively want to relocate.

---

## Q3 — Where Did You Grow Up [REFRAMED]

**Question:** Where did you grow up?
**Options:** Step 1: `India` / `Outside India` → Step 2: If India: State. If outside: Country.

**Scoring:** Matched against partner's raised-in preference (Q3-pref, hard gate). If they pass the gate = 1.0. Gate handles elimination.

---

## Q4 — Mother Tongue

**Question:** What is your mother tongue?
**Options:** `Hindi` / `Gujarati` / `Marathi` / `Tamil` / `Telugu` / `Kannada` / `Malayalam` / `Bengali` / `Punjabi` / `Urdu` / `Odia` / `Assamese` / `Sindhi` / `Konkani` / `Tulu` / `Other`

Auto-select suggestion based on where they grew up (Q3).

**Scoring:**
- Same mother tongue = 1.0
- Different mother tongue but share a common non-English language (from Q5) = 0.8
- Only English in common = 0.5
- No shared language at all = 0.0

Note: Q15 (partner mother tongue preference) is now a hard gate. If someone says "Same language only" and tongues don't match, pair is eliminated before scoring.

---

## Q5 — Languages Spoken

**Question:** What other languages do you speak?
**Options (multi-select):** Same list as Q4 (minus their mother tongue) + `English`

**Scoring:** Not scored independently. Feeds into Q4 scoring (shared language check).

---

## Q29 — Diet [UPDATED OPTIONS]

**Question:** What is your diet?
**Options:** `Veg` / `Vegan` / `Eggetarian` / `Non-veg` / `Occasionally non-veg` / `Jain` / `Other`

(Remove religion-specific variants. Universal options.)

**Scoring:** Matched against partner's diet preference (Q33, hard gate). If they pass the gate = 1.0. Gate handles elimination. You either match or you don't.

---

## Q30 — Drinking

**Question:** Do you drink alcohol?
**Options:** `Never` / `Socially / Occasionally` / `Regularly`

**Scoring:** Matched against partner's drinking preference (Q34, hard gate). If they pass the gate:
- Same habit = 1.0
- Adjacent (Never + Social, or Social + Regular) = 0.5
- Passed gate but far apart = 0.25

---

## Q31 — Smoking

**Question:** Do you smoke?
**Options:** `Never` / `Socially / Occasionally` / `Regularly`

**Scoring:**
- Same habit = 1.0
- Adjacent (Never + Social) = 0.5
- Far apart = 0.0

---

## Q32 — Fitness Frequency [WOW FACTOR]

**Question:** How often do you exercise or play sports?
**Options:** `Daily` / `3-5 times a week` / `1-2 times a week` / `Rarely` / `Never`

**Scoring (WOW factor):**
- Same level = 1.5
- One step apart = 1.0
- Two steps apart = 0.5
- Far apart = 0.0

WOW because two gym-daily people finding each other is a bonus signal — lifestyle alignment that goes beyond dealbreakers.

---

## Q52 — Social Style [WOW FACTOR]

**Question:** How social are you?
**Options:** `Very social — love big gatherings` / `Social — enjoy going out but need downtime` / `Introverted — prefer small groups` / `Very introverted — homebody`

**Scoring (WOW factor):**
- Same style = 1.5
- One step apart = 1.0
- Two steps apart = 0.5
- Extremes = 0.0

---

## Q53 — Conflict Style [WOW FACTOR]

**Question:** When there's a disagreement, you tend to...
**Options:** `Talk it out immediately` / `Take some time, then discuss` / `Avoid conflict` / `Get heated, then cool down`

**Scoring (WOW factor):**
- Same style = 1.5
- One step apart = 1.0
- Two+ steps apart = 0.5

---

## Q16 — Education Level

**Question:** What is your highest education?
**Options:** `High school` / `Diploma` / `Bachelor's` / `Master's` / `Doctorate / PhD` / `Professional (CA, CS, MBBS, LLB)`

**Scoring:** Matched against partner's minimum education preference (Q20). Meets or exceeds = 1.0. Below = 0.0. Binary.

---

## Q17 — Education Field

**Question:** What field?
**Options:** `Engineering / IT` / `Medicine / Healthcare` / `Business / MBA` / `Law` / `Finance / CA / CS` / `Arts / Humanities` / `Science` / `Design / Architecture` / `Government / Civil Services` / `Other`

---

## Q17-pref — Partner Education Field Preference [NEW]

**Question:** Do you have a preference for your partner's field of study?
**Options:** `Same as mine` / `Doesn't matter` / `Specific fields...` (multi-select from Q17 list)

**Scoring:** "Same as mine" + match = 1.0, no match = 0.0. "Specific fields" + candidate in list = 1.0, not in list = 0.0. "Doesn't matter" = 1.0 always.

---

## Q18 — Occupation Sector

**Question:** What sector do you work in?
**Options:** `Public / Government` / `Private` / `Professional (Doctor, Lawyer, CA)` / `Business / Self-employed` / `Startup` / `Not working` / `Student` / `Other`

**Scoring:** Same sector = 1.0. Different sector = 0.0. Simple match.

---

## Q19 — Annual Income [UPDATED]

**Question:** What is your annual income?
**Options:** Country-based ranges (detected from Q2 location):
- India: `Under ₹5 lakh` / `₹5-10 lakh` / `₹10-20 lakh` / `₹20-35 lakh` / `₹35-50 lakh` / `₹50-75 lakh` / `₹75 lakh - ₹1 crore` / `₹1-2 crore` / `Above ₹2 crore` / `Prefer not to say`
- US: `Under $30K` / `$30-50K` / `$50-75K` / `$75-100K` / `$100-150K` / `$150-250K` / `Above $250K`
- UK, Canada, etc.: Country-specific ranges TBD

---

## Q21 — Partner Income Minimum [UPDATED]

**Question:** Minimum income you'd want in a partner?
**Options:** Same country-based brackets as Q19 + `Doesn't matter`

**Scoring:** Don't assume — explicit preference match. Candidate meets or exceeds = 1.0. Below = 0.0. "Doesn't matter" = 1.0 always.

---

## Q20 — Partner Education Minimum

**Question:** Minimum education you'd want in a partner?
**Options:** `Doesn't matter` / `At least High school` / `At least Bachelor's` / `At least Master's` / `At least Professional degree`

**Scoring:** Candidate meets or exceeds = 1.0. Below = 0.0. "Doesn't matter" = 1.0 always.

---

## Q23 — Family Financial Status [UPDATED]

**Question:** How would you describe your family's financial status?
**Options (India):**
- `Less than ₹10 lakh annual income`
- `₹10-30 lakh annual income + some assets`
- `₹30-70 lakh annual income + assets`
- `₹70 lakh+ annual income + significant assets`
- `Assets over ₹10 crore`
- `Prefer not to say`

**Options (Outside India):** Country-specific tiers TBD (based on Q2 location).

**Scoring:** Matched against Q50 (partner family status preference).

---

## Q50 — Partner Family Status Preference [NOW SCORED]

**Question:** Partner's family financial status preference?
**Options:** `Same or higher` / `Doesn't matter`

**Scoring:** "Doesn't matter" = 1.0 always. "Same or higher" = compare Q23 values. Candidate same or higher tier = 1.0. Lower = 0.0.

---

## Q22 — Family Type [REFRAMED]

**Question:** Were you raised in a nuclear or joint family?
**Options:** `Nuclear` / `Joint` / `Semi-joint`

---

## Q22-pref — Partner Family Type Preference [NEW]

**Question:** Do you prefer your partner to be raised in a similar family setup?
**Options:** `Same as mine` / `Doesn't matter`

**Scoring:** "Same as mine" + match = 1.0, no match = 0.0. "Doesn't matter" = 1.0 always.

---

## Q25 — Father's Occupation

**Question:** Father's occupation?
**Options:** `Business / Self-employed` / `Service / Salaried` / `Professional (Doctor, Lawyer, CA)` / `Government` / `Retired` / `Not alive` / `Prefer not to say`

**Scoring:** Same category = 1.0. Different = 0.0. ("Not alive" and "Prefer not to say" = skip, no penalty.)

---

## Q26 — Mother's Occupation

**Question:** Mother's occupation?
**Options:** `Homemaker` / `Working professional` / `Business` / `Government` / `Retired` / `Not alive` / `Prefer not to say`

**Scoring:** Same category = 1.0. Different = 0.0. ("Not alive" and "Prefer not to say" = skip, no penalty.)

---

## Q27 — Siblings

**Question:** Do you have siblings?
**Options:** `Only child` / `1 sibling` / `2 siblings` / `3+ siblings`

---

## Q27-pref — Partner Siblings Preference [NEW]

**Question:** Do you have a preference about your partner's siblings?
**Options:** `Must have siblings` / `Single child is fine` / `Doesn't matter`

**Scoring:** "Must have siblings" + candidate is only child = 0.0, has siblings = 1.0. "Single child is fine" + "Doesn't matter" = 1.0 always.

---

## Q37a — Children Timeline

**Question:** When would you want children?
**Options:** `Soon after marriage` / `After 2-3 years` / `After 4+ years`
**Only shown if:** Q37 ≠ "No"

---

## Q37a-pref — Partner Children Timeline Preference [NEW]

**Question:** When would you want your partner to be open to having children?
**Options:** `Soon after marriage` / `After 2-3 years` / `After 4+ years` / `Doesn't matter`

**Scoring:** Match = 1.0. No match = 0.0. "Doesn't matter" = 1.0 always.

---

## Q36 — Marriage Timeline (also a hard gate) [UPDATED]

**Question:** How soon are you looking to get married?
**Options:** `Within 1 year` / `1-2 years` / `2-3 years` / `Just exploring`

**Scoring:** Same timeline = 1.0. One step apart (passes hard gate) = 0.5. This is scored in addition to the hard gate filter.

---

## Q38 — Living Arrangement

**Question:** After marriage, where would you want to live?
**Options:** `With parents (joint family)` / `Near parents but separate` / `Independent — wherever life takes us` / `Open to discussion`

---

## Q38-pref — Partner Living Arrangement Preference [NEW]

**Question:** What living arrangement would you need your partner to be open to?
**Options:** Same as Q38 options + `Doesn't matter`

**Scoring:** Match = 1.0. No match = 0.0. "Doesn't matter" or either said "Open to discussion" = 1.0.

---

## Q46 — Financial Planning (Both genders)

**Question:** How should finances work in a marriage?
**Options:** `Fully joint` / `Joint for household, separate for personal` / `Mostly separate`

**Scoring:** Plain match. Same = 1.0. Different = 0.0.

---

## Q42M — Cooking Contribution (Men)

**Question:** Out of 15 meals in a week, how many are you willing to cook?
**Options:** `0` / `1-3` / `4-7` / `8-10` / `More than 10`

---

## Q42M-pref — Partner Cooking Expectation (Men) [NEW]

**Question:** How often do you need your partner to cook?
**Options:** `Regularly (7+ meals a week)` / `Sometimes (3-6 meals)` / `Rarely (1-2 meals)` / `Never — I'll handle it or we'll outsource`

Matched against her cooking contribution (Q43F). Meets or exceeds = 1.0. Exceeds by 2+ levels = 1.5 (WOW). Below = 0.0.

---

## Q44M — Partner Working Preference (Men)

**Question:** Do you want your partner to work?
**Options:** `Yes, she should have a career` / `Her choice` / `Prefer she focuses on home`

**Scoring:** Cross-matched against her career_after_marriage (Q46F). Aligned = 1.0. Misaligned = 0.0. "Her choice" = 1.0 with anything.

---

## Q42F — Do You Cook (Women)

**Question:** Do you know how to cook?
**Options:** `Yes, I cook regularly` / `Yes, but I don't cook often` / `No, but I'm willing to learn` / `No`

---

## Q42F-pref — Does Partner Need to Cook (Women) [NEW — ask men this]

**Question (asked to men):** Do you need your partner to know how to cook?
**Options:** `Yes, must cook regularly` / `Some cooking is enough` / `Doesn't matter`

**Scoring:** Matched against her Q42F answer. "Must cook regularly" + she cooks regularly = 1.0. "Must cook regularly" + she says No = 0.0. "Doesn't matter" = 1.0 always.

---

## Q43F — Cooking Contribution (Women)

**Question:** Out of 15 meals in a week, how many are you willing to cook?
**Options:** `0` / `1-3` / `4-7` / `8-10` / `More than 10`

**Scoring:** Matched against his Q42M-pref (partner cooking expectation for men). Meets or exceeds expectation = 1.0. Exceeds by 2+ levels = 1.5 (WOW). Below = 0.0.

---

## Q44F — Partner Cooking Preference (Women)

**Question:** How often do you need your partner to cook?
**Options:** `Regularly (7+ meals a week)` / `Sometimes (3-6 meals)` / `Rarely (1-2 meals)` / `Never — I'll handle it or we'll outsource`

**Scoring:** Matched against his cooking_contribution (Q42M). Meets or exceeds = 1.0. Exceeds by 2+ levels = 1.5 (WOW). Below = 0.0.

---

## Q43M — Household Contribution (Men) [NOW SCORED]

**Question:** How do you see household responsibilities?
**Options:** `Mostly her` / `Shared equally` / `Mostly outsourced (cook/maid)` / `Flexible — whatever works`

**Scoring:** Cross-matched against her Q45F (partner household preference). Match = 1.0. No match = 0.0. "Flexible" = 1.0 with anything.

---

## Q45F — Partner Household Preference (Women) [NOW SCORED]

**Question:** How much do you need your partner to contribute to household chores?
**Options:** `Equal share` / `Significant help` / `Some help` / `Not needed — I'll manage or outsource`

**Scoring:** Matched against his Q43M. "Equal share" + he says "Shared equally" = 1.0. "Equal share" + he says "Mostly her" = 0.0. "Not needed" = 1.0 with anything.

---

## Q46F — Career After Marriage (Women)

**Question:** Do you plan to continue working after marriage?
**Options:** `Yes, definitely` / `Yes, but open to a break for kids` / `Undecided` / `No, prefer homemaking`

**Scoring:** Cross-matched against his Q44M (partner working preference). Aligned = 1.0. Misaligned = 0.0.

---

## Q48F — Living with In-Laws (Women)

**Question:** Would you be OK living with his parents?
**Options:** `Yes, happy to` / `For some time, not permanently` / `Prefer not to` / `Depends on the situation`

**Scoring:** Cross-matched against his Q38 (living arrangement). He wants joint family + she's happy to = 1.0. He wants joint + she prefers not to = 0.0. He wants independent = 1.0 regardless. "Depends" = 0.5 with joint, 1.0 with anything else.

---

## Q7 — Height

**Question:** How tall are you?
**Options (Women):** `Below 5'2"` / `5'2"` / `5'3"` / `5'4"` / `5'5"` / `5'6"` / `5'7"` / `Above 5'7"`
**Options (Men):** `Below 5'5"` / `5'5"` / `5'6"` / `5'7"` / `5'8"` / `5'9"` / `5'10"` / `5'11"` / `6'0"` / `6'1"` / `6'2"` / `6'3"` / `Above 6'3"`

**Scoring:** Matched via Q41 hard gate. If they pass the gate = 1.0.

---

## Q8 — Weight / BMI [NOW SCORED]

**Question:** What is your weight?
**Options (Women):** `Below 45 kg` / `45-50 kg` / `50-55 kg` / `55-60 kg` / `60-65 kg` / `65-70 kg` / `70-75 kg` / `75-80 kg` / `Above 80 kg`
**Options (Men):** `Below 60 kg` / `60-65 kg` / `65-70 kg` / `70-75 kg` / `75-80 kg` / `80-85 kg` / `85-90 kg` / `90-100 kg` / `Above 100 kg`

**Scoring:** Calculate BMI from height (Q7) + weight (Q8). Compare BMI ranges:
- BMI categories: Underweight (<18.5) / Normal (18.5-24.9) / Overweight (25-29.9) / Obese (30+)
- Same BMI range = 1.0
- One step apart = 0.5
- Two steps apart = 0.25
- Three steps apart = 0.0

---

# PART 3: SKIPPED QUESTIONS

These are either removed from intake or collected but not used in free-tier matching.

---

## Q24 — Family Values [SKIP]

~~How would you describe your family's values? Traditional / Moderate / Liberal~~

**Skipped.** Self-assessment is unreliable. Everyone thinks they're "moderate." Remove from intake for now.

---

## Q28 — Family Involvement in Decision [SKIP]

~~How involved will your family be in the decision?~~

**Skipped.** If you're on Masii, your family is involved. That's the whole point. If they weren't, they'd be on Tinder. Remove from intake.

---

## Q11 — Sect / Denomination [SKIP]

~~What is your sect or denomination?~~

**Skipped.** Not enough data to tree this properly yet. Keep for future premium matching. Remove from free-tier intake.

---

## Q48 / Q48a — Gotra [SKIP]

~~What is your gotra? / Any gotras you cannot match with?~~

**Skipped.** They can match this later. Remove from free-tier intake.

---

## Q49 — Family Property [SKIP]

~~Does your family own property?~~

**Skipped.** Covered by family wealth question (Q23). Remove from intake.

---

## Q47F — Financial Contribution View (Women) [SKIP]

~~How do you see financial contribution in a marriage?~~

**Skipped.** Doesn't filter anything new — financial planning (Q46) already covers this for both genders. Remove from intake.

---

# PART 4: NEW QUESTIONS SUMMARY

All new questions that need to be added to the intake flow:

| ID | Question | Asked to | After | Type |
|----|----------|----------|-------|------|
| Q6-pref | Partner marital status preference | All | Q6 | Hard gate |
| Q6a-pref | Partner existing children preference | All (if applicable) | Q6a | Hard gate |
| Q3-pref | Partner raised-in preference | All | Q3 | Hard gate |
| Q2-pref | Partner current location preference | All | Q2 | Hard gate |
| Q15 | Partner mother tongue preference | All | Q4 | Hard gate (moved from unused) |
| Q17-pref | Partner education field preference | All | Q17 | Scored |
| Q22-pref | Partner family type preference | All | Q22 | Scored |
| Q27-pref | Partner siblings preference | All | Q27 | Scored |
| Q37a-pref | Partner children timeline preference | If Q37 ≠ No | Q37a | Scored |
| Q38-pref | Partner living arrangement preference | All | Q38 | Scored |
| Q42M-pref | Partner cooking expectation | Men | Q42M | Scored |
| Q42F-pref | Does partner need to cook | Men (about women) | Q42M | Scored |
| Q51-disability | Disability question | All | Q51 | Hard gate input |
| Q51a-disability | Partner disability preference | All | Q51a | Hard gate |

---

# PART 5: SCORING MODEL

**Total score = sum of all scored questions / max possible score**

Example with ~50 scored questions (after skips):
- Hard gates eliminate first — if any gate fails, pair is never scored
- Remaining pairs get scored: each question contributes 0.0 to 1.0 (or 1.5 for WOW)
- Max possible ≈ 55-60 points (with WOW factors)
- Match quality = total / max × 100

**Score tiers for free introductions:**
- 75%+ = strong match, free introduction
- 60-74% = decent match, free introduction
- Below 60% = not shown in free tier

**What this means:** With ~50 questions at 1.0 each and 5 WOW questions at 1.5 each (fitness, social, conflict, cooking M↔F, cooking F↔M), max is ~57.5. A 75% threshold means ~43 questions need to match. A pair that matches on all the important stuff (religion, caste, location, age, diet, lifestyle, family) but differs on fitness and parents' occupation still clears easily.

**Hard gates ensure the floor.** The score determines the ceiling. Religion weight comes from the hard gate, not from inflated scoring.
