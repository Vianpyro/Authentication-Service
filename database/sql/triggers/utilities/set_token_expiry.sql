-- Set the expiry time for a token depending on its type when it is inserted into the tokens table
CREATE TRIGGER trg_set_token_expiry
BEFORE INSERT ON tokens
FOR EACH ROW EXECUTE FUNCTION set_token_expiry();
