=== RTIO Corner Ribbon ===
Contributors: rtiodev
Tags: ribbon, tribute, memorial
Requires at least: 6.0
Tested up to: 7.1
Requires PHP: 7.4
Stable tag: 1.1.2
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

A diagonal corner tribute with editable text, colors, and an optional link.

== Description ==

Shows R.I.P. ERIC in a black upper-left ribbon with mint (#00e49a) text and borders, matching the Beep theme. Uses the site's font. The ribbon scrolls away with the page; small screens gain space above the header.

Change the name/message, colors, optional destination URL, or visibility in Settings > Corner Ribbon. Enter the full wording; R.I.P. is editable too. Short messages work best; labels are limited to 24 characters. A blank label hides the ribbon. Choose colors with the WordPress color pickers or enter three- or six-digit hex values. Links must use HTTP or HTTPS and open in the same tab. Clear the URL to remove the link.

No frontend JavaScript, remote services, tracking, external assets, or theme edits. WordPress's color picker loads only on the plugin's settings screen. Settings are local to each site. Deactivation preserves settings; deleting the plugin removes its option for the current site. On multisite, remove other sites' settings before network deletion if needed.

Source code, tests, and packaging instructions are available on [GitHub](https://github.com/rtio/corner-ribbon). The plugin ships readable PHP, CSS, and JavaScript; no compilation is required.

== Installation ==

1. In WordPress, open Plugins > Add New Plugin > Upload Plugin.
2. Upload rtio-corner-ribbon.zip, install, and activate it.
3. Visit Settings > Corner Ribbon to adjust the ribbon.
4. If the site caches pages, clear the page cache after changing settings or deactivating the plugin.

== Frequently Asked Questions ==

= Does it change my theme? =

No. Deactivate it to remove the ribbon. It uses WordPress's body-open hook with a footer fallback.

= Can it link to a tribute? =

Yes. Set an optional URL in Settings > Corner Ribbon. The link supports keyboard navigation and a visible focus state. Without a URL, the ribbon does not intercept clicks.

= How does it behave on phones? =

It becomes smaller and reserves 72 pixels above the page below 601 pixels wide. Between 601 and 900 pixels it reserves 48 pixels to keep tablet headers clear. It accounts for the standard WordPress admin bar and hides when printing. Themes with unusual body positioning or their own body pseudo-elements may need a CSS adjustment.

== Changelog ==

= 1.1.2 =
Use the distinctive RTIO Corner Ribbon directory name and matching translation domain. Existing ribbon settings are preserved.

= 1.1.1 =
Prepare directory metadata and verify compatibility with WordPress 7.1.3. Ribbon behavior is unchanged.

= 1.1.0 =
Clarify editable name/message and URL fields. Add accessible WordPress color pickers. Expand save/reload, rendering, and validation regression coverage.

= 1.0.0 =
Initial release.
