"""
Daily Matching Cron — Ties together matcher + delivery.

Run modes:
    1. `python cron.py`            — Full cycle: match + deliver
    2. `python cron.py --match`    — Only run matching (create match records)
    3. `python cron.py --deliver`  — Only run delivery (offer + introduce)
    4. `python cron.py --dry-run`  — Print what would happen, no DB writes

Schedule:
    Matching: Once daily (e.g., 2am IST via cron or Fly.io scheduled machine)
    Delivery: Every hour (check for pending offers, expirations, responses)

Environment variables:
    DATABASE_URL       — Supabase Postgres connection string
    TELEGRAM_BOT_TOKEN — For sending match offers via Telegram
    SMTP_HOST          — Email server (for introductions)
    SMTP_PORT          — Email port (default 587)
    SMTP_USER          — Email username
    SMTP_PASS          — Email password
    SMTP_FROM          — From address (default masii@masii.co)
"""

import argparse
import logging
import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot'))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("masii.cron")


def run_matching_cycle(db, dry_run=False):
    """Run the matching engine to find new pairs."""
    from matcher import MatcherEngine

    logger.info("=" * 60)
    logger.info("MATCHING CYCLE START")
    logger.info("=" * 60)

    engine = MatcherEngine(db=None if dry_run else db)

    if dry_run:
        logger.info("[DRY RUN] Would load eligible profiles and run matching")
        logger.info("[DRY RUN] No database writes will be made")
        return {"dry_run": True}

    summary = engine.run_matching_cycle()

    logger.info(f"Matching complete:")
    logger.info(f"  Profiles checked: {summary['profiles_checked']}")
    logger.info(f"  Matches created:  {summary['matches_created']}")
    logger.info(f"  Almost matches:   {summary['almost_matches']}")
    logger.info(f"  No match found:   {len(summary['no_match_profiles'])} profiles")

    return summary


def run_delivery_cycle(db, telegram_bot=None, dry_run=False):
    """Run the delivery engine to offer matches and send introductions."""
    from delivery import DeliveryEngine

    logger.info("=" * 60)
    logger.info("DELIVERY CYCLE START")
    logger.info("=" * 60)

    engine = DeliveryEngine(
        db=None if dry_run else db,
        telegram_bot=telegram_bot,
    )

    if dry_run:
        logger.info("[DRY RUN] Would check for pending offers and expirations")
        return {"dry_run": True}

    summary = engine.run_delivery_cycle()

    logger.info(f"Delivery complete:")
    logger.info(f"  Expired offers:  {summary['expired']}")
    logger.info(f"  Offered to A:    {summary['offered_a']}")
    logger.info(f"  Offered to B:    {summary['offered_b']}")
    logger.info(f"  Errors:          {summary['errors']}")

    return summary


def run_full_cycle(db, telegram_bot=None, dry_run=False):
    """Run both matching and delivery."""
    match_summary = run_matching_cycle(db, dry_run=dry_run)
    delivery_summary = run_delivery_cycle(db, telegram_bot=telegram_bot, dry_run=dry_run)

    return {
        "matching": match_summary,
        "delivery": delivery_summary,
    }


def get_db():
    """Initialize database adapter."""
    from db_adapter import DatabaseAdapter

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        sys.exit(1)

    return DatabaseAdapter(database_url)


def get_telegram_bot():
    """Initialize Telegram bot (optional, for sending match offers)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram notifications disabled")
        return None

    try:
        from telegram.ext import Application
        app = Application.builder().token(token).build()
        return app
    except ImportError:
        logger.warning("python-telegram-bot not installed — Telegram notifications disabled")
        return None


def main():
    parser = argparse.ArgumentParser(description="Masii Matching Cron")
    parser.add_argument("--match", action="store_true", help="Only run matching")
    parser.add_argument("--deliver", action="store_true", help="Only run delivery")
    parser.add_argument("--dry-run", action="store_true", help="No DB writes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Masii Matching Cron starting...")

    db = None
    telegram_bot = None

    if not args.dry_run:
        db = get_db()
        telegram_bot = get_telegram_bot()

    try:
        if args.match:
            run_matching_cycle(db, dry_run=args.dry_run)
        elif args.deliver:
            run_delivery_cycle(db, telegram_bot=telegram_bot, dry_run=args.dry_run)
        else:
            run_full_cycle(db, telegram_bot=telegram_bot, dry_run=args.dry_run)
    finally:
        if db:
            db.close()
        logger.info("Masii Matching Cron finished.")


if __name__ == "__main__":
    main()
