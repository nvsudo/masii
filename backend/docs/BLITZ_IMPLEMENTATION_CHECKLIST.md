# JODI TELEGRAM BOT — IMPLEMENTATION CHECKLIST FOR BLITZ

**Created:** Feb 21, 2026  
**For:** Blitz (Implementation Lead)  
**From:** Seema (Product Co-Founder, Jodi)  
**Source:** Tab 3 "Updated MVP questions" from Jodi Schema sheet

---

## 📋 OVERVIEW

**Deliverable:** Telegram bot that executes the 77-question onboarding flow with conditional logic

**Tech Stack:**
- **Bot Framework:** python-telegram-bot or similar
- **Database:** Supabase (Postgres)
- **State Management:** Conversation state table + in-memory session cache
- **Button Handling:** Telegram inline keyboards (callback queries)
- **Conditional Logic:** Router pattern based on user answers

**Key Challenges:**
1. **Conditional branching:** 6-10 questions appear/disappear based on earlier answers
2. **Multi-select:** Languages spoken (C26) needs checkbox-style multi-select
3. **Two-step questions:** Partner age range (H56) is min → max flow
4. **Dynamic dropdowns:** State/city lists change based on country selection
5. **Save & resume:** User can exit mid-flow and resume later

---

## 🏗️ ARCHITECTURE

### 1. Conversation State Machine

**States:**
```python
class OnboardingState(Enum):
    INTRO = "intro"                    # Messages 1-7
    SECTION_A = "identity_basics"      # Questions 1-9
    SECTION_B = "location_mobility"    # Questions 10-17
    SECTION_C = "religion_culture"     # Questions 18-27
    SECTION_D = "education_career"     # Questions 28-32
    SECTION_E = "financial"            # Questions 33-37
    SECTION_F = "family"               # Questions 38-44
    SECTION_G = "lifestyle"            # Questions 45-55
    SECTION_H = "partner_prefs"        # Questions 56-64
    SECTION_I = "values"               # Questions 65-72
    SECTION_J = "dealbreakers"         # Questions 73-77
    PHOTO_UPLOAD = "photo_upload"
    SUMMARY = "summary"
    CONVERSATIONAL = "conversational"  # LLM mode
```

### 2. Data Models

**Session State (in-memory/Redis):**
```python
{
    "user_id": 123456789,
    "current_state": "SECTION_C",
    "current_question": 21,
    "answers": {
        "gender_identity": "Male",
        "religion": "Hindu",
        "residency_type": "Indian citizen (in India)",
        # ... collected answers
    },
    "skip_questions": [11, 17, 34],  # Conditional questions not shown
    "multi_select_buffer": {
        "languages_spoken": ["Hindi", "English"]
    },
    "photo_urls": [],
    "started_at": "2026-02-21T10:30:00Z",
    "last_active": "2026-02-21T10:35:00Z"
}
```

**Database Schema Mapping:**
- `users` table: Direct columns (gender_identity, religion, marital_status, etc.)
- `preferences` table: JSONB (partner preferences, dealbreakers)
- `personality` table: JSONB (soft signals, algo weights)

---

## 🔀 CONDITIONAL LOGIC ROUTER

### Core Routing Function
```python
def get_next_question(user_answers: dict, current_question: int) -> int | None:
    """
    Returns next question number, or None if section complete.
    Implements all conditional skip logic.
    """
    next_q = current_question + 1
    
    # A5: Show only if marital_status ≠ "Never married"
    if next_q == 5:
        if user_answers.get("marital_status") == "Never married":
            return get_next_question(user_answers, next_q)  # Skip to A6
    
    # B11: Show only if residency_type ≠ "Indian citizen (in India)"
    if next_q == 11:
        if user_answers.get("residency_type") == "Indian citizen (in India)":
            return get_next_question(user_answers, next_q)  # Skip to B13
    
    # B12: Show only if residency_type = "Indian citizen (in India)"
    if next_q == 12:
        if user_answers.get("residency_type") != "Indian citizen (in India)":
            return get_next_question(user_answers, next_q)  # Skip to B13
    
    # B17: Show only if NRI/OCI
    if next_q == 17:
        if user_answers.get("residency_type") not in ["NRI", "OCI / PIO"]:
            return 18  # Jump to Section C
    
    # C21: Dropdown options change based on religion (always shown, just different options)
    # (No skip logic, handled in button generation)
    
    # C22-C24, C27: Show only for Hindu/Jain/Sikh/Buddhist
    if next_q in [22, 23, 24, 27]:
        religion = user_answers.get("religion")
        if religion not in ["Hindu", "Jain", "Sikh", "Buddhist"]:
            if next_q == 22:
                return 25  # Skip caste section, jump to mother_tongue
            elif next_q == 27:
                return 28  # Skip manglik, jump to Section D
            else:
                return get_next_question(user_answers, next_q)
    
    # C23: Show only if caste_community answered (not "Prefer not to say")
    if next_q == 23:
        if not user_answers.get("caste_community") or \
           user_answers.get("caste_community") == "Prefer not to say":
            return get_next_question(user_answers, next_q)  # Skip to C24
    
    # E34: Show only if NRI
    if next_q == 34:
        if user_answers.get("residency_type") == "Indian citizen (in India)":
            return get_next_question(user_answers, next_q)  # Skip to E35
    
    # I67: Show only if children_intent ≠ "Definitely not"
    if next_q == 67:
        if user_answers.get("children_intent") == "Definitely not":
            return get_next_question(user_answers, next_q)  # Skip to I68
    
    return next_q
```

---

## 🎮 BUTTON HANDLER PATTERNS

### Pattern 1: Simple Single-Select
**Example:** A1 (Gender Identity)

```python
@dp.callback_query_handler(lambda c: c.data.startswith('q1_'))
async def handle_gender_identity(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    answer = callback_query.data.replace('q1_', '')  # "male", "female", "nonbinary"
    
    # Map callback data to DB value
    value_map = {
        'male': 'Male',
        'female': 'Female',
        'nonbinary': 'Non-binary'
    }
    
    # Store answer
    session = get_session(user_id)
    session['answers']['gender_identity'] = value_map[answer]
    save_session(session)
    
    # Ack the button press
    await callback_query.answer()
    
    # Move to next question
    next_q = get_next_question(session['answers'], current_question=1)
    await ask_question(callback_query.message.chat.id, next_q, session)
```

**Button Generation:**
```python
def generate_buttons_q1():
    keyboard = [
        [InlineKeyboardButton("👨 Male", callback_data="q1_male")],
        [InlineKeyboardButton("👩 Female", callback_data="q1_female")],
        [InlineKeyboardButton("⚧️ Non-binary", callback_data="q1_nonbinary")],
        [InlineKeyboardButton("💬 Self-describe →", callback_data="q1_custom")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
```

---

### Pattern 2: Multi-Select (Checkbox Style)
**Example:** C26 (Languages Spoken)

```python
@dp.callback_query_handler(lambda c: c.data.startswith('q26_'))
async def handle_languages_spoken(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = get_session(user_id)
    
    # Initialize multi-select buffer if first tap
    if 'languages_spoken' not in session['multi_select_buffer']:
        session['multi_select_buffer']['languages_spoken'] = []
    
    selected = session['multi_select_buffer']['languages_spoken']
    
    # Toggle selection
    lang = callback_query.data.replace('q26_', '')
    if lang == 'done':
        # User clicked "Done" — finalize answer
        session['answers']['languages_spoken'] = selected
        session['multi_select_buffer'].pop('languages_spoken', None)
        save_session(session)
        
        await callback_query.answer("✓ Languages saved")
        next_q = get_next_question(session['answers'], current_question=26)
        await ask_question(callback_query.message.chat.id, next_q, session)
    else:
        # Toggle language in/out of selection
        if lang in selected:
            selected.remove(lang)
        else:
            selected.append(lang)
        
        # Update button UI to show checkmarks
        await callback_query.answer(f"{'✓ Added' if lang in selected else '✗ Removed'} {lang}")
        
        # Re-render buttons with updated checkmarks
        keyboard = generate_buttons_q26(selected)
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
```

**Button Generation (with checkmarks):**
```python
def generate_buttons_q26(selected: list):
    languages = ["Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", 
                 "Bengali", "Marathi", "Gujarati", "Punjabi", "English"]
    
    keyboard = []
    for lang in languages:
        check = "✓ " if lang in selected else ""
        keyboard.append([InlineKeyboardButton(
            f"{check}{lang}", 
            callback_data=f"q26_{lang}"
        )])
    
    # Add "Done" button at bottom
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="q26_done")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
```

---

### Pattern 3: Two-Step Sequential
**Example:** H56 (Partner Age Range — Min then Max)

```python
@dp.callback_query_handler(lambda c: c.data.startswith('q56_'))
async def handle_partner_age_range(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = get_session(user_id)
    
    value = callback_query.data.replace('q56_', '')
    
    # Step 1: Collecting min age
    if 'pref_age_min' not in session['answers']:
        session['answers']['pref_age_min'] = int(value)
        save_session(session)
        await callback_query.answer()
        
        # Ask for max age
        await ask_question_h56_step2(callback_query.message.chat.id, session)
    
    # Step 2: Collecting max age
    else:
        session['answers']['pref_age_max'] = int(value)
        
        # Combine into JSONB object for DB
        session['answers']['pref_age_range'] = {
            'min': session['answers']['pref_age_min'],
            'max': session['answers']['pref_age_max']
        }
        
        # Clean up temp fields
        session['answers'].pop('pref_age_min', None)
        session['answers'].pop('pref_age_max', None)
        
        save_session(session)
        await callback_query.answer()
        
        next_q = get_next_question(session['answers'], current_question=56)
        await ask_question(callback_query.message.chat.id, next_q, session)
```

---

### Pattern 4: Dynamic Conditional Dropdown
**Example:** C21 (Sect/Denomination — changes based on religion)

```python
def generate_buttons_q21(religion: str):
    """Generate sect options based on user's religion from Q18."""
    
    if religion == "Hindu":
        options = ["Shaivite", "Vaishnavite", "Arya Samaj", "Smartha", 
                   "None", "Prefer not to say"]
    elif religion == "Muslim":
        options = ["Sunni", "Shia", "Sufi", "Ahmadiyya", 
                   "None", "Prefer not to say"]
    elif religion == "Christian":
        options = ["Catholic", "Protestant", "Orthodox", "Evangelical", "Other"]
    elif religion == "Sikh":
        options = ["Amritdhari", "Keshdhari", "Sehajdhari", "None"]
    elif religion == "Jain":
        options = ["Digambar", "Shwetambar", "None"]
    else:
        # For Buddhist, Parsi, Jewish, Atheist, etc. → skip this question
        return None
    
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"q21_{opt.lower().replace(' ', '_')}")] 
                for opt in options]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('q21_'))
async def handle_sect_denomination(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    session = get_session(user_id)
    
    answer = callback_query.data.replace('q21_', '').replace('_', ' ').title()
    session['answers']['sect_denomination'] = answer
    save_session(session)
    
    await callback_query.answer()
    next_q = get_next_question(session['answers'], current_question=21)
    await ask_question(callback_query.message.chat.id, next_q, session)
```

---

### Pattern 5: Text Input (Free-Form)
**Example:** A3 (Date of Birth)

```python
@dp.message_handler(state=OnboardingState.SECTION_A, 
                   content_types=['text'])
async def handle_text_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    session = get_session(user_id)
    
    current_q = session['current_question']
    
    if current_q == 3:  # Date of birth
        # Validate format
        try:
            dob = datetime.strptime(message.text, "%d/%m/%Y")
            age = calculate_age(dob)
            
            if age < 18 or age > 80:
                await message.reply("Age must be between 18 and 80. Please try again:")
                return
            
            session['answers']['date_of_birth'] = dob.isoformat()
            save_session(session)
            
            await message.reply(f"{age} — got it ✓")
            
            next_q = get_next_question(session['answers'], current_question=3)
            await ask_question(message.chat.id, next_q, session)
        
        except ValueError:
            await message.reply("Invalid format. Please use DD/MM/YYYY (e.g., 15/03/1995):")
            return
```

---

## 🗄️ DATABASE SCHEMA MAPPINGS

### Field → Table Mapping

| Question # | Field Name | Storage Location | Type | Indexed |
|------------|------------|-----------------|------|---------|
| 1 | gender_identity | users.gender_identity | VARCHAR | ✓ |
| 2 | looking_for_gender | users.looking_for_gender | VARCHAR | ✓ |
| 3 | date_of_birth | users.date_of_birth | DATE | ✓ |
| 4 | marital_status | users.marital_status | VARCHAR | ✓ |
| 5 | children_existing | users.children_existing | VARCHAR | |
| 6 | height_cm | users.height_cm | INT | |
| 7 | body_type | users.body_type | VARCHAR | |
| 8 | complexion | users.complexion | VARCHAR | |
| 9 | disability_status | users.disability_status | VARCHAR | |
| 10 | residency_type | users.residency_type | VARCHAR | ✓ |
| 11 | country_current | users.country_current | VARCHAR | ✓ |
| 12 | state_india | users.state_india | VARCHAR | |
| 13 | city_current | users.city_current | VARCHAR | |
| 14 | hometown_state | users.hometown_state | VARCHAR | |
| 15 | willing_to_relocate | users.willing_to_relocate | VARCHAR | |
| 16 | partner_location_pref | preferences.partner_location_pref | JSONB | |
| 17 | settling_country | users.settling_country | VARCHAR | |
| 18 | religion | users.religion | VARCHAR | ✓ |
| 19 | religious_practice | users.religious_practice | VARCHAR | |
| 20 | partner_religion_pref | preferences.partner_religion_pref | JSONB | |
| 21 | sect_denomination | users.sect_denomination | VARCHAR | |
| 22 | caste_community | users.caste_community | VARCHAR | ✓ |
| 23 | sub_caste | users.sub_caste | VARCHAR | |
| 24 | caste_importance | preferences.caste_importance | JSONB | |
| 25 | mother_tongue | users.mother_tongue | VARCHAR | |
| 26 | languages_spoken | users.languages_spoken | ARRAY | |
| 27 | manglik_status | users.manglik_status | VARCHAR | |
| 28 | education_level | users.education_level | VARCHAR | |
| 29 | education_institute_tier | users.education_institute_tier | VARCHAR | |
| 30 | employment_status | users.employment_status | VARCHAR | |
| 31 | work_industry | users.work_industry | VARCHAR | |
| 32 | career_ambition | personality.career_ambition | JSONB | |
| 33 | annual_income | users.annual_income | VARCHAR (PRIVATE) | |
| 34 | income_currency | users.income_currency | VARCHAR (PRIVATE) | |
| 35 | net_worth_range | users.net_worth_range | VARCHAR (PRIVATE) | |
| 36 | property_ownership | users.property_ownership | VARCHAR (PRIVATE) | |
| 37 | financial_dependents | users.financial_dependents | VARCHAR (PRIVATE) | |
| 38 | family_type | users.family_type | VARCHAR | |
| 39 | family_financial_status | users.family_financial_status | VARCHAR | |
| 40 | father_occupation | users.father_occupation | VARCHAR | |
| 41 | family_values | personality.family_values | JSONB | |
| 42 | living_with_parents_post_marriage | users.living_with_parents_post_marriage | VARCHAR | |
| 43 | family_involvement_search | users.family_involvement_search | VARCHAR | |
| 44 | siblings | users.siblings | VARCHAR | |
| 45 | diet | users.diet | VARCHAR | ✓ |
| 46 | partner_diet_pref | preferences.partner_diet_pref | JSONB | |
| 47 | smoking | users.smoking | VARCHAR | ✓ |
| 48 | smoking_partner_ok | preferences.smoking_partner_ok | JSONB | |
| 49 | drinking | users.drinking | VARCHAR | ✓ |
| 50 | drinking_partner_ok | preferences.drinking_partner_ok | JSONB | |
| 51 | fitness_frequency | personality.fitness_frequency | JSONB | |
| 52 | social_style | personality.social_style | JSONB | |
| 53 | weekend_style | personality.weekend_style | JSONB | |
| 54 | pet_ownership | users.pet_ownership | VARCHAR | |
| 55 | sleep_schedule | personality.sleep_schedule | JSONB | |
| 56 | pref_age_range | preferences.pref_age_range | JSONB | |
| 57 | pref_height | preferences.pref_height | JSONB | |
| 58 | pref_complexion | preferences.pref_complexion | JSONB | |
| 59 | pref_education_min | preferences.pref_education_min | JSONB | |
| 60 | pref_income_range | preferences.pref_income_range | JSONB | |
| 61 | pref_marital_status | preferences.pref_marital_status | JSONB | |
| 62 | pref_children_ok | preferences.pref_children_ok | JSONB | |
| 63 | pref_disability_ok | preferences.pref_disability_ok | JSONB | |
| 64 | pref_working_spouse | preferences.pref_working_spouse | JSONB | |
| 65 | relationship_intent | users.relationship_intent | VARCHAR | ✓ |
| 66 | children_intent | users.children_intent | VARCHAR | ✓ |
| 67 | children_timeline | users.children_timeline | VARCHAR | |
| 68 | gender_roles_household | personality.gender_roles_household | JSONB | |
| 69 | financial_management | personality.financial_management | JSONB | |
| 70 | political_leaning | personality.political_leaning | JSONB | |
| 71 | astrology_belief | users.astrology_belief | VARCHAR | |
| 72 | interfaith_intercaste_openness | users.interfaith_intercaste_openness | VARCHAR | |
| 73 | db_divorced_ok | preferences.db_divorced_ok | BOOLEAN | |
| 74 | db_widowed_ok | preferences.db_widowed_ok | BOOLEAN | |
| 75 | db_children_ok | preferences.db_children_ok | BOOLEAN | |
| 76 | db_nri_ok | preferences.db_nri_ok | VARCHAR | |
| 77 | db_age_gap_max | preferences.db_age_gap_max | VARCHAR | |

---

## ✅ VALIDATION RULES

| Field | Validation | Error Message |
|-------|------------|---------------|
| date_of_birth | Age 18-80 | "Age must be between 18 and 80." |
| date_of_birth | Valid date format | "Invalid format. Use DD/MM/YYYY (e.g., 15/03/1995)" |
| height_cm | 140-220 cm | "Height must be between 140cm and 220cm." |
| pref_age_max | Must be ≥ pref_age_min | "Max age must be greater than or equal to min age." |
| photo | Min 1 photo | "You need at least one photo to continue." |
| photo | Image format (JPG/PNG) | "Please send a valid image (JPG or PNG)." |
| photo | Max file size 10MB | "Image too large. Max 10MB." |
| languages_spoken | At least 1 selected | "Please select at least one language." |

---

## 🔄 SAVE & RESUME LOGIC

### Scenario 1: User Exits Mid-Flow
```python
# Save current state to DB
def save_checkpoint(user_id: int, session: dict):
    supabase.table('conversation_state').upsert({
        'user_id': user_id,
        'state': session['current_state'],
        'current_question': session['current_question'],
        'answers': json.dumps(session['answers']),
        'skip_questions': session['skip_questions'],
        'last_active': datetime.utcnow().isoformat()
    }).execute()
```

### Scenario 2: User Returns After Exiting
```python
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    user_id = message.from_user.id
    
    # Check if user has an incomplete onboarding
    checkpoint = supabase.table('conversation_state')\
        .select('*')\
        .eq('user_id', user_id)\
        .single()\
        .execute()
    
    if checkpoint.data and checkpoint.data['current_question'] < 77:
        # Resume from where they left off
        await message.reply(
            f"Hey! We were getting through the quick questions — "
            f"want to pick up where we left off?\n\n"
            f"Progress: {checkpoint.data['current_question']}/77"
        )
        
        keyboard = [
            [InlineKeyboardButton("✓ Resume", callback_data="resume_onboarding")],
            [InlineKeyboardButton("⟲ Start over", callback_data="restart_onboarding")]
        ]
        await message.reply("What would you like to do?", 
                          reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    else:
        # Fresh start
        await show_intro_message_1(message)
```

---

## 🧪 TESTING CHECKLIST

### Unit Tests
- [ ] `get_next_question()` correctly skips conditional questions
- [ ] Multi-select buffer adds/removes items correctly
- [ ] Two-step questions store both values before proceeding
- [ ] Date validation catches invalid formats and out-of-range ages
- [ ] Dynamic dropdown generates correct options for each religion

### Integration Tests
- [ ] **Path 1: Hindu, never married, India**
  - Questions shown: 1-4, 6-9, 10, 12-16, 18-27, 28-77
  - Questions skipped: 5 (children_existing), 11 (country_current), 17 (settling_country), 34 (income_currency)
  - Total: 75 questions
  
- [ ] **Path 2: Muslim, never married, India**
  - Questions shown: 1-4, 6-9, 10, 12-21, 25-26, 28-77
  - Questions skipped: 5, 11, 17, 22-24 (caste), 27 (manglik), 34
  - Total: 71 questions
  
- [ ] **Path 3: NRI Hindu, never married, abroad**
  - Questions shown: 1-4, 6-9, 10-11, 13-16, 17-27, 28-33, 34-77
  - Questions skipped: 5, 12 (state_india)
  - Total: 75 questions
  
- [ ] **Path 4: Divorced Hindu, has children, India**
  - Questions shown: 1-9, 10, 12-16, 18-27, 28-77
  - Questions skipped: 11, 17, 34
  - Total: 76 questions

### End-to-End Tests
- [ ] Complete onboarding start-to-finish (all 77 Qs)
- [ ] Save & resume: Exit at Q30, return, verify resume from Q30
- [ ] Photo upload: Upload 1 photo, then 2 more, verify all saved
- [ ] Summary screen: Verify all answers displayed correctly
- [ ] Transition to conversational mode works
- [ ] All data written to correct DB tables/columns

### Error Handling Tests
- [ ] User sends text when button expected → Reply: "Just tap one of the options above 👆"
- [ ] User sends sticker/GIF during buttons → Reply: "😄 Save that energy — just tap a button for now"
- [ ] User goes idle >24 hours → Send resume prompt on next /start
- [ ] Network error during DB write → Retry 3x, then show error message
- [ ] Photo upload fails → Allow retry without losing progress

---

## 📦 DELIVERABLES CHECKLIST

### Code
- [ ] `bot.py` — Main bot entry point
- [ ] `handlers/onboarding.py` — Button + text handlers for Q1-Q77
- [ ] `handlers/photo.py` — Photo upload handler
- [ ] `utils/conditional_logic.py` — `get_next_question()` router
- [ ] `utils/button_generators.py` — All button generation functions
- [ ] `utils/validation.py` — Input validation functions
- [ ] `utils/db.py` — Supabase write functions
- [ ] `config.py` — Button text, options, field mappings (data-driven)

### Tests
- [ ] `tests/test_conditional_logic.py` — Unit tests for router
- [ ] `tests/test_button_generators.py` — Button generation tests
- [ ] `tests/test_validation.py` — Input validation tests
- [ ] `tests/test_onboarding_paths.py` — Integration tests for 4 user paths

### Documentation
- [ ] `README.md` — Setup instructions, deployment steps
- [ ] `CONDITIONAL_LOGIC.md` — Visual flowchart of all branches
- [ ] `BUTTON_CONFIG.md` — Reference for all button options

### Deployment
- [ ] Deploy to Fly.io
- [ ] Test with 5 real users (different religions, NRI vs India)
- [ ] Monitor logs for errors
- [ ] Report completion to Seema

---

## 🚨 CRITICAL NOTES

1. **Don't hardcode button options** — Use `config.py` so we can tweak text without code changes
2. **Privacy fields (E33-E37)** — Mark as PRIVATE in DB, never show to matches
3. **Multi-select UX** — Show checkmarks (✓) next to selected items, "✅ Done" button at bottom
4. **Save frequently** — Write to DB after every answer (not just at end)
5. **Error recovery** — If DB write fails, cache answer in session and retry on next answer
6. **No LLM calls** — Button phase is $0.00, keep it that way

---

## 🎯 SUCCESS CRITERIA

**Done when:**
1. All 77 questions flow correctly with conditional branching
2. All 4 user paths tested end-to-end (Hindu/Muslim/NRI/Divorced)
3. Save & resume works reliably
4. All data written to correct DB tables
5. Photo upload functional
6. Deployed to Fly.io and tested with 5 real users
7. Zero crashes or data loss during testing

**Ping Seema when:**
- You hit any blockers
- Conditional logic is unclear
- Button options need tweaking
- Ready for final review before deployment

---

**Good luck, Blitz! You got this. 💪**

—Seema
