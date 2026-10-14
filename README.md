# RTIO Corner Ribbon

A small WordPress plugin for an editable diagonal tribute ribbon. Set the full message, an optional link, text/border color, background color, and visibility in **Settings → Corner Ribbon**.

The default is **R.I.P. ERIC** in mint green on black. The ribbon sits in the upper-left corner, scrolls with the page, and leaves space above the header on smaller screens. It supports the WordPress admin bar and keyboard focus for linked ribbons.

## Install

Download or clone this repository, then build the installable ZIP:

```sh
python3 scripts/build.py
```

In WordPress, open **Plugins → Add New Plugin → Upload Plugin**, upload `dist/rtio-corner-ribbon.zip`, and activate it. To update an installed RTIO Corner Ribbon copy, select **Replace current with uploaded**. If upgrading the original GitHub-only Corner Ribbon 1.1.0/1.1.1, deactivate it before installing this directory release. Both use the same saved settings. Keep the old copy inactive; deleting it runs its uninstaller and removes the shared settings. GitHub's source ZIP contains the whole repository; use the built plugin ZIP for installation.

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

## Release to WordPress.org

The [Test and release workflow](.github/workflows/release.yml) validates the plugin on pushes to `main`, pull requests, manual runs, and GitHub releases. It builds the installable ZIP, installs it in disposable WordPress with MySQL, and runs the behavior tests and Plugin Check. The tested ZIP is available as the `rtio-corner-ribbon` workflow artifact for 14 days.

Publishing a **stable GitHub release** also publishes that exact package to WordPress.org once the approval gate is enabled. A tag push alone does not publish. Drafts, prereleases, branch pushes, and manual validation runs never deploy. The workflow uses read-only GitHub permissions; SVN credentials are available only to the deployment action.

### One-time setup after directory approval

1. Confirm WordPress.org has approved the plugin with the slug `rtio-corner-ribbon` and granted your account SVN access. If review changes the slug, update the package and workflow before enabling deployment.
2. Generate an [SVN-specific password in your WordPress.org profile](https://profiles.wordpress.org/me/profile/edit/group/3/?screen=svn-password). This is separate from your WordPress.org login password.
3. In the repository's [Environments settings](https://github.com/rtio/corner-ribbon/settings/environments), open `wordpress-org`. Set the environment variable `SVN_USERNAME` to your WordPress.org committer username and add the environment secret `SVN_PASSWORD`. Keep the environment restricted to `v*` tags. Do not put the password in source files, release notes, or workflow logs.
4. Set the repository Actions variable `WORDPRESS_ORG_APPROVED` to `true` in [Actions variables](https://github.com/rtio/corner-ribbon/settings/variables/actions). Leave it `false` until approval and credentials are ready.

### Each release

1. Update `Version` in `corner-ribbon/corner-ribbon.php`, `Stable tag` and the changelog in `corner-ribbon/readme.txt`, and any changed asset versions. Use a stable `X.Y.Z` version greater than all existing SVN tags.
2. Merge or push the changes to `main` and wait for the checks to pass.
3. [Publish a GitHub release](https://github.com/rtio/corner-ribbon/releases/new) with the matching `vX.Y.Z` tag targeting that commit on `main`. Leave **Set as a pre-release** unchecked.
4. Check the workflow's **Publish to WordPress.org** job. It publishes SVN `trunk` and `tags/X.Y.Z` in one commit, then compares the published tag with the tested package. WordPress.org may take time to refresh its public listing.

Version disagreement, Plugin Check findings, unexpected package files, and an existing or newer SVN version stop publication. Correct a failure before the SVN commit and rerun the release workflow. If SVN already contains the version, inspect it first; the workflow deliberately refuses to overwrite it. Publish a new version for corrections. Manual **Run workflow** only validates; releases published before setup are not submitted retroactively. Set `WORDPRESS_ORG_APPROVED=false` to disable future deployments.

## License

Copyright (C) 2026 Rafael Meneses.

Licensed under the **GNU General Public License, version 2 or any later version** (`GPL-2.0-or-later`). See [LICENSE](LICENSE). The plugin archive includes the same license. Distributed without warranty.
