"""
Double Opt-In Flow — Match delivery and introduction.

Flow:
1. Match created with status='pending' by matcher
2. Cron picks up pending matches, offers to Person A (girl first) → status='offered_a'
3. Person A responds: accept → status='accepted_a', decline → status='declined_a'
4. If A accepted, offer to Person B → status='offered_b'
5. Person B responds: accept → status='accepted', decline → status='declined_b'
6. If both accepted → introduce on email → status='introduced'
7. 72h timeout on each offer → status='expired_a' or 'expired_b'

Status lifecycle:
    pending → offered_a → accepted_a → offered_b → accepted → introduced
                       → declined_a (end)
                       → expired_a (can retry in 30 days)
                                              → declined_b (end, A never told)
                                              → expired_b (can retry in 30 days)
"""

import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Timeout for each person to respond
OFFER_TIMEOUT_HOURS = 72

# Minimum score to offer
MIN_OFFER_SCORE = 75


class DeliveryEngine:
    """
    Handles the double opt-in flow and email introductions.
    Works with the matches table and sends notifications via Telegram + email.
    """

    def __init__(self, db=None, telegram_bot=None):
        """
        db: DatabaseAdapter instance
        telegram_bot: python-telegram-bot Application (for sending Telegram messages)
        """
        self.db = db
        self.bot = telegram_bot

    # ============== MATCH OFFERING ==============

    def get_pending_matches(self) -> List[Dict]:
        """Get all matches in 'pending' status ready to be offered."""
        if not self.db:
            return []

        query = """
            SELECT m.id, m.user_id, m.matched_user_id, m.match_score,
                   m.match_explanation, m.status, m.created_at,
                   u1.full_name as user_name, u1.gender as user_gender,
                   u1.telegram_id as user_telegram_id, u1.phone as user_phone,
                   u2.full_name as matched_name, u2.gender as matched_gender,
                   u2.telegram_id as matched_telegram_id, u2.phone as matched_phone
            FROM matches m
            JOIN users u1 ON m.user_id = u1.id
            JOIN users u2 ON m.matched_user_id = u2.id
            WHERE m.status = 'pending'
              AND m.match_score >= %s
            ORDER BY m.match_score DESC
        """
        results = self.db._execute(query, (MIN_OFFER_SCORE,), fetch=True)
        if not results:
            return []
        if isinstance(results, dict):
            results = [results]
        return results

    def get_offered_matches_needing_followup(self) -> List[Dict]:
        """Get matches where Person A accepted and Person B needs to be offered."""
        if not self.db:
            return []

        query = """
            SELECT m.id, m.user_id, m.matched_user_id, m.match_score,
                   m.match_explanation, m.status, m.updated_at,
                   u1.full_name as user_name, u1.gender as user_gender,
                   u1.telegram_id as user_telegram_id, u1.phone as user_phone,
                   u2.full_name as matched_name, u2.gender as matched_gender,
                   u2.telegram_id as matched_telegram_id, u2.phone as matched_phone
            FROM matches m
            JOIN users u1 ON m.user_id = u1.id
            JOIN users u2 ON m.matched_user_id = u2.id
            WHERE m.status = 'accepted_a'
            ORDER BY m.match_score DESC
        """
        results = self.db._execute(query, fetch=True)
        if not results:
            return []
        if isinstance(results, dict):
            results = [results]
        return results

    def get_expired_offers(self) -> List[Dict]:
        """Get matches where the offer has timed out (72h)."""
        if not self.db:
            return []

        cutoff = datetime.utcnow() - timedelta(hours=OFFER_TIMEOUT_HOURS)
        query = """
            SELECT m.id, m.status, m.updated_at
            FROM matches m
            WHERE m.status IN ('offered_a', 'offered_b')
              AND m.updated_at < %s
        """
        results = self.db._execute(query, (cutoff,), fetch=True)
        if not results:
            return []
        if isinstance(results, dict):
            results = [results]
        return results

    # ============== OFFER TO PERSON A (Girl first) ==============

    def offer_to_person_a(self, match: Dict) -> bool:
        """
        Send match offer to Person A.
        Convention: offer to the female first.
        If user_gender is Female, Person A = user_id.
        If matched_gender is Female, Person A = matched_user_id.
        """
        # Determine who is Person A (female) and Person B (male)
        if match["user_gender"] == "Female":
            person_a_id = match["user_id"]
            person_a_name = match["user_name"]
            person_a_telegram = match.get("user_telegram_id")
            person_b_name = match["matched_name"]
            person_b_id = match["matched_user_id"]
        else:
            person_a_id = match["matched_user_id"]
            person_a_name = match["matched_name"]
            person_a_telegram = match.get("matched_telegram_id")
            person_b_name = match["user_name"]
            person_b_id = match["user_id"]

        # Build match summary for Person A
        explanation = match.get("match_explanation") or {}
        if isinstance(explanation, str):
            import json
            try:
                explanation = json.loads(explanation)
            except:
                explanation = {}

        highlights = explanation.get("highlights", [])
        score = match.get("match_score", 0)

        # Load Person B's summary profile for the offer
        person_b_summary = self._get_profile_summary(person_b_id)

        message = self._build_offer_message(
            recipient_name=person_a_name,
            match_name=person_b_summary.get("first_name", "someone"),
            match_age=person_b_summary.get("age"),
            match_city=person_b_summary.get("city"),
            match_education=person_b_summary.get("education"),
            match_occupation=person_b_summary.get("occupation"),
            score=score,
            highlights=highlights,
            match_id=match["id"],
        )

        # Send via Telegram if available
        if person_a_telegram and self.bot:
            self._send_telegram_offer(person_a_telegram, message, match["id"])

        # Update status
        self._update_match_status(match["id"], "offered_a")

        logger.info(f"Offered match {match['id']} to Person A (user {person_a_id})")
        return True

    def offer_to_person_b(self, match: Dict) -> bool:
        """
        Send match offer to Person B (the male).
        Called after Person A accepted.
        """
        # Determine Person B
        if match["user_gender"] == "Male":
            person_b_id = match["user_id"]
            person_b_name = match["user_name"]
            person_b_telegram = match.get("user_telegram_id")
            person_a_name = match["matched_name"]
            person_a_id = match["matched_user_id"]
        else:
            person_b_id = match["matched_user_id"]
            person_b_name = match["matched_name"]
            person_b_telegram = match.get("matched_telegram_id")
            person_a_name = match["user_name"]
            person_a_id = match["user_id"]

        explanation = match.get("match_explanation") or {}
        if isinstance(explanation, str):
            import json
            try:
                explanation = json.loads(explanation)
            except:
                explanation = {}

        highlights = explanation.get("highlights", [])
        score = match.get("match_score", 0)

        person_a_summary = self._get_profile_summary(person_a_id)

        message = self._build_offer_message(
            recipient_name=person_b_name,
            match_name=person_a_summary.get("first_name", "someone"),
            match_age=person_a_summary.get("age"),
            match_city=person_a_summary.get("city"),
            match_education=person_a_summary.get("education"),
            match_occupation=person_a_summary.get("occupation"),
            score=score,
            highlights=highlights,
            match_id=match["id"],
        )

        if person_b_telegram and self.bot:
            self._send_telegram_offer(person_b_telegram, message, match["id"])

        self._update_match_status(match["id"], "offered_b")

        logger.info(f"Offered match {match['id']} to Person B (user {person_b_id})")
        return True

    # ============== RESPONSE HANDLING ==============

    def handle_response(self, match_id: int, responder_role: str, accepted: bool, reason: str = None):
        """
        Handle a user's response to a match offer.

        responder_role: 'a' or 'b'
        accepted: True if they said yes
        reason: optional rejection reason (never shared with other party)
        """
        if not self.db:
            return

        match = self._get_match(match_id)
        if not match:
            logger.error(f"Match {match_id} not found")
            return

        if responder_role == "a":
            if accepted:
                self._update_match_status(match_id, "accepted_a")
                logger.info(f"Match {match_id}: Person A accepted")
            else:
                self._update_match_status(match_id, "declined_a")
                if reason:
                    self._save_rejection_reason(match_id, "a", reason)
                logger.info(f"Match {match_id}: Person A declined")

        elif responder_role == "b":
            if accepted:
                self._update_match_status(match_id, "accepted")
                logger.info(f"Match {match_id}: Person B accepted — MUTUAL MATCH!")
                # Both accepted — trigger introduction
                self._introduce_match(match_id)
            else:
                self._update_match_status(match_id, "declined_b")
                if reason:
                    self._save_rejection_reason(match_id, "b", reason)
                logger.info(f"Match {match_id}: Person B declined (Person A never told)")

    # ============== INTRODUCTION ==============

    def _introduce_match(self, match_id: int):
        """
        Both parties said yes. Send introduction with contact info.
        Sends via email (primary) and Telegram (notification).
        """
        match = self._get_match_full(match_id)
        if not match:
            return

        user_a = match["user_a"]
        user_b = match["user_b"]
        explanation = match.get("explanation", {})

        # Send introduction emails to both
        self._send_introduction_email(
            recipient=user_a,
            match=user_b,
            explanation=explanation,
            score=match.get("match_score", 0),
        )
        self._send_introduction_email(
            recipient=user_b,
            match=user_a,
            explanation=explanation,
            score=match.get("match_score", 0),
        )

        # Send Telegram notifications
        if user_a.get("telegram_id") and self.bot:
            self._send_telegram_intro_notification(
                user_a["telegram_id"],
                user_a.get("full_name", "").split()[0],
                user_b.get("full_name", "").split()[0],
            )
        if user_b.get("telegram_id") and self.bot:
            self._send_telegram_intro_notification(
                user_b["telegram_id"],
                user_b.get("full_name", "").split()[0],
                user_a.get("full_name", "").split()[0],
            )

        self._update_match_status(match_id, "introduced")
        logger.info(f"Match {match_id}: Introduction sent to both parties!")

    def _send_introduction_email(
        self,
        recipient: Dict,
        match: Dict,
        explanation: Dict,
        score: float,
    ):
        """Send the introduction email to one party."""
        recipient_email = recipient.get("phone")  # Use phone as email placeholder for now
        recipient_name = (recipient.get("full_name") or "").split()[0] or "there"
        match_name = match.get("full_name", "your match")
        match_first = match_name.split()[0] if match_name else "your match"

        highlights = explanation.get("highlights", [])
        highlights_text = "\n".join(f"  - {h}" for h in highlights) if highlights else "  - Great compatibility across multiple dimensions"

        # Build email
        subject = f"Masii: Meet {match_first} - You both said yes!"

        body_html = f"""
        <div style="font-family: 'Georgia', serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #DC6B2F;">
                <h1 style="color: #DC6B2F; font-size: 28px; margin: 0;">Masii</h1>
                <p style="color: #666; font-style: italic; margin: 5px 0 0 0;">You deserve to meet.</p>
            </div>

            <div style="padding: 30px 0;">
                <p style="font-size: 18px; color: #333;">Hi {recipient_name},</p>

                <p style="font-size: 16px; color: #333; line-height: 1.6;">
                    Great news! Both you and <strong>{match_first}</strong> said yes.
                    Masii thinks you two would really get along.
                </p>

                <div style="background: #FFF8F0; border-left: 4px solid #DC6B2F; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                    <h3 style="color: #DC6B2F; margin: 0 0 10px 0;">Why Masii matched you:</h3>
                    <p style="margin: 0; color: #555; line-height: 1.8;">
{highlights_text}
                    </p>
                    <p style="margin: 15px 0 0 0; color: #DC6B2F; font-weight: bold;">
                        Match strength: {score:.0f}%
                    </p>
                </div>

                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin: 0 0 15px 0;">About {match_first}:</h3>
                    <table style="width: 100%; font-size: 15px; color: #444;">
                        <tr><td style="padding: 5px 0;"><strong>Name:</strong></td><td>{match_name}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>Age:</strong></td><td>{self._calc_age_from_dob(match.get('date_of_birth'))}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>Location:</strong></td><td>{match.get('city_current', 'N/A')}, {match.get('country_current', '')}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>Education:</strong></td><td>{match.get('education_level', 'N/A')}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>Works in:</strong></td><td>{match.get('occupation_sector', 'N/A')}</td></tr>
                        <tr><td style="padding: 5px 0;"><strong>Religion:</strong></td><td>{match.get('religion', 'N/A')}</td></tr>
                    </table>
                </div>

                <div style="background: #E8F5E9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2E7D32; margin: 0 0 10px 0;">How to reach {match_first}:</h3>
                    <p style="font-size: 16px; margin: 0; color: #333;">
                        Phone: <strong>{match.get('phone', 'N/A')}</strong>
                    </p>
                    <p style="font-size: 14px; color: #666; margin: 10px 0 0 0;">
                        Send them a message — Masii suggests starting with something about what you have in common.
                    </p>
                </div>

                <p style="font-size: 14px; color: #888; line-height: 1.6; margin-top: 30px;">
                    Masii will check in with you in a week to see how things are going.
                    Remember: be yourself, be kind, be open. You deserve to meet.
                </p>
            </div>

            <div style="text-align: center; padding: 20px 0; border-top: 1px solid #eee; color: #999; font-size: 12px;">
                <p>Masii — Your wise friend in the search for love.</p>
                <p>This email was sent because you opted into Masii matchmaking.</p>
            </div>
        </div>
        """

        body_text = f"""
Hi {recipient_name},

Great news! Both you and {match_first} said yes.

Why Masii matched you:
{highlights_text}

Match strength: {score:.0f}%

About {match_first}:
- Name: {match_name}
- Age: {self._calc_age_from_dob(match.get('date_of_birth'))}
- Location: {match.get('city_current', 'N/A')}, {match.get('country_current', '')}
- Education: {match.get('education_level', 'N/A')}
- Works in: {match.get('occupation_sector', 'N/A')}
- Religion: {match.get('religion', 'N/A')}

How to reach {match_first}:
Phone: {match.get('phone', 'N/A')}

Send them a message. Masii will check in with you in a week.

—
Masii
You deserve to meet.
        """

        self._send_email(
            to_email=recipient_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
        )

    # ============== EXPIRATION ==============

    def expire_stale_offers(self):
        """Mark timed-out offers as expired."""
        expired = self.get_expired_offers()
        for match in expired:
            match_id = match["id"]
            current_status = match["status"]

            if current_status == "offered_a":
                self._update_match_status(match_id, "expired_a")
                logger.info(f"Match {match_id}: Person A offer expired (72h)")
            elif current_status == "offered_b":
                self._update_match_status(match_id, "expired_b")
                logger.info(f"Match {match_id}: Person B offer expired (72h)")

        return len(expired)

    # ============== DELIVERY CYCLE ==============

    def run_delivery_cycle(self) -> Dict:
        """
        Run one delivery cycle:
        1. Expire stale offers
        2. Offer pending matches to Person A
        3. Offer accepted_a matches to Person B
        4. (Responses handled asynchronously via handle_response)
        """
        summary = {
            "expired": 0,
            "offered_a": 0,
            "offered_b": 0,
            "errors": 0,
        }

        # Step 1: Expire stale
        summary["expired"] = self.expire_stale_offers()

        # Step 2: Offer to Person A
        pending = self.get_pending_matches()
        for match in pending:
            try:
                self.offer_to_person_a(match)
                summary["offered_a"] += 1
            except Exception as e:
                logger.error(f"Failed to offer match {match['id']} to Person A: {e}")
                summary["errors"] += 1

        # Step 3: Offer to Person B (where A accepted)
        accepted_a = self.get_offered_matches_needing_followup()
        for match in accepted_a:
            try:
                self.offer_to_person_b(match)
                summary["offered_b"] += 1
            except Exception as e:
                logger.error(f"Failed to offer match {match['id']} to Person B: {e}")
                summary["errors"] += 1

        logger.info(f"Delivery cycle complete: {summary}")
        return summary

    # ============== HELPERS ==============

    def _get_match(self, match_id: int) -> Optional[Dict]:
        if not self.db:
            return None
        query = "SELECT * FROM matches WHERE id = %s"
        return self.db._execute(query, (match_id,), fetch=True)

    def _get_match_full(self, match_id: int) -> Optional[Dict]:
        """Get match with full user profiles for introduction."""
        if not self.db:
            return None

        query = """
            SELECT m.*,
                   u1.full_name as user_a_name, u1.telegram_id as user_a_telegram,
                   u1.phone as user_a_phone, u1.gender as user_a_gender,
                   u2.full_name as user_b_name, u2.telegram_id as user_b_telegram,
                   u2.phone as user_b_phone, u2.gender as user_b_gender
            FROM matches m
            JOIN users u1 ON m.user_id = u1.id
            JOIN users u2 ON m.matched_user_id = u2.id
            WHERE m.id = %s
        """
        match = self.db._execute(query, (match_id,), fetch=True)
        if not match:
            return None

        # Load full profiles for both
        user_a_query = "SELECT * FROM users WHERE id = %s"
        user_b_query = "SELECT * FROM users WHERE id = %s"
        user_a = self.db._execute(user_a_query, (match["user_id"],), fetch=True) or {}
        user_b = self.db._execute(user_b_query, (match["matched_user_id"],), fetch=True) or {}

        explanation = match.get("match_explanation") or {}
        if isinstance(explanation, str):
            import json
            try:
                explanation = json.loads(explanation)
            except:
                explanation = {}

        return {
            **match,
            "user_a": dict(user_a),
            "user_b": dict(user_b),
            "explanation": explanation,
        }

    def _get_profile_summary(self, user_id: int) -> Dict:
        """Get a summary of a profile for match offers (no sensitive info)."""
        if not self.db:
            return {}

        query = """
            SELECT full_name, gender, date_of_birth, city_current, country_current,
                   education_level, occupation_sector, religion
            FROM users WHERE id = %s
        """
        user = self.db._execute(query, (user_id,), fetch=True)
        if not user:
            return {}

        name = user.get("full_name", "")
        first_name = name.split()[0] if name else "Someone"

        age = self._calc_age_from_dob(user.get("date_of_birth"))

        return {
            "first_name": first_name,
            "age": age,
            "city": user.get("city_current"),
            "country": user.get("country_current"),
            "education": user.get("education_level"),
            "occupation": user.get("occupation_sector"),
            "religion": user.get("religion"),
        }

    def _calc_age_from_dob(self, dob) -> Optional[int]:
        if not dob:
            return None
        from datetime import date as date_type
        if isinstance(dob, date_type):
            today = date_type.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

    def _build_offer_message(
        self,
        recipient_name: str,
        match_name: str,
        match_age: Optional[int],
        match_city: Optional[str],
        match_education: Optional[str],
        match_occupation: Optional[str],
        score: float,
        highlights: list,
        match_id: int,
    ) -> str:
        """Build the match offer message (Telegram format)."""
        first = recipient_name.split()[0] if recipient_name else "there"
        age_str = f", {match_age}" if match_age else ""
        city_str = f" in {match_city}" if match_city else ""
        edu_str = f"\nEducation: {match_education}" if match_education else ""
        occ_str = f"\nWorks in: {match_occupation}" if match_occupation else ""

        highlights_str = ""
        if highlights:
            highlights_str = "\n\nWhy Masii thinks you'd click:\n" + "\n".join(f"  - {h}" for h in highlights[:4])

        return (
            f"Hi {first}! Masii found someone for you.\n\n"
            f"Name: {match_name}{age_str}{city_str}"
            f"{edu_str}{occ_str}"
            f"\n\nMatch strength: {score:.0f}%"
            f"{highlights_str}"
            f"\n\nWant to meet them?"
        )

    def _update_match_status(self, match_id: int, status: str):
        if not self.db:
            logger.info(f"[DRY RUN] Match {match_id} → {status}")
            return
        query = "UPDATE matches SET status = %s, updated_at = NOW() WHERE id = %s"
        self.db._execute(query, (status, match_id))

    def _save_rejection_reason(self, match_id: int, role: str, reason: str):
        """Save rejection reason (private, never shared)."""
        if not self.db:
            return
        import json
        query = """
            UPDATE matches
            SET match_explanation = COALESCE(match_explanation, '{}'::jsonb) || %s::jsonb,
                updated_at = NOW()
            WHERE id = %s
        """
        data = json.dumps({f"rejection_{role}": reason})
        self.db._execute(query, (data, match_id))

    def _send_telegram_offer(self, telegram_id: int, message: str, match_id: int):
        """Send match offer via Telegram with accept/decline buttons."""
        if not self.bot:
            logger.info(f"[NO BOT] Would send to {telegram_id}: {message[:50]}...")
            return

        try:
            import asyncio
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes, I'm interested", callback_data=f"match_accept_{match_id}"),
                    InlineKeyboardButton("Not this time", callback_data=f"match_decline_{match_id}"),
                ],
                [
                    InlineKeyboardButton("Tell me more", callback_data=f"match_more_{match_id}"),
                ],
            ])

            asyncio.get_event_loop().run_until_complete(
                self.bot.bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                    reply_markup=keyboard,
                )
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram offer to {telegram_id}: {e}")

    def _send_telegram_intro_notification(self, telegram_id: int, recipient_name: str, match_name: str):
        """Send Telegram notification that an introduction email was sent."""
        if not self.bot:
            return

        message = (
            f"Great news, {recipient_name}! Both you and {match_name} said yes.\n\n"
            f"Check your email — Masii sent you an introduction with {match_name}'s details "
            f"and contact info.\n\n"
            f"Be yourself, be kind, be open. You deserve to meet."
        )

        try:
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                self.bot.bot.send_message(chat_id=telegram_id, text=message)
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram intro notification to {telegram_id}: {e}")

    def _send_email(self, to_email: str, subject: str, body_html: str, body_text: str):
        """
        Send email via SMTP.
        Configure with environment variables:
            SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
        """
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        smtp_from = os.getenv("SMTP_FROM", "masii@masii.co")

        if not smtp_host or not smtp_user:
            logger.warning(f"SMTP not configured. Would send email to {to_email}: {subject}")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Masii <{smtp_from}>"
        msg["To"] = to_email

        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            logger.info(f"Email sent to {to_email}: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")


# ============== SCHEMA MIGRATION for new statuses ==============

MIGRATION_SQL = """
-- Add new status values for double opt-in flow.
-- The status column is VARCHAR so no migration needed for new values.
-- But let's add an index for the new statuses:
CREATE INDEX IF NOT EXISTS idx_matches_offered
    ON matches(status, updated_at)
    WHERE status IN ('offered_a', 'offered_b', 'accepted_a');

-- Add a column for tracking who was offered first (for reporting)
ALTER TABLE matches ADD COLUMN IF NOT EXISTS offered_first VARCHAR(10);
COMMENT ON COLUMN matches.offered_first IS 'Who was offered first: a (user_id) or b (matched_user_id)';
"""
