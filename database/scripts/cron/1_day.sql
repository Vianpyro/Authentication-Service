-- Cron job to clean up expired data from various tables
DELETE FROM pending_users
WHERE expires_at <= current_timestamp;

DELETE FROM sessions
WHERE
    expires_at <= current_timestamp
    AND is_active = FALSE;

DELETE FROM password_reset_tokens
WHERE expires_at <= current_timestamp;

-- Cron job to delete users scheduled for deletion after 90 days
DELETE FROM users
WHERE
    scheduled_for_deletion_at IS NOT NULL
    AND scheduled_for_deletion_at <= current_timestamp - interval '90 days';

-- Sanitize old users scheduled for deletion and collect their IDs
CREATE TEMP TABLE sanitized_users_ids (id uuid);

INSERT INTO sanitized_users_ids (id)
UPDATE users
SET
    email_encrypted = NULL,
    password_hash = NULL,
    phone_encrypted = NULL,
    phone_hash = NULL,
    is_2fa_enabled = FALSE
WHERE
    scheduled_for_deletion_at IS NOT NULL
    AND scheduled_for_deletion_at <= current_timestamp - interval '2 days'
    AND email_encrypted IS NOT NULL
RETURNING id;

INSERT INTO security_events (user_id, event_type, metadata, occurred_at)
SELECT
    id AS user_id,
    'sanitized' AS event_type,
    jsonb_build_object('reason', 'scheduled_deletion') AS metadata,
    current_timestamp AS occurred_at
FROM sanitized_users_ids;

DELETE FROM totp_secrets
WHERE user_id IN (SELECT id FROM sanitized_users_ids);
DELETE FROM sessions
WHERE user_id IN (SELECT id FROM sanitized_users_ids);
DELETE FROM password_reset_tokens
WHERE user_id IN (SELECT id FROM sanitized_users_ids);
DELETE FROM device_fingerprints
WHERE user_id IN (SELECT id FROM sanitized_users_ids);

DROP TABLE sanitized_users_ids;
