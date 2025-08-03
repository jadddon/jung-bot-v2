-- Jung AI Analysis System - Supabase Database Schema (Fixed)
-- Run this in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email TEXT UNIQUE NOT NULL,
    preferred_name TEXT,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    total_sessions INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0
);

-- Create sessions table (using UUID type consistently)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'New Jung Analysis Session',
    is_anonymous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    session_type TEXT DEFAULT 'general',
    context_summary TEXT,
    therapeutic_goals JSONB,
    key_insights JSONB,
    message_count INTEGER DEFAULT 0,
    duration_minutes INTEGER DEFAULT 0
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    sources JSONB,
    analysis_type TEXT,
    therapeutic_techniques JSONB,
    model_used TEXT,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    cost_usd TEXT,
    relevance_score TEXT,
    therapeutic_value TEXT
);

-- Create session_contexts table
CREATE TABLE IF NOT EXISTS session_contexts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id UUID UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    recurring_themes JSONB,
    emotional_patterns JSONB,
    therapeutic_progress JSONB,
    archetypal_patterns JSONB,
    shadow_work_progress JSONB,
    individuation_stage TEXT,
    related_sessions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_created ON sessions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_anonymous_created ON sessions(is_anonymous, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active, last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON sessions(user_id, is_active, last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_cleanup ON sessions(is_anonymous, last_activity) WHERE is_anonymous = true;

CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp ON messages(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_role_timestamp ON messages(role, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_messages_session_recent ON messages(session_id, timestamp DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sessions_updated_at ON sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_contexts_updated_at ON session_contexts;
CREATE TRIGGER update_session_contexts_updated_at
    BEFORE UPDATE ON session_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_contexts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::TEXT = id::TEXT);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::TEXT = id::TEXT);

-- Create RLS policies for sessions
CREATE POLICY "Users can view own sessions and anonymous sessions" ON sessions
    FOR SELECT USING (
        user_id IS NULL OR 
        user_id = auth.uid()
    );

CREATE POLICY "Users can create sessions" ON sessions
    FOR INSERT WITH CHECK (
        user_id IS NULL OR 
        user_id = auth.uid()
    );

CREATE POLICY "Users can update own sessions and anonymous sessions" ON sessions
    FOR UPDATE USING (
        user_id IS NULL OR 
        user_id = auth.uid()
    );

CREATE POLICY "Users can delete own sessions and anonymous sessions" ON sessions
    FOR DELETE USING (
        user_id IS NULL OR 
        user_id = auth.uid()
    );

-- Create RLS policies for messages
CREATE POLICY "Users can view messages from accessible sessions" ON messages
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages in accessible sessions" ON messages
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update messages in accessible sessions" ON messages
    FOR UPDATE USING (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete messages in accessible sessions" ON messages
    FOR DELETE USING (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

-- Create RLS policies for session_contexts
CREATE POLICY "Users can view context for accessible sessions" ON session_contexts
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create context for accessible sessions" ON session_contexts
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update context for accessible sessions" ON session_contexts
    FOR UPDATE USING (
        session_id IN (
            SELECT id FROM sessions 
            WHERE user_id IS NULL OR user_id = auth.uid()
        )
    );

-- Create function to cleanup old anonymous sessions
CREATE OR REPLACE FUNCTION cleanup_old_anonymous_sessions(hours_old INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions 
    WHERE is_anonymous = TRUE 
    AND last_activity < (NOW() - INTERVAL '1 hour' * hours_old);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to update session activity
CREATE OR REPLACE FUNCTION update_session_activity(session_id_param UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE sessions 
    SET last_activity = NOW() 
    WHERE id = session_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to increment message count
CREATE OR REPLACE FUNCTION increment_session_message_count(session_id_param UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE sessions 
    SET message_count = message_count + 1,
        last_activity = NOW()
    WHERE id = session_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get user session context
CREATE OR REPLACE FUNCTION get_user_session_context(
    user_id_param BIGINT,
    current_session_id_param UUID,
    limit_param INTEGER DEFAULT 5
)
RETURNS JSONB AS $$
DECLARE
    context_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'previous_sessions', 
        COALESCE(jsonb_agg(
            jsonb_build_object(
                'id', s.id,
                'title', s.title,
                'type', s.session_type,
                'summary', s.context_summary,
                'created_at', s.created_at
            )
        ), '[]'::jsonb),
        'session_count', COUNT(*)
    )
    INTO context_result
    FROM sessions s
    WHERE s.user_id = user_id_param 
    AND s.id != current_session_id_param
    AND s.is_anonymous = FALSE
    ORDER BY s.last_activity DESC
    LIMIT limit_param;
    
    RETURN COALESCE(context_result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- Create view for session summaries
CREATE OR REPLACE VIEW session_summaries AS
SELECT 
    s.id,
    s.title,
    s.session_type,
    s.created_at,
    s.last_activity,
    s.message_count,
    s.is_anonymous,
    s.user_id,
    CASE 
        WHEN s.message_count > 0 THEN 'active'
        ELSE 'empty'
    END as status
FROM sessions s
ORDER BY s.last_activity DESC;

-- Create view for user statistics
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.id,
    u.email,
    u.preferred_name,
    u.created_at,
    COUNT(DISTINCT s.id) as total_sessions,
    COUNT(DISTINCT m.id) as total_messages,
    MAX(s.last_activity) as last_session_activity,
    AVG(s.message_count) as avg_messages_per_session
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN messages m ON s.id = m.session_id
GROUP BY u.id, u.email, u.preferred_name, u.created_at;

-- Success message
SELECT 'Jung AI Database Schema created successfully with UUID fix!' as message; 