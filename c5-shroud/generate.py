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
    # a tongue on the blade clicks onto the clip under the cover. A wing (ear) at each end
    # screws to the carrier. It is taller at the hood end than at the fender end.
    shroud_t: float = 3.0         # thinnest wall (at the shallow side of each tunnel)
    shroud_margin_top: float = 8.0   # bezel top (the cover's underside) above the pod tops (ESTIMATE)
    bezel_h_hood: float = 79.6    # front height at the hood end, top of the blade to the bottom (flat bottom at z = -18,
                                  # just under the carrier's lip and the screw tabs, as the owner marked it)
    bezel_h_fender: float = 79.6  # same at the fender end: the bottom is level
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
    front_bow: float = 12.0       # the face bows forward this much in the middle, following the nose
    face_belly: float = 7.0       # seen from the side, the face swells forward this much halfway down...
    face_tuck: float = 8.0        # ...and rolls back this much at its lower edge
    bottom_sag: float = 0.0       # the lower edge is straight (the owner cut off the sagging chin)
    slot_smile: float = 5.0       # the slot's lower lip dips this much in the middle at the front edge
    edge_r: float = 2.6           # rolled edge right round the outside of the face
    face_t: float = 3.0           # the face is a shell this thick, with the slot cut through it
    top_corner_r: float = 10.0    # outline corners at the top, under the door
    mouth_wall: float = 3.0       # the slot's walls, from the face back to the pods
    mask_t: float = 1.5           # black mask just in front of each pod, with one window the size of the pod face
    shelf_t: float = 3.0
    rail_t: float = 3.0           # top blade thickness; its front edge is rounded
    blade_depth: float = 30.0     # flat top blade, from the front edge back (slides under the cover)
    # the clip under the cover, measured from the owner's model of the covers (Covers.stl, see
    # cover_scan.py): a U-shaped rib hanging about 9 mm under the skin behind the front edge,
    # a cross bar with two short legs running back from its ends
    clip_u: float = -9.9          # clip centre across the front, from the middle of the bezel (hood end is -)
    clip_back: float = 61.2       # front face of the cross bar, behind the cover's front edge
    clip_bar_t: float = 3.5       # cross bar thickness
    clip_skew: float = 0.36       # the bar runs 0.36 mm further forward per mm toward the fender (20 deg)
    clip_leg_gap: float = 26.0    # between the legs' inner faces
    cover_edge_n: float = 5.0     # the door's front edge sits this far behind the blade's front, just behind the bead
    # a tongue on the blade runs back under the clip: the bar drops into a groove across it and the
    # legs sit either side of it (it prints flush with the blade, so the blade still lies flat)
    tongue_w: float = 23.0
    groove_clear: float = 1.0     # groove is this much wider than the bar front and back
    groove_depth: float = 2.0     # the bar hangs about 1.2 mm below the cover's lip
    tooth_len: float = 4.5        # tongue behind the groove, chamfered so it ramps under the bar
    # the door's lip is not level: in the owner's model it runs about level over the hood half and
    # drops about 9 mm toward the fender. The top of the bezel follows it so the door sits down on
    # the blade all the way across (COVER_LIP below).
    lip_follow: float = 1.0       # 1 = follow the door's lip as measured, 0 = level top
    lip_roll: float = 0.0         # extra tilt of the top toward the fender, degrees (+ = fender end lower)
    rim_r: float = 3.0            # the rolled rim round the slot is a tube this radius (6 mm lip)
    corner_r: float = 30.0        # the front turns back into the ears round this radius, seen from above
    end_wall_x: float = 123.0     # end walls of the frame start this far out (just past the outer pods)
    wing_t: float = 3.0           # side wings (ears)
    wing_screw_y: float = -54.0   # M4 screw through each wing into a boss on the carrier
    wing_screw_z: float = 4.0
    # The wings are full side walls like the stock ears: they run back past the pods to
    # just in front of the arm and the pad, and down over the carrier.
    wing_back_y: float = -90.0    # rear edge of the wings (the arm and pad faces are at -95)
    wing_back_z: float = -18.0    # bottom of the wings at their rear edge, level with the face's bottom
    wing_r: float = 10.0          # rounded rear corners
    access_hole_d: float = 28.0   # hood-end wing: hole to reach the aiming adjuster, like the stock ear
    access_hole_yz: tuple = (-72.0, 38.0)
    # ears like the stock bezel's: a side panel each end, outside the headlight door's side flange,
    # held by screws through it and the flange's holes into the headlight, as the stock ears are
    # (owner's photo of a stock headlight). They follow the flange's shape, measured from the
    # owner's model of the doors (cover_sides.json, from cover_scan.py), and print as separate parts.
    ear_t: float = 3.0
    # the one-piece shell (owner's reference photo)
    shell_t: float = 3.0          # wall thickness everywhere
    post_w: float = 6.0           # posts between the windows, at their narrowest (on the gaps between pods)
    post_setback: float = 4.0     # posts stand this far back from the front edge, clear of the lenses
    post_depth: float = 13.0      # posts run this far back from the front
    window_r: float = 15.0        # window corner radius: the posts flare into the floor and blade
    window_wrap: float = 12.7     # the end windows run this far round into the corners
    floor_depth: float = 22.0     # shallow floor under the pods, back from the front
    lip_r: float = 3.5            # rounded lip along the bottom front edge (7 mm tall)
    bead_r: float = 1.5           # raised bead along the blade's front edge, where the door seals
    ear_start_y: tuple = (-35.0, -45.0)   # hood, fender: where the door's side flange starts
    ear_tip_past: float = 15.0    # ears end this far past the last screw hole
    ear_tip_above: float = 14.0   # ...and taper to this far above it (and 12 below)
    tongue_root_w: float = 40.0   # clip tongue: width where it leaves the blade
    tongue_slot_w: float = 5.0    # ...and the slot along it
    dowel_d: float = 3.1          # dowel holes across the print split (3 mm pins)
    dowel_depth: float = 6.0      # each side of the split
    ear_gap: float = 0.8          # between the ear and the door
    ear_top_gap: float = 8.0      # ear's top edge this far under the top of the door's side: up to its painted edge, no gap
    ear_hole_d: float = 6.5       # clearance for the stock ear screws, at every hole in the flange
    ear_access_d: float = 40.0    # hood-end ear: hole for the aiming adjuster's access plug (from the photo)
    ear_access_yz: tuple = (-132.0, 16.0)
    # the front of the door's fender-side flange comes down over the top of the fender wing: the
    # wing is trimmed under it (from the owner's model). (x from, x to, y from, y to, z at x from,
    # drop per mm toward the fender)
    door_corner_cut: tuple = None  # replaced by door_clearance(), from the door's measured underside
    door_clear: float = 0.25      # the bezel's top is trimmed this far under the door's underside
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


# the underside of the door's front lip, measured from the owner's model of the covers
# (cover_scan.py): across the front from the hood end (-) to the fender end (+), mm
COVER_LIP_U = list(range(-140, 141, 10))
COVER_LIP_Z = [24.0, 24.1, 24.5, 24.6, 24.8, 24.8, 24.8, 24.8, 24.7, 24.5, 24.3, 24.1, 23.9, 23.6, 23.3,
               23.0, 22.6, 22.1, 21.7, 21.1, 20.6, 20.1, 19.5, 18.9, 18.2, 17.4, 16.5, 15.8, 15.8]


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


def top_rise(p, u):
    """How far the bezel's top is raised at u (along the front) to follow the door's lip.
    It is never lowered: the lowest point of the lip, at the fender end, is where the top was."""
    U = (p.opening_w / 2 - p.opening_side_clear) / front_frame(p)[0][0]

    def lip(u_):
        return np.interp(u_, COVER_LIP_U, COVER_LIP_Z) - math.tan(math.radians(p.lip_roll)) * np.asarray(u_)
    ref = lip(np.linspace(-U - 3, U + 3, 200)).min()
    return p.lip_follow * np.maximum(lip(u) - ref, 0.0)


def lift_top(p, man):
    """Raise the top of the bezel to follow the door's lip. Everything from the blade's underside
    up moves as one; the thin band between the tops of the pod windows and the blade stretches
    to take it up, so the windows and everything round the pods stay where they are."""
    z_top = bezel_z(p)[0]
    z0 = pod_zc(p) + p.pod_face_h / 2 + p.window_clear_y + 0.2
    z1 = z_top - p.rail_t - 0.3
    s, c0 = front_line(p)
    k = 1 / math.hypot(1, s)

    def f(v):
        out = v.copy()
        u = k * v[:, 0] + s * k * (v[:, 1] - c0)
        t = np.clip((v[:, 2] - z0) / (z1 - z0), 0, 1)
        out[:, 2] += top_rise(p, u) * t * t * (3 - 2 * t)
        return out
    return man.refine_to_length(6.0).warp_batch(f)


def top_tilt(p):
    """Slope (rise per mm along the front) of the straight line that best fits the bezel's top."""
    U = (p.opening_w / 2 - p.opening_side_clear) / front_frame(p)[0][0]
    u = np.linspace(-U + 5, U - 5, 100)
    return float(np.polyfit(u, top_rise(p, u), 1)[0])


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


def clip_n(p, u):
    """Front face of the clip's cross bar at u, in the front's own frame (before the bow)."""
    return -p.cover_edge_n - p.clip_back + p.clip_skew * (u - p.clip_u)          # the nose is at n = 0


def clip_tongue(p, z_top):
    """The tongue on the blade that clicks onto the cover's clip, and the groove the bar drops
    into, in the front's own frame (before the bow). It tapers back from a wide root and has
    a slot along its middle. The tongue fits between the clip's legs
    and ends in a chamfered tooth that ramps under the bar as the blade slides in."""
    ul, ur = p.clip_u - p.tongue_w / 2, p.clip_u + p.tongue_w / 2
    g0 = [clip_n(p, u) + p.groove_clear for u in (ul, ur)]                 # groove front edge
    g1 = [clip_n(p, u) - p.clip_bar_t - p.groove_clear for u in (ul, ur)]  # groove back edge
    tb = [n - p.tooth_len for n in g1]                                      # end of the tooth
    zb = z_top - p.rail_t
    # tapered from a wide root at the blade to the tooth, with a slot along it (as in the photo)
    rw = p.tongue_root_w / 2
    n_r = -p.blade_depth + 1
    n_n = min(g0) + 4                                    # the taper ends just ahead of the groove
    plan = CS([[[ul, tb[0]], [ur, tb[1]], [ur, n_n], [p.clip_u + rw, n_r], [p.clip_u - rw, n_r], [ul, n_n]]])
    plan = plan - CS.square([p.tongue_slot_w, n_r - 4 - (n_n - 2)]).translate([p.clip_u - p.tongue_slot_w / 2, n_n - 2])
    tongue = M.extrude(plan, p.rail_t).translate([0, 0, zb])
    # chamfer the back of the tooth: 1.8 mm down at its end, running out 3 mm in
    ch = M.hull_points([[u, n + dn, z] for (u, n) in ((ul - 1, tb[0] - p.clip_skew), (ur + 1, tb[1] + p.clip_skew))
                        for (dn, z) in ((-1, z_top - 2.4), (-1, z_top + 1), (4.67, z_top + 1))])
    tongue = tongue - ch
    gr = CS([[[ul - 1, g1[0] - p.clip_skew], [ur + 1, g1[1] + p.clip_skew],
              [ur + 1, g0[1] + p.clip_skew], [ul - 1, g0[0] - p.clip_skew]]])
    groove = M.extrude(gr, p.groove_depth + 1).translate([0, 0, z_top - p.groove_depth])
    return tongue, groove


def face_profile(p, z):
    """Side view of the bezel face: how far it swells forward (or rolls back) at height z."""
    z_top, zb_hood, zb_fender = bezel_z(p)
    zlow = min(zb_hood, zb_fender) - p.bottom_sag
    t = np.clip((z_top - z) / (z_top - zlow), 0, 1)
    return p.face_belly * np.sin(np.pi * t) - p.face_tuck * t ** 3


_SIDES = {}


def door_side(name):
    """The door's side flange ("hood" or "fender") from cover_sides.json: its holes, and a function
    giving how far out (|x|) the door reaches at (y, z). The map is filled straight down below the
    flange and forward/back past its ends, and widened by one cell so it errs outward."""
    if name not in _SIDES:
        import json
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
            d = json.load(fh)[name]
        ys, zs = np.asarray(d["y"]), np.asarray(d["z"])
        X = np.array([[np.nan if q is None else q for q in row] for row in d["x"]], float)
        for i in range(len(ys)):                     # fill each column down from its lowest point, and up
            col = X[i]
            ok = np.flatnonzero(~np.isnan(col))
            if len(ok):
                col[:ok[0]] = col[ok[0]]
                col[ok[-1] + 1:] = col[ok[-1]]
        have = np.flatnonzero(~np.isnan(X[:, 0]))
        for i in range(len(ys)):                     # columns past the ends take the nearest one
            if np.isnan(X[i, 0]):
                X[i] = X[have[np.argmin(np.abs(have - i))]]
        Xd = X.copy()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                Xd = np.fmax(Xd, np.roll(np.roll(X, di, 0), dj, 1))
        # smooth it so the ear is a fair surface, but never inside the door itself
        S = Xd.copy()
        for _ in range(3):
            P_ = np.pad(S, 1, mode="edge")
            S = sum(P_[1 + di:P_.shape[0] - 1 + di, 1 + dj:P_.shape[1] - 1 + dj]
                    for di in (-1, 0, 1) for dj in (-1, 0, 1)) / 9
        Xd = np.fmax(S, X)

        def reach(y, z):
            fy = np.clip((np.asarray(y) - ys[0]) / (ys[1] - ys[0]), 0, len(ys) - 1.001)
            fz = np.clip((np.asarray(z) - zs[0]) / (zs[1] - zs[0]), 0, len(zs) - 1.001)
            i, j = fy.astype(int), fz.astype(int)
            a, b = fy - i, fz - j
            return ((1 - a) * (1 - b) * Xd[i, j] + a * (1 - b) * Xd[i + 1, j] +
                    (1 - a) * b * Xd[i, j + 1] + a * b * Xd[i + 1, j + 1])
        # the door's side edge seen from the side: the top of the door over each fore-aft position
        tops = np.array([zs[np.flatnonzero(~np.isnan(np.asarray([np.nan if q is None else q for q in row], float)))].max()
                         if any(q is not None for q in row) else np.nan for row in d["x"]])
        ok = ~np.isnan(tops)
        tops = np.interp(ys, ys[ok], tops[ok])
        tops = np.convolve(np.pad(tops, 2, mode="edge"), np.ones(5) / 5, mode="valid")

        def door_top(y):
            return np.interp(y, ys, tops)
        def reach_raw(y, z):                          # the same, without the widening and smoothing
            fy = np.clip((np.asarray(y) - ys[0]) / (ys[1] - ys[0]), 0, len(ys) - 1.001)
            fz = np.clip((np.asarray(z) - zs[0]) / (zs[1] - zs[0]), 0, len(zs) - 1.001)
            i, j = fy.astype(int), fz.astype(int)
            a, b = fy - i, fz - j
            return np.fmax.reduce([X[i, j], X[i + 1, j], X[i, j + 1], X[i + 1, j + 1]])
        reach.raw = reach_raw
        _SIDES[name] = (d["holes"], reach, door_top)
    return _SIDES[name]


def _along(man, nrm, at):
    """Turn a part built along +z onto the direction nrm and move its origin to at."""
    nrm = np.asarray(nrm, float) / np.linalg.norm(nrm)
    k = np.cross([0, 0, 1], nrm)
    sn, cs_ = np.linalg.norm(k), nrm[2]
    K = np.zeros((3, 3)) if sn < 1e-9 else np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]]) / sn
    Rm = np.eye(3) + sn * K + (1 - cs_) * K @ K
    return man.transform(np.hstack([Rm, np.asarray(at, float)[:, None]]))


def _rot_to(a, b):
    a, b = np.asarray(a, float) / np.linalg.norm(a), np.asarray(b, float) / np.linalg.norm(b)
    k = np.cross(a, b)
    sn, cs_ = np.linalg.norm(k), a @ b
    if sn < 1e-9:
        return np.eye(3) if cs_ > 0 else np.diag([1.0, -1.0, -1.0])
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]]) / sn
    return np.eye(3) + sn * K + (1 - cs_) * K @ K


# ---------------------------------------------------------------------------------------------
# The bezel: one continuous thin shell, U-shaped from above (owner's reference photo)
# ---------------------------------------------------------------------------------------------

def bow(p, u):
    """How far the front sits forward of the flat front line at u (the nose's curve)."""
    U = (p.opening_w / 2 - p.opening_side_clear) / front_frame(p)[0][0]
    return p.front_bow * (1 - np.minimum(np.abs(np.asarray(u, float)) / U, 1) ** 2)


def bow_warp(p, man, edge=4.0):
    """Bend a part built against the flat front line (front frame) onto the curved front."""
    def f(v):
        out = v.copy()
        out[:, 1] += bow(p, v[:, 0])
        return out
    return man.refine_to_length(edge).warp_batch(f)


def _fpt(F, u, n):
    """Plan position (x, y) of front-frame point (u, n)."""
    return np.array([F[0][0] * u + F[0][1] * n + F[0][3], F[1][0] * u + F[1][1] * n + F[1][3]])


def front_uv(p, x, y):
    """Front-frame u of plan point(s) (x, y)."""
    s, c0 = front_line(p)
    k = 1 / math.hypot(1, s)
    return k * np.asarray(x) + s * k * (np.asarray(y) - c0)


def shell_levels(p):
    """Heights of the shell before the top is raised to follow the door: blade top, blade
    underside, window bottom (= floor top), floor bottom, lip bottom."""
    z_top = bezel_z(p)[0]
    z_wb = pod_zc(p) - p.pod_face_h / 2 - p.window_clear_y
    return z_top, z_top - p.rail_t, z_wb, z_wb - p.shell_t, z_wb - 2 * p.lip_r


def shell_plan(p):
    """The shell's outline from above, and each ear's flat plane.

    The front follows the curved front line. At each end it turns back round a corner_r radius
    into a short straight side, then into a long flat ear that lies just outside the door's
    side flange, back past its last screw hole. Returns the outer outline (closed far behind),
    and per side: the corner's tangent u on the front, the ear's inside line |x| = a + b y,
    where the ear starts (y_k) and ends (y_tip), and the arc's end y."""
    F = front_frame(p)
    R = p.corner_r
    z_top, _, _, _, z_lb = shell_levels(p)
    front_pts = lambda u: _fpt(F, u, float(bow(p, u)))
    sides = {}
    for name, sx in (("hood", -1), ("fender", 1)):
        holes, reach, door_top = door_side(name)
        y_k = p.ear_start_y[0 if sx < 0 else 1]
        y_tip = min(h["at"][1] for h in holes) - p.ear_tip_past
        z_tip = min(h["at"][2] for h in holes) - 12
        ys = np.linspace(y_tip, y_k, 40)
        X = np.array([max(float(reach.raw(y, z)) for z in np.linspace(z_lb + (z_tip - z_lb) * (y - y_k) / (y_tip - y_k),
                                                                   float(door_top(y)) - p.ear_top_gap, 12))
                      for y in ys])
        b = np.polyfit(ys, X, 1)[0]
        a = float((X - b * ys).max()) + p.ear_gap            # the ear's inside clears the door
        X_out = a + b * y_k + p.shell_t                      # outside of the straight side
        # corner: the arc of radius R tangent to the front curve and to the straight side
        def centre(u):
            h = 0.5
            t = front_pts(u + h) - front_pts(u - h)
            t /= np.linalg.norm(t)
            n_in = np.array([t[1], -t[0]])                   # pointing back from the front
            if n_in @ np.array([-F[0][1], -F[1][1]]) < 0:
                n_in = -n_in
            return front_pts(u) + R * n_in
        lo, hi = (-250.0, 0.0) if sx < 0 else (0.0, 250.0)
        target = sx * (X_out - R)
        for _ in range(60):
            mid = (lo + hi) / 2
            if (centre(mid)[0] - target) * sx > 0:
                hi, lo = (mid, lo) if sx > 0 else (hi, mid)
            else:
                lo, hi = (mid, hi) if sx > 0 else (lo, mid)
        u_t = (lo + hi) / 2
        c = centre(u_t)
        p0 = front_pts(u_t)
        a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
        a1 = 0.0 if sx > 0 else math.pi
        if sx > 0:
            while a0 < a1:
                a0 += 2 * math.pi
            while a0 - a1 > 2 * math.pi:
                a0 -= 2 * math.pi
        else:
            while a0 > a1:
                a0 -= 2 * math.pi
            while a1 - a0 > 2 * math.pi:
                a0 += 2 * math.pi
        arc = [c + R * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(a0, a1, 24)]
        # straight side back to the start of the flange, a short blend, then the flat ear
        y_k = min(y_k, c[1] - 26)                            # room for a short straight side
        side = [np.array([sx * X_out, y]) for y in np.linspace(c[1] - 1, y_k + 12, 6)]
        blend = []
        for t in np.linspace(0, 1, 7)[1:-1]:
            y_ = y_k + 12 - 24 * t
            x_line = a + b * y_ + p.shell_t
            w = t * t * (3 - 2 * t)
            blend.append(np.array([sx * ((1 - w) * X_out + w * x_line), y_]))
        ear = [np.array([sx * (a + b * y + p.shell_t), y]) for y in np.linspace(y_k - 12, y_tip, 12)]
        sides[name] = dict(sx=sx, u_t=u_t, p0=p0, arc_end_y=c[1], y_k=y_k, y_tip=y_tip, z_tip=z_tip, a=a, b=b,
                           path=arc + side + blend + ear, holes=holes, door_top=door_top)
    hood, fen = sides["hood"], sides["fender"]
    fr = [front_pts(u) for u in np.linspace(hood["u_t"], fen["u_t"], 80)]
    outline = hood["path"][::-1] + fr[1:-1] + fen["path"]
    outline += [np.array([fen["path"][-1][0], -600.0]), np.array([hood["path"][-1][0], -600.0])]
    return np.asarray(outline)[::-1], sides              # counter-clockwise


def _tube3(pts, r, segs=16):
    """A round bar of radius r along a 3D polyline (hulls of spheres, unioned)."""
    ball = M.sphere(r, segs)
    parts = [M.batch_hull([ball.translate(list(a)), ball.translate(list(b))]) for a, b in zip(pts, pts[1:])]
    return M.batch_boolean(parts, m3d.OpType.Add)


def shell_parts(p):
    """The one-piece bezel (passenger side as modelled), before it's split for printing."""
    F = front_frame(p)
    Fm = np.vstack([np.asarray(F, float), [0, 0, 0, 1]])
    z_top, z_bu, z_wb, z_fb, z_lb = shell_levels(p)
    outline, sides = shell_plan(p)
    U3 = M.extrude(CS([outline]), 400).translate([0, 0, -150])            # inside the outline
    hood, fen = sides["hood"], sides["fender"]
    ua, ub = hood["u_t"], fen["u_t"]
    t = p.shell_t

    # --- the front, built against the flat front line, then bent onto the curve ---
    wide = (ua - 60, ub + 60)
    slab = box(ua - 30, ub + 30, -p.post_setback - p.post_depth, 0.3, z_fb, z_top)   # posts come out of this
    blade = box(*wide, -p.blade_depth, 0.3, z_bu, z_top)
    floor = box(*wide, -p.floor_depth, 0.3, z_fb, z_wb)
    tongue, groove = clip_tongue(p, z_top)
    front = M.batch_boolean([bow_warp(p, m) for m in (slab, blade, floor, tongue)], m3d.OpType.Add).transform(F)
    front = front ^ M.extrude(CS([outline]).offset(-0.07, m3d.JoinType.Round), 400).translate([0, 0, -150])  # just inside the walls' face
    # lip rolled along the bottom front edge, and a bead along the blade's front edge, both
    # running round the corners
    def edge_path(n_in, z):
        fr = [np.append(_fpt(F, u, float(bow(p, u)) - n_in), z) for u in np.linspace(ua, ub, 60)]
        out = []
        for s_ in (hood, fen):
            c_arc = s_["path"][:21]                                    # arc, front to nearly the side
            cen = _arc_centre(c_arc)
            arc_in = [np.append(cen + (q - cen) * (p.corner_r - n_in) / p.corner_r, z) for q in c_arc]
            out.append(arc_in)
        return out[0][::-1] + fr + out[1]
    lip = _tube3(edge_path(p.lip_r, z_wb - p.lip_r), p.lip_r)
    bead = _tube3(edge_path(p.bead_r, z_top), p.bead_r)
    front = M.batch_boolean([front, lip, bead], m3d.OpType.Add)
    front = front - bow_warp(p, groove, 1.0).transform(F)

    # --- windows: one rounded rectangle per pod; the posts are what's left between them. The
    # posts sit on the gaps between the pods, a little back from the front edge ---
    poses = pod_poses(p)
    gaps = []
    for (xa, ya, _), (xb, yb, _) in zip(poses, poses[1:]):
        xg = (xa + xb) / 2
        u0 = float(front_uv(p, xg, 0.0))
        yf_ = float(_fpt(F, u0, float(bow(p, u0)))[1])
        gaps.append(float(front_uv(p, xg, yf_ - p.post_setback - p.post_depth / 2)))
    edges = []
    for i in range(len(poses)):                          # the end windows run out into the corners
        lo_ = gaps[i - 1] + p.post_w / 2 if i > 0 else ua - p.window_wrap
        hi_ = gaps[i] - p.post_w / 2 if i < len(gaps) else ub + p.window_wrap
        edges.append((lo_, hi_))
    hgt = z_bu - z_wb - 0.1
    zc = (z_bu + z_wb) / 2
    wins = []
    for (lo_, hi_) in edges:
        cs = rrect(hi_ - lo_, hgt, p.window_r).translate([(lo_ + hi_) / 2, zc])
        wins.append(M.extrude(cs, 70).transform([[1, 0, 0, 0], [0, 0, 1, -70 - p.post_setback], [0, 1, 0, 0]]))
    lo_, hi_ = edges[0][0] + 0.37, edges[-1][1] - 0.37   # in front of the posts: one opening
    cs = rrect(hi_ - lo_, hgt - 0.3, p.window_r).translate([(lo_ + hi_) / 2, zc])
    wins.append(M.extrude(cs, 20 + p.post_setback + 0.3).transform([[1, 0, 0, 0], [0, 0, 1, -p.post_setback - 0.3], [0, 1, 0, 0]]))
    windows = M.batch_boolean(wins, m3d.OpType.Add).transform(F)

    front = lift_top(p, front)
    windows = lift_top(p, windows)

    # --- the corners and ears: one thin wall, the corner's height, running back to a thin ear
    # that tapers to its tip past the last screw hole ---
    walls2d = CS([outline]) - CS([outline]).offset(-t, m3d.JoinType.Miter)
    walls = []
    bosses, holes = [], []
    for s_ in (hood, fen):
        sx = s_["sx"]
        u_end = np.linspace(s_["u_t"], s_["u_t"] + sx * 45, 10)
        wall_top = z_top + float(np.max(top_rise(p, u_end)))
        y_c, y_k, y_tip = s_["arc_end_y"], s_["y_k"], s_["y_tip"]
        # the ear's top edge is a straight line, as high as it can be while staying under the
        # door's side all the way along
        yy = np.linspace(y_k, y_tip, 40)
        dd = np.array([float(s_["door_top"](y)) - p.ear_top_gap for y in yy])
        kk, cc = np.polyfit(yy, dd, 1)
        cc -= max(0.0, float(np.max(kk * yy + cc - dd)))
        rt = 6.0                                         # the ear's tip is rounded, seen from the side

        # like the photo the ear tapers toward its tip: the top edge runs down from the door's
        # edge at the corner to 14 mm above the last screw hole
        z_last = min(h["at"][2] for h in s_["holes"])
        z_start = kk * y_k + cc
        kk = (z_start - (z_last + p.ear_tip_above)) / (y_k - y_tip)
        cc = z_start - kk * y_k

        def top_z(y):
            y = np.asarray(y, float)
            line = np.minimum(kk * y + cc, np.polyval([kk, cc], y))
            w = np.clip((y_c - y) / (y_c - y_k), 0, 1)
            zt = np.where(y >= y_c, wall_top, np.where(y >= y_k, (1 - w) * wall_top + w * line, line))
            d = np.clip(y_tip + rt - y, 0, rt)
            return zt - (rt - np.sqrt(rt * rt - d * d))

        def bot_z(y):
            y = np.asarray(y, float)
            zb_ = np.where(y >= y_k, z_lb, z_lb + (s_["z_tip"] - z_lb) * (y - y_k) / (y_tip - y_k))
            d = np.clip(y_tip + rt - y, 0, rt)
            return zb_ + (rt - np.sqrt(rt * rt - d * d))
        x_t = float(s_["p0"][0])                         # where the corner leaves the front
        keep = CS.square([400, 800]).translate([x_t - 400 + 0.2 if sx < 0 else x_t - 0.2, y_tip + 0.05])
        ring = M.extrude(walls2d ^ keep, 1.0).refine_to_length(3.0)

        def fw(v):
            out = v.copy()
            zt, zb_ = top_z(v[:, 1]), bot_z(v[:, 1])
            out[:, 2] = zb_ + v[:, 2] * (zt - zb_)
            return out
        walls.append(ring.warp_batch(fw))
        # screw holes at every hole in the door's flange, with a boss filling any gap behind
        for h in s_["holes"]:
            at, nrm = np.asarray(h["at"], float), np.asarray(h["normal"], float)
            x_out = s_["a"] + s_["b"] * at[1] + t
            ln = (x_out - abs(at[0])) / abs(nrm[0])
            if ln > 0.6:
                bosses.append(_along(M.cylinder(ln - 0.3, 7, 7, 32), nrm, at + 0.3 * nrm))
            holes.append(_along(M.cylinder(60, p.ear_hole_d / 2, p.ear_hole_d / 2, 24).translate([0, 0, -30]), nrm, at))
    body = M.batch_boolean([front] + walls + bosses, m3d.OpType.Add)
    body = body - M.batch_boolean([windows] + holes, m3d.OpType.Add)
    if p.door_corner_cut:
        x0, x1, y0, y1, z0, dz = p.door_corner_cut
        body = body - M.hull_points([[x, y, z] for x in (x0, x1) for y in (y0, y1)
                                     for z in (z0 - dz * (x - x0), z0 + 40)])
    return body


def _arc_centre(arc):
    """Centre of a circular arc given as points."""
    a, b, c = np.asarray(arc[0]), np.asarray(arc[len(arc) // 2]), np.asarray(arc[-1])
    A = np.array([b - a, c - b]) * 2
    rhs = np.array([b @ b - a @ a, c @ c - b @ b])
    return np.linalg.solve(A, rhs)


def door_clearance(p):
    """Everything above the door's underside (less door_clear) over the front of the bezel, from
    the owner's model of the door (cover_sides.json "underside"): cut away so the door closes
    onto the bezel without touching it anywhere but its lip on the blade."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        d = json.load(fh).get("underside")
    if not d:
        return None
    xs, ys = np.asarray(d["x"]), np.asarray(d["y"])
    Z = np.array([[np.nan if q is None else q for q in row] for row in d["z"]], float)
    Z = np.where(np.isnan(Z), 400.0, Z - p.door_clear)
    blk = M.cube([xs[-1] - xs[0], ys[-1] - ys[0], 1]).translate([xs[0], ys[0], 0]).refine_to_length(1.0)

    def f(v):                                            # bottom follows the door, interpolated smoothly
        out = v.copy()
        fx = np.clip((v[:, 0] - xs[0]) / 2, 0, len(xs) - 1.001)
        fy = np.clip((v[:, 1] - ys[0]) / 2, 0, len(ys) - 1.001)
        i, j = fx.astype(int), fy.astype(int)
        a, b = fx - i, fy - j
        zz = ((1 - a) * (1 - b) * Z[i, j] + a * (1 - b) * Z[i + 1, j] + (1 - a) * b * Z[i, j + 1] + a * b * Z[i + 1, j + 1])
        zmin = np.minimum.reduce([Z[i, j], Z[i + 1, j], Z[i, j + 1], Z[i + 1, j + 1]])
        zz = np.where(zz > 300, 399.0, np.where(zz - zmin > 3, zmin, zz))   # at the door's edge, take its lowest
        out[:, 2] = np.where(v[:, 2] < 0.5, zz, 450.0)
        return out
    return blk.warp_batch(f)


def shroud(p):
    """The bezel as one piece (passenger side as modelled)."""
    body = shell_parts(p)
    cut = door_clearance(p)
    return body if cut is None else body - cut


def split_plane_u(p):
    """Where the shell is split for printing: through the middle of the hood-side post."""
    poses = pod_poses(p)
    us = [float(front_uv(p, x, y)) for (x, y, _) in poses]
    return (us[0] + us[1]) / 2


def split_shell(p, man):
    """The two print pieces: cut through the middle of the hood-side post, with two dowel holes
    across the cut, one where the post meets the floor and one where it meets the blade."""
    F = front_frame(p)
    us = split_plane_u(p)
    z_top, z_bu, z_wb, z_fb, z_lb = shell_levels(p)
    n_c = float(bow(p, us)) - p.post_depth / 2 - p.post_setback
    pins = []
    for z in (z_wb - 0.2, z_bu + 0.2):
        pin = M.cylinder(2 * p.dowel_depth, p.dowel_d / 2, p.dowel_d / 2, 24, True)
        pins.append(pin.transform([[0, 0, 1, us], [1, 0, 0, n_c], [0, 1, 0, z]]))
    pins = lift_top(p, M.batch_boolean(pins, m3d.OpType.Add).transform(F))
    left = box(-2000, us, -2000, 2000, -500, 500).transform(F)
    right = box(us, 2000, -2000, 2000, -500, 500).transform(F)
    return (man ^ left) - pins, (man ^ right) - pins


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
    """Quick print: just the bezel's top blade, bead and clip tongue, following the door's lip. Slide it in under
    the front of the headlight cover to check the tongue clicks onto the clip and the front edge
    lines up."""
    z_top = bezel_z(p)[0]
    F = front_frame(p)
    U = (p.opening_w / 2 - p.opening_side_clear) / F[0][0]
    keep = lift_top(p, box(-U - 60, U + 60, -p.clip_back - 30, p.front_bow + 8, z_top - p.rail_t + 0.3, z_top + 3).transform(F))
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


def print_orient_shroud(man, p=None):
    """Print the bezel (passenger side as modelled) upside down, standing on its top blade.
    The top follows the door's lip, so it's first tipped to lay the blade as flat as it goes;
    the ends of the blade then sit up to about 3 mm off the bed (turn on supports)."""
    p = p or P
    s, _ = front_line(p)
    k = 1 / math.hypot(1, s)
    a = math.atan(top_tilt(p))
    ax = np.array([-s * k, k, 0.0])
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    R = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
    return man.transform(np.hstack([R, np.zeros((3, 1))])).rotate([180, 0, 0])


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
    # the driver bezel is the mirror image of the passenger one. The one-piece model is saved for
    # reference; it prints as two pieces split through the hood-side post, joined with dowels
    save(print_orient_shroud(s), os.path.join(out, "bezel_passenger_one_piece.stl"))
    save(mirror_x(print_orient_shroud(s)), os.path.join(out, "bezel_driver_one_piece.stl"))
    for tag, piece in zip(("hood_piece", "fender_piece"), split_shell(P, s)):
        save(print_orient_shroud(piece), os.path.join(out, f"bezel_passenger_{tag}.stl"))
        save(mirror_x(print_orient_shroud(piece)), os.path.join(out, f"bezel_driver_{tag}.stl"))
    save(fit_test(P), os.path.join(out, "fit_test_window.stl"))
    blade = fit_test_blade(P)                            # split like the bezel, to fit the bed
    for tag, piece in zip(("hood_piece", "fender_piece"), split_shell(P, blade)):
        save(print_orient_shroud(piece), os.path.join(out, f"fit_test_blade_passenger_{tag}.stl"))
        save(mirror_x(print_orient_shroud(piece)), os.path.join(out, f"fit_test_blade_driver_{tag}.stl"))
    save(fit_test_mount(P), os.path.join(out, "fit_test_mount_passenger.stl"))
    save(mirror_x(fit_test_mount(P)), os.path.join(out, "fit_test_mount_driver.stl"))
    save(spacers(P), os.path.join(out, "spacer_washers.stl"))

    preview(P, os.path.join(here, "preview", "assembly.png"))
