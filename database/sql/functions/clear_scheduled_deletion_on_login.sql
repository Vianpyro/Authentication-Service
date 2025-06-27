-- Function to clear scheduled deletion on user login
CREATE OR REPLACE FUNCTION clear_scheduled_deletion_on_login()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.last_login_at IS DISTINCT FROM OLD.last_login_at
       AND NEW.last_login_at IS NOT NULL THEN
        NEW.scheduled_for_deletion_at := NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
