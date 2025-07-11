CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 🧱 Domains for common data types and constraints
CREATE DOMAIN argon2id_hash AS TEXT CHECK (value ~ '^\$argon2id\$v=\d+\$m=\d+,t=\d+,p=\d+\$[a-zA-Z0-9+\/=]+\$[a-zA-Z0-9+\/=]+$');

CREATE DOMAIN non_empty_text AS TEXT CHECK (trim(value) <> '');

CREATE DOMAIN non_future_timestamptz AS TIMESTAMPTZ CHECK (value <= current_timestamp);

CREATE DOMAIN sha_256_hash AS TEXT CHECK (value ~ '^[a-f0-9]{64}$');

CREATE DOMAIN user_agent_str AS TEXT CHECK (
    char_length(value) <= 256
    AND value ~ '^[A-Za-z0-9\\s\\-\\._;:/\\(\\),]+$'
);

-- 🧩 Custom Types
CREATE TYPE token_type AS ENUM (
    'email_verification',
    'mfa_challenge',
    'password_reset',
    'recovery_email_verification',
    'session'
);
CREATE TYPE session_token_type AS ENUM ('access', 'mfa_challenge', 'refresh');
CREATE TYPE event_type AS ENUM ('password_changed', '2fa_enabled', '2fa_disabled', 'account_locked', 'sanitized');
CREATE TYPE api_permission AS ENUM ('read_users', 'write_users', 'admin', 'analytics', 'webhooks');

-- 🚀 Applications Table: Stores registered applications using the service
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9_-]{3,50}$'),
    name TEXT NOT NULL CHECK (char_length(name) >= 3 AND char_length(name) <= 100),
    description TEXT CHECK (char_length(description) <= 500),
    api_rate_limit INTEGER DEFAULT 1000 CHECK (api_rate_limit > 0),
    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    updated_at NON_FUTURE_TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 👤 Users Table: Only verified users live here
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,

    email_encrypted NON_EMPTY_TEXT NOT NULL,
    -- email_iv BYTEA NOT NULL,
    -- email_tag BYTEA NOT NULL,
    email_key_version SMALLINT DEFAULT 1,

    email_hash SHA_256_HASH NOT NULL,

    recovery_email_encrypted NON_EMPTY_TEXT,
    recovery_email_iv BYTEA,
    recovery_email_tag BYTEA,
    recovery_email_key_version SMALLINT DEFAULT 1,

    password_hash ARGON2ID_HASH NOT NULL,

    phone_encrypted NON_EMPTY_TEXT,
    phone_iv BYTEA,
    phone_tag BYTEA,
    phone_key_version SMALLINT DEFAULT 1,

    phone_hash SHA_256_HASH,

    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_recovery_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_2fa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
    failed_login_count INTEGER NOT NULL DEFAULT 0,

    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    updated_at NON_FUTURE_TIMESTAMPTZ,
    last_login_at NON_FUTURE_TIMESTAMPTZ,
    scheduled_for_deletion_at NON_FUTURE_TIMESTAMPTZ,
    account_locked_at NON_FUTURE_TIMESTAMPTZ,

    CONSTRAINT unique_user_per_app UNIQUE (email_hash, app_id),
    CONSTRAINT chk_email_hash_present CHECK (email_encrypted IS NOT NULL AND email_hash IS NOT NULL),
    CONSTRAINT chk_phone_hash_present CHECK (
        (phone_encrypted IS NULL AND phone_hash IS NULL)
        OR (phone_encrypted IS NOT NULL AND phone_hash IS NOT NULL)
    )
);

-- 🔒 RLS Policy for Users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON users USING (app_id = current_setting('app.id')::UUID);

-- 🪙 Unified Token Management Table
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    token_hash BYTEA NOT NULL UNIQUE,
    token_type TOKEN_TYPE NOT NULL,
    session_type SESSION_TOKEN_TYPE, -- only used if token_type = 'session'
    metadata JSONB DEFAULT '{}'::JSONB,

    user_id UUID REFERENCES users (id) ON DELETE CASCADE,
    app_id UUID REFERENCES applications (id) ON DELETE CASCADE,

    -- Used only if token_type = 'recovery_email_verification'
    email_encrypted TEXT,
    email_iv BYTEA,
    email_tag BYTEA,
    email_key_version SMALLINT DEFAULT 1,

    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    expires_at TIMESTAMPTZ NOT NULL,

    -- Business logic constraints
    CONSTRAINT chk_user_id_required CHECK (
        (token_type = 'email_verification' AND user_id IS NULL) OR user_id IS NOT NULL
    ),
    -- Ensure encrypted email is only present for recovery email verification tokens
    CONSTRAINT chk_email_if_needed CHECK (
        (token_type = 'recovery_email_verification' AND email_encrypted IS NOT NULL AND email_iv IS NOT NULL AND email_tag IS NOT NULL)
        OR (token_type <> 'recovery_email_verification' AND email_encrypted IS NULL AND email_iv IS NULL AND email_tag IS NULL)
    ),
    CONSTRAINT chk_app_id_required CHECK (
        (token_type = 'email_verification' AND app_id IS NULL) OR app_id IS NOT NULL
    ),
    CONSTRAINT chk_email_for_verification CHECK (
        (token_type = 'recovery_email_verification' AND email_encrypted IS NOT NULL)
        OR (token_type <> 'recovery_email_verification' AND email_encrypted IS NULL)
    ),
    -- Ensure session_type is only set for session tokens
    CONSTRAINT chk_session_type_only_when_session CHECK (
        (token_type IN ('session', 'mfa_challenge') AND session_type IS NOT NULL)
        OR (token_type NOT IN ('session', 'mfa_challenge') AND session_type IS NULL)
    )
);

-- 🕐 Pending Users Table: Awaiting email verification
CREATE TABLE pending_users (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL REFERENCES tokens (id) ON DELETE CASCADE,

    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    email_encrypted NON_EMPTY_TEXT NOT NULL,
    -- email_iv BYTEA NOT NULL,
    -- email_tag BYTEA NOT NULL,
    email_key_version SMALLINT DEFAULT 1,

    email_hash SHA_256_HASH NOT NULL,

    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp + INTERVAL '24 hour',

    ip_address INET CHECK (ip_address IS NULL OR family(ip_address) IN (4, 6)),
    user_agent USER_AGENT_STR,

    CONSTRAINT unique_pending_user_per_app UNIQUE (email_hash, app_id)
);

-- 🔐 RLS Policy for Pending Users
CREATE POLICY policy_tenant_isolation ON pending_users USING (app_id = current_setting('app.id')::UUID);

-- 🧠 Device Fingerprints Table: Tracks devices for each user
CREATE TABLE device_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,

    fingerprint_hash SHA_256_HASH NOT NULL,
    name TEXT NOT NULL DEFAULT 'Unknown Device' CHECK (name <> '' AND char_length(name) <= 100),
    user_agent USER_AGENT_STR,
    last_seen_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,

    CONSTRAINT unique_fingerprint_per_user UNIQUE (user_id, fingerprint_hash)
);

-- 🔐 RLS Policy for Device Fingerprints
ALTER TABLE device_fingerprints ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON device_fingerprints USING (app_id = current_setting('app.id')::UUID);

-- 📦 Sessions Table: Opaque session token management
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,

    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_id INTEGER NOT NULL REFERENCES tokens (id) ON DELETE CASCADE,

    ip_address INET CHECK (ip_address IS NULL OR family(ip_address) IN (4, 6)),
    user_agent USER_AGENT_STR,
    device_fingerprint UUID REFERENCES device_fingerprints (id) ON DELETE SET NULL,

    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,

    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 🔐 RLS Policy for Sessions
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON sessions USING (app_id = current_setting('app.id')::UUID);

-- 🧩 Index for active sessions by token
CREATE UNIQUE INDEX unique_active_token_idx ON sessions (token_id) WHERE is_active = TRUE;

-- 🔑 TOTP 2FA Secrets
CREATE TABLE totp_secrets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    secret_encrypted NON_EMPTY_TEXT NOT NULL,
    secret_hash SHA_256_HASH NOT NULL,
    key_version SMALLINT NOT NULL DEFAULT 1,
    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    confirmed_at NON_FUTURE_TIMESTAMPTZ
);

-- 🔐 RLS Policy for TOTP Secrets
ALTER TABLE totp_secrets ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON totp_secrets
USING (user_id IN (
    SELECT id FROM users
    WHERE app_id = current_setting('app.id')::UUID
));

-- 🔐 MFA Backup Codes Table: Stores 2FA backup codes
CREATE TABLE mfa_backup_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    code_hash SHA_256_HASH NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    used_at NON_FUTURE_TIMESTAMPTZ
);

-- 🔐 RLS Policy for MFA Backup Codes
ALTER TABLE mfa_backup_codes ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON mfa_backup_codes USING (app_id = current_setting('app.id')::UUID);

-- 🧪 Login Attempt Logs: Brute force protection and auditing
CREATE TABLE login_attempts (
    id SERIAL PRIMARY KEY,

    user_id UUID REFERENCES users (id) ON DELETE SET NULL,
    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,

    email_encrypted NON_EMPTY_TEXT NOT NULL CHECK (char_length(email_encrypted) >= 5),
    email_hash SHA_256_HASH NOT NULL,
    ip_address INET CHECK (ip_address IS NULL OR family(ip_address) IN (4, 6)),
    user_agent USER_AGENT_STR,

    was_successful BOOLEAN NOT NULL,
    attempted_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp
);

-- 🔐 RLS Policy for Login Attempts
ALTER TABLE login_attempts ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON login_attempts USING (app_id = current_setting('app.id')::UUID);

-- 🚨 Security Events Table: Tracks security-sensitive operations
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users (id) ON DELETE CASCADE,
    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    event_type EVENT_TYPE NOT NULL,
    metadata JSONB,
    occurred_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp
);

-- 🔐 RLS Policy for Security Events
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON security_events USING (app_id = current_setting('app.id')::UUID);

-- 🚫 IP Blocklist Table: IPs blocked manually or automatically
CREATE TABLE ip_blocklist (
    ip_address INET PRIMARY KEY,
    blocked_by_user_id UUID REFERENCES users (id) ON DELETE SET NULL,
    manual_block BOOLEAN NOT NULL DEFAULT FALSE,
    reason TEXT,
    duration INTERVAL NOT NULL DEFAULT '3 days' CHECK (duration > INTERVAL '0 seconds'),
    blocked_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp
);

-- 🔐 RLS Policy for IP Blocklist
ALTER TABLE ip_blocklist ENABLE ROW LEVEL SECURITY;
CREATE POLICY policy_tenant_isolation ON ip_blocklist USING (TRUE);

-- 🔐 API Keys Table: For server-to-server authentication
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    app_id UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,

    name TEXT NOT NULL CHECK (char_length(name) >= 3 AND char_length(name) <= 100),
    key_hash SHA_256_HASH NOT NULL UNIQUE,
    key_prefix TEXT NOT NULL CHECK (key_prefix ~ '^ak_[a-z0-9]{8}$'),

    permissions API_PERMISSION [] NOT NULL DEFAULT '{}' CHECK (array_length(permissions, 1) > 0),

    created_at NON_FUTURE_TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp + INTERVAL '1 year',
    last_used_at NON_FUTURE_TIMESTAMPTZ,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT unique_name_per_app UNIQUE (app_id, name)
);

-- 🔍 Users: lookup & uniqueness enforcement
CREATE INDEX idx_users_email_app ON users (email_hash, app_id);
CREATE INDEX idx_fingerprint_user_seen ON device_fingerprints (user_id, last_seen_at DESC);
CREATE INDEX idx_login_attempts_app_time ON login_attempts (app_id, attempted_at DESC);
CREATE INDEX idx_tokens_session_type ON tokens (session_type);
CREATE INDEX idx_tokens_user_type ON tokens (user_id, token_type);
CREATE INDEX idx_pending_users_token ON pending_users (token_id, app_id);
CREATE INDEX idx_api_keys_hash ON api_keys (key_hash);
CREATE INDEX idx_users_app_id ON users (app_id);
CREATE INDEX idx_users_last_login ON users (last_login_at DESC);

-- 🕐 Tokens: expiration + lookup
CREATE INDEX idx_tokens_user_expires ON tokens (user_id, expires_at);
CREATE INDEX idx_tokens_app_type_expires ON tokens (app_id, token_type, expires_at);
CREATE INDEX idx_tokens_session_active ON tokens (user_id, session_type) WHERE token_type = 'session';

-- 🧪 Pending Users: expiry + email lookup
CREATE INDEX idx_pending_users_expires ON pending_users (expires_at);
CREATE INDEX idx_pending_users_app_email ON pending_users (app_id, email_hash);

-- 🧿 Sessions: active tracking
CREATE INDEX idx_sessions_user_active ON sessions (user_id, is_active);
CREATE INDEX idx_sessions_last_activity ON sessions (last_activity_at DESC);
CREATE INDEX idx_sessions_app_user ON sessions (app_id, user_id);
CREATE INDEX idx_sessions_token_id ON sessions (token_id);

-- 🔑 Device Fingerprints
CREATE INDEX idx_device_fingerprints_user_seen ON device_fingerprints (user_id, last_seen_at DESC);
CREATE INDEX idx_device_fingerprints_app_user ON device_fingerprints (app_id, user_id);

-- 🔐 TOTP secrets: confirm tracking
CREATE INDEX idx_totp_secrets_confirmed ON totp_secrets (user_id) WHERE confirmed_at IS NOT NULL;

-- 🔁 MFA backup codes
CREATE INDEX idx_mfa_codes_user_used ON mfa_backup_codes (user_id, used);
CREATE INDEX idx_mfa_codes_app_user ON mfa_backup_codes (app_id, user_id);

-- 🚨 Login Attempts: brute-force defense
CREATE INDEX idx_login_attempts_email_app ON login_attempts (email_hash, app_id, attempted_at DESC);
CREATE INDEX idx_login_attempts_ip_time ON login_attempts (ip_address, attempted_at DESC);

-- ⚠️ Security Events
CREATE INDEX idx_security_events_user_time ON security_events (user_id, occurred_at DESC);
CREATE INDEX idx_security_events_app_time ON security_events (app_id, occurred_at DESC);

-- 🚫 IP Blocklist
CREATE INDEX idx_ip_blocklist_blocked_at ON ip_blocklist (blocked_at DESC);

-- 📟 API keys
CREATE INDEX idx_api_keys_app_active ON api_keys (app_id, is_active);
CREATE INDEX idx_api_keys_prefix ON api_keys (key_prefix);

-- 🔐 Applications
CREATE INDEX idx_applications_slug ON applications (slug);

-- 🚫 Revoke public access to all tables
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM public;
