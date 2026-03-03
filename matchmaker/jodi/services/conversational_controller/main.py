from fastapi import FastAPI, HTTPException
from .models import ConversationState, UpdateStateRequest, AdvanceStateRequest
from .config import settings, AUTO_CONFIDENCE, REVIEW_CONFIDENCE
from .extractor import extract_from_text
from typing import Dict
from uuid import uuid4
from datetime import datetime

app = FastAPI(title="Conversational Controller")

# In-memory store (placeholder for DB integration)
_store: Dict[str, ConversationState] = {}

@app.post("/state/update")
def update_state(req: UpdateStateRequest):
    session_key = req.session_id
    # If incoming state_json contains raw_text, run extractor
    extractor_payload = None
    if isinstance(req.state_json, dict) and "raw_text" in req.state_json:
        extractor_payload = extract_from_text(req.state_json.get("raw_text"))

    obj = _store.get(session_key)
    if not obj:
        obj = ConversationState(id=uuid4(), user_id=req.user_id, session_id=req.session_id, state_json=req.state_json or {}, confidence_map={"last": req.confidence}, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    else:
        # merge state
        obj.state_json = {**(obj.state_json or {}), **(req.state_json or {})}
        obj.confidence_map["last"] = req.confidence
        obj.updated_at = datetime.utcnow()

    # If extractor returned structured updates, merge them
    if extractor_payload:
        obj.state_json = {**obj.state_json, **extractor_payload.get("state_updates", {})}
        obj.completion_map = {**(obj.completion_map or {}), **extractor_payload.get("completion_map", {})}
        obj.confidence_map = {**(obj.confidence_map or {}), **extractor_payload.get("confidence_map", {})}
        overall_conf = extractor_payload.get("overall_confidence", req.confidence)
    else:
        overall_conf = req.confidence

    # set progress_pct as mean confidence for now
    obj.progress_pct = float(overall_conf * 100)
    _store[session_key] = obj

    # Decide action based on confidence thresholds
    if overall_conf >= AUTO_CONFIDENCE:
        status = "auto"
    elif overall_conf >= REVIEW_CONFIDENCE:
        status = "review"
    else:
        status = "clarify"

    return {"session_id": session_key, "status": status, "progress_pct": obj.progress_pct}

@app.get("/state/{session_id}")
def get_state(session_id: str):
    obj = _store.get(session_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

@app.post("/state/advance")
def advance_state(req: AdvanceStateRequest):
    obj = _store.get(req.session_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    # Gate: if progress_pct >= 100 -> can't advance
    if obj.progress_pct >= 100.0:
        return {"session_id": req.session_id, "progress_pct": obj.progress_pct, "status": "complete"}

    # TODO: integrate Claude extractor / planner to compute next action
    # For now, bump progress
    obj.progress_pct = min(100.0, obj.progress_pct + 10.0)
    obj.updated_at = datetime.utcnow()
    _store[req.session_id] = obj
    return {"session_id": req.session_id, "progress_pct": obj.progress_pct}
