"""
JODI Extraction Pipeline Enhancements
Implements N's requirements:
- DOB parsing with age validation (18-80 years)
- Telegram buttons for categorical fields
- Full CRUD support for profile management
"""

from datetime import datetime, date
from dateutil import parser as date_parser
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Optional, Dict, List, Tuple
import re


# ============================================================================
# DOB PARSING & AGE VALIDATION
# ============================================================================

def parse_and_validate_dob(text: str) -> Tuple[Optional[date], Optional[str]]:
    """
    Parse date of birth from text and validate age is 18-80.
    
    Args:
        text: User input (e.g., "1995-05-15", "May 15, 1995", "15/05/1995")
    
    Returns:
        (parsed_date, error_message)
        - If valid: (date object, None)
        - If invalid: (None, error message)
    
    Examples:
        >>> parse_and_validate_dob("1995-05-15")
        (date(1995, 5, 15), None)
        
        >>> parse_and_validate_dob("2010-01-01")
        (None, "You must be at least 18 years old to use Jodi.")
        
        >>> parse_and_validate_dob("1940-01-01")
        (None, "Please provide a valid date of birth (age 18-80).")
    """
    # Try parsing the date
    try:
        # Use dateutil parser for flexible parsing
        parsed_date = date_parser.parse(text, fuzzy=True).date()
    except (ValueError, TypeError):
        return None, "I couldn't understand that date. Could you try again? For example: '1995-05-15' or 'May 15, 1995'"
    
    # Calculate age
    today = date.today()
    age = today.year - parsed_date.year - ((today.month, today.day) < (parsed_date.month, parsed_date.day))
    
    # Validate age range
    if age < 18:
        return None, "You must be at least 18 years old to use Jodi."
    elif age > 80:
        return None, "Please provide a valid date of birth (age 18-80)."
    elif parsed_date > today:
        return None, "Date of birth cannot be in the future."
    
    return parsed_date, None


def extract_dob_from_message(message: str) -> Optional[date]:
    """
    Attempt to extract DOB from a conversational message.
    
    Handles formats like:
    - "I was born on May 15, 1995"
    - "My birthday is 05/15/1995"
    - "I'm 28 years old" -> Not supported (need explicit DOB)
    
    Returns:
        date object if found and valid, None otherwise
    """
    # Regex patterns for common date formats
    patterns = [
        r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',  # YYYY-MM-DD or YYYY/MM/DD
        r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',  # DD-MM-YYYY or MM/DD/YYYY
        r'\b([A-Za-z]+\s+\d{1,2},?\s+\d{4})\b',  # Month DD, YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            date_str = match.group(1)
            parsed_date, error = parse_and_validate_dob(date_str)
            if parsed_date:
                return parsed_date
    
    return None


# ============================================================================
# TELEGRAM BUTTON BUILDERS (Categorical Fields)
# ============================================================================

def get_gender_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for gender identity selection."""
    keyboard = [
        [
            InlineKeyboardButton("Male", callback_data="gender:Male"),
            InlineKeyboardButton("Female", callback_data="gender:Female")
        ],
        [
            InlineKeyboardButton("Non-binary", callback_data="gender:Non-binary"),
            InlineKeyboardButton("Other", callback_data="gender:Other")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_sexual_orientation_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for sexual orientation."""
    keyboard = [
        [
            InlineKeyboardButton("Heterosexual", callback_data="orientation:Heterosexual"),
            InlineKeyboardButton("Gay", callback_data="orientation:Gay")
        ],
        [
            InlineKeyboardButton("Lesbian", callback_data="orientation:Lesbian"),
            InlineKeyboardButton("Bisexual", callback_data="orientation:Bisexual")
        ],
        [
            InlineKeyboardButton("Other", callback_data="orientation:Other"),
            InlineKeyboardButton("Prefer not to say", callback_data="orientation:PreferNotToSay")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_smoking_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for smoking status."""
    keyboard = [
        [
            InlineKeyboardButton("Never", callback_data="smoking:Never"),
            InlineKeyboardButton("Socially", callback_data="smoking:Socially")
        ],
        [
            InlineKeyboardButton("Regularly", callback_data="smoking:Regularly"),
            InlineKeyboardButton("Trying to quit", callback_data="smoking:TryingToQuit")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_drinking_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for drinking habits."""
    keyboard = [
        [
            InlineKeyboardButton("Never", callback_data="drinking:Never"),
            InlineKeyboardButton("Socially", callback_data="drinking:Socially")
        ],
        [
            InlineKeyboardButton("Regularly", callback_data="drinking:Regularly"),
            InlineKeyboardButton("Occasionally", callback_data="drinking:Occasionally")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_religion_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for religion/faith."""
    keyboard = [
        [
            InlineKeyboardButton("Muslim", callback_data="religion:Muslim"),
            InlineKeyboardButton("Hindu", callback_data="religion:Hindu")
        ],
        [
            InlineKeyboardButton("Christian", callback_data="religion:Christian"),
            InlineKeyboardButton("Jewish", callback_data="religion:Jewish")
        ],
        [
            InlineKeyboardButton("Buddhist", callback_data="religion:Buddhist"),
            InlineKeyboardButton("Sikh", callback_data="religion:Sikh")
        ],
        [
            InlineKeyboardButton("Spiritual", callback_data="religion:Spiritual"),
            InlineKeyboardButton("Atheist/Agnostic", callback_data="religion:Atheist")
        ],
        [
            InlineKeyboardButton("Other", callback_data="religion:Other")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_children_intent_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for children intent."""
    keyboard = [
        [
            InlineKeyboardButton("Want kids", callback_data="children:WantKids"),
            InlineKeyboardButton("Don't want kids", callback_data="children:DontWantKids")
        ],
        [
            InlineKeyboardButton("Already have kids", callback_data="children:AlreadyHave"),
            InlineKeyboardButton("Open to either", callback_data="children:OpenToEither")
        ],
        [
            InlineKeyboardButton("Not sure yet", callback_data="children:NotSure")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_marital_history_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for marital history."""
    keyboard = [
        [
            InlineKeyboardButton("Never married", callback_data="marital:NeverMarried"),
            InlineKeyboardButton("Divorced", callback_data="marital:Divorced")
        ],
        [
            InlineKeyboardButton("Widowed", callback_data="marital:Widowed"),
            InlineKeyboardButton("Separated", callback_data="marital:Separated")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_relationship_intent_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for relationship intent."""
    keyboard = [
        [
            InlineKeyboardButton("Marriage", callback_data="intent:Marriage"),
            InlineKeyboardButton("Long-term committed", callback_data="intent:LongTerm")
        ],
        [
            InlineKeyboardButton("Open to both", callback_data="intent:OpenToBoth"),
            InlineKeyboardButton("Exploring", callback_data="intent:Exploring")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_relationship_timeline_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for relationship timeline."""
    keyboard = [
        [
            InlineKeyboardButton("Ready now", callback_data="timeline:ReadyNow"),
            InlineKeyboardButton("Within 1 year", callback_data="timeline:Within1Year")
        ],
        [
            InlineKeyboardButton("1-2 years", callback_data="timeline:1To2Years"),
            InlineKeyboardButton("2-5 years", callback_data="timeline:2To5Years")
        ],
        [
            InlineKeyboardButton("Just exploring", callback_data="timeline:Exploring")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_dietary_restrictions_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for dietary restrictions."""
    keyboard = [
        [
            InlineKeyboardButton("None", callback_data="diet:None"),
            InlineKeyboardButton("Halal", callback_data="diet:Halal")
        ],
        [
            InlineKeyboardButton("Kosher", callback_data="diet:Kosher"),
            InlineKeyboardButton("Vegetarian", callback_data="diet:Vegetarian")
        ],
        [
            InlineKeyboardButton("Vegan", callback_data="diet:Vegan"),
            InlineKeyboardButton("Other", callback_data="diet:Other")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_education_level_buttons() -> InlineKeyboardMarkup:
    """Telegram buttons for education level."""
    keyboard = [
        [
            InlineKeyboardButton("High School", callback_data="education:HighSchool"),
            InlineKeyboardButton("Some College", callback_data="education:SomeCollege")
        ],
        [
            InlineKeyboardButton("Bachelor's", callback_data="education:Bachelors"),
            InlineKeyboardButton("Master's", callback_data="education:Masters")
        ],
        [
            InlineKeyboardButton("PhD", callback_data="education:PhD"),
            InlineKeyboardButton("Other", callback_data="education:Other")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================================================
# BUTTON ROUTER
# ============================================================================

BUTTON_GETTERS = {
    'gender': get_gender_buttons,
    'orientation': get_sexual_orientation_buttons,
    'smoking': get_smoking_buttons,
    'drinking': get_drinking_buttons,
    'religion': get_religion_buttons,
    'children': get_children_intent_buttons,
    'marital': get_marital_history_buttons,
    'intent': get_relationship_intent_buttons,
    'timeline': get_relationship_timeline_buttons,
    'diet': get_dietary_restrictions_buttons,
    'education': get_education_level_buttons,
}


def get_buttons_for_field(field_name: str) -> Optional[InlineKeyboardMarkup]:
    """
    Get Telegram buttons for a given field name.
    
    Args:
        field_name: Database field name or button category
    
    Returns:
        InlineKeyboardMarkup if buttons exist for this field, None otherwise
    
    Examples:
        >>> buttons = get_buttons_for_field('gender')
        >>> buttons = get_buttons_for_field('smoking')
    """
    # Map database field names to button categories
    field_mapping = {
        'gender_identity': 'gender',
        'sexual_orientation': 'orientation',
        'smoking': 'smoking',
        'drinking': 'drinking',
        'religion': 'religion',
        'children_intent': 'children',
        'marital_history': 'marital',
        'relationship_intent': 'intent',
        'relationship_timeline': 'timeline',
        'dietary_restrictions': 'diet',
        'education_level': 'education',
    }
    
    category = field_mapping.get(field_name, field_name)
    getter_func = BUTTON_GETTERS.get(category)
    
    if getter_func:
        return getter_func()
    return None


def parse_button_callback(callback_data: str) -> Tuple[str, str]:
    """
    Parse button callback data.
    
    Args:
        callback_data: Format "category:value" (e.g., "gender:Male")
    
    Returns:
        (field_name, value) tuple
    
    Examples:
        >>> parse_button_callback("gender:Male")
        ('gender_identity', 'Male')
        
        >>> parse_button_callback("smoking:Never")
        ('smoking', 'Never')
    """
    category, value = callback_data.split(':', 1)
    
    # Map button category to database field name
    category_to_field = {
        'gender': 'gender_identity',
        'orientation': 'sexual_orientation',
        'smoking': 'smoking',
        'drinking': 'drinking',
        'religion': 'religion',
        'children': 'children_intent',
        'marital': 'marital_history',
        'intent': 'relationship_intent',
        'timeline': 'relationship_timeline',
        'diet': 'dietary_restrictions',
        'education': 'education_level',
    }
    
    field_name = category_to_field.get(category, category)
    
    # Clean up value (remove underscores, convert to proper case)
    if value == 'PreferNotToSay':
        value = 'Prefer not to say'
    elif value in ['WantKids', 'DontWantKids', 'AlreadyHave', 'OpenToEither', 'NotSure']:
        # Children intent values
        mapping = {
            'WantKids': 'Want kids',
            'DontWantKids': "Don't want kids",
            'AlreadyHave': 'Already have kids',
            'OpenToEither': 'Open to either',
            'NotSure': 'Not sure yet'
        }
        value = mapping[value]
    elif value in ['NeverMarried', 'TryingToQuit', 'ReadyNow', 'Within1Year', 'HighSchool', 'SomeCollege']:
        # Multi-word values
        # Insert space before capital letters
        value = re.sub(r'([a-z])([A-Z])', r'\1 \2', value)
    elif value in ['1To2Years', '2To5Years']:
        value = value.replace('To', '-')
    
    return field_name, value


# ============================================================================
# PROFILE CRUD HELPERS
# ============================================================================

def should_use_buttons_for_question(missing_field: str) -> bool:
    """
    Determine if we should use buttons for a specific missing field.
    
    Returns:
        True if buttons should be used, False for free-text input
    """
    button_fields = {
        'gender_identity', 'sexual_orientation', 'smoking', 'drinking',
        'religion', 'children_intent', 'marital_history',
        'relationship_intent', 'relationship_timeline',
        'dietary_restrictions', 'education_level'
    }
    return missing_field in button_fields


def get_next_tier1_question_with_buttons(telegram_id: int, db) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """
    Get the next Tier 1 question for a user, with buttons if applicable.
    
    Args:
        telegram_id: User's Telegram ID
        db: Database instance
    
    Returns:
        (question_text, buttons_or_none)
    
    Usage in bot:
        question, buttons = get_next_tier1_question_with_buttons(user_id, db)
        if buttons:
            await update.message.reply_text(question, reply_markup=buttons)
        else:
            await update.message.reply_text(question)
    """
    user = db.get_user(telegram_id)
    if not user:
        return ("Let's start! What's your name?", None)
    
    # Check which Tier 1 fields are missing
    tier1_fields = {
        'full_name': "What's your name?",
        'date_of_birth': "When were you born? (e.g., May 15, 1995)",
        'gender_identity': "How do you identify?",
        'city': "Which city do you live in?",
        'religion': "Do you practice a religion?",
        'children_intent': "How do you feel about having kids?",
        'marital_history': "Have you been married before?",
        'smoking': "Do you smoke?",
        'drinking': "How often do you drink?",
        'relationship_intent': "What kind of relationship are you looking for?",
        'relationship_timeline': "What's your timeline?",
        'occupation': "What do you do for work?",
    }
    
    for field, question in tier1_fields.items():
        if not user.get(field):
            # Found a missing field
            buttons = get_buttons_for_field(field) if should_use_buttons_for_question(field) else None
            return (question, buttons)
    
    return ("Great! You've completed the basics. Tell me more about yourself!", None)


# ============================================================================
# ENHANCED LLM EXTRACTION PROMPT
# ============================================================================

DOB_EXTRACTION_ADDENDUM = """
**CRITICAL: Date of Birth Handling**

If user mentions their birth date:
1. Extract to "date_of_birth" field in hard_filters
2. Format as YYYY-MM-DD (ISO 8601)
3. Confidence = 1.0 (explicit)

Valid formats:
- "I was born on May 15, 1995" → "1995-05-15"
- "My birthday is 05/15/1995" → "1995-05-15"
- "15th May 1995" → "1995-05-15"

DO NOT extract if:
- User only mentions age ("I'm 28") - need explicit DOB
- Date is ambiguous or unclear

Age will be calculated automatically from DOB (don't extract "age" separately).
"""


BUTTON_FIELD_GUIDANCE = """
**Fields That Use Telegram Buttons (DO NOT extract from free text):**

The following fields will be collected via buttons, so only extract if EXPLICITLY stated:
- gender_identity (Male/Female/Non-binary/Other)
- sexual_orientation (Heterosexual/Gay/Lesbian/Bisexual/Other)
- smoking (Never/Socially/Regularly/Trying to quit)
- drinking (Never/Socially/Regularly/Occasionally)
- religion (Muslim/Hindu/Christian/Jewish/Buddhist/Sikh/Spiritual/Atheist/Other)
- children_intent (Want kids/Don't want kids/Already have kids/Open to either/Not sure yet)
- marital_history (Never married/Divorced/Widowed/Separated)
- relationship_intent (Marriage/Long-term committed/Open to both/Exploring)
- relationship_timeline (Ready now/Within 1 year/1-2 years/2-5 years/Just exploring)
- dietary_restrictions (None/Halal/Kosher/Vegetarian/Vegan/Other)
- education_level (High School/Some College/Bachelor's/Master's/PhD/Other)

Only extract these if the user explicitly states them (confidence = 1.0).
DO NOT infer from context for these fields.
"""


# Export enhanced prompt additions
ENHANCED_EXTRACTION_GUIDANCE = DOB_EXTRACTION_ADDENDUM + "\n\n" + BUTTON_FIELD_GUIDANCE
