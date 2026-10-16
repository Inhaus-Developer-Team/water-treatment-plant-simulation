import bpy
import bmesh
import math
import os
import random

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

mat_bark = create_pbr_material("TreeBarkOak", (0.14, 0.09, 0.05), metallic=0.0, roughness=0.92)
mat_leaves_deep = create_pbr_material("CanopyDeepGreen", (0.03, 0.11, 0.02), metallic=0.0, roughness=0.84)
mat_leaves_mid  = create_pbr_material("CanopyMidGreen",  (0.06, 0.18, 0.04), metallic=0.0, roughness=0.78)
mat_leaves_sun  = create_pbr_material("CanopySunlitGreen", (0.11, 0.27, 0.06), metallic=0.0, roughness=0.74)

tree_root = bpy.data.objects.new("RealisticDeciduousTree", None)
bpy.context.scene.collection.objects.link(tree_root)

def link_to_tree(obj, smooth=True):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = tree_root
    if obj.type == 'MESH' and smooth:
        for poly in obj.data.polygons:
            poly.use_smooth = True

def create_gnarled_branch(name, points_radii, seed=42, segments=16):
    """Creates a gnarled organic trunk/branch with bark furrow displacement"""
    random.seed(seed)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for idx, (x, y, z, r) in enumerate(points_radii):
        ring = []
        for s in range(segments):
            ang = 2.0 * math.pi * s / segments
            # Root flare and organic bark ridges
            furrow = 1.0 + 0.08 * math.sin(ang * 5.0 + z * 1.8) + 0.05 * math.cos(ang * 3.0 - z * 1.2)
            if z < 0.6:
                # Buttress root flare at base
                furrow += (0.6 - z) * 0.45 * max(0.0, math.cos(ang * 4.0))
            vx = x + math.cos(ang) * r * furrow
            vy = y + math.sin(ang) * r * furrow
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
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_bark)
    link_to_tree(obj, smooth=True)
    return obj

# 1. GNARLED MAIN TRUNK WITH ROOT FLARES (Z: 0.0 to 3.8m)
trunk_pts = [
    (0.00,  0.00, 0.00, 0.48),
    (0.02, -0.01, 0.40, 0.36),
    (0.04,  0.02, 1.00, 0.31),
    (0.01,  0.05, 1.70, 0.28),
    (-0.03, 0.03, 2.40, 0.25),
    (-0.02, 0.00, 3.10, 0.21),
    (0.00, -0.02, 3.70, 0.16),
]
create_gnarled_branch("MainOakTrunk", trunk_pts, seed=101, segments=20)

# Primary Boughs & Secondary Forking Limbs
boughs = [
    # Bough 1 (+X, +Y)
    [(0.01, 0.03, 2.2, 0.18), (0.35, 0.28, 2.9, 0.14), (0.85, 0.62, 3.6, 0.10), (1.35, 0.95, 4.3, 0.06)],
    # Bough 2 (-X, +Y)
    [(-0.02, 0.02, 2.5, 0.17), (-0.42, 0.30, 3.2, 0.13), (-0.95, 0.65, 3.9, 0.09), (-1.45, 0.90, 4.5, 0.05)],
    # Bough 3 (+X, -Y)
    [(0.00, -0.01, 2.7, 0.16), (0.40, -0.38, 3.4, 0.12), (0.90, -0.82, 4.1, 0.08), (1.30, -1.15, 4.7, 0.05)],
    # Bough 4 (-X, -Y)
    [(-0.02, -0.01, 2.9, 0.15), (-0.38, -0.35, 3.6, 0.11), (-0.85, -0.78, 4.3, 0.08), (-1.25, -1.10, 4.8, 0.05)],
    # Bough 5 (Central Crown Leader)
    [(0.00, -0.02, 3.5, 0.15), (0.08, 0.12, 4.3, 0.11), (0.15, 0.20, 5.1, 0.07), (0.10, 0.15, 5.8, 0.04)],
]
for b_idx, b_pts in enumerate(boughs):
    create_gnarled_branch(f"PrimaryBough_{b_idx}", b_pts, seed=200 + b_idx, segments=12)

# 2. ORGANIC FOLIAGE CANOPY CLUSTERS WITH IRREGULAR LEAFY DISPLACEMENT
# Instead of smooth balloons, displace vertices radially with multi-frequency botanical noise
canopy_specs = [
    # Lower shaded skirt clusters (Deep Green)
    (( 1.35,  0.95, 4.3), (1.15, 1.10, 0.72), mat_leaves_deep, 11),
    ((-1.40,  0.88, 4.4), (1.20, 1.05, 0.75), mat_leaves_deep, 12),
    (( 1.25, -1.10, 4.5), (1.10, 1.15, 0.70), mat_leaves_deep, 13),
    ((-1.20, -1.05, 4.6), (1.15, 1.10, 0.72), mat_leaves_deep, 14),
    (( 0.05,  1.45, 4.4), (1.05, 0.95, 0.68), mat_leaves_deep, 15),
    ((-0.05, -1.40, 4.5), (1.05, 1.00, 0.68), mat_leaves_deep, 16),
    
    # Mid-canopy volume clusters (Mid Green)
    (( 0.85,  0.55, 5.1), (1.35, 1.25, 0.88), mat_leaves_mid, 21),
    ((-0.90,  0.50, 5.2), (1.30, 1.30, 0.90), mat_leaves_mid, 22),
    (( 0.75, -0.65, 5.2), (1.25, 1.30, 0.85), mat_leaves_mid, 23),
    ((-0.80, -0.60, 5.3), (1.30, 1.20, 0.88), mat_leaves_mid, 24),
    (( 0.00,  0.00, 4.9), (1.50, 1.45, 0.95), mat_leaves_mid, 25),
    (( 1.55, -0.10, 4.8), (0.95, 1.05, 0.75), mat_leaves_mid, 26),
    ((-1.55,  0.05, 4.9), (1.00, 1.00, 0.75), mat_leaves_mid, 27),
    
    # Upper sunlit crown puffs (Sunlit Green)
    (( 0.45,  0.40, 5.9), (1.15, 1.10, 0.82), mat_leaves_sun, 31),
    ((-0.50,  0.35, 6.0), (1.10, 1.15, 0.80), mat_leaves_sun, 32),
    (( 0.35, -0.45, 6.0), (1.05, 1.10, 0.78), mat_leaves_sun, 33),
    ((-0.40, -0.40, 6.1), (1.10, 1.05, 0.80), mat_leaves_sun, 34),
    (( 0.05,  0.05, 6.5), (1.20, 1.15, 0.82), mat_leaves_sun, 35),
    (( 0.00, -0.05, 7.0), (0.85, 0.85, 0.65), mat_leaves_sun, 36),
]

for idx, (loc, scale, mat, seed) in enumerate(canopy_specs):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=loc)
    puff = bpy.context.active_object
    puff.name = f"BotanicalCanopy_{idx}"
    
    # Apply organic multi-frequency displacement in bmesh so it looks like ruffled leaf clusters, not spheres
    bm = bmesh.new()
    bm.from_mesh(puff.data)
    for v in bm.verts:
        nx, ny, nz = v.co.x, v.co.y, v.co.z
        # High-frequency botanical leaf clumping noise
        clump = (
            0.16 * math.sin(nx * 4.5 + seed) * math.cos(ny * 4.5 - seed) +
            0.12 * math.cos(nz * 5.2 + nx * 3.8) +
            0.08 * math.sin((nx + ny + nz) * 7.5 + seed * 1.7)
        )
        # Flatten bottom slightly like real tree foliage sub-crowns
        z_squash = 0.75 if nz < 0 else 1.0
        v.co.x = nx * scale[0] * (1.0 + clump)
        v.co.y = ny * scale[1] * (1.0 + clump)
        v.co.z = nz * scale[2] * z_squash * (1.0 + clump * 0.8)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(puff.data)
    bm.free()
    
    puff.data.materials.append(mat)
    link_to_tree(puff, smooth=True)

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
