# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
"""Release checks must reject unsafe or inconsistent publications."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source / "corner-ribbon", self.root / "corner-ribbon")
        self.version = release.validate_source(self.root)

    def change(self, name, old, new):
        file = self.root / "corner-ribbon" / name
        file.write_text(file.read_text().replace(old, new))

    def archive(self, extra=False, changed=False):
        archive = self.root / "plugin.zip"
        with zipfile.ZipFile(archive, "w") as output:
            for name in release.FILES:
                data = (self.root / "corner-ribbon" / name).read_bytes()
                if changed and name == "assets/ribbon.css":
                    data += b"body {display:none}"
                output.writestr("rtio-corner-ribbon/" + name, data)
            if extra:
                output.writestr("rtio-corner-ribbon/.env", "PRIVATE=value")
        return archive

    def test_matching_stable_tag(self):
        self.assertEqual(self.version, release.validate_source(self.root, "v" + self.version))

    def test_wrong_tag_or_prerelease_is_rejected(self):
        for tag in ["v99.99.99", self.version, "v1.2.3-beta", "v01.2.3", "../main", "v1.2.3\n"]:
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.validate_source(self.root, tag)

    def test_readme_version_must_match(self):
        self.change("readme.txt", "Stable tag: " + self.version, "Stable tag: 99.0.0")
        with self.assertRaises(ValueError):
            release.validate_source(self.root)

    def test_slug_must_match(self):
        self.change("corner-ribbon.php", "Text Domain: rtio-corner-ribbon", "Text Domain: other")
        with self.assertRaises(ValueError):
            release.validate_source(self.root)

    def test_missing_duplicate_or_unstable_version_is_rejected(self):
        file = self.root / "corner-ribbon/corner-ribbon.php"
        original = file.read_text()
        version_header = " * Version: " + self.version
        for replacement in ["", " * Version: ", " * Version: 1.2.3-beta", version_header + "\n" + version_header]:
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                file.write_text(original.replace(version_header, replacement))
                release.validate_source(self.root)

    def test_missing_source_file_is_rejected(self):
        (self.root / "corner-ribbon/LICENSE").unlink()
        with self.assertRaises(ValueError):
            release.validate_source(self.root)

    def test_valid_archive(self):
        release.validate_archive(self.root, self.archive())

    def test_extra_or_changed_files_are_rejected(self):
        for values in [{"extra": True}, {"changed": True}]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                release.validate_archive(self.root, self.archive(**values))

    def test_duplicate_zip_entries_are_rejected(self):
        archive = self.archive()
        with self.assertWarns(UserWarning), zipfile.ZipFile(archive, "a") as output:
            output.writestr("rtio-corner-ribbon/readme.txt", "duplicate")
        with self.assertRaises(ValueError):
            release.validate_archive(self.root, archive)

    def test_incomplete_zip_is_rejected(self):
        archive = self.root / "incomplete.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("rtio-corner-ribbon/readme.txt", "incomplete")
        with self.assertRaises(ValueError):
            release.validate_archive(self.root, archive)

    def test_source_symlinks_are_rejected(self):
        file = self.root / "corner-ribbon/assets/ribbon.css"
        file.unlink()
        file.symlink_to(self.root / "corner-ribbon/readme.txt")
        with self.assertRaises(ValueError):
            release.validate_source(self.root)

    def test_first_or_newer_svn_version_is_allowed(self):
        release.validate_svn_version("1.1.2", '<lists><list path="tags"/></lists>')
        release.validate_svn_version("1.10.0", self.svn("1.9.9"))

    def test_overwrite_or_downgrade_is_rejected(self):
        for version in ["1.1.2", "1.1.1", "1.0.99"]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                release.validate_svn_version(version, self.svn("1.1.2"))

    def test_unexpected_svn_output_is_rejected(self):
        for value in ["", "<html/>", self.svn("unknown"), "<lists/>"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                release.validate_svn_version("1.1.2", value)

    def test_plugin_check_success(self):
        release.validate_plugin_check("Success: Checks complete. No errors found.\n")
        release.validate_plugin_check("[]")

    def test_plugin_check_findings_or_unexpected_output_fail(self):
        for result in ['[{"type":"ERROR"}]', '[{"type":"WARNING"}]', "", "null", "{}", "Fatal error", "[] trailing"]:
            with self.subTest(result=result), self.assertRaises(ValueError):
                release.validate_plugin_check(result)

    @staticmethod
    def svn(version):
        return '<lists><list path="tags"><entry kind="dir"><name>' + version + '</name></entry></list></lists>'


if __name__ == "__main__":
    unittest.main()
