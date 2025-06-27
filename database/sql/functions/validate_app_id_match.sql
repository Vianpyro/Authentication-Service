-- Function to validate app_id matches user app_id
CREATE OR REPLACE FUNCTION validate_app_id_match()
RETURNS TRIGGER AS $$
DECLARE
  expected_app_id UUID;
BEGIN
  SELECT app_id INTO expected_app_id FROM users WHERE id = NEW.user_id;
  IF NEW.app_id IS DISTINCT FROM expected_app_id THEN
    RAISE EXCEPTION 'app_id mismatch for user %', NEW.user_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
