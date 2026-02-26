# Prompt Library MVP - Plan V2

**Core thesis:** Agents need a library of battle-tested prompts. Track what works (signals), iterate (versioning), designed for programmatic access.

---

## Scope: Free Prompts + Signals + Versioning

**User actions:**
1. Submit prompt
2. Search prompts
3. Use prompt (fetch via UI or API)
4. Signal: upvote/downvote
5. Signal: leave feedback
6. Signal: track fetches/usage
7. Create new version (fork/iterate)

**Agent actions:**
- Fetch prompts via API
- Submit improved versions
- Track upstream/downstream version chains

---

## Task Estimation

**Depth:** 3-4 (submit → use → track signals → version management)  
**Breadth:** 7 features (submit, search, use, upvote, feedback, track, version)  
**Heartbeats (build):** ~20-30 (schema design, API routes, UI, deploy)  
**Dependencies:** Fly.io Postgres, API design, version graph logic

**Effort Level:** **Simple-Moderate**  
**Time Estimate:** **2-3 hours** (agent build)  
**Human Time Equivalent:** 16-24 hours

---

## Architecture

**Stack:**
- **DB:** Fly.io Postgres (provisioned via `fly postgres create`)
- **Backend:** Node.js/Express API (or Next.js API routes)
- **Frontend:** Next.js + Tailwind
- **Deploy:** Fly.io (backend + static frontend)
- **Auth:** Optional for v1 (API key for agents, public for humans)

---

## Database Schema

```sql
-- Core entity
CREATE TABLE prompts (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  prompt_text TEXT NOT NULL,
  category VARCHAR(100),
  tags TEXT[], -- array of strings
  submitted_by VARCHAR(255), -- username or agent id
  
  -- Versioning
  upstream_id INTEGER REFERENCES prompts(id), -- previous version (null if original)
  downstream_id INTEGER REFERENCES prompts(id), -- next version (null if latest)
  version_number INTEGER DEFAULT 1,
  version_notes TEXT, -- what changed in this version
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Computed (updated via triggers or app logic)
  fetch_count INTEGER DEFAULT 0,
  upvote_count INTEGER DEFAULT 0,
  downvote_count INTEGER DEFAULT 0,
  feedback_count INTEGER DEFAULT 0,
  
  -- Status
  is_deprecated BOOLEAN DEFAULT FALSE, -- mark old versions
  is_latest_in_chain BOOLEAN DEFAULT TRUE -- only one TRUE per version chain
);

-- Signals: Fetches
CREATE TABLE prompt_fetches (
  id SERIAL PRIMARY KEY,
  prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
  fetched_by VARCHAR(255), -- user id, agent id, or IP
  fetched_at TIMESTAMP DEFAULT NOW(),
  source VARCHAR(50), -- 'web', 'api', 'cli'
  
  INDEX idx_prompt_fetches_prompt_id (prompt_id),
  INDEX idx_prompt_fetches_fetched_at (fetched_at)
);

-- Signals: Votes
CREATE TABLE prompt_votes (
  id SERIAL PRIMARY KEY,
  prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
  voted_by VARCHAR(255) NOT NULL, -- user id or session id
  vote_type VARCHAR(10) CHECK (vote_type IN ('upvote', 'downvote')),
  voted_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE (prompt_id, voted_by), -- one vote per user per prompt
  INDEX idx_prompt_votes_prompt_id (prompt_id)
);

-- Signals: Feedback
CREATE TABLE prompt_feedback (
  id SERIAL PRIMARY KEY,
  prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
  feedback_text TEXT NOT NULL,
  submitted_by VARCHAR(255), -- user id or agent id
  submitted_at TIMESTAMP DEFAULT NOW(),
  
  -- Optional: rating/sentiment
  rating INTEGER CHECK (rating BETWEEN 1 AND 5), -- 1-5 stars
  
  INDEX idx_prompt_feedback_prompt_id (prompt_id),
  INDEX idx_prompt_feedback_submitted_at (submitted_at)
);

-- Optional: Users (defer to v2 if no auth in v1)
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  api_key VARCHAR(255) UNIQUE, -- for agent access
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes:**
```sql
-- Search
CREATE INDEX idx_prompts_title ON prompts USING gin(to_tsvector('english', title));
CREATE INDEX idx_prompts_prompt_text ON prompts USING gin(to_tsvector('english', prompt_text));
CREATE INDEX idx_prompts_tags ON prompts USING gin(tags);
CREATE INDEX idx_prompts_category ON prompts(category);

-- Versioning
CREATE INDEX idx_prompts_upstream_id ON prompts(upstream_id);
CREATE INDEX idx_prompts_downstream_id ON prompts(downstream_id);
CREATE INDEX idx_prompts_latest_in_chain ON prompts(is_latest_in_chain) WHERE is_latest_in_chain = TRUE;

-- Sorting
CREATE INDEX idx_prompts_created_at ON prompts(created_at DESC);
CREATE INDEX idx_prompts_upvote_count ON prompts(upvote_count DESC);
CREATE INDEX idx_prompts_fetch_count ON prompts(fetch_count DESC);
```

**Triggers (auto-update counts):**
```sql
-- Update upvote_count on prompts table
CREATE OR REPLACE FUNCTION update_prompt_vote_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prompts
  SET 
    upvote_count = (SELECT COUNT(*) FROM prompt_votes WHERE prompt_id = NEW.prompt_id AND vote_type = 'upvote'),
    downvote_count = (SELECT COUNT(*) FROM prompt_votes WHERE prompt_id = NEW.prompt_id AND vote_type = 'downvote')
  WHERE id = NEW.prompt_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_vote_count
AFTER INSERT OR UPDATE OR DELETE ON prompt_votes
FOR EACH ROW EXECUTE FUNCTION update_prompt_vote_count();

-- Update fetch_count
CREATE OR REPLACE FUNCTION update_prompt_fetch_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prompts
  SET fetch_count = (SELECT COUNT(*) FROM prompt_fetches WHERE prompt_id = NEW.prompt_id)
  WHERE id = NEW.prompt_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fetch_count
AFTER INSERT ON prompt_fetches
FOR EACH ROW EXECUTE FUNCTION update_prompt_fetch_count();

-- Update feedback_count
CREATE OR REPLACE FUNCTION update_prompt_feedback_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prompts
  SET feedback_count = (SELECT COUNT(*) FROM prompt_feedback WHERE prompt_id = NEW.prompt_id)
  WHERE id = NEW.prompt_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_feedback_count
AFTER INSERT OR DELETE ON prompt_feedback
FOR EACH ROW EXECUTE FUNCTION update_prompt_feedback_count();
```

---

## API Design (for Agents)

**Base URL:** `https://prompts.yourapp.dev/api/v1`

### 1. Search Prompts
```
GET /prompts/search?q=<query>&category=<cat>&tags=<tag1,tag2>&limit=20
```
**Response:**
```json
{
  "prompts": [
    {
      "id": 123,
      "title": "System prompt for code review",
      "prompt_text": "You are an expert...",
      "category": "code",
      "tags": ["review", "quality"],
      "signals": {
        "fetches": 450,
        "upvotes": 89,
        "downvotes": 3,
        "feedback_count": 12
      },
      "version": {
        "number": 2,
        "upstream_id": 122,
        "downstream_id": null,
        "is_latest": true
      },
      "created_at": "2026-02-20T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1
}
```

### 2. Get Prompt (with tracking)
```
GET /prompts/:id?fetched_by=<agent_id>&source=api
```
**Response:**
```json
{
  "id": 123,
  "title": "...",
  "prompt_text": "...",
  "signals": { ... },
  "version": { ... },
  "version_chain": [
    {"id": 120, "version": 1, "created_at": "..."},
    {"id": 122, "version": 2, "created_at": "..."},
    {"id": 123, "version": 3, "created_at": "...", "is_latest": true}
  ]
}
```
**Side effect:** Increments `fetch_count`, logs to `prompt_fetches`

### 3. Submit New Prompt
```
POST /prompts
{
  "title": "System prompt for X",
  "prompt_text": "...",
  "category": "code",
  "tags": ["review", "python"],
  "submitted_by": "agent_blitz"
}
```

### 4. Submit New Version
```
POST /prompts/:id/version
{
  "prompt_text": "...", // updated text
  "version_notes": "Improved handling of edge cases",
  "submitted_by": "agent_blitz"
}
```
**Logic:**
- Creates new prompt row
- Sets `upstream_id` to original prompt
- Updates original's `downstream_id` to new prompt
- Marks original as `is_latest_in_chain = FALSE`
- New prompt is `is_latest_in_chain = TRUE`
- Auto-increments `version_number`

### 5. Vote
```
POST /prompts/:id/vote
{
  "voted_by": "agent_blitz",
  "vote_type": "upvote" // or "downvote"
}
```
**Logic:** Upsert (if user already voted, update their vote)

### 6. Submit Feedback
```
POST /prompts/:id/feedback
{
  "feedback_text": "Works great for Python, struggles with Go",
  "submitted_by": "agent_blitz",
  "rating": 4 // optional 1-5
}
```

---

## UI Pages

**1. Home / Browse (`/`)**
- Grid view of prompts
- Sort by: Latest, Most Used, Top Rated
- Filter by: Category, Tags
- Search bar (full-text)

**2. Submit Prompt (`/submit`)**
- Form: Title, Prompt Text, Category, Tags
- Optional: `submitted_by` (default: anonymous)

**3. Prompt Detail (`/prompt/:id`)**
- Display full prompt text
- Copy button (tracks fetch)
- Signals: Upvote/downvote buttons, feedback form
- Version chain (if applicable): "← v1 | v2 (you are here) | v3 →"
- Feedback comments below

**4. Version History (`/prompt/:id/versions`)**
- Show full version chain
- Diff view (what changed between versions)
- Link to each version

---

## Versioning Logic

**Scenario 1: Agent updates own prompt**
```
Original prompt (id=100, version=1)
  ↓
Agent fetches id=100, improves it, submits version
  ↓
New prompt (id=101, version=2, upstream_id=100)
Original (id=100, downstream_id=101, is_latest=FALSE)
```

**Scenario 2: Multiple forks (future)**
```
Original (v1, id=100)
  ↓
Agent A creates v2 (id=101, upstream_id=100)
Agent B creates v2b (id=102, upstream_id=100)  ← fork

Result: Two branches from same upstream
```
For v1, we'll only support **linear chains** (one downstream per prompt). Forks in v2.

**Scenario 3: Deprecation**
When a prompt is outdated:
```
UPDATE prompts SET is_deprecated = TRUE WHERE id = 100;
```
Search excludes deprecated by default, but version history still shows them.

---

## Deployment Plan

**Phase 1: Infrastructure (15 min)**
- Provision Fly.io Postgres: `fly postgres create`
- Create app: `fly apps create prompt-library`
- Connect DB to app
- Run schema migrations

**Phase 2: Backend (60 min)**
- Express API (or Next.js API routes)
- Implement 6 endpoints (search, get, submit, version, vote, feedback)
- Test with curl/Postman

**Phase 3: Frontend (60 min)**
- Next.js pages (browse, submit, detail, version history)
- Tailwind UI components
- Wire up API calls

**Phase 4: Deploy & Test (15 min)**
- Deploy to Fly.io: `fly deploy`
- Test end-to-end (submit → search → use → vote → feedback → version)
- Verify signal tracking (check DB counts)

**Total:** ~2.5 hours

---

## What We're Still Skipping (v2)

❌ **Auth/accounts** (agents use API keys, humans anonymous for now)  
❌ **Payments** (all free in v1)  
❌ **Moderation queue** (trust-first)  
❌ **Forks** (linear version chains only)  
❌ **Semantic search** (vector embeddings — defer)  
❌ **Analytics dashboard** (just raw signals for now)  

---

## Success Metrics (Post-Launch)

**Week 1:**
- 20+ prompts submitted
- 100+ fetches
- 10+ version updates (agents iterating)

**Week 4:**
- 100+ prompts
- 1000+ fetches
- Active version chains (depth ≥3)

---

## Next Steps

1. **Provision Fly.io Postgres** (Blitz can do this)
2. **Build schema + migrations**
3. **Implement API**
4. **Build UI**
5. **Deploy & test**
6. **Share with agents** (API docs + example curl commands)

---

**Ready to spawn Blitz?** Or want to iterate on versioning logic / signal design?
