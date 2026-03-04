"""
Conditional Logic Router for Masii Onboarding
Source of truth: docs/question_matching_protocol.md (v2)

Handles all branching, skip logic, and tree routing based on user answers.

Skip logic:
  - Religion → Practice level (Q10), Caste (Q12)
  - Gender → Household questions (Q42-51 gender-forked)
  - Marital status → Children existing (sub-Q after Q6)
  - Caste → Caste importance (sub-Q after Q12)
  - Religion → Caste preference (Q14) — skip if no castes for religion
  - Pref_religion → Religion exclude list (sub-Q after Q13)
  - Pref_caste → Caste exclude list (sub-Q after Q14)
  - Children intent → Timeline (sub-Q after Q37)
  - Sensitive gate → Skip Q54, Q57-58 if gate = "no"
  - Manglik → Only Hindu/Jain (Q54)
  - Location → India/abroad → state/country → city (Q2, Q3 multi-step)
  - Location → Income brackets INR vs USD (Q19, Q21)
  - Location → Family status options (Q23)
  - Location → Partner raised-in pref options (pref_raised_in sub-Q)

v2 always-skip:
  - Q11 (sect) — not enough data to tree yet
  - Q24 (family_values) — self-assessment unreliable
  - Q28 (family_involvement) — implied by being on Masii
  - Q50 (financial_contribution Female) — covered by Q52
  - Q55 (gotra) — deferred to premium
  - Q56 (family_property) — covered by Q23
"""

from typing import Dict, Optional

from config import (
    get_practice_by_religion,
    get_sects_by_religion,
    get_castes_by_religion,
    get_diet_by_religion,
    get_height_by_gender,
    get_weight_by_gender,
    get_height_opposite_gender,
    get_income_by_location,
    get_income_by_location_with_doesnt_matter,
    get_languages_minus_mother_tongue,
    get_age_range_min,
    get_age_range_max,
    get_gotras_by_religion,
    get_family_status_by_location,
    get_pref_raised_in_options,
    TOTAL_QUESTIONS,
)


def should_skip_question(question_num: int, answers: Dict) -> bool:
    """
    Determine if a question should be skipped based on previous answers.
    Returns True if question should be skipped.
    """
    gender = answers.get("gender")

    # Q10 (practice): skip if religion has no practice options
    if question_num == 10:
        religion = answers.get("religion")
        return get_practice_by_religion(religion) is None

    # Q11 (sect): always skip — not enough data to tree properly yet (v2 protocol)
    if question_num == 11:
        return True

    # Q12 (caste): skip if no castes for this religion
    if question_num == 12:
        religion = answers.get("religion")
        return get_castes_by_religion(religion) is None

    # Q14 (pref_caste): skip if religion has no caste system
    if question_num == 14:
        religion = answers.get("religion")
        return get_castes_by_religion(religion) is None

    # Q24 (family_values): always skip — self-assessment unreliable (v2 protocol)
    if question_num == 24:
        return True

    # Q28 (family_involvement): always skip — implied by being on Masii (v2 protocol)
    if question_num == 28:
        return True

    # Q42-44 (Male household): skip if Female
    if question_num in (42, 43, 44):
        return gender == "Female"

    # Q45-49, Q51 (Female household): skip if Male
    # Q50 (financial_contribution Female): always skip — covered by Q52 (v2 protocol)
    if question_num == 50:
        return True

    if question_num in (45, 46, 47, 48, 49, 51):
        return gender == "Male"

    # Q54 (manglik): skip if gate="no" OR not Hindu/Jain
    if question_num == 54:
        if answers.get("sensitive_gate") == "no":
            return True
        religion = answers.get("religion")
        return religion not in ("Hindu", "Jain")

    # Q55 (gotra): always skip — deferred to premium matching (v2 protocol)
    if question_num == 55:
        return True

    # Q56 (family_property): always skip — covered by Q23 family wealth (v2 protocol)
    if question_num == 56:
        return True

    # Q57-58 (Sensitive questions): skip if gate said "no"
    if question_num in (57, 58):
        return answers.get("sensitive_gate") == "no"

    return False


def should_ask_sub_question(sub_key: str, answers: Dict) -> bool:
    """
    Determine if a sub-question should be asked.
    """
    if sub_key == "children_existing":
        return answers.get("marital_status") not in ("Never married", None)

    if sub_key == "caste_importance":
        caste = answers.get("caste_community")
        return caste is not None and caste != "Prefer not to say"

    if sub_key == "pref_religion_exclude":
        return answers.get("pref_religion") == "Open, but not..."

    if sub_key == "pref_caste_exclude":
        return answers.get("pref_caste") == "Open, but not..."

    if sub_key == "children_timeline":
        return answers.get("children_intent") != "No"

    if sub_key == "pref_manglik":
        status = answers.get("manglik_status")
        return status is not None and status != "Not applicable"

    if sub_key == "pref_gotra_exclude":
        # v2: gotra (Q55) is always skipped — never ask gotra exclude
        return False

    if sub_key == "pref_conditions":
        # Always ask after known_conditions (Q58) if the sensitive gate was answered
        return answers.get("sensitive_gate") == "yes"

    # --- New v2 sub-questions ---

    if sub_key == "pref_partner_location":
        # Always ask after Q2 (current location)
        return True

    if sub_key == "pref_raised_in":
        # Always ask after Q3 (where did you grow up)
        return True

    if sub_key == "pref_marital_status":
        # Always ask after Q6 (marital status)
        return True

    if sub_key == "pref_children_existing":
        # Ask after children_existing sub-Q (only if user is not Never married)
        return answers.get("marital_status") not in ("Never married", None)

    if sub_key == "pref_education_field":
        # Always ask after Q17 (education field)
        return True

    if sub_key == "pref_family_type":
        # Always ask after Q22 (family type)
        return True

    if sub_key == "pref_siblings":
        # Always ask after Q27 (siblings)
        return True

    if sub_key == "pref_children_timeline":
        # Ask after children_timeline sub-Q (only if children_intent != No)
        return answers.get("children_intent") != "No"

    if sub_key == "pref_living_arrangement":
        # Always ask after Q38 (living arrangement)
        return True

    if sub_key == "pref_partner_cooking_m":
        # Ask only for males, after Q42M (cooking contribution)
        return answers.get("gender") == "Male"

    if sub_key == "pref_partner_cooks":
        # Ask only for males, after male cooking questions
        return answers.get("gender") == "Male"

    if sub_key == "disability":
        # Always ask after Q58 (known_conditions) if sensitive gate was answered
        return answers.get("sensitive_gate") == "yes"

    if sub_key == "pref_disability":
        # Always ask after disability sub-Q if sensitive gate was answered
        return answers.get("sensitive_gate") == "yes"

    return False


def get_next_question(answers: Dict, current_question: int) -> int:
    """
    Calculate the next question number based on current and answers.
    Handles skip logic. Sub-questions are handled separately in the handler.
    """
    next_q = current_question + 1

    while next_q <= TOTAL_QUESTIONS and should_skip_question(next_q, answers):
        next_q += 1

    return next_q


def get_section_for_question(question_num: int) -> str:
    """Return the section name for a given question number"""
    if question_num <= 0:
        return "setup"
    elif question_num <= 8:
        return "basics"
    elif question_num <= 12:
        return "background"
    elif question_num <= 15:
        return "partner_bg"
    elif question_num <= 21:
        return "education"
    elif question_num <= 28:
        return "family"
    elif question_num <= 35:
        return "lifestyle"
    elif question_num <= 39:
        return "marriage"
    elif question_num <= 41:
        return "partner_physical"
    elif question_num <= 52:
        return "household"
    elif question_num <= 58:
        return "sensitive"
    elif question_num <= 60:
        return "social"
    else:
        return "complete"


def get_completion_percentage(answers: Dict, skip_questions: list) -> float:
    """
    Calculate onboarding completion percentage.
    """
    total_possible = TOTAL_QUESTIONS
    total_required = total_possible - len(skip_questions)
    answered = len(answers)

    if total_required == 0:
        return 0.0

    return min((answered / total_required) * 100, 100.0)


def get_conditional_options(question_num: int, answers: Dict) -> Optional[list]:
    """
    Return conditional options for questions whose choices depend on prior answers.
    Returns None if the question should use its default options or be skipped.
    """
    religion = answers.get("religion")
    gender = answers.get("gender")

    # Q5: languages minus mother tongue
    if question_num == 5:
        mother_tongue = answers.get("mother_tongue")
        if mother_tongue:
            return get_languages_minus_mother_tongue(mother_tongue)
        return None

    # Q7: height by gender
    if question_num == 7:
        return get_height_by_gender(gender) if gender else None

    # Q8: weight by gender
    if question_num == 8:
        return get_weight_by_gender(gender) if gender else None

    # Q10: Practice level by religion
    if question_num == 10:
        return get_practice_by_religion(religion)

    # Q11: Sect by religion
    if question_num == 11:
        return get_sects_by_religion(religion)

    # Q12: Caste by religion
    if question_num == 12:
        return get_castes_by_religion(religion)

    # Q19: Income brackets by location
    if question_num == 19:
        is_nri = answers.get("_location_type") == "Outside India"
        return get_income_by_location(is_nri)

    # Q21: Income preference with "Doesn't matter"
    if question_num == 21:
        is_nri = answers.get("_location_type") == "Outside India"
        return get_income_by_location_with_doesnt_matter(is_nri)

    # Q23: Family financial status by location
    if question_num == 23:
        is_nri = answers.get("_location_type") == "Outside India"
        return get_family_status_by_location(is_nri)

    # Q40 step2: Age range max (depends on min)
    # Handled in handler via two_step_range logic

    # Q41: Height range (opposite gender)
    if question_num == 41:
        return get_height_opposite_gender(gender) if gender else None

    # Q55: Gotras by religion
    if question_num == 55:
        return get_gotras_by_religion(religion)

    return None


def get_sub_question_conditional_options(sub_key: str, answers: Dict) -> Optional[list]:
    """
    Return conditional options for sub-questions whose choices depend on prior answers.
    Returns None if the sub-question should use its default options.
    """
    # pref_raised_in: options depend on whether user is in India or abroad
    if sub_key == "pref_raised_in":
        is_nri = answers.get("_location_type") == "Outside India"
        return get_pref_raised_in_options(is_nri)

    return None


# ============== SECTION TRANSITION DETECTION ==============

def get_transition_key(current_section: str, previous_section: str) -> Optional[str]:
    """
    Return the section name as transition key if entering a new section.
    Returns None if no transition needed.
    """
    if current_section == previous_section:
        return None
    # The SECTION_TRANSITIONS dict in config uses section names as keys
    return current_section


# ============== VALIDATION TESTS ==============

TEST_PATHS = [
    {
        "name": "Hindu male, never married (full tree)",
        "answers": {
            "gender": "Male",
            "marital_status": "Never married",
            "religion": "Hindu",
            "caste_community": "Brahmin",
            "children_intent": "Yes",
            "pref_religion": "Same religion only",
            "pref_caste": "Same caste only",
            "sensitive_gate": "yes",
            "manglik_status": "Yes",
            "gotra": "Bharadwaj",
            "_location_type": "India",
        },
        # Female household Qs + v2 always-skip: Q11, Q24, Q28, Q50, Q55, Q56
        "expected_skip": [11, 24, 28, 45, 46, 47, 48, 49, 50, 51, 55, 56],
        "expected_sub_questions": [
            "caste_importance", "children_timeline", "pref_manglik", "pref_conditions",
            "pref_partner_location", "pref_raised_in", "pref_marital_status",
            "pref_education_field", "pref_family_type", "pref_siblings",
            "pref_children_timeline", "pref_living_arrangement",
            "pref_partner_cooking_m", "pref_partner_cooks",
            "disability", "pref_disability",
        ],
        "skip_sub_questions": ["children_existing", "pref_religion_exclude", "pref_caste_exclude", "pref_children_existing", "pref_gotra_exclude"],
    },
    {
        "name": "Muslim female, never married",
        "answers": {
            "gender": "Female",
            "marital_status": "Never married",
            "religion": "Muslim",
            "children_intent": "Yes",
            "pref_religion": "Open, but not...",
            "pref_caste": "Open to all",
            "sensitive_gate": "yes",
            "_location_type": "Outside India",
        },
        # No caste, male Qs, no manglik for Muslim + v2 always-skip: Q11, Q24, Q28, Q50, Q55, Q56
        "expected_skip": [11, 12, 14, 24, 28, 42, 43, 44, 50, 54, 55, 56],
        "expected_sub_questions": [
            "pref_religion_exclude", "children_timeline", "pref_conditions",
            "pref_partner_location", "pref_raised_in", "pref_marital_status",
            "pref_education_field", "pref_family_type", "pref_siblings",
            "pref_children_timeline", "pref_living_arrangement",
            "disability", "pref_disability",
        ],
        "skip_sub_questions": [
            "children_existing", "caste_importance", "pref_caste_exclude",
            "pref_children_existing", "pref_partner_cooking_m", "pref_partner_cooks",
            "pref_gotra_exclude",
        ],
    },
    {
        "name": "Buddhist female, divorced, skip sensitive",
        "answers": {
            "gender": "Female",
            "marital_status": "Divorced",
            "religion": "Buddhist",
            "children_intent": "No",
            "pref_religion": "Open to all",
            "pref_caste": "Open to all",
            "sensitive_gate": "no",
            "_location_type": "India",
        },
        # v2 always-skip: Q11, Q24, Q28, Q50, Q55, Q56 + Buddhist skips: Q10, Q12, Q14
        # + Male household skip: Q42, Q43, Q44 + sensitive gate no: Q54, Q57, Q58
        "expected_skip": [10, 11, 12, 14, 24, 28, 42, 43, 44, 50, 54, 55, 56, 57, 58],
        "expected_sub_questions": [
            "children_existing",
            "pref_partner_location", "pref_raised_in", "pref_marital_status",
            "pref_children_existing",
            "pref_education_field", "pref_family_type", "pref_siblings",
            "pref_living_arrangement",
        ],
        "skip_sub_questions": [
            "caste_importance", "pref_religion_exclude", "pref_caste_exclude",
            "children_timeline", "pref_children_timeline",
            "pref_partner_cooking_m", "pref_partner_cooks",
            "disability", "pref_disability", "pref_conditions",
            "pref_gotra_exclude",
        ],
    },
]


def validate_conditional_logic(test_paths: list = None) -> Dict:
    """Test conditional logic with known user paths."""
    if test_paths is None:
        test_paths = TEST_PATHS

    results = {}

    for path in test_paths:
        path_name = path["name"]
        answers = path["answers"]
        expected_skip = path.get("expected_skip", [])

        actual_skip = []
        for q in range(1, TOTAL_QUESTIONS + 1):
            if should_skip_question(q, answers):
                actual_skip.append(q)

        skip_match = set(actual_skip) == set(expected_skip)

        expected_sub = path.get("expected_sub_questions", [])
        skip_sub = path.get("skip_sub_questions", [])

        sub_match = True
        for sub_key in expected_sub:
            if not should_ask_sub_question(sub_key, answers):
                sub_match = False
        for sub_key in skip_sub:
            if should_ask_sub_question(sub_key, answers):
                sub_match = False

        results[path_name] = {
            "passed": skip_match and sub_match,
            "expected_skip": expected_skip,
            "actual_skip": actual_skip,
            "sub_questions_correct": sub_match,
        }

    return results


if __name__ == "__main__":
    print("Running conditional logic validation...\n")
    results = validate_conditional_logic()

    for path_name, result in results.items():
        status = "\u2713 PASS" if result["passed"] else "\u2717 FAIL"
        print(f"{status} {path_name}")
        if not result["passed"]:
            print(f"  Expected skip: {result['expected_skip']}")
            print(f"  Actual skip:   {result['actual_skip']}")
            print(f"  Sub-Q correct: {result['sub_questions_correct']}")
        print()
