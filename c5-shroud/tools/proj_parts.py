"""Projector stand-ins, lenses and the projector bracket into style_<BEZEL_STYLE>/, plus clash checks."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); VIEW = os.path.join(HERE, 'viewer')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['LIGHTS'] = 'projectors'
import numpy as np, trimesh, manifold3d as m3d
import generate as g, bezel_styles as bs
P = g.P; st = os.environ['BEZEL_STYLE']
T = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
d = os.path.join(VIEW, f'style_{st}')
def write(name, man):
    m = man.to_mesh(); v = np.round(np.asarray(m.vert_properties)[:, :3] @ T.T * 20) / 20
    json.dump({"p": v.ravel().tolist(), "i": np.asarray(m.tri_verts).ravel().astype(int).tolist()},
              open(os.path.join(d, name), 'w'), separators=(",", ":"))
U = lambda L: g.M.batch_boolean(L, m3d.OpType.Add)
proj = g.projector_dummy(P)       # for the clash checks
# for the pictures: each head with a round recess in its face, a domed lens sunk in it and a
# trim ring standing 0.4 mm proud round it (no two surfaces in the same place, so no flicker)
vis, lens = [], []
R_L, CAP = 19.0, 2.6
RS = (R_L ** 2 + CAP ** 2) / (2 * CAP)
for x, yf, zc in g.proj_poses(P):
    cyl = lambda r, y0, y1: g.M.cylinder(y1 - y0, r, r, 96).rotate([-90, 0, 0]).translate([x, y0, zc])
    vis.append(cyl(23.0, yf - 0.6, yf + 0.4) - cyl(20.2, yf - 1.0, yf + 1.0))       # trim ring
    dome = g.M.sphere(RS, 192).translate([x, yf - 0.3 - RS, zc]) ^ cyl(R_L, yf - 3.5, yf)
    lens.append(dome + cyl(R_L, yf - 3.5, yf - 2.0))
proj_vis = U([proj - U([g.M.cylinder(4.0, 20.2, 20.2, 96).rotate([-90, 0, 0]).translate([x, yf - 3.0, zc]) for x, yf, zc in g.proj_poses(P)])] + vis)
lens = U(lens)
car = g.carrier(P)
write('pods_passenger.json', proj_vis); write('lenses_passenger.json', lens); write('carrier_passenger.json', car)
tm = trimesh.load(d + '/bezel.stl'); m = g.M(m3d.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32)))
print(st, 'bezel vs projectors %.2f mm3, vs bracket %.2f mm3; bracket vs projectors %.2f mm3'
      % ((m ^ proj).volume(), (m ^ car).volume(), (car ^ proj).volume()))
