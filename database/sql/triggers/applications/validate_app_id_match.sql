-- Trigger to validate application id on sessions
CREATE TRIGGER trg_sessions_app_check
BEFORE INSERT OR UPDATE ON sessions
FOR EACH ROW
EXECUTE FUNCTION validate_app_id_match();
