CREATE OR REPLACE FUNCTION register_application(
    p_app_name TEXT,
    p_app_slug TEXT
)
RETURNS UUID
AS $$
DECLARE
    v_app_id UUID;
BEGIN
    INSERT INTO applications (slug, app_name)
    VALUES (p_app_slug, p_app_name)
    RETURNING id INTO v_app_id;

    RETURN v_app_id;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON PROCEDURE register_application TO api;
