CREATE OR REPLACE FUNCTION update_application(
    p_app_id UUID,
    p_new_name TEXT,
    p_new_slug TEXT,
    p_new_description TEXT,
    p_new_status BOOLEAN
)
RETURNS TABLE (
    name TEXT,
    slug TEXT,
    description TEXT,
    is_active BOOLEAN,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    UPDATE applications a
    SET
        name = COALESCE(p_new_name, a.name),
        slug = COALESCE(p_new_slug, a.slug),
        description = COALESCE(p_new_description, a.description),
        is_active = p_new_status,
        updated_at = current_timestamp
    WHERE a.id = p_app_id
    RETURNING a.name, a.slug, a.description, a.is_active, a.updated_at::TIMESTAMPTZ;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION update_application TO api;
