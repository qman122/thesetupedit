import json, os, sys, numpy as np, trimesh, manifold3d as m3d
HERE = os.path.dirname(os.path.abspath(__file__)); VIEW = os.path.join(HERE, 'viewer')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import generate as g
T = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
d = os.path.join(VIEW, 'style_' + os.environ['BEZEL_STYLE']) + '/'
def load(n):
    j = json.load(open(d + n)); v = np.array(j['p']).reshape(-1, 3) @ T; return trimesh.Trimesh(v, np.array(j['i']).reshape(-1, 3))
M = lambda t: g.M(m3d.Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
b = M(trimesh.load(d + 'bezel.stl'))
print(os.environ['BEZEL_STYLE'], 'visual parts vs bezel:', ', '.join('%s %.3f mm3' % (n.split('_')[0], (b ^ M(load(n))).volume())
      for n in ('pods_passenger.json', 'lenses_passenger.json', 'carrier_passenger.json')))
