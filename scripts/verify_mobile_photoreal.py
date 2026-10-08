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

        print("Navigating to http://localhost:8085/mobile.html...")
        await page.goto("http://localhost:8085/mobile.html", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3500)

        # 1. Focus on Truck & Engineer
        print("Clicking Operations Truck camera preset...")
        await page.click("#btn-cam-truck")
        await page.wait_for_timeout(2500)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/mobile_photoreal_truck_engineer.png")
        print("Saved mobile_photoreal_truck_engineer.png")

        # 2. Facility Overview with PBR Desert IBL
        print("Clicking Overview camera preset...")
        await page.click("#btn-cam-overview")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/mobile_photoreal_overview.png")
        print("Saved mobile_photoreal_overview.png")

        # 3. Buffer Tanks & Pump Skid Closeup
        print("Clicking Raw Influent Vessel preset...")
        await page.click("#btn-cam-buffer")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/mobile_photoreal_tanks_skid.png")
        print("Saved mobile_photoreal_tanks_skid.png")

        # 4. X-Ray Mode
        print("Toggling X-Ray Mode...")
        await page.click("#btn-xray-toggle")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/mobile_photoreal_xray.png")
        print("Saved mobile_photoreal_xray.png")

        await browser.close()

    print(f"\n--- VERIFICATION RESULTS ---")
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
        print("SUCCESS: 0 console errors on mobile.html!")

if __name__ == "__main__":
    asyncio.run(main())
