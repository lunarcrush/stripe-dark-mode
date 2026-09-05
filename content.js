// Dark Mode for Stripe Dashboard by LunarCrush — content.js (runs at document_start in every stripe.com frame)
(() => {
  const DASH = "https://dashboard.stripe.com";
  const isTop = window.top === window;

  // Activate only on the Dashboard itself, or inside frames embedded in it.
  const inDashboardFrame = () => {
    if (isTop) return location.origin === DASH;
    try {
      const anc = location.ancestorOrigins; // Chromium
      if (anc && anc.length) return Array.from(anc).includes(DASH);
    } catch (_) {}
    try { return new URL(document.referrer).origin === DASH; } catch (_) { return false; } // Firefox fallback: exact origin only
  };
  if (!inDashboardFrame()) return;

  const DEFAULTS = { enabled: true, invert: 0.92, brightness: 1, contrast: 1, keepImages: true };
  const html = document.documentElement;
  const CACHE_KEY = "sdm:enabled";

  const apply = (s) => {
    // Top document: full inversion. Embedded Stripe frames are already inverted by the top document's root filter, so a
    // frame instance applies NO root filter of its own (that would double-invert to light) and only restores its media.
    html.setAttribute("data-sdm", s.enabled ? (isTop ? "on" : "frame") : "off");
    html.style.setProperty("--sdm-invert", String(s.invert));
    html.style.setProperty("--sdm-brightness", String(s.brightness));
    html.style.setProperty("--sdm-contrast", String(s.contrast));
    html.style.setProperty("--sdm-media-invert", s.keepImages ? "1" : "0");
    if (isTop) { try { localStorage.setItem(CACHE_KEY, s.enabled ? "1" : "0"); } catch (_) {} }
  };

  // Paint immediately from the synchronous cache to avoid a white flash, then reconcile with synced settings.
  let cached = null;
  if (isTop) { try { cached = localStorage.getItem(CACHE_KEY); } catch (_) {} }
  apply({ ...DEFAULTS, enabled: cached === null ? true : cached === "1" });

  chrome.storage.sync.get(DEFAULTS, (s) => apply({ ...DEFAULTS, ...s }));
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== "sync") return;
    chrome.storage.sync.get(DEFAULTS, (s) => apply({ ...DEFAULTS, ...s }));
  });

  // Natively dark regions (Workbench, code panels, dark modals) would be flipped light by the root
  // inversion. Filters do not change computed styles, so we can detect them by their real colors
  // and tag the OUTERMOST such region; theme.css re-inverts tagged regions back to native.
  const NATIVE = "data-sdm-native";
  const MIN_AREA = 40000; // ~200x200 px; ignores badges, tooltips, buttons
  const lum = (rgb) => {
    const m = rgb.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?/);
    if (!m) return null; if (m[4] !== undefined && Number(m[4]) < 0.9) return null;
    return (0.2126 * m[1] + 0.7152 * m[2] + 0.0722 * m[3]) / 255;
  };
  let scanQueued = false, lastScan = 0;
  const SCAN_MIN_INTERVAL = 400; // ms; Stripe's SPA mutates constantly, so cap the work
  const scan = () => {
    scanQueued = false;
    if (html.getAttribute("data-sdm") !== "on" || !document.body || document.hidden) return;
    lastScan = performance.now();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    let el;
    while ((el = walker.nextNode())) {
      if (el.parentElement && el.parentElement.closest(`[${NATIVE}]`)) continue; // inside a tagged region; the element itself is re-evaluated so it can be untagged
      if (/^(IMG|VIDEO|CANVAS|SVG|IFRAME|SCRIPT|STYLE)$/.test(el.tagName)) continue;
      if (!el.offsetParent && el.tagName !== "BODY" && getComputedStyle(el).position !== "fixed") continue; // display:none subtrees
      const r = el.getBoundingClientRect(); if (r.width * r.height < MIN_AREA) continue;
      const L = lum(getComputedStyle(el).backgroundColor); if (L === null) continue;
      if (L < 0.25) el.setAttribute(NATIVE, ""); else if (el.hasAttribute(NATIVE)) el.removeAttribute(NATIVE);
    }
  };
  const queueScan = () => {
    if (scanQueued) return;
    scanQueued = true;
    const wait = Math.max(50, SCAN_MIN_INTERVAL - (performance.now() - lastScan));
    setTimeout(() => requestAnimationFrame(scan), wait);
  };
  document.addEventListener("visibilitychange", () => { if (!document.hidden) queueScan(); });
  const startObserver = () => {
    if (!document.body) return;
    scan();
    new MutationObserver(queueScan).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ["class", "style"] });
  };
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", startObserver) : startObserver();

  // Unpacked installs only: ?sdm-dev=1|0 toggles developer mode, ?sdm-reload=1 reloads the extension.
  if (isTop && !chrome.runtime.getManifest().update_url) {
    const q = new URLSearchParams(location.search);
    if (q.has("sdm-dev")) chrome.storage.sync.set({ dev: q.get("sdm-dev") !== "0" });
    if (q.has("sdm-enabled")) chrome.storage.sync.set({ enabled: q.get("sdm-enabled") !== "0" });
    if (q.has("sdm-reload")) chrome.runtime.sendMessage({ type: "sdm:reload" }, () => void chrome.runtime.lastError);
  }

  // Dev hot-reload: when settings.dev is on, the background worker serves theme.css fresh from disk on
  // every page load, so CSS edits to an unpacked install apply on refresh without reloading the extension.
  chrome.storage.sync.get({ dev: false }, ({ dev }) => {
    if (!dev) return;
    if (isTop) chrome.storage.local.get("sdmBoot", ({ sdmBoot }) => { if (sdmBoot) html.dataset.sdmBoot = String(sdmBoot); });
    chrome.runtime.sendMessage({ type: "sdm:theme-css" }, (css) => {
      if (chrome.runtime.lastError || !css) return;
      const st = document.createElement("style"); st.id = "sdm-dev-theme"; st.textContent = css;
      (document.head || html).appendChild(st);
    });
  });

  // Route template for diagnostics: only well-known Dashboard section names survive; every other path segment
  // (account ids, customer/payment/session ids, search terms, anything unexpected) is replaced with "…".
  const ROUTE_WORDS = new Set(["dashboard","test","sandbox","live","home","overview","payments","customers","balance","balances","transactions","payouts","subscriptions","invoices","products","product","prices","coupons","quotes","reports","settings","developers","workbench","logs","events","webhooks","apikeys","connect","accounts","billing","radar","rules","terminal","issuing","cards","cardholders","tax","identity","disputes","refunds","payment-links","checkout","search","notifications","apps","capital","financial-connections","reviews","topups","transfers","orders","climate","catalog"]);
  const routeTemplate = (p) => "/" + p.split("/").filter(Boolean).map((seg) => ROUTE_WORDS.has(seg.toLowerCase()) ? seg.toLowerCase() : "…").join("/");

  // Diagnostics ("Copy report" in the popup, user-initiated only): version, settings, a route with every Stripe object id
  // masked, viewport, and a tally of the page's colors. Nothing is transmitted; the report goes to the clipboard.
  chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
    if (msg?.type !== "sdm:diagnostics" || !isTop) return;
    const bg = new Map(), fg = new Map();
    const els = document.querySelectorAll("body *");
    const n = Math.min(els.length, 6000);
    for (let i = 0; i < n; i++) {
      const cs = getComputedStyle(els[i]);
      const b = cs.backgroundColor, c = cs.color;
      if (b && b !== "rgba(0, 0, 0, 0)" && b !== "transparent") bg.set(b, (bg.get(b) || 0) + 1);
      if (c) fg.set(c, (fg.get(c) || 0) + 1);
    }
    const top = (m) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 40);
    const natives = [...document.querySelectorAll(`[${NATIVE}]`)].slice(0, 12).map(e => {
      const r = e.getBoundingClientRect();
      return { tag: e.tagName.toLowerCase(), size: `${Math.round(r.width)}x${Math.round(r.height)}`, bg: getComputedStyle(e).backgroundColor };
    });
    reply({
      route: routeTemplate(location.pathname), // allowlisted Dashboard section names only; ids and unknown segments become "…"; no query string
      viewport: `${innerWidth}x${innerHeight}`, theme: html.getAttribute("data-sdm"),
      natives, sampled: n, totalElements: els.length,
      backgrounds: top(bg), foregrounds: top(fg),
      version: chrome.runtime.getManifest().version
    });
    return true;
  });
})();
