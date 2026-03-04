"""
Compatibility Scoring — Stage 2 of Masii Matching (v2)

v2 architecture: ~35 per-question scorers, each returns (score, max_possible).
Total = sum(scores) / sum(max_possible) * 100.

When a question is unanswerable (missing data for both sides), returns (0.0, 0.0)
— doesn't count toward total. This prevents penalizing incomplete profiles.

Bidirectional: min(A→B, B→A) — same as v1.
"""

from datetime import date
from typing import Dict, List, Optional, Tuple

try:
    from .filters import (
        calculate_age,
        EDUCATION_RANK,
        INCOME_RANK,
        TIMELINE_RANK,
        DIET_STRICT,
    )
except ImportError:
    from filters import (
        calculate_age,
        EDUCATION_RANK,
        INCOME_RANK,
        TIMELINE_RANK,
        DIET_STRICT,
    )


# ============== HELPER ==============

def _skip() -> Tuple[float, float]:
    """Return (0, 0) to skip a question — doesn't affect total."""
    return (0.0, 0.0)


# ============== REGULAR SCORERS (max 1.0 each) ==============


def score_religion(user: Dict, candidate: Dict) -> Tuple[float, float]:
    """Same religion = 1.0, different = 0.0."""
    ur = user.get("religion")
    cr = candidate.get("religion")
    if not ur or not cr:
        return _skip()
    return (1.0, 1.0) if ur == cr else (0.0, 1.0)


def score_religious_practice(user_prefs: Dict, cand_prefs: Dict) -> Tuple[float, float]:
    """Same = 1.0, 1 step = 0.5, 2 = 0.25, opposite = 0.0."""
    practice_rank = {
        "Very religious": 4, "Very religious (Amritdhari)": 4,
        "Religious": 3, "Religious (Keshdhari)": 3,
        "Moderately religious": 2, "Moderate": 2, "Moderate (Sahajdhari)": 2,
        "Not religious": 1, "Not very religious": 1, "Liberal": 1,
    }
    up = user_prefs.get("religious_practice")
    cp = cand_prefs.get("religious_practice")
    if not up or not cp:
        return _skip()
    u = practice_rank.get(up, 2)
    c = practice_rank.get(cp, 2)
    diff = abs(u - c)
    if diff == 0:
        return (1.0, 1.0)
    elif diff == 1:
        return (0.5, 1.0)
    elif diff == 2:
        return (0.25, 1.0)
    else:
        return (0.0, 1.0)


def score_caste_importance(user_prefs: Dict, cand_prefs: Dict) -> Tuple[float, float]:
    """
    "Doesn't matter" = 1.0.
    "Must match" + same = 1.0 (different already eliminated by gate).
    "Prefer same" + different = 0.5, same = 1.0.
    """
    importance = user_prefs.get("caste_importance")
    if not importance:
        return _skip()

    if importance == "Doesn't matter":
        return (1.0, 1.0)

    user_caste = user_prefs.get("caste_community")
    cand_caste = cand_prefs.get("caste_community")

    if not user_caste or not cand_caste:
        return _skip()

    same = user_caste == cand_caste

    if importance == "Must be same caste":
        return (1.0, 1.0) if same else (0.0, 1.0)

    if importance == "Prefer same, open to others":
        return (1.0, 1.0) if same else (0.5, 1.0)

    return (1.0, 1.0)


def score_age(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """Within range = 1.0 (redundant with gate but included for completeness)."""
    dob = candidate.get("date_of_birth")
    pref_min = user_prefs.get("pref_age_min")
    pref_max = user_prefs.get("pref_age_max")
    if not dob or (pref_min is None and pref_max is None):
        return _skip()
    age = calculate_age(dob) if isinstance(dob, date) else None
    if age is None:
        return _skip()
    min_age = int(pref_min) if pref_min else 18
    max_age = int(pref_max) if pref_max else 60
    return (1.0, 1.0) if min_age <= age <= max_age else (0.0, 1.0)


def score_current_location(user_prefs: Dict) -> Tuple[float, float]:
    """Has location pref + passed gate = 1.0."""
    pref = user_prefs.get("pref_current_location")
    if not pref or pref == "Anywhere":
        return _skip()
    # If we get here, candidate passed the gate
    return (1.0, 1.0)


def score_raised_in(user_prefs: Dict) -> Tuple[float, float]:
    """Has raised-in pref + passed gate = 1.0."""
    pref = user_prefs.get("pref_raised_in")
    if not pref or pref == "Doesn't matter":
        return _skip()
    return (1.0, 1.0)


def score_mother_tongue(user: Dict, candidate: Dict) -> Tuple[float, float]:
    """Same = 1.0, shared non-English = 0.8, only English = 0.5, none = 0.0."""
    user_mt = user.get("mother_tongue")
    cand_mt = candidate.get("mother_tongue")
    if not user_mt or not cand_mt:
        return _skip()

    if user_mt == cand_mt:
        return (1.0, 1.0)

    user_langs = set(user.get("languages_spoken") or [])
    user_langs.add(user_mt)
    cand_langs = set(candidate.get("languages_spoken") or [])
    cand_langs.add(cand_mt)

    shared = user_langs & cand_langs
    shared_non_english = shared - {"English"}

    if shared_non_english:
        return (0.8, 1.0)
    elif "English" in shared:
        return (0.5, 1.0)
    else:
        return (0.0, 1.0)


def score_diet(user_prefs: Dict) -> Tuple[float, float]:
    """Has diet pref + passed gate = 1.0."""
    pref = user_prefs.get("pref_diet")
    if not pref or pref == "Doesn't matter":
        return _skip()
    return (1.0, 1.0)


def score_drinking(user_signals: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Same = 1.0, adjacent = 0.5, far = 0.25."""
    drink_rank = {"Never": 1, "Socially / Occasionally": 2, "Regularly": 3}
    ud = user_signals.get("drinking")
    cd = cand_signals.get("drinking")
    if not ud or not cd:
        return _skip()
    u = drink_rank.get(ud, 2)
    c = drink_rank.get(cd, 2)
    diff = abs(u - c)
    if diff == 0:
        return (1.0, 1.0)
    elif diff == 1:
        return (0.5, 1.0)
    else:
        return (0.25, 1.0)


def score_smoking(user_signals: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Same = 1.0, adjacent = 0.5, far = 0.0."""
    smoke_rank = {"Never": 1, "Socially / Occasionally": 2, "Regularly": 3}
    us = user_signals.get("smoking")
    cs = cand_signals.get("smoking")
    if not us or not cs:
        return _skip()
    u = smoke_rank.get(us, 2)
    c = smoke_rank.get(cs, 2)
    diff = abs(u - c)
    if diff == 0:
        return (1.0, 1.0)
    elif diff == 1:
        return (0.5, 1.0)
    else:
        return (0.0, 1.0)


def score_education_level(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """Meets min = 1.0, below = 0.0, "Doesn't matter" = 1.0."""
    pref_edu = user_prefs.get("pref_education_min")
    cand_edu = candidate.get("education_level")

    if not pref_edu or pref_edu == "Doesn't matter":
        return (1.0, 1.0)

    if not cand_edu:
        return _skip()

    pref_level = pref_edu.replace("At least ", "")
    p_rank = EDUCATION_RANK.get(pref_level, 3)
    c_rank = EDUCATION_RANK.get(cand_edu, 3)
    return (1.0, 1.0) if c_rank >= p_rank else (0.0, 1.0)


def score_education_field(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """
    "Same as mine" + match = 1.0, no match = 0.0.
    "Doesn't matter" = 1.0.
    "Specific fields..." + candidate in list = 1.0.
    """
    pref = user_prefs.get("pref_education_field")
    if not pref or pref == "Doesn't matter":
        return (1.0, 1.0)

    cand_field = candidate.get("education_field")
    if not cand_field:
        return _skip()

    if pref == "Same as mine":
        user_field = user_prefs.get("_user_education_field")
        if not user_field:
            return _skip()
        return (1.0, 1.0) if user_field == cand_field else (0.0, 1.0)

    # "Specific fields..." — pref itself could be a list or check sub-key
    pref_fields = user_prefs.get("pref_education_field_list") or []
    if isinstance(pref_fields, str):
        pref_fields = [pref_fields]
    if pref_fields:
        return (1.0, 1.0) if cand_field in pref_fields else (0.0, 1.0)

    return (1.0, 1.0)


def score_occupation_sector(user: Dict, candidate: Dict) -> Tuple[float, float]:
    """Same = 1.0, different = 0.0."""
    us = user.get("occupation_sector")
    cs = candidate.get("occupation_sector")
    if not us or not cs:
        return _skip()
    return (1.0, 1.0) if us == cs else (0.0, 1.0)


def score_income(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """Meets min = 1.0, below = 0.0, "Doesn't matter" = 1.0."""
    pref = user_prefs.get("pref_income_min")
    if not pref or pref == "Doesn't matter":
        return (1.0, 1.0)

    cand_income = candidate.get("annual_income")
    if not cand_income or cand_income == "Prefer not to say":
        return _skip()

    p_rank = INCOME_RANK.get(pref, 0)
    c_rank = INCOME_RANK.get(cand_income, 0)
    return (1.0, 1.0) if c_rank >= p_rank else (0.0, 1.0)


def score_family_type(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """
    "Same as mine" + match = 1.0.
    "Doesn't matter" = 1.0.
    """
    pref = user_prefs.get("pref_family_type")
    if not pref or pref == "Doesn't matter":
        return (1.0, 1.0)

    cand_ft = candidate.get("family_type")
    if not cand_ft:
        return _skip()

    if pref == "Same as mine":
        user_ft = user_prefs.get("_user_family_type")
        if not user_ft:
            return _skip()
        return (1.0, 1.0) if user_ft == cand_ft else (0.0, 1.0)

    return (1.0, 1.0)


def score_family_status(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """
    "Same or higher" + meets = 1.0.
    "Doesn't matter" = 1.0.
    """
    pref = user_prefs.get("pref_family_status")
    if not pref or pref == "Doesn't matter":
        return (1.0, 1.0)

    user_fs = user_prefs.get("_user_family_status")
    cand_fs = candidate.get("family_status")

    if not user_fs or not cand_fs:
        return _skip()

    fs_rank = {
        "Middle class": 1,
        "Upper middle class": 2,
        "Affluent": 3,
        "Prefer not to say": 0,
    }

    u = fs_rank.get(user_fs, 0)
    c = fs_rank.get(cand_fs, 0)

    if u == 0 or c == 0:
        return _skip()

    if pref == "Same or higher":
        return (1.0, 1.0) if c >= u else (0.0, 1.0)

    return (1.0, 1.0)


def score_father_occupation(user: Dict, candidate: Dict) -> Tuple[float, float]:
    """Same = 1.0, different = 0.0. Skip if "Not alive"/"Prefer not to say"."""
    skip_vals = {"Not alive", "Prefer not to say", None, ""}
    uf = user.get("father_occupation")
    cf = candidate.get("father_occupation")
    if uf in skip_vals or cf in skip_vals:
        return _skip()
    return (1.0, 1.0) if uf == cf else (0.0, 1.0)


def score_mother_occupation(user: Dict, candidate: Dict) -> Tuple[float, float]:
    """Same = 1.0, different = 0.0. Skip if "Not alive"/"Prefer not to say"."""
    skip_vals = {"Not alive", "Prefer not to say", None, ""}
    um = user.get("mother_occupation")
    cm = candidate.get("mother_occupation")
    if um in skip_vals or cm in skip_vals:
        return _skip()
    return (1.0, 1.0) if um == cm else (0.0, 1.0)


def score_siblings(user_prefs: Dict, candidate: Dict) -> Tuple[float, float]:
    """
    "Must have siblings" + only child = 0.0, has siblings = 1.0.
    "Doesn't matter" / "Single child is fine" = 1.0.
    """
    pref = user_prefs.get("pref_siblings")
    if not pref or pref in ("Doesn't matter", "Single child is fine"):
        return (1.0, 1.0)

    cand_siblings = candidate.get("siblings")
    if not cand_siblings:
        return _skip()

    if pref == "Must have siblings":
        return (0.0, 1.0) if cand_siblings == "Only child" else (1.0, 1.0)

    return (1.0, 1.0)


def score_children_timeline(user_prefs: Dict, cand_prefs: Dict) -> Tuple[float, float]:
    """Match = 1.0, "Doesn't matter" = 1.0, no match = 0.0."""
    pref = user_prefs.get("pref_children_timeline")
    if not pref or pref == "Doesn't matter":
        return (1.0, 1.0)

    cand_tl = cand_prefs.get("children_timeline")
    if not cand_tl:
        return _skip()

    return (1.0, 1.0) if pref == cand_tl else (0.0, 1.0)


def score_marriage_timeline(user_prefs: Dict, cand_prefs: Dict) -> Tuple[float, float]:
    """Same = 1.0, 1 step = 0.5."""
    user_tl = user_prefs.get("marriage_timeline")
    cand_tl = cand_prefs.get("marriage_timeline")
    if not user_tl or not cand_tl:
        return _skip()
    u = TIMELINE_RANK.get(user_tl, 2)
    c = TIMELINE_RANK.get(cand_tl, 2)
    diff = abs(u - c)
    if diff == 0:
        return (1.0, 1.0)
    elif diff == 1:
        return (0.5, 1.0)
    else:
        return (0.0, 1.0)


def score_living_arrangement(user_prefs: Dict, cand_prefs: Dict) -> Tuple[float, float]:
    """Match = 1.0, "Doesn't matter"/"Open to discussion" = 1.0."""
    pref = user_prefs.get("pref_living_arrangement")
    if not pref or pref == "Doesn't matter":
        return (1.0, 1.0)

    cand_la = cand_prefs.get("living_arrangement")
    if not cand_la:
        return _skip()

    if pref == "Open to discussion" or cand_la == "Open to discussion":
        return (1.0, 1.0)

    return (1.0, 1.0) if pref == cand_la else (0.0, 1.0)


def score_financial_planning(user_signals: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Same = 1.0, different = 0.0."""
    uf = user_signals.get("financial_planning")
    cf = cand_signals.get("financial_planning")
    if not uf or not cf:
        return _skip()
    return (1.0, 1.0) if uf == cf else (0.0, 1.0)


def score_height(user_prefs: Dict) -> Tuple[float, float]:
    """Has height pref + passed gate = 1.0."""
    pref_min = user_prefs.get("pref_height_min")
    pref_max = user_prefs.get("pref_height_max")
    if pref_min is None and pref_max is None:
        return _skip()
    return (1.0, 1.0)


def score_bmi(user: Dict, candidate: Dict) -> Tuple[float, float]:
    """Same BMI range = 1.0, 1 step = 0.5, 2 = 0.25, 3 = 0.0."""
    def _bmi_category(height_cm, weight_kg):
        if not height_cm or not weight_kg or height_cm <= 0:
            return None
        bmi = weight_kg / ((height_cm / 100) ** 2)
        if bmi < 18.5:
            return 0  # Underweight
        elif bmi < 25:
            return 1  # Normal
        elif bmi < 30:
            return 2  # Overweight
        else:
            return 3  # Obese

    u_cat = _bmi_category(user.get("height_cm"), user.get("weight_kg"))
    c_cat = _bmi_category(candidate.get("height_cm"), candidate.get("weight_kg"))

    if u_cat is None or c_cat is None:
        return _skip()

    diff = abs(u_cat - c_cat)
    if diff == 0:
        return (1.0, 1.0)
    elif diff == 1:
        return (0.5, 1.0)
    elif diff == 2:
        return (0.25, 1.0)
    else:
        return (0.0, 1.0)


# ============== GENDER-SPECIFIC SCORERS (max 1.0 each) ==============


def score_partner_working(user: Dict, user_prefs: Dict, user_signals: Dict,
                          candidate: Dict, cand_prefs: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Q44M vs Q46F cross-match. 'Her choice' = 1.0 with anything."""
    user_gender = user.get("gender")
    cand_gender = candidate.get("gender")

    if user_gender == "Male" and cand_gender == "Female":
        man_pref = user_prefs.get("partner_working")
        woman_plan = cand_signals.get("career_after_marriage")
    elif user_gender == "Female" and cand_gender == "Male":
        man_pref = cand_prefs.get("partner_working")
        woman_plan = user_signals.get("career_after_marriage")
    else:
        return _skip()

    if not man_pref or not woman_plan:
        return _skip()

    if man_pref == "Her choice":
        return (1.0, 1.0)

    compat = {
        ("Yes, she should have a career", "Yes, definitely"): 1.0,
        ("Yes, she should have a career", "Yes, but open to break for kids"): 1.0,
        ("Yes, she should have a career", "Yes, but open to a break for kids"): 1.0,
        ("Yes, she should have a career", "Undecided"): 0.5,
        ("Yes, she should have a career", "No, prefer homemaking"): 0.0,
        ("Prefer she focuses on home", "No, prefer homemaking"): 1.0,
        ("Prefer she focuses on home", "Undecided"): 0.5,
        ("Prefer she focuses on home", "Yes, but open to break for kids"): 0.0,
        ("Prefer she focuses on home", "Yes, but open to a break for kids"): 0.0,
        ("Prefer she focuses on home", "Yes, definitely"): 0.0,
    }
    score = compat.get((man_pref, woman_plan), 0.5)
    return (score, 1.0)


def score_partner_can_cook(user: Dict, user_prefs: Dict,
                           candidate: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Q42F-pref (men ask) vs Q42F (women answer). "Doesn't matter" = 1.0."""
    user_gender = user.get("gender")
    cand_gender = candidate.get("gender")

    if user_gender == "Male" and cand_gender == "Female":
        man_pref = user_prefs.get("pref_partner_cooking")
        if not man_pref:
            man_pref = user_prefs.get("pref_partner_cook")
        woman_cook = cand_signals.get("do_you_cook")
    elif user_gender == "Female" and cand_gender == "Male":
        man_pref = cand_signals.get("pref_partner_cooking")
        if not man_pref:
            man_pref = cand_signals.get("pref_partner_cook")
        woman_cook = user_prefs.get("do_you_cook")
        if not woman_cook:
            woman_cook = user_signals_fallback(user)
    else:
        return _skip()

    if not man_pref or man_pref == "Doesn't matter":
        return (1.0, 1.0)
    if not woman_cook:
        return _skip()

    cook_rank = {
        "Yes, I cook regularly": 3,
        "Yes, but I don't cook often": 2,
        "No, but I'm willing to learn": 1,
        "No": 0,
    }
    pref_rank = {
        "Yes, must cook regularly": 3,
        "Some cooking is enough": 2,
        "Doesn't matter": 0,
    }

    w = cook_rank.get(woman_cook, 1)
    p = pref_rank.get(man_pref, 1)
    return (1.0, 1.0) if w >= p else (0.0, 1.0)


def user_signals_fallback(user: Dict):
    """Helper — not a real function, just returns None for missing cross-gender data."""
    return None


def score_household(user: Dict, user_prefs: Dict, user_signals: Dict,
                    candidate: Dict, cand_prefs: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Q43M vs Q45F cross-match. 'Flexible'/'Not needed' = 1.0."""
    user_gender = user.get("gender")
    cand_gender = candidate.get("gender")

    if user_gender == "Male" and cand_gender == "Female":
        man_hh = user_signals.get("household_contribution")
        woman_pref = cand_prefs.get("pref_partner_household")
    elif user_gender == "Female" and cand_gender == "Male":
        man_hh = cand_signals.get("household_contribution")
        woman_pref = user_prefs.get("pref_partner_household")
    else:
        return _skip()

    if not man_hh or not woman_pref:
        return _skip()

    if woman_pref in ("Not needed — I'll manage or outsource", "Not needed"):
        return (1.0, 1.0)
    if man_hh in ("Flexible — whatever works", "Flexible"):
        return (1.0, 1.0)

    compat = {
        ("Shared equally", "Equal share"): 1.0,
        ("Shared equally", "Significant help"): 1.0,
        ("Shared equally", "Some help"): 1.0,
        ("Mostly outsourced (cook/maid)", "Equal share"): 0.0,
        ("Mostly outsourced (cook/maid)", "Significant help"): 0.0,
        ("Mostly outsourced (cook/maid)", "Some help"): 0.5,
        ("Mostly her", "Equal share"): 0.0,
        ("Mostly her", "Significant help"): 0.0,
        ("Mostly her", "Some help"): 0.5,
    }
    score = compat.get((man_hh, woman_pref), 0.5)
    return (score, 1.0)


def score_inlaws(user: Dict, user_prefs: Dict, user_signals: Dict,
                 candidate: Dict, cand_prefs: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Q48F vs Q38. Joint + happy = 1.0, joint + prefer not = 0.0, 'Depends' = 0.5."""
    user_gender = user.get("gender")
    cand_gender = candidate.get("gender")

    if user_gender == "Female" and cand_gender == "Male":
        woman_inlaws = user_signals.get("live_with_inlaws")
        man_la = cand_prefs.get("living_arrangement")
    elif user_gender == "Male" and cand_gender == "Female":
        woman_inlaws = cand_signals.get("live_with_inlaws")
        man_la = user_prefs.get("living_arrangement")
    else:
        return _skip()

    if not woman_inlaws or not man_la:
        return _skip()

    if man_la in ("Independent", "Independent — wherever life takes us",
                  "Open to discussion", "Near parents but separate"):
        return (1.0, 1.0)

    if man_la in ("With parents (joint)", "With parents (joint family)"):
        if woman_inlaws in ("Yes, happy to",):
            return (1.0, 1.0)
        elif woman_inlaws in ("For some time, not permanently",):
            return (0.5, 1.0)
        elif woman_inlaws in ("Depends on the situation",):
            return (0.5, 1.0)
        else:  # "Prefer not to"
            return (0.0, 1.0)

    return (0.5, 1.0)


# ============== WOW FACTOR SCORERS (max 1.5 each) ==============


def score_fitness_wow(user_signals: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Same = 1.5, 1 step = 1.0, 2 = 0.5, far = 0.0."""
    fitness_rank = {
        "Daily": 5, "3-5 times a week": 4,
        "1-2 times a week": 3, "Rarely": 2, "Never": 1,
    }
    uf = user_signals.get("fitness_frequency")
    cf = cand_signals.get("fitness_frequency")
    if not uf or not cf:
        return _skip()
    u = fitness_rank.get(uf, 3)
    c = fitness_rank.get(cf, 3)
    diff = abs(u - c)
    if diff == 0:
        return (1.5, 1.5)
    elif diff == 1:
        return (1.0, 1.5)
    elif diff == 2:
        return (0.5, 1.5)
    else:
        return (0.0, 1.5)


def score_social_wow(user_signals: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Same = 1.5, 1 step = 1.0, 2 = 0.5, extremes = 0.0."""
    social_rank = {
        "Very social — love big gatherings": 4,
        "Social — enjoy going out but need downtime": 3,
        "Introverted — prefer small groups": 2,
        "Very introverted — homebody": 1,
    }
    us = user_signals.get("social_style")
    cs = cand_signals.get("social_style")
    if not us or not cs:
        return _skip()
    u = social_rank.get(us, 3)
    c = social_rank.get(cs, 3)
    diff = abs(u - c)
    if diff == 0:
        return (1.5, 1.5)
    elif diff == 1:
        return (1.0, 1.5)
    elif diff == 2:
        return (0.5, 1.5)
    else:
        return (0.0, 1.5)


def score_conflict_wow(user_signals: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """Same = 1.5, 1 step = 1.0, 2+ = 0.5."""
    conflict_rank = {
        "Talk it out immediately": 4,
        "Take some time, then discuss": 3,
        "Get heated, then cool down": 2,
        "Avoid conflict": 1,
    }
    uc = user_signals.get("conflict_style")
    cc = cand_signals.get("conflict_style")
    if not uc or not cc:
        return _skip()
    u = conflict_rank.get(uc, 3)
    c = conflict_rank.get(cc, 3)
    diff = abs(u - c)
    if diff == 0:
        return (1.5, 1.5)
    elif diff == 1:
        return (1.0, 1.5)
    else:
        return (0.5, 1.5)


def score_cooking_wow(user: Dict, user_prefs: Dict, user_signals: Dict,
                      candidate: Dict, cand_prefs: Dict, cand_signals: Dict) -> Tuple[float, float]:
    """
    Man's expectation (Q42M-pref) vs woman's contribution (Q43F).
    Meets = 1.0, exceeds by 2+ = 1.5, below = 0.0.
    Also: Woman's expectation (Q44F) vs man's contribution (Q42M).
    """
    user_gender = user.get("gender")
    cand_gender = candidate.get("gender")

    cook_rank = {"0": 0, "1-3": 1, "4-7": 2, "8-10": 3, "More than 10": 4}
    pref_rank = {
        "Never — I'll handle it or we'll outsource": 0, "Never": 0,
        "Rarely (1-2)": 1, "Rarely (1-2 meals)": 1,
        "Sometimes (3-6)": 2, "Sometimes (3-6 meals)": 2,
        "Regularly (7+ meals)": 3, "Regularly (7+ meals a week)": 3,
    }

    if user_gender == "Male" and cand_gender == "Female":
        man_expectation = user_prefs.get("pref_partner_cooking")
        woman_contribution = cand_signals.get("cooking_contribution")
        if not woman_contribution:
            woman_contribution = cand_signals.get("cooking_meals")
    elif user_gender == "Female" and cand_gender == "Male":
        man_expectation = cand_prefs.get("pref_partner_cooking")
        woman_contribution = user_signals.get("cooking_contribution")
        if not woman_contribution:
            woman_contribution = user_signals.get("cooking_meals")
    else:
        return _skip()

    if not man_expectation or not woman_contribution:
        return _skip()

    p = pref_rank.get(man_expectation, 1)
    w = cook_rank.get(woman_contribution, 1)

    if w >= p + 2:
        return (1.5, 1.5)  # WOW — exceeds by 2+
    elif w >= p:
        return (1.0, 1.5)  # Meets expectation
    else:
        return (0.0, 1.5)  # Below expectation


# ============== COMPOSITE SCORING ==============


def calculate_match_score(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> Dict:
    """
    Calculate v2 compatibility score for one direction.
    Returns dict with: score (0-100), total, max, details.
    """
    # Inject user's own data into prefs for "Same as mine" comparisons
    prefs = {
        **user_prefs,
        "_user_diet": user_signals.get("diet"),
        "_user_education_field": user.get("education_field"),
        "_user_family_type": user.get("family_type"),
        "_user_family_status": user.get("family_status"),
    }

    results = []

    # Regular scorers
    results.append(("religion", score_religion(user, candidate)))
    results.append(("religious_practice", score_religious_practice(prefs, candidate_prefs)))
    results.append(("caste_importance", score_caste_importance(prefs, candidate_prefs)))
    results.append(("age", score_age(prefs, candidate)))
    results.append(("current_location", score_current_location(prefs)))
    results.append(("raised_in", score_raised_in(prefs)))
    results.append(("mother_tongue", score_mother_tongue(user, candidate)))
    results.append(("diet", score_diet(prefs)))
    results.append(("drinking", score_drinking(user_signals, candidate_signals)))
    results.append(("smoking", score_smoking(user_signals, candidate_signals)))
    results.append(("education_level", score_education_level(prefs, candidate)))
    results.append(("education_field", score_education_field(prefs, candidate)))
    results.append(("occupation_sector", score_occupation_sector(user, candidate)))
    results.append(("income", score_income(prefs, candidate)))
    results.append(("family_type", score_family_type(prefs, candidate)))
    results.append(("family_status", score_family_status(prefs, candidate)))
    results.append(("father_occupation", score_father_occupation(user, candidate)))
    results.append(("mother_occupation", score_mother_occupation(user, candidate)))
    results.append(("siblings", score_siblings(prefs, candidate)))
    results.append(("children_timeline", score_children_timeline(prefs, candidate_prefs)))
    results.append(("marriage_timeline", score_marriage_timeline(prefs, candidate_prefs)))
    results.append(("living_arrangement", score_living_arrangement(prefs, candidate_prefs)))
    results.append(("financial_planning", score_financial_planning(user_signals, candidate_signals)))
    results.append(("height", score_height(prefs)))
    results.append(("bmi", score_bmi(user, candidate)))

    # Gender-specific
    results.append(("partner_working", score_partner_working(user, prefs, user_signals, candidate, candidate_prefs, candidate_signals)))
    results.append(("partner_can_cook", score_partner_can_cook(user, prefs, candidate, candidate_signals)))
    results.append(("household", score_household(user, prefs, user_signals, candidate, candidate_prefs, candidate_signals)))
    results.append(("inlaws", score_inlaws(user, prefs, user_signals, candidate, candidate_prefs, candidate_signals)))

    # WOW factors
    results.append(("fitness_wow", score_fitness_wow(user_signals, candidate_signals)))
    results.append(("social_wow", score_social_wow(user_signals, candidate_signals)))
    results.append(("conflict_wow", score_conflict_wow(user_signals, candidate_signals)))
    results.append(("cooking_wow", score_cooking_wow(user, prefs, user_signals, candidate, candidate_prefs, candidate_signals)))

    total_score = sum(r[1][0] for r in results)
    total_max = sum(r[1][1] for r in results)

    if total_max == 0:
        return {"score": 0, "total": 0, "max": 0, "details": {}}

    pct = round((total_score / total_max) * 100, 1)

    details = {name: {"score": s, "max": m} for name, (s, m) in results if m > 0}

    return {
        "score": pct,
        "total": round(total_score, 2),
        "max": round(total_max, 2),
        "details": details,
    }


def calculate_bidirectional_score(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
) -> Dict:
    """
    Score both directions. Use lower score (conservative).
    """
    a_for_b = calculate_match_score(user_a, prefs_a, signals_a, user_b, prefs_b, signals_b)
    b_for_a = calculate_match_score(user_b, prefs_b, signals_b, user_a, prefs_a, signals_a)

    final_score = min(a_for_b["score"], b_for_a["score"])

    return {
        "score": final_score,
        "score_a_for_b": a_for_b["score"],
        "score_b_for_a": b_for_a["score"],
        "details_a": a_for_b["details"],
        "details_b": b_for_a["details"],
        "total_a": a_for_b["total"],
        "total_b": b_for_a["total"],
        "max_a": a_for_b["max"],
        "max_b": b_for_a["max"],
    }


def calculate_confidence(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
) -> str:
    """
    Confidence level based on profile completeness.
    Returns 'high', 'medium', or 'low'.
    """
    def count_filled(u, p, s):
        count = 0
        for d in [u, p, s]:
            for k, v in d.items():
                if v is not None and v != "" and not k.startswith("_"):
                    count += 1
        return count

    a_count = count_filled(user_a, prefs_a, signals_a)
    b_count = count_filled(user_b, prefs_b, signals_b)

    min_count = min(a_count, b_count)

    if min_count >= 25:
        return "high"
    elif min_count >= 15:
        return "medium"
    else:
        return "low"


def generate_explanation(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
    score_result: Dict,
) -> Dict:
    """
    Generate a human-readable explanation of why these two match.
    Simplified for v2: build highlights from matched fields. Max 5 highlights, 2 differences.
    """
    highlights = []
    differences = []

    # Religion
    if user_a.get("religion") == user_b.get("religion"):
        highlights.append(f"Both {user_a['religion']}")
    else:
        if user_a.get("religion") and user_b.get("religion"):
            differences.append(f"Different religions ({user_a['religion']} and {user_b['religion']})")

    # Mother tongue
    if user_a.get("mother_tongue") == user_b.get("mother_tongue"):
        highlights.append(f"Both speak {user_a['mother_tongue']}")

    # Diet
    a_diet = signals_a.get("diet")
    b_diet = signals_b.get("diet")
    if a_diet and b_diet and a_diet == b_diet:
        highlights.append(f"Both {a_diet.lower()}")

    # Location
    a_city = user_a.get("city_current")
    b_city = user_b.get("city_current")
    if a_city and b_city and a_city.lower() == b_city.lower():
        highlights.append(f"Both in {a_city}")
    elif user_a.get("country_current") == user_b.get("country_current"):
        highlights.append(f"Both in {user_a.get('country_current', 'the same country')}")

    # Education
    a_edu = user_a.get("education_level")
    b_edu = user_b.get("education_level")
    if a_edu and b_edu:
        a_rank = EDUCATION_RANK.get(a_edu, 0)
        b_rank = EDUCATION_RANK.get(b_edu, 0)
        if a_rank >= 4 and b_rank >= 4:
            highlights.append("Both highly educated")

    # Lifestyle — smoking
    if signals_a.get("smoking") == "Never" and signals_b.get("smoking") == "Never":
        highlights.append("Neither smokes")

    # Lifestyle — drinking
    if signals_a.get("drinking") == "Never" and signals_b.get("drinking") == "Never":
        highlights.append("Neither drinks")

    return {
        "highlights": highlights[:5],
        "differences": differences[:2],
        "score": score_result["score"],
    }
