# Release runbook

## Cut a version
1. Bump `version` in `manifest.json` (SemVer). Bump `@version` in `stripe-dark-mode.user.css` if the theme changed.
2. Move the `Unreleased` CHANGELOG entries under `## [x.y.z] - YYYY-MM-DD`.
3. If the popup or the look changed: `python3 store/tools/capture.py` and commit `store/assets/`.
4. Commit, then tag and push: `git tag v<x.y.z> && git push origin main --tags`.
5. The **release** workflow builds both zips, runs the smoke test against the packaged Chrome build, verifies the tag matches the manifest, and publishes a GitHub Release with `stripe-dark-mode-chrome-v<x.y.z>.zip`, `stripe-dark-mode-firefox-v<x.y.z>.zip` and `SHA256SUMS`.

## Chrome Web Store
1. Sign in to the developer console with the LunarCrush publisher account (which account, and the group-publisher setup, are documented internally).
2. New item → upload the chrome zip from the GitHub Release → fill the listing from `store/LISTING.md` (paste-ready) → upload `store/assets/01…05` screenshots, the 440x280 small tile and the 1400x560 marquee → Privacy tab: single purpose, permission justifications, "does not collect user data", privacy policy URL (this repository's PRIVACY.md).
3. Submit for review. Storage-only extensions with a single-domain host scope typically clear in 1–3 days.
4. Updates: upload the new zip on the existing item; the version must be higher than the published one.
5. The extension is free. There is no paid tier.

## Firefox Add-ons (AMO) and Edge Add-ons
- AMO: https://addons.mozilla.org/developers/ → Submit → upload the firefox zip. Source is unminified, no source package needed. Free.
- Edge: https://partner.microsoft.com/dashboard/microsoftedge → upload the chrome zip. Free.

## Chrome Web Store API (optional automation)
`.github/workflows/publish-cws.yml` uploads and publishes the built chrome zip via the CWS API when the repository secrets `CWS_EXTENSION_ID`, `CWS_CLIENT_ID`, `CWS_CLIENT_SECRET` and `CWS_REFRESH_TOKEN` exist (see https://developer.chrome.com/docs/webstore/using-api). Until then the workflow is dispatch-only and fails fast at the token step.

## Rollback
The stores do not roll back. Bump the patch version, revert the change, release again.
