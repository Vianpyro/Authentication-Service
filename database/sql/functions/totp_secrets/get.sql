CREATE OR REPLACE FUNCTION get_totp_secret(
    p_user_id UUID
) RETURNS TABLE (
    secret_encrypted NON_EMPTY_TEXT,
    key_version SMALLINT,
    created_at NON_FUTURE_TIMESTAMPTZ,
    confirmed_at NON_FUTURE_TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT secret_encrypted, key_version, created_at, confirmed_at
    FROM totp_secrets
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;
