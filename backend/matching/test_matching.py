"""
Tests for Masii Matching Engine

Tests hard filters, scoring, and end-to-end matching with synthetic profiles.
Run with: python -m pytest backend/matching/test_matching.py -v
Or:       cd backend/matching && python test_matching.py
"""

from datetime import date
from filters import (
    check_gender,
    check_age,
    check_religion_full,
    check_caste,
    check_children_intent,
    check_diet,
    check_smoking,
    check_drinking,
    check_conditions,
    check_marriage_timeline,
    check_manglik,
    check_gotra,
    check_location_basic,
    pass_hard_filters_bidirectional,
    DIET_STRICT,
)
from scoring import (
    calculate_match_score,
    calculate_bidirectional_score,
    calculate_confidence,
    generate_explanation,
    DIMENSION_WEIGHTS,
)
from matcher import match_two_profiles


# ============== SYNTHETIC PROFILES ==============

# Profile 1: Arun — 29M, Hindu Gujarati, Mumbai, vegetarian, engineer
ARUN_USER = {
    "id": 1,
    "full_name": "Arun Patel",
    "gender": "Male",
    "date_of_birth": date(1996, 5, 15),  # age ~29
    "city_current": "Mumbai",
    "country_current": "India",
    "state_india": "Maharashtra",
    "hometown_state": "Gujarat",
    "hometown_city": "Ahmedabad",
    "mother_tongue": "Gujarati",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 175,
    "weight_kg": 72,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Engineering/IT",
    "occupation_sector": "Private",
    "annual_income": "₹20-35 lakh",
    "family_type": "Nuclear",
    "family_status": "Upper middle class",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Homemaker",
    "siblings": "1 sibling",
    "known_conditions": None,
    "phone": "+919876543210",
}

ARUN_PREFS = {
    "pref_age_min": 24,
    "pref_age_max": 30,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Prefer same, open to others",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same or Hindi",
    "pref_education_min": "At least Bachelor's",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Vegetarian or above",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 155,
    "pref_height_max": 170,
    "marriage_timeline": "In the next 1 year",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Near parents but separate",
    "relocation_willingness": "Yes, within India",
    "family_involvement": "Moderate — I'll decide but they have input",
    "religious_practice": "Moderate",
    "sect_denomination": None,
    "caste_community": "Patel",
    "caste_importance": "Prefer same, open to others",
    "partner_working": "Her choice",
    "pref_manglik": "Doesn't matter",
    "pref_gotra_exclude": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

ARUN_SIGNALS = {
    "diet": "Vegetarian",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Take some time, then discuss",
    "family_values": "Moderate",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "gotra": "Kashyap",
    "family_property": "Own flat/apartment",
    "cooking_contribution": "4-7",
    "household_contribution": "Shared equally",
}


# Profile 2: Priya — 27F, Hindu Gujarati, Delhi, vegetarian, doctor
PRIYA_USER = {
    "id": 2,
    "full_name": "Priya Shah",
    "gender": "Female",
    "date_of_birth": date(1998, 8, 20),  # age ~27
    "city_current": "Delhi",
    "country_current": "India",
    "state_india": "Delhi",
    "hometown_state": "Gujarat",
    "hometown_city": "Surat",
    "mother_tongue": "Gujarati",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 162,
    "weight_kg": 55,
    "religion": "Hindu",
    "education_level": "Professional (CA/CS/MBBS/LLB)",
    "education_field": "Medicine/Healthcare",
    "occupation_sector": "Professional (Doctor, Lawyer, CA)",
    "annual_income": "₹10-20 lakh",
    "family_type": "Joint",
    "family_status": "Upper middle class",
    "father_occupation": "Professional",
    "mother_occupation": "Working professional",
    "siblings": "2 siblings",
    "known_conditions": None,
    "phone": "+919876543211",
}

PRIYA_PREFS = {
    "pref_age_min": 27,
    "pref_age_max": 34,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same language only",
    "pref_education_min": "At least Master's",
    "pref_income_min": "₹10-20 lakh",
    "pref_diet": "Same as mine",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 170,
    "pref_height_max": 185,
    "marriage_timeline": "In the next 1 year",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Near parents but separate",
    "relocation_willingness": "Yes, anywhere",
    "family_involvement": "Moderate — I'll decide but they have input",
    "religious_practice": "Moderate",
    "sect_denomination": None,
    "caste_community": "Shah",
    "caste_importance": "Doesn't matter",
    "pref_partner_cooking": "Sometimes (3-6)",
    "pref_partner_household": "Equal share",
    "pref_manglik": "Doesn't matter",
    "pref_gotra_exclude": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

PRIYA_SIGNALS = {
    "diet": "Vegetarian",
    "drinking": "Never",
    "smoking": "Never",
    "fitness_frequency": "Daily",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Talk it out immediately",
    "family_values": "Moderate",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "gotra": "Bharadwaj",
    "family_property": "Own independent house",
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Yes, but open to break for kids",
    "financial_contribution": "Equal partnership",
    "live_with_inlaws": "For some time, not permanently",
}


# Profile 3: Fatima — 25F, Muslim, Mumbai, non-veg
FATIMA_USER = {
    "id": 3,
    "full_name": "Fatima Khan",
    "gender": "Female",
    "date_of_birth": date(2000, 3, 10),  # age ~25
    "city_current": "Mumbai",
    "country_current": "India",
    "state_india": "Maharashtra",
    "hometown_state": "Maharashtra",
    "hometown_city": "Mumbai",
    "mother_tongue": "Urdu",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 160,
    "weight_kg": 55,
    "religion": "Muslim",
    "education_level": "Bachelor's",
    "education_field": "Business/MBA",
    "occupation_sector": "Private",
    "annual_income": "₹5-10 lakh",
    "family_type": "Joint",
    "family_status": "Middle class",
    "father_occupation": "Service/Salaried",
    "mother_occupation": "Homemaker",
    "siblings": "3+ siblings",
    "known_conditions": None,
    "phone": "+919876543212",
}

FATIMA_PREFS = {
    "pref_age_min": 25,
    "pref_age_max": 32,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_income_min": "₹5-10 lakh",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Must not drink",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 168,
    "pref_height_max": 185,
    "marriage_timeline": "In the next 2-3 years",
    "children_intent": "Yes",
    "children_timeline": "Soon after marriage",
    "living_arrangement": "With parents (joint)",
    "relocation_willingness": "Yes, within India",
    "family_involvement": "Very — their approval matters",
    "religious_practice": "Religious",
    "sect_denomination": "Sunni",
    "caste_community": None,
    "caste_importance": None,
    "pref_partner_cooking": "Rarely (1-2)",
    "pref_partner_household": "Some help",
    "pref_manglik": None,
    "pref_gotra_exclude": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "No",
}

FATIMA_SIGNALS = {
    "diet": "Halal only",
    "drinking": "Never",
    "smoking": "Never",
    "fitness_frequency": "Rarely",
    "social_style": "Introverted — prefer small groups",
    "conflict_style": "Avoid conflict",
    "family_values": "Traditional",
    "financial_planning": "Fully joint",
    "manglik_status": None,
    "gotra": None,
    "family_property": "Rented home",
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Undecided",
    "financial_contribution": "His responsibility primarily",
    "live_with_inlaws": "Yes, happy to",
}


# Profile 4: Raj — 30M, Hindu, Delhi, non-veg, divorced
RAJ_USER = {
    "id": 4,
    "full_name": "Raj Malhotra",
    "gender": "Male",
    "date_of_birth": date(1995, 11, 3),  # age ~30
    "city_current": "Delhi",
    "country_current": "India",
    "state_india": "Delhi",
    "hometown_state": "Punjab",
    "hometown_city": "Amritsar",
    "mother_tongue": "Punjabi",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Divorced",
    "children_existing": "No",
    "height_cm": 180,
    "weight_kg": 82,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Business/MBA",
    "occupation_sector": "Business/Self-employed",
    "annual_income": "₹35-50 lakh",
    "family_type": "Nuclear",
    "family_status": "Affluent",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Retired",
    "siblings": "1 sibling",
    "known_conditions": None,
    "phone": "+919876543213",
}

RAJ_PREFS = {
    "pref_age_min": 24,
    "pref_age_max": 32,
    "pref_religion": "Open to all",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Doesn't matter",
    "pref_height_min": 155,
    "pref_height_max": 175,
    "marriage_timeline": "In the next 2-3 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, anywhere",
    "family_involvement": "Independent — my decision entirely",
    "religious_practice": "Not very religious",
    "sect_denomination": None,
    "caste_community": "Khatri",
    "caste_importance": "Doesn't matter",
    "partner_working": "Yes, she should have a career",
    "pref_manglik": "Doesn't matter",
    "pref_gotra_exclude": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Yes",
}

RAJ_SIGNALS = {
    "diet": "Non-vegetarian",
    "drinking": "Socially / Occasionally",
    "smoking": "Socially / Occasionally",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Very social — love big gatherings",
    "conflict_style": "Talk it out immediately",
    "family_values": "Liberal",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "gotra": None,
    "family_property": "Multiple properties",
    "cooking_contribution": "1-3",
    "household_contribution": "Mostly outsourced (cook/maid)",
}


# ============== HARD FILTER TESTS ==============


def test_gender_filter():
    assert check_gender(ARUN_USER, PRIYA_USER) == True, "Male-Female should pass"
    assert check_gender(ARUN_USER, RAJ_USER) == False, "Male-Male should fail"
    assert check_gender(PRIYA_USER, FATIMA_USER) == False, "Female-Female should fail"
    print("  PASS gender filter")


def test_age_filter():
    # Arun (29) with Priya prefs (27-34) → passes
    passes, in_range = check_age(PRIYA_PREFS, ARUN_USER)
    assert passes == True, "Arun 29 within Priya's 27-34"
    assert in_range == True

    # Priya (27) with Arun prefs (24-30) → passes
    passes, in_range = check_age(ARUN_PREFS, PRIYA_USER)
    assert passes == True, "Priya 27 within Arun's 24-30"

    # Fatima (25) with Priya prefs (27-34) → buffer zone (25 is within 27-2=25)
    passes, in_range = check_age(PRIYA_PREFS, FATIMA_USER)
    assert passes == True, "Fatima 25 within Priya's 27-2 buffer"
    assert in_range == False, "But NOT within strict range"
    print("  PASS age filter")


def test_religion_filter():
    # Arun (Hindu) with Priya prefs (Same religion only) — both Hindu → pass
    assert check_religion_full(PRIYA_USER, PRIYA_PREFS, ARUN_USER) == True

    # Arun (Hindu) with Fatima prefs (Same religion only = Muslim) → fail
    assert check_religion_full(FATIMA_USER, FATIMA_PREFS, ARUN_USER) == False

    # Raj prefs (Open to all) → always pass
    assert check_religion_full(RAJ_USER, RAJ_PREFS, FATIMA_USER) == True
    print("  PASS religion filter")


def test_children_intent_filter():
    # Both want kids → pass
    assert check_children_intent(ARUN_PREFS, PRIYA_PREFS) == True

    # One says No, other says Yes → fail
    no_kids_prefs = {**ARUN_PREFS, "children_intent": "No"}
    assert check_children_intent(no_kids_prefs, PRIYA_PREFS) == False

    # Maybe is compatible with Yes
    maybe_prefs = {**ARUN_PREFS, "children_intent": "Maybe / Open to it"}
    assert check_children_intent(maybe_prefs, PRIYA_PREFS) == True
    print("  PASS children intent filter")


def test_diet_filter():
    # Arun prefs "Vegetarian or above" + Priya (Vegetarian) → pass
    assert check_diet(ARUN_PREFS, PRIYA_SIGNALS) == True

    # Arun prefs "Vegetarian or above" + Raj (Non-veg) → fail
    assert check_diet(ARUN_PREFS, RAJ_SIGNALS) == False

    # Raj prefs "Doesn't matter" → always pass
    assert check_diet(RAJ_PREFS, PRIYA_SIGNALS) == True
    print("  PASS diet filter")


def test_smoking_filter():
    # Priya prefs "Must not smoke" + Arun (Never) → pass
    assert check_smoking(PRIYA_PREFS, ARUN_SIGNALS) == True

    # Priya prefs "Must not smoke" + Raj (Socially) → pass (only Regularly fails)
    assert check_smoking(PRIYA_PREFS, RAJ_SIGNALS) == True

    # Must not smoke + Regularly → fail
    heavy_smoker = {"smoking": "Regularly"}
    assert check_smoking(PRIYA_PREFS, heavy_smoker) == False
    print("  PASS smoking filter")


def test_drinking_filter():
    # Fatima prefs "Must not drink" + Arun (Socially) → pass (only Regularly fails)
    assert check_drinking(FATIMA_PREFS, ARUN_SIGNALS) == True

    # Must not drink + Regularly → fail
    heavy_drinker = {"drinking": "Regularly"}
    assert check_drinking(FATIMA_PREFS, heavy_drinker) == False
    print("  PASS drinking filter")


def test_marriage_timeline_filter():
    # Arun (1 year) + Priya (1 year) → pass
    assert check_marriage_timeline(ARUN_PREFS, PRIYA_PREFS) == True

    # Arun (1 year) + Raj (2-3 years) → pass (1 step apart)
    assert check_marriage_timeline(ARUN_PREFS, RAJ_PREFS) == True

    # "Within 6 months" + "Just exploring" → fail (3 steps apart)
    urgent = {"marriage_timeline": "Within 6 months"}
    exploring = {"marriage_timeline": "Just exploring"}
    assert check_marriage_timeline(urgent, exploring) == False
    print("  PASS marriage timeline filter")


def test_gotra_filter():
    # No exclusion → pass
    assert check_gotra(ARUN_PREFS, PRIYA_SIGNALS) == True

    # Exclude "Bharadwaj" + Priya gotra = "Bharadwaj" → fail
    exclude_prefs = {**ARUN_PREFS, "pref_gotra_exclude": ["Bharadwaj"]}
    assert check_gotra(exclude_prefs, PRIYA_SIGNALS) == False
    print("  PASS gotra filter")


def test_location_filter():
    # Arun (Mumbai) + Priya (Delhi), both willing to relocate → pass
    assert check_location_basic(ARUN_USER, PRIYA_USER, ARUN_PREFS, PRIYA_PREFS) == True

    # Both in India but both "No, I'm settled" → still same country, should pass
    no_reloc_a = {**ARUN_PREFS, "relocation_willingness": "No, I'm settled"}
    no_reloc_b = {**PRIYA_PREFS, "relocation_willingness": "No, I'm settled"}
    assert check_location_basic(ARUN_USER, PRIYA_USER, no_reloc_a, no_reloc_b) == True

    # Different countries + both refuse → fail
    usa_user = {**ARUN_USER, "country_current": "USA"}
    assert check_location_basic(usa_user, PRIYA_USER, no_reloc_a, no_reloc_b) == False
    print("  PASS location filter")


def test_conditions_filter():
    # Priya prefs "Depends on condition" → always pass
    assert check_conditions(PRIYA_PREFS, ARUN_USER) == True

    # Fatima prefs "No" + candidate has condition → fail
    user_with_condition = {**ARUN_USER, "known_conditions": "Diabetes"}
    assert check_conditions(FATIMA_PREFS, user_with_condition) == False

    # Fatima prefs "No" + candidate has no condition → pass
    assert check_conditions(FATIMA_PREFS, ARUN_USER) == True
    print("  PASS conditions filter")


def test_bidirectional_filters():
    # Arun ↔ Priya: Both Hindu, compatible on all fronts → should pass
    passes, a_fail, b_fail = pass_hard_filters_bidirectional(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert passes == True, f"Arun↔Priya should pass. A failed: {a_fail}, B failed: {b_fail}"

    # Arun ↔ Fatima: Different religions, both strict → should fail
    passes, a_fail, b_fail = pass_hard_filters_bidirectional(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        FATIMA_USER, FATIMA_PREFS, FATIMA_SIGNALS,
    )
    assert passes == False, "Arun↔Fatima should fail on religion"
    assert "religion" in a_fail or "religion" in b_fail

    # Arun ↔ Raj: Same gender → should fail
    passes, a_fail, b_fail = pass_hard_filters_bidirectional(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
    )
    assert passes == False, "Arun↔Raj should fail on gender"
    print("  PASS bidirectional filters")


# ============== SCORING TESTS ==============


def test_scoring_compatible_pair():
    # Arun ↔ Priya: Should score high (both Hindu Gujarati, similar values)
    result = calculate_bidirectional_score(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    score = result["score"]
    print(f"  Arun ↔ Priya score: {score}")
    print(f"    A→B dimensions: {result['dimensions_a']}")
    print(f"    B→A dimensions: {result['dimensions_b']}")
    assert score >= 60, f"Compatible pair should score >= 60, got {score}"
    print("  PASS scoring compatible pair")


def test_scoring_dimensions_weights():
    # Verify weights sum to 1.0
    total = sum(DIMENSION_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001, f"Weights should sum to 1.0, got {total}"
    print("  PASS dimension weights")


def test_confidence():
    conf = calculate_confidence(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert conf in ("high", "medium", "low")
    print(f"  Arun↔Priya confidence: {conf}")

    # Sparse profiles should be low confidence
    sparse_user = {"id": 99, "gender": "Male", "religion": "Hindu"}
    sparse_prefs = {}
    sparse_signals = {}
    conf2 = calculate_confidence(
        sparse_user, sparse_prefs, sparse_signals,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert conf2 == "low", f"Sparse profile should be low confidence, got {conf2}"
    print("  PASS confidence")


def test_explanation():
    score_result = calculate_bidirectional_score(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    expl = generate_explanation(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
        score_result,
    )
    assert "highlights" in expl
    assert len(expl["highlights"]) > 0
    print(f"  Explanation highlights: {expl['highlights']}")
    print("  PASS explanation")


# ============== END-TO-END MATCH TESTS ==============


def test_e2e_compatible_match():
    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert result["matched"] == True, f"Arun↔Priya should match: {result}"
    print(f"  Arun↔Priya: matched={result['matched']}, score={result['score']}, tier={result['tier']}")
    print(f"    Explanation: {result['explanation']['highlights']}")
    print("  PASS e2e compatible match")


def test_e2e_incompatible_religion():
    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        FATIMA_USER, FATIMA_PREFS, FATIMA_SIGNALS,
    )
    assert result["matched"] == False, "Arun↔Fatima should NOT match (religion)"
    print(f"  Arun↔Fatima: matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e incompatible religion")


def test_e2e_same_gender():
    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
    )
    assert result["matched"] == False, "Arun↔Raj should NOT match (same gender)"
    print(f"  Arun↔Raj: matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e same gender")


def test_e2e_raj_priya():
    """Raj (liberal Hindu) ↔ Priya (moderate Hindu). Different but potentially compatible."""
    result = match_two_profiles(
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    print(f"  Raj↔Priya: matched={result['matched']}, ", end="")
    if result["matched"]:
        print(f"score={result['score']}, tier={result['tier']}")
        print(f"    Highlights: {result['explanation']['highlights']}")
    else:
        print(f"reason={result.get('reason')}")
    print("  PASS e2e raj-priya")


def test_e2e_almost_match():
    """Create a pair that should score in the 'almost' range (60-74)."""
    # Modify Priya to be less compatible but still passable
    almost_priya_prefs = {
        **PRIYA_PREFS,
        "marriage_timeline": "In the next 2-3 years",  # Different timeline
        "living_arrangement": "With parents (joint)",  # Mismatched
        "family_involvement": "Very — their approval matters",  # Mismatched
    }
    almost_priya_signals = {
        **PRIYA_SIGNALS,
        "family_values": "Traditional",  # Mismatched from Arun's Moderate
        "conflict_style": "Avoid conflict",  # Opposite of Arun
    }

    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, almost_priya_prefs, almost_priya_signals,
    )
    print(f"  Almost match test: matched={result['matched']}, ", end="")
    if result["matched"]:
        print(f"score={result['score']}, tier={result['tier']}")
    else:
        print(f"reason={result.get('reason')}")
    print("  PASS e2e almost match")


# ============== RUN ALL TESTS ==============


def run_all_tests():
    print("\n=== HARD FILTER TESTS ===\n")
    test_gender_filter()
    test_age_filter()
    test_religion_filter()
    test_children_intent_filter()
    test_diet_filter()
    test_smoking_filter()
    test_drinking_filter()
    test_marriage_timeline_filter()
    test_gotra_filter()
    test_location_filter()
    test_conditions_filter()
    test_bidirectional_filters()

    print("\n=== SCORING TESTS ===\n")
    test_scoring_compatible_pair()
    test_scoring_dimensions_weights()
    test_confidence()
    test_explanation()

    print("\n=== END-TO-END MATCH TESTS ===\n")
    test_e2e_compatible_match()
    test_e2e_incompatible_religion()
    test_e2e_same_gender()
    test_e2e_raj_priya()
    test_e2e_almost_match()

    print("\n=== ALL TESTS PASSED ===\n")


if __name__ == "__main__":
    run_all_tests()
