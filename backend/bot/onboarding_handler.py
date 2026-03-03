"""
Masii Telegram Onboarding Flow Handler — The 36 Gunas
Handles the intro sequence, proxy flow, 36-guna questions with tree branching,
sub-questions, location tree, and section transitions.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import (
    INTRO_MESSAGES,
    INTENT_MESSAGE,
    PROXY_MESSAGES,
    PROXY_NO_CONSENT_MESSAGE,
    QUESTIONS,
    SUB_QUESTIONS,
    SECTION_TRANSITIONS,
    CLOSE_MESSAGE,
    ERROR_MESSAGES,
    RESUME_PROMPT,
    RESUME_BUTTONS,
    TOTAL_GUNAS,
    VALIDATION_RULES,
    get_birth_years,
    get_countries,
    get_states_india,
)
from conditional_logic import (
    get_next_question,
    should_skip_question,
    should_ask_sub_question,
    get_conditional_options,
    get_section_for_question,
    get_completion_percentage,
    get_transition_key,
)
from validation import validate_input
from db_adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


class OnboardingHandler:
    """Manages the 36-guna onboarding flow"""

    def __init__(self, db_adapter: DatabaseAdapter):
        self.db = db_adapter
        self.dynamic_options = {
            "birth_years": get_birth_years(),
            "countries": get_countries(),
            "states_india": get_states_india(),
        }

    # ================================================================
    # ENTRY POINT
    # ================================================================

    async def start_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Entry point: /start command"""
        user = update.effective_user
        telegram_id = user.id

        # Check for existing progress
        session = self.db.get_session(telegram_id)

        if session and session.get("current_question", 0) > 0 and session.get("current_question", 0) <= TOTAL_GUNAS:
            await self._show_resume_prompt(update, context, session)
        else:
            await self._start_intro(update, context, telegram_id, user)

    # ================================================================
    # INTRO SEQUENCE (Messages 1-3 → Intent → Proxy)
    # ================================================================

    async def _start_intro(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                           telegram_id: int, user: Any):
        """Start the intro sequence"""
        session = {
            "user_id": telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "current_section": "intro",
            "current_question": 0,
            "intro_index": 0,
            "answers": {},
            "skip_questions": [],
            "asked_questions": [],
            "multi_select_buffer": {},
            "location_buffer": {},
            "proxy": None,
            "started_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
        }
        self.db.save_session(session)
        await self._show_intro_message(update.message.chat.id, context, 0, telegram_id)

    async def _show_intro_message(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                  index: int, telegram_id: int):
        """Show intro message with 'next' button"""
        if index >= len(INTRO_MESSAGES):
            # Intro messages done → show intent question
            await self._show_intent_question(chat_id, context, telegram_id)
            return

        intro = INTRO_MESSAGES[index]
        keyboard = [[InlineKeyboardButton(
            intro["button"],
            callback_data=f"intro_next_{index}"
        )]]

        await context.bot.send_message(
            chat_id=chat_id,
            text=intro["text"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _show_intent_question(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                    telegram_id: int):
        """Message 4: Are you filling this for yourself or someone else?"""
        keyboard = []
        for opt in INTENT_MESSAGE["options"]:
            keyboard.append([InlineKeyboardButton(
                opt["label"],
                callback_data=f"intent_{opt['value']}"
            )])

        await context.bot.send_message(
            chat_id=chat_id,
            text=INTENT_MESSAGE["text"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _handle_intent(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                             telegram_id: int, intent: str):
        """Handle intent answer (self vs proxy)"""
        session = self.db.get_session(telegram_id)

        if intent == "self":
            session["proxy"] = None
            self.db.save_session(session)
            await self._start_gunas(chat_id, context, telegram_id)
        elif intent == "proxy":
            session["proxy"] = {"type": "proxy"}
            session["proxy_step"] = 0
            self.db.save_session(session)
            await self._show_proxy_question(chat_id, context, telegram_id, 0)

    async def _show_proxy_question(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                   telegram_id: int, step: int):
        """Show proxy flow questions"""
        if step >= len(PROXY_MESSAGES):
            # Proxy flow complete → start gunas
            await self._start_gunas(chat_id, context, telegram_id)
            return

        proxy_q = PROXY_MESSAGES[step]
        keyboard = []
        for opt in proxy_q["options"]:
            keyboard.append([InlineKeyboardButton(
                opt["label"],
                callback_data=f"proxy_{step}_{opt['value']}"
            )])

        await context.bot.send_message(
            chat_id=chat_id,
            text=proxy_q["text"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _handle_proxy_answer(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                   telegram_id: int, step: int, value: str):
        """Handle proxy flow answers"""
        session = self.db.get_session(telegram_id)

        if step == 0:
            # Relationship to candidate
            session["proxy"]["relationship"] = value
            session["proxy_step"] = 1
            self.db.save_session(session)
            await self._show_proxy_question(chat_id, context, telegram_id, 1)
        elif step == 1:
            # Consent
            session["proxy"]["consent"] = value
            self.db.save_session(session)

            if value == "not_yet":
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=PROXY_NO_CONSENT_MESSAGE,
                )
                # Still proceed — but matching will be paused
                session["proxy"]["matching_paused"] = True
                self.db.save_session(session)

            # Small delay before starting gunas
            await asyncio.sleep(1)
            await self._start_gunas(chat_id, context, telegram_id)

    # ================================================================
    # GUNA FLOW
    # ================================================================

    async def _start_gunas(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                           telegram_id: int):
        """Transition from intro to the 36 gunas"""
        session = self.db.get_session(telegram_id)
        session["current_section"] = "niyat"
        session["current_question"] = 1
        self.db.save_session(session)

        # Show Section 1 buy-in
        await context.bot.send_message(
            chat_id=chat_id,
            text=SECTION_TRANSITIONS["niyat_buyin"],
        )
        await asyncio.sleep(0.5)

        # Ask first guna
        await self._ask_question(chat_id, context, 1, session)

    async def _ask_question(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                            question_num: int, session: Dict):
        """Display a guna question with appropriate UI"""
        if question_num > TOTAL_GUNAS:
            # All 36 gunas complete
            await self._show_close(chat_id, context, session)
            return

        # Section transition
        previous_q = session.get("current_question", 0)
        previous_section = get_section_for_question(previous_q)
        current_section = get_section_for_question(question_num)

        if current_section != previous_section and question_num != 1:
            transition_key = get_transition_key(current_section, previous_section)
            if transition_key and transition_key in SECTION_TRANSITIONS:
                name = session.get("answers", {}).get("first_name", "")
                transition_text = SECTION_TRANSITIONS[transition_key].format(name=name)
                await context.bot.send_message(chat_id=chat_id, text=transition_text)
                await asyncio.sleep(0.5)

        # Halfway milestone (after section 5 starts)
        if question_num == 29 and "halfway_sent" not in session:
            name = session.get("answers", {}).get("first_name", "")
            milestone = SECTION_TRANSITIONS.get("jeevan_shaili_milestone", "")
            if milestone:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=milestone.format(name=name),
                )
                await asyncio.sleep(0.5)
            session["halfway_sent"] = True

        # Loop detection
        asked_questions = session.get("asked_questions", [])
        if question_num in asked_questions:
            logger.error(f"LOOP DETECTED: Q{question_num} already asked for user {session['user_id']}")
            next_q = get_next_question(session["answers"], question_num)
            if next_q == question_num:
                logger.error(f"INFINITE LOOP: Q{question_num}. Stopping.")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Something went wrong with the flow. Let me get this fixed.",
                )
                return
            await self._ask_question(chat_id, context, next_q, session)
            return

        # Skip check
        if should_skip_question(question_num, session["answers"]):
            session["skip_questions"].append(question_num)
            self.db.save_session(session)
            next_q = get_next_question(session["answers"], question_num)
            await self._ask_question(chat_id, context, next_q, session)
            return

        question = QUESTIONS.get(question_num)
        if not question:
            logger.error(f"Guna {question_num} not found in config")
            next_q = question_num + 1
            await self._ask_question(chat_id, context, next_q, session)
            return

        # Update session
        session["current_question"] = question_num
        session["current_section"] = current_section
        if "asked_questions" not in session:
            session["asked_questions"] = []
        session["asked_questions"].append(question_num)
        self.db.save_session(session)

        # Route to appropriate UI
        q_type = question["type"]
        if q_type == "single_select":
            await self._ask_single_select(chat_id, context, question_num, question, session)
        elif q_type == "text_input":
            await self._ask_text_input(chat_id, context, question_num, question)
        elif q_type == "two_step_date":
            await self._ask_two_step_date(chat_id, context, question_num, question, session)
        elif q_type == "location_tree":
            await self._ask_location_tree(chat_id, context, question_num, question, session)

    # ================================================================
    # QUESTION TYPE HANDLERS
    # ================================================================

    async def _ask_single_select(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                 question_num: int, question: Dict, session: Dict):
        """Display single-select buttons"""
        # Check for conditional options
        conditional_opts = get_conditional_options(question_num, session["answers"])

        if conditional_opts is not None:
            options = conditional_opts
        else:
            options = question["options"]
            if isinstance(options, str):
                options = self.dynamic_options.get(options, [])

        if not options:
            # No options available (e.g., religion with no practice options) → skip
            next_q = get_next_question(session["answers"], question_num)
            await self._ask_question(chat_id, context, next_q, session)
            return

        columns = question.get("columns", 1)
        keyboard = self._build_keyboard(options, question_num, columns)

        await context.bot.send_message(
            chat_id=chat_id,
            text=question["text"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _ask_text_input(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                              question_num: int, question: Dict):
        """Ask for text input"""
        placeholder = question.get("placeholder", "Type your answer...")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"{question['text']}\n\n\U0001f4ac {placeholder}",
        )

    async def _ask_two_step_date(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                 question_num: int, question: Dict, session: Dict):
        """Two-step date question (year → month) for DOB"""
        if "two_step_buffer" not in session:
            session["two_step_buffer"] = {}

        step1_field = question["step1"]["field"]

        if step1_field not in session.get("two_step_buffer", {}):
            # Step 1: birth year
            step_q = {**question["step1"], "field": step1_field}
            await self._ask_single_select(chat_id, context, question_num, step_q, session)
        else:
            # Step 2: birth month
            step_q = {**question["step2"], "field": question["step2"]["field"]}
            await self._ask_single_select(chat_id, context, question_num, step_q, session)

    async def _ask_location_tree(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                 question_num: int, question: Dict, session: Dict):
        """Three-step location question: India/abroad → state/country → city"""
        if "location_buffer" not in session:
            session["location_buffer"] = {}

        loc = session["location_buffer"]

        if "location_type" not in loc:
            # Step 1: India or Outside India
            step_q = question["step1"]
            keyboard = self._build_keyboard(step_q["options"], question_num, 1, prefix="loc1")
            await context.bot.send_message(
                chat_id=chat_id,
                text=step_q["text"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        elif "region" not in loc:
            # Step 2: state or country
            location_type = loc["location_type"]
            if location_type == "India":
                step_q = question["step2_india"]
            else:
                step_q = question["step2_abroad"]

            options = step_q["options"]
            if isinstance(options, str):
                options = self.dynamic_options.get(options, [])

            columns = step_q.get("columns", 1)
            keyboard = self._build_keyboard(options, question_num, columns, prefix="loc2")
            await context.bot.send_message(
                chat_id=chat_id,
                text=step_q["text"],
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            # Step 3: city (text input)
            step_q = question["step3"]
            session["current_sub_step"] = "location_city"
            self.db.save_session(session)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{step_q['text']}\n\n\U0001f4ac {step_q.get('placeholder', 'Type your city...')}",
            )

    # ================================================================
    # SUB-QUESTION HANDLER
    # ================================================================

    async def _ask_sub_question(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                sub_key: str, session: Dict):
        """Ask a sub-question (not a guna)"""
        sub_q = SUB_QUESTIONS.get(sub_key)
        if not sub_q:
            return

        session["current_sub_question"] = sub_key
        self.db.save_session(session)

        keyboard = self._build_keyboard(sub_q["options"], 0, 1, prefix=f"sub_{sub_key}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=sub_q["text"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _handle_sub_answer(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                 telegram_id: int, sub_key: str, value: str):
        """Process sub-question answer"""
        session = self.db.get_session(telegram_id)
        sub_q = SUB_QUESTIONS.get(sub_key)
        if not sub_q:
            return

        # Resolve actual value
        actual_value = self._resolve_value(value, sub_q["options"])

        # Save answer
        field = sub_q["field"]
        session["answers"][field] = actual_value
        session["last_active"] = datetime.utcnow().isoformat()
        session.pop("current_sub_question", None)
        self.db.save_session(session)

        # Save to DB
        await self.db.save_answer(telegram_id, sub_q["db_table"], field, actual_value)

        # Continue to next guna (after the guna that triggered this sub-question)
        after_guna = sub_q["after_guna"]
        next_q = get_next_question(session["answers"], after_guna)

        # But first check if there are more sub-questions to ask
        pending_sub = self._get_pending_sub_questions(after_guna, session)
        if pending_sub:
            await self._ask_sub_question(chat_id, context, pending_sub[0], session)
        else:
            await self._ask_question(chat_id, context, next_q, session)

    def _get_pending_sub_questions(self, after_guna: int, session: Dict) -> list:
        """Get list of sub-questions that should be asked after a given guna"""
        pending = []
        for sub_key, sub_q in SUB_QUESTIONS.items():
            if sub_q["after_guna"] == after_guna:
                if should_ask_sub_question(sub_key, session["answers"]):
                    if sub_q["field"] not in session["answers"]:
                        pending.append(sub_key)
        return pending

    # ================================================================
    # CALLBACK HANDLER (main router for button presses)
    # ================================================================

    async def handle_button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all button press callbacks"""
        query = update.callback_query
        await query.answer()

        telegram_id = query.from_user.id
        data = query.data
        chat_id = query.message.chat.id

        # Route based on callback prefix
        if data.startswith("intro_next_"):
            index = int(data.split("_")[-1])
            await self._show_intro_message(chat_id, context, index + 1, telegram_id)

        elif data.startswith("intent_"):
            intent = data.split("_", 1)[1]
            await self._handle_intent(chat_id, context, telegram_id, intent)

        elif data.startswith("proxy_"):
            parts = data.split("_", 2)
            step = int(parts[1])
            value = parts[2]
            await self._handle_proxy_answer(chat_id, context, telegram_id, step, value)

        elif data.startswith("sub_"):
            # sub_{sub_key}_{value}
            rest = data[4:]  # remove "sub_"
            # Find the sub_key (may contain underscores)
            for sub_key in SUB_QUESTIONS:
                prefix = f"{sub_key}_"
                if rest.startswith(prefix):
                    value = rest[len(prefix):]
                    await self._handle_sub_answer(chat_id, context, telegram_id, sub_key, value)
                    return

        elif data.startswith("loc1_"):
            # Location step 1 answer
            value = data.split("_", 2)[-1]
            await self._handle_location_step1(chat_id, context, telegram_id, value)

        elif data.startswith("loc2_"):
            # Location step 2 answer
            value = data.split("_", 2)[-1]
            await self._handle_location_step2(chat_id, context, telegram_id, value)

        elif data.startswith("q"):
            # Guna answer: q<num>_<value>
            await self._handle_question_answer(query, context, telegram_id, data)

        elif data == "resume_onboarding":
            session = self.db.get_session(telegram_id)
            current_q = session.get("current_question", 1)
            await self._ask_question(chat_id, context, current_q, session)

        elif data == "restart_onboarding":
            self.db.clear_session(telegram_id)
            await self._start_intro(update, context, telegram_id, query.from_user)

    # ================================================================
    # GUNA ANSWER PROCESSING
    # ================================================================

    async def _handle_question_answer(self, query, context: ContextTypes.DEFAULT_TYPE,
                                      telegram_id: int, callback_data: str):
        """Process answer from a guna button"""
        parts = callback_data.split("_", 1)
        question_num = int(parts[0][1:])  # Remove 'q' prefix
        value = parts[1] if len(parts) > 1 else None

        session = self.db.get_session(telegram_id)
        question = QUESTIONS.get(question_num)

        if not question:
            return

        chat_id = query.message.chat.id

        # Handle two-step date
        if question["type"] == "two_step_date":
            await self._handle_two_step_date(query, context, telegram_id, question_num, question, value, session)
            return

        # Single-select — save answer
        field = question["field"]

        # Resolve actual value from options
        conditional_opts = get_conditional_options(question_num, session["answers"])
        if conditional_opts is not None:
            options = conditional_opts
        else:
            options = question.get("options", [])
            if isinstance(options, str):
                options = self.dynamic_options.get(options, [])

        actual_value = self._resolve_value(value, options)

        session["answers"][field] = actual_value
        session["last_active"] = datetime.utcnow().isoformat()
        self.db.save_session(session)

        # Save to DB
        await self.db.save_answer(telegram_id, question["db_table"], field, actual_value)

        # Check for sub-questions after this guna
        pending_sub = self._get_pending_sub_questions(question_num, session)
        if pending_sub:
            await self._ask_sub_question(chat_id, context, pending_sub[0], session)
        else:
            # Move to next guna
            next_q = get_next_question(session["answers"], question_num)
            await self._ask_question(chat_id, context, next_q, session)

    async def _handle_two_step_date(self, query, context, telegram_id: int,
                                    question_num: int, question: Dict,
                                    value: str, session: Dict):
        """Handle two-step date answer (year, then month)"""
        if "two_step_buffer" not in session:
            session["two_step_buffer"] = {}

        step1_field = question["step1"]["field"]
        chat_id = query.message.chat.id

        if step1_field not in session["two_step_buffer"]:
            # Step 1: save birth year
            session["two_step_buffer"][step1_field] = value
            self.db.save_session(session)
            await self._ask_two_step_date(chat_id, context, question_num, question, session)
        else:
            # Step 2: save birth month and construct date
            birth_year = session["two_step_buffer"][step1_field]
            birth_month = value

            try:
                date_obj = datetime(int(birth_year), int(birth_month), 1)
                date_str = date_obj.strftime("%Y-%m-%d")
                age = (datetime.now() - date_obj).days // 365

                field = question.get("field", "date_of_birth")
                session["answers"][field] = date_str
                session["two_step_buffer"] = {}
                session["last_active"] = datetime.utcnow().isoformat()
                self.db.save_session(session)

                await self.db.save_answer(telegram_id, question["db_table"], field, date_str)

                # Show age confirmation
                response_template = question.get("response_template")
                if response_template:
                    await query.message.reply_text(response_template.format(age=age))

                next_q = get_next_question(session["answers"], question_num)
                await self._ask_question(chat_id, context, next_q, session)

            except (ValueError, KeyError) as e:
                logger.error(f"Error constructing date: {e}")
                await query.message.reply_text("Something went wrong. Let me ask that again.")
                session["two_step_buffer"] = {}
                self.db.save_session(session)
                await self._ask_two_step_date(chat_id, context, question_num, question, session)

    # ================================================================
    # LOCATION TREE HANDLERS
    # ================================================================

    async def _handle_location_step1(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                     telegram_id: int, value: str):
        """Handle location step 1: India / Outside India"""
        session = self.db.get_session(telegram_id)
        if "location_buffer" not in session:
            session["location_buffer"] = {}

        # Resolve the value
        location_type = "India" if "india" in value.lower() else "Outside India"
        session["location_buffer"]["location_type"] = location_type
        self.db.save_session(session)

        question = QUESTIONS[8]
        await self._ask_location_tree(chat_id, context, 8, question, session)

    async def _handle_location_step2(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                     telegram_id: int, value: str):
        """Handle location step 2: state or country"""
        session = self.db.get_session(telegram_id)
        loc = session.get("location_buffer", {})
        location_type = loc.get("location_type", "India")

        # Resolve the actual value
        if location_type == "India":
            step_q = QUESTIONS[8]["step2_india"]
            field = "state_india"
        else:
            step_q = QUESTIONS[8]["step2_abroad"]
            field = "country_current"

        options = step_q["options"]
        if isinstance(options, str):
            options = self.dynamic_options.get(options, [])

        actual_value = self._resolve_value(value, options)

        session["answers"][field] = actual_value
        session["location_buffer"]["region"] = actual_value
        self.db.save_session(session)

        # Save to DB
        await self.db.save_answer(telegram_id, "users", field, actual_value)

        # Ask step 3 (city — text input)
        question = QUESTIONS[8]
        await self._ask_location_tree(chat_id, context, 8, question, session)

    async def _handle_location_city(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                    telegram_id: int, city: str):
        """Handle location step 3: city text input"""
        session = self.db.get_session(telegram_id)

        session["answers"]["city_current"] = city
        session["location_buffer"] = {}
        session.pop("current_sub_step", None)
        session["last_active"] = datetime.utcnow().isoformat()
        self.db.save_session(session)

        # Save to DB
        await self.db.save_answer(telegram_id, "users", "city_current", city)

        # Move to next guna
        next_q = get_next_question(session["answers"], 8)

        # Check sub-questions after guna 8
        pending_sub = self._get_pending_sub_questions(8, session)
        if pending_sub:
            await self._ask_sub_question(chat_id, context, pending_sub[0], session)
        else:
            await self._ask_question(chat_id, context, next_q, session)

    # ================================================================
    # TEXT INPUT HANDLER
    # ================================================================

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input during questions"""
        telegram_id = update.effective_user.id
        text = update.message.text
        chat_id = update.message.chat.id

        session = self.db.get_session(telegram_id)
        if not session:
            return

        # Check if we're in location city step
        if session.get("current_sub_step") == "location_city":
            await self._handle_location_city(chat_id, context, telegram_id, text.strip())
            return

        current_q = session.get("current_question")
        if not current_q:
            return

        question = QUESTIONS.get(current_q)
        if not question or question["type"] != "text_input":
            await update.message.reply_text(ERROR_MESSAGES["button_expected"])
            return

        # Validate
        validation_rule = question.get("validation")
        if validation_rule:
            is_valid, error_msg, processed_value = validate_input(
                text, validation_rule, VALIDATION_RULES
            )
            if not is_valid:
                await update.message.reply_text(error_msg)
                return
            value = processed_value
        else:
            value = text.strip()

        # Save answer
        field = question["field"]
        session["answers"][field] = value
        session["last_active"] = datetime.utcnow().isoformat()
        self.db.save_session(session)

        await self.db.save_answer(telegram_id, question["db_table"], field, value)

        # Check sub-questions
        pending_sub = self._get_pending_sub_questions(current_q, session)
        if pending_sub:
            await self._ask_sub_question(chat_id, context, pending_sub[0], session)
        else:
            next_q = get_next_question(session["answers"], current_q)
            await self._ask_question(chat_id, context, next_q, session)

    # ================================================================
    # CLOSE / RESUME
    # ================================================================

    async def _show_close(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                          session: Dict):
        """Show the closing message after all 36 gunas"""
        name = session.get("answers", {}).get("first_name", "")
        close_text = CLOSE_MESSAGE.format(name=name)

        await context.bot.send_message(chat_id=chat_id, text=close_text)

        # Update session state
        session["current_section"] = "complete"
        session["current_question"] = TOTAL_GUNAS + 1
        self.db.save_session(session)

    async def _show_resume_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  session: Dict):
        """Show resume prompt for incomplete onboarding"""
        name = session.get("answers", {}).get("first_name", update.effective_user.first_name)
        current = session.get("current_question", 0)

        text = RESUME_PROMPT.format(name=name, current=current, total=TOTAL_GUNAS)

        keyboard = [[
            InlineKeyboardButton(RESUME_BUTTONS[0], callback_data="resume_onboarding"),
            InlineKeyboardButton(RESUME_BUTTONS[1], callback_data="restart_onboarding"),
        ]]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _build_keyboard(self, options: list, question_num: int, columns: int = 1,
                        prefix: str = None) -> list:
        """Build an InlineKeyboard from options"""
        cb_prefix = prefix or f"q{question_num}"
        keyboard = []

        if columns == 1:
            for opt in options:
                keyboard.append([InlineKeyboardButton(
                    opt["label"],
                    callback_data=f"{cb_prefix}_{self._sanitize_callback(opt.get('value'))}"
                )])
        else:
            for i in range(0, len(options), columns):
                row = []
                for opt in options[i:i + columns]:
                    row.append(InlineKeyboardButton(
                        opt["label"],
                        callback_data=f"{cb_prefix}_{self._sanitize_callback(opt.get('value'))}"
                    ))
                keyboard.append(row)

        return keyboard

    def _sanitize_callback(self, value: Any) -> str:
        """Sanitize value for callback_data (max 64 bytes)"""
        if value is None:
            return "none"
        s = str(value).lower().replace(" ", "_").replace("/", "_")
        # Telegram callback_data max is 64 bytes
        return s[:60]

    def _resolve_value(self, callback_value: str, options: list) -> Any:
        """Resolve actual value from sanitized callback value"""
        if not options:
            return callback_value

        for opt in options:
            if self._sanitize_callback(opt.get("value")) == callback_value:
                return opt.get("value")

        # Fallback: return the callback value as-is
        return callback_value
