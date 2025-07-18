FROM alpine:3.22

# Set environment variables
ENV LANG=en_US.UTF-8 \
    PGDATA=/var/lib/postgresql/data \
    POSTGRES_DB=authentication-service \
    POSTGRES_USER=postgres \
    FLATTEN_SQL_DIR=/tmp/flattened-sql

# Install PostgreSQL and required tools
RUN apk add --no-cache bash postgresql postgresql-contrib postgresql-pg_cron tini

# Ensure required directories exist and are owned by the postgres user
RUN mkdir -p /run/postgresql "$PGDATA" && \
    chown -R postgres:postgres /run/postgresql "$PGDATA"

# Copy entrypoint scripts and database initialization files
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY scripts/flatten-sql.sh /usr/local/bin/flatten-sql.sh
COPY scripts/rebuild-db.sh /usr/local/bin/init-db.sh
COPY scripts/override-pg_hba.sh /docker-entrypoint-initdb.d/
COPY sql/ /docker-entrypoint-initdb.d/

# Ensure scripts are executable and have correct ownership
RUN chmod +x /usr/local/bin/*.sh && \
    chmod +x /docker-entrypoint-initdb.d/override-pg_hba.sh && \
    chown root:root /usr/local/bin/*.sh && \
    chown -R postgres:postgres /docker-entrypoint-initdb.d && \
    sed -i 's/\r$//' /usr/local/bin/*.sh

# Copy configuration files (as root before switching user)
COPY config/. /etc/postgresql/

# Drop root privileges
USER postgres

# Use tini for proper signal handling
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/entrypoint.sh"]

# Default command
CMD []

# Expose port
EXPOSE 5432/tcp

# Healthcheck to ensure PostgreSQL is ready
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD pg_isready -q -h /run/postgresql -U "$POSTGRES_USER" || exit 1
