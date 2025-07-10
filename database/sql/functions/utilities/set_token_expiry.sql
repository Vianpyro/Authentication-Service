CREATE FUNCTION set_token_expiry()
RETURNS trigger AS $$
BEGIN
    IF NEW.expires_at IS NULL THEN
        IF NEW.token_type = 'email_verification' OR NEW.token_type = 'recovery_email_verification' THEN
            NEW.expires_at := current_timestamp + INTERVAL '24 hours';
        ELSIF NEW.token_type = 'mfa_challenge' THEN
            NEW.expires_at := current_timestamp + INTERVAL '5 minutes';
        ELSIF NEW.token_type = 'password_reset' THEN
            NEW.expires_at := current_timestamp + INTERVAL '1 hour';
        ELSIF NEW.token_type = 'session' THEN
            IF NEW.session_type = 'access' THEN
                NEW.expires_at := current_timestamp + INTERVAL '1 hour';
            ELSIF NEW.session_type = 'refresh' THEN
                NEW.expires_at := current_timestamp + INTERVAL '30 days';
            END IF;
        ELSE
            RAISE EXCEPTION 'Token type % does not have a default expiry', NEW.token_type;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
