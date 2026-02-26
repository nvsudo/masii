#!/usr/bin/env python3
"""
Add MVP Questions tab to Jodi Schema Google Sheet
India-specific, 36 button-tap questions
"""

import sys
sys.path.insert(0, '/Users/nikunjvora/clawd')

from google_api import update_sheet, add_sheet_tab

SHEET_ID = "18iDif3BzPxlQ-i5ZiJO8eEjvnsqsm-dlu-9g2jakaPE"
TAB_NAME = "MVP Questions India"

# MVP Questions for India-specific matching
headers = [
    "Q#", "Category", "Field Name", "Question Text", "Button Options", "Notes"
]

data = [
    headers,
    # IDENTITY & TARGETING (9Q)
    ["1", "Identity", "gender_identity", "I am a:", "Male | Female | Prefer to self-describe", ""],
    ["2", "Identity", "looking_for_gender", "Looking for:", "Men | Women | Either", ""],
    ["3", "Identity", "age", "Your age:", "18-22 | 23-25 | 26-28 | 29-31 | 32-35 | 36-40 | 41-45 | 46-50 | 50+", "Exact age or bracket"],
    ["4", "Identity", "residency_status", "Your residency status:", "Indian citizen (in India) | NRI (Non-Resident Indian) | OCI (Overseas Citizen) | PIO (Person of Indian Origin)", "India-specific targeting"],
    ["5", "Identity", "current_city", "Current city:", "[City dropdown or text input with autocomplete]", "Major Indian cities + international for NRI"],
    ["6", "Identity", "current_state", "Current state/country:", "[State/Country dropdown]", "Indian states + countries for NRI"],
    ["7", "Identity", "willing_to_relocate", "Willing to relocate?", "Yes, anywhere | Yes, within India | Yes, within my state | Maybe | No, staying put", ""],
    ["8", "Identity", "distance_preference", "Distance matters?", "Same city only | Same state/region | Anywhere in India | International OK (NRI)", ""],
    ["9", "Identity", "height_cm", "Your height:", "Below 150cm | 150-155 | 156-160 | 161-165 | 166-170 | 171-175 | 176-180 | 181-185 | 186-190 | 190+", "Metric for India"],
    
    # DEALBREAKERS (18Q)
    ["10", "Dealbreaker", "religion", "Your religion:", "Hindu | Muslim | Christian | Sikh | Jain | Buddhist | Parsi | Jewish | No religion | Other", ""],
    ["11", "Dealbreaker", "religious_practice_level", "How religious are you?", "Very devout (daily practice) | Moderately religious (festivals, rituals) | Culturally religious (identity, not practice) | Spiritual but not religious | Not religious at all", ""],
    ["12", "Dealbreaker", "partner_religion_requirement", "Partner's religion:", "Must be same religion | Prefer same, open to others | Doesn't matter at all", ""],
    ["13", "Dealbreaker", "caste_community", "Your caste/community:", "[Dropdown: General | SC | ST | OBC | EBC | Brahmin | Kshatriya | Vaishya | Shudra | Other] OR [Text input for specific community]", "Sensitive but common filter in Indian matchmaking"],
    ["14", "Dealbreaker", "permitted_castes", "Acceptable castes/communities for partner:", "[Multi-select or checkboxes] | All castes OK | Prefer not to answer", "Positive filter list"],
    ["15", "Dealbreaker", "excluded_castes", "Castes/communities to exclude:", "[Multi-select or checkboxes] | No exclusions | Prefer not to answer", "Negative filter list"],
    ["16", "Dealbreaker", "caste_importance", "How important is caste to you?", "Very important (dealbreaker) | Somewhat important (strong preference) | Slightly matters | Doesn't matter at all", "Weight for matching algo"],
    ["17", "Dealbreaker", "children_intent", "Do you want children?", "Yes, definitely | Open to it | Don't want kids | Already have kids", ""],
    ["18", "Dealbreaker", "partner_existing_children_ok", "OK with partner having kids?", "Yes, no issue | Depends on situation | Prefer not | No, dealbreaker", ""],
    ["19", "Dealbreaker", "marital_history", "Marital status:", "Never married | Divorced | Widowed | Separated | Annulled", ""],
    ["20", "Dealbreaker", "smoking", "Do you smoke?", "Never | Socially/Occasionally | Regularly | Prefer not to say", ""],
    ["21", "Dealbreaker", "smoking_tolerance", "Smoking in partner?", "Dealbreaker | Prefer non-smoker | Don't care", ""],
    ["22", "Dealbreaker", "drinking", "Do you drink alcohol?", "Never | Socially/Occasionally | Regularly | Prefer not to say", ""],
    ["23", "Dealbreaker", "drinking_tolerance", "Drinking in partner?", "Dealbreaker | Prefer non-drinker | Don't care", ""],
    ["24", "Dealbreaker", "dietary_restriction", "Your diet:", "Vegetarian (no meat/fish/eggs) | Vegetarian (eggs OK) | Non-vegetarian | Vegan | Jain (no root veg) | Halal only | No restrictions", "India-specific options"],
    ["25", "Dealbreaker", "partner_diet_requirement", "Partner's diet:", "Must match mine | Prefer similar | Doesn't matter", ""],
    ["26", "Dealbreaker", "relationship_timeline", "When are you looking to settle down?", "Ready to marry within 6 months | 6-12 months | 1-2 years | Just exploring, no rush", ""],
    ["27", "Dealbreaker", "relationship_intent", "What are you looking for?", "Marriage | Long-term relationship leading to marriage | Committed relationship | Open to see where it goes", ""],
    
    # PREFERENCES (5Q)
    ["28", "Preference", "age_range_preference", "Partner's age range:", "Same as mine (±2 years) | 18-25 | 26-30 | 31-35 | 36-40 | 41-45 | 46-50 | 50+ | Age doesn't matter", "Min-max sliders in UI"],
    ["29", "Preference", "education_minimum", "Partner's education:", "High school | Bachelor's degree | Master's/professional degree | PhD/Doctorate | Doesn't matter", ""],
    ["30", "Preference", "partner_income_expectation", "Partner's income (annual):", "Below ₹5L | ₹5-10L | ₹10-20L | ₹20-40L | ₹40L-1Cr | 1Cr+ | Doesn't matter", "India-specific (INR lakhs/crores)"],
    ["31", "Preference", "partner_networth_expectation", "Partner's net worth:", "Below ₹10L | ₹10-50L | ₹50L-1Cr | 1-5Cr | 5Cr+ | Doesn't matter", ""],
    ["32", "Preference", "height_preference", "Partner's height:", "Shorter than me | Same as me (±5cm) | Taller than me | Doesn't matter", "Relative preference"],
    
    # YOUR FINANCIALS (2Q - Private)
    ["33", "Financial (Private)", "user_income_annual", "🔒 Your annual income:", "Below ₹5L | ₹5-10L | ₹10-20L | ₹20-40L | ₹40L-1Cr | 1Cr+ | Prefer not to say", "🔒 Won't be shown to matches. For quality matching only."],
    ["34", "Financial (Private)", "user_networth", "🔒 Your net worth:", "Below ₹10L | ₹10-50L | ₹50L-1Cr | 1-5Cr | 5Cr+ | Prefer not to say", "🔒 Won't be shown to matches. For quality matching only."],
    
    # LIFESTYLE (5Q)
    ["35", "Lifestyle", "living_situation", "Living arrangement:", "Alone | With roommates | With parents/family | Own house/apartment | Other", ""],
    ["36", "Lifestyle", "work_industry", "Work/study:", "Tech/IT | Finance/Banking | Healthcare | Education | Government | Business/Entrepreneur | Student | Homemaker | Other", "Industry categories for India"],
    ["37", "Lifestyle", "fitness_frequency", "Exercise/fitness:", "Daily (gym/yoga/sports) | Few times a week | Occasionally | Rarely/Never", ""],
    ["38", "Lifestyle", "social_energy", "Your vibe:", "Very outgoing (love socializing) | Moderately social (balanced) | Quiet/introverted (prefer small groups) | Homebody (mostly stay in)", ""],
    ["39", "Lifestyle", "weekend_style", "Weekends are for:", "Going out (restaurants, events, travel) | Mix of both (some out, some in) | Staying in (family, hobbies, rest) | Working (career-focused)", ""],
    ["40", "Lifestyle", "family_involvement", "Family involvement in search:", "Parents/family are actively involved | Family knows and supports | Family will be involved later | This is my decision alone", "Cultural context for India"],
]

def main():
    print("Adding MVP Questions tab to Google Sheet...")
    
    # Step 1: Create new tab
    sheet_id = add_sheet_tab(SHEET_ID, TAB_NAME)
    
    if not sheet_id:
        print("❌ Error creating tab (might already exist)")
        # Try to update anyway in case it exists
    else:
        print(f"✅ Created tab '{TAB_NAME}' (ID: {sheet_id})")
    
    # Step 2: Populate with data
    result = update_sheet(SHEET_ID, f"'{TAB_NAME}'!A1", data)
    
    if result:
        print(f"✅ Populated with {len(data)} rows")
        print(f"\n📊 Google Sheet URL:")
        print(f"https://docs.google.com/spreadsheets/d/18iDif3BzPxlQ-i5ZiJO8eEjvnsqsm-dlu-9g2jakaPE/edit")
        print(f"\n40 questions total (including 4 caste-specific for Indians)")
        print(f"Matching threshold: 32/36 = 89% alignment")
    else:
        print("❌ Error populating sheet")
    
    return result

if __name__ == "__main__":
    main()
