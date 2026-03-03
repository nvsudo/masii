# Conversational Controller - System Design

## 1. Component Overview

- State Persistence Layer
  - Responsible for durable storage of conversation state.
  - Implemented with SQLAlchemy and Postgres (conversation_state table).
  - Stores: id, user_id, session_id, state_json (JSONB), completion_map (JSONB), confidence_map (JSONB), progress_pct, priority_tier, created_at, updated_at.

- Feature Flag / Gating Layer
  - Controls staged rollout and gating behavior.
  - Env-configured `ROLLOUT_PCT` (0-100).
  - Deterministic hashing of user_id -> percentile to decide inclusion.

- Progress Calculation Engine
  - Calculates `progress_pct` using signals from extraction and completion_map.
  - Uses configurable `PROGRESS_WEIGHTS` per field to compute a weighted completeness score.
  - Maps progress_pct to priority_tier (HIGH/MED/LOW) using tunable cutoffs.

- Extraction Layer (Pluggable)
  - Responsible for converting free-text user messages into structured fields (name, age, location, intent, etc.) and confidence scores.
  - Designed to be pluggable: initial implementation is a stub; integration will target Claude/Sonnet (Anthropic) or gpt-5.
  - Outputs: extracted_fields (dict), completion_map (dict of field->0..1), confidence_map (dict of field->0..1), overall_confidence.

- API Endpoints
  - POST /state/update — Accepts session_id, user_id, state_json (may include raw_text), confidence (optional). Runs extractor if raw_text present, merges state, updates progress and confidence, returns status (auto/review/clarify) and progress_pct.
  - GET /state/{session_id} — Retrieve the current conversation state and metadata.
  - POST /state/advance — Advance the conversation planning flow; checks gating and updates progress/priority.

## 2. Data Flow (request → response)

1. Bot/user sends a message to the system (raw text) and calls POST /state/update with {session_id, user_id, state_json: { raw_text }}.
2. The service checks feature flags (ROLLOUT_PCT) to determine whether to run the extraction pipeline.
3. If enabled, call Extraction Layer (Claude/Sonnet) with a system prompt and the user text.
4. Extraction Layer returns structured fields, completion_map, confidence_map, overall_confidence.
5. Progress Calculation Engine computes `progress_pct` using configured weights and the completion_map.
6. Gating Layer evaluates `progress_pct` against thresholds and decides:
   - If overall_confidence >= AUTO_CONFIDENCE (0.85): automatically proceed (status: auto).
   - If 0.65 <= overall_confidence < 0.85: mark for human review (status: review).
   - If overall_confidence < 0.65: ask clarifying question (status: clarify).
7. Persist updated conversation_state to Postgres.
8. Return status and progress_pct to caller.

## 3. Tuning Levers

- CONFIDENCE_THRESHOLDS
  - AUTO: 0.85
  - REVIEW: 0.65-0.85
  - CLARIFY: <0.65

- PROGRESS_WEIGHTS (example)
  - name: 0.2
  - age: 0.15
  - location: 0.25
  - preferences: 0.4
  - These weights are configurable per deployment and used to compute weighted completeness.

- ROLLOUT_PCT
  - Controls percentage of users included in the extractor/path.
  - Range 0 to 100 — use deterministic hashing of user_id to select.

- PRIORITY_TIER_CUTOFFS
  - High: progress_pct >= 80
  - Med: 50 <= progress_pct < 80
  - Low: progress_pct < 50

- Model Selection
  - Use opus/sonnet/gpt-5 for extraction (swapable post-MVP).

- Extraction Strategy
  - Direct LLM extraction (Claude -> JSON)
  - UI nudges (Telegram/Buttons) for low-confidence fields
  - Hybrid: LLM suggests clarifying questions and UI collects answers

## 4. Constraints & Decisions

- LLM Constraint: Use only opus/sonnet/gpt-5 for extraction tasks per product decision.
- DB: Postgres conversation_state table is the single source of truth for conversation progress.
- Privacy: Persist only fields necessary for matching. Avoid storing sensitive PII unless required and protected.
- Rollout: Feature flags control staged rollout; start small and increase as confidence improves.

## 5. Next Phase: Claude Extraction Integration

- Where it plugs in
  - Implement `extraction_layer.py` with a clean interface (extract(text: str, ctx: dict) -> dict).
  - Wire the interface in services/conversational_controller/main.py where `extract_from_text` currently sits.

- Interface Contract
  - Input: raw_text (string), optional context (user_id, session state)
  - Output JSON structure:
    {
      "extracted_fields": { ... },
      "completion_map": { field: 0..1 },
      "confidence_map": { field: 0..1 },
      "overall_confidence": 0..1
    }

- System Prompt
  - Use a dedicated system prompt file curated by product (Shreya) describing the fields to extract, expected formats, and examples.

- Testing
  - Start with unit tests mocking the extraction responses.
  - Add integration tests running against a dev Claude instance once credentials and rate limits are cleared.

---

Document created as a baseline for Day 2 extraction integration work.
