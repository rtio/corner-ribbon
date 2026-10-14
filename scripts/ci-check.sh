#!/usr/bin/env bash
# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
set -euo pipefail

# This bootstrap creates a disposable site against the workflow's MySQL service.
[[ "${GITHUB_ACTIONS:-}" == true ]] || { echo 'Run this bootstrap in GitHub Actions.' >&2; exit 1; }
: "${RUNNER_TEMP:?Missing runner temporary directory}"
repo_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
export RIBBON_WP_PATH="$RUNNER_TEMP/ribbon-wordpress"
export RIBBON_TEST_URL='http://127.0.0.1:8765'
export RIBBON_ADMIN_USER='qa-ribbon'
export RIBBON_ADMIN_PASSWORD_FILE="$RUNNER_TEMP/ribbon-admin-password"
umask 077
mkdir "$RIBBON_WP_PATH"
python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > "$RIBBON_ADMIN_PASSWORD_FILE"
admin_password=$(cat "$RIBBON_ADMIN_PASSWORD_FILE")
echo "::add-mask::$admin_password"

wp --path="$RIBBON_WP_PATH" core download
wp --path="$RIBBON_WP_PATH" config create --dbname=ribbon_test --dbuser=root \
  --dbpass=qa-only --dbhost=127.0.0.1:3306
wp --path="$RIBBON_WP_PATH" core install --url="$RIBBON_TEST_URL" --title='Ribbon QA' \
  --admin_user="$RIBBON_ADMIN_USER" --admin_password="$admin_password" \
  --admin_email=qa@example.test --skip-email
unset admin_password
wp --path="$RIBBON_WP_PATH" plugin install "$repo_dir/dist/rtio-corner-ribbon.zip" --activate
wp --path="$RIBBON_WP_PATH" plugin install plugin-check --version=2.1.0 --activate

php -S 127.0.0.1:8765 -t "$RIBBON_WP_PATH" > "$RUNNER_TEMP/ribbon-server.log" 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
for attempt in {1..30}; do
  if curl --fail --silent --output /dev/null "$RIBBON_TEST_URL/wp-login.php"; then
    break
  fi
  sleep 1
done
curl --fail --silent --output /dev/null "$RIBBON_TEST_URL/wp-login.php"
bash "$repo_dir/tests/run.sh"

# Plugin Check can return exit code zero even when it reports findings.
wp --path="$RIBBON_WP_PATH" plugin check rtio-corner-ribbon \
  --require="$RIBBON_WP_PATH/wp-content/plugins/plugin-check/cli.php" \
  --format=strict-json --include-low-severity-errors --include-low-severity-warnings \
  > "$RUNNER_TEMP/ribbon-plugin-check.txt"
cat "$RUNNER_TEMP/ribbon-plugin-check.txt"
python3 "$repo_dir/scripts/release.py" --plugin-check "$RUNNER_TEMP/ribbon-plugin-check.txt"
