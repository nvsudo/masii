# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Supabase Databases

### JODI (Matchmaking Platform)

**Project:** JODI Matchmaking  
**Region:** AP South 1 (Mumbai)  
**Created:** 2026-02-10

**Connection Details:**
```
Project ID: herqdldjaxmfusjjpwdg
Database URL (IPv4 pooler): postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres
Supabase URL: https://herqdldjaxmfusjjpwdg.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlcnFkbGRqYXhtZnVzampwd2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MzQ3NzcsImV4cCI6MjA4NjMxMDc3N30.IJF22gilascdOyI4gRFZMyI5PJjwuHAODSlcHxsZ7g4
Service Role Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlcnFkbGRqYXhtZnVzampwd2RnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDczNDc3NywiZXhwIjoyMDg2MzEwNzc3fQ.8gTkUSVIyb7pasm__pav-FGPapAt3ILws6wSzVUTggE
Password: syO9opxb37SlEV9Q
```

**Access:** A, Kavi, Blitz, Seema  
**Schema:** 11 tables (profiles, matches, user_preferences, user_signals, conversation_logs, photos, interactions, match_feedback, tier_progress, profile_readiness, users)  
**Status:** Production - 100+ data point framework deployed (2026-02-21)

**Python Connection:**
```python
import psycopg2
conn = psycopg2.connect("postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres")
```

---

### IGNITION CLUB (Recruitment Platform)

**Project:** IGNITION CLUB Candidate Intelligence  
**Region:** EU West 1 (Ireland)  
**Created:** 2026-02-15

**Connection Details:**
```
Project ID: pfqpkxxkpqnhnspxpirp
Database URL (IPv4 pooler): postgresql://postgres.pfqpkxxkpqnhnspxpirp:1QAfoOaxJRXmHW2g@aws-1-eu-west-1.pooler.supabase.com:5432/postgres
Supabase URL: https://pfqpkxxkpqnhnspxpirp.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmcXBreHhrcHFuaG5zcHhwaXJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3ODY4NDAsImV4cCI6MjA4NjM2Mjg0MH0.eI9ZeP_xZPs9pA5ZcSnqxrtP7NSa_V8ypEzqnP0w4zg
Service Role Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmcXBreHhrcHFuaG5zcHhwaXJwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDc4Njg0MCwiZXhwIjoyMDg2MzYyODQwfQ.j7x8SZKkl9vL6RLqmIvbjWsqeh2mAEDBtrgvNxOx_6Y
Password: 1QAfoOaxJRXmHW2g
```

**Access:** A, Kavi, Blitz, Sam  
**Schema:** 7 tables (conversations, emails_sent, extraction_field_decisions, extraction_runs, haystack_users, processed_messages, users)  
**Status:** Production - Recruitment intelligence platform

**Python Connection:**
```python
import psycopg2
conn = psycopg2.connect("postgresql://postgres.pfqpkxxkpqnhnspxpirp:1QAfoOaxJRXmHW2g@aws-1-eu-west-1.pooler.supabase.com:5432/postgres")
```

---

## Google API (Docs, Drive, Gmail, Calendar)

### 🔐 CANONICAL TOKEN LOCATION (All Agents)
**ONLY use this path for Google OAuth tokens:**
```
/Users/nikunjvora/clawd/ops/credentials/google_tokens.json
```

⚠️ **DO NOT create local copies** — All scripts must reference this canonical location.  
⚠️ **Token expires ~1 hour** — Re-auth with `/clawd/google_reauth.py` if needed.

### Account Structure
- **MY account (AI's working account):** ea.nikvora@gmail.com
  - This is where I create docs, check calendar, send emails
  - I should have FULL permissions on this account
- **YOUR account (human's personal account):** nikunj.vora@gmail.com
  - This is where I SHARE things so you can access them
  - Always share docs/sheets/slides with writer/editor access

### Current Setup
- **Tokens:** `/clawd/ops/credentials/google_tokens.json` ← CANONICAL LOCATION
- **Auth account:** ea.nikvora@gmail.com (MY working account)
- **Helper script:** `google_api.py` (loads from canonical location)

### Current Scopes (✅ COMPLETE as of 2026-02-10)
```
✅ gmail.readonly
✅ gmail.send
✅ gmail.modify
✅ calendar
✅ calendar.events
✅ spreadsheets
✅ documents
✅ presentations
✅ drive (FULL ACCESS - can create, share, organize)
```

### ✅ FIXED: Can Now Share Documents Programmatically
**Status:** Re-authed on 2026-02-10 with full `drive` scope (not `drive.readonly`)

**Now works:**
- ✅ Creating documents, sheets, slides
- ✅ Reading document content
- ✅ Sharing documents (modifying permissions)
- ✅ Moving/organizing files in Drive

### Best Practices
- **Always share with nikunj.vora@gmail.com** (writer/editor access)
- If auto-share fails, return the doc link and ask user to manually share
- Check token expiry before long operations (expires ~1 hour after issue)

### Re-auth Command (when needed)

**📌 REMEMBER: This fixes scope issues instantly**

```bash
python3 /Users/nikunjvora/clawd/google_reauth.py
```

**What it does:** Opens OAuth flow in browser, gets all 9 scopes (Gmail, Calendar, Docs, Sheets, Slides, Drive), updates `/clawd/ops/credentials/google_tokens.json`

**When to run:**
- "Insufficient authentication scopes" error
- Token expired (rare, auto-refreshes normally)
- Need to add new scopes

**Last run:** 2026-02-21 (added Docs scope for JODI tracker)

### Lessons Learned
- 2026-02-10 AM: Hit issue creating Jodi PRD — could create doc but not share it (had `drive.readonly`)
- 2026-02-10 PM: **FIXED** — Re-authed with full `drive` scope. Now can share programmatically.
- **For future:** Use `google_reauth.py` script which requests all needed scopes correctly

## Agent Capability Matrix & Shared Auth

**See:** `/AGENT_CAPABILITIES.md` (comprehensive matrix)

### Shared Google Workspace Access

**All agents** have read/write access to:
- Google Docs
- Google Sheets
- Google Slides
- Google Drive

**Auth Setup:**
- **Account:** ea.nikvora@gmail.com (shared working account)
- **Token file:** `/clawd/ops/credentials/google_tokens.json`
- **Scopes:** docs, sheets, slides, drive, gmail (A + Michael only), calendar (A + Michael only)

**Always share output documents** with nikunj.vora@gmail.com (editor access)

### Exclusive Access

| Agent | Email | Calendar | CRM | Tools |
|-------|-------|----------|-----|-------|
| **A** | ✅ | ✅ | — | All |
| **Michael** | ✅ (with approval) | ✅ | ✅ | Outreach, CRM, Email |
| **Others** | — | — | Varies | See AGENT_CAPABILITIES.md |

---

## Twitter/X API (Read-Only)

**⚠️ Current Access:** Read-only (Bearer token, app-only auth)  
**Posting tweets requires:** OAuth 2.0 User Context (not yet configured)  
**Cost:** $0.005 per tweet read (pay-per-use)

**Credentials:** Stored in `~/.moltbot/moltbot.json` → `env` section
- `TWITTER_BEARER_TOKEN` (for read operations)

**Hard Limits (Cost Control):**
- Max 20 tweets per search query ($0.10 max)
- Max 15 tweets per user timeline ($0.075 max)
- Enforced in helper script

**Helper Script:** `/clawd/twitter_helper.py`

**Usage:**
```bash
# Search tweets
python twitter_helper.py search "GTM strategy EMEA" 20

# Get user's recent tweets
python twitter_helper.py user username 10

# Monitor hashtag
python twitter_helper.py hashtag sales 20

# Search topic (with spam filtering)
python twitter_helper.py topic "revenue operations" 20
```

**From Python:**
```python
import sys
sys.path.insert(0, '/Users/nikunjvora/clawd')
from twitter_helper import search_tweets, get_user_tweets, monitor_hashtag, search_conversation

# Search for conversations
result = search_tweets("fractional CRO", max_results=20)
for tweet in result['tweets']:
    author = tweet.get('author', {})
    metrics = tweet.get('public_metrics', {})
    print(f"{author.get('name')}: {tweet['text']}")
    print(f"  Likes: {metrics.get('like_count')}, RTs: {metrics.get('retweet_count')}\n")

# Monitor hashtag
result = monitor_hashtag("sales", max_results=30)

# Search with spam filtering
result = search_conversation("GTM challenges", exclude_spam=True, max_results=20)
```

**Search Query Operators:**
- `from:username` — Tweets from specific user
- `to:username` — Replies to specific user
- `#hashtag` — Hashtag search
- `"exact phrase"` — Exact match
- `OR` — Boolean OR
- `-term` — Exclude term

**Rate Limits:**
- **Search:** 300 requests per 15 minutes
- **User timeline:** 1500 requests per 15 minutes

**Agent Access (Read-Only):**
- **Main (A):** Search conversations, monitor topics, gather signals
- **Scout:** Find frustrations on Twitter (complement Reddit scans), track trends
- **Greg:** Monitor content performance, analyze competitor content, find engagement opportunities

---

## Cloudflare Pages

**Account ID:** `eb8a91913fdddf8bc12e7c4128a821dc`  
**API Token:** Stored in `~/.moltbot/moltbot.json` → `env.CLOUDFLARE_API_TOKEN`

**Active Projects:**
- **tbw-external** (TBW External site)
  - Production: https://tbw-external.pages.dev
  - Branch deploys: `https://<branch-name>.tbw-external.pages.dev`
  - GitHub repo: https://github.com/nvsudo/tbw_external
  - Build: `npm run build` → output: `out/`

**Deploy via CLI:**
```bash
# Export credentials
export CLOUDFLARE_ACCOUNT_ID=eb8a91913fdddf8bc12e7c4128a821dc
export CLOUDFLARE_API_TOKEN=<from moltbot.json>

# Create new project
npx wrangler pages project create <project-name> --production-branch=main

# Deploy
npx wrangler pages deploy <directory> --project-name=<project-name>
```

**Features:**
✅ Unlimited free hosting (seriously)  
✅ Auto preview deployments per PR  
✅ Build error notifications (email + UI)  
✅ Global CDN  
✅ Custom domains  
✅ Auto-rebuild on push

---

## API Keys & Environment

**Location:** `~/.moltbot/moltbot.json` → `env` section

```json
{
  "env": {
    "OPENAI_API_KEY": "sk-proj-...",
    "GOOGLE_API_KEY": "AIzaSy...",
    "BRAVE_API_KEY": "BSAsd...",
    "GROQ_API_KEY": "gsk_..."
  }
}
```

**Agent-specific overrides:** Store in `/agents/{agent-id}/.env` (not committed to git)

---

## Google Workspace Re-authentication

When scopes change or tokens expire:

```bash
python /Users/nikunjvora/clawd/google_reauth.py
```

This updates `/clawd/ops/credentials/google_tokens.json` with all required scopes.

---

## Environment Setup

### For Local Testing (agent development)

```bash
# Create agent .env file
cat > /agents/{agent-id}/.env <<EOF
OPENAI_API_KEY="your-key"
GOOGLE_API_KEY="your-key"
CRM_API_KEY="your-key"  # If agent needs CRM access
EOF

# Load in scripts
set -a
source /agents/{agent-id}/.env
set +a
```

### For Moltbot (production)

All shared API keys go in `~/.moltbot/moltbot.json` → `env`.

Agent-specific secrets (CRM_API_KEY, GitHub tokens, etc.) can go in agent `.env` files.

---

## Hunter.io API (Domain Search & Email Intelligence)

**API Key:** Stored in `/clawd/ops/credentials/hunter_key.txt`  
**Access:** A, Michael (for CRM email enrichment)  
**Use cases:** Company org chart discovery, verified email enrichment, contact intelligence

**Main Tool:** Network Intel repo (`/clawd/ops/network-intel/`)  
**Documentation:** `/clawd/ops/network-intel/TOOL_DESIGN.md`

**Architecture (Domain-First):**
- One Domain Search per company → Get ALL emails (up to 10 on free plan, 100 on paid)
- Match target contacts by name
- Store ALL discovered emails (targets marked Target=TRUE, others Target=FALSE)
- Result: Full org chart per company in one API call

**Usage:**
```bash
cd /Users/nikunjvora/clawd/ops/network-intel

# Preview pending domains
python3 scripts/enrich.py

# Enrich all pending (with confirmation)
python3 scripts/enrich.py
# (type 'yes' to confirm)

# Auto mode (cron, max 20 domains, no confirmation)
python3 scripts/enrich.py --auto --max 20

# Enrich specific domain
python3 scripts/enrich.py --domain company.com
```

**Output:**
- Full JSON responses saved to `contact_jsons/YYYY-MM-DD/HHMMSS_domain.json`
- Auto-updates Google Sheet (Cold Prospects tab) with:
  - **Target contacts:** Email populated, enrichment fields filled, Target=TRUE
  - **Discovered contacts:** New rows appended, Target=FALSE, full enrichment data
- Enrichment fields: Email, Email Score (0-100), Email Verified, Department, Seniority, LinkedIn, Twitter, Phone, Sources Count, Last Seen, Data Path
- Daily logs to `logs/YYYY-MM-DD.log`

**Automation:**  
Cron job runs daily at 7:00 AM Dubai, enriches up to 20 domains (~$2/run), reports summary via Telegram

**Rate Limits:** 50 searches/month (free plan), 500/mo (Starter), 10 emails/domain (free), 100/domain (paid)  
**Email Score:** 90+ = very confident, 70-89 = confident, <70 = risky

**Cost:** ~$0.10 per domain (5-50x more contacts per dollar vs per-person enrichment)

**2026-02-23 Update:** Migrated to domain-first architecture. Benefits:
- One API call per company (not per contact)
- Full org chart visibility (sales, exec, product, ops)
- Alternative contact paths (if person A doesn't reply, try person B)
- Future-proof (if someone leaves, we have their replacement)

---

## CRM & Tool Integrations

| Tool | Account | Access | Location |
|------|---------|--------|----------|
| Hunter.io | N's account | Email enrichment (A, Michael) | `/clawd/ops/credentials/hunter_key.txt` |
| Pipedrive | N's account | R/W (Michael, Shreya) | CRM_API_KEY in env |
| GitHub | N's account | R/W (Blitz, Kavi) | `.github_pat` file |
| Google Workspace | ea.nikvora@gmail.com | R/W (all) | `google_tokens.json` |
| Gmail | N's account | R/S (A, Michael) | OAuth in google_tokens.json |
| Calendar | N's account | R/W (A, Michael) | OAuth in google_tokens.json |

---

## What Goes Here (Local Setup)

Things like:
- Camera names and locations (if applicable)
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### SSH Hosts
- fly-app → api.fly.io (Blitz uses for deploys)
- prod-db → db.internal (Kavi uses for backups)

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

### Tools
- GitHub repo (main): github.com/N/project
- Design system: Figma (link)
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

Capability matrix (`AGENT_CAPABILITIES.md`) is shared; agent TOOLS.md files are per-agent.

---

Add whatever helps you do your job. This is your cheat sheet.
