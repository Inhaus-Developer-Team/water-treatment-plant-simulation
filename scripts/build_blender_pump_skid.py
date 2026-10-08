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
mat_pump_blue = create_pbr_material("PumpIndustrialBlue", (0.08, 0.32, 0.65), metallic=0.35, roughness=0.35)
mat_motor_teal = create_pbr_material("MotorTeal", (0.12, 0.45, 0.52), metallic=0.30, roughness=0.38)
mat_safety_yellow = create_pbr_material("SafetyYellow", (0.92, 0.76, 0.08), metallic=0.15, roughness=0.40)
mat_stainless = create_pbr_material("StainlessSteel316", (0.86, 0.88, 0.90), metallic=0.92, roughness=0.18)
mat_galvanized = create_pbr_material("GalvanizedSteel", (0.55, 0.57, 0.58), metallic=0.75, roughness=0.45)
mat_cast_iron = create_pbr_material("CastIronBlack", (0.12, 0.12, 0.13), metallic=0.80, roughness=0.60)
mat_rubber = create_pbr_material("EPDMRubberBlack", (0.05, 0.05, 0.05), metallic=0.05, roughness=0.88)
mat_estop_red = create_pbr_material("EStopRed", (0.88, 0.05, 0.05), metallic=0.10, roughness=0.30)
mat_gauge_face = create_pbr_material("GaugeDialWhite", (0.95, 0.95, 0.95), metallic=0.05, roughness=0.20)
mat_chrome = create_pbr_material("ChromeTrim", (0.95, 0.95, 0.95), metallic=0.98, roughness=0.05)

skid_root = bpy.data.objects.new("PumpSkid_PC10", None)
bpy.context.scene.collection.objects.link(skid_root)

def link_to_skid(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = skid_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# 1. STRUCTURAL C-CHANNEL BASE SKID (z: 0.00 to 0.14)
# Skid frame rails (X: -1.2 to 1.2, Y: -0.6 to 0.6)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.07))
skid_base = bpy.context.active_object
skid_base.name = "Skid_ChannelFrame"
skid_base.scale = (2.40, 1.20, 0.14)
skid_base.data.materials.append(mat_galvanized)
link_to_skid(skid_base)

# Diamond Plate Top Grating
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.145))
grating = bpy.context.active_object
grating.name = "Skid_DeckPlate"
grating.scale = (2.36, 1.16, 0.015)
grating.data.materials.append(mat_stainless)
link_to_skid(grating)

# 4x Lifting Eye Lugs on corners
for lx, ly in [(-1.12, -0.52), (1.12, -0.52), (-1.12, 0.52), (1.12, 0.52)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.045, minor_radius=0.014, location=(lx, ly, 0.18), rotation=(0, math.pi/2, 0))
    lug = bpy.context.active_object
    lug.name = f"LiftingLug_{lx}_{ly}"
    lug.data.materials.append(mat_safety_yellow)
    link_to_skid(lug)

# 2. DUAL DUPLEX CENTRIFUGAL PUMPS (PC-10A & PC-10B: Lead/Lag)
for idx, py in enumerate([-0.28, 0.28]):
    tag = "A" if idx == 0 else "B"
    
    # Concrete inertia base block
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, py, 0.22))
    pad = bpy.context.active_object
    pad.name = f"InertiaPad_{tag}"
    pad.scale = (1.60, 0.44, 0.14)
    pad.data.materials.append(mat_cast_iron)
    link_to_skid(pad)
    
    # 4x Neoprene vibration isolation mounts
    for vx, vy in [(-0.85, py - 0.18), (-0.85, py + 0.18), (0.55, py - 0.18), (0.55, py + 0.18)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.04, location=(vx, vy, 0.165))
        vib = bpy.context.active_object
        vib.name = f"VibMount_{tag}_{vx}"
        vib.data.materials.append(mat_rubber)
        link_to_skid(vib)
        
    # Pump Volute Casing (Spiral casing)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.24, location=(-0.45, py, 0.44), rotation=(0, math.pi/2, 0))
    volute = bpy.context.active_object
    volute.name = f"PumpVolute_{tag}"
    volute.data.materials.append(mat_pump_blue)
    link_to_skid(volute)
    
    # Volute discharge nozzle (pointing UP)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.22, location=(-0.45, py, 0.62))
    nozzle_d = bpy.context.active_object
    nozzle_d.name = f"DischargeNozzle_{tag}"
    nozzle_d.data.materials.append(mat_pump_blue)
    link_to_skid(nozzle_d)
    
    # Flange ring on discharge nozzle
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.035, location=(-0.45, py, 0.72))
    flange_d = bpy.context.active_object
    flange_d.name = f"DischargeFlange_{tag}"
    flange_d.data.materials.append(mat_stainless)
    link_to_skid(flange_d)
    
    # Volute suction nozzle (pointing LEFT / -X)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.18, location=(-0.65, py, 0.44), rotation=(0, math.pi/2, 0))
    nozzle_s = bpy.context.active_object
    nozzle_s.name = f"SuctionNozzle_{tag}"
    nozzle_s.data.materials.append(mat_pump_blue)
    link_to_skid(nozzle_s)
    
    # Flange ring on suction
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.035, location=(-0.74, py, 0.44), rotation=(0, math.pi/2, 0))
    flange_s = bpy.context.active_object
    flange_s.name = f"SuctionFlange_{tag}"
    flange_s.data.materials.append(mat_stainless)
    link_to_skid(flange_s)
    
    # Hydraulic Institute Standard: ASME Flat-on-Top Eccentric Reducer (Prevents cavitation)
    bpy.ops.mesh.primitive_cone_add(radius1=0.13, radius2=0.09, depth=0.22, location=(-0.86, py, 0.44), rotation=(0, math.pi/2, 0))
    ecc = bpy.context.active_object
    ecc.name = f"EccentricReducer_{tag}"
    ecc.data.materials.append(mat_stainless)
    link_to_skid(ecc)
    
    # Rubber Expansion Joint (Bellows)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.03, location=(-1.00, py, 0.44), rotation=(0, math.pi/2, 0))
    bellows = bpy.context.active_object
    bellows.name = f"SuctionExpansionJoint_{tag}"
    bellows.data.materials.append(mat_rubber)
    link_to_skid(bellows)
    
    # Electric Drive Motor (TEFC)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.48, location=(0.02, py, 0.44), rotation=(0, math.pi/2, 0))
    motor = bpy.context.active_object
    motor.name = f"TEFC_Motor_{tag}"
    motor.data.materials.append(mat_motor_teal)
    link_to_skid(motor)
    
    # Motor Cooling Fan Shroud
    bpy.ops.mesh.primitive_cylinder_add(radius=0.195, depth=0.12, location=(0.30, py, 0.44), rotation=(0, math.pi/2, 0))
    fan_cowl = bpy.context.active_object
    fan_cowl.name = f"FanCowl_{tag}"
    fan_cowl.data.materials.append(mat_cast_iron)
    link_to_skid(fan_cowl)
    
    # Motor Terminal Junction Box
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.02, py + 0.16, 0.58))
    jbox = bpy.context.active_object
    jbox.name = f"MotorJunctionBox_{tag}"
    jbox.scale = (0.16, 0.12, 0.14)
    jbox.data.materials.append(mat_safety_yellow)
    link_to_skid(jbox)
    
    # OSHA Shaft Coupling Guard
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.20, location=(-0.24, py, 0.44), rotation=(0, math.pi/2, 0))
    guard = bpy.context.active_object
    guard.name = f"CouplingGuard_{tag}"
    guard.data.materials.append(mat_safety_yellow)
    link_to_skid(guard)
    
    # Discharge Piping: Concentric Expander + Check Valve + Butterfly Valve
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.11, depth=0.16, location=(-0.45, py, 0.81))
    conc = bpy.context.active_object
    conc.name = f"ConcentricExpander_{tag}"
    conc.data.materials.append(mat_stainless)
    link_to_skid(conc)
    
    # Butterfly Valve Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.08, location=(-0.45, py, 0.94))
    bfv = bpy.context.active_object
    bfv.name = f"ButterflyValve_{tag}"
    bfv.data.materials.append(mat_cast_iron)
    link_to_skid(bfv)
    
    # Valve Handwheel Gear Operator
    bpy.ops.mesh.primitive_torus_add(major_radius=0.09, minor_radius=0.012, location=(-0.45, py + 0.18, 1.02), rotation=(math.pi/2, 0, 0))
    hwheel = bpy.context.active_object
    hwheel.name = f"ValveHandwheel_{tag}"
    hwheel.data.materials.append(mat_estop_red)
    link_to_skid(hwheel)
    
    # Pressure Gauge with Syphon Loop
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.15, location=(-0.45, py, 1.10))
    syphon = bpy.context.active_object
    syphon.name = f"GaugeStem_{tag}"
    syphon.data.materials.append(mat_stainless)
    link_to_skid(syphon)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.035, location=(-0.45, py, 1.20), rotation=(math.pi/2, 0, 0))
    gauge = bpy.context.active_object
    gauge.name = f"BourdonGauge_{tag}"
    gauge.data.materials.append(mat_stainless)
    link_to_skid(gauge)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.005, location=(-0.45, py - 0.018, 1.20), rotation=(math.pi/2, 0, 0))
    dial = bpy.context.active_object
    dial.name = f"GaugeDial_{tag}"
    dial.data.materials.append(mat_gauge_face)
    link_to_skid(dial)

# 3. MAGNETIC FLOW METER (Magmeter) ON COMMON DISCHARGE
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.32, location=(0.60, 0, 0.94), rotation=(0, math.pi/2, 0))
magmeter = bpy.context.active_object
magmeter.name = "Magmeter_Body"
magmeter.data.materials.append(mat_pump_blue)
link_to_skid(magmeter)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.60, 0, 1.18))
mag_head = bpy.context.active_object
mag_head.name = "Magmeter_Transmitter"
mag_head.scale = (0.16, 0.16, 0.18)
mag_head.data.materials.append(mat_safety_yellow)
link_to_skid(mag_head)

# 4. EMERGENCY STOP STATION (OSHA E-STOP)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=1.10, location=(1.02, 0.48, 0.65))
stanchion = bpy.context.active_object
stanchion.name = "EStop_Stanchion"
stanchion.data.materials.append(mat_safety_yellow)
link_to_skid(stanchion)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.02, 0.48, 1.22))
estop_box = bpy.context.active_object
estop_box.name = "EStop_Enclosure"
estop_box.scale = (0.12, 0.10, 0.16)
estop_box.data.materials.append(mat_safety_yellow)
link_to_skid(estop_box)

bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.035, location=(1.02, 0.42, 1.22), rotation=(math.pi/2, 0, 0))
estop_btn = bpy.context.active_object
estop_btn.name = "EStop_MushroomButton"
estop_btn.data.materials.append(mat_estop_red)
link_to_skid(estop_btn)

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
