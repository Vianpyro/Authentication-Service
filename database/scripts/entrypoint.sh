#!/bin/sh
set -e

USERNAME=${USERNAME:-postgres}
PGUSER=${POSTGRES_USER:-postgres}
PGDB=${POSTGRES_DB:-$PGUSER}
PGPASS=${POSTGRES_PASSWORD}
PGDATA=${PGDATA:-/var/lib/postgresql/data}
FLATTENED_SQL_DIR=${FLATTEN_SQL_DIR:-/tmp/flattened-sql}

echo "🔒 Ensuring correct permissions..."
chown -R "$USERNAME:$USERNAME" "$PGDATA" /run/postgresql

echo "⚙️ Overriding pg_hba.conf and postgresql.conf..."
cp /etc/postgresql/pg_hba.conf /tmp/pg_hba.conf
cp /etc/postgresql/postgresql.conf /tmp/postgresql.conf

if [ ! -f "$PGDATA/PG_VERSION" ] && [ "$(ls -A "$PGDATA")" ]; then
  echo "⚠️  PG_VERSION missing, but $PGDATA is not empty. Cleaning up..."
  rm -rf "${PGDATA:?}/"*
fi

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "📥 Running initdb..."
  echo "$PGPASS" > /tmp/pwfile
  chmod 600 /tmp/pwfile
  chown "$USERNAME:$USERNAME" /tmp/pwfile

  initdb -D "$PGDATA" --auth=scram-sha-256 --username="$PGUSER" --pwfile=/tmp/pwfile
  rm /tmp/pwfile

  if [ "$PGDB" != "postgres" ]; then
    echo "🛠️  Creating database '$PGDB'..."
    postgres --single -jE -D "$PGDATA" -k /run/postgresql <<-EOSQL
      CREATE DATABASE "$PGDB" OWNER "$PGUSER";
EOSQL
  fi

  echo "📂 Flattening SQL files..."
  /usr/local/bin/flatten-sql.sh /docker-entrypoint-initdb.d "$FLATTENED_SQL_DIR"

  echo "🗑️  Cleaning up /docker-entrypoint-initdb.d/..."
  rm -rf /docker-entrypoint-initdb.d/*

  echo "🔁 Applying custom config files..."
  cp /tmp/pg_hba.conf "$PGDATA/pg_hba.conf"
  cp /tmp/postgresql.conf "$PGDATA/postgresql.conf"
  chown "$USERNAME:$USERNAME" "$PGDATA/pg_hba.conf" "$PGDATA/postgresql.conf"

  echo "🚀 Starting PostgreSQL temporarily with pg_cron..."
  postgres -D "$PGDATA" -k /run/postgresql \
    -c shared_preload_libraries=pg_cron \
    -c cron.database_name="$PGDB" &
  PG_PID=$!

  until pg_isready -h /run/postgresql -U "$PGUSER"; do
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 1
  done

  echo "🧩 Creating pg_cron extension in $PGDB..."
  psql -h /run/postgresql -U "$PGUSER" -d "$PGDB" -c "CREATE EXTENSION IF NOT EXISTS pg_cron;"

  echo "✅ Running init-db.sh..."
  /usr/local/bin/init-db.sh "$PGUSER" "$PGDB"

  echo "🧼 Stopping temporary PostgreSQL..."
  kill "$PG_PID"
  wait "$PG_PID"
else
  echo "🔁 Reusing existing database volume."
  echo "🔁 Applying config overrides..."
  cp /tmp/pg_hba.conf "$PGDATA/pg_hba.conf"
  cp /tmp/postgresql.conf "$PGDATA/postgresql.conf"
  chown "$USERNAME:$USERNAME" "$PGDATA/pg_hba.conf" "$PGDATA/postgresql.conf"
fi

echo "🚀 Starting PostgreSQL with pg_cron..."
exec postgres -D "$PGDATA" -k /run/postgresql \
  -c shared_preload_libraries=pg_cron \
  -c cron.database_name="$PGDB"
