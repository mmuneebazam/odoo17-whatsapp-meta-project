#!/usr/bin/env bash
# Start the Odoo 17 server for this project.
# Usage:
#   ./scripts/run_odoo.sh                                                  # run server
#   ./scripts/run_odoo.sh -u whatsapp_meta_integration --stop-after-init   # update module
#   ./scripts/run_odoo.sh --dev=all                                        # dev mode (auto-reload)
# Override defaults with env vars: ODOO_SRC, ODOO_VENV, ODOO_DB
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ODOO_SRC="${ODOO_SRC:-$HOME/odoo17}"
ODOO_VENV="${ODOO_VENV:-$HOME/odoo17-venv}"
DB_NAME="${ODOO_DB:-whatsapp_odoo17}"

exec "$ODOO_VENV/bin/python" "$ODOO_SRC/odoo-bin" \
    -c "$PROJECT_DIR/odoo.conf" \
    -d "$DB_NAME" \
    "$@"
