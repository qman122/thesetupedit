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


carrier, shroud, pods = g.carrier(P), g.shroud(P), g.lights_dummy(P)
PODS = P.lights == "pods"           # LIGHTS=projectors checks the projector bracket and bezel instead
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
    # and only as wide as the hole: solid 1.5 mm out from its sides, so the nut's washer bears on it
    side = P.mount_hole_d / 2 + 1.5
    for sd in (-side, side):
        qx, qz = (x, z + sd) if ax == "x" else (x + sd, z)
        solid = min(solid, overlap(carrier, g.cyl_y(1, y_back + 0.5, y_back + t - 0.5, qx, qz)))
    check(f"{n}: M6 slot open through the wall, +/-{travel:.1f} mm travel",
          max(probe_open) < 1e-6 and solid > 1, f"at x={x:.1f} z={z:.1f}")

# 2b. each pod's stud slot is only as wide as the stud's clearance, with the floor either side of
#     it, so the nut in the channel below can't pull up through it
half_ = (P.pod_slot_len - P.pod_bolt_d) / 2
ok_stud = True
for pose in (g.pod_poses(P) if PODS else []):
    sx_, sy_ = g.pose_pt(pose, 0, P.pod_bolt_nominal_y)
    for sd in (-(P.pod_bolt_d / 2 + 1.5), P.pod_bolt_d / 2 + 1.5):
        ok_stud &= overlap(carrier, g.cyl_z(1, -P.floor_t + 0.5, -0.5, sx_ + sd, sy_)) > 1e-3
    ok_stud &= overlap(carrier, g.cyl_z(P.pod_bolt_d - 1, -P.floor_t - 1, 1, sx_, sy_)) < 1e-6
if PODS:
    check(f"pod stud slots {P.pod_bolt_d} mm wide, floor either side (the nut can't pull through)", ok_stud)

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
if not PODS:
    fwd = back = 0.0
worst = max(overlap(carrier, g.lights_dummy(P, s)) for s in (-back, 0, fwd))
gap_nominal = min(y for (_, y, _) in g.pod_poses(P)) - P.pod_depth - (y_back + t)   # the rearmost pod
gap_min = gap_nominal - back
if PODS:
    check(f"pods clear the carrier from {back:.1f} mm back to {fwd:.1f} mm forward", worst < 1e-6)
    check(f"cable room behind the pods: {gap_nominal:.1f} mm default, {gap_min:.1f} mm at full rearward",
          gap_min >= 5 and gap_nominal >= 15)
else:
    check("the projectors sit in their cradles without touching them", worst < 1e-6)
    spans = [g.proj_cradle_span(P, yf, x) for (x, yf, _) in g.proj_poses(P)]
    check("every cradle stops in front of the mounting tabs' plane", min(y0 for y0, _ in spans) >= y_back + t,
          ", ".join(f"{y1 - y0:.0f} mm long" for y0, y1 in spans))

# 5. pods and shroud don't touch, and each pod face sits inside its window
check(f"{'pods' if PODS else 'projectors'} clear the shroud", overlap(pods, shroud) < 1e-6)
if PODS:
    check(f"window gap {P.window_clear_x} mm each side, {P.window_clear_y} mm top and bottom", min(P.window_clear_x, P.window_clear_y) > 0.3)
else:
    mis = max(overlap(shroud, g.lights_dummy(P).translate([dx, 0, dz])) for dx in (-1.5, 0, 1.5) for dz in (-0.5, 0, 0.5))
    check("projectors still clear the bezel 1.5 mm off side to side and 0.5 mm up or down", mis < 1e-6)

# 6. shroud and carrier only touch at the screw tabs
ov = overlap(shroud, carrier)
check("shroud and carrier don't overlap", ov < 1e-3, f"overlap {ov:.4f} mm^3")

# 6b. the bezel slides forward with the pods (0 to bezel_travel); it never goes back
worst_nut = worst_car = worst_pod = 0.0
for s_ in ((0.0, P.bezel_travel / 2, P.bezel_travel) if PODS else (0.0,)):
    bz = shroud.translate([0, s_, 0])
    worst_car = max(worst_car, overlap(bz, carrier))
    worst_pod = max(worst_pod, overlap(bz, g.lights_dummy(P, s_)))
    for n, (x, z, ax) in pts.items():
        ln = P.arm_slot_len if ax == "x" else P.pad_slot_len
        tr = (ln - P.mount_hole_d) / 2
        for d_ in (-tr, tr):
            px, pz = (x + d_, z) if ax == "x" else (x, z + d_)
            worst_nut = max(worst_nut, overlap(bz, g.cyl_y(2 * P.nut_r, y_back + t + 0.01, y_back + t + 8, px, pz)))
if PODS:
    check(f"bezel clears the carrier anywhere in its {P.bezel_travel:.0f} mm of forward travel", worst_car < 1e-3)
    check("bezel clears the pods when both slide forward together", worst_pod < 1e-6)
else:
    check("bezel clears the projector bracket", worst_car < 1e-3)
check("bezel wrap clears all four mounting nuts", worst_nut < 1e-6)
if PODS:
    check("pods can also sit up to 10 mm further back with the bezel in place",
          max(overlap(shroud, g.pod_dummy(P, -s_)) for s_ in (0, back)) < 1e-6)
# only the part of the bezel in line with the nuts counts; the wings run back beside them
nut_x = max(abs(x) + (P.arm_slot_len / 2 if ax == "x" else 0) + P.nut_r for (x, z, ax) in pts.values())
gap = (shroud ^ g.box(-nut_x, nut_x, -300, 300, -300, 300)).bounding_box()[1] - (y_back + t + 8)
check(f"bezel sits {gap:.1f} mm in front of the nuts (the wings pass outside them)", gap > 2)

# 6c. every lens sees out straight ahead: no ray from anywhere on a lens, within 10 degrees
#     either side of straight ahead (seen from above, at lens height), hits the bezel
_lens_z = g.pod_zc(P) if PODS else g.proj_poses(P)[0][2]
_polys = [Path(np.asarray(q)) for q in shroud.slice(_lens_z).to_polygons()]


def _hits(pts_):
    c = np.zeros(len(pts_), int)
    for pa in _polys:
        c += pa.contains_points(pts_)
    return (c % 2 == 1).any()


blocked = 0
_lenses = ([(px, py, lx) for (px, py, _) in g.pod_poses(P) for lx in (-18.5, 18.5)] if PODS
           else [(x, yf, 0.0) for (x, yf, _) in g.proj_poses(P)])
for (px, py, lx) in _lenses:
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
nose = -P.cover_edge_n                  # the door's front edge, behind the bead on the blade's front


def bow(u):
    return P.front_bow * (1 - min(abs(u) / U_, 1) ** 2)


lip_min = min(np.interp(u, g.COVER_LIP_U, g.COVER_LIP_Z) for u in np.linspace(-U_ - 3, U_ + 3, 200))
lip_gap, lip_pen = [], []
for u in np.arange(-U_ + 12, U_ - 11, 10.0):
    zl = z_top + float(np.interp(u, g.COVER_LIP_U, g.COVER_LIP_Z)) - lip_min
    strip = g.box(u - 4, u + 4, nose + bow(u) - 5, nose + bow(u), zl, zl + 5).transform(F_)
    lip_pen.append(overlap(shroud, strip) / 40)                     # the strips are 8 x 5 mm
    # the highest point of the bezel under the lip there (the bead): how far below the lip
    under = shroud ^ g.box(u - 4, u + 4, nose + bow(u) - 5, nose + bow(u), zl - 5, zl + 5).transform(F_)
    lip_gap.append(zl - under.bounding_box()[5] if not under.is_empty() else 5.0)
worst = int(np.argmax(lip_gap))
check("the door's lip sits on the top rail all the way across (no clash, no gap)",
      max(lip_pen) < 0.15 and max(lip_gap) <= 0.2,
      f"{len(lip_gap)} places along the front: at most {max(lip_pen):.2f} mm into it, "
      f"at most {max(lip_gap):.2f} mm below it (u = {np.arange(-U_ + 12, U_ - 11, 10.0)[worst]:.0f})")


def bar(dn=0.0, dz=0.0):
    hw = P.clip_leg_gap / 2 + 2
    zc = z_top + float(g.top_rise(P, P.clip_u)) - 1.2 + dz          # bar bottom, 1.2 mm under the lip
    pts = [[u, g.clip_n(P, u) + bow(u) + dn - t_, z] for u in (P.clip_u - hw, P.clip_u + hw)
           for t_ in (0.0, P.clip_bar_t) for z in (zc, zc + 9)]
    return M.hull_points(pts).transform(F_)


# the tongue ends where its taper ends: the owner's fit test clipped on once its narrow end
# (with the groove and tooth) was cut off there. It stays clear of the clip's cross bar.
check("the clip's cross bar clears the tongue", overlap(shroud, bar()) < 1e-3)
n_tip = min(g.clip_n(P, u) + P.groove_clear for u in (P.clip_u - P.tongue_w / 2, P.clip_u + P.tongue_w / 2)) + 7
lip_ = z_top + float(g.top_rise(P, P.clip_u))
tip_in = g.box(P.clip_u - 3, P.clip_u + 3, n_tip + bow(P.clip_u) + 1, n_tip + bow(P.clip_u) + 2, lip_ - 3, lip_ - 2).transform(F_)
tip_out = g.box(P.clip_u - 3, P.clip_u + 3, n_tip + bow(P.clip_u) - 3, n_tip + bow(P.clip_u) - 2, lip_ - 5, lip_ + 1).transform(F_)
check(f"the tongue ends where its taper ends, {-P.blade_depth + 1.5 - n_tip:.0f} mm behind the rail",
      overlap(shroud, tip_in) > 1 and overlap(shroud, tip_out) < 1e-3)
tw = P.tongue_w
check(f"the tongue ({tw:.0f} mm) fits between the clip's legs ({P.clip_leg_gap:.0f} mm apart)",
      P.clip_leg_gap - tw >= 2)

# 7. the bezel is one continuous shell; its ears lie outside the door's side flanges with a
#    screw hole on every hole in the flange (where the stock bezel's ears screw on)
check("the bezel is one piece", len(shroud.decompose()) == 1)
for name in ("hood", "fender"):
    holes = g.door_side(name)[0]
    ok_holes = True
    for h in holes:
        at, nrm = np.asarray(h["at"]), np.asarray(h["normal"])                     # passenger frame
        bore = g._along(M.cylinder(16, 2.2, 2.2, 16), nrm, at + 0.5 * nrm)          # screw path, clear
        # material round it, in the first mm out from the flange (the side now sits just inside
        # the door's outline, so there's as little as 2 mm between the flange and its outside)
        ring = g._along(M.cylinder(1, 6.5, 6.5, 32) - M.cylinder(1, 4.5, 4.5, 32), nrm, at + 0.6 * nrm)
        ok_holes &= overlap(shroud, bore) < 1e-6 and overlap(shroud, ring) > 20
    check(f"{name} ear: a screw hole on each of the door's {len(holes)} flange holes", ok_holes)

# 7a. split for printing through the hood-side post: two pieces that each fit the A1's 256 mm bed,
#     with the dowel holes open on both cut faces
pieces = g.split_shell(P, shroud)
fits = all(len(pc.decompose()) == 1 and max(np.ptp(np.asarray(g.print_orient_shroud(pc).to_mesh().vert_properties)[:, :2], 0)) <= 256
           for pc in pieces)
check("print pieces: each one solid and fits the 256 mm bed", fits,
      " / ".join("%.0f x %.0f" % tuple(np.ptp(np.asarray(g.print_orient_shroud(pc).to_mesh().vert_properties)[:, :2], 0)) for pc in pieces))
F_ = g.front_frame(P)
us_, n_c, z_dw = g.dowel_spot(P)
z_top_, z_bu_, z_wb_, _, _ = g.shell_levels(P)
dowels_ok = True
walled = 1.0
for z in z_dw:
    for du in (-P.dowel_depth + 1, P.dowel_depth - 1):
        probe = g.lift_top(P, g.box(us_ + du - 0.5, us_ + du + 0.5, n_c - 0.4, n_c + 0.4, z - 0.4, z + 0.4).transform(F_))
        dowels_ok &= all(overlap(pc, probe) < 1e-6 for pc in pieces)
    # and there's wall round the hole: a 1 mm ring round it is (almost all) in the bezel
    ring = (M.cylinder(2 * P.dowel_depth - 1, P.dowel_d / 2 + 1.0, P.dowel_d / 2 + 1.0, 32, True)
            - M.cylinder(2 * P.dowel_depth, P.dowel_d / 2 + 0.05, P.dowel_d / 2 + 0.05, 32, True))
    ring = g.lift_top(P, ring.transform([[0, 0, 1, us_], [1, 0, 0, n_c], [0, 1, 0, z]]).transform(F_))
    walled = min(walled, (ring ^ shroud).volume() / ring.volume())
check("dowel holes go into both pieces, with wall round them", dowels_ok and walled > 0.85,
      f"{100 * walled:.0f}% of a 1 mm ring round the hole is solid")

# 7b. keep clear of the car parts next to the holes (seen in the owner's photos)
z4 = pts["arm hole 4"][1]
ax = pts["arm hole 4"][0]
pivot_zone = g.box(ax - 20, ax + 20, y_back - 5, y_back + t + 30, z4 - 45, z4 - 20)
check("nothing reaches the arm's pivot bolt, 20+ mm below hole 4", overlap(carrier, pivot_zone) < 1e-6)
pu = pts["pad upper"]
square_zone = g.box(pu[0] - 15, pu[0] + 15, y_back - 5, y_back + t + 30, pu[1] + 13, pu[1] + 45)
check("nothing reaches the pad's square adjuster, 13+ mm above the upper hole", overlap(carrier, square_zone) < 1e-6)
if not PODS:
    check("the projectors clear the pad's square adjuster too", overlap(pods, square_zone) < 1e-6,
          f"{overlap(pods, square_zone):.0f} mm^3 inside its space")
mid = g.box(-60, 60, y_back - 5, y_back + t, 5, 80)
check("the middle of the back is open (no wall between the tabs)", overlap(carrier, mid) < 1e-6)

# 8. driver part is the mirror: arm on -X
drv = g.mirror_x(carrier)
arm_x = pts["arm hole 4"][0]
open_drv = overlap(drv, g.cyl_y(P.mount_hole_d - 1, y_back - 1, y_back + t + 1, -arm_x, pts["arm hole 4"][1]))
check("driver carrier has the arm slots on the other side", open_drv < 1e-6)

# 8a. the driver side is the mirror image, and everything still fits there
d_car, d_bez = g.mirror_x(carrier), g.mirror_x(shroud)
d_pods = g.mirror_x(g.lights_dummy(P))
check("driver side: bezel, carrier and pods are the passenger ones mirrored, same size",
      abs(d_bez.volume() - shroud.volume()) < 1 and abs(d_car.volume() - carrier.volume()) < 1
      and abs(d_bez.bounding_box()[0] + shroud.bounding_box()[3]) < 1e-3)
check("driver side: the bezel clears the carrier and the pods",
      overlap(d_bez, d_car) < 1e-3 and overlap(d_bez, d_pods) < 1e-3)

# 9. every exported STL is one watertight solid lying flat on the bed
here = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(here, "stl", "**", "*.stl"), recursive=True)):
    if os.sep + "cad" + os.sep in f:            # the bezel model itself (car frame), not a print file
        continue
    tm = trimesh.load(f)
    name = os.path.relpath(f, here)
    flat = tm.bounds[0][2] == 0 and tm.area_faces[(tm.face_normals[:, 2] < -0.99)
                                                  & (tm.triangles_center[:, 2] < 0.01)].sum() > 50
    parts = len(M(m3d.Mesh(tm.vertices.astype("float32"), tm.faces.astype("uint32"))).decompose())
    multi = ("spacer" in name or "fit_test_mount" in name or "fit_test_window" in name      # printed as separate pieces on purpose
             or "joint_test" in name
             or "drl_diffusers" in name or "projector_straps" in name
             or "assembled" in name)                                                            # (and the fit-check assemblies)
    curved = "bezel_" in name or "fit_test_blade" in name or "assembled" in name   # the top follows the door: supports under it
    ok = tm.is_watertight and tm.volume > 0 and tm.bounds[0][2] == 0 and (flat or curved) and (parts == 1 or multi)
    check(f"{name}: watertight, {'on' if curved else 'flat on'} the bed, {parts} piece(s)", ok)

print(f"\n{sum(results)}/{len(results)} checks passed")
raise SystemExit(0 if all(results) else 1)
