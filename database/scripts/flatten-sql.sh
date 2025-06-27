#!/bin/sh

set -e

# Default directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SRC_DIR="${1:-$PROJECT_ROOT/sql}"
DEST_DIR="${2:-${FLATTEN_SQL_DIR:-$PROJECT_ROOT/.tmp/flattened-sql}}"

echo "📦 Flattening SQL files from '$SRC_DIR' to '$DEST_DIR'..."

rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"

find "$SRC_DIR" -type f -name "*.sql" ! -name "*.session.sql" ! -name "*.test.sql" | while read -r file; do
	rel_path="${file#"$SRC_DIR"/}"
	new_name=$(echo "$rel_path" | sed 's|/|_|g')
	depth=$(echo "$rel_path" | awk -F'/' '{print NF-1}')
	cp "$file" "$DEST_DIR/${depth}${new_name}"
	echo "✅ Copied: $file → $DEST_DIR/${depth}${new_name}"
done
