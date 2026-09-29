"""The bezel as a signed-distance model, shaped like the reference photo.

OpenCascade could loft the section along the path, but the loft folded over itself round the
corners and its fillets never finished, so the same design is built here as a signed distance
field (SDF) and meshed with marching cubes. Every rounding is exact by construction, and the
mesh is one closed surface that can't intersect itself.

The layout is the same as bezel_cad.py:
- One path seen from above: across the front, round the 30 mm corners and back along each ear.
- One cross-section swept along it. The section is a thin C with a constant 3 mm wall: a rolled
  bottom lip, a shallow floor, the front wall and a thin top rail with a bead on its front edge.
- Toward the corners the rail and floor narrow to nothing, so the ears are the ends of the same
  sweep, flattened into 3 mm flanges with rounded tips.
- Three rounded-rectangle windows (12 mm corners) are cut through the front, centred on the pods,
  each with a 3 mm tunnel from the front back to just in front of its pod's face, so every
  light is closed in all round. The posts are what's left between them.
- The clip tongue is a thin tapered plate blended into the rail.
- Every edge is rounded, 1 mm or more.

Writes stl/cad/bezel_cad_passenger.stl (model frame); generate.shroud() picks it up.
Run: python3 bezel_sdf.py   (about 2-4 minutes)
"""
import os
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bezel_cad as bc  # noqa: E402  (path, section parameters and fit, shared with the CAD loft)

g, P = bc.g, bc.P
HERE = bc.HERE
T_WALL = bc.T_WALL
H = 0.25            # grid step, mm: the mesh follows the surface to about 0.01 mm (see the check)
WIN_R = 12.0        # window corner radius
R_WIN_EDGE = 1.5    # round on the windows' edges
R_EDGE = 1.0        # smallest round anywhere else
R_OUT = 1.2         # the rail's and floor's outside corners
BOSS_R = 7.5        # screw bosses on the ears
TUNNEL_BACK = -0.5  # the tunnels round the lights end this far in front of each pod's face (its
                    # corners are tighter than the windows', so the tunnel can't wrap round it)
RL_MAX = 4.0        # the rolled bottom lip's radius across the front
BEAD_N = P.cover_edge_n + 2.5   # the bead's centre behind the front: under the middle of the door's lip
TARGET_FACES = 600_000   # after simplifying (the refine step adds back what the 0.05 mm needs)


# ---------- SDF building blocks (all vectorised over numpy arrays) ----------

def round_box2(px, pz, n0, n1, z0, z1, r_ft, r_fb, r_bt, r_bb):
    """Signed distance to a box n0..n1 x z0..z1 in the section plane, each corner rounded by its
    own radius: front (+n) top/bottom, back top/bottom."""
    cn, cz = (n0 + n1) / 2, (z0 + z1) / 2
    bn, bz = (n1 - n0) / 2, (z1 - z0) / 2
    qn, qz = px - cn, pz - cz
    lim = 0.49 * np.minimum(bn, bz) * 2
    r = np.where(qn > 0, np.where(qz > 0, r_ft, r_fb), np.where(qz > 0, r_bt, r_bb))
    r = np.minimum(r, lim)
    an, az = np.abs(qn) - bn + r, np.abs(qz) - bz + r
    return np.minimum(np.maximum(an, az), 0) + np.hypot(np.maximum(an, 0), np.maximum(az, 0)) - r


def round_rect_xz(px, pz, hw, hh, r):
    an, az = np.abs(px) - hw + r, np.abs(pz) - hh + r
    return np.minimum(np.maximum(an, az), 0) + np.hypot(np.maximum(an, 0), np.maximum(az, 0)) - r


def union_round(a, b, r):
    u, v = np.maximum(r - a, 0), np.maximum(r - b, 0)
    return np.maximum(r, np.minimum(a, b)) - np.hypot(u, v)


def inter_round(a, b, r):
    u, v = np.maximum(r + a, 0), np.maximum(r + b, 0)
    return np.minimum(-r, np.maximum(a, b)) + np.hypot(u, v)


def diff_round(a, b, r):
    return inter_round(a, -b, r)


def smin(a, b, k):
    """Polynomial smooth minimum (k may be an array; k = 0 is a plain min)."""
    k = np.maximum(k, 1e-6)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def poly_sdf(px, py, V):
    """Signed distance to a closed polygon V (m x 2) in plan."""
    V = np.asarray(V, float)
    d = (px - V[0, 0]) ** 2 + (py - V[0, 1]) ** 2
    s = np.ones_like(px)
    m = len(V)
    for i in range(m):
        j = i - 1
        ex, ey = V[j, 0] - V[i, 0], V[j, 1] - V[i, 1]
        wx, wy = px - V[i, 0], py - V[i, 1]
        t = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
        bx, by = wx - ex * t, wy - ey * t
        d = np.minimum(d, bx * bx + by * by)
        c1, c2, c3 = py >= V[i, 1], py < V[j, 1], ex * wy > ey * wx
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(flip, -s, s)
    return s * np.sqrt(d)


def inset(V, r):
    """Polygon V moved in by r on every side (for rounding its corners by r)."""
    q = g.CS([np.asarray(V, float)]).offset(-r, g.m3d.JoinType.Miter).to_polygons()
    return np.asarray(max(q, key=len), float)


def round_poly_sdf(px, py, V, r):
    """Signed distance to the convex polygon V with its corners rounded by r."""
    return poly_sdf(px, py, inset(V, r)) - r


# ---------- the sweep ----------

class Sweep:
    def __init__(self):
        path, rows, sides, tips = self._layout()
        self.path, self.sides, self.tips = path, sides, tips
        n = len(path)
        seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
        self.L = np.r_[0, np.cumsum(seg)]
        self.nrm = np.array([r[2] for r in rows], float)
        cols = np.array([r[3:] for r in rows], float)      # T, B, Dr, Df, rb, R_lip
        self.T, self.B, Dr, Df, self.rb, self.Rl = cols.T
        # the top follows the door's lip and edge, which are measured points joined by straight
        # lines; smooth them over a couple of mm so the surfaces have no creases between them
        from scipy.ndimage import gaussian_filter1d
        self.T = gaussian_filter1d(self.T, 2.0, mode="nearest")
        self.B = gaussian_filter1d(self.B, 2.0, mode="nearest")
        # the rolled lip: up to RL_MAX across the front, so the windows can sit on top of it
        self.Rl = 1.0 + (self.Rl - 1.0) * (RL_MAX - 1.0) / (self.Rl.max() - 1.0)
        # rail and floor go down to just the 3 mm wall at the ears (constant wall), keeping
        # their full depth across the front
        self.Dr = T_WALL + (Dr - 3.6) * (P.blade_depth - T_WALL) / (P.blade_depth - 3.6)
        self.Df = T_WALL + (Df - 3.6) * (P.floor_depth - T_WALL) / (P.floor_depth - 3.6)
        self.tree = cKDTree(path)
        from scipy.interpolate import CubicSpline
        self.cs = CubicSpline(self.L, path)
        t0 = self.cs(self.L[len(path) // 2], 1)
        self.nsign = 1.0 if (t0[1] * self.nrm[len(path) // 2, 0] - t0[0] * self.nrm[len(path) // 2, 1]) > 0 else -1.0
        self.n = n

    @staticmethod
    def _layout():
        _, path, rows, sides, tips = bc.build(skip_loft=True)
        return path, rows, sides, tips

    def project(self, qx, qy):
        """For plan points: path parameter s, signed distance n from the outside face (+ out),
        and e, the distance past the nearer ear tip along the path (negative before it)."""
        P_, n = self.path, self.n
        _, i = self.tree.query(np.c_[qx, qy], workers=-1)
        best_d = np.full(len(qx), np.inf)
        best_s = np.zeros(len(qx))
        for off in (-1, 0):
            j = np.clip(i + off, 0, n - 2)
            ax, ay = P_[j, 0], P_[j, 1]
            bx, by = P_[j + 1, 0], P_[j + 1, 1]
            ex, ey = bx - ax, by - ay
            t = ((qx - ax) * ex + (qy - ay) * ey) / (ex * ex + ey * ey)
            lo = np.where(j == 0, -np.inf, 0.0)
            hi = np.where(j == n - 2, np.inf, 1.0)
            t = np.clip(t, lo, hi)
            d = np.hypot(qx - ax - t * ex, qy - ay - t * ey)
            better = d < best_d
            best_d = np.where(better, d, best_d)
            best_s = np.where(better, j + t, best_s)
        s = best_s
        # then exactly onto the smooth spline through the path (Newton on the foot point), so the
        # field has no facets from the path's 1 mm segments, however far in from the front
        Lt = self.L[-1]
        u = np.interp(np.clip(s, 0, n - 1), np.arange(n), self.L)
        inside = (s > 0) & (s < n - 1)
        for _ in range(4):
            c, d1, d2 = self.cs(u), self.cs(u, 1), self.cs(u, 2)
            wx, wy = qx - c[:, 0], qy - c[:, 1]
            f_ = wx * d1[:, 0] + wy * d1[:, 1]
            df = -(d1 * d1).sum(1) + wx * d2[:, 0] + wy * d2[:, 1]
            u = np.where(inside, np.clip(u - f_ / np.where(np.abs(df) > 1e-9, df, -1.0), 0.0, Lt), u)
        c, d1 = self.cs(u), self.cs(u, 1)
        k = np.hypot(d1[:, 0], d1[:, 1])
        nx, ny = d1[:, 1] / k * self.nsign, -d1[:, 0] / k * self.nsign
        nn = (qx - c[:, 0]) * nx + (qy - c[:, 1]) * ny
        # arc length, extended straight past each end
        seg0, seg1 = self.L[1] - self.L[0], self.L[-1] - self.L[-2]
        arc = np.where(s < 0, s * seg0, np.where(s > n - 1, Lt + (s - (n - 1)) * seg1, u))
        e = np.maximum(-arc, arc - Lt)
        sc = np.clip(np.interp(u, self.L, np.arange(n)), 0, n - 1)
        return sc, nn, e

    def params(self, sc):
        if not hasattr(self, "_pcs"):
            from scipy.interpolate import CubicSpline
            self._pcs = CubicSpline(np.arange(self.n), np.c_[self.T, self.B, self.Dr, self.Df, self.rb, self.Rl])
        v = self._pcs(sc)
        return [v[..., k] for k in range(6)]

    def section(self, nn, z, T, B, Dr, Df, rb, Rl):
        """The C section at (n, z): outside minus the channel, both with rounded corners, so
        every corner of the section is exactly round; the bead added with a smooth union."""
        t = T_WALL
        zm = (T + B) / 2
        rail = round_box2(nn, z, -Dr, 0.0, zm - 1.0, T, R_OUT, 0.0, R_OUT, 0.0)
        floor = round_box2(nn, z, -Df, 0.0, B, zm + 1.0, 0.0, Rl, 0.0, R_OUT)
        outer = np.minimum(rail, floor)
        h_ch = (T - t) - (B + t)
        # where the rail (or floor) runs out to a short stub, its inside fillet and its end's round
        # share what depth there is, so the stub's underside stays one smooth S-curve
        avail_r, avail_f = np.maximum(Dr - t, 0.0), np.maximum(Df - t, 0.0)
        rin_t = np.minimum(np.minimum(1.5, 0.5 * avail_r + 0.3), 0.45 * h_ch)
        rin_b = np.minimum(np.minimum(np.maximum(1.5, Rl - t), 0.5 * avail_f + 0.3), 0.45 * h_ch)
        chan = round_box2(nn, z, -200.0, -t, B + t, T - t, rin_t, rin_b, 0.0, 0.0)
        sdf = np.maximum(outer, -chan)
        # round the rail's and floor's back ends where they meet the channel
        for (n_end, z_c, sgn, avail) in ((-Dr, T - t, 1.0, avail_r), (-Df, B + t, -1.0, avail_f)):
            rc = np.clip(0.5 * avail, 0.0, R_OUT)
            cn, cz = n_end + rc, z_c + sgn * rc          # the round's centre, inside the material
            zlo, zhi = (z_c - 1.0, z_c + rc) if sgn > 0 else (z_c - rc, z_c + 1.0)
            sq = round_box2(nn, z, n_end - 1.0, n_end + rc, zlo, zhi, 0, 0, 0, 0)
            corner = np.maximum(sq, -(np.hypot(nn - cn, z - cz) - rc))
            sdf = np.maximum(sdf, -corner)
        # the bead: a half round on the rail's front edge, faded out round the corners
        # on the rail it runs along the front edge, right under the door's lip (which starts
        # cover_edge_n behind the front), so the lip rests on it; where the rail runs out round the
        # corners it slides onto the middle of the wall's top and carries on as a rounded ridge
        hb = rb
        a_ = np.clip((Dr - t) / 7.0, 0, 1)
        nc = -BEAD_N * a_ - (t / 2) * (1 - a_)
        bead = np.hypot(nn - nc, z - (T - 0.3)) - (hb + 0.3)
        sdf = smin(sdf, bead, 0.8 * np.clip(hb / 0.6, 0, 1))
        return sdf

    def body(self, x, y, z):
        """SDF of the swept shell with rounded ear tips. x, y: (N,), z: (M,) -> (N, M)."""
        sc, nn, e = self.project(x, y)
        T, B, Dr, Df, rb, Rl = [a[:, None] for a in self.params(sc)]
        sec = self.section(nn[:, None], z[None, :], T, B, Dr, Df, rb, Rl)
        return inter_round(sec, e[:, None] + 0.0 * z[None, :], R_EDGE)


# ---------- features ----------

def feature_geometry(sw):
    """Windows, tongue and screw holes: the same geometry as bezel_cad.features, and the door."""
    zc = g.pod_zc(P)
    ww, wh = P.pod_face_w + 2 * P.window_clear_x, P.pod_face_h + 2 * P.window_clear_y
    floor_top = g.shell_levels(P)[2] - 0.15
    z_bot = floor_top - T_WALL + RL_MAX + 0.1      # the sill sits just on top of the rolled lip
    z_topw = zc + wh / 2
    wins = [(px, py, (z_bot + z_topw) / 2, ww / 2, (z_topw - z_bot) / 2) for (px, py, _) in g.pod_poses(P)]

    F = g.front_frame(P)
    z_top = g.shell_levels(P)[0]
    ul, ur = P.clip_u - P.tongue_w / 2, P.clip_u + P.tongue_w / 2
    g0 = [g.clip_n(P, u) + P.groove_clear for u in (ul, ur)]
    g1 = [g.clip_n(P, u) - P.clip_bar_t - P.groove_clear for u in (ul, ur)]
    tb = [n_ - P.tooth_len for n_ in g1]
    rw = P.tongue_root_w / 2
    n_r = -P.blade_depth + 1.5
    n_n = min(g0) + 7
    lip_c = z_top + float(g.top_rise(P, P.clip_u))

    def xy(u, n_):
        return g._fpt(F, u, n_ + float(g.bow(P, u)))
    tongue = np.array([xy(ul, tb[0]), xy(ur, tb[1]), xy(ur, n_n), xy(P.clip_u + rw, n_r),
                       xy(P.clip_u - rw, n_r), xy(ul, n_n)])
    su0, su1 = P.clip_u - P.tongue_slot_w / 2, P.clip_u + P.tongue_slot_w / 2
    slot = np.array([xy(su0, n_n - 2), xy(su1, n_n - 2), xy(su1, n_r - 4), xy(su0, n_r - 4)])
    groove = np.array([xy(ul - 1, g1[0] - P.clip_skew), xy(ur + 1, g1[1] + P.clip_skew),
                       xy(ur + 1, g0[1] + P.clip_skew), xy(ul - 1, g0[0] - P.clip_skew)])
    # the tooth's chamfer: from 2.4 mm down at the tooth's end, up to the top 5.67 mm further in
    ta, tb_ = xy(ul - 1, tb[0] - P.clip_skew - 1), xy(ur + 1, tb[1] + P.clip_skew - 1)
    tooth = (ta, tb_, lip_c - 2.4, 3.4 / 5.67)

    holes = []
    for name in ("hood", "fender"):
        for h in sw.sides[name]["holes"]:
            holes.append((np.asarray(h["at"], float), np.asarray(h["normal"], float) / np.linalg.norm(h["normal"])))
    return dict(wins=wins, tongue=tongue, slot=slot, groove=groove, tooth=tooth, lip_c=lip_c,
                holes=holes, door=door_lookup())


DOOR_SDF = os.path.join(HERE, "door_sdf.npz")
DOOR_GAP = 0.3      # between the ears and the door


def make_door_sdf(door_npz, step=1.0):
    """Sample the door's signed distance (negative inside) on a 1 mm grid round each ear and save
    it to door_sdf.npz, so the bezel can be cut clear of the door without the door scan itself.
    door_npz is cover_scan.py's SAVE_DOOR output (vertices v, faces f of the measured door)."""
    import igl
    d = np.load(door_npz)
    V, Fc = d["v"].astype(np.float64), d["f"].astype(np.int64)
    out = {}
    for name, (xa, xb) in (("hood", (-166.0, -110.0)), ("fender", (110.0, 176.0))):
        xs, ys, zs = np.arange(xa, xb, step), np.arange(-215.0, 40.0, step), np.arange(-4.0, 76.0, step)
        G = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
        sd = igl.signed_distance(G, V, Fc)[0]
        out[name] = np.clip(sd, -8, 8).astype(np.float16).reshape(len(xs), len(ys), len(zs))
        out[name + "_o"] = np.array([xa, -215.0, -4.0, step])
        print("door sdf", name, out[name].shape, flush=True)
    np.savez_compressed(DOOR_SDF, **out)


def door_lookup():
    """Trilinear lookup into door_sdf.npz: f(x, y, z) -> signed distance to the door (8 = far)."""
    if not os.path.exists(DOOR_SDF):
        return None
    d = np.load(DOOR_SDF)
    grids = [(d[n].astype(np.float32), d[n + "_o"]) for n in ("hood", "fender")]

    def f(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z)
        out = np.full(x.shape, 8.0, np.float32)
        for G, (xa, ya, za, st) in grids:
            fx, fy, fz = (x - xa) / st, (y - ya) / st, (z - za) / st
            m = (fx >= 0) & (fy >= 0) & (fz >= 0) & (fx < G.shape[0] - 1) & (fy < G.shape[1] - 1) & (fz < G.shape[2] - 1)
            if not m.any():
                continue
            i, j, k = np.floor(fx[m]).astype(int), np.floor(fy[m]).astype(int), np.floor(fz[m]).astype(int)
            u, v, w = fx[m] - i, fy[m] - j, fz[m] - k
            acc = 0.0
            for di in (0, 1):
                for dj in (0, 1):
                    for dk in (0, 1):
                        acc = acc + G[i + di, j + dj, k + dk] * (u if di else 1 - u) * (v if dj else 1 - v) * (w if dk else 1 - w)
            # fade in over 6 mm from the grid's inner end, so the cut has no step there
            x_in = xa + (G.shape[0] - 1) * st if xa < 0 else xa
            fade = np.clip((np.abs(x[m] - x_in) - 1.0) / 6.0, 0, 1)
            out[m] = fade * acc + (1 - fade) * 8.0
        return out
    return f


def apply_features(F, x, y, z, fg, pointwise=False, outside=None, door=None):
    """F (N, M) for plan points x, y (N,) and heights z (M,); pointwise: z (N,) and F (N, 1).
    outside: the sweep's distance out past its outside face at each plan point (N, 1)."""
    X, Y = x[:, None], y[:, None]
    Z = z[:, None] if pointwise else z[None, :]
    # the tongue: a thin tapered plate, top at the door's lip, blended into the rail
    lip_c = fg["lip_c"]
    plan = round_poly_sdf(x, y, fg["tongue"], 2.0)[:, None]
    slab = np.abs(Z - (lip_c - T_WALL / 2)) - T_WALL / 2
    tongue = inter_round(plan, slab + 0 * plan, R_EDGE)
    slot = round_poly_sdf(x, y, fg["slot"], 1.5)[:, None] + 0 * Z
    tongue = diff_round(tongue, slot, R_EDGE)
    groove = inter_round(round_poly_sdf(x, y, fg["groove"], R_EDGE)[:, None] + 0 * Z, (lip_c - P.groove_depth) - Z, R_EDGE)
    tongue = diff_round(tongue, groove, R_EDGE)
    # the tooth's chamfer: w is the distance in from the tooth's end, and everything above a
    # plane from 2.4 mm down at the end, rising to the top 5.67 mm in, is taken off
    ta, tb, z0, slope = fg["tooth"]
    dx, dy = tb[0] - ta[0], tb[1] - ta[1]
    L = np.hypot(dx, dy)
    w = ((X - ta[0]) * dy - (Y - ta[1]) * dx) / L
    c = np.mean(fg["tongue"][2:6], axis=0) - ta
    if (c[0] * dy - c[1] * dx) < 0:                          # w grows into the tongue
        w = -w
    above = -(Z - (z0 + w * slope)) / np.hypot(1, slope)   # negative above the plane
    tongue = diff_round(tongue, np.maximum(above, w - 7.0), R_EDGE)
    F = union_round(F, tongue, 1.2)
    # a tunnel round each light: a 3 mm sleeve on the window's outline from the front wall back
    # to just in front of the pod's face, so each light is closed in all round. Solid blocks are blended in first
    # (neighbouring ones merge into the posts), then each opening is cut once, front to back.
    blocks = None
    for (px, py, zc, hw, hh) in fg["wins"]:
        blk = round_rect_xz(X - px, Z - zc, hw + T_WALL, hh + T_WALL, WIN_R + T_WALL)
        blk = inter_round(blk, (py - TUNNEL_BACK) - Y + 0 * Z, R_EDGE)        # rounded back rim
        blk = inter_round(blk, outside + 1.5 + 0 * Z, R_EDGE)                 # ends inside the front wall
        blocks = blk if blocks is None else smin(blocks, blk, 2.0)
    F = union_round(F, blocks, 2.0)
    for (px, py, zc, hw, hh) in fg["wins"]:
        w = inter_round(round_rect_xz(X - px, Z - zc, hw, hh, WIN_R), (py - TUNNEL_BACK - 2.0) - Y + 0 * Z, R_EDGE)
        F = diff_round(F, w, R_WIN_EDGE)
    # a round boss on each of the door's flange holes, from the flange out to the ear, blended in
    axes = []
    for (at, nv) in fg["holes"]:
        vx, vy, vz = X - at[0], Y - at[1], Z - at[2]
        along = vx * nv[0] + vy * nv[1] + vz * nv[2]
        rad = np.sqrt(np.maximum(vx * vx + vy * vy + vz * vz - along * along, 0))
        axes.append(rad)
        boss = inter_round(rad - BOSS_R, np.maximum(-1.0 - along, along - 8.0), R_EDGE)
        # it ends inside the ear's wall (a boss face flush with the outside face would bulge in the blend)
        boss = inter_round(boss, outside + 1.6 + 0 * boss, R_EDGE)
        F = union_round(F, boss, 1.5)
    # clear of the door (the ears' inside follows it where it comes within the wall)
    if door is not None:
        F = diff_round(F, door(X, Y, Z) - DOOR_GAP, R_EDGE)
    # the screw holes along each flange hole's axis
    for rad in axes:
        F = diff_round(F, rad - P.ear_hole_d / 2, R_EDGE)
    return F


def sdf_points(sw, fg, pts):
    """The whole SDF at arbitrary points (N x 3), for checking the mesh."""
    out = np.empty(len(pts))
    for a in range(0, len(pts), 200000):
        q = pts[a:a + 200000]
        sc, nn, e = sw.project(q[:, 0], q[:, 1])
        T, B, Dr, Df, rb, Rl = sw.params(sc)
        F = inter_round(sw.section(nn, q[:, 2], T, B, Dr, Df, rb, Rl), e, R_EDGE)
        out[a:a + len(q)] = apply_features(F[:, None], q[:, 0], q[:, 1], q[:, 2], fg, pointwise=True,
                                           outside=nn[:, None], door=fg["door"])[:, 0]
    return out


def snap(verts, sw, fg, iters=4, tol=1e-3):
    """Move each vertex onto the exact surface (F = 0) with Newton steps along the gradient,
    so the mesh lies on the true surface and only the flat triangles between vertices differ."""
    v = verts.copy()
    idx = np.arange(len(v))
    for _ in range(iters):
        F = sdf_points(sw, fg, v[idx])
        keep = np.abs(F) > tol
        idx, F = idx[keep], F[keep]
        if not len(idx):
            break
        p, e = v[idx], 0.01
        gr = np.stack([(sdf_points(sw, fg, p + e * ax) - sdf_points(sw, fg, p - e * ax)) / (2 * e)
                       for ax in np.eye(3)], 1)
        step = (F / np.maximum((gr * gr).sum(1), 1e-6))[:, None] * gr
        ln = np.linalg.norm(step, axis=1)
        step *= (np.minimum(ln, 0.1) / np.maximum(ln, 1e-12))[:, None]
        v[idx] = p - step
        print(f"  snap: {len(idx)} vertices moved, largest {ln.max():.3f} mm", flush=True)
    return v


def split_faces(v, f, sel):
    """Split the selected triangles in four (edge midpoints) and their neighbours in two or three
    along the same edges, so the mesh stays closed with no T-junctions."""
    rows = np.arange(len(f))
    e = np.sort(np.stack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]], 1), axis=2).astype(np.int64)
    key = e[..., 0] * len(v) + e[..., 1]
    todo = np.unique(key[sel].ravel())
    is_s = np.isin(key, todo)
    mid = np.full(key.shape, -1, np.int64)
    mid[is_s] = len(v) + np.searchsorted(todo, key[is_s])
    a_, b_ = todo // len(v), todo % len(v)
    v2 = np.vstack([v, (v[a_] + v[b_]) / 2])
    ns = is_s.sum(1)
    out = [f[ns == 0]]
    m = ns == 3
    A, B, C = f[m, 0], f[m, 1], f[m, 2]
    m0, m1, m2 = mid[m, 0], mid[m, 1], mid[m, 2]
    out += [np.c_[A, m0, m2], np.c_[m0, B, m1], np.c_[m2, m1, C], np.c_[m0, m1, m2]]
    for cnt in (1, 2):
        idx = rows[ns == cnt]
        if not len(idx):
            continue
        # rotate each face so its split edge is edge 0 (one split) or its whole edge is edge 2 (two)
        k = np.argmax(is_s[idx], 1) if cnt == 1 else np.argmin(is_s[idx], 1)
        r = k if cnt == 1 else (k + 1) % 3
        A, B, C = (f[idx, (r + j) % 3] for j in range(3))
        M0, M1 = mid[idx, r], mid[idx, (r + 1) % 3]
        if cnt == 1:
            out += [np.c_[A, M0, C], np.c_[M0, B, C]]
        else:
            out += [np.c_[M0, B, M1], np.c_[A, M0, M1], np.c_[A, M1, C]]
    return v2, np.vstack(out), len(v)


def refine(verts, faces, sw, fg, tol=0.025, rounds=3):
    """Where a flat triangle still strays more than tol from the true surface (tight curves), split
    it and put the new points on the surface; everywhere else the triangles are already close."""
    for _ in range(rounds):
        c = verts[faces].mean(1)
        F = np.abs(sdf_points(sw, fg, c))
        cand = np.flatnonzero(F > tol * 0.5)
        if len(cand):
            p, e = c[cand], 0.01
            gr = np.stack([(sdf_points(sw, fg, p + e * ax) - sdf_points(sw, fg, p - e * ax)) / (2 * e)
                           for ax in np.eye(3)], 1)
            F[cand] = F[cand] / np.maximum(np.linalg.norm(gr, axis=1), 0.3)
        # only triangles still big enough to matter (tiny ones sit on a crease the field can't settle)
        tri = verts[faces]
        longest = np.max(np.linalg.norm(tri - np.roll(tri, 1, axis=1), axis=2), axis=1)
        sel = (F > tol) & (longest > 0.15)
        if not sel.any():
            break
        verts, faces, n0 = split_faces(verts, faces, sel)
        verts[n0:] = snap(verts[n0:], sw, fg)
        print(f"  refine: split {sel.sum()} triangles, now {len(faces)}", flush=True)
    return verts, faces


def decimate(verts, faces, target):
    """Fewer, larger triangles on the flat and gently curved parts (quadric edge collapse, keeping
    the topology); the vertices are snapped back onto the surface and refined afterwards."""
    import pymeshlab
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(verts.astype(np.float64), faces.astype(np.int32)))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=int(target), preservetopology=True, preservenormal=True,
                                                optimalplacement=True, planarquadric=True, qualitythr=0.4)
    m = ms.current_mesh()
    return np.asarray(m.vertex_matrix(), float), np.asarray(m.face_matrix(), np.int64)


def self_hits(verts, faces):
    """Triangles that cut through another one (checked in float32, as the STL is written)."""
    import pymeshlab
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(verts.astype(np.float32).astype(np.float64), faces.astype(np.int32)))
    ms.compute_selection_by_self_intersections_per_face()
    return np.flatnonzero(ms.current_mesh().face_selection_array())


def untangle(verts, faces, sw, fg, rounds=8):
    """Where the simplified mesh folded a few triangles over each other, move those vertices (and
    their neighbours) to the middle of their neighbours and back onto the surface, until none cross."""
    import trimesh
    nb = trimesh.Trimesh(verts, faces, process=False).vertex_neighbors
    for _ in range(rounds):
        bad = self_hits(verts, faces)
        print(f"  untangle: {len(bad)} crossing triangles", flush=True)
        if not len(bad):
            break
        vs = set(faces[bad].ravel())
        for v in list(vs):
            vs.update(nb[v])
        vs = np.array(sorted(vs))
        verts[vs] = np.array([verts[nb[v]].mean(0) for v in vs])
        verts[vs] = snap(verts[vs], sw, fg)
    return verts


def build(h=H):
    t0 = time.time()
    sw = Sweep()
    fg = feature_geometry(sw)
    x0, x1 = sw.path[:, 0].min() - 6, sw.path[:, 0].max() + 6
    y0 = min(sw.path[:, 1].min(), fg["tongue"][:, 1].min()) - 6
    y1 = sw.path[:, 1].max() + 6
    z0, z1 = sw.B.min() - 6, max(sw.T.max(), fg["lip_c"]) + 6
    xs = np.arange(x0, x1, h)
    ys = np.arange(y0, y1, h)
    zs = np.arange(z0, z1, h)
    print(f"grid {len(xs)} x {len(ys)} x {len(zs)} = {len(xs) * len(ys) * len(zs) / 1e6:.0f} M", flush=True)
    V = np.full((len(xs), len(ys), len(zs)), 4.0, np.float32)
    tb = fg["tongue"]
    tbox = (tb[:, 0].min() - 4, tb[:, 0].max() + 4, tb[:, 1].min() - 4, tb[:, 1].max() + 4)
    Dm = np.maximum(sw.Dr, sw.Df)
    for i in range(0, len(xs), 8):
        X, Y = np.meshgrid(xs[i:i + 8], ys, indexing="ij")
        x, y = X.ravel(), Y.ravel()
        sc, nn, e = sw.project(x, y)
        dm = np.interp(sc, np.arange(sw.n), Dm)
        act = ((nn > -dm - 8) & (nn < 4) & (e < 4)) | \
              ((x > tbox[0]) & (x < tbox[1]) & (y > tbox[2]) & (y < tbox[3]))
        for (px, py, _, hw, _) in fg["wins"]:                  # the tunnels round the lights
            act |= (np.abs(x - px) < hw + T_WALL + 5) & (y > py - TUNNEL_BACK - 6) & (nn < 4)
        if not act.any():
            continue
        F = sw.body(x[act], y[act], zs)
        F = apply_features(F, x[act], y[act], zs, fg, outside=nn[act][:, None], door=fg["door"])
        blk = np.full((len(x), len(zs)), 4.0, np.float32)
        blk[act] = np.clip(F, -4, 4)
        V[i:i + 8] = blk.reshape(X.shape[0], X.shape[1], len(zs))
    print(f"field {time.time() - t0:.0f} s", flush=True)
    from skimage.measure import marching_cubes
    # a grid point sitting right on the surface makes zero-size slivers; nudge it 0.001 mm out
    V[np.abs(V) < 1e-3] = 1e-3
    verts, faces, _, _ = marching_cubes(V, level=0.0, spacing=(h, h, h))
    verts += np.array([xs[0], ys[0], zs[0]])
    print(f"meshed {len(faces)} triangles, {time.time() - t0:.0f} s", flush=True)
    verts = snap(verts, sw, fg)
    verts, faces = decimate(verts, faces, TARGET_FACES)
    print(f"decimated to {len(faces)} triangles, {time.time() - t0:.0f} s", flush=True)
    verts = snap(verts, sw, fg)
    print(f"snapped, {time.time() - t0:.0f} s", flush=True)
    verts, faces = refine(verts, faces, sw, fg, rounds=6)
    for _ in range(4):                          # untangling can leave a triangle off; refine again
        verts = untangle(verts, faces, sw, fg)
        n_before = len(faces)
        verts, faces = refine(verts, faces, sw, fg, rounds=3)
        if len(faces) == n_before:
            break
    print(f"refined, {time.time() - t0:.0f} s", flush=True)
    return verts, faces, sw, fg


if __name__ == "__main__":
    import trimesh
    if os.environ.get("DOOR_MODEL"):           # resample the door (cover_scan.py SAVE_DOOR output)
        make_door_sdf(os.environ["DOOR_MODEL"])
    verts, faces, sw, fg = build()
    tm = trimesh.Trimesh(verts, faces, process=True)
    if tm.volume < 0:
        tm.invert()
    out = os.path.join(HERE, "stl", "cad", "bezel_cad_passenger.stl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tm.export(out)
    import pymeshlab
    ms = pymeshlab.MeshSet()
    saved = trimesh.load(out)                  # check the file itself (float32, as written)
    ms.add_mesh(pymeshlab.Mesh(saved.vertices, saved.faces))
    ms.compute_selection_by_self_intersections_per_face()
    print("watertight", saved.is_watertight, "volume", round(saved.volume), "self-intersecting faces",
          ms.current_mesh().selected_face_number(), "->", out, flush=True)
