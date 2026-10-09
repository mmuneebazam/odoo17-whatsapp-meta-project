#!/usr/bin/env bash
# One-shot local environment setup for the Odoo 17 WhatsApp & Meta Integration project.
# Usage: ./scripts/setup_env.sh
# Override defaults with env vars, e.g.: ODOO_SRC=/opt/odoo17 ./scripts/setup_env.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ODOO_SRC="${ODOO_SRC:-$HOME/odoo17}"
ODOO_VENV="${ODOO_VENV:-$HOME/odoo17-venv}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
DB_NAME="${ODOO_DB:-whatsapp_odoo17}"
DB_USER="${ODOO_DB_USER:-odoo}"
DB_PASSWORD="${ODOO_DB_PASSWORD:-odoo}"

echo "==> Project:  $PROJECT_DIR"
echo "==> Odoo src: $ODOO_SRC"
echo "==> Venv:     $ODOO_VENV"

# 1. System packages (Debian/Ubuntu). Skipped automatically on macOS/other.
if command -v apt-get >/dev/null 2>&1; then
    echo "==> Installing system packages (apt)..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq git postgresql libpq-dev libxml2-dev libxslt1-dev \
        libldap2-dev libsasl2-dev libjpeg-dev zlib1g-dev libffi-dev build-essential "$PYTHON_BIN" \
        "$PYTHON_BIN-venv" "$PYTHON_BIN-dev" || true
fi

# 2. Odoo 17 source
if [ ! -d "$ODOO_SRC/odoo" ]; then
    echo "==> Cloning Odoo 17 into $ODOO_SRC ..."
    git clone --depth 1 --branch 17.0 https://github.com/odoo/odoo "$ODOO_SRC"
else
    echo "==> Odoo source already present."
fi

# 3. Python virtual environment + Odoo requirements
if [ ! -d "$ODOO_VENV" ]; then
    echo "==> Creating virtual environment ..."
    "$PYTHON_BIN" -m venv "$ODOO_VENV"
fi
echo "==> Installing Python requirements (this can take a few minutes) ..."
"$ODOO_VENV/bin/pip" install -q wheel
"$ODOO_VENV/bin/pip" install -q -r "$ODOO_SRC/requirements.txt"

# 4. PostgreSQL role
if command -v sudo >/dev/null 2>&1 && sudo -n -u postgres psql -c "SELECT 1" >/dev/null 2>&1; then
    echo "==> Creating PostgreSQL role '$DB_USER' ..."
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB SUPERUSER;" 2>/dev/null \
        || echo "    (role probably already exists)"
fi

# 5. odoo.conf from sample
if [ ! -f "$PROJECT_DIR/odoo.conf" ]; then
    echo "==> Creating odoo.conf from odoo.conf.sample ..."
    sed -e "s|/path/to/odoo17|$ODOO_SRC|g" \
        -e "s|/path/to/odoo17_whatsapp_meta_project|$PROJECT_DIR|g" \
        -e "s|db_password = odoo|db_password = $DB_PASSWORD|" \
        "$PROJECT_DIR/odoo.conf.sample" > "$PROJECT_DIR/odoo.conf"
    echo "    Please review $PROJECT_DIR/odoo.conf"
else
    echo "==> odoo.conf already exists."
fi

# 6. Database + module install
if command -v createdb >/dev/null 2>&1; then
    echo "==> Creating database '$DB_NAME' and installing whatsapp_meta_integration ..."
    PGPASSWORD="$DB_PASSWORD" createdb -h localhost -U "$DB_USER" "$DB_NAME" 2>/dev/null \
        || echo "    (database probably already exists)"
    "$ODOO_VENV/bin/python" "$ODOO_SRC/odoo-bin" -c "$PROJECT_DIR/odoo.conf" -d "$DB_NAME" \
        -i whatsapp_meta_integration --stop-after-init
fi

echo
echo "==> Done! Start the server with:"
echo "    $PROJECT_DIR/scripts/run_odoo.sh"
echo "    then open http://localhost:8069"
