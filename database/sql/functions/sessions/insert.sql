CREATE OR REPLACE FUNCTION create_session(
    p_app_id UUID,
    p_user_id UUID,
    p_session_token TEXT,
    p_refresh_token TEXT
)
RETURNS VOID
AS $$
BEGIN
    INSERT INTO sessions (user_id, session_token, refresh_token)
    VALUES (p_user_id, p_session_token, p_refresh_token);
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION create_session TO api;
