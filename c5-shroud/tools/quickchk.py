import os, sys, numpy as np, trimesh, manifold3d as m3d
HERE = os.path.dirname(os.path.abspath(__file__)); VIEW = os.path.join(HERE, 'viewer')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); os.environ['LIGHTS'] = 'projectors'
import generate as g
M = g.M; P = g.P; st = os.environ['BEZEL_STYLE']
tm = trimesh.load(os.path.join(VIEW, f'style_{st}', 'bezel.stl')); sh = M(m3d.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32)))
d = g.lights_dummy(P); F_ = g.front_frame(P); us_, n_c, zs = g.dowel_spot(P)
w = 1.0
for z in zs:
    ring = (M.cylinder(2 * P.dowel_depth - 1, P.dowel_d / 2 + 1.0, P.dowel_d / 2 + 1.0, 32, True) - M.cylinder(2 * P.dowel_depth, P.dowel_d / 2 + 0.05, P.dowel_d / 2 + 0.05, 32, True))
    ring = g.lift_top(P, ring.transform([[0, 0, 1, us_], [1, 0, 0, n_c], [0, 1, 0, z]]).transform(F_))
    w = min(w, (ring ^ sh).volume() / ring.volume())
pcs = g.split_shell(P, sh)
print(st, 'pieces', len(sh.decompose()), 'split', [len(p.decompose()) for p in pcs], 'dowel wall %.2f' % w,
      'mis %.4f' % max((sh ^ d.translate([dx, 0, dz])).volume() for dx in (-1.5, 0, 1.5) for dz in (-0.5, 0, 0.5)),
      'vs bracket %.3f' % (sh ^ g.carrier(P)).volume())
