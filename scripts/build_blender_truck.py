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
mat_paint = create_pbr_material("CarPaintWhite", (0.94, 0.95, 0.97), metallic=0.28, roughness=0.14, clearcoat=1.0)
mat_trim = create_pbr_material("TrimBlack", (0.045, 0.045, 0.05), metallic=0.12, roughness=0.62)
mat_bedliner = create_pbr_material("BedLinerTextured", (0.06, 0.06, 0.065), metallic=0.05, roughness=0.88)
mat_chrome = create_pbr_material("Chrome", (0.96, 0.96, 0.98), metallic=0.98, roughness=0.04)
mat_diamond = create_pbr_material("DiamondPlateAlum", (0.82, 0.85, 0.88), metallic=0.92, roughness=0.22)
mat_tire = create_pbr_material("TireRubber", (0.05, 0.05, 0.055), metallic=0.0, roughness=0.84)
mat_alloy = create_pbr_material("AlloyRim", (0.78, 0.81, 0.85), metallic=0.94, roughness=0.18)
mat_brake = create_pbr_material("BrakeRotor", (0.68, 0.70, 0.72), metallic=0.95, roughness=0.25)
mat_caliper = create_pbr_material("BrakeCaliperRed", (0.85, 0.08, 0.08), metallic=0.35, roughness=0.28)
mat_glass = create_pbr_material("GlassTint", (0.08, 0.12, 0.16), metallic=0.15, roughness=0.03, transmission=0.86)
mat_interior = create_pbr_material("CabInteriorCharcoal", (0.10, 0.11, 0.12), metallic=0.05, roughness=0.78)
mat_headlight_glass = create_pbr_material("HeadlightGlass", (0.92, 0.96, 1.0), metallic=0.1, roughness=0.02, transmission=0.94)
mat_headlight_led = create_pbr_material("LEDHeadlight", (1.0, 1.0, 1.0), emission=(1.0, 0.98, 0.92), emission_strength=6.0)
mat_taillight_red = create_pbr_material("TaillightRed", (0.88, 0.03, 0.03), metallic=0.1, roughness=0.10, transmission=0.45, emission=(0.92, 0.02, 0.02), emission_strength=2.5)
mat_amber = create_pbr_material("AmberBeacon", (0.98, 0.58, 0.02), metallic=0.1, roughness=0.15, emission=(0.98, 0.58, 0.02), emission_strength=3.5)
mat_hydro_blue = create_pbr_material("HydroBlue", (0.04, 0.44, 0.88), metallic=0.35, roughness=0.20)
mat_coil_red = create_pbr_material("SuspensionSpringRed", (0.82, 0.10, 0.08), metallic=0.3, roughness=0.35)

truck_root = bpy.data.objects.new("OperationsTruck", None)
bpy.context.scene.collection.objects.link(truck_root)

def add_bevel(obj, width=0.025, segments=3):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(30)

def link_to_truck(obj, smooth=True, bevel=False, bevel_width=0.025, subdiv=0):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = truck_root
    if obj.type == 'MESH':
        if bevel:
            add_bevel(obj, width=bevel_width, segments=3)
        if subdiv > 0:
            mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
            mod.levels = subdiv
            mod.render_levels = subdiv
        if smooth:
            for poly in obj.data.polygons:
                poly.use_smooth = True

# =========================================================================
# 1. HEAVY-DUTY LADDER CHASSIS, AXLES, COILOVERS & EXHAUST (z: 0.35 to 0.65)
# =========================================================================
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.46, 0, 0.44))
    rail = bpy.context.active_object
    rail.name = f"FrameRail_{side}"
    rail.scale = (0.10, 4.95, 0.16)
    rail.data.materials.append(mat_trim)
    link_to_truck(rail, bevel=True, bevel_width=0.01)

# Crossmembers
for cy in [-2.2, -1.2, -0.2, 0.8, 1.8]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, cy, 0.44))
    cm = bpy.context.active_object
    cm.name = f"Crossmember_{cy}"
    cm.scale = (0.85, 0.10, 0.12)
    cm.data.materials.append(mat_trim)
    link_to_truck(cm)

# Front & Rear Solid Axles, Differentials & Coilover Shocks
for y_pos in [1.55, -1.55]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.058, depth=1.78, location=(0, y_pos, 0.45), rotation=(0, math.pi/2, 0))
    axle = bpy.context.active_object
    axle.name = f"Axle_{y_pos}"
    axle.data.materials.append(mat_trim)
    link_to_truck(axle)
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.165, location=(0.14, y_pos, 0.45))
    diff = bpy.context.active_object
    diff.name = f"DiffPumpkin_{y_pos}"
    diff.scale = (1.1, 0.9, 1.0)
    diff.data.materials.append(mat_trim)
    link_to_truck(diff)
    
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.36, location=(side * 0.64, y_pos, 0.62))
        shock = bpy.context.active_object
        shock.name = f"Coilover_{y_pos}_{side}"
        shock.data.materials.append(mat_coil_red)
        link_to_truck(shock)

# Driveshaft
bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=3.10, location=(0.14, 0, 0.45), rotation=(math.pi/2, 0, 0))
driveshaft = bpy.context.active_object
driveshaft.name = "Driveshaft"
driveshaft.data.materials.append(mat_trim)
link_to_truck(driveshaft)

# =========================================================================
# 2. SCULPTED CREW CAB BODYWORK WITH TUMBLEHOME, PILLARS & RECESSED WINDOWS
# =========================================================================
# Create sculpted Cab Lower Body with contoured rocker panels & shoulder line
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.28, 1.08))
cab_lower = bpy.context.active_object
cab_lower.name = "Cab_LowerBody"
cab_lower.scale = (1.96, 2.54, 0.68)
bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new()
bm.from_mesh(cab_lower.data)
# Subdivide along Y and Z to allow body shoulder crease and rocker taper
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
for v in bm.verts:
    # Taper lower rocker panel slightly inward
    if v.co.z < -0.22:
        v.co.x *= 0.92
    # Bulge mid-door beltline outward
    elif abs(v.co.z) < 0.15:
        v.co.x *= 1.02
bm.to_mesh(cab_lower.data)
bm.free()
cab_lower.data.materials.append(mat_paint)
link_to_truck(cab_lower, bevel=True, bevel_width=0.03, subdiv=1)

# Sculpted Cab Greenhouse (Upper Cabin with realistic A-pillar rake and tumblehome)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.16, 1.66))
cab_upper = bpy.context.active_object
cab_upper.name = "Cab_Greenhouse"
cab_upper.scale = (1.82, 2.02, 0.58)
bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new()
bm.from_mesh(cab_upper.data)
for v in bm.verts:
    if v.co.z > 0:
        # Tumblehome (roof narrower than beltline)
        v.co.x *= 0.88
        # Rake windshield A-pillars backward at top
        if v.co.y > 0:
            v.co.y -= 0.34
        else:
            # Slight C-pillar taper
            v.co.y += 0.06
bm.to_mesh(cab_upper.data)
bm.free()
cab_upper.data.materials.append(mat_paint)
link_to_truck(cab_upper, bevel=True, bevel_width=0.035, subdiv=1)

# Recessed Flush Windshield with Black Frit Border
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.99, 1.65), rotation=(math.radians(30), 0, 0))
windshield = bpy.context.active_object
windshield.name = "FlushWindshield"
windshield.scale = (1.58, 0.025, 0.62)
windshield.data.materials.append(mat_glass)
link_to_truck(windshield, bevel=True, bevel_width=0.008)

# Windshield Wipers
for wx in [-0.38, 0.22]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, 1.15, 1.40), rotation=(math.radians(30), 0, math.radians(-12)))
    wiper = bpy.context.active_object
    wiper.name = f"WindshieldWiper_{wx}"
    wiper.scale = (0.48, 0.018, 0.015)
    wiper.data.materials.append(mat_trim)
    link_to_truck(wiper)

# Side Windows (Front & Rear Crew Cab Doors with Black B-Pillar Divider & Weatherstripping)
for side in [-1, 1]:
    # Black window surround trim
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.855, 0.10, 1.64), rotation=(0, side * math.radians(-11), 0))
    win_frame = bpy.context.active_object
    win_frame.name = f"SideWindowFrame_{side}"
    win_frame.scale = (0.025, 1.62, 0.48)
    win_frame.data.materials.append(mat_trim)
    link_to_truck(win_frame, bevel=True, bevel_width=0.008)
    
    # Front door glass
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.862, 0.46, 1.64), rotation=(0, side * math.radians(-11), 0))
    f_glass = bpy.context.active_object
    f_glass.name = f"FrontDoorGlass_{side}"
    f_glass.scale = (0.022, 0.74, 0.43)
    f_glass.data.materials.append(mat_glass)
    link_to_truck(f_glass)
    
    # Rear crew door glass
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.862, -0.34, 1.64), rotation=(0, side * math.radians(-11), 0))
    r_glass = bpy.context.active_object
    r_glass.name = f"RearDoorGlass_{side}"
    r_glass.scale = (0.022, 0.72, 0.43)
    r_glass.data.materials.append(mat_glass)
    link_to_truck(r_glass)
    
    # Door Seam Panel Lines (Subtle vertical black seam strips at front, B-pillar, and rear door edges)
    for seam_y in [0.92, 0.06, -0.78]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.985, seam_y, 1.08))
        seam = bpy.context.active_object
        seam.name = f"DoorSeam_{side}_{seam_y}"
        seam.scale = (0.006, 0.008, 0.62)
        seam.data.materials.append(mat_trim)
        link_to_truck(seam)

# Rear Cab Window
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.82, 1.66), rotation=(math.radians(-6), 0, 0))
rear_glass = bpy.context.active_object
rear_glass.name = "RearCabWindow"
rear_glass.scale = (1.52, 0.025, 0.44)
rear_glass.data.materials.append(mat_glass)
link_to_truck(rear_glass)

# =========================================================================
# 3. CAB INTERIOR: DASHBOARD, STEERING WHEEL, FRONT & REAR SEATS
# =========================================================================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.82, 1.32))
dash = bpy.context.active_object
dash.name = "InteriorDashboard"
dash.scale = (1.62, 0.38, 0.28)
dash.data.materials.append(mat_interior)
link_to_truck(dash, bevel=True)

bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.022, location=(-0.42, 0.62, 1.42), rotation=(math.radians(65), 0, 0))
s_wheel = bpy.context.active_object
s_wheel.name = "SteeringWheel"
s_wheel.data.materials.append(mat_trim)
link_to_truck(s_wheel)

for sx in [-0.44, 0.44]:
    for sy in [0.28, -0.42]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, 1.28), rotation=(math.radians(-10), 0, 0))
        seat = bpy.context.active_object
        seat.name = f"CabSeat_{sx}_{sy}"
        seat.scale = (0.46, 0.14, 0.56)
        seat.data.materials.append(mat_interior)
        link_to_truck(seat, bevel=True)

# =========================================================================
# 4. SCULPTED POWER-DOME HOOD, COWL VENTS & WIDE FENDER FLARES
# =========================================================================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.88, 1.26), rotation=(math.radians(-3.5), 0, 0))
hood = bpy.context.active_object
hood.name = "SculptedHood"
hood.scale = (1.88, 1.36, 0.24)
bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new()
bm.from_mesh(hood.data)
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
for v in bm.verts:
    # Raised center power dome
    if v.co.z > 0 and abs(v.co.x) < 0.45:
        v.co.z += 0.045
    # Taper front nose slightly
    if v.co.y > 0.4:
        v.co.x *= 0.95
bm.to_mesh(hood.data)
bm.free()
hood.data.materials.append(mat_paint)
link_to_truck(hood, bevel=True, bevel_width=0.025, subdiv=1)

# Heavy-Duty Molded Wheel Arch Fender Flares (Curved Arch Geometry)
for side in [-1, 1]:
    for fy, fname in [(1.55, "Front"), (-1.55, "Rear")]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.54, depth=0.16, location=(side * 0.96, fy, 0.52), rotation=(0, math.pi/2, 0))
        flare = bpy.context.active_object
        flare.name = f"FenderFlare_{fname}_{side}"
        bm = bmesh.new()
        bm.from_mesh(flare.data)
        # Keep only top half of cylinder for wheel arch flare
        del_v = [v for v in bm.verts if v.co.z < -0.05]
        bmesh.ops.delete(bm, geom=del_v, context='VERTS')
        bm.to_mesh(flare.data)
        bm.free()
        mod_s = flare.modifiers.new(name="Solidify", type='SOLIDIFY')
        mod_s.thickness = 0.065
        flare.data.materials.append(mat_trim)
        link_to_truck(flare, smooth=True, subdiv=1)

# =========================================================================
# 5. FRONT GRILLE, PROJECTOR LED HEADLIGHTS, STEEL WINCH BUMPER & BULL BAR
# =========================================================================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.55, 1.08))
grille = bpy.context.active_object
grille.name = "FrontGrilleSurround"
grille.scale = (1.72, 0.10, 0.42)
grille.data.materials.append(mat_trim)
link_to_truck(grille, bevel=True, bevel_width=0.02)

# Twin Chrome Horizontal Grille Bars & Center Hydro Badge
for gz in [1.00, 1.08, 1.16]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.60, gz))
    bar = bpy.context.active_object
    bar.name = f"GrilleChromeBar_{gz}"
    bar.scale = (1.22, 0.03, 0.032)
    bar.data.materials.append(mat_chrome)
    link_to_truck(bar, bevel=True, bevel_width=0.005)

bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.04, location=(0, 2.61, 1.08), rotation=(math.pi/2, 0, 0))
emblem = bpy.context.active_object
emblem.name = "HydroGrilleEmblem"
emblem.data.materials.append(mat_hydro_blue)
link_to_truck(emblem)

# Dual Projector Headlights with C-Shaped DRL Signature
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.73, 2.54, 1.10))
    hl_house = bpy.context.active_object
    hl_house.name = f"HeadlightHousing_{side}"
    hl_house.scale = (0.34, 0.10, 0.24)
    hl_house.data.materials.append(mat_trim)
    link_to_truck(hl_house, bevel=True, bevel_width=0.015)
    
    for px in [-0.07, 0.07]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.06, location=(side * 0.73 + px, 2.58, 1.10), rotation=(math.pi/2, 0, 0))
        led = bpy.context.active_object
        led.name = f"ProjectorLED_{side}_{px}"
        led.data.materials.append(mat_headlight_led)
        link_to_truck(led)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.73, 2.60, 1.10))
    hl_lens = bpy.context.active_object
    hl_lens.name = f"HeadlightClearLens_{side}"
    hl_lens.scale = (0.35, 0.02, 0.25)
    hl_lens.data.materials.append(mat_headlight_glass)
    link_to_truck(hl_lens, bevel=True, bevel_width=0.005)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.88, 2.57, 1.10))
    amber = bpy.context.active_object
    amber.name = f"CornerTurnSignal_{side}"
    amber.scale = (0.055, 0.04, 0.22)
    amber.data.materials.append(mat_amber)
    link_to_truck(amber)

# Heavy-Duty Steel Off-Road Winch Bumper, Skid Plate & Bull Bar
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.64, 0.68))
front_bumper = bpy.context.active_object
front_bumper.name = "SteelWinchBumper"
front_bumper.scale = (2.02, 0.30, 0.32)
front_bumper.data.materials.append(mat_trim)
link_to_truck(front_bumper, bevel=True, bevel_width=0.03)

# Aluminum Front Skid Bash Plate
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 2.48, 0.48), rotation=(math.radians(-28), 0, 0))
skid_plate = bpy.context.active_object
skid_plate.name = "FrontSkidPlate"
skid_plate.scale = (1.15, 0.45, 0.03)
skid_plate.data.materials.append(mat_diamond)
link_to_truck(skid_plate)

# Tubular Bull Bar Hoop & Winch Fairlead + Red D-Ring Shackles
bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=1.35, location=(0, 2.78, 0.96), rotation=(0, math.pi/2, 0))
bull_bar = bpy.context.active_object
bull_bar.name = "BullBarTopHoop"
bull_bar.data.materials.append(mat_trim)
link_to_truck(bull_bar)

for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=0.34, location=(side * 0.66, 2.74, 0.82), rotation=(math.radians(15), 0, 0))
    b_upright = bpy.context.active_object
    b_upright.name = f"BullBarUpright_{side}"
    b_upright.data.materials.append(mat_trim)
    link_to_truck(b_upright)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.052, minor_radius=0.016, location=(side * 0.42, 2.81, 0.64), rotation=(0, math.pi/2, 0))
    dring = bpy.context.active_object
    dring.name = f"RecoveryShackle_{side}"
    dring.data.materials.append(mat_caliper)
    link_to_truck(dring)

# Tubular Side Rock Sliders / Steps with Step Pads
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.036, depth=2.15, location=(side * 1.02, 0.12, 0.56), rotation=(math.pi/2, 0, 0))
    step = bpy.context.active_object
    step.name = f"SideStepBar_{side}"
    step.data.materials.append(mat_trim)
    link_to_truck(step)

# =========================================================================
# 6. TELESCOPIC TOW MIRRORS WITH AMBER LED MARKERS & SCULPTED DOOR HANDLES
# =========================================================================
for side in [-1, 1]:
    # Dual support arms from door frame
    for mz in [1.46, 1.56]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.96, 0.76, mz))
        m_arm = bpy.context.active_object
        m_arm.name = f"TowMirrorArm_{side}_{mz}"
        m_arm.scale = (0.18, 0.035, 0.025)
        m_arm.data.materials.append(mat_trim)
        link_to_truck(m_arm, bevel=True, bevel_width=0.005)
    
    # Vertical Tow Mirror Housing
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.08, 0.74, 1.54), rotation=(0, 0, side * math.radians(12)))
    m_house = bpy.context.active_object
    m_house.name = f"TowMirrorHousing_{side}"
    m_house.scale = (0.14, 0.11, 0.26)
    m_house.data.materials.append(mat_trim)
    link_to_truck(m_house, bevel=True, bevel_width=0.015)
    
    # Mirror Glass (Rear-facing)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.08, 0.682, 1.54), rotation=(0, 0, side * math.radians(12)))
    m_glass = bpy.context.active_object
    m_glass.name = f"TowMirrorGlass_{side}"
    m_glass.scale = (0.12, 0.01, 0.23)
    m_glass.data.materials.append(mat_chrome)
    link_to_truck(m_glass)
    
    # Amber LED Clearance Strip on Mirror Front
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 1.11, 0.795, 1.54), rotation=(0, 0, side * math.radians(12)))
    m_led = bpy.context.active_object
    m_led.name = f"TowMirrorAmberLED_{side}"
    m_led.scale = (0.06, 0.012, 0.14)
    m_led.data.materials.append(mat_amber)
    link_to_truck(m_led)
    
    # Contoured Pull Door Handles with Keyhole Escutcheon
    for dy in [0.35, -0.45]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.995, dy, 1.22))
        d_handle = bpy.context.active_object
        d_handle.name = f"PullDoorHandle_{side}_{dy}"
        d_handle.scale = (0.032, 0.16, 0.038)
        d_handle.data.materials.append(mat_trim)
        link_to_truck(d_handle, bevel=True, bevel_width=0.008)

# =========================================================================
# 7. PICKUP BED, DIAMOND-PLATE TOOLBOX, HEADACHE RACK & AMBER STROBE BEACON
# =========================================================================
# Ribbed Bedliner Floor
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.75, 0.88))
bed_floor = bpy.context.active_object
bed_floor.name = "BedFloorLiner"
bed_floor.scale = (1.88, 1.94, 0.10)
bed_floor.data.materials.append(mat_bedliner)
link_to_truck(bed_floor, bevel=True)

# Crossover Diamond-Plate Aluminum Saddle Toolbox behind Cab
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.04, 1.24))
toolbox = bpy.context.active_object
toolbox.name = "DiamondPlateToolbox"
toolbox.scale = (1.94, 0.46, 0.44)
toolbox.data.materials.append(mat_diamond)
link_to_truck(toolbox, bevel=True, bevel_width=0.015)

# Sculpted Pickup Bed Sides & Top Rail Caps
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.92, -1.75, 1.16))
    bed_side = bpy.context.active_object
    bed_side.name = f"BedSidePanel_{side}"
    bed_side.scale = (0.12, 1.94, 0.56)
    bed_side.data.materials.append(mat_paint)
    link_to_truck(bed_side, bevel=True, bevel_width=0.025, subdiv=1)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.92, -1.75, 1.45))
    rail = bpy.context.active_object
    rail.name = f"BedRailProtector_{side}"
    rail.scale = (0.135, 1.96, 0.032)
    rail.data.materials.append(mat_trim)
    link_to_truck(rail, bevel=True, bevel_width=0.006)

# Tailgate, LED Taillights, Rear Step Bumper & Class V Tow Hitch
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.69, 1.16))
tailgate = bpy.context.active_object
tailgate.name = "Tailgate"
tailgate.scale = (1.86, 0.10, 0.54)
tailgate.data.materials.append(mat_paint)
link_to_truck(tailgate, bevel=True, bevel_width=0.02)

for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(side * 0.89, -2.71, 1.18))
    tl = bpy.context.active_object
    tl.name = f"LEDTaillight_{side}"
    tl.scale = (0.13, 0.06, 0.38)
    tl.data.materials.append(mat_taillight_red)
    link_to_truck(tl, bevel=True, bevel_width=0.01)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.76, 0.66))
rear_bumper = bpy.context.active_object
rear_bumper.name = "RearStepBumper"
rear_bumper.scale = (1.98, 0.22, 0.20)
rear_bumper.data.materials.append(mat_trim)
link_to_truck(rear_bumper, bevel=True, bevel_width=0.02)

# Tubular Chase / Headache Rack & Roof Amber Warning Strobe Bar
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=0.68, location=(side * 0.84, -0.86, 1.76), rotation=(math.radians(-8), 0, 0))
    upright = bpy.context.active_object
    upright.name = f"HeadacheRackUpright_{side}"
    upright.data.materials.append(mat_trim)
    link_to_truck(upright)

bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=1.68, location=(0, -0.81, 2.08), rotation=(0, math.pi/2, 0))
cross_bar = bpy.context.active_object
cross_bar.name = "HeadacheRackCross"
cross_bar.data.materials.append(mat_trim)
link_to_truck(cross_bar)

# Amber Safety Strobe Lightbar on Cab Roof
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.15, 2.00))
strobe_base = bpy.context.active_object
strobe_base.name = "RoofStrobeBase"
strobe_base.scale = (1.12, 0.22, 0.04)
strobe_base.data.materials.append(mat_trim)
link_to_truck(strobe_base, bevel=True, bevel_width=0.008)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.15, 2.04))
strobe_lens = bpy.context.active_object
strobe_lens.name = "RoofAmberStrobeBar"
strobe_lens.scale = (1.08, 0.19, 0.055)
strobe_lens.data.materials.append(mat_amber)
link_to_truck(strobe_lens, bevel=True, bevel_width=0.01)

# =========================================================================
# 8. SCULPTED OFF-ROAD MUD-TERRAIN TIRES WITH TREAD LUGS, ALLOY RIMS & BRAKES
# =========================================================================
wheel_coords = [
    ("FL", -0.96, 1.55),
    ("FR",  0.96, 1.55),
    ("RL", -0.96, -1.55),
    ("RR",  0.96, -1.55),
]

for name, wx, wy in wheel_coords:
    out_dir_sign = 1 if wx > 0 else -1
    
    # Contoured Tire Sidewall Carcass (Torus + Cylinder combo for rounded shoulder profile)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.435, depth=0.31, location=(wx, wy, 0.45), rotation=(0, math.pi/2, 0))
    tire = bpy.context.active_object
    tire.name = f"TireCarcass_{name}"
    tire.data.materials.append(mat_tire)
    link_to_truck(tire, bevel=True, bevel_width=0.045)
    
    # 24 Radial Off-Road Mud-Terrain Tread Lug Blocks around circumference
    num_lugs = 24
    for l_idx in range(num_lugs):
        ang = 2.0 * math.pi * l_idx / num_lugs
        ly = wy + math.cos(ang) * 0.442
        lz = 0.45 + math.sin(ang) * 0.442
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, ly, lz), rotation=(ang, 0, 0))
        lug = bpy.context.active_object
        lug.name = f"TireTreadLug_{name}_{l_idx}"
        lug.scale = (0.28, 0.055, 0.028)
        lug.data.materials.append(mat_tire)
        link_to_truck(lug, bevel=True, bevel_width=0.005)
    
    # Recessed Tire Center Bore (Dark cavity behind spokes)
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.275, depth=0.29, location=(wx, wy, 0.45), rotation=(0, math.pi/2, 0))
    rim_barrel = bpy.context.active_object
    rim_barrel.name = f"RimBarrel_{name}"
    rim_barrel.data.materials.append(mat_trim)
    link_to_truck(rim_barrel)
    
    # Machined Beadlock Outer Rim Lip Ring
    bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=16, major_radius=0.265, minor_radius=0.022, location=(wx + out_dir_sign * 0.135, wy, 0.45), rotation=(0, math.pi/2, 0))
    lip = bpy.context.active_object
    lip.name = f"BeadlockRing_{name}"
    lip.data.materials.append(mat_alloy)
    link_to_truck(lip)
    
    # 6 Split-Spoke Heavy-Duty Alloy Wheel Spokes
    for s in range(6):
        angle = s * (math.pi / 3)
        sy = wy + math.cos(angle) * 0.145
        sz = 0.45 + math.sin(angle) * 0.145
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx + out_dir_sign * 0.115, sy, sz), rotation=(angle, 0, 0))
        spoke = bpy.context.active_object
        spoke.name = f"AlloySpoke_{name}_{s}"
        spoke.scale = (0.032, 0.052, 0.22)
        spoke.data.materials.append(mat_alloy)
        link_to_truck(spoke, bevel=True, bevel_width=0.006)
        
    # Center Locking Hub Cap & 6 Chrome Lug Nuts
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.075, depth=0.06, location=(wx + out_dir_sign * 0.135, wy, 0.45), rotation=(0, math.pi/2, 0))
    hub = bpy.context.active_object
    hub.name = f"CenterHub_{name}"
    hub.data.materials.append(mat_trim)
    link_to_truck(hub, bevel=True, bevel_width=0.008)
    
    for n_idx in range(6):
        n_ang = n_idx * (math.pi / 3) + 0.25
        ny = wy + math.cos(n_ang) * 0.052
        nz = 0.45 + math.sin(n_ang) * 0.052
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.010, depth=0.025, location=(wx + out_dir_sign * 0.158, ny, nz), rotation=(0, math.pi/2, 0))
        lug_nut = bpy.context.active_object
        lug_nut.name = f"LugNut_{name}_{n_idx}"
        lug_nut.data.materials.append(mat_chrome)
        link_to_truck(lug_nut)
    
    # Ventilated Disc Brake Rotor & Twin-Piston Red Caliper
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.22, depth=0.025, location=(wx + out_dir_sign * 0.04, wy, 0.45), rotation=(0, math.pi/2, 0))
    rotor = bpy.context.active_object
    rotor.name = f"BrakeRotor_{name}"
    rotor.data.materials.append(mat_brake)
    link_to_truck(rotor)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx + out_dir_sign * 0.045, wy + 0.15, 0.52))
    caliper = bpy.context.active_object
    caliper.name = f"BrakeCaliper_{name}"
    caliper.scale = (0.075, 0.11, 0.14)
    caliper.data.materials.append(mat_caliper)
    link_to_truck(caliper, bevel=True, bevel_width=0.01)

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
