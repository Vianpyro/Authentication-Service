CREATE OR REPLACE FUNCTION get_application(
    p_app_id UUID
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    slug TEXT,
    description TEXT,
    is_active BOOLEAN,
    created_at NON_FUTURE_TIMESTAMPTZ,
    updated_at NON_FUTURE_TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.name,
        a.slug,
        a.description,
        a.is_active,
        a.created_at,
        a.updated_at
    FROM applications a
    WHERE a.id = p_app_id;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION get_application TO api;
