CREATE OR REPLACE FUNCTION get_application_name(
    p_app_id UUID
)
RETURNS TEXT
AS $$
DECLARE
    v_app_name TEXT;
BEGIN
    SELECT app_name INTO v_app_name
    FROM applications
    WHERE id = p_app_id;

    RETURN v_app_name;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON PROCEDURE get_application_name TO api;
