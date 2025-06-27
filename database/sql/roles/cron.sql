-- Grant privileges to cron role
GRANT SELECT, UPDATE, DELETE ON users TO cron;
GRANT SELECT, DELETE ON pending_users TO cron;
GRANT SELECT, DELETE ON sessions TO cron;
GRANT SELECT, DELETE ON password_reset_tokens TO cron;
GRANT SELECT, DELETE ON totp_secrets TO cron;
GRANT SELECT, DELETE ON device_fingerprints TO cron;
GRANT INSERT ON security_events TO cron;
GRANT USAGE ON SCHEMA public TO cron;
