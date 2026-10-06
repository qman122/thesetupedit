"""Photoreal render of one bezel style with Blender Cycles.
usage: python rr_render.py STYLE SHOT DRL(white|amber|off) OUT.png [res_pct] [samples]"""
import json, math, os, sys
import bpy, bmesh
from mathutils import Vector
S = os.path.dirname(os.path.abspath(__file__))
st, shot, drl, out = sys.argv[1:5]
pct = int(sys.argv[5]) if len(sys.argv) > 5 else 100
spp = int(sys.argv[6]) if len(sys.argv) > 6 else 160
D = os.path.join(S, 'scene', st)
sc = json.load(open(os.path.join(D, 'scene.json')))
MM = 0.001

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- materials ----------
def principled(name, base, rough, metal=0.0, coat=0.0, coat_rough=0.03, trans=0.0, ior=1.5, emit=None, emit_strength=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = coat_rough
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    b.inputs['Specular IOR Level'].default_value = spec
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_strength
    return m, b

satin, sb = principled('satin black', (0.010, 0.010, 0.011), 0.42, coat=0.25, coat_rough=0.32)
# a faint print-texture in the roughness, so the satin doesn't read as CG-perfect
nt = satin.node_tree
noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 900.0; noise.inputs['Detail'].default_value = 6
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.36; mr.inputs['To Max'].default_value = 0.50
nt.links.new(noise.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], sb.inputs['Roughness'])
bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.04
nt.links.new(noise.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], sb.inputs['Normal'])

paint, _ = principled('torch red', (0.50, 0.012, 0.010), 0.38, metal=0.25, coat=1.0, coat_rough=0.02)
alu, _ = principled('black anodised', (0.025, 0.025, 0.028), 0.33, metal=1.0)
chrome, _ = principled('chrome', (0.92, 0.92, 0.93), 0.06, metal=1.0)
smoked, _ = principled('smoked reflector', (0.35, 0.36, 0.38), 0.18, metal=1.0)
glass, _ = principled('lens glass', (0.96, 0.98, 1.0), 0.0, trans=1.0, ior=1.52)
dark, _ = principled('emitter', (0.02, 0.022, 0.03), 0.25)
floor_m, _ = principled('floor', (0.005, 0.005, 0.006), 0.32, spec=0.5)
col = {'white': (1.0, 0.97, 0.92), 'amber': (1.0, 0.22, 0.0)}.get(drl)
if col:
    diffuser, _ = principled('diffuser lit', (0.9, 0.9, 0.9) if drl == 'white' else (0.3, 0.07, 0.0), 0.5, emit=col, emit_strength=38.0 if drl == 'white' else 6.0)
else:
    diffuser, _ = principled('diffuser off', (0.85, 0.86, 0.86), 0.55, trans=0.3)

# ---------- geometry ----------
def load(name, mat, smooth_angle):
    bpy.ops.wm.ply_import(filepath=os.path.join(D, name + '.ply'))
    ob = bpy.context.selected_objects[0]
    ob.scale = (MM, MM, MM)
    ob.data.materials.append(mat)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle))
    return ob
load('bezel', satin, 35)
load('drl', diffuser, 40)
if os.path.exists(os.path.join(D, 'cover.ply')):     # the pop-up door, if prep.py was given one
    cov = load('cover', paint, 70)
    bm = bmesh.new(); bm.from_mesh(cov.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.05); bm.to_mesh(cov.data); bm.free()   # weld the scan's loose triangles
    sub = cov.modifiers.new('smooth', 'SUBSURF'); sub.levels = 2; sub.render_levels = 2   # soften the scan's facets

hw, hd, hh = sc['head']; bw, bd = sc['body']; lr = sc['lens_d'] / 2
for p in sc['poses']:
    x, yf, zc = p['x'], p['yf'], p['zc']
    # head: a bevelled block, with a round cavity in its face for the lens and its reflector
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * MM, (yf - hd / 2) * MM, zc * MM))
    h = bpy.context.object; h.scale = (hw * MM, hd * MM, hh * MM); bpy.ops.object.transform_apply(scale=True)
    bv = h.modifiers.new('bevel', 'BEVEL'); bv.width = 2.5 * MM; bv.segments = 4
    bpy.ops.mesh.primitive_cylinder_add(radius=(lr + 0.5) * MM, depth=24 * MM, vertices=96,
                                        location=(x * MM, (yf - 6) * MM, zc * MM), rotation=(math.pi / 2, 0, 0))
    cav = bpy.context.object
    bo = h.modifiers.new('cavity', 'BOOLEAN'); bo.object = cav; bo.operation = 'DIFFERENCE'
    cav.hide_render = True; cav.hide_viewport = True
    h.data.materials.append(alu)
    # body behind
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * MM, (yf - hd - bd / 2) * MM, zc * MM))
    b_ = bpy.context.object; b_.scale = (bw * MM, bd * MM, bw * MM); b_.data.materials.append(alu)
    # reflector bowl: a chrome cone opening toward the lens, a dark emitter at its throat
    bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=6 * MM, radius2=(lr - 0.5) * MM, depth=10 * MM, end_fill_type='NOTHING',
                                    location=(x * MM, (yf - 9) * MM, zc * MM), rotation=(-math.pi / 2, 0, 0))
    cone = bpy.context.object; cone.data.materials.append(smoked)
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=6.2 * MM, fill_type='NGON', location=(x * MM, (yf - 13.8) * MM, zc * MM), rotation=(math.pi / 2, 0, 0))
    bpy.context.object.data.materials.append(dark)
    # the low-beam cut-off shield across the bowl
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * MM, (yf - 8) * MM, (zc - 3.5) * MM))
    sh = bpy.context.object; sh.scale = (2 * (lr - 2) * MM, 8 * MM, 0.8 * MM); sh.data.materials.append(smoked)
    # the lens: a domed glass cap on the face, and a thin chrome trim ring round it
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=lr * MM, location=(x * MM, (yf - 0.5) * MM, zc * MM))
    ln = bpy.context.object; ln.scale = (1, 6.5 / lr, 1); ln.data.materials.append(glass); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=(lr + 0.6) * MM, minor_radius=0.9 * MM, major_segments=96, minor_segments=16,
                                     location=(x * MM, (yf - 0.3) * MM, zc * MM), rotation=(math.pi / 2, 0, 0))
    bpy.context.object.data.materials.append(chrome); bpy.ops.object.shade_smooth()

# floor under the bezel's lowest point
zmin = min(v.co.z for v in bpy.data.objects['bezel'].data.vertices) * MM if 'bezel' in bpy.data.objects else -0.01
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, zmin - 0.0005))
floor_ob = bpy.context.object
floor_ob.data.materials.append(floor_m)
# the floor's gloss fades to matte black away from the headlight (a studio surface falling off into
# the dark), so the lights' far reflections don't streak across the frame
fn = floor_m.node_tree; pb = fn.nodes['Principled BSDF']; outn = fn.nodes['Material Output']
geo = fn.nodes.new('ShaderNodeNewGeometry'); ln_ = fn.nodes.new('ShaderNodeVectorMath'); ln_.operation = 'LENGTH'
fn.links.new(geo.outputs['Position'], ln_.inputs[0])
fade = fn.nodes.new('ShaderNodeMapRange'); fade.inputs['From Min'].default_value = 0.28; fade.inputs['From Max'].default_value = 0.55
fn.links.new(ln_.outputs['Value'], fade.inputs['Value'])
matte = fn.nodes.new('ShaderNodeBsdfDiffuse'); matte.inputs['Color'].default_value = (0.002, 0.002, 0.002, 1)
mix = fn.nodes.new('ShaderNodeMixShader')
fn.links.new(fade.outputs['Result'], mix.inputs['Fac']); fn.links.new(pb.outputs['BSDF'], mix.inputs[1]); fn.links.new(matte.outputs['BSDF'], mix.inputs[2])
fn.links.new(mix.outputs['Shader'], outn.inputs['Surface'])

# ---------- light ----------
RIMCOL = bpy.data.collections.new('rim receivers')
for ob in list(scene.collection.objects) + list(bpy.data.objects):
    if ob.type == 'MESH' and ob.name != floor_ob.name and ob.name not in RIMCOL.objects:
        RIMCOL.objects.link(ob)
world = bpy.data.worlds.new('studio'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.0025, 0.0027, 0.003, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

def area(name, loc, size, power, color=(1, 1, 1), look=(0.0, 0.0, 0.03), shape='RECTANGLE'):
    if shot == 'hood34':              # seen from the other side: the same rig, mirrored
        loc = (-loc[0], loc[1], loc[2])
    l = bpy.data.lights.new(name, 'AREA'); l.energy = power; l.shape = shape; l.color = color
    if shape == 'RECTANGLE':
        l.size, l.size_y = size
    else:
        l.size = size[0]
    o = bpy.data.objects.new(name, l); scene.collection.objects.link(o); o.location = loc
    o.visible_camera = False          # light the scene, but don't show up in frame
    if name.startswith('rim'):        # rims light the headlight only, not the floor (no glare across it)
        o.light_linking.receiver_collection = RIMCOL
    d = Vector(look) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o
dim = 0.10 if col else 0.35
area('key softbox', (0.55, 0.75, 0.85), (1.2, 0.8), 420 * dim)
area('top strip', (0.0, 0.05, 0.9), (1.6, 0.25), 260 * dim)
area('rim left', (-0.9, -0.35, 0.35), (0.12, 1.0), 180 * dim, color=(0.85, 0.9, 1.0))
area('rim right', (0.9, -0.35, 0.30), (0.12, 1.0), 160 * dim, color=(0.85, 0.9, 1.0))
area('front kicker', (-0.3, 1.2, 0.30), (0.8, 0.3), 70 * dim)

# ---------- camera ----------
cams = {'34': ((0.74, 0.84, 0.34), (0.0, -0.04, 0.022), 85),
        'front': ((0.012, 1.0, 0.07), (0.008, 0.0, 0.026), 85),
        'hood34': ((-0.74, 0.76, 0.24), (0.01, -0.03, 0.024), 85),
        'low': ((0.30, 0.85, 0.0), (0.01, 0.0, 0.03), 70),
        'close': ((0.26, 0.45, 0.12), (-0.04, 0.0, 0.03), 100)}
loc, look, lens = cams[shot]
cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.sensor_width = 36
cd.dof.use_dof = True; cd.dof.aperture_fstop = 5.6 if shot != 'close' else 4.0
cam = bpy.data.objects.new('cam', cd); scene.collection.objects.link(cam); scene.camera = cam
cam.location = loc; d = Vector(look) - Vector(loc); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cd.dof.focus_distance = d.length

# ---------- render ----------
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = spp
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 10; scene.cycles.transmission_bounces = 10; scene.cycles.glossy_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = 1800, 1100
scene.render.resolution_percentage = pct
scene.render.threads_mode = 'FIXED'; scene.render.threads = 4
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_depth = '16'
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print('wrote', out)
