#!/usr/bin/env python3
import urllib.request, urllib.parse, json
from google_api import refresh_access_token

SHEET_ID = "18nvSgfJ0yD_DDoNMhV8-0JvjP_DT0tbsPkOHDjclywA"

def sheets_values_update(spreadsheet_id, range_name, values):
    access_token = refresh_access_token()
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{urllib.parse.quote(range_name)}?valueInputOption=RAW"
    body = {"values": values}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# Updated USERS TABLE rows (first_name, last_name, full_name, alias - all 4 fields)
updated_rows = [
    ["Field Name", "Data Type", "Tier", "Required", "Input Method", "Description"],
    # Tier 1A: Identity & Demographics
    ["first_name", "VARCHAR(100)", "1A", "Yes", "LLM", "User's first name"],
    ["last_name", "VARCHAR(100)", "1A", "Yes", "LLM", "User's last name"],
    ["full_name", "VARCHAR(255)", "1A", "Yes", "AUTO", "Full name (auto-generated from first + last, or user override)"],
    ["alias", "VARCHAR(100)", "1A", "No", "LLM", "Preferred nickname/alias (optional)"],
    ["date_of_birth", "DATE", "1A", "Yes", "LLM", "Date of birth (age calculated automatically)"],
    ["age", "INT", "1A", "Yes", "AUTO", "Auto-calculated from DOB (18-80 validation)"],
    ["gender_identity", "VARCHAR(50)", "1A", "Yes", "BUTTON", "Gender identity (Male/Female/Non-binary/Custom)"],
    ["sexual_orientation", "VARCHAR(50)", "1A", "Yes", "BUTTON", "Sexual orientation (Heterosexual/Gay/Lesbian/Bi/Pan/Ace/Other)"],
    ["city", "VARCHAR(255)", "1A", "Yes", "LLM", "Current city of residence"],
    ["country", "VARCHAR(100)", "1A", "Yes", "LLM", "Current country"],
    ["nationality", "VARCHAR(100)", "1A", "Yes", "LLM", "Nationality/citizenship"],
    ["native_languages", "TEXT[]", "1A", "Yes", "LLM", "Array of native/fluent languages"],
    ["ethnicity", "VARCHAR(100)", "1A", "No", "LLM", "Ethnicity/race (optional, culturally sensitive)"],
    
    # Tier 1B: Hard Deal-Breakers
    ["religion", "VARCHAR(100)", "1B", "Yes", "BUTTON", "Religion (Muslim/Hindu/Christian/Jewish/Buddhist/Sikh/Spiritual/Atheist/Agnostic/Other)"],
    ["children_intent", "VARCHAR(50)", "1B", "Yes", "BUTTON", "Children intent (Want kids/Don't want/Already have/Not sure/Want more)"],
    ["marital_history", "VARCHAR(50)", "1B", "Yes", "BUTTON", "Marital status (Never married/Divorced/Widowed/Separated)"],
    ["smoking", "VARCHAR(50)", "1B", "Yes", "BUTTON", "Smoking status (Never/Socially/Current/Former/Vape)"],
    ["drinking", "VARCHAR(50)", "1B", "Yes", "BUTTON", "Drinking frequency (Never/Socially/Occasionally/Regularly/Former)"],
    ["dietary_restrictions", "VARCHAR(100)", "1B", "Yes", "BUTTON", "Dietary restrictions (None/Halal/Kosher/Vegetarian/Vegan/Pescatarian/GF/Other)"],
    ["relationship_intent", "VARCHAR(100)", "1B", "Yes", "BUTTON", "Relationship goal (Marriage/Long-term/Open to either/Dating)"],
    ["relationship_timeline", "VARCHAR(50)", "1B", "Yes", "BUTTON", "Timeline (Ready now/Within year/1-2 years/2+ years/Exploring)"],
    
    # Tier 1C: Basic Preferences
    ["occupation", "VARCHAR(255)", "1C", "No", "LLM", "Current occupation/job title"],
    ["industry", "VARCHAR(100)", "1C", "No", "LLM", "Industry sector"],
    ["education_level", "VARCHAR(100)", "1C", "No", "LLM", "Highest education level"],
    ["caste_community", "VARCHAR(100)", "1C", "No", "LLM", "Caste/community (Indian/Jewish/other cultures)"],
    ["height_cm", "INT", "1C", "No", "LLM", "Height in centimeters"],
    
    # Profile Status Fields
    ["tier_level", "INT", "Meta", "No", "AUTO", "Current tier (1-4), auto-updated by system"],
    ["profile_active", "BOOLEAN", "Meta", "No", "AUTO", "TRUE when MVP criteria met (matching activated)"],
    ["completeness_score", "DECIMAL(5,2)", "Meta", "No", "AUTO", "Weighted completion 0-100 (T1=50%, T2=35%, T3=15%)"],
    ["priority_score", "DECIMAL(5,2)", "Meta", "No", "AUTO", "Matching queue priority = completeness + recency"],
    ["matching_activated_at", "TIMESTAMPTZ", "Meta", "No", "AUTO", "Timestamp when user became match-eligible"],
    
    # Standard Fields
    ["telegram_id", "BIGINT", "Meta", "Yes", "AUTO", "Telegram user ID (primary identifier)"],
    ["created_at", "TIMESTAMPTZ", "Meta", "No", "AUTO", "Account creation timestamp"],
    ["updated_at", "TIMESTAMPTZ", "Meta", "No", "AUTO", "Last profile update timestamp"],
]

sheets_values_update(SHEET_ID, "'USERS TABLE'!A1", updated_rows)
print("✅ Updated USERS TABLE: first_name, last_name, full_name, alias (4 fields)")
print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
