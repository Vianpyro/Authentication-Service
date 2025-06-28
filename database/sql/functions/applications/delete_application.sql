CREATE OR REPLACE FUNCTION delete_application(
    p_app_id UUID,
    p_app_slug TEXT
)
RETURNS TEXT
AS $$
DECLARE
    old_app_name TEXT;
BEGIN
    DELETE FROM applications
    WHERE id = p_app_id AND slug = p_app_slug
    RETURNING app_name INTO old_app_name;

    RETURN old_app_name;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON PROCEDURE delete_application TO api;
