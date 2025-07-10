CREATE OR REPLACE FUNCTION get_totp_secret(
    p_token_hash BYTEA
) RETURNS TABLE (
    secret_encrypted NON_EMPTY_TEXT,
    key_version SMALLINT,
    created_at NON_FUTURE_TIMESTAMPTZ,
    confirmed_at NON_FUTURE_TIMESTAMPTZ
) AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Retrieve the user ID associated with the TOTP token
    SELECT user_id INTO v_user_id
    FROM tokens
    WHERE token_hash = p_token_hash AND token_type = 'mfa_challenge';

    -- If no user ID is found, raise an exception
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'TOTP token not found';
    END IF;

    -- Select the TOTP secret details for the user
    RETURN QUERY
    SELECT secret_encrypted, key_version, created_at, confirmed_at
    FROM totp_secrets
    WHERE user_id = v_user_id;
END;
$$ LANGUAGE plpgsql;
