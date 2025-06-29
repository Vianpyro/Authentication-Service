-- Cron job to lock accounts with excessive failed login attempts
WITH recent_failures AS (
    SELECT
        user_id,
        COUNT(*) AS failures
    FROM login_attempts
    WHERE
        attempted_at >= CURRENT_TIMESTAMP - interval '15 minutes'
        AND was_successful = FALSE
        AND user_id IS NOT NULL
    GROUP BY user_id
)

UPDATE users
SET
    is_suspended = TRUE,
    account_locked_at = CURRENT_TIMESTAMP
FROM recent_failures
WHERE
    users.id = recent_failures.user_id
    AND recent_failures.failures >= 5
    AND is_suspended = FALSE;
