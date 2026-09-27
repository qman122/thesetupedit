"""Parametric C5 Corvette sleepy-eye pod carrier and shroud (1997-2004 pop-up headlights).

Holds three generic 3 in x 2 in dual-lens LED pods per side in place of the stock
headlight unit, the same way the KnightDriveTV kit does: one carrier per side that
bolts to the stock headlight mounting points, plus a front shroud that frames the pods.

Run:  python3 generate.py            -> writes STL files to ./stl and previews to ./preview
All sizes are millimetres. Change the numbers in PARAMS and re-run.

Axes (driver-side part as modelled): X across the car (+X toward the fender),
Y fore-aft (+Y toward the front of the car), Z up. Pod faces sit at Y = 0 and
the top of the carrier floor is Z = 0. The passenger part is a mirror copy.
"""

import os
from dataclasses import dataclass, field

import manifold3d as m3d
import numpy as np

m3d.set_circular_segments(48)
M = m3d.Manifold
CS = m3d.CrossSection


@dataclass
class Params:
    # --- LED pod (measured from the owner's photos; confirm with calipers) ---
    pod_face_w: float = 76.0      # front bezel width (3.0 in)
    pod_face_h: float = 48.0      # front bezel height (1 7/8 in)
    pod_face_r: float = 6.0       # front bezel corner radius
    pod_body_w: float = 80.0      # widest point of the finned body
    pod_body_h: float = 52.0      # tallest point of the finned body
    pod_depth: float = 65.0       # lens face to back of the fins (ESTIMATE)
    pod_gap: float = 6.0          # space between neighbouring pods
    pod_bolt_d: float = 8.6       # slot width for the pod bracket bolt (M8 or 5/16 in)
    pod_bolt_y: float = -30.0     # slot centre, measured back from the pod face
    pod_slot_len: float = 24.0    # fore-aft adjustment in each slot

    # --- carrier ---
    floor_t: float = 5.0          # floor thickness
    wall_t: float = 4.0           # end cheeks and dividers
    divider_h: float = 14.0       # height of the locating ribs between pods
    lip_h: float = 8.0            # stiffening lip under the front and rear floor edges
    floor_front_setback: float = 3.0  # floor front edge sits this far behind the pod faces

    # Mounting wall: a solid vertical plate behind the pods. The stock headlight
    # bolts run fore-aft through it. With mount_holes empty it is left blank
    # ("drill to fit"): hold the stock headlight's tabs against it, mark, drill 6.5 mm.
    mount_wall_y: float = -95.0   # front face of the wall, behind the pod faces (ESTIMATE)
    mount_wall_t: float = 6.0
    mount_wall_z0: float = -12.0  # bottom of the wall relative to the floor top
    mount_wall_z1: float = 62.0   # top of the wall
    mount_wall_extra_w: float = 20.0  # extra width past each end of the pod row
    mount_hole_d: float = 6.5     # M6 clearance
    # (x, z) positions on the wall once measured, e.g. [(130, 20), (130, 50), (-128, 30), (40, 58)]
    mount_holes: list = field(default_factory=list)
    cable_hole_d: float = 22.0    # one pass-through per pod for the pigtail and plug

    # --- shroud (front frame) ---
    shroud_t: float = 3.0         # face thickness
    shroud_margin_x: float = 10.0  # frame material past the outer pods, each side
    shroud_margin_top: float = 8.0
    shroud_margin_bot: float = 12.0
    shroud_r: float = 14.0        # outer corner radius
    shroud_return: float = 12.0   # depth of the lip that wraps back from the face
    window_clear: float = 0.8     # clearance around each pod bezel
    shroud_tab_screw_d: float = 3.4  # M4 self-tapping into the carrier floor
    shroud_gap: float = 0.5       # air gap between pod faces and the back of the shroud face

    # --- splitting for printers smaller than ~310 mm ---
    # Cut between the middle and outer pods; the halves bolt together with splice plates.
    splice_screw_d: float = 4.4   # M4 clearance
    splice_t: float = 5.0         # splice plate thickness


P = Params()


# ---------- helpers ----------

def box(x0, x1, y0, y1, z0, z1):
    return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def rrect(w, h, r):
    """Rounded rectangle centred on the origin, as a CrossSection."""
    r = min(r, w / 2 - 0.01, h / 2 - 0.01)
    return CS.square([w - 2 * r, h - 2 * r], center=True).offset(r, m3d.JoinType.Round)


def plate_xz(section, y_front, t):
    """Extrude an XZ-plane cross section backwards (-Y) by t from y_front."""
    solid = M.extrude(section, t)          # along +Z
    solid = solid.rotate([90, 0, 0])      # section X->X, section Y->Z, extrusion -> -Y
    return solid.translate([0, y_front, 0])


def cyl_y(d, y0, y1, x, z):
    """Cylinder along Y from y0 to y1 at (x, z)."""
    c = M.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0])
    return c.translate([x, y0, z])


def cyl_z(d, z0, z1, x, y):
    return M.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def slot_z(w, length, z0, z1, x, y):
    """Fore-aft slot through a horizontal plate."""
    s = CS.square([w, length - w], center=True).offset(w / 2, m3d.JoinType.Round)
    return M.extrude(s, z1 - z0).translate([x, y, z0])


def pod_x(p):
    pitch = p.pod_body_w + p.pod_gap
    return [-pitch, 0.0, pitch]


def row_w(p):
    return 3 * p.pod_body_w + 2 * p.pod_gap


# ---------- parts ----------

def carrier(p):
    half = row_w(p) / 2 + p.wall_t
    y_front = -p.floor_front_setback
    y_back = p.mount_wall_y
    parts = []

    # floor
    parts.append(box(-half, half, y_back, y_front, -p.floor_t, 0))
    # stiffening lips under the front and rear edges
    parts.append(box(-half, half, y_front - p.wall_t, y_front, -p.floor_t - p.lip_h, 0))
    parts.append(box(-half, half, y_back, y_back + p.wall_t, -p.floor_t - p.lip_h, 0))

    # locating ribs: two end cheeks plus two dividers
    for x in [-half + p.wall_t / 2, half - p.wall_t / 2]:
        parts.append(box(x - p.wall_t / 2, x + p.wall_t / 2, y_back, y_front, 0, p.divider_h))
    for i in range(2):
        x = pod_x(p)[i] + (p.pod_body_w + p.pod_gap) / 2
        parts.append(box(x - p.wall_t / 2, x + p.wall_t / 2,
                         -p.pod_depth + 5, y_front, 0, p.divider_h))

    # mounting wall behind the pods
    wall_half = half + p.mount_wall_extra_w
    wall_sec = CS.square([2 * wall_half, p.mount_wall_z1 - p.mount_wall_z0])
    wall_sec = wall_sec.translate([-wall_half, p.mount_wall_z0])
    parts.append(plate_xz(wall_sec, y_back + p.mount_wall_t, p.mount_wall_t))

    # gussets tying the wall to the floor, one in each gap and at each end
    gx = [-half + p.wall_t / 2, half - p.wall_t / 2]
    gx += [pod_x(p)[i] + (p.pod_body_w + p.pod_gap) / 2 for i in range(2)]
    g_len = 25.0
    g_h = p.mount_wall_z1 * 0.7
    tri = CS([[[0, 0], [g_len, 0], [0, g_h]]])        # (Y offset, Z) profile
    for x in gx:
        # profile X -> world Y, profile Y -> world Z, extrusion -> world X
        g = M.extrude(tri, p.wall_t).transform(
            [[0, 0, 1, x - p.wall_t / 2],
             [1, 0, 0, y_back + p.mount_wall_t],
             [0, 1, 0, 0]])
        parts.append(g)

    # bosses under the floor for the shroud screws
    boss_z0 = -p.floor_t - p.lip_h
    for x in shroud_tab_x(p):
        parts.append(cyl_z(11, boss_z0, -p.floor_t + 0.01, x, y_front - 12))

    body = M.batch_boolean(parts, m3d.OpType.Add)

    cuts = []
    for x in pod_x(p):
        # bracket bolt slot under each pod
        cuts.append(slot_z(p.pod_bolt_d, p.pod_slot_len, -p.floor_t - 1, 1, x, p.pod_bolt_y))
        # cable pass-through in the wall, centred behind each pod
        cuts.append(cyl_y(p.cable_hole_d, y_back - 1, y_back + p.mount_wall_t + 1,
                          x, p.pod_body_h / 2))
    for (hx, hz) in p.mount_holes:
        cuts.append(cyl_y(p.mount_hole_d, y_back - 1, y_back + p.mount_wall_t + 1, hx, hz))
    # shroud screw holes near the front edge of the floor, in the gaps between pods
    for x in shroud_tab_x(p):
        # blind pilot hole for an M4 self-tapping screw, stops 1.5 mm under the floor top
        cuts.append(cyl_z(p.shroud_tab_screw_d - 0.4, boss_z0 - 1, -1.5, x, y_front - 12))
    # splice holes: countersunk from the top of the floor so the pods sit flat
    for (hx, hy) in splice_floor_holes(p):
        cuts.append(cyl_z(p.splice_screw_d, -p.floor_t - 1, 1, hx, hy))
        cuts.append(M.cylinder(2.3, p.splice_screw_d / 2, 4.2).translate([hx, hy, -2.3 + 0.001]))
    for (hx, hz) in splice_wall_holes(p):
        cuts.append(cyl_y(p.splice_screw_d, y_back - 1, y_back + p.mount_wall_t + 1, hx, hz))
    return M.batch_boolean([body] + cuts, m3d.OpType.Subtract)


def splice_plates(p):
    """Floor plate (goes under the floor) and wall plate (goes behind the wall)."""
    sx, t = split_x(p), p.splice_t
    ys = [y for (_, y) in splice_floor_holes(p)]
    floor = box(sx - 26, sx + 26, min(ys) - 9, max(ys) + 9, 0, t)
    for (hx, hy) in splice_floor_holes(p):
        floor = floor - cyl_z(p.splice_screw_d, -1, t + 1, hx, hy)
    zs = [z for (_, z) in splice_wall_holes(p)]
    wall = box(sx - 26, sx + 26, min(zs) - 9, max(zs) + 9, 0, t)
    for (hx, hz) in splice_wall_holes(p):
        wall = wall - cyl_z(p.splice_screw_d, -1, t + 1, hx, hz)
    return floor.translate([-sx, 0, 0]), wall.translate([-sx, 0, 0])


def shroud_splice(p):
    """Backing strip glued behind the shroud face across the split line."""
    sx = split_x(p)
    bar = pitch(p) - (p.pod_face_w + 2 * p.window_clear)       # material between windows
    z_bot = -p.shroud_margin_bot - p.floor_t + p.shroud_t + 0.5
    win_bot = p.pod_body_h / 2 - (p.pod_face_h / 2 + p.window_clear)
    strip = box(sx - bar / 2 + 0.6, sx + bar / 2 - 0.6, 0, 2.5, z_bot, win_bot + p.pod_face_h)
    foot = box(sx - 22, sx + 22, 0, 2.5, z_bot, win_bot - 0.5)
    return (strip + foot).rotate([-90, 0, 0]).translate([-sx, 0, 0])


def pitch(p):
    return p.pod_body_w + p.pod_gap


def split_x(p):
    return pitch(p) / 2


def shroud_tab_x(p):
    return [-pitch(p) / 2, pitch(p) + 14]


def splice_floor_holes(p):
    sx = split_x(p)
    return [(sx + dx, y) for dx in (-16, 16) for y in (-20, p.mount_wall_y + 16)]


def splice_wall_holes(p):
    sx = split_x(p)
    return [(sx + dx, z) for dx in (-16, 16) for z in (6, 44)]


def shroud(p):
    ow = row_w(p) + 2 * p.shroud_margin_x
    z_bot = -p.shroud_margin_bot - p.floor_t
    z_top = p.pod_body_h + p.shroud_margin_top
    oh = z_top - z_bot
    zc = (z_top + z_bot) / 2
    y_face = p.shroud_t + p.shroud_gap     # front of the shroud face

    outer = rrect(ow, oh, p.shroud_r).translate([0, zc])
    face = plate_xz(outer, y_face, p.shroud_t)

    # return lip wrapping back around the outside edge
    inner = rrect(ow - 2 * p.shroud_t, oh - 2 * p.shroud_t,
                  max(p.shroud_r - p.shroud_t, 1)).translate([0, zc])
    ring = outer - inner
    lip = plate_xz(ring, y_face - p.shroud_t, p.shroud_return)

    # windows for the pod bezels, centred on each pod face
    win_w = p.pod_face_w + 2 * p.window_clear
    win_h = p.pod_face_h + 2 * p.window_clear
    wins = [plate_xz(rrect(win_w, win_h, p.pod_face_r + p.window_clear)
                     .translate([x, p.pod_body_h / 2]), y_face + 1, p.shroud_t + 2)
            for x in pod_x(p)]

    # tabs that reach back under the carrier floor for two M4 screws
    tabs = []
    tab_y0 = -p.floor_front_setback - 20
    for x in shroud_tab_x(p):
        t = box(x - 9, x + 9, tab_y0, y_face - p.shroud_t,
                -p.floor_t - p.lip_h - 3, -p.floor_t - p.lip_h)
        t = t - cyl_z(p.shroud_tab_screw_d, -40, 0, x, -p.floor_front_setback - 12)
        tabs.append(t)
    # the tabs overlap the bottom of the return lip, which ties them to the face
    body = M.batch_boolean([face, lip] + tabs, m3d.OpType.Add)
    return M.batch_boolean([body] + wins, m3d.OpType.Subtract)


def fit_test(p):
    """Quick print: one shroud window in a 2 mm plate, to check the pod bezel fits."""
    win = rrect(p.pod_face_w + 2 * p.window_clear, p.pod_face_h + 2 * p.window_clear,
                p.pod_face_r + p.window_clear)
    plate = rrect(p.pod_face_w + 24, p.pod_face_h + 24, 8) - win
    return M.extrude(plate, 2.0)


def pod_dummy(p):
    """Stand-in pod used only in the preview images."""
    pods = []
    for x in pod_x(p):
        face = plate_xz(rrect(p.pod_face_w, p.pod_face_h, p.pod_face_r)
                        .translate([x, p.pod_body_h / 2]), 0, 8)
        body = box(x - p.pod_body_w / 2, x + p.pod_body_w / 2, -p.pod_depth, -8,
                   0, p.pod_body_h)
        pods += [face, body]
    return M.batch_boolean(pods, m3d.OpType.Add)


# ---------- output ----------

def to_trimesh(man):
    import trimesh
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


def mirror_x(man):
    return man.mirror([1, 0, 0])


def print_orient_shroud(man):
    """Lay the shroud face-down on the bed (face at Z = 0)."""
    return man.rotate([-90, 0, 0])


def print_orient_carrier(man):
    """Stand the carrier on the flat back of its mounting wall (no supports under the floor)."""
    return man.rotate([90, 0, 0])


def save(man, path):
    tm = to_trimesh(man)
    b = tm.bounds
    tm.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    tm.export(path)
    size = tm.bounds[1] - tm.bounds[0]
    print(f"{os.path.basename(path):32s} {size[0]:6.1f} x {size[1]:6.1f} x {size[2]:6.1f} mm"
          f"  watertight={tm.is_watertight}")
    return tm


def preview(p, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    items = [(carrier(p), "#4a6fa5"), (shroud(p), "#2b2b2b"), (pod_dummy(p), "#c9a227")]
    views = [("front (from ahead of the car)", 0, 90), ("three-quarter", 25, 55),
             ("from above", 89, 90), ("from behind", 15, -90)]
    fig = plt.figure(figsize=(14, 10))
    for i, (title, elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, i + 1, projection="3d")
        for man, col in items:
            tm = to_trimesh(man)
            light = np.array([0.3, 0.5, 0.8]) / np.linalg.norm([0.3, 0.5, 0.8])
            k = 0.45 + 0.55 * np.clip(tm.face_normals @ light, 0, 1)
            rgb = np.array(matplotlib.colors.to_rgb(col))
            ax.add_collection3d(Poly3DCollection(tm.triangles, facecolors=k[:, None] * rgb,
                                                 edgecolors="none"))
        ax.set_xlim(-160, 160); ax.set_ylim(-140, 40); ax.set_zlim(-40, 80)
        ax.set_box_aspect((320, 180, 120))
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title); ax.set_axis_off()
    fig.suptitle("C5 sleepy-eye pod carrier (blue), shroud (black), pods (gold) - driver side")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print("preview ->", out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "stl"), exist_ok=True)
    os.makedirs(os.path.join(here, "preview"), exist_ok=True)
    c, s = carrier(P), shroud(P)
    save(print_orient_carrier(c), os.path.join(here, "stl", "carrier_driver.stl"))
    save(print_orient_carrier(mirror_x(c)), os.path.join(here, "stl", "carrier_passenger.stl"))
    save(print_orient_shroud(s), os.path.join(here, "stl", "shroud_driver.stl"))
    save(print_orient_shroud(mirror_x(s)), os.path.join(here, "stl", "shroud_passenger.stl"))
    save(fit_test(P), os.path.join(here, "stl", "fit_test_window.stl"))

    # split versions for beds smaller than ~310 mm
    os.makedirs(os.path.join(here, "stl", "split"), exist_ok=True)
    sd = os.path.join(here, "stl", "split")
    for side, cc, ss, sgn in [("driver", c, s, 1), ("passenger", mirror_x(c), mirror_x(s), -1)]:
        a, b = cc.split_by_plane([sgn, 0, 0], split_x(P))
        save(print_orient_carrier(b), os.path.join(sd, f"carrier_{side}_A.stl"))
        save(print_orient_carrier(a), os.path.join(sd, f"carrier_{side}_B.stl"))
        a, b = ss.split_by_plane([sgn, 0, 0], split_x(P))
        save(print_orient_shroud(b), os.path.join(sd, f"shroud_{side}_A.stl"))
        save(print_orient_shroud(a), os.path.join(sd, f"shroud_{side}_B.stl"))
    fp, wp = splice_plates(P)
    save(fp, os.path.join(sd, "splice_floor_x2.stl"))
    save(wp, os.path.join(sd, "splice_wall_x2.stl"))
    save(shroud_splice(P), os.path.join(sd, "shroud_splice_x2.stl"))
    preview(P, os.path.join(here, "preview", "assembly.png"))
