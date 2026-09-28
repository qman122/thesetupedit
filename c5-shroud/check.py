"""Sanity checks for the C5 pod carrier and shroud. Run: python3 check.py

Checks the measured hole spacing, that bolts, nuts, pods and the shroud don't collide
anywhere in their adjustment range, that the shroud fits the opening, and that every
printable part is one clean solid.
"""

import glob
import math
import os

import manifold3d as m3d
import numpy as np
import trimesh
from matplotlib.path import Path

import generate as g

P = g.P
M = g.M
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def overlap(a, b):
    return (a ^ b).volume()


carrier, shroud, pods = g.carrier(P), g.shroud(P), g.pod_dummy(P)
y_back, t = P.mount_wall_y, P.mount_wall_t
pts = {n: (x, z, ax) for (n, x, z, ax) in g.mount_points(P)}

# 1. hole spacing matches the tape measurements
a = pts["arm hole 1"][1] - pts["arm hole 4"][1]
h = pts["pad upper"][1] - pts["pad lower"][1]
b = pts["arm hole 4"][0] - pts["pad upper"][0]
d = pts["pad upper"][1] - pts["arm hole 4"][1]
for label, got, want in [("A arm hole 1-4", a, 43.2), ("H pad upper-lower", h, 19.0),
                         ("B across, pad upper to arm 4", b, 222.3),
                         ("D pad upper above arm 4", d, 19.3)]:
    check(f"{label} = {got:.1f} mm", abs(got - want) < 0.05, f"target {want} mm")

# 2. every slot is open through the wall, and solid just past its ends
for n, (x, z, ax) in pts.items():
    ln = P.arm_slot_len if ax == "x" else P.pad_slot_len
    travel = (ln - P.mount_hole_d) / 2
    probe_open = []
    for s in (-travel, 0, travel):
        px, pz = (x + s, z) if ax == "x" else (x, z + s)
        probe_open.append(overlap(carrier, g.cyl_y(P.mount_hole_d - 1, y_back - 1, y_back + t + 1, px, pz)))
    past = travel + P.mount_hole_d / 2 + 2.5
    px, pz = (x + past, z) if ax == "x" else (x, z + past)
    solid = overlap(carrier, g.cyl_y(2, y_back + 0.5, y_back + t - 0.5, px, pz))
    check(f"{n}: M6 slot open through the wall, +/-{travel:.1f} mm travel",
          max(probe_open) < 1e-6 and solid > 1, f"at x={x:.1f} z={z:.1f}")

# 3. nuts on the front of the wall clear the carrier and the pods at both slot ends
for n, (x, z, ax) in pts.items():
    ln = P.arm_slot_len if ax == "x" else P.pad_slot_len
    travel = (ln - P.mount_hole_d) / 2
    worst = 0.0
    for s in (-travel, travel):
        px, pz = (x + s, z) if ax == "x" else (x, z + s)
        nut = g.cyl_y(2 * P.nut_r, y_back + t + 0.01, y_back + t + 8, px, pz)
        worst = max(worst, overlap(carrier, nut), overlap(pods, nut))
    check(f"{n}: 15 mm flange nut clears carrier and pods", worst < 1e-6)

# 4. pods sit clear of the carrier across their whole fore-aft slot travel,
#    and there's always room behind them for the pigtail and plug
half = (P.pod_slot_len - P.pod_bolt_d) / 2
fwd = (P.pod_bolt_y + half) - P.pod_bolt_nominal_y
back = P.pod_bolt_nominal_y - (P.pod_bolt_y - half)
worst = max(overlap(carrier, g.pod_dummy(P, s)) for s in (-back, 0, fwd))
gap_nominal = min(y for (_, y, _) in g.pod_poses(P)) - P.pod_depth - (y_back + t)   # the rearmost pod
gap_min = gap_nominal - back
check(f"pods clear the carrier from {back:.1f} mm back to {fwd:.1f} mm forward", worst < 1e-6)
check(f"cable room behind the pods: {gap_nominal:.1f} mm default, {gap_min:.1f} mm at full rearward",
      gap_min >= 5 and gap_nominal >= 15)

# 5. pods and shroud don't touch, and each pod face sits inside its window
check("pods clear the shroud", overlap(pods, shroud) < 1e-6)
check(f"window gap {P.window_clear_x} mm each side, {P.window_clear_y} mm top and bottom", min(P.window_clear_x, P.window_clear_y) > 0.3)

# 6. shroud and carrier only touch at the screw tabs
ov = overlap(shroud, carrier)
check("shroud and carrier don't overlap", ov < 1e-3, f"overlap {ov:.4f} mm^3")

# 6b. the bezel slides forward with the pods (0 to bezel_travel); it never goes back
worst_nut = worst_car = worst_pod = 0.0
for s_ in (0.0, P.bezel_travel / 2, P.bezel_travel):
    bz = shroud.translate([0, s_, 0])
    worst_car = max(worst_car, overlap(bz, carrier))
    worst_pod = max(worst_pod, overlap(bz, g.pod_dummy(P, s_)))
    for n, (x, z, ax) in pts.items():
        ln = P.arm_slot_len if ax == "x" else P.pad_slot_len
        tr = (ln - P.mount_hole_d) / 2
        for d_ in (-tr, tr):
            px, pz = (x + d_, z) if ax == "x" else (x, z + d_)
            worst_nut = max(worst_nut, overlap(bz, g.cyl_y(2 * P.nut_r, y_back + t + 0.01, y_back + t + 8, px, pz)))
check(f"bezel clears the carrier anywhere in its {P.bezel_travel:.0f} mm of forward travel", worst_car < 1e-3)
check("bezel clears the pods when both slide forward together", worst_pod < 1e-6)
check("bezel wrap clears all four mounting nuts", worst_nut < 1e-6)
check("pods can also sit up to 10 mm further back with the bezel in place",
      max(overlap(shroud, g.pod_dummy(P, -s_)) for s_ in (0, back)) < 1e-6)
# only the part of the bezel in line with the nuts counts; the wings run back beside them
nut_x = max(abs(x) + (P.arm_slot_len / 2 if ax == "x" else 0) + P.nut_r for (x, z, ax) in pts.values())
gap = (shroud ^ g.box(-nut_x, nut_x, -300, 300, -300, 300)).bounding_box()[1] - (y_back + t + 8)
check(f"bezel sits {gap:.1f} mm in front of the nuts (the wings pass outside them)", gap > 2)

# 6c. every lens sees out straight ahead: no ray from anywhere on a lens, within 10 degrees
#     either side of straight ahead (seen from above, at lens height), hits the bezel
_polys = [Path(np.asarray(q)) for q in shroud.slice(g.pod_zc(P)).to_polygons()]


def _hits(pts_):
    c = np.zeros(len(pts_), int)
    for pa in _polys:
        c += pa.contains_points(pts_)
    return (c % 2 == 1).any()


blocked = 0
for (px, py, _) in g.pod_poses(P):
    for lx in (-18.5, 18.5):
        for x0 in px + lx + np.linspace(-15, 15, 7):
            for a_ in range(-10, 11, 2):
                t_ = math.radians(a_)
                s_ = np.arange(0.8, 160, 0.5)
                blocked += _hits(np.stack([x0 + s_ * math.sin(t_), py + 0.3 + s_ * math.cos(t_)], 1))
check("every lens has a clear view 10 degrees either side of straight ahead", blocked == 0,
      f"{blocked} blocked rays")

# 6d. the headlight door (measured from the owner's model, cover_scan.py): its lip rests on the
#     top blade all the way across, and the clip's cross bar drops into the groove in the tongue
F_ = g.front_frame(P)
U_ = (P.opening_w / 2 - P.opening_side_clear) / F_[0][0]
z_top = g.bezel_z(P)[0]
nose = 2.37 - P.cover_edge_n


def bow(u):
    return P.front_bow * (1 - min(abs(u) / U_, 1) ** 2)


lip_min = min(np.interp(u, g.COVER_LIP_U, g.COVER_LIP_Z) for u in np.linspace(-U_ - 3, U_ + 3, 200))
lip_gap, lip_touch = [], []
for u in np.arange(-U_ + 12, U_ - 11, 10.0):
    zl = z_top + float(np.interp(u, g.COVER_LIP_U, g.COVER_LIP_Z)) - lip_min
    strip = g.box(u - 4, u + 4, nose + bow(u) - 5, nose + bow(u), zl, zl + 5).transform(F_)
    lip_gap.append(overlap(shroud, strip))
    lip_touch.append(overlap(shroud, strip.translate([0, 0, -0.4])))
pen = max(lip_gap) / 40                                             # the strips are 8 x 5 mm
check("the door's lip sits on the top blade all the way across (no clash, no gap)",
      pen < 0.15 and min(lip_touch) > 1, f"{len(lip_gap)} places along the front, at most {pen:.2f} mm deep")


def bar(dn=0.0, dz=0.0):
    hw = P.clip_leg_gap / 2 + 2
    zc = z_top + float(g.top_rise(P, P.clip_u)) - 1.2 + dz          # bar bottom, 1.2 mm under the lip
    pts = [[u, g.clip_n(P, u) + bow(u) + dn - t_, z] for u in (P.clip_u - hw, P.clip_u + hw)
           for t_ in (0.0, P.clip_bar_t) for z in (zc, zc + 9)]
    return M.hull_points(pts).transform(F_)


check("the clip's cross bar sits in the groove across the tongue", overlap(shroud, bar()) < 1e-3)
check("pulled forward, the bar catches on the tongue's tooth",
      overlap(shroud, bar(dn=-(P.clip_bar_t + 2 * P.groove_clear))) > 1)
tw = P.tongue_w
check(f"the tongue ({tw:.0f} mm) fits between the clip's legs ({P.clip_leg_gap:.0f} mm apart)",
      P.clip_leg_gap - tw >= 2)

# 7. shroud fits the 11 in opening (the ear pads further back reach out to the door's flanges)
sb = (shroud ^ g.box(-300, 300, -60, 300, -300, 300)).bounding_box()
sw = sb[3] - sb[0]
check(f"shroud width {sw:.1f} mm fits the {P.opening_w:.1f} mm opening",
      sw <= P.opening_w - 2 * P.opening_side_clear + 0.01,
      f"{(P.opening_w - sw) / 2:.1f} mm clear each side")

# 7a. an ear pad on each wing comes out to the door's side flange, 0.5 mm short of it, with its
#     screw hole on the door's slot (where the stock bezel's ear screws on)
sv = np.asarray(shroud.to_mesh().vert_properties)[:, :3]
for (x, y, z, nrm) in P.ear_slots:
    nrm = np.asarray(nrm)
    rel = sv - [x, y, z]
    near = sv[np.linalg.norm(rel - np.outer(rel @ nrm, nrm), axis=1) < P.ear_pad_d / 2 + 0.5]   # on the pad
    reach = float(((near - [x, y, z]) @ nrm).max())                      # pad face vs the flange
    hole = [x, y, z] - nrm * np.arange(1.0, 8.0, 0.5)[:, None]          # along the screw, into the pad
    side = "hood" if x < 0 else "fender"
    solid_at = [overlap(shroud, g.box(q[0] - 0.4, q[0] + 0.4, q[1] - 0.4, q[1] + 0.4, q[2] - 0.4, q[2] + 0.4)) for q in hole]
    check(f"{side} ear pad reaches the door's flange ({-reach:.1f} mm gap) with its hole on the door's slot",
          0.3 < -reach < 0.8 and max(solid_at) < 1e-6)

# 7b. keep clear of the car parts next to the holes (seen in the owner's photos)
z4 = pts["arm hole 4"][1]
ax = pts["arm hole 4"][0]
pivot_zone = g.box(ax - 20, ax + 20, y_back - 5, y_back + t + 30, z4 - 45, z4 - 20)
check("nothing reaches the arm's pivot bolt, 20+ mm below hole 4", overlap(carrier, pivot_zone) < 1e-6)
pu = pts["pad upper"]
square_zone = g.box(pu[0] - 15, pu[0] + 15, y_back - 5, y_back + t + 30, pu[1] + 13, pu[1] + 45)
check("nothing reaches the pad's square adjuster, 13+ mm above the upper hole", overlap(carrier, square_zone) < 1e-6)
mid = g.box(-60, 60, y_back - 5, y_back + t, 5, 80)
check("the middle of the back is open (no wall between the tabs)", overlap(carrier, mid) < 1e-6)

# 8. driver part is the mirror: arm on -X
drv = g.mirror_x(carrier)
arm_x = pts["arm hole 4"][0]
open_drv = overlap(drv, g.cyl_y(P.mount_hole_d - 1, y_back - 1, y_back + t + 1, -arm_x, pts["arm hole 4"][1]))
check("driver carrier has the arm slots on the other side", open_drv < 1e-6)

# 9. every exported STL is one watertight solid lying flat on the bed
here = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(here, "stl", "**", "*.stl"), recursive=True)):
    tm = trimesh.load(f)
    name = os.path.relpath(f, here)
    flat = tm.bounds[0][2] == 0 and tm.area_faces[(tm.face_normals[:, 2] < -0.99)
                                                  & (tm.triangles_center[:, 2] < 0.01)].sum() > 50
    parts = len(M(m3d.Mesh(tm.vertices.astype("float32"), tm.faces.astype("uint32"))).decompose())
    multi = "spacer" in name or "fit_test_mount" in name or "fit_test_window" in name      # printed as separate pieces on purpose
    ok = tm.is_watertight and tm.volume > 0 and flat and (parts == 1 or multi)
    check(f"{name}: watertight, flat on the bed, {parts} piece(s)", ok)

print(f"\n{sum(results)}/{len(results)} checks passed")
raise SystemExit(0 if all(results) else 1)
