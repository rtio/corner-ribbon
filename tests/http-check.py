# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
"""Check the Settings API through real HTTP requests in the disposable test site."""
import http.cookiejar
import os
from pathlib import Path
import re
import secrets
import subprocess
import urllib.error
import urllib.parse
import urllib.request

root = Path(os.environ["RIBBON_WP_PATH"])
base = os.environ["RIBBON_TEST_URL"].rstrip("/")
admin_user = os.environ.get("RIBBON_ADMIN_USER", "qa-ribbon")
password_file = Path(os.environ["RIBBON_ADMIN_PASSWORD_FILE"])
if urllib.parse.urlsplit(base).hostname not in {"localhost", "127.0.0.1", "::1"}:
    raise RuntimeError("These mutating tests require a disposable localhost site")
checks = 0


def check(condition, message):
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


def session():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )


def request(client, path, data=None):
    encoded = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with client.open(base + path, encoded, timeout=15) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def login(client, username, password):
    request(client, "/wp-login.php")
    return request(client, "/wp-login.php", {
        "log": username, "pwd": password,
        "wp-submit": "Log In", "redirect_to": base + "/wp-admin/", "testcookie": "1",
    })


admin = session()
login(admin, admin_user, password_file.read_text().strip())
status, page = request(admin, "/wp-admin/options-general.php?page=corner-ribbon")
check(status == 200 and 'id="rtio-cr-text"' in page, "Administrator can open settings")
nonce = re.search(r'name="_wpnonce" value="([^"]+)"', page).group(1)
defaults = {
    "option_page": "rtio_corner_ribbon", "action": "update", "_wpnonce": nonce,
    "rtio_corner_ribbon[enabled]": "1", "rtio_corner_ribbon[text]": "R.I.P. ERIC",
    "rtio_corner_ribbon[accent]": "#00e49a", "rtio_corner_ribbon[background]": "#000000",
    "rtio_corner_ribbon[url]": "",
}

try:
    status, _ = request(admin, "/wp-admin/options.php", {
        **defaults, "rtio_corner_ribbon[text]": "Remember Eric",
        "rtio_corner_ribbon[url]": "https://example.test/tribute",
    })
    check(status == 200, "Valid settings submission succeeds")
    _, front = request(session(), "/")
    check('href="https://example.test/tribute"' in front and "Remember Eric" in front,
          "Saved label and URL appear on frontend")
    check(front.count('id="rtio-corner-ribbon"') == 1, "Only one ribbon is rendered")

    no_nonce = {k: v for k, v in defaults.items() if k != "_wpnonce"}
    status, _ = request(admin, "/wp-admin/options.php", no_nonce)
    check(status == 403, "Submission without nonce is rejected")
    _, front = request(session(), "/")
    check("Remember Eric" in front, "Rejected submission does not change saved settings")

    password = secrets.token_urlsafe(24)
    subprocess.run(["wp", "--path=" + str(root), "user", "update", "qa-ribbon-subscriber",
                    "--user_pass=" + password], check=True, capture_output=True)
    subscriber = session()
    login(subscriber, "qa-ribbon-subscriber", password)
    status, _ = request(subscriber, "/wp-admin/options-general.php?page=corner-ribbon")
    check(status == 403, "Subscriber cannot open settings")
    status, denied = request(subscriber, "/wp-admin/options.php", defaults)
    check(status == 403, "Subscriber cannot save settings")
    check("not allowed to manage options" in denied, "Subscriber is denied by capability before nonce verification")
    _, front = request(session(), "/")
    check("Remember Eric" in front, "Subscriber submission does not mutate settings")

    disabled = {k: v for k, v in defaults.items() if k != "rtio_corner_ribbon[enabled]"}
    status, _ = request(admin, "/wp-admin/options.php", disabled)
    check(status == 200, "Visibility can be turned off")
    _, front = request(session(), "/")
    check('id="rtio-corner-ribbon"' not in front and "ribbon.css" not in front,
          "Disabled plugin emits neither ribbon nor stylesheet")

    status, _ = request(admin, "/wp-admin/options.php", defaults)
    check(status == 200, "Default settings restore successfully")
    _, front = request(session(), "/")
    check('<span class="rtio-cr-band">R.I.P. ERIC</span>' in front,
          "Default ribbon is non-interactive text")
    _, feed = request(session(), "/?feed=rss2")
    check('id="rtio-corner-ribbon"' not in feed, "Feeds contain no ribbon")
    print(f"PASS: {checks} real HTTP checks")
finally:
    request(admin, "/wp-admin/options.php", defaults)
