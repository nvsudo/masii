"""
JODI Bot Configuration
Data-driven button configurations for all 77 onboarding questions
"""

from enum import Enum
from typing import Dict, List, Optional

class OnboardingSection(Enum):
    INTRO = "intro"
    IDENTITY_BASICS = "identity_basics"  # Section A: 1-9
    LOCATION_MOBILITY = "location_mobility"  # Section B: 10-17
    RELIGION_CULTURE = "religion_culture"  # Section C: 18-27
    EDUCATION_CAREER = "education_career"  # Section D: 28-32
    FINANCIAL = "financial"  # Section E: 33-37
    FAMILY = "family"  # Section F: 38-44
    LIFESTYLE = "lifestyle"  # Section G: 45-55
    PARTNER_PREFS = "partner_prefs"  # Section H: 56-64
    VALUES = "values"  # Section I: 65-72
    DEALBREAKERS = "dealbreakers"  # Section J: 73-77
    PHOTO_UPLOAD = "photo_upload"
    SUMMARY = "summary"
    CONVERSATIONAL = "conversational"


# ============== INTRO MESSAGES ==============

INTRO_MESSAGES = [
    {
        "text": """Hey! 👋 I'm Jodi.

I help people find real, lasting relationships.
No swiping. No algorithms optimized to keep you scrolling.

Just one great introduction at a time.""",
        "button": "Tell me more →"
    },
    {
        "text": """Before we start — something important.

This is your space. Whatever you share here is between us. It doesn't go on a profile. It doesn't go on a form. Your parents won't see it. Your friends won't see it. No one sees anything unless you approve it.

You can tell me things here that you might not say out loud — what you actually want, what you've been through, what matters to you when no one's watching.

I'm not here to judge. I'm here to find you the right person. The more honest you are with me, the better I can do that.""",
        "button": "I like that. Keep going →"
    },
    {
        "text": """One thing we do differently — photos come at the end of our process, not the beginning.

We know not everyone photographs well. And honestly, AI filters have made photos pretty unreliable anyway.

I'd rather understand who you are first — your values, your energy, what makes you laugh, what you need in a partner. That's what actually predicts a great match.

Photos matter, but they're not the whole story. And they're definitely not the first chapter.""",
        "button": "That's refreshing →"
    },
    {
        "text": """Here's how I find people for you:

I start with your basics and deal-breakers to filter out anyone who clearly isn't right.

Then I go deeper — personality, values, lifestyle, the stuff that actually makes two people click.

When I find someone promising, I'll introduce you. One person at a time, with context on why I think you'd work well together.""",
        "button": "And then? →"
    },
    {
        "text": """The best part — I learn as we go.

When I show you a match, your reaction teaches me something. What excited you. What felt off. What surprised you.

Even the matches that don't work out make the next one better. Think of it like a friend who sets you up — except I remember everything and never stop trying.""",
        "button": "Makes sense →"
    },
    {
        "text": """Okay, here's the plan:

First, I'll ask some quick-tap questions — deal-breakers, lifestyle, the structured stuff. Takes about 8 minutes. No typing, just tapping.

After that, we switch to real conversation. I'll ask you questions a good friend would ask if they were setting you up. Answer whenever you feel like it — no rush, no pressure.

And if you ever want to change an answer, just tell me later during our chats. Nothing is locked in.""",
        "button": "Let's start →"
    },
    {
        "text": """Last thing — your privacy.

🔒 Your data is encrypted and never sold
🔒 Matches only see what you approve
🔒 You can delete everything at any time
🔒 I'll always ask before sharing anything

This only works if we trust each other. I take that seriously.""",
        "button": "Got it, let's go →"
    }
]


# ============== QUESTION DEFINITIONS ==============

QUESTIONS = {
    # SECTION A: IDENTITY & BASICS (Q1-Q9)
    1: {
        "section": "identity_basics",
        "field": "gender_identity",
        "db_table": "users",
        "text": "How do you identify?",
        "type": "single_select",
        "options": [
            {"label": "👨 Male", "value": "Male"},
            {"label": "👩 Female", "value": "Female"},
            {"label": "⚧️ Non-binary", "value": "Non-binary"},
            {"label": "💬 Self-describe →", "value": "custom", "requires_text": True}
        ]
    },
    
    2: {
        "section": "identity_basics",
        "field": "looking_for_gender",
        "db_table": "users",
        "text": "Who are you looking to meet?",
        "type": "single_select",
        "options": [
            {"label": "Men", "value": "Men"},
            {"label": "Women", "value": "Women"},
            {"label": "Both", "value": "Both"},
            {"label": "Other →", "value": "Other", "requires_text": True}
        ],
        "columns": 2
    },
    
    3: {
        "section": "identity_basics",
        "field": "date_of_birth",
        "db_table": "users",
        "type": "two_step_date",
        "step1": {
            "text": "What year were you born?",
            "type": "single_select",
            "field": "birth_year",
            "options": "birth_years",  # Dynamic
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
        "response_template": "{age} — got it ✓"
    },
    
    4: {
        "section": "identity_basics",
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
    
    5: {
        "section": "identity_basics",
        "field": "children_existing",
        "db_table": "users",
        "text": "Do you have children already?",
        "type": "single_select",
        "condition": "marital_status != 'Never married'",
        "options": [
            {"label": "No", "value": "No"},
            {"label": "Yes, they live with me", "value": "Yes, they live with me"},
            {"label": "Yes, they don't live with me", "value": "Yes, they don't live with me"}
        ]
    },
    
    6: {
        "section": "identity_basics",
        "field": "height_cm",
        "db_table": "users",
        "text": "How tall are you? (Optional)",
        "type": "single_select",
        "options": [
            {"label": "Under 5'2\" / <157cm", "value": "150"},
            {"label": "5'2\"–5'5\" / 157–165cm", "value": "160"},
            {"label": "5'5\"–5'8\" / 165–173cm", "value": "170"},
            {"label": "5'8\"–5'11\" / 173–180cm", "value": "177"},
            {"label": "5'11\"–6'1\" / 180–185cm", "value": "183"},
            {"label": "6'1\"+ / 185cm+", "value": "190"},
            {"label": "Skip", "value": None}
        ],
        "columns": 2
    },
    
    7: {
        "section": "identity_basics",
        "field": "body_type",
        "db_table": "users",
        "text": "How would you describe your build?",
        "type": "single_select",
        "options": [
            {"label": "Slim", "value": "Slim"},
            {"label": "Average", "value": "Average"},
            {"label": "Athletic", "value": "Athletic"},
            {"label": "Curvy", "value": "Curvy"},
            {"label": "Full-figured", "value": "Full-figured"},
            {"label": "Prefer not to say", "value": None}
        ],
        "columns": 2
    },
    
    8: {
        "section": "identity_basics",
        "field": "partner_body_type_pref",
        "db_table": "preferences",
        "text": "What about your ideal partner?",
        "type": "single_select",
        "options": [
            {"label": "Slim", "value": "Slim"},
            {"label": "Average", "value": "Average"},
            {"label": "Athletic", "value": "Athletic"},
            {"label": "Curvy / Full-figured", "value": "Curvy / Full-figured"},
            {"label": "Any body type is fine", "value": "Any"}
        ],
        "columns": 2
    },
    
    9: {
        "section": "identity_basics",
        "field": "complexion",
        "db_table": "users",
        "text": "And your skin tone? (Optional — just for photo matching)",
        "type": "single_select",
        "options": [
            {"label": "Fair", "value": "Fair"},
            {"label": "Wheatish", "value": "Wheatish"},
            {"label": "Dusky", "value": "Dusky"},
            {"label": "Dark", "value": "Dark"},
            {"label": "Skip", "value": None}
        ],
        "columns": 2
    },
    
    12: {
        "section": "identity_basics",
        "field": "partner_complexion_pref",
        "db_table": "preferences",
        "text": "Your ideal partner's complexion?",
        "type": "single_select",
        "options": [
            {"label": "Fair preferred", "value": "Fair preferred"},
            {"label": "No preference", "value": "No preference"},
            {"label": "Skip", "value": None}
        ],
        "columns": 2
    },
    
    13: {
        "section": "identity_basics",
        "field": "disability_status",
        "db_table": "users",
        "text": "Do you have any disability or special needs we should know about?",
        "type": "single_select",
        "options": [
            {"label": "No", "value": "No"},
            {"label": "Yes (I'll explain)", "value": "Yes", "requires_text": True},
            {"label": "Prefer not to say", "value": None}
        ]
    },
    
    # SECTION B: LOCATION & MOBILITY (Q12-Q19)
    12: {
        "section": "location_mobility",
        "field": "residency_type",
        "db_table": "users",
        "text": "What's your residency status?",
        "type": "single_select",
        "options": [
            {"label": "Indian citizen (in India)", "value": "Indian citizen (in India)"},
            {"label": "NRI", "value": "NRI"},
            {"label": "OCI / PIO", "value": "OCI / PIO"},
            {"label": "Foreign national", "value": "Foreign national"}
        ]
    },
    
    13: {
        "section": "location_mobility",
        "field": "country_current",
        "db_table": "users",
        "type": "two_step_region",
        "condition": "residency_type != 'Indian citizen (in India)'",
        "step1": {
            "text": "Which region are you in?",
            "type": "single_select",
            "field": "region",
            "options": [
                {"label": "🇺🇸 USA", "value": "USA"},
                {"label": "🇬🇧 UK", "value": "UK"},
                {"label": "🇪🇺 Europe", "value": "Europe"},
                {"label": "🕌 Middle East", "value": "Middle East"},
                {"label": "🌏 Asia-Pacific", "value": "Asia-Pacific"},
                {"label": "🌍 Other", "value": "Other"}
            ],
            "columns": 2
        },
        "step2": {
            "text": "Which country?",
            "type": "single_select",
            "field": "country_current",
            "options": "countries_by_region",  # Dynamic based on region
            "columns": 2
        }
    },
    
    14: {
        "section": "location_mobility",
        "field": "state_india",
        "db_table": "users",
        "text": "Which state in India?",
        "type": "single_select",
        "condition": "residency_type == 'Indian citizen (in India)'",
        "options": "states_india",  # Dynamic list
        "columns": 2
    },
    
    15: {
        "section": "location_mobility",
        "field": "city_current",
        "db_table": "users",
        "text": "Which city?",
        "type": "text_input",
        "placeholder": "e.g. Mumbai, Dubai, Singapore..."
    },
    
    16: {
        "section": "location_mobility",
        "field": "hometown_state",
        "db_table": "users",
        "text": "Where's your hometown / family from?",
        "type": "text_input",
        "placeholder": "State or city..."
    },
    
    17: {
        "section": "location_mobility",
        "field": "willing_to_relocate",
        "db_table": "users",
        "text": "Would you be willing to relocate for the right person?",
        "type": "single_select",
        "options": [
            {"label": "Yes, anywhere", "value": "Yes, anywhere"},
            {"label": "Within India", "value": "Within India"},
            {"label": "Abroad only", "value": "Abroad only"},
            {"label": "No, prefer to stay here", "value": "No, prefer to stay here"}
        ]
    },
    
    18: {
        "section": "location_mobility",
        "field": "partner_location_pref",
        "db_table": "preferences",
        "text": "Does your partner need to be in your city?",
        "type": "single_select",
        "options": [
            {"label": "Same city only", "value": "Same city only"},
            {"label": "Same country is fine", "value": "Same country is fine"},
            {"label": "Open to distance", "value": "Open to distance"},
            {"label": "Open to relocating", "value": "Open to relocating"}
        ]
    },
    
    19: {
        "section": "location_mobility",
        "field": "settling_country",
        "db_table": "users",
        "text": "Where do you ultimately want to settle down?",
        "type": "single_select",
        "condition": "residency_type in ['NRI', 'OCI / PIO']",
        "options": [
            {"label": "India", "value": "India"},
            {"label": "Current country", "value": "Current country"},
            {"label": "Flexible / Open", "value": "Flexible / Open"}
        ]
    },
    
    # SECTION C: RELIGION, CASTE & CULTURE (Q20-Q29)
    20: {
        "section": "religion_culture",
        "field": "religion",
        "db_table": "users",
        "text": "Your religion:",
        "type": "single_select",
        "options": [
            {"label": "Hindu", "value": "Hindu"},
            {"label": "Muslim", "value": "Muslim"},
            {"label": "Christian", "value": "Christian"},
            {"label": "Sikh", "value": "Sikh"},
            {"label": "Jain", "value": "Jain"},
            {"label": "Buddhist", "value": "Buddhist"},
            {"label": "Parsi/Zoroastrian", "value": "Parsi/Zoroastrian"},
            {"label": "Jewish", "value": "Jewish"},
            {"label": "No religion / Atheist", "value": "No religion / Atheist"},
            {"label": "Spiritual but not religious", "value": "Spiritual but not religious"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },
    
    21: {
        "section": "religion_culture",
        "field": "religious_practice",
        "db_table": "users",
        "text": "How religious are you?",
        "type": "single_select",
        "options": [
            {"label": "Very devout (daily practice)", "value": "Very devout (daily practice)"},
            {"label": "Moderately observant (festivals, rituals)", "value": "Moderately observant (festivals, rituals)"},
            {"label": "Culturally identify (not practicing)", "value": "Culturally identify (not practicing)"},
            {"label": "Spiritual, not religious", "value": "Spiritual, not religious"},
            {"label": "Not at all", "value": "Not at all"}
        ]
    },
    
    22: {
        "section": "religion_culture",
        "field": "partner_religion_pref",
        "db_table": "preferences",
        "pre_message": """Quick pause here 👋

Now I'm going to ask about what you're looking for in a partner.

Some of these questions might feel a bit direct — "Must they be the same religion?" "What income range?" — but here's why I ask:

I'd rather know your honest answer now than introduce you to someone who's a bad fit. If religion matters to you, that's valid. If it doesn't, that's valid too.

These answers stay private. I use them to filter matches, not judge you.""",
        "text": "Partner's religion:",
        "type": "single_select",
        "options": [
            {"label": "Must be same", "value": "Must be same"},
            {"label": "Prefer same, open to others", "value": "Prefer same, open to others"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ]
    },
    
    23: {
        "section": "religion_culture",
        "field": "sect_denomination",
        "db_table": "users",
        "text": "Which tradition do you follow?",
        "type": "single_select",
        "options": "sects_by_religion",  # Dynamic based on religion
        "condition": "religion in ['Hindu', 'Muslim', 'Christian', 'Sikh']"
    },
    
    24: {
        "section": "religion_culture",
        "field": "caste_community",
        "db_table": "users",
        "text": "Your community:",
        "type": "single_select",
        "options": "castes_by_religion",  # Dynamic based on religion
        "condition": "religion in ['Hindu', 'Jain', 'Sikh', 'Buddhist']"
    },
    
    25: {
        "section": "religion_culture",
        "field": "sub_caste",
        "db_table": "users",
        "text": "Sub-community or gotra? (Optional)",
        "type": "text_input",
        "placeholder": "e.g., Iyer, Agarwal, Garg...",
        "condition": "caste_community is not None"
    },
    
    26: {
        "section": "religion_culture",
        "field": "caste_importance",
        "db_table": "preferences",
        "text": "How important is caste/community match?",
        "type": "single_select",
        "options": [
            {"label": "Dealbreaker — must match", "value": "Dealbreaker — must match"},
            {"label": "Strong preference", "value": "Strong preference"},
            {"label": "Slight preference", "value": "Slight preference"},
            {"label": "Doesn't matter at all", "value": "Doesn't matter at all"}
        ]
    },
    
    27: {
        "section": "religion_culture",
        "field": "mother_tongue",
        "db_table": "users",
        "text": "Mother tongue:",
        "type": "single_select",
        "options": [
            {"label": "Hindi", "value": "Hindi"},
            {"label": "Tamil", "value": "Tamil"},
            {"label": "Telugu", "value": "Telugu"},
            {"label": "Kannada", "value": "Kannada"},
            {"label": "Malayalam", "value": "Malayalam"},
            {"label": "Bengali", "value": "Bengali"},
            {"label": "Marathi", "value": "Marathi"},
            {"label": "Gujarati", "value": "Gujarati"},
            {"label": "Punjabi", "value": "Punjabi"},
            {"label": "Odia", "value": "Odia"},
            {"label": "Assamese", "value": "Assamese"},
            {"label": "Urdu", "value": "Urdu"},
            {"label": "Konkani", "value": "Konkani"},
            {"label": "Sindhi", "value": "Sindhi"},
            {"label": "Kashmiri", "value": "Kashmiri"},
            {"label": "English", "value": "English"},
            {"label": "Other →", "value": "Other", "requires_text": True}
        ],
        "columns": 2
    },
    
    28: {
        "section": "religion_culture",
        "field": "languages_spoken",
        "db_table": "users",
        "text": "Languages you speak:",
        "type": "multi_select",
        "options": [
            {"label": "Hindi", "value": "Hindi"},
            {"label": "English", "value": "English"},
            {"label": "Tamil", "value": "Tamil"},
            {"label": "Telugu", "value": "Telugu"},
            {"label": "Kannada", "value": "Kannada"},
            {"label": "Malayalam", "value": "Malayalam"},
            {"label": "Bengali", "value": "Bengali"},
            {"label": "Marathi", "value": "Marathi"},
            {"label": "Gujarati", "value": "Gujarati"},
            {"label": "Punjabi", "value": "Punjabi"},
            {"label": "Odia", "value": "Odia"},
            {"label": "Assamese", "value": "Assamese"},
            {"label": "Urdu", "value": "Urdu"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },
    
    29: {
        "section": "religion_culture",
        "field": "manglik_status",
        "db_table": "users",
        "text": "Manglik status:",
        "type": "single_select",
        "condition": "religion in ['Hindu', 'Jain']",
        "options": [
            {"label": "Manglik", "value": "Manglik"},
            {"label": "Non-Manglik", "value": "Non-Manglik"},
            {"label": "Anshik Manglik", "value": "Anshik Manglik"},
            {"label": "Don't know", "value": "Don't know"},
            {"label": "Not applicable", "value": "Not applicable"}
        ]
    },
    
    # SECTION D: EDUCATION & CAREER (Q30-Q34)
    30: {
        "section": "education_career",
        "field": "education_level",
        "db_table": "users",
        "text": "Highest education:",
        "type": "single_select",
        "options": [
            {"label": "High school / 12th", "value": "High school / 12th"},
            {"label": "Diploma / ITI", "value": "Diploma / ITI"},
            {"label": "Bachelor's (BA/BSc/BCom)", "value": "Bachelor's (BA/BSc/BCom)"},
            {"label": "Bachelor's (BTech/BE/BBA)", "value": "Bachelor's (BTech/BE/BBA)"},
            {"label": "Master's (MA/MSc/MCom)", "value": "Master's (MA/MSc/MCom)"},
            {"label": "Master's (MBA/MTech)", "value": "Master's (MBA/MTech)"},
            {"label": "Professional (CA/CS/CFA/MBBS/LLB)", "value": "Professional (CA/CS/CFA/MBBS/LLB)"},
            {"label": "PhD / Doctorate", "value": "PhD / Doctorate"}
        ]
    },
    
    31: {
        "section": "education_career",
        "field": "education_institute_tier",
        "db_table": "users",
        "text": "Institute type:",
        "type": "single_select",
        "options": [
            {"label": "IIT / IIM / AIIMS / NLU / ISB", "value": "IIT / IIM / AIIMS / NLU / ISB"},
            {"label": "NITs / IIITs / Top private (BITS, VIT, etc.)", "value": "NITs / IIITs / Top private (BITS, VIT, etc.)"},
            {"label": "State university / Other private", "value": "State university / Other private"},
            {"label": "Studied abroad", "value": "Studied abroad"},
            {"label": "Other", "value": "Other"}
        ]
    },
    
    32: {
        "section": "education_career",
        "field": "employment_status",
        "db_table": "users",
        "text": "Employment:",
        "type": "single_select",
        "options": [
            {"label": "Employed full-time", "value": "Employed full-time"},
            {"label": "Self-employed / Business owner", "value": "Self-employed / Business owner"},
            {"label": "Freelancer / Consultant", "value": "Freelancer / Consultant"},
            {"label": "Government job", "value": "Government job"},
            {"label": "Student", "value": "Student"},
            {"label": "Between jobs", "value": "Between jobs"},
            {"label": "Homemaker", "value": "Homemaker"},
            {"label": "Retired", "value": "Retired"}
        ]
    },
    
    33: {
        "section": "education_career",
        "field": "work_industry",
        "db_table": "users",
        "text": "Industry / field:",
        "type": "single_select",
        "options": [
            {"label": "IT / Software", "value": "IT / Software"},
            {"label": "Finance / Banking", "value": "Finance / Banking"},
            {"label": "Healthcare / Pharma", "value": "Healthcare / Pharma"},
            {"label": "Education / Academia", "value": "Education / Academia"},
            {"label": "Government / PSU", "value": "Government / PSU"},
            {"label": "Legal", "value": "Legal"},
            {"label": "Media / Entertainment", "value": "Media / Entertainment"},
            {"label": "Manufacturing", "value": "Manufacturing"},
            {"label": "Real estate", "value": "Real estate"},
            {"label": "Agriculture / Farming", "value": "Agriculture / Farming"},
            {"label": "Startup", "value": "Startup"},
            {"label": "E-commerce", "value": "E-commerce"},
            {"label": "Defence / Armed forces", "value": "Defence / Armed forces"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 2
    },
    
    34: {
        "section": "education_career",
        "field": "career_ambition",
        "db_table": "users",
        "text": "Career priority:",
        "type": "single_select",
        "options": [
            {"label": "Highly ambitious (career comes first)", "value": "Highly ambitious (career comes first)"},
            {"label": "Career-oriented but balanced", "value": "Career-oriented but balanced"},
            {"label": "Flexible / adaptable", "value": "Flexible / adaptable"},
            {"label": "Prefer homemaking", "value": "Prefer homemaking"},
            {"label": "Planning career break", "value": "Planning career break"}
        ]
    },
    
    # SECTION E: FINANCIAL PROFILE (Q35-Q39)
    35: {
        "section": "financial",
        "field": "annual_income",
        "db_table": "users",
        "text": "🔒 Your annual income:",
        "type": "single_select",
        "options": [
            {"label": "Below ₹5L", "value": "Below ₹5L"},
            {"label": "₹5–10L", "value": "₹5–10L"},
            {"label": "₹10–20L", "value": "₹10–20L"},
            {"label": "₹20–40L", "value": "₹20–40L"},
            {"label": "₹40–75L", "value": "₹40–75L"},
            {"label": "₹75L–1Cr", "value": "₹75L–1Cr"},
            {"label": "₹1–3Cr", "value": "₹1–3Cr"},
            {"label": "₹3Cr+", "value": "₹3Cr+"},
            {"label": "Prefer not to say", "value": None}
        ],
        "columns": 2
    },
    
    36: {
        "section": "financial",
        "field": "income_currency",
        "db_table": "users",
        "text": "🔒 Income currency:",
        "type": "single_select",
        "condition": "residency_type != 'Indian citizen (in India)'",
        "options": [
            {"label": "INR", "value": "INR"},
            {"label": "USD", "value": "USD"},
            {"label": "GBP", "value": "GBP"},
            {"label": "EUR", "value": "EUR"},
            {"label": "AED", "value": "AED"},
            {"label": "SGD", "value": "SGD"},
            {"label": "AUD", "value": "AUD"},
            {"label": "CAD", "value": "CAD"},
            {"label": "Other", "value": "Other"}
        ],
        "columns": 3
    },
    
    37: {
        "section": "financial",
        "field": "net_worth_range",
        "db_table": "users",
        "text": "🔒 Approximate net worth:",
        "type": "single_select",
        "options": [
            {"label": "Below ₹10L", "value": "Below ₹10L"},
            {"label": "₹10–50L", "value": "₹10–50L"},
            {"label": "₹50L–1Cr", "value": "₹50L–1Cr"},
            {"label": "₹1–5Cr", "value": "₹1–5Cr"},
            {"label": "₹5–10Cr", "value": "₹5–10Cr"},
            {"label": "₹10Cr+", "value": "₹10Cr+"},
            {"label": "Prefer not to say", "value": None}
        ],
        "columns": 2
    },
    
    38: {
        "section": "financial",
        "field": "property_ownership",
        "db_table": "users",
        "text": "🔒 Own property?",
        "type": "single_select",
        "options": [
            {"label": "Yes, own house/flat", "value": "Yes, own house/flat"},
            {"label": "Yes, land/plot", "value": "Yes, land/plot"},
            {"label": "Family property (will inherit)", "value": "Family property (will inherit)"},
            {"label": "No", "value": "No"},
            {"label": "Prefer not to say", "value": None}
        ]
    },
    
    39: {
        "section": "financial",
        "field": "financial_dependents",
        "db_table": "users",
        "text": "🔒 Financial dependents?",
        "type": "single_select",
        "options": [
            {"label": "None", "value": "None"},
            {"label": "Parents", "value": "Parents"},
            {"label": "Siblings", "value": "Siblings"},
            {"label": "Extended family", "value": "Extended family"},
            {"label": "Children", "value": "Children"},
            {"label": "Multiple dependents", "value": "Multiple dependents"}
        ]
    },
    
    # SECTION F: FAMILY BACKGROUND (Q40-Q46)
    40: {
        "section": "family",
        "field": "family_type",
        "db_table": "users",
        "text": "Family type:",
        "type": "single_select",
        "options": [
            {"label": "Nuclear", "value": "Nuclear"},
            {"label": "Joint family", "value": "Joint family"},
            {"label": "Extended joint family", "value": "Extended joint family"}
        ]
    },
    
    41: {
        "section": "family",
        "field": "family_financial_status",
        "db_table": "users",
        "text": "Family background:",
        "type": "single_select",
        "options": [
            {"label": "Upper class", "value": "Upper class"},
            {"label": "Upper-middle class", "value": "Upper-middle class"},
            {"label": "Middle class", "value": "Middle class"},
            {"label": "Lower-middle class", "value": "Lower-middle class"},
            {"label": "Prefer not to say", "value": None}
        ]
    },
    
    42: {
        "section": "family",
        "field": "father_occupation",
        "db_table": "users",
        "text": "Father's occupation:",
        "type": "single_select",
        "options": [
            {"label": "Business owner", "value": "Business owner"},
            {"label": "Government / PSU", "value": "Government / PSU"},
            {"label": "Private sector", "value": "Private sector"},
            {"label": "Professional (Doctor/Lawyer/CA)", "value": "Professional (Doctor/Lawyer/CA)"},
            {"label": "Agriculture / Farming", "value": "Agriculture / Farming"},
            {"label": "Retired", "value": "Retired"},
            {"label": "Late", "value": "Late"},
            {"label": "Other", "value": "Other"}
        ]
    },
    
    43: {
        "section": "family",
        "field": "family_values",
        "db_table": "users",
        "text": "Family values:",
        "type": "single_select",
        "options": [
            {"label": "Very traditional / orthodox", "value": "Very traditional / orthodox"},
            {"label": "Moderate — mix of tradition and modern", "value": "Moderate — mix of tradition and modern"},
            {"label": "Liberal / progressive", "value": "Liberal / progressive"},
            {"label": "We're pretty chill", "value": "We're pretty chill"}
        ]
    },
    
    44: {
        "section": "family",
        "field": "living_with_parents_post_marriage",
        "db_table": "users",
        "text": "After marriage, live with parents?",
        "type": "single_select",
        "options": [
            {"label": "Yes, with my parents", "value": "Yes, with my parents"},
            {"label": "Yes, with partner's parents", "value": "Yes, with partner's parents"},
            {"label": "Open to it", "value": "Open to it"},
            {"label": "Prefer independent", "value": "Prefer independent"},
            {"label": "Definitely not", "value": "Definitely not"}
        ]
    },
    
    45: {
        "section": "family",
        "field": "family_involvement_search",
        "db_table": "users",
        "text": "Family involvement in this search:",
        "type": "single_select",
        "options": [
            {"label": "Parents are driving this", "value": "Parents are driving this"},
            {"label": "Family knows and supports", "value": "Family knows and supports"},
            {"label": "Family will be involved later", "value": "Family will be involved later"},
            {"label": "This is my decision alone", "value": "This is my decision alone"}
        ]
    },
    
    46: {
        "section": "family",
        "field": "siblings",
        "db_table": "users",
        "text": "Siblings:",
        "type": "single_select",
        "options": [
            {"label": "Only child", "value": "Only child"},
            {"label": "1 brother", "value": "1 brother"},
            {"label": "1 sister", "value": "1 sister"},
            {"label": "Multiple siblings", "value": "Multiple siblings"},
            {"label": "Prefer not to say", "value": None}
        ]
    },
    
    # SECTION G: LIFESTYLE & HABITS (Q47-Q57)
    47: {
        "section": "lifestyle",
        "field": "diet",
        "db_table": "users",
        "text": "Your diet:",
        "type": "single_select",
        "options": [
            {"label": "Pure vegetarian (no eggs)", "value": "Pure vegetarian (no eggs)"},
            {"label": "Vegetarian (eggs OK)", "value": "Vegetarian (eggs OK)"},
            {"label": "Eggetarian", "value": "Eggetarian"},
            {"label": "Non-vegetarian", "value": "Non-vegetarian"},
            {"label": "Vegan", "value": "Vegan"},
            {"label": "Jain food (no root veg, no onion/garlic)", "value": "Jain food (no root veg, no onion/garlic)"},
            {"label": "Halal only", "value": "Halal only"},
            {"label": "No restrictions", "value": "No restrictions"}
        ],
        "columns": 2
    },
    
    48: {
        "section": "lifestyle",
        "field": "partner_diet_pref",
        "db_table": "preferences",
        "text": "Partner's diet:",
        "type": "single_select",
        "options": [
            {"label": "Must match mine", "value": "Must match mine"},
            {"label": "Prefer similar", "value": "Prefer similar"},
            {"label": "Vegetarian preferred", "value": "Vegetarian preferred"},
            {"label": "Non-veg OK", "value": "Non-veg OK"},
            {"label": "Don't care", "value": "Don't care"}
        ]
    },
    
    49: {
        "section": "lifestyle",
        "field": "smoking",
        "db_table": "users",
        "text": "Smoking:",
        "type": "single_select",
        "options": [
            {"label": "Never", "value": "Never"},
            {"label": "Occasionally / Socially", "value": "Occasionally / Socially"},
            {"label": "Regularly", "value": "Regularly"},
            {"label": "Trying to quit", "value": "Trying to quit"},
            {"label": "Prefer not to say", "value": None}
        ]
    },
    
    50: {
        "section": "lifestyle",
        "field": "smoking_partner_ok",
        "db_table": "preferences",
        "text": "Partner smoking:",
        "type": "single_select",
        "options": [
            {"label": "Dealbreaker", "value": "Dealbreaker"},
            {"label": "Prefer non-smoker", "value": "Prefer non-smoker"},
            {"label": "Don't care", "value": "Don't care"}
        ]
    },
    
    51: {
        "section": "lifestyle",
        "field": "drinking",
        "db_table": "users",
        "text": "Alcohol:",
        "type": "single_select",
        "options": [
            {"label": "Never", "value": "Never"},
            {"label": "Socially / Occasionally", "value": "Socially / Occasionally"},
            {"label": "Regularly", "value": "Regularly"},
            {"label": "Prefer not to say", "value": None}
        ]
    },
    
    52: {
        "section": "lifestyle",
        "field": "drinking_partner_ok",
        "db_table": "preferences",
        "text": "Partner drinking:",
        "type": "single_select",
        "options": [
            {"label": "Dealbreaker", "value": "Dealbreaker"},
            {"label": "Prefer non-drinker", "value": "Prefer non-drinker"},
            {"label": "Don't care", "value": "Don't care"}
        ]
    },
    
    53: {
        "section": "lifestyle",
        "field": "fitness_frequency",
        "db_table": "users",
        "text": "Exercise / fitness:",
        "type": "single_select",
        "options": [
            {"label": "Daily (gym, yoga, sports)", "value": "Daily (gym, yoga, sports)"},
            {"label": "Few times a week", "value": "Few times a week"},
            {"label": "Occasionally", "value": "Occasionally"},
            {"label": "Rarely / Never", "value": "Rarely / Never"}
        ]
    },
    
    54: {
        "section": "lifestyle",
        "field": "social_style",
        "db_table": "users",
        "text": "Social energy:",
        "type": "single_select",
        "options": [
            {"label": "Very outgoing — love big gatherings", "value": "Very outgoing — love big gatherings"},
            {"label": "Social but balanced", "value": "Social but balanced"},
            {"label": "Prefer small groups", "value": "Prefer small groups"},
            {"label": "Homebody — love staying in", "value": "Homebody — love staying in"}
        ]
    },
    
    55: {
        "section": "lifestyle",
        "field": "weekend_style",
        "db_table": "users",
        "text": "Weekends are for:",
        "type": "single_select",
        "options": [
            {"label": "Going out (restaurants, travel, events)", "value": "Going out (restaurants, travel, events)"},
            {"label": "Mix of both", "value": "Mix of both"},
            {"label": "Staying in (family, hobbies, rest)", "value": "Staying in (family, hobbies, rest)"},
            {"label": "Working / side hustle", "value": "Working / side hustle"},
            {"label": "Religious / community activities", "value": "Religious / community activities"}
        ]
    },
    
    56: {
        "section": "lifestyle",
        "field": "pet_ownership",
        "db_table": "users",
        "text": "Pets:",
        "type": "single_select",
        "options": [
            {"label": "Have pets (dogs)", "value": "Have pets (dogs)"},
            {"label": "Have pets (cats)", "value": "Have pets (cats)"},
            {"label": "Have pets (other)", "value": "Have pets (other)"},
            {"label": "No pets, want one", "value": "No pets, want one"},
            {"label": "No pets, don't want one", "value": "No pets, don't want one"},
            {"label": "Allergic", "value": "Allergic"}
        ]
    },
    
    57: {
        "section": "lifestyle",
        "field": "sleep_schedule",
        "db_table": "users",
        "text": "Your schedule:",
        "type": "single_select",
        "options": [
            {"label": "Early bird (up before 6am)", "value": "Early bird (up before 6am)"},
            {"label": "Standard (7-8am)", "value": "Standard (7-8am)"},
            {"label": "Night owl (up past midnight)", "value": "Night owl (up past midnight)"},
            {"label": "Shift worker / irregular", "value": "Shift worker / irregular"}
        ]
    },
    
    # SECTION H: PARTNER PREFERENCES (Q58-Q66)
    58: {
        "section": "partner_prefs",
        "field": "pref_age_range",
        "db_table": "preferences",
        "text": "Partner age range:",
        "type": "single_select",
        "options": [
            {"label": "Same as me (±2yr)", "value": "Same as me (±2yr)"},
            {"label": "Younger (up to 5yr)", "value": "Younger (up to 5yr)"},
            {"label": "Older (up to 5yr)", "value": "Older (up to 5yr)"},
            {"label": "Wide range OK", "value": "Wide range OK"},
            {"label": "No preference", "value": "No preference"}
        ]
    },
    
    59: {
        "section": "partner_prefs",
        "field": "pref_height",
        "db_table": "preferences",
        "text": "Partner height:",
        "type": "single_select",
        "options": [
            {"label": "Shorter than me", "value": "Shorter than me"},
            {"label": "Similar to me (±5cm)", "value": "Similar to me (±5cm)"},
            {"label": "Taller than me", "value": "Taller than me"},
            {"label": "No preference", "value": "No preference"}
        ]
    },
    
    60: {
        "section": "partner_prefs",
        "field": "pref_complexion",
        "db_table": "preferences",
        "text": "Partner complexion:",
        "type": "single_select",
        "options": [
            {"label": "Fair preferred", "value": "Fair preferred"},
            {"label": "No preference", "value": "No preference"},
            {"label": "Prefer not to answer", "value": None}
        ]
    },
    
    61: {
        "section": "partner_prefs",
        "field": "pref_education_min",
        "db_table": "preferences",
        "text": "Partner education (minimum):",
        "type": "single_select",
        "options": [
            {"label": "Any education", "value": "Any education"},
            {"label": "Graduate (Bachelor's)", "value": "Graduate (Bachelor's)"},
            {"label": "Postgraduate (Master's+)", "value": "Postgraduate (Master's+)"},
            {"label": "Professional degree (CA/MBBS/LLB)", "value": "Professional degree (CA/MBBS/LLB)"},
            {"label": "No preference", "value": "No preference"}
        ]
    },
    
    62: {
        "section": "partner_prefs",
        "field": "pref_income_range",
        "db_table": "preferences",
        "text": "Partner income expectation:",
        "type": "single_select",
        "options": [
            {"label": "Below ₹5L", "value": "Below ₹5L"},
            {"label": "₹5–10L", "value": "₹5–10L"},
            {"label": "₹10–20L", "value": "₹10–20L"},
            {"label": "₹20–40L", "value": "₹20–40L"},
            {"label": "₹40L+", "value": "₹40L+"},
            {"label": "₹1Cr+", "value": "₹1Cr+"},
            {"label": "Doesn't matter", "value": "Doesn't matter"}
        ],
        "columns": 2
    },
    
    63: {
        "section": "partner_prefs",
        "field": "pref_marital_status",
        "db_table": "preferences",
        "text": "Partner marital history OK?",
        "type": "single_select",
        "options": [
            {"label": "Never married only", "value": "Never married only"},
            {"label": "Divorced OK", "value": "Divorced OK"},
            {"label": "Widowed OK", "value": "Widowed OK"},
            {"label": "Any", "value": "Any"},
            {"label": "Depends on situation", "value": "Depends on situation"}
        ]
    },
    
    64: {
        "section": "partner_prefs",
        "field": "pref_children_ok",
        "db_table": "preferences",
        "text": "Partner having existing children?",
        "type": "single_select",
        "options": [
            {"label": "OK", "value": "OK"},
            {"label": "Depends", "value": "Depends"},
            {"label": "Prefer not", "value": "Prefer not"},
            {"label": "Dealbreaker", "value": "Dealbreaker"}
        ]
    },
    
    65: {
        "section": "partner_prefs",
        "field": "pref_disability_ok",
        "db_table": "preferences",
        "text": "Partner with disability?",
        "type": "single_select",
        "options": [
            {"label": "Yes, open to it", "value": "Yes, open to it"},
            {"label": "Depends on type", "value": "Depends on type"},
            {"label": "Prefer not", "value": "Prefer not"},
            {"label": "No", "value": "No"}
        ]
    },
    
    66: {
        "section": "partner_prefs",
        "field": "pref_working_spouse",
        "db_table": "preferences",
        "text": "Want a working partner?",
        "type": "single_select",
        "options": [
            {"label": "Yes, must work", "value": "Yes, must work"},
            {"label": "Prefer working", "value": "Prefer working"},
            {"label": "Open to either", "value": "Open to either"},
            {"label": "Prefer homemaker", "value": "Prefer homemaker"},
            {"label": "No preference", "value": "No preference"}
        ]
    },
    
    # SECTION I: VALUES & RELATIONSHIP STYLE (Q67-Q74)
    67: {
        "section": "values",
        "field": "relationship_intent",
        "db_table": "users",
        "text": "What are you looking for?",
        "type": "single_select",
        "options": [
            {"label": "Marriage — ready now", "value": "Marriage — ready now"},
            {"label": "Marriage — in 6-12 months", "value": "Marriage — in 6-12 months"},
            {"label": "Marriage — in 1-2 years", "value": "Marriage — in 1-2 years"},
            {"label": "Long-term committed relationship", "value": "Long-term committed relationship"},
            {"label": "Open to see where it goes", "value": "Open to see where it goes"}
        ]
    },
    
    68: {
        "section": "values",
        "field": "children_intent",
        "db_table": "users",
        "text": "Want children?",
        "type": "single_select",
        "options": [
            {"label": "Yes, definitely", "value": "Yes, definitely"},
            {"label": "Probably yes", "value": "Probably yes"},
            {"label": "Open to it", "value": "Open to it"},
            {"label": "Probably not", "value": "Probably not"},
            {"label": "Definitely not", "value": "Definitely not"}
        ]
    },
    
    69: {
        "section": "values",
        "field": "children_timeline",
        "db_table": "users",
        "text": "Children timeline:",
        "type": "single_select",
        "condition": "children_intent != 'Definitely not'",
        "options": [
            {"label": "Soon after marriage", "value": "Soon after marriage"},
            {"label": "1–2 years", "value": "1–2 years"},
            {"label": "3–5 years", "value": "3–5 years"},
            {"label": "No rush", "value": "No rush"},
            {"label": "Not applicable", "value": "Not applicable"}
        ]
    },
    
    70: {
        "section": "values",
        "field": "gender_roles_household",
        "db_table": "users",
        "text": "Household responsibilities:",
        "type": "single_select",
        "options": [
            {"label": "Should be shared equally", "value": "Should be shared equally"},
            {"label": "Mostly wife's domain", "value": "Mostly wife's domain"},
            {"label": "Mostly husband's domain", "value": "Mostly husband's domain"},
            {"label": "Hire help, don't stress", "value": "Hire help, don't stress"},
            {"label": "Flexible — figure it out together", "value": "Flexible — figure it out together"}
        ]
    },
    
    71: {
        "section": "values",
        "field": "financial_management",
        "db_table": "users",
        "text": "Money in marriage:",
        "type": "single_select",
        "options": [
            {"label": "Joint accounts, full transparency", "value": "Joint accounts, full transparency"},
            {"label": "Partially joint, some independence", "value": "Partially joint, some independence"},
            {"label": "Completely separate finances", "value": "Completely separate finances"},
            {"label": "Haven't thought about it", "value": "Haven't thought about it"}
        ]
    },
    
    72: {
        "section": "values",
        "field": "political_leaning",
        "db_table": "users",
        "text": "Political leaning:",
        "type": "single_select",
        "options": [
            {"label": "Very conservative", "value": "Very conservative"},
            {"label": "Center-right", "value": "Center-right"},
            {"label": "Centrist / moderate", "value": "Centrist / moderate"},
            {"label": "Center-left", "value": "Center-left"},
            {"label": "Very liberal / progressive", "value": "Very liberal / progressive"},
            {"label": "Apolitical", "value": "Apolitical"}
        ],
        "columns": 2
    },
    
    73: {
        "section": "values",
        "field": "astrology_belief",
        "db_table": "users",
        "text": "Importance of kundli / astrology:",
        "type": "single_select",
        "options": [
            {"label": "Very important — must match", "value": "Very important — must match"},
            {"label": "Somewhat important", "value": "Somewhat important"},
            {"label": "Don't believe but family does", "value": "Don't believe but family does"},
            {"label": "Not important at all", "value": "Not important at all"}
        ]
    },
    
    74: {
        "section": "values",
        "field": "interfaith_intercaste_openness",
        "db_table": "users",
        "text": "Open to inter-faith or inter-caste marriage?",
        "type": "single_select",
        "options": [
            {"label": "Yes, fully open", "value": "Yes, fully open"},
            {"label": "Open but family may resist", "value": "Open but family may resist"},
            {"label": "Prefer within community", "value": "Prefer within community"},
            {"label": "Not open", "value": "Not open"}
        ]
    },
    
    # SECTION J: HARD DEALBREAKER CHECKBOXES (Q75-Q79)
    75: {
        "section": "dealbreakers",
        "field": "db_divorced_ok",
        "db_table": "preferences",
        "text": "OK with divorced partner?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "No", "value": "No"}
        ]
    },
    
    76: {
        "section": "dealbreakers",
        "field": "db_widowed_ok",
        "db_table": "preferences",
        "text": "OK with widowed partner?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "No", "value": "No"}
        ]
    },
    
    77: {
        "section": "dealbreakers",
        "field": "db_children_ok",
        "db_table": "preferences",
        "text": "OK with partner who has children?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "No", "value": "No"}
        ]
    },
    
    78: {
        "section": "dealbreakers",
        "field": "db_nri_ok",
        "db_table": "preferences",
        "text": "OK with NRI partner?",
        "type": "single_select",
        "options": [
            {"label": "Yes", "value": "Yes"},
            {"label": "No", "value": "No"},
            {"label": "Prefer NRI", "value": "Prefer NRI"}
        ]
    },
    
    79: {
        "section": "dealbreakers",
        "field": "db_age_gap_max",
        "db_table": "preferences",
        "text": "Maximum age gap acceptable:",
        "type": "single_select",
        "options": [
            {"label": "±2 years", "value": "±2 years"},
            {"label": "±5 years", "value": "±5 years"},
            {"label": "±8 years", "value": "±8 years"},
            {"label": "±10+ years", "value": "±10+ years"},
            {"label": "No limit", "value": "No limit"}
        ]
    }
}

# Dynamic option generators
def get_birth_years():
    """Birth years from 1980 to 2006 (ages 18-44)"""
    return [
        {"label": str(year), "value": str(year)}
        for year in range(2006, 1979, -1)
    ]

def get_countries_by_region(region: str):
    """Countries organized by region for hierarchical selection"""
    regions = {
        "USA": [
            {"label": "United States", "value": "United States"}
        ],
        "UK": [
            {"label": "United Kingdom", "value": "United Kingdom"}
        ],
        "Europe": [
            {"label": "🇩🇪 Germany", "value": "Germany"},
            {"label": "🇫🇷 France", "value": "France"},
            {"label": "🇮🇹 Italy", "value": "Italy"},
            {"label": "🇪🇸 Spain", "value": "Spain"},
            {"label": "🇳🇱 Netherlands", "value": "Netherlands"},
            {"label": "🇨🇭 Switzerland", "value": "Switzerland"},
            {"label": "🇸🇪 Sweden", "value": "Sweden"},
            {"label": "🇳🇴 Norway", "value": "Norway"},
            {"label": "Other →", "value": "Other", "requires_text": True}
        ],
        "Middle East": [
            {"label": "🇦🇪 UAE", "value": "UAE"},
            {"label": "🇸🇦 Saudi Arabia", "value": "Saudi Arabia"},
            {"label": "🇶🇦 Qatar", "value": "Qatar"},
            {"label": "🇧🇭 Bahrain", "value": "Bahrain"},
            {"label": "🇰🇼 Kuwait", "value": "Kuwait"},
            {"label": "🇴🇲 Oman", "value": "Oman"},
            {"label": "Other →", "value": "Other", "requires_text": True}
        ],
        "Asia-Pacific": [
            {"label": "🇸🇬 Singapore", "value": "Singapore"},
            {"label": "🇦🇺 Australia", "value": "Australia"},
            {"label": "🇳🇿 New Zealand", "value": "New Zealand"},
            {"label": "🇨🇦 Canada", "value": "Canada"},
            {"label": "🇲🇾 Malaysia", "value": "Malaysia"},
            {"label": "🇭🇰 Hong Kong", "value": "Hong Kong"},
            {"label": "🇯🇵 Japan", "value": "Japan"},
            {"label": "Other →", "value": "Other", "requires_text": True}
        ],
        "Other": [
            {"label": "🇿🇦 South Africa", "value": "South Africa"},
            {"label": "🇧🇷 Brazil", "value": "Brazil"},
            {"label": "🇲🇽 Mexico", "value": "Mexico"},
            {"label": "Other →", "value": "Other", "requires_text": True}
        ]
    }
    return regions.get(region, [])

def get_countries():
    """Top countries for NRI population"""
    return [
        {"label": "🇮🇳 India", "value": "India"},
        {"label": "🇦🇪 UAE", "value": "UAE"},
        {"label": "🇺🇸 USA", "value": "USA"},
        {"label": "🇬🇧 UK", "value": "UK"},
        {"label": "🇸🇬 Singapore", "value": "Singapore"},
        {"label": "🇸🇦 Saudi Arabia", "value": "Saudi Arabia"},
        {"label": "🇶🇦 Qatar", "value": "Qatar"},
        {"label": "🇧🇭 Bahrain", "value": "Bahrain"},
        {"label": "🇰🇼 Kuwait", "value": "Kuwait"},
        {"label": "🇵🇰 Pakistan", "value": "Pakistan"},
        {"label": "Other →", "value": "Other", "requires_text": True}
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
        {"label": "Punjab", "value": "Punjab"},
        {"label": "Telangana", "value": "Telangana"},
        {"label": "Haryana", "value": "Haryana"},
        {"label": "Other →", "value": "Other", "requires_text": True}
    ]

def get_sects_by_religion(religion):
    """Religious sects/denominations based on selected religion"""
    sects = {
        "Hindu": [
            {"label": "Shaivite", "value": "Shaivite"},
            {"label": "Vaishnavite", "value": "Vaishnavite"},
            {"label": "Arya Samaj", "value": "Arya Samaj"},
            {"label": "Smartha", "value": "Smartha"},
            {"label": "None / Prefer not to say", "value": None}
        ],
        "Muslim": [
            {"label": "Sunni", "value": "Sunni"},
            {"label": "Shia", "value": "Shia"},
            {"label": "Sufi", "value": "Sufi"},
            {"label": "Ahmadiyya", "value": "Ahmadiyya"},
            {"label": "None / Prefer not to say", "value": None}
        ],
        "Christian": [
            {"label": "Catholic", "value": "Catholic"},
            {"label": "Protestant", "value": "Protestant"},
            {"label": "Orthodox", "value": "Orthodox"},
            {"label": "Evangelical", "value": "Evangelical"},
            {"label": "None / Prefer not to say", "value": None}
        ],
        "Sikh": [
            {"label": "Amritdhari", "value": "Amritdhari"},
            {"label": "Keshdhari", "value": "Keshdhari"},
            {"label": "Sehajdhari", "value": "Sehajdhari"},
            {"label": "None / Prefer not to say", "value": None}
        ]
    }
    return sects.get(religion, [{"label": "None / Prefer not to say", "value": None}])

def get_castes_by_religion(religion):
    """Caste/community options based on selected religion"""
    castes = {
        "Hindu": [
            {"label": "Brahmin", "value": "Brahmin"},
            {"label": "Kshatriya", "value": "Kshatriya"},
            {"label": "Vaishya", "value": "Vaishya"},
            {"label": "SC", "value": "SC"},
            {"label": "ST", "value": "ST"},
            {"label": "OBC", "value": "OBC"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": None}
        ],
        "Jain": [
            {"label": "Digambar", "value": "Digambar"},
            {"label": "Shwetambar", "value": "Shwetambar"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": None}
        ],
        "Sikh": [
            {"label": "Jat", "value": "Jat"},
            {"label": "Khatri", "value": "Khatri"},
            {"label": "Ramgarhia", "value": "Ramgarhia"},
            {"label": "Arora", "value": "Arora"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": None}
        ],
        "Buddhist": [
            {"label": "General", "value": "General"},
            {"label": "Neo-Buddhist", "value": "Neo-Buddhist"},
            {"label": "Other", "value": "Other"},
            {"label": "Prefer not to say", "value": None}
        ]
    }
    return castes.get(religion, [{"label": "Prefer not to say", "value": None}])


# ============== VALIDATION RULES ==============

VALIDATION_RULES = {
    "date_of_birth": {
        "format": "DD/MM/YYYY",
        "min_age": 18,
        "max_age": 80,
        "error_format": "Invalid format. Please use DD/MM/YYYY (e.g., 15/03/1995)",
        "error_range": "Age must be between 18 and 80."
    },
    "height_cm": {
        "min": 140,
        "max": 220,
        "error": "Height must be between 140cm and 220cm."
    }
}


# ============== TRANSITION MESSAGES ==============

SECTION_TRANSITIONS = {
    "after_intro": """Those are the big ones ✓

Now a few quick ones about you.""",
    
    "after_identity": """Almost there, {name} — you're flying through this ✓

A few more about your lifestyle and preferences, then we switch to the good stuff.""",
    
    "after_location": """Great ✓

Now about your faith and culture.""",
    
    "after_religion": """Nicely done ✓

Now a bit about your education and career.""",
    
    "after_education": """Looking good ✓

Next — some private financial questions. 🔒 These stay private, just help with matching.""",
    
    "after_financial": """Perfect ✓

Now about your family background.""",
    
    "after_family": """Almost halfway ✓

A few questions about your day-to-day lifestyle.""",
    
    "after_lifestyle": """You're on a roll ✓

Now — what are you looking for in a partner?""",
    
    "after_partner_prefs": """Nearly there ✓

Last section — values and relationship style.""",
    
    "after_values": """Final stretch ✓

Just a few quick dealbreakers, then we're done with the tap-tap questions."""
}

FINAL_TRANSITION = """You're in, {name} ✓

I now know your basics and your filters. That's about 25% of what I need to find you someone great.

Here's what happens next:

The quick-tap stuff tells me who to filter OUT.
The conversation tells me who to filter IN.

Starting now, I'll ask you real questions — the kind a good friend would ask if they were setting you up. Answer in your own words, whenever you feel like it.

There's no rush. The more I understand you, the better your first introduction will be.

Ready for the first one?"""


# ============== ERROR MESSAGES ==============

ERROR_MESSAGES = {
    "button_expected": "Just tap one of the options above 👆",
    "sticker_during_buttons": "😄 Save that energy — just tap a button for now, we'll chat properly soon.",
    "photo_expected": "Please send a photo (JPG or PNG format, max 10MB)",
    "photo_size": "Image too large. Max 10MB.",
    "photo_format": "Please send a valid image (JPG or PNG).",
    "invalid_input": "That doesn't look right. Please try again:",
    "network_error": "Oops, something went wrong. Let me try that again..."
}


# ============== RESUME MESSAGES ==============

RESUME_PROMPT = """Hey {name}, we were getting through the quick questions — want to pick up where we left off?

Progress: {current}/{total}"""

RESUME_BUTTONS = ["✓ Resume", "⟲ Start over"]
