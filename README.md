# RTIO Corner Ribbon

A WordPress plugin that adds a diagonal tribute ribbon to the top-left corner of your site. It starts with “R.I.P. ERIC” in mint green on black. You can change the wording, link, and colors.

## Install

Requires WordPress 6.0+ and PHP 7.4+.

Clone or download this repository, then build the plugin ZIP:

```sh
python3 scripts/build.py
```

In WordPress, go to Plugins → Add New Plugin → Upload Plugin, upload `dist/rtio-corner-ribbon.zip`, and activate it. Choose “Replace current with uploaded” when updating an existing copy.

Open Settings → Corner Ribbon to edit the message (up to 24 characters), choose colors, add a link, or turn the ribbon off. Clear your page cache after changes if needed.

If you're upgrading from Corner Ribbon 1.1.0 or 1.1.1, deactivate the old copy before installing this one. Keep the old copy installed, because deleting it also deletes the settings used by the new plugin.

Read the [plugin notes](corner-ribbon/readme.txt) for compatibility and uninstall details. For development, see the [test instructions](tests/README.md) and [release guide](docs/releasing.md).

Licensed under [GPL-2.0-or-later](LICENSE). Copyright (C) 2026 Rafael Meneses.
