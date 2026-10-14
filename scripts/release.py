#!/usr/bin/env python3
# Copyright (C) 2026 Rafael Meneses
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate a release before any publishing credentials are used."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from build import FILES, ROOT

SLUG = "rtio-corner-ribbon"
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"


def header(text, key):
    matches = re.findall(r"^[ \t]*(?:\* )?" + re.escape(key) + r":[ \t]*(.+?)[ \t]*$", text, re.M)
    if len(matches) != 1:
        raise ValueError("Expected one " + key + " header")
    return matches[0]


def validate_source(root, tag=None):
    plugin = root.resolve() / "corner-ribbon"
    for name in FILES:
        file = plugin / name
        if not file.is_file() or file.is_symlink() or file.resolve() != file.absolute():
            raise ValueError("Missing or symlinked release file: " + name)
    main = (plugin / "corner-ribbon.php").read_text()
    readme = (plugin / "readme.txt").read_text()
    version = header(main, "Version")
    if not re.fullmatch(VERSION, version):
        raise ValueError("Use a stable X.Y.Z plugin version")
    if header(readme, "Stable tag") != version:
        raise ValueError("Version and Stable tag must match")
    if header(main, "Text Domain") != SLUG:
        raise ValueError("Text Domain must match " + SLUG)
    if tag is not None and (not re.fullmatch("v" + VERSION, tag) or tag != "v" + version):
        raise ValueError("Release tag must be v" + version)
    return version


def validate_archive(root, archive):
    validate_source(root)
    with zipfile.ZipFile(archive) as package:
        expected = {SLUG + "/" + name for name in FILES}
        if set(package.namelist()) != expected or len(package.namelist()) != len(expected):
            raise ValueError("ZIP must contain exactly the allowed plugin files")
        for name in FILES:
            if package.read(SLUG + "/" + name) != (root / "corner-ribbon" / name).read_bytes():
                raise ValueError("ZIP differs from checked source: " + name)


def validate_svn_version(version, xml):
    if not re.fullmatch(VERSION, version):
        raise ValueError("Use a stable X.Y.Z release version")
    try:
        listing = ET.fromstring(xml)
    except ET.ParseError as error:
        raise ValueError("Invalid SVN listing") from error
    if listing.tag != "lists" or len(listing.findall("list")) != 1:
        raise ValueError("Unexpected SVN listing; deployment stopped")
    current = tuple(map(int, version.split(".")))
    for entry in listing.findall("list/entry"):
        name = entry.findtext("name", "")
        if entry.get("kind") != "dir" or not re.fullmatch(VERSION, name):
            raise ValueError("Unexpected SVN tag: " + name)
        if tuple(map(int, name.split("."))) >= current:
            raise ValueError("SVN already contains this or a newer version: " + name)


def validate_plugin_check(output):
    if output.strip() == "Success: Checks complete. No errors found.":
        return
    try:
        findings = json.loads(output)
    except json.JSONDecodeError as error:
        raise ValueError("Unexpected Plugin Check output") from error
    if findings != []:
        raise ValueError("Plugin Check findings must be resolved before release")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--svn-list", type=Path)
    parser.add_argument("--plugin-check", type=Path)
    args = parser.parse_args()
    try:
        version = validate_source(ROOT, args.tag)
        if args.archive:
            validate_archive(ROOT, args.archive)
        if args.svn_list:
            validate_svn_version(version, args.svn_list.read_text())
        if args.plugin_check:
            validate_plugin_check(args.plugin_check.read_text())
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, str(error) + "\n")
    print(version)


if __name__ == "__main__":
    main()
