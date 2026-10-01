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


class Spec:
    """One size of light channel. slot: visible slot height; inner: channel height (the diffuser
    insert's height); wall: channel walls; skin: the face in front of the diffuser; depth: the
    channel behind the skin (diffuser plus LED strip); insert: diffuser thickness."""
    def __init__(self, slot, inner, wall, skin, depth, insert):
        self.slot, self.inner, self.wall, self.skin, self.depth, self.insert = slot, inner, wall, skin, depth, insert


# top blade: a 3.5 mm slot, 6 mm diffuser 2 mm thick, room for a 5 mm COB strip behind it
TOP = Spec(slot=3.5, inner=6.0, wall=1.5, skin=2.0, depth=5.0, insert=2.0)
# lower lights: a 3 mm slot, 4.2 mm diffuser 1.5 mm thick, for a 4 mm COB strip
LOW = Spec(slot=3.0, inner=4.2, wall=1.0, skin=1.6, depth=4.0, insert=1.5)
LOW_Z = 3.6          # the lower lights' centre line: walls from 0.5 (bracket floor at 0) to 6.7 (pods at 7.6)
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

    def dist(self, a, z, reach):
        """Distance from (a, z) (any broadcastable shapes) to the line; 99 beyond reach."""
        shape = np.broadcast_shapes(np.shape(a), np.shape(z))
        A, Zb = np.broadcast_to(a, shape), np.broadcast_to(z, shape)
        out = np.full(shape, 99.0)
        m = (A > self.lo[0] - reach) & (A < self.hi[0] + reach) & (Zb > self.lo[1] - reach) & (Zb < self.hi[1] + reach)
        if m.any():
            out[m] = self.tree.query(np.c_[A[m], Zb[m]], workers=-1)[0]
        return out


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


class Channel:
    def __init__(self, pts, spec, base=0.0):
        self.path, self.s, self.base = Path2D(pts), spec, base
        self.back = base + spec.skin + spec.depth      # depth of the channel's back

    def d(self, a, nn, Z):
        reach = self.s.inner / 2 + self.s.wall + 3.0
        near = (nn > -self.back - 3.0) & (nn < 4.0)
        return np.where(near, self.path.dist(a, Z, reach), 99.0)

    def walls(self, d, nn):
        s = self.s
        return np.maximum(d - (s.inner / 2 + s.wall), slab(nn, -self.back, -(self.base + 0.5)))

    def keep(self, d, nn):
        s = self.s
        return np.maximum(d - (s.inner / 2 + s.wall), slab(nn, -self.back, 1.0))

    def inner(self, d, nn):
        s = self.s
        return np.maximum(d - s.inner / 2, slab(nn, -self.back - 1.0, -(self.base + s.skin)))

    def slot(self, d, nn):
        s = self.s
        return np.maximum(d - s.slot / 2, slab(nn, -(self.base + s.skin + 0.5), 3.0))

    def insert(self, d, nn):
        s = self.s
        return np.maximum(d - (s.inner / 2 - INSERT_CLEAR),
                          slab(nn, -(self.base + s.skin + s.insert), -(self.base + s.skin + 0.05)))


def chamfer_rect(x, z, hw, hh, ch, r=3.0):
    """Rectangle with its corners cut at 45 degrees (legs ch), centred at 0; r rounds what's left."""
    an, az = np.abs(x) - hw + r, np.abs(z) - hh + r
    box = np.minimum(np.maximum(an, az), 0) + np.hypot(np.maximum(an, 0), np.maximum(az, 0)) - r
    return np.maximum(box, (np.abs(x) + np.abs(z) - (hw + hh - ch)) / SQ2)


class Style:
    def __init__(self, name, sw, fg, ops):
        self.name, self.sw, self.ops = name, sw, ops
        self.chamfer = name in ("B", "BC")
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
        if name == "C":
            ta0, ta1 = ax(x_out_h) - TRAY_MARGIN, ax(x_out_f) + TRAY_MARGIN
            self.tray = (ta0, ta1, 1.2)                    # arc range, bottom edge
            self.channels.append(Channel([(ta0 + 6.0, LOW_Z), (ta1 - 6.0, LOW_Z)], LOW, base=TRAY_RECESS))
            for (pa, pb) in zip(self.fronts, self.fronts[1:]):
                self.fins.append(ax((pa[0] + pa[1] + pb[0] - pb[1]) / 2))

    def arc_of_x(self, x):
        return float(np.interp(x, *self._ax))

    def tray_top(self, a):
        return np.minimum(self.T_of_a(a) - 4.0, 59.0)

    def tray2d(self, a, Z):
        ta0, ta1, zb = self.tray
        ac, ha = (ta0 + ta1) / 2, (ta1 - ta0) / 2
        da = np.abs(a - ac) - ha
        zt = self.tray_top(a)
        zm, hz = (zt + zb) / 2, (zt - zb) / 2
        dz = np.abs(Z - zm) - hz
        r = TRAY_R
        qa, qz = da + r, dz + r
        return np.minimum(np.maximum(qa, qz), 0) + np.hypot(np.maximum(qa, 0), np.maximum(qz, 0)) - r

    # ---- the steps apply_features calls ----

    def ctx(self, X, Z, nn, sc):
        a = np.interp(sc, np.arange(self.sw.n), self.sw.L)[:, None]
        return dict(a=a, nn=nn, Z=Z, X=X, d=[ch.d(a, nn, Z) for ch in self.channels])

    def window(self, x, z, hw, hh, r_, e_):
        """The tunnel's cross-section: cut corners for B and BC, from nothing at the pod to CH at
        the front."""
        if not self.chamfer:
            return None
        return chamfer_rect(x, z, hw, hh, CH * e_)

    def solids(self, F, c):
        o = self.ops
        a, nn, Z, X = c["a"], c["nn"], c["Z"], c["X"]
        if self.chin is not None:
            ca, cb = self.chin
            f = np.clip(np.minimum(a - ca, cb - a) / 20.0, 0, 1)
            f = f * f * (3 - 2 * f)
            sc_ = np.interp(a, self.sw.L, np.arange(self.sw.n))
            T, B, Dr, Df, rb, Rl = self.sw.params(sc_)
            zb = B - np.maximum(B - CHIN_Z, 0) * f
            chin = o.round_box2(nn, Z, -3.0, 0.0, zb, B + 6.0, 0.0, np.maximum(Rl, 1.0), 0.0, 1.0)
            F = np.minimum(F, chin)
        if self.tray is not None:
            t2 = self.tray2d(a, Z)
            backing = reduce(np.maximum, [t2 - 2.5, slab(nn, -(TRAY_RECESS + 2.5), -0.5), CHIN_Z + 0.5 - Z])
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
        F = o.diff_round(F, np.maximum(t2, slab(nn, -TRAY_RECESS, 3.0)), 0.8)
        for ch, d in zip(self.channels, c["d"]):
            F = o.diff_round(F, ch.inner(d, nn), 0.5)
            F = o.diff_round(F, ch.slot(d, nn), 0.4)
        k = (1.65 - FIN_EDGE) / (TRAY_RECESS - FIN_FRONT)
        for af in self.fins:
            depth = np.maximum(-nn - FIN_FRONT, 0)
            side = (np.abs(a - af) - FIN_EDGE - k * depth) / np.sqrt(1 + k * k)
            fin = o.inter_round(side, nn + FIN_FRONT, 0.5)
            fin = reduce(np.maximum, [fin, -(nn + TRAY_RECESS + 1.0), t2 - 1.0])
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
        if self.tray is None:
            for ch, d in zip(self.channels, c["d"]):
                F = o.diff_round(F, ch.inner(d, nn), 0.5)
                F = o.diff_round(F, ch.slot(d, nn), 0.4)
        if self.chamfer:
            for (px, hw, zc, hh) in self.fronts:
                bev = chamfer_rect(X - px, Z - zc, hw, hh, CH) - np.clip(nn, 0, FRAME_BEVEL)
                F = o.diff_round(F, np.maximum(bev, -0.2 - nn), 0.4)
        return F

    def inserts(self, a, nn, Z):
        """The diffuser inserts (one solid per channel, min of all)."""
        out = None
        for ch in self.channels:
            v = ch.insert(ch.d(a, nn, Z), nn)
            out = v if out is None else np.minimum(out, v)
        return out
