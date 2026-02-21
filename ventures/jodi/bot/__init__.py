"""
JODI Telegram Bot Package
Button-based onboarding flow for matchmaking platform
"""

__version__ = "1.0.0"
__author__ = "Blitz"

from .bot import main
from .onboarding_handler import OnboardingHandler
from .db_adapter import DatabaseAdapter
from .config import QUESTIONS, INTRO_MESSAGES

__all__ = [
    'main',
    'OnboardingHandler',
    'DatabaseAdapter',
    'QUESTIONS',
    'INTRO_MESSAGES'
]
