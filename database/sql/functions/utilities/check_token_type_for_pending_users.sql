CREATE OR REPLACE FUNCTION check_token_type_for_pending_users()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT token_type FROM tokens WHERE id = NEW.token_id) != 'email_verification' THEN
        RAISE EXCEPTION 'Token must be of type email_verification for pending users';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
