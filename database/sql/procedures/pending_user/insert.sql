CREATE OR REPLACE PROCEDURE register_pending_user(
    p_app_id UUID,
    p_email_encrypted NON_EMPTY_TEXT,
    p_email_hash SHA_256_HASH,
    p_token URLSAFE_TOKEN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_token_id INTEGER;
BEGIN
    -- First insert the token and capture the generated ID
    INSERT INTO tokens (token_type, app_id)
    VALUES ('email_verification', p_app_id)
    RETURNING id INTO v_token_id;

    -- Then insert the pending user with the token ID reference
    INSERT INTO pending_users (token_id, app_id, email_encrypted, email_hash)
    VALUES (v_token_id, p_app_id, p_email_encrypted, p_email_hash);
END;
$$;
