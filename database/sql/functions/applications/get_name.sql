CREATE OR REPLACE FUNCTION get_application_name(
    p_app_id UUID
)
RETURNS TEXT AS $$
DECLARE
    v_name TEXT;
BEGIN
    SELECT name INTO v_name
    FROM applications
    WHERE id = p_app_id;

    RETURN v_name;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION get_application_name TO api;
