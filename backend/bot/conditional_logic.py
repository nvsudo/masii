"""
Conditional Logic Router for Masii Onboarding — The 36 Gunas
Implements all branching, skip logic, and tree routing based on user answers.

Tree branches:
  - Religion → Practice level (guna 11)
  - Religion → Sect/denomination (guna 12)
  - Religion → Caste/community (guna 13) + caste_importance sub-Q
  - Religion → Diet options (guna 22)
  - Marital status → Children existing (sub-Q after guna 9)
  - Children intent → Timeline (guna 21)
  - Location → India/abroad → state/country → city (guna 8 multi-step)
"""

from typing import Dict, Optional

from config import (
    get_practice_by_religion,
    get_sects_by_religion,
    get_castes_by_religion,
    get_diet_by_religion,
)


def should_skip_question(question_num: int, answers: Dict) -> bool:
    """
    Determine if a guna should be skipped based on previous answers.
    Returns True if question should be skipped.
    """

    # Guna 11 (practice): skip if religion is Buddhist/Other/None
    if question_num == 11:
        religion = answers.get("religion")
        return get_practice_by_religion(religion) is None

    # Guna 12 (sect): skip if no sects for this religion
    if question_num == 12:
        religion = answers.get("religion")
        return get_sects_by_religion(religion) is None

    # Guna 13 (caste): skip if no castes for this religion
    if question_num == 13:
        religion = answers.get("religion")
        return get_castes_by_religion(religion) is None

    # Guna 21 (children timeline): skip if children_intent is "No"
    if question_num == 21:
        return answers.get("children_intent") == "No"

    return False


def should_ask_sub_question(sub_key: str, answers: Dict) -> bool:
    """
    Determine if a sub-question (not a guna) should be asked.
    Sub-questions are conditional branches within a guna's flow.
    """
    if sub_key == "children_existing":
        return answers.get("marital_status") not in ("Never married", None)

    if sub_key == "caste_importance":
        caste = answers.get("caste_community")
        return caste is not None and caste != "Prefer not to say"

    return False


def get_next_question(answers: Dict, current_question: int) -> int:
    """
    Calculate the next guna number based on current guna and answers.
    Handles skip logic. Sub-questions are handled separately in the handler.
    """
    next_q = current_question + 1

    # Keep skipping until we find a non-skipped question or exceed 36
    while next_q <= 36 and should_skip_question(next_q, answers):
        next_q += 1

    return next_q


def get_section_for_question(question_num: int) -> str:
    """Return the section name for a given guna number"""
    if question_num <= 0:
        return "intro"
    elif question_num <= 4:
        return "niyat"
    elif question_num <= 9:
        return "parichay"
    elif question_num <= 16:
        return "dharam"
    elif question_num <= 21:
        return "parivar"
    elif question_num <= 28:
        return "jeevan_shaili"
    elif question_num <= 36:
        return "soch"
    else:
        return "complete"


def get_completion_percentage(answers: Dict, skip_questions: list) -> float:
    """
    Calculate onboarding completion percentage.
    Total = 36 gunas - legitimately skipped gunas
    """
    total_possible = 36
    total_required = total_possible - len(skip_questions)

    # Count answered guna fields (not sub-questions)
    answered = len(answers)

    if total_required == 0:
        return 0.0

    return min((answered / total_required) * 100, 100.0)


def get_conditional_options(question_num: int, answers: Dict) -> Optional[list]:
    """
    Return conditional options for questions whose choices depend on prior answers.
    Returns None if the question should use its default options or be skipped.
    """

    # Guna 11: Practice level — options depend on religion
    if question_num == 11:
        religion = answers.get("religion")
        return get_practice_by_religion(religion)

    # Guna 12: Sect/denomination — options depend on religion
    if question_num == 12:
        religion = answers.get("religion")
        return get_sects_by_religion(religion)

    # Guna 13: Caste/community — options depend on religion
    if question_num == 13:
        religion = answers.get("religion")
        return get_castes_by_religion(religion)

    # Guna 22: Diet — options depend on religion (and practice for Jain)
    if question_num == 22:
        religion = answers.get("religion")
        practice = answers.get("religious_practice")
        return get_diet_by_religion(religion, practice)

    return None


# ============== SECTION TRANSITION DETECTION ==============

# Map: when entering this section, which transition key to use
SECTION_TRANSITION_MAP = {
    "niyat": "niyat_buyin",
    "parichay": "after_niyat",
    "dharam": "after_parichay",
    "parivar": "after_dharam",
    "jeevan_shaili": "after_parivar",
    "soch": "soch_buyin",
}


def get_transition_key(current_section: str, previous_section: str) -> Optional[str]:
    """
    Return the transition message key if entering a new section.
    Returns None if no transition needed.
    """
    if current_section == previous_section:
        return None
    return SECTION_TRANSITION_MAP.get(current_section)


# ============== VALIDATION TESTS ==============

TEST_PATHS = [
    {
        "name": "Hindu, never married (full tree)",
        "answers": {
            "marital_status": "Never married",
            "religion": "Hindu",
            "caste_community": "Brahmin",
            "children_intent": "Yes",
        },
        "expected_gunas": list(range(1, 37)),  # All 36
        "expected_sub_questions": ["caste_importance"],
        "skip_sub_questions": ["children_existing"],
    },
    {
        "name": "Muslim, never married (no caste, no sect skip)",
        "answers": {
            "marital_status": "Never married",
            "religion": "Muslim",
            "children_intent": "Yes",
        },
        "expected_skip": [13],  # Caste skipped for Muslims
        "expected_sub_questions": [],
        "skip_sub_questions": ["children_existing", "caste_importance"],
    },
    {
        "name": "Buddhist, divorced with children",
        "answers": {
            "marital_status": "Divorced",
            "religion": "Buddhist",
            "children_intent": "No",
        },
        "expected_skip": [11, 12, 13, 21],  # Practice, sect, caste, kids timeline
        "expected_sub_questions": ["children_existing"],
        "skip_sub_questions": ["caste_importance"],
    },
    {
        "name": "Jain, never married (full Jain tree)",
        "answers": {
            "marital_status": "Never married",
            "religion": "Jain",
            "caste_community": "Oswal",
            "children_intent": "Open",
        },
        "expected_skip": [],  # Jain gets everything
        "expected_sub_questions": ["caste_importance"],
        "skip_sub_questions": ["children_existing"],
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

        # Check which gunas would be skipped
        actual_skip = []
        for q in range(1, 37):
            if should_skip_question(q, answers):
                actual_skip.append(q)

        skip_match = set(actual_skip) == set(expected_skip)

        # Check sub-questions
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
    print("Running 36 Gunas conditional logic validation...\n")
    results = validate_conditional_logic()

    for path_name, result in results.items():
        status = "\u2713 PASS" if result["passed"] else "\u2717 FAIL"
        print(f"{status} {path_name}")
        if not result["passed"]:
            print(f"  Expected skip: {result['expected_skip']}")
            print(f"  Actual skip:   {result['actual_skip']}")
            print(f"  Sub-Q correct: {result['sub_questions_correct']}")
        print()
