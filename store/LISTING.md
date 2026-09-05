# Chrome Web Store listing — Dark Mode for Stripe Dashboard by LunarCrush

Everything below is paste-ready for the developer console. Screenshots and tiles are in `store/assets/` (regenerate with `python3 store/tools/capture.py`). All screenshot content is synthetic: an invented business, invented people, invented numbers, rendered from `store/mock/index.html` through the real extension. No real Stripe account, page, or data was used.

## Name (45 max)
Dark Mode for Stripe Dashboard by LunarCrush

## Summary (132 max; also the manifest `description`)
Dark mode for dashboard.stripe.com. One-click toggle, tunable intensity, images keep true color, zero tracking. Made by LunarCrush.

## Description
```
Stripe's web Dashboard never got a dark mode. This gives it one.

Flip it on and dashboard.stripe.com turns into a proper dark workspace: deep charcoal surfaces, readable text, and every brand color exactly where Stripe put it. Charts keep their hues. Customer photos and avatars are restored to their true colors. Status badges still read green, amber and red. It looks like Stripe designed it, because nothing about the layout changes, only the light.

WHY IT FEELS NATIVE
Most page darkeners guess at colors and break on the next redesign. This one flips luminance while preserving hue, then restores photographic media to true color. It is built to survive Dashboard redesigns, and regions Stripe already renders dark (Workbench, code panels, dark modals) are detected and left exactly as they are.

WHAT YOU GET
• One-click toggle from the toolbar, or press Alt+Shift+D
• Intensity, brightness and contrast sliders, synced across your browsers
• Photos and avatars keep their true colors; charts keep their hues
• Never inverts when printing, so invoices and reports print light
• Runs only on dashboard.stripe.com and the Stripe frames embedded in it
• Nothing to sign up for, nothing to configure

PRIVACY, IN ONE LINE
It collects nothing. No analytics, no network requests, no accounts. Your settings live in your browser's extension storage and never reach us. Read the full policy at the link below.

MADE BY LUNARCRUSH
Built by the LunarCrush team, who spend their days in the Stripe Dashboard and wanted it to match the rest of their dark desks. Free to use.

Not affiliated with or endorsed by Stripe, Inc. "Stripe" is a trademark of Stripe, Inc., used here to describe what the extension is for.
```

## Category
Productivity (Chrome Web Store) · Appearance (Firefox Add-ons)

## Language
English (United States)

## Store assets (`store/assets/`)
| File | Size | Use |
|---|---|---|
| `01-dashboard-dark.png` | 1280×800 | Screenshot 1: Dashboard home, dark |
| `02-before-after.png` | 1280×800 | Screenshot 2: light / dark split |
| `03-payments-dark.png` | 1280×800 | Screenshot 3: Payments list, dark |
| `04-customer-popup.png` | 1280×800 | Screenshot 4: customer page with the popup open |
| `05-features.png` | 1280×800 | Screenshot 5: feature card |
| `promo-small-440x280.png` | 440×280 | Small promo tile |
| `promo-marquee-1400x560.png` | 1400×560 | Marquee promo tile |
| `icon-128.png` | 128×128 | Store icon (same as `icons/icon128.png`) |
| `popup-320.png` | 320×389 | Popup, for docs and social |

Screenshots are 24-bit PNG without alpha, as the store requires. The mock merchant is "Acme Demo Roasters"; every person, card and figure is invented, a dashed "Synthetic demo data" chip is visible in the top bar of every page, and no card-network or Stripe marks appear.

## Privacy tab
- **Single purpose:** Apply a dark color theme to the Stripe Dashboard (dashboard.stripe.com).
- **storage:** Persist the user's theme settings (enabled, intensity, brightness, contrast, keep-images, developer mode) and sync them across the user's browsers.
- **Host permission (dashboard.stripe.com, *.stripe.com):** Required to inject the theme stylesheet into the Dashboard and the Stripe-hosted frames it embeds (invoice and checkout previews). The content script exits immediately on any stripe.com page that is not the Dashboard or embedded in it.
- **Remote code:** No.
- **Data use:** Does not collect or use user data. Nothing is transmitted off the device. The popup's user-initiated "Copy report" writes a local diagnostics summary (version, settings, an id-free route template, viewport, color counts) to the user's own clipboard and nowhere else. Not sold, not used for unrelated purposes, not used for creditworthiness.
- **Privacy policy URL:** this repository's `PRIVACY.md` (public).
- **Support email:** support@lunarcrush.com (also the contact in PRIVACY.md and SECURITY.md, and the popup's "Send feedback" link).

## Publisher
Display name **LunarCrush** · homepage https://lunarcrush.com · support support@lunarcrush.com · free, no paid tier. Account details are documented internally.

## Trademark note
"Stripe" appears descriptively ("for Stripe Dashboard"), the same way the existing third-party dark-mode extensions are named. The description carries the not-affiliated line. The icon, tiles and screenshots contain no Stripe logo or wordmark and no card-network marks; the mock business is "Acme Demo Roasters" with example.com customers and a visible synthetic-data chip on every page.
