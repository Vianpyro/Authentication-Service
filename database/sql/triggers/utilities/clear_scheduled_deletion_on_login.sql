-- Trigger to clear scheduled deletion on user login
CREATE TRIGGER trg_clear_scheduled_deletion_on_login
BEFORE UPDATE ON users
FOR EACH ROW
WHEN (old.scheduled_for_deletion_at IS NOT NULL)
EXECUTE FUNCTION clear_scheduled_deletion_on_login();
