CREATE OR REPLACE PROCEDURE create_pending_user(
    app_id UUID,
    token URLSAFE_TOKEN,
    email_encrypted NON_EMPTY_TEXT,
    email_hash SHA_256_HASH,
    ip_address INET,
    user_agent USER_AGENT_STR
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pending_users (app_id, token, email_encrypted, email_hash, created_at, expires_at, ip_address, user_agent)
    VALUES (app_id, token, email_encrypted, email_hash, current_timestamp, current_timestamp + INTERVAL '24 hours', ip_address, user_agent);
END;
$$;

GRANT EXECUTE ON PROCEDURE create_pending_user TO api;
