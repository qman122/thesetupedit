"""Measure the owner's model of the C5 headlight covers and check the bezel against it.

    python3 cover_scan.py /path/to/Covers.stl [/path/to/lighter_copy.stl]

Covers.stl (the pair of pop-up doors, about 190 MB, not kept in this repo) is laid out with the
skin facing +z, the front edge toward -y, and the two doors mirrored about x = 0. This script
uses the +x door. It prints the measurements behind the clip_* parameters in generate.py, puts
the door on the passenger bezel (front edge along the blade, lip on the blade), and draws
diagrams/cover_fit.png. Given a lighter (decimated) copy of the same file as well, it also
writes the placed door for the 3D mockup (mockup/cover_*.json). It also writes
cover_sides.json: the holes in the door's side flanges and their shape, for the bezel's ears.
"""

import os
import sys

import manifold3d as m3d
import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import generate as g  # noqa: E402

P, M = g.P, g.M
X_MID = 174.45     # centres the door's two side flanges (where they screw on) on the opening


def load_door(path):
    tm = trimesh.load(path, process=False)
    v = tm.vertices[tm.faces.reshape(-1)]
    keep = (v.reshape(-1, 3, 3)[:, :, 0] > 0).all(1)             # the +x door only
    u, inv = np.unique(np.round(v.reshape(-1, 3, 3)[keep].reshape(-1, 3), 4), axis=0, return_inverse=True)
    f = inv.reshape(-1, 3)
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    return M(m3d.Mesh(u.astype(np.float32), f.astype(np.uint32)))


def main(path, view_path=None):
    door = load_door(path)
    V = np.asarray(door.to_mesh().vert_properties)[:, :3]
    xs = np.arange(40.0, 302.0, 2.0)
    edge, lip = [], []
    for x in xs:
        s = V[np.abs(V[:, 0] - x) < 1.0]
        edge.append(s[:, 1].min())
        lip.append(s[s[:, 1] < s[:, 1].min() + 4][:, 2].min())
    edge, lip = np.array(edge), np.array(lip)
    u = xs - X_MID                                              # +u toward the fender
    ow = P.opening_w - 2 * P.opening_side_clear
    F = g.front_frame(P)
    U = ow / 2 / F[0][0]
    bow = P.front_bow * (1 - np.clip(u / U, -1, 1) ** 2)
    m = np.abs(u) < 110
    c1, c0 = np.polyfit(u[m], bow[m] - (-edge[m]), 1)
    res = -edge + c0 + c1 * u - bow
    print(f"door front edge vs the bezel's bow, after turning the door {np.degrees(np.arctan(c1)):.1f} deg:")
    print(f"  within {np.abs(res[m]).max():.1f} mm for |u| < 110; at the ends "
          f"{res[0]:+.1f} (hood) and {res[-1]:+.1f} mm (fender)")
    print(f"  lip bottom height along the edge: {lip.max() - lip.min():.1f} mm high to low, "
          f"lowest at the fender end")

    # the clip: the only thing hanging under the middle of the door
    cl = V[(V[:, 0] > 120) & (V[:, 0] < 210) & (V[:, 1] > -120) & (V[:, 1] < -60) & (V[:, 2] < 29)]
    print(f"clip: x {cl[:, 0].min():.1f}..{cl[:, 0].max():.1f}, y {cl[:, 1].min():.1f}..{cl[:, 1].max():.1f}, "
          f"lowest z {cl[:, 2].min():.1f}; centre between the legs u = {164.5 - X_MID:.1f}")
    ul = np.arange(-140, 141, 10.0)
    print("COVER_LIP_Z =", [round(float(z), 1) for z in np.interp(ul + X_MID, xs, lip)])

    # put the door on the passenger bezel: front edge at the nose less cover_edge_n at the clip,
    # lip bottom on the blade at the clip
    z_top = g.bezel_z(P)[0]
    uc = P.clip_u
    e_c = np.interp(uc, u, -edge)
    lip_c = np.interp(uc, u, lip)
    n_c = 2.37 - P.cover_edge_n + P.front_bow * (1 - (uc / U) ** 2)
    A = np.array([[1, 0, 0, -X_MID], [c1, -1, 0, n_c - (e_c + c1 * uc) - c1 * X_MID], [0, 0, 1, z_top + g.top_rise(P, uc) - lip_c]])
    local = door.transform(A)          # a mirror; manifold keeps the solid the right way out
    front = local ^ g.box(-U - 10, U + 10, -95, 20, -50, 200)
    bez_local = g.shroud(P).transform(np.linalg.inv(np.vstack([F, [0, 0, 0, 1]]))[:3])
    ov = (front ^ bez_local).volume()
    print(f"bezel and door overlap: {ov:.1f} mm^3 (0 = no clash)")
    door_m = local.transform(np.vstack([np.asarray(F, float), [0, 0, 0, 1]])[:3])
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")):
        for name in ("hood", "fender"):
            iv = door_m ^ g.ear(P, name)
            print(f"{name} ear and door overlap: {iv.volume():.1f} mm^3")
            for pc in iv.decompose():
                if pc.volume() > 0.5:
                    print("   at", np.round(pc.bounding_box(), 1))
    if view_path:
        export_view(view_path, A, F)
    find_sides(local.transform(np.vstack([np.asarray(F, float), [0, 0, 0, 1]])[:3]))

    # blade top against the lip, along the front
    gaps = lip - lip_c - (g.top_rise(P, u) - g.top_rise(P, uc))
    print("lip bottom above the blade top (mm), hood end to fender end:")
    print("  " + "  ".join(f"u={a:+.0f}:{b:+.1f}" for a, b in zip(u[::15], gaps[::15])))

    # --- diagram ---
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(2, 1, 1)
    blade = g.fit_test_blade(P).transform(np.linalg.inv(np.vstack([F, [0, 0, 0, 1]]))[:3])
    for poly in blade.project().to_polygons():
        q = np.vstack([poly, poly[:1]])
        ax.fill(q[:, 0], q[:, 1], color="#555", alpha=0.8, lw=0)
    for poly in (front ^ g.box(-U - 10, U + 10, -95, 20, z_top - 5, z_top + 30)).project().to_polygons():
        q = np.vstack([poly, poly[:1]])
        ax.plot(q[:, 0], q[:, 1], color="#c0392b", lw=0.8)
    ax.set_title("From above: bezel top blade and clip tongue (grey), headlight door's front edge "
                 "and clip from the owner's model (red outline)")
    ax.set_xlabel("across the front, mm (hood end left)")
    ax.set_ylabel("forward, mm")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax = fig.add_subplot(2, 1, 2)
    rot = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]], float)
    for man, col, a in ((bez_local, "#555", 0.8), (local ^ g.box(-U, U, -95, 20, -50, 200), "#c0392b", 0.55)):
        for poly in man.transform(rot).slice(uc + 1.5).to_polygons():
            q = np.vstack([poly, poly[:1]])
            ax.fill(q[:, 0], q[:, 1], color=col, alpha=a, lw=0)
    ax.set_xlim(-95, 15)
    ax.set_ylim(z_top - 22, z_top + 22)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_title("Side section through the clip: the bar drops into the groove in the tongue, "
                 "the door's lip sits on the blade (door in red)")
    ax.set_xlabel("forward, mm")
    ax.set_ylabel("up, mm")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams", "cover_fit.png")
    fig.savefig(out, dpi=90)
    print("diagram ->", out)


def find_sides(door_m):
    """The door's two side flanges, in the passenger model frame, for the bezel's ears: every hole
    in them (where the stock ears screw on) and a map of how far out the door reaches at each
    height and fore-aft position. Written to cover_sides.json for generate.py."""
    import json
    mm = door_m.to_mesh()
    v, f = np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)
    c = v[f].mean(1)
    n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    a = np.linalg.norm(n, axis=1)
    n = n / (a[:, None] + 1e-12)
    pts = np.vstack([v, c])
    out = {}
    for name, sx in (("hood", -1), ("fender", 1)):
        holes = []
        for y0 in range(-260, 0, 20):                  # windows along the flange: fit its plane, find holes
            sel = (c[:, 0] * sx > 110) & (np.abs(c[:, 1] - y0) < 25) & (n[:, 0] * sx > 0.5)
            if sel.sum() < 50:
                continue
            cen = (c[sel] * a[sel, None]).sum(0) / a[sel].sum()
            e3 = np.linalg.svd((c[sel] - cen) * np.sqrt(a[sel])[:, None], full_matrices=False)[2][2]
            e3 = e3 * np.sign(e3[0] * sx)
            e1 = np.cross([0, 0, 1], e3)
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(e3, e1)
            R = door_m.transform(np.array([np.r_[e1, -e1 @ cen], np.r_[e2, -e2 @ cen], np.r_[e3, -e3 @ cen]]))
            for poly in (R ^ M.cube([50, 160, 30], True)).project().to_polygons():
                q = np.asarray(poly)
                ar = 0.5 * np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])
                if not -150 < ar < -15:
                    continue
                ctr = q.mean(0)
                w, h = q.max(0) - q.min(0)
                ring = R ^ M.cube([w + 6, h + 6, 30], True).translate([ctr[0], ctr[1], 0])
                p_out = cen + ctr[0] * e1 + ctr[1] * e2 + ring.bounding_box()[5] * e3
                if all(np.linalg.norm(p_out - np.array(h_["at"])) > 4 for h_ in holes):
                    holes.append({"at": [round(float(q_), 1) for q_ in p_out],
                                  "normal": [round(float(q_), 3) for q_ in e3],
                                  "size": [round(float(w), 1), round(float(h), 1)]})
        holes.sort(key=lambda h_: -h_["at"][1])
        for h_ in holes:
            print(f"{name} flange hole {h_['size'][0]} x {h_['size'][1]} mm, outside face at {tuple(h_['at'])}")
        # how far out the door reaches (|x|), on a 4 mm grid of (y, z)
        ys, zs = np.arange(-240.0, 48.0, 4.0), np.arange(-60.0, 88.0, 4.0)
        X = np.full((len(ys), len(zs)), np.nan)
        s_ = pts[pts[:, 0] * sx > 112]
        iy = np.rint((s_[:, 1] - ys[0]) / 4).astype(int)
        iz = np.rint((s_[:, 2] - zs[0]) / 4).astype(int)
        ok = (iy >= 0) & (iy < len(ys)) & (iz >= 0) & (iz < len(zs))
        np.fmax.at(X, (iy[ok], iz[ok]), s_[ok, 0] * sx)
        out[name] = {"holes": holes, "y": ys.tolist(), "z": zs.tolist(),
                     "x": [[None if np.isnan(q_) else round(float(q_), 1) for q_ in row] for row in X]}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")
    with open(path, "w") as fh:
        json.dump(out, fh, separators=(",", ":"))
    print("door side flanges ->", path)


def export_view(view_path, A, F):
    """Put the +x door of a lighter copy of Covers.stl where main() put the full one, in the
    model frame, and write it for the 3D mockup (both sides)."""
    import json
    tm = trimesh.load(view_path, process=False)
    f = tm.faces[(tm.vertices[tm.faces][:, :, 0] > 0).all(1)]
    v = tm.vertices
    Fm = np.vstack([np.asarray(F, float), [0, 0, 0, 1]])
    Am = np.vstack([A, [0, 0, 0, 1]])
    vm = (np.hstack([v, np.ones((len(v), 1))]) @ (Fm @ Am).T)[:, :3]
    T = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)          # viewer frame, as export_parts.py
    here = os.path.dirname(os.path.abspath(__file__))
    for side, sx in (("passenger", 1), ("driver", -1)):
        w = vm * [sx, 1, 1]
        tri = f[:, ::-1] if sx == 1 else f                            # A mirrors; so does the driver flip
        p = np.round(w @ T.T * 20) / 20
        with open(os.path.join(here, "mockup", f"cover_{side}.json"), "w") as fh:
            json.dump({"p": [float(x) for x in p.ravel()], "i": [int(x) for x in tri.ravel()]}, fh,
                      separators=(",", ":"))
    print("mockup door ->", os.path.join(here, "mockup", "cover_*.json"), len(f), "tris")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Covers.stl", sys.argv[2] if len(sys.argv) > 2 else None)
