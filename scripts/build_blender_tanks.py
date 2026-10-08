import bpy
import bmesh
import math
import os

def reset_scene():
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

out_dir = "/Users/inhausuxui/.gemini/antigravity/scratch/water-treatment-plant-simulation/assets/models"
os.makedirs(out_dir, exist_ok=True)

# =========================================================================
# TANK 1: ASME Section VIII Div 1 Horizontal Pressure Vessel
# =========================================================================
reset_scene()
mat_tank_shell = create_pbr_material("ASME_TankShellWhite", (0.92, 0.93, 0.95), metallic=0.25, roughness=0.22, clearcoat=0.8)
mat_stainless = create_pbr_material("SS316_Flanges", (0.86, 0.88, 0.90), metallic=0.92, roughness=0.18)
mat_saddle_steel = create_pbr_material("StructuralSaddles", (0.20, 0.22, 0.25), metallic=0.75, roughness=0.45)
mat_brass = create_pbr_material("BrassNameplate", (0.85, 0.68, 0.22), metallic=0.90, roughness=0.25)
mat_red = create_pbr_material("IndicatorRed", (0.85, 0.05, 0.05), metallic=0.10, roughness=0.25)
mat_glass = create_pbr_material("SightGlass", (0.90, 0.95, 1.0), metallic=0.10, roughness=0.05, transmission=0.90)

h_root = bpy.data.objects.new("ASME_HorizontalTank", None)
bpy.context.scene.collection.objects.link(h_root)

def link_h(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = h_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# Main Cylindrical Shell (L = 4.2m, R = 0.95m, elevation Z = 1.35m)
bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=4.2, location=(0, 0, 1.35), rotation=(0, math.pi/2, 0))
shell = bpy.context.active_object
shell.name = "CylindricalShell"
shell.data.materials.append(mat_tank_shell)
link_h(shell)

# Dished 2:1 Semi-Ellipsoidal Heads on each end (at X = -2.1 and +2.1)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.95, location=(side * 2.10, 0, 1.35))
    head = bpy.context.active_object
    head.name = f"DishedHead_{side}"
    head.scale = (0.50, 1.0, 1.0)
    head.data.materials.append(mat_tank_shell)
    link_h(head)

# Zick Saddles (Support Saddles with 120-degree wrap angle at X = -1.3 and +1.3)
for sx in [-1.30, 1.30]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.38))
    saddle = bpy.context.active_object
    saddle.name = f"ZickSaddle_{sx}"
    saddle.scale = (0.35, 1.95, 0.76)
    saddle.data.materials.append(mat_saddle_steel)
    link_h(saddle)
    
    # Baseplate & Anchor Bolts
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.03))
    baseplate = bpy.context.active_object
    baseplate.name = f"BasePlate_{sx}"
    baseplate.scale = (0.45, 2.15, 0.06)
    baseplate.data.materials.append(mat_saddle_steel)
    link_h(baseplate)

# Top Davit-Arm 24" Manway with Bolted Blind Flange (at X = -0.5, Z = 2.30)
bpy.ops.mesh.primitive_cylinder_add(radius=0.36, depth=0.35, location=(-0.5, 0, 2.35))
manway_neck = bpy.context.active_object
manway_neck.name = "ManwayNeck"
manway_neck.data.materials.append(mat_stainless)
link_h(manway_neck)

bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=0.08, location=(-0.5, 0, 2.52))
manway_flange = bpy.context.active_object
manway_flange.name = "ManwayBlindFlange"
manway_flange.data.materials.append(mat_stainless)
link_h(manway_flange)

# Radar Level Transmitter Nozzle (at X = 0.8, Z = 2.30)
bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.30, location=(0.8, 0, 2.38))
radar_neck = bpy.context.active_object
radar_neck.name = "RadarNeck"
radar_neck.data.materials.append(mat_stainless)
link_h(radar_neck)

bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.22, location=(0.8, 0, 2.60))
radar_head = bpy.context.active_object
radar_head.name = "RadarHousing"
radar_head.data.materials.append(mat_saddle_steel)
link_h(radar_head)

# Magnetic Level Indicator (MLI) Bypass Chamber on Front Face
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.40, location=(0.2, 1.08, 1.35))
mli_tube = bpy.context.active_object
mli_tube.name = "MLI_Chamber"
mli_tube.data.materials.append(mat_stainless)
link_h(mli_tube)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.2, 1.12, 1.35))
mli_scale = bpy.context.active_object
mli_scale.name = "MLI_IndicatorScale"
mli_scale.scale = (0.06, 0.02, 1.30)
mli_scale.data.materials.append(mat_red)
link_h(mli_scale)

# ASME Code Stamped Stamped Nameplate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.98, 1.35))
nameplate = bpy.context.active_object
nameplate.name = "ASME_CodeNameplate"
nameplate.scale = (0.32, 0.02, 0.20)
nameplate.data.materials.append(mat_brass)
link_h(nameplate)

# Export ASME Tank
tank1_path = os.path.join(out_dir, "asme_horizontal_tank.glb")
bpy.ops.export_scene.gltf(
    filepath=tank1_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {tank1_path} ({os.path.getsize(tank1_path)} bytes)")

# =========================================================================
# TANK 2: ASTM D1998 Vertical Cone-Bottom Tank with Top Agitator Mixer
# =========================================================================
reset_scene()
mat_hdpe = create_pbr_material("ASTM_HDPE_White", (0.94, 0.94, 0.96), metallic=0.08, roughness=0.35, clearcoat=0.5)
mat_legs = create_pbr_material("StructuralSteelLegs", (0.18, 0.20, 0.22), metallic=0.85, roughness=0.40)
mat_motor = create_pbr_material("MixerMotorTeal", (0.10, 0.42, 0.48), metallic=0.35, roughness=0.38)
mat_shaft = create_pbr_material("MixerShaftSS316", (0.88, 0.90, 0.92), metallic=0.95, roughness=0.15)
mat_impeller = create_pbr_material("HydrofoilImpeller", (0.85, 0.88, 0.90), metallic=0.92, roughness=0.20)

v_root = bpy.data.objects.new("ASTM_VerticalTank", None)
bpy.context.scene.collection.objects.link(v_root)

def link_v(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = v_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# Structural Steel Stand: 4 I-Beam Legs (Elevation Z = 0 to 1.2m)
leg_coords = [(-0.95, -0.95), (0.95, -0.95), (-0.95, 0.95), (0.95, 0.95)]
for lx, ly in leg_coords:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, 0.60))
    leg = bpy.context.active_object
    leg.name = f"TankLeg_{lx}_{ly}"
    leg.scale = (0.14, 0.14, 1.20)
    leg.data.materials.append(mat_legs)
    link_v(leg)

# Top Ring Girder on Legs
bpy.ops.mesh.primitive_cylinder_add(radius=1.38, depth=0.14, location=(0, 0, 1.20))
ring = bpy.context.active_object
ring.name = "StandRingGirder"
ring.data.materials.append(mat_legs)
link_v(ring)

# Cone Bottom (30-degree cone for complete solids drainage)
bpy.ops.mesh.primitive_cone_add(radius1=1.35, radius2=0.18, depth=0.85, location=(0, 0, 1.25))
cone = bpy.context.active_object
cone.name = "ConeBottom"
cone.data.materials.append(mat_hdpe)
link_v(cone)

# Main Cylindrical Vessel Shell (Radius 1.35m, Height 2.8m, Z = 1.68 to 4.48m)
bpy.ops.mesh.primitive_cylinder_add(radius=1.35, depth=2.80, location=(0, 0, 3.08))
v_shell = bpy.context.active_object
v_shell.name = "VerticalCylinderShell"
v_shell.data.materials.append(mat_hdpe)
link_v(v_shell)

# Dished Top Dome Head (Z = 4.48 to 4.95m)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.35, location=(0, 0, 4.48))
dome = bpy.context.active_object
dome.name = "TopDomeHead"
dome.scale = (1.0, 1.0, 0.35)
dome.data.materials.append(mat_hdpe)
link_v(dome)

# Top Agitator Mixer Motor & Planetary Gearbox (Z = 5.0 to 5.7m)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 5.05))
mixer_gearbox = bpy.context.active_object
mixer_gearbox.name = "MixerGearbox"
mixer_gearbox.scale = (0.48, 0.48, 0.35)
mixer_gearbox.data.materials.append(mat_motor)
link_v(mixer_gearbox)

bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.48, location=(0, 0, 5.42))
mixer_motor = bpy.context.active_object
mixer_motor.name = "MixerTEFCMotor"
mixer_motor.data.materials.append(mat_motor)
link_v(mixer_motor)

# Internal Mixer Agitator Shaft (extends down into tank)
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=3.40, location=(0, 0, 3.20))
shaft = bpy.context.active_object
shaft.name = "AgitatorShaft"
shaft.data.materials.append(mat_shaft)
link_v(shaft)

# Dual Tier Hydrofoil Impeller Blades (Upper & Lower)
for iz in [2.4, 3.6]:
    for b in range(3):
        angle = b * (2 * math.pi / 3)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(math.cos(angle)*0.35, math.sin(angle)*0.35, iz), rotation=(math.radians(20), 0, angle))
        blade = bpy.context.active_object
        blade.name = f"ImpellerBlade_{iz}_{b}"
        blade.scale = (0.65, 0.12, 0.02)
        blade.data.materials.append(mat_impeller)
        link_v(blade)

# Export ASTM Tank
tank2_path = os.path.join(out_dir, "astm_vertical_tank.glb")
bpy.ops.export_scene.gltf(
    filepath=tank2_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {tank2_path} ({os.path.getsize(tank2_path)} bytes)")
