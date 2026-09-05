# Contributing

- One manifest (`manifest.json`); `build.sh` derives the per-browser variants. Never hand-edit files under `dist/`.
- Every user-visible change gets a CHANGELOG entry under an `Unreleased` heading; the release cuts it into a version.
- Before opening a PR: `bash build.sh && python3 tests/smoke.py --ext dist/build/chrome` must pass. CI runs the same.
- Theme changes: audit on the live Dashboard with the unpacked install (`?sdm-dev=1` hot-reloads `theme.css`). Regenerate store assets only when the popup or the look changes (`python3 store/tools/capture.py`).
- Brand: the extension has its own mark (`icons/icon.svg`); LunarCrush appears only as the maker (wordmark in the popup footer and tiles). Popup colors and type follow the LunarCrush design system (green `#14B881`, blue `#6EA6F8`, canvas `#0B121E`, Plus Jakarta Sans). The retired purple palette is not used anywhere.
- No new permissions, hosts, or network calls without a design discussion. See SECURITY.md.
