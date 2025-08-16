-- Database initialization script for ZZP Scanner
-- This script is executed when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'Europe/Amsterdam';

-- Create indexes for better performance
-- (These will be created by SQLAlchemy models, but we can add some additional ones)

-- Full text search index for business names
CREATE INDEX IF NOT EXISTS idx_businesses_name_fts 
ON businesses USING gin(to_tsvector('dutch', name));

-- Trigram index for fuzzy matching
CREATE INDEX IF NOT EXISTS idx_businesses_name_trgm 
ON businesses USING gin(name gin_trgm_ops);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_businesses_location_website 
ON businesses(city, country, website_exists) 
WHERE website_exists = false;

-- Index for recent activity queries
CREATE INDEX IF NOT EXISTS idx_businesses_created_at 
ON businesses(created_at DESC);

-- Index for website checks
CREATE INDEX IF NOT EXISTS idx_website_checks_business_created 
ON website_checks(business_id, created_at DESC);

-- Index for crawl jobs
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status_created 
ON crawl_jobs(status, created_at DESC);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scanner;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scanner;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO scanner;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
-- (These will be created by SQLAlchemy models, but we can add them here as well)

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'ZZP Scanner database initialized successfully';
END $$; 