"""
Hard Filters — Stage 1 of Masii Matching

Binary pass/fail elimination. If any filter fails, the pair is impossible.
Both directions (A→B and B→A) must pass for a match to proceed.

Filters check: gender, age, religion, caste, location, marital status,
children intent, diet, smoking, drinking, medical conditions, marriage timeline,
manglik, gotra.
"""

from datetime import date
from typing import Dict, Optional, Tuple

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

# Marriage timeline overlap matrix
# Two timelines are compatible if they're within 1 step of each other
TIMELINE_RANK = {
    "Within 6 months": 1,
    "In the next 1 year": 2,
    "In the next 2-3 years": 3,
    "Just exploring": 4,
}

# Diet strictness hierarchy
DIET_STRICT = {
    "Strict Jain (no onion/garlic)": 1,
    "Jain vegetarian": 2,
    "Pure vegetarian": 2,
    "Vegetarian": 3,
    "Eggetarian": 4,
    "Non-vegetarian": 5,
    "Halal only": 5,
    "Flexible": 6,
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


def check_age(user_prefs: Dict, candidate: Dict) -> Tuple[bool, bool]:
    """
    Check if candidate's age is within user's preferred range.
    Returns (passes_hard, within_buffer).
    Hard fail if outside range + 2yr buffer.
    """
    dob = candidate.get("date_of_birth")
    pref_min = user_prefs.get("pref_age_min")
    pref_max = user_prefs.get("pref_age_max")

    if not dob:
        return True, False  # No data = pass (can't filter)

    age = calculate_age(dob) if isinstance(dob, date) else None
    if age is None:
        return True, False

    if pref_min is None and pref_max is None:
        return True, True  # No preference = pass

    min_age = int(pref_min) if pref_min else 18
    max_age = int(pref_max) if pref_max else 60
    buffer = 2

    if min_age <= age <= max_age:
        return True, True  # Within range
    elif (min_age - buffer) <= age <= (max_age + buffer):
        return True, False  # Within buffer (soft penalty)
    else:
        return False, False  # Hard fail


def check_religion(user_prefs: Dict, candidate: Dict, candidate_prefs: Dict) -> bool:
    """
    Check religion compatibility.
    'Same religion only' = must match user's religion.
    'Open, but not...' = candidate's religion must NOT be in exclude list.
    'Open to all' = pass.
    """
    pref = user_prefs.get("pref_religion")
    candidate_religion = candidate.get("religion")

    if not pref or pref == "Open to all":
        return True

    if pref == "Same religion only":
        # User's own religion is on the users table, not prefs.
        # We need the calling code to pass the user's own religion.
        # It's stored in user dict, not user_prefs. Handle in caller.
        # For now, this is called with user (users table) separately.
        return True  # Handled at caller level with user's religion

    if pref == "Open, but not...":
        exclude = user_prefs.get("pref_religion_exclude") or []
        if isinstance(exclude, str):
            exclude = [exclude]
        return candidate_religion not in exclude

    return True


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


def check_marital_status(user: Dict, candidate: Dict) -> bool:
    """
    No explicit marital preference column exists — this is implicit.
    Never-married users usually prefer never-married.
    For now, pass all — can tighten later with data.
    """
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
    Diet as hard filter only when user says 'Same as mine' or 'Vegetarian or above'
    and candidate is non-veg.
    """
    pref = user_prefs.get("pref_diet")
    candidate_diet = candidate_signals.get("diet")

    if not pref or pref == "Doesn't matter" or not candidate_diet:
        return True

    if pref == "Vegetarian or above":
        # Candidate must be vegetarian or stricter
        rank = DIET_STRICT.get(candidate_diet, 6)
        return rank <= 3  # Veg, pure veg, Jain

    if pref == "Same as mine":
        # Soft filter — handled in scoring. Only eliminate extreme mismatch.
        # Strict Jain vs Non-veg = eliminate
        user_diet_rank = DIET_STRICT.get(user_prefs.get("_user_diet"), 6)
        cand_diet_rank = DIET_STRICT.get(candidate_diet, 6)
        # Eliminate if user is veg (rank <= 3) and candidate is non-veg (rank >= 5)
        if user_diet_rank <= 3 and cand_diet_rank >= 5:
            return False

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
    'Within 6 months' and 'Just exploring' = no overlap = eliminate.
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

    # Both must be same (Yes-Yes or No-No)
    return user_manglik == candidate_manglik


def check_gotra(user_prefs: Dict, candidate_signals: Dict) -> bool:
    """Hard filter: candidate's gotra must not be in user's exclude list."""
    exclude = user_prefs.get("pref_gotra_exclude") or []
    if isinstance(exclude, str):
        exclude = [exclude]
    if not exclude:
        return True

    candidate_gotra = candidate_signals.get("gotra")
    if not candidate_gotra:
        return True

    return candidate_gotra not in exclude


def check_location_basic(user: Dict, candidate: Dict, user_prefs: Dict, candidate_prefs: Dict) -> bool:
    """
    Location as hard filter only when BOTH refuse to relocate
    AND they're in different countries.
    """
    user_country = user.get("country_current")
    cand_country = candidate.get("country_current")

    if not user_country or not cand_country:
        return True

    if user_country == cand_country:
        return True  # Same country = always pass

    # Different countries — check relocation willingness
    user_reloc = user_prefs.get("relocation_willingness", "")
    cand_reloc = candidate_prefs.get("relocation_willingness", "")

    # If both refuse to relocate and in different countries = eliminate
    if user_reloc == "No, I'm settled" and cand_reloc == "No, I'm settled":
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

    passes_age, _ = check_age(user_prefs, candidate)
    if not passes_age:
        failed.append("age")

    if not check_religion_full(user, user_prefs, candidate):
        failed.append("religion")

    if not check_caste(user_prefs, candidate_prefs):
        failed.append("caste")

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

    if not check_gotra(user_prefs, candidate_signals):
        failed.append("gotra")

    if not check_location_basic(user, candidate, user_prefs, candidate_prefs):
        failed.append("location")

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
