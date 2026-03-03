"""
JODI Telegram Onboarding Flow
Complete button-based onboarding sequence from /start to conversational mode

Implements:
- 7-message intro sequence
- Phase 1: Top Filters (12 screens)
- Phase 2: Identity (7 screens)  
- Phase 3: Lifestyle (12-14 screens)
- Phase 4: Photo + Close (3 screens)
- State management and resumption
- Conversational transition

Author: Blitz
Date: 2026-02-12
"""

from typing import Dict, Optional, List, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ContextTypes
from datetime import datetime, date
import json

from db_postgres_v2 import JodiDB


class OnboardingFlow:
    """
    Manages the complete button-based onboarding flow.
    
    Flow stages:
    - INTRO: 7 messages (welcome, privacy, philosophy, matching, learning, plan, privacy bullets)
    - PHASE_1: Top Filters (12 screens - relationship, religion, children, lifestyle basics)
    - PHASE_2: Identity (7 screens - name, gender, orientation, DOB, location)
    - PHASE_3: Lifestyle (12-14 screens - work, education, income, fitness, preferences)
    - PHASE_4: Photo + Close (3 screens - photo upload, summary, transition)
    - CONVERSATIONAL: Hand off to LLM-driven depth building
    """
    
    # State keys
    STATE_PHASE = 'onboarding_phase'  # INTRO|PHASE_1|PHASE_2|PHASE_3|PHASE_4|CONVERSATIONAL
    STATE_SCREEN = 'onboarding_screen'  # Current screen number within phase
    STATE_DATA = 'onboarding_data'  # Temporary data storage during onboarding
    STATE_PHOTO_COUNT = 'photo_count'  # Number of photos uploaded
    
    def __init__(self, db: JodiDB):
        self.db = db
        
        # Intro messages
        self.intro_messages = [
            {
                'text': (
                    "Hey! 👋 I'm Jodi.\n\n"
                    "I help people find real, lasting relationships.\n"
                    "No swiping. No algorithms optimized to keep you scrolling.\n\n"
                    "Just one great introduction at a time."
                ),
                'button': "Tell me more →"
            },
            {
                'text': (
                    "Before we start — something important.\n\n"
                    "This is your space. Whatever you share here is between us. "
                    "It doesn't go on a profile. It doesn't go on a form. "
                    "Your parents won't see it. Your friends won't see it. "
                    "No one sees anything unless you approve it.\n\n"
                    "You can tell me things here that you might not say out loud — "
                    "what you actually want, what you've been through, what matters "
                    "to you when no one's watching.\n\n"
                    "I'm not here to judge. I'm here to find you the right person. "
                    "The more honest you are with me, the better I can do that."
                ),
                'button': "I like that. Keep going →"
            },
            {
                'text': (
                    "One thing we do differently — photos come at the end "
                    "of our process, not the beginning.\n\n"
                    "We know not everyone photographs well. And honestly, "
                    "AI filters have made photos pretty unreliable anyway.\n\n"
                    "I'd rather understand who you are first — your values, "
                    "your energy, what makes you laugh, what you need in a partner. "
                    "That's what actually predicts a great match.\n\n"
                    "Photos matter, but they're not the whole story. "
                    "And they're definitely not the first chapter."
                ),
                'button': "That's refreshing →"
            },
            {
                'text': (
                    "Here's how I find people for you:\n\n"
                    "I start with your basics and deal-breakers to filter out "
                    "anyone who clearly isn't right.\n\n"
                    "Then I go deeper — personality, values, lifestyle, "
                    "the stuff that actually makes two people click.\n\n"
                    "When I find someone promising, I'll introduce you. "
                    "One person at a time, with context on why I think you'd work well together."
                ),
                'button': "And then? →"
            },
            {
                'text': (
                    "The best part — I learn as we go.\n\n"
                    "When I show you a match, your reaction teaches me something. "
                    "What excited you. What felt off. What surprised you.\n\n"
                    "Even the matches that don't work out make the next one better. "
                    "Think of it like a friend who sets you up — "
                    "except I remember everything and never stop trying."
                ),
                'button': "Makes sense →"
            },
            {
                'text': (
                    "Okay, here's the plan:\n\n"
                    "First, I'll ask some quick-tap questions — "
                    "deal-breakers, lifestyle, the structured stuff. "
                    "Takes about 8 minutes. No typing, just tapping.\n\n"
                    "After that, we switch to real conversation. "
                    "I'll ask you questions a good friend would ask if they were setting you up. "
                    "Answer whenever you feel like it — no rush, no pressure.\n\n"
                    "And if you ever want to change an answer, just tell me later during our chats. "
                    "Nothing is locked in."
                ),
                'button': "Let's start →"
            },
            {
                'text': (
                    "Last thing — your privacy.\n\n"
                    "🔒 Your data is encrypted and never sold\n"
                    "🔒 Matches only see what you approve\n"
                    "🔒 You can delete everything at any time\n"
                    "🔒 I'll always ask before sharing anything\n\n"
                    "This only works if we trust each other. I take that seriously."
                ),
                'button': "Got it, let's go →"
            }
        ]
    
    def get_state(self, telegram_id: int) -> Dict:
        """Get current onboarding state from conversation_state"""
        state = self.db.get_conversation_state(telegram_id) or {}
        return {
            'phase': state.get(self.STATE_PHASE, 'INTRO'),
            'screen': state.get(self.STATE_SCREEN, 0),
            'data': state.get(self.STATE_DATA, {}),
            'photo_count': state.get(self.STATE_PHOTO_COUNT, 0)
        }
    
    def set_state(self, telegram_id: int, phase: str = None, screen: int = None, 
                  data: Dict = None, photo_count: int = None):
        """Update onboarding state"""
        state = self.db.get_conversation_state(telegram_id) or {}
        
        if phase is not None:
            state[self.STATE_PHASE] = phase
        if screen is not None:
            state[self.STATE_SCREEN] = screen
        if data is not None:
            state[self.STATE_DATA] = data
        if photo_count is not None:
            state[self.STATE_PHOTO_COUNT] = photo_count
        
        self.db.update_conversation_state(telegram_id, state)
    
    def is_onboarding_complete(self, telegram_id: int) -> bool:
        """Check if user has completed onboarding"""
        state = self.get_state(telegram_id)
        return state['phase'] == 'CONVERSATIONAL'
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Handle incoming message during onboarding.
        Returns True if handled by onboarding, False if should pass to conversational mode.
        """
        telegram_id = update.effective_user.id
        state = self.get_state(telegram_id)
        
        # Check if onboarding is complete
        if state['phase'] == 'CONVERSATIONAL':
            return False  # Pass to conversational handler
        
        # Handle based on current phase
        if state['phase'] == 'INTRO':
            await self._handle_intro(update, context, state)
        elif state['phase'] == 'PHASE_1':
            await self._handle_phase_1(update, context, state)
        elif state['phase'] == 'PHASE_2':
            await self._handle_phase_2(update, context, state)
        elif state['phase'] == 'PHASE_3':
            await self._handle_phase_3(update, context, state)
        elif state['phase'] == 'PHASE_4':
            await self._handle_phase_4(update, context, state)
        
        return True  # Handled by onboarding
    
    async def start_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start or resume onboarding flow"""
        telegram_id = update.effective_user.id
        state = self.get_state(telegram_id)
        
        # Check if user has already completed onboarding
        if state['phase'] == 'CONVERSATIONAL':
            await update.message.reply_text(
                f"Welcome back! 👋\n\n"
                "Your profile is set up. Want to:\n"
                "• Update something? Just tell me what changed.\n"
                "• See matches? Type /matches\n"
                "• Check progress? Type /progress"
            )
            return
        
        # Check if resuming
        if state['phase'] != 'INTRO' or state['screen'] > 0:
            await self._resume_onboarding(update, context, state)
            return
        
        # Start fresh - show first intro message
        await self._show_intro_message(update, context, 0)
        self.set_state(telegram_id, phase='INTRO', screen=0)
    
    async def _resume_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
        """Resume onboarding from where user left off"""
        telegram_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        keyboard = [[InlineKeyboardButton("Resume →", callback_data="resume_onboarding")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Hey {user_name}, we were getting through the quick questions — "
            f"want to pick up where we left off?",
            reply_markup=reply_markup
        )
    
    async def _handle_intro(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
        """Handle intro sequence"""
        telegram_id = update.effective_user.id
        current_screen = state['screen']
        
        # Show next intro message
        next_screen = current_screen + 1
        if next_screen < len(self.intro_messages):
            await self._show_intro_message(update, context, next_screen)
            self.set_state(telegram_id, screen=next_screen)
        else:
            # Intro complete, move to Phase 1
            self.set_state(telegram_id, phase='PHASE_1', screen=0)
            await self._show_phase_1_screen(update, context, 0)
    
    async def _show_intro_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, screen: int):
        """Show an intro message with button"""
        msg = self.intro_messages[screen]
        keyboard = [[InlineKeyboardButton(msg['button'], callback_data=f"intro_{screen}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Use callback query if available (button press), otherwise message
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                msg['text'],
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                msg['text'],
                reply_markup=reply_markup
            )
    
    # ============== PHASE 1: TOP FILTERS ==============
    
    def _get_phase_1_screens(self) -> List[Dict]:
        """Define Phase 1 screens (Top Filters)"""
        return [
            # F1: Relationship Intent
            {
                'id': 'relationship_intent',
                "question": "What are you looking for?",
                'options': [
                    ('Marriage', 'Marriage'),
                    ('Long-term relationship', 'Long-term committed'),
                    ('Open to either', 'Open to marriage or LTR')
                ],
                'layout': 'single',  # single column
                'store_as': 'column',
                'column': 'relationship_intent'
            },
            # F2: Religion
            {
                'id': 'religion',
                'question': "What's your religion or faith?",
                'options': [
                    ('☪️ Islam', 'Muslim'),
                    ('🕉️ Hinduism', 'Hindu'),
                    ('✝️ Christianity', 'Christian'),
                    ('✡️ Judaism', 'Jewish'),
                    ('☬ Sikhism', 'Sikh'),
                    ('☸️ Buddhism', 'Buddhist'),
                    ('🔮 Spiritual', 'Spiritual'),
                    ('🚫 Not religious', 'Atheist'),
                    ('💬 Other', 'Other')
                ],
                'layout': 'double',  # two columns
                'store_as': 'column',
                'column': 'religion'
            },
            # F3: Religion Practice (conditional)
            {
                'id': 'religious_practice_level',
                "question": "How would you describe your practice?",
                'condition': lambda data: data.get('religion') not in ['Spiritual', 'Atheist', 'Agnostic'],
                'options': [
                    ('Very practicing / Devout', 'Devout'),
                    ('Practicing', 'Practicing'),
                    ('Cultural / Moderate', 'Cultural'),
                    ('Not very practicing', 'Non-practicing')
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'religious_practice_level'
            },
            # F4: Partner Religion Match
            {
                'id': 'partner_religion_preference',
                "question": "Does your partner's religion matter?",
                'options': [
                    ('Must be same as mine', 'same_only'),
                    ('Prefer same, open to others', 'prefer_same'),
                    ('Open to others except some', 'open_except'),
                    ("Doesn't matter", 'any')
                ],
                'layout': 'single',
                'store_as': 'preference',
                'follow_up': {
                    'trigger': 'open_except',
                    'type': 'text',
                    'question': "Which religions are you NOT open to?"
                }
            },
            # F5: Children Intent
            {
                'id': 'children_intent',
                'question': "Do you want children in the future?",
                'options': [
                    ('Definitely yes', 'Want kids'),
                    ('Probably yes', 'Probably yes'),
                    ('Open to it', 'Open to kids'),
                    ('Probably not', 'Probably not'),
                    ('Definitely not', "Don't want kids")
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'children_intent'
            },
            # F6: Existing Children
            {
                'id': 'has_children',
                "question": "Do you have children already?",
                'options': [
                    ('No', False),
                    ('Yes, they live with me', 'live_with_me'),
                    ("Yes, they don't live with me", 'live_separately')
                ],
                'layout': 'single',
                'store_as': 'derived',  # Store boolean + details
                'column': 'has_children'
            },
            # F7: Smoking
            {
                'id': 'smoking',
                "question": "Do you smoke?",
                'options': [
                    ('Never', 'Never'),
                    ('Socially', 'Socially'),
                    ('Regularly', 'Current smoker'),
                    ('Quitting', 'Former smoker')
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'smoking'
            },
            # F8: Drinking
            {
                'id': 'drinking',
                "question": "Do you drink alcohol?",
                'options': [
                    ('Never', 'Never'),
                    ('Socially', 'Socially'),
                    ('Regularly', 'Regularly'),
                    ('Prefer not to say', 'Prefer not to say')
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'drinking'
            },
            # F9: Dietary Preferences
            {
                'id': 'dietary_restrictions',
                'question': (
                    'Any dietary preferences?\n\n'
                    '(Matters more than people think — shared meals are a big part of life together)'
                ),
                'options': [
                    ('No restrictions', 'None'),
                    ('Halal', 'Halal'),
                    ('Vegetarian', 'Vegetarian'),
                    ('Kosher', 'Kosher'),
                    ('Vegan', 'Vegan'),
                    ('Jain vegetarian', 'Jain'),
                    ('Other', 'Other')
                ],
                'layout': 'double',
                'store_as': 'column',
                'column': 'dietary_restrictions'
            },
            # F10: Marital History
            {
                'id': 'marital_history',
                "question": "Have you been married before?",
                'options': [
                    ('Never married', 'Never married'),
                    ('Divorced', 'Divorced'),
                    ('Widowed', 'Widowed'),
                    ('Separated', 'Separated')
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'marital_history'
            },
            # F11: Timeline
            {
                'id': 'relationship_timeline',
                "question": "How soon are you looking to find someone?",
                'options': [
                    ('Ready now — actively looking', 'Ready now'),
                    ('Within the next year', 'Within a year'),
                    ('1-2 years, no rush', '1-2 years'),
                    ('Just starting to explore', 'Exploring')
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'relationship_timeline'
            },
            # F12: Education Preference
            {
                'id': 'education_preference',
                "question": "Does your partner's education level matter?",
                'options': [
                    ('Must have a degree', 'degree_required'),
                    ('Postgraduate preferred', 'postgrad_preferred'),
                    ("Doesn't matter", 'no_preference')
                ],
                'layout': 'single',
                'store_as': 'preference'
            }
        ]
    
    async def _handle_phase_1(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
        """Handle Phase 1 (Top Filters) navigation"""
        telegram_id = update.effective_user.id
        
        # Text during button phase - redirect
        if update.message and update.message.text:
            await update.message.reply_text(
                "Just tap one of the options above 👆"
            )
            return
        
        # Button press - handled in callback handler
        pass
    
    async def _show_phase_1_screen(self, update: Update, context: ContextTypes.DEFAULT_TYPE, screen_num: int):
        """Show a Phase 1 screen"""
        telegram_id = update.effective_user.id
        screens = self._get_phase_1_screens()
        state = self.get_state(telegram_id)
        data = state['data']
        
        # Check if this screen should be skipped (conditional)
        if screen_num < len(screens):
            screen = screens[screen_num]
            
            # Check condition
            if 'condition' in screen:
                if not screen['condition'](data):
                    # Skip this screen
                    next_screen = screen_num + 1
                    if next_screen < len(screens):
                        await self._show_phase_1_screen(update, context, next_screen)
                        self.set_state(telegram_id, screen=next_screen)
                    else:
                        # Phase 1 complete
                        await self._transition_to_phase_2(update, context)
                    return
            
            # Show the screen
            keyboard = self._build_keyboard(screen['options'], screen['layout'])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    screen['question'],
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    screen['question'],
                    reply_markup=reply_markup
                )
        else:
            # Phase 1 complete
            await self._transition_to_phase_2(update, context)
    
    def _build_keyboard(self, options: List[Tuple], layout: str) -> List[List[InlineKeyboardButton]]:
        """Build inline keyboard from options"""
        if layout == 'single':
            # One button per row
            return [[InlineKeyboardButton(text, callback_data=f"opt_{i}")] 
                    for i, (text, value) in enumerate(options)]
        else:
            # Two buttons per row
            keyboard = []
            for i in range(0, len(options), 2):
                row = [InlineKeyboardButton(options[i][0], callback_data=f"opt_{i}")]
                if i + 1 < len(options):
                    row.append(InlineKeyboardButton(options[i+1][0], callback_data=f"opt_{i+1}"))
                keyboard.append(row)
            return keyboard
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callback during onboarding"""
        query = update.callback_query
        telegram_id = update.effective_user.id
        state = self.get_state(telegram_id)
        
        callback_data = query.data
        
        # Handle intro buttons
        if callback_data.startswith('intro_'):
            await self._handle_intro(update, context, state)
            return
        
        # Handle resume
        if callback_data == 'resume_onboarding':
            await query.answer()
            if state['phase'] == 'INTRO':
                await self._show_intro_message(update, context, state['screen'])
            elif state['phase'] == 'PHASE_1':
                await self._show_phase_1_screen(update, context, state['screen'])
            elif state['phase'] == 'PHASE_2':
                await self._show_phase_2_screen(update, context, state['screen'])
            elif state['phase'] == 'PHASE_3':
                await self._show_phase_3_screen(update, context, state['screen'])
            elif state['phase'] == 'PHASE_4':
                await self._show_phase_4_screen(update, context, state['screen'])
            return
        
        # Handle option selection
        if callback_data.startswith('opt_'):
            await self._handle_option_selection(update, context, callback_data)
            return
        
        # Handle phase-specific callbacks
        if callback_data == 'start_conversational':
            await self._start_conversational_mode(update, context)
            return
    
    async def _handle_option_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle button option selection"""
        query = update.callback_query
        telegram_id = update.effective_user.id
        state = self.get_state(telegram_id)
        
        # Parse option index
        option_idx = int(callback_data.split('_')[1])
        
        # Get current screen config based on phase
        if state['phase'] == 'PHASE_1':
            screens = self._get_phase_1_screens()
            screen = screens[state['screen']]
            
            # Get selected value
            selected_text, selected_value = screen['options'][option_idx]
            
            # Store in temporary data
            data = state['data']
            data[screen['id']] = selected_value
            self.set_state(telegram_id, data=data)
            
            # Store in database
            await self._store_screen_data(telegram_id, screen, selected_value)
            
            # Move to next screen
            next_screen = state['screen'] + 1
            if next_screen < len(screens):
                await self._show_phase_1_screen(update, context, next_screen)
                self.set_state(telegram_id, screen=next_screen)
            else:
                # Phase 1 complete
                await self._transition_to_phase_2(update, context)
        
        elif state['phase'] == 'PHASE_2':
            screens = self._get_phase_2_screens()
            screen = screens[state['screen']]
            
            # Handle dynamic options
            if screen.get('options_dynamic'):
                if screen['id'] == 'city':
                    options = self._get_city_options(state['data'].get('country', 'Other'))
                else:
                    options = screen.get('options', [])
            else:
                options = screen.get('options', [])
            
            selected_text, selected_value = options[option_idx]
            
            # Store in temporary data
            data = state['data']
            data[screen['id']] = selected_value
            self.set_state(telegram_id, data=data)
            
            # Store in database
            await self._store_screen_data(telegram_id, screen, selected_value)
            
            # Move to next screen
            next_screen = state['screen'] + 1
            if next_screen < len(screens):
                await self._show_phase_2_screen(update, context, next_screen)
                self.set_state(telegram_id, screen=next_screen)
            else:
                # Phase 2 complete
                await self._transition_to_phase_3(update, context)
        
        elif state['phase'] == 'PHASE_3':
            screens = self._get_phase_3_screens()
            screen = screens[state['screen']]
            
            # Handle dynamic options
            if screen.get('options_dynamic'):
                if screen['id'] == 'income_bracket':
                    options = self._get_income_options(state['data'].get('country', 'Other'))
                elif screen['id'] in ['partner_age_min', 'partner_age_max']:
                    user_age = self._calculate_age(state['data'].get('date_of_birth', '01/01/2000'))
                    options = self._get_age_range_options(user_age, screen['id'] == 'partner_age_min')
                else:
                    options = screen.get('options', [])
            else:
                options = screen.get('options', [])
            
            selected_text, selected_value = options[option_idx]
            
            # Store in temporary data
            data = state['data']
            data[screen['id']] = selected_value
            self.set_state(telegram_id, data=data)
            
            # Store in database
            await self._store_screen_data(telegram_id, screen, selected_value)
            
            # Move to next screen
            next_screen = state['screen'] + 1
            if next_screen < len(screens):
                await self._show_phase_3_screen(update, context, next_screen)
                self.set_state(telegram_id, screen=next_screen)
            else:
                # Phase 3 complete
                await self._transition_to_phase_4(update, context)
        
        elif state['phase'] == 'PHASE_4':
            # Handle Phase 4 button presses (photo add/done, summary confirmation, etc.)
            if callback_data == 'add_photo':
                await query.answer()
                await query.edit_message_text(
                    "Great! Send me another photo 📸"
                )
            elif callback_data == 'photos_done':
                # Move to summary screen
                await query.answer()
                next_screen = state['screen'] + 1
                self.set_state(telegram_id, screen=next_screen)
                await self._show_phase_4_screen(update, context, next_screen)
            elif callback_data.startswith('phase4_'):
                # Generic Phase 4 screen progression
                await query.answer()
                next_screen = state['screen'] + 1
                self.set_state(telegram_id, screen=next_screen)
                await self._show_phase_4_screen(update, context, next_screen)
            elif callback_data == 'later':
                await query.answer()
                await query.edit_message_text(
                    "No problem! Come back whenever you're ready. Just send me a message and we'll continue from here. 🙏"
                )
    
    async def _store_screen_data(self, telegram_id: int, screen: Dict, value):
        """Store screen response in database"""
        if screen['store_as'] == 'column':
            # Store in users table column
            self.db.update_user_hard_filters(telegram_id, {screen['column']: value})
        elif screen['store_as'] == 'preference':
            # Store in user_preferences table
            # For now, store in conversation_state until preferences table is implemented
            state = self.db.get_conversation_state(telegram_id) or {}
            if 'preferences' not in state:
                state['preferences'] = {}
            state['preferences'][screen['id']] = value
            self.db.update_conversation_state(telegram_id, state)
        elif screen['store_as'] == 'signal':
            # Store in user_signals JSONB
            category = screen.get('category', 'lifestyle')
            signal_data = {
                screen['id']: {
                    'value': value,
                    'confidence': 1.0,  # Explicit from buttons
                    'source': 'explicit',
                    'captured_at': datetime.now().isoformat()
                }
            }
            self.db.upsert_user_signals(telegram_id, category, signal_data)
        elif screen['store_as'] == 'derived':
            # Special handling for derived fields (e.g., has_children with details)
            if screen['id'] == 'has_children':
                has_children = value != False
                self.db.update_user_hard_filters(telegram_id, {'has_children': has_children})
                # Store details in signals if needed
                if has_children:
                    signal_data = {
                        'children_living_situation': {
                            'value': value,
                            'confidence': 1.0,
                            'source': 'explicit'
                        }
                    }
                    self.db.upsert_user_signals(telegram_id, 'family_background', signal_data)
    
    async def _transition_to_phase_2(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Transition from Phase 1 to Phase 2"""
        telegram_id = update.effective_user.id
        
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "Those are the big ones ✓\n\nNow a few quick ones about you."
        )
        
        # Wait a moment, then show first Phase 2 screen
        import asyncio
        await asyncio.sleep(1.5)
        
        self.set_state(telegram_id, phase='PHASE_2', screen=0)
        await self._show_phase_2_screen(update, context, 0)
    
    # ============== PHASE 2: IDENTITY ==============
    
    def _get_phase_2_screens(self) -> List[Dict]:
        """Define Phase 2 screens (Identity)"""
        return [
            # I1: First Name (text input)
            {
                'id': 'first_name',
                "question": "What should I call you?",
                'type': 'text',
                'placeholder': 'Your first name...',
                'store_as': 'column',
                'column': 'first_name',
                'response': lambda name: f"Nice to meet you, {name} 👋"
            },
            # I2: Gender
            {
                'id': 'gender_identity',
                "question": "How do you identify?",
                'type': 'buttons',
                'options': [
                    ('Man', 'Male'),
                    ('Woman', 'Female'),
                    ('Non-binary', 'Non-binary'),
                    ('Prefer to describe', 'Other')
                ],
                'layout': 'double',
                'store_as': 'column',
                'column': 'gender_identity'
            },
            # I3: Orientation
            {
                'id': 'sexual_orientation',
                "question": "Who are you looking to meet?",
                'type': 'buttons',
                'options': [
                    ('Men', 'Men'),
                    ('Women', 'Women'),
                    ('Both', 'Both'),
                    ('Other', 'Other')
                ],
                'layout': 'double',
                'store_as': 'column',
                'column': 'sexual_orientation'
            },
            # I4: DOB (text input with validation)
            {
                'id': 'date_of_birth',
                'question': (
                    'When were you born? (DD/MM/YYYY)\n\n'
                    'I keep your exact date private — only your age shows to matches.'
                ),
                'type': 'text',
                'placeholder': 'DD/MM/YYYY',
                'validation': 'date',
                'store_as': 'column',
                'column': 'date_of_birth',
                'response': lambda dob: f"{self._calculate_age(dob)} — got it ✓"
            },
            # I5: Country
            {
                'id': 'country',
                "question": "Where are you based?",
                'type': 'buttons',
                'options': [
                    ('🇮🇳 India', 'India'),
                    ('🇦🇪 UAE', 'UAE'),
                    ('🇺🇸 USA', 'USA'),
                    ('🇬🇧 UK', 'UK'),
                    ('🇸🇬 Singapore', 'Singapore'),
                    ('🇸🇦 Saudi Arabia', 'Saudi Arabia'),
                    ('🇶🇦 Qatar', 'Qatar'),
                    ('🇧🇭 Bahrain', 'Bahrain'),
                    ('🇰🇼 Kuwait', 'Kuwait'),
                    ('🇵🇰 Pakistan', 'Pakistan'),
                    ('Other', 'Other')
                ],
                'layout': 'double',
                'store_as': 'column',
                'column': 'country'
            },
            # I6: City (dynamic by country)
            {
                'id': 'city',
                "question": "Which city?",
                'type': 'buttons',
                'options_dynamic': True,  # Options depend on country
                'store_as': 'column',
                'column': 'city'
            },
            # I7: Nationality/Ethnicity (text input)
            {
                'id': 'ethnicity',
                'question': "What's your nationality or ethnicity?",
                'type': 'text',
                'placeholder': 'e.g. Indian, Pakistani-American, British-Arab...',
                'store_as': 'column',
                'column': 'ethnicity'
            }
        ]
    
    def _calculate_age(self, dob_string: str) -> int:
        """Calculate age from DOB string"""
        try:
            dob = datetime.strptime(dob_string, '%d/%m/%Y').date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except:
            return 0
    
    async def _handle_phase_2(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
        """Handle Phase 2 (Identity) navigation"""
        telegram_id = update.effective_user.id
        screens = self._get_phase_2_screens()
        current_screen = screens[state['screen']]
        
        # Handle text input screens
        if current_screen.get('type') == 'text' and update.message and update.message.text:
            # Validate input if needed
            user_input = update.message.text.strip()
            
            if current_screen.get('validation') == 'date':
                # Validate date format
                if not self._validate_date(user_input):
                    await update.message.reply_text(
                        "Please enter a valid date in DD/MM/YYYY format (e.g., 15/03/1995)"
                    )
                    return
            
            # Store the input
            data = state['data']
            data[current_screen['id']] = user_input
            self.set_state(telegram_id, data=data)
            
            # Store in database
            await self._store_screen_data(telegram_id, current_screen, user_input)
            
            # Send response if defined
            if 'response' in current_screen:
                response = current_screen['response'](user_input) if callable(current_screen['response']) else current_screen['response']
                await update.message.reply_text(response)
            
            # Move to next screen
            import asyncio
            await asyncio.sleep(0.5)
            next_screen = state['screen'] + 1
            if next_screen < len(screens):
                await self._show_phase_2_screen(update, context, next_screen)
                self.set_state(telegram_id, screen=next_screen)
            else:
                # Phase 2 complete
                await self._transition_to_phase_3(update, context)
            return
        
        # Text during button phase - redirect
        if update.message and update.message.text:
            await update.message.reply_text(
                "Just tap one of the options above 👆"
            )
            return
    
    async def _show_phase_2_screen(self, update: Update, context: ContextTypes.DEFAULT_TYPE, screen_num: int):
        """Show a Phase 2 screen"""
        telegram_id = update.effective_user.id
        screens = self._get_phase_2_screens()
        state = self.get_state(telegram_id)
        data = state['data']
        
        if screen_num < len(screens):
            screen = screens[screen_num]
            
            # Handle text input screens
            if screen.get('type') == 'text':
                # Use ForceReply to request text input
                await update.message.reply_text(
                    screen['question'],
                    reply_markup=ForceReply(selective=True, input_field_placeholder=screen.get('placeholder', ''))
                )
            
            # Handle button screens
            elif screen.get('type') == 'buttons':
                # Handle dynamic options
                if screen.get('options_dynamic'):
                    if screen['id'] == 'city':
                        options = self._get_city_options(data.get('country', 'Other'))
                    else:
                        options = screen['options']
                else:
                    options = screen['options']
                
                keyboard = self._build_keyboard(options, screen['layout'])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                question = screen['question'](data) if callable(screen['question']) else screen['question']
                
                if update.callback_query:
                    await update.callback_query.answer()
                    await update.callback_query.edit_message_text(question, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(question, reply_markup=reply_markup)
        else:
            # Phase 2 complete
            await self._transition_to_phase_3(update, context)
    
    def _validate_date(self, date_string: str) -> bool:
        """Validate date format DD/MM/YYYY"""
        try:
            dob = datetime.strptime(date_string, '%d/%m/%Y').date()
            # Check age range (18-80)
            age = self._calculate_age(date_string)
            return 18 <= age <= 80
        except:
            return False
    
    # ============== PHASE 3: LIFESTYLE ==============
    
    def _get_phase_3_screens(self) -> List[Dict]:
        """Define Phase 3 screens (Lifestyle)"""
        return [
            # L1: Work Style
            {
                'id': 'work_style',
                'question': "What's your work situation?",
                'type': 'buttons',
                'options': [
                    ('Corporate / MNC', 'Corporate'),
                    ('Startup', 'Startup'),
                    ('Own business', 'Business owner'),
                    ('Freelance', 'Freelance'),
                    ('Government', 'Government'),
                    ('Student', 'Student'),
                    ('Between jobs', 'Between jobs'),
                    ('Prefer not to say', 'Prefer not to say')
                ],
                'layout': 'double',
                'store_as': 'signal',
                'category': 'lifestyle'
            },
            # L2: Education Level
            {
                'id': 'education_level',
                "question": "Highest education?",
                'type': 'buttons',
                'options': [
                    ('High school', 'High school'),
                    ("Bachelor's degree", 'Bachelors'),
                    ("Master's degree", 'Masters'),
                    ('PhD / Doctorate', 'PhD'),
                    ('Professional (MD, JD, CA, etc.)', 'Professional'),
                    ('Other', 'Other')
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'education_level'
            },
            # L3: Income Bracket (dynamic by country)
            {
                'id': 'income_bracket',
                'question': (
                    "Roughly what's your annual income range?\n\n"
                    "(This stays completely private — never shown to matches. "
                    "It helps me understand lifestyle compatibility.)"
                ),
                'type': 'buttons',
                'options_dynamic': True,  # Varies by country
                'store_as': 'column',
                'column': 'income_bracket'
            },
            # L4: Living Situation
            {
                'id': 'living_situation',
                "question": "Current living situation?",
                'type': 'buttons',
                'options': [
                    ('Live alone', 'Alone'),
                    ('With roommates', 'Roommates'),
                    ('With family', 'With family'),
                    ('Own my place', 'Own'),
                    ('Other', 'Other')
                ],
                'layout': 'single',
                'store_as': 'signal',
                'category': 'lifestyle'
            },
            # L5: Exercise / Fitness
            {
                'id': 'exercise_fitness',
                "question": "How active are you?",
                'type': 'buttons',
                'options': [
                    ('Very active — daily exercise', 'Very active'),
                    ('Active — few times a week', 'Active'),
                    ('Moderate — occasional', 'Moderate'),
                    ('Not very active', 'Sedentary')
                ],
                'layout': 'single',
                'store_as': 'signal',
                'category': 'lifestyle'
            },
            # L6: Social Energy
            {
                'id': 'social_energy',
                "question": "At a party, you're more likely to...",
                'type': 'buttons',
                'options': [
                    ('Work the room — love meeting new people', 'Extrovert'),
                    ('Stick with people I know', 'Ambivert'),
                    ('Find one person and have a deep convo', 'Selective'),
                    ('Wonder why I came', 'Introvert')
                ],
                'layout': 'single',
                'store_as': 'signal',
                'category': 'personality'
            },
            # L7: Travel
            {
                'id': 'travel_frequency',
                "question": "How much do you travel?",
                'type': 'buttons',
                'options': [
                    ('Homebody — love being home', 'Homebody'),
                    ('A few trips a year', 'Moderate traveler'),
                    ('Travel frequently', 'Frequent traveler'),
                    ('Digital nomad / constantly moving', 'Digital nomad')
                ],
                'layout': 'single',
                'store_as': 'signal',
                'category': 'lifestyle'
            },
            # L8: Pets
            {
                'id': 'pet_ownership',
                "question": "Pets?",
                'type': 'buttons',
                'options': [
                    ('Have pets 🐾', 'Has pets'),
                    ('Want pets', 'Wants pets'),
                    ('No pets, no plans', 'No pets'),
                    ('Allergies 😬', 'Allergic to pets')
                ],
                'layout': 'double',
                'store_as': 'signal',
                'category': 'lifestyle'
            },
            # L9: Substance Use
            {
                'id': 'substance_use',
                "question": "Any recreational substance use? (Cannabis, etc.)",
                'type': 'buttons',
                'options': [
                    ('Never', 'Never'),
                    ('Occasionally', 'Occasionally'),
                    ('Regularly', 'Regularly'),
                    ('Prefer not to say', 'Prefer not to say')
                ],
                'layout': 'single',
                'store_as': 'signal',
                'category': 'lifestyle'
            },
            # L10: Height
            {
                'id': 'height_cm',
                "question": "How tall are you? (Optional)",
                'type': 'buttons',
                'options': [
                    ("Under 5'2\" / <157cm", 155),
                    ("5'2\"–5'5\" / 157–165cm", 162),
                    ("5'5\"–5'8\" / 165–173cm", 169),
                    ("5'8\"–5'11\" / 173–180cm", 176),
                    ("5'11\"–6'1\" / 180–185cm", 182),
                    ("6'1\"+ / 185cm+", 188),
                    ('Skip', None)
                ],
                'layout': 'single',
                'store_as': 'column',
                'column': 'height_cm'
            },
            # L11: Partner Age Range (2-step)
            {
                'id': 'partner_age_min',
                "question": "What age range works for you in a partner?\n\nYoungest:",
                'type': 'buttons',
                'options_dynamic': True,  # Centered around user's age
                'store_as': 'preference'
            },
            {
                'id': 'partner_age_max',
                "question": "Oldest:",
                'type': 'buttons',
                'options_dynamic': True,  # Based on min selected
                'store_as': 'preference'
            },
            # L12: Location Flexibility
            {
                'id': 'location_flexibility',
                'question': lambda data: f"Does your partner need to be in {data.get('city', 'your city')}?",
                'type': 'buttons',
                'options': [
                    ('Same city only', 'same_city'),
                    ('Same country is fine', 'same_country'),
                    ('Open to distance', 'open_distance'),
                    ('Open to relocating', 'open_relocate')
                ],
                'layout': 'single',
                'store_as': 'preference'
            },
            # L13: Caste/Community (conditional)
            {
                'id': 'caste_community',
                'question': (
                    'Does community matter for your match?\n\n'
                    '(No judgment — just want to filter right for you)'
                ),
                'type': 'buttons',
                'condition': lambda data: (
                    data.get('country') in ['India', 'Pakistan', 'Bangladesh'] and
                    data.get('religion') in ['Hindu', 'Muslim', 'Sikh', 'Jain']
                ),
                'options': [
                    ('Must be same community', 'required'),
                    ('Prefer same, flexible', 'preferred'),
                    ("Doesn't matter at all", 'no_preference')
                ],
                'layout': 'single',
                'follow_up': {
                    'trigger': ['required', 'preferred'],
                    'type': 'text',
                    'question': "What's your community?",
                    'placeholder': 'e.g. Brahmin, Patel, Sunni, Rajput...'
                },
                'store_as': 'column',
                'column': 'caste_community'
            },
            # L14: Family Involvement (conditional)
            {
                'id': 'family_involvement',
                "question": "Is your family involved in your search?",
                'type': 'buttons',
                'condition': lambda data: (
                    data.get('country') in ['India', 'Pakistan', 'Bangladesh', 'UAE', 'Saudi Arabia', 'Qatar'] or
                    data.get('religion') in ['Muslim', 'Hindu', 'Sikh']
                ),
                'options': [
                    ('Yes, actively helping', 'active'),
                    ("They know I'm looking", 'aware'),
                    ("They don't know yet", 'not_aware'),
                    ('Keeping this private', 'private')
                ],
                'layout': 'single',
                'store_as': 'signal',
                'category': 'family_background'
            }
        ]
    
    async def _transition_to_phase_3(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Transition from Phase 2 to Phase 3"""
        telegram_id = update.effective_user.id
        user_name = self.db.get_user(telegram_id).get('first_name', 'there')
        
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            f"Almost there, {user_name} — you're flying through this ✓\n\n"
            f"A few more about your lifestyle and preferences, then we switch to the good stuff."
        )
        
        # Wait a moment, then show first Phase 3 screen
        import asyncio
        await asyncio.sleep(1.5)
        
        self.set_state(telegram_id, phase='PHASE_3', screen=0)
        await self._show_phase_3_screen(update, context, 0)
    
    async def _handle_phase_3(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
        """Handle Phase 3 (Lifestyle) navigation"""
        # Similar to Phase 1
        telegram_id = update.effective_user.id
        
        # Text during button phase - redirect
        if update.message and update.message.text:
            await update.message.reply_text(
                "Just tap one of the options above 👆"
            )
            return
    
    async def _show_phase_3_screen(self, update: Update, context: ContextTypes.DEFAULT_TYPE, screen_num: int):
        """Show a Phase 3 screen"""
        telegram_id = update.effective_user.id
        screens = self._get_phase_3_screens()
        state = self.get_state(telegram_id)
        data = state['data']
        
        # Check if this screen should be skipped (conditional)
        if screen_num < len(screens):
            screen = screens[screen_num]
            
            # Check condition
            if 'condition' in screen:
                if not screen['condition'](data):
                    # Skip this screen
                    next_screen = screen_num + 1
                    if next_screen < len(screens):
                        await self._show_phase_3_screen(update, context, next_screen)
                        self.set_state(telegram_id, screen=next_screen)
                    else:
                        # Phase 3 complete
                        await self._transition_to_phase_4(update, context)
                    return
            
            # Handle dynamic options
            if screen.get('options_dynamic'):
                if screen['id'] == 'income_bracket':
                    options = self._get_income_options(data.get('country', 'Other'))
                elif screen['id'] in ['partner_age_min', 'partner_age_max']:
                    user_age = self._calculate_age(data.get('date_of_birth', '01/01/2000'))
                    options = self._get_age_range_options(user_age, screen['id'] == 'partner_age_min')
                else:
                    options = screen['options']
            else:
                options = screen['options']
            
            # Show the screen
            keyboard = self._build_keyboard(options, screen['layout'])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            question = screen['question'](data) if callable(screen['question']) else screen['question']
            
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    question,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    question,
                    reply_markup=reply_markup
                )
        else:
            # Phase 3 complete
            await self._transition_to_phase_4(update, context)
    
    # ============== PHASE 4: PHOTO + CLOSE ==============
    
    def _get_phase_4_screens(self) -> List[Dict]:
        """Define Phase 4 screens (Photo + Close)"""
        return [
            # Transition message
            {
                'id': 'transition_to_photos',
                'type': 'message',
                'text': lambda data: (
                    f"That's all the quick questions done, {data.get('first_name', 'there')} ✓\n\n"
                    f"One last thing before we switch to conversation mode —"
                )
            },
            # P1: Photo Upload
            {
                'id': 'photos',
                'question': (
                    'I need at least one recent photo of you.\n\n'
                    'It stays private — only shared when I introduce you to a match, '
                    'and only with your approval.\n\n'
                    'Send me a clear photo where your face is visible 📸'
                ),
                'type': 'photo',
                'min_photos': 1,
                'response': 'Great photo ✓ Want to add more? Better photos = better first impressions.',
                'buttons': [
                    ('Add another photo', 'add_photo'),
                    ("That's enough", 'photos_done')
                ]
            },
            # P2: Quick Summary
            {
                'id': 'summary',
                'type': 'message',
                'text': lambda data: self._generate_summary(data),
                'button': "Looks good →"
            },
            # P3: THE TRANSITION (CRITICAL)
            {
                'id': 'final_transition',
                'type': 'message',
                'text': lambda data: (
                    f"You're in, {data.get('first_name', 'there')} ✓\n\n"
                    f"I now know your basics and your filters. That's about 25% of what "
                    f"I need to find you someone great.\n\n"
                    f"Here's what happens next:\n\n"
                    f"The quick-tap stuff tells me who to filter OUT.\n"
                    f"The conversation tells me who to filter IN.\n\n"
                    f"Starting now, I'll ask you real questions — the kind a good friend "
                    f"would ask if they were setting you up. Answer in your own words, "
                    f"whenever you feel like it.\n\n"
                    f"There's no rush. The more I understand you, the better your first "
                    f"introduction will be.\n\n"
                    f"Ready for the first one?"
                ),
                'buttons': [
                    ('Ask me something →', 'start_conversational'),
                    ("I'll come back later", 'later')
                ]
            }
        ]
    
    def _generate_summary(self, data: Dict) -> str:
        """Generate profile summary for user review"""
        name = data.get('first_name', 'You')
        age = data.get('age', '?')
        city = data.get('city', '?')
        country = data.get('country', '?')
        religion = data.get('religion', '?')
        practice = data.get('religious_practice_level', '')
        intent = data.get('relationship_intent', '?')
        orientation = data.get('sexual_orientation', '?')
        age_min = data.get('partner_age_min', '?')
        age_max = data.get('partner_age_max', '?')
        
        summary = (
            f"Here's a quick snapshot:\n\n"
            f"{name}, {age} · {city}, {country}\n"
            f"{religion}"
        )
        
        if practice:
            summary += f" ({practice})"
        
        summary += f" · Looking for {intent}\n"
        summary += f"{orientation} · {age_min}–{age_max}\n\n"
        summary += "If anything looks off, just tell me later in chat and I'll fix it instantly."
        
        return summary
    
    async def _transition_to_phase_4(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Transition from Phase 3 to Phase 4"""
        telegram_id = update.effective_user.id
        
        self.set_state(telegram_id, phase='PHASE_4', screen=0)
        await self._show_phase_4_screen(update, context, 0)
    
    async def _handle_phase_4(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: Dict):
        """Handle Phase 4 (Photo + Close) navigation"""
        telegram_id = update.effective_user.id
        
        # Check if this is a photo upload
        if update.message and update.message.photo:
            await self._handle_photo_upload(update, context)
            return
        
        # Text during button phase - redirect
        if update.message and update.message.text:
            await update.message.reply_text(
                "Just tap one of the options above 👆"
            )
            return
    
    async def _show_phase_4_screen(self, update: Update, context: ContextTypes.DEFAULT_TYPE, screen_num: int):
        """Show a Phase 4 screen"""
        telegram_id = update.effective_user.id
        screens = self._get_phase_4_screens()
        state = self.get_state(telegram_id)
        data = state['data']
        
        if screen_num < len(screens):
            screen = screens[screen_num]
            
            # Handle different screen types
            if screen['type'] == 'message':
                text = screen['text'](data) if callable(screen['text']) else screen['text']
                
                if 'button' in screen:
                    keyboard = [[InlineKeyboardButton(screen['button'], callback_data=f"phase4_{screen_num}")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                elif 'buttons' in screen:
                    keyboard = [[InlineKeyboardButton(btn[0], callback_data=btn[1]) for btn in screen['buttons']]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                else:
                    reply_markup = None
                
                if update.callback_query:
                    await update.callback_query.answer()
                    if reply_markup:
                        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
                    else:
                        await update.callback_query.edit_message_text(text)
                else:
                    await update.message.reply_text(text, reply_markup=reply_markup)
            
            elif screen['type'] == 'photo':
                # Request photo upload
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(screen['question'])
        else:
            # Phase 4 complete - should not reach here
            await self._start_conversational_mode(update, context)
    
    async def _handle_photo_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo upload during Phase 4"""
        telegram_id = update.effective_user.id
        state = self.get_state(telegram_id)
        
        # Get photo file_id (largest size)
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Store photo file_id in database
        # TODO: Implement photo storage
        
        # Increment photo count
        photo_count = state['photo_count'] + 1
        self.set_state(telegram_id, photo_count=photo_count)
        
        # Show add-more prompt
        keyboard = [
            [
                InlineKeyboardButton("Add another photo", callback_data="add_photo"),
                InlineKeyboardButton("That's enough", callback_data="photos_done")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Great photo ✓ Want to add more? Better photos = better first impressions.",
            reply_markup=reply_markup
        )
    
    # ============== CONVERSATIONAL TRANSITION ==============
    
    async def _start_conversational_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Transition to conversational mode"""
        query = update.callback_query
        telegram_id = update.effective_user.id
        user_name = self.db.get_user(telegram_id).get('first_name', 'there')
        
        await query.answer()
        await query.edit_message_text(
            f"Okay {user_name}, here's one I love asking —\n\n"
            f"Describe your ideal Saturday. Not the Instagram version — the real one. "
            f"What does a genuinely great day off look like for you?"
        )
        
        # Mark onboarding complete
        self.set_state(telegram_id, phase='CONVERSATIONAL', screen=0)
        
        # Mark MVP achieved (button phase complete)
        self.db.execute_query(
            "UPDATE user_tier_progress SET mvp_achieved = TRUE WHERE telegram_id = %s",
            (telegram_id,)
        )
    
    # ============== HELPER METHODS ==============
    
    def _get_city_options(self, country: str) -> List[Tuple[str, str]]:
        """Get city options based on country"""
        city_maps = {
            'UAE': [
                ('Dubai', 'Dubai'),
                ('Abu Dhabi', 'Abu Dhabi'),
                ('Sharjah', 'Sharjah'),
                ('Other', 'Other')
            ],
            'India': [
                ('Mumbai', 'Mumbai'),
                ('Delhi NCR', 'Delhi NCR'),
                ('Bangalore', 'Bangalore'),
                ('Hyderabad', 'Hyderabad'),
                ('Chennai', 'Chennai'),
                ('Pune', 'Pune'),
                ('Kolkata', 'Kolkata'),
                ('Other', 'Other')
            ],
            'USA': [
                ('New York', 'New York'),
                ('Los Angeles', 'Los Angeles'),
                ('Chicago', 'Chicago'),
                ('San Francisco', 'San Francisco'),
                ('Other', 'Other')
            ]
            # Add more country-city mappings
        }
        
        return city_maps.get(country, [('Other', 'Other')])
    
    def _get_income_options(self, country: str) -> List[Tuple[str, str]]:
        """Get income bracket options based on country"""
        if country == 'India':
            return [
                ('Under ₹10L', '<10L'),
                ('₹10L–₹25L', '10L-25L'),
                ('₹25L–₹50L', '25L-50L'),
                ('₹50L–₹1Cr', '50L-1Cr'),
                ('₹1Cr+', '>1Cr'),
                ('Prefer not to say', 'not_specified')
            ]
        else:
            # USD/AED/GBP markets
            return [
                ('Under $50K', '<50K'),
                ('$50K–$100K', '50K-100K'),
                ('$100K–$200K', '100K-200K'),
                ('$200K–$500K', '200K-500K'),
                ('$500K+', '>500K'),
                ('Prefer not to say', 'not_specified')
            ]
    
    def _get_age_range_options(self, user_age: int, is_min: bool) -> List[Tuple[str, int]]:
        """Generate age range options centered around user's age"""
        if is_min:
            # Min age: user_age - 10 to user_age + 5
            start = max(18, user_age - 10)
            end = user_age + 5
        else:
            # Max age: user_age - 5 to user_age + 15
            start = user_age - 5
            end = min(80, user_age + 15)
        
        options = [(str(age), age) for age in range(start, end + 1, 2)]
        return options
