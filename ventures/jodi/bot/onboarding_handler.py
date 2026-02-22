"""
JODI Telegram Onboarding Flow Handler
Handles button-based structured onboarding (Questions 1-79)
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from config import (
    INTRO_MESSAGES,
    QUESTIONS,
    SECTION_TRANSITIONS,
    FINAL_TRANSITION,
    ERROR_MESSAGES,
    RESUME_PROMPT,
    RESUME_BUTTONS,
    VALIDATION_RULES,
    get_birth_years,
    get_countries,
    get_states_india
)
from conditional_logic import get_next_question, should_skip_question, get_conditional_options, get_section_for_question
from validation import validate_input
from db_adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


class OnboardingHandler:
    """Manages the onboarding flow state and progression"""
    
    def __init__(self, db_adapter: DatabaseAdapter):
        self.db = db_adapter
        self.dynamic_options = {
            "birth_years": get_birth_years(),
            "countries": get_countries(),
            "states_india": get_states_india()
        }
    
    async def start_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Entry point: /start command"""
        user = update.effective_user
        telegram_id = user.id
        
        # Check if user has existing progress
        session = self.db.get_session(telegram_id)
        
        if session and session.get('current_question', 0) > 0 and session.get('current_question', 0) < 79:
            # User has incomplete onboarding
            await self._show_resume_prompt(update, context, session)
        else:
            # Fresh start - show intro
            await self._start_intro(update, context, telegram_id, user)
    
    async def _start_intro(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          telegram_id: int, user: Any):
        """Start intro sequence"""
        # Initialize session
        session = {
            "user_id": telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "current_section": "intro",
            "current_question": 0,
            "intro_index": 0,
            "answers": {},
            "skip_questions": [],
            "asked_questions": [],  # Loop detection: track all asked questions
            "multi_select_buffer": {},
            "photo_urls": [],
            "started_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat()
        }
        
        self.db.save_session(session)
        
        # Show first intro message
        await self._show_intro_message(update.message.chat.id, context, 0, telegram_id)
    
    async def _show_intro_message(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                 index: int, telegram_id: int):
        """Show intro message with button"""
        if index >= len(INTRO_MESSAGES):
            # Intro complete, move to questions
            await self._start_questions(chat_id, context, telegram_id)
            return
        
        intro = INTRO_MESSAGES[index]
        
        keyboard = [[InlineKeyboardButton(
            intro["button"],
            callback_data=f"intro_next_{index}"
        )]]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=intro["text"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _start_questions(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                              telegram_id: int):
        """Transition from intro to questions"""
        session = self.db.get_session(telegram_id)
        session['current_section'] = 'identity_basics'
        session['current_question'] = 1
        self.db.save_session(session)
        
        # Show first transition
        await context.bot.send_message(
            chat_id=chat_id,
            text=SECTION_TRANSITIONS['after_intro']
        )
        
        # Ask first question
        await self._ask_question(chat_id, context, 1, session)
    
    async def _send_section_transition(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                       current_q: int, previous_q: int, session: Dict):
        """Send transition message if entering a new section"""
        if previous_q is None or previous_q == 0:
            return  # No transition needed (first question or after intro)
        
        current_section = get_section_for_question(current_q)
        previous_section = get_section_for_question(previous_q)
        
        if current_section != previous_section:
            # Map section names to transition keys
            transition_key_map = {
                "identity_basics": None,  # No transition (comes after intro)
                "location_mobility": "after_identity",
                "religion_culture": "after_location",
                "education_career": "after_religion",
                "financial": "after_education",
                "family": "after_financial",
                "lifestyle": "after_family",
                "partner_prefs": "after_lifestyle",
                "values": "after_partner_prefs",
                "dealbreakers": "after_values"
            }
            
            transition_key = transition_key_map.get(current_section)
            if transition_key and transition_key in SECTION_TRANSITIONS:
                # Calculate progress percentage for some transitions
                total_questions = 79
                answered = len(session.get('answers', {}))
                progress_pct = int((answered / total_questions) * 100)
                
                transition_text = SECTION_TRANSITIONS[transition_key]
                # Add progress indicator for some transitions
                if transition_key in ["after_family", "after_lifestyle"]:
                    transition_text += f"\n\n📊 {progress_pct}% complete"
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=transition_text
                )
    
    async def _ask_question(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                           question_num: int, session: Dict):
        """Display a question with appropriate UI"""
        if question_num > 79:
            # All questions complete
            await self._show_photo_upload(chat_id, context, session)
            return
        
        # Send section transition message if entering new section
        previous_q = session.get('current_question', 0)
        await self._send_section_transition(chat_id, context, question_num, previous_q, session)
        
        # LOOP DETECTION: Check if this question was already asked
        asked_questions = session.get('asked_questions', [])
        if question_num in asked_questions:
            logger.error(f"🔁 LOOP DETECTED: Q{question_num} already asked for user {session['user_id']}")
            logger.error(f"  Path: {asked_questions}")
            logger.error(f"  Current answers: {list(session['answers'].keys())}")
            
            # Alert monitoring (send to N via logger - can wire to Telegram later)
            # Skip this question and try next
            next_q = get_next_question(session['answers'], question_num)
            if next_q == question_num:
                # Infinite loop detected - bail out
                logger.error(f"🚨 INFINITE LOOP: Q{question_num} → Q{question_num}. Stopping.")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Something went wrong with the flow. Let me get this fixed — I'll ping you when it's ready."
                )
                return
            await self._ask_question(chat_id, context, next_q, session)
            return
        
        # Check if question should be skipped
        if should_skip_question(question_num, session['answers']):
            session['skip_questions'].append(question_num)
            self.db.save_session(session)
            next_q = get_next_question(session['answers'], question_num)
            await self._ask_question(chat_id, context, next_q, session)
            return
        
        question = QUESTIONS.get(question_num)
        if not question:
            logger.error(f"Question {question_num} not found in config")
            next_q = question_num + 1
            await self._ask_question(chat_id, context, next_q, session)
            return
        
        # Update session and mark question as asked
        session['current_question'] = question_num
        if 'asked_questions' not in session:
            session['asked_questions'] = []
        session['asked_questions'].append(question_num)
        self.db.save_session(session)
        
        # Build and send question
        if question['type'] == 'single_select':
            await self._ask_single_select(chat_id, context, question_num, question, session)
        elif question['type'] == 'multi_select':
            await self._ask_multi_select(chat_id, context, question_num, question, session)
        elif question['type'] == 'text_input':
            await self._ask_text_input(chat_id, context, question_num, question)
        elif question['type'] == 'two_step':
            await self._ask_two_step(chat_id, context, question_num, question, session)
        elif question['type'] == 'two_step_date':
            await self._ask_two_step_date(chat_id, context, question_num, question, session)
        elif question['type'] == 'two_step_region':
            await self._ask_two_step_region(chat_id, context, question_num, question, session)
    
    async def _ask_single_select(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                question_num: int, question: Dict, session: Dict):
        """Display single-select question with buttons"""
        # Check for conditional options first (e.g., Q21 sect based on religion)
        conditional_opts = get_conditional_options(question_num, session['answers'])
        
        if conditional_opts is not None:
            options = conditional_opts
        else:
            # Get options from question config
            options = question['options']
            if isinstance(options, str):
                # Dynamic options
                options = self.dynamic_options.get(options, [])
        
        # Build keyboard
        columns = question.get('columns', 1)
        keyboard = []
        
        if columns == 1:
            for opt in options:
                keyboard.append([InlineKeyboardButton(
                    opt['label'],
                    callback_data=f"q{question_num}_{self._sanitize_callback(opt['value'])}"
                )])
        else:
            # Multi-column layout
            for i in range(0, len(options), columns):
                row = []
                for opt in options[i:i+columns]:
                    row.append(InlineKeyboardButton(
                        opt['label'],
                        callback_data=f"q{question_num}_{self._sanitize_callback(opt['value'])}"
                    ))
                keyboard.append(row)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=question['text'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _ask_multi_select(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                               question_num: int, question: Dict, session: Dict):
        """Display multi-select question with checkboxes"""
        # Initialize buffer if first time
        field = question['field']
        if field not in session['multi_select_buffer']:
            session['multi_select_buffer'][field] = []
            self.db.save_session(session)
        
        selected = session['multi_select_buffer'][field]
        
        # Build keyboard with checkmarks
        keyboard = []
        for opt in question['options']:
            check = "✓ " if opt['value'] in selected else ""
            keyboard.append([InlineKeyboardButton(
                f"{check}{opt['label']}",
                callback_data=f"q{question_num}_{self._sanitize_callback(opt['value'])}"
            )])
        
        # Add "Done" button
        keyboard.append([InlineKeyboardButton(
            "✅ Done",
            callback_data=f"q{question_num}_done"
        )])
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=question['text'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _ask_text_input(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                             question_num: int, question: Dict):
        """Ask for text input"""
        await context.bot.send_message(
            chat_id=chat_id,
            text=question['text'] + f"\n\n💬 {question.get('placeholder', 'Type your answer...')}"
        )
    
    async def _ask_two_step(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                           question_num: int, question: Dict, session: Dict):
        """Two-step question (e.g., age range min/max)"""
        # Check if we're on step 1 or step 2
        step1_field = question.get('step1_field')
        
        if step1_field not in session['answers']:
            # Step 1
            await self._ask_single_select(chat_id, context, question_num, 
                                         question['step1'], session)
        else:
            # Step 2
            await self._ask_single_select(chat_id, context, question_num,
                                         question['step2'], session)
    
    async def _ask_two_step_date(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                 question_num: int, question: Dict, session: Dict):
        """Two-step date question (year, then month for DOB)"""
        # Check if we're on step 1 (year) or step 2 (month)
        step1_field = question['step1']['field']
        
        if step1_field not in session.get('two_step_buffer', {}):
            # Step 1: Ask for birth year
            step_question = {**question['step1'], 'field': step1_field}
            await self._ask_single_select(chat_id, context, question_num, step_question, session)
        else:
            # Step 2: Ask for birth month
            step_question = {**question['step2'], 'field': question['step2']['field']}
            await self._ask_single_select(chat_id, context, question_num, step_question, session)
    
    async def _ask_two_step_region(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                   question_num: int, question: Dict, session: Dict):
        """Two-step hierarchical region/country selection"""
        from config import get_countries_by_region
        
        step1_field = question['step1']['field']
        
        if step1_field not in session.get('two_step_buffer', {}):
            # Step 1: Ask for region
            step_question = {**question['step1'], 'field': step1_field}
            await self._ask_single_select(chat_id, context, question_num, step_question, session)
        else:
            # Step 2: Ask for country based on selected region
            selected_region = session['two_step_buffer'][step1_field]
            countries = get_countries_by_region(selected_region)
            
            step_question = {
                **question['step2'],
                'field': question['step2']['field'],
                'options': countries
            }
            await self._ask_single_select(chat_id, context, question_num, step_question, session)
    
    async def handle_button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button press callbacks"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        data = query.data
        
        # Parse callback data
        if data.startswith('intro_next_'):
            # Intro navigation
            index = int(data.split('_')[-1])
            await self._show_intro_message(query.message.chat.id, context, index + 1, telegram_id)
        
        elif data.startswith('q'):
            # Question answer
            await self._handle_question_answer(query, context, telegram_id, data)
        
        elif data == 'resume_onboarding':
            session = self.db.get_session(telegram_id)
            current_q = session.get('current_question', 1)
            await self._ask_question(query.message.chat.id, context, current_q, session)
        
        elif data == 'restart_onboarding':
            # Clear session and restart
            self.db.clear_session(telegram_id)
            await self._start_intro(update, context, telegram_id, query.from_user)
    
    async def _handle_question_answer(self, query, context: ContextTypes.DEFAULT_TYPE,
                                     telegram_id: int, callback_data: str):
        """Process question answer from button callback"""
        # Parse: q<num>_<value>
        parts = callback_data.split('_', 1)
        question_num = int(parts[0][1:])  # Remove 'q' prefix
        value = parts[1] if len(parts) > 1 else None
        
        session = self.db.get_session(telegram_id)
        question = QUESTIONS.get(question_num)
        
        if not question:
            return
        
        # Handle multi-select
        if question['type'] == 'multi_select':
            await self._handle_multi_select(query, context, telegram_id, 
                                           question_num, question, value, session)
            return
        
        # Handle two-step
        if question['type'] == 'two_step':
            await self._handle_two_step(query, context, telegram_id,
                                       question_num, question, value, session)
            return
        
        # Handle two-step date (for DOB)
        if question['type'] == 'two_step_date':
            await self._handle_two_step_date(query, context, telegram_id,
                                            question_num, question, value, session)
            return
        
        # Handle two-step region (for NRI location)
        if question['type'] == 'two_step_region':
            await self._handle_two_step_region(query, context, telegram_id,
                                              question_num, question, value, session)
            return
        
        # Single-select - save answer
        field = question['field']
        
        # Find actual value from options
        actual_value = None
        options = question.get('options', [])
        if isinstance(options, str):
            options = self.dynamic_options.get(options, [])
        
        for opt in options:
            if self._sanitize_callback(opt.get('value')) == value:
                actual_value = opt.get('value')
                break
        
        session['answers'][field] = actual_value
        session['last_active'] = datetime.utcnow().isoformat()
        self.db.save_session(session)
        
        # Write to database
        await self.db.save_answer(telegram_id, question['db_table'], field, actual_value)
        
        # Move to next question
        next_q = get_next_question(session['answers'], question_num)
        await self._ask_question(query.message.chat.id, context, next_q, session)
    
    async def _handle_multi_select(self, query, context, telegram_id: int,
                                   question_num: int, question: Dict, 
                                   value: str, session: Dict):
        """Handle multi-select checkbox logic"""
        field = question['field']
        
        if value == 'done':
            # Finalize selection
            selected = session['multi_select_buffer'].get(field, [])
            session['answers'][field] = selected
            session['multi_select_buffer'].pop(field, None)
            self.db.save_session(session)
            
            # Save to DB
            await self.db.save_answer(telegram_id, question['db_table'], field, selected)
            
            # Next question
            next_q = get_next_question(session['answers'], question_num)
            await self._ask_question(query.message.chat.id, context, next_q, session)
        else:
            # Toggle selection
            selected = session['multi_select_buffer'].get(field, [])
            
            if value in selected:
                selected.remove(value)
                await query.answer(f"✗ Removed {value}")
            else:
                selected.append(value)
                await query.answer(f"✓ Added {value}")
            
            session['multi_select_buffer'][field] = selected
            self.db.save_session(session)
            
            # Re-render buttons
            await self._ask_multi_select(query.message.chat.id, context,
                                        question_num, question, session)
    
    async def _handle_two_step_date(self, query, context, telegram_id: int,
                                    question_num: int, question: Dict, 
                                    value: str, session: Dict):
        """Handle two-step date input (year, then month)"""
        # Initialize two_step_buffer if needed
        if 'two_step_buffer' not in session:
            session['two_step_buffer'] = {}
        
        step1_field = question['step1']['field']
        step2_field = question['step2']['field']
        
        # Check if we're processing step 1 or step 2
        if step1_field not in session['two_step_buffer']:
            # Step 1: Save birth year
            session['two_step_buffer'][step1_field] = value
            self.db.save_session(session)
            
            # Ask step 2
            await self._ask_two_step_date(query.message.chat.id, context, 
                                         question_num, question, session)
        else:
            # Step 2: Save birth month and construct date
            session['two_step_buffer'][step2_field] = value
            
            birth_year = session['two_step_buffer'][step1_field]
            birth_month = session['two_step_buffer'][step2_field]
            
            # Construct date (assuming day 1 for now - we can make this more sophisticated later)
            from datetime import datetime
            try:
                # Create date: YYYY-MM-01
                date_obj = datetime(int(birth_year), int(birth_month), 1)
                date_str = date_obj.strftime('%Y-%m-%d')
                
                # Calculate age
                age = (datetime.now() - date_obj).days // 365
                
                # Save to answers and database
                field = question.get('field', 'date_of_birth')
                session['answers'][field] = date_str
                session['two_step_buffer'] = {}  # Clear buffer
                session['last_active'] = datetime.utcnow().isoformat()
                self.db.save_session(session)
                
                # Save to DB
                await self.db.save_answer(telegram_id, question['db_table'], field, date_str)
                
                # Show response template if exists
                response_template = question.get('response_template')
                if response_template:
                    response = response_template.format(age=age)
                    await query.message.reply_text(response)
                
                # Move to next question
                next_q = get_next_question(session['answers'], question_num)
                await self._ask_question(query.message.chat.id, context, next_q, session)
                
            except (ValueError, KeyError) as e:
                logger.error(f"Error constructing date: {e}")
                await query.message.reply_text("Something went wrong. Let me ask that again.")
                session['two_step_buffer'] = {}
                self.db.save_session(session)
                await self._ask_two_step_date(query.message.chat.id, context,
                                             question_num, question, session)
    
    async def _handle_two_step_region(self, query, context, telegram_id: int,
                                      question_num: int, question: Dict,
                                      value: str, session: Dict):
        """Handle two-step region/country selection"""
        # Initialize two_step_buffer if needed
        if 'two_step_buffer' not in session:
            session['two_step_buffer'] = {}
        
        step1_field = question['step1']['field']
        step2_field = question['step2']['field']
        
        # Check if we're processing step 1 or step 2
        if step1_field not in session['two_step_buffer']:
            # Step 1: Save region selection
            session['two_step_buffer'][step1_field] = value
            self.db.save_session(session)
            
            # Ask step 2 (country selection based on region)
            await self._ask_two_step_region(query.message.chat.id, context,
                                           question_num, question, session)
        else:
            # Step 2: Save country selection
            field = question.get('field', step2_field)
            session['answers'][field] = value
            session['two_step_buffer'] = {}  # Clear buffer
            session['last_active'] = datetime.utcnow().isoformat()
            self.db.save_session(session)
            
            # Save to DB
            await self.db.save_answer(telegram_id, question['db_table'], field, value)
            
            # Move to next question
            next_q = get_next_question(session['answers'], question_num)
            await self._ask_question(query.message.chat.id, context, next_q, session)
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input during questions"""
        telegram_id = update.effective_user.id
        text = update.message.text
        
        session = self.db.get_session(telegram_id)
        if not session:
            return
        
        current_q = session.get('current_question')
        if not current_q:
            return
        
        question = QUESTIONS.get(current_q)
        if not question or question['type'] != 'text_input':
            # Not expecting text input
            await update.message.reply_text(ERROR_MESSAGES['button_expected'])
            return
        
        # Validate input
        validation_rule = question.get('validation')
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
        field = question['field']
        session['answers'][field] = value
        session['last_active'] = datetime.utcnow().isoformat()
        self.db.save_session(session)
        
        # Save to DB
        await self.db.save_answer(telegram_id, question['db_table'], field, value)
        
        # Show response template if exists
        response_template = question.get('response_template')
        if response_template:
            # Calculate age if date_of_birth
            if field == 'date_of_birth':
                dob = datetime.fromisoformat(value)
                age = (datetime.now() - dob).days // 365
                response = response_template.format(age=age)
                await update.message.reply_text(response)
        
        # Move to next question
        next_q = get_next_question(session['answers'], current_q)
        await self._ask_question(update.message.chat.id, context, next_q, session)
    
    async def _show_photo_upload(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE,
                                session: Dict):
        """Request photo upload"""
        text = """That's all the quick questions done ✓

One last thing before we switch to conversation mode —

I need at least one recent photo of you.

It stays private — only shared when I introduce you to a match, and only with your approval.

Send me a clear photo where your face is visible 📸"""
        
        await context.bot.send_message(chat_id=chat_id, text=text)
        
        # Update session state
        session['current_section'] = 'photo_upload'
        self.db.save_session(session)
    
    async def _show_resume_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 session: Dict):
        """Show resume prompt for incomplete onboarding"""
        name = session.get('answers', {}).get('first_name', update.effective_user.first_name)
        current = session.get('current_question', 0)
        
        text = RESUME_PROMPT.format(name=name, current=current, total=79)
        
        keyboard = [[
            InlineKeyboardButton(RESUME_BUTTONS[0], callback_data='resume_onboarding'),
            InlineKeyboardButton(RESUME_BUTTONS[1], callback_data='restart_onboarding')
        ]]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def _sanitize_callback(self, value: Any) -> str:
        """Sanitize value for use in callback_data"""
        if value is None:
            return 'none'
        return str(value).lower().replace(' ', '_').replace('/', '_')
