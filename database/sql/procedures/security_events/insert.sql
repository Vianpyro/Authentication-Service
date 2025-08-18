CREATE OR REPLACE PROCEDURE insert_security_event(
    p_app_id UUID,
    p_user_id UUID,
    p_event_type VARCHAR,
    p_metadata JSONB
)
AS $$
BEGIN
    INSERT INTO security_events (app_id, user_id, event_type, metadata)
    VALUES (p_app_id, p_user_id, p_event_type, p_metadata);
END;
$$ LANGUAGE plpgsql;
