-- Create the main application database
CREATE DATABASE xero_db;

-- Create the test database
CREATE DATABASE test_xero_db;

-- Connect to test database and load test data
\c test_xero_db;

-- Load the test data
\i /docker-entrypoint-initdb.d/reset_db.sql
