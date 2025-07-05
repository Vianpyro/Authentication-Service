CREATE OR REPLACE FUNCTION delete_application(
    p_app_id UUID,
    p_app_slug TEXT
)
RETURNS TEXT
AS $$
DECLARE
    v_app_name TEXT;
BEGIN
    DELETE FROM applications
    WHERE id = p_app_id AND slug = p_app_slug
    RETURNING app_name INTO v_app_name;

    RETURN v_app_name;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION delete_application TO api;
