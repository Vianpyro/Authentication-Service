CREATE OR REPLACE FUNCTION update_application(
    p_id UUID,
    p_new_name TEXT,
    p_new_slug TEXT,
    p_new_description TEXT,
    p_new_status BOOLEAN
)
RETURNS TABLE (
    app_name TEXT,
    slug TEXT,
    app_description TEXT,
    is_active BOOLEAN,
    updated_at TIMESTAMPTZ
)
AS $$
BEGIN
    RETURN QUERY
    UPDATE applications a
    SET
        app_name = COALESCE(p_new_name, a.app_name),
        slug = COALESCE(p_new_slug, a.slug),
        app_description = COALESCE(p_new_description, a.app_description),
        is_active = p_new_status,
        updated_at = current_timestamp
    WHERE a.id = p_id
    RETURNING a.app_name, a.slug, a.app_description, a.is_active, a.updated_at::TIMESTAMPTZ;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION update_application TO api;
