"""
Jodi V2 - Telegram Matchmaker Bot
4-Tier Data Capture Framework with Confidence Scoring

Entry point for users: message the bot, start chatting.
"""

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import json
from datetime import datetime

from db_postgres_v2 import JodiDB
from conversation_v2 import ConversationOrchestratorV2
from matching import ContextualMatcher
from onboarding_flow import OnboardingFlow

# Load environment variables
load_dotenv()

# Global references (will be initialized in main())
db = None
conv = None
matcher = None
onboarding = None


# ============== COMMAND HANDLERS ==============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    telegram_id = user.id
    
    # Create or get user
    db_user = db.get_user(telegram_id)
    if not db_user:
        db.create_user(telegram_id, user.username, user.first_name)
        # Increment session count
        db.update_tier_progress(telegram_id, session_increment=True)
    else:
        # Returning user - increment session count
        db.update_tier_progress(telegram_id, session_increment=True)
    
    # Start or resume onboarding flow
    await onboarding.start_onboarding(update, context)


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command - show profile completion status"""
    telegram_id = update.effective_user.id
    
    summary = conv.get_progress_summary(telegram_id)
    await update.message.reply_text(summary)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "**Jodi - Your Matchmaking Companion** 🙏\n\n"
        "**Commands:**\n"
        "/start - Start or continue your journey\n"
        "/progress - See your profile completion\n"
        "/matches - See your potential matches\n"
        "/help - Show this help message\n\n"
        "**How it works:**\n"
        "1. We chat naturally and I get to know you\n"
        "2. I understand what you're looking for\n"
        "3. Once your profile is complete (you'll know when!), I'll show you matches\n"
        "4. If both sides are interested, I'll introduce you\n\n"
        "Just talk to me naturally — no forms, no interrogations. 💫"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


# ============== MESSAGE HANDLER ==============

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main conversation handler - processes user messages through V2 orchestrator.
    
    Flow:
    1. Check if user is in onboarding mode
    2. If onboarding: handle via onboarding flow
    3. If conversational: process through orchestrator (extraction + routing + progress tracking)
    4. Send bot response
    5. Check MVP status and offer matches if ready
    6. Store conversation turn
    """
    user = update.effective_user
    telegram_id = user.id
    user_message = update.message.text
    
    print(f"📥 [STAGE 1] Message received from {telegram_id}: '{user_message[:100]}'")
    
    # Ensure user exists
    print(f"🔍 [STAGE 2] Looking up user {telegram_id} in database...")
    db_user = db.get_user(telegram_id)
    if not db_user:
        print(f"✨ [STAGE 2] User not found, creating new user...")
        await start(update, context)
        print(f"✅ [STAGE 2] New user created and welcomed")
        return
    print(f"✅ [STAGE 2] User found")
    
    # Check if user is in onboarding mode
    print(f"🔍 [STAGE 2.5] Checking onboarding status...")
    if not onboarding.is_onboarding_complete(telegram_id):
        print(f"📋 [STAGE 2.5] User in onboarding mode, routing to onboarding handler")
        handled = await onboarding.handle_message(update, context)
        if handled:
            print(f"✅ [STAGE 2.5] Onboarding handler processed message")
            return
        print(f"➡️ [STAGE 2.5] Onboarding complete, falling through to conversational mode")
    else:
        print(f"✅ [STAGE 2.5] User in conversational mode")
    
    # Get conversation history
    print(f"📚 [STAGE 3] Retrieving conversation history...")
    conversation_history = _get_conversation_history(telegram_id)
    print(f"✅ [STAGE 3] Retrieved {len(conversation_history)} history messages")
    
    # Add current message to history
    conversation_history.append({
        'role': 'user',
        'content': user_message
    })
    print(f"✅ [STAGE 3] Added current message to history")
    
    # Process message through V2 orchestrator
    print(f"🤖 [STAGE 4] Calling conversation orchestrator...")
    try:
        result = conv.process_user_message(
            telegram_id=telegram_id,
            user_message=user_message,
            conversation_history=conversation_history
        )
        print(f"✅ [STAGE 4] Orchestrator returned successfully")
        print(f"   - Extracted data keys: {list(result.get('extracted_data', {}).keys())}")
        tier_prog = result.get('tier_progress', {})
        print(f"   - Tier progress: T1={tier_prog.get('tier1_completion')}%, T2={tier_prog.get('tier2_completion')}%")
        print(f"   - Completeness: {result.get('completeness')}%")
        print(f"   - MVP status: {result.get('mvp_status', {}).get('meets_mvp')}")
    except Exception as e:
        # Log error and send fallback response
        print(f"❌ [STAGE 4] Orchestrator failed with error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            "I'm having a bit of trouble understanding right now. "
            "Could you try saying that again? 🙏"
        )
        return
    
    # Send bot's response
    print(f"💬 [STAGE 5] Sending bot response...")
    next_message = result['next_message']
    await update.message.reply_text(next_message)
    print(f"✅ [STAGE 5] Response sent: '{next_message[:100]}'")
    
    # Store conversation turn
    print(f"💾 [STAGE 6] Storing conversation turn...")
    conversation_history.append({
        'role': 'assistant',
        'content': next_message
    })
    _save_conversation_history(telegram_id, conversation_history)
    print(f"✅ [STAGE 6] Conversation stored")
    
    print(f"✅ [COMPLETE] Message processing finished for {telegram_id}")
    
    # Check MVP status
    mvp_status = result.get('mvp_status')
    if mvp_status and mvp_status.get('meets_mvp'):
        # Just achieved MVP - celebrate and offer matches
        tier_progress = db.get_tier_progress(telegram_id)
        
        # Check if this is the first time achieving MVP
        if tier_progress and not tier_progress.get('mvp_achieved'):
            await update.message.reply_text(
                "🎉 **Congratulations!**\n\n"
                "Your profile is complete and ready for matching!\n\n"
                "Let me look through the community and find some great matches for you..."
            )
            
            # Find and present matches
            await find_and_present_matches(update, context, telegram_id)
    
    # Optional: Show progress nudge periodically
    completeness = result.get('completeness', 0)
    if completeness < 45 and _should_show_progress_nudge(telegram_id):
        blocked_reasons = mvp_status.get('blocked_reasons', []) if mvp_status else []
        if blocked_reasons:
            nudge_text = f"💡 You're {completeness:.0f}% complete. Almost there!"
            await update.message.reply_text(nudge_text)


# ============== MATCHING FUNCTIONS ==============

async def find_and_present_matches(update: Update, context: ContextTypes.DEFAULT_TYPE, telegram_id: int):
    """Find matches and present them to the user"""
    user_profile = db.get_full_profile(telegram_id)
    
    # Get all other users with complete profiles
    # Note: Simplified - in production, filter by profile_active=TRUE
    all_profiles = db.get_all_profiles()
    
    # Convert V2 profile format to V1 format for matcher
    # TODO: Update matcher to work with V2 schema
    v1_profile = _convert_profile_v2_to_v1(user_profile)
    v1_all_profiles = [_convert_profile_v2_to_v1(p) for p in all_profiles if p]
    
    # Find matches
    matches = matcher.find_matches(v1_profile, v1_all_profiles, min_score=40.0, limit=5)
    
    if not matches:
        await update.message.reply_text(
            "I haven't found any strong matches yet, but don't worry! "
            "As more people join and I learn more about what you're looking for, "
            "I'll keep looking.\n\n"
            "I'll notify you when I find someone promising. 🙏"
        )
        return
    
    # Store matches in database
    for match_profile, score, breakdown in matches:
        # Get telegram_id from V1 format profile
        match_telegram_id = match_profile.get('telegram_id')
        if match_telegram_id:
            db.create_match(
                telegram_id,
                match_telegram_id,
                score,
                breakdown
            )
    
    # Present top match
    top_match_profile, top_score, top_breakdown = matches[0]
    match_demo = top_match_profile.get('demographics', {})
    
    match_text = (
        f"I found {len(matches)} potential matches for you!\n\n"
        f"Here's someone I think you should meet:\n\n"
        f"📍 {match_demo.get('location', 'Location not specified')}\n"
        f"💼 {match_demo.get('occupation', 'Occupation not specified')}\n"
        f"🎂 {match_demo.get('age', 'Age not specified')} years old\n"
        f"🗣️ {match_demo.get('language', 'Language not specified')}\n\n"
        f"Match score: {top_score:.1f}/100\n\n"
        f"Why I think you'd connect:\n"
    )
    
    # Add breakdown highlights
    for key, value in top_breakdown.items():
        if value > 0 and key != 'total':
            match_text += f"• {key.replace('_', ' ').title()}: +{value}\n"
    
    # Add action buttons
    keyboard = [
        [
            InlineKeyboardButton("👍 Interested", callback_data=f"match_yes_{top_match_profile.get('telegram_id')}"),
            InlineKeyboardButton("👎 Pass", callback_data=f"match_no_{top_match_profile.get('telegram_id')}")
        ],
        [InlineKeyboardButton("🔍 See more matches", callback_data="see_more_matches")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(match_text, reply_markup=reply_markup)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries (button presses)"""
    query = update.callback_query
    telegram_id = update.effective_user.id
    data = query.data
    
    # Check if this is an onboarding callback
    if not onboarding.is_onboarding_complete(telegram_id):
        await onboarding.handle_callback(update, context)
        return
    
    # Otherwise, handle match-related callbacks
    await handle_match_response(update, context)


async def handle_match_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's response to a match (interested/pass)"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    data = query.data
    
    if data.startswith("match_yes_"):
        match_telegram_id = int(data.split("_")[2])
        
        # Update match status
        matches = db.get_matches_for_user(telegram_id)
        match = next((m for m in matches if m.get('status') == 'proposed' and 
                     (m.get('user_b') == match_telegram_id or m.get('user_a') == match_telegram_id)), None)
        
        if match:
            db.update_match_status(match['id'], "interested")
        
        await query.edit_message_text(
            "Great! I'll let them know you're interested. 💫\n\n"
            "If they're also interested, I'll introduce you both!"
        )
        
        # TODO: Notify the other person
    
    elif data.startswith("match_no_"):
        match_telegram_id = int(data.split("_")[2])
        
        matches = db.get_matches_for_user(telegram_id)
        match = next((m for m in matches if m.get('status') == 'proposed' and 
                     (m.get('user_b') == match_telegram_id or m.get('user_a') == match_telegram_id)), None)
        
        if match:
            db.update_match_status(match['id'], "rejected")
        
        await query.edit_message_text(
            "No problem! I'll keep looking for better matches. 🙏"
        )
    
    elif data == "see_more_matches":
        # Show next match
        matches = db.get_matches_for_user(telegram_id)
        proposed_matches = [m for m in matches if m.get('status') == 'proposed']
        
        if len(proposed_matches) > 1:
            await query.edit_message_text(
                "Here's another person I think you might like...\n\n"
                "(Showing next match - implementation pending)"
            )
        else:
            await query.edit_message_text(
                "That's all the matches I have for you right now.\n\n"
                "I'll keep looking and let you know when I find more! 🌟"
            )


async def matches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /matches command - show existing matches"""
    telegram_id = update.effective_user.id
    
    # Check if MVP achieved
    profile = db.get_full_profile(telegram_id)
    mvp_status = profile.get('mvp_status') if profile else None
    
    if not mvp_status or not mvp_status.get('meets_mvp'):
        # Profile not complete yet
        completeness = profile.get('completeness', 0) if profile else 0
        blocked_reasons = mvp_status.get('blocked_reasons', []) if mvp_status else []
        
        response = (
            f"Your profile is {completeness:.0f}% complete.\n\n"
            "I need a bit more information before I can show you matches.\n\n"
        )
        
        if blocked_reasons:
            response += "**Still need:**\n"
            for reason in blocked_reasons[:3]:
                response += f"• {reason}\n"
            response += "\nKeep chatting with me — we're almost there! 💫"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return
    
    # Profile complete - show matches
    matches = db.get_matches_for_user(telegram_id)
    proposed_matches = [m for m in matches if m.get('status') == 'proposed']
    
    if not proposed_matches:
        await update.message.reply_text(
            "No matches yet! I'm still looking. 🔍\n\n"
            "I'll notify you when I find someone promising."
        )
    else:
        await update.message.reply_text(
            f"You have {len(proposed_matches)} potential matches.\n\n"
            "Let me show you the first one..."
        )
        # TODO: Present matches one by one


# ============== HELPER FUNCTIONS ==============

def _get_conversation_history(telegram_id: int, limit: int = 10) -> list:
    """Retrieve recent conversation history for context."""
    state = db.get_conversation_state(telegram_id)
    if not state:
        return []
    
    history = state.get('conversation_history', [])
    return history[-limit:] if len(history) > limit else history


def _save_conversation_history(telegram_id: int, history: list):
    """Save conversation history to database."""
    state = db.get_conversation_state(telegram_id) or {}
    state['conversation_history'] = history[-50:]  # Keep last 50 messages
    state['message_count'] = state.get('message_count', 0) + 1
    db.update_conversation_state(telegram_id, state)


def _should_show_progress_nudge(telegram_id: int) -> bool:
    """Determine if we should show a progress nudge."""
    state = db.get_conversation_state(telegram_id) or {}
    message_count = state.get('message_count', 0)
    last_nudge = state.get('last_progress_nudge', 0)
    
    # Show every 5 messages, but not if shown in last 3
    if message_count % 5 == 0 and (message_count - last_nudge) >= 3:
        state['last_progress_nudge'] = message_count
        db.update_conversation_state(telegram_id, state)
        return True
    
    return False


def _convert_profile_v2_to_v1(profile_v2: dict) -> dict:
    """
    Convert V2 profile format to V1 format for matcher compatibility.
    
    TODO: Update matching.py to work directly with V2 schema.
    This is a temporary bridge.
    """
    if not profile_v2:
        return {}
    
    user = profile_v2.get('user', {})
    signals = profile_v2.get('signals', {})
    
    # Extract demographics from V2 schema
    demographics = {
        'age': user.get('age'),
        'location': user.get('city'),
        'occupation': user.get('occupation'),
        'language': user.get('native_languages', [None])[0] if user.get('native_languages') else None,
        'caste': user.get('caste_community'),
        'vegetarian': user.get('dietary_restrictions') == 'Vegetarian',
        'religion': user.get('religion')
    }
    
    # Extract preferences (simplified)
    preferences = {}
    
    # Extract signals (simplified - just surface level for now)
    extracted_signals = []
    
    return {
        'telegram_id': user.get('telegram_id'),
        'demographics': demographics,
        'preferences': preferences,
        'signals': extracted_signals
    }


# ============== MAIN APPLICATION ==============

def main():
    """Start the bot"""
    global db, conv, matcher, onboarding
    
    print("🔧 Initializing Jodi V2 with Onboarding Flow...")
    
    # Check required environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("⚠️  WARNING: ANTHROPIC_API_KEY not found!")
    
    # Initialize components
    print("   Initializing database...")
    try:
        db = JodiDB()
        print("   ✅ Database connected")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return
    
    print("   Initializing onboarding flow...")
    try:
        onboarding = OnboardingFlow(db)
        print("   ✅ Onboarding flow initialized")
    except Exception as e:
        print(f"   ❌ Onboarding initialization failed: {e}")
        return
    
    print("   Initializing conversation orchestrator...")
    try:
        conv = ConversationOrchestratorV2(
            anthropic_api_key=anthropic_key,
            model='claude-sonnet-4-20250514'
        )
        print("   ✅ Orchestrator initialized")
    except Exception as e:
        print(f"   ❌ Orchestrator initialization failed: {e}")
        return
    
    print("   Initializing matcher...")
    try:
        matcher = ContextualMatcher()
        print("   ✅ Matcher initialized")
    except Exception as e:
        print(f"   ❌ Matcher initialization failed: {e}")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CommandHandler("matches", matches_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))  # Handle all button presses
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))  # Handle photo uploads
    
    # Start bot
    print("🚀 Jodi V2 bot is running...")
    print("   Model: claude-sonnet-4-20250514")
    print("   Database: Connected to Supabase")
    print("   Press Ctrl+C to stop.")
    print("")
    print("   Initializing polling...")
    
    try:
        print("   Calling run_polling() with close_loop=False...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # Clear any pending updates on start
            close_loop=False  # Don't close the event loop on stop
        )
        print("   run_polling() returned (this should never happen!)")
    except KeyboardInterrupt:
        print("\n   Bot stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Bot crashed with error: {e}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise to see the error in logs
    finally:
        print("   Cleaning up...")
    
    print("   main() function exiting (this should never happen!)")


if __name__ == "__main__":
    main()
