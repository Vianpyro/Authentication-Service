-- Delete roles if they exist
DROP ROLE IF EXISTS api;
DROP ROLE IF EXISTS automation;
DROP ROLE IF EXISTS cron;

-- Create roles
CREATE ROLE api NOLOGIN;
CREATE ROLE automation NOLOGIN;
CREATE ROLE cron NOLOGIN;
