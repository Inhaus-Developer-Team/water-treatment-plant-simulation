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

# Materials
mat_pump_blue = create_pbr_material("PumpIndustrialBlue", (0.06, 0.30, 0.64), metallic=0.40, roughness=0.28, clearcoat=0.5)
mat_motor_teal = create_pbr_material("MotorTeal", (0.10, 0.44, 0.52), metallic=0.35, roughness=0.32)
mat_safety_yellow = create_pbr_material("SafetyYellow", (0.94, 0.76, 0.05), metallic=0.15, roughness=0.35)
mat_stainless = create_pbr_material("StainlessSteel316", (0.86, 0.88, 0.91), metallic=0.94, roughness=0.16)
mat_galvanized = create_pbr_material("GalvanizedSteel", (0.52, 0.54, 0.56), metallic=0.78, roughness=0.42)
mat_cast_iron = create_pbr_material("CastIronBlack", (0.11, 0.11, 0.12), metallic=0.82, roughness=0.55)
mat_rubber = create_pbr_material("EPDMRubberBlack", (0.04, 0.04, 0.045), metallic=0.05, roughness=0.86)
mat_estop_red = create_pbr_material("EStopRed", (0.88, 0.05, 0.05), metallic=0.15, roughness=0.26)
mat_gauge_face = create_pbr_material("GaugeDialWhite", (0.96, 0.96, 0.98), metallic=0.05, roughness=0.15)
mat_panel_gray = create_pbr_material("NEMAPanelGray", (0.72, 0.74, 0.76), metallic=0.35, roughness=0.30)

skid_root = bpy.data.objects.new("PumpSkid_PC10", None)
bpy.context.scene.collection.objects.link(skid_root)

def link_to_skid(obj, smooth=True):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = skid_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

def add_bolted_flange(name, loc, rot, pipe_r, flange_r, thickness=0.032, num_bolts=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=flange_r, depth=thickness, location=loc, rotation=rot)
    fl = bpy.context.active_object
    fl.name = name
    fl.data.materials.append(mat_stainless)
    link_to_skid(fl)
    # Add hex bolts around bolt circle
    bc_r = (pipe_r + flange_r) * 0.52
    for b in range(num_bolts):
        ang = 2.0 * math.pi * b / num_bolts
        if abs(rot[1]) > 0.5: # X-aligned flange
            bx = loc[0]
            by = loc[1] + math.cos(ang) * bc_r
            bz = loc[2] + math.sin(ang) * bc_r
        elif abs(rot[0]) > 0.5: # Y-aligned flange
            bx = loc[0] + math.cos(ang) * bc_r
            by = loc[1]
            bz = loc[2] + math.sin(ang) * bc_r
        else: # Z-aligned flange
            bx = loc[0] + math.cos(ang) * bc_r
            by = loc[1] + math.sin(ang) * bc_r
            bz = loc[2]
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.009, depth=thickness + 0.018, location=(bx, by, bz), rotation=rot)
        bolt = bpy.context.active_object
        bolt.name = f"{name}_Bolt_{b}"
        bolt.data.materials.append(mat_cast_iron)
        link_to_skid(bolt)

# =========================================================================
# 1. STRUCTURAL C-CHANNEL BASE SKID, FORKLIFT POCKETS & DIAMOND PLATE DECK
# =========================================================================
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.07))
skid_base = bpy.context.active_object
skid_base.name = "Skid_ChannelFrame"
skid_base.scale = (2.40, 1.24, 0.14)
skid_base.data.materials.append(mat_galvanized)
link_to_skid(skid_base)

# Forklift tine pockets on front/back of C-channel skid
for fx in [-0.55, 0.55]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, 0, 0.055))
    pocket = bpy.context.active_object
    pocket.name = f"ForkliftPocket_{fx}"
    pocket.scale = (0.22, 1.26, 0.08)
    pocket.data.materials.append(mat_cast_iron)
    link_to_skid(pocket)

# Diamond Plate Top Deck & Perimeter Drip Rim
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.145))
grating = bpy.context.active_object
grating.name = "Skid_DeckPlate"
grating.scale = (2.34, 1.18, 0.016)
grating.data.materials.append(mat_stainless)
link_to_skid(grating)

# 4x Heavy Lifting Eye Lugs on corners
for lx, ly in [(-1.12, -0.54), (1.12, -0.54), (-1.12, 0.54), (1.12, 0.54)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.045, minor_radius=0.014, location=(lx, ly, 0.18), rotation=(0, math.pi/2, 0))
    lug = bpy.context.active_object
    lug.name = f"LiftingLug_{lx}_{ly}"
    lug.data.materials.append(mat_safety_yellow)
    link_to_skid(lug)

# =========================================================================
# 2. DUPLEX SIMPLEX BASKET STRAINERS ON SUCTION MANIFOLD (X = -1.02)
# =========================================================================
# Common 6" Suction Header Manifold along Y at X = -1.12, Z = 0.44
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.095, depth=0.92, location=(-1.12, 0, 0.44), rotation=(math.pi/2, 0, 0))
s_header = bpy.context.active_object
s_header.name = "CommonSuctionHeader"
s_header.data.materials.append(mat_stainless)
link_to_skid(s_header)

# =========================================================================
# 3. DUAL DUPLEX CENTRIFUGAL PUMPS (PC-10A & PC-10B: Lead/Lag)
# =========================================================================
for idx, py in enumerate([-0.30, 0.30]):
    tag = "A" if idx == 0 else "B"
    
    # Cast Inertia Base Pad + 4x Neoprene Spring Vibration Isolators
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.10, py, 0.21))
    pad = bpy.context.active_object
    pad.name = f"InertiaPad_{tag}"
    pad.scale = (1.52, 0.44, 0.12)
    pad.data.materials.append(mat_cast_iron)
    link_to_skid(pad)
    
    for vx, vy in [(-0.78, py - 0.18), (-0.78, py + 0.18), (0.58, py - 0.18), (0.58, py + 0.18)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.036, depth=0.04, location=(vx, vy, 0.165))
        vib = bpy.context.active_object
        vib.name = f"VibMount_{tag}_{vx}"
        vib.data.materials.append(mat_rubber)
        link_to_skid(vib)
    
    # Coarse Simplex Basket Strainer Housing with Bolted Quick-Release Cover & Davit
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.125, depth=0.46, location=(-0.96, py, 0.42))
    strainer = bpy.context.active_object
    strainer.name = f"BasketStrainer_{tag}"
    strainer.data.materials.append(mat_pump_blue)
    link_to_skid(strainer)
    
    add_bolted_flange(f"StrainerCover_{tag}", (-0.96, py, 0.66), (0, 0, 0), 0.08, 0.145, thickness=0.028, num_bolts=8)
    
    # Pump Volute Spiral Casing
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.22, depth=0.22, location=(-0.44, py, 0.44), rotation=(0, math.pi/2, 0))
    volute = bpy.context.active_object
    volute.name = f"PumpVolute_{tag}"
    volute.data.materials.append(mat_pump_blue)
    link_to_skid(volute)
    
    # Suction Nozzle, Bolted Flange & ASME Flat-on-Top Eccentric Reducer
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.085, depth=0.22, location=(-0.62, py, 0.44), rotation=(0, math.pi/2, 0))
    nozzle_s = bpy.context.active_object
    nozzle_s.name = f"SuctionNozzle_{tag}"
    nozzle_s.data.materials.append(mat_pump_blue)
    link_to_skid(nozzle_s)
    
    add_bolted_flange(f"SuctionFlange_{tag}", (-0.72, py, 0.44), (0, math.pi/2, 0), 0.085, 0.13, num_bolts=8)
    
    # Molded Twin-Sphere EPDM Rubber Expansion Joint
    for rx_off in [-0.79, -0.85]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.025, location=(rx_off, py, 0.44), rotation=(0, math.pi/2, 0))
        bellows = bpy.context.active_object
        bellows.name = f"EPDM_Bellows_{tag}_{rx_off}"
        bellows.data.materials.append(mat_rubber)
        link_to_skid(bellows)
    
    # TEFC Electric Drive Motor with Axial Cooling Fins, Eye Bolt & Conduit Box
    bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=0.185, depth=0.48, location=(0.06, py, 0.44), rotation=(0, math.pi/2, 0))
    motor = bpy.context.active_object
    motor.name = f"TEFC_Motor_{tag}"
    motor.data.materials.append(mat_motor_teal)
    link_to_skid(motor)
    
    # 12 Axial Motor Cooling Fins around Motor Stator
    for f_idx in range(12):
        f_ang = 2.0 * math.pi * f_idx / 12
        fy = py + math.cos(f_ang) * 0.188
        fz = 0.44 + math.sin(f_ang) * 0.188
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.04, fy, fz), rotation=(f_ang, 0, 0))
        fin = bpy.context.active_object
        fin.name = f"MotorFin_{tag}_{f_idx}"
        fin.scale = (0.36, 0.008, 0.024)
        fin.data.materials.append(mat_motor_teal)
        link_to_skid(fin)
        
    # Top Forged Lifting Eye Bolt on Motor
    bpy.ops.mesh.primitive_torus_add(major_radius=0.032, minor_radius=0.009, location=(0.04, py, 0.65), rotation=(0, math.pi/2, 0))
    m_eye = bpy.context.active_object
    m_eye.name = f"MotorEyeBolt_{tag}"
    m_eye.data.materials.append(mat_stainless)
    link_to_skid(m_eye)
    
    # Fan Shroud Cowl & Terminal Box
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.192, depth=0.13, location=(0.34, py, 0.44), rotation=(0, math.pi/2, 0))
    fan_cowl = bpy.context.active_object
    fan_cowl.name = f"FanCowl_{tag}"
    fan_cowl.data.materials.append(mat_cast_iron)
    link_to_skid(fan_cowl)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.06, py + (0.17 if idx == 1 else -0.17), 0.56))
    jbox = bpy.context.active_object
    jbox.name = f"MotorJunctionBox_{tag}"
    jbox.scale = (0.14, 0.11, 0.13)
    jbox.data.materials.append(mat_safety_yellow)
    link_to_skid(jbox)
    
    # OSHA Perforated Shaft Coupling Guard
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.13, depth=0.20, location=(-0.22, py, 0.44), rotation=(0, math.pi/2, 0))
    guard = bpy.context.active_object
    guard.name = f"CouplingGuard_{tag}"
    guard.data.materials.append(mat_safety_yellow)
    link_to_skid(guard)
    
    # Discharge Riser Nozzle, Bolted Flanges, Swing Check Valve, Butterfly Isolation Valve & Gauge
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.075, depth=0.48, location=(-0.44, py, 0.72))
    nozzle_d = bpy.context.active_object
    nozzle_d.name = f"DischargeRiser_{tag}"
    nozzle_d.data.materials.append(mat_stainless)
    link_to_skid(nozzle_d)
    
    add_bolted_flange(f"DischargeFlange_{tag}", (-0.44, py, 0.66), (0, 0, 0), 0.075, 0.125, num_bolts=8)
    add_bolted_flange(f"CheckValveFlange_{tag}", (-0.44, py, 0.88), (0, 0, 0), 0.075, 0.125, num_bolts=8)
    
    # Wafer Butterfly Valve Body + Red Gear Handwheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.125, depth=0.07, location=(-0.44, py, 0.94))
    bfv = bpy.context.active_object
    bfv.name = f"ButterflyValve_{tag}"
    bfv.data.materials.append(mat_cast_iron)
    link_to_skid(bfv)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.013, location=(-0.44, py + (0.19 if idx == 1 else -0.19), 0.96), rotation=(math.pi/2, 0, 0))
    hwheel = bpy.context.active_object
    hwheel.name = f"ValveHandwheel_{tag}"
    hwheel.data.materials.append(mat_estop_red)
    link_to_skid(hwheel)
    
    # Bourdon Pressure Gauge with Coil Pigtail Syphon
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.035, location=(-0.44, py, 1.16), rotation=(math.pi/2, 0, 0))
    gauge = bpy.context.active_object
    gauge.name = f"BourdonGauge_{tag}"
    gauge.data.materials.append(mat_stainless)
    link_to_skid(gauge)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.006, location=(-0.44, py - 0.018, 1.16), rotation=(math.pi/2, 0, 0))
    dial = bpy.context.active_object
    dial.name = f"GaugeDial_{tag}"
    dial.data.materials.append(mat_gauge_face)
    link_to_skid(dial)

# =========================================================================
# 4. COMMON DISCHARGE HEADER, ELECTROMAGNETIC FLOWMETER & NEMA-4X VFD PANEL
# =========================================================================
# Transverse Discharge Manifold uniting Pump A and Pump B at X = -0.44, Z = 1.00
bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.085, depth=0.68, location=(-0.44, 0, 1.00), rotation=(math.pi/2, 0, 0))
d_manifold = bpy.context.active_object
d_manifold.name = "DischargeManifold"
d_manifold.data.materials.append(mat_stainless)
link_to_skid(d_manifold)

# Main Discharge Pipe Header running to +X (through Magmeter)
bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.088, depth=1.35, location=(0.24, 0, 1.00), rotation=(0, math.pi/2, 0))
d_pipe = bpy.context.active_object
d_pipe.name = "MainDischargeHeader"
d_pipe.data.materials.append(mat_stainless)
link_to_skid(d_pipe)

# Electromagnetic Flowmeter (Magmeter) with Twin Bolted Flanges & Digital Transmitter Head
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.145, depth=0.30, location=(0.48, 0, 1.00), rotation=(0, math.pi/2, 0))
magmeter = bpy.context.active_object
magmeter.name = "Magmeter_Body"
magmeter.data.materials.append(mat_pump_blue)
link_to_skid(magmeter)

add_bolted_flange("MagmeterFlange_In",  (0.32, 0, 1.00), (0, math.pi/2, 0), 0.088, 0.148, num_bolts=8)
add_bolted_flange("MagmeterFlange_Out", (0.64, 0, 1.00), (0, math.pi/2, 0), 0.088, 0.148, num_bolts=8)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.48, 0, 1.24))
mag_head = bpy.context.active_object
mag_head.name = "Magmeter_Transmitter"
mag_head.scale = (0.16, 0.16, 0.18)
mag_head.data.materials.append(mat_safety_yellow)
link_to_skid(mag_head)

# NEMA-4X Stainless Steel Local VFD Control Panel on Skid Unistrut Stand + E-Stop
for sx in [0.78, 1.08]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=1.25, location=(sx, -0.46, 0.76))
    leg = bpy.context.active_object
    leg.name = f"VFDPanelStand_{sx}"
    leg.data.materials.append(mat_galvanized)
    link_to_skid(leg)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.93, -0.42, 1.08))
vfd_panel = bpy.context.active_object
vfd_panel.name = "NEMA4X_VFDPanel"
vfd_panel.scale = (0.44, 0.22, 0.56)
vfd_panel.data.materials.append(mat_panel_gray)
link_to_skid(vfd_panel)

# Rotary Disconnect Handle & Red Mushroom E-Stop Button on VFD Panel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.08, -0.30, 1.12))
disc = bpy.context.active_object
disc.name = "RotaryDisconnect"
disc.scale = (0.04, 0.04, 0.12)
disc.data.materials.append(mat_estop_red)
link_to_skid(disc)

# OSHA Emergency Stop Pedestal on Front Corner
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=1.05, location=(1.02, 0.48, 0.65))
stanchion = bpy.context.active_object
stanchion.name = "EStop_Stanchion"
stanchion.data.materials.append(mat_safety_yellow)
link_to_skid(stanchion)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.02, 0.48, 1.18))
ebox = bpy.context.active_object
ebox.name = "EStop_Box"
ebox.scale = (0.12, 0.12, 0.14)
ebox.data.materials.append(mat_safety_yellow)
link_to_skid(ebox)

bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.04, location=(1.02, 0.55, 1.18), rotation=(math.pi/2, 0, 0))
ebtn = bpy.context.active_object
ebtn.name = "EStop_MushroomButton"
ebtn.data.materials.append(mat_estop_red)
link_to_skid(ebtn)

# Export as GLB
out_path = "/Users/inhausuxui/.gemini/antigravity/scratch/water-treatment-plant-simulation/assets/models/pump_skid.glb"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {out_path} ({os.path.getsize(out_path)} bytes)")
