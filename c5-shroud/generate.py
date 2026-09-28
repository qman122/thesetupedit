"""Parametric C5 Corvette sleepy-eye pod carrier and shroud (1997-2004 pop-up headlights).

Holds three 2.9 x 1.8 in dual-lens LED pods per side in place of the stock
headlight unit, the same way the KnightDriveTV kit does: one carrier per side that
bolts to the stock headlight mounting points, plus a front bezel styled after the
KnightDriveTV TripLED bezel.

Run:  python3 generate.py            -> writes STL files to ./stl and previews to ./preview
All sizes are millimetres. Change the numbers in PARAMS and re-run.

Axes (passenger-side part as modelled): X across the car (+X toward the fender),
Y fore-aft (+Y toward the front of the car), Z up. Pod faces sit at Y = 0 and
the top of the carrier floor is Z = 0. The driver part is a mirror copy.
Seen from in front of the car, the driver-side fender arm is on the right and the
aiming pad on the left.
"""

import math
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
    # The row follows the slope of the headlight opening: every pod faces straight ahead, and
    # each one is stepped back from its neighbour toward the fender (a staircase, like the
    # KnightDriveTV bracket). pod_arc_deg can also turn the outer pods; 0 keeps them parallel.
    pod_step: float = 12.0        # each pod sits this far behind the one on its hood side
    pod_arc_deg: float = 0.0
    pod_bolt_d: float = 8.6       # slot width for the bracket stud (about 8 mm / 5/16 in)
    pod_stud_d: float = 8.0       # stud diameter, from the drawing
    nut_channel: float = 13.4     # rails under each slot, this far apart: an M8 (13 mm) or 5/16 in (1/2 in) nut slides but can't turn
    nut_rail_w: float = 3.0
    nut_rail_h: float = 4.0
    pod_bolt_y: float = -31.5     # slot centre, measured back from the pod face
    pod_slot_len: float = 34.6    # fore-aft adjustment: 16 mm forward (bezel follows), 10 mm back
    pod_bolt_nominal_y: float = -34.5  # stud position in the default spot (1.36 in behind the face)

    # --- carrier ---
    floor_t: float = 5.0          # floor thickness
    cup_wall: float = 3.0         # walls of the pocket each pod's bracket foot sits in
    cup_h: float = 3.5            # pocket depth (stays under the bezel's window cells)
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

    # --- bezel: the outside shape of the stock C5 bezel (GM 10435411/12), which the
    # KnightDriveTV TripLED bezel copies, with a tunnel back to each pod ---
    # Like the stock one, its flat top blade slides in under the front of the headlight cover and
    # a forked tab on the blade slides onto the clip under the cover. A wing (ear) at each end
    # screws to the carrier. It is taller at the hood end than at the fender end.
    shroud_t: float = 3.0         # thinnest wall (at the shallow side of each tunnel)
    shroud_margin_top: float = 8.0   # bezel top (the cover's underside) above the pod tops (ESTIMATE)
    bezel_h_hood: float = 100.0   # front height at the hood end, top of the blade to the bottom of the lip (ESTIMATE)
    bezel_h_fender: float = 78.0  # front height at the fender end; the lip rises toward the fender (ESTIMATE)
    bezel_travel: float = 16.0    # the bezel's screw slots let it slide this far forward of the pods (never back)
    # KnightDriveTV-style open frame: a floor shelf just under the pods, and a thin round post
    # with flared ends in front of each gap between pods, set back from the front edge
    post_d: float = 9.0           # post width across the car
    post_len: float = 13.0        # post length front to back (slightly elongated, like theirs)
    post_root_w: float = 9.0      # posts flare mostly at the bottom, spreading into the floor like roots
    post_root_h: float = 22.0
    post_cap_w: float = 1.5       # ...and only a little where they meet the blade
    post_cap_h: float = 3.0
    shadow_line: float = 1.5      # groove along the underside of the blade at the top of the slot
    post_recess: float = 5.0      # posts sit this far behind the front edge
    pod_recess: float = 14.0      # the pods sit this much deeper in the mouth (lenses back in the shadow)
    mouth_r: float = 16.0         # corner radius of the slot at the back (25 mm at the front edge): near-round ends like the reference scan
    mouth_flare: float = 4.0      # the opening widens this much at the front edge along the bottom
    mouth_wrap: float = 9.0       # ...and this much at the ends, so the ends curve round instead of a flat side
    front_bow: float = 6.0        # the face bows forward this much in the middle, following the nose
    face_t: float = 3.0           # the face is a shell this thick, with the slot cut through it
    top_corner_r: float = 10.0    # outline corners at the top, under the door
    mouth_wall: float = 3.0       # the slot's walls, from the face back to the pods
    mask_t: float = 1.5           # black mask just in front of each pod: only the lenses show through
    mask_hole_r: float = 16.5     # (lens radius 16 plus 0.5)
    shelf_t: float = 3.0
    rail_t: float = 4.0           # top blade thickness; its front edge is rounded
    blade_depth: float = 30.0     # flat top blade, from the front edge back (slides under the cover)
    fork_len: float = 25.0        # forked tab behind the blade: slides onto the clip under the cover
    fork_w: float = 26.0
    fork_slot: float = 5.0
    fork_t: float = 2.5
    fork_x: float = 0.0           # fork centre, across the car from the middle of the bezel
    lip_ext: float = 6.0          # the face's lower edge sits this far forward of its top edge
    rim_r: float = 3.0            # the rolled rim round the slot is a tube this radius (6 mm lip)
    corner_r: float = 28.0        # bottom corners of the outline, sweeping up into the sides
    end_wall_x: float = 123.0     # end walls of the frame start this far out (just past the outer pods)
    wing_t: float = 3.0           # side wings (ears)
    wing_screw_y: float = -54.0   # M4 screw through each wing into a boss on the carrier
    wing_screw_z: float = 4.0
    # The wings are full side walls like the stock ears: they run back past the pods to
    # just in front of the arm and the pad, and down over the carrier.
    wing_back_y: float = -90.0    # rear edge of the wings (the arm and pad faces are at -95)
    wing_back_z: float = -20.0    # bottom of the wings at their rear edge (under the carrier's tabs)
    wing_r: float = 10.0          # rounded rear corners
    access_hole_d: float = 28.0   # hood-end wing: hole to reach the aiming adjuster, like the stock ear
    access_hole_yz: tuple = (-72.0, 38.0)
    # Window gap around the pod bezel, per side, at the back of each tunnel (the 1-notch test frame fit)
    window_clear_x: float = 2.0   # each side, left and right (the 1-notch test frame fit)
    window_clear_y: float = 1.6   # top and bottom
    # (x, y) gaps on the window fit test, 1-3 notches; the first one matches the bezel
    window_ladder: tuple = ((2.0, 1.6), (2.3, 1.3), (2.6, 1.0))
    shroud_tab_screw_d: float = 3.4  # M4 self-tapping into the carrier floor
    shroud_gap: float = 0.5       # air gap between pod faces and the back of the shroud face
    shroud_tab_slot: float = 16.0  # fore-aft slot in each shroud tab, follows the pod slots


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


def pod_poses(p):
    """(x, y, yaw in degrees) of each pod's face centre, left to right. Adjacent pod centres
    are one pitch apart along an arc, so the outer pods sit back and turn outward."""
    a = math.radians(p.pod_arc_deg)
    if a == 0:
        base = [(k * pitch(p), 0.0, 0.0) for k in (-1, 0, 1)]
    else:
        r = pitch(p) / (2 * math.sin(a / 2))
        base = [(r * math.sin(k * a), -r * (1 - math.cos(k * a)), -k * p.pod_arc_deg) for k in (-1, 0, 1)]
    # step each pod back toward the fender (+X): the hood-side pod stays put, the middle one
    # sits one step back and the fender-side one two steps back
    return [(x, y - (k + 1) * p.pod_step, yaw) for k, (x, y, yaw) in zip((-1, 0, 1), base)]


def at_pose(man, pose):
    x, y, yaw = pose
    return man.rotate([0, 0, yaw]).translate([x, y, 0])


def pose_pt(pose, lx, ly, dy=0.0):
    x, y, yaw = pose
    c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return [x + lx * c - ly * s_, y + lx * s_ + ly * c + dy]


def pod_x(p):
    return [x for (x, _, _) in pod_poses(p)]

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

    arm_ear, pad_ear = ears(p)
    # A beam under the pods with a pocket for each pod's bracket foot. The pockets follow the
    # curve of the row, and each is long enough for its pod to slide straight fore and aft.
    half_slot = (p.pod_slot_len - p.pod_bolt_d) / 2
    fwd = (p.pod_bolt_y + half_slot) - p.pod_bolt_nominal_y
    back = p.pod_bolt_nominal_y - (p.pod_bolt_y - half_slot)
    cup_w = p.pod_bracket_w + 1.5
    ly0 = p.pod_bolt_nominal_y - p.pod_bracket_d / 2 - 0.75
    ly1 = p.pod_bolt_nominal_y + p.pod_bracket_d / 2 + 0.75

    def swept(pose, grow):
        pts = []
        for dy in (-back, fwd):
            for lx in (-cup_w / 2 - grow, cup_w / 2 + grow):
                for ly in (ly0 - grow, ly1 + grow):
                    pts.append(pose_pt(pose, lx, ly, dy))
        return pts

    poses = pod_poses(p)
    feet = [CS.hull_points(swept(pose, p.cup_wall)) for pose in poses]
    # spine: joins the pockets across the band of depth they all share, like a stepped bracket
    ys_lo = max(min(q[1] for q in swept(pose, p.cup_wall)) for pose in poses)
    ys_hi = min(max(q[1] for q in swept(pose, p.cup_wall)) for pose in poses)
    xs_all = [q[0] for pose in poses for q in swept(pose, p.cup_wall)]
    spine = CS.square([max(xs_all) - min(xs_all), ys_hi - ys_lo]).translate([min(xs_all), ys_lo])
    beam = CS.batch_boolean(feet + [spine], m3d.OpType.Add).offset(1.0, m3d.JoinType.Round)
    parts.append(M.extrude(beam, p.floor_t).translate([0, 0, -p.floor_t]))
    # stiffening rib round the beam's edge, kept away from the ends (the arm's pivot bolt)
    ring = (beam.offset(-0.3, m3d.JoinType.Miter) - beam.offset(-p.wall_t - 0.3, m3d.JoinType.Miter)) ^ CS.square([170, 400], center=True)
    parts.append(M.extrude(ring, p.lip_h + 1).translate([0, 0, -p.floor_t - p.lip_h]))   # 1 mm into the floor
    for pose in poses:
        cup = CS.hull_points(swept(pose, p.cup_wall)) - CS.hull_points(swept(pose, 0))
        parts.append(M.extrude(cup, p.cup_h + 1).translate([0, 0, -1]))   # 1 mm into the floor
    # knees: an angled plate from each end of the beam back to its mounting tab
    for (x0, x1, _, _) in (arm_ear, pad_ear):
        pose = poses[2] if x0 > 0 else poses[0]           # the end pod on this tab's side
        tx0, tx1 = x0 - p.wall_t, x1 + p.wall_t
        ty1 = y_back + p.mount_wall_t + 22
        knee = CS.hull_points(swept(pose, p.cup_wall) +
                              [[tx0, y_back], [tx1, y_back], [tx0, ty1], [tx1, ty1]]).offset(0.6, m3d.JoinType.Round)
        parts.append(M.extrude(knee, p.floor_t).translate([0, 0, -p.floor_t]))

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
    for (x, y) in shroud_tabs(p):
        parts.append(cyl_z(11, boss_z0, -p.floor_t + 0.01, x, y))
    # bosses for the screws through the bezel's side wings, outboard of the pods
    for (xa, xb) in wing_boss_x(p):
        parts.append(box(xa, xb, -89, p.wing_screw_y + 7, -p.floor_t, 0))           # ties into the tab floor
        xa2, xb2 = (row_w(p) / 2 + 1.25, xb) if xb > 0 else (xa, -row_w(p) / 2 - 1.25)
        parts.append(box(xa2, xb2, p.wing_screw_y - 7, p.wing_screw_y + 7, -p.floor_t, p.wing_screw_z + 8))

    # nut channel under each pod slot (from the owner's bracket sketch): two rails hold the
    # pod's nut so it can slide with the stud but can't turn, so each pod bolts on from above
    ax4, z4 = [(x, z) for (n, x, z, _) in mount_points(p) if n == "arm hole 4"][0]
    pivot_keepout = box(ax4 - 21, ax4 + 21, y_back - 6, y_back + p.mount_wall_t + 31, z4 - 46, z4 - 19)
    for pose in pod_poses(p):
        sx_, sy_ = pose_pt(pose, 0, p.pod_bolt_nominal_y)
        ln = fwd + back + p.pod_bolt_d + 12
        yc = sy_ + (fwd - back) / 2
        for side in (-1, 1):
            xr = sx_ + side * (p.nut_channel / 2 + p.nut_rail_w / 2)
            rail = box(xr - p.nut_rail_w / 2, xr + p.nut_rail_w / 2, yc - ln / 2, yc + ln / 2,
                       -p.floor_t - p.nut_rail_h, -p.floor_t + 0.5)
            parts.append(rail - pivot_keepout)          # stays clear of the arm's pivot bolt

    body = M.batch_boolean(parts, m3d.OpType.Add)

    cuts = []
    for pose in pod_poses(p):
        # stud slot under each pod, straight fore and aft
        sx_, sy_ = pose_pt(pose, 0, p.pod_bolt_nominal_y)
        cuts.append(slot_z(p.pod_bolt_d, fwd + back + p.pod_bolt_d, -p.floor_t - 1, 1, sx_,
                           sy_ + (fwd - back) / 2))
    for (_, hx, hz, axis) in mount_points(p):
        ln = p.arm_slot_len if axis == "x" else p.pad_slot_len
        cuts.append(slot_y(p.mount_hole_d, ln, axis, y_back - 1, y_back + p.mount_wall_t + 1, hx, hz))
    # shroud screw holes near the front edge of the floor, in the gaps between pods
    for (x, y) in shroud_tabs(p):
        # blind pilot hole for an M4 self-tapping screw, stops 1.5 mm under the floor top
        cuts.append(cyl_z(p.shroud_tab_screw_d - 0.4, boss_z0 - 1, -1.5, x, y))

    for (xa, xb) in wing_boss_x(p):
        xw = xb if xb > 0 else xa
        x0, x1 = (xw - 7, xw + 1) if xb > 0 else (xw - 1, xw + 7)
        cuts.append(cyl_x(p.shroud_tab_screw_d - 0.4, x0, x1, p.wing_screw_y, p.wing_screw_z))
    return M.batch_boolean([body] + cuts, m3d.OpType.Subtract)


def pitch(p):
    return p.pod_body_w + p.pod_gap


def wing_boss_x(p):
    """(x0, x1) of the lower plate under each wing screw boss; x1 (or x0) stops just inside the wing."""
    xw = p.opening_w / 2 - p.opening_side_clear - p.wing_t - 0.3
    return [(row_w(p) / 2 - 4, xw), (-xw, -row_w(p) / 2 + 4)]


def shroud_tabs(p):
    """(x, y) of the two front bezel screws: beside each outer pod's stud (toward the middle),
    under that pod's own pocket and clear of the steps in the bezel face."""
    out = []
    for pose, side in ((pod_poses(p)[0], 1), (pod_poses(p)[2], -1)):
        x, y = pose_pt(pose, side * 18, -p.floor_front_setback - 12)
        out.append((x, y))
    return out


def front_line(p):
    """The bezel front seen from above, y = c0 + s * x. It follows the pods' step and sits
    pod_recess further forward than the closest it could be to the pod faces."""
    poses = pod_poses(p)
    s = (poses[-1][1] - poses[0][1]) / (poses[-1][0] - poses[0][0])
    half = p.pod_face_w / 2 + p.window_clear_x
    c0 = max(y + p.shroud_gap + p.shroud_t - s * (x + dx) for (x, y, _) in poses for dx in (-half, half))
    return s, c0 + p.pod_recess


def post_xy(p):
    """(x, y, y_min) of the posts: one in front of each gap between neighbouring pods,
    post_recess behind the front edge; y_min is the face of the forward pod plus a gap."""
    poses = pod_poses(p)
    s, c0 = front_line(p)
    out = []
    for a, b in zip(poses, poses[1:]):
        x = (a[0] + b[0]) / 2
        y_min = max(a[1], b[1]) + p.shroud_gap + 0.3
        y = max(c0 + s * x - p.post_recess - p.post_len / 2, y_min + 0.5 + p.post_len / 2)
        out.append((x, y, y_min))
    return out


def front_frame(p):
    """Transform from the front's own frame (u along the front, n forward, z up) to the model."""
    s, c0 = front_line(p)
    k = 1 / math.hypot(1, s)
    return [[k, -s * k, 0, 0], [s * k, k, 0, c0], [0, 0, 1, 0]]


def ball_pts(u, n, z, r):
    return np.asarray(M.sphere(r, 24).translate([u, n, z]).to_mesh().vert_properties)[:, :3].tolist()


def cyl_x(d, x0, x1, y, z):
    """Cylinder along X from x0 to x1."""
    return M.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])


def bezel_z(p):
    """(top, bottom at the hood end, bottom at the fender end) of the bezel front."""
    z_top = pod_top(p) + p.shroud_margin_top
    return z_top, z_top - p.bezel_h_hood, z_top - p.bezel_h_fender


def tube(path, r, n0, segs=20):
    """A closed-ended tube of radius r along a polyline of (u, z) points, centred at n = n0
    (front frame coordinates), built directly as a mesh so it is one clean solid."""
    path = np.asarray(path, float)
    verts, tris = [], []
    k = len(path)
    for i in range(k):
        a, b = path[max(i - 1, 0)], path[min(i + 1, k - 1)]
        tu, tz = (b - a) / np.linalg.norm(b - a)
        nu, nz = -tz, tu                            # in-plane normal
        for j in range(segs):
            ang = 2 * math.pi * j / segs
            c, s_ = math.cos(ang), math.sin(ang)
            verts.append([path[i][0] + r * c * nu, n0 + r * s_, path[i][1] + r * c * nz])
    for i in range(k - 1):
        for j in range(segs):
            a0, a1 = i * segs + j, i * segs + (j + 1) % segs
            b0, b1 = a0 + segs, a1 + segs
            tris += [[a0, b0, b1], [a0, b1, a1]]
    for end, ring in ((0, 0), (1, k - 1)):          # end caps
        verts.append(list(np.mean(np.asarray(verts[ring * segs:(ring + 1) * segs]), 0)))
        cidx = len(verts) - 1
        for j in range(segs):
            a0, a1 = ring * segs + j, ring * segs + (j + 1) % segs
            tris.append([cidx, a0, a1] if end == 0 else [cidx, a1, a0])
    mesh = m3d.Mesh(np.asarray(verts, np.float32), np.asarray(tris, np.uint32))
    man = M(mesh)
    return man if man.volume() > 0 else M(m3d.Mesh(np.asarray(verts, np.float32), np.asarray(tris, np.uint32)[:, ::-1].copy()))


def shroud(p):
    """The bezel, built like KnightDriveTV's: a curved face that fills the pocket under the door,
    with a letterbox slot cut through it and a rolled rim round the slot. The face's outline
    follows the stock C5 bezel and the door: big rounded lower corners, taller at the hood end.
    Inside the slot the pods sit back in shadow behind a black mask with holes for the lenses
    only, and thin posts that spread into the floor like roots. The flat top blade slides in under
    the front of the headlight cover with a forked tab onto its clip, like the stock bezel, and a
    wing (ear) at each end screws to the carrier."""
    ow = p.opening_w - 2 * p.opening_side_clear
    z_top, zb_hood, zb_fender = bezel_z(p)
    s, c0 = front_line(p)
    F = front_frame(p)
    kx = F[0][0]                                    # cos of the sweep angle
    U = ow / 2 / kx                                 # the ends, measured along the front
    poses = pod_poses(p)
    f_bot = pod_zc(p) - p.pod_face_h / 2 - 1.2      # bottom of the slot, just under the pod faces
    f_top = z_top - p.rail_t                        # top of the slot: the underside of the blade
    dm = p.pod_recess + p.shroud_t                  # depth of the slot, front to the nearest pod face
    zmin = min(zb_hood, zb_fender)

    def yf(x):
        return c0 + s * x

    def zb(u):                                      # bottom of the face; the hood end is -u
        t = min(max((u + U) / (2 * U), 0.0), 1.0)
        return zb_hood + t * (zb_fender - zb_hood)

    def bulge(u, z):                                # how far the curved face sits in front of the flat front line
        return p.front_bow * (1 - (u / U) ** 2) + p.lip_ext * (z_top - z) / (z_top - zmin)

    def warp(man, edge=4.0):
        """Bend a part built against the flat front onto the curved face."""
        def f(v):
            out = v.copy()
            out[:, 1] += p.front_bow * (1 - np.clip(v[:, 0] / U, -1, 1) ** 2) + \
                p.lip_ext * (z_top - v[:, 2]) / (z_top - zmin)
            return out
        return man.refine_to_length(edge).warp_batch(f)

    parts = []
    # --- the face: a shell with the door-shaped outline, bent to the nose ---
    ctr = [(-U + p.top_corner_r, z_top - p.top_corner_r, p.top_corner_r),
           (U - p.top_corner_r, z_top - p.top_corner_r, p.top_corner_r),
           (-U + p.corner_r, zb(-U) + p.corner_r, p.corner_r),
           (U - p.corner_r, zb(U) + p.corner_r, p.corner_r)]
    outline = CS.hull_points([[cu + rr * math.cos(a / 24 * math.pi), cz + rr * math.sin(a / 24 * math.pi)]
                              for (cu, cz, rr) in ctr for a in range(48)])
    face = plate_xz(outline, 0, p.face_t)            # n from -face_t to 0
    # the slot's walls: a shell lofted from the face back to the pods, easing in on a curve
    uo = (p.end_wall_x - 0.4) / kx
    ztop = f_top - 0.29                             # (clear of the blade nose's lowest facets)

    def slot_secs(grow, n_front, n_back):
        out = []
        for i in range(13):
            t = i / 12
            e = (1 - t) ** 2
            half = uo + p.mouth_wrap * e + grow
            zlo = f_bot - p.mouth_flare * e - grow
            rad = p.mouth_r + p.mouth_wrap * e + grow
            zt = ztop - 0.03 * i + (grow and 0.6)     # the outer shell tucks up into the blade
            out.append(plate_xz(rrect(2 * half, zt - zlo, rad).translate([0, (zt + zlo) / 2]),
                                n_front - t * (n_front - n_back), 0.2))
        return [M.batch_hull([a_, b_]) for a_, b_ in zip(out, out[1:])]
    walls = slot_secs(p.mouth_wall, -1.0, -dm)
    parts.append(warp(M.batch_boolean([face] + walls, m3d.OpType.Add)).transform(F))

    # floor shelf under the slot, from the slot walls back to just in front of each pod's face
    xs = [x for (x, _, _) in poses]
    mids = [(xs[0] + xs[1]) / 2, (xs[1] + xs[2]) / 2]
    cols = [(-ow / 2 - 0.5, mids[0]), (mids[0] - 2, mids[1]), (mids[1] - 2, ow / 2 + 0.5)]   # ends trimmed below
    plan = CS.batch_boolean([CS([[[xa, y + p.shroud_gap], [xb, y + p.shroud_gap], [xb, yf(xb) - dm + 3], [xa, yf(xa) - dm + 3]]])
                             for (xa, xb), (_, y, _) in zip(cols, poses)], m3d.OpType.Add)
    parts.append(M.extrude(plan.simplify(0.01), p.shelf_t + 0.13).translate([0, 0, f_bot - p.shelf_t - 0.13]))
    # end walls of the cavity: from the slot walls back to the outer pods' faces
    for (xa, xb), (_, y, _) in (((-ow / 2 - 0.5, -p.end_wall_x), poses[0]), ((p.end_wall_x, ow / 2 + 0.5), poses[2])):
        sec = CS([[[xa, y + p.shroud_gap], [xb, y + p.shroud_gap], [xb, yf(xb) - 1], [xa, yf(xa) - 1]]])
        parts.append(M.extrude(sec, z_top - 0.5 - (f_bot - p.shelf_t - 0.37)).translate([0, 0, f_bot - p.shelf_t - 0.37]))
    # black mask just in front of each pod: a plate with holes for the two lenses only
    for (x, y, _) in poses:
        plate = rrect(p.pod_face_w + p.pod_gap + 1.0, f_top - f_bot + 1.0, 1.0).translate([0, (f_top + f_bot) / 2])
        for lx in (-18.5, 18.5):
            plate = plate - CS.circle(p.mask_hole_r, 64).translate([lx, pod_zc(p)])
        parts.append(plate_xz(plate, y + p.shroud_gap + p.mask_t, p.mask_t).translate([x, 0, 0]))
    # where the pods step back, a thin wall joins one mask to the next so no pod shows between them
    for a, b in zip(poses, poses[1:]):
        xm = (a[0] + b[0]) / 2
        y0, y1 = min(a[1], b[1]) + p.shroud_gap + 0.3, max(a[1], b[1]) + p.shroud_gap + p.mask_t - 0.3
        parts.append(box(xm - p.mask_t / 2, xm + p.mask_t / 2, y0, y1, f_bot - 0.37, f_top + 0.21))

    # top blade: thin and continuous, slides in under the front of the headlight cover
    rt = p.rail_t / 2
    blade = [box(-U, U, -p.blade_depth, -0.5, z_top - p.rail_t, z_top),
             M.hull_points(ball_pts(-U + rt + 0.2, 0.37, z_top - rt - 0.13, rt) +
                           ball_pts(U - rt - 0.2, 0.37, z_top - rt - 0.13, rt))]
    uf = p.fork_x / kx
    blade.append(box(uf - p.fork_w / 2, uf + p.fork_w / 2, -p.blade_depth - p.fork_len, -p.blade_depth + 1,
                     z_top - p.fork_t, z_top))
    parts.append(warp(M.batch_boolean(blade, m3d.OpType.Add)).transform(F))

    # side wings (ears): full side walls from the face back past the pods to just in front of
    # the arm and the pad
    wy, wz, wr_ = p.wing_screw_y, p.wing_screw_z, p.wing_r
    for side in (1, -1):
        xo, xi = side * (ow / 2 + 0.5), side * (ow / 2 - p.wing_t)      # outer face trimmed below
        yfr = min(yf(xo), yf(xi)) - 0.71
        ze = zb(side * U) + p.corner_r * 0.6        # where the rounded bottom corner meets the side
        yb_, zbk = p.wing_back_y + wr_, p.wing_back_z + wr_
        corners = [[yb_ + wr_ * math.cos(a / 8 * math.pi), zc_ + wr_ * math.sin(a / 8 * math.pi)]
                   for zc_ in (z_top - wr_, zbk) for a in range(16)]
        prof = CS.hull_points([[yfr + bulge(side * U, ze) - 1.0, ze], [yfr, z_top], [yfr - 20, z_top]] +
                              [q for q in corners if q[1] <= z_top])
        x0 = min(xo, xi)
        parts.append(M.extrude(prof, p.wing_t + 0.5).transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]]))

    # front tabs reaching back under the carrier floor for two M4 screws (forward-only slots)
    zt_ = -p.floor_t - p.lip_h
    for (x, ys), pose in zip(shroud_tabs(p), (poses[0], poses[2])):
        yface = yf(x) + bulge(x / kx, zt_) - p.face_t + 1.0
        parts.append(box(x - 9, x + 9, ys - p.bezel_travel - 7, yface, zt_ - 3, zt_))
    body = M.batch_boolean(parts, m3d.OpType.Add)

    cuts = []
    # the slot itself, and a shadow line along the underside of the blade at its top
    cuts.append(warp(M.batch_boolean(slot_secs(0.0, 3.0, -dm - 1.0), m3d.OpType.Add)).transform(F))
    cuts.append(warp(box(-uo, uo, -3.0, 3.0, ztop - 0.5, f_top + p.shadow_line)).transform(F))
    sl = CS.square([p.fork_slot, p.fork_len], center=True).offset(p.fork_slot / 2 * 0.999, m3d.JoinType.Round)
    sl = sl ^ CS.square([p.fork_slot + 2, p.fork_len + p.fork_slot], center=True).translate([0, -p.fork_slot / 2])
    cuts.append(warp(M.extrude(sl.translate([uf, -p.blade_depth - p.fork_len / 2 - 0.01 - 4]), p.fork_t + 2)
                     .translate([0, 0, z_top - p.fork_t - 1])).transform(F))
    for (x, ys) in shroud_tabs(p):
        cuts.append(slot_z(p.shroud_tab_screw_d + 0.6, p.bezel_travel + p.shroud_tab_screw_d + 0.6,
                           -40, 0, x, ys - p.bezel_travel / 2))
    ay, az = p.access_hole_yz
    cuts.append(cyl_x(p.access_hole_d, -ow / 2 - 5, -ow / 2 + p.wing_t + 5, ay, az))
    for side in (1, -1):
        sl = CS.square([p.bezel_travel, 0.01], center=True).offset((p.shroud_tab_screw_d + 0.6) / 2, m3d.JoinType.Round)
        sl = sl.translate([wy - p.bezel_travel / 2, wz])
        cuts.append(M.extrude(sl, 20).transform([[0, 0, 1, side * ow / 2 - 10], [1, 0, 0, 0], [0, 1, 0, 0]]))
    out = M.batch_boolean([body] + cuts, m3d.OpType.Subtract)

    # rolled rim round the slot's front edge: down one side, along the bottom, up the other,
    # its ends buried in the blade
    rr = p.rim_r
    hw = uo + p.mouth_wrap + rr * 0.6
    zl = f_bot - p.mouth_flare - rr * 0.6
    rc = p.mouth_r + p.mouth_wrap + rr * 0.6
    zt_end = z_top - p.rail_t / 2
    path = [(-hw, z) for z in np.arange(zt_end, zl + rc, -2.0)]
    path += [(-hw + rc - rc * math.cos(a), zl + rc - rc * math.sin(a)) for a in np.linspace(0, math.pi / 2, 16)]
    path += [(u, zl) for u in np.arange(-hw + rc + 2.0, hw - rc - 1.0, 2.0)]
    path += [(hw - rc + rc * math.sin(a), zl + rc - rc * math.cos(a)) for a in np.linspace(0, math.pi / 2, 16)]
    path += [(hw, z) for z in np.arange(zl + rc + 2.0, zt_end + 0.01, 2.0)]
    clean = [path[0]]
    for q in path[1:]:
        if math.hypot(q[0] - clean[-1][0], q[1] - clean[-1][1]) > 0.5:
            clean.append(q)
    rim = warp(tube(clean, rr, -rr * 0.35), 2.0)

    # posts: slightly elongated front to back, spreading into the floor like roots and only
    # just flaring into the blade, trimmed flat behind so they never reach the pods
    sec = CS.square([0.01, max(p.post_len - p.post_d, 0.01)], center=True).offset(p.post_d / 2 - 0.005, m3d.JoinType.Round)
    h = f_top - f_bot + 1.0                         # 0.5 mm into the shelf and the blade
    hwp, hlp = p.post_d / 2, p.post_len / 2

    def flare(v):
        z = v[:, 2]
        g_ = p.post_root_w * np.clip(1 - z / p.post_root_h, 0, 1) ** 2 + \
            p.post_cap_w * np.clip(1 - (h - z) / p.post_cap_h, 0, 1) ** 2
        out = v.copy()
        out[:, 0] *= (hwp + g_) / hwp
        out[:, 1] *= (hlp + g_) / hlp
        return out
    posts = []
    for (x, y, y_min) in post_xy(p):
        post = M.extrude(sec, h, n_divisions=int(h / 0.6)).warp_batch(flare).translate([x, y, f_bot - 0.5])
        post = post ^ box(x - 30, x + 30, y_min + p.mask_t, y + 40, f_bot - 1, f_top + 1)
        posts.append(post ^ box(-U, U, -300, -0.8, -300, 300).transform(F))   # stays behind the front edge
    out = M.batch_boolean([out, rim.transform(F)] + posts, m3d.OpType.Add)
    return out ^ box(-ow / 2, ow / 2, -300, 300, -300, 300)


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


def fit_test_blade(p):
    """Quick print: just the bezel's top blade and fork, 3.7 mm thick. Slide it in under the
    front of the headlight cover to check the fork finds the clip and the front edge lines up."""
    z_top = bezel_z(p)[0]
    F = front_frame(p)
    U = (p.opening_w / 2 - p.opening_side_clear) / F[0][0]
    keep = box(-U - 5, U + 5, -p.blade_depth - p.fork_len - 2, 8, z_top - p.rail_t + 0.3, z_top + 1).transform(F)
    return shroud(p) ^ keep


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
    """Stand-in pods from the maker's drawing (body, bezel, bracket foot, stud), placed on the
    curve. dy slides them straight fore-aft (for the clearance checks)."""
    one = [plate_xz(rrect(p.pod_face_w, p.pod_face_h, p.pod_face_r).translate([0, pod_zc(p)]), 0, 8),
           box(-p.pod_body_w / 2, p.pod_body_w / 2, -p.pod_depth, -8, p.pod_lift, pod_top(p)),
           box(-p.pod_bracket_w / 2, p.pod_bracket_w / 2,
               p.pod_bolt_nominal_y - p.pod_bracket_d / 2, p.pod_bolt_nominal_y + p.pod_bracket_d / 2,
               0.01, p.pod_lift + 1),
           cyl_z(p.pod_stud_d, -p.floor_t - 12, 0.02, 0, p.pod_bolt_nominal_y)]
    pod = M.batch_boolean(one, m3d.OpType.Add)
    return M.batch_boolean([at_pose(pod, pose) for pose in pod_poses(p)], m3d.OpType.Add).translate([0, dy, 0])


def pod_lenses(p):
    """Two lens discs per pod, for the mockup and diagrams."""
    discs = []
    for pose in pod_poses(p):
        for dx in (-18.5, 18.5):
            d = M.cylinder(0.6, 16).rotate([-90, 0, 0]).translate([dx, 0.2, pod_zc(p)])
            discs.append(at_pose(d, pose))
    return M.batch_boolean(discs, m3d.OpType.Add)

# ---------- output ----------

def to_trimesh(man):
    import trimesh
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


def mirror_x(man):
    return man.mirror([1, 0, 0])


def print_orient_shroud(man):
    """Print the bezel upside down, standing on its flat top rail."""
    return man.rotate([180, 0, 0])


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
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(here, "preview"), exist_ok=True)
    c, s = carrier(P), shroud(P)
    # modelled part is the passenger side; the driver side is its mirror image
    sides = [("passenger", c, s, 1), ("driver", mirror_x(c), mirror_x(s), -1)]
    for side, cc, ss, _ in sides:
        save(print_orient_carrier(cc), os.path.join(out, f"carrier_{side}.stl"))
        save(print_orient_shroud(ss), os.path.join(out, f"bezel_{side}.stl"))
    save(fit_test(P), os.path.join(out, "fit_test_window.stl"))
    blade = fit_test_blade(P)
    save(print_orient_shroud(blade), os.path.join(out, "fit_test_blade_passenger.stl"))
    save(print_orient_shroud(mirror_x(blade)), os.path.join(out, "fit_test_blade_driver.stl"))
    save(fit_test_mount(P), os.path.join(out, "fit_test_mount_passenger.stl"))
    save(mirror_x(fit_test_mount(P)), os.path.join(out, "fit_test_mount_driver.stl"))
    save(spacers(P), os.path.join(out, "spacer_washers.stl"))

    preview(P, os.path.join(here, "preview", "assembly.png"))
