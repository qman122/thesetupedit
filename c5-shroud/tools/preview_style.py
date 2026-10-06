"""Quick look at one bezel style: BEZEL_STYLE=X python3 preview_style.py -> viewer JSONs."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); VIEW = os.path.join(HERE, 'viewer')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import bezel_sdf as b
st = os.environ.get("BEZEL_STYLE", "") or "base"
OUT = os.environ.get('PREVIEW_OUT', os.path.join(VIEW, f'style_{st}'))
os.makedirs(OUT, exist_ok=True)
T = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
def write(name, v, f):
    v = np.round(np.asarray(v) @ T.T * 20) / 20
    json.dump({"p": v.ravel().tolist(), "i": np.asarray(f).ravel().astype(int).tolist()},
              open(os.path.join(OUT, name), 'w'), separators=(",", ":"))
t0 = time.time()
v, f, sw, fg = b.build(h=float(os.environ.get("BEZEL_H", "0.5")), preview=True)
import trimesh
tm = trimesh.Trimesh(v, f, process=True)
if tm.volume < 0: tm.invert()
tm.export(os.path.join(OUT, 'bezel.stl'))
write('shroud_passenger.json', tm.vertices, tm.faces)
ins = b.build_inserts(sw, fg)
if ins is not None:
    ti = trimesh.Trimesh(*ins, process=True)
    if ti.volume < 0: ti.invert()
    ti.export(os.path.join(OUT, 'inserts.stl'))
    write('drl_passenger.json', ti.vertices, ti.faces)
print(st, 'done', len(tm.faces), 'tris, watertight', tm.is_watertight, f'{time.time()-t0:.0f} s', flush=True)
