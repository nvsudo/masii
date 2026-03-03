# Conversational Controller (JODI)

This service manages conversation state for the JODI project.

Endpoints
- POST /state/update: create or update conversation state. Accepts session_id, user_id, state_json, confidence.
- GET /state/{session_id}: fetch conversation state.
- POST /state/advance: advance a conversation's progress (used by the planner/extractor).

Configuration
- DATABASE_URL: Postgres connection string
- FEATURE_ROLLOUT_PCT: integer 0-100 to control feature rollout

Run (dev):
- pip install -r services/conversational_controller/requirements.txt
- uvicorn services.conversational_controller.main:app --reload --port 8001

TODOs
- Wire repository to real DB and run alembic migrations
- Implement extractor integration and confidence thresholds
