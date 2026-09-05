// Where "Send feedback" goes. mailto: opens the user's mail client; an http(s) URL opens a tab. Empty = link hidden.
const FEEDBACK_URL = "mailto:support@lunarcrush.com?subject=Dark%20Mode%20for%20Stripe%20Dashboard";
const DEFAULTS = { enabled: true, invert: 0.92, brightness: 1, contrast: 1, keepImages: true, dev: false };
const $ = (id) => document.getElementById(id);
const status = (t) => { $("status").textContent = t; if (t) setTimeout(() => ($("status").textContent = ""), 2500); };

const render = (s) => {
  $("enabled").checked = !!s.enabled;
  for (const k of ["invert", "brightness", "contrast"]) { $(k).value = s[k]; $(k + "-out").value = Math.round(s[k] * 100) + "%"; }
  $("keepImages").checked = !!s.keepImages;
  $("dev").checked = !!s.dev;
};

$("ver").textContent = "v" + chrome.runtime.getManifest().version;
// The developer hot-reload switch only does anything on unpacked installs; store builds (which carry an update_url) hide it.
if (chrome.runtime.getManifest().update_url) $("dev").closest(".check").hidden = true;
chrome.storage.sync.get(DEFAULTS, (s) => render({ ...DEFAULTS, ...s }));

$("enabled").addEventListener("change", (e) => chrome.storage.sync.set({ enabled: e.target.checked }));
$("dev").addEventListener("change", (e) => chrome.storage.sync.set({ dev: e.target.checked }));
$("keepImages").addEventListener("change", (e) => chrome.storage.sync.set({ keepImages: e.target.checked }));
for (const k of ["invert", "brightness", "contrast"]) {
  $(k).addEventListener("input", (e) => { $(k + "-out").value = Math.round(e.target.value * 100) + "%"; chrome.storage.sync.set({ [k]: Number(e.target.value) }); });
}
$("reset").addEventListener("click", () => { chrome.storage.sync.set(DEFAULTS); render(DEFAULTS); status("Reset to defaults"); });

$("diag").addEventListener("click", async () => {
  // tab.url is not readable without extra permissions; the content script answering is the test.
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return status("Open a Stripe Dashboard tab first");
  try {
    const page = await chrome.tabs.sendMessage(tab.id, { type: "sdm:diagnostics" });
    const settings = await new Promise((r) => chrome.storage.sync.get(DEFAULTS, r));
    const report = { extension: chrome.runtime.getManifest().name, version: chrome.runtime.getManifest().version, when: new Date().toISOString(), settings, page };
    await navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    status(`Report copied (${page.natives.length} native-dark regions on ${page.route})`);
  } catch (e) { status("Open a Stripe Dashboard tab first (or reload it), then retry"); }
});
if (FEEDBACK_URL) {
  const a = $("feedback"); a.hidden = false; a.href = FEEDBACK_URL; $("feedback-sep").hidden = false;
  if (!FEEDBACK_URL.startsWith("mailto:")) a.addEventListener("click", (e) => { e.preventDefault(); chrome.tabs.create({ url: FEEDBACK_URL }); });
}
