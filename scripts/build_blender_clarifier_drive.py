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
        
    return mat

mat_concrete = create_pbr_material("ConcretePier", (0.68, 0.67, 0.65), metallic=0.05, roughness=0.88)
mat_galv_steel = create_pbr_material("StructuralGalvSteel", (0.58, 0.60, 0.62), metallic=0.85, roughness=0.35)
mat_stainless = create_pbr_material("StainlessSteel304", (0.85, 0.86, 0.88), metallic=0.92, roughness=0.18)
mat_safety_yellow = create_pbr_material("SafetyYellowRailing", (0.95, 0.78, 0.05), metallic=0.15, roughness=0.35)
mat_motor_teal = create_pbr_material("DriveMotorTeal", (0.12, 0.42, 0.48), metallic=0.35, roughness=0.40)
mat_scum_poly = create_pbr_material("ScumBladePoly", (0.85, 0.45, 0.12), metallic=0.05, roughness=0.50)
mat_life_ring = create_pbr_material("LifeRingOrange", (0.95, 0.32, 0.05), metallic=0.05, roughness=0.40)

clarifier_root = bpy.data.objects.new("ClarifierBridgeMechanism", None)
bpy.context.scene.collection.objects.link(clarifier_root)

def link_to_mech(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = clarifier_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# 1. SLENDER CENTER PIER & TURNTABLE DRIVE
# Concrete center pier (radius 0.28m, height 1.4m)
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=1.40, location=(0, 0, 0.70))
pier = bpy.context.active_object
pier.name = "CenterConcretePier"
pier.data.materials.append(mat_concrete)
link_to_mech(pier)

# Slewing ring bearing / turntable (radius 0.38m, height 0.12m)
bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.12, location=(0, 0, 1.46))
turntable = bpy.context.active_object
turntable.name = "SlewingRingBearing"
turntable.data.materials.append(mat_stainless)
link_to_mech(turntable)

# Center Feedwell (Realistic compact baffle: radius 0.75m, height 0.65m, submerged around water line)
bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.65, location=(0, 0, 1.05))
feedwell = bpy.context.active_object
feedwell.name = "CenterFeedwellBaffle"
feedwell.data.materials.append(mat_galv_steel)
link_to_mech(feedwell)

# Planetary reduction drive motor atop Center Turntable
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.32, location=(0, 0, 1.68))
gearbox = bpy.context.active_object
gearbox.name = "PlanetaryGearbox"
gearbox.data.materials.append(mat_motor_teal)
link_to_mech(gearbox)

bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.38, location=(0, 0, 2.03))
motor = bpy.context.active_object
motor.name = "DriveMotor"
motor.data.materials.append(mat_motor_teal)
link_to_mech(motor)

# 2. ROTATING RADIAL BRIDGE WALKWAY (Spans from center x=0 to rim x=3.4m)
bridge_length = 3.4
bridge_cx = bridge_length * 0.5

# Main I-Beams
for by in [-0.28, 0.28]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.48))
    beam = bpy.context.active_object
    beam.name = f"BridgeIBeam_{by}"
    beam.scale = (bridge_length, 0.08, 0.16)
    beam.data.materials.append(mat_galv_steel)
    link_to_mech(beam)

# Diamond Plate Walkway Deck
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, 0, 1.57))
deck = bpy.context.active_object
deck.name = "WalkwayDeck"
deck.scale = (bridge_length, 0.68, 0.03)
deck.data.materials.append(mat_stainless)
link_to_mech(deck)

# OSHA Safety Railings (Top rail, mid rail, kickplate) along both sides
for by in [-0.34, 0.34]:
    # Top handrail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=bridge_length, location=(bridge_cx, by, 2.45), rotation=(0, math.pi/2, 0))
    top_rail = bpy.context.active_object
    top_rail.name = f"HandrailTop_{by}"
    top_rail.data.materials.append(mat_safety_yellow)
    link_to_mech(top_rail)
    
    # Mid safety rail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=bridge_length, location=(bridge_cx, by, 2.02), rotation=(0, math.pi/2, 0))
    mid_rail = bpy.context.active_object
    mid_rail.name = f"HandrailMid_{by}"
    mid_rail.data.materials.append(mat_safety_yellow)
    link_to_mech(mid_rail)
    
    # Kickplate (Toe board)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, by, 1.63))
    kick = bpy.context.active_object
    kick.name = f"KickPlate_{by}"
    kick.scale = (bridge_length, 0.012, 0.10)
    kick.data.materials.append(mat_safety_yellow)
    link_to_mech(kick)
    
    # Stanchions every 0.75m
    for px in range(1, 5):
        sx = px * 0.72
        bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.92, location=(sx, by, 2.04))
        stanch = bpy.context.active_object
        stanch.name = f"Stanchion_{by}_{px}"
        stanch.data.materials.append(mat_safety_yellow)
        link_to_mech(stanch)

# Safety Lifebuoy ring on bridge stanchion
bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.045, location=(1.8, 0.36, 2.05), rotation=(0, math.pi/2, 0))
ring = bpy.context.active_object
ring.name = "SafetyLifeRing"
ring.data.materials.append(mat_life_ring)
link_to_mech(ring)

# Submerged Scum Skimmer Blade (dips into water)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_cx, -0.42, 1.18))
skimmer = bpy.context.active_object
skimmer.name = "ScumSkimmerBlade"
skimmer.scale = (bridge_length * 0.85, 0.03, 0.18)
skimmer.data.materials.append(mat_scum_poly)
link_to_mech(skimmer)

# End Traction Drive Carriage (Rides on outer tank rim at x=3.35m)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.35, 0, 1.48))
carriage = bpy.context.active_object
carriage.name = "EndDriveCarriage"
carriage.scale = (0.28, 0.72, 0.22)
carriage.data.materials.append(mat_galv_steel)
link_to_mech(carriage)

# Polyurethane drive wheels
for wy in [-0.28, 0.28]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.08, location=(3.35, wy, 1.34), rotation=(0, math.pi/2, 0))
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
