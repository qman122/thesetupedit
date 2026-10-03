"""Face styles for the bezel, from the owner's design brief: DRL light slots, chamfered pod
frames, a recessed tray with fins, and the channels and diffuser inserts behind each light slot.

Pick one with BEZEL_STYLE (bezel_sdf.py reads it):
  A   a light blade along the top, just under the door's lip, across the three pods
  B   a raised frame with cut corners round each pod, and an L-shaped light at each outer end
      that runs down the outer edge and turns in under the outer pod
  C   the pods in one recessed tray with thin tapered fins between them, and a light bar
      along the bottom of the tray that the fins break into three
  BC  B's frames with a light bar under each pod (three segments)

Everything on the face is laid out in face coordinates: a, the arc length along the bezel's
path (its outside face seen from above), z, the height, and nn, the depth behind the outside
face (negative inward). Each light is a slot through a thin skin, a channel behind it with a
ledge round the slot for a frosted diffuser insert, and an open back for the LED strip and its
wires.

Room for the lights (measured from the model):
- Above the pods the rail leaves about 14 mm at the hood end and 6 mm at the fender end, so
  the top blade follows the door's lip and stops short of the fender pod's outer corner,
  where that pod comes within about 3 mm of the face.
- Below the pods there are only about 7.5 mm between the bracket's floor (z = 0) and the pods'
  bottom edge (z = 7.6), so the lower lights use a slimmer channel and the bezel's bottom edge
  comes down 2.6 mm (to z = 0.4) to carry it.
"""
from functools import reduce

import os
import numpy as np
from scipy.spatial import cKDTree

SQ2 = np.sqrt(2.0)


def slab(nn, lo, hi):
    return np.maximum(lo - nn, nn - hi)


def iround(a, b, r):
    """Intersection of two fields with the edge between them rounded by r (no sharp creases:
    the mesher and its clean-up passes need every edge round)."""
    u, v = np.maximum(r + a, 0), np.maximum(r + b, 0)
    return np.minimum(-r, np.maximum(a, b)) + np.hypot(u, v)


class Spec:
    """One size of light channel. slot: visible slot height; inner: channel height (the diffuser
    insert's height); wall: channel walls; skin: the face in front of the diffuser; depth: the
    channel behind the skin (diffuser plus LED strip); insert: diffuser thickness."""
    def __init__(self, slot, inner, wall, skin, depth, insert, front=False, closed=0.0):
        self.slot, self.inner, self.wall, self.skin, self.depth, self.insert = slot, inner, wall, skin, depth, insert
        self.front = front     # front-loading: no lip, the diffuser presses in flush with the face
        self.closed = closed   # a back wall this thick behind the channel (for strips below the floor,
                               # which would otherwise have nothing behind them)


# top blade: a 3.5 mm slot, 6 mm diffuser 2 mm thick, room for a 5 mm COB strip behind it
TOP = Spec(slot=3.5, inner=6.0, wall=1.5, skin=2.0, depth=5.0, insert=2.0)
# lower lights: a 3 mm slot, 4.2 mm diffuser 1.5 mm thick, for a 4 mm COB strip
LOW = Spec(slot=3.0, inner=4.2, wall=1.0, skin=1.6, depth=4.0, insert=1.5)
# C7's light blade, front-loading: its channel is closed at the back by the bezel's floor, so
# the 4 mm LED strip sticks to the channel's back and the diffuser presses in flush from the front
BLADE = Spec(slot=4.2, inner=4.2, wall=1.0, skin=0.0, depth=3.8, insert=1.5, front=True)
BLADE_FLUSH = 0.3    # the diffuser's face sits this far behind the bezel's
WIRE_R = 1.3         # wire hole from the blade's channel out underneath
LOW_Z = 3.6          # the lower lights' centre line: walls from 0.5 (bracket floor at 0) to 6.7 (pods at 7.6)
PROJ_W, PROJ_H = 55.0, 48.0   # P3: the owner's mini 2.0 in bi-LED projector, head face on (eBay listing's size drawing)
PROJ_LIP = (1.5, 1.0)  # the bezel's opening is this much smaller than the head's face (side, top and bottom):
                       # it frames the face (the lens, about 44 mm, stays clear) and hides the gap round it
PROJ_X = (-75.0, 0.75, 76.5)  # head centres: the fender one 8 mm in from the pod's place, so its body clears the
                              # arm's mounting tab; the hood one far enough in that its body clears the aiming
                              # pad's square adjuster; the middle one halfway, for even gaps
# four heads (P4 looks): evenly spaced from the hood corner to where the fender-side body just
# clears the arm's tab (0.8 mm), each front 4 mm behind the bezel's face across its width
PROJ4 = ((-101.0, 24.3), (-41.67, 18.5), (17.67, 9.7), (77.0, -3.6))
# P3J (the owner's reference render, "the goal": three in a line with the bold strip under them
# wrapping up round the outer end): spread as far as the car allows, like the render's close-up
# (the hood one's body clears the pad's square adjuster, the fender one's the arm's tab), each
# front 4 mm behind the face across its width (the face as PROJ4 found it)
PROJ3J = ((-75.0, 21.8), (0.75, 12.2), (76.5, -3.5))
# P3C (C7 look): the heads where P3J's were
PROJ3C = PROJ3J
# J now brings its heads forward, so they stand proud of the light face: each front 0.5 mm behind the
# bezel's original face line at its tightest edge (the face sits at the door's outline, and the whole
# assembly swings down into the body when the lights close, so nothing goes past that line); the
# light face is recessed deeper (EYELID_J) to leave them standing forward of it
J_FWD = 3.5
PROJ3J_FWD = tuple((x, y + J_FWD) for x, y in PROJ3J)
J_LIP = (-2.0, -0.75)   # J's openings: an even gap round each head (2 mm each side, 0.75 top and bottom,
                        # the same as its clearance behind), so it can stand through them
EYELID_J = 5.0
J_OPEN_R = 3.0          # the openings' corners
P3C_STRIP_Z = 2.5    # P3C: the bold strip's bottom run, its walls from -3.5 to 8.5, just under the housing
P3C_CHIN = -4.0      # ...and the bottom edge under it
P3C_TRAY_BOTTOM = 9.0   # the housing's bottom edge: the windows' bottoms
P3C_TRAY_HOOD_X = -129.0  # ...its hood end, where P4's first window ends (the hood-side head can't go further
                          # that way: its body would reach the pad's square adjuster)
# P3J's light line: a thin strip (5 mm, like a modern car's), the face's full width, kicking up at
# both ends at crisp corners (in three pieces of strip, or one that bends that tight edgeways)
THIN = Spec(slot=5.0, inner=5.0, wall=1.0, skin=0.0, depth=7.0, insert=6.0, front=True, closed=1.5)
# ...now 8 mm, behind a frosted diffuser pressed in flush (printed, drl_diffusers_*.stl): the strip
# (a flat COB strip or a side-bend neon, up to 5 mm thick) sits behind it, and its joins don't show
DIFF = Spec(slot=8.0, inner=8.0, wall=1.0, skin=0.0, depth=8.0, insert=2.5, front=True, closed=1.5)
SW_HOOD = (-139.0, 21.0)   # the swoosh's hood end: on the face where it turns into the corner, a third of the way up
SW_SIDE = ((508.0, 2.5), (522.0, 3.5), (533.0, 7.0), (540.0, 13.0), (545.0, 19.0), (549.0, 24.0), (554.0, 26.5), (561.0, 27.0))
                           # ...and its fender end, (arc position, z): round the corner low, then up the side
                           # panel; the door's side flange sits ~4 mm behind the panel above z ~30 from
                           # here back, so the line (9.5 mm deep) can't go higher or further back
HOOK_GAP = 1.2       # the light line's hook wraps the outer pocket's bottom corner on the same centre,
                     # with this much plastic between the channel's wall and the pocket
THIN_Z = 3.0         # its bottom run: walls from -0.5 to 6.5 (the pockets' chamfered bottoms end at 8)
THIN_CHIN = -1.2     # the bottom edge under it
STRIP_HOOD_X = -146.0   # the inner kick-up, on the hood-side corner itself (the line runs the full length)
KICK_IN = (3.0, 24.0)   # ...leaning 3 mm toward the corner, up to z 24
HOOK_CURVE_R = 36.0  # the outer end's J: its radius on the centre line (the bigger, the easier on the strip)
KICK_IN_R = 10.0     # ...and the inner kick-up's
WRAP = 46.0          # the bottom run carries on round the fender-side corner onto the side, this much
                     # further along the face than past the fender head (it bends the easy way there)
KICK_OUT = (6.0, 44.0)  # ...and kicks up on the side, swept 6 mm back, up to z 44 (well short of the ear's
                        # screw boss, 40 mm further back)
EYELID = 2.0         # P3J: the whole light face (pockets and line) sits this far back in a recess under the top
                     # rail, so the rail overhangs it like an eyelid
EYELID_BOTTOM, EYELID_TOP = -2.7, (5.0, 58.0)   # the recess: from just under the light line up to 5 mm under
                                                # the rail's top (at most z 58); a 1 mm lip stays below it
EYELID_CHIN = -3.7   # the bottom edge under it
POCKET_R = (4.0, 8.0)   # the pockets' top corners: rounded 4 mm at the head (clear of the lens) to 8 at
                            # the face
POCKET_CHAMFER = (8.0, 1.5, 0.0)   # P3J's pockets at the face: this much wider each side and deeper at
                                   # the bottom than at the head, in flat chamfers; none at the top,
                                   # which stays a straight, sharp brow over the lenses
# P3V (the owner's concept sheet): J's heads, pockets and recess, with a 4 mm light line in a W under
# them (humps between the pockets), a diagonal leg at the fender end that stops before the tight
# corner, and a sweep up and round the curved corner at the hood end
LINE4 = Spec(slot=5.0, inner=5.0, wall=1.0, skin=0.0, depth=7.0, insert=2.0, front=True, closed=1.5)
V_LEG = (-15.0, 40.0)     # the fender leg leaves the outer pocket's corner at this angle (deg), up to z 42
V_HOOD = (-140.0, 18.0, 6.0, 44.0)   # the hood end: turns up at x -140, radius 18, leaning 6 mm round
                                     # the corner, up to z 44
V_HUMP = 35.0             # each hump leaves the pockets' corners at this angle (deg) and peaks between them
V_CHAMFER = (5.0, 1.5, 0.0)   # V's pockets: smaller side bevels than J's, for wider posts to hump between
# P3D (the owner's "dual straight DRL" concept): two light bars, one above the projectors and one
# below, wrapping round onto the hood-side face and stopping before the tight fender corner; the
# bezel's face covers each head, with a round hole for its lens. The heads sit 3 mm lower than J's
# so a bar fits between them and the rail (the top bar follows the rail, 3 mm under it), and their
# fronts are 1.8 mm behind the face (a 1.5 mm skin over each head's face)
RAIL_T = 3.0             # the top rail's thickness (generate.Params.rail_t)
D_LIFT = -3.0            # the heads' height, against the pods' (J and W: PROJ_LIFT)
PROJ3D = tuple((x, y + 2.2) for x, y in PROJ3J)
LENS_D = 42.0            # the lens's visible diameter (MEASURE: the 2.0 in projector's lens; the hole follows it)
LENS_GAP = 2.0           # round the lens, in its hole (the misalignment clearance)
LENS_BEVEL = 2.0         # the holes' edges bevelled this much wider at the face
D_BAR_UNDER_RAIL = 3.0   # the top bar's centre line, this far under the rail's underside
D_BOTTOM_Z = -1.2        # the bottom bar's centre line (straight)
D_SQUINT = (-115.0, -145.0, 35.0, 8.0)   # the "mean" squint: the top bar runs level across the heads
                                         # (as low as the rail at the fender end allows), then,
                                         # past the hood-side head, angles down 35 degrees from
                                         # x -115 to x -145 round a radius 8 bend...
D_SQUINT_LOW = (-115.0, -145.0, 30.0, 8.0)   # ...and the bottom bar angles up 30 degrees over the same
                                             # stretch, so the eye tapers to its inner corner
D_ENDS = (190.0, 486.0)  # where both bars end (arc position): 25 mm round onto the hood-side face (the
                         # door's side flange is close behind it further round), and before the tight
                         # fender corner
# P3R (the owner's Audi R8-style board): D's face and lens holes, with one light line in a "C" round
# the heads: along the top, down a leaning, round-cornered end at the fender side, and back along
# the bottom, open toward the hood, the bottom run reaching further in (round onto the hood-side
# face) than the top one
R_LIFT = -3.6            # the heads a little lower than D's, so the top run clears them where it
                         # rounds the fender-side corner (the rail drops toward the fender corner)
R_TOP_IN = -118.0        # the top run's inner end (x, head on)
R_CORNER = (116.0, 106.0, 10.0)  # the leaning end: its top corner at x 116, its bottom corner at x 106,
                                 # both round radius 10
R_CLEAR = 1.3            # each run's slot clear of the lens holes' bevels by this much
R_REC = 4.0              # inside the C the face steps back this far (a housing round the lenses), its ends
                         # leaning with the C's: the light line runs round it on a raised frame
R_REC_IN = 4.5           # the step this far inside the line's centre (2 mm of wall to its channel)
R_REC_R = 6.0            # the recess's corner radius
R_FIN = (1.2, 1.6, 2.6)  # a blade between each two lenses, leaning with the ends: its front edge 1.2 mm behind
                         # the face, 3.2 mm wide there, 5.2 at the floor
J_SHAPE = os.environ.get("J_SHAPE", "")      # J's sculpted face (face_relief): '', 'visor', 'scoop'
J_TEXTURE = os.environ.get("J_TEXTURE", "") == "1"   # J's honeycomb (trial)
V_SHAPE = os.environ.get("V_SHAPE", "")      # W's sculpted face (face_relief): '', 'visor', 'scoop'
R_SHAPE = os.environ.get("R_SHAPE", "")      # the face's sculpted form (R_RELIEF): '', 'visor', 'wedge', 'scoop'
R_SHAPE_BACK = {"": 0.0, "visor": 5.0, "wedge": 8.2, "scoop": 6.0}[R_SHAPE]   # its deepest over the heads
PROJ3R = tuple((x, y - R_REC - R_SHAPE_BACK) for x, y in PROJ3D)   # the heads back by as much, the same skin over each


def smoothstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def face_relief(shape, T_of_a):
    """A sculpt map for the face: how far back the face sits at (a, z). Nothing on the side panels (the door's
    screw bosses) or at the top rail (the door's lip sits on its front edge), easing in below it.
      visor: 5 mm back under the rail, which overhangs it as a brow
      wedge: raked back 7 degrees toward the bottom, the top leaning forward
      scoop: concave, 6 mm back through the middle, the top and bottom edges flaring out"""
    def f(a, z):
        wa = smoothstep(a, 195.0, 222.0) * (1.0 - smoothstep(a, 503.0, 528.0))
        T = T_of_a(a)
        wt = 1.0 - smoothstep(z, T - 10.0, T - 3.5)
        if shape == "visor":
            d = 5.0 + 0.0 * z
        elif shape == "wedge":
            d = np.clip(0.125 * (T - 3.5 - z), 0, None)
        else:
            u = np.clip((z + 7.0) / (T - 3.5 + 7.0), 0, 1)
            d = 6.0 * np.sin(np.pi * u) ** 0.7
        return wa * wt * d
    return f
# R's sculpting (the bezel's own shapes, cut into its surfaces so nothing passes the door's outline):
R_STRAKES = [((150.0, 16.0), (52.0, 23.0), 3.6),    # hood-side panel: three grooves like speed lines, rising
             ((150.0, 24.5), (66.0, 31.0), 3.6),    # toward the back, each one shorter (front end, back end,
             ((150.0, 33.0), (82.0, 38.5), 3.6)]    # width), clear of the door's screw bosses
R_STRAKE_DEPTH = 1.4     # into the 3 mm wall, with 45 degree sides
R_GILLS = (504.0, 7.5, 4, 3.0, (12.0, 50.0))   # the fender corner past the C: 4 slots from a 504, 7.5 apart,
                                               # 3 mm wide, z 12 to 50, leaning with the C
R_GILL_DEPTH = 1.4
R_HONEY = (6.5, 0.9, 0.6)    # the housing's floor: raised honeycomb, cells 6.5 mm across, ridges 0.9 wide, 0.6 high
BOLD_STYLES = ("P3J", "P4J", "P3C", "P3V", "P3D", "P3R")   # the looks with the bold strip (and the lower bottom edge)


def is_proj(style):
    return style.startswith("P3") or style.startswith("P4")


def proj_lip(style):
    """(side, top/bottom) of how much smaller each opening is than the head's face (negative: a gap)."""
    return J_LIP if style in ("P3J", "P3D", "P3R") else PROJ_LIP


def proj_lift(style):
    """How much higher than the pods the heads sit."""
    return D_LIFT if style == "P3D" else R_LIFT if style == "P3R" else PROJ_LIFT


def proj_layout(style, pod_ys):
    """(x, y of the head's front) per projector: P4 from PROJ4; P3 at PROJ_X, 1 mm behind the
    pods' faces (pod_ys)."""
    if style.startswith("P4"):
        return list(PROJ4)
    if style == "P3J":
        return list(PROJ3J_FWD)
    if style == "P3D":
        return list(PROJ3D)
    if style == "P3R":
        return list(PROJ3R)
    if style == "P3V":
        return list(PROJ3J)
    if style == "P3C":
        return list(PROJ3C)
    return [(x, py - 1.0) for x, py in zip(PROJ_X, pod_ys)]
PROJ_LIFT = 2.9      # P3: the heads sit this much higher than the pods did: z 9.5 to 57.5, between the thick strip
                     # (its walls end at 8.95) and the rail (its underside is at 59.0 over the fender head)
# P3's thick light strip: a silicone switchback (white DRL / amber signal) strip, about 6.5 mm wide
# and 6 mm thick, pressed into the channel from the front, flush; it is its own diffuser
THICK = Spec(slot=6.5, inner=6.5, wall=1.0, skin=0.0, depth=7.0, insert=6.0, front=True, closed=1.5)
THICK_Z = 4.7        # its bottom run: walls from 0.45 (just above the bracket) to 8.95 (under the windows)
# P4J's bold strip: 10 mm (a wide high-output switchback strip, up to 6.5 mm thick); the bezel's
# bottom comes down to -3.5 to carry it (the owner first marked the bottom as low as -18)
BOLD = Spec(slot=10.0, inner=10.0, wall=1.0, skin=0.0, depth=7.0, insert=6.0, front=True, closed=1.5)
BOLD_Z = 3.0         # its bottom run: walls from -3 to 9 (the windows start at 9)
BOLD_CHIN = -3.5    # the bottom edge under the bold strip
CHIN_Z = 0.4         # the bottom edge comes down to here wherever there's a lower light
INSERT_CLEAR = 0.15  # the diffuser insert is this much smaller than its channel all round

CH = 8.0             # B: cut corners on the windows (legs of the 45 degree chamfer)
FRAME_W = 4.0        # B: frame width round the sides and top of each window
FRAME_WB = 1.2       # ...and under it (the lower light runs just below)
FRAME_H = 1.5        # ...standing this far proud of the face
FRAME_BEVEL = 0.8    # the frame's inner edge is bevelled 45 degrees this deep

TRAY_RECESS = 3.0    # C: the tray steps back this far from the face
TRAY_MARGIN = 4.0    # ...and reaches this far past the outer windows
TRAY_R = 8.0         # its corner radius
RAKE = np.tan(np.radians(10.0))   # C7: windows, blades, tray ends and ladder lean 10 degrees (tops toward the fender)
C7_TRAY_BOTTOM = 7.0 # C7: the housing's bottom edge, just under the windows (the light blade runs below it)
C7_TRAY_MARGIN = 2.5 # ...its ends this far past the outer windows (and past the ladder)
C7_TRAY_R = 2.5      # ...crisp corners
C7_EDGE = 0.8        # C7: rounds on the window and tray edges (crisp)
LADDER = Spec(slot=2.2, inner=0.0, wall=1.0, skin=1.4, depth=3.6, insert=1.5)
LADDER_N, LADDER_PITCH, LADDER_RUNG, LADDER_Z0 = 6, 5.5, 7.0, 15.0
FIN_FRONT = 0.6      # C: the fins' front edges sit this far behind the face
FIN_EDGE = 0.8       # ...half their width at the front edge (1.6 mm, rounded)


class Path2D:
    """A centre line in (a, z), resampled densely; distance by nearest sample (rounded ends)."""
    def __init__(self, pts, step=0.15):
        pts = np.asarray(pts, float)
        seg = np.hypot(*np.diff(pts, axis=0).T)
        cum = np.r_[0, np.cumsum(seg)]
        s = np.unique(np.r_[np.arange(0, cum[-1], step), cum[-1]])
        self.pts = np.c_[np.interp(s, cum, pts[:, 0]), np.interp(s, cum, pts[:, 1])]
        self.tree = cKDTree(self.pts)
        self.lo, self.hi = self.pts.min(0), self.pts.max(0)

        self.s = s

    def dist(self, a, z, reach):
        """Distance from (a, z) (any broadcastable shapes) to the line, 99 beyond reach, and how
        far along the line the nearest point is."""
        shape = np.broadcast_shapes(np.shape(a), np.shape(z))
        A, Zb = np.broadcast_to(a, shape), np.broadcast_to(z, shape)
        out, along = np.full(shape, 99.0), np.zeros(shape)
        m = (A > self.lo[0] - reach) & (A < self.hi[0] + reach) & (Zb > self.lo[1] - reach) & (Zb < self.hi[1] + reach)
        if m.any():
            d, i = self.tree.query(np.c_[A[m], Zb[m]], workers=-1)
            out[m], along[m] = d, self.s[i]
        return out, along


def rounded_l(p0, corner, p1, r, step=0.5):
    """Polyline p0 -> corner -> p1 with the corner rounded by r."""
    p0, c, p1 = (np.asarray(p, float) for p in (p0, corner, p1))
    u0, u1 = (p0 - c) / np.linalg.norm(p0 - c), (p1 - c) / np.linalg.norm(p1 - c)
    t0, t1 = c + u0 * r, c + u1 * r                     # tangent points (90 degree corner)
    centre = c + (u0 + u1) * r
    a0, a1 = np.arctan2(*(t0 - centre)[::-1]), np.arctan2(*(t1 - centre)[::-1])
    da = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi
    arc = centre + r * np.c_[np.cos(a0 + da * np.linspace(0, 1, 24)), np.sin(a0 + da * np.linspace(0, 1, 24))]
    return np.vstack([p0, t0, arc, t1, p1])


def filleted(pts, r):
    """Polyline with each inner corner rounded (a quadratic curve from r before it to r after); r is
    one radius for every corner or a list, one per corner."""
    pts = [np.asarray(p, float) for p in pts]
    rs = list(r) if np.ndim(r) else [r] * (len(pts) - 2)
    out = [pts[0]]
    for p0, c, p1, r in zip(pts[:-2], pts[1:-1], pts[2:], rs):
        u0, u1 = (p0 - c) / np.linalg.norm(p0 - c), (p1 - c) / np.linalg.norm(p1 - c)
        a, b = c + u0 * r, c + u1 * r
        t = np.linspace(0, 1, 20)[:, None]
        out += list((1 - t) ** 2 * a + 2 * t * (1 - t) * c + t ** 2 * b)
    out.append(pts[-1])
    return np.array(out)


def capsule(a, z, p0, p1, w):
    """Distance from a capsule (a segment p0-p1, half width w/2) in the face's (a, z)."""
    (a0, z0), (a1, z1) = p0, p1
    da, dz = a1 - a0, z1 - z0
    t = np.clip(((a - a0) * da + (z - z0) * dz) / (da * da + dz * dz), 0, 1)
    return np.hypot(a - a0 - t * da, z - z0 - t * dz) - w / 2


def honeycomb(a, z, cell, w):
    """Distance from the walls of a honeycomb (flat-topped hexagons, cell mm across the flats) in (a, z),
    less half the walls' width: negative on the ridges."""
    sx, sy = cell * np.sqrt(3.0), cell                # the lattice: two rectangular grids, one offset
    best = None
    for ox, oy in ((0.0, 0.0), (sx / 2, sy / 2)):
        qx = (a - ox) - sx * np.round((a - ox) / sx)
        qy = (z - oy) - sy * np.round((z - oy) / sy)
        d = np.hypot(qx, qy)
        if best is None:
            best, bx, by = d, qx, qy
        else:
            m = d < best
            best, bx, by = np.where(m, d, best), np.where(m, qx, bx), np.where(m, qy, by)
    # distance to the cell's edge: its hexagonal 'radius' (pointy along a) is the inradius cell/2
    hexr = np.maximum(np.abs(by), np.abs(bx) * (np.sqrt(3.0) / 2) + np.abs(by) / 2)
    return np.abs(cell / 2 - hexr) - w / 2


class Channel:
    """A light along a centre line: a slot (tapered to taper[1] of its height over the first
    taper[0] mm, if given) and a channel behind it, both rounded at the ends."""
    def __init__(self, pts, spec, base=0.0, taper=None, base_fn=None):
        self.path, self.s, self.base0, self.taper = Path2D(pts), spec, base, taper
        self.base_fn = base_fn     # the recess it sits in, by arc position (where it runs out of one)
        self.base = base
        self.back = base + spec.skin + spec.depth      # depth of the channel's back
        self.lo, self.hi = self.path.lo, self.path.hi

    def _set_base(self, a):
        if self.base_fn is not None:
            self.base = self.base_fn(a)
            self.back = self.base + self.s.skin + self.s.depth

    def profile(self, a, nn, Z):
        """(inside of the channel, visible slot) as 2D distances in the face, 99 when far."""
        self._set_base(a)
        s = self.s
        reach = s.inner / 2 + s.wall + 3.0
        near = (nn > -self.back - 3.0) & (nn < 4.0)
        d, along = self.path.dist(a, Z, reach)
        d = np.where(near, d, 99.0)
        half = s.slot / 2
        if self.taper is not None:
            t = np.clip(along / self.taper[0], 0, 1)
            half = half * (self.taper[1] + (1 - self.taper[1]) * t * t * (3 - 2 * t))
        if s.front:                       # the opening is the channel, tapered and all
            return d - half, d - half
        return d - s.inner / 2, d - half

    def walls(self, pr, nn):
        return iround(pr[0] - self.s.wall, slab(nn, -self.back - self.s.closed, -(self.base + 0.5)), 0.8)

    def keep(self, pr, nn):
        return iround(pr[0] - self.s.wall, slab(nn, -self.back, 1.0), 0.8)

    def inner(self, pr, nn):
        if self.s.front:                  # closed at the back, open through the face
            return iround(pr[0], slab(nn, -self.back, 3.0), 0.4)
        return iround(pr[0], slab(nn, -self.back - 1.0, -(self.base + self.s.skin)), 0.4)

    def slot(self, pr, nn):
        if self.s.front:
            return 99.0 + 0 * pr[1]
        return iround(pr[1], slab(nn, -(self.base + self.s.skin + 0.5), 3.0), 0.3)

    def insert(self, pr, nn):
        s = self.s
        if s.front:
            return iround(pr[0] + INSERT_CLEAR, slab(nn, -(self.base + BLADE_FLUSH + s.insert),
                                                     -(self.base + BLADE_FLUSH)), min(0.3 * s.insert / 1.5, 2.0))
        return iround(pr[0] + INSERT_CLEAR,
                      slab(nn, -(self.base + s.skin + s.insert), -(self.base + s.skin + 0.05)), 0.3)

    def access(self, X, Y, Z, nn):
        return None


class Ladder(Channel):
    """C7: a ladder of short rungs up the outer end, raked like the blades, all lit from one
    pocket behind them (one short piece of LED strip standing upright). The corner behind it
    is solid, so a channel runs straight back from the pocket to the back of the fill, for the
    diffuser and the strip to slide in and the wires to come out."""
    def __init__(self, a_mid, z0, n, pitch, rung_len, spec, base, rake, sw=None, y_back=None):
        self.s, self.base, self.taper, self.rake = spec, base, None, rake
        self.base0, self.base_fn = base, None
        self.back = base + spec.skin + spec.depth
        self.a_mid, self.zs = a_mid, z0 + pitch * np.arange(n)
        self.zm, self.rung_len = self.zs.mean(), rung_len
        self.hz = (self.zs[-1] - self.zs[0]) / 2 + spec.slot / 2 + 1.2     # pocket half height
        self.ha = rung_len / 2 + 1.2                                      # ...and half width
        r = max(self.ha, self.hz) + spec.wall + 4.0
        self.lo, self.hi = np.array([a_mid - r, self.zm - r]), np.array([a_mid + r, self.zm + r])
        self.chan = None
        if sw is not None:
            # the pocket's footprint seen from the front (along y), from just behind the skin to
            # its back, at each height: the channel behind must clear all of it
            zz = np.linspace(self.zm - self.hz, self.zm + self.hz, 33)
            lo, hi = [], []
            for z in zz:
                aa = a_mid + (z - self.zm) * rake + np.linspace(-self.ha, self.ha, 9)
                p, d1 = sw.cs(aa), sw.cs(aa, 1)
                nrm = np.c_[d1[:, 1], -d1[:, 0]] / np.hypot(d1[:, 0], d1[:, 1])[:, None] * sw.nsign
                xs = np.concatenate([p[:, 0] - dd * nrm[:, 0] for dd in np.linspace(spec.skin, self.back, 5)])
                lo.append(xs.min() - 1.0)          # 1 mm round the pocket: a real step, not a thin ledge
                hi.append(xs.max() + 1.0)
            self.chan = (zz, np.array(lo), np.array(hi), y_back)

    def access(self, X, Y, Z, nn):
        zz, lo, hi, y_back = self.chan
        xz = reduce(np.maximum, [np.interp(Z, zz, lo) - X, X - np.interp(Z, zz, hi),
                                 (zz[0] - 0.2) - Z, Z - (zz[-1] + 0.2)])
        ch = iround(xz, nn + self.s.skin + self.s.insert + 0.5, 0.4)   # from behind the diffuser
        return iround(ch, np.maximum(y_back - Y, nn + 1.5), 0.4)   # to the fill's back; 1.5 mm inside the face

    def profile(self, a, nn, Z):
        s = self.s
        u = a - self.a_mid - (Z - self.zm) * self.rake           # across the rungs, raked
        near = (nn > -self.back - 3.0) & (nn < 4.0) & (np.abs(u) < 30) & (np.abs(Z - self.zm) < 40)
        r = 1.5
        qa, qz = np.abs(u) - self.ha + r, np.abs(Z - self.zm) - self.hz + r
        pocket = np.minimum(np.maximum(qa, qz), 0) + np.hypot(np.maximum(qa, 0), np.maximum(qz, 0)) - r
        k = np.clip(np.round((Z - self.zs[0]) / (self.zs[1] - self.zs[0])), 0, len(self.zs) - 1)
        zr = self.zs[0] + k * (self.zs[1] - self.zs[0])
        ru = np.maximum(np.abs(u) - (self.rung_len / 2 - s.slot / 2), 0)
        rung = np.hypot(ru, Z - zr) - s.slot / 2
        return np.where(near, pocket, 99.0), np.where(near, rung, 99.0)


def chamfer_rect(x, z, hw, hh, ch, r=3.0):
    """Rectangle with its corners cut at 45 degrees (legs ch), centred at 0; r rounds what's left."""
    an, az = np.abs(x) - hw + r, np.abs(z) - hh + r
    box = np.minimum(np.maximum(an, az), 0) + np.hypot(np.maximum(an, 0), np.maximum(az, 0)) - r
    return np.maximum(box, (np.abs(x) + np.abs(z) - (hw + hh - ch)) / SQ2)


class Style:
    def __init__(self, name, sw, fg, ops):
        self.name, self.sw, self.ops = name, sw, ops
        self.chamfer = name in ("B", "BC")
        self.wire = None
        self.chin_z = CHIN_Z
        self.rake = RAKE if name in ("C7", "P3C") else 0.0
        self.win_edge = C7_EDGE if name in ("C7", "P3C") else None
        self.pocket = None     # (side, bottom, top) chamfers of the pockets at the face
        self.tray_recess = TRAY_RECESS
        self.pocket_r = POCKET_R
        self.lens_hole = None
        self.block_extra = 0.0   # the tunnels' solid blocks reach this much further sideways
        self.fin = (FIN_FRONT, FIN_EDGE, 2.15)   # the fins: front edge behind the face, half width there and at the floor
        self.grooves = []        # sculpted grooves: ((a0, z0), (a1, z1), width, depth), cut with 45 degree sides
        self.honey = None        # (cell, ridge width, height): raised honeycomb on the recess's floor
        L, path = sw.L, sw.path
        i0 = int(np.argmin(path[:, 0]))              # from the hood corner on, x only grows
        self._ax = (path[i0:, 0], L[i0:])
        self.T_of_a = lambda a: np.interp(a, L, sw.T)
        wins = fg["wins"]
        fronts = [t[3] for t in fg["tunnels"]]
        self.fronts = [(t[0], f[0], f[2], f[1]) for t, f in zip(fg["tunnels"], fronts)]  # px, hw, zc, hh
        x_out_h = wins[0][0] - wins[0][3] - 0.5          # outer edges of the outer windows' openings
        x_out_f = wins[-1][0] + wins[-1][3] + 0.5
        self.channels = []
        self.chin = None
        self.tray = None
        self.fins = []
        ax = self.arc_of_x
        if name == "A":
            # along the top, just under the door's lip (the rail is its roof), from the hood
            # pod's outer end to just short of the fender pod's outer corner
            a0, a1 = ax(-112.0), ax(108.0)
            aa = np.arange(a0, a1 + 0.1, 0.5)
            zc = self.T_of_a(aa) - 3.2 - TOP.inner / 2
            self.channels.append(Channel(np.c_[aa, zc], TOP))
        if name in ("B", "BC", "C"):
            self.chin = (ax(x_out_h) - 22.0, ax(x_out_f) + 22.0)
        if name == "B":
            for sgn, x_out, x_in in ((-1, x_out_h, wins[0][0] + wins[0][3]), (1, x_out_f, wins[-1][0] - wins[-1][3])):
                a_leg = ax(x_out) + sgn * (FRAME_W + 1.5 + LOW.inner / 2 + LOW.wall)
                z_top = min(fronts[0 if sgn < 0 else -1][2] + fronts[0 if sgn < 0 else -1][1] + FRAME_W - 2.0,
                            float(self.T_of_a(a_leg)) - 5.0)
                a_end = ax(x_in) + sgn * 8.0
                pts = rounded_l((a_leg, z_top), (a_leg, LOW_Z), (a_end, LOW_Z), 6.0)
                self.channels.append(Channel(pts, LOW))
        if name == "BC":
            for (px, hw, zc, hh) in self.fronts:
                a0, a1 = ax(px - hw + 7.0), ax(px + hw - 7.0)
                self.channels.append(Channel([(a0, LOW_Z), (a1, LOW_Z)], LOW))
        zmid = self.fronts[0][2]
        if name == "C":
            ta0, ta1 = ax(x_out_h) - TRAY_MARGIN, ax(x_out_f) + TRAY_MARGIN
            self.tray = dict(u0=ta0, u1=ta1, zb=1.2, zmid=zmid, r=TRAY_R, top=(4.0, 59.0))
            self.channels.append(Channel([(ta0 + 6.0, LOW_Z), (ta1 - 6.0, LOW_Z)], LOW, base=TRAY_RECESS))
        if name == "C7":
            # GM's C7 headlamp: a black housing round the projectors, a thin light blade under
            # them that tapers to a point inboard, and a ladder of LEDs up the outboard edge.
            # Here the housing is a recessed tray with raked ends, the windows and the blades
            # between them lean back, the blade runs under all three pods, and the ladder
            # stands past the fender pod.
            # (the ladder stands just past the housing's end: inside it, its pocket would run
            # into the fender pod's outer corner, which is only about 3 mm behind the face there)
            ta0 = ax(x_out_h) - C7_TRAY_MARGIN
            ta1 = ax(x_out_f) + C7_TRAY_MARGIN
            lad = Ladder(0.0, LADDER_Z0, LADDER_N, LADDER_PITCH, LADDER_RUNG, LADDER, 0.0, RAKE)
            a_lad = ta1 + 9.5 + LADDER.wall + lad.ha        # far enough round the corner that its channel keeps 2.5 mm from the pod's tunnel
            fpod = fg["tunnels"][-1]
            lad = Ladder(a_lad, LADDER_Z0, LADDER_N, LADDER_PITCH, LADDER_RUNG, LADDER, 0.0, RAKE,
                         sw=sw, y_back=fpod[1] - 18.0 - 4.0)
            self.tray = dict(u0=ta0, u1=ta1, zb=C7_TRAY_BOTTOM, zmid=zmid, r=C7_TRAY_R, top=(4.5, 61.5))
            a0, a1 = ax(x_out_h) + 3.0, ax(x_out_f) - 3.0
            self.channels.append(Channel([(a0, LOW_Z), (a1, LOW_Z)], BLADE, taper=(45.0, 0.45)))
            self.wire = (a1 - 6.0, 3.0, 6.0)   # the blade's wire hole: arc position, height, length behind the channel
            self.channels.append(lad)
            self.chin = (a0 - 22.0, a1 + 22.0)
        if name == "P3D":
            a0, a1 = D_ENDS
            xs, xe, ang, rb = D_SQUINT
            aa = np.linspace(ax(xs), a1, 120)
            z_flat = float(np.min(self.T_of_a(aa) - RAIL_T - D_BAR_UNDER_RAIL))   # level, under the rail's lowest
            z_end = z_flat - (xs - xe) * np.tan(np.radians(ang))
            top = list(filleted([(ax(xe), z_end), (ax(xs), z_flat), (a1, z_flat)], [rb]))
            xs2, xe2, ang2, rb2 = D_SQUINT_LOW
            bot = list(filleted([(ax(xe2), D_BOTTOM_Z + (xs2 - xe2) * np.tan(np.radians(ang2))),
                                 (ax(xs2), D_BOTTOM_Z), (a1, D_BOTTOM_Z)], [rb2]))
            self.channels.append(Channel(top, LINE4))
            self.channels.append(Channel(bot, LINE4))
            self.wire = (ax(xs2) + 6.0, D_BOTTOM_Z, 25.0)                   # the bars are wired together behind
            self.chin = (ax(xe2) - 15.0, a1 + 15.0)
            self.chin_z = D_BOTTOM_Z - LINE4.inner / 2 - LINE4.wall - 1.0
            self.lens_hole = LENS_D / 2 + LENS_GAP
            self.win_edge = 0.6
        if name == "P3R":
            a0, _ = D_ENDS
            x_of_a = lambda a_: float(np.interp(a_, self._ax[1], self._ax[0]))
            zc = self.fronts[0][2]
            off = LENS_D / 2 + LENS_GAP + LENS_BEVEL + LINE4.slot / 2 + R_CLEAR    # each run from the heads' centres
            zt, zb = zc + off, zc - off
            xt, xb, rc = R_CORNER
            pts = filleted([(R_TOP_IN, zt), (xt, zt), (xb, zb), (x_of_a(a0), zb)], [rc, rc])
            seg = np.hypot(*np.diff(pts, axis=0).T)
            cum = np.r_[0, np.cumsum(seg)]
            s_ = np.r_[np.arange(0, cum[-1], 1.0), cum[-1]]
            x_, z_ = np.interp(s_, cum, pts[:, 0]), np.interp(s_, cum, pts[:, 1])
            # the bottom run's last stretch goes round the hood-side corner onto the side face: there
            # it follows the arc position on out to a0 (head on, x stops at the corner)
            a_ = np.array([self.arc_of_x(q) for q in x_])
            a_[-1] = a0
            line = np.c_[a_, z_]
            room = self.T_of_a(line[:, 0]) - RAIL_T - D_BAR_UNDER_RAIL - line[:, 1]
            assert room.min() > -0.05, f"R: the top run is {-room.min():.2f} mm too close to the rail (R_LIFT)"
            self.channels.append(Channel(line, LINE4))
            # the recessed housing inside the C: a parallelogram, its ends leaning with the C's leaning
            # end, the top run's inner end at its top inner corner
            lean = (self.arc_of_x(xt) - self.arc_of_x(xb)) / (zt - zb)
            ri = R_REC_IN
            u1 = self.arc_of_x((xt + xb) / 2) - ri          # the outer end, at mid height
            u0 = self.arc_of_x(R_TOP_IN) - lean * (zt - zc)  # the inner end, under the top run's end
            self.tray = dict(u0=u0, u1=u1, zb=zb + ri, zmid=zc, r=R_REC_R, top=(-1e3, zt - ri), lean=lean)
            self.tray_recess = R_REC
            pxs = [f[0] for f in self.fronts]
            self.fins = [self.arc_of_x((p0 + p1) / 2) for p0, p1 in zip(pxs, pxs[1:])]
            self.fin = R_FIN
            self.wire = (a0 + 6.0, zb, 25.0)          # the strip's wires leave at its bottom end, by the hood side
            self.grooves = [(p0, p1, w, R_STRAKE_DEPTH) for p0, p1, w in R_STRAKES]
            ga, gs, gn, gw, (gz0, gz1) = R_GILLS
            for k in range(gn):
                a_ = ga + k * gs
                self.grooves.append(((a_ - lean * (zc - gz0), gz0), (a_ + lean * (gz1 - zc), gz1), gw, R_GILL_DEPTH))
            self.honey = R_HONEY
            if R_SHAPE:
                sw.relief = face_relief(R_SHAPE, self.T_of_a)
            self.chin = (a0 - 15.0, self.arc_of_x(xb) + 15.0)
            self.chin_z = zb - LINE4.inner / 2 - LINE4.wall - 1.0
            self.lens_hole = LENS_D / 2 + LENS_GAP
            self.win_edge = 0.6
        if name == "P3V":
            pxs = [t[0] for t in fg["tunnels"]]
            zc = self.fronts[0][2]
            hwp = PROJ_W / 2 - PROJ_LIP[0] + V_CHAMFER[0]               # the pockets at the recess's floor
            zbot = zc - (PROJ_H / 2 - PROJ_LIP[1]) - V_CHAMFER[1]
            rp = POCKET_R[1]
            off = rp + HOOK_GAP + LINE4.inner / 2 + LINE4.wall          # the line's centre round a corner
            zrun = zbot + rp - off                                       # under the pockets
            zcc = zbot + rp                                              # the bottom corners' centres' height
            vh = np.radians(V_HUMP)
            arc_up = np.linspace(-np.pi / 2, -vh, 24)
            xy = []                                                      # head-on (x, z), hood to fender
            for k, px in enumerate(pxs):
                cl, cr = px - hwp + rp, px + hwp - rp                    # this pocket's bottom corners' centres
                if k > 0:                                                # down from the hump, round the left corner
                    xy += [(cl - off * np.cos(v), zcc + off * np.sin(v)) for v in arc_up[::-1]]
                xy += [(cl, zrun), (cr, zrun)]
                if k < len(pxs) - 1:                                     # round the right corner, up to the hump
                    xy += [(cr + off * np.cos(v), zcc + off * np.sin(v)) for v in arc_up]
                    x0, z0 = xy[-1]
                    xm = (cr + pxs[k + 1] - hwp + rp) / 2                # halfway to the next pocket's corner
                    xy.append((xm, z0 + (xm - x0) / np.tan(vh)))          # the peak, on the tangents
            # the fender end: round the outer pocket's corner to the leg's angle, then straight on up
            cr = pxs[-1] + hwp - rp
            v_end = np.radians(V_LEG[0])
            for v in np.linspace(-np.pi / 2, v_end, 30)[1:]:
                xy.append((cr + off * np.cos(v), zcc + off * np.sin(v)))
            x0, z0 = xy[-1]
            dx, dz = -np.sin(v_end), np.cos(v_end)                        # the tangent there
            xy.append((x0 + dx * (V_LEG[1] - z0) / dz, V_LEG[1]))
            pts = [(ax(x), z) for x, z in xy]
            # the hood end: from the run, turn up round the curved corner
            hx, hr, hlean, htop = V_HOOD
            a_turn = ax(hx)
            pts = list(filleted([(a_turn - hlean, htop), (a_turn, zrun), pts[0]], [hr])) + pts[1:]
            # round the humps' peaks a little (Chaikin on the whole line keeps it smooth)
            arr = np.array(pts)
            for _ in range(2):
                q = [arr[0]]
                for p0, p1 in zip(arr[:-1], arr[1:]):
                    q += [0.8 * p0 + 0.2 * p1, 0.2 * p0 + 0.8 * p1]
                arr = np.array(q + [arr[-1]])
            pts = [tuple(p) for p in arr]
            self.channels.append(Channel(pts, LINE4, base=EYELID))
            self.wire = (a_turn + 12.0, zrun, 25.0)
            hw_line = LINE4.inner / 2 + LINE4.wall
            ea0 = min(p[0] for p in pts) - hw_line - 5.0
            ea1 = max(p[0] for p in pts) + hw_line + 5.0
            zb_t = zrun - hw_line - 0.8
            self.tray = dict(u0=ea0, u1=ea1, zb=zb_t, zmid=zc, r=4.0, top=EYELID_TOP)
            self.tray_recess = EYELID
            self.chin = (ea0 - 20.0, ea1 + 20.0)
            self.chin_z = zb_t - 1.0
            self.pocket = V_CHAMFER
            self.block_extra = V_CHAMFER[0]
            self.honey = R_HONEY                     # honeycomb on the recess's floor, between the pockets
            if V_SHAPE:                              # the face sculpted (the heads stand proud of it, as J's)
                sw.relief = face_relief(V_SHAPE, self.T_of_a)
        if name == "P3J":
            # three projectors in a line, in stepped pockets under a sharp brow; a thin light line
            # runs the face's full width under them and kicks up at both ends at crisp corners
            pxs = [t[0] for t in fg["tunnels"]]
            half = PROJ_W / 2 + 1.0
            a_start, a0 = ax(STRIP_HOOD_X), ax(pxs[-1] + half + 12.0)
            head = [(a_start - KICK_IN[0], KICK_IN[1]), (a_start, THIN_Z)]
            end = os.environ.get("P3J_END", "swoosh")   # the line's shape (the others were options tried)
            if end == "swoosh":
                # the owner's sketch: from the fender-side side panel (as high and as far back as the
                # door's side flange behind it allows), an S down and forward, round the fender corner
                # low, under the projectors, then rising toward the hood end
                lip = proj_lip(name)
                hwo = PROJ_W / 2 - lip[0]                                        # the openings
                zlow = self.fronts[0][2] - PROJ_H / 2 + lip[1] - HOOK_GAP - DIFF.inner / 2 - DIFF.wall
                x_rise = pxs[0] - hwo - HOOK_GAP - DIFF.inner / 2 - DIFF.wall   # past the hood-side opening
                ctrl = [(ax(SW_HOOD[0]), SW_HOOD[1]), (ax(SW_HOOD[0] + 9.0), SW_HOOD[1] - 7.0),
                        (ax(x_rise - 6.0), zlow + 2.5), (ax(x_rise + 4.0), zlow)]
                ctrl += [(ax(x), zlow) for x in np.linspace(x_rise + 12.0, 100.0, 12)]
                ctrl += [(a, z if z > zlow else zlow) for a, z in SW_SIDE]
                arr = np.array(ctrl, float)
                for _ in range(4):                      # one flowing line (Chaikin)
                    q = [arr[0]]
                    for p0, p1 in zip(arr[:-1], arr[1:]):
                        q += [0.75 * p0 + 0.25 * p1, 0.25 * p0 + 0.75 * p1]
                    arr = np.array(q + [arr[-1]])
                pts = [tuple(p) for p in arr]
                a_start = pts[0][0]
            elif end == "wrap_pocket":     # a J round the outer pocket's bottom corner, on the same centre
                xe = pxs[-1] + PROJ_W / 2 - PROJ_LIP[0] + POCKET_CHAMFER[0]          # the pocket's outer edge
                zbot = self.fronts[-1][2] - (PROJ_H / 2 - PROJ_LIP[1]) - POCKET_CHAMFER[1]
                rp = POCKET_R[1]
                x_cen, z_cen = xe - rp, zbot + rp                                       # its corner's centre
                rj = rp + HOOK_GAP + DIFF.inner / 2 + DIFF.wall
                th = np.linspace(-np.pi / 2, 0.0, 24)     # laid out as seen head-on, then onto the face
                arc = [(ax(x_cen + rj * np.cos(v)), z_cen + rj * np.sin(v)) for v in th]
                zrun = z_cen - rj                                                       # the bottom run's height
                head = [(a_start - KICK_IN[0], KICK_IN[1]), (a_start, zrun)]
                pts = list(filleted(head + [arc[0]], [KICK_IN_R])) + arc[1:] + [(ax(x_cen + rj), 46.0)]
            elif end == "hook":            # a smooth hook up the face
                pts = list(filleted(head + [(a0, THIN_Z), (a0 + 8.0, 46.0)], 14.0))
            elif end.startswith("curve"):   # a big, smooth J up the outer corner (curve26, curve36: radius);
                r = float(end[5:] or HOOK_CURVE_R)    # the inner kick-up curves to match, smaller
                pts = list(filleted(head + [(a0 + 14.0, THIN_Z), (a0 + 20.0, 46.0)], [KICK_IN_R, r]))
            elif end == "crisp":         # a crisp kick-up on the face
                pts = head + [(a0, THIN_Z), (a0 + 8.0, 46.0)]
            elif end == "wrap":          # round the corner onto the side, and ends there
                pts = head + [(a0 + 60.0, THIN_Z)]
            elif end == "sweep":         # round the corner, then a long sweep up and back along the side
                pts = list(filleted(head + [(a0 + 20.0, THIN_Z), (a0 + 75.0, 30.0)], 20.0))
            elif end == "corner":        # kicks up on the rounded corner itself, seen from front and side
                pts = list(filleted(head + [(a0 + 10.0, THIN_Z), (a0 + 14.0, 46.0)], 6.0))
            else:                        # round the corner, kicking up on the side
                pts = head + [(a0 + WRAP, THIN_Z), (a0 + WRAP + KICK_OUT[0], KICK_OUT[1])]
            hw_line = DIFF.inner / 2 + DIFF.wall
            ea0 = min(p[0] for p in pts) - hw_line - 5.0
            if end == "swoosh":
                # the recess covers the face only, to just past the fender-side opening; the line's
                # channel steps out of it there, onto the corner and the side panel
                ea1 = ax(pxs[-1] + PROJ_W / 2 - proj_lip(name)[0] + 6.0)
                b0, b1 = ea1 - 10.0, ea1 + 4.0
                base_fn = lambda a, b0=b0, b1=b1: EYELID_J * (1.0 - np.clip((a - b0) / (b1 - b0), 0, 1) ** 2 * (3 - 2 * np.clip((a - b0) / (b1 - b0), 0, 1)))
                self.channels.append(Channel(pts, DIFF, base=EYELID_J, base_fn=base_fn))
                low = [p[0] for p in pts if p[1] < 8.0]
                self.chin = (ea0 - 20.0, max(low) + 12.0)
                self.tray_recess = EYELID_J
                self.pocket = (0.0, 0.0, 0.0)          # straight-through openings, an even gap round each head
                self.pocket_r = (J_OPEN_R, J_OPEN_R)
                self.block_extra = 0.0
            else:
                ea1 = max(p[0] for p in pts) + hw_line + 5.0
                self.channels.append(Channel(pts, DIFF, base=EYELID))
                self.chin = (ea0 - 20.0, ea1 + 20.0)
                self.tray_recess = EYELID
                self.pocket = POCKET_CHAMFER
                self.block_extra = POCKET_CHAMFER[0]
            self.wire = (a_start + 12.0, min(p[1] for p in pts), 25.0)
            self.tray = dict(u0=ea0, u1=ea1, zb=EYELID_BOTTOM, zmid=self.fronts[0][2], r=4.0, top=EYELID_TOP)
            self.chin_z = EYELID_CHIN
            self.win_edge = 0.6
            if J_TEXTURE:
                self.honey = R_HONEY                 # honeycomb on the recess's floor round the openings
            if J_SHAPE:                              # the face sculpted (the heads, forward already, stand prouder)
                sw.relief = face_relief(J_SHAPE, self.T_of_a)
        if name == "P3C":
            # the C7 look round three projectors: a black housing (a recessed tray with raked ends and
            # crisp corners) round the windows, which lean back like the C7's, with a raked fin
            # between each pair; the bold strip runs just under the housing and kicks up past its
            # fender end, parallel to it
            pxs = [t[0] for t in fg["tunnels"]]
            half = PROJ_W / 2 + 1.0
            ta0 = ax(P3C_TRAY_HOOD_X) - C7_TRAY_MARGIN    # on past the hood-side head, to fill the room
            ta1 = ax(x_out_f) + C7_TRAY_MARGIN
            self.tray = dict(u0=ta0, u1=ta1, zb=P3C_TRAY_BOTTOM, zmid=zmid, r=C7_TRAY_R, top=(4.5, 61.5))
            a_leg = ta1 + BOLD.inner / 2 + BOLD.wall + 2.0          # the up-stroke's centre line at zmid
            z0, z1 = P3C_STRIP_Z, 48.0
            a_start = ta0 + 4.0
            pts = filleted([(a_start, z0), (a_leg + (z0 - zmid) * RAKE, z0), (a_leg + (z1 - zmid) * RAKE, z1)], 7.0)
            self.channels.append(Channel(pts, BOLD))
            self.wire = (a_start + 12.0, 0.5, 25.0)
            self.chin = (a_start - 22.0, a_leg + 12.0)
            self.chin_z = P3C_CHIN
        if name == "P3W":
            # three small projectors at the pods' places; one light strip that dips under each one,
            # peaks between them and sweeps up past the fender-side one
            pxs = [t[0] for t in fg["tunnels"]]
            half = PROJ_W / 2 + 1.0
            xs = [pxs[0] - half + 4.0, pxs[0] - half + 9.0]
            zs = [THICK_Z + 6.0, THICK_Z]
            for xa, xb in zip(pxs, pxs[1:]):         # flat under each window, peaking in the gaps
                xm = (xa + xb) / 2
                xs += [xa + half + 3.5, xm - 2.0, xm, xm + 2.0, xb - half - 3.5]
                zs += [THICK_Z, 22.0, 24.0, 22.0, THICK_Z]
            xs += [pxs[-1] + half + 4.0, pxs[-1] + half + 10.0, pxs[-1] + half + 10.0]
            zs += [THICK_Z, THICK_Z + 8.0, 46.0]
            pts = np.c_[[ax(x) for x in xs], zs]
            for _ in range(3):                       # round the corners a little (Chaikin)
                q = [pts[0]]
                for p0, p1 in zip(pts[:-1], pts[1:]):
                    q += [0.85 * p0 + 0.15 * p1, 0.15 * p0 + 0.85 * p1]
                pts = np.array(q + [pts[-1]])
            self.channels.append(Channel(pts, THICK))
            # the strip's wires: out of the channel's back at the hood end, low, and straight back in
            # a groove under the bezel's floor to where the bracket's beam is (zip-tie slots there)
            self.wire = (ax(pxs[0] - half + 12.0), 3.0, 25.0)
            self.chin = (ax(pxs[0] - half) - 22.0, ax(pxs[-1] + half + 12.0) + 12.0)
        if name == "P4J":
            # four projectors in a tight line; the bold strip under them wraps up round the fender
            # end in a wide curve, as on P3J (a little further out, past the fourth head's corner)
            pxs = [t[0] for t in fg["tunnels"]]
            half = PROJ_W / 2 + 1.0
            a_start, a_bend = ax(pxs[0] - half + 3.5), ax(pxs[-1] + half + 12.0)
            pts = filleted([(a_start, BOLD_Z), (a_bend, BOLD_Z), (a_bend + 11.0, 46.0)], 14.0)
            self.channels.append(Channel(pts, BOLD))
            self.wire = (a_start + 12.0, 0.5, 25.0)
            self.chin = (a_start - 22.0, a_bend + 12.0)
            self.chin_z = BOLD_CHIN
        if self.chin is not None:
            # the front wall comes down to CHIN_Z between the chin's ends, fading out over 20 mm;
            # the sweep builds it into its own section (Sweep.Bw), so it can't leave a lip
            ca, cb = self.chin
            f = np.clip(np.minimum(L - ca, cb - L) / 20.0, 0, 1)
            f = f * f * (3 - 2 * f)
            sw.Bw = sw.B - np.maximum(sw.B - self.chin_z, 0) * f
            if hasattr(sw, "_pcs"):
                del sw._pcs
        if name in ("C", "C7", "P3C"):
            for (pa, pb) in zip(self.fronts, self.fronts[1:]):
                self.fins.append(ax((pa[0] + pa[1] + pb[0] - pb[1]) / 2))

    def arc_of_x(self, x):
        return float(np.interp(x, *self._ax))

    def tray2d(self, a, Z):
        """The tray's outline in the face: between its ends (raked for C7), its bottom edge and
        a top that follows the door's lip (top[0] under it, at most top[1])."""
        t = self.tray
        u = a - (Z - t["zmid"]) * t.get("lean", self.rake)
        ac, ha = (t["u0"] + t["u1"]) / 2, (t["u1"] - t["u0"]) / 2
        da = np.abs(u - ac) - ha
        zt = np.minimum(self.T_of_a(a) - t["top"][0], t["top"][1])
        zm, hz = (zt + t["zb"]) / 2, (zt - t["zb"]) / 2
        dz = np.abs(Z - zm) - hz
        r = t["r"]
        qa, qz = da + r, dz + r
        return np.minimum(np.maximum(qa, qz), 0) + np.hypot(np.maximum(qa, 0), np.maximum(qz, 0)) - r

    # ---- the steps apply_features calls ----

    def ctx(self, X, Z, nn, sc, Y=None):
        self._Y = Y
        a = np.interp(sc, np.arange(self.sw.n), self.sw.L)[:, None]
        return dict(a=a, nn=nn, Z=Z, X=X, Y=self._Y, d=[ch.profile(a, nn, Z) for ch in self.channels])

    def window(self, x, z, hw, hh, r_, e_, t=None, outside=None):
        """The tunnel's cross-section: cut corners for B and BC, from nothing at the pod to CH at
        the front; for C7 leaning back, from upright at the pod to RAKE at the front."""
        if self.chamfer:
            return chamfer_rect(x, z, hw, hh, CH * e_)
        if self.lens_hole is not None:       # a round hole for the lens; the face covers the rest of the head,
            t = np.sqrt(np.clip(e_, 0, 1))   # with a bevel round the hole's edge, widest at the face
            return np.hypot(x, z) - (self.lens_hole + LENS_BEVEL * t)
        if self.pocket is not None:          # flat chamfers, from nothing at the head to full at the face
            cs, cb, ct = self.pocket
            if t is not None and self.tray is not None:
                # the chamfers run from nothing at the head to full at the recess's floor (not the face):
                # the fraction of the way from the tunnel's back to the floor
                t = np.clip(np.where(t > 0, t / np.maximum(t - (outside + self.tray_recess), 1e-3), 0.0), 0, 1)
            else:
                t = np.sqrt(np.clip(e_, 0, 1))   # e_ is the square of the depth fraction
            zt, zb = hh + ct * t, -hh - cb * t
            rc = self.pocket_r[0] + (self.pocket_r[1] - self.pocket_r[0]) * t     # all four corners
            hx = hw + cs * t
            return self.ops.round_box2(x, z, -hx, hx, zb, zt, rc, rc, rc, rc)
        if self.rake:
            return self.ops.round_rect_xz(x - self.shear(z, e_), z, hw, hh, r_)
        return None

    def shear(self, z, e_):
        """How far the tunnel (and its block) leans at height z above its centre."""
        return z * self.rake * e_ if self.rake else 0.0

    def solids(self, F, c):
        o = self.ops
        a, nn, Z, X = c["a"], c["nn"], c["Z"], c["X"]
        if self.tray is not None:
            t2 = self.tray2d(a, Z)
            backing = iround(iround(t2 - 2.5, slab(nn, -(self.tray_recess + 2.5), -0.5), 1.0),
                             np.maximum(self.chin_z + 0.5 - Z, Z - (self.T_of_a(a) - 2.0)), 1.0)   # up into the rail
            F = o.union_round(F, backing, 1.0)
        if self.chamfer:
            for (px, hw, zc, hh) in self.fronts:
                fx = X - px
                zt, zb = zc + hh + FRAME_W, zc - hh - FRAME_WB
                xo = hw + FRAME_W
                ch_t = CH + FRAME_W * (2 - SQ2)
                ch_b = CH - 2.0
                outl = reduce(np.maximum, [np.abs(fx) - xo, Z - zt, zb - Z,
                                          (np.abs(fx) + (Z - zt) - (xo - ch_t)) / SQ2,
                                          (np.abs(fx) + (zb - Z) - (xo - ch_b)) / SQ2])
                frame = o.inter_round(outl, slab(nn, -1.0, FRAME_H), 0.6)
                F = o.union_round(F, frame, 0.6)
        for ch, d in zip(self.channels, c["d"]):
            F = o.union_round(F, ch.walls(d, nn), 1.0)
        return F

    def pre_cuts(self, F, c):
        """C: the tray, its light bar, then the fins standing in it."""
        if self.tray is None:
            return F
        o = self.ops
        a, nn, Z = c["a"], c["nn"], c["Z"]
        t2 = self.tray2d(a, Z)
        F = o.diff_round(F, iround(t2, slab(nn, -self.tray_recess, 3.0), 0.8), 0.8 if not self.rake else 0.5)
        for ch, d in zip(self.channels, c["d"]):
            if ch.base0 > 0:      # in a recess (its depth can vary along it)
                F = o.diff_round(F, ch.inner(d, nn), 0.5)
                F = o.diff_round(F, ch.slot(d, nn), 0.3)
        f_front, f_edge, f_floor = self.fin
        k = (f_floor - f_edge) / (self.tray_recess - f_front)   # wider at the floor (C: the windows trim them to the post)
        lean = self.tray.get("lean", self.rake)
        for af in self.fins:
            depth = np.maximum(-nn - f_front, 0)
            side = (np.abs(a - af - (Z - self.tray["zmid"]) * lean) - f_edge - k * depth) / np.sqrt(1 + k * k)
            fin = o.inter_round(side, nn + f_front, 0.5)
            fin = iround(fin, np.maximum(-(nn + self.tray_recess + 1.0), t2 - 1.0), 0.4)
            F = o.union_round(F, fin, 0.8)
        return F

    def keep(self, c):
        """Where the windows mustn't be cut: the top blade's channel caps the windows under it."""
        if self.name != "A":
            return None
        k = None
        for ch, d in zip(self.channels, c["d"]):
            kk = ch.keep(d, c["nn"])
            k = kk if k is None else np.minimum(k, kk)
        return k

    def post_cuts(self, F, c):
        o = self.ops
        a, nn, Z, X = c["a"], c["nn"], c["Z"], c["X"]
        for ch, d in zip(self.channels, c["d"]):
            if ch.base0 == 0:
                F = o.diff_round(F, ch.inner(d, nn), 0.5)
                F = o.diff_round(F, ch.slot(d, nn), 0.4)
            acc = ch.access(X, c["Y"], Z, nn)
            if acc is not None:
                F = o.diff_round(F, acc, 0.5)
        if self.wire is not None:
            # straight in along the face's normal, from the channel's back out underneath
            aw, zw, wl = self.wire
            dep = self.channels[0].back      # the channel's back (its depth, plus any recess it sits in)
            hole = iround(np.hypot(a - aw, Z - zw) - WIRE_R, slab(nn, -(dep + wl), -(dep - 1.0)), 0.3)
            F = o.diff_round(F, hole, 0.4)
        for (p0, p1, w, dep) in self.grooves:          # sculpted grooves, 45 degree sides
            cap = capsule(a, Z, p0, p1, w)
            cut = np.maximum(np.maximum((cap - (nn + dep)) / SQ2, -(nn + dep)), nn - 3.0)
            F = o.diff_round(F, cut, 0.3)
        if self.honey is not None and self.tray is not None:
            cell, w, h = self.honey
            fl = -self.tray_recess
            ridge = np.maximum(honeycomb(a, Z, cell, w), np.abs(nn - fl - (h - 0.5) / 2) - (h + 0.5) / 2)   # 0.5 into the floor
            ridge = np.maximum(ridge, self.tray2d(a, Z) + 1.2)            # inside the housing, clear of its walls
            for (px, hw, zc, hh) in self.fronts:
                if self.lens_hole is not None:                            # clear of the lens holes' bevels
                    ridge = np.maximum(ridge, self.lens_hole + LENS_BEVEL + 1.0 - np.hypot(X - px, Z - zc))
                elif self.pocket is not None:                             # or of the pockets and their chamfers
                    cs, cb, ct = self.pocket
                    out_ = np.maximum(np.abs(X - px) - (hw + cs + 1.2),
                                      np.maximum(zc - hh - cb - 1.2 - Z, Z - (zc + hh + ct + 1.2)))
                    ridge = np.maximum(ridge, -out_)
            for ch, d in zip(self.channels, c["d"]):                      # and of the light line's channel
                ridge = np.maximum(ridge, -(d[0] - ch.s.wall - 1.0))
            F = o.union_round(F, ridge, 0.25)
        if self.chamfer:
            for (px, hw, zc, hh) in self.fronts:
                bev = chamfer_rect(X - px, Z - zc, hw, hh, CH) - np.clip(nn, 0, FRAME_BEVEL)
                F = o.diff_round(F, np.maximum(bev, -0.2 - nn), 0.4)
        return F

    def inserts(self, a, nn, Z):
        """The diffuser inserts (one solid per channel, min of all)."""
        out = None
        for ch in self.channels:
            v = ch.insert(ch.profile(a, nn, Z), nn)
            out = v if out is None else np.minimum(out, v)
        return out
