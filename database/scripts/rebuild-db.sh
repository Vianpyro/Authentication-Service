#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

DB_USER="$1"
DB_NAME="$2"
DB_PASS="${POSTGRES_PASSWORD}"
FLATTENED_SQL_DIR="${FLATTEN_SQL_DIR:-$PROJECT_ROOT/.tmp/flattened-sql}"

export PGPASSWORD="$DB_PASS"

# Drop and recreate the database
echo "🔁 Dropping and recreating database '$DB_NAME'..."
dropdb -h /run/postgresql -U "$DB_USER" "$DB_NAME" || true
createdb -h /run/postgresql -U "$DB_USER" "$DB_NAME"

# Execute all flattened SQL files (excluding nested ones)
find "$FLATTENED_SQL_DIR" -maxdepth 1 -name "*.sql" | sort | while read -r file; do
	echo "📄 Running $file..."
	psql -h /run/postgresql -U "$DB_USER" -d "$DB_NAME" -f "$file"
done

# Cleanup
rm -rf "$FLATTENED_SQL_DIR"
