-- Initialize Exam Proctor Database
CREATE DATABASE exam_proctor;
\c exam_proctor;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'STUDENT')),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Exams table
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
    end_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_min INTEGER NOT NULL,
    settings_json JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Exam assignments table
CREATE TABLE exam_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'ASSIGNED' CHECK (status IN ('ASSIGNED', 'STARTED', 'SUBMITTED', 'REVIEWED')),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    submitted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(exam_id, student_id)
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    device_info_json JSONB NOT NULL DEFAULT '{}',
    final_risk_score INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Proctor events table
CREATE TABLE proctor_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    ts TIMESTAMP WITH TIME ZONE NOT NULL,
    type VARCHAR(100) NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}',
    risk_delta INTEGER NOT NULL DEFAULT 0,
    snapshot_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Risk ticks table (sampled risk scores)
CREATE TABLE risk_ticks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    ts TIMESTAMP WITH TIME ZONE NOT NULL,
    risk_score INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('MCQ', 'TEXT')),
    prompt TEXT NOT NULL,
    options_json JSONB,
    answer_key TEXT,
    points INTEGER DEFAULT 1,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Answers table
CREATE TABLE answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    payload_json JSONB NOT NULL DEFAULT '{}',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    scope VARCHAR(100) NOT NULL DEFAULT 'read',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_exam_assignments_exam_id ON exam_assignments(exam_id);
CREATE INDEX idx_exam_assignments_student_id ON exam_assignments(student_id);
CREATE INDEX idx_exam_assignments_status ON exam_assignments(status);
CREATE INDEX idx_sessions_exam_id ON sessions(exam_id);
CREATE INDEX idx_sessions_student_id ON sessions(student_id);
CREATE INDEX idx_sessions_started_at ON sessions(started_at);
CREATE INDEX idx_proctor_events_session_id ON proctor_events(session_id);
CREATE INDEX idx_proctor_events_ts ON proctor_events(ts);
CREATE INDEX idx_proctor_events_type ON proctor_events(type);
CREATE INDEX idx_risk_ticks_session_id ON risk_ticks(session_id);
CREATE INDEX idx_risk_ticks_ts ON risk_ticks(ts);
CREATE INDEX idx_questions_exam_id ON questions(exam_id);
CREATE INDEX idx_answers_session_id ON answers(session_id);
CREATE INDEX idx_answers_question_id ON answers(question_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exams_updated_at BEFORE UPDATE ON exams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users (id, role, name, email, password_hash) VALUES (
    uuid_generate_v4(),
    'ADMIN',
    'System Administrator',
    'admin@examproctor.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.Ge'
);

-- Insert sample exam
INSERT INTO exams (id, title, description, start_at, end_at, duration_min, settings_json) VALUES (
    uuid_generate_v4(),
    'Sample Mathematics Test',
    'A comprehensive test covering algebra, calculus, and statistics',
    CURRENT_TIMESTAMP + INTERVAL '1 day',
    CURRENT_TIMESTAMP + INTERVAL '2 days',
    120,
    '{"camera_required": true, "mic_required": true, "allowed_devices": ["desktop", "mobile"], "max_attempts": 2}'
);

-- Create function to get exam statistics
CREATE OR REPLACE FUNCTION get_exam_stats(exam_uuid UUID)
RETURNS TABLE (
    total_students BIGINT,
    started_sessions BIGINT,
    completed_sessions BIGINT,
    avg_risk_score NUMERIC,
    max_risk_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT ea.student_id)::BIGINT as total_students,
        COUNT(DISTINCT CASE WHEN ea.status IN ('STARTED', 'SUBMITTED', 'REVIEWED') THEN ea.student_id END)::BIGINT as started_sessions,
        COUNT(DISTINCT CASE WHEN ea.status IN ('SUBMITTED', 'REVIEWED') THEN ea.student_id END)::BIGINT as completed_sessions,
        AVG(s.final_risk_score)::NUMERIC as avg_risk_score,
        MAX(s.final_risk_score)::INTEGER as max_risk_score
    FROM exam_assignments ea
    LEFT JOIN sessions s ON ea.exam_id = s.exam_id AND ea.student_id = s.student_id
    WHERE ea.exam_id = exam_uuid;
END;
$$ LANGUAGE plpgsql;

-- Create function to get session timeline
CREATE OR REPLACE FUNCTION get_session_timeline(session_uuid UUID)
RETURNS TABLE (
    event_type VARCHAR(100),
    event_count BIGINT,
    total_risk_delta INTEGER,
    first_occurrence TIMESTAMP WITH TIME ZONE,
    last_occurrence TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pe.type as event_type,
        COUNT(*)::BIGINT as event_count,
        SUM(pe.risk_delta)::INTEGER as total_risk_delta,
        MIN(pe.ts) as first_occurrence,
        MAX(pe.ts) as last_occurrence
    FROM proctor_events pe
    WHERE pe.session_id = session_uuid
    GROUP BY pe.type
    ORDER BY event_count DESC;
END;
$$ LANGUAGE plpgsql;
