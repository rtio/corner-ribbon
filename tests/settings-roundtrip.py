# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
"""Regression tests against a disposable WordPress site, using real form submissions."""
from html.parser import HTMLParser
import http.cookiejar
import os
from pathlib import Path
import unittest
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ["RIBBON_TEST_URL"].rstrip("/")
ADMIN = os.environ.get("RIBBON_ADMIN_USER", "qa-ribbon")
PASSWORD_FILE = Path(os.environ["RIBBON_ADMIN_PASSWORD_FILE"])
SETTINGS = "/wp-admin/options-general.php?page=corner-ribbon"
DEFAULTS = {"enabled": "1", "text": "R.I.P. ERIC", "accent": "#00e49a", "background": "#000000", "url": ""}


class Page(HTMLParser):
    """Inspect parsed form/ribbon values rather than matching unrelated page text."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.inputs, self.labels = {}, {}
        self.ribbon, self.band = None, None
        self.ribbon_count, self.band_text = 0, ""
        self.scripts, self.styles = [], []
        self._label, self._in_band = None, False
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "input" and "name" in attrs:
            self.inputs[attrs["name"]] = attrs
        if tag == "label":
            self._label = attrs.get("for")
        if attrs.get("id") == "rtio-corner-ribbon":
            self.ribbon_count += 1
            self.ribbon = attrs
        if "rtio-cr-band" in attrs.get("class", "").split():
            self.band = {"tag": tag, **attrs}
            self._in_band = True
        if tag == "script" and "src" in attrs:
            self.scripts.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.styles.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "label":
            self._label = None
        if self.band and tag == self.band["tag"]:
            self._in_band = False

    def handle_data(self, data):
        if self._label:
            self.labels[self._label] = self.labels.get(self._label, "") + data
        if self._in_band:
            self.band_text += data

    def setting(self, key):
        field = self.inputs[f"rtio_corner_ribbon[{key}]"]
        return ("checked" in field) if key == "enabled" else field.get("value", "")

    def colors(self):
        return dict(part.strip().split(":", 1) for part in self.ribbon["style"].split(";") if part.strip())


def session():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(client, path, data=None):
    encoded = urllib.parse.urlencode(data).encode() if data is not None else None
    try:
        with client.open(BASE + path, encoded, timeout=15) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


class EditableSettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if urllib.parse.urlsplit(BASE).hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise RuntimeError("These mutating tests require a disposable localhost site")
        cls.admin = session()
        request(cls.admin, "/wp-login.php")
        request(cls.admin, "/wp-login.php", {"log": ADMIN, "pwd": PASSWORD_FILE.read_text().strip(),
                "wp-submit": "Log In", "redirect_to": BASE + "/wp-admin/", "testcookie": "1"})
        status, html = request(cls.admin, SETTINGS)
        if status != 200 or 'id="rtio-cr-text"' not in html:
            raise RuntimeError("Test administrator cannot open settings")
        page = Page(html)
        cls.nonce = page.inputs["_wpnonce"]["value"]
        cls.original = {key: page.setting(key) for key in DEFAULTS}
        cls.original["enabled"] = "1" if cls.original["enabled"] else "0"

    @classmethod
    def tearDownClass(cls):
        if cls.submit(cls.original)[0] != 200:
            raise RuntimeError("Could not restore the test site's original settings")

    @classmethod
    def submit(cls, settings, nonce=None):
        data = {f"rtio_corner_ribbon[{key}]": value for key, value in settings.items()}
        data.update(option_page="rtio_corner_ribbon", action="update")
        if nonce != "omit":
            data["_wpnonce"] = cls.nonce if nonce is None else nonce
        return request(cls.admin, "/wp-admin/options.php", data)

    def setUp(self):
        self.assertEqual(200, self.submit(DEFAULTS)[0])

    def saved(self):
        status, html = request(self.admin, SETTINGS)
        self.assertEqual(200, status)
        return Page(html)

    def frontend(self):
        status, html = request(session(), "/")
        self.assertEqual(200, status)
        return Page(html)

    def save(self, **changes):
        self.assertEqual(200, self.submit({**DEFAULTS, **changes})[0])

    def test_form_exposes_editable_name_url_and_colors(self):
        page = self.saved()
        self.assertEqual("Name or message", page.labels["rtio-cr-text"])
        for key in ("text", "url", "accent", "background"):
            with self.subTest(field=key):
                attrs = page.inputs[f"rtio_corner_ribbon[{key}]"]
                self.assertNotIn("disabled", attrs)
                self.assertNotIn("readonly", attrs)
                self.assertIn("rtio-cr-" + key, page.labels)
        self.assertTrue(any("/color-picker" in src for src in page.scripts))
        self.assertTrue(any("/corner-ribbon/assets/settings.js" in src for src in page.scripts))

    def test_every_field_persists_and_replaces_previous_value(self):
        cases = [
            {"text": 'R.I.P. José & Ana', "url": 'https://example.test/tribute?a=1&b=2#memory', "accent": "#AABBCC", "background": "#123456"},
            {"text": 'Remember "Alex"', "url": 'http://example.test/another', "accent": "#F0A", "background": "#abc"},
        ]
        for values in cases:
            with self.subTest(values=values):
                self.save(**values)
                page, front = self.saved(), self.frontend()
                for key, value in values.items():
                    self.assertEqual(value.lower() if key in {"accent", "background"} else value, page.setting(key), key)
                self.assertEqual(values["text"], front.band_text)
                self.assertEqual(values["url"], front.band["href"])
                self.assertEqual("a", front.band["tag"])
                self.assertEqual(values["accent"].lower(), front.colors()["--rtio-cr-accent"])
                self.assertEqual(values["background"].lower(), front.colors()["--rtio-cr-background"])
                self.assertEqual(1, front.ribbon_count)

    def test_editing_one_field_preserves_the_other_fields(self):
        values = {"text": "R.I.P. Morgan", "url": "https://example.test/remember", "accent": "#abcdef", "background": "#123456"}
        self.save(**values)
        for key, replacement in {"text": "In memory of Sam", "url": "https://example.test/sam", "accent": "#fedcba", "background": "#654321"}.items():
            with self.subTest(field=key):
                values[key] = replacement
                self.save(**values)
                page = self.saved()
                self.assertEqual(values, {name: page.setting(name) for name in values})

    def test_clearing_url_removes_link_but_keeps_message_and_colors(self):
        self.save(url="https://example.test/tribute")
        self.save(url="", text="R.I.P. Casey", accent="#ace", background="#123")
        self.assertEqual("", self.saved().setting("url"))
        front = self.frontend()
        self.assertEqual("span", front.band["tag"])
        self.assertNotIn("href", front.band)
        self.assertEqual("R.I.P. Casey", front.band_text)
        self.assertEqual("#ace", front.colors()["--rtio-cr-accent"])
        self.assertEqual("#123", front.colors()["--rtio-cr-background"])

    def test_unicode_quotes_and_length_boundary(self):
        for text in ("R.I.P. João", 'R.I.P. "Anne" & Bob', "á" * 24, "á" * 30):
            with self.subTest(text=text):
                self.save(text=text)
                self.assertEqual(text[:24], self.saved().setting("text"))
                self.assertEqual(text[:24], self.frontend().band_text)

    def test_blank_name_and_unchecked_visibility_hide_ribbon(self):
        self.save(text="   ")
        self.assertIsNone(self.frontend().ribbon)
        self.assertEqual(200, self.submit({key: value for key, value in DEFAULTS.items() if key != "enabled"})[0])
        self.assertFalse(self.saved().setting("enabled"))
        front = self.frontend()
        self.assertIsNone(front.ribbon)
        self.assertFalse(any("corner-ribbon" in src for src in front.styles))

    def test_invalid_colors_cannot_inject_css(self):
        for value in ("red", "#12", "#abcd", "#12345678", "#fff;display:none", '\"><script>alert(1)</script>'):
            with self.subTest(value=value):
                self.save(accent=value, background=value)
                page, front = self.saved(), self.frontend()
                self.assertEqual(DEFAULTS["accent"], page.setting("accent"))
                self.assertEqual(DEFAULTS["background"], page.setting("background"))
                self.assertEqual({"--rtio-cr-accent": "#00e49a", "--rtio-cr-background": "#000000"}, front.colors())

    def test_unsafe_or_incomplete_urls_are_not_clickable(self):
        for url in ("javascript:alert(1)", "data:text/html,test", "mailto:test@example.test", "//example.test", "/relative", "https://"):
            with self.subTest(url=url):
                self.save(url=url)
                self.assertEqual("", self.saved().setting("url"))
                self.assertEqual("span", self.frontend().band["tag"])

    def test_name_markup_is_stripped(self):
        self.save(text='<b>Eric</b><img src=x onerror=alert(1)>')
        self.assertEqual("Eric", self.saved().setting("text"))
        self.assertEqual("Eric", self.frontend().band_text)

    def test_array_inputs_do_not_crash_or_enable_ribbon(self):
        malformed = {key + "[]": value for key, value in DEFAULTS.items()}
        self.assertEqual(200, self.submit(malformed)[0])
        page = self.saved()
        self.assertFalse(page.setting("enabled"))
        self.assertEqual("", page.setting("text"))
        self.assertEqual("", page.setting("url"))
        self.assertIsNone(self.frontend().ribbon)

    def test_bad_or_missing_nonce_cannot_mutate_settings(self):
        for nonce in ("omit", "invalid-nonce"):
            with self.subTest(nonce=nonce):
                self.assertEqual(403, self.submit({**DEFAULTS, "text": "Unauthorized", "accent": "#fff"}, nonce=nonce)[0])
                page = self.saved()
                for key in ("text", "url", "accent", "background"):
                    self.assertEqual(DEFAULTS[key], page.setting(key))

    def test_color_picker_scripts_do_not_load_on_dashboard_or_frontend(self):
        _, dashboard = request(self.admin, "/wp-admin/index.php")
        for page in (Page(dashboard), self.frontend()):
            self.assertFalse(any("corner-ribbon/assets/settings.js" in src for src in page.scripts))


if __name__ == "__main__":
    unittest.main(verbosity=2)
