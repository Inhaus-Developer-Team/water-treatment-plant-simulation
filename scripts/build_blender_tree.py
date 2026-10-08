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
        
    return mat

mat_bark = create_pbr_material("TreeBarkOak", (0.28, 0.20, 0.14), metallic=0.0, roughness=0.92)
mat_leaves_dark = create_pbr_material("TreeCanopyDark", (0.16, 0.35, 0.12), metallic=0.0, roughness=0.65)
mat_leaves_light = create_pbr_material("TreeCanopyLight", (0.24, 0.48, 0.18), metallic=0.0, roughness=0.60)

tree_root = bpy.data.objects.new("RealisticDeciduousTree", None)
bpy.context.scene.collection.objects.link(tree_root)

def link_to_tree(obj, smooth=True):
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = tree_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

# 1. ROOT BUTTRESS & TRUNK
# Flared base
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.6, location=(0, 0, 0.3))
base = bpy.context.active_object
base.name = "TrunkBase"
base.scale = (1.2, 0.95, 1.0)
base.data.materials.append(mat_bark)
link_to_tree(base)

# Main Trunk (Tapering upward)
bpy.ops.mesh.primitive_cone_add(radius1=0.38, radius2=0.22, depth=3.2, location=(0, 0, 2.0))
trunk = bpy.context.active_object
trunk.name = "MainTrunk"
trunk.data.materials.append(mat_bark)
link_to_tree(trunk)

# Main Branches
branch_data = [
    ((0.35, 0.25, 3.4), (0.12, 0.08), 1.6, math.radians(35), math.radians(40)),
    ((-0.38, 0.20, 3.6), (0.11, 0.07), 1.5, math.radians(-38), math.radians(25)),
    ((0.15, -0.35, 3.8), (0.10, 0.06), 1.4, math.radians(20), math.radians(-45)),
    ((-0.20, -0.30, 4.0), (0.09, 0.05), 1.3, math.radians(-30), math.radians(-35)),
    ((0.0, 0.10, 4.5), (0.12, 0.06), 1.8, math.radians(10), math.radians(15)),
]

for idx, (loc, (r1, r2), length, rx, ry) in enumerate(branch_data):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=length, location=loc, rotation=(rx, ry, 0))
    branch = bpy.context.active_object
    branch.name = f"Branch_{idx}"
    branch.data.materials.append(mat_bark)
    link_to_tree(branch)

# 2. MULTI-CLUSTER VOLUMETRIC CANOPY CLUSTERS
canopy_clusters = [
    ((0.0, 0.0, 5.8), (1.5, 1.5, 1.2), mat_leaves_light),
    ((0.7, 0.5, 4.8), (1.2, 1.3, 1.0), mat_leaves_dark),
    ((-0.8, 0.4, 5.0), (1.3, 1.2, 1.1), mat_leaves_light),
    ((0.3, -0.8, 4.9), (1.25, 1.15, 1.0), mat_leaves_dark),
    ((-0.5, -0.6, 5.2), (1.1, 1.2, 0.95), mat_leaves_light),
    ((0.0, 0.3, 4.4), (1.4, 1.35, 1.1), mat_leaves_dark),
    ((0.5, -0.3, 6.2), (1.0, 1.0, 0.9), mat_leaves_light),
    ((-0.4, 0.2, 6.4), (0.95, 1.05, 0.85), mat_leaves_dark),
    ((0.0, 0.0, 6.9), (0.8, 0.85, 0.75), mat_leaves_light),
]

for idx, (loc, scale, mat) in enumerate(canopy_clusters):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=loc)
    puff = bpy.context.active_object
    puff.name = f"CanopyPuff_{idx}"
    puff.scale = scale
    puff.data.materials.append(mat)
    link_to_tree(puff)

# Export as GLB
out_path = "/Users/inhausuxui/.gemini/antigravity/scratch/water-treatment-plant-simulation/assets/models/realistic_tree.glb"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=out_path,
    export_format='GLB',
    use_selection=False,
    export_materials='EXPORT',
    export_apply=True
)
print(f"SUCCESS: Exported {out_path} ({os.path.getsize(out_path)} bytes)")
