import bpy
import bmesh
import math
import os

# Clear scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh, do_unlink=True)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat, do_unlink=True)

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, clearcoat=0.0, transmission=0.0, emission=None, emission_strength=1.0):
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
        
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = transmission
        
    if emission:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*emission, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
            
    return mat

# Materials
mat_concrete = create_pbr_material("ConcreteFormwork", (0.68, 0.67, 0.65), metallic=0.05, roughness=0.88)
mat_galv_steel = create_pbr_material("StructuralGalvSteel", (0.58, 0.60, 0.62), metallic=0.85, roughness=0.35)
mat_stainless = create_pbr_material("StainlessSteel304", (0.85, 0.86, 0.88), metallic=0.92, roughness=0.20)
mat_safety_yellow = create_pbr_material("SafetyYellowRailing", (0.95, 0.78, 0.05), metallic=0.15, roughness=0.35)
mat_motor_teal = create_pbr_material("DriveMotorTeal", (0.12, 0.42, 0.48), metallic=0.35, roughness=0.40)
mat_scum_poly = create_pbr_material("ScumBladePoly", (0.85, 0.45, 0.12), metallic=0.05, roughness=0.50)

clarifier_root = bpy.data.objects.new("ClarifierBridgeMechanism", None)
bpy.context.scene.collection.objects.link(clarifier_root)

def link_to_mech(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = clarifier_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# 1. CENTER PIER & TURNTABLE DRIVE
# Center concrete column (z: -1.0 to 1.2)
bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=2.4, location=(0, 0, 0.2))
pier = bpy.context.active_object
pier.name = "CenterConcretePier"
pier.data.materials.append(mat_concrete)
link_to_mech(pier)

# Slewing ring bearing / turntable
bpy.ops.mesh.primitive_cylinder_add(radius=1.15, depth=0.18, location=(0, 0, 1.45))
turntable = bpy.context.active_object
turntable.name = "SlewingRingBearing"
turntable.data.materials.append(mat_stainless)
link_to_mech(turntable)

# Center Feedwell (Cylindrical energy-dissipating baffle, radius 2.6m, depth 2.2m)
bpy.ops.mesh.primitive_cylinder_add(radius=2.6, depth=2.2, location=(0, 0, 0.2))
feedwell = bpy.context.active_object
feedwell.name = "CenterFeedwellBaffle"
feedwell.data.materials.append(mat_galv_steel)
link_to_mech(feedwell)

# Electric Drive Motor & Gearbox atop Center Turntable
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.85))
gearbox = bpy.context.active_object
gearbox.name = "PlanetaryGearbox"
gearbox.scale = (0.75, 0.75, 0.55)
gearbox.data.materials.append(mat_motor_teal)
link_to_mech(gearbox)

bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.55, location=(0, 0, 2.38))
motor = bpy.context.active_object
motor.name = "DriveMotor"
motor.data.materials.append(mat_motor_teal)
link_to_mech(motor)

bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.24, location=(0, 0, 2.72))
slip_ring = bpy.context.active_object
slip_ring.name = "CollectorSlipRing"
slip_ring.data.materials.append(mat_stainless)
link_to_mech(slip_ring)

# 2. ROTATING RADIAL BRIDGE (Spans from center x=0 to rim x=14.0m)
bridge_length = 14.0
bridge_cx = bridge_length * 0.5

# Main Twin I-Beams (Galvanized structural steel)
for by in [-0.55, 0.55]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.55))
    beam = bpy.context.active_object
    beam.name = f"BridgeIBeam_{by}"
    beam.scale = (bridge_length, 0.14, 0.38)
    beam.data.materials.append(mat_galv_steel)
    link_to_mech(beam)

# Diamond Plate Walkway Decking
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, 0, 1.76))
deck = bpy.context.active_object
deck.name = "WalkwayDeck"
deck.scale = (bridge_length, 1.30, 0.04)
deck.data.materials.append(mat_stainless)
link_to_mech(deck)

# Safety Railings (Top rail, mid rail, kickplate) along both sides
for by in [-0.62, 0.62]:
    # Top handrail (height 1.1m)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=bridge_length, location=(bridge_cx, by, 2.85), rotation=(0, math.pi/2, 0))
    top_rail = bpy.context.active_object
    top_rail.name = f"HandrailTop_{by}"
    top_rail.data.materials.append(mat_safety_yellow)
    link_to_mech(top_rail)
    
    # Mid safety rail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=bridge_length, location=(bridge_cx, by, 2.30), rotation=(0, math.pi/2, 0))
    mid_rail = bpy.context.active_object
    mid_rail.name = f"HandrailMid_{by}"
    mid_rail.data.materials.append(mat_safety_yellow)
    link_to_mech(mid_rail)
    
    # Kickplate (Toe board)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.84))
    kick = bpy.context.active_object
    kick.name = f"KickPlate_{by}"
    kick.scale = (bridge_length, 0.015, 0.12)
    kick.data.materials.append(mat_safety_yellow)
    link_to_mech(kick)
    
    # Stanchion posts every 1.75m
    for px in range(1, 9):
        sx = px * 1.65
        bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=1.10, location=(sx, by, 2.30))
        stanch = bpy.context.active_object
        stanch.name = f"Stanchion_{by}_{px}"
        stanch.data.materials.append(mat_safety_yellow)
        link_to_mech(stanch)

# 3. UNDERWATER SLUDGE SCRAPER ARMS & SURFACE SCUM SKIMMER
# Surface Scum Skimmer Arm
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, -0.75, 1.10))
skimmer = bpy.context.active_object
skimmer.name = "ScumSkimmerBlade"
skimmer.scale = (bridge_length * 0.9, 0.05, 0.28)
skimmer.data.materials.append(mat_scum_poly)
link_to_mech(skimmer)

# End Traction Drive Carriage (Rides on outer tank rim at x=14.0m)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(13.9, 0, 1.55))
carriage = bpy.context.active_object
carriage.name = "EndDriveCarriage"
carriage.scale = (0.75, 1.45, 0.42)
carriage.data.materials.append(mat_galv_steel)
link_to_mech(carriage)

# Polyurethane drive wheels riding on tank coping
for wy in [-0.55, 0.55]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.12, location=(13.9, wy, 1.25), rotation=(0, math.pi/2, 0))
    wheel = bpy.context.active_object
    wheel.name = f"RimTractionWheel_{wy}"
    wheel.data.materials.append(mat_scum_poly)
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
