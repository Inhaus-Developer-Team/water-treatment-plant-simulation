import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    print("\n=======================================================")
    print("VERIFYING CLARIFIER BRIDGE WIREFRAME TOGGLE RESOLUTION")
    print("=======================================================")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        console_errors = []
        page.on("pageerror", lambda err: console_errors.append(f"PageError: {err}"))
        page.on("console", lambda msg: console_errors.append(f"ConsoleError: {msg.text}") if msg.type == "error" else None)

        print("1. Loading simulation at clarifier camera preset...")
        await page.goto("http://127.0.0.1:8085/index.html?cam=clarifier", wait_until="networkidle")
        await asyncio.sleep(3.5) # Wait for GLB models to resolve

        async def get_bridge_status():
            return await page.evaluate("""() => {
                const b0 = window.clarifierBridges[0];
                const b1 = window.clarifierBridges[1];
                
                function analyzeBridge(b, label) {
                    if (!b) return { label, found: false };
                    
                    let meshCount = 0;
                    let visibleMeshCount = 0;
                    let wireframeCount = 0;
                    let invalidMatCount = 0;
                    let pbrCount = 0;
                    const sampleMaterials = [];
                    
                    b.traverse(node => {
                        if (node.isMesh) {
                            meshCount++;
                            if (node.visible) visibleMeshCount++;
                            const mat = node.material;
                            if (!mat || (typeof mat !== 'object') || !mat.isMaterial) {
                                invalidMatCount++;
                            } else {
                                if (mat.wireframe) wireframeCount++;
                                if (mat.isMeshStandardMaterial || mat.isMeshPhysicalMaterial) pbrCount++;
                                if (sampleMaterials.length < 3) {
                                    sampleMaterials.push({
                                        name: node.name || 'unnamed',
                                        type: mat.type,
                                        wireframe: !!mat.wireframe,
                                        color: mat.color ? mat.color.getHexString() : null
                                    });
                                }
                            }
                        }
                    });
                    
                    return {
                        label,
                        found: true,
                        name: b.name,
                        visible: b.visible,
                        rotY: b.rotation.y,
                        parentName: b.parent ? b.parent.name : null,
                        meshCount,
                        visibleMeshCount,
                        wireframeCount,
                        invalidMatCount,
                        pbrCount,
                        sampleMaterials
                    };
                }
                
                return {
                    b0: analyzeBridge(b0, "CL-01 Bridge (Left)"),
                    b1: analyzeBridge(b1, "CL-02 Bridge (Right)")
                };
            }""")

        # Status 1: Initial PBR
        s1 = await get_bridge_status()
        print("Status 1 (Initial PBR):", json.dumps(s1, indent=2))
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/clarifier_fixed_1_initial_pbr.png")
        assert s1["b0"]["visibleMeshCount"] > 0, "CL-01 bridge has 0 visible meshes on load!"
        assert s1["b1"]["visibleMeshCount"] > 0, "CL-02 bridge has 0 visible meshes on load!"
        assert s1["b0"]["invalidMatCount"] == 0, f"CL-01 has invalid materials: {s1['b0']['invalidMatCount']}"
        assert s1["b1"]["invalidMatCount"] == 0, f"CL-02 has invalid materials: {s1['b1']['invalidMatCount']}"

        # Status 2: Toggle Wireframe ON via HUD button (#btn-wireframe)
        print("\n2. Toggling CAD Wireframe mode ON via HUD #btn-wireframe...")
        await page.click("#btn-wireframe")
        await asyncio.sleep(1.0)
        s2 = await get_bridge_status()
        print("Status 2 (Wireframe ON):", json.dumps(s2, indent=2))
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/clarifier_fixed_2_wireframe.png")
        assert s2["b0"]["wireframeCount"] > 0, "CL-01 should have wireframe meshes!"
        assert s2["b1"]["wireframeCount"] > 0, "CL-02 should have wireframe meshes!"
        assert s2["b0"]["visibleMeshCount"] > 0, "CL-01 lost visible meshes in wireframe!"
        assert s2["b1"]["visibleMeshCount"] > 0, "CL-02 lost visible meshes in wireframe!"

        # Status 3: Toggle Wireframe OFF via HUD button (#btn-wireframe)
        print("\n3. Toggling CAD Wireframe mode OFF via HUD #btn-wireframe...")
        await page.click("#btn-wireframe")
        await asyncio.sleep(1.0)
        s3 = await get_bridge_status()
        print("Status 3 (PBR Restored after toggle):", json.dumps(s3, indent=2))
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/clarifier_fixed_3_pbr_restored.png")
        assert s3["b0"]["visibleMeshCount"] > 0, "CL-01 bridge vanished after wireframe toggle off!"
        assert s3["b1"]["visibleMeshCount"] > 0, "CL-02 bridge vanished after wireframe toggle off! (BUG STILL PRESENT)"
        assert s3["b0"]["wireframeCount"] == 0, "CL-01 stuck in wireframe!"
        assert s3["b1"]["wireframeCount"] == 0, "CL-02 stuck in wireframe!"
        assert s3["b1"]["invalidMatCount"] == 0, f"CL-02 has invalid materials: {s3['b1']['invalidMatCount']}"
        assert s3["b1"]["pbrCount"] > 0, "CL-02 has no PBR materials restored!"

        # Status 4: Toggle again to verify repeated stability
        print("\n4. Toggling Wireframe ON and OFF again (stability check)...")
        await page.click("#btn-wireframe") # ON
        await asyncio.sleep(0.5)
        await page.click("#btn-wireframe") # OFF
        await asyncio.sleep(0.5)
        s4 = await get_bridge_status()
        print("Status 4 (Second Toggle Cycle OFF):", json.dumps(s4, indent=2))
        assert s4["b1"]["visibleMeshCount"] > 0, "CL-02 vanished on repeated toggle!"
        assert s4["b1"]["invalidMatCount"] == 0, "CL-02 has invalid materials on repeated toggle!"

        # Status 5: Check continuous rotation
        print("\n5. Verifying continuous counter-rotation of both clarifier bridges...")
        initial_rot_b0 = s4["b0"]["rotY"]
        initial_rot_b1 = s4["b1"]["rotY"]
        await asyncio.sleep(1.5)
        s5 = await get_bridge_status()
        new_rot_b0 = s5["b0"]["rotY"]
        new_rot_b1 = s5["b1"]["rotY"]
        print(f"CL-01 rotation: {initial_rot_b0:.4f} -> {new_rot_b0:.4f} (diff: {new_rot_b0 - initial_rot_b0:.4f})")
        print(f"CL-02 rotation: {initial_rot_b1:.4f} -> {new_rot_b1:.4f} (diff: {new_rot_b1 - initial_rot_b1:.4f})")
        assert abs(new_rot_b0 - initial_rot_b0) > 0.01, "CL-01 bridge is not rotating!"
        assert abs(new_rot_b1 - initial_rot_b1) > 0.01, "CL-02 bridge is not rotating!"

        # Status 6: Test other shading modes: Normals and Clay
        print("\n6. Testing Normals and Clay shading modes on both bridges...")
        await page.evaluate("() => window.setShadingMode('normals')")
        await asyncio.sleep(0.5)
        s_norm = await get_bridge_status()
        assert s_norm["b1"]["visibleMeshCount"] > 0, "CL-02 vanished in Normals mode!"

        await page.evaluate("() => window.setShadingMode('clay')")
        await asyncio.sleep(0.5)
        s_clay = await get_bridge_status()
        assert s_clay["b1"]["visibleMeshCount"] > 0, "CL-02 vanished in Clay mode!"

        await page.evaluate("() => window.setShadingMode('pbr')")
        await asyncio.sleep(0.5)
        s_pbr_final = await get_bridge_status()
        assert s_pbr_final["b1"]["visibleMeshCount"] > 0, "CL-02 vanished in final PBR mode!"
        assert s_pbr_final["b1"]["invalidMatCount"] == 0, "CL-02 has invalid materials in final PBR!"
        await page.screenshot(path="/Users/inhausuxui/.gemini/antigravity/brain/81117592-88af-4153-89d7-7f876639c4f5/clarifier_fixed_5_final_proof.png")

        print("\nConsole errors check:", console_errors)
        assert len(console_errors) == 0, f"Detected console errors: {console_errors}"

        print("\n=========================================================================================")
        print("✅ VERIFIED: BOTH CLARIFIER BRIDGES FULLY FUNCTIONAL ACROSS ALL SHADING MODES & TOGGLES!")
        print("=========================================================================================")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
