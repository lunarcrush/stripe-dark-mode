"""Build every Chrome Web Store asset for Dark Mode for Stripe Dashboard by LunarCrush.
- Loads the REAL extension (this folder) into Playwright Chromium (headless=new).
- Routes https://dashboard.stripe.com/* to store/mock/index.html (synthetic data), so the content script + theme.css
  theme the mock exactly as they would the live Dashboard. No real Stripe page or account is touched.
- Captures at 2x and downsamples to the store's 1280x800, then composes the split, popup and promo tiles.
Outputs to store/assets/. Run: python3 store/tools/capture.py
Butler (display font for the tiles only) is fetched from lunarcrush.com into store/brand/_fetched/ (gitignored) so the
repo does not redistribute it; Plus Jakarta Sans (OFL) ships with the popup and is reused for the tiles.
"""
import asyncio, os, tempfile, json, urllib.request
from PIL import Image, ImageFilter, ImageDraw
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORE = os.path.join(ROOT, "store"); ASSETS = os.path.join(STORE, "assets"); os.makedirs(ASSETS, exist_ok=True)
MOCK = open(os.path.join(STORE, "mock", "index.html"), encoding="utf-8").read()

def store_like_build():
    """Copy the extension into a temp dir and add the update_url the Chrome Web Store injects on install, so the
    screenshots show exactly what installed users see (no developer switch, dev URL switches inert)."""
    import shutil
    d = tempfile.mkdtemp(prefix="sdm-storelike-")
    for f in ("manifest.json", "theme.css", "content.js", "background.js", "LICENSE"): shutil.copy(os.path.join(ROOT, f), d)
    for sub in ("popup", "icons"): shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub))
    m = json.load(open(os.path.join(d, "manifest.json"))); m["update_url"] = "https://clients2.google.com/service/update2/crx"
    json.dump(m, open(os.path.join(d, "manifest.json"), "w"), indent=2); return d
W, H, DSF = 1280, 800, 2
PAGES = {"home": "/test/dashboard", "payments": "/test/payments", "customer": "/test/customers/cus_demo_9F2kQ7Lx"}

def down(src, dst, size=(W, H)):
    im = Image.open(src).convert("RGB"); im = im.resize(size, Image.LANCZOS); im.save(dst, optimize=True); os.remove(src); return im

async def main():
    async with async_playwright() as p:
        ud = tempfile.mkdtemp(prefix="sdm-store-")
        EXT = store_like_build()
        ctx = await p.chromium.launch_persistent_context(ud, headless=False, viewport={"width": W, "height": H}, device_scale_factor=DSF,
            args=["--headless=new", f"--disable-extensions-except={EXT}", f"--load-extension={EXT}", "--hide-scrollbars"])
        sw = ctx.service_workers or [await ctx.wait_for_event("serviceworker", timeout=15000)]
        ext_id = sw[0].url.split("/")[2]
        await ctx.route("https://dashboard.stripe.com/**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=MOCK))
        pop = await ctx.new_page(); await pop.goto(f"chrome-extension://{ext_id}/popup/popup.html"); await pop.wait_for_timeout(300)
        async def set_enabled(v):
            await pop.evaluate("(v) => new Promise(r => chrome.storage.sync.set({enabled: v}, r))", v); await pop.wait_for_timeout(150)
        page = await ctx.new_page()
        shots = {}
        for mode in ("light", "dark"):
            await set_enabled(mode == "dark")
            for name, path in PAGES.items():
                await page.goto("https://dashboard.stripe.com" + path); await page.wait_for_timeout(500)
                attr = await page.evaluate("document.documentElement.getAttribute('data-sdm')")
                assert attr == ("on" if mode == "dark" else "off"), f"{name}/{mode}: data-sdm={attr}"
                raw = os.path.join(ASSETS, f"_raw-{name}-{mode}.png"); await page.screenshot(path=raw)
                shots[(name, mode)] = raw
                print(f"captured {name} {mode} (data-sdm={attr})")
        # popup at 1x logical, 2x pixels
        await set_enabled(True); await pop.reload(); await pop.wait_for_timeout(400)
        popraw = os.path.join(ASSETS, "_raw-popup.png"); await pop.locator("body").screenshot(path=popraw)
        await ctx.close()

    # ---- 1280x800 screenshots ----
    dark_home = down(shots[("home","dark")], os.path.join(ASSETS, "01-dashboard-dark.png"))
    light_home = down(shots[("home","light")], os.path.join(ASSETS, "_home-light.png"))
    down(shots[("payments","dark")], os.path.join(ASSETS, "03-payments-dark.png"))
    cust_dark = down(shots[("customer","dark")], os.path.join(ASSETS, "_customer-dark.png"))
    for k in (("payments","light"), ("customer","light")): os.remove(shots[k])

    # 02: before/after split with a green divider
    split = Image.new("RGB", (W, H)); cut = W // 2
    split.paste(light_home.crop((0, 0, cut, H)), (0, 0)); split.paste(dark_home.crop((cut, 0, W, H)), (cut, 0))
    d = ImageDraw.Draw(split); d.rectangle([cut - 2, 0, cut + 1, H], fill=(20, 184, 129))
    split.save(os.path.join(ASSETS, "02-before-after.png"), optimize=True); os.remove(os.path.join(ASSETS, "_home-light.png"))

    # 04: customer page with the popup open (top-right, drop shadow)
    popup = Image.open(popraw).convert("RGBA"); popup = popup.resize((popup.width // DSF, popup.height // DSF), Image.LANCZOS); os.remove(popraw)
    base = cust_dark.convert("RGBA"); x, y = W - popup.width - 28, 8
    shadow = Image.new("RGBA", (popup.width + 80, popup.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([40, 48, 40 + popup.width, 48 + popup.height], radius=14, fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22)); base.alpha_composite(shadow, (x - 40, y - 40))
    mask = Image.new("L", popup.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, popup.width - 1, popup.height - 1], radius=12, fill=255)
    rounded = Image.new("RGBA", popup.size, (0, 0, 0, 0)); rounded.paste(popup, (0, 0), mask); base.alpha_composite(rounded, (x, y))
    base.convert("RGB").save(os.path.join(ASSETS, "04-customer-popup.png"), optimize=True); os.remove(os.path.join(ASSETS, "_customer-dark.png"))
    popup.convert("RGB").save(os.path.join(ASSETS, "popup-320.png"), optimize=True)

    # ---- promo tiles + feature card (plain Chromium, file://) ----
    fetched = os.path.join(STORE, "brand", "_fetched"); os.makedirs(fetched, exist_ok=True)
    butler = os.path.join(fetched, "Butler-Free-Lgt.otf")
    if not os.path.exists(butler):
        req = urllib.request.Request("https://lunarcrush.com/landing-assets/Butler-Free-Lgt.otf", headers={"User-Agent": "Mozilla/5.0 (Macintosh) stripe-dark-mode/store-tools"})
        with urllib.request.urlopen(req, timeout=30) as r, open(butler, "wb") as f: f.write(r.read())
        print("fetched Butler for the tiles")
    promo = "file://" + os.path.join(STORE, "tools", "promo.html")
    async with async_playwright() as p:
        b = await p.chromium.launch(); 
        for kind, size, out in (("small", (440, 280), "promo-small-440x280.png"), ("marq", (1400, 560), "promo-marquee-1400x560.png"), ("feat", (1280, 800), "05-features.png")):
            pg = await b.new_page(viewport={"width": size[0], "height": size[1]}, device_scale_factor=DSF)
            await pg.goto(f"{promo}?kind={kind}&shot=../assets/01-dashboard-dark.png"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
            raw = os.path.join(ASSETS, f"_raw-{kind}.png"); await pg.screenshot(path=raw); down(raw, os.path.join(ASSETS, out), size); await pg.close()
        await b.close()
    # store icon
    Image.open(os.path.join(ROOT, "icons", "icon128.png")).convert("RGBA").save(os.path.join(ASSETS, "icon-128.png"))
    inv = {f: Image.open(os.path.join(ASSETS, f)).size for f in sorted(os.listdir(ASSETS)) if f.endswith(".png")}
    json.dump(inv, open(os.path.join(ASSETS, "inventory.json"), "w"), indent=2); print(json.dumps(inv, indent=2))
asyncio.run(main())
