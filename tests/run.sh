#!/bin/sh
# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
set -eu

: "${RIBBON_WP_PATH:?Set the path to a disposable WordPress install}"
: "${RIBBON_TEST_URL:?Set the localhost URL of that install}"
: "${RIBBON_ADMIN_PASSWORD_FILE:?Set the path to its test admin password file}"

case "$RIBBON_TEST_URL" in
	http://localhost:*|http://127.0.0.1:*|http://\[::1\]:*) ;;
	*) echo 'Use a disposable localhost HTTP server with an explicit port.' >&2; exit 1 ;;
esac

test_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
plugin_dir="$test_dir/../corner-ribbon"

php -l "$plugin_dir/corner-ribbon.php"
php -l "$plugin_dir/includes/settings.php"
php -l "$plugin_dir/uninstall.php"
node --check "$plugin_dir/assets/settings.js"
wp --path="$RIBBON_WP_PATH" eval-file "$test_dir/integration.php"
python3 "$test_dir/http-check.py"
python3 "$test_dir/settings-roundtrip.py"
