"""Render the extension icons from icons/icon.svg (the extension's own mark: a crescent inverting across a
light/dark split). Output icons/icon{16,32,48,128,256,512}.png. Playwright Chromium rasterizes, Pillow downsamples."""
import asyncio, os, base64
from PIL import Image
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SVG = open(os.path.join(ROOT, "icons", "icon.svg"), "rb").read()
SIZE = 1024
HTML = f"""<!doctype html><html><body style="margin:0;background:transparent"><img src="data:image/svg+xml;base64,{base64.b64encode(SVG).decode()}" style="width:{SIZE}px;height:{SIZE}px;display:block"></body></html>"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": SIZE, "height": SIZE}, device_scale_factor=1)
        await pg.set_content(HTML); await pg.wait_for_timeout(200)
        raw = os.path.join(ROOT, "icons", "icon1024.png")
        await pg.screenshot(path=raw, omit_background=True, clip={"x": 0, "y": 0, "width": SIZE, "height": SIZE})
        await b.close()
    im = Image.open(raw).convert("RGBA")
    for s in (16, 32, 48, 128, 256, 512):
        im.resize((s, s), Image.LANCZOS).save(os.path.join(ROOT, "icons", f"icon{s}.png"), optimize=True)
    os.remove(raw)
    print("icons written:", sorted(f for f in os.listdir(os.path.join(ROOT, "icons"))))
asyncio.run(main())
