-- Prompt Library Schema

-- Core entity
CREATE TABLE IF NOT EXISTS prompts (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  prompt_text TEXT NOT NULL,
  category VARCHAR(100),
  tags TEXT[],
  submitted_by VARCHAR(255),
  
  -- Versioning
  upstream_id INTEGER REFERENCES prompts(id),
  downstream_id INTEGER REFERENCES prompts(id),
  version_number INTEGER DEFAULT 1,
  version_notes TEXT,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Computed signals
  fetch_count INTEGER DEFAULT 0,
  upvote_count INTEGER DEFAULT 0,
  downvote_count INTEGER DEFAULT 0,
  feedback_count INTEGER DEFAULT 0,
  
  -- Status
  is_deprecated BOOLEAN DEFAULT FALSE,
  is_latest_in_chain BOOLEAN DEFAULT TRUE
);

-- Signals: Fetches
CREATE TABLE IF NOT EXISTS prompt_fetches (
  id SERIAL PRIMARY KEY,
  prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
  fetched_by VARCHAR(255),
  fetched_at TIMESTAMP DEFAULT NOW(),
  source VARCHAR(50)
);

-- Signals: Votes
CREATE TABLE IF NOT EXISTS prompt_votes (
  id SERIAL PRIMARY KEY,
  prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
  voted_by VARCHAR(255) NOT NULL,
  vote_type VARCHAR(10) CHECK (vote_type IN ('upvote', 'downvote')),
  voted_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (prompt_id, voted_by)
);

-- Signals: Feedback
CREATE TABLE IF NOT EXISTS prompt_feedback (
  id SERIAL PRIMARY KEY,
  prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
  feedback_text TEXT NOT NULL,
  submitted_by VARCHAR(255),
  submitted_at TIMESTAMP DEFAULT NOW(),
  rating INTEGER CHECK (rating BETWEEN 1 AND 5)
);

-- Indexes for search
CREATE INDEX IF NOT EXISTS idx_prompts_title ON prompts USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_prompts_prompt_text ON prompts USING gin(to_tsvector('english', prompt_text));
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);

-- Indexes for versioning
CREATE INDEX IF NOT EXISTS idx_prompts_upstream_id ON prompts(upstream_id);
CREATE INDEX IF NOT EXISTS idx_prompts_downstream_id ON prompts(downstream_id);
CREATE INDEX IF NOT EXISTS idx_prompts_latest_in_chain ON prompts(is_latest_in_chain) WHERE is_latest_in_chain = TRUE;

-- Indexes for sorting
CREATE INDEX IF NOT EXISTS idx_prompts_created_at ON prompts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_prompts_upvote_count ON prompts(upvote_count DESC);
CREATE INDEX IF NOT EXISTS idx_prompts_fetch_count ON prompts(fetch_count DESC);

-- Indexes for signals
CREATE INDEX IF NOT EXISTS idx_prompt_fetches_prompt_id ON prompt_fetches(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_fetches_fetched_at ON prompt_fetches(fetched_at);
CREATE INDEX IF NOT EXISTS idx_prompt_votes_prompt_id ON prompt_votes(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_feedback_prompt_id ON prompt_feedback(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_feedback_submitted_at ON prompt_feedback(submitted_at);

-- Triggers to auto-update counts

-- Update vote counts
CREATE OR REPLACE FUNCTION update_prompt_vote_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prompts
  SET 
    upvote_count = (SELECT COUNT(*) FROM prompt_votes WHERE prompt_id = COALESCE(NEW.prompt_id, OLD.prompt_id) AND vote_type = 'upvote'),
    downvote_count = (SELECT COUNT(*) FROM prompt_votes WHERE prompt_id = COALESCE(NEW.prompt_id, OLD.prompt_id) AND vote_type = 'downvote')
  WHERE id = COALESCE(NEW.prompt_id, OLD.prompt_id);
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_vote_count ON prompt_votes;
CREATE TRIGGER trigger_update_vote_count
AFTER INSERT OR UPDATE OR DELETE ON prompt_votes
FOR EACH ROW EXECUTE FUNCTION update_prompt_vote_count();

-- Update fetch count
CREATE OR REPLACE FUNCTION update_prompt_fetch_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prompts
  SET fetch_count = (SELECT COUNT(*) FROM prompt_fetches WHERE prompt_id = NEW.prompt_id)
  WHERE id = NEW.prompt_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_fetch_count ON prompt_fetches;
CREATE TRIGGER trigger_update_fetch_count
AFTER INSERT ON prompt_fetches
FOR EACH ROW EXECUTE FUNCTION update_prompt_fetch_count();

-- Update feedback count
CREATE OR REPLACE FUNCTION update_prompt_feedback_count()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE prompts
  SET feedback_count = (SELECT COUNT(*) FROM prompt_feedback WHERE prompt_id = COALESCE(NEW.prompt_id, OLD.prompt_id))
  WHERE id = COALESCE(NEW.prompt_id, OLD.prompt_id);
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_feedback_count ON prompt_feedback;
CREATE TRIGGER trigger_update_feedback_count
AFTER INSERT OR DELETE ON prompt_feedback
FOR EACH ROW EXECUTE FUNCTION update_prompt_feedback_count();
