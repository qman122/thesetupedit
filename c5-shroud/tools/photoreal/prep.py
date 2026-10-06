"""Geometry for the photoreal renders, in the model frame (mm, z up, y forward): bezel, diffusers,
door cover and projector poses, per style."""
import json, os, sys, numpy as np, trimesh
S = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(S, 'scene')
REPO = os.path.dirname(os.path.dirname(S)); sys.path.insert(0, REPO); os.environ['LIGHTS'] = 'projectors'
T = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
for st in (sys.argv[1:] or ['P3R', 'P3J', 'P3V']):
    os.environ['BEZEL_STYLE'] = st
    for m in [k for k in sys.modules if k in ('generate', 'bezel_styles', 'bezel_sdf')]:
        del sys.modules[m]
    import generate as g, bezel_styles as bs
    d = os.path.join(OUT, st); os.makedirs(d, exist_ok=True)
    for nm, fn in (('bezel', f'bezel_cad_passenger_{st}.stl'), ('drl', f'drl_inserts_passenger_{st}.stl')):
        tm = trimesh.load(os.path.join(REPO, 'stl', 'cad', fn)); tm.export(os.path.join(d, nm + '.ply'))
        print(st, nm, len(tm.faces))
    # the pop-up door: optional, and not in the repo (it comes from a third-party car scan). Point
    # COVER_JSON at a viewer-frame door mesh (cover_passenger.json) to include it
    cj = os.environ.get('COVER_JSON')
    if cj and os.path.exists(cj):
        j = json.load(open(cj))
        v = np.array(j['p']).reshape(-1, 3) @ T
        trimesh.Trimesh(v, np.array(j['i']).reshape(-1, 3), process=False).export(os.path.join(d, 'cover.ply'))
    poses = [dict(x=x, yf=yf, zc=zc) for (x, yf, zc) in g.proj_poses(g.P)]
    json.dump(dict(poses=poses, head=[bs.PROJ_W, g.P.proj_head_d, bs.PROJ_H], body=[g.P.proj_body_w, g.P.proj_body_d],
                   lens_d=bs.LENS_D, recessed_face=st in ('P3D', 'P3R')), open(os.path.join(d, 'scene.json'), 'w'), indent=1)
    print(st, poses)
