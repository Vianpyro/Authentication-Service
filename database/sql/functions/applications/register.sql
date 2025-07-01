CREATE OR REPLACE FUNCTION register_application(
    p_app_name TEXT,
    p_app_slug TEXT,
    p_app_description TEXT DEFAULT NULL
)
RETURNS UUID
AS $$
DECLARE
    v_app_id UUID;
BEGIN
    INSERT INTO applications (slug, app_name, app_description)
    VALUES (p_app_slug, p_app_name, p_app_description)
    RETURNING id INTO v_app_id;

    RETURN v_app_id;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON PROCEDURE register_application TO api;
