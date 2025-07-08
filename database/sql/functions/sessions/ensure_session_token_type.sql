CREATE OR REPLACE FUNCTION ensure_session_token_type()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM tokens
        WHERE id = NEW.token_id AND token_type IN ('session', 'mfa_challenge')
    ) THEN
        RAISE EXCEPTION 'Token ID % is not a session token.', NEW.token_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
