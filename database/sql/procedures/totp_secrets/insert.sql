CREATE OR REPLACE PROCEDURE insert_totp_secret(
    p_user_id UUID,
    p_secret_encrypted NON_EMPTY_TEXT,
    p_secret_hash SHA_256_HASH,
    p_key_version SMALLINT DEFAULT 1
) AS $$
BEGIN
    INSERT INTO totp_secrets (user_id, secret_encrypted, secret_hash, key_version)
    VALUES (p_user_id, p_secret_encrypted, p_secret_hash, p_key_version);
END;
$$ LANGUAGE plpgsql;
