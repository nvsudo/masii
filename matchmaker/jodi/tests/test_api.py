from fastapi.testclient import TestClient
from services.conversational_controller.main import app
from uuid import uuid4

client = TestClient(app)

def test_update_and_get_state():
    user_id = str(uuid4())
    session_id = "sess-123"
    resp = client.post("/state/update", json={"session_id": session_id, "user_id": user_id, "state_json": {"foo": "bar"}, "confidence": 0.9})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "auto"

    get = client.get(f"/state/{session_id}")
    assert get.status_code == 200
    data = get.json()
    assert data["session_id"] == session_id

def test_advance_state():
    user_id = str(uuid4())
    session_id = "sess-adv"
    client.post("/state/update", json={"session_id": session_id, "user_id": user_id, "state_json": {}, "confidence": 0.5})
    resp = client.post("/state/advance", json={"session_id": session_id, "user_id": user_id, "action": "next"})
    assert resp.status_code == 200
    body = resp.json()
    assert "progress_pct" in body

# feature flag tests
from services.conversational_controller.feature_flag import in_rollout

def test_feature_flag_bounds():
    # when rollout is 0, no one is included
    from services.conversational_controller.config import settings
    settings.FEATURE_ROLLOUT_PCT = 0
    assert in_rollout("any-user") is False
    settings.FEATURE_ROLLOUT_PCT = 100
    assert in_rollout("any-user") is True
