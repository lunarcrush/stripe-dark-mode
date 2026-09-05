"""Render the extension icons: white LunarCrush mark on a #0B121E rounded tile (LunarCrush brand: white mark on the near-black canvas).
Output icons/icon{16,32,48,128,256,512}.png. Uses Playwright Chromium for the SVG raster, Pillow for downsampling."""
import asyncio, os, base64
from PIL import Image
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARK = open(os.path.join(ROOT, "popup", "lc-mark.svg"), "rb").read()
SIZE = 1024
HTML = f"""<!doctype html><html><body style="margin:0;background:transparent">
<div style="width:{SIZE}px;height:{SIZE}px;border-radius:{int(SIZE*0.22)}px;background:#0B121E;box-shadow:inset 0 0 0 {int(SIZE*0.012)}px rgba(255,255,255,0.07);display:grid;place-items:center;overflow:hidden;position:relative">
  <div style="position:absolute;inset:0;background:radial-gradient(60% 55% at 50% 42%, rgba(20,184,129,0.10), rgba(20,184,129,0) 70%)"></div>
  <img src="data:image/svg+xml;base64,{base64.b64encode(MARK).decode()}" style="width:{int(SIZE*0.60)}px;height:auto;position:relative;transform:translateY(-{int(SIZE*0.01)}px)">
</div></body></html>"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": SIZE, "height": SIZE}, device_scale_factor=1)
        await pg.set_content(HTML); await pg.wait_for_timeout(200)
        raw = os.path.join(ROOT, "icons", "icon1024.png")
        await pg.screenshot(path=raw, omit_background=True, clip={"x":0,"y":0,"width":SIZE,"height":SIZE})
        await b.close()
    im = Image.open(raw).convert("RGBA")
    for s in (16, 32, 48, 128, 256, 512):
        im.resize((s, s), Image.LANCZOS).save(os.path.join(ROOT, "icons", f"icon{s}.png"), optimize=True)
    os.remove(raw)
    print("icons written:", sorted(os.listdir(os.path.join(ROOT, "icons"))))
asyncio.run(main())
