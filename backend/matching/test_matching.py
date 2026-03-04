"""
Tests for Masii Matching Engine (v2)

Tests hard filters, per-question scoring, and end-to-end matching with synthetic profiles.
Run with: python -m pytest backend/matching/test_matching.py -v
Or:       cd backend/matching && python test_matching.py
"""

from datetime import date
from filters import (
    check_gender,
    check_age,
    check_religion_full,
    check_caste,
    check_marital_status,
    check_children_existing,
    check_children_intent,
    check_diet,
    check_smoking,
    check_drinking,
    check_conditions,
    check_marriage_timeline,
    check_manglik,
    check_current_location,
    check_raised_in,
    check_mother_tongue,
    check_height,
    check_disability,
    pass_hard_filters_bidirectional,
    DIET_STRICT,
)
from scoring import (
    calculate_match_score,
    calculate_bidirectional_score,
    calculate_confidence,
    generate_explanation,
)
from matcher import match_two_profiles


# ============== SYNTHETIC PROFILES (v2) ==============

# Profile 1: Arun — 29M, Hindu Gujarati, Mumbai, veg, engineer
ARUN_USER = {
    "id": 1,
    "full_name": "Arun Patel",
    "gender": "Male",
    "date_of_birth": date(1996, 5, 15),  # age ~29
    "city_current": "Mumbai",
    "country_current": "India",
    "state_india": "Maharashtra",
    "raised_in_state": "Gujarat",
    "raised_in_city": "Ahmedabad",
    "raised_in_country": "India",
    "mother_tongue": "Gujarati",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 175,
    "weight_kg": 72,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Engineering/IT",
    "occupation_sector": "Private",
    "annual_income": "₹20-35 lakh",
    "family_type": "Nuclear",
    "family_status": "Upper middle class",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Homemaker",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543210",
}

ARUN_PREFS = {
    "pref_age_min": 24,
    "pref_age_max": 30,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Prefer same, open to others",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same or Hindi",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Veg",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 155,
    "pref_height_max": 170,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "Near parents but separate",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Near parents but separate",
    "relocation_willingness": "Yes, within India",
    "religious_practice": "Moderate",
    "sect_denomination": None,
    "caste_community": "Patel",
    "caste_importance": "Prefer same, open to others",
    "partner_working": "Her choice",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

ARUN_SIGNALS = {
    "diet": "Veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Take some time, then discuss",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "cooking_contribution": "4-7",
    "household_contribution": "Shared equally",
}


# Profile 2: Priya — 27F, Hindu Gujarati, Delhi, veg, doctor
PRIYA_USER = {
    "id": 2,
    "full_name": "Priya Shah",
    "gender": "Female",
    "date_of_birth": date(1998, 8, 20),  # age ~27
    "city_current": "Delhi",
    "country_current": "India",
    "state_india": "Delhi",
    "raised_in_state": "Gujarat",
    "raised_in_city": "Surat",
    "raised_in_country": "India",
    "mother_tongue": "Gujarati",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 162,
    "weight_kg": 55,
    "religion": "Hindu",
    "education_level": "Professional (CA/CS/MBBS/LLB)",
    "education_field": "Medicine/Healthcare",
    "occupation_sector": "Professional (Doctor, Lawyer, CA)",
    "annual_income": "₹10-20 lakh",
    "family_type": "Joint",
    "family_status": "Upper middle class",
    "father_occupation": "Professional",
    "mother_occupation": "Working professional",
    "siblings": "2 siblings",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543211",
}

PRIYA_PREFS = {
    "pref_age_min": 27,
    "pref_age_max": 34,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same language only",
    "pref_education_min": "At least Master's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "₹10-20 lakh",
    "pref_diet": "Same as mine",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 170,
    "pref_height_max": 185,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "After 2-3 years",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Near parents but separate",
    "relocation_willingness": "Yes, anywhere",
    "religious_practice": "Moderate",
    "sect_denomination": None,
    "caste_community": "Shah",
    "caste_importance": "Doesn't matter",
    "pref_partner_cooking": "Sometimes (3-6)",
    "pref_partner_household": "Equal share",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

PRIYA_SIGNALS = {
    "diet": "Veg",
    "drinking": "Never",
    "smoking": "Never",
    "fitness_frequency": "Daily",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Talk it out immediately",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Yes, but open to break for kids",
    "live_with_inlaws": "For some time, not permanently",
}


# Profile 3: Fatima — 25F, Muslim, Mumbai, non-veg
FATIMA_USER = {
    "id": 3,
    "full_name": "Fatima Khan",
    "gender": "Female",
    "date_of_birth": date(2000, 3, 10),  # age ~25
    "city_current": "Mumbai",
    "country_current": "India",
    "state_india": "Maharashtra",
    "raised_in_state": "Maharashtra",
    "raised_in_city": "Mumbai",
    "raised_in_country": "India",
    "mother_tongue": "Urdu",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 160,
    "weight_kg": 55,
    "religion": "Muslim",
    "education_level": "Bachelor's",
    "education_field": "Business/MBA",
    "occupation_sector": "Private",
    "annual_income": "₹5-10 lakh",
    "family_type": "Joint",
    "family_status": "Middle class",
    "father_occupation": "Service/Salaried",
    "mother_occupation": "Homemaker",
    "siblings": "3+ siblings",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543212",
}

FATIMA_PREFS = {
    "pref_age_min": 25,
    "pref_age_max": 32,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "₹5-10 lakh",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Must not drink",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 168,
    "pref_height_max": 185,
    "pref_marital_status": "Any",
    "pref_children_existing": "Yes",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "With parents (joint)",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "Depends",
    "marriage_timeline": "2-3 years",
    "children_intent": "Yes",
    "children_timeline": "Soon after marriage",
    "living_arrangement": "With parents (joint)",
    "relocation_willingness": "Yes, within India",
    "religious_practice": "Religious",
    "sect_denomination": "Sunni",
    "caste_community": None,
    "caste_importance": None,
    "pref_partner_cooking": "Rarely (1-2)",
    "pref_partner_household": "Some help",
    "pref_manglik": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "No",
}

FATIMA_SIGNALS = {
    "diet": "Non-veg",
    "drinking": "Never",
    "smoking": "Never",
    "fitness_frequency": "Rarely",
    "social_style": "Introverted — prefer small groups",
    "conflict_style": "Avoid conflict",
    "financial_planning": "Fully joint",
    "manglik_status": None,
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Undecided",
    "live_with_inlaws": "Yes, happy to",
}


# Profile 4: Raj — 30M, Hindu, Delhi, non-veg, divorced
RAJ_USER = {
    "id": 4,
    "full_name": "Raj Malhotra",
    "gender": "Male",
    "date_of_birth": date(1995, 11, 3),  # age ~30
    "city_current": "Delhi",
    "country_current": "India",
    "state_india": "Delhi",
    "raised_in_state": "Punjab",
    "raised_in_city": "Amritsar",
    "raised_in_country": "India",
    "mother_tongue": "Punjabi",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Divorced",
    "children_existing": "No",
    "height_cm": 180,
    "weight_kg": 82,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Business/MBA",
    "occupation_sector": "Business/Self-employed",
    "annual_income": "₹35-50 lakh",
    "family_type": "Nuclear",
    "family_status": "Affluent",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Retired",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543213",
}

RAJ_PREFS = {
    "pref_age_min": 24,
    "pref_age_max": 32,
    "pref_religion": "Open to all",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Doesn't matter",
    "pref_height_min": 155,
    "pref_height_max": 175,
    "pref_marital_status": "Any",
    "pref_children_existing": "Yes",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "Yes",
    "marriage_timeline": "2-3 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, anywhere",
    "religious_practice": "Not very religious",
    "sect_denomination": None,
    "caste_community": "Khatri",
    "caste_importance": "Doesn't matter",
    "partner_working": "Yes, she should have a career",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Yes",
}

RAJ_SIGNALS = {
    "diet": "Non-veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Socially / Occasionally",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Very social — love big gatherings",
    "conflict_style": "Talk it out immediately",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "cooking_contribution": "1-3",
    "household_contribution": "Mostly outsourced (cook/maid)",
}


# ============== NRI / DIASPORA PROFILES ==============

# Profile 5: Vikram — 31M, Hindu Tamil, NRI in San Francisco, tech, raised in Chennai
VIKRAM_USER = {
    "id": 5,
    "full_name": "Vikram Sundaram",
    "gender": "Male",
    "date_of_birth": date(1994, 7, 22),  # age ~31
    "city_current": "San Francisco",
    "country_current": "USA",
    "state_india": None,
    "raised_in_state": "Tamil Nadu",
    "raised_in_city": "Chennai",
    "raised_in_country": "India",
    "mother_tongue": "Tamil",
    "languages_spoken": ["English", "Hindi"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 178,
    "weight_kg": 75,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Engineering/IT",
    "occupation_sector": "Private",
    "annual_income": "$100,000-150,000",
    "family_type": "Nuclear",
    "family_status": "Upper middle class",
    "father_occupation": "Professional",
    "mother_occupation": "Working professional",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+14155551234",
}

VIKRAM_PREFS = {
    "pref_age_min": 25,
    "pref_age_max": 31,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 155,
    "pref_height_max": 172,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, anywhere",
    "religious_practice": "Moderate",
    "sect_denomination": None,
    "caste_community": "Iyer",
    "caste_importance": "Doesn't matter",
    "partner_working": "Yes, she should have a career",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

VIKRAM_SIGNALS = {
    "diet": "Occasionally non-veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Talk it out immediately",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "cooking_contribution": "4-7",
    "household_contribution": "Shared equally",
}


# Profile 6: Meera — 28F, Hindu Tamil, NRI in Sydney, doctor, raised in Bangalore
MEERA_USER = {
    "id": 6,
    "full_name": "Meera Krishnan",
    "gender": "Female",
    "date_of_birth": date(1997, 11, 5),  # age ~28
    "city_current": "Sydney",
    "country_current": "Australia",
    "state_india": None,
    "raised_in_state": "Karnataka",
    "raised_in_city": "Bangalore",
    "raised_in_country": "India",
    "mother_tongue": "Tamil",
    "languages_spoken": ["English", "Hindi", "Kannada"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 163,
    "weight_kg": 56,
    "religion": "Hindu",
    "education_level": "Professional (CA/CS/MBBS/LLB)",
    "education_field": "Medicine/Healthcare",
    "occupation_sector": "Professional (Doctor, Lawyer, CA)",
    "annual_income": "$100,000-150,000",
    "family_type": "Nuclear",
    "family_status": "Upper middle class",
    "father_occupation": "Professional",
    "mother_occupation": "Working professional",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+61412345678",
}

MEERA_PREFS = {
    "pref_age_min": 28,
    "pref_age_max": 35,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same or Hindi",
    "pref_education_min": "At least Master's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 172,
    "pref_height_max": 188,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "After 2-3 years",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, anywhere",
    "religious_practice": "Moderate",
    "sect_denomination": None,
    "caste_community": "Iyengar",
    "caste_importance": "Doesn't matter",
    "pref_partner_cooking": "Sometimes (3-6)",
    "pref_partner_household": "Equal share",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

MEERA_SIGNALS = {
    "diet": "Veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "Daily",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Take some time, then discuss",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": "No",
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Yes, definitely",
    "live_with_inlaws": "Prefer not to",
}


# Profile 7: Arjun — 29M, Hindu Gujarati, 2nd gen in San Francisco, raised in USA
ARJUN_USER = {
    "id": 7,
    "full_name": "Arjun Desai",
    "gender": "Male",
    "date_of_birth": date(1996, 3, 12),  # age ~29
    "city_current": "San Francisco",
    "country_current": "USA",
    "state_india": None,
    "raised_in_state": None,
    "raised_in_city": "San Jose",
    "raised_in_country": "USA",
    "mother_tongue": "Gujarati",
    "languages_spoken": ["English", "Hindi"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 177,
    "weight_kg": 76,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Engineering/IT",
    "occupation_sector": "Private",
    "annual_income": "$150,000-250,000",
    "family_type": "Nuclear",
    "family_status": "Affluent",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Working professional",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+14085551234",
}

ARJUN_PREFS = {
    "pref_age_min": 25,
    "pref_age_max": 31,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 155,
    "pref_height_max": 172,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Same country as me",
    "pref_raised_in": "Same country as me",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, within my state/country",
    "religious_practice": "Not very religious",
    "sect_denomination": None,
    "caste_community": "Patel",
    "caste_importance": "Doesn't matter",
    "partner_working": "Yes, she should have a career",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

ARJUN_SIGNALS = {
    "diet": "Occasionally non-veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Very social — love big gatherings",
    "conflict_style": "Talk it out immediately",
    "financial_planning": "Mostly separate",
    "manglik_status": None,
    "cooking_contribution": "4-7",
    "household_contribution": "Shared equally",
}


# Profile 8: Neha — 27F, Hindu Gujarati, 2nd gen in San Francisco, raised in USA
NEHA_USER = {
    "id": 8,
    "full_name": "Neha Mehta",
    "gender": "Female",
    "date_of_birth": date(1998, 9, 25),  # age ~27
    "city_current": "San Francisco",
    "country_current": "USA",
    "state_india": None,
    "raised_in_state": None,
    "raised_in_city": "Fremont",
    "raised_in_country": "USA",
    "mother_tongue": "Gujarati",
    "languages_spoken": ["English", "Hindi"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 165,
    "weight_kg": 57,
    "religion": "Hindu",
    "education_level": "Master's",
    "education_field": "Business/MBA",
    "occupation_sector": "Private",
    "annual_income": "$100,000-150,000",
    "family_type": "Nuclear",
    "family_status": "Affluent",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Working professional",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+15105551234",
}

NEHA_PREFS = {
    "pref_age_min": 27,
    "pref_age_max": 33,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "$100,000-150,000",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 172,
    "pref_height_max": 188,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "After 2-3 years",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Same country as me",
    "pref_raised_in": "Same country as me",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, within my state/country",
    "religious_practice": "Not very religious",
    "sect_denomination": None,
    "caste_community": "Patel",
    "caste_importance": "Doesn't matter",
    "pref_partner_cooking": "Sometimes (3-6)",
    "pref_partner_household": "Equal share",
    "pref_manglik": "Doesn't matter",
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

NEHA_SIGNALS = {
    "diet": "Occasionally non-veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "3-5 times a week",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Talk it out immediately",
    "financial_planning": "Mostly separate",
    "manglik_status": None,
    "do_you_cook": "Yes, but I don't cook often",
    "career_after_marriage": "Yes, definitely",
    "live_with_inlaws": "Prefer not to",
}


# Profile 9: Imran — 29M, Muslim, Delhi, religious, non-veg
IMRAN_USER = {
    "id": 9,
    "full_name": "Imran Sheikh",
    "gender": "Male",
    "date_of_birth": date(1996, 4, 18),  # age ~29
    "city_current": "Delhi",
    "country_current": "India",
    "state_india": "Delhi",
    "raised_in_state": "Uttar Pradesh",
    "raised_in_city": "Lucknow",
    "raised_in_country": "India",
    "mother_tongue": "Urdu",
    "languages_spoken": ["Hindi", "English"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 176,
    "weight_kg": 74,
    "religion": "Muslim",
    "education_level": "Master's",
    "education_field": "Business/MBA",
    "occupation_sector": "Private",
    "annual_income": "₹20-35 lakh",
    "family_type": "Joint",
    "family_status": "Upper middle class",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Homemaker",
    "siblings": "2 siblings",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543300",
}

IMRAN_PREFS = {
    "pref_age_min": 22,
    "pref_age_max": 28,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same or Hindi",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Must not drink",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 155,
    "pref_height_max": 170,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "With parents (joint)",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "Soon after marriage",
    "living_arrangement": "With parents (joint)",
    "relocation_willingness": "Yes, within India",
    "religious_practice": "Religious",
    "sect_denomination": "Sunni",
    "caste_community": None,
    "caste_importance": None,
    "partner_working": "Her choice",
    "pref_manglik": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "No",
}

IMRAN_SIGNALS = {
    "diet": "Non-veg",
    "drinking": "Never",
    "smoking": "Never",
    "fitness_frequency": "1-2 times a week",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Take some time, then discuss",
    "financial_planning": "Fully joint",
    "manglik_status": None,
    "cooking_contribution": "1-3",
    "household_contribution": "Mostly her",
}


# Profile 10: Sarah — 26F, Christian, Bangalore, religious
SARAH_USER = {
    "id": 10,
    "full_name": "Sarah Thomas",
    "gender": "Female",
    "date_of_birth": date(1999, 12, 3),  # age ~26
    "city_current": "Bangalore",
    "country_current": "India",
    "state_india": "Karnataka",
    "raised_in_state": "Kerala",
    "raised_in_city": "Kochi",
    "raised_in_country": "India",
    "mother_tongue": "Malayalam",
    "languages_spoken": ["English", "Hindi"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 160,
    "weight_kg": 54,
    "religion": "Christian",
    "education_level": "Master's",
    "education_field": "Engineering/IT",
    "occupation_sector": "Private",
    "annual_income": "₹10-20 lakh",
    "family_type": "Nuclear",
    "family_status": "Upper middle class",
    "father_occupation": "Professional",
    "mother_occupation": "Working professional",
    "siblings": "1 sibling",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543400",
}

SARAH_PREFS = {
    "pref_age_min": 26,
    "pref_age_max": 33,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Same or Hindi",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "Doesn't matter",
    "pref_diet": "Doesn't matter",
    "pref_drinking": "Social drinking OK",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 170,
    "pref_height_max": 188,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "After 2-3 years",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "2-3 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Independent",
    "relocation_willingness": "Yes, anywhere",
    "religious_practice": "Religious",
    "sect_denomination": "Catholic",
    "caste_community": None,
    "caste_importance": None,
    "pref_partner_cooking": "Doesn't matter",
    "pref_partner_household": "Equal share",
    "pref_manglik": None,
    "pref_family_status": "Doesn't matter",
    "pref_conditions": "Depends on condition",
}

SARAH_SIGNALS = {
    "diet": "Non-veg",
    "drinking": "Socially / Occasionally",
    "smoking": "Never",
    "fitness_frequency": "1-2 times a week",
    "social_style": "Social — enjoy going out but need downtime",
    "conflict_style": "Take some time, then discuss",
    "financial_planning": "Joint for household, separate for personal",
    "manglik_status": None,
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Yes, definitely",
    "live_with_inlaws": "Prefer not to",
}


# Profile 11: Sonal — 25F, Jain, Mumbai, strict Jain veg
SONAL_USER = {
    "id": 11,
    "full_name": "Sonal Jain",
    "gender": "Female",
    "date_of_birth": date(2000, 6, 14),  # age ~25
    "city_current": "Mumbai",
    "country_current": "India",
    "state_india": "Maharashtra",
    "raised_in_state": "Rajasthan",
    "raised_in_city": "Jaipur",
    "raised_in_country": "India",
    "mother_tongue": "Hindi",
    "languages_spoken": ["English", "Marathi"],
    "marital_status": "Never married",
    "children_existing": None,
    "height_cm": 158,
    "weight_kg": 50,
    "religion": "Jain",
    "education_level": "Bachelor's",
    "education_field": "Finance / CA / CS",
    "occupation_sector": "Professional (Doctor, Lawyer, CA)",
    "annual_income": "₹10-20 lakh",
    "family_type": "Joint",
    "family_status": "Affluent",
    "father_occupation": "Business/Self-employed",
    "mother_occupation": "Homemaker",
    "siblings": "2 siblings",
    "known_conditions": None,
    "disability": None,
    "phone": "+919876543500",
}

SONAL_PREFS = {
    "pref_age_min": 25,
    "pref_age_max": 32,
    "pref_religion": "Same religion only",
    "pref_religion_exclude": None,
    "pref_caste": "Open to all",
    "pref_caste_exclude": None,
    "pref_mother_tongue": "Doesn't matter",
    "pref_education_min": "At least Bachelor's",
    "pref_education_field": "Doesn't matter",
    "pref_income_min": "₹10-20 lakh",
    "pref_diet": "Same as mine",
    "pref_drinking": "Must not drink",
    "pref_smoking": "Must not smoke",
    "pref_height_min": 168,
    "pref_height_max": 185,
    "pref_marital_status": ["Never married"],
    "pref_children_existing": "No",
    "pref_siblings": "Doesn't matter",
    "pref_children_timeline": "Doesn't matter",
    "pref_living_arrangement": "Doesn't matter",
    "pref_current_location": "Anywhere",
    "pref_raised_in": "Doesn't matter",
    "pref_disability": "No",
    "marriage_timeline": "1-2 years",
    "children_intent": "Yes",
    "children_timeline": "After 2-3 years",
    "living_arrangement": "Open to discussion",
    "relocation_willingness": "Yes, within India",
    "religious_practice": "Very religious",
    "sect_denomination": "Shwetambar",
    "caste_community": None,
    "caste_importance": None,
    "pref_partner_cooking": "Doesn't matter",
    "pref_partner_household": "Some help",
    "pref_manglik": None,
    "pref_family_status": "Same or higher",
    "pref_conditions": "No",
}

SONAL_SIGNALS = {
    "diet": "Jain",
    "drinking": "Never",
    "smoking": "Never",
    "fitness_frequency": "1-2 times a week",
    "social_style": "Introverted — prefer small groups",
    "conflict_style": "Take some time, then discuss",
    "financial_planning": "Fully joint",
    "manglik_status": None,
    "do_you_cook": "Yes, I cook regularly",
    "career_after_marriage": "Yes, but open to break for kids",
    "live_with_inlaws": "Yes, happy to",
}


# ============== HARD FILTER TESTS ==============


def test_gender_filter():
    assert check_gender(ARUN_USER, PRIYA_USER) == True, "Male-Female should pass"
    assert check_gender(ARUN_USER, RAJ_USER) == False, "Male-Male should fail"
    assert check_gender(PRIYA_USER, FATIMA_USER) == False, "Female-Female should fail"
    print("  PASS gender filter")


def test_age_filter():
    # Arun (29) with Priya prefs (27-34) → passes
    passes = check_age(PRIYA_PREFS, ARUN_USER)
    assert passes == True, "Arun 29 within Priya's 27-34"

    # Priya (27) with Arun prefs (24-30) → passes
    passes = check_age(ARUN_PREFS, PRIYA_USER)
    assert passes == True, "Priya 27 within Arun's 24-30"

    # Fatima (25) with Priya prefs (27-34) → v2 strict: FAIL (no buffer)
    passes = check_age(PRIYA_PREFS, FATIMA_USER)
    assert passes == False, "Fatima 25 outside Priya's 27-34, no buffer in v2"
    print("  PASS age filter")


def test_religion_filter():
    # Arun (Hindu) with Priya prefs (Same religion only) — both Hindu → pass
    assert check_religion_full(PRIYA_USER, PRIYA_PREFS, ARUN_USER) == True

    # Arun (Hindu) with Fatima prefs (Same religion only = Muslim) → fail
    assert check_religion_full(FATIMA_USER, FATIMA_PREFS, ARUN_USER) == False

    # Raj prefs (Open to all) → always pass
    assert check_religion_full(RAJ_USER, RAJ_PREFS, FATIMA_USER) == True
    print("  PASS religion filter")


def test_marital_status_filter():
    # Arun prefs ["Never married"] + Priya (Never married) → pass
    assert check_marital_status(ARUN_PREFS, PRIYA_USER) == True

    # Arun prefs ["Never married"] + Raj (Divorced) → fail
    assert check_marital_status(ARUN_PREFS, RAJ_USER) == False

    # Fatima prefs "Any" → always pass
    assert check_marital_status(FATIMA_PREFS, RAJ_USER) == True

    # No pref → pass
    assert check_marital_status({}, RAJ_USER) == True
    print("  PASS marital status filter")


def test_children_existing_filter():
    # "No" + candidate has no children → pass
    assert check_children_existing(ARUN_PREFS, PRIYA_USER) == True

    # "No" + candidate has children → fail
    parent = {**PRIYA_USER, "children_existing": "Yes, they live with me"}
    assert check_children_existing(ARUN_PREFS, parent) == False

    # "Only if they don't live with them" + "Yes, they live with me" → fail
    pref = {"pref_children_existing": "Only if they don't live with them"}
    assert check_children_existing(pref, parent) == False

    # "Only if they don't live with them" + "Yes, they don't live with me" → pass
    non_custodial = {**PRIYA_USER, "children_existing": "Yes, they don't live with me"}
    assert check_children_existing(pref, non_custodial) == True

    # "Yes" → always pass
    assert check_children_existing({"pref_children_existing": "Yes"}, parent) == True
    print("  PASS children existing filter")


def test_children_intent_filter():
    # Both want kids → pass
    assert check_children_intent(ARUN_PREFS, PRIYA_PREFS) == True

    # One says No, other says Yes → fail
    no_kids_prefs = {**ARUN_PREFS, "children_intent": "No"}
    assert check_children_intent(no_kids_prefs, PRIYA_PREFS) == False

    # Maybe is compatible with Yes
    maybe_prefs = {**ARUN_PREFS, "children_intent": "Maybe / Open to it"}
    assert check_children_intent(maybe_prefs, PRIYA_PREFS) == True
    print("  PASS children intent filter")


def test_diet_filter():
    # Arun prefs "Veg" + Priya (Veg) → pass
    assert check_diet(ARUN_PREFS, PRIYA_SIGNALS) == True

    # Arun prefs "Veg" + Raj (Non-veg) → fail
    assert check_diet(ARUN_PREFS, RAJ_SIGNALS) == False

    # "Any but not non-veg" + Eggetarian → pass
    pref = {"pref_diet": "Any but not non-veg"}
    assert check_diet(pref, {"diet": "Eggetarian"}) == True

    # "Any but not non-veg" + Non-veg → fail
    assert check_diet(pref, {"diet": "Non-veg"}) == False

    # "Any but not non-veg" + Occasionally non-veg → fail
    assert check_diet(pref, {"diet": "Occasionally non-veg"}) == False

    # Raj prefs "Doesn't matter" → always pass
    assert check_diet(RAJ_PREFS, PRIYA_SIGNALS) == True

    # "Same as mine" with matching diet → pass
    same_pref = {"pref_diet": "Same as mine", "_user_diet": "Veg"}
    assert check_diet(same_pref, {"diet": "Veg"}) == True

    # "Same as mine" with different diet → fail
    assert check_diet(same_pref, {"diet": "Non-veg"}) == False
    print("  PASS diet filter")


def test_smoking_filter():
    # Priya prefs "Must not smoke" + Arun (Never) → pass
    assert check_smoking(PRIYA_PREFS, ARUN_SIGNALS) == True

    # Priya prefs "Must not smoke" + Raj (Socially) → pass (only Regularly fails)
    assert check_smoking(PRIYA_PREFS, RAJ_SIGNALS) == True

    # Must not smoke + Regularly → fail
    heavy_smoker = {"smoking": "Regularly"}
    assert check_smoking(PRIYA_PREFS, heavy_smoker) == False
    print("  PASS smoking filter")


def test_drinking_filter():
    # Fatima prefs "Must not drink" + Arun (Socially) → pass (only Regularly fails)
    assert check_drinking(FATIMA_PREFS, ARUN_SIGNALS) == True

    # Must not drink + Regularly → fail
    heavy_drinker = {"drinking": "Regularly"}
    assert check_drinking(FATIMA_PREFS, heavy_drinker) == False
    print("  PASS drinking filter")


def test_marriage_timeline_filter():
    # Arun (1-2 years) + Priya (1-2 years) → pass
    assert check_marriage_timeline(ARUN_PREFS, PRIYA_PREFS) == True

    # Arun (1-2 years) + Raj (2-3 years) → pass (1 step apart)
    assert check_marriage_timeline(ARUN_PREFS, RAJ_PREFS) == True

    # "Within 1 year" + "Just exploring" → fail (3 steps apart)
    urgent = {"marriage_timeline": "Within 1 year"}
    exploring = {"marriage_timeline": "Just exploring"}
    assert check_marriage_timeline(urgent, exploring) == False
    print("  PASS marriage timeline filter")


def test_mother_tongue_filter():
    # Priya prefs "Same language only" + Arun (Gujarati) → pass (both Gujarati)
    assert check_mother_tongue(PRIYA_USER, PRIYA_PREFS, ARUN_USER) == True

    # Priya prefs "Same language only" + Raj (Punjabi) → fail
    assert check_mother_tongue(PRIYA_USER, PRIYA_PREFS, RAJ_USER) == False

    # Arun prefs "Same or Hindi" + Priya (Gujarati) → pass (same language)
    assert check_mother_tongue(ARUN_USER, ARUN_PREFS, PRIYA_USER) == True

    # Arun prefs "Same or Hindi" + Fatima (Urdu, speaks Hindi) → pass (speaks Hindi)
    assert check_mother_tongue(ARUN_USER, ARUN_PREFS, FATIMA_USER) == True

    # "Same or Hindi" + someone who speaks neither → fail
    no_hindi = {**FATIMA_USER, "mother_tongue": "Tamil", "languages_spoken": ["English"]}
    assert check_mother_tongue(ARUN_USER, ARUN_PREFS, no_hindi) == False

    # "Doesn't matter" → always pass
    assert check_mother_tongue(FATIMA_USER, FATIMA_PREFS, ARUN_USER) == True
    print("  PASS mother tongue filter")


def test_height_filter():
    # Arun prefs (155-170) + Priya (162) → pass
    assert check_height(ARUN_PREFS, PRIYA_USER) == True

    # Arun prefs (155-170) + tall candidate → fail
    tall = {**PRIYA_USER, "height_cm": 175}
    assert check_height(ARUN_PREFS, tall) == False

    # Arun prefs (155-170) + short candidate → fail
    short = {**PRIYA_USER, "height_cm": 150}
    assert check_height(ARUN_PREFS, short) == False

    # No height pref → pass
    assert check_height({}, PRIYA_USER) == True

    # Missing candidate height → pass (don't eliminate)
    assert check_height(ARUN_PREFS, {"height_cm": None}) == True
    print("  PASS height filter")


def test_disability_filter():
    # Arun prefs "No" + Priya (no disability) → pass
    assert check_disability(ARUN_PREFS, PRIYA_USER) == True

    # Arun prefs "No" + candidate with disability → fail
    disabled = {**PRIYA_USER, "disability": "Yes"}
    assert check_disability(ARUN_PREFS, disabled) == False

    # Fatima prefs "Depends" → always pass
    assert check_disability(FATIMA_PREFS, disabled) == True

    # Raj prefs "Yes" → always pass
    assert check_disability(RAJ_PREFS, disabled) == True

    # No pref → pass
    assert check_disability({}, disabled) == True
    print("  PASS disability filter")


def test_current_location_filter():
    # "Same city" + same city → pass
    same_city_prefs = {**ARUN_PREFS, "pref_current_location": "Same city as me"}
    fatima_in_mumbai = FATIMA_USER  # Also in Mumbai
    assert check_current_location(ARUN_USER, same_city_prefs, fatima_in_mumbai, FATIMA_PREFS) == True

    # "Same city" + different city → fail
    assert check_current_location(ARUN_USER, same_city_prefs, PRIYA_USER, PRIYA_PREFS) == False

    # "Anywhere" + both refuse to relocate + different countries → fail (relocation fallback)
    anywhere_prefs = {**ARUN_PREFS, "pref_current_location": "Anywhere",
                      "relocation_willingness": "No, I'm settled"}
    usa_user = {**PRIYA_USER, "country_current": "USA"}
    usa_prefs = {**PRIYA_PREFS, "relocation_willingness": "No, I'm settled"}
    assert check_current_location(ARUN_USER, anywhere_prefs, usa_user, usa_prefs) == False

    # "Anywhere" + same country → pass regardless
    assert check_current_location(ARUN_USER, anywhere_prefs, PRIYA_USER, PRIYA_PREFS) == True
    print("  PASS current location filter")


def test_raised_in_filter():
    # "Same country as me" + both India → pass
    same_country_prefs = {**ARUN_PREFS, "pref_raised_in": "Same country as me"}
    assert check_raised_in(ARUN_USER, same_country_prefs, PRIYA_USER) == True

    # "Same country as me" + different country → fail
    usa_raised = {**PRIYA_USER, "raised_in_country": "USA"}
    assert check_raised_in(ARUN_USER, same_country_prefs, usa_raised) == False

    # "Same state" + same state → pass (both raised in Gujarat)
    same_state_prefs = {**ARUN_PREFS, "pref_raised_in": "Same state"}
    assert check_raised_in(ARUN_USER, same_state_prefs, PRIYA_USER) == True

    # "Same state" + different state → fail
    diff_state = {**PRIYA_USER, "raised_in_state": "Maharashtra"}
    assert check_raised_in(ARUN_USER, same_state_prefs, diff_state) == False

    # "Doesn't matter" → always pass
    assert check_raised_in(ARUN_USER, ARUN_PREFS, PRIYA_USER) == True
    print("  PASS raised_in filter")


def test_conditions_filter():
    # Priya prefs "Depends on condition" → always pass
    assert check_conditions(PRIYA_PREFS, ARUN_USER) == True

    # Fatima prefs "No" + candidate has condition → fail
    user_with_condition = {**ARUN_USER, "known_conditions": "Diabetes"}
    assert check_conditions(FATIMA_PREFS, user_with_condition) == False

    # Fatima prefs "No" + candidate has no condition → pass
    assert check_conditions(FATIMA_PREFS, ARUN_USER) == True
    print("  PASS conditions filter")


def test_bidirectional_filters():
    # Arun ↔ Priya: Both Hindu, compatible on all fronts → should pass
    passes, a_fail, b_fail = pass_hard_filters_bidirectional(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert passes == True, f"Arun↔Priya should pass. A failed: {a_fail}, B failed: {b_fail}"

    # Arun ↔ Fatima: Different religions, both strict → should fail
    passes, a_fail, b_fail = pass_hard_filters_bidirectional(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        FATIMA_USER, FATIMA_PREFS, FATIMA_SIGNALS,
    )
    assert passes == False, "Arun↔Fatima should fail on religion"
    assert "religion" in a_fail or "religion" in b_fail

    # Arun ↔ Raj: Same gender → should fail
    passes, a_fail, b_fail = pass_hard_filters_bidirectional(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
    )
    assert passes == False, "Arun↔Raj should fail on gender"
    print("  PASS bidirectional filters")


# ============== SCORING TESTS ==============


def test_scoring_compatible_pair():
    # Arun ↔ Priya: Should score reasonably high (both Hindu Gujarati, similar values)
    result = calculate_bidirectional_score(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    score = result["score"]
    print(f"  Arun ↔ Priya score: {score}")
    print(f"    A→B: {result['score_a_for_b']} ({result['total_a']}/{result['max_a']})")
    print(f"    B→A: {result['score_b_for_a']} ({result['total_b']}/{result['max_b']})")
    assert score >= 50, f"Compatible pair should score >= 50, got {score}"
    print("  PASS scoring compatible pair")


def test_per_question_scoring():
    """Verify per-question scoring model returns expected structure."""
    result = calculate_match_score(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    # Must have score, total, max, details
    assert "score" in result
    assert "total" in result
    assert "max" in result
    assert "details" in result
    assert result["max"] > 0, "Max possible should be > 0"
    assert 0 <= result["score"] <= 100, f"Score should be 0-100, got {result['score']}"

    # Details should contain question-level scores
    details = result["details"]
    assert len(details) > 0, "Should have scored questions"
    # Check a known question
    assert "religion" in details
    assert details["religion"]["score"] == 1.0, "Same religion should score 1.0"
    assert details["religion"]["max"] == 1.0

    print(f"  Score: {result['score']}, Total: {result['total']}/{result['max']}")
    print(f"  Scored questions: {len(details)}")
    print("  PASS per-question scoring")


def test_confidence():
    conf = calculate_confidence(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert conf in ("high", "medium", "low")
    print(f"  Arun↔Priya confidence: {conf}")

    # Sparse profiles should be low confidence
    sparse_user = {"id": 99, "gender": "Male", "religion": "Hindu"}
    sparse_prefs = {}
    sparse_signals = {}
    conf2 = calculate_confidence(
        sparse_user, sparse_prefs, sparse_signals,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert conf2 == "low", f"Sparse profile should be low confidence, got {conf2}"
    print("  PASS confidence")


def test_explanation():
    score_result = calculate_bidirectional_score(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    expl = generate_explanation(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
        score_result,
    )
    assert "highlights" in expl
    assert len(expl["highlights"]) > 0
    print(f"  Explanation highlights: {expl['highlights']}")
    print("  PASS explanation")


# ============== END-TO-END MATCH TESTS ==============


def test_e2e_compatible_match():
    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert result["matched"] == True, f"Arun↔Priya should match: {result}"
    print(f"  Arun↔Priya: matched={result['matched']}, score={result['score']}, tier={result['tier']}")
    print(f"    Explanation: {result['explanation']['highlights']}")
    print("  PASS e2e compatible match")


def test_e2e_incompatible_religion():
    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        FATIMA_USER, FATIMA_PREFS, FATIMA_SIGNALS,
    )
    assert result["matched"] == False, "Arun↔Fatima should NOT match (religion)"
    print(f"  Arun↔Fatima: matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e incompatible religion")


def test_e2e_same_gender():
    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
    )
    assert result["matched"] == False, "Arun↔Raj should NOT match (same gender)"
    print(f"  Arun↔Raj: matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e same gender")


def test_e2e_raj_priya():
    """Raj (liberal Hindu) ↔ Priya (moderate Hindu). Different but potentially compatible."""
    result = match_two_profiles(
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    print(f"  Raj↔Priya: matched={result['matched']}, ", end="")
    if result["matched"]:
        print(f"score={result['score']}, tier={result['tier']}")
        print(f"    Highlights: {result['explanation']['highlights']}")
    else:
        print(f"reason={result.get('reason')}")
    print("  PASS e2e raj-priya")


def test_e2e_almost_match():
    """Create a pair that should score in the 'almost' range."""
    almost_priya_prefs = {
        **PRIYA_PREFS,
        "marriage_timeline": "2-3 years",
        "living_arrangement": "With parents (joint)",
    }
    almost_priya_signals = {
        **PRIYA_SIGNALS,
        "conflict_style": "Avoid conflict",
    }

    result = match_two_profiles(
        ARUN_USER, ARUN_PREFS, ARUN_SIGNALS,
        PRIYA_USER, almost_priya_prefs, almost_priya_signals,
    )
    print(f"  Almost match test: matched={result['matched']}, ", end="")
    if result["matched"]:
        print(f"score={result['score']}, tier={result['tier']}")
    else:
        print(f"reason={result.get('reason')}")
    print("  PASS e2e almost match")


# ============== DIASPORA / CROSS-RELIGION SCENARIO TESTS ==============


def test_e2e_nri_us_australia():
    """
    Vikram (Hindu Tamil, NRI San Francisco) ↔ Meera (Hindu Tamil, NRI Sydney).
    Different countries, both willing to relocate anywhere. Same religion, same mother tongue,
    similar education/career. Should pass filters and score well.
    """
    result = match_two_profiles(
        VIKRAM_USER, VIKRAM_PREFS, VIKRAM_SIGNALS,
        MEERA_USER, MEERA_PREFS, MEERA_SIGNALS,
    )
    assert result["matched"] == True, f"NRI US↔NRI Australia should match: {result}"
    assert result["score"] >= 60, f"NRI compatible pair should score 60+, got {result['score']}"
    print(f"  Vikram(SF)↔Meera(Sydney): matched={result['matched']}, score={result['score']}, tier={result['tier']}")
    print(f"    Highlights: {result['explanation']['highlights']}")
    print("  PASS e2e NRI US ↔ NRI Australia")


def test_e2e_nri_us_australia_settled():
    """
    Both NRIs in different countries but BOTH refuse to relocate.
    Should fail on the relocation fallback gate.
    """
    vikram_settled = {**VIKRAM_PREFS, "relocation_willingness": "No, I'm settled"}
    meera_settled = {**MEERA_PREFS, "relocation_willingness": "No, I'm settled"}

    result = match_two_profiles(
        VIKRAM_USER, vikram_settled, VIKRAM_SIGNALS,
        MEERA_USER, meera_settled, MEERA_SIGNALS,
    )
    assert result["matched"] == False, "Both NRIs settled in different countries should fail"
    print(f"  Vikram(SF,settled)↔Meera(Sydney,settled): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e NRI both settled different countries")


def test_e2e_2nd_gen_us_match():
    """
    Arjun (2nd gen SF, raised USA) ↔ Neha (2nd gen SF, raised USA).
    Both want partner raised in same country (USA), same city, same religion,
    both Gujarati. Should score very high.
    """
    result = match_two_profiles(
        ARJUN_USER, ARJUN_PREFS, ARJUN_SIGNALS,
        NEHA_USER, NEHA_PREFS, NEHA_SIGNALS,
    )
    assert result["matched"] == True, f"2nd gen US pair should match: {result}"
    assert result["score"] >= 70, f"2nd gen US compatible pair should score 70+, got {result['score']}"
    print(f"  Arjun(2ndGen SF)↔Neha(2ndGen SF): matched={result['matched']}, score={result['score']}, tier={result['tier']}")
    print(f"    Highlights: {result['explanation']['highlights']}")
    print("  PASS e2e 2nd gen US ↔ 2nd gen US")


def test_e2e_2nd_gen_rejects_india_raised():
    """
    Arjun (2nd gen, wants partner raised in USA) ↔ Priya (raised in India).
    Should fail on raised_in gate — Arjun requires "Same country as me" (USA).
    """
    result = match_two_profiles(
        ARJUN_USER, ARJUN_PREFS, ARJUN_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert result["matched"] == False, "2nd gen wanting USA-raised should reject India-raised"
    assert "raised_in" in result.get("reason", ""), f"Should fail on raised_in, got: {result.get('reason')}"
    print(f"  Arjun(2ndGen)↔Priya(India-raised): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e 2nd gen rejects India-raised")


def test_e2e_2nd_gen_rejects_different_country():
    """
    Arjun (2nd gen SF, wants same country) ↔ Meera (NRI Sydney, raised India).
    Fails on BOTH raised_in (USA vs India) AND current_location (USA vs Australia).
    """
    result = match_two_profiles(
        ARJUN_USER, ARJUN_PREFS, ARJUN_SIGNALS,
        MEERA_USER, MEERA_PREFS, MEERA_SIGNALS,
    )
    assert result["matched"] == False, "2nd gen US should reject NRI in Australia"
    print(f"  Arjun(2ndGen SF)↔Meera(NRI Sydney): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e 2nd gen rejects different country NRI")


def test_e2e_muslim_christian_no_match():
    """
    Imran (Muslim, "Same religion only") ↔ Sarah (Christian, "Same religion only").
    Both strict on religion. Should hard-fail bidirectionally on religion.
    """
    result = match_two_profiles(
        IMRAN_USER, IMRAN_PREFS, IMRAN_SIGNALS,
        SARAH_USER, SARAH_PREFS, SARAH_SIGNALS,
    )
    assert result["matched"] == False, "Muslim↔Christian both strict should NOT match"
    assert "religion" in result.get("reason", ""), f"Should fail on religion, got: {result.get('reason')}"
    print(f"  Imran(Muslim)↔Sarah(Christian): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e Muslim ↔ Christian no match")


def test_e2e_imran_fatima():
    """
    Imran (29M Muslim Delhi) ↔ Fatima (25F Muslim Mumbai).
    Same religion, both religious, similar values. Should match well.
    """
    result = match_two_profiles(
        IMRAN_USER, IMRAN_PREFS, IMRAN_SIGNALS,
        FATIMA_USER, FATIMA_PREFS, FATIMA_SIGNALS,
    )
    assert result["matched"] == True, f"Muslim pair should match: {result}"
    print(f"  Imran↔Fatima: matched={result['matched']}, score={result['score']}, tier={result['tier']}")
    print(f"    Highlights: {result['explanation']['highlights']}")
    print("  PASS e2e Imran ↔ Fatima (Muslim pair)")


def test_e2e_jain_strict_veg_vs_nonveg():
    """
    Sonal (Jain, diet="Jain", pref="Same as mine") ↔ Raj (Hindu, diet="Non-veg").
    Sonal requires Jain diet match. Hard filter should kill on religion AND diet.
    """
    result = match_two_profiles(
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
        SONAL_USER, SONAL_PREFS, SONAL_SIGNALS,
    )
    assert result["matched"] == False, "Jain strict veg should not match non-veg Hindu"
    # Sonal's direction: religion (Jain≠Hindu) + diet (Jain≠Non-veg)
    print(f"  Raj(Non-veg Hindu)↔Sonal(Jain strict): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e Jain strict veg vs non-veg")


def test_e2e_divorced_with_kids_rejected():
    """
    Raj modified to have kids + Priya who says "No" to existing children.
    Should fail on children_existing gate.
    """
    raj_with_kids = {**RAJ_USER, "children_existing": "Yes, they live with me"}
    result = match_two_profiles(
        raj_with_kids, RAJ_PREFS, RAJ_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert result["matched"] == False, "Divorced with kids should fail against 'No children' pref"
    assert "children_existing" in result.get("reason", ""), f"Should fail on children_existing, got: {result.get('reason')}"
    print(f"  Raj(divorced+kids)↔Priya(no kids pref): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e divorced with kids rejected")


def test_e2e_nri_wants_raised_abroad_only():
    """
    Vikram with pref "Raised abroad" ↔ Priya (raised in India).
    Should fail because Priya was raised in India, not abroad.
    """
    vikram_abroad_only = {**VIKRAM_PREFS, "pref_raised_in": "Raised abroad"}
    result = match_two_profiles(
        VIKRAM_USER, vikram_abroad_only, VIKRAM_SIGNALS,
        PRIYA_USER, PRIYA_PREFS, PRIYA_SIGNALS,
    )
    assert result["matched"] == False, "NRI wanting 'Raised abroad' should reject India-raised"
    assert "raised_in" in result.get("reason", ""), f"Should fail on raised_in, got: {result.get('reason')}"
    print(f"  Vikram('Raised abroad')↔Priya(India-raised): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e NRI wants raised abroad only")


def test_e2e_open_religion_cross_match():
    """
    Raj (Hindu, "Open to all") ↔ Fatima (Muslim, "Same religion only").
    Raj is open, but Fatima isn't. Should fail on Fatima's direction (religion).
    """
    result = match_two_profiles(
        RAJ_USER, RAJ_PREFS, RAJ_SIGNALS,
        FATIMA_USER, FATIMA_PREFS, FATIMA_SIGNALS,
    )
    assert result["matched"] == False, "Open Hindu ↔ strict Muslim should fail (one-sided religion gate)"
    print(f"  Raj(Open Hindu)↔Fatima(strict Muslim): matched={result['matched']}, reason={result.get('reason')}")
    print("  PASS e2e open religion vs strict religion")


# ============== RUN ALL TESTS ==============


def run_all_tests():
    print("\n=== HARD FILTER TESTS ===\n")
    test_gender_filter()
    test_age_filter()
    test_religion_filter()
    test_marital_status_filter()
    test_children_existing_filter()
    test_children_intent_filter()
    test_diet_filter()
    test_smoking_filter()
    test_drinking_filter()
    test_marriage_timeline_filter()
    test_mother_tongue_filter()
    test_height_filter()
    test_disability_filter()
    test_current_location_filter()
    test_raised_in_filter()
    test_conditions_filter()
    test_bidirectional_filters()

    print("\n=== SCORING TESTS ===\n")
    test_scoring_compatible_pair()
    test_per_question_scoring()
    test_confidence()
    test_explanation()

    print("\n=== END-TO-END MATCH TESTS ===\n")
    test_e2e_compatible_match()
    test_e2e_incompatible_religion()
    test_e2e_same_gender()
    test_e2e_raj_priya()
    test_e2e_almost_match()

    print("\n=== DIASPORA / CROSS-RELIGION SCENARIOS ===\n")
    test_e2e_nri_us_australia()
    test_e2e_nri_us_australia_settled()
    test_e2e_2nd_gen_us_match()
    test_e2e_2nd_gen_rejects_india_raised()
    test_e2e_2nd_gen_rejects_different_country()
    test_e2e_muslim_christian_no_match()
    test_e2e_imran_fatima()
    test_e2e_jain_strict_veg_vs_nonveg()
    test_e2e_divorced_with_kids_rejected()
    test_e2e_nri_wants_raised_abroad_only()
    test_e2e_open_religion_cross_match()

    print("\n=== ALL TESTS PASSED ===\n")


if __name__ == "__main__":
    run_all_tests()
