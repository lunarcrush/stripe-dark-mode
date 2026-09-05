// Dark Mode for Stripe Dashboard by LunarCrush — background (MV3 service worker / Firefox background script)
const DEFAULTS = { enabled: true, invert: 0.92, brightness: 1, contrast: 1, keepImages: true, dev: false };

const setBadge = (enabled) => {
  chrome.action.setBadgeText({ text: enabled ? "" : "off" });
  chrome.action.setBadgeBackgroundColor({ color: "#6B7290" }); // LunarCrush muted
};

chrome.runtime.onInstalled.addListener(() => {
  // Fill only the keys that are missing; never overwrite settings that already exist.
  chrome.storage.sync.get(null, (s) => {
    const missing = Object.fromEntries(Object.entries(DEFAULTS).filter(([k]) => !(k in s)));
    if (Object.keys(missing).length) chrome.storage.sync.set(missing);
    setBadge(s.enabled ?? true);
  });
});

chrome.commands.onCommand.addListener((cmd) => {
  if (cmd !== "toggle-dark") return;
  chrome.storage.sync.get(DEFAULTS, (s) => chrome.storage.sync.set({ enabled: !s.enabled }));
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "sync" && changes.enabled) setBadge(changes.enabled.newValue);
});

// Developer conveniences, active only while the popup's "Developer" switch is on.
chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (msg?.type !== "sdm:theme-css") return;
  chrome.storage.sync.get({ dev: false }, ({ dev }) => {
    if (!dev) return reply(null);
    fetch(chrome.runtime.getURL("theme.css")).then(r => r.text()).then(reply).catch(() => reply(null));
  });
  return true;
});
// Unpacked installs only (store builds carry an update_url): reload on request from the content script,
// and stamp each worker boot so a reload can be verified from outside.
const UNPACKED = !chrome.runtime.getManifest().update_url;
chrome.runtime.onMessage.addListener((msg) => {
  if (msg?.type === "sdm:reload" && UNPACKED) chrome.storage.sync.get({ dev: false }, ({ dev }) => { if (dev) chrome.runtime.reload(); });
});
if (UNPACKED) chrome.storage.sync.get({ dev: false }, ({ dev }) => { if (dev) chrome.storage.local.set({ sdmBoot: Date.now() }); });
