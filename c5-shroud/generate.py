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
    pod_bracket_w: float = 76.2   # width of the bracket foot (3.0 in, the owner's pods; was 43)
    pod_bracket_d: float = 21.0   # front-to-back length of the bracket foot
    pod_gap: float = 8.0          # space between neighbouring pods
    # The row follows the slope of the headlight opening: every pod faces straight ahead, and
    # each one is stepped back from its neighbour toward the fender (a staircase, like the
    # KnightDriveTV bracket). pod_arc_deg can also turn the outer pods; 0 keeps them parallel.
    pod_step: float = 12.0        # each pod sits this far behind the one on its hood side
    pod_arc_deg: float = 0.0
    sleeve_t: float = 2.0         # the sleeve round each window, from the front back to its pod
    sleeve_back: float = 12.0     # the sleeve carries on this far back past each pod's face, wrapping it
    sleeve_flare: float = 3.5     # each window opens out this much at the front (top: under the blade the door sits on)
    sleeve_flare_end: float = 8.0 # ...at the outer ends of the row
    sleeve_flare_bottom: float = 5.0
    sleeve_flare_len: float = 12.0  # ...curving out over this much depth, like the reference
    window_corner_r: float = 10.0 # window corners (still 0.9 mm clear of the pod face's corners)
    sleeve_flare_between: float = 0.5   # ...and only this much between pods, so the posts stay
    even_steps: bool = True       # the middle pod halfway back between the outer two (equal steps)
    pod_face_back: float = 3.0    # each pod comes forward until its face is this far behind the bezel's front (None: leave them on the layout)
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
    cup_wall: float = 3.5         # walls of the pocket each pod's bracket foot sits in (neighbours' walls fuse)
    cup_h: float = 2.6            # pocket depth (stays under the bezel's floor, which the pods now sit over)
    lights: str = os.environ.get("LIGHTS", "pods")   # "pods" (3 x 3 in pods) or "projectors" (3 mini bi-LED projectors)
    # the owner's mini 2.0 in bi-LED projectors (eBay listing's size drawing); the head's size and
    # height are in bezel_styles (PROJ_W, PROJ_H, PROJ_LIFT, PROJ_X), shared with the bezel
    proj_head_d: float = 50.0     # head, front to back
    proj_body_w: float = 41.0     # fan / heatsink body behind the head, square (confirm with calipers)
    proj_body_d: float = 44.0
    proj_stem_d: float = 24.0     # threaded mounting stem behind the body, 37 mm long: a detachable bracket
    proj_stem_len: float = 37.0   # (4 screws on the back, per the listing); the cradles hold the body, so it
    proj_stem: bool = False       # comes off. True puts it back on the stand-ins (checks, pictures)
    cradle_wall: float = 4.0      # cradle walls round the body
    cradle_clear: float = 0.4     # body to cradle (add a strip of foam tape)
    strap_t: float = 3.5          # the strap across the top of each body
    strap_screw_d: float = 3.4    # pilot holes for M4 self-tapping screws (or 5.6 for M4 heat-set inserts)
    pocket_front_open: bool = True  # pockets are open at the front (the stud slot is the forward stop), clear of the bezel's light blade
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
    blade_depth: float = 38.1     # flat top blade, from the front edge back to the tongue (owner measured S4 = 1.5 in on the stock bezel)
    # the clip under the cover, measured from the owner's model of the covers (Covers.stl, see
    # cover_scan.py): a U-shaped rib hanging about 9 mm under the skin behind the front edge,
    # a cross bar with two short legs running back from its ends
    clip_u: float = -9.9          # clip centre across the front, from the middle of the bezel (hood end is -)
    clip_back: float = 61.2       # front face of the cross bar, behind the cover's front edge
    clip_bar_t: float = 3.5       # cross bar thickness
    clip_skew: float = 0.36       # the bar runs 0.36 mm further forward per mm toward the fender (20 deg)
    clip_leg_gap: float = 26.0    # between the legs' inner faces
    cover_edge_n: float = 2.5     # the door's front edge sits this far behind the blade's front, just behind the bead
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
    lip_r: float = 6.0            # rounded lip along the bottom front edge (12 mm tall, like the reference)
    bead_r: float = 1.5           # raised bead along the blade's front edge, where the door seals
    ear_start_y: tuple = (-35.0, -45.0)   # hood, fender: where the door's side flange starts
    ear_tip_past: float = 15.0    # ears end this far past the last screw hole
    ear_tip_above: float = 14.0   # ...and taper to this far above it (and 12 below)
    tongue_root_w: float = 40.0   # clip tongue: width where it leaves the blade
    tongue_slot_w: float = 5.0    # ...and the slot along it
    dowel_d: float = 3.1          # dowel holes across the print split (3 mm pins)
    dowel_depth: float = 6.0      # each side of the split
    min_wall: float = 1.05        # thinnest the side wall gets where it's pocketed round the door's flange
    outline_gap: float = 0.2      # the bezel stays this far inside the door's outline seen from above
    rim_gap: float = 0.05         # the corner and ear tops sit this far under the door's edge
    window_under: float = 3.0     # round the corners the windows stop this far under the door's edge
    shelf_t: float = 2.37         # shelf under the door's lip round each corner and side
    shelf_under: float = 2.0      # ...reaching this far in past the lip
    rim_fade: float = 0.0        # ...except the start of each corner, where the blade and bead come round, over this much of it
    ear_gap: float = 0.8          # between the ear and the door
    ear_step_gap: float = 1.5     # under the imprint's step: sets the height the straight side's position is taken at (the top edge itself follows rim_gap)
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
    s = CS.square([1e-3, length - w], center=True).offset(w / 2, m3d.JoinType.Round)   # w wide, length long
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
    """(x, y, yaw in degrees) of each pod's face centre, left to right, where they sit: each
    brought forward until its face is pod_face_back behind the bezel's front across its window, so
    the steps between them follow the front (pod_layout gives the layout the bezel is drawn from)."""
    base = pod_layout(p)
    if p.pod_face_back is None:
        return base
    half = p.pod_face_w / 2 + p.window_clear_x
    poses = [(x, min(bezel_front_y(p, x + dx) for dx in np.linspace(-half, half, 9)) - p.pod_face_back, yaw)
             for (x, _, yaw) in base]
    if p.even_steps and len(poses) == 3:
        # the middle pod goes back to halfway between the outer two, so the two steps are equal
        # (the outer ones stay pod_face_back behind the front; the middle one sits further back)
        (x0, y0, _), (x1, _, w1), (x2, y2, _) = poses
        poses[1] = (x1, (y0 + y2) / 2, w1)
    return poses


def bezel_front_y(p, x):
    """How far forward (y) the bezel's front comes at x: its curved front line, or the door's
    outline from above where that's further back (the bezel is trimmed to it)."""
    F = front_frame(p)
    u = float(front_uv(p, x, 0.0))
    for _ in range(20):                                  # the point on the front curve at this x
        q = _fpt(F, u, float(bow(p, u)))
        u += (x - q[0]) / F[0][0]
    y = float(_fpt(F, u, float(bow(p, u)))[1])
    ol = door_outline(p)
    if ol is not None:
        cut = (ol ^ CS.square([0.2, 800]).translate([x - 0.1, -400])).bounds()
        if cut[3] > cut[1]:
            y = min(y, float(cut[3]) - p.outline_gap)
    return y


def pod_layout(p):
    """(x, y, yaw in degrees) of each pod's face centre in the layout the bezel's front is drawn
    from. Adjacent pod centres are one pitch apart along an arc, so the outer pods sit back and
    turn outward."""
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
        s = CS.square([length - w, 1e-3], center=True)
    else:
        s = CS.square([1e-3, length - w], center=True)
    s = s.offset(w / 2, m3d.JoinType.Round).translate([x, z])       # w wide, length long
    return plate_xz(s, y1, y1 - y0)


# ---------- parts ----------

def proj_poses(p):
    """(x, y of the head's front, z of its centre) for each projector."""
    import bezel_styles as bs
    lay = bs.proj_layout(os.environ.get("BEZEL_STYLE", "P3J"), [py for (_, py, _) in pod_poses(p)])
    return [(x, yf, pod_zc(p) + bs.proj_lift(os.environ.get("BEZEL_STYLE", "P3J"))) for x, yf in lay]


def proj_keepouts(p):
    """(x0, x1, y1, z0, z1) of the spaces in front of the mounting tabs the bracket must stay out
    of (y1 is how far forward each reaches): a 15 mm flange nut at either end of each slot, and
    the aiming pad's square adjuster, 13 mm and more above its upper hole (as check.py has them)."""
    y_t = p.mount_wall_y + p.mount_wall_t
    out = []
    for (name, x, z, axis) in mount_points(p):
        tr = ((p.arm_slot_len if axis == "x" else p.pad_slot_len) - p.mount_hole_d) / 2
        rx, rz = p.nut_r + (tr if axis == "x" else 0.0), p.nut_r + (tr if axis == "z" else 0.0)
        out.append((x - rx, x + rx, y_t + 8.0, z - rz, z + rz))
        if name == "pad upper":
            out.append((x - 15.0, x + 15.0, y_t + 30.0, z + 13.0, z + 45.0))
    return out


def proj_cradle_span(p, yf, x=None):
    """(y0, y1) of a projector's cradle: along its body, stopping 1 mm in front of the mounting
    tabs' plane (the arm and the pad are behind it), and 1 mm in front of any nut or the pad's
    adjuster that the cradle or its strap would otherwise reach (given the cradle's x)."""
    y1 = yf - p.proj_head_d
    y0 = max(yf - p.proj_head_d - p.proj_body_d, p.mount_wall_y + p.mount_wall_t + 1.0)
    if x is not None:
        hw = p.proj_body_w / 2 + p.cradle_clear + p.cradle_wall + 5.5 + 0.5    # to the bosses' outside
        for (x0, x1, yk, _, _) in proj_keepouts(p):
            if x0 < x + hw and x - hw < x1:
                y0 = max(y0, yk + 1.0)
    return y0, y1


def proj_stem_off(p, x, yf):
    """True where a projector's threaded stem would run into a mounting tab (and the car's arm or
    aiming pad, and its bolt, behind it): that projector goes in with its stem taken off (P4's
    hood-end one, whose stem would land on the aiming pad's bolts)."""
    if yf - p.proj_head_d - p.proj_body_d - p.proj_stem_len > p.mount_wall_y + p.mount_wall_t + 1.0:
        return False
    r = p.proj_stem_d / 2 + 0.8
    return any(x0 - p.wall_t < x + r and x - r < x1 + p.wall_t for (x0, x1, _, _) in ears(p))


def projector_dummy(p, dy=0.0):
    """Stand-ins for the projectors: head, lens trim, body and stem."""
    import bezel_styles as bs
    out = []
    for (x, yf, zc) in proj_poses(p):
        bw = p.proj_body_w / 2
        out += [box(x - bs.PROJ_W / 2, x + bs.PROJ_W / 2, yf - p.proj_head_d, yf, zc - bs.PROJ_H / 2, zc + bs.PROJ_H / 2),
                box(x - bw, x + bw, yf - p.proj_head_d - p.proj_body_d, yf - p.proj_head_d + 0.5, zc - bw, zc + bw)]
        if p.proj_stem and not proj_stem_off(p, x, yf):
            out.append(M.cylinder(p.proj_stem_len + 0.5, p.proj_stem_d / 2, p.proj_stem_d / 2 - 2, 48).rotate([90, 0, 0])
                       .translate([x, yf - p.proj_head_d - p.proj_body_d + 0.5, zc]))
    return M.batch_boolean(out, m3d.OpType.Add).translate([0, dy, 0])


def lights_dummy(p, dy=0.0):
    return projector_dummy(p, dy) if p.lights == "projectors" else pod_dummy(p, dy)


def projector_straps(p):
    """One strap per projector, laid flat side by side for printing: it spans the body's top and
    screws down into the cradle's bosses (M4)."""
    out = []
    for i, (x, yf, zc) in enumerate(proj_poses(p)):
        y0, y1 = proj_cradle_span(p, yf, x)
        hw = p.proj_body_w / 2 + p.cradle_clear + p.cradle_wall + 4.5
        L = y1 - y0
        strap = M.extrude(CS.square([2 * hw, L], center=True), p.strap_t)
        for hx, hy in _strap_holes(p, L):
            strap = strap - cyl_z(4.5, -1, p.strap_t + 1, hx, hy)
        out.append(strap.translate([(i % 3) * (2 * hw + 8), (i // 3) * 60.0, 0]))   # 3 to a row
    return M.batch_boolean(out, m3d.OpType.Add)


def _strap_holes(p, L):
    """Screw positions relative to the strap's centre: two each side when it's long enough."""
    hx = p.proj_body_w / 2 + p.cradle_clear + p.cradle_wall + 1.0
    ys = (-L / 2 + 6.0, L / 2 - 6.0) if L > 30 else (0.0,)
    return [(sx * hx, y) for sx in (-1, 1) for y in ys]


def carrier_projectors(p):
    """The bracket for three projectors: the same mounting tabs, knees and gussets as the pod
    bracket, a beam under the projectors, a cradle round each one's body (with a strap across
    the top, screwed down), and room for the wiring: zip-tie slots, and a pad for a connector
    or the DRL module."""
    y_back = p.mount_wall_y
    arm_ear, pad_ear = ears(p)
    parts, cuts = [], []
    bw = p.proj_body_w / 2 + p.cradle_clear            # half the cradle's inside
    ow = bw + p.cradle_wall                             # ...and its outside
    # the beam stops this far behind the heads' fronts: 3 mm, or 11 under the light line, whose
    # channel brings the bezel's bottom edge down to -3.7 (P3J), over the beam's front
    import bezel_styles as bs
    st_ = os.environ.get("BEZEL_STYLE", "P3J")
    gap = 16.0 if st_ == "P3J" else 11.0 if st_ in bs.BOLD_STYLES else 3.0   # J: heads forward, recess deeper
    feet, spans = [], []
    for (x, yf, zc) in proj_poses(p):
        y0, y1 = proj_cradle_span(p, yf, x)
        spans.append((x, yf, zc, y0, y1))
        feet.append(CS.square([2 * (ow + 4.5), yf - gap - y0]).translate([x - ow - 4.5, y0]))
    ys_lo = max(sp[3] for sp in spans)
    ys_hi = min(sp[1] - gap for sp in spans)
    x_lo = min(sp[0] for sp in spans) - ow - 4.5
    x_hi = max(sp[0] for sp in spans) + ow + 4.5
    spine = CS.square([x_hi - x_lo, ys_hi - ys_lo]).translate([x_lo, ys_lo])
    beam = CS.batch_boolean(feet + [spine], m3d.OpType.Add).offset(1.0, m3d.JoinType.Round)
    parts.append(M.extrude(beam, p.floor_t).translate([0, 0, -p.floor_t]))
    ring = (beam.offset(-0.3, m3d.JoinType.Miter) - beam.offset(-p.wall_t - 0.3, m3d.JoinType.Miter)) ^ CS.square([170, 400], center=True)
    parts.append(M.extrude(ring, p.lip_h + 1).translate([0, 0, -p.floor_t - p.lip_h]))
    # the cradles: a saddle under the body, walls up its sides to its top, a boss at each screw
    for (x, yf, zc, y0, y1) in spans:
        zb, zt = zc - p.proj_body_w / 2 - p.cradle_clear, zc + p.proj_body_w / 2 + p.cradle_clear
        parts.append(box(x - ow, x + ow, y0, y1, -1.0, zb))
        parts += [box(x + bw, x + ow, y0, y1, -1.0, zt), box(x - ow, x - bw, y0, y1, -1.0, zt)]
        for hx, hy in _strap_holes(p, y1 - y0):
            parts.append(cyl_z(9.0, zt - 14.0, zt, x + hx, (y0 + y1) / 2 + hy))
            cuts.append(cyl_z(p.strap_screw_d, zt - 13.0, zt + 1.0, x + hx, (y0 + y1) / 2 + hy))
        # air for the body's fan: two windows in each wall
        L = y1 - y0
        if L < 25.0:            # a short cradle (kept off a nut): a rest under the head as well
            parts.append(box(x - 12.0, x + 12.0, y1 + 2.0, yf - 18.0, -1.0, zc - bs.PROJ_H / 2 - 0.4))
        for sx in (-1, 1):
            for (wa, wb) in ((y0 + 4.0, y0 + L / 2 - 2.0), (y0 + L / 2 + 2.0, y1 - 4.0)):
                if wb - wa > 4.0:
                    xa, xb = (x + bw - 1.0, x + ow + 1.0) if sx > 0 else (x - ow - 1.0, x - bw + 1.0)
                    cuts.append(box(xa, xb, wa, wb, zb + 6.0, zt - 16.0))
    # knees from the end cradles back to the mounting tabs
    for (x0, x1, _, _), sp in ((arm_ear, spans[-1]), (pad_ear, spans[0])):
        tx0, tx1 = x0 - p.wall_t, x1 + p.wall_t
        ty1 = y_back + p.mount_wall_t + 22
        x, yf, zc, y0, y1 = sp
        knee = CS.hull_points([[x - ow - 4.5, y0], [x + ow + 4.5, y0], [x - ow - 4.5, yf - gap], [x + ow + 4.5, yf - gap],
                               [tx0, y_back], [tx1, y_back], [tx0, ty1], [tx1, ty1]]).offset(0.6, m3d.JoinType.Round)
        parts.append(M.extrude(knee, p.floor_t).translate([0, 0, -p.floor_t]))
    parts += _tab_parts(p)
    # wiring, on the beam under the front of the heads (9.5 mm of room there): a raised pad with
    # two M3 holes 24 mm apart for a connector block, under the second head from the hood end,
    # and pairs of zip-tie slots under the others and by the hood end, where the strip's wires
    # come back from the bezel
    x2, yf2 = spans[1][0], spans[1][1]
    pf = max(7.0, gap - 4.0)              # the pad's front: back as far as the beam's front needs
    parts.append(box(x2 - 9.0, x2 + 9.0, yf2 - pf - 30.0, yf2 - pf, -1.0, 2.0))
    for dy in (-pf - 27.0, -pf - 3.0):
        cuts.append(cyl_z(2.6, -p.floor_t - 1, 3.0, x2, yf2 + dy))
    ties = [(sp[0], sp[1] - 12.0) for i, sp in enumerate(spans) if i != 1]
    ties.append((spans[0][0] - ow - 1.5, spans[0][1] - 24.0))
    for (tx, ty) in ties:
        for dx in (-5.0, 5.0):
            cuts.append(box(tx + dx - 1.25, tx + dx + 1.25, ty - 2.5, ty + 2.5, -p.floor_t - 1, 1.0))
    body = M.batch_boolean(parts, m3d.OpType.Add)
    for (_, hx, hz, axis) in mount_points(p):
        ln = p.arm_slot_len if axis == "x" else p.pad_slot_len
        cuts.append(slot_y(p.mount_hole_d, ln, axis, y_back - 1, y_back + p.mount_wall_t + 1, hx, hz))
    return M.batch_boolean([body] + cuts, m3d.OpType.Subtract)


def _tab_parts(p):
    """The mounting tabs (arm and pad), the floor under each, and a gusset on each one's outboard
    edge, as on the pod bracket; and the floor out beside the outer lights."""
    y_back = p.mount_wall_y
    arm_ear, pad_ear = ears(p)
    parts = []
    for (x0, x1, z0, z1) in (arm_ear, pad_ear):
        parts.append(plate_xz(ear_section(x0, x1, z0, z1), y_back + p.mount_wall_t, p.mount_wall_t))
        parts.append(box(x0 - p.wall_t, x1 + p.wall_t, y_back, y_back + p.mount_wall_t + 22, -p.floor_t, 0))
    cheek_len = 20.0
    for (x0, x1, _, z1) in (arm_ear, pad_ear):
        tri = CS([[[0, 0], [cheek_len, 0], [3.0, z1 - 8], [0, z1 - 8]]])
        xc = x1 - 1 if x1 > 0 else x0 - p.wall_t + 1
        parts.append(M.extrude(tri, p.wall_t).transform([[0, 0, 1, xc], [1, 0, 0, y_back + p.mount_wall_t], [0, 1, 0, 0]]))
    return parts


def carrier(p):
    if p.lights == "projectors":
        return carrier_projectors(p)
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
        if p.pocket_front_open:
            # no front wall: the side walls stop 0.5 mm past the foot's front at full forward
            # travel, leaving room for the light blade along the bezel's bottom edge
            y_cut = ly1 + fwd - 1.25
            cup = cup - CS.hull_points([pose_pt(pose, lx, ly) for lx in (-80, 80) for ly in (y_cut, 60)])
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
        # (Y offset, Z) profile: a gusset with a 3 mm flat top rather than a knife-edge point
        tri = CS([[[0, 0], [cheek_len, 0], [3.0, z1 - 8], [0, z1 - 8]]])
        xc = x1 - 1 if x1 > 0 else x0 - p.wall_t + 1          # outboard edge, 1 mm into the tab
        g = M.extrude(tri, p.wall_t).transform(
            [[0, 0, 1, xc],
             [1, 0, 0, y_back + p.mount_wall_t],
             [0, 1, 0, 0]])
        parts.append(g)

    # floor out beside the outer pods, tying into the tab floor (the bezel no longer screws to the
    # carrier, so the old screw bosses and upright plates here are gone: they left thin slivers)
    for (xa, xb) in wing_boss_x(p):
        parts.append(box(xa, xb, -89, p.wing_screw_y + 7, -p.floor_t, 0))

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
    poses = pod_layout(p)
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
    n_n = min(g0) + 7                                    # the taper ends ahead of the groove, clear of the bar's ends
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

def door_imprint(p, name):
    """The imprint the stock ear sits in on the door's side flange ("hood" or "fender"), from
    cover_sides.json: the step along its top edge (under the flange's raised band), and the
    recessed surface below it. Returns (ear_top(y), inside(y, z) as |x|, rear end y, lowest z)."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        im = json.load(fh)[name]["imprint"]
    st = np.asarray(im["step"], float)
    order = np.argsort(st[:, 0])
    sy, sz = st[order, 0], st[order, 1]
    # a fair curve: smoothed, but never above the step itself
    pad = np.pad(sz, 4, mode="edge")
    lo = np.array([pad[i:i + 9].min() for i in range(len(sz))])
    pad = np.pad(lo, 4, mode="edge")
    sz = np.minimum(np.array([pad[i:i + 9].mean() for i in range(len(sz))]), sz)
    k = np.asarray(im["recess_fit"], float)
    off = im["recess_clear"] + p.ear_gap

    def ear_top(y):
        return np.interp(y, sy, sz) - p.ear_step_gap

    def inside(y, z):
        y, z = np.asarray(y, float), np.asarray(z, float)
        return k[0] + k[1] * y + k[2] * z + k[3] * y * y + k[4] * y * z + k[5] * z * z + off
    return ear_top, inside, float(im["end_y"]), float(im["recess_zmin"])


def door_reach_measured(p, name):
    """How far out (|x|) the door itself reaches at (y, z) on one side, straight from the measured
    map in cover_sides.json (4 mm cells, the largest of the cells round the point; 0 where there's
    no door), without the filling door_side adds."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        d = json.load(fh)[name]
    ys, zs = np.asarray(d["y"]), np.asarray(d["z"])
    X = np.nan_to_num(np.array([[np.nan if q is None else q for q in row] for row in d["x"]], float), nan=0.0)

    def reach(y, z):
        fy = np.clip((np.asarray(y, float) - ys[0]) / (ys[1] - ys[0]), 0, len(ys) - 1.001)
        fz = np.clip((np.asarray(z, float) - zs[0]) / (zs[1] - zs[0]), 0, len(zs) - 1.001)
        i, j = fy.astype(int), fz.astype(int)
        return np.maximum.reduce([X[i, j], X[i + 1, j], X[i, j + 1], X[i + 1, j + 1]])
    return reach


def door_rim(p, name, inset=False):
    """The door's edge along the bezel's corner and side ("hood" or "fender"), from
    cover_sides.json "rim": the lowest point of its outer skin at each fore-aft position y.
    Returns rim(y); lightly smoothed, never above the measured edge. With inset=True, returns
    instead how far in from the bezel's outside face the edge is, as a function of y."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        side = json.load(fh)[name]
    r = np.asarray(side.get("rim") or side["imprint"]["step"], float)   # the step until cover_scan has run
    r = r[np.argsort(r[:, 0])]
    if inset:                                            # how far inside the bezel's outside the edge is
        ins = r[:, 2] if r.shape[1] > 2 else np.zeros(len(r))
        return lambda y: np.interp(y, r[:, 0], ins)
    ry = np.arange(r[0, 0], r[-1, 0], 1.0)
    rz = np.interp(ry, r[:, 0], r[:, 1])
    pad = np.pad(rz, 2, mode="edge")
    rz = np.minimum(np.array([pad[i:i + 5].mean() for i in range(len(rz))]), rz)

    def rim(y):
        return np.interp(y, ry, rz)
    return rim


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


def door_outline_side(p, name):
    """The door's outline from above along one side, as rows (y, |x| of its widest point), from
    cover_sides.json "sil". None before cover_scan has recorded it."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        side = json.load(fh)[name]
    return np.asarray(side["sil"], float) if "sil" in side else None


def door_flange(p, name):
    """The door's flange below its edge on one side, from cover_sides.json "flange": returns
    (reach(y, z) -> |x|, the largest within 1 mm, 0 where there's none; y0; z0; the raw 1 mm
    grid), or None before cover_scan has recorded it."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        side = json.load(fh)[name]
    if "flange" not in side:
        return None
    f = side["flange"]
    X = np.array([[np.nan if q is None else q for q in row] for row in f["x"]], float)
    Xz = np.nan_to_num(X, nan=0.0)
    Xd = Xz.copy()
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            Xd = np.maximum(Xd, np.roll(np.roll(Xz, di, 0), dj, 1))
    y0, z0 = f["y0"], f["z0"]

    def reach(y, z):
        i = np.clip(np.rint(np.asarray(y, float) - y0).astype(int), 0, Xd.shape[0] - 1)
        j = np.clip(np.rint(np.asarray(z, float) - z0).astype(int), 0, Xd.shape[1] - 1)
        return Xd[i, j]
    return reach, y0, z0, X


def door_outline(p):
    """The door's whole outline from above (a CrossSection), from cover_sides.json "outline"."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        d = json.load(fh)
    if "outline" not in d:
        return None
    q = np.asarray(d["outline"], float)
    if np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1]) < 0:
        q = q[::-1]
    return CS([q])


def door_plane(p, name):
    """The door's side ("hood" or "fender") as a flat vertical plane, from cover_sides.json:
    returns (a, b, clear) for |x| = a + b y, and how far anything on the flange under the door's
    edge stands out past it."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        side = json.load(fh)[name]
    if "plane" in side:
        return side["plane"][0], side["plane"][1], side["plane_clear"]
    # until cover_scan has fitted it: straight back, on the imprint's recess
    _, inside, _, _ = door_imprint(p, name)
    y_k = p.ear_start_y[0 if name == "hood" else 1]
    return float(inside(y_k, 30.0)), 0.0, -p.ear_gap


def shell_plan(p):
    """The shell's outline from above.

    The front follows the curved front line. At each end it turns back round a corner_r radius
    into a flat side that lies ear_gap outside the door's side (its flange's plane, clearing
    everything on it) and runs straight back past the last screw hole to the tip. Returns the
    outer outline (closed far behind) and per side: the corner's tangent u on the front, its
    start p0, where the arc meets the side (arc_end_y), the side's outer line |x| = A + B y,
    and where it ends (y_end)."""
    F = front_frame(p)
    R = p.corner_r
    front_pts = lambda u: _fpt(F, u, float(bow(p, u)))
    sides = {}
    for name, sx in (("hood", -1), ("fender", 1)):
        holes, reach, door_top = door_side(name)
        _, _, y_end, z_low = door_imprint(p, name)
        a, B, clear = door_plane(p, name)
        A = a + clear + p.ear_gap + p.shell_t                # outside of the side
        sil = door_outline_side(p, name)
        S_y = S_x = None
        if sil is not None:
            # just inside the door's outline from above, so none of the side shows past it
            o_ = np.argsort(sil[:, 0])
            S_y, raw = sil[o_, 0], sil[o_, 1] - p.outline_gap
            pad = np.pad(raw, 2, mode="edge")
            S_x = np.minimum(np.array([pad[i:i + 5].mean() for i in range(len(raw))]), raw)
            m_ = (S_y < -20.0) & (S_y > y_end + 8.0)
            B = float(np.polyfit(S_y[m_], S_x[m_], 1)[0])
            A = float(np.min(S_x[m_] - B * S_y[m_]))

        def corner(A, B):
            nv = np.array([sx, -B]) / math.hypot(1.0, B)     # the side's outward normal

            def dist(q):                                     # signed, + outside the side
                return (sx * q[0] - A - B * q[1]) / math.hypot(1.0, B)

            # the arc of radius R tangent to the front curve and to the side
            def centre(u):
                h = 0.5
                t = front_pts(u + h) - front_pts(u - h)
                t /= np.linalg.norm(t)
                n_in = np.array([t[1], -t[0]])               # pointing back from the front
                if n_in @ np.array([-F[0][1], -F[1][1]]) < 0:
                    n_in = -n_in
                return front_pts(u) + R * n_in
            lo, hi = (0.0, -250.0) if sx < 0 else (0.0, 250.0)   # lo: centre inside; hi: outside
            for _ in range(60):
                mid = (lo + hi) / 2
                if dist(centre(mid)) + R > 0:
                    hi = mid
                else:
                    lo = mid
            u_t = (lo + hi) / 2
            c = centre(u_t)
            return nv, u_t, c
        nv, u_t, c = corner(A, B)
        T = c + R * nv
        if S_x is not None:
            # the corner runs into a line fitted to the outline just behind it, then the side
            # follows the outline itself
            w_ = (S_y > T[1] - 30.0) & (S_y < T[1] + 2.0)
            B = float(np.polyfit(S_y[w_], S_x[w_], 1)[0])
            A = float(np.min(S_x[w_] - B * S_y[w_]))
            nv, u_t, c = corner(A, B)
            T = c + R * nv

            def side_x(y, A=A, B=B, T_y=float(T[1]), S_y=S_y, S_x=S_x):
                y = np.asarray(y, float)
                w = np.clip((T_y - y) / 20.0, 0, 1)
                w = w * w * (3 - 2 * w)
                s_ = np.interp(y, S_y, S_x)
                return np.minimum((1 - w) * (A + B * y) + w * s_, np.where(y < T_y, s_, 1e9))
        else:
            def side_x(y, A=A, B=B):
                return A + B * np.asarray(y, float)
        p0 = front_pts(u_t)
        a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
        a1 = math.atan2(nv[1], nv[0])
        if sx > 0:
            while a0 < a1:
                a0 += 2 * math.pi
            while a0 - a1 > 2 * math.pi:
                a0 -= 2 * math.pi
        else:
            a1 %= 2 * math.pi
            while a0 > a1:
                a0 -= 2 * math.pi
            while a1 - a0 > 2 * math.pi:
                a0 += 2 * math.pi
        arc = [c + R * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(a0, a1, 24)]
        side = [np.array([sx * float(side_x(y)), y]) for y in np.arange(T[1] - 1, y_end - 20, -2.0)]
        sides[name] = dict(sx=sx, u_t=u_t, p0=p0, arc_end_y=float(T[1]), y_end=y_end, z_low=z_low,
                           A=A, B=B, side_x=side_x, path=arc + side, holes=holes, door_top=door_top,
                           arc_c=c, arc_a=(a0, a1), T=T, nv=nv)
    hood, fen = sides["hood"], sides["fender"]
    fr = [front_pts(u) for u in np.linspace(hood["u_t"], fen["u_t"], 80)]
    outline = hood["path"][::-1] + fr[1:-1] + fen["path"]
    outline += [np.array([fen["path"][-1][0], -600.0]), np.array([hood["path"][-1][0], -600.0])]
    return np.asarray(outline)[::-1], sides              # counter-clockwise


def _clean_cs(cs, tol=0.05):
    """The same outline with any points closer than tol to the one before dropped (rounding
    offsets can leave near-duplicates, which pinch the solid)."""
    polys = []
    for q in cs.to_polygons():
        q = np.asarray(q)
        keep = [q[0]]
        for pt in q[1:]:
            if np.linalg.norm(pt - keep[-1]) > tol:
                keep.append(pt)
        if np.linalg.norm(keep[-1] - keep[0]) <= tol:
            keep.pop()
        if len(keep) >= 3:
            polys.append(np.asarray(keep))
    return CS(polys)


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

    # --- windows: one per pod, the pod's face plus window_clear_x each side and window_clear_y
    # top and bottom (the 1-notch test frame), corners rounded to match. Cut straight ahead
    # from each pod, the way it faces; the posts are what's left between them ---
    ww, wh = p.pod_face_w + 2 * p.window_clear_x, p.pod_face_h + 2 * p.window_clear_y
    wr = p.window_corner_r
    fx_ = np.arange(-170.0, 171.0, 2.0)
    fy_ = np.array([bezel_front_y(p, x_) for x_ in fx_])
    front_at = lambda x_: np.interp(x_, fx_, fy_)
    zc_ = pod_zc(p)
    poses_ = pod_poses(p)

    def flare(d, E):                                     # a long quarter-ellipse: E at the front, 0 by sleeve_flare_len back
        q = 1 - np.clip(d / p.sleeve_flare_len, 0, 1)
        return E * (1 - np.sqrt(np.clip(1 - q * q, 0, 1)))

    def flared(i, px, w, h, r, y_of):
        """A rounded rectangle round pod i, carried from its face to the front, opening out
        with a round curve at the front: sleeve_flare at the top and outer ends, less at the
        bottom, and just a little between neighbouring pods so the posts stay."""
        e_l = p.sleeve_flare_end if i == 0 else p.sleeve_flare_between
        e_r = p.sleeve_flare_end if i == len(poses_) - 1 else p.sleeve_flare_between
        pr = M.extrude(rrect(w, h, r).translate([px, zc_]), 1.0).refine_to_length(1.5)

        def fw(v):
            out = np.empty_like(v)
            x, z = v[:, 0], v[:, 1]
            y = y_of(x, 1.0 - v[:, 2])                  # (reversed, or the solid comes out inside out)
            d = front_at(x) - y
            ex = np.where(x > px, flare(d, e_r), flare(d, e_l))
            ez = np.where(z > zc_, flare(d, p.sleeve_flare), flare(d, p.sleeve_flare_bottom))
            out[:, 0] = px + (x - px) * (w / 2 + ex) / (w / 2)
            out[:, 2] = zc_ + (z - zc_) * (h / 2 + ez) / (h / 2)
            out[:, 1] = y
            return out
        return pr.warp_batch(fw).transform([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
    wins, sleeves = [], []
    for i, (px, py, yaw) in enumerate(poses_):
        # the window: from just behind the pod's face out past the front
        wins.append(flared(i, px, ww, wh, wr, lambda x, t, py=py: py - 0.5 + t * 60.0 + 0 * x))
        # a sleeve round it from the front back past the pod's face, so it wraps the pod
        sleeves.append(flared(i, px, ww + 2 * p.sleeve_t, wh + 2 * p.sleeve_t, wr + p.sleeve_t,
                              lambda x, t, py=py: py - p.sleeve_back + t * (front_at(x) - 0.05 - py + p.sleeve_back)))
        # behind the face the pod's body passes through: its own shape, the same gaps round it
        body = rrect(p.pod_body_w + 2 * p.window_clear_x, p.pod_body_h + 2 * p.window_clear_y, 1.0).translate([px, zc_])
        wins.append(M.extrude(body, 80.0).transform([[1, 0, 0, 0], [0, 0, 1, py - 80.0 - 0.2], [0, 1, 0, 0]]))
    windows = M.batch_boolean(wins, m3d.OpType.Add)

    front = lift_top(p, front)
    windows = lift_top(p, windows)

    # --- each corner and side: one thin wall round the corner and straight back along the
    # door's side to the tip, its top on the door's edge ---
    walls2d = CS([outline]) - CS([outline]).offset(-t, m3d.JoinType.Miter)
    walls = []
    bosses, holes, trims, ledges, win_caps, pockets = [], [], [], [], [], []
    for s_ in (hood, fen):
        sx = s_["sx"]
        u_end = np.linspace(s_["u_t"], s_["u_t"] + sx * 45, 10)
        wall_top = z_top + float(np.max(top_rise(p, u_end)))
        y_c, y_end = s_["arc_end_y"], s_["y_end"]
        rim = door_rim(p, "hood" if sx < 0 else "fender")
        # the top edge follows the door's edge all the way round the corner and back to the tip
        # (rim_gap under it). Only the first part of the corner, where the blade and bead come
        # round from the front, is allowed higher, fading out by rim_fade of the way round
        y0 = float(s_["p0"][1])
        y_f = y0 - p.rim_fade * (y0 - y_c)
        lift_a = max(0.0, wall_top + p.bead_r + 0.5 - (float(rim(y0)) - p.rim_gap))

        def trim_z(y):
            y = np.asarray(y, float)
            if p.rim_fade <= 0:
                return rim(y) - p.rim_gap
            w = np.clip((y - y_f) / (y0 - y_f), 0, 1)
            return rim(y) - p.rim_gap + w * w * (3 - 2 * w) * lift_a

        def top_z(y):                                    # built a little proud, trimmed to trim_z below
            return np.minimum(wall_top, trim_z(y) + 0.3)

        # the tip: where the door's edge comes lowest at the back of its side. The bottom edge runs
        # level round the corner, then straight back to it (the line of the door's bottom edge),
        # rounded into the level over the first 12 mm
        yy_ = np.arange(y_end - 15.0, y_end + 12.0, 0.5)
        y_t = float(yy_[np.argmin(rim(yy_))])
        z_be = float(trim_z(y_t))
        s0, L_ = 12.0, y_c - y_t

        def bot_z(y):
            d = np.clip(y_c - np.asarray(y, float), 0, None)
            return z_lb + (z_be - z_lb) * np.where(d < s0, d * d / (2 * s0), d - s0 / 2) / (L_ - s0 / 2)
        x_t = float(s_["p0"][0])                         # where the corner leaves the front
        keep = CS.square([400, 800]).translate([x_t - 400 + 0.2 if sx < 0 else x_t - 0.2, min(y_end, y_t) - 10])
        ring = M.extrude(walls2d ^ keep, 1.0).refine_to_length(3.0)

        def fw(v):
            out = v.copy()
            zb = bot_z(v[:, 1])
            out[:, 2] = zb + v[:, 2] * (top_z(v[:, 1]) - zb)
            return out
        walls.append(ring.warp_batch(fw))
        # side view of it all beyond the corner's start: top on trim_z, the tip rounded. Anything
        # outside that (walls, blade ends, bead) comes off
        ys_ = np.linspace(y0 + 40.0, y_t, 260)
        prof = np.array([[y, float(trim_z(y)) + 0.6] for y in ys_] + [[y, float(bot_z(y)) - 0.5] for y in ys_[::-1]])
        if np.sum(prof[:, 0] * np.roll(prof[:, 1], -1) - np.roll(prof[:, 0], -1) * prof[:, 1]) < 0:
            prof = prof[::-1]
        prof = _clean_cs(CS([prof]).offset(-3, m3d.JoinType.Round).offset(3, m3d.JoinType.Round))
        outside = CS.square([y0 + 30.0 - (y_end - 60.0), 500.0]).translate([y_end - 60.0, -100.0]) - prof
        x_a = x_t if sx > 0 else x_t - 250.0
        trims.append(M.extrude(outside, 250.0).transform([[0, 0, 1, x_a], [1, 0, 0, 0], [0, 1, 0, 0]]))
        # the top: everything above trim_z comes off, blending in over 25 mm from the front so
        # there's no step where the corner starts
        hx0 = x_t
        hf = M.cube([275.0, y0 + 40.0 - (y_t - 20.0), 1.0]).translate([hx0 if sx > 0 else hx0 - 275.0, y_t - 20.0, 0])
        hf = hf.refine_to_length(1.0)

        def fh(v, trim_z=trim_z, hx0=hx0, sx=sx, y0=y0, y_c=y_c):
            out = v.copy()
            w = np.clip(np.maximum(sx * (v[:, 0] - hx0) / 25.0, (y0 - v[:, 1]) / max(y0 - y_c, 1.0)), 0, 1)
            z_ = trim_z(v[:, 1]) + (1 - w * w * (3 - 2 * w)) * 8.0
            out[:, 2] = np.where(v[:, 2] < 0.5, z_, 450.0)
            return out
        trims.append(hf.warp_batch(fh))
        # round the corner the end window stops window_under the door's edge, leaving a solid band
        # under it with nothing to see through
        wq = np.array([[y, float(trim_z(y)) - p.window_under] for y in ys_] + [[ys_[-1], 400.0], [ys_[0], 400.0]])
        if np.sum(wq[:, 0] * np.roll(wq[:, 1], -1) - np.roll(wq[:, 0], -1) * wq[:, 1]) < 0:
            wq = wq[::-1]
        win_caps.append(M.extrude(CS([wq]), 250.0).transform([[0, 0, 1, x_a], [1, 0, 0, 0], [0, 1, 0, 0]]))
        # the door's lip sits inside the wall, most at the corner: a thin shelf along the inside of
        # the wall's top, just under the lip, runs round the corner and back along the side from
        # the wall to shelf_under past the lip, so there's no gap under the door's edge to see
        # through. It narrows wherever the door's flange hangs down beside the wall
        if p.shelf_t > 0:
            inset = door_rim(p, "hood" if sx < 0 else "fender", inset=True)
            reach = door_reach_measured(p, "hood" if sx < 0 else "fender")
            cen, (ga0, ga1), T_, nv_ = np.asarray(s_["arc_c"]), s_["arc_a"], np.asarray(s_["T"]), np.asarray(s_["nv"])
            R_ = p.corner_r
            L_arc = R_ * abs(ga1 - ga0)
            tan_ = np.array([nv_[1], -nv_[0]])
            tan_ = tan_ if tan_[1] < 0 else -tan_                     # along the side, heading back
            y_stop = max(y_t + 30.0, T_[1] - 45.0)                   # round the corner and a little way back: the lip sits at the wall further back
            L_side = T_[1] - y_stop                                 # along the side, by fore-aft distance
            sxf = s_["side_x"]

            def path_at(sv):
                sv = np.asarray(sv, float)
                ang = ga0 + np.clip(sv, 0, L_arc) / L_arc * (ga1 - ga0)
                pa = cen + R_ * np.c_[np.cos(ang), np.sin(ang)]
                na = -np.c_[np.cos(ang), np.sin(ang)]              # inward, toward the arc's centre
                # behind the corner: on the side itself, which follows the door's outline
                yl = T_[1] - np.clip(sv - L_arc, 0, None)
                pl = np.c_[sx * sxf(yl), yl]
                dx = sx * (sxf(yl + 0.5) - sxf(yl - 0.5))           # x change per mm of y
                nl = np.c_[-sx * np.ones_like(yl), sx * dx * sx] / np.sqrt(1 + dx * dx)[:, None]
                on = (sv > L_arc)[:, None]
                return np.where(on, pl, pa), np.where(on, nl, na)
            s_top = lambda y_: rim(y_) - p.rim_gap - 0.05
            shelf = M.cube([L_arc + L_side - 1.5, 1.0, 1.0]).translate([1.5, 0, 0]).refine_to_length(1.5)   # starts just past the corner's start

            def fs(v, sx=sx, inset=inset, reach=reach, s_top=s_top):
                out = v.copy()
                P_, N_ = path_at(v[:, 0])
                y_ = P_[:, 1]
                top = s_top(y_)
                zb = top - p.shelf_t
                d_in = np.clip(inset(y_) + p.shelf_under, t - 0.2, t + 30.0)
                # keep clear of the door where it comes out beside the wall (its side flange)
                far = np.max([reach(y_ + dy, zb - dz) for dy in (-4.0, 0.0, 4.0) for dz in (4.0, 8.0, 12.0)], axis=0)
                nx = -sx * N_[:, 0]                              # how much the inward normal points in x
                lim = np.where(nx > 0.3, (sx * P_[:, 0] - (far + 1.5)) / np.maximum(nx, 0.3), 1e9)
                d_in = np.clip(np.minimum(d_in, lim), t - 0.2, None)
                f_ = v[:, 1] if sx < 0 else 1.0 - v[:, 1]       # (mirrored on the fender side, or it's inside out)
                d = (t - 0.5) + f_ * (d_in - (t - 0.5))
                xy = P_ + N_ * d[:, None]
                out[:, 0], out[:, 1] = xy[:, 0], xy[:, 1]
                out[:, 2] = zb + v[:, 2] * (top - zb)
                return out
            ledges.append(shelf.warp_batch(fs))
        # the side now sits just inside the door's outline, so where the door's flange comes out
        # toward it the inside of the wall is pocketed ear_gap clear of the flange, leaving at
        # least min_wall
        fl = door_flange(p, "hood" if sx < 0 else "fender")
        if fl is not None:
            fx, fy0, fz0, FX = fl
            sxf = s_["side_x"]
            ys_f = np.arange(max(y_t - 5.0, fy0 + 2), y_c - 1.0, 1.0)
            # where along the side the flange comes within reach of the wall, and its lowest point
            near = [(y, FX[int(round(y - fy0))]) for y in ys_f]
            seg, cur = [], []
            for y, col in near:
                hit = np.flatnonzero(np.nan_to_num(col, nan=0.0) > float(sxf(y)) - 12.0)
                if len(hit):
                    cur.append((y, fz0 + hit.min() - 2.0))
                elif cur:
                    seg.append(cur)
                    cur = []
            if cur:
                seg.append(cur)
            for sg in seg:
                if len(sg) < 2:
                    continue
                sg = [(sg[0][0] + 1.0, sg[0][1])] + sg + [(sg[-1][0] - 1.0, sg[-1][1])]
                q = np.array([[y, zl] for y, zl in sg] + [[y, float(rim(y)) + 1.37] for y, _ in sg[::-1]])
                if np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1]) < 0:
                    q = q[::-1]
                pk = M.extrude(_clean_cs(CS([q])), 1.0).refine_to_length(1.0)

                def fp(v, fx=fx, sxf=sxf, sx=sx):
                    out = np.empty_like(v)
                    y, z = v[:, 0], v[:, 1]
                    wall = sxf(y)
                    edge = np.clip(fx(y, z) + p.ear_gap, wall - 14.7, wall - p.min_wall)
                    f_ = v[:, 2] if sx > 0 else 1.0 - v[:, 2]      # (mirrored on the hood side, or it's inside out)
                    out[:, 0] = sx * (wall - 15.0 + f_ * (edge - (wall - 15.0)))
                    out[:, 1], out[:, 2] = y, z
                    return out
                pockets.append(pk.warp_batch(fp))
        # screw holes at every hole in the door's flange, with a boss filling any gap behind
        for h in s_["holes"]:
            at, nrm = np.asarray(h["at"], float), np.asarray(h["normal"], float)
            x_out = float(s_["side_x"](at[1]))
            ln = (x_out - abs(at[0])) / abs(nrm[0])
            if ln > 0.6:
                bosses.append(_along(M.cylinder(ln - 0.3, 7, 7, 32), nrm, at + 0.3 * nrm))
            holes.append(_along(M.cylinder(60, p.ear_hole_d / 2, p.ear_hole_d / 2, 24).translate([0, 0, -30]), nrm, at))
    body = M.batch_boolean([front] + walls + sleeves, m3d.OpType.Add)
    body = body - M.batch_boolean(pockets, m3d.OpType.Add)
    body = M.batch_boolean([body] + bosses, m3d.OpType.Add)
    body = body - M.batch_boolean(trims, m3d.OpType.Add)
    body = M.batch_boolean([body] + [lg - M.batch_boolean(trims + pockets, m3d.OpType.Add) for lg in ledges], m3d.OpType.Add)
    windows = windows - M.batch_boolean(win_caps, m3d.OpType.Add)
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


def door_underside(p):
    """The door's underside (less door_clear) as a function of plan position, from the owner's
    model of the door (cover_sides.json "underside"): underside(x, y) -> z, 399 where there's no
    door overhead. Also returns the map's extent (x0, x1, y0, y1). None before cover_scan has run."""
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_sides.json")) as fh:
        d = json.load(fh).get("underside")
    if not d:
        return None
    xs, ys = np.asarray(d["x"]), np.asarray(d["y"])
    Z = np.array([[np.nan if q is None else q for q in row] for row in d["z"]], float)
    Z = np.where(np.isnan(Z), 400.0, Z - p.door_clear)
    # single-cell spikes (a stray down-facing sliver of the scan, 3+ mm under both neighbours
    # along x or along y) would notch the walls and pinch the mesh: fill them from the neighbours
    Zs = Z.copy()
    for ax in (0, 1):
        lo, hi = np.roll(Z, 1, ax), np.roll(Z, -1, ax)
        spike = (Z < lo - 3) & (Z < hi - 3) & (lo < 300) & (hi < 300)
        edge = np.zeros_like(spike)
        idx = [slice(None)] * 2
        for k in (0, -1):
            idx[ax] = k
            edge[tuple(idx)] = True
        Zs = np.where(spike & ~edge, np.minimum(lo, hi), Zs)
    Z = Zs

    def under(x, y):                                     # interpolated smoothly
        fx = np.clip((np.asarray(x, float) - xs[0]) / 2, 0, len(xs) - 1.001)
        fy = np.clip((np.asarray(y, float) - ys[0]) / 2, 0, len(ys) - 1.001)
        i, j = fx.astype(int), fy.astype(int)
        a, b = fx - i, fy - j
        zz = ((1 - a) * (1 - b) * Z[i, j] + a * (1 - b) * Z[i + 1, j] + (1 - a) * b * Z[i, j + 1] + a * b * Z[i + 1, j + 1])
        zmin = np.minimum.reduce([Z[i, j], Z[i + 1, j], Z[i, j + 1], Z[i + 1, j + 1]])
        return np.where(zz > 300, 399.0, np.where(zz - zmin > 3, zmin, zz))   # at the door's edge, take its lowest
    return under, (float(xs[0]), float(xs[-1]), float(ys[0]), float(ys[-1]))


def door_clearance(p):
    """Everything above the door's underside over the front of the bezel: cut away so the door
    closes onto the bezel without touching it anywhere but its lip on the blade."""
    du = door_underside(p)
    if du is None:
        return None
    under, (x0, x1, y0, y1) = du
    # the whole width, corners included, so the top is one surface with no step where the
    # corners start
    blk = M.cube([x1 - x0, y1 - y0, 1]).translate([x0, y0, 0]).refine_to_length(1.0)
    _, sides = shell_plan(p)

    def f(v):
        out = v.copy()
        # over the last 2 mm at the back of the map it lifts clear, so that edge never sits on the part
        ramp = np.clip((y0 + 2.0 - v[:, 1]) / 2.0, 0, 1)
        # and it leaves the side walls behind the corners alone: they're trimmed to the door's
        # edge and pocketed round its flange (shell_parts), and this map is too coarse for them
        for s_ in sides.values():
            inw = s_["side_x"](v[:, 1]) - s_["sx"] * v[:, 0]          # how far inside the side's outside
            off = np.clip((p.shell_t + 1.5 - inw) / 1.5, 0, 1) * np.clip((s_["arc_end_y"] - 2.0 - v[:, 1]) / 3.0, 0, 1)
            ramp = np.maximum(ramp, off)
        out[:, 2] = np.where(v[:, 2] < 0.5, under(v[:, 0], v[:, 1]) + 20.0 * ramp, 450.0)
        return out
    return blk.warp_batch(f)


def bezel_cad_name(kind="bezel"):
    """The bezel_sdf.py output for BEZEL_STYLE: C7 (the default) keeps the plain names."""
    st = os.environ.get("BEZEL_STYLE", "C7")
    suffix = "" if st == "C7" else "_" + st
    return f"{'bezel_cad' if kind == 'bezel' else 'drl_inserts'}_passenger{suffix}.stl"


def shroud(p):
    """The bezel as one piece (passenger side as modelled): the CAD build (bezel_cad.py) when
    it's there, otherwise the older mesh build below."""
    cad = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "cad", bezel_cad_name())
    if os.path.exists(cad) and not os.environ.get("OLD_BEZEL"):
        import trimesh
        tm = trimesh.load(cad)                          # merges the STL's repeated vertices
        return M(m3d.Mesh(np.asarray(tm.vertices, np.float32), np.asarray(tm.faces, np.uint32)))
    return shroud_mesh(p)


def diffusers(p):
    """The frosted diffuser inserts for the bezel's light slots (bezel_sdf.py writes them in the
    model frame), each standing on its flat bottom edge, laid side by side for one print. None
    if the bezel has no lights."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "cad", bezel_cad_name("inserts"))
    if not os.path.exists(path):
        return None
    import trimesh
    tm = trimesh.load(path)
    pieces = [M(m3d.Mesh(np.asarray(q.vertices, np.float32), np.asarray(q.faces, np.uint32)))
              for q in sorted(tm.split(only_watertight=False), key=lambda q: -q.volume)]
    st = os.environ.get("BEZEL_STYLE", "")
    if st == "P3R":
        # R's "C" would stand with its top run in the air: cut across its leaning end, level with the
        # heads' centres, into two L's, each standing on its long run's straight edge (the top one
        # upside down)
        import bezel_styles as bs
        zc = pod_zc(p) + bs.proj_lift(st)
        cut = []
        for m in pieces:
            up, down = m.split_by_plane([0, 0, 1], zc)
            cut += [down, up.rotate([0, 180, 0])]
        pieces = cut
    out, y = [], 0.0
    for m in pieces:
        b = m.bounding_box()
        out.append(m.translate([-(b[0] + b[3]) / 2, y - b[1], -b[2]]))
        y += b[4] - b[1] + 6.0
    whole = M.batch_boolean(out, m3d.OpType.Add)
    b = whole.bounding_box()
    return whole.translate([0, -(b[1] + b[4]) / 2, 0])


def shroud_mesh(p):
    """The older bezel, built from stacked meshes."""
    body = shell_parts(p)
    cut = door_clearance(p)
    man = body if cut is None else body - cut
    # nothing past the door's outline seen from above
    ol = door_outline(p)
    if ol is not None:
        man = man ^ M.extrude(ol.offset(-p.outline_gap, m3d.JoinType.Round), 400.0).translate([0, 0, -150.0])
    # the door cut can leave a crumb of blade corner (under 1 mm3) floating clear of the shell: drop it
    keep = [pc for pc in man.decompose() if pc.volume() > 5]
    return keep[0] if len(keep) == 1 else M.batch_boolean(keep, m3d.OpType.Add)


def split_plane_u(p):
    """Where the shell is split for printing: through the middle of the hood-side post (between
    the first two lights)."""
    poses = proj_poses(p) if proj_lights(p) else pod_poses(p)
    us = [float(front_uv(p, x, y)) for (x, y, _) in poses]
    return (us[0] + us[1]) / 2


def on_bed_diagonal(man, bed=256.0):
    """Turn a long flat part about Z to whatever angle takes the least room on the bed, and centre it."""
    v = np.asarray(man.to_mesh().vert_properties)[:, :3]
    best = None
    for a in np.arange(0.0, 180.0, 0.5):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        xy = v[:, :2] @ np.array([[c, s_], [-s_, c]])
        side = max(np.ptp(xy, axis=0))
        if best is None or side < best[0]:
            best = (side, a)
    out = man.rotate([0, 0, best[1]])
    b = out.bounding_box()
    return out.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def dowel_levels(p):
    """Heights of the dowel pins across the print split. Just the one, in the floor under the
    post: the cut face is solid there. (The rail above is only 3 mm thick, too thin for a 3 mm pin,
    and the post between the tunnels is too narrow for one to run 6 mm into each half.) The
    joint's strength is the glue over the whole cut face; the pin lines the halves up."""
    return (shell_levels(p)[2] - 0.2,)


def proj_lights(p):
    """The projector set (LIGHTS=projectors, or a projector bezel style being built)."""
    import bezel_styles as bs
    return p.lights == "projectors" or bs.is_proj(os.environ.get("BEZEL_STYLE", ""))


def dowel_spot(p):
    """(u, n, heights) of the dowel pins across the print split, in the front frame. With the
    projectors the floor under the post is only 3 mm thick, so the pin goes 5 mm further back and
    a little lower, in a boss the bezel builds round it (bezel_sdf), under the heads' clearance."""
    us = split_plane_u(p)
    n_c = float(bow(p, us)) - p.post_depth / 2 - p.post_setback
    if os.environ.get("BEZEL_STYLE", "") in ("P3J", "P3D", "P3R"):
        # J: its floor is taken by the deeper recess and the light line's channel, so the pin goes up
        # in the post between the first two openings, half way up, just behind the recessed face
        return us, n_c + 1.5, (33.5,)
    if proj_lights(p):
        return us, n_c - 5.0, (4.5,)
    return us, n_c, dowel_levels(p)


SPLICE_T = 2.4          # the splice sleeve's plates (6 perimeters at 0.4 mm)
SPLICE_IN = 7.0         # how far it reaches into the fender piece
SPLICE_BACK = 6.0       # ...and how far it runs along the inside of the hood piece
SPLICE_H = 45.0         # its face plate, down from the rail's underside
SPLICE_CLEAR = 0.15     # round the fender piece's walls, so the halves slide together


def splice_sleeve(p, man, us):
    """Projector bezels: an L-shaped sleeve across the print split, on the hood piece. Its plates
    follow the inside of the face wall and the underside of the top rail at the cut, 6 mm along
    the hood piece (fused to it) and 7 mm on into the fender piece, which slides onto it: the
    halves line up in depth and height, and the joint's glue area grows several times over. Where
    the fender piece's walls wander or carry ribs and bosses within the 7 mm, the sleeve is
    trimmed to clear them all along (so it slides in) by SPLICE_CLEAR. None of it shows."""
    from matplotlib.path import Path
    F = np.array(front_frame(p))
    R, t = F[:, :3], F[:, 3]
    to_cut = (np.c_[np.eye(3)[[1, 2, 0]], [0, 0, -us]] @ np.r_[np.c_[R.T, -R.T @ t], [[0, 0, 0, 1]]])[:3]
    back = np.r_[np.c_[R, t], [[0, 0, 0, 1]]] @ np.r_[np.c_[np.eye(3)[[2, 0, 1]], [us, 0, 0]], [[0, 0, 0, 1]]]
    loc = man.transform(to_cut.tolist())                     # (n, z, u - us)
    polys = [Path(q) for q in loc.slice(0.0).to_polygons()]
    (n0, z0), (n1, z1) = loc.slice(0.0).bounds()[:2], loc.slice(0.0).bounds()[2:]
    nn = np.arange(n0 - 1, n1 + 1, 0.1)

    def solid(row):          # material along n at one height (even-odd over the section's outlines)
        pts = np.c_[nn, np.full_like(nn, row)]
        c = sum(pa.contains_points(pts).astype(int) for pa in polys)
        return c % 2 == 1

    def front_run_start(row):   # the back of the frontmost material at this height (the face's inner side)
        m = solid(row)
        if not m.any():
            return None
        i = len(m) - 1 - np.argmax(m[::-1])          # the frontmost solid cell
        while i > 0 and m[i - 1]:
            i -= 1
        return nn[i]
    # the rail's underside: the bottom of the topmost material, a little behind the face
    zz = np.arange(z0, z1, 0.1)
    n_probe = n0 + 0.4 * (n1 - n0)
    col = np.array([any(pa.contains_points([[n_probe, z]]).any() for pa in polys) for z in zz])
    i = len(col) - 1 - np.argmax(col[::-1])
    while i > 0 and col[i - 1]:
        i -= 1
    z_ru = zz[i]
    rows = np.r_[np.arange(z_ru - SPLICE_H, z_ru - SPLICE_T, 0.25), z_ru - SPLICE_T + 0.5]   # into the rail plate
    nfi = [front_run_start(r) for r in rows]
    keep = [(r, n) for r, n in zip(rows, nfi) if n is not None]
    rows, nfi = np.array([k[0] for k in keep]), np.array([k[1] for k in keep])
    n_top = nfi[-1]
    face = np.r_[np.c_[nfi + 0.3, rows], np.c_[nfi[::-1] - SPLICE_T, rows[::-1]]]
    rail = [[n0 + 3.0, z_ru - SPLICE_T], [n_top + 0.3, z_ru - SPLICE_T], [n_top + 0.3, z_ru + 0.3], [n0 + 3.0, z_ru + 0.3]]
    prof = CS([face.tolist()]) + CS([rail])
    # what it must clear, seen along the cut's normal: the fender piece's walls within its reach
    # (grown by the clearance) and the projectors (grown by 1 mm), over the whole length
    lights = lights_dummy(p).transform(to_cut.tolist())

    def clear_of_lights(u0, u1):      # the projectors' outline (1 mm round it) between u0 and u1
        return (lights ^ box(-500, 500, -500, 500, u0 - 1.0, u1 + 1.0)).project().offset(1.0, m3d.JoinType.Round)
    # into the fender piece it reaches up to SPLICE_IN, stopping 0.5 mm short of the first thing in
    # its way there besides the walls it hugs (the next tunnel's side wall, say)
    walls = loc.slice(0.05).offset(1.0, m3d.JoinType.Round)      # the walls it hugs, as they curve on
    inner = prof - walls
    hit = (loc ^ box(-500, 500, -500, 500, 0.05, SPLICE_IN + 0.5)) ^ M.extrude(inner, SPLICE_IN + 0.5)
    reach_in = SPLICE_IN if hit.is_empty() else max(2.0, min(SPLICE_IN, hit.bounding_box()[2] - 0.5))
    fender = (loc ^ box(-500, 500, -500, 500, 0.0, reach_in + 0.5)).project().offset(SPLICE_CLEAR, m3d.JoinType.Round)
    tenon = M.extrude(prof - fender - clear_of_lights(0.0, reach_in), reach_in + 0.3).translate([0, 0, -0.3])   # overlaps the root
    # on the hood piece the projectors stand at an angle to the cut, the nearest corner a few mm
    # from it: the sleeve runs the full SPLICE_BACK where it's clear of them, and all of it as far
    # back as the nearest one allows
    root = M.extrude(prof - clear_of_lights(-SPLICE_BACK, 0.0), SPLICE_BACK).translate([0, 0, -SPLICE_BACK])
    near = lights ^ M.extrude(prof, SPLICE_BACK + 1.0).translate([0, 0, -SPLICE_BACK - 1.0])
    free = SPLICE_BACK if near.is_empty() else min(SPLICE_BACK, -near.bounding_box()[5] - 1.0)
    if free > 0.5:
        root = root + M.extrude(prof, free).translate([0, 0, -free])
    return (root + tenon).transform(back[:3].tolist())


def joint_test(p, pieces, half=18.0):
    """A quick print to try the halves' fit: each piece cut 18 mm either side of the split, both
    as printed (on the top rail), side by side."""
    us = dowel_spot(p)[0]
    near = box(us - half, us + half, -2000, 2000, -500, 500).transform(front_frame(p))
    a, b = [print_orient_shroud(q ^ near) for q in pieces]
    ba, bb = a.bounding_box(), b.bounding_box()
    return a + b.translate([0, ba[4] - bb[1] + 8.0, ba[2] - bb[2]])


def split_shell(p, man):
    """The two print pieces: cut through the middle of the hood-side post, with a dowel hole
    across the cut in the floor under the post (dowel_levels), and for the projector bezels a
    splice sleeve across the cut on the hood piece (splice_sleeve)."""
    F = front_frame(p)
    us, n_c, zs = dowel_spot(p)
    pins = []
    for z in zs:
        pin = M.cylinder(2 * p.dowel_depth, p.dowel_d / 2, p.dowel_d / 2, 24, True)
        pins.append(pin.transform([[0, 0, 1, us], [1, 0, 0, n_c], [0, 1, 0, z]]))
    pins = lift_top(p, M.batch_boolean(pins, m3d.OpType.Add).transform(F))
    left = box(-2000, us, -2000, 2000, -500, 500).transform(F)
    right = box(us, 2000, -2000, 2000, -500, 500).transform(F)
    hood, fender = man ^ left, man ^ right
    if proj_lights(p):
        hood = hood + splice_sleeve(p, man, us)
        hood = M.batch_boolean([q for q in hood.decompose() if q.volume() > 1.0], m3d.OpType.Add)   # no slivers
    return hood - pins, fender - pins


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
    # the rail's top sits 1.3 mm under the lip (the bead comes up to it), so the slice starts
    # 1.3 mm lower to keep the rail's full thickness (less 0.3 mm, clear of the wall below it)
    keep = lift_top(p, box(-U - 60, U + 60, -p.clip_back - 30, p.front_bow + 8, z_top - 1.3 - p.rail_t + 0.3, z_top + 3).transform(F))
    strip = shroud(p) ^ keep
    return M.batch_boolean([pc for pc in strip.decompose() if pc.volume() > 5], m3d.OpType.Add)   # no slivers


def fit_test_mount(p):
    """Quick print: the two mounting tabs as flat 3 mm pieces, laid side by side.
    Checks the slots line up with the arm (A) and the pad (H) without anything in between."""
    pieces = []
    for (x0, x1, z0, z1) in ears(p):
        sec = ear_section(x0, x1, z0, z1)
        for (_, x, z, axis) in mount_points(p):
            ln = p.arm_slot_len if axis == "x" else p.pad_slot_len
            w = p.mount_hole_d
            sl = CS.square([ln - w, 1e-3] if axis == "x" else [1e-3, ln - w], center=True)   # w wide once offset
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
    import trimesh
    base = to_trimesh(man)
    b = base.bounds
    # centre it on the bed.  Two faces a few hundredths of a mm apart can round onto the same
    # float32 point once shifted, which pinches the STL when a slicer re-welds it: if the file
    # does not load back watertight, move the centring a few microns and write it again.
    for k in range(40):
        tm = base.copy()
        tm.apply_translation([-(b[0][0] + b[1][0]) / 2 + 0.0037 * k, -(b[0][1] + b[1][1]) / 2 + 0.0023 * k, -b[0][2]])
        tm.export(path)
        if not base.is_watertight or trimesh.load(path).is_watertight:
            break
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


def write_projector_set(here):
    """LIGHTS=projectors: the projector bracket, its straps, the bezel for BEZEL_STYLE (P3J) and
    its light line's diffusers, in stl/projectors_<style>/, with a fit-check assembly. The fit
    tests, spacers and the rest stay in stl/ (they don't change)."""
    st = os.environ.get("BEZEL_STYLE", "P3J")
    out = os.path.join(here, "stl", "projectors_" + st)
    os.makedirs(os.path.join(out, "assembled"), exist_ok=True)
    c, s = carrier(P), shroud(P)
    for side, f in (("passenger", lambda m: m), ("driver", mirror_x)):
        save(print_orient_carrier(f(c)), os.path.join(out, f"carrier_{side}.stl"))
        save(f(print_orient_shroud(s)), os.path.join(out, f"bezel_{side}_one_piece.stl"))
        pieces = split_shell(P, s)
        for tag, piece in zip(("hood_piece", "fender_piece"), pieces):
            save(f(print_orient_shroud(piece)), os.path.join(out, f"bezel_{side}_{tag}.stl"))
        save(f(joint_test(P, pieces)), os.path.join(out, f"bezel_joint_test_{side}.stl"))
        save(f(projector_straps(P)), os.path.join(out, f"projector_straps_{side}.stl"))
        dif = diffusers(P)
        if dif is not None:
            save(on_bed_diagonal(f(dif)), os.path.join(out, f"drl_diffusers_{side}.stl"))   # longer than the bed
        save(M.compose([f(c), f(s), f(projector_dummy(P))]), os.path.join(out, "assembled", f"assembly_{side}.stl"))


if __name__ == "__main__" and P.lights == "projectors":
    write_projector_set(os.path.dirname(os.path.abspath(__file__)))
elif __name__ == "__main__":
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
    # ...and in one piece: 294 mm long, it fits the A1's 256 mm bed turned diagonally (already turned)
    whole = on_bed_diagonal(print_orient_shroud(blade))
    save(whole, os.path.join(out, "fit_test_blade_passenger_one_piece.stl"))
    save(on_bed_diagonal(mirror_x(print_orient_shroud(blade))), os.path.join(out, "fit_test_blade_driver_one_piece.stl"))
    save(fit_test_mount(P), os.path.join(out, "fit_test_mount_passenger.stl"))
    save(mirror_x(fit_test_mount(P)), os.path.join(out, "fit_test_mount_driver.stl"))
    save(spacers(P), os.path.join(out, "spacer_washers.stl"))
    dif = diffusers(P)
    for side, f in (("passenger", lambda m: m), ("driver", mirror_x)):
        name = os.path.join(out, f"drl_diffusers_{side}.stl")
        if dif is not None:
            save(f(dif), name)
        elif os.path.exists(name):
            os.remove(name)
    # everything together where it goes on the car, one per side, to check the fit (not for
    # printing): carrier, bezel, and stand-ins for the three pods and their lenses
    os.makedirs(os.path.join(out, "assembled"), exist_ok=True)
    pods_, lens_ = pod_dummy(P), pod_lenses(P)
    for side, f_ in (("passenger", lambda m_: m_), ("driver", mirror_x)):
        asm = M.compose([f_(c), f_(s), f_(pods_), f_(lens_)])
        save(asm, os.path.join(out, "assembled", f"assembly_{side}.stl"))

    preview(P, os.path.join(here, "preview", "assembly.png"))
