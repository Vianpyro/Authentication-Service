CREATE OR REPLACE FUNCTION get_email_verification_status(
    p_user_id UUID,
    p_app_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_is_email_verified BOOLEAN;
BEGIN
    SELECT u.is_email_verified
    INTO v_is_email_verified
    FROM users u
    WHERE u.id = p_user_id
      AND u.app_id = p_app_id;

    RETURN v_is_email_verified;
END;
$$ LANGUAGE plpgsql;
