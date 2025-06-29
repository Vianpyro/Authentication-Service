# Authentication Service Database

This is the PostgreSQL database component of the Authentication Service. It provides a secure, multi-tenant database schema with advanced security features, automated cleanup, and comprehensive audit logging.

## 🏗️ Architecture

The database follows a security-first design with tenant isolation:

```
database/
├── sql/
│   ├── schema.sql           # Main database schema
│   ├── roles.sql            # Role definitions
│   ├── functions/           # Stored functions
│   │   ├── applications/    # Application management
│   │   └── utilities/       # Utility functions
│   ├── procedures/          # Stored procedures
│   ├── triggers/            # Database triggers
│   └── roles/               # Role-specific permissions
├── scripts/
│   ├── entrypoint.sh        # Docker entrypoint
│   ├── rebuild-db.sh        # Database rebuilding
│   ├── flatten-sql.sh       # SQL file processing
│   └── cron/                # Automated maintenance
│       ├── 5_min.sql/sh     # Frequent cleanup tasks
│       └── 1_day.sql/sh     # Daily maintenance
├── Dockerfile               # Database container
└── .sqlfluff                # SQL linting configuration
```

## 🚀 Getting Started

### Prerequisites

- Docker or PostgreSQL 15+
- Alpine Linux v3.22 (for container deployment)
- Sufficient disk space for database storage

### Docker Deployment (Recommended)

1. **Build the container:**
   ```bash
   docker build -t auth-database .
   ```

2. **Run the database:**
   ```bash
   docker run -d \
     --name auth-db \
     -e POSTGRES_PASSWORD=your_secure_password \
     -e POSTGRES_DB=authentication-service \
     -p 5432:5432 \
     -v db_data:/var/lib/postgresql/data \
     auth-database
   ```

### Manual Setup

1. **Initialize the database:**
   ```bash
   # Flatten SQL files
   ./scripts/flatten-sql.sh

   # Rebuild database
   ./scripts/rebuild-db.sh postgres authentication-service
   ```

2. **Set up cron jobs:**
   ```bash
   # Add to crontab
   */5 * * * * /path/to/scripts/cron/5_min.sh
   0 2 * * * /path/to/scripts/cron/1_day.sh
   ```

## 🗃️ Database Schema

### Core Tables

#### Applications
Stores registered applications using the authentication service:
- **Primary Key:** `id` (UUID)
- **Unique Fields:** `slug` (application identifier)
- **Validation:** URL format validation, slug pattern matching
- **Security:** Cascading deletes to maintain referential integrity

#### Users
Main user table with encrypted data storage:
- **Tenant Isolation:** Row-level security by `app_id`
- **Encryption:** Email and phone data encrypted at rest
- **Hashing:** SHA-256 hashes for searchable encrypted fields
- **Security Features:** Account locking, suspension, deletion scheduling

#### Sessions
Opaque session token management:
- **Token Types:** Access and refresh tokens
- **Security:** IP address tracking, user agent logging
- **Expiration:** Automatic cleanup of expired sessions
- **Isolation:** Tenant-specific session management

### Security Tables

#### Device Fingerprints
Device tracking and recognition:
- **Fingerprinting:** SHA-256 hashed device signatures
- **Tracking:** Last seen timestamps, device naming
- **Security:** Per-user device limits and validation

#### Multi-Factor Authentication
Comprehensive 2FA support:
- **TOTP Secrets:** Encrypted TOTP secrets with key versioning
- **Backup Codes:** Hashed backup codes for recovery
- **Security Events:** Audit trail for 2FA changes

#### Audit and Security
- **Login Attempts:** Brute force detection and logging
- **Security Events:** Comprehensive security event tracking
- **IP Blocklist:** Automated and manual IP blocking

### Data Types and Domains

The schema uses custom domains for data validation:

```sql
-- Security-focused custom domains
CREATE DOMAIN argon2id_hash AS TEXT CHECK (value ~ '^\$argon2id\$v=\d+\$m=\d+,t=\d+,p=\d+\$[a-zA-Z0-9+\/=]+\$[a-zA-Z0-9+\/=]+$');
CREATE DOMAIN sha_256_hash AS TEXT CHECK (value ~ '^[a-f0-9]{64}$');
CREATE DOMAIN urlsafe_token AS TEXT CHECK (value ~ '^[A-Za-z0-9_-]{32,128}$');
CREATE DOMAIN non_empty_text AS TEXT CHECK (trim(value) <> '');
CREATE DOMAIN non_future_timestamp AS TIMESTAMPTZ CHECK (value <= current_timestamp);
```

## 🔐 Security Features

### Row-Level Security (RLS)
All user data tables implement tenant isolation:
- **Users Table:** `app_id = current_setting('app.id')::UUID`
- **Device Fingerprints:** Tenant-specific device access
- **Security Events:** Isolated audit logs per application
- **Sessions:** Application-specific session management

### Database Roles
Three distinct roles with minimal privileges:

1. **API Role** ([`sql/roles.sql`](sql/roles.sql))
   - Application-level database access
   - Read/write permissions for user operations
   - Function execution privileges

2. **Cron Role** ([`sql/roles/cron.sql`](sql/roles/cron.sql))
   - Automated maintenance tasks
   - Cleanup operations
   - Security event logging

3. **VSCode Role** ([`sql/roles/vscode.sql`](sql/roles/vscode.sql))
   - Development environment access
   - **Development only** - should not exist in production

### Automated Security Functions

#### Trigger-Based Security
- **App ID Validation:** [`validate_app_id_match`](sql/functions/applications/validate_app_id_match.sql) ensures session consistency
- **Timestamp Updates:** [`update_updated_at_timestamp`](sql/functions/utilities/update_updated_at.sql) maintains audit trails
- **Login Recovery:** [`clear_scheduled_deletion_on_login`](sql/functions/utilities/clear_scheduled_deletion_on_login.sql) prevents accidental deletions

#### Application Management
- **Registration:** [`register_application`](sql/functions/applications/register_application.sql) with validation
- **Deletion:** [`delete_application`](sql/functions/applications/delete_application.sql) with cascading cleanup
- **Lookup:** [`get_application_name`](sql/functions/applications/get_application_name.sql) for display purposes

## 🔄 Automated Maintenance

### Frequent Cleanup (5 minutes)
The [`5_min.sql`](scripts/cron/5_min.sql) script handles:
- **Account Locking:** Automatic suspension after 5 failed attempts in 15 minutes
- **Brute Force Protection:** IP-based rate limiting

### Daily Maintenance (24 hours)
The [`1_day.sql`](scripts/cron/1_day.sql) script performs:
- **Expired Data Cleanup:**
  - Pending user registrations
  - Expired sessions and tokens
  - Password reset tokens
  - TOTP secrets for deleted users

- **User Lifecycle Management:**
  - Permanent deletion after 90 days
  - Data sanitization after 2 days
  - Security event logging for sanitization

### Cron Job Setup
```bash
# Production cron configuration
*/5 * * * * /usr/local/bin/5_min.sh
0 2 * * * /usr/local/bin/1_day.sh
```

## 🛠️ Development

### Database Rebuilding
Use the provided scripts for development:

```bash
# Rebuild entire database
./scripts/rebuild-db.sh vscode authentication-service

# Flatten SQL files for processing
./scripts/flatten-sql.sh ./sql ./.tmp/flattened-sql
```

### SQL Development Standards
- **Linting:** SQLFluff configuration in [`.sqlfluff`](.sqlfluff)
- **Line Length:** 160 characters maximum
- **Dialect:** PostgreSQL-specific features encouraged
- **Security:** All functions must validate inputs

### Testing
```bash
# Test database functions
psql -U vscode -d authentication-service -f test_functions.sql

# Validate schema
psql -U vscode -d authentication-service -c "\d+ users"
```

## 📊 Performance Optimizations

### Indexes
Strategic indexing for common queries:
- **User Lookup:** `idx_users_email_app` on `(email_hash, app_id)`
- **Session Management:** `idx_sessions_user_expires` on `(user_id, expires_at)`
- **Security Monitoring:** `idx_login_attempts_app_time` on `(app_id, attempted_at DESC)`
- **Device Tracking:** `idx_fingerprint_user_seen` on `(user_id, last_seen_at DESC)`

### Connection Pooling
- **Async Support:** Designed for asyncpg driver
- **Pool Management:** Configurable connection limits
- **Health Checks:** Automatic connection validation

## 🚀 Deployment

### Production Considerations

1. **Environment Variables:**
   ```bash
   POSTGRES_USER=auth_service
   POSTGRES_PASSWORD=secure_random_password
   POSTGRES_DB=authentication-service
   ```

2. **Volume Mounting:**
   ```bash
   # Persistent data storage
   docker run -v /host/db-data:/var/lib/postgresql/data auth-database
   ```

3. **Network Security:**
   - Use internal Docker networks
   - Restrict port access to application containers only
   - Enable SSL/TLS for external connections

### Backup Strategy
```bash
# Daily backups
pg_dump -U auth_service authentication-service > backup_$(date +%Y-%m-%d).sql

# Restore from backup
psql -U auth_service -d authentication-service < backup_2025-01-29.sql

# Point-in-time recovery setup
# Configure WAL archiving in postgresql.conf
```

## 🔍 Monitoring

### Key Metrics to Monitor
- **Connection Usage:** Active connections vs. pool size
- **Query Performance:** Slow query log analysis
- **Security Events:** Failed login attempts, account lockouts
- **Storage Growth:** Table sizes and index usage
- **Maintenance Jobs:** Cron job execution status

### Useful Queries
```sql
-- Check tenant isolation
SELECT app_id, COUNT(*) FROM users GROUP BY app_id;

-- Monitor failed login attempts
SELECT app_id, COUNT(*) as failures
FROM login_attempts
WHERE attempted_at > NOW() - INTERVAL '1 hour'
  AND was_successful = false
GROUP BY app_id;

-- Review security events
SELECT event_type, COUNT(*)
FROM security_events
WHERE occurred_at > NOW() - INTERVAL '1 day'
GROUP BY event_type;
```

## 🤝 Contributing

1. **SQL Standards:** Follow PostgreSQL best practices
2. **Security First:** All changes must maintain tenant isolation
3. **Documentation:** Update README for schema changes
4. **Testing:** Validate all functions and triggers
5. **Migration Scripts:** Provide upgrade paths for schema changes

## 📚 Additional Resources

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Row-Level Security:** https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **Security Best Practices:** https://www.postgresql.org/docs/current/security.html

## 🔧 Troubleshooting

### Common Issues

1. **Permission Denied:**
   ```bash
   # Check role assignments
   psql -c "\du" authentication-service
   ```

2. **RLS Policy Violations:**
   ```sql
   -- Check current app.id setting
   SELECT current_setting('app.id', true);
   ```

3. **Cron Job Failures:**
   ```bash
   # Check cron logs
   tail -f /var/log/cron.log
   ```

### Database Browser Access
```bash
# Open database in browser-based admin tool
"$BROWSER" "http://localhost:8080/admin/database"
```
