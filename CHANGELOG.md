# Changelog

All notable changes to this project are documented here. Versions follow [SemVer](https://semver.org); the `version` in `manifest.json` is the source of truth and every release is tagged `v<version>`.

## [1.0.2] - 2026-09-04
- Icon recolored into a palette that belongs in Stripe's world (pale lavender / deep navy, blurple crescent) while keeping the extension's own inverted-crescent mark. No Stripe logo or wordmark is used.

## [1.0.1] - 2026-09-04
- The extension has its own mark: a crescent that inverts across a light/dark split (`icons/icon.svg`), replacing the LunarCrush mark in the toolbar icon, popup header, store icon and promo tiles. LunarCrush appears only as the maker ("Made by LunarCrush" wordmark in the popup footer and tiles).

## [1.0.0] - 2026-09-04
First store release. Made by LunarCrush.
- Support contact is support@lunarcrush.com: privacy policy, security policy, store listing, and the popup's "Send feedback" link (opens a pre-addressed email).
- LunarCrush branding: popup rebuilt on the LunarCrush marketing system (near-black canvas, green primary, blue links, Plus Jakarta Sans bundled), "Made by LunarCrush" footer, new icons (white LunarCrush mark on the brand canvas), extension renamed "Dark Mode for Stripe Dashboard by LunarCrush".
- Store package: five 1280x800 screenshots, 440x280 and 1400x560 promo tiles, all rendered from a synthetic Stripe-style Dashboard mock with invented data (`store/mock/`), captured through the real extension.
- Build now emits browser-clean variants (Chrome/Brave/Edge: service worker only; Firefox: background scripts + gecko id) plus SHA256SUMS.
- CI: manifest checks, build, Chromium smoke test against the mock, zips as artifacts; tag push creates a GitHub Release with the zips.
- Popup shows the installed version; the developer hot-reload switch is hidden in store builds.
- Diagnostics report exports an id-free route template (known section names only), drops the query string, browser identity and CSS variables. Frame-origin check compares exact origins.
- Embedded Stripe frames no longer double-invert: a frame instance restores media only and applies no root filter. Native-dark regions can be untagged again when they turn light. LICENSE ships inside the packages.

## [0.1.5] - 2026-09-03
- Native-dark region detector: Workbench, code panels and dark modals are detected by their real background color and re-inverted back to native.
- Sandbox banner and Workbench rendering fixes found in visual QA across ~35 Dashboard surfaces.

## [0.1.4] - 2026-09-03
- "Send feedback" link (hidden until a URL is configured) and "Copy report" diagnostics with account ids redacted.

## [0.1.3] - 2026-09-03
- Production hardening: frame gating (Dashboard origin or frames embedded in it only), no white flash on load (synchronous cache), print never inverts, iframe double-inversion fix, mutation scanning capped to avoid load on Stripe's SPA.

## [0.1.0] - 2026-09-03
- Initial build: luminance inversion with hue preservation, image and avatar restoration, toggle, intensity/brightness/contrast sliders synced via `chrome.storage.sync`, `Alt+Shift+D` shortcut, unpacked-only dev switches, Stylus UserCSS variant.
