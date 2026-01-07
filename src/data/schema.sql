-- Database Schema for Social Media Generator
-- PostgreSQL Database Schema

-- Main posts table
CREATE TABLE IF NOT EXISTS generated_posts (
    id SERIAL PRIMARY KEY,
    user_prompt TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    generated_content TEXT NOT NULL,
    final_content TEXT, -- After human edits
    image_url TEXT,
    image_prompt TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- Status: draft, approved, published, rejected, scheduled, review_needed, needs_regeneration
    human_edits TEXT, -- JSON of what changed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    scheduled_for TIMESTAMP,
    jira_issue_key VARCHAR(50) -- Link to Jira task
);

-- Feedback on posts
CREATE TABLE IF NOT EXISTS post_feedback (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL,
    -- Types: approved_as_is, approved_with_edits, rejected, regenerated
    edit_details JSONB, -- What was changed
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) -- User who gave feedback
);

-- Performance metrics from platforms
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate FLOAT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality check results
CREATE TABLE IF NOT EXISTS quality_checks (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    check_type VARCHAR(50) NOT NULL,
    -- Types: appropriateness, brand_alignment, grammar, engagement_potential, platform_fit, image_appropriate
    passed BOOLEAN,
    score FLOAT, -- 0.0 to 1.0
    details JSONB,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Publishing log
CREATE TABLE IF NOT EXISTS publishing_log (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES generated_posts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255), -- ID from platform API
    status VARCHAR(50) NOT NULL, -- success, failed, retrying
    error_message TEXT,
    attempts INTEGER DEFAULT 1,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_posts_platform ON generated_posts(platform);
CREATE INDEX IF NOT EXISTS idx_posts_status ON generated_posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_created ON generated_posts(created_at);
CREATE INDEX IF NOT EXISTS idx_posts_published ON generated_posts(published_at);
CREATE INDEX IF NOT EXISTS idx_posts_jira ON generated_posts(jira_issue_key);
CREATE INDEX IF NOT EXISTS idx_metrics_post ON performance_metrics(post_id);
CREATE INDEX IF NOT EXISTS idx_feedback_post ON post_feedback(post_id);

-- Add update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_generated_posts_updated_at BEFORE UPDATE
    ON generated_posts FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
