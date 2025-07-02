CREATE FUNCTION set_token_expiry()
RETURNS trigger AS $$
BEGIN
  IF NEW.expires_at IS NULL THEN
    IF NEW.token_type = 'password_reset' THEN
      NEW.expires_at := current_timestamp + INTERVAL '15 minutes';
    ELSE
      NEW.expires_at := current_timestamp + INTERVAL '24 hours';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
