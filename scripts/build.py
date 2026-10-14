#!/usr/bin/env python3
# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build a deterministic installable ZIP containing only plugin release files."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "LICENSE",
    "corner-ribbon.php",
    "includes/settings.php",
    "assets/ribbon.css",
    "assets/settings.js",
    "readme.txt",
    "uninstall.php",
)


def build():
    destination = ROOT / "dist" / "corner-ribbon.zip"
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            entry = zipfile.ZipInfo("corner-ribbon/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, (ROOT / "corner-ribbon" / name).read_bytes())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Archive integrity verification failed")
    print("Built dist/corner-ribbon.zip")


if __name__ == "__main__":
    build()
