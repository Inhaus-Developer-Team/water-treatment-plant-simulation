import bpy
import bmesh
import math
import os

# Clear scene safely
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh, do_unlink=True)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat, do_unlink=True)

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, clearcoat=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = clearcoat
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = clearcoat
    return mat

mat_concrete = create_pbr_material("ConcretePier", (0.66, 0.65, 0.63), metallic=0.05, roughness=0.88)
mat_galv_steel = create_pbr_material("StructuralGalvSteel", (0.62, 0.65, 0.68), metallic=0.88, roughness=0.30)
mat_stainless = create_pbr_material("StainlessSteel316", (0.86, 0.88, 0.90), metallic=0.94, roughness=0.16)
mat_safety_yellow = create_pbr_material("SafetyYellowRailing", (0.95, 0.78, 0.04), metallic=0.18, roughness=0.32)
mat_motor_teal = create_pbr_material("DriveMotorTeal", (0.10, 0.42, 0.48), metallic=0.40, roughness=0.34)
mat_scum_poly = create_pbr_material("ScumBladeNeoprene", (0.12, 0.12, 0.14), metallic=0.05, roughness=0.75)
mat_scum_arm = create_pbr_material("ScumArmOrange", (0.88, 0.42, 0.08), metallic=0.20, roughness=0.42)
mat_life_ring = create_pbr_material("LifeRingOrange", (0.95, 0.30, 0.04), metallic=0.05, roughness=0.35)
mat_white_tape = create_pbr_material("ReflectiveWhite", (0.95, 0.96, 0.98), metallic=0.10, roughness=0.25)

clarifier_root = bpy.data.objects.new("ClarifierBridgeMechanism", None)
bpy.context.scene.collection.objects.link(clarifier_root)

def link_to_mech(obj, smooth=True):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = clarifier_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# =========================================================================
# 1. CENTER CONCRETE PIER, BOLTED SLEWING RING TURNTABLE & PLANETARY DRIVE
# =========================================================================
bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.28, depth=1.40, location=(0, 0, 0.70))
pier = bpy.context.active_object
pier.name = "CenterConcretePier"
pier.data.materials.append(mat_concrete)
link_to_mech(pier)

# Heavy Cast Turntable Base Flange with 16 Perimeter Bolts
bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.42, depth=0.12, location=(0, 0, 1.46))
turntable = bpy.context.active_object
turntable.name = "SlewingRingTurntable"
turntable.data.materials.append(mat_stainless)
link_to_mech(turntable)

for b_idx in range(16):
    ang = 2.0 * math.pi * b_idx / 16
    bx = math.cos(ang) * 0.38
    by = math.sin(ang) * 0.38
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.03, location=(bx, by, 1.53))
    bolt = bpy.context.active_object
    bolt.name = f"TurntableBolt_{b_idx}"
    bolt.data.materials.append(mat_stainless)
    link_to_mech(bolt)

# Center Energy-Dissipating Inlet Feedwell Drum with Flow-Diffuser Ports & Stiffener Ribs
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.76, depth=0.68, location=(0, 0, 1.05))
feedwell = bpy.context.active_object
feedwell.name = "CenterFeedwellBaffle"
feedwell.data.materials.append(mat_galv_steel)
link_to_mech(feedwell)

# Top & Bottom Angle-Iron Stiffener Rings on Feedwell
for fz in [0.74, 1.37]:
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=12, major_radius=0.77, minor_radius=0.022, location=(0, 0, fz))
    fring = bpy.context.active_object
    fring.name = f"FeedwellStiffener_{fz}"
    fring.data.materials.append(mat_stainless)
    link_to_mech(fring)

# 8 Tangential Energy-Dissipating Diffuser Ports around Feedwell
for p_idx in range(8):
    ang = 2.0 * math.pi * p_idx / 8
    px = math.cos(ang) * 0.76
    py = math.sin(ang) * 0.76
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, 1.12), rotation=(0, 0, ang))
    port = bpy.context.active_object
    port.name = f"FeedwellDiffuserPort_{p_idx}"
    port.scale = (0.04, 0.22, 0.16)
    port.data.materials.append(mat_scum_poly)
    link_to_mech(port)

# Planetary Reduction Gearbox, TEFC Finned Drive Motor & Local Control Panel on Center Pier
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.20, depth=0.30, location=(0, 0, 1.67))
gearbox = bpy.context.active_object
gearbox.name = "PlanetaryGearbox"
gearbox.data.materials.append(mat_motor_teal)
link_to_mech(gearbox)

bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.13, depth=0.38, location=(0, 0, 2.01))
motor = bpy.context.active_object
motor.name = "TEFC_DriveMotor"
motor.data.materials.append(mat_motor_teal)
link_to_mech(motor)

# Motor Radial Cooling Fins
for fin_z in [1.90, 1.96, 2.02, 2.08, 2.14]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.145, depth=0.008, location=(0, 0, fin_z))
    fin = bpy.context.active_object
    fin.name = f"MotorCoolingFin_{fin_z}"
    fin.data.materials.append(mat_motor_teal)
    link_to_mech(fin)

# Stainless Steel Local Disconnect / Torque Monitor Enclosure on Center Platform
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.28, 0.24, 1.98), rotation=(0, 0, math.radians(-35)))
lcp = bpy.context.active_object
lcp.name = "TorqueMonitorPanel"
lcp.scale = (0.14, 0.24, 0.32)
lcp.data.materials.append(mat_stainless)
link_to_mech(lcp)

# =========================================================================
# 2. RADIAL LATTICE TRUSS BRIDGE WALKWAY (Spans x = 0.0 to 3.4m)
# =========================================================================
bridge_length = 3.40
bridge_cx = bridge_length * 0.5

# Upper & Lower Structural Truss Chords + Diagonal Warren Truss Webbing
for by in [-0.30, 0.30]:
    # Lower structural channel chord
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.46))
    l_chord = bpy.context.active_object
    l_chord.name = f"LowerTrussChord_{by}"
    l_chord.scale = (bridge_length, 0.07, 0.12)
    l_chord.data.materials.append(mat_galv_steel)
    link_to_mech(l_chord)
    
    # Sub-deck truss bottom stringer
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.24))
    b_chord = bpy.context.active_object
    b_chord.name = f"BottomTrussStringer_{by}"
    b_chord.scale = (bridge_length * 0.92, 0.05, 0.06)
    b_chord.data.materials.append(mat_galv_steel)
    link_to_mech(b_chord)
    
    # Diagonal Warren truss web members between z=1.24 and z=1.46
    for t_idx in range(8):
        tx = 0.35 + t_idx * 0.38
        ang = math.radians(32 if t_idx % 2 == 0 else -32)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tx, by, 1.35), rotation=(0, ang, 0))
        diag = bpy.context.active_object
        diag.name = f"TrussWeb_{by}_{t_idx}"
        diag.scale = (0.36, 0.03, 0.03)
        diag.data.materials.append(mat_galv_steel)
        link_to_mech(diag)

# Non-Slip Bar Grating Walkway Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, 0, 1.54))
deck = bpy.context.active_object
deck.name = "WalkwayGratingDeck"
deck.scale = (bridge_length, 0.68, 0.035)
deck.data.materials.append(mat_stainless)
link_to_mech(deck)

# Transverse walkway cross-ribs every 0.35m for realistic grating texture
for r_idx in range(10):
    rx = 0.20 + r_idx * 0.34
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, 0, 1.562))
    rib = bpy.context.active_object
    rib.name = f"GratingCrossBar_{r_idx}"
    rib.scale = (0.025, 0.66, 0.01)
    rib.data.materials.append(mat_galv_steel)
    link_to_mech(rib)

# OSHA Tubular Safety Railings (Top rail, mid rail, 4" kickplate, stanchions & corner elbows)
for by in [-0.34, 0.34]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.019, depth=bridge_length, location=(bridge_cx, by, 2.46), rotation=(0, math.pi/2, 0))
    top_rail = bpy.context.active_object
    top_rail.name = f"HandrailTop_{by}"
    top_rail.data.materials.append(mat_safety_yellow)
    link_to_mech(top_rail)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=bridge_length, location=(bridge_cx, by, 2.02), rotation=(0, math.pi/2, 0))
    mid_rail = bpy.context.active_object
    mid_rail.name = f"HandrailMid_{by}"
    mid_rail.data.materials.append(mat_safety_yellow)
    link_to_mech(mid_rail)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.62))
    kick = bpy.context.active_object
    kick.name = f"KickPlate_{by}"
    kick.scale = (bridge_length, 0.015, 0.11)
    kick.data.materials.append(mat_safety_yellow)
    link_to_mech(kick)
    
    for px in range(6):
        sx = 0.15 + px * 0.64
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.92, location=(sx, by, 2.02))
        stanch = bpy.context.active_object
        stanch.name = f"Stanchion_{by}_{px}"
        stanch.data.materials.append(mat_safety_yellow)
        link_to_mech(stanch)

# Safety Lifebuoy Ring with 4 Reflective White Bands on Bridge Railing
bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=16, major_radius=0.20, minor_radius=0.046, location=(1.75, 0.37, 2.08), rotation=(math.pi/2, 0, 0))
ring = bpy.context.active_object
ring.name = "SafetyLifeRing"
ring.data.materials.append(mat_life_ring)
link_to_mech(ring)

for band_ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
    bx = 1.75 + math.cos(band_ang) * 0.20
    bz = 2.08 + math.sin(band_ang) * 0.20
    bpy.ops.mesh.primitive_cylinder_add(radius=0.050, depth=0.045, location=(bx, 0.37, bz), rotation=(0, math.pi/2 - band_ang, 0))
    tape = bpy.context.active_object
    tape.name = f"LifebuoyTape_{band_ang:.2f}"
    tape.data.materials.append(mat_white_tape)
    link_to_mech(tape)

# =========================================================================
# 3. SUBMERGED SLUDGE SCRAPER RAKE ARMS, SQUEEGEE BLADES & SURFACE SCUM SKIMMER
# =========================================================================
# Vertical Torque Cage Hangers descending from bridge to submerged rake arm
for hx in [0.95, 1.85, 2.75]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.72, location=(hx, -0.18, 1.05))
    hanger = bpy.context.active_object
    hanger.name = f"RakeTorqueHanger_{hx}"
    hanger.data.materials.append(mat_galv_steel)
    link_to_mech(hanger)

# Submerged Bottom Rake Truss Arm & Angled Plow Blades (Sweeps settled sludge to center cone)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.85, -0.18, 0.72))
rake_beam = bpy.context.active_object
rake_beam.name = "SubmergedRakeArm"
rake_beam.scale = (2.45, 0.06, 0.08)
rake_beam.data.materials.append(mat_galv_steel)
link_to_mech(rake_beam)

for b_idx in range(6):
    bx = 0.85 + b_idx * 0.38
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, -0.24, 0.65), rotation=(0, 0, math.radians(35)))
    plow = bpy.context.active_object
    plow.name = f"SludgeScraperBlade_{b_idx}"
    plow.scale = (0.28, 0.02, 0.14)
    plow.data.materials.append(mat_stainless)
    link_to_mech(plow)

# Surface Scum Skimmer Arm, Pivoting Neoprene Wiper Blade & Scum Box Trough
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.05, -0.44, 1.18))
skimmer_arm = bpy.context.active_object
skimmer_arm.name = "SurfaceScumSkimmerArm"
skimmer_arm.scale = (2.35, 0.04, 0.12)
skimmer_arm.data.materials.append(mat_scum_arm)
link_to_mech(skimmer_arm)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.05, -0.47, 1.10))
wiper = bpy.context.active_object
wiper.name = "NeopreneScumWiper"
wiper.scale = (2.35, 0.02, 0.14)
wiper.data.materials.append(mat_scum_poly)
link_to_mech(wiper)

# Peripheral Scum Beach / Collection Box near outer launder wall
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.05, 0.45, 1.12))
scum_box = bpy.context.active_object
scum_box.name = "ScumCollectionBox"
scum_box.scale = (0.42, 0.38, 0.24)
scum_box.data.materials.append(mat_stainless)
link_to_mech(scum_box)

# =========================================================================
# 4. END TRACTION DRIVE BOGIE TRUCK & DUAL FLANGED BOGIE WHEELS ON RIM
# =========================================================================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.35, 0, 1.48))
carriage = bpy.context.active_object
carriage.name = "EndTractionBogie"
carriage.scale = (0.32, 0.78, 0.22)
carriage.data.materials.append(mat_galv_steel)
link_to_mech(carriage)

# Outrigger Gearmotor on Traction Bogie
bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.26, location=(3.35, 0.28, 1.64), rotation=(0, math.pi/2, 0))
bogie_motor = bpy.context.active_object
bogie_motor.name = "TractionBogieMotor"
bogie_motor.data.materials.append(mat_motor_teal)
link_to_mech(bogie_motor)

for wy in [-0.30, 0.30]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.13, depth=0.09, location=(3.35, wy, 1.34), rotation=(0, math.pi/2, 0))
    wheel = bpy.context.active_object
    wheel.name = f"RimTractionWheel_{wy}"
    wheel.data.materials.append(mat_scum_arm)
    link_to_mech(wheel)

# Export as GLB
out_path = "/Users/inhausuxui/.gemini/antigravity/scratch/water-treatment-plant-simulation/assets/models/clarifier_drive.glb"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {out_path} ({os.path.getsize(out_path)} bytes)")
