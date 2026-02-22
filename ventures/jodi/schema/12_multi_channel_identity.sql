-- Multi-Channel Identity & State Management
-- Enables cross-channel user linking (Telegram, WhatsApp, Web)
-- Single source of truth for user state across all channels

-- ============================================
-- 1. Add phone to users table (universal identifier)
-- ============================================

ALTER TABLE users
ADD COLUMN IF NOT EXISTS phone VARCHAR(20) UNIQUE,
ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS preferred_channel VARCHAR(20) DEFAULT 'telegram',
ADD COLUMN IF NOT EXISTS last_channel VARCHAR(20),
ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Index for fast phone lookup
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- 2. User Channels (identity mapping)
-- ============================================

CREATE TABLE IF NOT EXISTS user_channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_type VARCHAR(20) NOT NULL CHECK (channel_type IN ('telegram', 'whatsapp', 'web', 'email')),
    channel_identifier VARCHAR(255) NOT NULL, -- telegram_id, whatsapp_phone, session_token, email
    is_primary BOOLEAN DEFAULT FALSE,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Prevent duplicate channel identifiers
    UNIQUE(channel_type, channel_identifier)
);

-- Indexes for fast channel → user_id lookup
CREATE INDEX idx_user_channels_user_id ON user_channels(user_id);
CREATE INDEX idx_user_channels_channel_lookup ON user_channels(channel_type, channel_identifier);
CREATE INDEX idx_user_channels_last_used ON user_channels(last_used DESC);

-- ============================================
-- 3. Sessions (ephemeral state per channel)
-- ============================================

CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_type VARCHAR(20) NOT NULL,
    channel_identifier VARCHAR(255) NOT NULL,
    current_question INT DEFAULT 1,
    current_section VARCHAR(50),
    answers JSONB DEFAULT '{}',
    asked_questions INT[] DEFAULT ARRAY[]::INT[], -- Loop detection
    skip_questions INT[] DEFAULT ARRAY[]::INT[],
    multi_select_buffer JSONB DEFAULT '{}',
    photo_urls TEXT[] DEFAULT ARRAY[]::TEXT[],
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '7 days',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for session lookup
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_channel ON sessions(channel_type, channel_identifier);
CREATE INDEX idx_sessions_last_active ON sessions(last_active DESC);
CREATE INDEX idx_sessions_expires ON sessions(expires_at) WHERE expires_at > NOW();

-- Auto-cleanup expired sessions (run daily)
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4. Conversation Logs (audit trail)
-- ============================================

-- Already exists, just add channel tracking
ALTER TABLE conversation_logs
ADD COLUMN IF NOT EXISTS channel_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS channel_identifier VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_conversation_logs_channel 
ON conversation_logs(channel_type, channel_identifier);

-- ============================================
-- 5. Helper Functions
-- ============================================

-- Get or create user by phone
CREATE OR REPLACE FUNCTION get_or_create_user_by_phone(
    p_phone VARCHAR(20),
    p_channel_type VARCHAR(20),
    p_channel_identifier VARCHAR(255)
)
RETURNS UUID AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Try to find existing user by phone
    SELECT id INTO v_user_id FROM users WHERE phone = p_phone;
    
    IF v_user_id IS NULL THEN
        -- Create new user
        INSERT INTO users (phone, preferred_channel, last_channel)
        VALUES (p_phone, p_channel_type, p_channel_type)
        RETURNING id INTO v_user_id;
    END IF;
    
    -- Link channel to user (upsert)
    INSERT INTO user_channels (user_id, channel_type, channel_identifier, last_used)
    VALUES (v_user_id, p_channel_type, p_channel_identifier, NOW())
    ON CONFLICT (channel_type, channel_identifier)
    DO UPDATE SET last_used = NOW();
    
    -- Update user's last channel
    UPDATE users 
    SET last_channel = p_channel_type, last_active_at = NOW()
    WHERE id = v_user_id;
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

-- Link existing channel to user
CREATE OR REPLACE FUNCTION link_channel_to_user(
    p_user_id UUID,
    p_channel_type VARCHAR(20),
    p_channel_identifier VARCHAR(255)
)
RETURNS void AS $$
BEGIN
    INSERT INTO user_channels (user_id, channel_type, channel_identifier, last_used)
    VALUES (p_user_id, p_channel_type, p_channel_identifier, NOW())
    ON CONFLICT (channel_type, channel_identifier)
    DO UPDATE SET user_id = p_user_id, last_used = NOW();
    
    UPDATE users 
    SET last_channel = p_channel_type, last_active_at = NOW()
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Get user_id from any channel identifier
CREATE OR REPLACE FUNCTION get_user_id_from_channel(
    p_channel_type VARCHAR(20),
    p_channel_identifier VARCHAR(255)
)
RETURNS UUID AS $$
DECLARE
    v_user_id UUID;
BEGIN
    SELECT user_id INTO v_user_id
    FROM user_channels
    WHERE channel_type = p_channel_type
    AND channel_identifier = p_channel_identifier;
    
    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6. Migration for existing Telegram users
-- ============================================

-- Migrate existing telegram_id to user_channels table
INSERT INTO user_channels (user_id, channel_type, channel_identifier, is_primary, created_at)
SELECT id, 'telegram', telegram_id::TEXT, TRUE, created_at
FROM users
WHERE telegram_id IS NOT NULL
ON CONFLICT (channel_type, channel_identifier) DO NOTHING;

-- Add comments
COMMENT ON TABLE user_channels IS 'Maps channel identifiers (telegram_id, whatsapp_phone, etc.) to unified user_id';
COMMENT ON TABLE sessions IS 'Ephemeral session state per channel. Syncs to users table periodically.';
COMMENT ON FUNCTION get_or_create_user_by_phone IS 'Creates user if not exists, links channel, returns user_id';
