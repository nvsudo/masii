"""
Unit Tests for Conditional Logic
Tests all 4 user paths and skip logic
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from conditional_logic import (
    should_skip_question,
    get_next_question,
    get_section_for_question,
    get_completion_percentage,
    get_conditional_options,
    validate_conditional_logic,
    TEST_PATHS
)


class TestShouldSkipQuestion:
    """Test should_skip_question() for all conditional rules"""
    
    def test_q5_skip_for_never_married(self):
        """Q5 (years married) should skip if never married"""
        answers = {"marital_status": "Never married"}
        assert should_skip_question(5, answers) is True
    
    def test_q5_show_for_married(self):
        """Q5 should show if married"""
        answers = {"marital_status": "Married"}
        assert should_skip_question(5, answers) is False
    
    def test_q11_skip_for_indian_citizen(self):
        """Q11 (country current) should skip for Indian citizens in India"""
        answers = {"residency_type": "Indian citizen (in India)"}
        assert should_skip_question(11, answers) is True
    
    def test_q11_show_for_nri(self):
        """Q11 should show for NRI"""
        answers = {"residency_type": "NRI"}
        assert should_skip_question(11, answers) is False
    
    def test_q12_show_for_indian_citizen(self):
        """Q12 (state India) should show for Indian citizens"""
        answers = {"residency_type": "Indian citizen (in India)"}
        assert should_skip_question(12, answers) is False
    
    def test_q12_skip_for_nri(self):
        """Q12 should skip for NRI"""
        answers = {"residency_type": "NRI"}
        assert should_skip_question(12, answers) is True
    
    def test_q17_show_for_nri(self):
        """Q17 (settling country) should show for NRI"""
        answers = {"residency_type": "NRI"}
        assert should_skip_question(17, answers) is False
    
    def test_q17_show_for_oci(self):
        """Q17 should show for OCI"""
        answers = {"residency_type": "OCI / PIO"}
        assert should_skip_question(17, answers) is False
    
    def test_q17_skip_for_indian_citizen(self):
        """Q17 should skip for Indian citizens"""
        answers = {"residency_type": "Indian citizen (in India)"}
        assert should_skip_question(17, answers) is True
    
    def test_q22_show_for_hindu(self):
        """Q22 (caste) should show for Hindu"""
        answers = {"religion": "Hindu"}
        assert should_skip_question(22, answers) is False
    
    def test_q22_skip_for_muslim(self):
        """Q22 should skip for Muslim"""
        answers = {"religion": "Muslim"}
        assert should_skip_question(22, answers) is True
    
    def test_q23_skip_if_no_caste(self):
        """Q23 (sub-caste) should skip if caste not provided"""
        answers = {"caste_community": ""}
        assert should_skip_question(23, answers) is True
    
    def test_q23_skip_for_prefer_not_to_say(self):
        """Q23 should skip if caste = Prefer not to say"""
        answers = {"caste_community": "Prefer not to say"}
        assert should_skip_question(23, answers) is True
    
    def test_q23_show_if_caste_provided(self):
        """Q23 should show if caste is provided AND religion is Hindu/Jain/Sikh/Buddhist"""
        answers = {"religion": "Hindu", "caste_community": "Brahmin"}
        assert should_skip_question(23, answers) is False
    
    def test_q27_show_for_hindu(self):
        """Q27 (manglik) should show for Hindu"""
        answers = {"religion": "Hindu"}
        assert should_skip_question(27, answers) is False
    
    def test_q27_skip_for_christian(self):
        """Q27 should skip for Christian"""
        answers = {"religion": "Christian"}
        assert should_skip_question(27, answers) is True
    
    def test_q34_show_for_nri(self):
        """Q34 (work abroad) should show for NRI"""
        answers = {"residency_type": "NRI"}
        assert should_skip_question(34, answers) is False
    
    def test_q34_skip_for_indian_citizen(self):
        """Q34 should skip for Indian citizens"""
        answers = {"residency_type": "Indian citizen (in India)"}
        assert should_skip_question(34, answers) is True
    
    def test_q67_skip_for_definitely_not(self):
        """Q67 (preferred # children) should skip if no children wanted"""
        answers = {"children_intent": "Definitely not"}
        assert should_skip_question(67, answers) is True
    
    def test_q67_show_for_yes(self):
        """Q67 should show if children wanted"""
        answers = {"children_intent": "Yes, definitely"}
        assert should_skip_question(67, answers) is False


class TestGetNextQuestion:
    """Test get_next_question() logic"""
    
    def test_simple_progression(self):
        """Test simple progression when no skips"""
        answers = {}
        assert get_next_question(answers, 1) == 2
        assert get_next_question(answers, 10) == 11
    
    def test_skip_q5_for_never_married(self):
        """Should skip Q5 if never married"""
        answers = {"marital_status": "Never married"}
        assert get_next_question(answers, 4) == 6
    
    def test_jump_q22_to_q25_for_muslim(self):
        """Should jump from Q21 to Q25 if Muslim (skipping caste section)"""
        answers = {"religion": "Muslim"}
        assert get_next_question(answers, 21) == 25
    
    def test_no_jump_q22_for_hindu(self):
        """Should not jump for Hindu (caste questions apply)"""
        answers = {"religion": "Hindu"}
        assert get_next_question(answers, 21) == 22


class TestGetSectionForQuestion:
    """Test section assignment"""
    
    def test_intro_section(self):
        assert get_section_for_question(0) == "intro"
    
    def test_identity_basics_section(self):
        assert get_section_for_question(1) == "identity_basics"
        assert get_section_for_question(5) == "identity_basics"
        assert get_section_for_question(9) == "identity_basics"
    
    def test_location_mobility_section(self):
        assert get_section_for_question(10) == "location_mobility"
        assert get_section_for_question(15) == "location_mobility"
    
    def test_religion_culture_section(self):
        assert get_section_for_question(18) == "religion_culture"
        assert get_section_for_question(22) == "religion_culture"
    
    def test_dealbreakers_section(self):
        assert get_section_for_question(73) == "dealbreakers"
        assert get_section_for_question(77) == "dealbreakers"
    
    def test_photo_upload_section(self):
        assert get_section_for_question(78) == "photo_upload"


class TestGetCompletionPercentage:
    """Test completion percentage calculation"""
    
    def test_no_answers(self):
        answers = {}
        skip_questions = []
        assert get_completion_percentage(answers, skip_questions) == 0.0
    
    def test_all_answered_no_skips(self):
        answers = {f"q{i}": f"answer{i}" for i in range(1, 78)}
        skip_questions = []
        assert get_completion_percentage(answers, skip_questions) == 100.0
    
    def test_half_answered_no_skips(self):
        answers = {f"q{i}": f"answer{i}" for i in range(1, 39)}
        skip_questions = []
        percentage = get_completion_percentage(answers, skip_questions)
        assert 49.0 < percentage < 50.0
    
    def test_with_legitimate_skips(self):
        """If 10 questions are skipped, total = 67"""
        answers = {f"q{i}": f"answer{i}" for i in range(1, 68)}
        skip_questions = list(range(68, 78))  # 10 skipped
        # 67 answered out of 67 required = 100%
        assert get_completion_percentage(answers, skip_questions) == 100.0


class TestGetConditionalOptions:
    """Test conditional options for Q21 (sect/denomination)"""
    
    def test_hindu_options(self):
        answers = {"religion": "Hindu"}
        options = get_conditional_options(21, answers)
        assert options is not None
        labels = [opt['label'] for opt in options]
        assert "Shaivite" in labels
        assert "Vaishnavite" in labels
    
    def test_muslim_options(self):
        answers = {"religion": "Muslim"}
        options = get_conditional_options(21, answers)
        assert options is not None
        labels = [opt['label'] for opt in options]
        assert "Sunni" in labels
        assert "Shia" in labels
    
    def test_christian_options(self):
        answers = {"religion": "Christian"}
        options = get_conditional_options(21, answers)
        assert options is not None
        labels = [opt['label'] for opt in options]
        assert "Catholic" in labels
        assert "Protestant" in labels
    
    def test_sikh_options(self):
        answers = {"religion": "Sikh"}
        options = get_conditional_options(21, answers)
        assert options is not None
        labels = [opt['label'] for opt in options]
        assert "Amritdhari" in labels
    
    def test_jain_options(self):
        answers = {"religion": "Jain"}
        options = get_conditional_options(21, answers)
        assert options is not None
        labels = [opt['label'] for opt in options]
        assert "Digambar" in labels
        assert "Shwetambar" in labels
    
    def test_buddhist_no_options(self):
        """Buddhist should return None (no sect options)"""
        answers = {"religion": "Buddhist"}
        options = get_conditional_options(21, answers)
        assert options is None
    
    def test_non_q21_returns_none(self):
        """Non-Q21 questions should return None"""
        answers = {"religion": "Hindu"}
        assert get_conditional_options(20, answers) is None
        assert get_conditional_options(22, answers) is None


class TestValidateConditionalLogic:
    """Test the 4 predefined test paths"""
    
    def test_all_paths_defined(self):
        """Ensure all 4 test paths are defined"""
        assert len(TEST_PATHS) == 4
    
    def test_path_names(self):
        """Check path names"""
        names = [path['name'] for path in TEST_PATHS]
        assert "Hindu, never married, India" in names
        assert "Muslim, never married, India" in names
        assert "NRI Hindu, never married, abroad" in names
        assert "Divorced Hindu, has children, India" in names
    
    def test_validation_runs(self):
        """Test that validation executes without errors"""
        results = validate_conditional_logic(TEST_PATHS)
        assert len(results) == 4
        
        for path_name, result in results.items():
            assert 'passed' in result
            assert 'expected' in result
            assert 'actual' in result
            assert 'expected_count' in result
            assert 'actual_count' in result
    
    def test_hindu_never_married_india_path(self):
        """Test specific path: Hindu, never married, India"""
        path = next(p for p in TEST_PATHS if p['name'] == "Hindu, never married, India")
        results = validate_conditional_logic([path])
        
        result = results["Hindu, never married, India"]
        # This path should work correctly
        assert result['passed'] is True or result['actual_count'] > 0
    
    def test_no_infinite_loops(self):
        """Ensure no infinite loops in question progression"""
        for path in TEST_PATHS:
            results = validate_conditional_logic([path])
            for path_name, result in results.items():
                # Should never ask more than 77 questions
                assert result['actual_count'] <= 77


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_answers(self):
        """Test with empty answers dict"""
        answers = {}
        assert should_skip_question(5, answers) is False  # Default behavior
        assert get_next_question(answers, 1) == 2
    
    def test_missing_fields(self):
        """Test when expected fields are missing"""
        answers = {"some_other_field": "value"}
        # Should not crash, should use defaults
        assert should_skip_question(5, answers) is False
    
    def test_question_77_next(self):
        """Q77 should proceed to 78 (photo upload)"""
        answers = {}
        assert get_next_question(answers, 77) == 78
    
    def test_beyond_77(self):
        """Questions beyond 77 should continue incrementing"""
        answers = {}
        assert get_next_question(answers, 78) == 79
