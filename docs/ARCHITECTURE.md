# 📐 System Architecture & Civil Engineering Layout

## 1. Civil Coordinate & Spatial Layout

The digital twin facility occupies a 120m × 120m site envelope enclosed by boundary tree buffers and an outer perimeter asphalt roadway loop. Equipment pads are cast from reinforced concrete (`#88929b`) with chamfered foundations and perimeter curbs.

```
+-----------------------------------------------------------------------------------------+
|                                  NORTH PERIMETER ROAD                                   |
|                                                                                         |
|                      [ STORMWATER RETENTION WETLAND LAGOON ]                            |
|                                (0.5, 0.08, -22.5)                                       |
|                                        ▲                                                |
|                                        │ Stepped Rock Cascade Weir                      |
|                  [ CLEAN EFFLUENT PARSHALL FLUME OUTFALL ]                              |
|                              (0.5, 0.0, -14.2)                                          |
|                                        ▲                                                |
|                                        │ Polished Disinfected Weir                      |
|                 [ TERTIARY SAND FILTRATION & UV COMPLEX ]                               |
|                              (0.5, 0.0, -9.6)                                           |
|                              ▲                ▲                                         |
|                  West Flume  │                │ East Flume                              |
|         [ CLARIFIER CL-01 ] ─┘                └─ [ CLARIFIER CL-02 ]                    |
|          (-4.5, 0.0, -4.5)                        (5.5, 0.0, -4.5)                      |
|                  ▲                                        ▲                             |
|                  └────────── [ FLOW SPLITTER ] ───────────┘                             |
|                               (0.5, 0.0, 1.2)                                           |
|                                      ▲                                                  |
|                                      │ Mixed Liquor (MLSS) Channel                      |
| [ BLOWER BUILDING ] ──► [ BIOLOGICAL AERATION BASIN ] ◄── [ RAW HEADWORKS ]             |
|  (-11.5, 0.0, 7.5)           (6.0, 0.0, 7.5)                 (18.0, 0.0, 7.5)           |
|         │                           ▲                                                   |
|         └─ Pipe Gantry Bridge ──────┘                                                   |
|                                                                                         |
|                                  SOUTH ENTRANCE ROAD                                    |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Structural & Mechanical Subsystems

### 2.1 Pipe Gantry Truss Bridge
* **Location**: Corridor between Blower Building and Aeration Basin (`x = -7.5` to `x = -1.0`).
* **Clearance**: Minimum vehicular headroom of **4.20 meters** (13'-9") over the 5.0m wide asphalt access roadway.
* **Superstructure**: Structural steel A-frame vertical lattice towers, horizontal box truss beam, safety yellow hazard clearance fascia, and pipe saddles with vibration damping pads.
* **Piping**: 500mm OD insulated low-pressure compressed air header running from blower compressor room with 90° radius bends into the aeration basin distribution manifold.

### 2.2 Secondary Clarifier Mechanical Scrapers
* **Diameter**: 16.0 meters center-feed circular clarifiers.
* **Bridge Mechanism**: Full-diameter structural steel bridge with 1.1m safety handrails, rotating continuously around the central concrete pier via a peripheral drive motor with slip ring electrical feed.
* **Submerged Rakes**: Angled squeegee blades plowing settled biological sludge toward the central collection hopper.

### 2.3 Tertiary Sand Filters & UV Disinfection
* **Structure**: Monolithic reinforced concrete tankage divided by a central longitudinal wall.
* **Filter Bays**: Granular media beds (anthracite cap over silica sand over garnet support gravel), equipped with stainless steel surface wash troughs and blue backwash manifold headers.
* **UV Disinfection Channels**: Multi-pass serpentine concrete channels housing submersible racks of medium-pressure ultraviolet lamps with electronic ballasts, emitting actinic blue/violet radiation to destroy pathogenic DNA.

---

## 3. Shading & Graphics Pipeline

The Three.js scene uses a multi-tier rendering architecture:

1. **Geometry Generation**:
   * All procedural meshes share optimized primitive geometries (`BoxGeometry`, `CylinderGeometry`, `TorusGeometry`, `PlaneGeometry`).
   * Vegetation tufts are merged into single instances with `BufferGeometryUtils.mergeGeometries`, reducing 8,400 individual planes to 2,800 instanced calls rendered in **1 single WebGL draw call**.
2. **Procedural Canvas Textures**:
   * Real-time in-memory HTML5 2D canvas generation for site terrain asphalt/concrete/turf masks, realistic cumulus cloud dome, foam bubbles, and brushed aluminum finishes.
3. **Lighting & Post-Processing**:
   * **Directional Sun Light**: Warm sunlight (`#fffdf5`, intensity 2.8) with 2048×2048 PCF soft shadow maps.
   * **Ambient & Sky Dome**: Rayleigh physical sky shader coupled with high-altitude cumulus cloud dome.
   * **Composer**: `EffectComposer` pipeline chaining `RenderPass`, `UnrealBloomPass` (subtle glow on water highlights and UV lamps), and `OutputPass` with ACES Filmic Tone Mapping.
