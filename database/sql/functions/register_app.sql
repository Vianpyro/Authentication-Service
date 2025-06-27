CREATE OR REPLACE FUNCTION register_app(
    slug TEXT,
    app_name TEXT
)
RETURNS UUID
AS $$
DECLARE
    new_app_id UUID;
BEGIN
    INSERT INTO apps (slug, app_name)
    VALUES (slug, app_name)
    RETURNING id INTO new_app_id;

    RETURN new_app_id;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON PROCEDURE register_app TO api;
