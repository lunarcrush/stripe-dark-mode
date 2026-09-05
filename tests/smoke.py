"""Smoke test: load the extension into Chromium, route dashboard.stripe.com to the synthetic mock, and prove the theme
engages, disengages, keeps images true, and that the popup renders with the right version.
Usage: python3 tests/smoke.py [--ext chrome|repo]   (chrome = the packaged build in dist/build/chrome, repo = the repo root;
default: chrome if it has been built, else repo)
Exit code 0 = pass. Prints one JSON line per check."""
import asyncio, os, sys, json, tempfile, argparse, re, shutil
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDS = {"chrome": os.path.join(ROOT, "dist", "build", "chrome"), "repo": ROOT}  # the only two trees Chromium can load
ap = argparse.ArgumentParser(); ap.add_argument("--ext", choices=sorted(BUILDS), default=None); args = ap.parse_args()
EXT = BUILDS["chrome"] if args.ext == "chrome" or (args.ext is None and os.path.isdir(BUILDS["chrome"])) else BUILDS["repo"]
MOCK = open(os.path.join(ROOT, "store", "mock", "index.html"), encoding="utf-8").read()
MANIFEST = json.load(open(os.path.join(EXT, "manifest.json")))
FRAME = """<html><body style="background:#fff;color:#111"><p>invoice preview</p><img id=i width=60 height=60 src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='60' height='60'><rect width='60' height='60' fill='%23ff0000'/></svg>"></body></html>"""
fails = []

def store_like(src):
    """Temp copy with the update_url the Chrome Web Store injects, so store-only behavior (hidden dev switch) is tested."""
    d = tempfile.mkdtemp(prefix="sdm-smoke-store-"); shutil.copytree(src, d, dirs_exist_ok=True)
    m = json.load(open(os.path.join(d, "manifest.json"))); m["update_url"] = "https://clients2.google.com/service/update2/crx"
    json.dump(m, open(os.path.join(d, "manifest.json"), "w"), indent=2); return d
def check(name, ok, detail=""):
    print(json.dumps({"check": name, "ok": bool(ok), "detail": detail})); 
    if not ok: fails.append(name)

async def main():
    check("manifest.name<=45", len(MANIFEST["name"]) <= 45, MANIFEST["name"])
    check("manifest.description<=132", len(MANIFEST["description"]) <= 132, str(len(MANIFEST["description"])))
    async with async_playwright() as p:
        ud = tempfile.mkdtemp(prefix="sdm-smoke-")
        ctx = await p.chromium.launch_persistent_context(ud, headless=False, viewport={"width": 1280, "height": 800},
            args=["--headless=new", f"--disable-extensions-except={EXT}", f"--load-extension={EXT}"])
        sw = ctx.service_workers or [await ctx.wait_for_event("serviceworker", timeout=20000)]
        ext_id = sw[0].url.split("/")[2]; check("service_worker.started", True, ext_id)
        await ctx.route("https://dashboard.stripe.com/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=MOCK))
        errors = []
        page = await ctx.new_page(); page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto("https://dashboard.stripe.com/test/dashboard"); await page.wait_for_timeout(600)
        check("dark.data-sdm=on", await page.evaluate("document.documentElement.getAttribute('data-sdm')") == "on")
        filt = await page.evaluate("getComputedStyle(document.documentElement).filter"); check("dark.root_filter", "invert(0.92)" in filt and "hue-rotate(180deg)" in filt, filt)
        imgf = await page.evaluate("getComputedStyle(document.querySelector('.cust img, .avatar')).filter"); check("dark.image_restored", "invert(1)" in imgf, imgf)
        check("dark.no_page_errors", not errors, "; ".join(errors)[:200])
        pop = await ctx.new_page(); await pop.goto(f"chrome-extension://{ext_id}/popup/popup.html"); await pop.wait_for_timeout(400)
        ver = await pop.evaluate("document.getElementById('ver').textContent"); check("popup.version", ver == "v" + MANIFEST["version"], ver)
        check("popup.toggle_checked", await pop.evaluate("document.getElementById('enabled').checked") is True)
        check("popup.font_loaded", await pop.evaluate("document.fonts.check('13px \"Plus Jakarta Sans\"')"))
        check("popup.made_by_link", (await pop.evaluate("document.querySelector('footer a.made')?.href")) == "https://lunarcrush.com/")
        fb = await pop.evaluate("(() => { const a = document.getElementById('feedback'); return a.hidden ? null : a.href; })()")
        check("popup.feedback_link", fb == "mailto:support@lunarcrush.com?subject=Dark%20Mode%20for%20Stripe%20Dashboard", str(fb))
        await pop.evaluate("new Promise(r => chrome.storage.sync.set({enabled:false}, r))"); await page.wait_for_timeout(200)
        check("toggle_off.data-sdm=off", await page.evaluate("document.documentElement.getAttribute('data-sdm')") == "off")
        check("toggle_off.root_filter_none", await page.evaluate("getComputedStyle(document.documentElement).filter") == "none")
        await pop.evaluate("new Promise(r => chrome.storage.sync.set({enabled:true}, r))"); await page.wait_for_timeout(200)
        check("toggle_on.data-sdm=on", await page.evaluate("document.documentElement.getAttribute('data-sdm')") == "on")
        # frame gating: a non-dashboard stripe.com top-level page must be untouched
        await ctx.route("https://docs.stripe.com/**", lambda r: r.fulfill(status=200, content_type="text/html", body="<html><body>docs</body></html>"))
        other = await ctx.new_page(); await other.goto("https://docs.stripe.com/x"); await other.wait_for_timeout(300)
        check("gating.docs_untouched", await other.evaluate("document.documentElement.getAttribute('data-sdm')") is None)
        # embedded Stripe frame: no root filter of its own (the top document already inverts it), media restored
        await ctx.route("https://invoice.stripe.com/**", lambda r: r.fulfill(status=200, content_type="text/html", body=FRAME))
        await page.evaluate("() => { const f = document.createElement('iframe'); f.id = 'sdmf'; f.src = 'https://invoice.stripe.com/i/preview'; f.width = 300; f.height = 200; document.body.appendChild(f); }")
        await page.wait_for_timeout(700)
        fr = next((f for f in page.frames if "invoice.stripe.com" in f.url), None)
        check("frame.found", fr is not None, "no invoice frame")
        if fr:
            check("frame.mode", await fr.evaluate("document.documentElement.getAttribute('data-sdm')") == "frame")
            check("frame.no_root_filter", await fr.evaluate("getComputedStyle(document.documentElement).filter") == "none")
            check("frame.media_restored", "invert(1)" in await fr.evaluate("getComputedStyle(document.getElementById('i')).filter"))
        # diagnostics: the route must never carry ids or unknown segments, and no query string
        await page.goto("https://dashboard.stripe.com/acct_1ABCDEFGHIJKLMNO/test/customers/cus_ABC123456789/cs_test_ABC123456789?secret=1"); await page.wait_for_timeout(500)
        rep = await pop.evaluate("""async () => {
          const tabs = await chrome.tabs.query({});
          for (const t of tabs) { try { const r = await chrome.tabs.sendMessage(t.id, {type: 'sdm:diagnostics'}); if (r && r.route !== undefined) return r; } catch (_) {} }
          return {error: 'no tab answered', tabs: tabs.map(t => t.url || '(no url)')};
        }""")
        check("diag.tab_answered", "route" in rep, json.dumps(rep)[:160])
        route = rep.get("route", ""); leak = re.search(r"ABC123456789|acct_1|secret", json.dumps(rep))
        check("diag.route_template", route == "/…/test/customers/…/…", route)
        check("diag.no_ids_anywhere", leak is None, leak.group(0) if leak else "")
        check("diag.no_ua_vars_classes", not any(k in rep for k in ("ua", "classHints", "rootCustomProperties", "rootColorProperties", "path")), ",".join(rep.keys()))
        await ctx.close()
        # store-like build: developer switch must be hidden
        ud2 = tempfile.mkdtemp(prefix="sdm-smoke2-"); EXT2 = store_like(EXT)
        ctx2 = await p.chromium.launch_persistent_context(ud2, headless=False, viewport={"width": 1280, "height": 800},
            args=["--headless=new", f"--disable-extensions-except={EXT2}", f"--load-extension={EXT2}"])
        sw2 = ctx2.service_workers or [await ctx2.wait_for_event("serviceworker", timeout=20000)]
        pop2 = await ctx2.new_page(); await pop2.goto(f"chrome-extension://{sw2[0].url.split('/')[2]}/popup/popup.html"); await pop2.wait_for_timeout(300)
        check("store_build.dev_switch_hidden", await pop2.evaluate("document.getElementById('dev').closest('.check').offsetParent === null"))
        check("store_build.other_rows_visible", await pop2.evaluate("document.getElementById('keepImages').closest('.check').offsetParent !== null"))
        await ctx2.close()
    print(json.dumps({"result": "PASS" if not fails else "FAIL", "failed": fails, "ext": EXT}))
    sys.exit(1 if fails else 0)
asyncio.run(main())
