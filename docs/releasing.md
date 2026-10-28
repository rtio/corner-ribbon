# Releasing Corner Ribbon

The [Test and release workflow](../.github/workflows/release.yml) validates the plugin on pushes to `main`, pull requests, manual runs, and GitHub releases. It builds the installable ZIP, installs it in disposable WordPress with MySQL, and runs the behavior tests and Plugin Check. The tested ZIP is available as the `rtio-corner-ribbon` workflow artifact for 14 days.

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
4. Check the workflow's **Publish to WordPress.org** job. It publishes SVN `trunk`, `tags/X.Y.Z`, and the directory artwork in one commit, then compares the published tag and artwork with the release files. WordPress.org may take time to refresh its public listing.

Keep directory banners and icons in `.wordpress-org`, using the [required filenames and dimensions](https://developer.wordpress.org/plugins/wordpress-org/plugin-assets/). The workflow publishes that folder to SVN `assets`; these images stay out of the installable ZIP. See the [artwork notes](artwork.md) for the original prompts.

Version disagreement, Plugin Check findings, unexpected package files, and an existing or newer SVN version stop publication. Correct a failure before the SVN commit and rerun the release workflow. If SVN already contains the version, inspect it first; the workflow deliberately refuses to overwrite it. Publish a new version for corrections. Manual **Run workflow** only validates; releases published before setup are not submitted retroactively. Set `WORDPRESS_ORG_APPROVED=false` to disable future deployments.
