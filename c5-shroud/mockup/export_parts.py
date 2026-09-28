"""Export the carrier, shroud and pod stand-ins in assembled position for the 3D mockup.

Converts the design frame (X toward the fender, Y forward, Z up) to the viewer's frame
(x toward the car's left, y up, z forward). Origin: centre of the pod row, pod faces,
top of the carrier floor.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import generate as g

T = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)   # det +1: a rotation, no mirroring


def export(man, path):
    """Write {"p": [x, y, z, ...], "i": [a, b, c, ...]} in mm, rounded to 0.05 mm."""
    import json
    mesh = man.to_mesh()
    v = np.round(np.asarray(mesh.vert_properties)[:, :3] @ T.T * 20) / 20
    f = np.asarray(mesh.tri_verts)
    with open(path, "w") as fh:
        json.dump({"p": [float(x) for x in v.ravel()], "i": [int(x) for x in f.ravel()]}, fh, separators=(",", ":"))
    print(os.path.basename(path), len(f), "tris", os.path.getsize(path) // 1024, "KB")


here = os.path.dirname(os.path.abspath(__file__))
P = g.P
c, p = g.carrier(P), g.pod_dummy(P)
s = g.M.batch_boolean([g.shroud(P), g.ear(P, "hood"), g.ear(P, "fender")], g.m3d.OpType.Add)   # bezel and its ears
lens = g.pod_lenses(P)
for side, f in [("passenger", lambda m: m), ("driver", g.mirror_x)]:
    export(f(c), os.path.join(here, f"carrier_{side}.json"))
    export(f(s), os.path.join(here, f"shroud_{side}.json"))
    # the pods are stepped, so each side needs its own copy
    export(f(p), os.path.join(here, f"pods_{side}.json"))
    export(f(lens), os.path.join(here, f"lenses_{side}.json"))
