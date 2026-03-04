"""
Hard Filters — Stage 1 of Masii Matching (v2)

Binary pass/fail elimination. If any filter fails, the pair is impossible.
Both directions (A→B and B→A) must pass for a match to proceed.

v2 gates: gender, age, religion, caste, marital_status, children_existing,
children_intent, diet, smoking, drinking, conditions, marriage_timeline,
manglik, current_location, raised_in, mother_tongue, height, disability.
"""

from datetime import date
from typing import Dict, List, Optional, Tuple

# Education levels ordered for comparison
EDUCATION_RANK = {
    "High school": 1,
    "Diploma": 2,
    "Bachelor's": 3,
    "Master's": 4,
    "Professional (CA/CS/MBBS/LLB)": 5,
    "Doctorate": 6,
}

# Income brackets ordered for comparison (INR)
INCOME_RANK = {
    "Below ₹5 lakh": 1,
    "₹5-10 lakh": 2,
    "₹10-20 lakh": 3,
    "₹20-35 lakh": 4,
    "₹35-50 lakh": 5,
    "₹50-75 lakh": 6,
    "₹75 lakh - ₹1 crore": 7,
    "₹1-2 crore": 8,
    "₹2 crore+": 9,
    # NRI brackets
    "Below $30,000": 1,
    "$30,000-60,000": 2,
    "$60,000-100,000": 3,
    "$100,000-150,000": 5,
    "$150,000-250,000": 7,
    "$250,000+": 9,
    "Prefer not to say": 0,
}

# Marriage timeline — v2 option names
TIMELINE_RANK = {
    "Within 1 year": 1,
    "1-2 years": 2,
    "2-3 years": 3,
    "Just exploring": 4,
}

# Diet strictness hierarchy — v2 universal options
DIET_STRICT = {
    "Jain": 1,
    "Vegan": 2,
    "Veg": 3,
    "Eggetarian": 4,
    "Occasionally non-veg": 5,
    "Non-veg": 6,
    "Other": 6,
}


def calculate_age(dob: date) -> int:
    """Calculate age from date of birth."""
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def check_gender(user: Dict, candidate: Dict) -> bool:
    """Both must be opposite gender. Male seeks Female, Female seeks Male."""
    ug = user.get("gender")
    cg = candidate.get("gender")
    if not ug or not cg:
        return False
    return ug != cg


def check_age(user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: Strict range check. In range = pass, out of range = fail. No buffer.
    """
    dob = candidate.get("date_of_birth")
    pref_min = user_prefs.get("pref_age_min")
    pref_max = user_prefs.get("pref_age_max")

    if not dob:
        return True  # No data = pass (can't filter)

    age = calculate_age(dob) if isinstance(dob, date) else None
    if age is None:
        return True

    if pref_min is None and pref_max is None:
        return True  # No preference = pass

    min_age = int(pref_min) if pref_min else 18
    max_age = int(pref_max) if pref_max else 60

    return min_age <= age <= max_age


def check_religion_full(user: Dict, user_prefs: Dict, candidate: Dict) -> bool:
    """Full religion check using both user profile and prefs."""
    pref = user_prefs.get("pref_religion")
    candidate_religion = candidate.get("religion")

    if not pref or not candidate_religion:
        return True

    if pref == "Open to all":
        return True

    if pref == "Same religion only":
        return user.get("religion") == candidate_religion

    if pref == "Open, but not...":
        exclude = user_prefs.get("pref_religion_exclude") or []
        if isinstance(exclude, str):
            exclude = [exclude]
        return candidate_religion not in exclude

    return True


def check_caste(user_prefs: Dict, candidate_prefs: Dict) -> bool:
    """
    Check caste compatibility.
    Only a hard filter if caste_importance = 'Must be same caste'
    AND pref_caste = 'Same caste only'.
    """
    pref_caste = user_prefs.get("pref_caste")
    importance = user_prefs.get("caste_importance")

    if not pref_caste or pref_caste == "Open to all":
        return True

    if pref_caste == "Same caste only" or importance == "Must be same caste":
        user_caste = user_prefs.get("caste_community")
        candidate_caste = candidate_prefs.get("caste_community")
        if user_caste and candidate_caste:
            return user_caste == candidate_caste
        return True  # Missing data = don't eliminate

    if pref_caste == "Open, but not...":
        exclude = user_prefs.get("pref_caste_exclude") or []
        if isinstance(exclude, str):
            exclude = [exclude]
        candidate_caste = candidate_prefs.get("caste_community")
        return candidate_caste not in exclude

    return True


def check_marital_status(user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: pref_marital_status is TEXT[]. Candidate's status must be in list.
    "Any" passes all.
    """
    pref = user_prefs.get("pref_marital_status")
    if not pref:
        return True

    if isinstance(pref, str):
        pref = [pref]

    if "Any" in pref:
        return True

    candidate_status = candidate.get("marital_status")
    if not candidate_status:
        return True  # Missing data = don't eliminate

    return candidate_status in pref


def check_children_existing(user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: pref_children_existing preference.
    "No" + candidate has children = fail.
    "Only if they don't live with them" + "Yes, they live with me" = fail.
    "Yes" passes everyone.
    """
    pref = user_prefs.get("pref_children_existing")
    if not pref or pref == "Yes":
        return True

    candidate_children = candidate.get("children_existing")
    if not candidate_children or candidate_children == "No":
        return True  # No children = always pass

    if pref == "No":
        # Candidate has children (any kind) = fail
        return False

    if pref == "Only if they don't live with them":
        if candidate_children == "Yes, they live with me":
            return False

    return True


def check_children_intent(user_prefs: Dict, candidate_prefs: Dict) -> bool:
    """
    Opposite children intents = hard eliminate.
    'Yes' vs 'No' = eliminate.
    'Maybe / Open to it' is compatible with both.
    """
    user_intent = user_prefs.get("children_intent")
    candidate_intent = candidate_prefs.get("children_intent")

    if not user_intent or not candidate_intent:
        return True

    if user_intent == "No" and candidate_intent == "Yes":
        return False
    if user_intent == "Yes" and candidate_intent == "No":
        return False

    return True


def check_diet(user_prefs: Dict, candidate_signals: Dict) -> bool:
    """
    v2 diet gate with new pref options:
    "Same as mine" = exact match required.
    "Any but not non-veg" = eliminates Non-veg + Occasionally non-veg.
    "Veg" = must be rank <= 3 (Jain, Vegan, Veg).
    "Doesn't matter" = pass.
    """
    pref = user_prefs.get("pref_diet")
    candidate_diet = candidate_signals.get("diet")

    if not pref or pref == "Doesn't matter" or not candidate_diet:
        return True

    if pref == "Veg":
        rank = DIET_STRICT.get(candidate_diet, 6)
        return rank <= 3

    if pref == "Any but not non-veg":
        rank = DIET_STRICT.get(candidate_diet, 6)
        return rank <= 4  # Eliminates Non-veg (6) and Occasionally non-veg (5)

    if pref == "Same as mine":
        user_diet = user_prefs.get("_user_diet")
        if not user_diet:
            return True  # Can't compare without user's own diet
        return user_diet == candidate_diet

    return True


def check_smoking(user_prefs: Dict, candidate_signals: Dict) -> bool:
    """Hard filter: 'Must not smoke' + candidate smokes regularly = eliminate."""
    pref = user_prefs.get("pref_smoking")
    candidate = candidate_signals.get("smoking")

    if not pref or pref == "Doesn't matter" or not candidate:
        return True

    if pref == "Must not smoke" and candidate == "Regularly":
        return False

    return True


def check_drinking(user_prefs: Dict, candidate_signals: Dict) -> bool:
    """Hard filter: 'Must not drink' + candidate drinks regularly = eliminate."""
    pref = user_prefs.get("pref_drinking")
    candidate = candidate_signals.get("drinking")

    if not pref or pref == "Doesn't matter" or not candidate:
        return True

    if pref == "Must not drink" and candidate == "Regularly":
        return False

    return True


def check_conditions(user_prefs: Dict, candidate: Dict) -> bool:
    """Hard filter: pref_conditions = 'No' + candidate has conditions = eliminate."""
    pref = user_prefs.get("pref_conditions")
    candidate_conditions = candidate.get("known_conditions")

    if not pref or pref in ("Yes", "Depends on condition"):
        return True

    if pref == "No" and candidate_conditions and candidate_conditions not in ("None", "No"):
        return False

    return True


def check_marriage_timeline(user_prefs: Dict, candidate_prefs: Dict) -> bool:
    """
    Timelines must overlap (within 1 step).
    'Within 1 year' and 'Just exploring' = no overlap = eliminate.
    """
    user_tl = user_prefs.get("marriage_timeline")
    cand_tl = candidate_prefs.get("marriage_timeline")

    if not user_tl or not cand_tl:
        return True

    u_rank = TIMELINE_RANK.get(user_tl, 2)
    c_rank = TIMELINE_RANK.get(cand_tl, 2)

    return abs(u_rank - c_rank) <= 1


def check_manglik(user_prefs: Dict, candidate_signals: Dict) -> bool:
    """Hard filter: pref_manglik = 'Must match' requires same manglik status."""
    pref = user_prefs.get("pref_manglik")
    if not pref or pref != "Must match":
        return True

    user_manglik = user_prefs.get("_user_manglik")  # Passed by caller
    candidate_manglik = candidate_signals.get("manglik_status")

    if not user_manglik or not candidate_manglik:
        return True

    return user_manglik == candidate_manglik


def check_raised_in(user: Dict, user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: pref_raised_in hard gate.
    "Same country as me" — candidate must have grown up in same country.
    "Same state" — candidate must have grown up in same state.
    "Raised abroad" — candidate's raised_in_country must not be "India".
    "Any state in India" — candidate must have grown up in India.
    "Raised in India is fine too" / "Abroad is fine too" / "Doesn't matter" — pass.
    "Nearby states" — pass (soft, not hard gate).
    """
    pref = user_prefs.get("pref_raised_in")
    if not pref or pref in ("Doesn't matter", "Raised in India is fine too",
                            "Abroad is fine too", "Nearby states"):
        return True

    user_country = user.get("raised_in_country")
    cand_country = candidate.get("raised_in_country")
    user_state = user.get("raised_in_state")
    cand_state = candidate.get("raised_in_state")

    if pref == "Same country as me":
        if not user_country or not cand_country:
            return True
        return user_country == cand_country

    if pref == "Same state":
        if not user_state or not cand_state:
            return True
        return user_state == cand_state

    if pref == "Raised abroad":
        if not cand_country:
            return True
        return cand_country != "India"

    if pref == "Any state in India":
        if not cand_country:
            return True
        return cand_country == "India"

    return True


def check_current_location(user: Dict, user_prefs: Dict, candidate: Dict,
                           candidate_prefs: Dict) -> bool:
    """
    v2: pref_current_location hard gate. Replaces check_location_basic.
    "Same city" — candidate must be in same city.
    "Same state" — candidate must be in same state.
    "Same country" — candidate must be in same country.
    "Specific countries..." — candidate must be in one of the listed countries.
    "Anywhere" / None — falls through to relocation check.
    """
    pref = user_prefs.get("pref_current_location")

    if pref == "Same city as me" or pref == "Same city":
        user_city = (user.get("city_current") or "").lower().strip()
        cand_city = (candidate.get("city_current") or "").lower().strip()
        if not user_city or not cand_city:
            return True
        return user_city == cand_city

    if pref == "Same state as me" or pref == "Same state":
        user_state = (user.get("state_india") or "").lower().strip()
        cand_state = (candidate.get("state_india") or "").lower().strip()
        if not user_state or not cand_state:
            return True
        return user_state == cand_state

    if pref == "Same country as me" or pref == "Same country":
        user_country = (user.get("country_current") or "").lower().strip()
        cand_country = (candidate.get("country_current") or "").lower().strip()
        if not user_country or not cand_country:
            return True
        return user_country == cand_country

    if pref and pref.startswith("Specific countries"):
        countries = user_prefs.get("pref_current_location_countries") or []
        if isinstance(countries, str):
            countries = [countries]
        if not countries:
            return True
        cand_country = candidate.get("country_current")
        if not cand_country:
            return True
        return cand_country in countries

    # "Anywhere" or no pref — fall through to relocation check
    return _check_relocation_fallback(user, user_prefs, candidate, candidate_prefs)


def _check_relocation_fallback(user: Dict, user_prefs: Dict,
                               candidate: Dict, candidate_prefs: Dict) -> bool:
    """
    Legacy relocation-refusal check. Both "No, I'm settled" + different countries = fail.
    Called by check_current_location when pref is null/Anywhere.
    """
    user_country = user.get("country_current")
    cand_country = candidate.get("country_current")

    if not user_country or not cand_country:
        return True

    if user_country == cand_country:
        return True

    user_reloc = user_prefs.get("relocation_willingness", "")
    cand_reloc = candidate_prefs.get("relocation_willingness", "")

    if user_reloc == "No, I'm settled where I am" and cand_reloc == "No, I'm settled where I am":
        return False
    if user_reloc == "No, I'm settled" and cand_reloc == "No, I'm settled":
        return False

    return True


def check_mother_tongue(user: Dict, user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: NOW A HARD GATE.
    "Same language only" = candidate's mother tongue must match user's.
    "Same or Hindi" = candidate must speak user's language or Hindi.
    "Doesn't matter" = pass.
    """
    pref = user_prefs.get("pref_mother_tongue")
    if not pref or pref == "Doesn't matter":
        return True

    user_mt = user.get("mother_tongue")
    cand_mt = candidate.get("mother_tongue")

    if not user_mt or not cand_mt:
        return True

    if pref == "Same language only":
        return user_mt == cand_mt

    if pref == "Same or Hindi":
        if user_mt == cand_mt:
            return True
        # Candidate must speak user's language or Hindi
        cand_langs = set(candidate.get("languages_spoken") or [])
        cand_langs.add(cand_mt)
        if user_mt in cand_langs or "Hindi" in cand_langs:
            return True
        return False

    return True


def check_height(user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: NOW A HARD GATE. pref_height_min/max vs candidate.height_cm. No buffer.
    """
    pref_min = user_prefs.get("pref_height_min")
    pref_max = user_prefs.get("pref_height_max")

    if pref_min is None and pref_max is None:
        return True

    cand_height = candidate.get("height_cm")
    if not cand_height:
        return True  # Missing data = don't eliminate

    if pref_min is not None and cand_height < pref_min:
        return False
    if pref_max is not None and cand_height > pref_max:
        return False

    return True


def check_disability(user_prefs: Dict, candidate: Dict) -> bool:
    """
    v2: pref_disability gate.
    "No" + candidate disability = "Yes" → fail.
    "Depends" / "Yes" → pass.
    """
    pref = user_prefs.get("pref_disability")
    if not pref or pref in ("Yes", "Depends"):
        return True

    candidate_disability = candidate.get("disability")
    if not candidate_disability:
        return True

    if pref == "No" and candidate_disability == "Yes":
        return False

    return True


# ============== MAIN FILTER FUNCTION ==============

def pass_hard_filters(
    user: Dict,
    user_prefs: Dict,
    user_signals: Dict,
    candidate: Dict,
    candidate_prefs: Dict,
    candidate_signals: Dict,
) -> Tuple[bool, list]:
    """
    Run all hard filters for one direction: does `user` accept `candidate`?

    Returns (passes: bool, failed_filters: list of str).
    Both directions must be checked separately by the caller.
    """
    failed = []

    if not check_gender(user, candidate):
        failed.append("gender")

    if not check_age(user_prefs, candidate):
        failed.append("age")

    if not check_religion_full(user, user_prefs, candidate):
        failed.append("religion")

    if not check_caste(user_prefs, candidate_prefs):
        failed.append("caste")

    if not check_marital_status(user_prefs, candidate):
        failed.append("marital_status")

    if not check_children_existing(user_prefs, candidate):
        failed.append("children_existing")

    if not check_children_intent(user_prefs, candidate_prefs):
        failed.append("children_intent")

    # Inject user's own diet for 'Same as mine' comparison
    user_prefs_with_diet = {**user_prefs, "_user_diet": user_signals.get("diet")}
    if not check_diet(user_prefs_with_diet, candidate_signals):
        failed.append("diet")

    if not check_smoking(user_prefs, candidate_signals):
        failed.append("smoking")

    if not check_drinking(user_prefs, candidate_signals):
        failed.append("drinking")

    if not check_conditions(user_prefs, candidate):
        failed.append("conditions")

    if not check_marriage_timeline(user_prefs, candidate_prefs):
        failed.append("marriage_timeline")

    # Inject user's own manglik for 'Must match' comparison
    user_prefs_with_manglik = {**user_prefs, "_user_manglik": user_signals.get("manglik_status")}
    if not check_manglik(user_prefs_with_manglik, candidate_signals):
        failed.append("manglik")

    if not check_current_location(user, user_prefs, candidate, candidate_prefs):
        failed.append("current_location")

    if not check_raised_in(user, user_prefs, candidate):
        failed.append("raised_in")

    if not check_mother_tongue(user, user_prefs, candidate):
        failed.append("mother_tongue")

    if not check_height(user_prefs, candidate):
        failed.append("height")

    if not check_disability(user_prefs, candidate):
        failed.append("disability")

    return (len(failed) == 0, failed)


def pass_hard_filters_bidirectional(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
) -> Tuple[bool, list, list]:
    """
    Check hard filters in both directions.
    Returns (passes, a_rejected_reasons, b_rejected_reasons).
    """
    a_ok, a_failed = pass_hard_filters(user_a, prefs_a, signals_a, user_b, prefs_b, signals_b)
    b_ok, b_failed = pass_hard_filters(user_b, prefs_b, signals_b, user_a, prefs_a, signals_a)

    return (a_ok and b_ok, a_failed, b_failed)
