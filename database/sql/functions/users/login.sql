CREATE OR REPLACE FUNCTION login_user(
    p_app_id UUID,
    p_email_hash TEXT,
    p_ip_address INET,
    p_user_agent TEXT
)
RETURNS TABLE (
    user_id UUID,
    password_hash ARGON2ID_HASH,
    is_email_verified BOOLEAN,
    is_2fa_enabled BOOLEAN,
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
)
AS $$
DECLARE
    v_user users%ROWTYPE;
BEGIN
    -- Look up the user by email hash
    SELECT *
    INTO v_user
    FROM users
    WHERE email_hash = p_email_hash
    AND app_id = p_app_id;

    -- If no user found, raise an error
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User not found with email hash: %', p_email_hash;
    END IF;

    -- Check if the user is suspended
    IF v_user.is_suspended THEN
        RAISE EXCEPTION 'User is suspended';
    END IF;

    -- Return user details
    RETURN QUERY SELECT
        v_user.id,
        v_user.password_hash,
        v_user.is_email_verified,
        v_user.is_2fa_enabled,
        v_user.is_suspended
    FROM users
    WHERE id = v_user.id
    AND app_id = p_app_id;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION delete_application TO api;
