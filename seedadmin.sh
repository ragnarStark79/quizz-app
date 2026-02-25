#!/usr/bin/env bash
# seedadmin.sh – Wrapper to seed an admin into the Quizz app
# Usage:
#   chmod +x seedadmin.sh
#   ./seedadmin.sh
#   ./seedadmin.sh --username admin --email admin@quizz.app --password MyPass123

set -e

# ── Configurable defaults ─────────────────────────
USERNAME="${ADMIN_USERNAME:-admin}"
EMAIL="${ADMIN_EMAIL:-admin@quizz.app}"
PASSWORD="${ADMIN_PASSWORD:-Admin@12345}"

# Parse any CLI flags that override env vars
ARGS=("$@")

cd "$(dirname "$0")"

if [ -d "venv" ]; then
  source venv/bin/activate
fi

python seedadmin.py \
  --username "$USERNAME" \
  --email    "$EMAIL" \
  --password "$PASSWORD" \
  "${ARGS[@]}"
