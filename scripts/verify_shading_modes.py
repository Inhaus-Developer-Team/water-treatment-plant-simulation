import asyncio
from playwright.async_api import async_playwright

async def verify_simulation(url, name):
    print(f"\n--- Testing Shading Modes & Material Restoration on {name} ({url}) ---")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        errors = []
        page.on("pageerror", lambda err: errors.append(f"PageError: {err}"))
        page.on("console", lambda msg: errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None)
        
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2.0) # allow any GLTF models to resolve
        
        # Test sequence: Wireframe -> PBR -> Clay -> PBR -> Normals -> PBR
        # Check that when in PBR mode, NO mesh has wireframe = true or MeshNormalMaterial or clay material
        modes_to_test = [
            ("btn-mode-wire", "wireframe"),
            ("btn-mode-pbr", "pbr"),
            ("btn-mode-clay", "clay"),
            ("btn-mode-pbr", "pbr"),
            ("btn-mode-normals", "normals"),
            ("btn-mode-pbr", "pbr"),
        ]
        
        for btn_id, mode in modes_to_test:
            btn = await page.query_selector(f"#{btn_id}")
            if not btn:
                print(f"Warning: button #{btn_id} not found!")
                continue
            await btn.click()
            await asyncio.sleep(0.5)
            
            # Inspect state
            stats = await page.evaluate("""() => {
                let totalMeshes = 0;
                let wireframeMeshes = 0;
                let normalMatMeshes = 0;
                let clayMeshes = 0;
                
                const group = window.facilityGroup || window.mobilePlantGroup;
                if (!group) return { error: "No root group found" };
                
                group.traverse(obj => {
                    if (obj.isMesh) {
                        totalMeshes++;
                        const mat = obj.material;
                        if (mat) {
                            if (mat.wireframe) wireframeMeshes++;
                            if (mat.type === 'MeshNormalMaterial') normalMatMeshes++;
                            if (mat.type === 'MeshStandardMaterial' && mat.color && typeof mat.color.getHexString === 'function') {
                                const hex = mat.color.getHexString().toLowerCase();
                                if (hex === 'f1f5f9' || hex === 'f5f5f4') clayMeshes++;
                            }
                        }
                    }
                });
                return { totalMeshes, wireframeMeshes, normalMatMeshes, clayMeshes };
            }""")
            print(f"  Mode '{mode}' -> Stats: {stats}")
            
            if mode == 'pbr':
                # Wireframes should be 0 (none stuck)
                assert stats['wireframeMeshes'] == 0, f"Stuck wireframe meshes in PBR! Count: {stats['wireframeMeshes']}"
                assert stats['normalMatMeshes'] == 0, f"Stuck normal material meshes in PBR! Count: {stats['normalMatMeshes']}"
                assert stats['clayMeshes'] == 0, f"Stuck clay material meshes in PBR! Count: {stats['clayMeshes']}"

        # Test toggle HUD button as well
        wireframe_hud = await page.query_selector("#btn-wireframe")
        if wireframe_hud:
            print("  Testing HUD Wireframe toggle button...")
            await wireframe_hud.click() # ON
            await asyncio.sleep(0.5)
            await wireframe_hud.click() # OFF
            await asyncio.sleep(0.5)
            stats = await page.evaluate("""() => {
                let wireframeMeshes = 0;
                const group = window.facilityGroup || window.mobilePlantGroup;
                group.traverse(obj => {
                    if (obj.isMesh && obj.material && obj.material.wireframe) wireframeMeshes++;
                });
                return { wireframeMeshes };
            }""")
            print(f"  HUD Wireframe Toggle Off -> {stats}")
            assert stats['wireframeMeshes'] == 0, f"Stuck wireframes after HUD toggle off! {stats}"

        # If on mobile.html, test X-Ray mode combined with Wireframe/Clay
        if 'mobile' in url:
            print("  Testing mobile X-Ray interaction...")
            xray_btn = await page.query_selector("#btn-xray-main")
            if xray_btn:
                await xray_btn.click() # Turn X-ray ON
                await asyncio.sleep(0.5)
                # Switch to Wireframe
                await (await page.query_selector("#btn-mode-wire")).click()
                await asyncio.sleep(0.5)
                # Switch back to PBR
                await (await page.query_selector("#btn-mode-pbr")).click()
                await asyncio.sleep(0.5)
                # Turn X-ray OFF
                await xray_btn.click()
                await asyncio.sleep(0.5)
                stats = await page.evaluate("""() => {
                    let wireframeMeshes = 0;
                    let clayMeshes = 0;
                    window.mobilePlantGroup.traverse(obj => {
                        if (obj.isMesh && obj.material) {
                            if (obj.material.wireframe) wireframeMeshes++;
                            if (obj.material.type === 'MeshStandardMaterial' && obj.material.color && typeof obj.material.color.getHexString === 'function' && obj.material.color.getHexString() === 'f5f5f4') clayMeshes++;
                        }
                    });
                    return { wireframeMeshes, clayMeshes };
                }""")
                print(f"  Mobile X-Ray + Wireframe round-trip -> {stats}")
                assert stats['wireframeMeshes'] == 0
                assert stats['clayMeshes'] == 0

        # Check console errors
        filtered_errors = [e for e in errors if "favicon" not in e.lower()]
        print(f"  Console errors: {len(filtered_errors)}")
        if filtered_errors:
            for err in filtered_errors:
                print(f"    {err}")
        assert len(filtered_errors) == 0, "Console errors detected!"
        print(f"  PASS: {name} material restoration verified successfully!")
        await browser.close()

async def main():
    await verify_simulation("http://localhost:8085/index.html", "Municipal WRRF Simulation")
    await verify_simulation("http://localhost:8085/mobile.html", "Mobile Rapid-Response Simulation")

if __name__ == "__main__":
    asyncio.run(main())
