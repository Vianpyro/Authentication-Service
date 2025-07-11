CREATE OR REPLACE PROCEDURE confirm_totp_secret(
    p_totp_secret_id UUID
)
AS $$
BEGIN
    UPDATE totp_secrets
    SET confirmed_at = current_timestamp
    WHERE id = p_totp_secret_id;
END;
$$ LANGUAGE plpgsql;
