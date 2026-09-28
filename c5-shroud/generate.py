"""Parametric C5 Corvette sleepy-eye pod carrier and shroud (1997-2004 pop-up headlights).

Holds three 2.9 x 1.8 in dual-lens LED pods per side in place of the stock
headlight unit, the same way the KnightDriveTV kit does: one carrier per side that
bolts to the stock headlight mounting points, plus a front shroud that frames the pods.

Run:  python3 generate.py            -> writes STL files to ./stl and previews to ./preview
All sizes are millimetres. Change the numbers in PARAMS and re-run.

Axes (passenger-side part as modelled): X across the car (+X toward the fender),
Y fore-aft (+Y toward the front of the car), Z up. Pod faces sit at Y = 0 and
the top of the carrier floor is Z = 0. The driver part is a mirror copy.
Seen from in front of the car, the driver-side fender arm is on the right and the
aiming pad on the left.
"""

import os
from dataclasses import dataclass

import manifold3d as m3d
import numpy as np

m3d.set_circular_segments(48)
M = m3d.Manifold
CS = m3d.CrossSection


@dataclass
class Params:
    # --- LED pod: maker's dimension drawing, 3.0 x 1.8 in face, 1.8 in deep, 2.1 in tall with bracket ---
    pod_face_w: float = 76.2      # front bezel width (3.0 in)
    pod_face_h: float = 45.7      # front bezel height (1.8 in)
    pod_face_r: float = 6.0       # front bezel corner radius
    pod_body_w: float = 76.5      # body width (same as the bezel, plus a hair)
    pod_body_h: float = 46.0      # body height
    pod_depth: float = 45.7       # front to back (1.8 in)
    pod_lift: float = 7.6         # the bracket holds the body this far above the floor (2.1 in overall minus the 1.8 in body)
    pod_bracket_w: float = 43.0   # width of the bracket foot
    pod_bracket_d: float = 21.0   # front-to-back length of the bracket foot
    pod_gap: float = 8.0          # space between neighbouring pods
    pod_bolt_d: float = 8.6       # slot width for the bracket stud (about 8 mm / 5/16 in)
    pod_stud_d: float = 8.0       # stud diameter, from the drawing
    pod_bolt_y: float = -31.5     # slot centre, measured back from the pod face
    pod_slot_len: float = 34.6    # fore-aft adjustment: 16 mm forward (bezel follows), 10 mm back
    pod_bolt_nominal_y: float = -34.5  # stud position in the default spot (1.36 in behind the face)

    # --- carrier ---
    floor_t: float = 5.0          # floor thickness
    wall_t: float = 4.0           # end cheeks and dividers
    divider_h: float = 14.0       # height of the locating ribs between pods
    lip_h: float = 8.0            # stiffening lip under the front and rear floor edges
    floor_front_setback: float = 3.0  # floor front edge sits this far behind the pod faces

    # Mounting wall: a vertical plate behind the pods that sits in front of the
    # car's fender arm and aiming pad. M6 bolts go through the car part, then the wall.
    mount_wall_y: float = -95.0   # back face of the wall, behind the pod faces (ESTIMATE)
    mount_wall_t: float = 6.0
    mount_wall_z0: float = -5.0   # bottom of the tabs: flush with the floor bottom, clear of the arm's pivot bolt
    mount_hole_d: float = 6.3     # snug on an M6 bolt so it stays put while you line things up
    tab_margin: float = 6.0       # plastic left around the slots (kept small to clear parts next to the holes)
    cable_hole_d: float = 22.0    # one pass-through per pod for the pigtail and plug

    # --- stock mounting points: owner's tape measurements (approximate) ---
    arm_hole_a: float = 43.2      # A: fender arm, hole 1 to hole 4, centres (1.7 in)
    pad_hole_h: float = 19.0      # H: aiming pad, upper to lower hole (measured 0.8 in; test tab said a bit closer)
    span_b: float = 222.3         # B: across the car, pad upper hole to arm hole 4 (8.75 in)
    pad_above_arm_d: float = 19.3  # D: pad upper hole sits this much above arm hole 4 (0.76 in)
    arm4_above_floor: float = 14.0  # arm hole 4 height above the floor top (sets pod height)
    arm_slot_len: float = 13.7    # arm holes: side-to-side slots, +/- 3.7 mm for error in B
    pad_slot_len: float = 9.9     # pad holes: up-down slots, +/- 1.8 mm for error in D
    nut_r: float = 7.5            # M6 flange nut / washer radius, for clearance checks

    # --- front opening: owner's measurement ---
    opening_w: float = 279.4      # F: 11 in
    opening_side_clear: float = 5.0  # shroud clearance to the body at each side

    # --- shroud (front frame) ---
    shroud_t: float = 3.0         # face thickness
    shroud_margin_top: float = 8.0
    shroud_margin_bot: float = 25.0  # below the floor; owner says there's plenty of room
    shroud_r: float = 14.0        # outer corner radius
    # The shroud is a full bezel: its edge wraps back on all four sides so only the face and
    # the three lenses show when the door goes up. It stops short of the mounting nuts.
    shroud_return: float = 78.0   # how far the top, bottom and sides wrap back from the face
    bezel_rear_screw_y: float = -56.0  # two more M4 screws up through the bezel bottom into the carrier
    bezel_travel: float = 16.0    # the bezel's screw slots let it slide this far forward with the pods (never back)
    foam_channel_w: float = 10.0  # recess on top for adhesive foam weatherstrip (seals to the door)
    foam_channel_d: float = 1.0
    foam_channel_y: float = -14.0  # centre of the recess, behind the face
    # Window gap around the pod bezel, per side. The 4-notch test frame (1.8 / 1.8) fit but
    # needed to be a little wider and a little shorter, so: 1 mm wider, 1 mm shorter overall.
    window_clear_x: float = 2.3   # each side, left and right
    window_clear_y: float = 1.3   # top and bottom
    # (x, y) gaps on the window fit test, 1-3 notches; the middle one matches the shroud
    window_ladder: tuple = ((2.0, 1.6), (2.3, 1.3), (2.6, 1.0))
    shroud_tab_screw_d: float = 3.4  # M4 self-tapping into the carrier floor
    shroud_gap: float = 0.5       # air gap between pod faces and the back of the shroud face
    shroud_tab_slot: float = 16.0  # fore-aft slot in each shroud tab, follows the pod slots

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


def pod_zc(p):
    """Height of the pod face centre above the carrier floor (the bracket lifts the body)."""
    return p.pod_lift + p.pod_body_h / 2


def pod_top(p):
    return p.pod_lift + p.pod_body_h


def pod_x(p):
    pitch = p.pod_body_w + p.pod_gap
    return [-pitch, 0.0, pitch]


def row_w(p):
    return 3 * p.pod_body_w + 2 * p.pod_gap


def mount_points(p):
    """(name, x, z, slot axis) for each stock mounting bolt, on the wall."""
    ax, px = p.span_b / 2, -p.span_b / 2          # arm toward the fender (+X), pad toward the hood
    z4 = p.arm4_above_floor
    zpu = z4 + p.pad_above_arm_d
    return [("arm hole 1", ax, z4 + p.arm_hole_a, "x"),
            ("arm hole 4", ax, z4, "x"),
            ("pad upper", px, zpu, "z"),
            ("pad lower", px, zpu - p.pad_hole_h, "z")]


def wall_extent(p):
    """(x0, x1, z0, z1) of the mounting wall: covers the pod row and every slot plus a margin."""
    half = row_w(p) / 2 + p.wall_t
    x0, x1, top = -half, half, pod_top(p) + 10
    for (_, x, z, axis) in mount_points(p):
        hx = (p.arm_slot_len if axis == "x" else p.mount_hole_d) / 2
        hz = (p.pad_slot_len if axis == "z" else p.mount_hole_d) / 2
        x0, x1 = min(x0, x - hx - p.tab_margin), max(x1, x + hx + p.tab_margin)
        top = max(top, z + hz + p.tab_margin)
    return x0, x1, p.mount_wall_z0, top


def ears(p):
    """(x0, x1, z0, z1) of the two mounting tabs: one around the arm slots, one around the pad slots."""
    out = []
    for want in ("x", "z"):
        xs0, xs1, zs1 = [], [], []
        for (_, x, z, axis) in mount_points(p):
            if axis != want:
                continue
            hx = (p.arm_slot_len if axis == "x" else p.mount_hole_d) / 2
            hz = (p.pad_slot_len if axis == "z" else p.mount_hole_d) / 2
            xs0.append(x - hx - p.tab_margin)
            xs1.append(x + hx + p.tab_margin)
            zs1.append(z + hz + p.tab_margin)
        out.append((min(xs0), max(xs1), p.mount_wall_z0, max(zs1)))
    return out          # [arm tab, pad tab]


def ear_section(x0, x1, z0, z1, r=5.0):
    """Tab outline: rounded top corners, square bottom where it meets the floor."""
    top = rrect(x1 - x0, z1 - z0, r).translate([(x0 + x1) / 2, (z0 + z1) / 2])
    bottom = CS.square([x1 - x0, (z1 - z0) / 2]).translate([x0, z0])
    return top + bottom


def slot_y(w, length, axis, y0, y1, x, z):
    """Slot through a plate in the XZ plane, long along X or Z."""
    if axis == "x":
        s = CS.square([length - w, w], center=True)
    else:
        s = CS.square([w, length - w], center=True)
    s = s.offset(w / 2, m3d.JoinType.Round).translate([x, z])
    return plate_xz(s, y1, y1 - y0)


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
    arm_ear, pad_ear = ears(p)
    lip_x0, lip_x1 = sorted([pad_ear[1] + 2, arm_ear[0] - 14])   # stays clear of the pivot bolt under arm hole 4
    parts.append(box(lip_x0, lip_x1, y_back, y_back + p.wall_t, -p.floor_t - p.lip_h, 0))

    # locating ribs: two end cheeks plus two dividers
    for x in [-half + p.wall_t / 2, half - p.wall_t / 2]:
        # stop short of the wall so the mounting nuts have room
        parts.append(box(x - p.wall_t / 2, x + p.wall_t / 2,
                         -p.pod_depth - 2, y_front, 0, p.divider_h))
    for i in range(2):
        x = pod_x(p)[i] + (p.pod_body_w + p.pod_gap) / 2
        parts.append(box(x - p.wall_t / 2, x + p.wall_t / 2,
                         -p.pod_depth + 5, y_front, 0, p.divider_h))

    # mounting tabs behind the pods, one at the arm and one at the pad; the middle stays open
    for (x0, x1, z0, z1) in (arm_ear, pad_ear):
        parts.append(plate_xz(ear_section(x0, x1, z0, z1), y_back + p.mount_wall_t, p.mount_wall_t))
        # floor under the tab, wide enough that the side cheek sits fully on it
        parts.append(box(x0 - p.wall_t, x1 + p.wall_t, y_back, y_back + p.mount_wall_t + 22, -p.floor_t, 0))
    # side cheeks on the outboard edge of each tab: outside the pod row and clear of the nuts
    cheek_len = 20.0
    for (x0, x1, _, z1) in (arm_ear, pad_ear):
        tri = CS([[[0, 0], [cheek_len, 0], [0, z1 - 8]]])     # (Y offset, Z) profile
        xc = x1 - 1 if x1 > 0 else x0 - p.wall_t + 1          # outboard edge, 1 mm into the tab
        g = M.extrude(tri, p.wall_t).transform(
            [[0, 0, 1, xc],
             [1, 0, 0, y_back + p.mount_wall_t],
             [0, 1, 0, 0]])
        parts.append(g)

    # bosses under the floor for the shroud screws
    boss_z0 = -p.floor_t - p.lip_h
    for x in shroud_tab_x(p):
        parts.append(cyl_z(11, boss_z0, -p.floor_t + 0.01, x, y_front - 12))
    # standoffs down to the bezel's bottom wall for its two rear screws
    bez_in = -p.shroud_margin_bot - p.floor_t + p.shroud_t
    for x in bezel_rear_x(p):
        parts.append(cyl_z(11, bez_in, -p.floor_t + 0.01, x, p.bezel_rear_screw_y))

    body = M.batch_boolean(parts, m3d.OpType.Add)

    cuts = []
    for x in pod_x(p):
        # bracket bolt slot under each pod
        cuts.append(slot_z(p.pod_bolt_d, p.pod_slot_len, -p.floor_t - 1, 1, x, p.pod_bolt_y))
    for (_, hx, hz, axis) in mount_points(p):
        ln = p.arm_slot_len if axis == "x" else p.pad_slot_len
        cuts.append(slot_y(p.mount_hole_d, ln, axis, y_back - 1, y_back + p.mount_wall_t + 1, hx, hz))
    # shroud screw holes near the front edge of the floor, in the gaps between pods
    for x in shroud_tab_x(p):
        # blind pilot hole for an M4 self-tapping screw, stops 1.5 mm under the floor top
        cuts.append(cyl_z(p.shroud_tab_screw_d - 0.4, boss_z0 - 1, -1.5, x, y_front - 12))

    for x in bezel_rear_x(p):
        cuts.append(cyl_z(p.shroud_tab_screw_d - 0.4, bez_in - 1, -1.5, x, p.bezel_rear_screw_y))
    # splice holes: countersunk from the top of the floor so the pods sit flat
    for (hx, hy) in splice_floor_holes(p):
        cuts.append(cyl_z(p.splice_screw_d, -p.floor_t - 1, 1, hx, hy))
        cuts.append(M.cylinder(2.3, p.splice_screw_d / 2, 4.2).translate([hx, hy, -2.3 + 0.001]))
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
    bar = pitch(p) - (p.pod_face_w + 2 * p.window_clear_x)     # material between windows
    z_bot = -p.shroud_margin_bot - p.floor_t + p.shroud_t + 0.5
    win_bot = pod_zc(p) - (p.pod_face_h / 2 + p.window_clear_y)
    strip = box(sx - bar / 2 + 0.6, sx + bar / 2 - 0.6, 0, 2.5, z_bot, win_bot + p.pod_face_h)
    foot = box(sx - 22, sx + 22, 0, 2.5, z_bot, win_bot - 0.5)
    return (strip + foot).rotate([-90, 0, 0]).translate([-sx, 0, 0])


def pitch(p):
    return p.pod_body_w + p.pod_gap


def split_x(p):
    return pitch(p) / 2


def bezel_rear_x(p):
    return [-pitch(p) / 2, pitch(p) / 2]


def shroud_tab_x(p):
    return [-pitch(p) / 2, pitch(p) + 14]


def splice_floor_holes(p):
    sx = split_x(p)
    return [(sx + dx, y) for dx in (-16, 16) for y in (-20, p.mount_wall_y + 16)]


def splice_wall_holes(p):
    sx = split_x(p)
    return [(sx + dx, z) for dx in (-16, 16) for z in (6, 44)]


def shroud(p):
    ow = p.opening_w - 2 * p.opening_side_clear
    z_bot = -p.shroud_margin_bot - p.floor_t
    z_top = pod_top(p) + p.shroud_margin_top
    oh = z_top - z_bot
    zc = (z_top + z_bot) / 2
    y_face = p.shroud_t + p.shroud_gap     # front of the shroud face

    # face and return lip as one shell: a solid slab with the back pocketed out
    outer = rrect(ow, oh, p.shroud_r).translate([0, zc])
    inner = rrect(ow - 2 * p.shroud_t, oh - 2 * p.shroud_t,
                  max(p.shroud_r - p.shroud_t, 1)).translate([0, zc])
    shell = plate_xz(outer, y_face, p.shroud_t + p.shroud_return)
    shell = shell - plate_xz(inner, y_face - p.shroud_t, p.shroud_return + 1)

    # windows for the pod bezels, centred on each pod face
    win_w = p.pod_face_w + 2 * p.window_clear_x
    win_h = p.pod_face_h + 2 * p.window_clear_y
    wins = [plate_xz(rrect(win_w, win_h, p.pod_face_r + min(p.window_clear_x, p.window_clear_y))
                     .translate([x, pod_zc(p)]), y_face + 1, p.shroud_t + 2)
            for x in pod_x(p)]

    # tabs that reach back under the carrier floor for two M4 screws
    tabs = []
    tab_y0 = -p.floor_front_setback - 20
    for x in shroud_tab_x(p):
        ys = -p.floor_front_setback - 12                    # screw position with the bezel all the way back
        t = box(x - 9, x + 9, ys - p.bezel_travel - 7, y_face - p.shroud_t + 1,
                -p.floor_t - p.lip_h - 3, -p.floor_t - p.lip_h)
        # forward-only slot: as the bezel slides forward, the screw moves back along the slot
        t = t - slot_z(p.shroud_tab_screw_d + 0.6, p.bezel_travel + p.shroud_tab_screw_d + 0.6,
                       -40, 0, x, ys - p.bezel_travel / 2)
        tabs.append(t)
    # the tabs run 1 mm into the back of the face, which ties them on
    body = M.batch_boolean([shell] + tabs, m3d.OpType.Add)
    cuts = list(wins)
    # shallow recess along the top for a strip of foam weatherstrip
    cuts.append(box(-ow / 2 + 20, ow / 2 - 20,
                    p.foam_channel_y - p.foam_channel_w / 2, p.foam_channel_y + p.foam_channel_w / 2,
                    z_top - p.foam_channel_d, z_top + 1))
    # rear screw holes in the bottom wall
    for x in bezel_rear_x(p):
        cuts.append(slot_z(p.shroud_tab_screw_d + 0.6, p.bezel_travel + p.shroud_tab_screw_d + 0.6,
                           z_bot - 1, z_bot + p.shroud_t + 1, x, p.bezel_rear_screw_y - p.bezel_travel / 2))
    return M.batch_boolean([body] + cuts, m3d.OpType.Subtract)


def fit_test(p):
    """Quick print: separate window frames with different gaps around the pod bezel.
    The number of notches on each frame's top edge is its position in window_ladder."""
    cells = []
    mx = max(c for c, _ in p.window_ladder)
    my = max(c for _, c in p.window_ladder)
    cw, ch = p.pod_face_w + 2 * mx + 16, p.pod_face_h + 2 * my + 16
    for n, (cx_, cy_) in enumerate(p.window_ladder):
        ww, wh = p.pod_face_w + 2 * cx_, p.pod_face_h + 2 * cy_
        cell = rrect(cw, ch, 6) - rrect(ww, wh, p.pod_face_r + min(cx_, cy_))
        for k in range(n + 1):
            cell = cell - CS.square([3, 4]).translate([-cw / 2 + 6 + k * 6, ch / 2 - 3])
        cells.append(cell.translate([0, n * (ch + 8)]))   # stacked 8 mm apart: separate pieces
    return M.extrude(CS.batch_boolean(cells, m3d.OpType.Add), 2.0)


def fit_test_mount(p):
    """Quick print: the two mounting tabs as flat 3 mm pieces, laid side by side.
    Checks the slots line up with the arm (A) and the pad (H) without anything in between."""
    pieces = []
    for (x0, x1, z0, z1) in ears(p):
        sec = ear_section(x0, x1, z0, z1)
        for (_, x, z, axis) in mount_points(p):
            ln = p.arm_slot_len if axis == "x" else p.pad_slot_len
            w = p.mount_hole_d
            sl = CS.square([ln - w, w] if axis == "x" else [w, ln - w], center=True)
            sec = sec - sl.offset(w / 2, m3d.JoinType.Round).translate([x, z])
        pieces.append(sec)
    arm, pad = pieces
    # move the pad piece next to the arm piece
    ab, pb = arm.bounds(), pad.bounds()
    pad = pad.translate([ab[0] - 10 - pb[2], 0])
    return M.extrude(arm + pad, 3.0)


def spacers(p):
    """M6 spacer washers, 4 each of 2, 4 and 6 mm, to shim the gap if the arm and pad
    faces don't sit at the same depth (measurement C)."""
    parts = []
    for row, t in enumerate((2.0, 4.0, 6.0)):
        for col in range(4):
            w = M.cylinder(t, 9) - M.cylinder(t + 2, p.mount_hole_d / 2).translate([0, 0, -1])
            parts.append(w.translate([col * 22, row * 22, 0]))
    return M.batch_boolean(parts, m3d.OpType.Add)


def pod_dummy(p, dy=0.0):
    """Stand-in pod from the maker's drawing: body, bezel, bracket foot and stud.
    dy slides the pods fore-aft (for the clearance checks)."""
    pods = []
    for x in pod_x(p):
        face = plate_xz(rrect(p.pod_face_w, p.pod_face_h, p.pod_face_r)
                        .translate([x, pod_zc(p)]), 0, 8)
        body = box(x - p.pod_body_w / 2, x + p.pod_body_w / 2, -p.pod_depth, -8,
                   p.pod_lift, pod_top(p))
        ys = p.pod_bolt_nominal_y
        foot = box(x - p.pod_bracket_w / 2, x + p.pod_bracket_w / 2,
                   ys - p.pod_bracket_d / 2, ys + p.pod_bracket_d / 2, 0.01, p.pod_lift + 1)
        stud = cyl_z(p.pod_stud_d, -p.floor_t - 12, 0.02, x, ys)
        pods += [face, body, foot, stud]
    return M.batch_boolean(pods, m3d.OpType.Add).translate([0, dy, 0])


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
    fig.suptitle("C5 sleepy-eye pod carrier (blue), shroud (black), pods (gold) - passenger side")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print("preview ->", out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "stl")
    sd = os.path.join(out, "split")
    os.makedirs(sd, exist_ok=True)
    os.makedirs(os.path.join(here, "preview"), exist_ok=True)
    c, s = carrier(P), shroud(P)
    # modelled part is the passenger side; the driver side is its mirror image
    sides = [("passenger", c, s, 1), ("driver", mirror_x(c), mirror_x(s), -1)]
    for side, cc, ss, _ in sides:
        save(print_orient_carrier(cc), os.path.join(out, f"carrier_{side}.stl"))
        save(print_orient_shroud(ss), os.path.join(out, f"bezel_{side}.stl"))
    save(fit_test(P), os.path.join(out, "fit_test_window.stl"))
    save(fit_test_mount(P), os.path.join(out, "fit_test_mount_passenger.stl"))
    save(mirror_x(fit_test_mount(P)), os.path.join(out, "fit_test_mount_driver.stl"))
    save(spacers(P), os.path.join(out, "spacer_washers.stl"))

    # split versions for small beds
    for side, cc, ss, sgn in sides:
        a, b = cc.split_by_plane([sgn, 0, 0], split_x(P))
        save(print_orient_carrier(b), os.path.join(sd, f"carrier_{side}_A.stl"))
        save(print_orient_carrier(a), os.path.join(sd, f"carrier_{side}_B.stl"))
        a, b = ss.split_by_plane([sgn, 0, 0], split_x(P))
        save(print_orient_shroud(b), os.path.join(sd, f"bezel_{side}_A.stl"))
        save(print_orient_shroud(a), os.path.join(sd, f"bezel_{side}_B.stl"))
    fp, _ = splice_plates(P)
    save(fp, os.path.join(sd, "splice_floor_x2.stl"))
    save(shroud_splice(P), os.path.join(sd, "bezel_splice_x2.stl"))
    preview(P, os.path.join(here, "preview", "assembly.png"))
