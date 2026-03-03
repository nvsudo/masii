"""
Integration Tests for Onboarding Handler
Tests question flow and state management
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import Mock, AsyncMock, patch
from onboarding_handler import OnboardingHandler


class TestOnboardingHandler:
    """Test OnboardingHandler initialization and setup"""
    
    def test_init(self, mock_db):
        """Test handler initialization"""
        handler = OnboardingHandler(mock_db)
        assert handler.db == mock_db
        assert 'countries' in handler.dynamic_options
        assert 'states_india' in handler.dynamic_options
    
    def test_dynamic_options_loaded(self, mock_db):
        """Test that dynamic options are loaded"""
        handler = OnboardingHandler(mock_db)
        
        # Countries should be loaded
        countries = handler.dynamic_options.get('countries')
        assert countries is not None
        assert len(countries) > 0
        
        # States should be loaded
        states = handler.dynamic_options.get('states_india')
        assert states is not None
        assert len(states) > 0


@pytest.mark.asyncio
class TestStartOnboarding:
    """Test /start command and intro flow"""
    
    async def test_start_new_user(self, mock_db, mock_update, mock_context):
        """Test starting onboarding for new user"""
        # No existing session
        mock_db.get_session.return_value = None
        
        handler = OnboardingHandler(mock_db)
        await handler.start_onboarding(mock_update, mock_context)
        
        # Should save new session
        assert mock_db.save_session.called
        
        # Should send first intro message
        assert mock_context.bot.send_message.called
    
    async def test_start_existing_incomplete_user(self, mock_db, mock_update, mock_context):
        """Test resuming onboarding for user with progress"""
        # User has progress at Q15
        mock_db.get_session.return_value = {
            'user_id': 123456789,
            'current_question': 15,
            'answers': {'gender_identity': 'Female'}
        }
        
        handler = OnboardingHandler(mock_db)
        await handler.start_onboarding(mock_update, mock_context)
        
        # Should show resume prompt
        assert mock_update.message.reply_text.called
        call_args = mock_update.message.reply_text.call_args
        assert 'resume' in str(call_args).lower() or 'continue' in str(call_args).lower()
    
    async def test_start_completed_user(self, mock_db, mock_update, mock_context):
        """Test starting for user who completed onboarding"""
        # User completed all 36 gunas
        mock_db.get_session.return_value = {
            'user_id': 123456789,
            'current_question': 37,
            'answers': {}
        }
        
        handler = OnboardingHandler(mock_db)
        await handler.start_onboarding(mock_update, mock_context)
        
        # Should start fresh intro (not resume)
        assert mock_context.bot.send_message.called


@pytest.mark.asyncio
class TestIntroFlow:
    """Test intro message flow"""
    
    async def test_intro_progression(self, mock_db, mock_context):
        """Test progressing through intro messages"""
        handler = OnboardingHandler(mock_db)
        
        # Show intro message 0
        await handler._show_intro_message(123456789, mock_context, 0, 123456789)
        
        # Should send message with button
        assert mock_context.bot.send_message.called
        call_args = mock_context.bot.send_message.call_args[1]
        assert 'reply_markup' in call_args
    
    async def test_intro_completion(self, mock_db, mock_context):
        """Test transition from intro to intent question"""
        handler = OnboardingHandler(mock_db)

        # Show intro beyond last message → should transition to intent
        from config import INTRO_MESSAGES
        await handler._show_intro_message(123456789, mock_context, len(INTRO_MESSAGES), 123456789)

        # Should send intent question (send_message called for intent)
        assert mock_context.bot.send_message.called
        call_args = mock_context.bot.send_message.call_args[1]
        assert 'reply_markup' in call_args


@pytest.mark.asyncio
class TestQuestionFlow:
    """Test question asking and progression"""
    
    async def test_ask_single_select_question(self, mock_db, mock_context, sample_session):
        """Test asking a single-select question"""
        mock_db.get_session.return_value = sample_session
        
        handler = OnboardingHandler(mock_db)
        
        # Ask Q1 (gender identity)
        from config import QUESTIONS
        q1 = QUESTIONS[1]
        
        await handler._ask_single_select(123456789, mock_context, 1, q1, sample_session)
        
        # Should send message with inline keyboard
        assert mock_context.bot.send_message.called
        call_args = mock_context.bot.send_message.call_args[1]
        assert 'reply_markup' in call_args
    
    async def test_ask_text_input_question(self, mock_db, mock_context):
        """Test asking a text input question"""
        handler = OnboardingHandler(mock_db)
        
        # Q3 is date_of_birth (text input)
        from config import QUESTIONS
        q3 = QUESTIONS[3]
        
        await handler._ask_text_input(123456789, mock_context, 3, q3)
        
        # Should send message
        assert mock_context.bot.send_message.called
        call_args = mock_context.bot.send_message.call_args[1]
        assert 'text' in call_args
    
    async def test_skip_question_logic(self, mock_db, mock_context):
        """Test that gunas are skipped correctly based on religion"""
        # Buddhist → guna 11 (practice) should be skipped
        session = {
            'user_id': 123456789,
            'current_question': 10,
            'answers': {'religion': 'Buddhist'},
            'skip_questions': [],
            'asked_questions': list(range(1, 11)),
        }
        mock_db.get_session.return_value = session

        handler = OnboardingHandler(mock_db)

        # Ask guna 11 (should skip — practice skipped for Buddhist)
        await handler._ask_question(123456789, mock_context, 11, session)

        # Guna 11 should be added to skip_questions
        assert 11 in session['skip_questions']


@pytest.mark.asyncio
class TestButtonCallbacks:
    """Test button callback handling"""
    
    async def test_intro_button_callback(self, mock_db, mock_context, mock_callback_query):
        """Test intro button callback"""
        mock_callback_query.data = "intro_next_0"
        
        handler = OnboardingHandler(mock_db)
        
        # Create mock update with callback query
        update = Mock()
        update.callback_query = mock_callback_query
        
        await handler.handle_button_callback(update, mock_context)
        
        # Should answer callback
        assert mock_callback_query.answer.called
    
    async def test_question_answer_callback(self, mock_db, mock_context, mock_callback_query):
        """Test question answer button callback"""
        session = {
            'user_id': 123456789,
            'current_question': 1,
            'answers': {},
            'skip_questions': []
        }
        mock_db.get_session.return_value = session
        
        # User selects "Marriage" for Q1 (relationship_intent)
        mock_callback_query.data = "q1_marriage"

        handler = OnboardingHandler(mock_db)

        update = Mock()
        update.callback_query = mock_callback_query

        await handler.handle_button_callback(update, mock_context)

        # Should save answer
        assert mock_db.save_answer.called

        # Should update session
        assert 'relationship_intent' in session['answers'] or mock_db.save_session.called
    
    async def test_resume_callback(self, mock_db, mock_context, mock_callback_query):
        """Test resume onboarding callback"""
        session = {
            'user_id': 123456789,
            'current_question': 10,
            'answers': {},
            'skip_questions': []
        }
        mock_db.get_session.return_value = session
        
        mock_callback_query.data = "resume_onboarding"
        
        handler = OnboardingHandler(mock_db)
        
        update = Mock()
        update.callback_query = mock_callback_query
        
        await handler.handle_button_callback(update, mock_context)
        
        # Should ask current question
        assert mock_context.bot.send_message.called
    
    async def test_restart_callback(self, mock_db, mock_context, mock_callback_query):
        """Test restart onboarding callback"""
        mock_callback_query.data = "restart_onboarding"
        
        handler = OnboardingHandler(mock_db)
        
        update = Mock()
        update.callback_query = mock_callback_query
        update.callback_query.from_user = Mock()
        update.callback_query.from_user.id = 123456789
        update.callback_query.from_user.username = "test"
        update.callback_query.from_user.first_name = "Test"
        
        await handler.handle_button_callback(update, mock_context)
        
        # Should clear session
        assert mock_db.clear_session.called


@pytest.mark.asyncio
class TestTextInputHandling:
    """Test text input handling"""
    
    async def test_valid_text_input(self, mock_db, mock_update, mock_context):
        """Test valid text input for name question"""
        session = {
            'user_id': 123456789,
            'current_question': 5,  # first_name (text_input)
            'answers': {},
            'skip_questions': [],
            'asked_questions': [1, 2, 3, 4, 5],
        }
        mock_db.get_session.return_value = session

        # User enters their name
        mock_update.message.text = "Priya"

        handler = OnboardingHandler(mock_db)
        await handler.handle_text_input(mock_update, mock_context)

        # Should save answer
        assert mock_db.save_answer.called
    
    async def test_invalid_text_input(self, mock_db, mock_update, mock_context):
        """Test text input when button expected"""
        session = {
            'user_id': 123456789,
            'current_question': 1,  # single_select — expects button not text
            'answers': {},
            'skip_questions': [],
            'asked_questions': [1],
        }
        mock_db.get_session.return_value = session

        # User types text when button is expected
        mock_update.message.text = "some text"
        
        handler = OnboardingHandler(mock_db)
        await handler.handle_text_input(mock_update, mock_context)
        
        # Should send error message
        assert mock_update.message.reply_text.called
        
        # Should NOT save answer
        # Check that save_answer was not called, or called count is 0
        assert mock_db.save_answer.call_count == 0
    
    async def test_text_input_when_button_expected(self, mock_db, mock_update, mock_context):
        """Test text input when button answer is expected"""
        session = {
            'user_id': 123456789,
            'current_question': 1,  # Single select question
            'answers': {},
            'skip_questions': [],
            'asked_questions': [1],
        }
        mock_db.get_session.return_value = session

        mock_update.message.text = "some text"
        
        handler = OnboardingHandler(mock_db)
        await handler.handle_text_input(mock_update, mock_context)
        
        # Should send error about button expected
        assert mock_update.message.reply_text.called


@pytest.mark.asyncio
class TestMultiSelect:
    """Test multi-select question handling"""
    
    async def test_multi_select_initial(self, mock_db, mock_context, sample_session):
        """Test showing initial multi-select question"""
        from config import QUESTIONS
        
        # Find a multi-select question
        multi_select_q = None
        for q_num, q in QUESTIONS.items():
            if q.get('type') == 'multi_select':
                multi_select_q = (q_num, q)
                break
        
        if multi_select_q:
            q_num, q = multi_select_q
            
            handler = OnboardingHandler(mock_db)
            await handler._ask_multi_select(123456789, mock_context, q_num, q, sample_session)
            
            # Should send message with checkboxes
            assert mock_context.bot.send_message.called
    
    async def test_multi_select_toggle(self, mock_db, mock_context, mock_callback_query):
        """Test toggling multi-select options"""
        from config import QUESTIONS
        
        # Find a multi-select question
        multi_select_q = None
        for q_num, q in QUESTIONS.items():
            if q.get('type') == 'multi_select':
                multi_select_q = (q_num, q)
                break
        
        if multi_select_q:
            q_num, q = multi_select_q
            
            session = {
                'user_id': 123456789,
                'current_question': q_num,
                'answers': {},
                'skip_questions': [],
                'multi_select_buffer': {}
            }
            mock_db.get_session.return_value = session
            
            # Get first option
            first_option = q['options'][0]['value']
            
            mock_callback_query.data = f"q{q_num}_{first_option}"
            
            handler = OnboardingHandler(mock_db)
            await handler._handle_multi_select(
                mock_callback_query, mock_context, 123456789, q_num, q, first_option, session
            )
            
            # Should add to buffer
            field = q['field']
            assert field in session['multi_select_buffer']


@pytest.mark.asyncio
class TestCloseFlow:
    """Test close flow after all 36 gunas"""

    async def test_show_close(self, mock_db, mock_context, sample_session):
        """Test showing close message after 36 gunas"""
        sample_session['answers']['first_name'] = 'Test'
        handler = OnboardingHandler(mock_db)

        await handler._show_close(123456789, mock_context, sample_session)

        # Should send close message
        assert mock_context.bot.send_message.called

        # Should update session to complete
        assert sample_session['current_section'] == 'complete'


class TestHelperMethods:
    """Test helper methods"""
    
    def test_sanitize_callback(self, mock_db):
        """Test callback data sanitization"""
        handler = OnboardingHandler(mock_db)
        
        assert handler._sanitize_callback("Test Value") == "test_value"
        assert handler._sanitize_callback("Yes/No") == "yes_no"
        assert handler._sanitize_callback(None) == "none"
        assert handler._sanitize_callback("Already have") == "already_have"
