CREATE TRIGGER trigger_check_token_type_pending_users
BEFORE INSERT OR UPDATE ON pending_users
FOR EACH ROW
EXECUTE FUNCTION check_token_type_for_pending_users();
