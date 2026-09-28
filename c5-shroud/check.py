"""Sanity checks for the C5 pod carrier and shroud. Run: python3 check.py

Checks the measured hole spacing, that bolts, nuts, pods and the shroud don't collide
anywhere in their adjustment range, that the shroud fits the opening, and that every
printable part is one clean solid.
"""

import glob
import os

import manifold3d as m3d
import trimesh

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
gap = (shroud.bounding_box()[1]) - (y_back + t + 8)
check(f"bezel back edge sits {gap:.1f} mm in front of the nuts", gap > 2)

# 7. shroud fits the 11 in opening
sb = shroud.bounding_box()
sw = sb[3] - sb[0]
check(f"shroud width {sw:.1f} mm fits the {P.opening_w:.1f} mm opening",
      sw <= P.opening_w - 2 * P.opening_side_clear + 0.01,
      f"{(P.opening_w - sw) / 2:.1f} mm clear each side")

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
