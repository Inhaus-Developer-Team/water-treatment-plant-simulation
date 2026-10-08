import bpy
import bmesh
import math
import os

# Clear scene objects safely
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

# Materials for Field Engineer
mat_skin = create_pbr_material("EngineerSkin", (0.76, 0.58, 0.46), metallic=0.0, roughness=0.62)
mat_hair = create_pbr_material("EngineerHair", (0.12, 0.08, 0.05), metallic=0.0, roughness=0.85)
mat_vest_hi_vis = create_pbr_material("HiVisYellow", (0.82, 0.95, 0.05), metallic=0.0, roughness=0.55)
mat_reflective = create_pbr_material("ReflectiveSilver", (0.92, 0.94, 0.96), metallic=0.85, roughness=0.15, emission=(0.9, 0.9, 0.95), emission_strength=1.2)
mat_shirt = create_pbr_material("WorkShirtNavy", (0.10, 0.16, 0.28), metallic=0.0, roughness=0.80)
mat_pants = create_pbr_material("CargoPantsCharcoal", (0.18, 0.20, 0.22), metallic=0.0, roughness=0.85)
mat_hard_hat = create_pbr_material("HardHatWhite", (0.95, 0.95, 0.97), metallic=0.05, roughness=0.25, clearcoat=0.6)
mat_boot_leather = create_pbr_material("BootLeatherBrown", (0.35, 0.22, 0.12), metallic=0.0, roughness=0.65)
mat_boot_sole = create_pbr_material("BootSoleRubber", (0.05, 0.05, 0.05), metallic=0.0, roughness=0.90)
mat_gloves = create_pbr_material("WorkGlovesLeather", (0.82, 0.65, 0.35), metallic=0.0, roughness=0.70)
mat_radio = create_pbr_material("RadioBlack", (0.04, 0.04, 0.04), metallic=0.1, roughness=0.45)
mat_glasses = create_pbr_material("SafetyGlassesTint", (0.15, 0.22, 0.25), metallic=0.2, roughness=0.05, transmission=0.80)

engineer_root = bpy.data.objects.new("FieldEngineer", None)
bpy.context.scene.collection.objects.link(engineer_root)

def link_to_eng(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = engineer_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# 1. BOOTS & FEET (z: 0.00 to 0.15)
for side in [-1, 1]:
    foot_x = side * 0.14
    # Lugged rubber sole
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, 0.03, 0.025))
    sole = bpy.context.active_object
    sole.name = f"BootSole_{side}"
    sole.scale = (0.12, 0.28, 0.045)
    sole.data.materials.append(mat_boot_sole)
    link_to_eng(sole)
    
    # Heel lift
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, -0.06, 0.055))
    heel = bpy.context.active_object
    heel.name = f"BootHeel_{side}"
    heel.scale = (0.115, 0.10, 0.025)
    heel.data.materials.append(mat_boot_sole)
    link_to_eng(heel)
    
    # Leather upper shoe
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.14, location=(foot_x, 0.02, 0.10), rotation=(math.radians(10), 0, 0))
    upper = bpy.context.active_object
    upper.name = f"BootUpper_{side}"
    upper.data.materials.append(mat_boot_leather)
    link_to_eng(upper)
    
    # Boot toe cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.062, location=(foot_x, 0.08, 0.07))
    toe = bpy.context.active_object
    toe.name = f"BootToe_{side}"
    toe.scale = (1.0, 1.3, 0.75)
    toe.data.materials.append(mat_boot_leather)
    link_to_eng(toe)

# 2. LEGS & CARGO PANTS (z: 0.15 to 0.95)
for side in [-1, 1]:
    leg_x = side * 0.13
    # Lower leg / calf
    bpy.ops.mesh.primitive_cylinder_add(radius=0.072, depth=0.42, location=(leg_x, 0.01, 0.36))
    calf = bpy.context.active_object
    calf.name = f"Calf_{side}"
    calf.scale = (1.0, 1.05, 1.0)
    calf.data.materials.append(mat_pants)
    link_to_eng(calf)
    
    # Knee reinforcement patch
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(leg_x, 0.07, 0.55))
    knee = bpy.context.active_object
    knee.name = f"KneePatch_{side}"
    knee.scale = (0.11, 0.03, 0.14)
    knee.data.materials.append(mat_pants)
    link_to_eng(knee)
    
    # Thigh / upper leg
    bpy.ops.mesh.primitive_cylinder_add(radius=0.088, depth=0.42, location=(leg_x, 0.0, 0.74))
    thigh = bpy.context.active_object
    thigh.name = f"Thigh_{side}"
    thigh.scale = (1.0, 1.1, 1.0)
    thigh.data.materials.append(mat_pants)
    link_to_eng(thigh)
    
    # Cargo side pocket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(leg_x + side * 0.085, 0.0, 0.72))
    pocket = bpy.context.active_object
    pocket.name = f"CargoPocket_{side}"
    pocket.scale = (0.04, 0.14, 0.16)
    pocket.data.materials.append(mat_pants)
    link_to_eng(pocket)

# Pelvis & Belt
bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.18, location=(0, 0, 0.98))
pelvis = bpy.context.active_object
pelvis.name = "Pelvis"
pelvis.scale = (1.1, 0.95, 1.0)
pelvis.data.materials.append(mat_pants)
link_to_eng(pelvis)

bpy.ops.mesh.primitive_cylinder_add(radius=0.178, depth=0.045, location=(0, 0, 1.04))
belt = bpy.context.active_object
belt.name = "Belt"
belt.scale = (1.1, 0.95, 1.0)
belt.data.materials.append(mat_radio)
link_to_eng(belt)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.172, 1.04))
buckle = bpy.context.active_object
buckle.name = "BeltBuckle"
buckle.scale = (0.05, 0.02, 0.04)
buckle.data.materials.append(mat_reflective)
link_to_eng(buckle)

# 3. TORSO & HIGH-VIS SAFETY VEST (z: 1.05 to 1.48)
# Base shirt torso
bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.44, location=(0, 0, 1.25))
torso = bpy.context.active_object
torso.name = "TorsoShirt"
torso.scale = (1.15, 0.88, 1.0)
torso.data.materials.append(mat_shirt)
link_to_eng(torso)

# High-Vis Vest Outer Shell
bpy.ops.mesh.primitive_cylinder_add(radius=0.205, depth=0.42, location=(0, 0, 1.26))
vest = bpy.context.active_object
vest.name = "HiVisVest"
vest.scale = (1.16, 0.90, 1.0)
vest.data.materials.append(mat_vest_hi_vis)
link_to_eng(vest)

# Reflective Silver Strips (Horizontal chest & waist bands)
for vz in [1.14, 1.34]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.21, depth=0.045, location=(0, 0, vz))
    strip = bpy.context.active_object
    strip.name = f"ReflectiveStrip_{vz}"
    strip.scale = (1.17, 0.91, 1.0)
    strip.data.materials.append(mat_reflective)
    link_to_eng(strip)

# Vertical Shoulder Reflective Bands
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.12, 0.0, 1.36))
    v_strip = bpy.context.active_object
    v_strip.name = f"ReflectiveVStrip_{side}"
    v_strip.scale = (0.045, 0.20, 0.24)
    v_strip.data.materials.append(mat_reflective)
    link_to_eng(v_strip)

# Two-Way Radio on Left Chest Harness
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.14, 0.18, 1.36))
radio = bpy.context.active_object
radio.name = "HandheldRadio"
radio.scale = (0.05, 0.035, 0.11)
radio.data.materials.append(mat_radio)
link_to_eng(radio)

bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.12, location=(-0.14, 0.18, 1.46))
antenna = bpy.context.active_object
antenna.name = "RadioAntenna"
antenna.data.materials.append(mat_radio)
link_to_eng(antenna)

# 4. ARMS & HANDS - NATURALLY DOWN BY SIDES (User requirement!)
for side in [-1, 1]:
    arm_x = side * 0.26
    # Shoulder joint
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(arm_x, 0.0, 1.42))
    shoulder = bpy.context.active_object
    shoulder.name = f"Shoulder_{side}"
    shoulder.data.materials.append(mat_vest_hi_vis)
    link_to_eng(shoulder)
    
    # Upper arm (hanging slightly angled outward and down)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.058, depth=0.28, location=(arm_x + side * 0.02, 0.0, 1.27), rotation=(0, side * math.radians(-5), 0))
    upper_arm = bpy.context.active_object
    upper_arm.name = f"UpperArm_{side}"
    upper_arm.data.materials.append(mat_shirt)
    link_to_eng(upper_arm)
    
    # Forearm
    bpy.ops.mesh.primitive_cylinder_add(radius=0.052, depth=0.28, location=(arm_x + side * 0.03, 0.01, 1.02), rotation=(0, side * math.radians(-3), 0))
    forearm = bpy.context.active_object
    forearm.name = f"Forearm_{side}"
    forearm.data.materials.append(mat_shirt)
    link_to_eng(forearm)
    
    # Wrist / watch on left arm
    if side == -1:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.056, depth=0.03, location=(arm_x + side * 0.03, 0.01, 0.90))
        watch = bpy.context.active_object
        watch.name = "TacticalWatch"
        watch.data.materials.append(mat_radio)
        link_to_eng(watch)
        
    # Work glove hand
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(arm_x + side * 0.035, 0.01, 0.82))
    hand = bpy.context.active_object
    hand.name = f"GloveHand_{side}"
    hand.scale = (0.05, 0.08, 0.12)
    hand.data.materials.append(mat_gloves)
    link_to_eng(hand)

# 5. NECK & HEAD (z: 1.48 to 1.78)
bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.10, location=(0, 0, 1.51))
neck = bpy.context.active_object
neck.name = "Neck"
neck.data.materials.append(mat_skin)
link_to_eng(neck)

# Head & Jaw
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(0, 0.02, 1.62))
head = bpy.context.active_object
head.name = "Head"
head.scale = (0.95, 1.05, 1.15)
head.data.materials.append(mat_skin)
link_to_eng(head)

# Safety Glasses
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.13, 1.64))
glasses = bpy.context.active_object
glasses.name = "SafetyGlasses"
glasses.scale = (0.16, 0.025, 0.04)
glasses.data.materials.append(mat_glasses)
link_to_eng(glasses)

# Hard Hat Dome
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.135, location=(0, 0.01, 1.70))
hat_dome = bpy.context.active_object
hat_dome.name = "HardHatDome"
hat_dome.scale = (1.02, 1.12, 0.95)
hat_dome.data.materials.append(mat_hard_hat)
link_to_eng(hat_dome)

# Hard Hat Front Brim
bpy.ops.mesh.primitive_cylinder_add(radius=0.165, depth=0.018, location=(0, 0.03, 1.66), rotation=(math.radians(5), 0, 0))
hat_brim = bpy.context.active_object
hat_brim.name = "HardHatBrim"
hat_brim.scale = (1.0, 1.15, 1.0)
hat_brim.data.materials.append(mat_hard_hat)
link_to_eng(hat_brim)

# Hard Hat Top Crown Ridge
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.01, 1.78))
hat_ridge = bpy.context.active_object
hat_ridge.name = "HardHatRidge"
hat_ridge.scale = (0.045, 0.20, 0.035)
hat_ridge.data.materials.append(mat_hard_hat)
link_to_eng(hat_ridge)

# Export as GLB
out_path = "/Users/inhausuxui/.gemini/antigravity/scratch/water-treatment-plant-simulation/assets/models/field_engineer.glb"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {out_path} ({os.path.getsize(out_path)} bytes)")
