"""
Conditional Logic Router for JODI Onboarding
Implements all branching and skip logic based on user answers
"""

from typing import Dict, Optional


def should_skip_question(question_num: int, answers: Dict) -> bool:
    """
    Determine if a question should be skipped based on previous answers.
    Returns True if question should be skipped.
    """
    
    # Q5: Show only if marital_status ≠ "Never married"
    if question_num == 5:
        return answers.get("marital_status") == "Never married"
    
    # Q13: Show only if residency_type ≠ "Indian citizen (in India)"
    if question_num == 13:
        return answers.get("residency_type") == "Indian citizen (in India)"
    
    # Q14: Show only if residency_type = "Indian citizen (in India)"
    if question_num == 14:
        return answers.get("residency_type") != "Indian citizen (in India)"
    
    # Q19: Show only if NRI/OCI
    if question_num == 19:
        residency = answers.get("residency_type")
        return residency not in ["NRI", "OCI / PIO"]
    
    # Q24-Q26, Q29: Show only for Hindu/Jain/Sikh/Buddhist
    if question_num in [24, 25, 26, 29]:
        religion = answers.get("religion")
        return religion not in ["Hindu", "Jain", "Sikh", "Buddhist"]
    
    # Q25: Show only if caste_community answered (not "Prefer not to say" or empty)
    if question_num == 25:
        caste = answers.get("caste_community")
        return not caste or caste == "Prefer not to say"
    
    # Q36: Show only if NRI
    if question_num == 36:
        return answers.get("residency_type") != "NRI"
    
    # Q69: Show only if children_intent ≠ "Definitely not"
    if question_num == 69:
        return answers.get("children_intent") == "Definitely not"
    
    return False


def get_next_question(answers: Dict, current_question: int) -> int:
    """
    Calculate the next question number based on current question and answers.
    Implements skip logic and section transitions.
    """
    next_q = current_question + 1
    
    # Keep checking if next question should be skipped
    while next_q <= 79 and should_skip_question(next_q, answers):
        next_q += 1
    
    # Handle section jumps
    
    # If Q24 (caste) should be skipped, jump to Q27 (mother_tongue)
    if current_question == 23 and should_skip_question(24, answers):
        next_q = 27
    
    # If Q29 (manglik) should be skipped after Q26, jump to Q30 (education)
    if current_question == 26 and should_skip_question(29, answers):
        next_q = 30
    
    # If Q19 should be skipped after Q18, jump to Q20 (religion section)
    if current_question == 18 and should_skip_question(19, answers):
        next_q = 20
    
    return next_q


def get_section_for_question(question_num: int) -> str:
    """Return the section name for a given question number"""
    if question_num <= 0:
        return "intro"
    elif question_num <= 11:
        return "identity_basics"
    elif question_num <= 19:
        return "location_mobility"
    elif question_num <= 29:
        return "religion_culture"
    elif question_num <= 34:
        return "education_career"
    elif question_num <= 39:
        return "financial"
    elif question_num <= 46:
        return "family"
    elif question_num <= 57:
        return "lifestyle"
    elif question_num <= 66:
        return "partner_prefs"
    elif question_num <= 74:
        return "values"
    elif question_num <= 79:
        return "dealbreakers"
    else:
        return "photo_upload"


def get_completion_percentage(answers: Dict, skip_questions: list) -> float:
    """
    Calculate onboarding completion percentage.
    Total questions = 79 - number of legitimately skipped questions
    """
    # Total possible questions
    total_possible = 79
    
    # Subtract legitimately skipped questions
    total_required = total_possible - len(skip_questions)
    
    # Count answered questions
    answered = len(answers)
    
    if total_required == 0:
        return 0.0
    
    return (answered / total_required) * 100


def get_conditional_options(question_num: int, answers: Dict) -> Optional[list]:
    """
    Return conditional options for questions that change based on previous answers.
    Currently handles:
    - Q23: sect/denomination based on religion
    - Q24: caste/community based on religion
    """
    
    if question_num == 23:
        # Sect/denomination options based on religion
        religion = answers.get("religion")
        
        if religion == "Hindu":
            return [
                {"label": "Shaivite (Shiv bhakt)", "value": "Shaivite"},
                {"label": "Vaishnavite (Vishnu bhakt)", "value": "Vaishnavite"},
                {"label": "Arya Samaji", "value": "Arya Samaj"},
                {"label": "Smartha", "value": "Smartha"},
                {"label": "Don't follow any specific tradition", "value": "None"},
                {"label": "Skip", "value": None}
            ]
        elif religion == "Muslim":
            return [
                {"label": "Sunni", "value": "Sunni"},
                {"label": "Shia", "value": "Shia"},
                {"label": "Sufi", "value": "Sufi"},
                {"label": "Ahmadiyya", "value": "Ahmadiyya"},
                {"label": "Don't follow any specific sect", "value": "None"},
                {"label": "Skip", "value": None}
            ]
        elif religion == "Christian":
            return [
                {"label": "Catholic", "value": "Catholic"},
                {"label": "Protestant", "value": "Protestant"},
                {"label": "Orthodox", "value": "Orthodox"},
                {"label": "Evangelical", "value": "Evangelical"},
                {"label": "Other", "value": "Other"}
            ]
        elif religion == "Sikh":
            return [
                {"label": "Amritdhari (baptized)", "value": "Amritdhari"},
                {"label": "Keshdhari (uncut hair)", "value": "Keshdhari"},
                {"label": "Sehajdhari", "value": "Sehajdhari"},
                {"label": "Don't follow any specific tradition", "value": "None"}
            ]
        elif religion == "Jain":
            return [
                {"label": "Digambar", "value": "Digambar"},
                {"label": "Shwetambar", "value": "Shwetambar"},
                {"label": "Don't follow any specific tradition", "value": "None"}
            ]
        else:
            # For Buddhist, Parsi, Jewish, Atheist, etc. → return None to skip
            return None
    
    elif question_num == 24:
        # Caste/community options based on religion
        religion = answers.get("religion")
        
        if religion == "Hindu":
            return [
                {"label": "Brahmin", "value": "Brahmin"},
                {"label": "Rajput / Kshatriya", "value": "Kshatriya / Rajput"},
                {"label": "Baniya / Vaishya", "value": "Vaishya / Baniya"},
                {"label": "Kayastha", "value": "Kayastha"},
                {"label": "Maratha", "value": "Maratha"},
                {"label": "Reddy", "value": "Reddy"},
                {"label": "Nair", "value": "Nair"},
                {"label": "Ezhava", "value": "Ezhava"},
                {"label": "SC", "value": "Scheduled Caste (SC)"},
                {"label": "ST", "value": "Scheduled Tribe (ST)"},
                {"label": "OBC", "value": "OBC (Other Backward Class)"},
                {"label": "Other community", "value": "Other"},
                {"label": "Skip", "value": None}
            ]
        elif religion == "Jain":
            return [
                {"label": "Digambar", "value": "Digambar"},
                {"label": "Shwetambar", "value": "Shwetambar"},
                {"label": "Agarwal", "value": "Agarwal"},
                {"label": "Oswal", "value": "Oswal"},
                {"label": "Porwal", "value": "Porwal"},
                {"label": "Other community", "value": "Other"},
                {"label": "Skip", "value": None}
            ]
        elif religion == "Sikh":
            return [
                {"label": "Jat", "value": "Jat"},
                {"label": "Khatri", "value": "Khatri"},
                {"label": "Arora", "value": "Arora"},
                {"label": "Ramgarhia", "value": "Ramgarhia"},
                {"label": "Saini", "value": "Saini"},
                {"label": "SC", "value": "Scheduled Caste (SC)"},
                {"label": "Other community", "value": "Other"},
                {"label": "Skip", "value": None}
            ]
        elif religion == "Buddhist":
            return [
                {"label": "SC", "value": "Scheduled Caste (SC)"},
                {"label": "ST", "value": "Scheduled Tribe (ST)"},
                {"label": "OBC", "value": "OBC (Other Backward Class)"},
                {"label": "Other community", "value": "Other"},
                {"label": "Skip", "value": None}
            ]
        else:
            # Muslim, Christian, Parsi, etc. - caste doesn't apply
            return None
    
    return None


def validate_conditional_logic(test_paths: list) -> Dict:
    """
    Test conditional logic with known user paths.
    Returns validation results.
    """
    results = {}
    
    for path in test_paths:
        path_name = path['name']
        answers = path['answers']
        expected_questions = path['expected_questions']
        
        # Simulate progression through questions
        asked_questions = []
        current_q = 1
        
        while current_q <= 77:
            if not should_skip_question(current_q, answers):
                asked_questions.append(current_q)
            current_q = get_next_question(answers, current_q)
            
            # Safety break
            if len(asked_questions) > 80:
                break
        
        # Compare
        matches = asked_questions == expected_questions
        results[path_name] = {
            "passed": matches,
            "expected": expected_questions,
            "actual": asked_questions,
            "expected_count": len(expected_questions),
            "actual_count": len(asked_questions)
        }
    
    return results


# Test paths for validation
TEST_PATHS = [
    {
        "name": "Hindu, never married, India",
        "answers": {
            "marital_status": "Never married",
            "residency_type": "Indian citizen (in India)",
            "religion": "Hindu"
        },
        "expected_questions": list(range(1, 5)) + list(range(6, 10)) + [10, 12] + 
                             list(range(13, 18)) + list(range(18, 78))
    },
    {
        "name": "Muslim, never married, India",
        "answers": {
            "marital_status": "Never married",
            "residency_type": "Indian citizen (in India)",
            "religion": "Muslim"
        },
        "expected_questions": list(range(1, 5)) + list(range(6, 10)) + [10, 12] + 
                             list(range(13, 17)) + list(range(18, 22)) + [25, 26] + 
                             list(range(28, 78))
    },
    {
        "name": "NRI Hindu, never married, abroad",
        "answers": {
            "marital_status": "Never married",
            "residency_type": "NRI",
            "religion": "Hindu"
        },
        "expected_questions": list(range(1, 5)) + list(range(6, 12)) + 
                             list(range(13, 18)) + list(range(18, 78))
    },
    {
        "name": "Divorced Hindu, has children, India",
        "answers": {
            "marital_status": "Divorced",
            "residency_type": "Indian citizen (in India)",
            "religion": "Hindu",
            "children_intent": "Already have"
        },
        "expected_questions": list(range(1, 10)) + [10, 12] + list(range(13, 78))
    }
]


if __name__ == "__main__":
    # Run validation tests
    print("Running conditional logic validation tests...\n")
    results = validate_conditional_logic(TEST_PATHS)
    
    for path_name, result in results.items():
        status = "✓ PASS" if result['passed'] else "✗ FAIL"
        print(f"{status} {path_name}")
        print(f"  Expected {result['expected_count']} questions, got {result['actual_count']}")
        
        if not result['passed']:
            expected_set = set(result['expected'])
            actual_set = set(result['actual'])
            missing = expected_set - actual_set
            extra = actual_set - expected_set
            
            if missing:
                print(f"  Missing questions: {sorted(missing)}")
            if extra:
                print(f"  Extra questions: {sorted(extra)}")
        print()
