CREATE OR REPLACE FUNCTION get_totp_secret(
    p_token_hash BYTEA
) RETURNS TABLE (
    user_id UUID,
    secret_encrypted NON_EMPTY_TEXT,
    key_version SMALLINT,
    created_at NON_FUTURE_TIMESTAMPTZ,
    confirmed_at NON_FUTURE_TIMESTAMPTZ
) AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Retrieve the user ID associated with the TOTP token
    SELECT t.user_id INTO v_user_id
    FROM tokens t
    WHERE t.token_hash = p_token_hash AND t.token_type = 'mfa_challenge';

    -- If no user ID is found, raise an exception
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'TOTP token not found';
    END IF;

    -- Select the TOTP secret details for the user and user_id
    RETURN QUERY
    SELECT v_user_id, ts.secret_encrypted, ts.key_version, ts.created_at, ts.confirmed_at
    FROM totp_secrets ts
    WHERE ts.user_id = v_user_id;
END;
$$ LANGUAGE plpgsql;
