CREATE TRIGGER trg_check_session_token
BEFORE INSERT OR UPDATE ON sessions
FOR EACH ROW
EXECUTE FUNCTION ensure_session_token_type();
