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

# Materials
mat_paint = create_pbr_material("CarPaintWhite", (0.92, 0.93, 0.95), metallic=0.25, roughness=0.18, clearcoat=1.0)
mat_trim = create_pbr_material("TrimBlack", (0.04, 0.04, 0.04), metallic=0.1, roughness=0.68)
mat_chrome = create_pbr_material("Chrome", (0.95, 0.95, 0.95), metallic=0.98, roughness=0.04)
mat_tire = create_pbr_material("TireRubber", (0.06, 0.06, 0.06), metallic=0.0, roughness=0.85)
mat_alloy = create_pbr_material("AlloyRim", (0.82, 0.84, 0.88), metallic=0.94, roughness=0.20)
mat_brake = create_pbr_material("BrakeRotor", (0.68, 0.70, 0.72), metallic=0.95, roughness=0.26)
mat_caliper = create_pbr_material("BrakeCaliperRed", (0.85, 0.08, 0.08), metallic=0.35, roughness=0.28)
mat_glass = create_pbr_material("GlassTint", (0.12, 0.16, 0.22), metallic=0.1, roughness=0.04, transmission=0.88)
mat_headlight_glass = create_pbr_material("HeadlightGlass", (0.92, 0.96, 1.0), metallic=0.1, roughness=0.03, transmission=0.94)
mat_headlight_led = create_pbr_material("LEDHeadlight", (1.0, 1.0, 1.0), emission=(1.0, 0.98, 0.92), emission_strength=5.0)
mat_taillight_red = create_pbr_material("TaillightRed", (0.88, 0.03, 0.03), metallic=0.1, roughness=0.10, transmission=0.45, emission=(0.9, 0.02, 0.02), emission_strength=2.0)
mat_amber = create_pbr_material("AmberTurn", (0.98, 0.58, 0.04), metallic=0.1, roughness=0.18, emission=(0.98, 0.58, 0.04), emission_strength=2.5)
mat_hydro_blue = create_pbr_material("HydroBlue", (0.04, 0.44, 0.88), metallic=0.3, roughness=0.22)

truck_root = bpy.data.objects.new("OperationsTruck", None)
bpy.context.scene.collection.objects.link(truck_root)

def add_bevel(obj, width=0.02, segments=2):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(35)

def link_to_truck(obj, smooth=True, bevel=False):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = truck_root
    if obj.type == 'MESH':
        if smooth:
            for poly in obj.data.polygons:
                poly.use_smooth = True
        if bevel:
            add_bevel(obj)

# 1. CHASSIS FRAME
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.40))
chassis = bpy.context.active_object
chassis.name = "Chassis_Frame"
chassis.scale = (1.1, 4.9, 0.16)
chassis.data.materials.append(mat_trim)
link_to_truck(chassis, bevel=True)

# Front & Rear Axles & Differentials
for y_pos in [1.55, -1.55]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.75, location=(0, y_pos, 0.44), rotation=(0, math.pi/2, 0))
    axle = bpy.context.active_object
    axle.name = f"Axle_{y_pos}"
    axle.data.materials.append(mat_trim)
    link_to_truck(axle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(0.14, y_pos, 0.44))
    diff = bpy.context.active_object
    diff.name = f"Diff_{y_pos}"
    diff.data.materials.append(mat_trim)
    link_to_truck(diff)

# Driveshaft
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=3.1, location=(0.14, 0, 0.44), rotation=(math.pi/2, 0, 0))
driveshaft = bpy.context.active_object
driveshaft.name = "Driveshaft"
driveshaft.data.materials.append(mat_trim)
link_to_truck(driveshaft)

# 2. CAB BODYWORK
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.28, 1.15))
cab_lower = bpy.context.active_object
cab_lower.name = "Cab_Lower"
cab_lower.scale = (1.94, 2.52, 0.68)
cab_lower.data.materials.append(mat_paint)
link_to_truck(cab_lower, bevel=True)

# Upper Greenhouse
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.18, 1.68))
cab_upper = bpy.context.active_object
cab_upper.name = "Cab_Greenhouse"
cab_upper.scale = (1.76, 1.88, 0.58)
cab_upper.data.materials.append(mat_paint)
link_to_truck(cab_upper, bevel=True)

# Roof Cap with Bevel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.18, 1.98))
roof = bpy.context.active_object
roof.name = "Roof_Cap"
roof.scale = (1.78, 1.90, 0.06)
roof.data.materials.append(mat_paint)
link_to_truck(roof, bevel=True)

# Windshield
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.02, 1.65), rotation=(math.radians(28), 0, 0))
windshield = bpy.context.active_object
windshield.name = "Windshield"
windshield.scale = (1.70, 0.04, 0.68)
windshield.data.materials.append(mat_glass)
link_to_truck(windshield)

# Rear Glass
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.76, 1.68))
rear_glass = bpy.context.active_object
rear_glass.name = "RearGlass"
rear_glass.scale = (1.64, 0.04, 0.52)
rear_glass.data.materials.append(mat_glass)
link_to_truck(rear_glass)

# Side Windows
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.89, 0.18, 1.66))
    side_glass = bpy.context.active_object
    side_glass.name = f"SideGlass_{side}"
    side_glass.scale = (0.03, 1.68, 0.48)
    side_glass.data.materials.append(mat_glass)
    link_to_truck(side_glass)

# Hood
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.90, 1.12), rotation=(math.radians(-3.5), 0, 0))
hood = bpy.context.active_object
hood.name = "Hood"
hood.scale = (1.90, 1.34, 0.46)
hood.data.materials.append(mat_paint)
link_to_truck(hood, bevel=True)

# Front Wheel Arch Flare Extensions (Fenders)
for side in [-1, 1]:
    # Front arch
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.98, 1.55, 0.82))
    fa = bpy.context.active_object
    fa.name = f"FenderFront_{side}"
    fa.scale = (0.12, 1.05, 0.14)
    fa.data.materials.append(mat_trim)
    link_to_truck(fa, bevel=True)
    
    # Rear arch
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.98, -1.55, 0.82))
    ra = bpy.context.active_object
    ra.name = f"FenderRear_{side}"
    ra.scale = (0.12, 1.05, 0.14)
    ra.data.materials.append(mat_trim)
    link_to_truck(ra, bevel=True)

# Front Grille & Fascia
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.56, 1.10))
grille = bpy.context.active_object
grille.name = "FrontGrille"
grille.scale = (1.72, 0.08, 0.38)
grille.data.materials.append(mat_trim)
link_to_truck(grille, bevel=True)

# Chrome Grille Louvers
for gz in [1.02, 1.10, 1.18]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.61, gz))
    bar = bpy.context.active_object
    bar.name = f"GrilleBar_{gz}"
    bar.scale = (1.54, 0.03, 0.025)
    bar.data.materials.append(mat_chrome)
    link_to_truck(bar)

# Hydro Emblem
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.04, location=(0, 2.62, 1.10), rotation=(math.pi/2, 0, 0))
emblem = bpy.context.active_object
emblem.name = "HydroEmblem"
emblem.data.materials.append(mat_hydro_blue)
link_to_truck(emblem)

# Headlights (Dual projector units)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.74, 2.56, 1.12))
    hl_house = bpy.context.active_object
    hl_house.name = f"HeadlightHousing_{side}"
    hl_house.scale = (0.34, 0.08, 0.22)
    hl_house.data.materials.append(mat_chrome)
    link_to_truck(hl_house)
    
    for px in [-0.07, 0.07]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.06, location=(side * 0.74 + px, 2.60, 1.12), rotation=(math.pi/2, 0, 0))
        led = bpy.context.active_object
        led.name = f"HeadlightLED_{side}_{px}"
        led.data.materials.append(mat_headlight_led)
        link_to_truck(led)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.74, 2.62, 1.12))
    hl_lens = bpy.context.active_object
    hl_lens.name = f"HeadlightLens_{side}"
    hl_lens.scale = (0.35, 0.02, 0.23)
    hl_lens.data.materials.append(mat_headlight_glass)
    link_to_truck(hl_lens)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.88, 2.60, 1.12))
    amber = bpy.context.active_object
    amber.name = f"AmberTurn_{side}"
    amber.scale = (0.06, 0.03, 0.20)
    amber.data.materials.append(mat_amber)
    link_to_truck(amber)

# Heavy Duty Steel Bumper & Bull Bar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.64, 0.68))
front_bumper = bpy.context.active_object
front_bumper.name = "FrontBumper"
front_bumper.scale = (2.04, 0.32, 0.34)
front_bumper.data.materials.append(mat_trim)
link_to_truck(front_bumper, bevel=True)

# Bull Bar Tube
bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=1.60, location=(0, 2.80, 0.95), rotation=(0, math.pi/2, 0))
bull_bar = bpy.context.active_object
bull_bar.name = "BullBar_Upper"
bull_bar.data.materials.append(mat_trim)
link_to_truck(bull_bar)

# Winch Fairlead & Shackles
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.81, 0.68))
winch = bpy.context.active_object
winch.name = "WinchFairlead"
winch.scale = (0.35, 0.08, 0.12)
winch.data.materials.append(mat_chrome)
link_to_truck(winch)

for side in [-1, 1]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.015, location=(side * 0.38, 2.82, 0.62), rotation=(0, math.pi/2, 0))
    dring = bpy.context.active_object
    dring.name = f"RecoveryShackle_{side}"
    dring.data.materials.append(mat_caliper)
    link_to_truck(dring)

# Tubular Side Rock Sliders / Steps
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=2.20, location=(side * 1.02, 0.18, 0.55), rotation=(math.pi/2, 0, 0))
    step = bpy.context.active_object
    step.name = f"RockSlider_{side}"
    step.data.materials.append(mat_trim)
    link_to_truck(step)

# 3. TRUCK BED
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.68, 0.95))
bed_floor = bpy.context.active_object
bed_floor.name = "BedFloor"
bed_floor.scale = (1.92, 2.00, 0.12)
bed_floor.data.materials.append(mat_trim)
link_to_truck(bed_floor, bevel=True)

for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.94, -1.68, 1.25))
    bed_side = bpy.context.active_object
    bed_side.name = f"BedSide_{side}"
    bed_side.scale = (0.12, 2.00, 0.55)
    bed_side.data.materials.append(mat_paint)
    link_to_truck(bed_side, bevel=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.94, -1.68, 1.54))
    rail = bpy.context.active_object
    rail.name = f"BedRail_{side}"
    rail.scale = (0.14, 2.02, 0.04)
    rail.data.materials.append(mat_trim)
    link_to_truck(rail)

# Tailgate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.66, 1.25))
tailgate = bpy.context.active_object
tailgate.name = "Tailgate"
tailgate.scale = (1.90, 0.10, 0.55)
tailgate.data.materials.append(mat_paint)
link_to_truck(tailgate, bevel=True)

# Rear Taillights
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.88, -2.68, 1.28))
    tl = bpy.context.active_object
    tl.name = f"Taillight_{side}"
    tl.scale = (0.14, 0.06, 0.36)
    tl.data.materials.append(mat_taillight_red)
    link_to_truck(tl)

# Rear Steel Bumper
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.72, 0.65))
rear_bumper = bpy.context.active_object
rear_bumper.name = "RearBumper"
rear_bumper.scale = (2.00, 0.22, 0.22)
rear_bumper.data.materials.append(mat_trim)
link_to_truck(rear_bumper, bevel=True)

# Roll Bar & Auxiliary LED Pods
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.88, location=(side * 0.86, -0.76, 1.72))
    upright = bpy.context.active_object
    upright.name = f"RollBarUpright_{side}"
    upright.data.materials.append(mat_trim)
    link_to_truck(upright)

bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.72, location=(0, -0.76, 2.16), rotation=(0, math.pi/2, 0))
cross_bar = bpy.context.active_object
cross_bar.name = "RollBarCross"
cross_bar.data.materials.append(mat_trim)
link_to_truck(cross_bar)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.76, 2.24))
light_bar = bpy.context.active_object
light_bar.name = "AuxLightBar"
light_bar.scale = (1.42, 0.08, 0.06)
light_bar.data.materials.append(mat_headlight_led)
link_to_truck(light_bar)

# Side Mirrors & Door Handles
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.06, 0.80, 1.58))
    m_house = bpy.context.active_object
    m_house.name = f"MirrorHousing_{side}"
    m_house.scale = (0.14, 0.24, 0.16)
    m_house.data.materials.append(mat_trim)
    link_to_truck(m_house, bevel=True)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.06, 0.74, 1.58))
    m_glass = bpy.context.active_object
    m_glass.name = f"MirrorGlass_{side}"
    m_glass.scale = (0.12, 0.02, 0.14)
    m_glass.data.materials.append(mat_chrome)
    link_to_truck(m_glass)
    
    for dy in [0.45, -0.15]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.99, dy, 1.26))
        d_handle = bpy.context.active_object
        d_handle.name = f"DoorHandle_{side}_{dy}"
        d_handle.scale = (0.04, 0.16, 0.04)
        d_handle.data.materials.append(mat_trim)
        link_to_truck(d_handle)

# 4. WHEELS (Deep Dish Off-Road Beadlock Rims + Knobby Mud Tires)
wheel_coords = [
    ("FL", -0.98, 1.55),
    ("FR", 0.98, 1.55),
    ("RL", -0.98, -1.55),
    ("RR", 0.98, -1.55),
]

for name, wx, wy in wheel_coords:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.32, location=(wx, wy, 0.45), rotation=(0, math.pi/2, 0))
    tire = bpy.context.active_object
    tire.name = f"Tire_{name}"
    tire.data.materials.append(mat_tire)
    link_to_truck(tire)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.28, location=(wx, wy, 0.45), rotation=(0, math.pi/2, 0))
    rim = bpy.context.active_object
    rim.name = f"Rim_{name}"
    rim.data.materials.append(mat_alloy)
    link_to_truck(rim)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.28, minor_radius=0.016, location=(wx + (0.15 if wx > 0 else -0.15), wy, 0.45), rotation=(0, math.pi/2, 0))
    lip = bpy.context.active_object
    lip.name = f"RimLip_{name}"
    lip.data.materials.append(mat_chrome)
    link_to_truck(lip)
    
    for s in range(6):
        angle = s * (math.pi / 3)
        sx = wx + (0.10 if wx > 0 else -0.10)
        sy = wy + math.cos(angle) * 0.14
        sz = 0.45 + math.sin(angle) * 0.14
        bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.20, location=(sx, sy, sz), rotation=(angle, 0, 0))
        spoke = bpy.context.active_object
        spoke.name = f"Spoke_{name}_{s}"
        spoke.data.materials.append(mat_alloy)
        link_to_truck(spoke)
        
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.06, location=(wx + (0.14 if wx > 0 else -0.14), wy, 0.45), rotation=(0, math.pi/2, 0))
    hub = bpy.context.active_object
    hub.name = f"HubCap_{name}"
    hub.data.materials.append(mat_trim)
    link_to_truck(hub)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.02, location=(wx + (0.02 if wx > 0 else -0.02), wy, 0.45), rotation=(0, math.pi/2, 0))
    rotor = bpy.context.active_object
    rotor.name = f"BrakeRotor_{name}"
    rotor.data.materials.append(mat_brake)
    link_to_truck(rotor)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx + (0.02 if wx > 0 else -0.02), wy + 0.16, 0.53))
    caliper = bpy.context.active_object
    caliper.name = f"BrakeCaliper_{name}"
    caliper.scale = (0.08, 0.12, 0.14)
    caliper.data.materials.append(mat_caliper)
    link_to_truck(caliper)

# Export as GLB
out_path = "/Users/inhausuxui/.gemini/antigravity/scratch/water-treatment-plant-simulation/assets/models/mobile_truck.glb"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {out_path} ({os.path.getsize(out_path)} bytes)")
