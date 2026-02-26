# JODI MVP — TELEGRAM ONBOARDING FLOW v2
**(77 Questions from Tab 3 Schema — India-Specific Matchmaking)**

**Created:** Feb 21, 2026  
**Status:** Ready for N's approval  
**Schema Source:** "Jodi Schema - MVP and 100+ Data Points" → Tab 3: "Updated MVP questions"

---

## 📋 OVERVIEW

**Total Questions:** 71-77 (varies by user path due to conditional logic)  
**Time Estimate:** 12-15 minutes for button phase  
**Format:** Button-based (Telegram inline keyboards)  
**Cost:** $0.00 for button phase  
**India-Specific Features:**
- Caste/community filtering (Hindu/Jain/Sikh)
- Manglik status (kundli matching)
- NRI vs India-based paths
- Gotra exclusion logic
- Diet types (Pure veg, Jain food, Halal)
- Joint family dynamics

---

## 🎬 INTRO SEQUENCE (2-3 minutes)
*[Keep existing intro — proven to work]*

### Message 1
```
Hey! 👋 I'm Jodi.

I help people find real, lasting relationships.
No swiping. No algorithms optimized to keep you scrolling.

Just one great introduction at a time.
```
**Button:** `[ Tell me more → ]`

---

### Message 2
```
Before we start — something important.

This is your space. Whatever you share here is between us. It doesn't go on a profile. It doesn't go on a form. Your parents won't see it. Your friends won't see it. No one sees anything unless you approve it.

You can tell me things here that you might not say out loud — what you actually want, what you've been through, what matters to you when no one's watching.

I'm not here to judge. I'm here to find you the right person. The more honest you are with me, the better I can do that.
```
**Button:** `[ I like that. Keep going → ]`

---

### Message 3
```
One thing we do differently — photos come at the end of our process, not the beginning.

We know not everyone photographs well. And honestly, AI filters have made photos pretty unreliable anyway.

I'd rather understand who you are first — your values, your energy, what makes you laugh, what you need in a partner. That's what actually predicts a great match.

Photos matter, but they're not the whole story. And they're definitely not the first chapter.
```
**Button:** `[ That's refreshing → ]`

---

### Message 4
```
Here's how I find people for you:

I start with your basics and deal-breakers to filter out anyone who clearly isn't right.

Then I go deeper — personality, values, lifestyle, the stuff that actually makes two people click.

When I find someone promising, I'll introduce you. One person at a time, with context on why I think you'd work well together.
```
**Button:** `[ And then? → ]`

---

### Message 5
```
The best part — I learn as we go.

When I show you a match, your reaction teaches me something. What excited you. What felt off. What surprised you.

Even the matches that don't work out make the next one better. Think of it like a friend who sets you up — except I remember everything and never stop trying.
```
**Button:** `[ Makes sense → ]`

---

### Message 6
```
Okay, here's the plan:

First, I'll ask some quick-tap questions — deal-breakers, lifestyle, the structured stuff. Takes about 12-15 minutes. No typing, just tapping.

After that, we switch to real conversation. I'll ask you questions a good friend would ask if they were setting you up. Answer whenever you feel like it — no rush, no pressure.

And if you ever want to change an answer, just tell me later during our chats. Nothing is locked in.
```
**Button:** `[ Let's start → ]`

---

### Message 7
```
Last thing — your privacy.

🔒 Your data is encrypted and never sold
🔒 Matches only see what you approve
🔒 You can delete everything at any time
🔒 I'll always ask before sharing anything

This only works if we trust each other. I take that seriously.
```
**Button:** `[ Got it, let's go → ]`

---

## A. IDENTITY & BASICS (9 questions)

**Section intro:**
```
Let's start with the basics — who you are and what you're looking for.
```

---

### A1. Gender Identity
**Field:** `gender_identity`  
**Question:** "I am a:"

**Buttons:**
```
[ 👨 Male ]
[ 👩 Female ]
[ ⚧️ Non-binary ]
[ 💬 Self-describe → ]
```

**Storage:** `users.gender_identity` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Core matching axis

---

### A2. Looking For Gender
**Field:** `looking_for_gender`  
**Question:** "Looking for:"

**Buttons:**
```
[ Men ]
[ Women ]
[ Either ]
```

**Storage:** `users.looking_for_gender` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Core matching axis

---

### A3. Date of Birth
**Field:** `date_of_birth`  
**Question:** 
```
Your date of birth: (DD/MM/YYYY)

I keep your exact date private — only your age shows to matches.
```

**Input:** Text reply  
**Placeholder:** "DD/MM/YYYY"  
**Validation:** Age 18-80, valid date format

**Response:** `"{age} — got it ✓"`

**Storage:** `users.date_of_birth` (DATE, indexed)  
**Filter Type:** Hard Filter  
**Why:** Exact age calc; age-range filtering; legal verification

---

### A4. Marital Status
**Field:** `marital_status`  
**Question:** "Marital status:"

**Buttons:**
```
[ Never married ]
[ Divorced ]
[ Widowed ]
[ Separated ]
[ Annulled ]
```

**Storage:** `users.marital_status` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Top-3 dealbreaker in Indian matchmaking

---

### A5. Do You Have Children? ⚠️ CONDITIONAL
**Field:** `children_existing`  
**Shows ONLY if:** `marital_status ≠ "Never married"`

**Question:** "Do you have children?"

**Buttons:**
```
[ No ]
[ Yes, living with me ]
[ Yes, not living with me ]
```

**Storage:** `users.children_existing` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Major dealbreaker; affects lifestyle compatibility

---

### A6. Height
**Field:** `height_cm`  
**Question:** "Your height:"

**Buttons (2 columns):**
```
[ < 150cm ]        [ 150-155cm ]
[ 156-160cm ]      [ 161-165cm ]
[ 166-170cm ]      [ 171-175cm ]
[ 176-180cm ]      [ 181-185cm ]
[ 186-190cm ]      [ 190cm+ ]
```

**Storage:** `users.height_cm` (INT)  
**Filter Type:** Soft Filter  
**Why:** Top physical filter in Indian matchmaking

---

### A7. Body Type
**Field:** `body_type`  
**Question:** "Body type:"

**Buttons:**
```
[ Slim ]
[ Athletic ]
[ Average ]
[ Curvy ]
[ Heavy ]
```

**Storage:** `users.body_type` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Physical compatibility signal

---

### A8. Complexion
**Field:** `complexion`  
**Question:** "Complexion:"

**Buttons (2 columns):**
```
[ Fair ]           [ Wheatish ]
[ Medium ]         [ Dusky ]
[ Dark ]           [ Prefer not to say ]
```

**Storage:** `users.complexion` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Controversial but real Indian filter; "Prefer not to say" respects choice

---

### A9. Disability Status
**Field:** `disability_status`  
**Question:** "Any physical disability?"

**Buttons:**
```
[ None ]
[ Yes, minor ]
[ Yes, significant ]
[ Prefer not to say ]
```

**Storage:** `users.disability_status` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Transparency; avoids awkward reveals later

---

## B. LOCATION & MOBILITY (8 questions)

**Section intro:**
```
Now let's talk about where you are and where you could be...
```

---

### B10. Residency Status
**Field:** `residency_type`  
**Question:** "Residency status:"

**Buttons:**
```
[ Indian citizen (in India) ]
[ NRI (Non-Resident Indian) ]
[ OCI / PIO ]
[ Foreign national of Indian origin ]
```

**Storage:** `users.residency_type` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Drives entire location & legal compatibility branch

---

### B11. Country You Live In ⚠️ CONDITIONAL
**Field:** `country_current`  
**Shows ONLY if:** `residency_type ≠ "Indian citizen (in India)"`

**Question:** "Country you live in:"

**Buttons (2 columns):**
```
[ 🇦🇪 UAE ]          [ 🇺🇸 USA ]
[ 🇬🇧 UK ]           [ 🇨🇦 Canada ]
[ 🇦🇺 Australia ]    [ 🇸🇬 Singapore ]
[ 🇩🇪 Germany ]      [ 🇸🇦 Saudi Arabia ]
[ 🇶🇦 Qatar ]        [ 💬 Other → ]
```

**Storage:** `users.country_current` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** NRI geography matters for timezone, visa, visits

---

### B12. State (India) ⚠️ CONDITIONAL
**Field:** `state_india`  
**Shows ONLY if:** `residency_type = "Indian citizen (in India)"`

**Question:** "State:"

**Buttons (scrollable list):**
```
[ Maharashtra ] [ Karnataka ] [ Tamil Nadu ]
[ Gujarat ] [ Delhi NCR ] [ Uttar Pradesh ]
[ West Bengal ] [ Rajasthan ] [ Kerala ]
[ Punjab ] [ Haryana ] [ Telangana ]
[ Andhra Pradesh ] [ Madhya Pradesh ] [ Odisha ]
[... all 28 states + 8 UTs ...]
```

**Storage:** `users.state_india` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Regional culture, language, cuisine alignment

---

### B13. City (Current)
**Field:** `city_current`  
**Question:** "City:"

**Dynamic buttons based on country/state selected**

**Example (India-Maharashtra):**
```
[ Mumbai ]
[ Pune ]
[ Nagpur ]
[ Thane ]
[ Other → ]
```

**Example (UAE):**
```
[ Dubai ]
[ Abu Dhabi ]
[ Sharjah ]
[ Other → ]
```

**Storage:** `users.city_current` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Proximity matching; metro vs tier-2 lifestyle gap

---

### B14. Hometown State
**Field:** `hometown_state`  
**Question:** "Native place / hometown state:"

**Buttons:** [Same dropdown as B12]

**Storage:** `users.hometown_state` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** "Where are you originally from" — cultural roots signal

---

### B15. Open to Relocating?
**Field:** `willing_to_relocate`  
**Question:** "Open to relocating?"

**Buttons:**
```
[ Yes, anywhere ]
[ Yes, within India ]
[ Yes, within my state ]
[ Yes, to India (NRI returning) ]
[ Maybe, depends on partner ]
[ No ]
```

**Storage:** `users.willing_to_relocate` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Eliminates geographic dead-ends early

---

### B16. Partner Location Preference
**Field:** `partner_location_pref`  
**Question:** "Partner location preference:"

**Buttons:**
```
[ Same city ]
[ Same state/region ]
[ Anywhere in India ]
[ NRI OK ]
[ International OK ]
[ No preference ]
```

**Storage:** `preferences.partner_location_pref` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Two-way geographic filter

---

### B17. Settle Long-Term? ⚠️ CONDITIONAL
**Field:** `settling_country`  
**Shows ONLY if:** `residency_type = "NRI" OR "OCI / PIO"`

**Question:** "Where do you plan to settle long-term?"

**Buttons:**
```
[ India ]
[ Abroad ]
[ Open to either ]
[ Haven't decided ]
```

**Storage:** `users.settling_country` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** NRI-specific: "are you coming back or staying?"

---

## C. RELIGION, CASTE & CULTURE (10 questions)
*⚠️ This section has the most conditional branching*

**Section intro:**
```
Next — religion and culture. These matter in Indian matchmaking, so let's be clear about where you stand...
```

---

### C18. Your Religion
**Field:** `religion`  
**Question:** "Your religion:"

**Buttons (2 columns):**
```
[ 🕉️ Hindu ]               [ ☪️ Muslim ]
[ ✝️ Christian ]           [ ☬ Sikh ]
[ 🔯 Jain ]                [ ☸️ Buddhist ]
[ ⚔️ Parsi/Zoroastrian ]   [ ✡️ Jewish ]
[ 🔮 Spiritual (not religious) ]
[ 🚫 No religion / Atheist ]
[ 💬 Other → ]
```

**Storage:** `users.religion` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** #1 filter in Indian matchmaking  
**Triggers:** Different C21 sect options based on selection

---

### C19. How Religious Are You?
**Field:** `religious_practice`  
**Question:** "How religious are you?"

**Buttons:**
```
[ Very devout (daily practice) ]
[ Moderately observant (festivals, rituals) ]
[ Culturally identify (not practicing) ]
[ Spiritual, not religious ]
[ Not at all ]
```

**Storage:** `users.religious_practice` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** Devout + non-religious = friction

---

### C20. Partner's Religion
**Field:** `partner_religion_pref`  
**Question:** "Partner's religion:"

**Buttons:**
```
[ Must be same ]
[ Prefer same, open to others ]
[ Doesn't matter ]
```

**Storage:** `preferences.partner_religion_pref` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Two-way religion filter

---

### C21. Sect / Denomination ⚠️ CONDITIONAL
**Field:** `sect_denomination`  
**Dropdown options CHANGE based on C18 religion selected**

**IF C18 = Hindu:**
```
Sect / denomination:

[ Shaivite ]
[ Vaishnavite ]
[ Arya Samaj ]
[ Smartha ]
[ None ]
[ Prefer not to say ]
```

**IF C18 = Muslim:**
```
Sect / denomination:

[ Sunni ]
[ Shia ]
[ Sufi ]
[ Ahmadiyya ]
[ None ]
[ Prefer not to say ]
```

**IF C18 = Christian:**
```
Sect / denomination:

[ Catholic ]
[ Protestant ]
[ Orthodox ]
[ Evangelical ]
[ Other → ]
```

**IF C18 = Sikh:**
```
Sect:

[ Amritdhari ]
[ Keshdhari ]
[ Sehajdhari ]
[ None ]
```

**IF C18 = Jain:**
```
Sect:

[ Digambar ]
[ Shwetambar ]
[ None ]
```

**Storage:** `users.sect_denomination` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Matters within religions; Sunni-Shia, Catholic-Protestant

---

### C22. Caste / Community ⚠️ CONDITIONAL
**Field:** `caste_community`  
**Shows ONLY if:** `religion = "Hindu" OR "Jain" OR "Sikh" OR "Buddhist"`

**IF Hindu:**
```
Caste / community:

[ Brahmin ]
[ Kshatriya ]
[ Vaishya ]
[ SC (Scheduled Caste) ]
[ ST (Scheduled Tribe) ]
[ OBC (Other Backward Class) ]
[ General ]
[ Other → ]
[ Prefer not to say ]
```

**IF Sikh:**
```
Caste / community:

[ Jat ]
[ Khatri ]
[ Ramgarhia ]
[ Other → ]
[ Prefer not to say ]
```

**IF Jain:**
```
Caste / community:

[ Oswal ]
[ Agarwal ]
[ Porwal ]
[ Digambar ]
[ Shwetambar ]
[ Other → ]
[ Prefer not to say ]
```

**Storage:** `users.caste_community` (VARCHAR, indexed)  
**Filter Type:** Hard Filter (if caste_importance high)  
**Why:** Real filter Indian families use

---

### C23. Sub-caste / Gotra ⚠️ CONDITIONAL
**Field:** `sub_caste`  
**Shows ONLY if:** `caste_community answered (not "Prefer not to say")`

**Question:** 
```
Sub-caste / gotra (optional):
```

**Input:** Text reply  
**Placeholder:** "e.g. Sharma, Reddy, Iyer, Agarwal..."

**Storage:** `users.sub_caste` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Gotra matters for same-gotra exclusion in some communities

---

### C24. How Important Is Caste Match?
**Field:** `caste_importance`  
**Shows ONLY if:** `caste_community answered`

**Question:** "How important is caste/community match?"

**Buttons:**
```
[ Dealbreaker — must match ]
[ Strong preference ]
[ Slight preference ]
[ Doesn't matter at all ]
```

**Storage:** `preferences.caste_importance` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Weights the caste filter; "doesn't matter" opens the pool

---

### C25. Mother Tongue
**Field:** `mother_tongue`  
**Question:** "Mother tongue:"

**Buttons (scrollable):**
```
[ Hindi ] [ Tamil ] [ Telugu ] [ Kannada ]
[ Malayalam ] [ Bengali ] [ Marathi ] [ Gujarati ]
[ Punjabi ] [ Odia ] [ Assamese ] [ Urdu ]
[ Konkani ] [ Sindhi ] [ Kashmiri ] [ English ]
[ Other → ]
```

**Storage:** `users.mother_tongue` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Language = culture; affects daily household dynamics

---

### C26. Languages You Speak
**Field:** `languages_spoken`  
**Question:** 
```
Languages you speak:

(Tap all that apply)
```

**Multi-select from same list as C25**

**Storage:** `users.languages_spoken` (ARRAY)  
**Filter Type:** Algo Weight  
**Why:** Communication compatibility; bilingual couples common

---

### C27. Manglik Status ⚠️ CONDITIONAL
**Field:** `manglik_status`  
**Shows ONLY if:** `religion = "Hindu" OR "Jain"`

**Question:** "Manglik status:"

**Buttons:**
```
[ Manglik ]
[ Non-Manglik ]
[ Anshik Manglik ]
[ Don't know ]
[ Not applicable ]
```

**Storage:** `users.manglik_status` (VARCHAR)  
**Filter Type:** Hard Filter (for users who care about it)  
**Why:** Kundli-based dealbreaker for many Hindu families

---

## D. EDUCATION & CAREER (5 questions)

**Section intro:**
```
Nice work — basics covered ✓

Now a few questions about your career...
```

---

### D28. Highest Education
**Field:** `education_level`  
**Question:** "Highest education:"

**Buttons:**
```
[ High school / 12th ]
[ Diploma / ITI ]
[ Bachelor's (BA/BSc/BCom) ]
[ Bachelor's (BTech/BE/BBA) ]
[ Master's (MA/MSc/MCom) ]
[ Master's (MBA/MTech) ]
[ Professional (CA/CS/CFA/MBBS/LLB) ]
[ PhD / Doctorate ]
```

**Storage:** `users.education_level` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Education level = social signaling in India

---

### D29. Institute Type
**Field:** `education_institute_tier`  
**Question:** "Institute type:"

**Buttons:**
```
[ IIT / IIM / AIIMS / NLU / ISB ]
[ NITs / IIITs / Top private (BITS, VIT) ]
[ State university / Other private ]
[ Studied abroad ]
[ Other ]
```

**Storage:** `users.education_institute_tier` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** "IIT boy" is a real filter in Indian matchmaking

---

### D30. Employment Status
**Field:** `employment_status`  
**Question:** "Employment:"

**Buttons (2 columns):**
```
[ Employed full-time ]    [ Self-employed / Business ]
[ Freelancer ]            [ Government job ]
[ Student ]               [ Between jobs ]
[ Homemaker ]             [ Retired ]
```

**Storage:** `users.employment_status` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Stability signal; govt job = prestige in India

---

### D31. Industry / Field
**Field:** `work_industry`  
**Question:** "Industry / field:"

**Buttons (2 columns):**
```
[ IT / Software ]         [ Finance / Banking ]
[ Healthcare / Pharma ]   [ Education / Academia ]
[ Government / PSU ]      [ Legal ]
[ Media / Entertainment ] [ Manufacturing ]
[ Real estate ]           [ Agriculture / Farming ]
[ Startup ]               [ E-commerce ]
[ Defence / Armed forces ][ Other → ]
```

**Storage:** `users.work_industry` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** Lifestyle & schedule compatibility

---

### D32. Career Priority
**Field:** `career_ambition`  
**Question:** "Career priority:"

**Buttons:**
```
[ Highly ambitious (career comes first) ]
[ Career-oriented but balanced ]
[ Flexible / adaptable ]
[ Prefer homemaking ]
[ Planning career break ]
```

**Storage:** `personality.career_ambition` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Dual-career vs single-income expectation alignment

---

## E. FINANCIAL PROFILE 🔒 (5 questions)
*[PRIVATE SECTION — Never shown to matches]*

**Section intro:**
```
Next section is about finances 💰

🔒 This stays 100% private — never shown to matches.
It helps me understand lifestyle compatibility.
```

---

### E33. Your Annual Income
**Field:** `annual_income`  
**Question:** "🔒 Your annual income:"

**IF country = India (INR):**
```
[ Below ₹5L ]
[ ₹5-10L ]
[ ₹10-20L ]
[ ₹20-40L ]
[ ₹40-75L ]
[ ₹75L-1Cr ]
[ ₹1-3Cr ]
[ ₹3Cr+ ]
[ Prefer not to say ]
```

**IF country = UAE/USA/UK/etc. (adjust currency dynamically):**
```
[ Below $50K ]
[ $50K-100K ]
[ $100K-200K ]
[ $200K-500K ]
[ $500K+ ]
[ Prefer not to say ]
```

**Storage:** `users.annual_income` (VARCHAR, PRIVATE)  
**Filter Type:** Algo Weight (Private)  
**Why:** Income-compatible matching without revealing numbers

---

### E34. Income Currency ⚠️ CONDITIONAL
**Field:** `income_currency`  
**Shows ONLY if:** `residency_type ≠ "Indian citizen (in India)"`

**Question:** "🔒 Income currency:"

**Buttons:**
```
[ INR ] [ USD ] [ GBP ] [ EUR ]
[ AED ] [ SGD ] [ AUD ] [ CAD ]
[ Other → ]
```

**Storage:** `users.income_currency` (VARCHAR, PRIVATE)  
**Filter Type:** Private  
**Why:** NRI incomes need currency context; $80K ≠ ₹80L lifestyle

---

### E35. Net Worth Range
**Field:** `net_worth_range`  
**Question:** "🔒 Approximate net worth:"

**IF India:**
```
[ Below ₹10L ]
[ ₹10-50L ]
[ ₹50L-1Cr ]
[ ₹1-5Cr ]
[ ₹5-10Cr ]
[ ₹10Cr+ ]
[ Prefer not to say ]
```

**Storage:** `users.net_worth_range` (VARCHAR, PRIVATE)  
**Filter Type:** Algo Weight (Private)  
**Why:** Wealth = lifestyle match signal

---

### E36. Own Property?
**Field:** `property_ownership`  
**Question:** "🔒 Own property?"

**Buttons:**
```
[ Yes, own house/flat ]
[ Yes, land/plot ]
[ Family property (will inherit) ]
[ No ]
[ Prefer not to say ]
```

**Storage:** `users.property_ownership` (VARCHAR, PRIVATE)  
**Filter Type:** Private  
**Why:** Asset signal; "family property" is very Indian

---

### E37. Financial Dependents?
**Field:** `financial_dependents`  
**Question:** "🔒 Financial dependents?"

**Buttons:**
```
[ None ]
[ Parents ]
[ Siblings ]
[ Extended family ]
[ Children ]
[ Multiple dependents ]
```

**Storage:** `users.financial_dependents` (VARCHAR, PRIVATE)  
**Filter Type:** Private  
**Why:** Hidden cost that affects couple finances

---

## F. FAMILY BACKGROUND (7 questions)

**Section intro:**
```
Almost halfway there — doing great ✓

Now some questions about family...
```

---

### F38. Family Type
**Field:** `family_type`  
**Question:** "Family type:"

**Buttons:**
```
[ Nuclear ]
[ Joint family ]
[ Extended joint family ]
```

**Storage:** `users.family_type` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Joint family = very different married life

---

### F39. Family Financial Status
**Field:** `family_financial_status`  
**Question:** "Family background:"

**Buttons:**
```
[ Upper class ]
[ Upper-middle class ]
[ Middle class ]
[ Lower-middle class ]
[ Prefer not to say ]
```

**Storage:** `users.family_financial_status` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** Lifestyle expectation alignment

---

### F40. Father's Occupation
**Field:** `father_occupation`  
**Question:** "Father's occupation:"

**Buttons:**
```
[ Business owner ]
[ Government / PSU ]
[ Private sector ]
[ Professional (Doctor/Lawyer/CA) ]
[ Agriculture / Farming ]
[ Retired ]
[ Late ]
[ Other → ]
```

**Storage:** `users.father_occupation` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** "What does your father do?" — classic Indian matchmaking Q

---

### F41. Family Values
**Field:** `family_values`  
**Question:** "Family values:"

**Buttons:**
```
[ Very traditional / orthodox ]
[ Moderate — mix of tradition and modern ]
[ Liberal / progressive ]
[ We're pretty chill ]
```

**Storage:** `personality.family_values` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Traditional vs modern household expectations

---

### F42. Live with Parents Post-Marriage?
**Field:** `living_with_parents_post_marriage`  
**Question:** "After marriage, live with parents?"

**Buttons:**
```
[ Yes, with my parents ]
[ Yes, with partner's parents ]
[ Open to it ]
[ Prefer independent ]
[ Definitely not ]
```

**Storage:** `users.living_with_parents_post_marriage` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Massive friction point; best to surface early

---

### F43. Family Involvement in Search
**Field:** `family_involvement_search`  
**Question:** "Family involvement in this search:"

**Buttons:**
```
[ Parents are driving this ]
[ Family knows and supports ]
[ Family will be involved later ]
[ This is my decision alone ]
```

**Storage:** `users.family_involvement_search` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** Signals independence level and pace of process

---

### F44. Siblings
**Field:** `siblings`  
**Question:** "Siblings:"

**Buttons:**
```
[ Only child ]
[ 1 brother ]
[ 1 sister ]
[ Multiple siblings ]
[ Prefer not to say ]
```

**Storage:** `users.siblings` (VARCHAR)  
**Filter Type:** Display Only  
**Why:** Context for family dynamics; inheritance implications

---

## G. LIFESTYLE & HABITS (11 questions)

**Section intro:**
```
Great progress — over halfway done ✓

Let's talk about daily life...
```

---

### G45. Your Diet
**Field:** `diet`  
**Question:** "Your diet:"

**Buttons:**
```
[ Pure vegetarian (no eggs) ]
[ Vegetarian (eggs OK) ]
[ Eggetarian ]
[ Non-vegetarian ]
[ Vegan ]
[ Jain food (no root veg, no onion/garlic) ]
[ Halal only ]
[ No restrictions ]
```

**Storage:** `users.diet` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Shared kitchen = shared diet rules in Indian homes

---

### G46. Partner's Diet Preference
**Field:** `partner_diet_pref`  
**Question:** "Partner's diet:"

**Buttons:**
```
[ Must match mine ]
[ Prefer similar ]
[ Vegetarian preferred ]
[ Non-veg OK ]
[ Don't care ]
```

**Storage:** `preferences.partner_diet_pref` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Two-way diet filter; veg families won't accept non-veg

---

### G47. Smoking
**Field:** `smoking`  
**Question:** "Smoking:"

**Buttons:**
```
[ Never ]
[ Occasionally / Socially ]
[ Regularly ]
[ Trying to quit ]
[ Prefer not to say ]
```

**Storage:** `users.smoking` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Strong dealbreaker for many Indian families

---

### G48. Partner Smoking OK?
**Field:** `smoking_partner_ok`  
**Question:** "Partner smoking:"

**Buttons:**
```
[ Dealbreaker ]
[ Prefer non-smoker ]
[ Don't care ]
```

**Storage:** `preferences.smoking_partner_ok` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Two-way filter

---

### G49. Alcohol
**Field:** `drinking`  
**Question:** "Alcohol:"

**Buttons:**
```
[ Never ]
[ Socially / Occasionally ]
[ Regularly ]
[ Prefer not to say ]
```

**Storage:** `users.drinking` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Cultural + religious sensitivity

---

### G50. Partner Drinking OK?
**Field:** `drinking_partner_ok`  
**Question:** "Partner drinking:"

**Buttons:**
```
[ Dealbreaker ]
[ Prefer non-drinker ]
[ Don't care ]
```

**Storage:** `preferences.drinking_partner_ok` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Two-way filter

---

### G51. Exercise / Fitness
**Field:** `fitness_frequency`  
**Question:** "Exercise / fitness:"

**Buttons:**
```
[ Daily (gym, yoga, sports) ]
[ Few times a week ]
[ Occasionally ]
[ Rarely / Never ]
```

**Storage:** `personality.fitness_frequency` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Lifestyle compatibility signal

---

### G52. Social Energy
**Field:** `social_style`  
**Question:** "Social energy:"

**Buttons:**
```
[ Very outgoing — love big gatherings ]
[ Social but balanced ]
[ Prefer small groups ]
[ Homebody — love staying in ]
```

**Storage:** `personality.social_style` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Introvert-extrovert mismatch = daily friction

---

### G53. Weekend Style
**Field:** `weekend_style`  
**Question:** "Weekends are for:"

**Buttons:**
```
[ Going out (restaurants, travel, events) ]
[ Mix of both ]
[ Staying in (family, hobbies, rest) ]
[ Working / side hustle ]
[ Religious / community activities ]
```

**Storage:** `personality.weekend_style` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Practical lifestyle alignment

---

### G54. Pets
**Field:** `pet_ownership`  
**Question:** "Pets:"

**Buttons:**
```
[ Have pets (dogs) ]
[ Have pets (cats) ]
[ Have pets (other) ]
[ No pets, want one ]
[ No pets, don't want one ]
[ Allergic ]
```

**Storage:** `users.pet_ownership` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** Pet allergies/aversion = real incompatibility

---

### G55. Sleep Schedule
**Field:** `sleep_schedule`  
**Question:** "Your schedule:"

**Buttons:**
```
[ Early bird (up before 6am) ]
[ Standard (7-8am) ]
[ Night owl (up past midnight) ]
[ Shift worker / irregular ]
```

**Storage:** `personality.sleep_schedule` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Different sleep schedules = less couple time

---

## H. PARTNER PREFERENCES (9 questions)

**Section intro:**
```
Almost done with the quick questions — just a few more about what you're looking for...
```

---

### H56. Partner Age Range
**Field:** `pref_age_range`  
**Question (two-step process):**

**Step 1:**
```
Partner age range:

Youngest age OK:
```
**Buttons (dynamic, based on user's age):**
```
[ 22 ] [ 24 ] [ 26 ] [ 28 ] [ 30 ]
[ 32 ] [ 34 ] [ 36 ] [ 38 ] [ 40+ ]
```

**Step 2:**
```
Oldest age OK:
```
**Buttons (dynamic):**
```
[ 28 ] [ 30 ] [ 32 ] [ 34 ] [ 36 ]
[ 38 ] [ 40 ] [ 42 ] [ 45 ] [ 50+ ]
```

**Storage:** `preferences.pref_age_range` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Age gap expectations; cultural norms around this

---

### H57. Partner Height
**Field:** `pref_height`  
**Question:** "Partner height:"

**Buttons:**
```
[ Shorter than me ]
[ Similar to me (±5cm) ]
[ Taller than me ]
[ No preference ]
```

**Storage:** `preferences.pref_height` (JSONB)  
**Filter Type:** Soft Filter  
**Why:** Physical preference

---

### H58. Partner Complexion
**Field:** `pref_complexion`  
**Question:** "Partner complexion:"

**Buttons:**
```
[ Fair preferred ]
[ No preference ]
[ Prefer not to answer ]
```

**Storage:** `preferences.pref_complexion` (JSONB)  
**Filter Type:** Soft Filter  
**Why:** Real filter; limited options to discourage colorism

---

### H59. Partner Education (Minimum)
**Field:** `pref_education_min`  
**Question:** "Partner education (minimum):"

**Buttons:**
```
[ Any education ]
[ Graduate (Bachelor's) ]
[ Postgraduate (Master's+) ]
[ Professional degree (CA/MBBS/LLB) ]
[ No preference ]
```

**Storage:** `preferences.pref_education_min` (JSONB)  
**Filter Type:** Soft Filter  
**Why:** Education match expectation

---

### H60. Partner Income Expectation
**Field:** `pref_income_range`  
**Question:** "Partner income expectation:"

**IF India:**
```
[ Below ₹5L ]
[ ₹5-10L ]
[ ₹10-20L ]
[ ₹20-40L ]
[ ₹40L+ ]
[ ₹1Cr+ ]
[ Doesn't matter ]
```

**Storage:** `preferences.pref_income_range` (JSONB)  
**Filter Type:** Soft Filter  
**Why:** Financial expectation alignment

---

### H61. Partner Marital History OK?
**Field:** `pref_marital_status`  
**Question:** "Partner marital history OK?"

**Buttons:**
```
[ Never married only ]
[ Divorced OK ]
[ Widowed OK ]
[ Any ]
[ Depends on situation ]
```

**Storage:** `preferences.pref_marital_status` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Strong filter in Indian market

---

### H62. Partner Having Children OK?
**Field:** `pref_children_ok`  
**Question:** "Partner having existing children?"

**Buttons:**
```
[ OK ]
[ Depends ]
[ Prefer not ]
[ Dealbreaker ]
```

**Storage:** `preferences.pref_children_ok` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Tied to marital history

---

### H63. Partner with Disability OK?
**Field:** `pref_disability_ok`  
**Question:** "Partner with disability?"

**Buttons:**
```
[ Yes, open to it ]
[ Depends on type ]
[ Prefer not ]
[ No ]
```

**Storage:** `preferences.pref_disability_ok` (JSONB)  
**Filter Type:** Hard Filter  
**Why:** Honest preference capture

---

### H64. Want a Working Partner?
**Field:** `pref_working_spouse`  
**Question:** "Want a working partner?"

**Buttons:**
```
[ Yes, must work ]
[ Prefer working ]
[ Open to either ]
[ Prefer homemaker ]
[ No preference ]
```

**Storage:** `preferences.pref_working_spouse` (JSONB)  
**Filter Type:** Soft Filter  
**Why:** Dual-income vs single-income household

---

## I. VALUES & RELATIONSHIP STYLE (8 questions)

**Section intro:**
```
Final stretch — last few questions about values...
```

---

### I65. Relationship Intent
**Field:** `relationship_intent`  
**Question:** "What are you looking for?"

**Buttons:**
```
[ Marriage — ready now ]
[ Marriage — in 6-12 months ]
[ Marriage — in 1-2 years ]
[ Long-term committed relationship ]
[ Open to see where it goes ]
```

**Storage:** `users.relationship_intent` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Timeline alignment prevents wasted time

---

### I66. Want Children?
**Field:** `children_intent`  
**Question:** "Want children?"

**Buttons:**
```
[ Yes, definitely ]
[ Probably yes ]
[ Open to it ]
[ Probably not ]
[ Definitely not ]
```

**Storage:** `users.children_intent` (VARCHAR, indexed)  
**Filter Type:** Hard Filter  
**Why:** Non-negotiable life decision

---

### I67. Children Timeline ⚠️ CONDITIONAL
**Field:** `children_timeline`  
**Shows ONLY if:** `children_intent ≠ "Definitely not"`

**Question:** "Children timeline:"

**Buttons:**
```
[ Soon after marriage ]
[ 1-2 years ]
[ 3-5 years ]
[ No rush ]
```

**Storage:** `users.children_timeline` (VARCHAR)  
**Filter Type:** Algo Weight  
**Why:** Aligned expectations

---

### I68. Household Responsibilities
**Field:** `gender_roles_household`  
**Question:** "Household responsibilities:"

**Buttons:**
```
[ Should be shared equally ]
[ Mostly wife's domain ]
[ Mostly husband's domain ]
[ Hire help, don't stress ]
[ Flexible — figure it out together ]
```

**Storage:** `personality.gender_roles_household` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Modern vs traditional expectation; daily life friction

---

### I69. Money in Marriage
**Field:** `financial_management`  
**Question:** "Money in marriage:"

**Buttons:**
```
[ Joint accounts, full transparency ]
[ Partially joint, some independence ]
[ Completely separate finances ]
[ Haven't thought about it ]
```

**Storage:** `personality.financial_management` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Financial compatibility signal

---

### I70. Political Leaning
**Field:** `political_leaning`  
**Question:** "Political leaning:"

**Buttons:**
```
[ Very conservative ]
[ Center-right ]
[ Centrist / moderate ]
[ Center-left ]
[ Very liberal / progressive ]
[ Apolitical ]
```

**Storage:** `personality.political_leaning` (JSONB)  
**Filter Type:** Algo Weight  
**Why:** Increasingly relevant; affects worldview

---

### I71. Importance of Kundli / Astrology
**Field:** `astrology_belief`  
**Question:** "Importance of kundli / astrology:"

**Buttons:**
```
[ Very important — must match ]
[ Somewhat important ]
[ Don't believe but family does ]
[ Not important at all ]
```

**Storage:** `users.astrology_belief` (VARCHAR)  
**Filter Type:** Soft Filter  
**Why:** India-specific; families block matches over kundli

---

### I72. Open to Inter-faith or Inter-caste?
**Field:** `interfaith_intercaste_openness`  
**Question:** "Open to inter-faith or inter-caste marriage?"

**Buttons:**
```
[ Yes, fully open ]
[ Open but family may resist ]
[ Prefer within community ]
[ Not open ]
```

**Storage:** `users.interfaith_intercaste_openness` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Cross-validates religion & caste filters

---

## J. HARD DEALBREAKER CHECKBOXES (5 questions)
*[Binary yes/no — eliminates matches instantly]*

**Section intro:**
```
Last 5 questions — quick yes/no dealbreakers...
```

---

### J73. OK with Divorced Partner?
**Field:** `db_divorced_ok`  
**Question:** "OK with divorced partner?"

**Buttons:**
```
[ Yes ] [ No ]
```

**Storage:** `preferences.db_divorced_ok` (BOOLEAN)  
**Filter Type:** Hard Filter  
**Why:** Binary dealbreaker

---

### J74. OK with Widowed Partner?
**Field:** `db_widowed_ok`  
**Question:** "OK with widowed partner?"

**Buttons:**
```
[ Yes ] [ No ]
```

**Storage:** `preferences.db_widowed_ok` (BOOLEAN)  
**Filter Type:** Hard Filter  
**Why:** Binary dealbreaker

---

### J75. OK with Partner Who Has Children?
**Field:** `db_children_ok`  
**Question:** "OK with partner who has children?"

**Buttons:**
```
[ Yes ] [ No ]
```

**Storage:** `preferences.db_children_ok` (BOOLEAN)  
**Filter Type:** Hard Filter  
**Why:** Binary dealbreaker

---

### J76. OK with NRI Partner?
**Field:** `db_nri_ok`  
**Question:** "OK with NRI partner?"

**Buttons:**
```
[ Yes ]
[ No ]
[ Prefer NRI ]
```

**Storage:** `preferences.db_nri_ok` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Geography dealbreaker

---

### J77. Maximum Age Gap Acceptable
**Field:** `db_age_gap_max`  
**Question:** "Maximum age gap acceptable:"

**Buttons:**
```
[ ±2 years ]
[ ±5 years ]
[ ±8 years ]
[ ±10+ years ]
[ No limit ]
```

**Storage:** `preferences.db_age_gap_max` (VARCHAR)  
**Filter Type:** Hard Filter  
**Why:** Enforced ceiling

---

## 📸 PHOTO UPLOAD

**Transition message:**
```
That's all 77 questions done — amazing work ✓

One last thing before we switch to conversation mode...
```

---

**Photo prompt:**
```
I need at least one recent photo of you.

It stays private — only shared when I introduce you to a match, and only with your approval.

Send me a clear photo where your face is visible 📸
```

**Input:** Photo message

**After upload:**
```
Great photo ✓ Want to add more? Better photos = better first impressions.
```

**Buttons:**
```
[ Add another photo ] [ That's enough ]
```

---

## ✅ COMPLETION SUMMARY

```
Here's a quick snapshot:

{name}, {age} · {city}, {country}
{religion} ({practice_level}) · Looking for {intent}
{orientation} · Partner age: {age_min}-{age_max}
{marital_status} · {children_intent}

If anything looks off, just tell me later in chat and I'll fix it instantly.
```

**Button:** `[ Looks good → ]`

---

## 🎯 TRANSITION TO CONVERSATIONAL MODE

**This is the MOST IMPORTANT message — the bridge from form-mode to relationship-mode**

```
You're in ✓

I now know your basics and your filters. That's about 30% of what I need to find you someone great.

Here's what happens next:

The quick-tap stuff tells me who to filter OUT.
The conversation tells me who to filter IN.

Starting now, I'll ask you real questions — the kind a good friend would ask if they were setting you up. Answer in your own words, whenever you feel like it.

There's no rush. The more I understand you, the better your first introduction will be.

Ready for the first one?
```

**Buttons:**
```
[ Ask me something → ] [ I'll come back later ]
```

---

## 🗣️ CONVERSATIONAL MODE BEGINS

*[LLM-driven from here — leveraging conversational state controller]*

**If user taps "Ask me something":**

### First LLM Question (example)
```
Okay {name}, here's one I love asking —

Describe your ideal Saturday. Not the Instagram version — the real one. What does a genuinely great day off look like for you?
```

**Input:** Free-form text reply (no buttons)

**From here:** All subsequent interactions are LLM-driven conversational depth-building.

---

## 📊 FLOW SUMMARY

| Section | Fields | Screens | Time | Conditional Questions |
|---------|--------|---------|------|----------------------|
| Intro | 0 | 7 | 2-3 min | — |
| A. Identity & Basics | 9 | 8-9 | 2 min | A5 (if divorced/widowed) |
| B. Location & Mobility | 8 | 5-8 | 2 min | B11, B12, B17 (NRI vs India) |
| C. Religion & Culture | 10 | 6-10 | 3 min | C21 (by religion), C22-24, C27 (Hindu/Jain/Sikh) |
| D. Education & Career | 5 | 5 | 2 min | — |
| E. Financial (Private) | 5 | 5-6 | 1 min | E34 (if NRI) |
| F. Family Background | 7 | 7 | 2 min | — |
| G. Lifestyle & Habits | 11 | 11 | 3 min | — |
| H. Partner Preferences | 9 | 9 | 2 min | — |
| I. Values & Style | 8 | 7-8 | 2 min | I67 (if wants children) |
| J. Dealbreaker Checks | 5 | 5 | 1 min | — |
| Photo Upload | 1 | 3 | 1 min | — |
| **TOTAL** | **77** | **71-77** | **12-15min** | **6-10 conditional** |

---

## 🔀 CONDITIONAL LOGIC SUMMARY

| Path | Questions | Notes |
|------|-----------|-------|
| Standard Indian (Hindu, never married) | 75 | Base + State + Caste flow + Manglik |
| NRI Hindu (never married, abroad) | 75 | Base + Country + Currency + Caste + Manglik |
| Muslim (never married, India) | 71 | Base + State + Sect (NO caste questions) |
| Divorced Hindu (India, has children) | 76 | Base + Children existing + Caste + Manglik |
| Christian NRI (never married) | 73 | Base + Country + Currency + Sect |
| Atheist (never married, India) | 71 | Base + State (no religion-specific Qs) |

**Minimum path:** 71 questions  
**Maximum path:** 77 questions

---

## ⚙️ TECHNICAL IMPLEMENTATION NOTES

### 1. Conditional Branching Logic
- **A5** shows if `A4 ≠ "Never married"`
- **B11** shows if `B10 ≠ "Indian citizen (in India)"`
- **B12** shows if `B10 = "Indian citizen (in India)"`
- **B17** shows if `B10 = "NRI" OR "OCI / PIO"`
- **C21** dropdown changes based on `C18` religion
- **C22-C24, C27** show only for Hindu/Jain/Sikh/Buddhist
- **E34** shows if `B10 ≠ "Indian citizen (in India)"`
- **I67** shows if `I66 ≠ "Definitely not"`

### 2. Two-Way Filtering Pairs
- A1 (Your gender) ↔ A2 (Looking for gender)
- C18 (Your religion) ↔ C20 (Partner religion pref)
- G45 (Your diet) ↔ G46 (Partner diet pref)
- G47 (Smoking) ↔ G48 (Partner smoking OK)
- G49 (Drinking) ↔ G50 (Partner drinking OK)
- A4 (Marital status) ↔ H61 (Partner marital history OK)
- A5 (Children existing) ↔ H62 (Partner children OK)

### 3. Hard Filters (Binary Yes/No Elimination)
All questions in Section J (J73-J77)  
Plus: A1, A2, A3, A4, G45-G50, I65, I66, C18-C20, B15-B16

### 4. Private Fields (🔒 Never Shown to Matches)
All Section E (E33-E37)

### 5. Storage Types
- `users.*` = Direct columns (indexed hard filters)
- `preferences.*` = JSONB (user preferences for matching)
- `personality.*` = JSONB (algo weight signals)

---

**End of Flow Document**

---

*Next: Implementation Checklist for Blitz*
