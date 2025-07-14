CREATE OR REPLACE FUNCTION register_pending_user(
    p_app_id UUID,
    p_token_hash BYTEA,
    p_email_encrypted NON_EMPTY_TEXT,
    p_email_hash SHA_256_HASH,
    p_ip_address INET,
    p_user_agent TEXT
) RETURNS TIMESTAMPTZ
LANGUAGE plpgsql AS $$
DECLARE
    v_token_id INTEGER;
    v_expires_at TIMESTAMPTZ;
BEGIN
    -- Insert the token and capture the generated ID and expiration time
    INSERT INTO tokens (token_hash, token_type, app_id)
    VALUES (p_token_hash, 'email_verification', p_app_id)
    RETURNING id, expires_at INTO v_token_id, v_expires_at;

    -- Insert the pending user with the token ID reference
    INSERT INTO pending_users (token_id, app_id, email_encrypted, email_hash, ip_address, user_agent)
    VALUES (v_token_id, p_app_id, p_email_encrypted, p_email_hash, p_ip_address, p_user_agent);

    -- Return the expiration time of the token
    RETURN v_expires_at;
END;
$$;

GRANT EXECUTE ON FUNCTION register_pending_user TO api;
