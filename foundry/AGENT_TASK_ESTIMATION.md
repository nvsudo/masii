# Agent Task Estimation Framework

**A practical framework for estimating effort when delegating work between AI agents.**

Use this when spawning sub-agents, delegating tasks, or estimating how long agent work will take.

---

## The Problem

When Agent A asks Agent B to do something, how much work is it *actually*?

- "Write a blog post" — 5 minutes or 5 hours?
- "Research competitors" — 10 web searches or 100?
- "Build a dashboard" — a single page or a full system?

Without a shared estimation framework, agents either:
- **Under-scope** (spawn sub-agents that fail because the task is too big)
- **Over-scope** (waste tokens on trivial work)
- **Mis-scope** (assign the wrong model/timeout/autonomy level)

This framework gives you **four dimensions** to estimate agent work:

1. **Depth** — How many steps/layers deep?
2. **Breadth** — How many parallel branches?
3. **Heartbeats** — How many LLM turns required?
4. **Dependencies** — What needs to exist first?

---

## The Four Dimensions

### 1. Depth (Vertical Complexity)

**"How many layers deep does this task go?"**

Think of depth like a decision tree or folder structure:

- **Depth 1:** Single action, no sub-tasks
  - Example: "Read file X and return line 5"
  
- **Depth 2:** One level of sub-tasks
  - Example: "Read file X, parse JSON, return the 'email' field"
  
- **Depth 3:** Two levels of sub-tasks
  - Example: "Read file X, parse JSON, validate email format, send test email, confirm delivery"
  
- **Depth 4+:** Multi-level recursion
  - Example: "Analyze codebase → identify files → parse each file → extract functions → generate docs → create index"

**Rule of thumb:**
- Depth 1-2: Single agent turn, synchronous
- Depth 3-4: Spawn sub-agent or background session
- Depth 5+: Break into phases, use persistent state

### 2. Breadth (Horizontal Complexity)

**"How many parallel things need to happen?"**

Breadth = number of independent branches:

- **Breadth 1:** Linear workflow (A → B → C)
  - Example: "Fetch data → transform → save"
  
- **Breadth 2-5:** Few parallel paths
  - Example: "Check 3 APIs for pricing data, return cheapest"
  
- **Breadth 6-20:** Moderate parallelism
  - Example: "Scan 15 subreddits for specific keywords"
  
- **Breadth 21+:** High parallelism
  - Example: "Enrich 100 LinkedIn profiles"

**Rule of thumb:**
- Breadth 1-5: Single agent, sequential processing
- Breadth 6-20: Single agent, batch processing
- Breadth 21+: Rate-limit, paginate, or spawn workers

### 3. Heartbeats (LLM Turns Required)

**"How many LLM inference calls will this take?"**

Heartbeats = number of times the agent needs to "think":

- **1 heartbeat:** Single inference
  - Example: "Summarize this 500-word article"
  
- **2-3 heartbeats:** Read → Think → Act
  - Example: "Read file, decide if it needs updating, update if yes"
  
- **4-10 heartbeats:** Iterative refinement
  - Example: "Draft email → review tone → revise → final check → send"
  
- **11-50 heartbeats:** Complex workflow
  - Example: "Research topic → outline → write 5 sections → edit → format → publish"
  
- **51+ heartbeats:** Long-running process
  - Example: "Monitor inbox hourly for a week, respond to emails"

**Rule of thumb:**
- 1-3 heartbeats: Synchronous, inline
- 4-10 heartbeats: Async sub-agent, ~5-15 min timeout
- 11-50 heartbeats: Background session, ~30-60 min timeout
- 51+ heartbeats: Cron job or persistent worker

### 4. Dependencies (Blockers & Sequencing)

**"What needs to exist or happen before this task can start?"**

Dependencies = external requirements:

- **No dependencies:** Can start immediately
  - Example: "Generate 10 startup ideas"
  
- **Data dependencies:** Needs input from elsewhere
  - Example: "Summarize Scout's report" (needs Scout to finish first)
  
- **Auth dependencies:** Needs credentials/permissions
  - Example: "Send email via Gmail" (needs OAuth token)
  
- **State dependencies:** Needs previous step to complete
  - Example: "Deploy to staging" (needs tests to pass first)
  
- **Human dependencies:** Needs approval/input
  - Example: "Send outreach email" (needs N to approve draft)

**Rule of thumb:**
- Zero dependencies: Spawn immediately
- 1-2 dependencies: Check readiness, spawn when clear
- 3+ dependencies: Use workflow orchestrator or queue

---

## Estimation Matrix

Combine the dimensions to estimate effort:

| Depth | Breadth | Heartbeats | Dependencies | Effort Level | Best Approach |
|-------|---------|------------|--------------|--------------|---------------|
| 1-2 | 1-5 | 1-3 | 0-1 | **Trivial** | Inline, synchronous |
| 2-3 | 1-10 | 3-10 | 1-2 | **Simple** | Sub-agent, 5-15 min timeout |
| 3-4 | 5-20 | 10-30 | 2-3 | **Moderate** | Background session, 30-60 min |
| 4-5 | 10-50 | 30-100 | 3-4 | **Complex** | Persistent worker, checkpoints |
| 5+ | 50+ | 100+ | 4+ | **Epic** | Multi-phase project, orchestration |

---

## Examples

### Example 1: "Create a Google Doc with the schema"

**Depth:** 2 (create doc → share with N)  
**Breadth:** 1 (linear)  
**Heartbeats:** 2 (call API → verify success)  
**Dependencies:** 1 (needs Google OAuth token)  

**Estimation:** Simple  
**Approach:** Spawn sub-agent, 5 min timeout, synchronous reply

---

### Example 2: "Enrich 100 contacts from CRM"

**Depth:** 2 (read sheet → enrich each row)  
**Breadth:** 100 (one per contact)  
**Heartbeats:** ~50 (batch API calls, process results, update sheet)  
**Dependencies:** 2 (needs Hunter.io API key + Google Sheets access)  

**Estimation:** Moderate  
**Approach:** Background session, 30 min timeout, batch processing (max 20/run), report when done

---

### Example 3: "Research competitors and write analysis"

**Depth:** 4 (identify competitors → research each → synthesize findings → write report)  
**Breadth:** ~10 (research 10 competitors in parallel)  
**Heartbeats:** ~40 (web searches, reading, synthesis, writing, editing)  
**Dependencies:** 1 (needs web search access)  

**Estimation:** Moderate-Complex  
**Approach:** Spawn research sub-agent (Opus for synthesis), 45 min timeout, deliver Google Doc when done

---

### Example 4: "Monitor inbox and reply to urgent emails"

**Depth:** 3 (check inbox → classify → respond)  
**Breadth:** Variable (depends on email volume)  
**Heartbeats:** Indefinite (runs continuously)  
**Dependencies:** 2 (Gmail access + CRM context)  

**Estimation:** Epic (ongoing)  
**Approach:** Cron job (every 30 min), isolated session, timeout per run = 5 min

---

## Best Practices

### 1. Estimate Before You Delegate

Before spawning a sub-agent or delegating to another agent:

```
Task: [Describe the task]
Estimated Depth: X
Estimated Breadth: X
Estimated Heartbeats: X
Dependencies: [List them]
→ Effort Level: [Trivial|Simple|Moderate|Complex|Epic]
→ Approach: [How you'll execute]
```

### 2. Right-Size Your Resources

**Model selection:**
- Trivial/Simple: Haiku, GPT-4o-mini
- Moderate: Sonnet, GPT-4o
- Complex: Opus (for strategy/synthesis), Sonnet (for execution)

**Timeout:**
- Trivial: 1-5 min
- Simple: 5-15 min
- Moderate: 15-60 min
- Complex: 1-3 hours
- Epic: No timeout (use checkpoints instead)

**Session type:**
- Inline: Depth 1-2, Heartbeats 1-3
- Spawn sub-agent: Depth 2-4, Heartbeats 3-30
- Background session: Depth 3-5, Heartbeats 10-100
- Cron/persistent: Ongoing work

### 3. Break Down Epic Tasks

If your estimate shows **Epic** effort:

1. **Phase it:** Break into Moderate chunks
2. **Checkpoint:** Save state between phases
3. **Delegate:** Use multiple sub-agents in parallel
4. **Orchestrate:** One coordinator agent manages the phases

Example:
```
Epic task: "Build entire matching system for Jodi"

Phase 1 (Moderate): Design data schema
Phase 2 (Moderate): Build profile capture bot
Phase 3 (Complex): Implement matching algorithm
Phase 4 (Simple): Create admin dashboard
Phase 5 (Moderate): Testing & refinement
```

### 4. Communicate Estimates

When delegating to another agent:

**Bad:**
> "Hey Kavi, build the database schema."

**Good:**
> "Hey Kavi, build the database schema.
> 
> Estimated effort: Moderate
> - Depth 3: Design schema → create migration → test
> - Breadth ~15: 15 tables
> - Heartbeats ~20: Review spec, design, iterate
> - Dependencies: Supabase access
> 
> Expected delivery: 30-45 min
> Deliverable: Migration SQL + schema diagram"

### 5. Track Actuals vs Estimates

After task completion, compare:

```
Estimated heartbeats: 20
Actual heartbeats: 35

Why? Discovered 5 edge cases during implementation.
Learning: Add +50% buffer for schema design tasks.
```

Build your own calibration over time.

---

## Common Patterns

### Pattern 1: The Quick Check

**Depth:** 1  
**Breadth:** 1  
**Heartbeats:** 1  
**Dependencies:** 0  

Examples: "Is file X present?", "What's the current time in Dubai?", "Count rows in sheet Y"

**Approach:** Inline, synchronous

---

### Pattern 2: The Research Task

**Depth:** 3-4  
**Breadth:** 5-20  
**Heartbeats:** 20-50  
**Dependencies:** Web search access  

Examples: "Find top 10 competitors in X market", "Research Y regulation in EU"

**Approach:** Spawn sub-agent (Opus for analysis), 30-45 min timeout

---

### Pattern 3: The Content Creation

**Depth:** 4  
**Breadth:** 1-5  
**Heartbeats:** 30-60  
**Dependencies:** Context/research, brand voice  

Examples: "Write blog post on X", "Create 5-email nurture sequence"

**Approach:** Spawn sub-agent (Opus for writing, Sonnet for editing), deliver Google Doc

---

### Pattern 4: The Data Pipeline

**Depth:** 2-3  
**Breadth:** 10-1000  
**Heartbeats:** Variable (batch size)  
**Dependencies:** API keys, auth  

Examples: "Enrich 500 contacts", "Process 100 support tickets"

**Approach:** Background session, batch processing, rate limiting, progress checkpoints

---

### Pattern 5: The Ongoing Monitor

**Depth:** 2-3  
**Breadth:** Variable  
**Heartbeats:** Infinite  
**Dependencies:** Access to monitored system  

Examples: "Monitor inbox every 30 min", "Check deployment status hourly"

**Approach:** Cron job, isolated session per run, state persistence between runs

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Scope Creep

**Bad:**
> "Build a dashboard" (no depth/breadth defined)

**Result:** Agent builds either a 1-page mockup or a full enterprise BI system

**Fix:** Specify depth/breadth explicitly

---

### ❌ Anti-Pattern 2: Timeout Mismatch

**Bad:**
> Complex task (Depth 5, Heartbeats 100) with 5-minute timeout

**Result:** Agent times out mid-work, loses all progress

**Fix:** Match timeout to estimated heartbeats (or use checkpoints)

---

### ❌ Anti-Pattern 3: Missing Dependencies

**Bad:**
> Spawn sub-agent without checking if API keys exist

**Result:** Agent fails immediately, wastes a turn

**Fix:** Validate dependencies before spawning

---

### ❌ Anti-Pattern 4: Over-Parallelization

**Bad:**
> Spawn 50 sub-agents to process 50 items

**Result:** API rate limits, context explosion, orchestration nightmare

**Fix:** Batch in single agent with rate limiting

---

## Integration with Agent Systems

### Moltbot Example

When using `sessions_spawn`:

```javascript
sessions_spawn({
  agentId: "researcher",
  task: "Research top 5 CRMs for SMBs. Depth: 3 (identify → research features → compare). Breadth: 5. Heartbeats: ~25. Dependencies: web search.",
  model: "anthropic/claude-opus-4-5",  // Complex analysis
  runTimeoutSeconds: 2400,  // 40 min (25 heartbeats × ~90s/heartbeat)
  cleanup: "delete"
})
```

### OpenAI Swarm Example

```python
# Estimate before delegating
task_estimate = {
    "depth": 3,
    "breadth": 10,
    "heartbeats": 30,
    "dependencies": ["api_key", "database_access"]
}

if task_estimate["heartbeats"] > 20:
    # Spawn sub-agent
    result = agent.handoff(
        "data_processor",
        context=task_estimate,
        timeout=1800  # 30 min
    )
else:
    # Handle inline
    result = process_inline()
```

### LangGraph Example

```python
# Add estimation node to workflow
def estimate_effort(state):
    depth = calculate_depth(state["task"])
    breadth = calculate_breadth(state["task"])
    heartbeats = estimate_heartbeats(depth, breadth)
    
    if heartbeats > 50:
        return {"route": "background_worker"}
    else:
        return {"route": "inline_execution"}
```

---

## Calibration Guide

Track your estimates over time:

| Task Type | Est. Heartbeats | Actual Heartbeats | Accuracy |
|-----------|-----------------|-------------------|----------|
| Blog post (1000 words) | 30 | 42 | -40% |
| API integration | 15 | 12 | +20% |
| Schema design | 20 | 35 | -75% |

**Learnings:**
- Writing tasks: Add +30% buffer (editing takes longer than expected)
- Schema design: Add +50% buffer (edge cases emerge during design)
- API integration: Usually accurate (well-defined scope)

---

## References

- **Depth/Breadth:** Inspired by Big-O notation and search algorithms
- **Heartbeats:** Anthropic's usage of "turns" in agent workflows
- **Dependencies:** Classic project management (PERT/CPM)

---

## Contributing

This framework is a living document. Improve it:

1. **Add examples** from your agent workflows
2. **Share calibration data** (estimated vs actual)
3. **Propose new dimensions** (what's missing?)
4. **Report anti-patterns** you've discovered

---

## License

MIT License — use freely, credit appreciated

---

**Created by:** A (Moltbot main agent)  
**Last updated:** 2026-02-20  
**Version:** 1.0  
**GitHub:** [link when published]
