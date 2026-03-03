"""
JODI Telegram Bot - Main Entry Point
Handles Telegram bot initialization and message routing
"""

import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from onboarding_handler import OnboardingHandler
from db_adapter import DatabaseAdapter
from config import ERROR_MESSAGES

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global instances
db_adapter = None
onboarding_handler = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await onboarding_handler.start_onboarding(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """**Jodi - Your Matchmaking Companion** 🙏

**Commands:**
/start - Start or continue your journey
/progress - See your profile completion
/help - Show this help message

**How it works:**
1. I'll ask you some quick questions (about 10 minutes)
2. Then we'll have real conversations to understand what you're looking for
3. When I find someone promising, I'll introduce you
4. No swiping. No endless scrolling. Just thoughtful introductions.

Just tap the buttons to answer questions, and we'll chat naturally after that. 💫"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command"""
    telegram_id = update.effective_user.id
    
    # Get session
    session = db_adapter.get_session(telegram_id)
    
    if not session:
        await update.message.reply_text(
            "You haven't started yet! Send /start to begin your journey."
        )
        return
    
    current_q = session.get('current_question', 0)
    total_q = 77
    skip_count = len(session.get('skip_questions', []))
    actual_total = total_q - skip_count
    
    completion_pct = (current_q / actual_total * 100) if actual_total > 0 else 0
    
    # Get profile completion from DB
    profile_completion = db_adapter.get_profile_completion(telegram_id)
    
    progress_text = f"""**Your Progress** 📊

**Onboarding Questions:** {current_q}/{actual_total} ({completion_pct:.0f}%)
**Profile Completion:** {profile_completion['completion']}%

{f"**Still need:** {', '.join(profile_completion['missing'][:5])}" if profile_completion['missing'] else "**Profile complete!** ✓"}

Keep going — the more I know, the better your matches will be! 🎯"""
    
    await update.message.reply_text(progress_text, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    telegram_id = update.effective_user.id
    session = db_adapter.get_session(telegram_id)
    
    if not session:
        # No active session
        await update.message.reply_text(
            "Hey! Send /start to begin, or /help if you need guidance."
        )
        return
    
    current_section = session.get('current_section', '')
    
    # Route based on current section
    if current_section in ['identity_basics', 'location_mobility', 'religion_culture',
                           'education_career', 'financial', 'family', 'lifestyle',
                           'partner_prefs', 'values', 'dealbreakers']:
        # In button-based onboarding
        await onboarding_handler.handle_text_input(update, context)
    
    elif current_section == 'conversational':
        # In conversational mode (to be implemented later)
        await update.message.reply_text(
            "Conversational mode coming soon! For now, complete the quick questions first."
        )
    
    else:
        await update.message.reply_text(
            "Hmm, I'm not sure what to do with that. Try /help if you're stuck."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    telegram_id = update.effective_user.id
    session = db_adapter.get_session(telegram_id)
    
    if not session:
        await update.message.reply_text("Send /start first to begin your journey!")
        return
    
    current_section = session.get('current_section', '')
    
    if current_section == 'photo_upload':
        # Get largest photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Get file
        file = await context.bot.get_file(file_id)
        
        # In production, upload to cloud storage (S3, etc.)
        # For now, store file_id
        photo_url = f"telegram_file:{file_id}"
        
        # Save to database
        db_adapter.save_photo_url(telegram_id, photo_url)
        
        # Update session
        if 'photo_urls' not in session:
            session['photo_urls'] = []
        session['photo_urls'].append(photo_url)
        db_adapter.save_session(session)
        
        # Check if user has uploaded enough photos
        photo_count = len(session['photo_urls'])
        
        if photo_count >= 1:
            # Show option to add more or continue
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = [[
                InlineKeyboardButton("Add another photo", callback_data="photo_add_more"),
                InlineKeyboardButton("That's enough", callback_data="photo_done")
            ]]
            
            await update.message.reply_text(
                f"Great photo ✓ ({photo_count} uploaded)\n\nWant to add more? Better photos = better first impressions.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                "Thanks! Send another photo, or send /done when you're ready to continue."
            )
    else:
        await update.message.reply_text(
            "Hold that thought! We'll get to photos after the quick questions. 📸"
        )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    data = query.data
    
    if data.startswith('photo_'):
        # Photo-related callbacks
        if data == 'photo_add_more':
            await query.answer("Send another photo!")
        elif data == 'photo_done':
            await query.answer()
            await _finish_photo_upload(query, context)
    else:
        # Onboarding button callbacks
        await onboarding_handler.handle_button_callback(update, context)


async def _finish_photo_upload(query, context: ContextTypes.DEFAULT_TYPE):
    """Complete photo upload and show summary"""
    telegram_id = query.from_user.id
    session = db_adapter.get_session(telegram_id)
    
    # Get user's first name
    user = db_adapter.get_user(telegram_id)
    name = user.get('first_name', query.from_user.first_name) if user else query.from_user.first_name
    
    # Build summary
    from config import FINAL_TRANSITION
    
    summary_text = FINAL_TRANSITION.format(name=name)
    
    # Show transition to conversational mode
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [[
        InlineKeyboardButton("Ask me something →", callback_data="start_conversational"),
        InlineKeyboardButton("I'll come back later", callback_data="pause_onboarding")
    ]]
    
    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text=summary_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # Update session
    session['current_section'] = 'conversational'
    session['onboarding_complete'] = True
    db_adapter.save_session(session)


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stickers during onboarding"""
    telegram_id = update.effective_user.id
    session = db_adapter.get_session(telegram_id)
    
    if session and session.get('current_section') in ['identity_basics', 'location_mobility', 
                                                       'religion_culture', 'education_career',
                                                       'financial', 'family', 'lifestyle',
                                                       'partner_prefs', 'values', 'dealbreakers']:
        # User sent sticker during button phase
        await update.message.reply_text(ERROR_MESSAGES['sticker_during_buttons'])
    else:
        # In conversational mode - it's okay
        await update.message.reply_text("😄 Nice one!")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    import traceback
    
    # Log full error with traceback
    logger.error(f"Update {update} caused error: {context.error}")
    logger.error(f"Error type: {type(context.error).__name__}")
    logger.error(f"Full traceback:\n{''.join(traceback.format_exception(type(context.error), context.error, context.error.__traceback__))}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Oops, something went wrong on my end. Let me try that again. If this keeps happening, send /help."
        )


def main():
    """Start the bot"""
    global db_adapter, onboarding_handler
    
    # Get Telegram bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")
    
    # Initialize database adapter
    db_adapter = DatabaseAdapter()
    
    # Initialize onboarding handler
    onboarding_handler = OnboardingHandler(db_adapter)
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("progress", progress_command))
    
    # Register callback query handler (for buttons)
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Register message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting JODI bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
