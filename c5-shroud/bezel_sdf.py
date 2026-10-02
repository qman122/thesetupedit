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
  each opening into a 3 mm tunnel that curves in to hug its pod and runs back past the pod's
  face, so every light sits inside its tunnel. The posts are what's left between them.
- The clip tongue is a thin tapered plate blended into the rail.
- Every edge is rounded, 1 mm or more.

The face is styled by bezel_styles.py (BEZEL_STYLE, C7 by default: a recessed housing with
raked windows and blades, a light blade under the pods and a ladder at the fender end).

Writes stl/cad/bezel_cad_passenger.stl and stl/cad/drl_inserts_passenger.stl (model frame);
generate.py picks them up.
Run: python3 bezel_sdf.py   (about 20-30 minutes)
"""
import os
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bezel_cad as bc  # noqa: E402  (path, section parameters and fit, shared with the CAD loft)
import bezel_styles as bs  # noqa: E402  (light slots, frames, tray: BEZEL_STYLE)

g, P = bc.g, bc.P
HERE = bc.HERE
T_WALL = bc.T_WALL
H = 0.25            # grid step, mm: the mesh follows the surface to about 0.01 mm (see the check)
WIN_R = 12.0        # window corner radius
R_WIN_EDGE = 1.5    # round on the windows' edges
R_EDGE = 1.0        # smallest round anywhere else
R_OUT = 1.2         # the rail's and floor's outside corners
BOSS_R = 7.5        # screw bosses on the ears
TUNNEL_BACK = 18.0  # the tunnels round the lights reach this far back past each pod's face (the
                    # pod's bracket starts 24 mm back)
TUNNEL_CLEAR = 1.0  # round the pod's body inside the tunnel
TUNNEL_T = 3.5      # the tunnels' side and top walls (a little over 3 so the taper doesn't thin them)
OUTER_FILL = 14.0   # the outer tunnels' outboard walls reach this much further out, to the corner walls
TONGUE_T = 5.0      # the clip tongue's thickness
FLARE_SIDE = 0.5    # the opening at the front: this much wider each side than the window,
FLARE_TOP = 6.0     # and up to this much taller at the top (less where the rail comes lower)
FLOOR_B = g.shell_levels(P)[2] - 0.15 - T_WALL   # the underside of the floor across the front
RL_MAX = 4.0        # the rolled bottom lip's radius across the front
BEAD_N = P.cover_edge_n + 2.5   # the bead's centre behind the front: under the middle of the door's lip
TARGET_FACES = 600_000   # after simplifying (the refine step adds back what the 0.05 mm needs)
STYLE = os.environ.get("BEZEL_STYLE", "C7")  # "C7" (the default), "A", "B", "C", "BC", or "plain" (see bezel_styles.py)
STYLE = "" if STYLE == "plain" else STYLE


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
        self.Bw = self.B.copy()        # the front wall's bottom: the style can bring it lower (a chin)
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
            self._pcs = CubicSpline(np.arange(self.n), np.c_[self.T, self.B, self.Dr, self.Df, self.rb, self.Rl, self.Bw])
        v = self._pcs(sc)
        return [v[..., k] for k in range(7)]

    def section(self, nn, z, T, B, Dr, Df, rb, Rl, Bw=None):
        """The C section at (n, z): outside minus the channel, both with rounded corners, so
        every corner of the section is exactly round; the bead added with a smooth union.
        Bw, where it's below B, carries the front wall down below the floor (the chin)."""
        t = T_WALL
        zm = (T + B) / 2
        rail = round_box2(nn, z, -Dr, 0.0, zm - 1.0, T, R_OUT, 0.0, R_OUT, 0.0)
        floor = round_box2(nn, z, -Df, 0.0, B, zm + 1.0, 0.0, Rl, 0.0, R_OUT)
        outer = np.minimum(rail, floor)
        if Bw is not None and np.any(Bw < B - 1e-3):
            # the wall's own box, with the same rounds the floor has where the floor is just
            # the wall (so they coincide where the chin fades out); filleted into the floor's
            # underside where the floor runs back behind it
            wall = round_box2(nn, z, -t, 0.0, Bw, B + t, 0.0, Rl, 0.0, R_OUT)
            r = np.clip((-nn - 1.5) / 1.0, 0, 1) * np.clip((Df - 4.0) / 3.0, 0, 1) * np.clip((B - Bw) / 0.5, 0, 1)
            outer = union_round(outer, wall, r)
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
        T, B, Dr, Df, rb, Rl, Bw = [a[:, None] for a in self.params(sc)]
        sec = self.section(nn[:, None], z[None, :], T, B, Dr, Df, rb, Rl, Bw)
        return inter_round(sec, e[:, None] + 0.0 * z[None, :], R_EDGE)


# ---------- features ----------

def feature_geometry(sw):
    """Windows, tongue and screw holes: the same geometry as bezel_cad.features, and the door."""
    zc = g.pod_zc(P)
    ww, wh = P.pod_face_w + 2 * P.window_clear_x, P.pod_face_h + 2 * P.window_clear_y
    poses = [(px, py) for (px, py, _) in g.pod_poses(P)]
    if bs.is_proj(STYLE):              # small projectors instead of the pods (bezel_styles.PROJ...)
        # the openings are a little smaller than the heads (PROJ_LIP), so the bezel frames each
        # head's face and no gap round it shows from the front, even a little out of line
        ww, wh = bs.PROJ_W - 2 * bs.PROJ_LIP[0], bs.PROJ_H - 2 * bs.PROJ_LIP[1]
        zc = zc + bs.PROJ_LIFT
        # each tunnel ends 0.5 mm in front of where its head's front goes (1 mm behind this)
        poses = [(x, yf + 1.0) for x, yf in bs.proj_layout(STYLE, [py for _, py in poses])]
    floor_top = g.shell_levels(P)[2] - 0.15
    z_bot = floor_top - T_WALL + RL_MAX + 1.0      # the sill sits 1 mm above the rolled lip's top, so the
                                                   # lip under it is solid (not a thin upturned edge)
    if bs.is_proj(STYLE):              # the sill just under the projector, with the light strip below it
        z_bot = zc - bs.PROJ_H / 2 + bs.PROJ_LIP[1]
    z_topw = zc + wh / 2
    wins = [(px, py, (z_bot + z_topw) / 2, ww / 2, (z_topw - z_bot) / 2) for (px, py) in poses]
    # the tunnels: behind each pod's face they hug the pod's body (TUNNEL_CLEAR all round, small
    # corners); forward of it they curve out to the opening at the front, which is a little wider
    # than the window and taller where the rail leaves room above it
    tunnels = []
    for (px, py) in poses:
        zb0, zb1 = P.pod_lift - TUNNEL_CLEAR, g.pod_top(P) + TUNNEL_CLEAR
        back = (P.pod_body_w / 2 + TUNNEL_CLEAR, (zb1 - zb0) / 2, (zb0 + zb1) / 2, 3.0)
        if bs.is_proj(STYLE):
            zb0, zb1 = zc - bs.PROJ_H / 2 + bs.PROJ_LIP[1], zc + bs.PROJ_H / 2 - bs.PROJ_LIP[1]
            back = (bs.PROJ_W / 2 - bs.PROJ_LIP[0], (zb1 - zb0) / 2, (zb0 + zb1) / 2, 1.0)   # near-square heads
        on = np.abs(sw.path[:, 0] - px) < ww / 2 + 4
        rail_under = float(np.min(sw.T[on & (sw.path[:, 1] > -60)])) - T_WALL
        flare = 0.0 if STYLE in ("B", "C", "BC", "C7") or bs.is_proj(STYLE) else FLARE_TOP     # even windows for the frames and the tray
        top = max(z_topw, min(z_topw + flare, rail_under - T_WALL - 2.0))
        front = (ww / 2 + FLARE_SIDE, (top - z_bot) / 2, (top + z_bot) / 2, 3.0 if STYLE in ("B", "BC") else 2.5 if STYLE == "C7" else 5.0 if bs.is_proj(STYLE) else WIN_R)
        if STYLE == "P3J":     # straight-sided pockets: the style chamfers them (bezel_styles.POCKET_CHAMFER)
            front = (ww / 2, (top - z_bot) / 2, (top + z_bot) / 2, 1.0)
        tunnels.append((px, py, back, front))

    F = g.front_frame(P)
    z_top = g.shell_levels(P)[0]
    ul, ur = P.clip_u - P.tongue_w / 2, P.clip_u + P.tongue_w / 2
    g0 = [g.clip_n(P, u) + P.groove_clear for u in (ul, ur)]
    rw = P.tongue_root_w / 2
    n_r = -P.blade_depth + 1.5
    n_n = min(g0) + 7
    lip_c = z_top + float(g.top_rise(P, P.clip_u))

    def xy(u, n_):
        return g._fpt(F, u, n_ + float(g.bow(P, u)))
    # it ends where its taper ends: on the car the owner's fit test clipped on once the narrow
    # end (the groove and tooth behind it) was cut off there
    n_end = n_n
    tongue = np.array([xy(ul, n_end), xy(ur, n_end), xy(P.clip_u + rw, n_r), xy(P.clip_u - rw, n_r)])
    su0, su1 = P.clip_u - P.tongue_slot_w / 2, P.clip_u + P.tongue_slot_w / 2
    slot = np.array([xy(su0, n_end + 4), xy(su1, n_end + 4), xy(su1, n_r - 4), xy(su0, n_r - 4)])
    # the tip's chamfer: from 2.4 mm down at the tip, up to the top 5.67 mm in, so it slides
    # in under the clip
    ta, tb_ = xy(ul - 1, n_end - 1), xy(ur + 1, n_end - 1)
    tooth = (ta, tb_, lip_c - 2.4, 3.4 / 5.67)

    holes = []
    for name in ("hood", "fender"):
        for h in sw.sides[name]["holes"]:
            holes.append((np.asarray(h["at"], float), np.asarray(h["normal"], float) / np.linalg.norm(h["normal"])))
    fg = dict(wins=wins, tunnels=tunnels, tongue=tongue, slot=slot, tooth=tooth, lip_c=lip_c,
              holes=holes, door=door_lookup())
    # projectors sit just behind their tunnels, not inside them, so a little misalignment between
    # the bezel (on the door) and the bracket (on the arm) can't make them rub
    fg["tunnel_back"] = 0.5 if bs.is_proj(STYLE) else TUNNEL_BACK
    fg["style"] = bs.Style(STYLE, sw, fg, sys.modules[__name__]) if STYLE else None
    return fg


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


def apply_features(F, x, y, z, fg, pointwise=False, outside=None, door=None, sc=None):
    """F (N, M) for plan points x, y (N,) and heights z (M,); pointwise: z (N,) and F (N, 1).
    outside: the sweep's distance out past its outside face at each plan point (N, 1); sc: the
    path parameter of each plan point (N,), for the face styles."""
    X, Y = x[:, None], y[:, None]
    Z = z[:, None] if pointwise else z[None, :]
    st = fg.get("style")
    sctx = st.ctx(X, Z, outside, sc, Y) if st is not None else None
    # the tongue: a thin tapered plate, top at the door's lip, blended into the rail
    lip_c = fg["lip_c"]
    plan = round_poly_sdf(x, y, fg["tongue"], 2.0)[:, None]
    slab = np.abs(Z - (lip_c - TONGUE_T / 2)) - TONGUE_T / 2
    tongue = inter_round(plan, slab + 0 * plan, R_EDGE)
    slot = round_poly_sdf(x, y, fg["slot"], 1.5)[:, None] + 0 * Z
    tongue = diff_round(tongue, slot, R_EDGE)
    # the tip's chamfer: w is the distance in from the tip, and everything above a plane from
    # 2.4 mm down at the tip, rising to the top 5.67 mm in, is taken off
    ta, tb, z0, slope = fg["tooth"]
    dx, dy = tb[0] - ta[0], tb[1] - ta[1]
    L = np.hypot(dx, dy)
    w = ((X - ta[0]) * dy - (Y - ta[1]) * dx) / L
    c = np.mean(fg["tongue"][2:], axis=0) - ta                # the root, inside the tongue
    if (c[0] * dy - c[1] * dx) < 0:                          # w grows into the tongue
        w = -w
    above = -(Z - (z0 + w * slope)) / np.hypot(1, slope)   # negative above the plane
    tongue = diff_round(tongue, np.maximum(above, w - 7.0), R_EDGE)
    F = union_round(F, tongue, 1.2)
    # a tunnel round each light, from the opening at the front back past the pod's face so the
    # light sits inside it. Its section curves in from the opening to hug the pod (a parabola in
    # the depth, flat at the pod and turning out toward the front). Solid blocks are blended in
    # first (neighbouring ones merge into the posts), then each opening is cut once, front to back.
    def section_at(py, back, front):
        t = Y - py + 0 * Z
        s_ = np.clip(np.where(t > 0, t / np.maximum(t - outside, 1e-3), 0.0), 0, 1)
        e_ = s_ ** 2
        # the floor comes up to the sill over the first half of the depth (smoothly), so it
        # meets the rolled lip at the front solidly instead of leaving the lip's top as a thin fin
        u_ = np.clip(2 * s_, 0, 1)
        eb = u_ * u_ * (3 - 2 * u_)
        (hw_b, hh_b, zc_b, r_b), (hw_f, hh_f, zc_f, r_f) = back, front
        top = (zc_b + hh_b) + ((zc_f + hh_f) - (zc_b + hh_b)) * e_
        bot = (zc_b - hh_b) + ((zc_f - hh_f) - (zc_b - hh_b)) * eb
        return [hw_b + (hw_f - hw_b) * e_, (top - bot) / 2, (top + bot) / 2, r_b + (r_f - r_b) * e_, e_]
    blocks = None
    n_t = len(fg["tunnels"])
    for k, (px, py, back, front) in enumerate(fg["tunnels"]):
        hw, hh, zc_, r_, e_ = section_at(py, back, front)
        # flat along the bottom (a 3 mm wall), so the posts between the tunnels stand on the floor;
        # the outer tunnels reach out to the corner walls, so there's no thin slit between them
        z_lo = zc_ - hh - T_WALL
        r_lo = 1.5 + 0 * r_
        bx = st.block_extra if st is not None else 0.0    # wider where the style chamfers the pockets
        x0 = -hw - TUNNEL_T - bx - (OUTER_FILL if k == 0 else 0.0)
        x1 = hw + TUNNEL_T + bx + (OUTER_FILL if k == n_t - 1 else 0.0)
        lean = st.shear(Z - zc_, e_) if st is not None else 0.0
        blk = round_box2(X - px - lean, Z, x0, x1, z_lo, zc_ + hh + TUNNEL_T,
                         r_ + TUNNEL_T, r_lo, r_ + TUNNEL_T, r_lo)
        blk = inter_round(blk, (py - fg.get("tunnel_back", TUNNEL_BACK)) - Y + 0 * Z, R_EDGE)        # rounded back rim
        blk = inter_round(blk, outside + 1.5 + 0 * Z, R_EDGE)                 # ends inside the front wall
        blocks = blk if blocks is None else smin(blocks, blk, 2.0)
    # the blend is 2 mm, shrinking to 0.5 mm near the floor's underside, which the tunnels' bottoms
    # run just above (a bigger blend there would bulge it)
    F = union_round(F, blocks, 0.5 + 1.5 * np.clip((Z - FLOOR_B - 1.5) / 1.5, 0, 1))
    if bs.is_proj(STYLE):
        # a boss round the print split's dowel pin (generate.dowel_spot), where the floor is thin
        us_, n_d, zs_d = g.dowel_spot(P)
        Fm = np.asarray(g.front_frame(P))
        ax_ = Fm[:, 0]
        for z_d in zs_d:
            c_ = Fm[:, :3] @ np.array([us_, n_d, z_d]) + Fm[:, 3]
            vx, vy, vz = X - c_[0], Y - c_[1], Z - c_[2]
            along = vx * ax_[0] + vy * ax_[1] + vz * ax_[2]
            rad = np.sqrt(np.maximum((vx - along * ax_[0]) ** 2 + (vy - along * ax_[1]) ** 2 + (vz - along * ax_[2]) ** 2, 0))
            boss = np.maximum(rad - (P.dowel_d / 2 + 2.0), np.abs(along) - (P.dowel_depth + 2.0))
            F = union_round(F, boss, 1.0)
    keep = None
    if st is not None:
        F = st.solids(F, sctx)            # chin, tray backing, pod frames, light channels' walls
        F = st.pre_cuts(F, sctx)          # the tray, its light bar and its fins
        keep = st.keep(sctx)
    for (px, py, back, front) in fg["tunnels"]:
        hw, hh, zc_, r_, e_ = section_at(py, back, front)
        shape = st.window(X - px, Z - zc_, hw, hh, r_, e_, t=Y - py + 0 * Z, outside=outside) if st is not None else None
        if shape is None:
            shape = round_rect_xz(X - px, Z - zc_, hw, hh, r_)
        w = inter_round(shape, (py - fg.get("tunnel_back", TUNNEL_BACK) - 2.0) - Y + 0 * Z, R_EDGE)
        if keep is not None:
            w = diff_round(w, keep, 1.0)
        F = diff_round(F, w, R_WIN_EDGE if st is None or st.win_edge is None else st.win_edge)
    if bs.is_proj(STYLE):
        # behind each head's front the bezel keeps clear of it, 2 mm side to side and 0.75 up and
        # down: the heads are staggered, so a neighbour's tunnel wall runs alongside a head's sides,
        # and the bezel (on the door) and the bracket (on the arm) won't line up exactly. Where two
        # heads are too close for a wall between their clearances, each one's runs to the midpoint.
        hw_, side = bs.PROJ_W / 2, 2.0
        pxs = [t[0] for t in fg["tunnels"]]
        for k, (px, py, back, front) in enumerate(fg["tunnels"]):
            lo, hi = px - hw_ - side, px + hw_ + side
            if k > 0 and (px - hw_) - (pxs[k - 1] + hw_) < 2 * side + 1.5:
                lo = (px - hw_ + pxs[k - 1] + hw_) / 2
            if k < len(pxs) - 1 and (pxs[k + 1] - hw_) - (px + hw_) < 2 * side + 1.5:
                hi = (px + hw_ + pxs[k + 1] - hw_) / 2
            env = round_rect_xz(X - (lo + hi) / 2, Z - back[2], (hi - lo) / 2, bs.PROJ_H / 2 + 0.75, 1.0)
            F = diff_round(F, np.maximum(env, Y - (py - 0.7)), 0.5)      # from 0.3 mm in front of it
    if st is not None:
        F = st.post_cuts(F, sctx)         # the light slots and channels, the frames' bevels
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
        T, B, Dr, Df, rb, Rl, Bw = sw.params(sc)
        F = inter_round(sw.section(nn, q[:, 2], T, B, Dr, Df, rb, Rl, Bw), e, R_EDGE)
        out[a:a + len(q)] = apply_features(F[:, None], q[:, 0], q[:, 1], q[:, 2], fg, pointwise=True,
                                           outside=nn[:, None], door=fg["door"], sc=sc)[:, 0]
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
        print(f"  untangle: {len(bad)} crossing triangles of {len(faces)}, {time.strftime('%H:%M:%S')}", flush=True)
        if not len(bad):
            break
        vs = set(faces[bad].ravel())
        for v in list(vs):
            vs.update(nb[v])
        vs = np.array(sorted(vs))
        verts[vs] = np.array([verts[nb[v]].mean(0) for v in vs])
        verts[vs] = snap(verts[vs], sw, fg)
    return verts


def mend(verts, faces, rounds=4):
    """Last resort for crossings untangle couldn't clear: delete the crossing triangles and a
    ring round them, and close the holes flat (each patch well under a millimetre across)."""
    import pymeshlab
    for _ in range(rounds):
        bad = self_hits(verts, faces)
        print(f"  mend: {len(bad)} crossing triangles", flush=True)
        if not len(bad):
            break
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(verts.astype(np.float64), faces.astype(np.int32)))
        ms.compute_selection_by_self_intersections_per_face()
        ms.apply_selection_dilatation()
        ms.meshing_remove_selected_vertices_and_faces()
        ms.meshing_remove_connected_component_by_face_number(mincomponentsize=200)
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_repair_non_manifold_vertices()
        ms.meshing_close_holes(maxholesize=2000, newfaceselected=False, selfintersection=False)
        m = ms.current_mesh()
        verts, faces = np.asarray(m.vertex_matrix(), float), np.asarray(m.face_matrix(), np.int64)
    return verts, faces


def build(h=H, preview=False):
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
            act |= (np.abs(x - px) < hw + TUNNEL_T + OUTER_FILL + 8) & (y > py - TUNNEL_BACK - 6) & (nn < 4)
        if not act.any():
            continue
        F = sw.body(x[act], y[act], zs)
        F = apply_features(F, x[act], y[act], zs, fg, outside=nn[act][:, None], door=fg["door"], sc=sc[act])
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
    verts, faces = decimate(verts, faces, TARGET_FACES if not preview else 350_000)
    print(f"decimated to {len(faces)} triangles, {time.time() - t0:.0f} s", flush=True)
    verts = snap(verts, sw, fg)
    print(f"snapped, {time.time() - t0:.0f} s", flush=True)
    if preview:                                 # a quick look: no refining
        return verts, faces, sw, fg
    if STYLE:
        # The styled faces have tight rounds next to thin features (light slots, blades), where
        # refining's new points snap across onto the wrong surface and fold the mesh. Their
        # vertices are already on the surface (snapped); only the flat triangles across the
        # tightest rounds sit off it, by less than a print's layer, so they're left as they are.
        verts = untangle(verts, faces, sw, fg)
        verts, faces = mend(verts, faces)
        print(f"untangled, {time.time() - t0:.0f} s", flush=True)
        return verts, faces, sw, fg
    verts, faces = refine(verts, faces, sw, fg, rounds=6)
    for _ in range(4):                          # untangling can leave a triangle off; refine again
        verts = untangle(verts, faces, sw, fg)
        n_before = len(faces)
        verts, faces = refine(verts, faces, sw, fg, rounds=3)
        if len(faces) == n_before:
            break
    print(f"refined, {time.time() - t0:.0f} s", flush=True)
    return verts, faces, sw, fg


def build_inserts(sw, fg, h=0.2):
    """The frosted diffuser inserts for the style's light channels, meshed on their own."""
    st = fg["style"]
    if st is None or not st.channels:
        return None
    from skimage.measure import marching_cubes
    lo = np.min([ch.lo for ch in st.channels], axis=0)
    hi = np.max([ch.hi for ch in st.channels], axis=0)
    xy = sw.cs(np.clip(np.linspace(lo[0], hi[0], 200), 0, sw.L[-1]))
    x0, x1 = xy[:, 0].min() - 15, xy[:, 0].max() + 15
    y0, y1 = xy[:, 1].min() - 15, xy[:, 1].max() + 15
    z0, z1 = lo[1] - 6, hi[1] + 6
    xs, ys, zs = np.arange(x0, x1, h), np.arange(y0, y1, h), np.arange(z0, z1, h)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    sc, nn, e = sw.project(X.ravel(), Y.ravel())
    a = np.interp(sc, np.arange(sw.n), sw.L)[:, None]
    V = np.full((X.size, len(zs)), 4.0, np.float32)
    near = nn > -15
    V[near] = np.clip(st.inserts(a[near], nn[near][:, None], zs[None, :]), -4, 4)
    V = V.reshape(len(xs), len(ys), len(zs))
    V[np.abs(V) < 1e-3] = 1e-3
    verts, faces, _, _ = marching_cubes(V, level=0.0, spacing=(h, h, h))
    return verts + np.array([xs[0], ys[0], zs[0]]), faces


if __name__ == "__main__":
    import trimesh
    if os.environ.get("DOOR_MODEL"):           # resample the door (cover_scan.py SAVE_DOOR output)
        make_door_sdf(os.environ["DOOR_MODEL"])
    verts, faces, sw, fg = build()
    tm = trimesh.Trimesh(verts, faces, process=True)
    parts = tm.split(only_watertight=False)
    if len(parts) > 1:                         # specks a cut can leave behind (well under 1 mm^3)
        print("dropping", len(parts) - 1, "specks of", [round(p.volume, 3) for p in parts if p is not max(parts, key=lambda q: abs(q.volume))], "mm^3", flush=True)
        tm = max(parts, key=lambda q: abs(q.volume))
        v_, f_ = mend(np.asarray(tm.vertices, float), np.asarray(tm.faces))
        tm = trimesh.Trimesh(v_, f_, process=True)
    if tm.volume < 0:
        tm.invert()
    out = os.path.join(HERE, "stl", "cad", g.bezel_cad_name())
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tm.export(out)
    import pymeshlab
    ms = pymeshlab.MeshSet()
    saved = trimesh.load(out)                  # check the file itself (float32, as written)
    ms.add_mesh(pymeshlab.Mesh(saved.vertices, saved.faces))
    ms.compute_selection_by_self_intersections_per_face()
    print("watertight", saved.is_watertight, "volume", round(saved.volume), "self-intersecting faces",
          ms.current_mesh().selected_face_number(), "->", out, flush=True)
    # the diffuser inserts for the light slots (model frame); generate.py lays them out for printing
    ins = build_inserts(sw, fg)
    out_i = os.path.join(HERE, "stl", "cad", g.bezel_cad_name("inserts"))
    if ins is not None:
        ti = trimesh.Trimesh(*ins, process=True)
        if ti.volume < 0:
            ti.invert()
        ti.export(out_i)
        print("inserts", len(ti.split(only_watertight=False)), "pieces ->", out_i, flush=True)
    elif os.path.exists(out_i):
        os.remove(out_i)
