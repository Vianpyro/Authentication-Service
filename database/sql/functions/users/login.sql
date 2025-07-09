CREATE OR REPLACE FUNCTION login_user(
    p_app_id UUID,
    p_email_hash TEXT,
    p_ip_address INET,
    p_user_agent TEXT
)
RETURNS TABLE (
    id UUID,
    password_hash ARGON2ID_HASH,
    is_email_verified BOOLEAN,
    is_2fa_enabled BOOLEAN
) AS $$
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
        RAISE EXCEPTION 'User not found with specified email';
    END IF;

    -- Check if the user is suspended
    IF v_user.is_suspended THEN
        RAISE EXCEPTION 'User is suspended';
    END IF;

    -- Return user details using the variable data
    RETURN QUERY SELECT
        v_user.id,
        v_user.password_hash,
        v_user.is_email_verified,
        v_user.is_2fa_enabled;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION login_user TO api;
