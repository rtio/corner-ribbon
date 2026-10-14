# Corner Ribbon

A small WordPress plugin for an editable diagonal tribute ribbon. Set the full message, an optional link, text/border color, background color, and visibility in **Settings → Corner Ribbon**.

The default is **R.I.P. ERIC** in mint green on black. The ribbon sits in the upper-left corner, scrolls with the page, and leaves space above the header on smaller screens. It supports the WordPress admin bar and keyboard focus for linked ribbons.

## Install

Download or clone this repository, then build the installable ZIP:

```sh
python3 scripts/build.py
```

In WordPress, open **Plugins → Add New Plugin → Upload Plugin**, upload `dist/corner-ribbon.zip`, and activate it. To update an installed copy, select **Replace current with uploaded**. GitHub's source ZIP contains the whole repository; use the built plugin ZIP for installation.

Requires WordPress 6.0+ and PHP 7.4+. Tested with WordPress 7.0.4 and 7.1.3, PHP 8.4.17, and the Beep theme.

## Configure

- **Name or message:** full wording, up to 24 characters. Leave blank to hide the ribbon.
- **Link URL:** optional HTTP/HTTPS address. Clear it for a ribbon without a link.
- **Colors:** use the WordPress color pickers or enter three- or six-digit hex values. Text and border share one color.
- **Visibility:** turn the ribbon on or off without deactivating the plugin.

The frontend uses CSS with no JavaScript, remote services, tracking, or theme edits. Color-picker JavaScript loads only on the settings screen. Clear any page cache after changing settings.

Deactivation preserves settings. Deleting the plugin removes its option for the current site; on multisite, remove other sites' settings before network deletion if needed. Themes with unusual body positioning or their own body pseudo-elements may need a CSS adjustment.

## Development

The `corner-ribbon/` directory contains the installable plugin. `tests/` contains real WordPress integration and HTTP regression checks. Python uses only its standard library; no npm dependencies or frontend build are required.

See [test instructions](tests/README.md) for setup and commands. Tests cover editable-field persistence, rendered text/URLs/colors, validation, Unicode, visibility, nonce checks, permissions, and asset isolation. Run them only against a disposable localhost installation.

## License

Copyright (C) 2026 Rafael Meneses.

Licensed under the **GNU General Public License, version 2 or any later version** (`GPL-2.0-or-later`). See [LICENSE](LICENSE). The plugin archive includes the same license. Distributed without warranty.
