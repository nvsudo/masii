"""
Pytest configuration and shared fixtures for 36-guna Masii bot tests
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime


@pytest.fixture
def mock_db():
    """Mock database adapter"""
    db = MagicMock()
    db.get_session = MagicMock(return_value=None)
    db.save_session = MagicMock()
    db.clear_session = MagicMock()
    db.save_answer = AsyncMock()
    db.get_user = MagicMock(return_value=None)
    db.create_user = MagicMock()
    return db


@pytest.fixture
def sample_session():
    """Sample onboarding session (36-guna flow)"""
    return {
        "user_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "current_section": "niyat",
        "current_question": 1,
        "intro_index": 0,
        "answers": {},
        "skip_questions": [],
        "asked_questions": [],
        "multi_select_buffer": {},
        "location_buffer": {},
        "proxy": None,
        "started_at": datetime.utcnow().isoformat(),
        "last_active": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_update():
    """Mock Telegram Update object"""
    update = Mock()
    update.effective_user = Mock()
    update.effective_user.id = 123456789
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.message = Mock()
    update.message.chat = Mock()
    update.message.chat.id = 123456789
    update.message.text = ""
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Mock Telegram Context object"""
    context = Mock()
    context.bot = Mock()
    context.bot.send_message = AsyncMock()
    return context


@pytest.fixture
def mock_callback_query():
    """Mock Telegram CallbackQuery object"""
    query = Mock()
    query.answer = AsyncMock()
    query.from_user = Mock()
    query.from_user.id = 123456789
    query.message = Mock()
    query.message.chat = Mock()
    query.message.chat.id = 123456789
    query.message.reply_text = AsyncMock()
    query.data = ""
    return query


# ============== SAMPLE ANSWER SETS ==============

@pytest.fixture
def hindu_never_married():
    """Hindu, never married"""
    return {
        "marital_status": "Never married",
        "religion": "Hindu",
        "caste_community": "Brahmin",
        "children_intent": "Yes",
    }


@pytest.fixture
def muslim_never_married():
    """Muslim, never married"""
    return {
        "marital_status": "Never married",
        "religion": "Muslim",
        "children_intent": "Yes",
    }


@pytest.fixture
def jain_never_married():
    """Jain, never married"""
    return {
        "marital_status": "Never married",
        "religion": "Jain",
        "caste_community": "Oswal",
        "children_intent": "Open",
    }


@pytest.fixture
def buddhist_divorced():
    """Buddhist, divorced"""
    return {
        "marital_status": "Divorced",
        "religion": "Buddhist",
        "children_intent": "No",
    }
