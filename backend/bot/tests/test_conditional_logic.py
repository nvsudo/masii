"""
Unit Tests for Conditional Logic — 36 Gunas
Tests tree branching, skip logic, and section routing
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from conditional_logic import (
    should_skip_question,
    should_ask_sub_question,
    get_next_question,
    get_section_for_question,
    get_completion_percentage,
    get_conditional_options,
    get_transition_key,
    validate_conditional_logic,
    TEST_PATHS,
)


class TestShouldSkipQuestion:
    """Test guna skip logic for tree branches"""

    def test_guna_11_skip_for_buddhist(self):
        """Practice skipped for Buddhist"""
        assert should_skip_question(11, {"religion": "Buddhist"}) is True

    def test_guna_11_skip_for_none(self):
        """Practice skipped for None/Atheist"""
        assert should_skip_question(11, {"religion": "None"}) is True

    def test_guna_11_show_for_hindu(self):
        assert should_skip_question(11, {"religion": "Hindu"}) is False

    def test_guna_11_show_for_muslim(self):
        assert should_skip_question(11, {"religion": "Muslim"}) is False

    def test_guna_11_show_for_jain(self):
        assert should_skip_question(11, {"religion": "Jain"}) is False

    def test_guna_12_skip_for_sikh(self):
        """Sect skipped for Sikh (practice covers it)"""
        assert should_skip_question(12, {"religion": "Sikh"}) is True

    def test_guna_12_skip_for_buddhist(self):
        assert should_skip_question(12, {"religion": "Buddhist"}) is True

    def test_guna_12_show_for_hindu(self):
        assert should_skip_question(12, {"religion": "Hindu"}) is False

    def test_guna_12_show_for_muslim(self):
        assert should_skip_question(12, {"religion": "Muslim"}) is False

    def test_guna_13_skip_for_muslim(self):
        """Caste skipped for Muslim"""
        assert should_skip_question(13, {"religion": "Muslim"}) is True

    def test_guna_13_skip_for_christian(self):
        assert should_skip_question(13, {"religion": "Christian"}) is True

    def test_guna_13_show_for_hindu(self):
        assert should_skip_question(13, {"religion": "Hindu"}) is False

    def test_guna_13_show_for_jain(self):
        assert should_skip_question(13, {"religion": "Jain"}) is False

    def test_guna_13_show_for_sikh(self):
        assert should_skip_question(13, {"religion": "Sikh"}) is False

    def test_guna_21_skip_if_no_children(self):
        """Kids timeline skipped if children_intent = No"""
        assert should_skip_question(21, {"children_intent": "No"}) is True

    def test_guna_21_show_if_yes(self):
        assert should_skip_question(21, {"children_intent": "Yes"}) is False

    def test_guna_21_show_if_open(self):
        assert should_skip_question(21, {"children_intent": "Open"}) is False

    def test_non_conditional_gunas_never_skip(self):
        """Non-conditional gunas should never skip"""
        for q in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20,
                  22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]:
            assert should_skip_question(q, {}) is False, f"Guna {q} should not skip"


class TestShouldAskSubQuestion:
    """Test sub-question conditional logic"""

    def test_children_existing_if_divorced(self):
        assert should_ask_sub_question("children_existing", {"marital_status": "Divorced"}) is True

    def test_children_existing_if_widowed(self):
        assert should_ask_sub_question("children_existing", {"marital_status": "Widowed"}) is True

    def test_children_existing_skip_if_never_married(self):
        assert should_ask_sub_question("children_existing", {"marital_status": "Never married"}) is False

    def test_caste_importance_if_caste_given(self):
        assert should_ask_sub_question("caste_importance", {"caste_community": "Brahmin"}) is True

    def test_caste_importance_skip_if_prefer_not_to_say(self):
        assert should_ask_sub_question("caste_importance", {"caste_community": "Prefer not to say"}) is False

    def test_caste_importance_skip_if_no_caste(self):
        assert should_ask_sub_question("caste_importance", {"caste_community": None}) is False


class TestGetNextQuestion:
    def test_simple_progression(self):
        assert get_next_question({}, 1) == 2
        assert get_next_question({}, 35) == 36

    def test_skip_all_religion_conditionals_for_buddhist(self):
        answers = {"religion": "Buddhist"}
        # Buddhist skips 11 (practice), 12 (sect), 13 (caste) → lands on 14
        assert get_next_question(answers, 10) == 14

    def test_skip_religion_conditionals_with_no_religion(self):
        # No religion set → skips 11, 12, 13
        assert get_next_question({}, 10) == 14

    def test_skip_caste_for_muslim(self):
        answers = {"religion": "Muslim"}
        assert get_next_question(answers, 12) == 14  # 13 skipped

    def test_no_skip_for_hindu(self):
        answers = {"religion": "Hindu"}
        assert get_next_question(answers, 10) == 11
        assert get_next_question(answers, 11) == 12
        assert get_next_question(answers, 12) == 13

    def test_skip_kids_timeline_if_no(self):
        answers = {"children_intent": "No"}
        assert get_next_question(answers, 20) == 22  # 21 skipped

    def test_end_at_37(self):
        assert get_next_question({}, 36) == 37  # Beyond 36 = done


class TestGetSectionForQuestion:
    def test_intro(self):
        assert get_section_for_question(0) == "intro"

    def test_niyat(self):
        for q in range(1, 5):
            assert get_section_for_question(q) == "niyat"

    def test_parichay(self):
        for q in range(5, 10):
            assert get_section_for_question(q) == "parichay"

    def test_dharam(self):
        for q in range(10, 17):
            assert get_section_for_question(q) == "dharam"

    def test_parivar(self):
        for q in range(17, 22):
            assert get_section_for_question(q) == "parivar"

    def test_jeevan_shaili(self):
        for q in range(22, 29):
            assert get_section_for_question(q) == "jeevan_shaili"

    def test_soch(self):
        for q in range(29, 37):
            assert get_section_for_question(q) == "soch"

    def test_complete(self):
        assert get_section_for_question(37) == "complete"
        assert get_section_for_question(40) == "complete"


class TestGetCompletionPercentage:
    def test_no_answers(self):
        assert get_completion_percentage({}, []) == 0.0

    def test_all_answered(self):
        answers = {f"q{i}": f"a{i}" for i in range(1, 37)}
        assert get_completion_percentage(answers, []) == 100.0

    def test_half_answered(self):
        answers = {f"q{i}": f"a{i}" for i in range(1, 19)}
        pct = get_completion_percentage(answers, [])
        assert 49 < pct < 51

    def test_with_skips(self):
        answers = {f"q{i}": f"a{i}" for i in range(1, 34)}
        skip = [11, 12, 13]  # 3 skipped
        pct = get_completion_percentage(answers, skip)
        assert pct == 100.0  # 33 out of 33 required


class TestGetConditionalOptions:
    def test_guna_11_hindu_practice(self):
        opts = get_conditional_options(11, {"religion": "Hindu"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert any("puja" in l.lower() for l in labels)

    def test_guna_11_muslim_practice(self):
        opts = get_conditional_options(11, {"religion": "Muslim"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert any("prayer" in l.lower() for l in labels)

    def test_guna_12_hindu_sects(self):
        opts = get_conditional_options(12, {"religion": "Hindu"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert "Shaiva" in labels

    def test_guna_12_muslim_sects(self):
        opts = get_conditional_options(12, {"religion": "Muslim"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert "Sunni" in labels

    def test_guna_13_hindu_castes(self):
        opts = get_conditional_options(13, {"religion": "Hindu"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert "Brahmin" in labels

    def test_guna_13_muslim_none(self):
        assert get_conditional_options(13, {"religion": "Muslim"}) is None

    def test_guna_22_diet_jain(self):
        opts = get_conditional_options(22, {"religion": "Jain"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert any("onion" in l.lower() for l in labels)

    def test_guna_22_diet_muslim(self):
        opts = get_conditional_options(22, {"religion": "Muslim"})
        assert opts is not None
        labels = [o["label"] for o in opts]
        assert any("halal" in l.lower() for l in labels)

    def test_non_conditional_guna_returns_none(self):
        assert get_conditional_options(1, {"religion": "Hindu"}) is None
        assert get_conditional_options(5, {}) is None
        assert get_conditional_options(29, {}) is None


class TestTransitionKeys:
    def test_entering_niyat(self):
        assert get_transition_key("niyat", "intro") == "niyat_buyin"

    def test_entering_parichay(self):
        assert get_transition_key("parichay", "niyat") == "after_niyat"

    def test_entering_dharam(self):
        assert get_transition_key("dharam", "parichay") == "after_parichay"

    def test_entering_soch(self):
        assert get_transition_key("soch", "jeevan_shaili") == "soch_buyin"

    def test_same_section_no_transition(self):
        assert get_transition_key("dharam", "dharam") is None


class TestValidateConditionalLogic:
    def test_all_paths_defined(self):
        assert len(TEST_PATHS) == 4

    def test_validation_runs(self):
        results = validate_conditional_logic()
        assert len(results) == 4
        for name, result in results.items():
            assert "passed" in result

    def test_no_infinite_loops(self):
        """Simulate progression — should never exceed 36"""
        test_answers_sets = [
            {"religion": "Hindu", "children_intent": "Yes"},
            {"religion": "Muslim", "children_intent": "Yes"},
            {"religion": "Buddhist", "children_intent": "No"},
            {"religion": "Jain", "children_intent": "Open"},
        ]
        for answers in test_answers_sets:
            q = 1
            count = 0
            while q <= 36:
                if not should_skip_question(q, answers):
                    count += 1
                q = get_next_question(answers, q)
                if count > 40:
                    pytest.fail(f"Possible infinite loop with {answers}")
            assert count <= 36


class TestEdgeCases:
    def test_empty_answers(self):
        assert should_skip_question(11, {}) is True  # No religion → skip practice
        assert get_next_question({}, 1) == 2

    def test_guna_36_next(self):
        assert get_next_question({}, 36) == 37

    def test_beyond_36(self):
        assert get_next_question({}, 37) == 38
