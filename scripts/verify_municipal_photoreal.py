import sys
import asyncio
from playwright.async_api import async_playwright

async def main():
    errors = []
    warnings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 900})

        page.on("console", lambda msg: (
            errors.append(msg.text) if msg.type == "error" else (
                warnings.append(msg.text) if msg.type == "warning" else None
            )
        ))
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("Navigating to http://localhost:8085/index.html...")
        await page.goto("http://localhost:8085/index.html", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3500)

        # 1. Aerial Overview
        print("Clicking Aerial Overview camera preset...")
        await page.evaluate("document.getElementById('btn-cam-overview')?.click()")
        await page.wait_for_timeout(2500)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/municipal_photoreal_aerial.png")
        print("Saved municipal_photoreal_aerial.png")

        # 2. Secondary Clarifiers closeup (Rotating mechanism & water reflections)
        print("Clicking Clarifiers camera preset...")
        await page.evaluate("document.getElementById('btn-cam-clarifier')?.click()")
        await page.wait_for_timeout(2500)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/municipal_photoreal_clarifiers.png")
        print("Saved municipal_photoreal_clarifiers.png")

        # 3. Aeration Basin
        print("Clicking Aeration Basin camera preset...")
        await page.evaluate("document.getElementById('btn-cam-aeration')?.click()")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/municipal_photoreal_aeration.png")
        print("Saved municipal_photoreal_aeration.png")

        # 4. Digesters
        print("Clicking Digesters camera preset...")
        await page.evaluate("document.getElementById('btn-cam-digesters')?.click()")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/municipal_photoreal_digesters.png")
        print("Saved municipal_photoreal_digesters.png")

        await browser.close()

    print(f"\n--- VERIFICATION RESULTS FOR MUNICIPAL WRRF ---")
    print(f"Total Errors: {len(errors)}")
    for e in errors:
        print(f"  ERROR: {e}")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings[:5]:
            print(f"  WARN: {w}")

    if errors:
        sys.exit(1)
    else:
        print("SUCCESS: 0 console errors on index.html!")

if __name__ == "__main__":
    asyncio.run(main())
