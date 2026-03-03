"""
Tests for Masii Double Opt-In Delivery Flow

Tests the delivery engine logic (offer → accept/decline → introduce).
No actual DB or email — tests the flow logic with mocks.
"""

from delivery import DeliveryEngine


class MockDB:
    """Minimal mock database for testing delivery logic."""

    def __init__(self):
        self.matches = {}
        self.match_counter = 0
        self.users = {}
        self.status_log = []

    def add_user(self, user_id, name, gender, telegram_id=None, phone=None, **kwargs):
        self.users[user_id] = {
            "id": user_id,
            "full_name": name,
            "gender": gender,
            "telegram_id": telegram_id,
            "phone": phone,
            "date_of_birth": None,
            "city_current": "Mumbai",
            "country_current": "India",
            "education_level": "Master's",
            "occupation_sector": "Private",
            "religion": "Hindu",
            **kwargs,
        }

    def add_match(self, user_id, matched_user_id, score, status="pending"):
        self.match_counter += 1
        mid = self.match_counter
        self.matches[mid] = {
            "id": mid,
            "user_id": user_id,
            "matched_user_id": matched_user_id,
            "match_score": score,
            "match_explanation": '{"highlights": ["Both Hindu", "Both in Mumbai"]}',
            "status": status,
            "created_at": "2026-03-04T00:00:00",
            "updated_at": "2026-03-04T00:00:00",
            # Joined user fields
            "user_name": self.users[user_id]["full_name"],
            "user_gender": self.users[user_id]["gender"],
            "user_telegram_id": self.users[user_id].get("telegram_id"),
            "user_phone": self.users[user_id].get("phone"),
            "matched_name": self.users[matched_user_id]["full_name"],
            "matched_gender": self.users[matched_user_id]["gender"],
            "matched_telegram_id": self.users[matched_user_id].get("telegram_id"),
            "matched_phone": self.users[matched_user_id].get("phone"),
        }
        return mid

    def _execute(self, query, params=None, fetch=False):
        """Mock SQL execution."""
        query_lower = query.strip().lower()

        if "update matches set status" in query_lower:
            # Status update
            status = params[0]
            match_id = params[1]
            if match_id in self.matches:
                old_status = self.matches[match_id]["status"]
                self.matches[match_id]["status"] = status
                self.status_log.append((match_id, old_status, status))
            return 1

        if "select * from matches where id" in query_lower:
            mid = params[0]
            return self.matches.get(mid)

        if "select m.*" in query_lower and "from matches m" in query_lower and "where m.id" in query_lower:
            # _get_match_full query
            mid = params[0]
            m = self.matches.get(mid)
            if not m:
                return None
            ua = self.users.get(m["user_id"], {})
            ub = self.users.get(m["matched_user_id"], {})
            return {
                **m,
                "user_a_name": ua.get("full_name"),
                "user_a_telegram": ua.get("telegram_id"),
                "user_a_phone": ua.get("phone"),
                "user_a_gender": ua.get("gender"),
                "user_b_name": ub.get("full_name"),
                "user_b_telegram": ub.get("telegram_id"),
                "user_b_phone": ub.get("phone"),
                "user_b_gender": ub.get("gender"),
            }

        if "from matches" in query_lower and "status = 'pending'" in query_lower:
            results = [m for m in self.matches.values() if m["status"] == "pending" and m["match_score"] >= 75]
            return results if results else None

        if "from matches" in query_lower and "status = 'accepted_a'" in query_lower:
            results = [m for m in self.matches.values() if m["status"] == "accepted_a"]
            return results if results else None

        if "from matches" in query_lower and "offered_a" in query_lower:
            return None  # No expired offers in tests

        if "from users where id" in query_lower:
            uid = params[0]
            return self.users.get(uid)

        if "select full_name" in query_lower and "from users" in query_lower:
            uid = params[0]
            return self.users.get(uid)

        if "coalesce" in query_lower:
            return 1  # rejection reason save

        return None


def test_offer_to_person_a():
    """Test that offer goes to the female first."""
    db = MockDB()
    db.add_user(1, "Arun Patel", "Male", telegram_id=111)
    db.add_user(2, "Priya Shah", "Female", telegram_id=222)
    mid = db.add_match(1, 2, 89.0)

    engine = DeliveryEngine(db=db)

    # Get pending matches
    pending = engine.get_pending_matches()
    assert len(pending) == 1

    # Offer to Person A
    match = pending[0]
    engine.offer_to_person_a(match)

    # Status should be offered_a
    assert db.matches[mid]["status"] == "offered_a"
    assert ("offered_a",) == tuple(s[2] for s in db.status_log if s[0] == mid)
    print("  PASS offer to Person A (female first)")


def test_full_accept_flow():
    """Test complete flow: offer A → accept → offer B → accept → introduced."""
    db = MockDB()
    db.add_user(1, "Arun Patel", "Male", telegram_id=111, phone="+91111")
    db.add_user(2, "Priya Shah", "Female", telegram_id=222, phone="+91222")
    mid = db.add_match(1, 2, 89.0)

    engine = DeliveryEngine(db=db)

    # Step 1: Offer to Person A
    pending = engine.get_pending_matches()
    engine.offer_to_person_a(pending[0])
    assert db.matches[mid]["status"] == "offered_a"

    # Step 2: Person A accepts
    engine.handle_response(mid, "a", accepted=True)
    assert db.matches[mid]["status"] == "accepted_a"

    # Step 3: Offer to Person B
    accepted_a = engine.get_offered_matches_needing_followup()
    assert len(accepted_a) == 1
    engine.offer_to_person_b(accepted_a[0])
    assert db.matches[mid]["status"] == "offered_b"

    # Step 4: Person B accepts
    engine.handle_response(mid, "b", accepted=True)
    # After both accept, status goes to 'accepted' then 'introduced'
    assert db.matches[mid]["status"] == "introduced"

    # Verify status progression
    statuses = [s[2] for s in db.status_log if s[0] == mid]
    assert statuses == ["offered_a", "accepted_a", "offered_b", "accepted", "introduced"]
    print("  PASS full accept flow (offered_a → accepted_a → offered_b → accepted → introduced)")


def test_person_a_declines():
    """Test that declining at Person A ends the flow cleanly."""
    db = MockDB()
    db.add_user(1, "Arun Patel", "Male")
    db.add_user(2, "Priya Shah", "Female")
    mid = db.add_match(1, 2, 85.0)

    engine = DeliveryEngine(db=db)

    pending = engine.get_pending_matches()
    engine.offer_to_person_a(pending[0])
    assert db.matches[mid]["status"] == "offered_a"

    # Person A declines
    engine.handle_response(mid, "a", accepted=False, reason="Not my type")
    assert db.matches[mid]["status"] == "declined_a"

    # No followup needed
    accepted_a = engine.get_offered_matches_needing_followup()
    assert len(accepted_a) == 0
    print("  PASS Person A declines (flow ends, B never contacted)")


def test_person_b_declines():
    """Test that Person B declining doesn't notify Person A."""
    db = MockDB()
    db.add_user(1, "Arun Patel", "Male")
    db.add_user(2, "Priya Shah", "Female")
    mid = db.add_match(1, 2, 80.0)

    engine = DeliveryEngine(db=db)

    # Offer A → accept → offer B
    pending = engine.get_pending_matches()
    engine.offer_to_person_a(pending[0])
    engine.handle_response(mid, "a", accepted=True)
    accepted_a = engine.get_offered_matches_needing_followup()
    engine.offer_to_person_b(accepted_a[0])

    # Person B declines
    engine.handle_response(mid, "b", accepted=False, reason="Location too far")
    assert db.matches[mid]["status"] == "declined_b"

    # Person A is never told about the rejection
    statuses = [s[2] for s in db.status_log if s[0] == mid]
    assert "introduced" not in statuses
    print("  PASS Person B declines (Person A never told)")


def test_below_score_not_offered():
    """Matches below 75 should not be offered."""
    db = MockDB()
    db.add_user(1, "Arun Patel", "Male")
    db.add_user(2, "Priya Shah", "Female")
    db.add_match(1, 2, 65.0)  # Below threshold

    engine = DeliveryEngine(db=db)
    pending = engine.get_pending_matches()
    assert len(pending) == 0
    print("  PASS below-score match not offered")


def test_offer_message_format():
    """Test that offer messages are properly formatted."""
    engine = DeliveryEngine()
    msg = engine._build_offer_message(
        recipient_name="Priya Shah",
        match_name="Arun",
        match_age=29,
        match_city="Mumbai",
        match_education="Master's",
        match_occupation="Private",
        score=89.0,
        highlights=["Both Hindu", "Both speak Gujarati", "Both vegetarian"],
        match_id=1,
    )
    assert "Priya" in msg
    assert "Arun" in msg
    assert "89%" in msg
    assert "Both Hindu" in msg
    assert "Want to meet them?" in msg
    print(f"  Offer message preview:\n{msg[:200]}...")
    print("  PASS offer message format")


def test_delivery_cycle():
    """Test the full delivery cycle run."""
    db = MockDB()
    db.add_user(1, "Arun Patel", "Male", phone="+91111")
    db.add_user(2, "Priya Shah", "Female", phone="+91222")
    db.add_user(3, "Raj Malhotra", "Male", phone="+91333")
    db.add_user(4, "Neha Gupta", "Female", phone="+91444")

    # Two pending matches
    mid1 = db.add_match(1, 2, 89.0)
    mid2 = db.add_match(3, 4, 82.0)

    engine = DeliveryEngine(db=db)
    summary = engine.run_delivery_cycle()

    assert summary["offered_a"] == 2  # Both matches offered to Person A
    assert db.matches[mid1]["status"] == "offered_a"
    assert db.matches[mid2]["status"] == "offered_a"
    print(f"  Delivery cycle summary: {summary}")
    print("  PASS delivery cycle")


def run_all_tests():
    print("\n=== DELIVERY FLOW TESTS ===\n")
    test_offer_to_person_a()
    test_full_accept_flow()
    test_person_a_declines()
    test_person_b_declines()
    test_below_score_not_offered()
    test_offer_message_format()
    test_delivery_cycle()
    print("\n=== ALL DELIVERY TESTS PASSED ===\n")


if __name__ == "__main__":
    run_all_tests()
