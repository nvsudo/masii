# JODI Team Briefing — Feb 11, 2026

**Agent-to-Agent Messaging:** ✅ ENABLED

All agents can now communicate directly. No more message bottlenecks.

---

## Status Update: Shreya ✅ DELIVERED

### Conversational State Management Spec
- **File:** `/JOJI_Conversational_State_Management_Spec.md`
- **Format:** Complete 1-page spec (sections 1-5)
- **Sections:**
  1. Controller API (endpoints, state model, priority tiers)
  2. JSON schema for extracted data + example
  3. System-prompt template (opus/sonnet/gpt-5)
  4. Acceptance criteria & QA tests (numeric thresholds: 0.85 auto, 0.65-0.85 review, <0.65 clarify)
  5. 2-week rollout plan (MVP extractor → gating → testing)

### Key Details
- **Confidence thresholds:** >=0.85 auto-advance | 0.65–0.85 manual review | <0.65 ask clarifying question
- **Priority tiers:** HIGH (80%+ complete) | MED (50–80%) | LOW (<50%)
- **Gating rule:** Don't match until HIGH tier (80%+ + no required fields <0.65)
- **LLM constraint:** opus/sonnet/gpt-5 only (no cheaper models)

---

## Next: Blitz — Implementation

### Deliverable (2-week rollout)
**Week 1:** Controller API + progress indicators
- Build endpoints: POST /state/update, GET /state/{session_id}, POST /state/advance
- Implement progress_pct calculation + priority tier logic
- Integrate opus/sonnet/gpt-5 extractor (use system-prompt template from Shreya's spec)
- Add progress indicator UI: per-step + overall % completion

**Week 2:** Gating logic + QA testing
- Implement gating: block matching until HIGH, manual review for 0.65-0.85, clarifying questions for <0.65
- Run automated QA tests (100-session simulation)
- Soft pilot: 5–10% traffic behind feature flag
- Full release: scale from 5% → 100%

### Resources
- `JOJI_Conversational_State_Management_Spec.md` — implementation guide (all details here)
- `JOJI_PROJECT.md` — project context + team + deadlines
- `docs/ONBOARDING_TECHNICAL.md` — current technical architecture

### Blockers or Questions?
Check the spec. If stuck, ping Shreya or A.

---

## Next: Greg — Content & Tone

### Deliverable (EOW)
**1-page tone guide** + **5-10 rewritten prompts**

### Task
Review onboarding copy for diaspora audience. Current flow is too casual/open-ended.

**Focus areas:**
- Greeting message (warm, auntie-like, welcoming)
- Field prompts (age, location, preferences, values)
- Gap-filling nudges ("I still need your location to make better matches...")
- Match intro ("Here's someone who might click with you...")

### Constraints
- Warm, conversational tone (like talking to an Indian auntie who runs a matchmaking service)
- Guide toward profile completeness (nudges without judgment)
- Diaspora-friendly language (Gujarati references, cultural understanding)

### Resources
- `JOJI_PROJECT.md` — project vision + target audience
- `docs/ONBOARDING_TECHNICAL.md` — current onboarding flow
- Ask N for examples of current bot copy if needed

---

## Next: Kavi — Infra & Monitoring

### Immediate (Parallel with Blitz's work)
1. **Monitoring checklist**
   - Fly.io app (jodi-matchmaker): requests/sec, latency p50/p95/p99, CPU/memory, scaling events
   - Error rate > 1% for 5m → alert
   - p95 latency > 800ms for 5m → alert
   - CPU or memory > 80% for 5m → alert

2. **Database health**
   - Supabase Postgres: connection pooling, indexes, PITR/backups
   - conversation_state persistence: schema validation, transaction atomicity
   - Projections: size growth, query performance

3. **Load testing**
   - Prepare k6 script for Mumbai region
   - Run during Blitz's soft pilot (5–10% traffic window)
   - Capture baseline metrics before rollout

### Deliverables
- Monitoring & alerting playbook (thresholds, runbook actions)
- Database health checklist + optimization suggestions
- Load-testing plan + k6 script
- Production deploy checklist (migrations, canary, rollback)

### Resources
- `JOJI_PROJECT.md` — deployment details (Fly app, Supabase project)
- `docs/ONBOARDING_TECHNICAL.md` — technical architecture
- Access needed: Fly.io (jodi-matchmaker app), Supabase (herqdldjaxmfusjjpwdg)

---

## Timeline

| Week | Blitz (Shipping) | Shreya (Product) | Greg (Content) | Kavi (Infra) |
|------|------------------|------------------|----------------|--------------|
| **This week (2/10-2/14)** | Implement Week 1 (API + progress) | ✅ Spec delivered | Write tone guide + prompts | Monitoring checklist |
| **Next week (2/17-2/21)** | Implement Week 2 (gating + QA) | Review + sign-off | — | Load testing + deploy prep |
| **Week 3 (2/24+)** | Soft pilot (5–10% traffic) | Monitor metrics | — | Monitoring + support |
| **Week 4** | Full rollout (5% → 100%) | — | — | Observability + runbooks |

---

## Key Files (All Agents)

- **`JOJI_PROJECT.md`** — Complete project hub (vision, status, team, decisions)
- **`JOJI_Conversational_State_Management_Spec.md`** — Implementation spec (Shreya's deliverable)
- **`docs/ONBOARDING_TECHNICAL.md`** — Technical architecture & DB schema
- **`MEMORY.md`** — Shared memory (cross-session context)

All files are in the root workspace (`/Users/nikunjvora/clawd/`) and copied to each agent's workspace for easy access.

---

## Questions or Blockers?

- **Product:** Ping Shreya (confidence thresholds, gating logic, priority tiers)
- **Implementation:** Ping Blitz (API integration, feature flags, testing)
- **Content:** Ping Greg (tone, messaging, diaspora audience)
- **Infra:** Ping Kavi (monitoring, database, deployment)
- **Overall:** Ping A or N

---

**Created:** 2026-02-11 10:15 GMT+4  
**Last Updated:** 2026-02-11 10:15 GMT+4

**Distribution:** All agents. Post-session reference.
