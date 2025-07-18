#!/bin/bash
set -e

echo "📄 Overriding pg_hba.conf and postgresql.conf..."

# Replace default config files
cp /etc/postgresql/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf
cp /etc/postgresql/postgresql.conf /var/lib/postgresql/data/postgresql.conf

# Ensure proper permissions
chown postgres:postgres /var/lib/postgresql/data/pg_hba.conf
chown postgres:postgres /var/lib/postgresql/data/postgresql.conf
