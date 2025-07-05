-- Update the `updated_at` timestamp for the users table
CREATE TRIGGER trg_update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_timestamp();

-- Update the `updated_at` timestamp for the applications table
CREATE TRIGGER trg_update_applications_timestamp
BEFORE UPDATE ON applications
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_timestamp();

-- Update the `updated_at` timestamp for the sessions table
CREATE TRIGGER trg_update_sessions_timestamp
BEFORE UPDATE ON sessions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_timestamp();

-- Update the `updated_at` timestamp for the login_attempts table
CREATE TRIGGER trg_update_login_attempts_timestamp
BEFORE UPDATE ON login_attempts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_timestamp();
