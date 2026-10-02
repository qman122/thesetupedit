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
# P3C (C7 look): the heads where P3J's are
PROJ3C = PROJ3J
P3C_STRIP_Z = 2.5    # P3C: the bold strip's bottom run, its walls from -3.5 to 8.5, just under the housing
P3C_CHIN = -4.0      # ...and the bottom edge under it
P3C_TRAY_BOTTOM = 9.0   # the housing's bottom edge: the windows' bottoms
P3C_TRAY_HOOD_X = -129.0  # ...its hood end, where P4's first window ends (the hood-side head can't go further
                          # that way: its body would reach the pad's square adjuster)
BOLD_STYLES = ("P3J", "P4J", "P3C")   # the looks with the bold strip (and the lower bottom edge)


def is_proj(style):
    return style.startswith("P3") or style.startswith("P4")


def proj_layout(style, pod_ys):
    """(x, y of the head's front) per projector: P4 from PROJ4; P3 at PROJ_X, 1 mm behind the
    pods' faces (pod_ys)."""
    if style.startswith("P4"):
        return list(PROJ4)
    if style == "P3J":
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
    """Polyline with each inner corner rounded (a quadratic curve from r before it to r after)."""
    pts = [np.asarray(p, float) for p in pts]
    out = [pts[0]]
    for p0, c, p1 in zip(pts[:-2], pts[1:-1], pts[2:]):
        u0, u1 = (p0 - c) / np.linalg.norm(p0 - c), (p1 - c) / np.linalg.norm(p1 - c)
        a, b = c + u0 * r, c + u1 * r
        t = np.linspace(0, 1, 20)[:, None]
        out += list((1 - t) ** 2 * a + 2 * t * (1 - t) * c + t ** 2 * b)
    out.append(pts[-1])
    return np.array(out)


class Channel:
    """A light along a centre line: a slot (tapered to taper[1] of its height over the first
    taper[0] mm, if given) and a channel behind it, both rounded at the ends."""
    def __init__(self, pts, spec, base=0.0, taper=None):
        self.path, self.s, self.base, self.taper = Path2D(pts), spec, base, taper
        self.back = base + spec.skin + spec.depth      # depth of the channel's back
        self.lo, self.hi = self.path.lo, self.path.hi

    def profile(self, a, nn, Z):
        """(inside of the channel, visible slot) as 2D distances in the face, 99 when far."""
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
        if name == "P3J":
            # three projectors in a line; the bold strip runs under them, from a little before the
            # hood-side one, and wraps up round the fender end in a wide curve, toward the corner's top
            pxs = [t[0] for t in fg["tunnels"]]
            half = PROJ_W / 2 + 1.0
            a_start, a_bend = ax(pxs[0] - half - 10.0), ax(pxs[-1] + half + 14.0)
            pts = filleted([(a_start, BOLD_Z), (a_bend, BOLD_Z), (a_bend + 10.0, 46.0)], 16.0)
            self.channels.append(Channel(pts, BOLD))
            self.wire = (a_start + 12.0, 0.5, 25.0)
            self.chin = (a_start - 22.0, a_bend + 12.0)
            self.chin_z = BOLD_CHIN
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
        u = a - (Z - t["zmid"]) * self.rake
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

    def window(self, x, z, hw, hh, r_, e_):
        """The tunnel's cross-section: cut corners for B and BC, from nothing at the pod to CH at
        the front; for C7 leaning back, from upright at the pod to RAKE at the front."""
        if self.chamfer:
            return chamfer_rect(x, z, hw, hh, CH * e_)
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
            backing = iround(iround(t2 - 2.5, slab(nn, -(TRAY_RECESS + 2.5), -0.5), 1.0),
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
        F = o.diff_round(F, iround(t2, slab(nn, -TRAY_RECESS, 3.0), 0.8), 0.8 if not self.rake else 0.5)
        for ch, d in zip(self.channels, c["d"]):
            if ch.base > 0:
                F = o.diff_round(F, ch.inner(d, nn), 0.5)
                F = o.diff_round(F, ch.slot(d, nn), 0.3)
        k = (2.15 - FIN_EDGE) / (TRAY_RECESS - FIN_FRONT)   # wider than the post at the floor: the windows trim them to it
        for af in self.fins:
            depth = np.maximum(-nn - FIN_FRONT, 0)
            side = (np.abs(a - af - (Z - self.tray["zmid"]) * self.rake) - FIN_EDGE - k * depth) / np.sqrt(1 + k * k)
            fin = o.inter_round(side, nn + FIN_FRONT, 0.5)
            fin = iround(fin, np.maximum(-(nn + TRAY_RECESS + 1.0), t2 - 1.0), 0.4)
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
            if ch.base == 0:
                F = o.diff_round(F, ch.inner(d, nn), 0.5)
                F = o.diff_round(F, ch.slot(d, nn), 0.4)
            acc = ch.access(X, c["Y"], Z, nn)
            if acc is not None:
                F = o.diff_round(F, acc, 0.5)
        if self.wire is not None:
            # straight in along the face's normal, from the channel's back out underneath
            aw, zw, wl = self.wire
            dep = self.channels[0].s.depth
            hole = iround(np.hypot(a - aw, Z - zw) - WIRE_R, slab(nn, -(dep + wl), -(dep - 1.0)), 0.3)
            F = o.diff_round(F, hole, 0.4)
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
