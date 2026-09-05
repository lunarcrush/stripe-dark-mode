# Privacy Policy — Dark Mode for Stripe Dashboard by LunarCrush

Effective 2026-09-04.

**The extension collects no data.** It has no analytics, makes no network requests, has no account system, and never sends anything to LunarCrush.

## What it does
It injects a stylesheet and a small script into pages on `dashboard.stripe.com` (and Stripe-hosted frames embedded in those pages) to render them with a dark theme. To do that, the script looks at the computed background color and size of page elements so regions Stripe already renders dark can be left alone. It does not read the text of the page, your data, or your account. It stores nothing from the page and transmits nothing. The one page-derived output is the diagnostics report described below, which exists only when you click the button and only on your clipboard.

## What it stores
Your theme settings (on/off, intensity, brightness, contrast, keep-images, developer mode) are saved with your browser's extension storage (`chrome.storage.sync`). If you have browser sync turned on, your browser copies those settings between your own devices through your browser account, which is the only way any setting leaves this device; LunarCrush never receives them. A single on/off flag is also cached in the page's `localStorage` on `dashboard.stripe.com` so the theme applies without a white flash on load.

## Diagnostics
Only when you click **Copy report** in the popup, the extension builds a text report (extension version, your settings, a route template made only of known Dashboard section names with every id or other segment replaced by "…", the viewport size, and a tally of how many elements use each color) and copies it to your clipboard. Nothing is sent anywhere; you decide whether to paste it into an email to us.

## Permissions
- `storage`: save your settings.
- Host access to `dashboard.stripe.com` and `*.stripe.com`: needed to apply the theme to the Dashboard and the Stripe frames it embeds. The script exits immediately on any stripe.com page that is not the Dashboard or embedded in it.

## Third parties
None. No third-party code, SDKs, or services run inside the extension.

## Changes
Changes to this policy ship with a new extension version and are noted in the CHANGELOG.

## Contact
LunarCrush, Inc. · support@lunarcrush.com · https://lunarcrush.com

Not affiliated with or endorsed by Stripe, Inc.
