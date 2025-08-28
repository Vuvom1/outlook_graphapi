-- Initialize the Outlook API database
-- This script runs when the PostgreSQL container starts for the first time

-- Create the database if it doesn't exist
SELECT 'CREATE DATABASE outlook_api'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'outlook_api');

-- Grant all privileges to the postgres user
GRANT ALL PRIVILEGES ON DATABASE outlook_api TO postgres;

-- Connect to the database
\c outlook_api;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log initialization
\echo 'Outlook API database initialized successfully!';
