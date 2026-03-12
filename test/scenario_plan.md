# Masii Matchmaking Flow — 100 Scenario Execution Plan

To fully stress-test the Masii v3 branching logic, soft-scoring, and hard gates, we will generate **100 unique test personas**. Instead of hand-coding 100 random people, we will structure them across **5 distinct matchmaking pools** (20 personas each). This ensures we test everything from hyper-niche conservative filters to broad, progressive NRI combinations.

---

## 1. The 5 Matchmaking Pools (100 Scenarios)

### Pool 1: The NRI / High-Income Diaspora (20 Scenarios)
*Focus: Currency matching, cross-border relocation, high education gates.*
- **Locations:** USA, UK, Canada, Australia, UAE, Singapore, Germany.
- **Income/Education:** Master's/PhD, Tier 7-9 currency brackets (e.g., $150K+, £120K+, SGD 250K+).
- **Preferences:** 
  - Often open to caste ("Doesn't matter" or "Same community, any caste").
  - Strict on partner's education (Must be Master's or Professional).
  - Open to relocation but usually within Western/Gulf markets.
- **Goal:** Tests the `getIncomeBrackets` currency logic, cross-currency tier equivalence, and multi-select location arrays.

### Pool 2: Tier-1 Metro Tech & Corporate (20 Scenarios)
*Focus: Progressive lifestyle, high INR income, DINKs, modern household dynamics.*
- **Locations:** Bangalore (Karnataka), Mumbai (Maharashtra), Delhi NCR, Gurgaon (Haryana).
- **Background:** Raised in India, living in India.
- **Lifestyle:** Non-veg or Eggetarian, Drinks occasionally/socially. 
- **Preferences:**
  - `pref_caste`: "Open to all" or "Doesn't matter".
  - `pref_children_timeline`: "Not sure" or "No children".
  - Household expectations: Equal split, modern career-first focus.
- **Goal:** Tests modern preference skipping, DINK matching, and open-caste matching.

### Pool 3: Regional & Linguistic Traditionalists (20 Scenarios)
*Focus: State-contextualized caste lists, strict language gates, same-state relocation.*
- **Locations:** Deep splits across Tamil Nadu, Andhra Pradesh, Gujarat, Maharashtra, MP.
- **Demographics:** Tamil/Telugu/Gujarati/Marathi mother tongues.
- **Preferences:**
  - `pref_mother_tongue`: "Same language only".
  - `pref_caste`: "Same caste only" (e.g., strictly Iyer, strictly Kamma, strictly Patel).
  - `pref_current_location`: "Same state as me".
- **Goal:** Tests the `raised_in_state` driven dynamic caste dropdowns (e.g., prioritizing Nadar/Thevar in TN) and language constraints.

### Pool 4: Swayamwar & Deeply Conservative (20 Scenarios)
*Focus: Extreme hard gates, strict diets, strict religious practice, traditional roles.*
- **Religions/Sects:** Strict Jains, Amritdhari Sikhs, Very Religious Muslims, Orthodox Hindus.
- **Lifestyle:** Strictly Veg / Jain / Halal only. Teetotalers.
- **Preferences:**
  - `pref_religion`: "Same religion only" + specific practice level required (e.g., "Very religious").
  - Gender roles: Traditional financial and household contributions.
  - `marriage_timeline`: "As soon as possible" / "Within 6 months".
- **Goal:** Tests the heaviest exclusion logic. Most of these personas will reject 95% of the database, ensuring our negative-match filters work perfectly.

### Pool 5: "Second Innings" & Progressive Open (20 Scenarios)
*Focus: Skip logic for divorce, older age brackets, mixed families.*
- **Marital Status:** "Divorced", "Awaiting divorce", "Widowed".
- **Age:** Late 30s to early 50s.
- **Preferences:**
  - `children_existing`: Mix of Yes (living with) and Yes (not living with).
  - `pref_marital_status`: Open to Divorced/Widowed.
  - `pref_children_existing`: "Yes".
  - Religion & Caste: Almost always "Doesn't matter".
- **Goal:** Tests the nested `children_existing` skip logic that is completely bypassed in the other pools, and ensures older/divorced cohorts don't accidentally match with strictly "Never married" traditionalists.

---

## 2. Technical Execution Plan

### Step 1: The Persona Generator Script
Instead of writing 100 JSON files by hand, we will create a Node.js script (`test/generate_personas.js`).
- The script will define 5 "factory functions"—one for each pool.
- Each factory will randomly draw from predefined sub-arrays (e.g., `const nriCountries = ['USA', 'UK', 'Germany']`) to generate 20 valid, complete `answers` objects that map exactly to the YAML keys.
- Output: `test/fixtures/100_personas.json`.

### Step 2: Validating Against the Flow (The Journey)
We will write a test runner (`test/validate_flow.js`) that imports `form-config.generated.js`.
- It will loop through all 100 personas.
- For each persona, it calls `getQuestionFlow(persona)`.
- **Validation:** It asserts that the persona's answers don't violate `shouldSkip` rules, and that selected options actually exist in the dynamic arrays resolved by `resolveOptions()`.

### Step 3: The Simulation Matrix (Running them against the tree)
We will create `test/simulate_matches.js`.
- It compares every persona against every other persona (10,000 combinations).
- It runs the Hard Gate logic (Gender opposite? Caste exclusion triggered? Marital status accepted?).
- It runs the Soft Scoring logic (BMI, religious practice proximity, income tier equivalence).
- **Output:** A CSV or JSON report showing exact match rates. For example, we should see Pool 4 (Conservative) having a < 2% match rate across the board, while Pool 2 matches well with Pool 1.

## Next Action
Once you approve this matrix strategy, I will switch to Execution mode. I will write the Node.js generator script to construct the 100 personas using the exact keys and allowed values from your `masii-reference-data.yaml` and `masii-questions.yaml`.
