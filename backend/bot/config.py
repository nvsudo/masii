"""
Masii Bot Configuration — Question Flow
Source of truth: docs/question-flow.md
All channels (Telegram, Web, WhatsApp) derive from this config.
"""

from enum import Enum
from typing import Dict, List, Optional


class Phase(Enum):
    SETUP = "setup"                    # Phase 0: Intent, Name, Gender
    BASICS = "basics"                  # Phase 1: Parichay
    BACKGROUND = "background"          # Phase 2: Dharam
    PARTNER_BG = "partner_bg"          # Phase 3: Partner Background
    EDUCATION = "education"            # Phase 4: Vidya
    FAMILY = "family"                  # Phase 5: Parivar
    LIFESTYLE = "lifestyle"            # Phase 6: Jeevan Shaili
    MARRIAGE = "marriage"              # Phase 7: Shaadi
    PARTNER_PHYS = "partner_physical"  # Phase 8: Partner Physical
    HOUSEHOLD = "household"            # Phase 9: Household (gender-forked)
    SENSITIVE = "sensitive"            # Phase 10: Sensitive (opt-in)
    SOCIAL = "social"                  # Phase 11: Social
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

I'll ask you a set of questions about your life —
your values, your lifestyle, your family, your future.

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

The more I know, the better the match.

Your data is never sold. Never shared without
your permission.""",
        "button": "Got it \u2192"
    },
]


# ============== PHASE 0: SETUP ==============

INTENT_MESSAGE = {
    "text": """Before we start —

Are you filling this out for yourself
or for someone else?""",
    "options": [
        {"label": "For myself", "value": "self"},
        {"label": "For someone else", "value": "proxy"}
    ]
}

# After intent = "self", ask name and gender before numbered questions
SETUP_QUESTIONS = {
    "full_name": {
        "field": "full_name",
        "db_table": "users",
        "text": "What's your name?",
        "type": "text_input",
        "placeholder": "Your first name"
    },
    "gender": {
        "field": "gender",
        "db_table": "users",
        "text": "Are you male or female?",
        "type": "single_select",
        "options": [
            {"label": "Male", "value": "Male"},
            {"label": "Female", "value": "Female"}
        ]
    },
}


# ============== PROXY FLOW ==============

PROXY_QUESTIONS = [
    {
        "field": "proxy_relation",
        "text": "What's your relationship to them?",
        "type": "single_select",
        "options": [
            {"label": "Parent", "value": "parent"},
            {"label": "Sibling", "value": "sibling"},
            {"label": "Relative", "value": "relative"},
            {"label": "Friend", "value": "friend"}
        ]
    },
    {
        "field": "person_name",
        "text": "What's their name?",
        "type": "text_input",
        "placeholder": "Their first name"
    },
    {
        "field": "person_gender",
        "text": "Male or female?",
        "type": "single_select",
        "options": [
            {"label": "Male", "value": "Male"},
            {"label": "Female", "value": "Female"}
        ]
    },
    {
        "field": "person_phone",
        "text": "What's their phone number? (I'll send them a message to complete their profile.)",
        "type": "phone_input",
        "placeholder": "Phone number"
    },
    {
        "field": "person_age",
        "text": "How old are they?",
        "type": "single_select",
        "options": "birth_years"
    },
    {
        "field": "person_location",
        "text": "Where do they live?",
        "type": "location_tree",
    },
    {
        "field": "person_religion",
        "text": "What's their religion?",
        "type": "single_select",
        "options": [
            {"label": "Hindu", "value": "Hindu"},
            {"label": "Muslim", "value": "Muslim"},
            {"label": "Sikh", "value": "Sikh"},
            {"label": "Jain", "value": "Jain"},
            {"label": "Christian", "value": "Christian"},
            {"label": "Buddhist", "value": "Buddhist"},
            {"label": "Parsi", "value": "Parsi"},
            {"label": "No religion", "value": "No religion"},
            {"label": "Other", "value": "Other"}
        ]
    },
    {
        "field": "person_caste",
        "text": "What's their caste/community?",
        "type": "single_select",
        "options": "castes_by_religion",  # conditional on person_religion
    },
    {
        "field": "person_marital_status",
        "text": "Marital status?",
        "type": "single_select",
        "options": [
            {"label": "Never married", "value": "Never married"},
            {"label": "Divorced", "value": "Divorced"},
            {"label": "Widowed", "value": "Widowed"},
            {"label": "Awaiting divorce", "value": "Awaiting divorce"}
        ]
    },
    {
        "field": "person_education",
        "text": "Highest education?",
        "type": "single_select",
        "options": [
            {"label": "High school", "value": "High school"},
            {"label": "Diploma", "value": "Diploma"},
            {"label": "Bachelor's", "value": "Bachelor's"},
            {"label": "Master's", "value": "Master's"},
            {"label": "Doctorate / PhD", "value": "Doctorate / PhD"},
            {"label": "Professional (CA, CS, MBBS, LLB)", "value": "Professional (CA, CS, MBBS, LLB)"}
        ]
    },
    {
        "field": "person_occupation",
        "text": "What do they do?",
        "type": "single_select",
        "options": [
            {"label": "Public / Government", "value": "Public / Government"},
            {"label": "Private", "value": "Private"},
            {"label": "Professional (Doctor, Lawyer, CA)", "value": "Professional (Doctor, Lawyer, CA)"},
            {"label": "Business / Self-employed", "value": "Business / Self-employed"},
            {"label": "Startup", "value": "Startup"},
            {"label": "Not working", "value": "Not working"},
            {"label": "Student", "value": "Student"},
            {"label": "Other", "value": "Other"}
        ]
    },
]

PROXY_CLOSE_MESSAGE = """Thanks! I'll send {person_name} a message at their number to complete the rest. Their answers will be private \u2014 you won't see them. I'll let you know when their profile is ready.

\u2014 Masii"""


# ============== QUESTION DEFINITIONS ==============
# Sequential integer keys 1-60. Handler iterates in order.
# Questions with a "gender" field are only shown to that gender.
# Questions with "skip_if" logic are handled by conditional_logic.py.

QUESTIONS = {

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 1: BASICS (Parichay)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    1: {
        "section": "basics",
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
        "response_template": "{age} \u2014 got it \u2713"
    },

    2: {
        "section": "basics",
        "field": "location",
        "db_table": "users",
        "type": "location_tree",
        "step1": {
            "text": "Where do you live right now?",
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

    3: {
        "section": "basics",
        "field": "hometown",
        "db_table": "users",
        "type": "two_step_location",
        "step1": {
            "text": "Where is your family originally from? (State)",
            "type": "single_select",
            "field": "hometown_state",
            "options": "states_india_full",
            "columns": 2
        },
        "step2": {
            "text": "Which city or town?",
            "type": "text_input",
            "field": "hometown_city",
            "placeholder": "e.g. Ahmedabad, Jaipur, Lucknow..."
        }
    },

    4: {
        "section": "basics",
        "field": "mother_tongue",
        "db_table": "users",
        "text": "What is your mother tongue?",
        "type": "single_select",
        "options": [
            {"label": "Hindi", "value": "Hindi"},
            {"label": "Gujarati", "value": "Gujarati"},
            {"label": "Marathi", "value": "Marathi"},
            {"label": "Tamil", "value": "Tamil"},
            {"label": "Telugu", "value": "Telugu"},
            {"label": "Kannada", "value": "Kannada"},
            {"label": "Malayalam", "value": "Malayalam"},
            {"label": "Bengali", "value": "Bengali"},
            {"label": "Punjabi", "value": "Punjabi"},
            {"label": "Urdu", "value": "Urdu"},
            {"label": "Odia", "value": "Odia"},
            {"label": "Assamese", "value": "Assamese"},
            {"label": "Sindhi", "value": "Sindhi"},
            {"label": "Konkani", "value": "Konkani"},
            {"label": "Tulu", "value": "Tulu"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },

    5: {
        "section": "basics",
        "field": "languages_spoken",
        "db_table": "users",
        "text": "What other languages do you speak?",
        "type": "multi_select",
        "options": "languages_minus_mother_tongue",
        "done_label": "Done \u2713"
    },

    6: {
        "section": "basics",
        "field": "marital_status",
        "db_table": "users",
        "text": "What's your current marital status?",
        "type": "single_select",
        "options": [
            {"label": "Never married", "value": "Never married"},
            {"label": "Divorced", "value": "Divorced"},
            {"label": "Widowed", "value": "Widowed"},
            {"label": "Awaiting divorce", "value": "Awaiting divorce"}
        ]
    },

    7: {
        "section": "basics",
        "field": "height_cm",
        "db_table": "users",
        "text": "How tall are you?",
        "type": "single_select",
        "options": "height_by_gender",
    },

    8: {
        "section": "basics",
        "field": "weight_kg",
        "db_table": "users",
        "text": "What is your weight?",
        "type": "single_select",
        "options": "weight_by_gender",
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 2: BACKGROUND (Dharam)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    9: {
        "section": "background",
        "field": "religion",
        "db_table": "users",
        "text": "What is your religion?",
        "type": "single_select",
        "options": [
            {"label": "Hindu", "value": "Hindu"},
            {"label": "Muslim", "value": "Muslim"},
            {"label": "Sikh", "value": "Sikh"},
            {"label": "Jain", "value": "Jain"},
            {"label": "Christian", "value": "Christian"},
            {"label": "Buddhist", "value": "Buddhist"},
            {"label": "Parsi", "value": "Parsi"},
            {"label": "No religion", "value": "No religion"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },

    10: {
        "section": "background",
        "field": "religious_practice",
        "db_table": "preferences",
        "text": "How would you describe your religious practice?",
        "type": "single_select",
        "options": "practice_by_religion",
    },

    11: {
        "section": "background",
        "field": "sect_denomination",
        "db_table": "preferences",
        "text": "What is your sect or denomination?",
        "type": "single_select",
        "options": "sects_by_religion",
    },

    12: {
        "section": "background",
        "field": "caste_community",
        "db_table": "preferences",
        "text": "What is your caste or community?",
        "type": "single_select",
        "options": "castes_by_religion",
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 3: PARTNER BACKGROUND PREFERENCES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    13: {
        "section": "partner_bg",
        "field": "pref_religion",
        "db_table": "preferences",
        "text": "Partner's religion preference?",
        "type": "single_select",
        "options": [
            {"label": "Same religion only", "value": "Same religion only"},
            {"label": "Open to all", "value": "Open to all"},
            {"label": "Open, but not...", "value": "Open, but not..."}
        ]
    },

    14: {
        "section": "partner_bg",
        "field": "pref_caste",
        "db_table": "preferences",
        "text": "Partner's caste preference?",
        "type": "single_select",
        "options": [
            {"label": "Same caste only", "value": "Same caste only"},
            {"label": "Same community, any caste", "value": "Same community, any caste"},
            {"label": "Open to all", "value": "Open to all"},
            {"label": "Open, but not...", "value": "Open, but not..."}
        ]
    },

    15: {
        "section": "partner_bg",
        "field": "pref_mother_tongue",
        "db_table": "preferences",
        "text": "Partner's mother tongue preference?",
        "type": "single_select",
        "options": [
            {"label": "Same language only", "value": "Same language only"},
            {"label": "Same or Hindi", "value": "Same or Hindi"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 4: EDUCATION & CAREER (Vidya)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    16: {
        "section": "education",
        "field": "education_level",
        "db_table": "users",
        "text": "What is your highest education?",
        "type": "single_select",
        "options": [
            {"label": "High school", "value": "High school"},
            {"label": "Diploma", "value": "Diploma"},
            {"label": "Bachelor's", "value": "Bachelor's"},
            {"label": "Master's", "value": "Master's"},
            {"label": "Doctorate / PhD", "value": "Doctorate / PhD"},
            {"label": "Professional (CA, CS, MBBS, LLB)", "value": "Professional (CA, CS, MBBS, LLB)"}
        ],
        "columns": 2
    },

    17: {
        "section": "education",
        "field": "education_field",
        "db_table": "users",
        "text": "What field?",
        "type": "single_select",
        "options": [
            {"label": "Engineering / IT", "value": "Engineering / IT"},
            {"label": "Medicine / Healthcare", "value": "Medicine / Healthcare"},
            {"label": "Business / MBA", "value": "Business / MBA"},
            {"label": "Law", "value": "Law"},
            {"label": "Finance / CA / CS", "value": "Finance / CA / CS"},
            {"label": "Arts / Humanities", "value": "Arts / Humanities"},
            {"label": "Science", "value": "Science"},
            {"label": "Design / Architecture", "value": "Design / Architecture"},
            {"label": "Government / Civil Services", "value": "Government / Civil Services"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },

    18: {
        "section": "education",
        "field": "occupation_sector",
        "db_table": "users",
        "text": "What sector do you work in?",
        "type": "single_select",
        "options": [
            {"label": "Public / Government", "value": "Public / Government"},
            {"label": "Private", "value": "Private"},
            {"label": "Professional (Doctor, Lawyer, CA)", "value": "Professional (Doctor, Lawyer, CA)"},
            {"label": "Business / Self-employed", "value": "Business / Self-employed"},
            {"label": "Startup", "value": "Startup"},
            {"label": "Not working", "value": "Not working"},
            {"label": "Student", "value": "Student"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },

    19: {
        "section": "education",
        "field": "annual_income",
        "db_table": "users",
        "text": "What is your annual income? (This is only used for matching, never displayed.)",
        "type": "single_select",
        "options": "income_by_location",
    },

    20: {
        "section": "education",
        "field": "pref_education_min",
        "db_table": "preferences",
        "text": "Minimum education you'd want in a partner?",
        "type": "single_select",
        "options": [
            {"label": "Doesn't matter", "value": "Doesn't matter"},
            {"label": "At least Bachelor's", "value": "At least Bachelor's"},
            {"label": "At least Master's", "value": "At least Master's"},
            {"label": "At least Professional degree", "value": "At least Professional degree"}
        ]
    },

    21: {
        "section": "education",
        "field": "pref_income_min",
        "db_table": "preferences",
        "text": "Minimum income you'd want in a partner?",
        "type": "single_select",
        "options": "income_by_location_with_doesnt_matter",
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 5: FAMILY (Parivar)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    22: {
        "section": "family",
        "field": "family_type",
        "db_table": "users",
        "text": "What type of family do you come from?",
        "type": "single_select",
        "options": [
            {"label": "Nuclear", "value": "Nuclear"},
            {"label": "Joint", "value": "Joint"},
            {"label": "Semi-joint", "value": "Semi-joint"}
        ]
    },

    23: {
        "section": "family",
        "field": "family_status",
        "db_table": "users",
        "text": "How would you describe your family's financial status?",
        "type": "single_select",
        "options": [
            {"label": "Middle class", "value": "Middle class"},
            {"label": "Upper middle class", "value": "Upper middle class"},
            {"label": "Affluent", "value": "Affluent"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ]
    },

    24: {
        "section": "family",
        "field": "family_values",
        "db_table": "signals",
        "text": "How would you describe your family's values?",
        "type": "single_select",
        "options": [
            {"label": "Traditional", "value": "Traditional"},
            {"label": "Moderate", "value": "Moderate"},
            {"label": "Liberal", "value": "Liberal"}
        ]
    },

    25: {
        "section": "family",
        "field": "father_occupation",
        "db_table": "users",
        "text": "Father's occupation?",
        "type": "single_select",
        "options": [
            {"label": "Business / Self-employed", "value": "Business / Self-employed"},
            {"label": "Service / Salaried", "value": "Service / Salaried"},
            {"label": "Professional (Doctor, Lawyer, CA)", "value": "Professional (Doctor, Lawyer, CA)"},
            {"label": "Government", "value": "Government"},
            {"label": "Retired", "value": "Retired"},
            {"label": "Not alive", "value": "Not alive"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ]
    },

    26: {
        "section": "family",
        "field": "mother_occupation",
        "db_table": "users",
        "text": "Mother's occupation?",
        "type": "single_select",
        "options": [
            {"label": "Homemaker", "value": "Homemaker"},
            {"label": "Working professional", "value": "Working professional"},
            {"label": "Business", "value": "Business"},
            {"label": "Government", "value": "Government"},
            {"label": "Retired", "value": "Retired"},
            {"label": "Not alive", "value": "Not alive"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ]
    },

    27: {
        "section": "family",
        "field": "siblings",
        "db_table": "users",
        "text": "Do you have siblings?",
        "type": "single_select",
        "options": [
            {"label": "Only child", "value": "Only child"},
            {"label": "1 sibling", "value": "1 sibling"},
            {"label": "2 siblings", "value": "2 siblings"},
            {"label": "3+ siblings", "value": "3+ siblings"}
        ]
    },

    28: {
        "section": "family",
        "field": "family_involvement",
        "db_table": "preferences",
        "text": "How involved will your family be in the decision?",
        "type": "single_select",
        "options": [
            {"label": "Very \u2014 their approval matters", "value": "Very \u2014 their approval matters"},
            {"label": "Moderate \u2014 I'll decide but they have input", "value": "Moderate \u2014 I'll decide but they have input"},
            {"label": "Independent \u2014 my decision entirely", "value": "Independent \u2014 my decision entirely"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 6: LIFESTYLE (Jeevan Shaili)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    29: {
        "section": "lifestyle",
        "field": "diet",
        "db_table": "signals",
        "text": "What is your diet?",
        "type": "single_select",
        "options": "diet_by_religion",
    },

    30: {
        "section": "lifestyle",
        "field": "drinking",
        "db_table": "signals",
        "text": "Do you drink alcohol?",
        "type": "single_select",
        "options": [
            {"label": "Never", "value": "Never"},
            {"label": "Socially / Occasionally", "value": "Socially / Occasionally"},
            {"label": "Regularly", "value": "Regularly"}
        ]
    },

    31: {
        "section": "lifestyle",
        "field": "smoking",
        "db_table": "signals",
        "text": "Do you smoke?",
        "type": "single_select",
        "options": [
            {"label": "Never", "value": "Never"},
            {"label": "Socially / Occasionally", "value": "Socially / Occasionally"},
            {"label": "Regularly", "value": "Regularly"}
        ]
    },

    32: {
        "section": "lifestyle",
        "field": "fitness_frequency",
        "db_table": "signals",
        "text": "How often do you exercise or play sports?",
        "type": "single_select",
        "options": [
            {"label": "Daily", "value": "Daily"},
            {"label": "3-5 times a week", "value": "3-5 times a week"},
            {"label": "1-2 times a week", "value": "1-2 times a week"},
            {"label": "Rarely", "value": "Rarely"},
            {"label": "Never", "value": "Never"}
        ]
    },

    33: {
        "section": "lifestyle",
        "field": "pref_diet",
        "db_table": "preferences",
        "text": "Partner's diet preference?",
        "type": "single_select",
        "options": [
            {"label": "Same as mine", "value": "Same as mine"},
            {"label": "Vegetarian or above", "value": "Vegetarian or above"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },

    34: {
        "section": "lifestyle",
        "field": "pref_drinking",
        "db_table": "preferences",
        "text": "Partner's drinking \u2014 dealbreaker?",
        "type": "single_select",
        "options": [
            {"label": "Must not drink", "value": "Must not drink"},
            {"label": "Social drinking OK", "value": "Social drinking OK"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },

    35: {
        "section": "lifestyle",
        "field": "pref_smoking",
        "db_table": "preferences",
        "text": "Partner's smoking \u2014 dealbreaker?",
        "type": "single_select",
        "options": [
            {"label": "Must not smoke", "value": "Must not smoke"},
            {"label": "Social smoking OK", "value": "Social smoking OK"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 7: MARRIAGE & LIVING (Shaadi)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    36: {
        "section": "marriage",
        "field": "marriage_timeline",
        "db_table": "preferences",
        "text": "How soon are you looking to get married?",
        "type": "single_select",
        "options": [
            {"label": "Within 6 months", "value": "Within 6 months"},
            {"label": "In the next 1 year", "value": "In the next 1 year"},
            {"label": "In the next 2-3 years", "value": "In the next 2-3 years"},
            {"label": "Just exploring", "value": "Just exploring"}
        ]
    },

    37: {
        "section": "marriage",
        "field": "children_intent",
        "db_table": "preferences",
        "text": "Do you want children?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "Maybe / Open to it", "value": "Maybe / Open to it"},
            {"label": "No", "value": "No"}
        ]
    },

    38: {
        "section": "marriage",
        "field": "living_arrangement",
        "db_table": "preferences",
        "text": "After marriage, where would you want to live?",
        "type": "single_select",
        "options": [
            {"label": "With parents (joint family)", "value": "With parents (joint family)"},
            {"label": "Near parents but separate", "value": "Near parents but separate"},
            {"label": "Independent \u2014 wherever life takes us", "value": "Independent \u2014 wherever life takes us"},
            {"label": "Open to discussion", "value": "Open to discussion"}
        ]
    },

    39: {
        "section": "marriage",
        "field": "relocation_willingness",
        "db_table": "preferences",
        "text": "Would you relocate for the right match?",
        "type": "single_select",
        "options": [
            {"label": "Yes, anywhere", "value": "Yes, anywhere"},
            {"label": "Yes, within India", "value": "Yes, within India"},
            {"label": "Yes, within my state/country", "value": "Yes, within my state/country"},
            {"label": "No, I'm settled where I am", "value": "No, I'm settled where I am"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 8: PARTNER PREFERENCES \u2014 Physical
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    40: {
        "section": "partner_physical",
        "field": "pref_age_range",
        "db_table": "preferences",
        "type": "two_step_range",
        "step1": {
            "text": "Partner's minimum age?",
            "type": "single_select",
            "field": "pref_age_min",
            "options": "age_range_min",
            "columns": 3
        },
        "step2": {
            "text": "Partner's maximum age?",
            "type": "single_select",
            "field": "pref_age_max",
            "options": "age_range_max",
            "columns": 3
        }
    },

    41: {
        "section": "partner_physical",
        "field": "pref_height_range",
        "db_table": "preferences",
        "type": "two_step_range",
        "has_doesnt_matter": True,
        "step1": {
            "text": "Partner's minimum height?",
            "type": "single_select",
            "field": "pref_height_min",
            "options": "height_opposite_gender",
            "columns": 2
        },
        "step2": {
            "text": "Partner's maximum height?",
            "type": "single_select",
            "field": "pref_height_max",
            "options": "height_opposite_gender",
            "columns": 2
        },
        "doesnt_matter_option": {"label": "Doesn't matter", "value": "doesnt_matter"}
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 9: HOUSEHOLD (Gender-forked)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # --- Men only ---

    42: {
        "section": "household",
        "field": "cooking_contribution",
        "db_table": "signals",
        "gender": "Male",
        "text": "Out of 15 meals in a week, how many are you willing to cook?",
        "type": "single_select",
        "options": [
            {"label": "0", "value": "0"},
            {"label": "1-3", "value": "1-3"},
            {"label": "4-7", "value": "4-7"},
            {"label": "8-10", "value": "8-10"},
            {"label": "More than 10", "value": "More than 10"}
        ]
    },

    43: {
        "section": "household",
        "field": "household_contribution",
        "db_table": "signals",
        "gender": "Male",
        "text": "How do you see household responsibilities?",
        "type": "single_select",
        "options": [
            {"label": "Mostly her", "value": "Mostly her"},
            {"label": "Shared equally", "value": "Shared equally"},
            {"label": "Mostly outsourced (cook/maid)", "value": "Mostly outsourced (cook/maid)"},
            {"label": "Flexible \u2014 whatever works", "value": "Flexible \u2014 whatever works"}
        ]
    },

    44: {
        "section": "household",
        "field": "partner_working",
        "db_table": "preferences",
        "gender": "Male",
        "text": "Do you want your partner to work?",
        "type": "single_select",
        "options": [
            {"label": "Yes, she should have a career", "value": "Yes, she should have a career"},
            {"label": "Her choice", "value": "Her choice"},
            {"label": "Prefer she focuses on home", "value": "Prefer she focuses on home"}
        ]
    },

    # --- Women only ---

    45: {
        "section": "household",
        "field": "do_you_cook",
        "db_table": "signals",
        "gender": "Female",
        "text": "Do you know how to cook?",
        "type": "single_select",
        "options": [
            {"label": "Yes, I cook regularly", "value": "Yes, I cook regularly"},
            {"label": "Yes, but I don't cook often", "value": "Yes, but I don't cook often"},
            {"label": "No, but I'm willing to learn", "value": "No, but I'm willing to learn"},
            {"label": "No", "value": "No"}
        ]
    },

    46: {
        "section": "household",
        "field": "cooking_contribution",
        "db_table": "signals",
        "gender": "Female",
        "text": "Out of 15 meals in a week, how many are you willing to cook?",
        "type": "single_select",
        "options": [
            {"label": "0", "value": "0"},
            {"label": "1-3", "value": "1-3"},
            {"label": "4-7", "value": "4-7"},
            {"label": "8-10", "value": "8-10"},
            {"label": "More than 10", "value": "More than 10"}
        ]
    },

    47: {
        "section": "household",
        "field": "pref_partner_cooking",
        "db_table": "preferences",
        "gender": "Female",
        "text": "How often do you need your partner to cook?",
        "type": "single_select",
        "options": [
            {"label": "Regularly (7+ meals a week)", "value": "Regularly (7+ meals a week)"},
            {"label": "Sometimes (3-6 meals)", "value": "Sometimes (3-6 meals)"},
            {"label": "Rarely (1-2 meals)", "value": "Rarely (1-2 meals)"},
            {"label": "Never \u2014 I'll handle it or we'll outsource", "value": "Never \u2014 I'll handle it or we'll outsource"}
        ]
    },

    48: {
        "section": "household",
        "field": "pref_partner_household",
        "db_table": "preferences",
        "gender": "Female",
        "text": "How much do you need your partner to contribute to household chores?",
        "type": "single_select",
        "options": [
            {"label": "Equal share", "value": "Equal share"},
            {"label": "Significant help", "value": "Significant help"},
            {"label": "Some help", "value": "Some help"},
            {"label": "Not needed \u2014 I'll manage or outsource", "value": "Not needed \u2014 I'll manage or outsource"}
        ]
    },

    49: {
        "section": "household",
        "field": "career_after_marriage",
        "db_table": "signals",
        "gender": "Female",
        "text": "Do you plan to continue working after marriage?",
        "type": "single_select",
        "options": [
            {"label": "Yes, definitely", "value": "Yes, definitely"},
            {"label": "Yes, but open to a break for kids", "value": "Yes, but open to a break for kids"},
            {"label": "Undecided", "value": "Undecided"},
            {"label": "No, prefer homemaking", "value": "No, prefer homemaking"}
        ]
    },

    50: {
        "section": "household",
        "field": "financial_contribution",
        "db_table": "signals",
        "gender": "Female",
        "text": "How do you see financial contribution in a marriage?",
        "type": "single_select",
        "options": [
            {"label": "Equal partnership", "value": "Equal partnership"},
            {"label": "I'll contribute, he leads", "value": "I'll contribute, he leads"},
            {"label": "His responsibility primarily", "value": "His responsibility primarily"},
            {"label": "Flexible \u2014 depends on situation", "value": "Flexible \u2014 depends on situation"}
        ]
    },

    51: {
        "section": "household",
        "field": "live_with_inlaws",
        "db_table": "signals",
        "gender": "Female",
        "text": "Would you be OK living with his parents?",
        "type": "single_select",
        "options": [
            {"label": "Yes, happy to", "value": "Yes, happy to"},
            {"label": "For some time, not permanently", "value": "For some time, not permanently"},
            {"label": "Prefer not to", "value": "Prefer not to"},
            {"label": "Depends on the situation", "value": "Depends on the situation"}
        ]
    },

    # --- Both ---

    52: {
        "section": "household",
        "field": "financial_planning",
        "db_table": "signals",
        "text": "How should finances work in a marriage?",
        "type": "single_select",
        "options": [
            {"label": "Fully joint", "value": "Fully joint"},
            {"label": "Joint for household, separate for personal", "value": "Joint for household, separate for personal"},
            {"label": "Mostly separate", "value": "Mostly separate"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 10: SENSITIVE (Opt-in gate)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    53: {
        "section": "sensitive",
        "field": "sensitive_gate",
        "db_table": "meta",
        "text": """The next few questions cover criteria that traditional matchmakers ask. Some families consider these important.

Your answers are only used for matching and never published or shared with anyone \u2014 not even your match.

Skip this section if you'd rather not answer.

Would you like to answer these?""",
        "type": "single_select",
        "is_gate": True,
        "options": [
            {"label": "Yes", "value": "yes"},
            {"label": "No, skip", "value": "no"}
        ]
    },

    54: {
        "section": "sensitive",
        "field": "manglik_status",
        "db_table": "signals",
        "text": "Are you Manglik?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "No", "value": "No"},
            {"label": "Don't know", "value": "Don't know"},
            {"label": "Not applicable", "value": "Not applicable"}
        ]
    },

    55: {
        "section": "sensitive",
        "field": "gotra",
        "db_table": "signals",
        "text": "What is your gotra?",
        "type": "single_select",
        "options": "gotras_by_religion",
    },

    56: {
        "section": "sensitive",
        "field": "family_property",
        "db_table": "signals",
        "text": "Does your family own property?",
        "type": "single_select",
        "options": [
            {"label": "Rented home", "value": "Rented home"},
            {"label": "Own flat/apartment", "value": "Own flat/apartment"},
            {"label": "Own independent house", "value": "Own independent house"},
            {"label": "Own bungalow/villa", "value": "Own bungalow/villa"},
            {"label": "Agricultural land", "value": "Agricultural land"},
            {"label": "Multiple properties", "value": "Multiple properties"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ]
    },

    57: {
        "section": "sensitive",
        "field": "pref_family_status",
        "db_table": "preferences",
        "text": "Partner's family financial status preference?",
        "type": "single_select",
        "options": [
            {"label": "Same or higher", "value": "Same or higher"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },

    58: {
        "section": "sensitive",
        "field": "known_conditions",
        "db_table": "users",
        "text": "Do you have any known medical conditions or disabilities?",
        "type": "single_select",
        "options": [
            {"label": "No", "value": "No"},
            {"label": "Yes", "value": "Yes"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ]
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 11: SOCIAL & PERSONALITY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    59: {
        "section": "social",
        "field": "social_style",
        "db_table": "signals",
        "text": "How social are you?",
        "type": "single_select",
        "options": [
            {"label": "Very social \u2014 love big gatherings", "value": "Very social \u2014 love big gatherings"},
            {"label": "Social \u2014 enjoy going out but need downtime", "value": "Social \u2014 enjoy going out but need downtime"},
            {"label": "Introverted \u2014 prefer small groups", "value": "Introverted \u2014 prefer small groups"},
            {"label": "Very introverted \u2014 homebody", "value": "Very introverted \u2014 homebody"}
        ]
    },

    60: {
        "section": "social",
        "field": "conflict_style",
        "db_table": "signals",
        "text": "When there's a disagreement, you tend to...",
        "type": "single_select",
        "options": [
            {"label": "Talk it out immediately", "value": "Talk it out immediately"},
            {"label": "Take some time, then discuss", "value": "Take some time, then discuss"},
            {"label": "Avoid conflict", "value": "Avoid conflict"},
            {"label": "Get heated, then cool down", "value": "Get heated, then cool down"}
        ]
    },
}

TOTAL_QUESTIONS = 60
TOTAL_GUNAS = TOTAL_QUESTIONS  # backward compat


# ============== SUB-QUESTIONS ==============

SUB_QUESTIONS = {
    "children_existing": {
        "section": "basics",
        "field": "children_existing",
        "db_table": "users",
        "text": "Do you have children?",
        "type": "single_select",
        "after_guna": 6,
        "condition": "marital_status != 'Never married'",
        "options": [
            {"label": "No", "value": "No"},
            {"label": "Yes, they live with me", "value": "Yes, they live with me"},
            {"label": "Yes, they don't live with me", "value": "Yes, they don't live with me"}
        ]
    },
    "caste_importance": {
        "section": "background",
        "field": "caste_importance",
        "db_table": "preferences",
        "text": "How important is caste in your partner?",
        "type": "single_select",
        "after_guna": 12,
        "condition": "caste_community is not None and caste_community != 'Prefer not to say'",
        "options": [
            {"label": "Must be same caste", "value": "Must be same caste"},
            {"label": "Prefer same, open to others", "value": "Prefer same, open to others"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },
    "pref_religion_exclude": {
        "section": "partner_bg",
        "field": "pref_religion_exclude",
        "db_table": "preferences",
        "text": "Which religions would you NOT want to match with?",
        "type": "multi_select",
        "after_guna": 13,
        "condition": "pref_religion == 'Open, but not...'",
        "options": [
            {"label": "Hindu", "value": "Hindu"},
            {"label": "Muslim", "value": "Muslim"},
            {"label": "Sikh", "value": "Sikh"},
            {"label": "Jain", "value": "Jain"},
            {"label": "Christian", "value": "Christian"},
            {"label": "Buddhist", "value": "Buddhist"},
            {"label": "Parsi", "value": "Parsi"},
            {"label": "No religion", "value": "No religion"}
        ],
        "done_label": "Done \u2713"
    },
    "pref_caste_exclude": {
        "section": "partner_bg",
        "field": "pref_caste_exclude",
        "db_table": "preferences",
        "text": "Which castes would you NOT want to match with?",
        "type": "multi_select",
        "after_guna": 14,
        "condition": "pref_caste == 'Open, but not...'",
        "options": "castes_by_religion",
        "done_label": "Done \u2713"
    },
    "children_timeline": {
        "section": "marriage",
        "field": "children_timeline",
        "db_table": "preferences",
        "text": "When would you want children?",
        "type": "single_select",
        "after_guna": 37,
        "condition": "children_intent != 'No'",
        "options": [
            {"label": "Soon after marriage", "value": "Soon after marriage"},
            {"label": "After 2-3 years", "value": "After 2-3 years"},
            {"label": "After 4+ years", "value": "After 4+ years"}
        ]
    },
    "pref_manglik": {
        "section": "sensitive",
        "field": "pref_manglik",
        "db_table": "preferences",
        "text": "Is Manglik status important in your partner?",
        "type": "single_select",
        "after_guna": 54,
        "condition": "manglik_status is not None and manglik_status != 'Not applicable'",
        "options": [
            {"label": "Must match", "value": "Must match"},
            {"label": "Prefer, but flexible", "value": "Prefer, but flexible"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },
    "pref_gotra_exclude": {
        "section": "sensitive",
        "field": "pref_gotra_exclude",
        "db_table": "preferences",
        "text": "Any gotras you cannot match with?",
        "type": "multi_select",
        "after_guna": 55,
        "condition": "gotra is not None and gotra != 'Don\\'t know' and gotra != 'Not applicable'",
        "options": "gotras_by_religion",
        "done_label": "None / Doesn't matter"
    },
    "pref_conditions": {
        "section": "sensitive",
        "field": "pref_conditions",
        "db_table": "preferences",
        "text": "Would you be open to a partner with a medical condition or disability?",
        "type": "single_select",
        "after_guna": 58,
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "Depends on the condition", "value": "Depends on the condition"},
            {"label": "No", "value": "No"}
        ]
    },
}


# ============== DYNAMIC OPTION GENERATORS ==============

def get_birth_years():
    """Birth years from 1970 to 2006"""
    return [
        {"label": str(year), "value": str(year)}
        for year in range(2006, 1969, -1)
    ]


def get_countries():
    """Top countries for Indian diaspora"""
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
    """Indian states (major, for location)"""
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


def get_states_india_full():
    """All Indian states + UTs (for hometown)"""
    return [
        {"label": "Andhra Pradesh", "value": "Andhra Pradesh"},
        {"label": "Arunachal Pradesh", "value": "Arunachal Pradesh"},
        {"label": "Assam", "value": "Assam"},
        {"label": "Bihar", "value": "Bihar"},
        {"label": "Chhattisgarh", "value": "Chhattisgarh"},
        {"label": "Delhi NCR", "value": "Delhi NCR"},
        {"label": "Goa", "value": "Goa"},
        {"label": "Gujarat", "value": "Gujarat"},
        {"label": "Haryana", "value": "Haryana"},
        {"label": "Himachal Pradesh", "value": "Himachal Pradesh"},
        {"label": "Jharkhand", "value": "Jharkhand"},
        {"label": "Karnataka", "value": "Karnataka"},
        {"label": "Kerala", "value": "Kerala"},
        {"label": "Madhya Pradesh", "value": "Madhya Pradesh"},
        {"label": "Maharashtra", "value": "Maharashtra"},
        {"label": "Manipur", "value": "Manipur"},
        {"label": "Meghalaya", "value": "Meghalaya"},
        {"label": "Mizoram", "value": "Mizoram"},
        {"label": "Nagaland", "value": "Nagaland"},
        {"label": "Odisha", "value": "Odisha"},
        {"label": "Punjab", "value": "Punjab"},
        {"label": "Rajasthan", "value": "Rajasthan"},
        {"label": "Sikkim", "value": "Sikkim"},
        {"label": "Tamil Nadu", "value": "Tamil Nadu"},
        {"label": "Telangana", "value": "Telangana"},
        {"label": "Tripura", "value": "Tripura"},
        {"label": "Uttar Pradesh", "value": "Uttar Pradesh"},
        {"label": "Uttarakhand", "value": "Uttarakhand"},
        {"label": "West Bengal", "value": "West Bengal"},
        {"label": "Jammu & Kashmir", "value": "Jammu & Kashmir"},
        {"label": "Chandigarh", "value": "Chandigarh"},
        {"label": "Puducherry", "value": "Puducherry"},
    ]


def get_languages():
    """All Indian languages for multi-select"""
    return [
        {"label": "Hindi", "value": "Hindi"},
        {"label": "English", "value": "English"},
        {"label": "Gujarati", "value": "Gujarati"},
        {"label": "Marathi", "value": "Marathi"},
        {"label": "Tamil", "value": "Tamil"},
        {"label": "Telugu", "value": "Telugu"},
        {"label": "Kannada", "value": "Kannada"},
        {"label": "Malayalam", "value": "Malayalam"},
        {"label": "Bengali", "value": "Bengali"},
        {"label": "Punjabi", "value": "Punjabi"},
        {"label": "Urdu", "value": "Urdu"},
        {"label": "Odia", "value": "Odia"},
        {"label": "Assamese", "value": "Assamese"},
        {"label": "Sindhi", "value": "Sindhi"},
        {"label": "Konkani", "value": "Konkani"},
        {"label": "Tulu", "value": "Tulu"},
    ]


def get_languages_minus_mother_tongue(mother_tongue: str):
    """Languages for Q5, excluding the user's mother tongue"""
    all_langs = get_languages()
    return [l for l in all_langs if l["value"] != mother_tongue]


def get_height_options_female():
    """Height options for women (5'2" to 5'7" range)"""
    return [
        {"label": "Below 5'2\"", "value": "155"},
        {"label": "5'2\"", "value": "157"},
        {"label": "5'3\"", "value": "160"},
        {"label": "5'4\"", "value": "163"},
        {"label": "5'5\"", "value": "165"},
        {"label": "5'6\"", "value": "168"},
        {"label": "5'7\"", "value": "170"},
        {"label": "Above 5'7\"", "value": "173"},
    ]


def get_height_options_male():
    """Height options for men (5'5" to 6'3" range)"""
    return [
        {"label": "Below 5'5\"", "value": "163"},
        {"label": "5'5\"", "value": "165"},
        {"label": "5'6\"", "value": "168"},
        {"label": "5'7\"", "value": "170"},
        {"label": "5'8\"", "value": "173"},
        {"label": "5'9\"", "value": "175"},
        {"label": "5'10\"", "value": "178"},
        {"label": "5'11\"", "value": "180"},
        {"label": "6'0\"", "value": "183"},
        {"label": "6'1\"", "value": "185"},
        {"label": "6'2\"", "value": "188"},
        {"label": "6'3\"", "value": "191"},
        {"label": "Above 6'3\"", "value": "193"},
    ]


def get_height_by_gender(gender: str):
    """Height options conditional on gender"""
    if gender == "Female":
        return get_height_options_female()
    return get_height_options_male()


def get_height_opposite_gender(gender: str):
    """Height options for the opposite gender (for partner prefs)"""
    if gender == "Male":
        return get_height_options_female()
    return get_height_options_male()


def get_weight_options_female():
    """Weight options for women"""
    return [
        {"label": "Below 45 kg", "value": "42"},
        {"label": "45-50 kg", "value": "47"},
        {"label": "50-55 kg", "value": "52"},
        {"label": "55-60 kg", "value": "57"},
        {"label": "60-65 kg", "value": "62"},
        {"label": "65-70 kg", "value": "67"},
        {"label": "70-75 kg", "value": "72"},
        {"label": "75-80 kg", "value": "77"},
        {"label": "Above 80 kg", "value": "85"},
    ]


def get_weight_options_male():
    """Weight options for men"""
    return [
        {"label": "Below 60 kg", "value": "57"},
        {"label": "60-65 kg", "value": "62"},
        {"label": "65-70 kg", "value": "67"},
        {"label": "70-75 kg", "value": "72"},
        {"label": "75-80 kg", "value": "77"},
        {"label": "80-85 kg", "value": "82"},
        {"label": "85-90 kg", "value": "87"},
        {"label": "90-100 kg", "value": "95"},
        {"label": "Above 100 kg", "value": "105"},
    ]


def get_weight_by_gender(gender: str):
    """Weight options conditional on gender"""
    if gender == "Female":
        return get_weight_options_female()
    return get_weight_options_male()


def get_practice_by_religion(religion: str):
    """Practice level options conditional on religion"""
    practice = {
        "Hindu": [
            {"label": "Very religious", "value": "Very religious"},
            {"label": "Religious", "value": "Religious"},
            {"label": "Moderately religious", "value": "Moderately religious"},
            {"label": "Not religious", "value": "Not religious"}
        ],
        "Muslim": [
            {"label": "Very religious", "value": "Very religious"},
            {"label": "Religious", "value": "Religious"},
            {"label": "Moderately religious", "value": "Moderately religious"},
            {"label": "Liberal", "value": "Liberal"}
        ],
        "Sikh": [
            {"label": "Very religious (Amritdhari)", "value": "Very religious (Amritdhari)"},
            {"label": "Religious (Keshdhari)", "value": "Religious (Keshdhari)"},
            {"label": "Moderate (Sahajdhari)", "value": "Moderate (Sahajdhari)"},
            {"label": "Not religious", "value": "Not religious"}
        ],
        "Jain": [
            {"label": "Very religious", "value": "Very religious"},
            {"label": "Religious", "value": "Religious"},
            {"label": "Moderately religious", "value": "Moderately religious"},
            {"label": "Not religious", "value": "Not religious"}
        ],
        "Christian": [
            {"label": "Very religious", "value": "Very religious"},
            {"label": "Religious", "value": "Religious"},
            {"label": "Moderately religious", "value": "Moderately religious"},
            {"label": "Not religious", "value": "Not religious"}
        ],
    }
    return practice.get(religion)  # None for Buddhist/Parsi/No religion/Other \u2192 skip


def get_sects_by_religion(religion: str):
    """Sect/denomination options based on religion"""
    sects = {
        "Hindu": [
            {"label": "Vaishnav", "value": "Vaishnav"},
            {"label": "Shaiv", "value": "Shaiv"},
            {"label": "Arya Samaji", "value": "Arya Samaji"},
            {"label": "Smartha", "value": "Smartha"},
            {"label": "ISKCON", "value": "ISKCON"},
            {"label": "None / Other", "value": "None / Other"}
        ],
        "Muslim": [
            {"label": "Sunni", "value": "Sunni"},
            {"label": "Shia", "value": "Shia"},
            {"label": "Sufi", "value": "Sufi"},
            {"label": "Ahmadiyya", "value": "Ahmadiyya"},
            {"label": "None / Other", "value": "None / Other"}
        ],
        "Jain": [
            {"label": "Digambar", "value": "Digambar"},
            {"label": "Shwetambar", "value": "Shwetambar"},
            {"label": "Other", "value": "Other"}
        ],
        "Christian": [
            {"label": "Catholic", "value": "Catholic"},
            {"label": "Protestant", "value": "Protestant"},
            {"label": "Orthodox", "value": "Orthodox"},
            {"label": "Evangelical", "value": "Evangelical"},
            {"label": "Other", "value": "Other"}
        ],
    }
    return sects.get(religion)  # None \u2192 skip


def get_castes_by_religion(religion: str):
    """Caste/community options based on religion"""
    castes = {
        "Hindu": [
            {"label": "Brahmin", "value": "Brahmin"},
            {"label": "Agarwal", "value": "Agarwal"},
            {"label": "Baniya", "value": "Baniya"},
            {"label": "Jat", "value": "Jat"},
            {"label": "Kayastha", "value": "Kayastha"},
            {"label": "Kshatriya", "value": "Kshatriya"},
            {"label": "Maratha", "value": "Maratha"},
            {"label": "Patel", "value": "Patel"},
            {"label": "Rajput", "value": "Rajput"},
            {"label": "Reddy", "value": "Reddy"},
            {"label": "Nair", "value": "Nair"},
            {"label": "Iyer", "value": "Iyer"},
            {"label": "Iyengar", "value": "Iyengar"},
            {"label": "Gupta", "value": "Gupta"},
            {"label": "Khatri", "value": "Khatri"},
            {"label": "Arora", "value": "Arora"},
            {"label": "Sindhi", "value": "Sindhi"},
            {"label": "Lingayat", "value": "Lingayat"},
            {"label": "Scheduled Caste", "value": "Scheduled Caste"},
            {"label": "Scheduled Tribe", "value": "Scheduled Tribe"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ],
        "Jain": [
            {"label": "Agarwal", "value": "Agarwal"},
            {"label": "Baniya", "value": "Baniya"},
            {"label": "Oswal", "value": "Oswal"},
            {"label": "Porwal", "value": "Porwal"},
            {"label": "Shrimal", "value": "Shrimal"},
            {"label": "Khandelwal", "value": "Khandelwal"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ],
        "Sikh": [
            {"label": "Jat Sikh", "value": "Jat Sikh"},
            {"label": "Khatri Sikh", "value": "Khatri Sikh"},
            {"label": "Arora Sikh", "value": "Arora Sikh"},
            {"label": "Ramgarhia", "value": "Ramgarhia"},
            {"label": "Saini", "value": "Saini"},
            {"label": "Ravidasia", "value": "Ravidasia"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": "Prefer not to say"}
        ],
    }
    return castes.get(religion)  # None \u2192 skip


def get_diet_by_religion(religion: str):
    """Diet options conditional on religion"""
    diets = {
        "Jain": [
            {"label": "Strict Jain (no onion/garlic)", "value": "Strict Jain (no onion/garlic)"},
            {"label": "Jain vegetarian", "value": "Jain vegetarian"},
            {"label": "Flexible", "value": "Flexible"}
        ],
        "Hindu": [
            {"label": "Pure vegetarian (no onion/garlic)", "value": "Pure vegetarian (no onion/garlic)"},
            {"label": "Vegetarian", "value": "Vegetarian"},
            {"label": "Eggetarian", "value": "Eggetarian"},
            {"label": "Non-vegetarian", "value": "Non-vegetarian"},
            {"label": "Flexible", "value": "Flexible"}
        ],
        "Muslim": [
            {"label": "Halal only", "value": "Halal only"},
            {"label": "Non-vegetarian", "value": "Non-vegetarian"},
            {"label": "Flexible", "value": "Flexible"}
        ],
        "Sikh": [
            {"label": "Vegetarian", "value": "Vegetarian"},
            {"label": "Non-vegetarian", "value": "Non-vegetarian"},
            {"label": "Flexible", "value": "Flexible"}
        ],
    }
    default = [
        {"label": "Vegetarian", "value": "Vegetarian"},
        {"label": "Vegan", "value": "Vegan"},
        {"label": "Eggetarian", "value": "Eggetarian"},
        {"label": "Non-vegetarian", "value": "Non-vegetarian"},
        {"label": "Flexible", "value": "Flexible"}
    ]
    return diets.get(religion, default)


def get_income_brackets_inr():
    """Income brackets in INR"""
    return [
        {"label": "Under \u20b95 lakh", "value": "Under \u20b95 lakh"},
        {"label": "\u20b95-10 lakh", "value": "\u20b95-10 lakh"},
        {"label": "\u20b910-20 lakh", "value": "\u20b910-20 lakh"},
        {"label": "\u20b920-35 lakh", "value": "\u20b920-35 lakh"},
        {"label": "\u20b935-50 lakh", "value": "\u20b935-50 lakh"},
        {"label": "\u20b950-75 lakh", "value": "\u20b950-75 lakh"},
        {"label": "\u20b975 lakh - \u20b91 crore", "value": "\u20b975 lakh - \u20b91 crore"},
        {"label": "\u20b91-2 crore", "value": "\u20b91-2 crore"},
        {"label": "Above \u20b92 crore", "value": "Above \u20b92 crore"},
        {"label": "Prefer not to say", "value": "Prefer not to say"}
    ]


def get_income_brackets_usd():
    """Income brackets in USD (for NRIs)"""
    return [
        {"label": "Under $30K", "value": "Under $30K"},
        {"label": "$30-50K", "value": "$30-50K"},
        {"label": "$50-75K", "value": "$50-75K"},
        {"label": "$75-100K", "value": "$75-100K"},
        {"label": "$100-150K", "value": "$100-150K"},
        {"label": "$150-250K", "value": "$150-250K"},
        {"label": "Above $250K", "value": "Above $250K"},
        {"label": "Prefer not to say", "value": "Prefer not to say"}
    ]


def get_income_by_location(is_nri: bool):
    """Income brackets based on location (India vs abroad)"""
    return get_income_brackets_usd() if is_nri else get_income_brackets_inr()


def get_income_by_location_with_doesnt_matter(is_nri: bool):
    """Income brackets + Doesn't matter option"""
    brackets = get_income_by_location(is_nri)
    return [{"label": "Doesn't matter", "value": "Doesn't matter"}] + brackets


def get_age_range_min():
    """Age range for partner preference min"""
    return [{"label": str(a), "value": str(a)} for a in range(18, 46)]


def get_age_range_max(min_age: int = 18):
    """Age range for partner preference max (starts at min_age)"""
    return [{"label": str(a), "value": str(a)} for a in range(min_age, 51)]


def get_gotras_by_religion(religion: str):
    """Common gotras based on religion"""
    gotras = {
        "Hindu": [
            {"label": "Bharadwaj", "value": "Bharadwaj"},
            {"label": "Kashyap", "value": "Kashyap"},
            {"label": "Vasishtha", "value": "Vasishtha"},
            {"label": "Gautam", "value": "Gautam"},
            {"label": "Atri", "value": "Atri"},
            {"label": "Vishwamitra", "value": "Vishwamitra"},
            {"label": "Jamadagni", "value": "Jamadagni"},
            {"label": "Agastya", "value": "Agastya"},
            {"label": "Sandilya", "value": "Sandilya"},
            {"label": "Kaushik", "value": "Kaushik"},
            {"label": "Other", "value": "Other"},
            {"label": "Don't know", "value": "Don't know"},
            {"label": "Not applicable", "value": "Not applicable"}
        ],
        "Jain": [
            {"label": "Kashyap", "value": "Kashyap"},
            {"label": "Gautam", "value": "Gautam"},
            {"label": "Other", "value": "Other"},
            {"label": "Don't know", "value": "Don't know"},
            {"label": "Not applicable", "value": "Not applicable"}
        ],
        "Sikh": [
            {"label": "Bharadwaj", "value": "Bharadwaj"},
            {"label": "Kashyap", "value": "Kashyap"},
            {"label": "Sandhu", "value": "Sandhu"},
            {"label": "Other", "value": "Other"},
            {"label": "Don't know", "value": "Don't know"},
            {"label": "Not applicable", "value": "Not applicable"}
        ],
    }
    return gotras.get(religion)  # None \u2192 skip


# ============== SECTION TRANSITIONS ==============

SECTION_TRANSITIONS = {
    "basics": "Let's start with the basics, {name}.",

    "background": """Now a bit about your background, {name}.
This helps me find people from compatible communities.""",

    "partner_bg": "Now let's talk about what you're looking for in a partner's background.",

    "education": "Let's talk about education and career, {name}.",

    "family": """Family matters in Indian matchmaking.
Let's cover that, {name}.""",

    "lifestyle": "Almost there, {name}. A few questions about how you live day to day.",

    "marriage": "Let's talk about what married life looks like for you, {name}.",

    "partner_physical": "A few preferences about your partner, {name}.",

    "household": "The next few are about how you see daily life in a marriage. No right answers \u2014 just honest ones.",

    "social": "Last stretch, {name}. A few about how you are socially.",
}

CLOSE_MESSAGE = """Done, {name}! I have everything I need. I'll start searching for your match and message you when I find someone worth your time. Sit tight.

\u2014 Masii"""


# ============== ERROR MESSAGES ==============

ERROR_MESSAGES = {
    "button_expected": "Just tap one of the options above \U0001f446",
    "sticker_during_buttons": "\U0001f604 Save that energy \u2014 just tap a button for now.",
    "invalid_input": "That doesn't look right. Please try again:",
    "network_error": "Oops, something went wrong. Let me try that again..."
}


# ============== RESUME MESSAGES ==============

RESUME_PROMPT = """Hey {name}, we were getting through your profile \u2014 want to pick up where we left off?

Progress: {current} of {total} questions"""

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
