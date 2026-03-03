"""
Masii Telegram Bot - Webhook Entry Point for Fly.io
Production deployment using webhooks instead of polling.
Also serves the web form intake API endpoint.
"""

import os
import json
import logging
from dotenv import load_dotenv
from aiohttp import web

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Import handlers from bot.py
from bot import (
    start_command,
    help_command,
    progress_command,
    handle_message,
    handle_photo,
    handle_callback_query,
    handle_sticker,
    error_handler
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============== CORS MIDDLEWARE ==============

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


@web.middleware
async def cors_middleware(request, handler):
    """Handle CORS for web form requests"""
    origin = request.headers.get("Origin", "")

    if request.method == "OPTIONS":
        resp = web.Response(status=204)
    else:
        resp = await handler(request)

    resp.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp


# ============== WEB FORM INTAKE ==============

async def web_intake(request):
    """
    POST /api/intake — Receive all 36-guna answers from the web form.
    Payload: { phone, name, answers: { field: { value, table } }, meta: { intent, ... } }
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    phone = data.get("phone", "").strip()
    name = data.get("name", "").strip()
    answers = data.get("answers", {})
    meta = data.get("meta", {})

    if not phone:
        return web.json_response({"error": "Phone number is required"}, status=400)
    if not answers:
        return web.json_response({"error": "No answers provided"}, status=400)

    try:
        user_id = db_adapter.get_or_create_user_by_phone(phone, name, channel="web")
        db_adapter.save_web_intake(user_id, answers, meta)
        logger.info(f"Web intake saved for user {user_id} (phone: {phone})")
        return web.json_response({"status": "ok", "user_id": str(user_id)})
    except Exception as e:
        logger.error(f"Web intake error: {e}")
        return web.json_response({"error": "Internal server error"}, status=500)


async def health_check(request):
    """Health check endpoint for Fly.io"""
    return web.Response(text="OK", status=200)


async def telegram_webhook(request):
    """Handle incoming webhook updates from Telegram"""
    try:
        update_data = await request.json()
        update = Update.de_json(update_data, application.bot)
        await application.update_queue.put(update)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)


async def on_startup(app):
    """Initialize bot on startup"""
    global application, db_adapter, onboarding_handler
    
    import bot
    from db_adapter import DatabaseAdapter
    from onboarding_handler import OnboardingHandler
    
    # Get configuration
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")
    
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("WEBHOOK_URL not set in environment")
    
    # Initialize database adapter
    db_adapter = DatabaseAdapter()
    
    # Initialize onboarding handler
    onboarding_handler = OnboardingHandler(db_adapter)
    
    # CRITICAL: Update bot.py's module-level globals so imported handlers can access them
    bot.db_adapter = db_adapter
    bot.onboarding_handler = onboarding_handler
    
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
    
    # Initialize the bot
    await application.initialize()
    await application.start()
    
    # Set webhook
    await application.bot.set_webhook(
        url=f"{webhook_url}/telegram",
        allowed_updates=Update.ALL_TYPES
    )
    
    logger.info(f"Bot started with webhook: {webhook_url}/telegram")


async def on_shutdown(app):
    """Cleanup on shutdown"""
    await application.stop()
    await application.shutdown()
    logger.info("Bot stopped")


def main():
    """Start the webhook server"""
    # Create aiohttp application with CORS middleware
    app = web.Application(middlewares=[cors_middleware])

    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_post('/telegram', telegram_webhook)
    app.router.add_post('/api/intake', web_intake)
    app.router.add_route('OPTIONS', '/api/intake', web_intake)  # CORS preflight
    
    # Register startup/shutdown handlers
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Get port from environment
    port = int(os.getenv('PORT', 8080))
    
    # Run server
    logger.info(f"Starting webhook server on port {port}")
    web.run_app(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
