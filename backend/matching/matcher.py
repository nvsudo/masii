"""
Matcher Engine — Pair identification, ranking, and match creation.

The main entry point is `run_matching_cycle()` which:
1. Fetches all eligible profiles from DB
2. For each profile, finds candidates that pass hard filters
3. Scores all surviving pairs
4. Ranks by score, creates match records
5. Handles "almost matches" (60-74 score) separately

Match tiers:
    87+  → High conviction, free introduction
    75-86 → Good match, free introduction
    60-74 → Almost match, shown to paid tiers or offered as "we have someone close"
    <60  → Not shown
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

try:
    from .filters import pass_hard_filters_bidirectional, calculate_age
    from .scoring import (
        calculate_bidirectional_score,
        calculate_confidence,
        generate_explanation,
    )
except ImportError:
    from filters import pass_hard_filters_bidirectional, calculate_age
    from scoring import (
        calculate_bidirectional_score,
        calculate_confidence,
        generate_explanation,
    )

logger = logging.getLogger(__name__)

# Score thresholds
SCORE_HIGH_CONVICTION = 87
SCORE_GOOD_MATCH = 75
SCORE_ALMOST_MATCH = 60
SCORE_MINIMUM = 60

# Max matches per user per cycle
MAX_MATCHES_PER_CYCLE = 3

# Minimum profile completeness to be matchable
MIN_PROFILE_FIELDS = 10


class MatcherEngine:
    """
    Core matching engine. Operates on profile dicts loaded from the database.
    Database operations are handled by the caller (cron.py or tests).
    """

    def __init__(self, db=None):
        """
        Initialize with optional database adapter.
        If db is None, operates in pure-logic mode (for testing).
        """
        self.db = db

    # ============== PROFILE LOADING ==============

    def load_all_eligible_profiles(self) -> List[Dict]:
        """
        Load all profiles eligible for matching from DB.
        A profile is eligible if:
          - Has gender, DOB, religion (minimum hard filter fields)
          - Has at least MIN_PROFILE_FIELDS total fields filled
          - Is not already in an active match (status = pending/accepted)
        """
        if not self.db:
            raise RuntimeError("No database adapter provided")

        query = """
            SELECT
                u.id,
                u.full_name,
                u.gender,
                u.date_of_birth,
                u.city_current,
                u.country_current,
                u.state_india,
                u.hometown_state,
                u.hometown_city,
                u.mother_tongue,
                u.languages_spoken,
                u.marital_status,
                u.children_existing,
                u.height_cm,
                u.weight_kg,
                u.religion,
                u.education_level,
                u.education_field,
                u.occupation_sector,
                u.annual_income,
                u.family_type,
                u.family_status,
                u.father_occupation,
                u.mother_occupation,
                u.siblings,
                u.known_conditions,
                u.phone
            FROM users u
            WHERE u.gender IS NOT NULL
              AND u.date_of_birth IS NOT NULL
              AND u.religion IS NOT NULL
              AND u.full_name IS NOT NULL
        """
        profiles = self.db._execute(query, fetch=True)
        if not profiles:
            return []

        # Normalize: _execute returns a single dict if only 1 row
        if isinstance(profiles, dict):
            profiles = [profiles]

        result = []
        for p in profiles:
            user_id = p["id"]

            # Load preferences
            prefs = self._load_preferences(user_id)
            if not prefs:
                prefs = {}

            # Load signals
            signals = self._load_signals(user_id)
            if not signals:
                signals = {}

            # Check minimum profile completeness
            filled = self._count_filled(p, prefs, signals)
            if filled < MIN_PROFILE_FIELDS:
                continue

            result.append({
                "user": dict(p),
                "prefs": dict(prefs) if prefs else {},
                "signals": dict(signals) if signals else {},
                "filled_count": filled,
            })

        logger.info(f"Loaded {len(result)} eligible profiles out of {len(profiles) if isinstance(profiles, list) else 1} total")
        return result

    def _load_preferences(self, user_id: int) -> Optional[Dict]:
        query = "SELECT * FROM user_preferences WHERE user_id = %s"
        return self.db._execute(query, (user_id,), fetch=True)

    def _load_signals(self, user_id: int) -> Optional[Dict]:
        query = "SELECT * FROM user_signals WHERE user_id = %s"
        return self.db._execute(query, (user_id,), fetch=True)

    def _count_filled(self, user: Dict, prefs: Dict, signals: Dict) -> int:
        count = 0
        for d in [user, prefs, signals]:
            for k, v in d.items():
                if k in ("id", "user_id", "created_at", "updated_at"):
                    continue
                if v is not None and v != "":
                    count += 1
        return count

    # ============== EXISTING MATCHES CHECK ==============

    def get_existing_matches(self, user_id: int) -> set:
        """Get set of user IDs this user has already been matched with."""
        if not self.db:
            return set()

        query = """
            SELECT matched_user_id FROM matches WHERE user_id = %s
            UNION
            SELECT user_id FROM matches WHERE matched_user_id = %s
        """
        results = self.db._execute(query, (user_id, user_id), fetch=True)
        if not results:
            return set()
        if isinstance(results, dict):
            results = [results]
        ids = set()
        for r in results:
            ids.add(r.get("matched_user_id") or r.get("user_id"))
        return ids

    def get_pending_match_count(self, user_id: int) -> int:
        """Count active (pending/accepted) matches for rate limiting."""
        if not self.db:
            return 0

        query = """
            SELECT COUNT(*) as cnt FROM matches
            WHERE (user_id = %s OR matched_user_id = %s)
              AND status IN ('pending', 'offered_a', 'offered_b', 'accepted')
        """
        result = self.db._execute(query, (user_id, user_id), fetch=True)
        return result["cnt"] if result else 0

    # ============== MATCHING LOGIC ==============

    def find_matches_for_profile(
        self,
        profile: Dict,
        all_profiles: List[Dict],
        existing_match_ids: set = None,
    ) -> List[Dict]:
        """
        For a single profile, find and rank all compatible candidates.

        Returns list of match results sorted by score (descending):
        [
            {
                "candidate_id": int,
                "score": float,
                "confidence": str,
                "score_detail": dict,
                "explanation": dict,
                "tier": str,  # "high", "good", "almost"
            },
            ...
        ]
        """
        user = profile["user"]
        prefs = profile["prefs"]
        signals = profile["signals"]
        user_id = user["id"]

        if existing_match_ids is None:
            existing_match_ids = set()

        matches = []

        for candidate_profile in all_profiles:
            cand = candidate_profile["user"]
            cand_prefs = candidate_profile["prefs"]
            cand_signals = candidate_profile["signals"]
            cand_id = cand["id"]

            # Skip self
            if cand_id == user_id:
                continue

            # Skip already matched
            if cand_id in existing_match_ids:
                continue

            # Stage 1: Hard filters (bidirectional)
            passes, a_failed, b_failed = pass_hard_filters_bidirectional(
                user, prefs, signals,
                cand, cand_prefs, cand_signals,
            )
            if not passes:
                continue

            # Stage 2: Scoring (bidirectional)
            score_result = calculate_bidirectional_score(
                user, prefs, signals,
                cand, cand_prefs, cand_signals,
            )

            final_score = score_result["score"]

            # Skip below minimum
            if final_score < SCORE_MINIMUM:
                continue

            # Stage 3: Confidence
            confidence = calculate_confidence(
                user, prefs, signals,
                cand, cand_prefs, cand_signals,
            )

            # Determine tier
            if final_score >= SCORE_HIGH_CONVICTION:
                tier = "high"
            elif final_score >= SCORE_GOOD_MATCH:
                tier = "good"
            else:
                tier = "almost"

            # Generate explanation
            explanation = generate_explanation(
                user, prefs, signals,
                cand, cand_prefs, cand_signals,
                score_result,
            )

            matches.append({
                "candidate_id": cand_id,
                "candidate_name": cand.get("full_name"),
                "score": final_score,
                "confidence": confidence,
                "score_detail": score_result,
                "explanation": explanation,
                "tier": tier,
            })

        # Sort by score descending
        matches.sort(key=lambda m: m["score"], reverse=True)

        return matches

    def run_matching_cycle(self) -> Dict:
        """
        Run a full matching cycle for all eligible profiles.

        Returns summary:
        {
            "profiles_checked": int,
            "matches_created": int,
            "almost_matches": int,
            "no_match_profiles": list of user IDs,
        }
        """
        logger.info("Starting matching cycle...")

        all_profiles = self.load_all_eligible_profiles()
        logger.info(f"Eligible profiles: {len(all_profiles)}")

        if len(all_profiles) < 2:
            logger.info("Not enough profiles to match")
            return {
                "profiles_checked": len(all_profiles),
                "matches_created": 0,
                "almost_matches": 0,
                "no_match_profiles": [p["user"]["id"] for p in all_profiles],
            }

        # Track which pairs have been processed (avoid duplicate A↔B and B↔A)
        processed_pairs = set()
        matches_created = 0
        almost_matches = 0
        no_match_profiles = []

        # Build a lookup for existing matches per user
        existing_matches = {}
        for p in all_profiles:
            uid = p["user"]["id"]
            existing_matches[uid] = self.get_existing_matches(uid)

        for profile in all_profiles:
            user_id = profile["user"]["id"]

            # Rate limit: skip if too many active matches
            pending = self.get_pending_match_count(user_id)
            if pending >= MAX_MATCHES_PER_CYCLE:
                continue

            # Find matches
            candidates = self.find_matches_for_profile(
                profile, all_profiles, existing_matches.get(user_id, set())
            )

            if not candidates:
                no_match_profiles.append(user_id)
                continue

            # Take top candidate(s) — up to (MAX_MATCHES_PER_CYCLE - pending)
            slots = MAX_MATCHES_PER_CYCLE - pending
            created_this_user = 0

            for match in candidates:
                if created_this_user >= slots:
                    break

                cand_id = match["candidate_id"]

                # Don't create duplicate pair
                pair_key = tuple(sorted([user_id, cand_id]))
                if pair_key in processed_pairs:
                    continue

                # Check candidate's pending matches too
                cand_pending = self.get_pending_match_count(cand_id)
                if cand_pending >= MAX_MATCHES_PER_CYCLE:
                    continue

                # Create match record
                if match["tier"] in ("high", "good"):
                    self._create_match_record(
                        user_id=user_id,
                        matched_user_id=cand_id,
                        score=match["score"],
                        explanation=match["explanation"],
                        confidence=match["confidence"],
                    )
                    matches_created += 1
                    created_this_user += 1
                    processed_pairs.add(pair_key)

                    # Add to existing matches so we don't re-match
                    existing_matches.setdefault(user_id, set()).add(cand_id)
                    existing_matches.setdefault(cand_id, set()).add(user_id)

                elif match["tier"] == "almost":
                    self._create_match_record(
                        user_id=user_id,
                        matched_user_id=cand_id,
                        score=match["score"],
                        explanation=match["explanation"],
                        confidence=match["confidence"],
                        status="almost",
                    )
                    almost_matches += 1
                    processed_pairs.add(pair_key)

        summary = {
            "profiles_checked": len(all_profiles),
            "matches_created": matches_created,
            "almost_matches": almost_matches,
            "no_match_profiles": no_match_profiles,
        }

        logger.info(f"Matching cycle complete: {summary}")
        return summary

    def _create_match_record(
        self,
        user_id: int,
        matched_user_id: int,
        score: float,
        explanation: Dict,
        confidence: str,
        status: str = "pending",
    ):
        """Create a match record in the database."""
        if not self.db:
            logger.info(f"[DRY RUN] Match: {user_id} ↔ {matched_user_id}, score={score}, status={status}")
            return

        import json
        query = """
            INSERT INTO matches (user_id, matched_user_id, match_score, match_explanation, status, created_at)
            VALUES (%s, %s, %s, %s::jsonb, %s, NOW())
            ON CONFLICT DO NOTHING
        """
        explanation_json = json.dumps({
            "highlights": explanation.get("highlights", []),
            "differences": explanation.get("differences", []),
            "confidence": confidence,
            "score": score,
        })

        self.db._execute(query, (user_id, matched_user_id, score, explanation_json, status))
        logger.info(f"Match created: {user_id} ↔ {matched_user_id}, score={score}, status={status}")


# ============== STANDALONE MATCHING (no DB) ==============


def match_two_profiles(
    user_a: Dict, prefs_a: Dict, signals_a: Dict,
    user_b: Dict, prefs_b: Dict, signals_b: Dict,
) -> Optional[Dict]:
    """
    Match two profiles directly (no DB needed). For testing and one-off comparisons.

    Returns match result dict or None if hard filters fail.
    """
    # Hard filters
    passes, a_failed, b_failed = pass_hard_filters_bidirectional(
        user_a, prefs_a, signals_a,
        user_b, prefs_b, signals_b,
    )

    if not passes:
        return {
            "matched": False,
            "reason": f"Hard filter failed: A rejected ({a_failed}), B rejected ({b_failed})",
        }

    # Score
    score_result = calculate_bidirectional_score(
        user_a, prefs_a, signals_a,
        user_b, prefs_b, signals_b,
    )

    # Confidence
    confidence = calculate_confidence(
        user_a, prefs_a, signals_a,
        user_b, prefs_b, signals_b,
    )

    # Explanation
    explanation = generate_explanation(
        user_a, prefs_a, signals_a,
        user_b, prefs_b, signals_b,
        score_result,
    )

    # Tier
    score = score_result["score"]
    if score >= SCORE_HIGH_CONVICTION:
        tier = "high"
    elif score >= SCORE_GOOD_MATCH:
        tier = "good"
    elif score >= SCORE_ALMOST_MATCH:
        tier = "almost"
    else:
        tier = "low"

    return {
        "matched": True,
        "score": score,
        "tier": tier,
        "confidence": confidence,
        "explanation": explanation,
        "score_detail": score_result,
    }
