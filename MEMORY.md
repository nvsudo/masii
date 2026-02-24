# MEMORY.md - World Model Log

Curated memory for cross-session context. Older entries archived to `memory/archive-2026-02-early.md`.

---

## 📚 Foundational Docs

**Read these first:**
- **Workspace Structure:** `/clawd/README.md` — Complete file organization and folder purposes
- **Agent Operating System:** `/clawd/foundry/AGENT_OPERATING_SYSTEM.md` — How agents work (threads, heartbeats, queues, v2.0)
- **Task Estimation Framework:** `/clawd/foundry/AGENT_TASK_ESTIMATION.md` — Depth/breadth/heartbeats concepts for scoping work
- **Task Execution Protocol:** `/clawd/TASK_EXECUTION_PROTOCOL.md` — PLAN → EXECUTE → REPORT → CHECK (mandatory for tasks >10min)

---

## 📋 Team & Structure

**Source of truth:** `TEAM_HANDBOOK.md`

**Main Agents:** A (main), Kavi, Blitz, Michael, Scout, Greg, Xing, DevOps, Sam, Seema
**Models:** Opus (Xing only), Sonnet (most agents), Haiku (Michael), GPT-5-mini (Scout)
**Agent-to-agent:** Enabled (`tools.agentToAgent.enabled=true`)

---

## 🎯 Core Operating Principles (Feb 15)

1. **Push back on over-engineering:** When N designs schemas/visions before user validation → stop him. Mom test first, speak to 10 users, build hacky first.
2. **Build hacky, ship fast:** Prototypes > perfect systems. Revenue > features. Cash is the signal.
3. **Agentic velocity:** Think in hours, not weeks. 100-300x faster than human estimates with proper spawning.
4. **Distribution lens:** Always ask: How do people find solutions? Can agents automate distribution?

---

## 🚀 Active Projects

### JODI (Diaspora Matchmaking)
- **Status:** Schema deployed, onboarding flow designed
- **DB:** Supabase (herqdldjaxmfusjjpwdg), 100+ data point framework
- **GitHub:** https://github.com/nvsudo/jodi
- **Architecture:** Tier-based onboarding (T1→T2→T3→T4), out-of-order capture, matching in async batch (Phase 2)
- **Co-founder:** Seema

### Ignition Club (AI Recruitment Intelligence)
- **Status:** MVP live, email-first
- **Intake:** talent.haystack@gmail.com
- **DB:** Supabase (pfqpkxxkpqnhnspxpirp)
- **Core:** Verify performance (quota docs, W2s), context indexing, fit scoring
- **Co-founder:** Sam

---

## 🤖 Agent Configurations

### Michael (Executive Assistant)
- Telegram group: -5152042869
- Role: Inbox triage, scheduling, CRM-first comms
- Model: Haiku
- CRM: https://docs.google.com/spreadsheets/d/1F6BjFpuVrD7-Ai9k9kuUf5n_A5L-Zu-4aTTL5fqBS7M/edit
- Cron: 15-min inbox monitoring (ea.nikvora@gmail.com)

### Scout (Opportunity Scanner)
- Runs: Nightly 11:30 PM Dubai
- Mode: Validation research + distribution lens
- Features: PAST_IDEAS.md dedup, subreddit rotation, feedback loop

### Greg (Content)
- Drive folder: https://drive.google.com/drive/folders/1H0oBy-hIorl0EbUsB36mDJuAebp3of37
- Drafts: https://drive.google.com/drive/folders/1KXBP_Y3UMLzp4s3oqdz0mCzpCEzRiakV
- Workflow: Creates Google Docs → N reviews → Manual publish

---

## 🔧 Key Tooling

### CRM (Google Sheets)
- **URL:** https://docs.google.com/spreadsheets/d/1F6BjFpuVrD7-Ai9k9kuUf5n_A5L-Zu-4aTTL5fqBS7M/edit
- **Sheets:** Main, Cold Prospects, Personal
- **Rule:** Anyone emailed → move from Cold to Personal

### Network Intel (Hunter.io)
- **Repo:** `/clawd/ops/network-intel/`
- **Cost:** ~$0.10/contact (domain search)
- **Cron:** 7:00 AM Dubai, max 20/run
- **Key:** `/clawd/ops/credentials/hunter_key.txt`

### Twitter/X API
- **Access:** Read-only (bearer token)
- **Cost:** $0.005/tweet
- **Helper:** `/clawd/twitter_helper.py`
- **Limits:** Max 20 tweets/search (enforced)

### Google Workspace
- **Tokens:** `/clawd/ops/credentials/google_tokens.json` (CANONICAL)
- **Account:** ea.nikvora@gmail.com (working), share to nikunj.vora@gmail.com
- **Re-auth:** `python3 /clawd/google_reauth.py`

---

## 📝 Recent Decisions

### 2026-02-24
- **Redis ANZ role:** Mark Peet passed — cited "not intentional" concern despite N's 4-year tenure track record. Clean rejection, no bridge burned.
- **Xpresso GTM #1:** Outreach sent to Rasmus Rothe (Merantix, lead investor in Xpresso). Exploring GTM role.
- **CRM rule:** Anyone emailed moves from Cold Prospects → Personal sheet.

### 2026-02-20
- Network Intel migrated from Apollo to Hunter.io (5x cost reduction)

### 2026-02-19
- Identity update: "AI Partner" not "AI Assistant"
- Scout upgraded: Validation research mode + distribution lens

### 2026-02-24 00:10
- **Agentic velocity lesson:** Behavr MVP shipped in 2 hours vs 8-12 week estimate. 100-300x faster with proper spawning. Default aggressive estimates going forward.

---

## 🔑 Quick Reference

- **GitHub PAT:** `/clawd/.github_pat`
- **Supabase (JODI):** herqdldjaxmfusjjpwdg (Mumbai)
- **Supabase (Ignition):** pfqpkxxkpqnhnspxpirp (Ireland)
- **Google tokens:** `/clawd/ops/credentials/google_tokens.json`
- **Hunter key:** `/clawd/ops/credentials/hunter_key.txt`
