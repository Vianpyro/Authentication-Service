CREATE OR REPLACE FUNCTION register_application(
    p_name TEXT,
    p_slug TEXT,
    p_description TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_app_id UUID;
BEGIN
    INSERT INTO applications (slug, name, description)
    VALUES (p_slug, p_name, p_description)
    RETURNING id INTO v_app_id;

    RETURN v_app_id;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION register_application TO api;
