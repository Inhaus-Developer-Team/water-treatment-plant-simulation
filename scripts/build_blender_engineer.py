import bpy
import bmesh
import math
import os
import random

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
mat_skin = create_pbr_material("EngineerSkin", (0.78, 0.57, 0.44), metallic=0.0, roughness=0.52)
mat_lips = create_pbr_material("EngineerLips", (0.68, 0.42, 0.36), metallic=0.0, roughness=0.45)
mat_hair = create_pbr_material("EngineerHair", (0.14, 0.09, 0.05), metallic=0.0, roughness=0.82)
mat_vest_hi_vis = create_pbr_material("HiVisYellow", (0.85, 0.96, 0.04), metallic=0.0, roughness=0.48)
mat_vest_trim = create_pbr_material("VestTrimOrange", (0.95, 0.38, 0.04), metallic=0.0, roughness=0.55)
mat_reflective = create_pbr_material("ReflectiveSilver", (0.94, 0.96, 0.98), metallic=0.88, roughness=0.14, emission=(0.85, 0.88, 0.92), emission_strength=0.6)
mat_shirt = create_pbr_material("WorkShirtNavy", (0.09, 0.17, 0.30), metallic=0.0, roughness=0.78)
mat_pants = create_pbr_material("CargoPantsCharcoal", (0.17, 0.19, 0.22), metallic=0.0, roughness=0.82)
mat_knee_pad = create_pbr_material("CorduraKneeBlack", (0.08, 0.09, 0.10), metallic=0.05, roughness=0.72)
mat_hard_hat = create_pbr_material("HardHatWhite", (0.96, 0.96, 0.98), metallic=0.05, roughness=0.18, clearcoat=0.85)
mat_hat_band = create_pbr_material("HardHatSuspension", (0.15, 0.16, 0.18), metallic=0.1, roughness=0.60)
mat_boot_leather = create_pbr_material("BootLeatherTan", (0.46, 0.29, 0.14), metallic=0.0, roughness=0.62)
mat_boot_sole = create_pbr_material("BootSoleRubber", (0.05, 0.05, 0.05), metallic=0.0, roughness=0.88)
mat_gloves = create_pbr_material("WorkGlovesLeather", (0.82, 0.64, 0.32), metallic=0.0, roughness=0.68)
mat_glove_cuff = create_pbr_material("GloveCuffBlack", (0.12, 0.12, 0.14), metallic=0.0, roughness=0.75)
mat_radio = create_pbr_material("RadioBlack", (0.04, 0.04, 0.05), metallic=0.15, roughness=0.40)
mat_glasses_frame = create_pbr_material("GlassesFrame", (0.05, 0.05, 0.06), metallic=0.3, roughness=0.25)
mat_glasses_lens = create_pbr_material("SafetyGlassesLens", (0.12, 0.22, 0.28), metallic=0.25, roughness=0.04, transmission=0.82)
mat_badge = create_pbr_material("IDBadgeWhite", (0.92, 0.95, 0.98), metallic=0.05, roughness=0.22)
mat_hydro_blue = create_pbr_material("HydroAccentBlue", (0.04, 0.48, 0.88), metallic=0.2, roughness=0.30)

engineer_root = bpy.data.objects.new("FieldEngineer", None)
bpy.context.scene.collection.objects.link(engineer_root)

def link_to_eng(obj, smooth=True, subdiv=0):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = engineer_root
    if obj.type == 'MESH':
        if subdiv > 0:
            mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
            mod.levels = subdiv
            mod.render_levels = subdiv
        if smooth:
            for poly in obj.data.polygons:
                poly.use_smooth = True

def create_OrganicLimb(name, points_radii, material, segments=24):
    """Creates a smooth organic lofted mesh along a 3D spine with varying cross-section radii (rx, ry)"""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for (x, y, z, rx, ry) in points_radii:
        ring = []
        for s in range(segments):
            ang = 2.0 * math.pi * s / segments
            vx = x + math.cos(ang) * rx
            vy = y + math.sin(ang) * ry
            vz = z
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        for s in range(segments):
            s_next = (s + 1) % segments
            bm.faces.new((r1[s], r1[s_next], r2[s_next], r2[s]))
    # Cap ends
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    link_to_eng(obj, smooth=True, subdiv=1)
    return obj

# =========================================================================
# 1. WORK BOOTS WITH LUGGED SOLES, HEEL, ANKLE COLLAR & LACES (z: 0.00 to 0.16)
# =========================================================================
for side in [-1, 1]:
    fx = side * 0.115
    # Contoured Lugged Rubber Sole
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, 0.035, 0.022))
    sole = bpy.context.active_object
    sole.name = f"BootSole_{side}"
    sole.scale = (0.105, 0.27, 0.042)
    sole.data.materials.append(mat_boot_sole)
    link_to_eng(sole, subdiv=1)
    
    # Defined heel block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, -0.055, 0.015))
    heel = bpy.context.active_object
    heel.name = f"BootHeel_{side}"
    heel.scale = (0.102, 0.09, 0.03)
    heel.data.materials.append(mat_boot_sole)
    link_to_eng(heel, subdiv=1)
    
    # Sculpted leather boot upper (vamp + quarter + steel toe)
    boot_pts = [
        (fx, -0.04, 0.04, 0.048, 0.065),
        (fx, 0.03, 0.065, 0.052, 0.125),
        (fx, 0.01, 0.105, 0.048, 0.085),
        (fx, -0.01, 0.155, 0.046, 0.055),
        (fx, -0.01, 0.185, 0.048, 0.056),
    ]
    create_OrganicLimb(f"BootUpper_{side}", boot_pts, mat_boot_leather, segments=20)
    
    # Rounded Steel-Toe Cap
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.054, location=(fx, 0.105, 0.058))
    toe = bpy.context.active_object
    toe.name = f"BootToe_{side}"
    toe.scale = (0.96, 1.35, 0.72)
    toe.data.materials.append(mat_boot_leather)
    link_to_eng(toe, subdiv=1)
    
    # Padded ankle collar
    bpy.ops.mesh.primitive_torus_add(major_radius=0.048, minor_radius=0.014, location=(fx, -0.01, 0.18))
    collar = bpy.context.active_object
    collar.name = f"BootCollar_{side}"
    collar.scale = (0.95, 1.15, 1.0)
    collar.data.materials.append(mat_boot_sole)
    link_to_eng(collar)

# =========================================================================
# 2. SCULPTED CARGO WORK PANTS WITH DRAPE FOLDS & ARTICULATED KNEES (z: 0.16 to 1.02)
# =========================================================================
for side in [-1, 1]:
    lx = side * 0.112
    # Lofted trouser leg with realistic hem flare, knee articulation, and thigh volume
    leg_pts = [
        (lx, -0.005, 0.16, 0.064, 0.072),   # Boot cuff opening
        (lx, 0.000,  0.24, 0.068, 0.075),   # Lower shin fold
        (lx, -0.008, 0.38, 0.074, 0.082),   # Calf muscle fullness
        (lx, 0.012,  0.53, 0.071, 0.078),   # Knee joint slight forward bend
        (lx, 0.006,  0.68, 0.082, 0.090),   # Mid-thigh
        (lx * 0.95,  0.000, 0.84, 0.092, 0.102), # Upper thigh
        (lx * 0.88, -0.005, 0.96, 0.096, 0.106), # Hip merge
    ]
    create_OrganicLimb(f"TrouserLeg_{side}", leg_pts, mat_pants, segments=24)
    
    # Cordura Articulated Knee Pad Reinforcement
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, 0.078, 0.53), rotation=(math.radians(4), 0, 0))
    kpad = bpy.context.active_object
    kpad.name = f"CorduraKneePad_{side}"
    kpad.scale = (0.095, 0.024, 0.135)
    kpad.data.materials.append(mat_knee_pad)
    link_to_eng(kpad, subdiv=1)
    
    # Pleated Bellows Cargo Pocket + Flap on Outer Thigh
    px = lx + side * 0.084
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0.005, 0.70), rotation=(0, side * math.radians(-3), 0))
    pocket = bpy.context.active_object
    pocket.name = f"CargoPocket_{side}"
    pocket.scale = (0.028, 0.135, 0.165)
    pocket.data.materials.append(mat_pants)
    link_to_eng(pocket, subdiv=1)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px + side * 0.004, 0.005, 0.775), rotation=(0, side * math.radians(-3), 0))
    flap = bpy.context.active_object
    flap.name = f"CargoPocketFlap_{side}"
    flap.scale = (0.032, 0.142, 0.045)
    flap.data.materials.append(mat_pants)
    link_to_eng(flap, subdiv=1)

# Sculpted Pelvis / Seat & Waistband
pelvis_pts = [
    (0, -0.005, 0.88, 0.165, 0.112),
    (0, -0.008, 0.95, 0.182, 0.125),
    (0,  0.000, 1.02, 0.176, 0.118),
    (0,  0.002, 1.06, 0.172, 0.115),
]
create_OrganicLimb("TrouserPelvis", pelvis_pts, mat_pants, segments=28)

# Heavy-Duty Leather Work Belt, Belt Loops & Metal Buckle
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=0.042, location=(0, 0.001, 1.04))
belt = bpy.context.active_object
belt.name = "LeatherWorkBelt"
belt.scale = (0.177, 0.119, 1.0)
belt.data.materials.append(mat_radio)
link_to_eng(belt)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.120, 1.04))
buckle = bpy.context.active_object
buckle.name = "BeltBuckle"
buckle.scale = (0.052, 0.016, 0.048)
buckle.data.materials.append(mat_reflective)
link_to_eng(buckle, subdiv=1)

# =========================================================================
# 3. ANATOMICAL TORSO, COLLARED WORK SHIRT & ANSI CLASS 2 HI-VIS VEST (z: 1.04 to 1.49)
# =========================================================================
torso_pts = [
    (0, 0.000, 1.03, 0.168, 0.112),  # Waist
    (0, 0.004, 1.15, 0.178, 0.120),  # Mid-riff
    (0, 0.010, 1.28, 0.194, 0.132),  # Chest / pectorals
    (0, 0.004, 1.40, 0.212, 0.126),  # Upper chest / deltoid bridge
    (0, -0.005, 1.47, 0.145, 0.095), # Base of neck / trapezius
]
create_OrganicLimb("TorsoWorkShirt", torso_pts, mat_shirt, segments=32)

# Shirt Polo/Button Collar around neck
bpy.ops.mesh.primitive_torus_add(major_radius=0.078, minor_radius=0.022, location=(0, 0.0, 1.475), rotation=(math.radians(6), 0, 0))
shirt_collar = bpy.context.active_object
shirt_collar.name = "ShirtCollar"
shirt_collar.scale = (1.05, 1.12, 1.15)
shirt_collar.data.materials.append(mat_shirt)
link_to_eng(shirt_collar)

# Sculpted ANSI Class 2 High-Visibility Safety Vest
vest_pts = [
    (0, 0.002, 1.07, 0.176, 0.119),
    (0, 0.006, 1.18, 0.186, 0.128),
    (0, 0.012, 1.30, 0.202, 0.139),
    (0, 0.005, 1.41, 0.198, 0.130),
    (0, -0.004, 1.45, 0.155, 0.102),
]
create_OrganicLimb("ANSI_HiVisVest", vest_pts, mat_vest_hi_vis, segments=32)

# Vest Front Zipper Seam (Contrast Orange/Black trim down center front)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.136, 1.24))
zipper = bpy.context.active_object
zipper.name = "VestFrontZipper"
zipper.scale = (0.016, 0.014, 0.34)
zipper.data.materials.append(mat_radio)
link_to_eng(zipper)

# Dual 3M Silver + Orange Contrast Reflective Tape Bands (Waist & Chest)
for vz, rx, ry in [(1.14, 0.184, 0.126), (1.30, 0.205, 0.141)]:
    # Orange contrast backing
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=0.052, location=(0, 0.008, vz))
    oband = bpy.context.active_object
    oband.name = f"ContrastBand_{vz}"
    oband.scale = (rx, ry, 1.0)
    oband.data.materials.append(mat_vest_trim)
    link_to_eng(oband)
    
    # Silver 3M retro-reflective center strip
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=0.032, location=(0, 0.008, vz))
    sband = bpy.context.active_object
    sband.name = f"ReflectiveBand_{vz}"
    sband.scale = (rx + 0.002, ry + 0.002, 1.0)
    sband.data.materials.append(mat_reflective)
    link_to_eng(sband)

# Over-the-Shoulder Reflective Suspender Stripes
for side in [-1, 1]:
    sx = side * 0.105
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.005, 1.38))
    v_orange = bpy.context.active_object
    v_orange.name = f"ShoulderContrast_{side}"
    v_orange.scale = (0.052, 0.245, 0.15)
    v_orange.data.materials.append(mat_vest_trim)
    link_to_eng(v_orange, subdiv=1)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.005, 1.382))
    v_silver = bpy.context.active_object
    v_silver.name = f"ShoulderReflective_{side}"
    v_silver.scale = (0.032, 0.249, 0.152)
    v_silver.data.materials.append(mat_reflective)
    link_to_eng(v_silver, subdiv=1)

# Clip-on Laminated Hydro Engineer ID Badge on Right Chest
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.10, 0.142, 1.33), rotation=(math.radians(-6), 0, 0))
badge = bpy.context.active_object
badge.name = "EngineerIDBadge"
badge.scale = (0.052, 0.006, 0.078)
badge.data.materials.append(mat_badge)
link_to_eng(badge)

# Motorola Two-Way Walkie-Talkie Radio + Whip Antenna + Coiled Cord on Left Chest
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.115, 0.142, 1.35), rotation=(math.radians(-5), 0, math.radians(8)))
radio = bpy.context.active_object
radio.name = "WalkieTalkieRadio"
radio.scale = (0.048, 0.032, 0.105)
radio.data.materials.append(mat_radio)
link_to_eng(radio, subdiv=1)

bpy.ops.mesh.primitive_cylinder_add(radius=0.0045, depth=0.11, location=(-0.128, 0.146, 1.44), rotation=(math.radians(-5), 0, 0))
antenna = bpy.context.active_object
antenna.name = "RadioWhipAntenna"
antenna.data.materials.append(mat_radio)
link_to_eng(antenna)

# =========================================================================
# 4. NATURAL RELAXED ARMS & ARTICULATED GLOVED HANDS AT SIDES (z: 0.78 to 1.44)
# =========================================================================
for side in [-1, 1]:
    # Natural relaxed posture: shoulders at x = +/-0.215, arms hanging comfortably with slight elbow bend
    arm_pts = [
        (side * 0.195, -0.005, 1.43, 0.068, 0.072), # Shoulder deltoid cap
        (side * 0.228, -0.010, 1.34, 0.062, 0.065), # Upper biceps / rolled sleeve
        (side * 0.242, -0.015, 1.22, 0.056, 0.058), # Mid upper arm
        (side * 0.250, -0.018, 1.12, 0.052, 0.054), # Elbow joint
        (side * 0.256,  0.005, 1.00, 0.049, 0.051), # Upper forearm (slight forward bend)
        (side * 0.258,  0.025, 0.89, 0.042, 0.045), # Wrist cuff
    ]
    create_OrganicLimb(f"ShirtSleeveArm_{side}", arm_pts, mat_shirt, segments=20)
    
    # Velcro Glove Cuff
    hx = side * 0.258
    hy = 0.028
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.042, location=(hx, hy, 0.875), rotation=(math.radians(-8), 0, 0))
    cuff = bpy.context.active_object
    cuff.name = f"GloveVelcroCuff_{side}"
    cuff.data.materials.append(mat_glove_cuff)
    link_to_eng(cuff)
    
    # Leather Work Glove Palm & Back of Hand
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hx, hy + 0.008, 0.825), rotation=(math.radians(-8), side * math.radians(-4), 0))
    palm = bpy.context.active_object
    palm.name = f"GlovePalm_{side}"
    palm.scale = (0.038, 0.078, 0.088)
    palm.data.materials.append(mat_gloves)
    link_to_eng(palm, subdiv=2)
    
    # Articulated Thumb (facing forward/+Y)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.058, location=(hx - side * 0.012, hy + 0.048, 0.812), rotation=(math.radians(-28), 0, 0))
    thumb = bpy.context.active_object
    thumb.name = f"GloveThumb_{side}"
    thumb.data.materials.append(mat_gloves)
    link_to_eng(thumb, subdiv=1)
    
    # 4 Curled Fingers (Index, Middle, Ring, Pinky)
    for f_idx, fy_off in enumerate([0.026, 0.009, -0.008, -0.024]):
        f_len = 0.062 if f_idx in [1, 2] else 0.054
        bpy.ops.mesh.primitive_cylinder_add(radius=0.011, depth=f_len, location=(hx - side * 0.006, hy + 0.008 + fy_off, 0.768), rotation=(0, side * math.radians(12), 0))
        finger = bpy.context.active_object
        finger.name = f"GloveFinger_{side}_{f_idx}"
        finger.data.materials.append(mat_gloves)
        link_to_eng(finger, subdiv=1)

# =========================================================================
# 5. SCULPTED HEAD, FACIAL FEATURES, EARS, WRAP-AROUND GLASSES & MSA HARD HAT
# =========================================================================
# Anatomical Neck & Adam's Apple contour
neck_pts = [
    (0, -0.006, 1.45, 0.066, 0.068),
    (0,  0.000, 1.50, 0.058, 0.060),
    (0,  0.005, 1.55, 0.056, 0.058),
]
create_OrganicLimb("AnatomicalNeck", neck_pts, mat_skin, segments=24)

# Sculpted Cranium, Jawline & Chin
head_pts = [
    (0,  0.018, 1.535, 0.052, 0.062), # Under-chin / jaw base
    (0,  0.022, 1.565, 0.078, 0.095), # Jawline & chin projection
    (0,  0.015, 1.605, 0.092, 0.106), # Cheekbones & mouth level
    (0,  0.008, 1.645, 0.096, 0.112), # Eye sockets / brow ridge
    (0,  0.000, 1.690, 0.098, 0.114), # Forehead & temples
    (0, -0.008, 1.730, 0.082, 0.096), # Upper cranium
    (0, -0.012, 1.755, 0.045, 0.055), # Crown
]
create_OrganicLimb("SculptedHead", head_pts, mat_skin, segments=32)

# Sculpted Nose Bridge & Tip
bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.018, radius2=0.008, depth=0.048, location=(0, 0.114, 1.622), rotation=(math.radians(-72), 0, 0))
nose = bpy.context.active_object
nose.name = "SculptedNose"
nose.scale = (0.85, 1.0, 1.0)
nose.data.materials.append(mat_skin)
link_to_eng(nose, subdiv=1)

# Subtle Mouth / Lip Line
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.104, 1.584))
lips = bpy.context.active_object
lips.name = "LipsContour"
lips.scale = (0.038, 0.012, 0.010)
lips.data.materials.append(mat_lips)
link_to_eng(lips, subdiv=1)

# Ears (Left & Right)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.024, location=(side * 0.096, 0.002, 1.625), rotation=(0, side * math.radians(-15), 0))
    ear = bpy.context.active_object
    ear.name = f"Ear_{side}"
    ear.scale = (0.42, 0.75, 1.25)
    ear.data.materials.append(mat_skin)
    link_to_eng(ear, subdiv=1)

# Short Cropped Hair & Sideburns at Back/Sides of Head under Hard Hat
hair_pts = [
    (0, -0.025, 1.56, 0.078, 0.075),
    (0, -0.020, 1.61, 0.095, 0.092),
    (0, -0.015, 1.66, 0.099, 0.100),
]
create_OrganicLimb("CroppedHair", hair_pts, mat_hair, segments=24)

# Wrap-Around Polycarbonate Safety Glasses (Curved Lens + Black Side Temples + Nosepiece)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.098, depth=0.036, location=(0, 0.025, 1.640))
# Keep only front arc of cylinder for wrap-around lens
lens_obj = bpy.context.active_object
lens_obj.name = "WrapSafetyGlassesLens"
bm = bmesh.new()
bm.from_mesh(lens_obj.data)
verts_to_del = [v for v in bm.verts if v.co.y < 0.035]
bmesh.ops.delete(bm, geom=verts_to_del, context='VERTS')
bm.to_mesh(lens_obj.data)
bm.free()
mod_solid = lens_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
mod_solid.thickness = 0.004
lens_obj.data.materials.append(mat_glasses_lens)
link_to_eng(lens_obj, smooth=True, subdiv=1)

# Glasses Top Brow Frame & Side Temple Arms
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.094, 0.038, 1.642))
    temple = bpy.context.active_object
    temple.name = f"GlassesTemple_{side}"
    temple.scale = (0.006, 0.085, 0.008)
    temple.data.materials.append(mat_glasses_frame)
    link_to_eng(temple)

# =========================================================================
# 6. MSA V-GARD INDUSTRIAL HARD HAT WITH BRIM, RATCHET NAPE & HYDRO BADGE
# =========================================================================
# Contoured Hard Hat Shell Dome
bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=20, radius=0.118, location=(0, 0.005, 1.685), rotation=(math.radians(-4), 0, 0))
hat_dome = bpy.context.active_object
hat_dome.name = "MSA_HardHatShell"
bm = bmesh.new()
bm.from_mesh(hat_dome.data)
for v in bm.verts:
    if v.co.z < -0.015:
        v.co.z = -0.015
    # Elongate front-to-back slightly
    v.co.y *= 1.16
    v.co.x *= 1.03
bm.to_mesh(hat_dome.data)
bm.free()
hat_dome.data.materials.append(mat_hard_hat)
link_to_eng(hat_dome, smooth=True, subdiv=1)

# Classic MSA V-Gard Crown V-Ridges
for rx_off, rot_y in [(0.0, 0), (-0.032, math.radians(-12)), (0.032, math.radians(12))]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx_off, 0.008, 1.792), rotation=(math.radians(-4), rot_y, 0))
    ridge = bpy.context.active_object
    ridge.name = f"VGardRidge_{rx_off}"
    ridge.scale = (0.022, 0.21, 0.028)
    ridge.data.materials.append(mat_hard_hat)
    link_to_eng(ridge, subdiv=1)

# Sculpted Front Peak Visor & Perimeter Rain Trough Brim
bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.126, depth=0.012, location=(0, 0.018, 1.672), rotation=(math.radians(5), 0, 0))
hat_brim = bpy.context.active_object
hat_brim.name = "HardHatBrimVisor"
hat_brim.scale = (1.02, 1.24, 1.0)
hat_brim.data.materials.append(mat_hard_hat)
link_to_eng(hat_brim, subdiv=1)

# Rear Fas-Trac Ratchet Suspension Nape Strap & Knob
bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.010, location=(0, -0.005, 1.648), rotation=(math.radians(12), 0, 0))
nape = bpy.context.active_object
nape.name = "HardHatRatchetBand"
nape.scale = (0.96, 1.08, 1.0)
nape.data.materials.append(mat_hat_band)
link_to_eng(nape)

bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.014, location=(0, -0.108, 1.628), rotation=(math.pi/2, 0, 0))
knob = bpy.context.active_object
knob.name = "RatchetAdjustmentKnob"
knob.data.materials.append(mat_hat_band)
link_to_eng(knob)

# Front Hydro Blue Safety Crest Emblem on Hard Hat Forehead
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.138, 1.715), rotation=(math.radians(-18), 0, 0))
crest = bpy.context.active_object
crest.name = "HardHatHydroCrest"
crest.scale = (0.048, 0.006, 0.036)
crest.data.materials.append(mat_hydro_blue)
link_to_eng(crest, subdiv=1)

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
