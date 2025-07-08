CREATE OR REPLACE PROCEDURE create_session(
    p_app_id UUID,
    p_user_id UUID,
    p_access_token_hash BYTEA,
    p_refresh_token_hash BYTEA,
    -- p_device_fingerprint_hash TEXT,
    -- p_device_name TEXT,
    p_ip_address INET,
    p_user_agent TEXT
)
AS $$
DECLARE
    v_access_token_id INTEGER;
    v_refresh_token_id INTEGER;
    v_device_fingerprint_id UUID;
BEGIN
    -- Insert the access token
    INSERT INTO tokens (token_hash, token_type, session_type, user_id, app_id)
    VALUES (
        p_access_token_hash,
        'session',
        'access',
        p_user_id,
        p_app_id
    )
    RETURNING id INTO v_access_token_id;

    -- Insert the refresh token
    INSERT INTO tokens (token_hash, token_type, session_type, user_id, app_id)
    VALUES (
        p_refresh_token_hash,
        'session',
        'refresh',
        p_user_id,
        p_app_id
    )
    RETURNING id INTO v_refresh_token_id;

    -- Handle device fingerprint
    -- INSERT INTO device_fingerprints (user_id, app_id, fingerprint_hash, name, user_agent, last_seen_at)
    -- VALUES (p_user_id, p_app_id, p_device_fingerprint_hash, p_device_name, p_user_agent, current_timestamp)
    -- ON CONFLICT (user_id, fingerprint_hash) DO UPDATE
    -- SET
    --     user_agent = EXCLUDED.user_agent,
    --     last_seen_at = current_timestamp
    -- RETURNING id INTO v_device_fingerprint_id;

    -- Insert the session record
    INSERT INTO sessions (app_id, user_id, token_id, device_fingerprint, ip_address, user_agent)
    VALUES (p_app_id, p_user_id, v_access_token_id, v_device_fingerprint_id, p_ip_address, p_user_agent);
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON PROCEDURE create_session TO api;
