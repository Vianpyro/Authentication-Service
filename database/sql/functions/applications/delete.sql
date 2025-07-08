CREATE OR REPLACE FUNCTION delete_application(
    p_app_id UUID,
    p_slug TEXT
)
RETURNS TEXT
AS $$
DECLARE
    v_name TEXT;
BEGIN
    DELETE FROM applications
    WHERE id = p_app_id AND slug = p_slug
    RETURNING name INTO v_name;

    RETURN v_name;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION delete_application TO api;
