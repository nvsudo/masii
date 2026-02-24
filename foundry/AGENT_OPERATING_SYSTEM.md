# AGENT OPERATING SYSTEM

**Version:** 2.0  
**Date:** 2026-02-22  
**Status:** CANONICAL — All agents must follow this

---

## 🎯 Core Principle

**Agents don't work in "time" — they work in threads, heartbeats, queues, and dependencies.**

You're not human. You scale differently. You parallelize differently. You don't sleep.

---

## 📋 TASK EXECUTION PROTOCOL (v2)

**All task execution follows the canonical protocol:**

**→ `/Users/nikunjvora/clawd/TASK_EXECUTION_PROTOCOL.md` ←**

**READ THIS BEFORE STARTING ANY TASK >10 MIN HUMAN-EQUIVALENT.**

Key changes in v2:
- **Central dashboard:** All agents report to A every check cycle
- **Spawn threshold:** Breadth ≥2 = always spawn (maximize parallelization)
- **Check rates:** 2/5/15 min (agent decides based on task complexity)
- **Blocker escalation:** Only [BLOCKER: N] goes to N's Telegram (via A)
- **A can redirect:** At any check cycle, A can shift priorities

**The rest of this document provides context. TASK_EXECUTION_PROTOCOL.md is the execution spec.**

---

## 📊 Work Decomposition Framework

Before starting ANY task, decompose it:

### 1. **Map Dependencies** (Sequential Chain)
- What MUST happen in order?
- Draw the tree: `A → B → C` or `A || B || C`
- **Depth = longest sequential chain**

**Example:**
```
Build matching system:
  Code review (depth 1)
    ↓
  Design algorithm (depth 2)
    ↓
  Implement (depth 3)
    ↓
  Test (depth 4)

DEPTH: 4 (must be sequential)
```

### 2. **Identify Parallelizable Work**
- What can run simultaneously?
- Can you spawn sub-agents?
- **Breadth = max parallel threads**

**Example:**
```
Build Jodi infrastructure:
  Code review || Design queue || Build matching || Build opt-in

BREADTH: 4 (all independent, spawn 4 agents)
```

### 3. **Find Blockers**
- What needs N's decision/approval?
- What's waiting on external input?
- **Blocker = work stops until resolved**

**Tag blockers explicitly:**
- `[BLOCKER: N]` — needs N's decision
- `[BLOCKER: External]` — waiting on API, vendor, etc.
- `[BLOCKER: Agent:Sam]` — waiting on another agent

### 4. **Estimate Heartbeat Cycles**
- **Heartbeat = one check-in cycle** (varies by agent: 30min, 1h, 2h)
- Simple task = 1-2 heartbeats
- Medium task = 3-4 heartbeats
- Complex task = 5-6 heartbeats
- **If >6 heartbeats, break into smaller tasks**

### 5. **Build Your Queue**
- List all tasks
- Mark: `OPERABLE` (can start now) vs `BLOCKED` (waiting)
- Order by: priority, dependencies

**Example Queue:**
```
[OPERABLE] Code review (no dependencies)
[OPERABLE] Build opt-in v1 (independent)
[BLOCKED: N] Choose queue tech (need decision: Celery vs Postgres)
[BLOCKED: Code review] Build matching (waiting for insights)
```

---

## 🔄 Self-Heartbeat Protocol

**Every heartbeat, run this check:**

### 1. **Am I Blocked?**
```
IF current task is BLOCKED:
  ↓
  Log blocker: "Waiting on [X]"
  ↓
  DON'T WAIT SILENTLY
  ↓
  Move to next OPERABLE task in queue
```

### 2. **Can I Unblock Myself?**
```
IF blocker = another agent:
  ↓
  Send message (sessions_send)
  ↓
  Continue on next task while waiting
```

### 3. **Should I Notify N?**
```
IF blocker = needs N's decision:
  ↓
  Flag in Telegram/session: "BLOCKER: Need your input on [X]"
  ↓
  Continue on next OPERABLE task
  ↓
  DON'T STOP ALL WORK
```

### 4. **Queue Management**
```
Check queue:
  ↓
  Any OPERABLE tasks? → Pick highest priority
  ↓
  All BLOCKED? → Report to N: "All tasks blocked, standing by"
  ↓
  Nothing in queue? → Check HEARTBEAT.md for background work
```

---

## 📡 Agent-to-Agent Communication

**You can talk to other agents WITHOUT waiting for N.**

### When to Message Another Agent

- You're blocked on their output
- You need their input/decision
- Coordinating parallel work
- Sharing insights that affect their work

### How to Send Messages

```bash
# Send to another agent
sessions_send(sessionKey="agent:sam:main", message="Your message")

# Example:
sessions_send(
  sessionKey="agent:seema:main",
  message="Code review complete. Found that matching logic needs user preference weights. Recommend adding 'preference_score' field to candidate_profiles. Proceeding with opt-in build (independent)."
)
```

### Response Protocol

- **Don't wait for immediate response** — they'll reply on their heartbeat
- **Check messages every heartbeat** (sessions_history or messages appear in your session)
- **Queue their request** if you receive it

---

## ⚡ Parallelization Decision Tree

### Should I Spawn Sub-Agents?

```
Is the work parallelizable?
  ↓ NO
  Do it yourself sequentially
  
  ↓ YES
  ↓
Is coordination cost low?
  ↓ NO (tasks need constant sync)
  Do it yourself sequentially
  
  ↓ YES (tasks are independent)
  ↓
Spawn sub-agents (sessions_spawn)
  ↓
Monitor progress (sessions_list, sessions_history)
  ↓
Integrate results when complete
```

### Coordination Cost Signals

**LOW (spawn):**
- Tasks share no state
- Output is independent files/modules
- Can integrate at the end

**HIGH (don't spawn):**
- Tasks need constant communication
- Shared mutable state
- Integration is complex

---

## 🎯 Progress Reporting Format

### ❌ Don't Say:
- "This will take 3 days"
- "Working on it"
- "Almost done"

### ✅ Do Say:

**Format:**
```
Task: [Name]
Depth: [N] (sequential steps)
Breadth: [N] (parallel threads)
Blockers: [List or None]
Status: [OPERABLE / BLOCKED / DONE]
Next heartbeat: [What will be complete]
Queue: [What's next if this is blocked]
```

**Example:**
```
Task: Build event-driven matching system

Depth: 4 levels
1. Code review (DONE)
2. Design algorithm (OPERABLE, in progress)
3. Implement (BLOCKED: waiting on step 2)
4. Test (BLOCKED: waiting on step 3)

Breadth: Currently 1 thread (could spawn 2: matching + opt-in)

Blockers: None on current work
         [BLOCKER: N] on queue tech choice (Celery vs Postgres)

Status: OPERABLE (working on algorithm design)

Next heartbeat: Algorithm design complete, implementation started

Queue if blocked:
  - Build opt-in v1 (independent, OPERABLE)
  - Design queue architecture (can draft options while waiting for N)
```

---

## 🔁 Heartbeat Checklist

**Every heartbeat (30min - 2h depending on agent), run through:**

```
[ ] Check current task status
    ↓
[ ] Am I blocked? If YES:
    ↓
    [ ] Can another agent unblock me? → Message them
    [ ] Does N need to decide? → Flag it, don't wait
    [ ] Move to next OPERABLE task
    ↓
[ ] Check messages from other agents
    ↓
    [ ] Any requests? → Add to queue
    [ ] Any blockers resolved? → Resume paused work
    ↓
[ ] Check queue
    ↓
    [ ] Any OPERABLE tasks? → Start highest priority
    [ ] All blocked? → Report status, check HEARTBEAT.md for background work
    ↓
[ ] Report progress (if significant change)
    ↓
[ ] Update queue state for next cycle
```

---

## 🚫 Anti-Patterns (Don't Do This)

### 1. **Silent Waiting**
❌ "I'm waiting for N to decide, so I'm not doing anything"  
✅ "Flagged blocker to N, moved to next task (opt-in build)"

### 2. **Human Time Estimates**
❌ "This will take 2-3 days"  
✅ "Depth 3, breadth 2, done in 4 heartbeats if no blockers"

### 3. **Unnecessary Serialization**
❌ "I'll finish A, then B, then C" (when B and C are independent)  
✅ "Spawn 2 sub-agents for B and C while I do A"

### 4. **Over-Spawning**
❌ Spawn 10 agents for tasks with high coordination cost  
✅ Spawn only when tasks are truly independent

### 5. **Not Using the Queue**
❌ "I'm stuck, nothing to do"  
✅ "Current task blocked, picked next OPERABLE from queue"

### 6. **Ignoring Agent Messages**
❌ Wait for next session to check messages  
✅ Check messages every heartbeat, respond or queue

---

## 📋 Example: Seema's Morning (Using This Framework)

**Tasks Given:**
1. Code review
2. Design event queue
3. Build matching v1
4. Build opt-in v1

### Old Way (Human Thinking):
"4 tasks, 16 hours of work, done by tomorrow"

### New Way (Agent OS):

**Initial Decomposition:**
```
QUEUE STATE (Morning):

[OPERABLE] Code review
  - Depth: 1
  - Breadth: 1
  - Heartbeats: 1
  - Action: Spawn Codex, scan repo

[OPERABLE] Design event queue  
  - Depth: 1 (can design now, implement later)
  - Breadth: 1
  - Heartbeats: 2 (draft options → wait for N's choice)
  - Action: Draft 3 options (Celery, Postgres, Temporal)
  - BLOCKER: N must choose before implementation

[OPERABLE] Build opt-in v1
  - Depth: 2 (design → implement)
  - Breadth: 1
  - Heartbeats: 2-3
  - Action: Can start immediately (independent)

[MAYBE BLOCKED] Build matching v1
  - Depth: 2 (design → implement)
  - Breadth: 1
  - Heartbeats: 3-4
  - Decision: Start now with assumptions OR wait for code review insights?
```

**Parallelization Decision:**
- Code review (1 thread, Codex)
- Opt-in v1 (spawn sub-agent)
- Queue design (draft options myself)
- Matching v1 (spawn sub-agent OR wait for review)

**DECISION: Spawn 3 threads**
1. Main thread: Code review → queue design draft
2. Sub-agent 1: Build opt-in v1
3. Sub-agent 2: Build matching v1 (with assumptions, adjust after review)

**Timeline:**
- Heartbeat 1 (now): All 3 threads started
- Heartbeat 2 (2h): Code review done, opt-in 50%, matching 50%, queue draft ready
- Heartbeat 3 (4h): Opt-in done, matching done, queue BLOCKED on N's choice

**Status to N at Heartbeat 3:**
```
✅ DONE: Code review (insights shared with matching sub-agent)
✅ DONE: Opt-in v1 (Telegram buttons live, tested)
✅ DONE: Matching v1 (basic algorithm, 5-10 matches per profile)
⏸️  BLOCKED: Queue implementation (drafted 3 options, need your choice)

QUEUE:
  - Deploy opt-in to staging (OPERABLE)
  - Test matching with 10 sample profiles (OPERABLE)
  - Implement queue (BLOCKED: waiting on your tech choice)

Next OPERABLE task: Deploying opt-in to staging while waiting for your decision.
```

**No silent waiting. All OPERABLE work done. Blocker flagged. Moving forward.**

---

## 🛠️ Implementation Notes

### For Co-Founders (Sam, Seema)
- This replaces "time estimates" in your thinking
- Read this doc every session start (add to AGENTS.md reading list)
- Use this framework for ALL task planning

### For A (Portfolio Coordinator)
- Use this when delegating to co-founders
- Don't ask "when will it be done?" → ask "what's the depth and blockers?"
- Help resolve blockers, don't create them

### For All Agents
- Check messages every heartbeat (sessions_history)
- Maintain your queue state (what's OPERABLE vs BLOCKED)
- Don't wait silently — flag blockers and move to next task

---

**This is your operating system. Use it.**

*Last updated: 2026-02-20 by A*  
*Changes require N's explicit approval*
