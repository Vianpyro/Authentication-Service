CREATE OR REPLACE FUNCTION confirm_pending_user(
    p_app_id UUID,
    p_token URLSAFE_TOKEN,
    p_password ARGON2ID_HASH,
    p_ip_address INET,
    p_user_agent TEXT
)
RETURNS UUID
AS $$
DECLARE
    v_pending_user pending_users%ROWTYPE;
    v_token tokens%ROWTYPE;
    v_user_id UUID;
    v_existing_user_id UUID;
BEGIN
    -- Look up the token first
    SELECT *
    INTO v_token
    FROM tokens
    WHERE token = p_token
    AND token_type = 'email_verification'
    AND app_id = p_app_id;

    -- If no token found, raise an error
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid verification token';
    END IF;

    -- Check if the token is expired
    IF v_token.expires_at < current_timestamp THEN
        RAISE EXCEPTION 'Token has expired';
    END IF;

    -- Look up the pending user by token_id
    SELECT *
    INTO v_pending_user
    FROM pending_users
    WHERE token_id = v_token.id AND app_id = p_app_id;

    -- If no pending user found, raise an error
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pending user not found';
    END IF;

    -- Check if the pending user record is expired
    IF v_pending_user.expires_at < current_timestamp THEN
        RAISE EXCEPTION 'Registration has expired';
    END IF;

    -- Check if user already exists
    SELECT id INTO v_existing_user_id
    FROM users
    WHERE email_hash = v_pending_user.email_hash AND app_id = p_app_id;

    IF FOUND THEN
        -- User already exists, clean up pending registration and return existing user ID
        DELETE FROM pending_users WHERE id = v_pending_user.id;
        RAISE EXCEPTION 'User already exists';
    END IF;

    -- Create the new user
    INSERT INTO users (app_id, email_encrypted, email_hash, password_hash)
    VALUES (v_pending_user.app_id, v_pending_user.email_encrypted, v_pending_user.email_hash, p_password)
    RETURNING id INTO v_user_id;

    -- If user creation is successful, delete the pending user (this will cascade delete the token)
    DELETE FROM pending_users WHERE id = v_pending_user.id;

    -- Return the new user ID
    RETURN v_user_id;
END;
$$
LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION delete_application TO api;
