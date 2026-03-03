# Telegram Interactive Onboarding — Capabilities & Design

**Goal:** Use Telegram inline buttons for fast, tap-friendly Tier 1 data collection

**Date:** 2026-02-12

---

## What Telegram Supports

### 1. **Inline Keyboards** ✅ (Already using for matches)

**What they are:**
- Buttons attached to a message
- User taps → callback sent to bot
- Can have multiple rows/columns
- Stay visible after tap (can be updated or removed)

**Example:**
```
Bot: "What's your gender?"
[Male] [Female] [Non-binary] [Prefer not to say]
```

**Code:**
```python
keyboard = [
    [
        InlineKeyboardButton("Male", callback_data="gender_male"),
        InlineKeyboardButton("Female", callback_data="gender_female")
    ],
    [
        InlineKeyboardButton("Non-binary", callback_data="gender_nonbinary"),
        InlineKeyboardButton("Prefer not to say", callback_data="gender_skip")
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("What's your gender?", reply_markup=reply_markup)
```

**Conditional flow:** ✅ YES
```python
async def handle_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge
    
    if query.data == "gender_male":
        # Ask next question based on gender
        keyboard = [[...]]  # Different buttons
        await query.edit_message_text("Great! Are you looking for:")
        # Show orientation options
    elif query.data == "gender_female":
        # Same next question, different flow possible
```

---

### 2. **Reply Keyboards** ✅ (Like WhatsApp quick replies)

**What they are:**
- Buttons appear above the keyboard
- User taps → sends text message
- Replace user's keyboard until dismissed

**Example:**
```
Bot: "Do you want children?"
[Yes, someday] [No] [Already have kids] [Not sure]
```

**Code:**
```python
from telegram import ReplyKeyboardMarkup, KeyboardButton

keyboard = [
    [KeyboardButton("Yes, someday"), KeyboardButton("No")],
    [KeyboardButton("Already have kids"), KeyboardButton("Not sure")]
]
reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
await update.message.reply_text("Do you want children?", reply_markup=reply_markup)
```

**Difference from Inline:**
- Sends actual text message (not callback)
- Keyboard disappears after tap (if `one_time_keyboard=True`)
- Better for longer text options

---

### 3. **Date Pickers** ❌ (NOT built-in, but can build)

**What Telegram has:**
- No native date picker widget

**What we CAN do:**
- Build custom date picker with inline buttons

**Example:**
```
Bot: "When were you born? Select month:"
[Jan] [Feb] [Mar]
[Apr] [May] [Jun]
[Jul] [Aug] [Sep]
[Oct] [Nov] [Dec]

→ User taps [Jun]

Bot updates message: "Select day:"
[1-10] [11-20] [21-31]

→ User taps [21-31]

Bot updates: "Which day?"
[21] [22] [23] [24] [25]
[26] [27] [28] [29] [30]

→ User taps [25]

Bot updates: "Select year:"
[1985-1989] [1990-1994] [1995-1999] [2000-2004]

→ User taps [1990-1994]

Bot updates: "Which year?"
[1990] [1991] [1992] [1993] [1994]

→ User taps [1992]

Bot: "Got it! June 25, 1992. Confirm?"
[✓ Yes, that's right] [✗ Start over]
```

**OR simpler:**
```
Bot: "Enter your birth year (e.g., 1992):"
User types: 1992

Bot: "Enter your birth month (1-12):"
User types: 6

Bot: "Enter day (1-31):"
User types: 25

Bot: "Got it! June 25, 1992. Confirm?"
[✓ Confirm] [✗ Redo]
```

**Recommendation:** Use text input for dates (simpler, faster)

---

### 4. **Text Input** ✅ (Always available)

**For:** Name, alias, occupation, city, etc.

**Flow:**
```
Bot: "What's your full name?"
User types: Nikunj Vora

Bot: "What should I call you? (nickname/alias)"
User types: Nik

Bot: "Got it, Nik! What city are you in?"
User types: Sydney
```

**Can mix with buttons:**
```
Bot: "What city are you in?"
[Mumbai] [Delhi] [Bangalore] [Sydney] [Dubai]
[Other (type it)]

→ If user taps [Other], bot prompts: "Type your city:"
```

---

### 5. **Multi-Select** ❌ (NOT built-in, but can fake)

**What Telegram has:**
- No native multi-select checkbox UI

**What we CAN do:**
- Use inline buttons that toggle on/off

**Example:**
```
Bot: "What languages do you speak? (Tap all that apply, then tap Done)"
[ ] Gujarati
[ ] Hindi
[ ] English
[ ] Marathi
[✓ Done]

→ User taps [Gujarati]

Bot updates message:
[✓] Gujarati  ← now checked
[ ] Hindi
[ ] English
[ ] Marathi
[✓ Done]

→ User taps [English]

Bot updates:
[✓] Gujarati
[ ] Hindi
[✓] English  ← now checked
[ ] Marathi
[✓ Done]

→ User taps [Done]

Bot: "Got it! You speak Gujarati and English."
```

**Code pattern:**
```python
# Store state in callback_data or context
callback_data = f"lang_toggle_gujarati_{user_id}"

# Track selected languages in user context
context.user_data['selected_languages'] = set()

# On each tap, toggle and redraw buttons
if lang in context.user_data['selected_languages']:
    context.user_data['selected_languages'].remove(lang)
else:
    context.user_data['selected_languages'].add(lang)

# Redraw keyboard with checkmarks
```

---

## Answering Your Questions

### 1. **Can we do conditional flow?**

✅ **YES** — Full control

```python
async def handle_gender_selection(update, context):
    query = update.callback_query
    gender = query.data.replace("gender_", "")
    
    # Save to DB
    db.update_user_hard_filters(user_id, {"gender_identity": gender})
    
    # Conditional next question
    if gender == "male":
        keyboard = [
            [InlineKeyboardButton("Women", callback_data="orientation_hetero")],
            [InlineKeyboardButton("Men", callback_data="orientation_gay")],
            [InlineKeyboardButton("Everyone", callback_data="orientation_bi")]
        ]
        await query.edit_message_text("Who are you interested in?", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif gender == "female":
        keyboard = [
            [InlineKeyboardButton("Men", callback_data="orientation_hetero")],
            [InlineKeyboardButton("Women", callback_data="orientation_gay")],
            [InlineKeyboardButton("Everyone", callback_data="orientation_bi")]
        ]
        await query.edit_message_text("Who are you interested in?", reply_markup=InlineKeyboardMarkup(keyboard))
```

---

### 2. **Can we invoke buttons at any time based on data/flag?**

✅ **YES** — Anytime, based on anything

**Scenarios:**

**A) Progress-based:**
```python
# User completed Tier 1, show next step
if tier1_completion == 100:
    keyboard = [[InlineKeyboardButton("Let's go! 🚀", callback_data="start_tier2")]]
    await bot.send_message(chat_id, "Your basics are complete! Ready for the next step?", 
                          reply_markup=InlineKeyboardMarkup(keyboard))
```

**B) Data-based:**
```python
# User said they want kids, ask about partner's kids
if user.children_intent == "want":
    keyboard = [
        [InlineKeyboardButton("Yes, that's fine", callback_data="partner_kids_ok")],
        [InlineKeyboardButton("Prefer no existing kids", callback_data="partner_kids_no")]
    ]
    await bot.send_message(chat_id, "Would you be open to a partner who already has kids?",
                          reply_markup=InlineKeyboardMarkup(keyboard))
```

**C) Time-based:**
```python
# User inactive for 24h, send nudge with button
if hours_since_last_message > 24:
    keyboard = [[InlineKeyboardButton("Continue my profile", callback_data="resume_onboarding")]]
    await bot.send_message(chat_id, "Still here! Want to finish your profile?",
                          reply_markup=InlineKeyboardMarkup(keyboard))
```

**D) Error recovery:**
```python
# User typed invalid city, offer suggestions
keyboard = [
    [InlineKeyboardButton("Mumbai", callback_data="city_mumbai")],
    [InlineKeyboardButton("Try again", callback_data="city_retry")]
]
await bot.send_message(chat_id, "Hmm, I didn't catch that. Did you mean:",
                      reply_markup=InlineKeyboardMarkup(keyboard))
```

---

### 3. **Only buttons? Or mix with text input?**

✅ **MIX is best** — Use buttons for structured, text for open-ended

**Recommended flow:**

**Buttons for:**
- Gender, orientation, religion (fixed options)
- Yes/No questions (children, smoking, drinking)
- Multiple choice (relationship intent, timeline)
- Common cities (top 10-20, then "Other")
- Common occupations (Engineer, Doctor, etc., then "Other")

**Text input for:**
- Name, alias (unique)
- City (if "Other" selected)
- Occupation (if "Other")
- Age/DOB (typing "1992" is faster than button drill-down)
- Open-ended (lifestyle, preferences)

**Example hybrid flow:**
```
Bot: "What's your name?"
→ User types: Nikunj

Bot: "What should I call you?"
→ User types: Nik

Bot: "Where are you, Nik?"
[Mumbai] [Delhi] [Bangalore] [Sydney] [Dubai] [Other]
→ User taps: [Sydney]

Bot: "What's your gender?"
[Male] [Female] [Non-binary]
→ User taps: [Male]

Bot: "Who are you looking for?"
[Women] [Men] [Everyone]
→ User taps: [Women]

Bot: "How old are you? (Just type the number)"
→ User types: 32

Bot: "What's your religion?"
[Hindu] [Muslim] [Christian] [Sikh] [Jewish] [No religion] [Other]
→ User taps: [Hindu]

Bot: "How important is it that your partner shares your faith?"
[Must match] [Prefer to match] [Open to others] [Not important]
→ User taps: [Prefer to match]

Bot: "Do you want children?"
[Yes, someday] [No] [Already have kids] [Not sure]
→ User taps: [Yes, someday]

Bot: "Great! You're 40% done. What do you do for work?"
→ User types: Product manager at a fintech startup
```

---

## Sample Onboarding Flow Design

### **Session 1: Basics (Tier 1) — 5-7 minutes**

```
1. Bot: "Hey! I'm Jodi 👋 Let's get to know you. What's your name?"
   → User types: Nikunj Vora

2. Bot: "Nice to meet you, Nikunj! What should I call you?"
   → User types: Nik

3. Bot: "Where are you, Nik?"
   [Mumbai] [Delhi] [Bangalore] [Dubai] [Sydney] [London] [Other]
   → Tap: [Sydney]

4. Bot: "What's your gender?"
   [Male] [Female] [Non-binary]
   → Tap: [Male]

5. Bot: "Who are you interested in?"
   [Women] [Men] [Everyone]
   → Tap: [Women]

6. Bot: "How old are you? (Just the number)"
   → Type: 32

7. Bot: "What's your religion?"
   [Hindu] [Muslim] [Christian] [Sikh] [Buddhist] [Jewish] [No religion] [Other]
   → Tap: [Hindu]

8. Bot: "How important is your partner's religion to you?"
   [Must match mine] [Prefer to match] [Open to others] [Not important]
   → Tap: [Prefer to match]

9. Bot: "Do you want children?"
   [Yes, someday] [No] [Already have kids] [Not sure]
   → Tap: [Yes, someday]

10. Bot: "Are you a smoker?"
    [No] [Socially] [Regularly] [Quit recently]
    → Tap: [No]

11. Bot: "How about drinking?"
    [No] [Socially] [Regularly] [Prefer not to say]
    → Tap: [Socially]

12. Bot: "What do you do for work?"
    → Type: Product manager at a fintech startup

13. Bot: "Last question — what are you looking for here?"
    [Marriage] [Long-term relationship] [Dating to see where it goes]
    → Tap: [Marriage]

14. Bot: "Perfect! You're all set up, Nik 🎉
    
    Your profile is 60% complete. The more I know, the better your matches.
    
    Want to keep going, or take a break?"
    [Keep going! 🚀] [I'll finish later]
```

---

## Technical Implementation

### State Machine Approach

```python
# Track onboarding state
class OnboardingState:
    WAITING_NAME = "waiting_name"
    WAITING_ALIAS = "waiting_alias"
    WAITING_CITY = "waiting_city"
    WAITING_GENDER = "waiting_gender"
    # ... etc
    COMPLETE = "complete"

# Store in DB or context
context.user_data['onboarding_state'] = OnboardingState.WAITING_NAME

# Message handler checks state
async def handle_message(update, context):
    state = context.user_data.get('onboarding_state')
    
    if state == OnboardingState.WAITING_NAME:
        # Save name, move to alias
        save_name(update.message.text)
        context.user_data['onboarding_state'] = OnboardingState.WAITING_ALIAS
        await ask_alias(update, context)
    
    elif state == OnboardingState.WAITING_ALIAS:
        # Save alias, show city buttons
        save_alias(update.message.text)
        context.user_data['onboarding_state'] = OnboardingState.WAITING_CITY
        await show_city_buttons(update, context)
```

### Button Callback Handler

```python
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge
    
    data = query.data
    
    # Parse callback_data
    if data.startswith("city_"):
        city = data.replace("city_", "")
        if city == "other":
            # Prompt for text input
            await query.edit_message_text("Type your city:")
            context.user_data['onboarding_state'] = OnboardingState.WAITING_CITY_TEXT
        else:
            # Save city, move to gender
            save_city(city)
            await show_gender_buttons(query, context)
    
    elif data.startswith("gender_"):
        gender = data.replace("gender_", "")
        save_gender(gender)
        await show_orientation_buttons(query, context)
    
    # ... etc
```

---

## Recommended Hybrid Approach

**Buttons for Tier 1 (Basics):**
- ✅ Gender, orientation, religion (3-4 options each)
- ✅ Yes/No questions (children, smoking, drinking)
- ✅ Common cities/occupations (with "Other" option)
- ✅ Relationship intent, timeline

**Text for Tier 1:**
- ✅ Name, alias
- ✅ Age/DOB (typing is faster)
- ✅ Occupation details

**Free-form chat for Tier 2+ (Ready, Deep):**
- Let user talk naturally
- Bot extracts signals
- Optionally show buttons for clarification ("Did you mean...?")

---

## Benefits

1. **Speed:** Tap 10 buttons in 60 seconds vs typing 10 answers
2. **Data quality:** Structured options = clean data (no typos, no "Mumabi")
3. **Engagement:** Interactive feels like a game, not a form
4. **Lower drop-off:** Seeing progress (8/15 questions) keeps users going
5. **Mobile-first:** Tapping >>> typing on phones

---

## Next Steps

Want me to:
1. **Build prototype flow** — Map out all Tier 1 questions with buttons
2. **Implement in bot.py** — Add button handlers + state machine
3. **Test it** — Deploy and you try it on Telegram
4. **Add to backlog** — Park for later

Which one?
