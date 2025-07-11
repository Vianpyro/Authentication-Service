CREATE OR REPLACE FUNCTION get_access_token(
    p_token_hash BYTEA
)
RETURNS TABLE (
    user_id UUID,
    app_id UUID,
    expires_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT t.user_id, t.app_id, t.expires_at
    FROM tokens t
    WHERE t.token_type = 'session'
      AND t.session_type = 'access'
      AND t.expires_at > current_timestamp
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;
