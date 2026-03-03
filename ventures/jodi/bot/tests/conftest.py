"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from unittest.mock import Mock, AsyncMock
from datetime import datetime


@pytest.fixture
def mock_db():
    """Mock database adapter"""
    from unittest.mock import MagicMock
    
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
    """Sample onboarding session"""
    return {
        "user_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "current_section": "identity_basics",
        "current_question": 1,
        "intro_index": 0,
        "answers": {},
        "skip_questions": [],
        "multi_select_buffer": {},
        "photo_urls": [],
        "started_at": datetime.utcnow().isoformat(),
        "last_active": datetime.utcnow().isoformat()
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
    query.data = ""
    
    return query


@pytest.fixture
def hindu_never_married_india():
    """Sample answers: Hindu, never married, in India"""
    return {
        "marital_status": "Never married",
        "residency_type": "Indian citizen (in India)",
        "religion": "Hindu"
    }


@pytest.fixture
def muslim_never_married_india():
    """Sample answers: Muslim, never married, in India"""
    return {
        "marital_status": "Never married",
        "residency_type": "Indian citizen (in India)",
        "religion": "Muslim"
    }


@pytest.fixture
def nri_hindu():
    """Sample answers: NRI Hindu"""
    return {
        "marital_status": "Never married",
        "residency_type": "NRI",
        "religion": "Hindu"
    }


@pytest.fixture
def divorced_with_children():
    """Sample answers: Divorced with children"""
    return {
        "marital_status": "Divorced",
        "residency_type": "Indian citizen (in India)",
        "religion": "Hindu",
        "children_intent": "Already have"
    }
