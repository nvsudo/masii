# JODI — Conversational State Management Spec

**Purpose**
Deliver a concise specification for conversational state management for JODI, the Gujarati-diaspora matchmaking bot. Covers Controller API, JSON schema, system-prompt template for opus/sonnet/gpt-5, acceptance criteria & QA, and a 2‑week rollout plan.

---

## 1) Controller API

**Endpoints**
- POST /state/update
  - payload: { session_id, turn_id, extracted_fields, confidence_map, completion_map, timestamp }
  - returns: { ok, new_state_version, next_action, progress_pct, priority_tier }
- GET /state/{session_id}
  - returns full state: { profile_fields, completion_map, confidence_map, progress_pct, priority_tier, pending_questions }
- POST /state/advance
  - payload: { session_id, reason, actor }
  - returns: { ok, matched?:bool, reason }

**Key concepts**
- completion_map: { field_name: { value, filled: bool, source: enum(user, inferred, default), updated_at } }
- confidence_map: { field_name: confidence_score (0.0-1.0) }
- priority_tiers: computed from progress_pct and verification signals:
  - HIGH: progress_pct >= 80% (eligible for matching)
  - MED: 50% <= progress_pct < 80%
  - LOW: progress_pct < 50%
- completion_pct calculation: weighted completeness across required fields (weights defined by product)

---

## 2) JSON schema for extracted data + example

**Schema (concise)**
- required top-level: session_id, turn_id, extracted_fields
- extracted_fields: object of field entries:
  - field_name: { value: string|enum|array, confidence: number, source: "user"|"inferred"|"default", updated_at: ISO8601, weight: number, required: bool }

**Example**

{
  "session_id":"s_1234",
  "turn_id":"t_42",
  "extracted_fields":{
    "name":{"value":"Anita Patel","confidence":0.99,"source":"user","updated_at":"2026-02-11T09:12:00Z","weight":0.1,"required":true},
    "age":{"value":30,"confidence":0.96,"source":"user","updated_at":"2026-02-11T09:12:00Z","weight":0.1,"required":true},
    "community":{"value":"Gujarati","confidence":0.88,"source":"inferred","updated_at":"2026-02-11T09:12:00Z","weight":0.15,"required":true},
    "bio":{"value":"Love cooking and weekend hikes","confidence":0.72,"source":"user","updated_at":"2026-02-11T09:12:00Z","weight":0.2,"required":false}
  }
}

---

## 3) System-prompt template (per turn)

**Purpose:** unify extraction + directive + guardrails so opus/sonnet/gpt-5 reliably extracts fields and produces user-facing text.

**Template** (variables in <>)

"System: You are JODI's extraction assistant. For each user turn, extract values for the target schema fields: <fields_list>. Output ONLY a JSON object with 'extracted_fields' mapping field→{value, confidence (0.00-1.00), source:user|inferred|default}. Follow these rules: 1) If value is explicit from user language, mark source:'user' and confidence ≥0.85. 2) If inferred, mark 'inferred' and confidence reflect model certainty. 3) If uncertain (<0.65) return null for value and confidence. 4) Do not hallucinate. 5) Provide a one-line user-facing directive in separate channel 'next_prompt' when confidence <0.85 suggesting a focused clarifying question. Tone: <tone> (casual|structured)."

**Expected output (parsing-safe)**

{ "extracted_fields": {...}, "next_prompt": "Quick clarifier: Which city in Gujarat are you from?" }

---

## 4) Acceptance criteria & QA tests

**Gate rules**
- progress_pct >= 80% AND no required field with confidence < 0.65 -> eligible for match
- If required fields exist with 0.65 <= confidence < 0.85 → surface for manual review or present inline clarification prompt
- If any required field confidence < 0.65 → block advance and ask clarifying question

**Numeric thresholds (defaults)**
- Auto-advance: >=0.85
- Manual review band: 0.65–0.85
- Clarify: <0.65

**QA test cases**
- Unit: inject synthetic turns with known entities -> assert extracted_fields match ground truth and confidence within expected buckets
- Edge: ambiguous input ("I'm from near Bombay") -> expect city=null/confidence<0.65 and next_prompt asks to clarify
- Regression: previously solved fields persist across turns (idempotency)
- Acceptance: Simulate 100 sessions; require >=95% of sessions that should be eligible flagged as HIGH and passed gating correctly
- UX: Verify progress indicator increments per step and overall percentage equals computed completeness

**Monitoring**
- Dashboard metrics: extraction accuracy over labeled data, % sessions blocked for low confidence, average time to completion, manual review queue size

---

## 5) 2-week rollout plan (MVP extractor → gating → testing)

**Prep (Day 0)**
- Finalize required fields + weights. Pull onboarding steps from docs/ONBOARDING_TECHNICAL.md.
- Provision feature flags for gating and tone slider.

**Week 1 (MVP extractor + progress indicators)**
- Day 1–2: Implement Controller API endpoints and state model; add progress_pct and priority tier computation.
- Day 3–5: Integrate opus/sonnet/gpt-5 extractor flow using system-prompt template; return extracted_fields + confidence_map.
- Day 5: UI update — show per-step progress + overall % and “You’re X% complete” nudges.
- Deliverable: Internal staging with extraction logs and visual progress.

**Week 2 (Gating + QA + rollout)**
- Day 8–10: Implement gating logic (block matching until HIGH), manual review UI for 0.65–0.85 band, clarifying question flow for <0.65.
- Day 11: Run automated QA tests and simulate 100 sessions (acceptance criteria).
- Day 12: Soft pilot: 5–10% of traffic behind feature flag; monitor metrics.
- Day 13–14: Triage issues, tune thresholds if needed, full release behind feature flag off -> onboard 100% when metrics stable.

**Post-MVP (nice-to-have)**
- Implement tone slider (casual↔structured) and A/B test impact on completion rates.
- Add incremental profiling nudges and smart defaults.

---

**Notes / Constraints**
- LLM constraint: all conversational extraction calls must use opus/sonnet/gpt-5 (no fallbacks to smaller models for the extraction layer).
- Privacy: store only fields required for matching; PII encryption at rest; keep consent flow in onboarding.

**Owner:** Shreya (Product & GTM)

---

File generated and placed at: /Users/nikunjvora/clawd/JODI_Conversational_State_Management_Spec.md
