# Corner Ribbon tests

These tests use real WordPress APIs and authenticated HTTP requests. They change options and create a disposable subscriber. Use a fresh local test installation, never a production site or a local copy containing important data.

Requirements: PHP, Node (syntax check only), Python 3, WP-CLI, a running WordPress installation with Corner Ribbon active, and a test administrator. No Python packages or npm dependencies are needed. Both MySQL and the official SQLite integration can be used; this release was tested with WordPress 7.0.4, PHP 8.4.17, SQLite, and Beep.

## Run

Set these variables to your disposable installation. The password file contains only the test administrator's password and must stay outside the plugin/source directory.

```sh
export RIBBON_WP_PATH="$TMPDIR/ribbon-test/wordpress"
export RIBBON_TEST_URL="http://127.0.0.1:8765"
export RIBBON_ADMIN_USER="qa-ribbon"
export RIBBON_ADMIN_PASSWORD_FILE="$TMPDIR/ribbon-test/admin-password"
sh tests/run.sh
```

Start your local server before running the suite. The runner requires a loopback URL with an explicit port. The legacy HTTP checks restore the default tribute; the settings round-trip suite restores the values it found at startup.

## Coverage

- `integration.php`: 19 assertions against WordPress option registration/sanitization and rendering hooks, including duplicate prevention and malformed values.
- `http-check.py`: 15 checks for authenticated saving, URL rendering, nonce enforcement, capability-specific subscriber denial, disabled output, and feed isolation.
- `settings-roundtrip.py`: 12 named unittest scenarios with subcases. Verify full name/message, URL, and both colors after fresh GETs; independent edits; replacement of earlier values; Unicode, quotes, and the length limit; clearing links; short/long hex values; invalid CSS/URLs; array inputs; blank labels; missing/bad nonces; and admin asset isolation.

The round-trip parser compares decoded field values and the ribbon's actual markup instead of searching for arbitrary matching text elsewhere on the page. Distinct color values catch swapped/defaulted colors, and two successive saves catch stale persistence.

## Browser verification

Also verified with JavaScript enabled: both color pickers initialize with descriptive accessible names; changing both picker values and submitting the actual form persists the name, URL, and colors; the frontend's computed text, border, and background colors match; the link has keyboard focus; picker JavaScript is absent from the frontend. Desktop/mobile layout checks from 1.0.0 remain applicable because ribbon geometry is unchanged.
