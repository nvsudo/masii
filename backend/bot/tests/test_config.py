"""
Config Validation Tests — 36 Gunas
Validates all 36 questions are properly configured
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    INTRO_MESSAGES,
    INTENT_MESSAGE,
    PROXY_MESSAGES,
    QUESTIONS,
    SUB_QUESTIONS,
    SECTION_TRANSITIONS,
    CLOSE_MESSAGE,
    ERROR_MESSAGES,
    RESUME_PROMPT,
    RESUME_BUTTONS,
    VALIDATION_RULES,
    TOTAL_GUNAS,
    get_countries,
    get_states_india,
    get_birth_years,
    get_practice_by_religion,
    get_sects_by_religion,
    get_castes_by_religion,
    get_diet_by_religion,
    OnboardingSection,
)


class TestIntroMessages:
    def test_intro_messages_exist(self):
        assert INTRO_MESSAGES is not None
        assert len(INTRO_MESSAGES) == 3  # 3 intro messages before intent

    def test_intro_message_structure(self):
        for i, intro in enumerate(INTRO_MESSAGES):
            assert "text" in intro, f"Intro {i} missing 'text'"
            assert "button" in intro, f"Intro {i} missing 'button'"
            assert len(intro["text"]) > 0
            assert len(intro["button"]) > 0

    def test_intent_message_exists(self):
        assert INTENT_MESSAGE is not None
        assert "text" in INTENT_MESSAGE
        assert "options" in INTENT_MESSAGE
        assert len(INTENT_MESSAGE["options"]) == 2

    def test_proxy_messages_exist(self):
        assert PROXY_MESSAGES is not None
        assert len(PROXY_MESSAGES) == 2
        for msg in PROXY_MESSAGES:
            assert "text" in msg
            assert "options" in msg


class TestQuestionConfiguration:
    def test_all_36_gunas_exist(self):
        for i in range(1, 37):
            assert i in QUESTIONS, f"Guna {i} not found in QUESTIONS"

    def test_no_extra_questions(self):
        for q_num in QUESTIONS.keys():
            assert 1 <= q_num <= 36, f"Invalid question number: {q_num}"

    def test_total_gunas_constant(self):
        assert TOTAL_GUNAS == 36

    def test_question_required_fields(self):
        required_fields = ["text", "type", "field", "db_table"]
        for q_num, question in QUESTIONS.items():
            # location_tree and two_step_date have 'text' in sub-steps
            if question["type"] in ("location_tree", "two_step_date"):
                assert "step1" in question
                continue
            for field in required_fields:
                assert field in question, f"Guna {q_num} missing field: {field}"

    def test_question_types_valid(self):
        valid_types = ["single_select", "text_input", "two_step_date", "location_tree"]
        for q_num, question in QUESTIONS.items():
            assert question["type"] in valid_types, f"Guna {q_num} invalid type: {question['type']}"

    def test_single_select_has_options(self):
        for q_num, question in QUESTIONS.items():
            if question["type"] == "single_select":
                assert "options" in question, f"Guna {q_num} missing options"
                options = question["options"]
                assert isinstance(options, (list, str)), f"Guna {q_num} options invalid"
                if isinstance(options, list):
                    assert len(options) > 0, f"Guna {q_num} empty options"

    def test_text_input_has_placeholder(self):
        for q_num, question in QUESTIONS.items():
            if question["type"] == "text_input":
                assert "placeholder" in question, f"Guna {q_num} missing placeholder"

    def test_option_structure(self):
        for q_num, question in QUESTIONS.items():
            if "options" in question and isinstance(question["options"], list):
                for i, opt in enumerate(question["options"]):
                    assert "label" in opt, f"Guna {q_num} opt {i} missing 'label'"
                    assert "value" in opt, f"Guna {q_num} opt {i} missing 'value'"

    def test_db_table_valid(self):
        valid_tables = ["users", "preferences", "signals"]
        for q_num, question in QUESTIONS.items():
            if question["type"] == "location_tree":
                continue
            assert question["db_table"] in valid_tables, f"Guna {q_num} invalid db_table: {question['db_table']}"


class TestSubQuestions:
    def test_sub_questions_exist(self):
        assert "children_existing" in SUB_QUESTIONS
        assert "caste_importance" in SUB_QUESTIONS

    def test_sub_question_structure(self):
        for key, sub_q in SUB_QUESTIONS.items():
            assert "field" in sub_q
            assert "db_table" in sub_q
            assert "text" in sub_q
            assert "type" in sub_q
            assert "after_guna" in sub_q
            assert "options" in sub_q

    def test_children_existing_after_guna_9(self):
        assert SUB_QUESTIONS["children_existing"]["after_guna"] == 9

    def test_caste_importance_after_guna_13(self):
        assert SUB_QUESTIONS["caste_importance"]["after_guna"] == 13


class TestSections:
    def test_section_enum(self):
        required = ["INTRO", "NIYAT", "PARICHAY", "DHARAM", "PARIVAR", "JEEVAN_SHAILI", "SOCH", "COMPLETE"]
        for section in required:
            assert hasattr(OnboardingSection, section), f"Missing section: {section}"

    def test_section_transitions_exist(self):
        assert SECTION_TRANSITIONS is not None
        expected_keys = [
            "niyat_buyin", "after_niyat", "after_parichay",
            "after_dharam", "after_parivar", "soch_buyin",
        ]
        for key in expected_keys:
            assert key in SECTION_TRANSITIONS, f"Missing transition: {key}"


class TestGunaDistribution:
    def test_niyat_gunas(self):
        """Gunas 1-4 are Niyat (Intent)"""
        for q in range(1, 5):
            assert QUESTIONS[q]["section"] == "niyat"

    def test_parichay_gunas(self):
        """Gunas 5-9 are Parichay (Introduction)"""
        for q in range(5, 10):
            assert QUESTIONS[q]["section"] == "parichay"

    def test_dharam_gunas(self):
        """Gunas 10-16 are Dharam (Faith & Culture)"""
        for q in range(10, 17):
            assert QUESTIONS[q]["section"] == "dharam"

    def test_parivar_gunas(self):
        """Gunas 17-21 are Parivar (Family)"""
        for q in range(17, 22):
            assert QUESTIONS[q]["section"] == "parivar"

    def test_jeevan_shaili_gunas(self):
        """Gunas 22-28 are Jeevan Shaili (Lifestyle)"""
        for q in range(22, 29):
            assert QUESTIONS[q]["section"] == "jeevan_shaili"

    def test_soch_gunas(self):
        """Gunas 29-36 are Soch (Values)"""
        for q in range(29, 37):
            assert QUESTIONS[q]["section"] == "soch"


class TestDynamicOptions:
    def test_get_countries(self):
        countries = get_countries()
        assert len(countries) > 0
        labels = [c["label"] for c in countries]
        assert "USA" in labels
        assert "UK" in labels

    def test_get_states_india(self):
        states = get_states_india()
        assert len(states) > 0
        labels = [s["label"] for s in states]
        assert "Maharashtra" in labels
        assert any("Delhi" in s for s in labels)

    def test_get_birth_years(self):
        years = get_birth_years()
        assert len(years) > 0
        values = [y["value"] for y in years]
        assert "2000" in values
        assert "1990" in values

    def test_practice_by_religion_hindu(self):
        options = get_practice_by_religion("Hindu")
        assert options is not None
        assert len(options) >= 3

    def test_practice_by_religion_muslim(self):
        options = get_practice_by_religion("Muslim")
        assert options is not None
        labels = [o["label"] for o in options]
        assert any("5 daily prayers" in l for l in labels)

    def test_practice_by_religion_buddhist_none(self):
        assert get_practice_by_religion("Buddhist") is None

    def test_practice_by_religion_none_none(self):
        assert get_practice_by_religion("None") is None

    def test_sects_hindu(self):
        sects = get_sects_by_religion("Hindu")
        assert sects is not None
        labels = [s["label"] for s in sects]
        assert "Shaiva" in labels

    def test_sects_muslim(self):
        sects = get_sects_by_religion("Muslim")
        assert sects is not None
        labels = [s["label"] for s in sects]
        assert "Sunni" in labels
        assert "Shia" in labels

    def test_sects_sikh_none(self):
        """Sikh practice already covers Amritdhari/Keshdhari — no sects"""
        assert get_sects_by_religion("Sikh") is None

    def test_castes_hindu(self):
        castes = get_castes_by_religion("Hindu")
        assert castes is not None
        labels = [c["label"] for c in castes]
        assert "Brahmin" in labels

    def test_castes_muslim_none(self):
        """Muslim has no caste"""
        assert get_castes_by_religion("Muslim") is None

    def test_castes_christian_none(self):
        assert get_castes_by_religion("Christian") is None

    def test_castes_jain(self):
        castes = get_castes_by_religion("Jain")
        assert castes is not None
        labels = [c["label"] for c in castes]
        assert "Oswal" in labels

    def test_castes_sikh(self):
        castes = get_castes_by_religion("Sikh")
        assert castes is not None
        labels = [c["label"] for c in castes]
        assert "Jat" in labels

    def test_diet_hindu(self):
        diet = get_diet_by_religion("Hindu")
        labels = [d["label"] for d in diet]
        assert "Vegetarian" in labels
        assert "Non-veg" in labels

    def test_diet_jain(self):
        diet = get_diet_by_religion("Jain")
        labels = [d["label"] for d in diet]
        assert any("onion" in l.lower() for l in labels)

    def test_diet_muslim(self):
        diet = get_diet_by_religion("Muslim")
        labels = [d["label"] for d in diet]
        assert any("halal" in l.lower() for l in labels)


class TestCloseMessage:
    def test_close_message_exists(self):
        assert CLOSE_MESSAGE is not None
        assert len(CLOSE_MESSAGE) > 0
        assert "{name}" in CLOSE_MESSAGE


class TestErrorMessages:
    def test_error_messages_exist(self):
        assert "button_expected" in ERROR_MESSAGES
        assert "invalid_input" in ERROR_MESSAGES


class TestResumePrompt:
    def test_resume_prompt(self):
        assert "{name}" in RESUME_PROMPT
        assert "{current}" in RESUME_PROMPT
        assert "{total}" in RESUME_PROMPT

    def test_resume_buttons(self):
        assert len(RESUME_BUTTONS) == 2


class TestSpecificGunas:
    def test_guna_1_intent(self):
        q = QUESTIONS[1]
        assert q["field"] == "relationship_intent"
        assert q["type"] == "single_select"

    def test_guna_5_name(self):
        q = QUESTIONS[5]
        assert q["field"] == "first_name"
        assert q["type"] == "text_input"

    def test_guna_7_dob(self):
        q = QUESTIONS[7]
        assert q["type"] == "two_step_date"
        assert "step1" in q
        assert "step2" in q

    def test_guna_8_location(self):
        q = QUESTIONS[8]
        assert q["type"] == "location_tree"
        assert "step1" in q
        assert "step2_india" in q
        assert "step2_abroad" in q
        assert "step3" in q

    def test_guna_10_religion(self):
        q = QUESTIONS[10]
        assert q["field"] == "religion"
        labels = [o["label"] for o in q["options"]]
        assert "Hindu" in labels
        assert "Muslim" in labels
        assert "Sikh" in labels

    def test_guna_29_open_text(self):
        q = QUESTIONS[29]
        assert q["type"] == "text_input"
        assert q["field"] == "what_matters"

    def test_guna_36_the_one_thing(self):
        q = QUESTIONS[36]
        assert q["type"] == "text_input"
        assert q["field"] == "the_one_thing"
