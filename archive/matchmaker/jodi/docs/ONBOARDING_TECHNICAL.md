# Jodi — Onboarding Technical Summary

This document describes the current user onboarding technical flow for the Jodi Telegram matchmaker bot.

1) What happens when a user opens / starts the bot

- Entry point: bot.py (start handler)
- When a user sends /start the handler does:
  - db.create_user(user.id, user.username, user.first_name)
  - profile = db.get_profile(user.id)
  - If profile exists and profile completeness indicates profile is complete (db.get_user(...).get('profile_complete')) → sends a "welcome back" message listing commands (/matches, /update, /help).
  - Else (new user or incomplete profile):
    - conv_manager.get_welcome_message() is sent. (ConversationManager.get_welcome_message())
    - db.update_conversation_state(user.id, {"stage": "getting_to_know", "started_at": datetime.now().isoformat()})

Code excerpt (bot.py - start):

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        db.create_user(user.id, user.username, user.first_name)
        profile = db.get_profile(user.id)
        if profile and db.get_user(user.id).get('profile_complete'):
            await update.message.reply_text("Welcome back...")
        else:
            welcome_msg = conv_manager.get_welcome_message()
            await update.message.reply_text(welcome_msg)
            db.update_conversation_state(user.id, {"stage": "getting_to_know", "started_at": ...})

2) New user vs returning user detection

- create_user upserts into users table using telegram_id; it also updates last_active timestamp.
- get_profile(telegram_id) queries profiles joined by user
- Decision logic in start():
  - If profile exists AND db.get_user(user.id).get('profile_complete') is truthy → considered returning user with complete profile.
  - Otherwise treated as new or incomplete profile.

Notes:
- The Postgres adapter's get_conversation_state and update_conversation_state are placeholders (get_conversation_state currently returns {} and update_conversation_state is a no-op). Conversation state persistence is planned but not fully implemented in db_postgres.py.

3) Database interactions — what gets created / queried

Primary DB adapter: db_postgres.JodiDB (expects DATABASE_URL env var). Key functions used during onboarding and early conversation:

- create_user(telegram_id, username, first_name)
  - Inserts into users (telegram_id, email placeholder, created_at, last_active). ON CONFLICT updates last_active.

- get_user(telegram_id)
  - SELECT * FROM users WHERE telegram_id = %s

- get_profile(telegram_id) / get_profile_by_user_id(user_id)
  - SELECT * FROM profiles WHERE user_id = %s

- create_or_update_profile(telegram_id, profile_dict)
  - Looks up user -> upsert_profile(user_id, profile_dict)
  - upsert_profile builds dynamic UPDATE/INSERT for profiles table. Accepts a mixture of scalar columns and JSON columns (preferences, personality_data, media_signals), and embedding. It expects profile_dict keys like demographics, preferences etc. If no updatable columns present it returns existing profile.

- mark_profile_complete(telegram_id)
  - Updates profiles.completeness_score = 100 for the user

- record_interaction(user_id, direction, content, extracted_data=None, interaction_type=None)
  - Inserts into interactions table (for conversation history / audit)

- get_interactions(user_id, limit=100)

- create_match / get_matches_for_user / update_match_status — used after profile completion to store matches

Important: db_postgres implements nearest_profiles embedding search with Postgres <-> operator for vector similarity and raw_query helper.

Tables inferred from adapter methods (schema details):
- users: (id PK, telegram_id UNIQUE, email, created_at, last_active, ...)
- profiles: (id PK, user_id UNIQUE, display_name, dob, gender, location_text, religion, relationship_intent, smoking, drinking, wants_children, education_level, height_cm, completeness_score, preferences jsonb, personality_data jsonb, media_signals jsonb, embedding, created_at, updated_at, ...)
- interactions: (id PK, user_id FK, direction, content, extracted_data jsonb, interaction_type, created_at)
- matches: (id PK, user_a, user_b, match_score, score_breakdown jsonb, status, created_at)

(Exact CREATE TABLE statements are not in repository; schema is inferred from db adapter SQL.)

4) Memory / conversation context handling

- ConversationManager holds the logic for multi-session flows and uses Claude to generate questions and extract structured data.
- Conversation history is stored in the profile as conversation_history (list) passed around in bot.py and saved via db.create_or_update_profile(..., conversation_history=conv_history).
- However, db_postgres.upsert_profile does not currently map a "conversation_history" JSON column explicitly in its allowed_cols/json_cols list. The seed scripts and bot.py assume profiles have a conversation_history field (JSON). The adapter's upsert supports JSON columns named in json_cols = ['preferences', 'personality_data', 'media_signals'] — so conversation_history will not be saved unless the DB schema includes a column and upsert_profile is extended.
- There is also an interactions table and record_interaction() which can be used to persist each message (direction user/assistant). The code currently calls db.create_or_update_profile to save the conversation_history blob.
- get_conversation_state/update_conversation_state are placeholders — stage/state is currently tracked by writing a state dict in bot.py to db.update_conversation_state but that function is a no-op in Postgres adapter. So per-user stage persistence is partially implemented in application logic but not persisted in this adapter.

5) Anthropic API integration — how context is passed to Claude

- ConversationManager uses anthropic.Anthropic client (expects ANTHROPIC_API_KEY).
- get_next_question builds a prompt containing:
  - JSON dump of partial_profile
  - Recent conversation history (last ~6 messages)
  - Stage-specific instructions (templates in get_next_question)

- It then calls:
    response = self.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
  and returns response.content[0].text.strip()

- process_user_response similarly builds an extraction prompt containing the user's latest message and the current profile and asks Claude to return ONLY a JSON object with extracted demographics, preferences, signals, cultural_weight etc. It then parses JSON from the model response and merges into profile via _merge_profile.

Notes: Error handling falls back to hardcoded fallback questions if the Claude call fails.

6) Welcome messages / onboarding prompts in code

- ConversationManager.get_welcome_message(): long friendly multi-paragraph greeting explaining the conversational approach and prompting "tell me a bit about yourself".

- Stage-specific prompt templates in ConversationManager.get_next_question: there are templates for:
  - getting_to_know (asks about location, work, cultural background, family)
  - preferences_surface
  - preferences_deep
  - review_profile

- Fallback hard-coded questions exist in _get_fallback_question for each stage.

Additional implementation notes / gaps discovered

- Conversation state persistence is not fully implemented in db_postgres: get_conversation_state returns {} and update_conversation_state is a no-op. The bot relies on these for stage transitions.
- upsert_profile currently expects specific keys and JSON columns; bot.py calls create_or_update_profile with keyword parameters (demographics=..., preferences=..., conversation_history=...) — but create_or_update_profile in db_postgres signature expects (telegram_id, profile_dict) whereas bot.py passes different args. There is a mismatch between the older db.py (sqlite) API and db_postgres adapter. The seed_data.py imports db.JodiDB (sqlite) and calls create_or_update_profile with keyword args. This repository contains both styles: db_postgres (Postgres adapter) and seed_data.py + db.py (sqlite adapter) — confirm which is in use.

- Several places assume profile has keys like 'telegram_id' in profile rows returned from DB. db_postgres.get_profile (SELECT * FROM profiles WHERE user_id=...) returns columns of profiles table; it doesn't add telegram_id into that dict. The bot passes profiles around expecting telegram_id on the profile. That likely comes from the sqlite implementation (db.py) which may have returned denormalized results. These are integration inconsistencies to be addressed.

What I accomplished / found

- Located and analyzed bot.py, conversation.py, db_postgres.py, matching.py, seed_data.py and README.
- Documented the onboarding flow for /start and message handling.
- Identified how new vs returning users are detected.
- Listed database operations used during onboarding and inferred schema.
- Explained conversation memory usage and shortcomings in persistence implementation.
- Documented Anthropic (Claude) integration including prompt construction and JSON extraction flow.
- Collected code snippets and highlighted integration mismatches (db API differences and missing conversation_state persistence).

Next recommended actions (short):
- Align DB adapter API and parameters: ensure create_or_update_profile signature is consistent between bot.py/seed_data.py and db_postgres.
- Persist conversation state: implement conversation_state column in users or profiles and update get_conversation_state/update_conversation_state.
- Ensure upsert_profile supports conversation_history column (add to json_cols list) or use interactions table for message-level persistence and simple profile JSON for summary.
- Add telegram_id into profile rows returned by JodiDB.get_profile (or join users->profiles) so downstream code that expects profile['telegram_id'] works.

Saved file: matchmaker/jodi/docs/ONBOARDING_TECHNICAL.md

If you want, I can also open PR-style patches to db_postgres.py to fix the interface mismatches and add conversation_state persistence.