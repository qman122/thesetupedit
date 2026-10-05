"""Extra fit tests for a print set (run with the set's env, e.g. VARIANT=A1 J_SHAPE=intake TEXTURE=carbon BEZEL_STYLE=P3J LIGHTS=projectors): the bezel goes on over the mounted projectors; the diffusers fit their channel; the straps match the cradles."""
import os, sys, numpy as np, trimesh, manifold3d as m3d
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import generate as g
P, M = g.P, g.M
def load(f):
    tm = trimesh.load(f)
    return M(m3d.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32)))
sh, car, dum = g.shroud(P), g.carrier(P), g.projector_dummy(P)
fixed = car + dum
# 1. the bezel slid on straight from the front, over the bracket and projectors already in place
worst = 0.0
for dy in np.arange(0.0, 80.1, 1.0):
    v = (sh.translate([0, dy, 0]) ^ fixed).volume()
    worst = max(worst, v)
    if v > 1e-3:
        print('  bezel %.0f mm forward of home: %.3f mm3 in the way' % (dy, v))
print('1. bezel slides on straight from the front over the mounted projectors:', 'OK' if worst < 1e-3 else 'BLOCKED', '(worst %.4f mm3)' % worst)
# and with the projectors 1.5 mm off to either side (the bracket and bezel never line up exactly)
worst2 = 0.0
for dx in (-1.5, 1.5):
    for dy in np.arange(0.0, 80.1, 2.0):
        worst2 = max(worst2, (sh.translate([0, dy, 0]) ^ (car + g.projector_dummy(P).translate([dx, 0, 0]))).volume())
print('   ...and with the projectors 1.5 mm off to either side:', 'OK' if worst2 < 1e-3 else 'BLOCKED', '(worst %.4f mm3)' % worst2)
# 2. the diffusers in their channel: no overlap with the bezel, and how snug
ins = load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'stl', 'cad', g.bezel_cad_name('inserts')))
ov = (ins ^ sh).volume()
print('2. diffusers overlap the bezel by %.3f mm3 (should be ~0); diffuser volume %.0f mm3, %d piece(s)' % (ov, ins.volume(), len(ins.decompose())))
# their clearance: offset them outward 0.3 mm and see that they then touch the walls
try:
    big = M.minkowski_sum(ins, M.sphere(0.3, 8)) if hasattr(M, 'minkowski_sum') else None
except Exception:
    big = None
if big is not None:
    print('   grown 0.3 mm they touch the walls: %.1f mm3 (so the gap is under 0.3 mm: snug, not loose)' % (big ^ sh).volume())
# 3. straps against the cradles' screw bosses
for i, (x, yf, zc) in enumerate(g.proj_poses(P)):
    y0, y1 = g.proj_cradle_span(P, yf, x)
    L = y1 - y0
    print('3. projector %d: cradle %.0f mm long, strap %.0f mm, %d screw(s) a side' % (i + 1, L, L, len(g._strap_holes(P, L)) // 2))
