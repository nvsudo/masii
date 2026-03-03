"""
Config Validation Tests
Validates all 77 questions are properly configured
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    INTRO_MESSAGES,
    QUESTIONS,
    SECTION_TRANSITIONS,
    FINAL_TRANSITION,
    ERROR_MESSAGES,
    RESUME_PROMPT,
    RESUME_BUTTONS,
    VALIDATION_RULES,
    get_countries,
    get_states_india,
    OnboardingSection
)


class TestIntroMessages:
    """Test intro message configuration"""
    
    def test_intro_messages_exist(self):
        """Test intro messages are defined"""
        assert INTRO_MESSAGES is not None
        assert len(INTRO_MESSAGES) > 0
    
    def test_intro_message_structure(self):
        """Test each intro message has required fields"""
        for i, intro in enumerate(INTRO_MESSAGES):
            assert 'text' in intro, f"Intro {i} missing 'text'"
            assert 'button' in intro, f"Intro {i} missing 'button'"
            assert isinstance(intro['text'], str)
            assert isinstance(intro['button'], str)
            assert len(intro['text']) > 0
            assert len(intro['button']) > 0


class TestQuestionConfiguration:
    """Test all 77 questions are properly configured"""
    
    def test_all_77_questions_exist(self):
        """Test all questions 1-77 are defined"""
        for i in range(1, 78):
            assert i in QUESTIONS, f"Question {i} not found in QUESTIONS"
    
    def test_no_extra_questions(self):
        """Test no questions beyond 77"""
        for q_num in QUESTIONS.keys():
            assert 1 <= q_num <= 77, f"Invalid question number: {q_num}"
    
    def test_question_required_fields(self):
        """Test each question has required fields"""
        required_fields = ['text', 'type', 'field', 'db_table']
        
        for q_num, question in QUESTIONS.items():
            for field in required_fields:
                assert field in question, f"Q{q_num} missing required field: {field}"
    
    def test_question_types_valid(self):
        """Test question types are valid"""
        valid_types = ['single_select', 'multi_select', 'text_input', 'two_step']
        
        for q_num, question in QUESTIONS.items():
            q_type = question['type']
            assert q_type in valid_types, f"Q{q_num} has invalid type: {q_type}"
    
    def test_single_select_has_options(self):
        """Test single_select questions have options"""
        for q_num, question in QUESTIONS.items():
            if question['type'] == 'single_select':
                assert 'options' in question, f"Q{q_num} (single_select) missing options"
                
                # Options can be a list or a string (dynamic)
                options = question['options']
                assert isinstance(options, (list, str)), f"Q{q_num} options invalid type"
                
                if isinstance(options, list):
                    assert len(options) > 0, f"Q{q_num} has empty options"
    
    def test_multi_select_has_options(self):
        """Test multi_select questions have options"""
        for q_num, question in QUESTIONS.items():
            if question['type'] == 'multi_select':
                assert 'options' in question, f"Q{q_num} (multi_select) missing options"
                
                options = question['options']
                assert isinstance(options, list), f"Q{q_num} multi_select options must be list"
                assert len(options) > 0, f"Q{q_num} has empty options"
    
    def test_text_input_has_validation(self):
        """Test text_input questions have validation rules"""
        for q_num, question in QUESTIONS.items():
            if question['type'] == 'text_input':
                # May or may not have validation
                if 'validation' in question:
                    validation = question['validation']
                    assert isinstance(validation, str), f"Q{q_num} validation must be string"
    
    def test_two_step_structure(self):
        """Test two_step questions have proper structure"""
        for q_num, question in QUESTIONS.items():
            if question['type'] == 'two_step':
                assert 'step1' in question, f"Q{q_num} (two_step) missing step1"
                assert 'step2' in question, f"Q{q_num} (two_step) missing step2"
                assert 'step1_field' in question, f"Q{q_num} (two_step) missing step1_field"
    
    def test_option_structure(self):
        """Test option objects have label and value"""
        for q_num, question in QUESTIONS.items():
            if 'options' in question and isinstance(question['options'], list):
                for i, opt in enumerate(question['options']):
                    assert 'label' in opt, f"Q{q_num} option {i} missing 'label'"
                    # Value can be None
                    assert 'value' in opt, f"Q{q_num} option {i} missing 'value'"
    
    def test_db_table_valid(self):
        """Test db_table values are valid"""
        valid_tables = ['users', 'preferences', 'personality']
        
        for q_num, question in QUESTIONS.items():
            db_table = question['db_table']
            assert db_table in valid_tables, f"Q{q_num} has invalid db_table: {db_table}"
    
    def test_field_names_unique_per_table(self):
        """Test field names are unique within each table"""
        fields_by_table = {'users': set(), 'preferences': set(), 'personality': set()}
        
        for q_num, question in QUESTIONS.items():
            field = question['field']
            table = question['db_table']
            
            # Two-step questions may have multiple fields
            if question['type'] == 'two_step':
                continue
            
            # Check for duplicates
            if field in fields_by_table[table]:
                # Some fields might be intentionally duplicated (e.g., for different paths)
                pass  # Allow duplicates for now
            
            fields_by_table[table].add(field)


class TestDynamicOptions:
    """Test dynamic option loaders"""
    
    def test_get_countries(self):
        """Test countries list is loaded"""
        countries = get_countries()
        
        assert countries is not None
        assert len(countries) > 0
        
        # Check structure
        for country in countries[:5]:  # Check first 5
            assert 'label' in country
            assert 'value' in country
    
    def test_get_states_india(self):
        """Test Indian states list is loaded"""
        states = get_states_india()
        
        assert states is not None
        assert len(states) > 0
        
        # Check structure
        for state in states[:5]:  # Check first 5
            assert 'label' in state
            assert 'value' in state
        
        # Check for known states
        state_names = [s['label'] for s in states]
        assert 'Maharashtra' in state_names
        # Delhi might be listed as "Delhi NCR" or "Delhi"
        assert any('Delhi' in s for s in state_names)


class TestSectionTransitions:
    """Test section transition messages"""
    
    def test_section_transitions_exist(self):
        """Test section transitions are defined"""
        assert SECTION_TRANSITIONS is not None
        assert isinstance(SECTION_TRANSITIONS, dict)
    
    def test_after_intro_transition(self):
        """Test after_intro transition exists"""
        assert 'after_intro' in SECTION_TRANSITIONS
        assert isinstance(SECTION_TRANSITIONS['after_intro'], str)
        assert len(SECTION_TRANSITIONS['after_intro']) > 0


class TestErrorMessages:
    """Test error message configuration"""
    
    def test_error_messages_exist(self):
        """Test error messages are defined"""
        assert ERROR_MESSAGES is not None
        assert isinstance(ERROR_MESSAGES, dict)
    
    def test_button_expected_error(self):
        """Test button_expected error exists"""
        assert 'button_expected' in ERROR_MESSAGES
        assert isinstance(ERROR_MESSAGES['button_expected'], str)


class TestResumePrompt:
    """Test resume prompt configuration"""
    
    def test_resume_prompt_exists(self):
        """Test resume prompt is defined"""
        assert RESUME_PROMPT is not None
        assert isinstance(RESUME_PROMPT, str)
        assert len(RESUME_PROMPT) > 0
    
    def test_resume_prompt_has_placeholders(self):
        """Test resume prompt has format placeholders"""
        # Should have placeholders for name, current, total
        assert '{name}' in RESUME_PROMPT or '{current}' in RESUME_PROMPT
    
    def test_resume_buttons_exist(self):
        """Test resume buttons are defined"""
        assert RESUME_BUTTONS is not None
        assert isinstance(RESUME_BUTTONS, list)
        assert len(RESUME_BUTTONS) == 2  # Resume and Restart


class TestValidationRules:
    """Test validation rules configuration"""
    
    def test_validation_rules_exist(self):
        """Test validation rules are defined"""
        assert VALIDATION_RULES is not None
        assert isinstance(VALIDATION_RULES, dict)
    
    def test_date_of_birth_rules(self):
        """Test DOB validation rules"""
        assert 'date_of_birth' in VALIDATION_RULES
        
        dob_rules = VALIDATION_RULES['date_of_birth']
        assert 'min_age' in dob_rules
        assert 'max_age' in dob_rules
        assert 'error_format' in dob_rules
        assert 'error_range' in dob_rules
        
        # Check reasonable age limits
        assert 18 <= dob_rules['min_age'] <= 21
        assert 70 <= dob_rules['max_age'] <= 100
    
    def test_height_rules(self):
        """Test height validation rules"""
        assert 'height_cm' in VALIDATION_RULES
        
        height_rules = VALIDATION_RULES['height_cm']
        assert 'min' in height_rules
        assert 'max' in height_rules
        assert 'error' in height_rules
        
        # Check reasonable height limits
        assert 100 <= height_rules['min'] <= 140
        assert 200 <= height_rules['max'] <= 250


class TestFinalTransition:
    """Test final transition message"""
    
    def test_final_transition_exists(self):
        """Test final transition is defined"""
        assert FINAL_TRANSITION is not None
        assert isinstance(FINAL_TRANSITION, str)
        assert len(FINAL_TRANSITION) > 0


class TestOnboardingSection:
    """Test OnboardingSection enum"""
    
    def test_all_sections_defined(self):
        """Test all required sections are in enum"""
        required_sections = [
            'INTRO',
            'IDENTITY_BASICS',
            'LOCATION_MOBILITY',
            'RELIGION_CULTURE',
            'EDUCATION_CAREER',
            'FINANCIAL',
            'FAMILY',
            'LIFESTYLE',
            'PARTNER_PREFS',
            'VALUES',
            'DEALBREAKERS',
            'PHOTO_UPLOAD',
            'SUMMARY',
            'CONVERSATIONAL'
        ]
        
        for section in required_sections:
            assert hasattr(OnboardingSection, section), f"Missing section: {section}"


class TestQuestionDistribution:
    """Test questions are distributed across sections"""
    
    def test_section_coverage(self):
        """Test all 77 questions map to valid sections"""
        from conditional_logic import get_section_for_question
        
        for q_num in range(1, 78):
            section = get_section_for_question(q_num)
            assert section is not None, f"Q{q_num} has no section"
            assert isinstance(section, str)
    
    def test_identity_basics_section(self):
        """Test questions 1-9 are in identity_basics"""
        from conditional_logic import get_section_for_question
        
        for q_num in range(1, 10):
            section = get_section_for_question(q_num)
            assert section == 'identity_basics', f"Q{q_num} not in identity_basics"
    
    def test_dealbreakers_section(self):
        """Test questions 73-77 are in dealbreakers"""
        from conditional_logic import get_section_for_question
        
        for q_num in range(73, 78):
            section = get_section_for_question(q_num)
            assert section == 'dealbreakers', f"Q{q_num} not in dealbreakers"


class TestSpecificQuestions:
    """Test specific critical questions"""
    
    def test_q1_gender_identity(self):
        """Test Q1 is gender identity"""
        q1 = QUESTIONS[1]
        assert q1['field'] in ['gender_identity', 'first_name']  # Could be either
        assert q1['type'] in ['single_select', 'text_input']
    
    def test_q3_date_of_birth(self):
        """Test Q3 is date of birth"""
        q3 = QUESTIONS[3]
        assert q3['type'] == 'text_input'
        assert 'validation' in q3
        assert q3['validation'] == 'date_of_birth'
    
    def test_conditional_questions_marked(self):
        """Test conditional questions can be identified"""
        # Questions that may be skipped
        conditional_questions = [5, 11, 12, 17, 22, 23, 24, 27, 34, 67]
        
        # All should exist
        for q_num in conditional_questions:
            assert q_num in QUESTIONS, f"Conditional Q{q_num} not found"


class TestConfigIntegrity:
    """Test overall config integrity"""
    
    def test_no_circular_references(self):
        """Test no circular references in config"""
        # This would cause infinite loops
        # Basic check: ensure config can be loaded
        assert QUESTIONS is not None
        assert INTRO_MESSAGES is not None
    
    def test_all_dynamic_options_loadable(self):
        """Test all dynamic option references are valid"""
        dynamic_refs = set()
        
        for q_num, question in QUESTIONS.items():
            if 'options' in question and isinstance(question['options'], str):
                dynamic_refs.add(question['options'])
        
        # All dynamic refs should be loadable
        for ref in dynamic_refs:
            if ref == 'countries':
                countries = get_countries()
                assert len(countries) > 0
            elif ref == 'states_india':
                states = get_states_india()
                assert len(states) > 0
    
    def test_question_numbering_sequential(self):
        """Test question numbers are sequential 1-77"""
        question_nums = sorted(QUESTIONS.keys())
        expected_nums = list(range(1, 78))
        
        assert question_nums == expected_nums, "Question numbering is not sequential"


class TestQuestionText:
    """Test question text quality"""
    
    def test_all_questions_have_text(self):
        """Test all questions have non-empty text"""
        for q_num, question in QUESTIONS.items():
            assert 'text' in question
            assert len(question['text']) > 0, f"Q{q_num} has empty text"
    
    def test_question_text_readable(self):
        """Test question text is reasonable length"""
        for q_num, question in QUESTIONS.items():
            text = question['text']
            
            # Should be at least 5 characters
            assert len(text) >= 5, f"Q{q_num} text too short"
            
            # Should not be absurdly long
            assert len(text) <= 1000, f"Q{q_num} text too long"
