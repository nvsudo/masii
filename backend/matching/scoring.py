"""
Compatibility Scoring — Stage 2 of Masii Matching

7 dimensions, each scored 0-10, with weighted contribution to a 0-100 composite.
Scoring is directional: score_a_for_b means "how well does B match A's preferences."
The final match score uses the LOWER of the two directions (conservative).

Dimensions & Weights:
    Cultural Alignment    20%
    Lifestyle Match       18%
    Life Stage            15%
    Location              12%
    Education & Career    10%
    Values & Personality  15%
    Family Dynamics       10%
"""

from datetime import date
from typing import Dict, Optional, Tuple

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

DIMENSION_WEIGHTS = {
    "cultural": 0.20,
    "lifestyle": 0.18,
    "life_stage": 0.15,
    "location": 0.12,
    "education": 0.10,
    "values": 0.15,
    "family": 0.10,
}


def _clamp(val: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(val, hi))


# ============== DIMENSION SCORERS ==============


def score_cultural(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Cultural Alignment (0-10, weight 20%)
    Sub-signals: religion match, practice level, caste alignment, mother tongue, family values.
    """
    score = 0.0
    data_points = 0

    # Religion match (0-4)
    user_religion = user.get("religion")
    cand_religion = candidate.get("religion")
    if user_religion and cand_religion:
        data_points += 1
        if user_religion == cand_religion:
            score += 4.0
            # Bonus for same practice level
            user_practice = user_prefs.get("religious_practice")
            cand_practice = candidate_prefs.get("religious_practice")
            if user_practice and cand_practice:
                data_points += 1
                if user_practice == cand_practice:
                    score += 1.0
                else:
                    score += 0.5  # Same religion, different practice
        else:
            # Different religion — check openness
            pref = user_prefs.get("pref_religion")
            if pref == "Open to all":
                score += 2.0
            elif pref == "Open, but not...":
                score += 1.5
            else:
                score += 0.5  # Hard filter should have caught strict cases

    # Caste alignment (0-2)
    user_caste = user_prefs.get("caste_community")
    cand_caste = candidate_prefs.get("caste_community")
    importance = user_prefs.get("caste_importance")
    if user_caste and cand_caste:
        data_points += 1
        if user_caste == cand_caste:
            score += 2.0  # Same caste
        elif importance == "Doesn't matter":
            score += 1.5
        elif importance == "Prefer same, open to others":
            score += 0.5
        else:
            score += 0.0

    # Mother tongue (0-2)
    user_mt = user.get("mother_tongue")
    cand_mt = candidate.get("mother_tongue")
    if user_mt and cand_mt:
        data_points += 1
        if user_mt == cand_mt:
            score += 2.0
        else:
            # Check if they share a language
            user_langs = set(user.get("languages_spoken") or [])
            cand_langs = set(candidate.get("languages_spoken") or [])
            user_langs.add(user_mt)
            cand_langs.add(cand_mt)
            if user_langs & cand_langs:
                score += 1.0
            else:
                score += 0.0

    # Family values alignment (0-2)
    user_fv = user_signals.get("family_values")
    cand_fv = candidate_signals.get("family_values")
    if user_fv and cand_fv:
        data_points += 1
        fv_rank = {"Traditional": 1, "Moderate": 2, "Liberal": 3}
        u = fv_rank.get(user_fv, 2)
        c = fv_rank.get(cand_fv, 2)
        diff = abs(u - c)
        if diff == 0:
            score += 2.0
        elif diff == 1:
            score += 1.0
        else:
            score += 0.0

    return _clamp(score, 0, 10)


def score_lifestyle(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Lifestyle Match (0-10, weight 18%)
    Sub-signals: diet compatibility, smoking/drinking habits, fitness, social style.
    """
    score = 0.0
    data_points = 0

    # Diet (0-3)
    user_diet = user_signals.get("diet")
    cand_diet = candidate_signals.get("diet")
    if user_diet and cand_diet:
        data_points += 1
        u_rank = DIET_STRICT.get(user_diet, 6)
        c_rank = DIET_STRICT.get(cand_diet, 6)
        diff = abs(u_rank - c_rank)
        if diff == 0:
            score += 3.0
        elif diff == 1:
            score += 2.5
        elif diff <= 2:
            score += 1.5
        else:
            score += 0.5

    # Smoking (0-1.5)
    user_smoke = user_signals.get("smoking")
    cand_smoke = candidate_signals.get("smoking")
    if user_smoke and cand_smoke:
        data_points += 1
        if user_smoke == cand_smoke:
            score += 1.5
        elif {user_smoke, cand_smoke} == {"Never", "Socially / Occasionally"}:
            score += 1.0
        else:
            score += 0.0

    # Drinking (0-1.5)
    user_drink = user_signals.get("drinking")
    cand_drink = candidate_signals.get("drinking")
    if user_drink and cand_drink:
        data_points += 1
        if user_drink == cand_drink:
            score += 1.5
        elif {user_drink, cand_drink} == {"Never", "Socially / Occasionally"}:
            score += 1.0
        else:
            score += 0.0

    # Fitness (0-2)
    fitness_rank = {
        "Daily": 5, "3-5 times a week": 4,
        "1-2 times a week": 3, "Rarely": 2, "Never": 1,
    }
    user_fit = user_signals.get("fitness_frequency")
    cand_fit = candidate_signals.get("fitness_frequency")
    if user_fit and cand_fit:
        data_points += 1
        u = fitness_rank.get(user_fit, 3)
        c = fitness_rank.get(cand_fit, 3)
        diff = abs(u - c)
        if diff <= 1:
            score += 2.0
        elif diff == 2:
            score += 1.0
        else:
            score += 0.0

    # Social style (0-2)
    social_rank = {
        "Very social — love big gatherings": 4,
        "Social — enjoy going out but need downtime": 3,
        "Introverted — prefer small groups": 2,
        "Very introverted — homebody": 1,
    }
    user_social = user_signals.get("social_style")
    cand_social = candidate_signals.get("social_style")
    if user_social and cand_social:
        data_points += 1
        u = social_rank.get(user_social, 3)
        c = social_rank.get(cand_social, 3)
        diff = abs(u - c)
        if diff <= 1:
            score += 2.0
        elif diff == 2:
            score += 1.0
        else:
            score += 0.0

    return _clamp(score, 0, 10)


def score_life_stage(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Life Stage (0-10, weight 15%)
    Sub-signals: age fit, children intent alignment, marriage timeline overlap.
    """
    score = 0.0
    data_points = 0

    # Age fit (0-3)
    cand_dob = candidate.get("date_of_birth")
    pref_min = user_prefs.get("pref_age_min")
    pref_max = user_prefs.get("pref_age_max")
    if cand_dob and isinstance(cand_dob, date):
        age = calculate_age(cand_dob)
        data_points += 1
        min_age = int(pref_min) if pref_min else 18
        max_age = int(pref_max) if pref_max else 60
        if min_age <= age <= max_age:
            score += 3.0
        elif (min_age - 2) <= age <= (max_age + 2):
            score += 2.0  # Buffer zone
        else:
            score += 0.0

    # Children intent (0-4)
    user_ci = user_prefs.get("children_intent")
    cand_ci = candidate_prefs.get("children_intent")
    if user_ci and cand_ci:
        data_points += 1
        if user_ci == cand_ci:
            score += 4.0
        elif "Maybe" in (user_ci, cand_ci) or "Open to it" in (user_ci, cand_ci):
            score += 2.0
        else:
            score += 0.0  # Hard filter should have caught Yes vs No

    # Marriage timeline (0-3)
    user_tl = user_prefs.get("marriage_timeline")
    cand_tl = candidate_prefs.get("marriage_timeline")
    if user_tl and cand_tl:
        data_points += 1
        u = TIMELINE_RANK.get(user_tl, 2)
        c = TIMELINE_RANK.get(cand_tl, 2)
        diff = abs(u - c)
        if diff == 0:
            score += 3.0
        elif diff == 1:
            score += 1.5
        else:
            score += 0.0

    return _clamp(score, 0, 10)


def score_location(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Location Compatibility (0-10, weight 12%)
    Same city = 10, same state = 8, same country = 6, different country + willing = 4.
    """
    data_points = 0

    user_city = (user.get("city_current") or "").lower().strip()
    cand_city = (candidate.get("city_current") or "").lower().strip()
    user_state = (user.get("state_india") or "").lower().strip()
    cand_state = (candidate.get("state_india") or "").lower().strip()
    user_country = (user.get("country_current") or "").lower().strip()
    cand_country = (candidate.get("country_current") or "").lower().strip()

    if not user_country and not cand_country:
        return 5.0  # No data = neutral

    data_points += 1

    # Same city
    if user_city and cand_city and user_city == cand_city:
        return 10.0

    # Same state (India)
    if user_state and cand_state and user_state == cand_state:
        return 8.0

    # Same country, different city/state
    if user_country and cand_country and user_country == cand_country:
        return 6.0

    # Different country — check relocation willingness
    user_reloc = user_prefs.get("relocation_willingness", "")
    cand_reloc = candidate_prefs.get("relocation_willingness", "")

    reloc_rank = {
        "Yes, anywhere": 4,
        "Yes, within India": 3,
        "Yes, within my state/country": 2,
        "No, I'm settled": 1,
    }

    u = reloc_rank.get(user_reloc, 2)
    c = reloc_rank.get(cand_reloc, 2)
    best = max(u, c)

    if best >= 4:
        return 5.0  # One is willing to go anywhere
    elif best >= 3:
        return 3.0
    elif best >= 2:
        return 2.0
    else:
        return 1.0


def score_education(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Education & Career (0-10, weight 10%)
    Sub-signals: education level meets minimum, similar career sector.
    """
    score = 0.0
    data_points = 0

    # Education level vs preference (0-5)
    pref_edu = user_prefs.get("pref_education_min")
    cand_edu = candidate.get("education_level")
    if pref_edu and cand_edu and pref_edu != "Doesn't matter":
        data_points += 1
        # Map "At least X" to the education level
        pref_level = pref_edu.replace("At least ", "")
        p_rank = EDUCATION_RANK.get(pref_level, 3)
        c_rank = EDUCATION_RANK.get(cand_edu, 3)
        if c_rank >= p_rank:
            score += 5.0
        elif c_rank == p_rank - 1:
            score += 3.0
        else:
            score += 1.0
    elif not pref_edu or pref_edu == "Doesn't matter":
        score += 5.0  # No preference = full marks

    # Career sector similarity (0-3) — same sector = bonus
    user_sector = user.get("occupation_sector")
    cand_sector = candidate.get("occupation_sector")
    if user_sector and cand_sector:
        data_points += 1
        if user_sector == cand_sector:
            score += 3.0
        else:
            score += 1.5  # Different sectors = neutral

    # Income meets preference (0-2)
    pref_income = user_prefs.get("pref_income_min")
    cand_income = candidate.get("annual_income")
    if pref_income and cand_income and pref_income != "Doesn't matter":
        data_points += 1
        p_rank = INCOME_RANK.get(pref_income, 0)
        c_rank = INCOME_RANK.get(cand_income, 0)
        if c_rank >= p_rank:
            score += 2.0
        elif c_rank >= p_rank - 1:
            score += 1.0
        else:
            score += 0.0
    else:
        score += 2.0  # No preference = full marks

    return _clamp(score, 0, 10)


def score_values(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Values & Personality (0-10, weight 15%)
    Sub-signals: conflict style, financial planning, family involvement alignment.
    """
    score = 0.0
    data_points = 0

    # Conflict style (0-3)
    conflict_rank = {
        "Talk it out immediately": 4,
        "Take some time, then discuss": 3,
        "Avoid conflict": 1,
        "Get heated, then cool down": 2,
    }
    user_cs = user_signals.get("conflict_style")
    cand_cs = candidate_signals.get("conflict_style")
    if user_cs and cand_cs:
        data_points += 1
        u = conflict_rank.get(user_cs, 3)
        c = conflict_rank.get(cand_cs, 3)
        diff = abs(u - c)
        if diff == 0:
            score += 3.0
        elif diff == 1:
            score += 2.0
        else:
            score += 1.0

    # Financial planning alignment (0-3)
    fin_rank = {
        "Fully joint": 3,
        "Joint for household, separate for personal": 2,
        "Mostly separate": 1,
    }
    user_fp = user_signals.get("financial_planning")
    cand_fp = candidate_signals.get("financial_planning")
    if user_fp and cand_fp:
        data_points += 1
        u = fin_rank.get(user_fp, 2)
        c = fin_rank.get(cand_fp, 2)
        diff = abs(u - c)
        if diff == 0:
            score += 3.0
        elif diff == 1:
            score += 2.0
        else:
            score += 0.5

    # Family involvement alignment (0-4)
    fi_rank = {
        "Very — their approval matters": 3,
        "Moderate — I'll decide but they have input": 2,
        "Independent — my decision entirely": 1,
    }
    user_fi = user_prefs.get("family_involvement")
    cand_fi = candidate_prefs.get("family_involvement")
    if user_fi and cand_fi:
        data_points += 1
        u = fi_rank.get(user_fi, 2)
        c = fi_rank.get(cand_fi, 2)
        diff = abs(u - c)
        if diff == 0:
            score += 4.0
        elif diff == 1:
            score += 2.5
        else:
            score += 1.0

    return _clamp(score, 0, 10)


def score_family(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> float:
    """
    Family Dynamics (0-10, weight 10%)
    Sub-signals: living arrangement, family status, household expectations (gendered).
    """
    score = 0.0
    data_points = 0

    # Living arrangement compatibility (0-4)
    la_rank = {
        "With parents (joint)": 3,
        "Near parents but separate": 2,
        "Independent": 1,
        "Open to discussion": 2,  # Flexible = middle ground
    }
    user_la = user_prefs.get("living_arrangement")
    cand_la = candidate_prefs.get("living_arrangement")
    if user_la and cand_la:
        data_points += 1
        if user_la == "Open to discussion" or cand_la == "Open to discussion":
            score += 3.5  # One is flexible
        else:
            u = la_rank.get(user_la, 2)
            c = la_rank.get(cand_la, 2)
            diff = abs(u - c)
            if diff == 0:
                score += 4.0
            elif diff == 1:
                score += 2.5
            else:
                score += 0.5

    # Family status (0-3)
    fs_rank = {
        "Middle class": 1,
        "Upper middle class": 2,
        "Affluent": 3,
        "Prefer not to say": 0,
    }
    user_fs = user.get("family_status")
    cand_fs = candidate.get("family_status")
    pref_fs = user_prefs.get("pref_family_status")
    if user_fs and cand_fs:
        data_points += 1
        u = fs_rank.get(user_fs, 0)
        c = fs_rank.get(cand_fs, 0)
        if u == 0 or c == 0:
            score += 1.5  # One declined to share
        elif abs(u - c) <= 1:
            score += 3.0
        else:
            score += 1.0

    # Household expectations — gendered cross-matching (0-3)
    user_gender = user.get("gender")
    cand_gender = candidate.get("gender")

    if user_gender == "Male" and cand_gender == "Female":
        # Man's partner_working vs woman's career_after_marriage
        man_pref = user_prefs.get("partner_working")
        woman_plan = candidate_signals.get("career_after_marriage")
        if man_pref and woman_plan:
            data_points += 1
            compatible = _household_working_compatible(man_pref, woman_plan)
            score += compatible

        # Man's cooking_contribution vs woman's pref_partner_cooking
        man_cook = user_signals.get("cooking_contribution")
        woman_pref_cook = candidate_prefs.get("pref_partner_cooking")
        if man_cook and woman_pref_cook:
            data_points += 1
            score += _household_cooking_compatible(man_cook, woman_pref_cook)

    elif user_gender == "Female" and cand_gender == "Male":
        # Woman's live_with_inlaws vs man's living_arrangement
        woman_inlaws = user_signals.get("live_with_inlaws")
        man_la = candidate_prefs.get("living_arrangement")
        if woman_inlaws and man_la:
            data_points += 1
            score += _inlaws_compatible(woman_inlaws, man_la)

    return _clamp(score, 0, 10)


def _household_working_compatible(man_pref: str, woman_plan: str) -> float:
    """Score: man's partner_working pref vs woman's career_after_marriage."""
    compat = {
        ("Yes, she should have a career", "Yes, definitely"): 3.0,
        ("Yes, she should have a career", "Yes, but open to break for kids"): 2.5,
        ("Yes, she should have a career", "Undecided"): 1.5,
        ("Yes, she should have a career", "No, prefer homemaking"): 0.0,
        ("Her choice", "Yes, definitely"): 3.0,
        ("Her choice", "Yes, but open to break for kids"): 3.0,
        ("Her choice", "Undecided"): 2.5,
        ("Her choice", "No, prefer homemaking"): 2.0,
        ("Prefer she focuses on home", "No, prefer homemaking"): 3.0,
        ("Prefer she focuses on home", "Undecided"): 1.5,
        ("Prefer she focuses on home", "Yes, but open to break for kids"): 1.0,
        ("Prefer she focuses on home", "Yes, definitely"): 0.0,
    }
    return compat.get((man_pref, woman_plan), 1.5)


def _household_cooking_compatible(man_cook: str, woman_pref: str) -> float:
    """Score: man's cooking_contribution vs woman's pref_partner_cooking."""
    cook_rank = {"0": 0, "1-3": 1, "4-7": 2, "8-10": 3, "More than 10": 4}
    pref_rank = {
        "Never": 0,
        "Rarely (1-2)": 1,
        "Sometimes (3-6)": 2,
        "Regularly (7+ meals)": 3,
    }
    m = cook_rank.get(man_cook, 1)
    w = pref_rank.get(woman_pref, 1)
    if m >= w:
        return 1.5  # Man meets or exceeds expectation
    elif m >= w - 1:
        return 1.0
    else:
        return 0.0


def _inlaws_compatible(woman_inlaws: str, man_la: str) -> float:
    """Score: woman's live_with_inlaws vs man's living_arrangement."""
    if man_la == "With parents (joint)":
        if woman_inlaws in ("Yes, happy to", "For some time, not permanently"):
            return 2.0
        elif woman_inlaws == "Depends on the situation":
            return 1.0
        else:
            return 0.0
    elif man_la == "Near parents but separate":
        if woman_inlaws == "Prefer not to":
            return 2.0
        else:
            return 1.5
    elif man_la in ("Independent", "Open to discussion"):
        return 2.0  # No in-law conflict
    return 1.0


# ============== COMPOSITE SCORE ==============


def calculate_match_score(
    user: Dict, user_prefs: Dict, user_signals: Dict,
    candidate: Dict, candidate_prefs: Dict, candidate_signals: Dict,
) -> Dict:
    """
    Calculate compatibility score for one direction: how well does candidate match user's prefs.

    Returns dict with:
        score: 0-100
        dimensions: { dimension_name: 0-10 score }
        data_points: how many fields contributed
    """
    args = (user, user_prefs, user_signals, candidate, candidate_prefs, candidate_signals)

    dimensions = {
        "cultural": score_cultural(*args),
        "lifestyle": score_lifestyle(*args),
        "life_stage": score_life_stage(*args),
        "location": score_location(*args),
        "education": score_education(*args),
        "values": score_values(*args),
        "family": score_family(*args),
    }

    # Weighted composite → 0-10 scale
    composite = sum(dimensions[d] * DIMENSION_WEIGHTS[d] for d in dimensions)
    # Scale to 0-100
    match_score = round(composite * 10, 1)

    return {
        "score": match_score,
        "dimensions": dimensions,
        "weighted_contributions": {
            d: round(dimensions[d] * DIMENSION_WEIGHTS[d] * 10, 1)
            for d in dimensions
        },
    }


def calculate_bidirectional_score(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
) -> Dict:
    """
    Score both directions. Use lower score (conservative).
    Returns combined result.
    """
    a_for_b = calculate_match_score(user_a, prefs_a, signals_a, user_b, prefs_b, signals_b)
    b_for_a = calculate_match_score(user_b, prefs_b, signals_b, user_a, prefs_a, signals_a)

    # Use lower score
    final_score = min(a_for_b["score"], b_for_a["score"])

    return {
        "score": final_score,
        "score_a_for_b": a_for_b["score"],
        "score_b_for_a": b_for_a["score"],
        "dimensions_a": a_for_b["dimensions"],
        "dimensions_b": b_for_a["dimensions"],
        "contributions_a": a_for_b["weighted_contributions"],
        "contributions_b": b_for_a["weighted_contributions"],
    }


def calculate_confidence(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
) -> str:
    """
    Confidence level based on profile completeness and data coverage.
    Returns 'high', 'medium', or 'low'.
    """
    # Count filled fields per profile
    def count_filled(u, p, s):
        count = 0
        for d in [u, p, s]:
            for k, v in d.items():
                if v is not None and v != "" and not k.startswith("_"):
                    count += 1
        return count

    a_count = count_filled(user_a, prefs_a, signals_a)
    b_count = count_filled(user_b, prefs_b, signals_b)

    # Need at least 15 fields per profile for medium confidence
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
    Returns dict with highlights (shared strengths), differences, and a summary.
    """
    highlights = []
    differences = []

    # Religion
    if user_a.get("religion") == user_b.get("religion"):
        highlights.append(f"Both {user_a['religion']}")
    else:
        if user_a.get("religion") and user_b.get("religion"):
            differences.append(f"Different religions ({user_a['religion']} and {user_b['religion']}), but both open")

    # Mother tongue
    if user_a.get("mother_tongue") == user_b.get("mother_tongue"):
        highlights.append(f"Both speak {user_a['mother_tongue']}")

    # Diet
    a_diet = signals_a.get("diet")
    b_diet = signals_b.get("diet")
    if a_diet and b_diet and a_diet == b_diet:
        highlights.append(f"Both {a_diet.lower()}")

    # Children
    a_ci = prefs_a.get("children_intent")
    b_ci = prefs_b.get("children_intent")
    if a_ci and b_ci and a_ci == b_ci:
        if a_ci == "Yes":
            a_tl = prefs_a.get("children_timeline", "")
            b_tl = prefs_b.get("children_timeline", "")
            if a_tl and a_tl == b_tl:
                highlights.append(f"Both want children {a_tl.lower()}")
            else:
                highlights.append("Both want children")

    # Marriage timeline
    a_mt = prefs_a.get("marriage_timeline")
    b_mt = prefs_b.get("marriage_timeline")
    if a_mt and b_mt and a_mt == b_mt:
        highlights.append(f"Both looking to marry {a_mt.lower()}")

    # Location
    a_city = user_a.get("city_current")
    b_city = user_b.get("city_current")
    if a_city and b_city and a_city.lower() == b_city.lower():
        highlights.append(f"Both in {a_city}")
    elif user_a.get("country_current") == user_b.get("country_current"):
        highlights.append(f"Both in {user_a.get('country_current', 'the same country')}")

    # Family values
    a_fv = signals_a.get("family_values")
    b_fv = signals_b.get("family_values")
    if a_fv and b_fv and a_fv == b_fv:
        highlights.append(f"Both from {a_fv.lower()} families")

    # Lifestyle
    a_smoke = signals_a.get("smoking")
    b_smoke = signals_b.get("smoking")
    if a_smoke == "Never" and b_smoke == "Never":
        highlights.append("Neither smokes")

    a_drink = signals_a.get("drinking")
    b_drink = signals_b.get("drinking")
    if a_drink == "Never" and b_drink == "Never":
        highlights.append("Neither drinks")

    # Education
    a_edu = user_a.get("education_level")
    b_edu = user_b.get("education_level")
    if a_edu and b_edu:
        a_rank = EDUCATION_RANK.get(a_edu, 0)
        b_rank = EDUCATION_RANK.get(b_edu, 0)
        if a_rank >= 4 and b_rank >= 4:
            highlights.append("Both highly educated")

    return {
        "highlights": highlights[:5],  # Max 5 highlights
        "differences": differences[:2],  # Max 2 differences
        "score": score_result["score"],
    }
