"""
Masii Bot Configuration — The 36 Gunas
Data-driven question config for the Masii onboarding flow.
36 gunas across 6 sections, with conditional tree branching.
"""

from enum import Enum
from typing import Dict, List, Optional


class OnboardingSection(Enum):
    INTRO = "intro"
    NIYAT = "niyat"              # Section 1: Intent (gunas 1-4)
    PARICHAY = "parichay"        # Section 2: Introduction (gunas 5-9)
    DHARAM = "dharam"            # Section 3: Faith & Culture (gunas 10-16)
    PARIVAR = "parivar"          # Section 4: Family (gunas 17-21)
    JEEVAN_SHAILI = "jeevan_shaili"  # Section 5: Lifestyle (gunas 22-28)
    SOCH = "soch"                # Section 6: Values & Connection (gunas 29-36)
    COMPLETE = "complete"


# ============== INTRO MESSAGES ==============

INTRO_MESSAGES = [
    {
        "text": """Hey! I'm Masii — your AI matchmaker.

I help people find real, lasting relationships.
I ask questions, I listen, and I find your person.

Think of me as the auntie who knows everyone
and never forgets what you told her.""",
        "button": "Tell me more \u2192"
    },
    {
        "text": """Here's how this works:

I'll ask you 36 questions — like the 36 gunas,
but for real life. Not your horoscope. Your values,
your lifestyle, your family, your future.

Takes about 10 minutes. Then I go to work.

When I find someone worth your time, I'll message
you with my reasoning. Both of you say yes?
I make the introduction. For free.""",
        "button": "Sounds good \u2192"
    },
    {
        "text": """One thing first:

Everything you tell me stays between us. I use
your answers to find matches, never to judge.
Some questions are personal — you can skip any
of them. But the more I know, the better the match.

Your data is never sold. Never shared without
your permission.""",
        "button": "Got it \u2192"
    },
]

# Message 4 is the intent/proxy question — handled separately in the handler
INTENT_MESSAGE = {
    "text": """Before we start —

Are you filling this out for yourself
or for someone else?""",
    "options": [
        {"label": "For myself", "value": "self"},
        {"label": "For a family member / friend", "value": "proxy"}
    ]
}

PROXY_MESSAGES = [
    {
        "text": """That's sweet. How are you connected to them?""",
        "options": [
            {"label": "I'm their parent", "value": "parent"},
            {"label": "I'm their sibling", "value": "sibling"},
            {"label": "I'm their friend", "value": "friend"},
            {"label": "Other relative", "value": "other_relative"}
        ]
    },
    {
        "text": """Do they know you're doing this?""",
        "options": [
            {"label": "Yes, they asked me to", "value": "asked"},
            {"label": "Yes, they're okay with it", "value": "okay"},
            {"label": "Not yet, I'll tell them", "value": "not_yet"}
        ]
    }
]

PROXY_NO_CONSENT_MESSAGE = """No worries. Fill everything out — I'll save it.
But I won't start matching until they say yes.
When they're ready, have them message me and
I'll activate their profile."""


# ============== QUESTION DEFINITIONS — THE 36 GUNAS ==============

QUESTIONS = {

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 1: NIYAT (Intent) — Gunas 1-4
    # "Not your name, not your age. What you actually want."
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    1: {
        "section": "niyat",
        "field": "relationship_intent",
        "db_table": "users",
        "text": "What are you looking for?",
        "type": "single_select",
        "options": [
            {"label": "Marriage", "value": "Marriage"},
            {"label": "Long-term partner", "value": "Long-term partner"},
            {"label": "Open to both", "value": "Open to both"}
        ]
    },

    2: {
        "section": "niyat",
        "field": "timeline",
        "db_table": "signals",
        "text": "How soon?",
        "type": "single_select",
        "options": [
            {"label": "Ready now", "value": "Ready now"},
            {"label": "6 months", "value": "6 months"},
            {"label": "1 year", "value": "1 year"},
            {"label": "No rush", "value": "No rush"}
        ]
    },

    3: {
        "section": "niyat",
        "field": "looking_for_gender",
        "db_table": "users",
        "text": "Looking for a...",
        "type": "single_select",
        "options": [
            {"label": "Man", "value": "Men"},
            {"label": "Woman", "value": "Women"}
        ]
    },

    4: {
        "section": "niyat",
        "field": "match_priority",
        "db_table": "signals",
        "text": "What matters MOST in a partner? (pick one)",
        "type": "single_select",
        "options": [
            {"label": "Cultural fit", "value": "Cultural fit"},
            {"label": "Values alignment", "value": "Values alignment"},
            {"label": "Lifestyle match", "value": "Lifestyle match"},
            {"label": "Family compatibility", "value": "Family compatibility"},
            {"label": "Ambition match", "value": "Ambition match"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 2: PARICHAY (Introduction) — Gunas 5-9
    # "The basics. Fast. Buttons only."
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    5: {
        "section": "parichay",
        "field": "first_name",
        "db_table": "users",
        "text": "What's your name?",
        "type": "text_input",
        "placeholder": "Your first name"
    },

    6: {
        "section": "parichay",
        "field": "gender_identity",
        "db_table": "users",
        "text": "Gender",
        "type": "single_select",
        "options": [
            {"label": "Male", "value": "Male"},
            {"label": "Female", "value": "Female"},
            {"label": "Non-binary", "value": "Non-binary"}
        ]
    },

    7: {
        "section": "parichay",
        "field": "date_of_birth",
        "db_table": "users",
        "type": "two_step_date",
        "step1": {
            "text": "What year were you born?",
            "type": "single_select",
            "field": "birth_year",
            "options": "birth_years",
            "columns": 3
        },
        "step2": {
            "text": "Which month?",
            "type": "single_select",
            "field": "birth_month",
            "options": [
                {"label": "January", "value": "1"},
                {"label": "February", "value": "2"},
                {"label": "March", "value": "3"},
                {"label": "April", "value": "4"},
                {"label": "May", "value": "5"},
                {"label": "June", "value": "6"},
                {"label": "July", "value": "7"},
                {"label": "August", "value": "8"},
                {"label": "September", "value": "9"},
                {"label": "October", "value": "10"},
                {"label": "November", "value": "11"},
                {"label": "December", "value": "12"}
            ],
            "columns": 2
        },
        "response_template": "{age} — got it \u2713"
    },

    8: {
        "section": "parichay",
        "field": "location",
        "db_table": "users",
        "type": "location_tree",
        "step1": {
            "text": "Where are you based?",
            "type": "single_select",
            "field": "location_type",
            "options": [
                {"label": "India", "value": "India"},
                {"label": "Outside India", "value": "Outside India"}
            ]
        },
        "step2_india": {
            "text": "Which state?",
            "type": "single_select",
            "field": "state_india",
            "options": "states_india",
            "columns": 2
        },
        "step2_abroad": {
            "text": "Which country?",
            "type": "single_select",
            "field": "country_current",
            "options": "countries",
            "columns": 2
        },
        "step3": {
            "text": "Which city?",
            "type": "text_input",
            "field": "city_current",
            "placeholder": "e.g. Mumbai, Dubai, Toronto..."
        }
    },

    9: {
        "section": "parichay",
        "field": "marital_status",
        "db_table": "users",
        "text": "Have you been married before?",
        "type": "single_select",
        "options": [
            {"label": "Never married", "value": "Never married"},
            {"label": "Divorced", "value": "Divorced"},
            {"label": "Widowed", "value": "Widowed"},
            {"label": "Separated", "value": "Separated"}
        ]
    },

    # 9b: children — conditional, asked only if not "Never married"
    # Handled via conditional_logic skip + a sub-question

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 3: DHARAM (Faith & Culture) — Gunas 10-16
    # "Not the checkbox version. The real one."
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    10: {
        "section": "dharam",
        "field": "religion",
        "db_table": "users",
        "text": "Your faith / religion",
        "type": "single_select",
        "options": [
            {"label": "Hindu", "value": "Hindu"},
            {"label": "Muslim", "value": "Muslim"},
            {"label": "Christian", "value": "Christian"},
            {"label": "Sikh", "value": "Sikh"},
            {"label": "Jain", "value": "Jain"},
            {"label": "Buddhist", "value": "Buddhist"},
            {"label": "Other", "value": "Other"},
            {"label": "None / Atheist", "value": "None"}
        ],
        "columns": 2
    },

    11: {
        "section": "dharam",
        "field": "religious_practice",
        "db_table": "users",
        "text": "How practicing are you?",
        "type": "single_select",
        "options": "practice_by_religion",  # Dynamic — conditional on religion
    },

    12: {
        "section": "dharam",
        "field": "sect_denomination",
        "db_table": "users",
        "text": "Which tradition do you follow?",
        "type": "single_select",
        "options": "sects_by_religion",  # Dynamic — conditional on religion
    },

    13: {
        "section": "dharam",
        "field": "caste_community",
        "db_table": "users",
        "text": "Your community:",
        "type": "single_select",
        "options": "castes_by_religion",  # Dynamic — conditional on religion
    },

    14: {
        "section": "dharam",
        "field": "mother_tongue",
        "db_table": "users",
        "text": "What's your mother tongue?",
        "type": "single_select",
        "options": [
            {"label": "Hindi", "value": "Hindi"},
            {"label": "Gujarati", "value": "Gujarati"},
            {"label": "Tamil", "value": "Tamil"},
            {"label": "Telugu", "value": "Telugu"},
            {"label": "Kannada", "value": "Kannada"},
            {"label": "Malayalam", "value": "Malayalam"},
            {"label": "Bengali", "value": "Bengali"},
            {"label": "Marathi", "value": "Marathi"},
            {"label": "Punjabi", "value": "Punjabi"},
            {"label": "Urdu", "value": "Urdu"},
            {"label": "Odia", "value": "Odia"},
            {"label": "Assamese", "value": "Assamese"},
            {"label": "Konkani", "value": "Konkani"},
            {"label": "Sindhi", "value": "Sindhi"},
            {"label": "English", "value": "English"},
            {"label": "Other \u2192", "value": "Other", "requires_text": True}
        ],
        "columns": 2
    },

    15: {
        "section": "dharam",
        "field": "partner_religion_pref",
        "db_table": "preferences",
        "text": "Partner's religion \u2014 preference?",
        "type": "single_select",
        "options": [
            {"label": "Same only", "value": "Same only"},
            {"label": "Same preferred", "value": "Same preferred"},
            {"label": "Open", "value": "Open"},
            {"label": "Specific", "value": "Specific", "requires_text": True}
        ]
    },

    16: {
        "section": "dharam",
        "field": "partner_religiosity",
        "db_table": "signals",
        "text": "How important is their practice level?",
        "type": "single_select",
        "options": [
            {"label": "Must match mine", "value": "Must match"},
            {"label": "Somewhat important", "value": "Somewhat important"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 4: PARIVAR (Family) — Gunas 17-21
    # "Choose your person. Family happy too. Matching for both."
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    17: {
        "section": "parivar",
        "field": "family_type",
        "db_table": "users",
        "text": "Family structure",
        "type": "single_select",
        "options": [
            {"label": "Nuclear", "value": "Nuclear"},
            {"label": "Joint family", "value": "Joint family"},
            {"label": "Extended joint family", "value": "Extended joint family"}
        ]
    },

    18: {
        "section": "parivar",
        "field": "family_involvement_search",
        "db_table": "users",
        "text": "How involved should family be in your search?",
        "type": "single_select",
        "options": [
            {"label": "Very involved", "value": "Very involved"},
            {"label": "Somewhat", "value": "Somewhat"},
            {"label": "I'll tell them after", "value": "I'll tell them after"},
            {"label": "Not at all", "value": "Not at all"}
        ]
    },

    19: {
        "section": "parivar",
        "field": "living_with_parents_post_marriage",
        "db_table": "users",
        "text": "Open to living with/near parents?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "Open to it", "value": "Open to it"},
            {"label": "Prefer not", "value": "Prefer not"}
        ]
    },

    20: {
        "section": "parivar",
        "field": "children_intent",
        "db_table": "users",
        "text": "Do you want children?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "No", "value": "No"},
            {"label": "Already have", "value": "Already have"},
            {"label": "Open", "value": "Open"}
        ]
    },

    21: {
        "section": "parivar",
        "field": "children_timeline",
        "db_table": "users",
        "text": "When?",
        "type": "single_select",
        "options": [
            {"label": "Soon", "value": "Soon"},
            {"label": "2\u20133 years", "value": "2-3 years"},
            {"label": "Eventually", "value": "Eventually"},
            {"label": "Not sure", "value": "Not sure"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 5: JEEVAN SHAILI (Lifestyle) — Gunas 22-28
    # "The practical compatibility layer."
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    22: {
        "section": "jeevan_shaili",
        "field": "diet",
        "db_table": "users",
        "text": "Your diet",
        "type": "single_select",
        "options": "diet_by_religion",  # Dynamic — conditional on religion
    },

    23: {
        "section": "jeevan_shaili",
        "field": "drinking",
        "db_table": "users",
        "text": "Alcohol?",
        "type": "single_select",
        "options": [
            {"label": "Never", "value": "Never"},
            {"label": "Social", "value": "Socially / Occasionally"},
            {"label": "Regular", "value": "Regularly"}
        ]
    },

    24: {
        "section": "jeevan_shaili",
        "field": "smoking",
        "db_table": "users",
        "text": "Smoking?",
        "type": "single_select",
        "options": [
            {"label": "Never", "value": "Never"},
            {"label": "Social", "value": "Occasionally / Socially"},
            {"label": "Regular", "value": "Regularly"}
        ]
    },

    25: {
        "section": "jeevan_shaili",
        "field": "education_level",
        "db_table": "users",
        "text": "Highest education",
        "type": "single_select",
        "options": [
            {"label": "High school", "value": "High school / 12th"},
            {"label": "Bachelor's", "value": "Bachelor's"},
            {"label": "Master's", "value": "Master's"},
            {"label": "PhD", "value": "PhD / Doctorate"},
            {"label": "Professional (MD/JD/CA)", "value": "Professional (CA/CS/CFA/MBBS/LLB)"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },

    26: {
        "section": "jeevan_shaili",
        "field": "work_industry",
        "db_table": "users",
        "text": "What do you do?",
        "type": "single_select",
        "options": [
            {"label": "Tech", "value": "IT / Software"},
            {"label": "Finance", "value": "Finance / Banking"},
            {"label": "Medicine", "value": "Healthcare / Pharma"},
            {"label": "Law", "value": "Legal"},
            {"label": "Business", "value": "Self-employed / Business owner"},
            {"label": "Creative", "value": "Media / Entertainment"},
            {"label": "Government", "value": "Government / PSU"},
            {"label": "Education", "value": "Education / Academia"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 3
    },

    27: {
        "section": "jeevan_shaili",
        "field": "willing_to_relocate",
        "db_table": "users",
        "text": "Open to relocating for the right person?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes, anywhere"},
            {"label": "Maybe", "value": "Maybe"},
            {"label": "No", "value": "No, prefer to stay here"}
        ]
    },

    28: {
        "section": "jeevan_shaili",
        "field": "partner_diet_pref",
        "db_table": "preferences",
        "text": "Partner's diet \u2014 preference?",
        "type": "single_select",
        "options": [
            {"label": "Must match mine", "value": "Must match mine"},
            {"label": "Prefer similar", "value": "Prefer similar"},
            {"label": "Flexible", "value": "Don't care"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SECTION 6: SOCH (Values & Connection) — Gunas 29-36
    # "Not what you look like on paper, but who you actually are."
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    29: {
        "section": "soch",
        "field": "what_matters",
        "db_table": "signals",
        "text": "What matters most to you in a partner? In your own words.",
        "type": "text_input",
        "placeholder": "Take your time. The more you write, the better your match."
    },

    30: {
        "section": "soch",
        "field": "dealbreakers_text",
        "db_table": "signals",
        "text": "Anything that's a dealbreaker? Be honest.",
        "type": "text_input",
        "placeholder": "What would be a non-starter for you?"
    },

    31: {
        "section": "soch",
        "field": "financial_outlook",
        "db_table": "signals",
        "text": "How important is partner's financial stability?",
        "type": "single_select",
        "options": [
            {"label": "Very important", "value": "Very"},
            {"label": "Somewhat", "value": "Somewhat"},
            {"label": "Not important", "value": "Not important"}
        ]
    },

    32: {
        "section": "soch",
        "field": "career_ambition",
        "db_table": "users",
        "text": "Where are you in your career?",
        "type": "single_select",
        "options": [
            {"label": "Climbing", "value": "Highly ambitious (career comes first)"},
            {"label": "Stable", "value": "Career-oriented but balanced"},
            {"label": "Building something", "value": "Building something"},
            {"label": "Figuring it out", "value": "Figuring it out"}
        ]
    },

    33: {
        "section": "soch",
        "field": "social_style",
        "db_table": "users",
        "text": "You're more...",
        "type": "single_select",
        "options": [
            {"label": "Introvert", "value": "Prefer small groups"},
            {"label": "Extrovert", "value": "Very outgoing \u2014 love big gatherings"},
            {"label": "Depends on the day", "value": "Social but balanced"}
        ]
    },

    34: {
        "section": "soch",
        "field": "conflict_style",
        "db_table": "signals",
        "text": "When you disagree with someone, you...",
        "type": "single_select",
        "options": [
            {"label": "Talk it out", "value": "Talk it out"},
            {"label": "Need space first", "value": "Need space first"},
            {"label": "Avoid conflict", "value": "Avoid"},
            {"label": "Compromise fast", "value": "Compromise fast"}
        ]
    },

    35: {
        "section": "soch",
        "field": "love_language",
        "db_table": "signals",
        "text": "How do you show love?",
        "type": "single_select",
        "options": [
            {"label": "Words", "value": "Words of affirmation"},
            {"label": "Touch", "value": "Physical touch"},
            {"label": "Quality time", "value": "Quality time"},
            {"label": "Gifts", "value": "Gifts"},
            {"label": "Acts of service", "value": "Acts of service"}
        ]
    },

    36: {
        "section": "soch",
        "field": "the_one_thing",
        "db_table": "signals",
        "text": "One thing Masii should know about you that no question above captured.",
        "type": "text_input",
        "placeholder": "Anything. Something that makes you, you."
    },
}

# Total gunas
TOTAL_GUNAS = 36

# Sub-questions that don't count as gunas but are part of the tree
SUB_QUESTIONS = {
    "children_existing": {
        "section": "parichay",
        "field": "children_existing",
        "db_table": "users",
        "text": "Do you have children?",
        "type": "single_select",
        "after_guna": 9,
        "condition": "marital_status != 'Never married'",
        "options": [
            {"label": "No", "value": "No"},
            {"label": "Yes, they live with me", "value": "Yes, they live with me"},
            {"label": "Yes, they don't live with me", "value": "Yes, they don't live with me"}
        ]
    },
    "caste_importance": {
        "section": "dharam",
        "field": "caste_importance",
        "db_table": "preferences",
        "text": "How important is caste in your partner?",
        "type": "single_select",
        "after_guna": 13,
        "condition": "caste_community is not None and caste_community != 'Prefer not to say'",
        "options": [
            {"label": "Very important", "value": "Dealbreaker \u2014 must match"},
            {"label": "Somewhat", "value": "Slight preference"},
            {"label": "Doesn't matter", "value": "Doesn't matter at all"}
        ]
    },
}


# ============== DYNAMIC OPTION GENERATORS ==============

def get_birth_years():
    """Birth years from 1980 to 2008 (ages 18-46)"""
    return [
        {"label": str(year), "value": str(year)}
        for year in range(2008, 1979, -1)
    ]


def get_countries():
    """Top countries for Indian population outside India"""
    return [
        {"label": "USA", "value": "USA"},
        {"label": "UK", "value": "UK"},
        {"label": "Canada", "value": "Canada"},
        {"label": "Australia", "value": "Australia"},
        {"label": "UAE", "value": "UAE"},
        {"label": "Singapore", "value": "Singapore"},
        {"label": "Germany", "value": "Germany"},
        {"label": "New Zealand", "value": "New Zealand"},
        {"label": "Saudi Arabia", "value": "Saudi Arabia"},
        {"label": "Qatar", "value": "Qatar"},
        {"label": "Other \u2192", "value": "Other", "requires_text": True}
    ]


def get_states_india():
    """Indian states"""
    return [
        {"label": "Maharashtra", "value": "Maharashtra"},
        {"label": "Delhi NCR", "value": "Delhi NCR"},
        {"label": "Karnataka", "value": "Karnataka"},
        {"label": "Tamil Nadu", "value": "Tamil Nadu"},
        {"label": "Gujarat", "value": "Gujarat"},
        {"label": "Rajasthan", "value": "Rajasthan"},
        {"label": "Uttar Pradesh", "value": "Uttar Pradesh"},
        {"label": "West Bengal", "value": "West Bengal"},
        {"label": "Kerala", "value": "Kerala"},
        {"label": "Telangana", "value": "Telangana"},
        {"label": "Punjab", "value": "Punjab"},
        {"label": "Haryana", "value": "Haryana"},
        {"label": "Madhya Pradesh", "value": "Madhya Pradesh"},
        {"label": "Bihar", "value": "Bihar"},
        {"label": "Andhra Pradesh", "value": "Andhra Pradesh"},
        {"label": "Other \u2192", "value": "Other", "requires_text": True}
    ]


def get_practice_by_religion(religion: str):
    """Practice level options conditional on religion"""
    practice = {
        "Hindu": [
            {"label": "Very (daily puja, temple weekly)", "value": "Very devout (daily practice)"},
            {"label": "Moderate (festivals, occasional temple)", "value": "Moderately observant (festivals, rituals)"},
            {"label": "Cultural (identify as Hindu, not practicing)", "value": "Culturally identify (not practicing)"},
            {"label": "Not really", "value": "Not at all"}
        ],
        "Muslim": [
            {"label": "Very (5 daily prayers, Quran regularly)", "value": "Very devout (daily practice)"},
            {"label": "Moderate (Jummah, Ramadan, Eid)", "value": "Moderately observant (festivals, rituals)"},
            {"label": "Cultural (identify as Muslim, not strictly practicing)", "value": "Culturally identify (not practicing)"},
            {"label": "Not really", "value": "Not at all"}
        ],
        "Sikh": [
            {"label": "Amritdhari (baptized)", "value": "Very devout (daily practice)"},
            {"label": "Keshdhari (keeps hair)", "value": "Moderately observant (festivals, rituals)"},
            {"label": "Sehajdhari (clean-shaven Sikh)", "value": "Culturally identify (not practicing)"},
            {"label": "Cultural", "value": "Not at all"}
        ],
        "Jain": [
            {"label": "Strict (no onion, garlic, root vegetables)", "value": "Very devout (daily practice)"},
            {"label": "Moderate (vegetarian, occasional flexibility)", "value": "Moderately observant (festivals, rituals)"},
            {"label": "Cultural (identify as Jain, flexible diet)", "value": "Culturally identify (not practicing)"}
        ],
        "Christian": [
            {"label": "Regular (church weekly, prayer daily)", "value": "Very devout (daily practice)"},
            {"label": "Moderate (church on occasions, holidays)", "value": "Moderately observant (festivals, rituals)"},
            {"label": "Cultural (identify as Christian, not practicing)", "value": "Culturally identify (not practicing)"}
        ],
    }
    return practice.get(religion)  # Returns None for Buddhist/Other/None → skip


def get_sects_by_religion(religion: str):
    """Sect/denomination options based on religion"""
    sects = {
        "Hindu": [
            {"label": "Shaiva", "value": "Shaivite"},
            {"label": "Vaishnava", "value": "Vaishnavite"},
            {"label": "Arya Samaji", "value": "Arya Samaj"},
            {"label": "Smartha", "value": "Smartha"},
            {"label": "None / Other", "value": None}
        ],
        "Muslim": [
            {"label": "Sunni", "value": "Sunni"},
            {"label": "Shia", "value": "Shia"},
            {"label": "Sufi", "value": "Sufi"},
            {"label": "Ahmadiyya", "value": "Ahmadiyya"},
            {"label": "None / Other", "value": None}
        ],
        "Christian": [
            {"label": "Catholic", "value": "Catholic"},
            {"label": "Protestant", "value": "Protestant"},
            {"label": "Orthodox", "value": "Orthodox"},
            {"label": "Evangelical", "value": "Evangelical"},
            {"label": "Other", "value": "Other"}
        ],
        "Jain": [
            {"label": "Digambar", "value": "Digambar"},
            {"label": "Shwetambar", "value": "Shwetambar"},
            {"label": "Other", "value": "Other"}
        ],
        # Sikh: practice level already covers Amritdhari/Keshdhari/Sehajdhari
        # Buddhist/Other/None: skip
    }
    return sects.get(religion)  # Returns None → skip


def get_castes_by_religion(religion: str):
    """Caste/community options based on religion"""
    castes = {
        "Hindu": [
            {"label": "Brahmin", "value": "Brahmin"},
            {"label": "Rajput / Kshatriya", "value": "Kshatriya / Rajput"},
            {"label": "Baniya / Vaishya", "value": "Vaishya / Baniya"},
            {"label": "Kayastha", "value": "Kayastha"},
            {"label": "Maratha", "value": "Maratha"},
            {"label": "Reddy", "value": "Reddy"},
            {"label": "Nair", "value": "Nair"},
            {"label": "Ezhava", "value": "Ezhava"},
            {"label": "Patel", "value": "Patel"},
            {"label": "Agarwal", "value": "Agarwal"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ],
        "Jain": [
            {"label": "Agarwal", "value": "Agarwal"},
            {"label": "Oswal", "value": "Oswal"},
            {"label": "Porwal", "value": "Porwal"},
            {"label": "Digambar", "value": "Digambar"},
            {"label": "Shwetambar", "value": "Shwetambar"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ],
        "Sikh": [
            {"label": "Jat", "value": "Jat"},
            {"label": "Khatri", "value": "Khatri"},
            {"label": "Arora", "value": "Arora"},
            {"label": "Ramgarhia", "value": "Ramgarhia"},
            {"label": "Saini", "value": "Saini"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ],
        # Muslim: skip caste
        # Christian: skip caste
        # Buddhist: skip caste
        # Other/None: skip caste
    }
    return castes.get(religion)  # Returns None → skip


def get_diet_by_religion(religion: str, practice: str = None):
    """Diet options conditional on religion and practice level"""
    diets = {
        "Jain": [
            {"label": "Jain veg (no onion/garlic)", "value": "Jain food (no root veg, no onion/garlic)"},
            {"label": "Jain veg (flexible)", "value": "Pure vegetarian (no eggs)"},
            {"label": "Other", "value": "Other"}
        ],
        "Hindu": [
            {"label": "Vegetarian", "value": "Pure vegetarian (no eggs)"},
            {"label": "Eggetarian", "value": "Eggetarian"},
            {"label": "Non-veg", "value": "Non-vegetarian"},
            {"label": "Flexible", "value": "No restrictions"}
        ],
        "Muslim": [
            {"label": "Halal non-veg", "value": "Halal only"},
            {"label": "Non-veg (any)", "value": "Non-vegetarian"},
            {"label": "Vegetarian", "value": "Pure vegetarian (no eggs)"},
            {"label": "Flexible", "value": "No restrictions"}
        ],
        "Sikh": [
            {"label": "Vegetarian", "value": "Pure vegetarian (no eggs)"},
            {"label": "Non-veg", "value": "Non-vegetarian"},
            {"label": "Flexible", "value": "No restrictions"}
        ],
        "Christian": [
            {"label": "Vegetarian", "value": "Pure vegetarian (no eggs)"},
            {"label": "Non-veg", "value": "Non-vegetarian"},
            {"label": "Flexible", "value": "No restrictions"}
        ],
    }
    # Default for Buddhist/Other/None
    default = [
        {"label": "Vegetarian", "value": "Pure vegetarian (no eggs)"},
        {"label": "Vegan", "value": "Vegan"},
        {"label": "Non-veg", "value": "Non-vegetarian"},
        {"label": "Flexible", "value": "No restrictions"}
    ]
    return diets.get(religion, default)


# ============== SECTION TRANSITIONS & BUY-INS ==============

SECTION_TRANSITIONS = {
    "niyat_buyin": """Let's start with the important stuff \u2014
not your name, not your age. What you
actually want. This helps me understand
what kind of match to look for.""",

    "after_niyat": """Good. Now I know what I'm looking for on your behalf.
Let me learn about you \u2014 the basics first. Quick stuff.""",

    "after_parichay": """Got it, {name}. Quick and easy \u2713

Now \u2014 your faith, your culture, your roots.

Not the checkbox version. The real one.""",

    "after_dharam": """\u2713 Faith & culture \u2014 done.

Now about your family.

You want to choose your person. You also want
your family to be happy with that choice.

I'm matching for both.""",

    "after_parivar": """\u2713 Family \u2014 done.

Now the everyday stuff. Diet, lifestyle, habits.
The things that seem small but end up mattering
a lot when you're building a life together.""",

    "jeevan_shaili_milestone": """You're past the halfway mark \u2713

Four more gunas about your values, then we're
done. You're doing great, {name}.""",

    "soch_buyin": """Last section. This is the good stuff \u2014 not what
you look like on paper, but who you actually are.

Two of these are open-ended. Take your time.
The more you write, the better your match.""",
}

CLOSE_MESSAGE = """{name}, you're in. All 36 gunas \u2014 done. \u2713

Here's what happens now:

I'm going to look through the community for
someone who fits \u2014 not just on paper, but in
real life. Culture, values, lifestyle, family vibe.

When I find someone I'm confident about, I'll
message you with my reasoning. No name, no photo
\u2014 just why I think you two should meet.

If you say yes, they see the same about you.
If they say yes too, I make the introduction.

It might take a few days. It might take longer.
I'd rather wait than send you someone who
isn't right.

I'll be in touch. \u2713"""


# ============== ERROR MESSAGES ==============

ERROR_MESSAGES = {
    "button_expected": "Just tap one of the options above \U0001f446",
    "sticker_during_buttons": "\U0001f604 Save that energy \u2014 just tap a button for now.",
    "invalid_input": "That doesn't look right. Please try again:",
    "network_error": "Oops, something went wrong. Let me try that again..."
}


# ============== RESUME MESSAGES ==============

RESUME_PROMPT = """Hey {name}, we were getting through the 36 gunas \u2014 want to pick up where we left off?

Progress: {current}/{total} gunas"""

RESUME_BUTTONS = ["\u2713 Resume", "\u21BB Start over"]


# ============== VALIDATION RULES ==============

VALIDATION_RULES = {
    "date_of_birth": {
        "format": "DD/MM/YYYY",
        "min_age": 18,
        "max_age": 80,
        "error_format": "Invalid format. Please use DD/MM/YYYY (e.g., 15/03/1995)",
        "error_range": "Age must be between 18 and 80."
    },
}
