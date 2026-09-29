"""The bezel as real CAD (build123d / OpenCascade), shaped like the reference photo.

One cross-section is lofted along one smooth path: across the front, round the corners and
back along each ear. The section is a thin C: a rolled bottom lip, a shallow floor, a 3 mm
front wall and a thin top rail with a bead on its front edge. Toward the corners the rail
and floor narrow until the section is just the wall, so the ears are the ends of the same
sweep, flattened into thin flanges. Each section is one smooth closed spline, so every edge
along the sweep is rounded. Three rounded-rectangle windows are cut through the front,
centred on the pods; the posts are what's left between them. The clip tongue is a thin
tapered plate on the back of the rail.

The fit is the same as before: the rail's bead meets the door's lip, the ears' top edge
runs along the door's edge and their outside stays just inside the door's outline, with
pockets clear of the door's flange and a screw hole on every flange hole.

Writes stl/cad/bezel_cad_passenger.stl (model frame); generate.shroud() picks it up.
"""
import math
import os
import sys

import numpy as np
from build123d import (Axis, Box, Cylinder, Face, Location, Plane, Polyline, Pos, Solid, Spline, Wire,
                       export_stl, extrude, fillet, loft, Vector, Edge, Rot, make_face)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as g  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
P = g.Params()
P.corner_r = 30.0
T_WALL = 3.0


def smooth(a, k):
    pad = np.pad(a, (k, k), mode="edge")
    return np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode="valid")


def plan_path():
    """The bezel's outside seen from above, hood ear tip to fender ear tip: the outline the
    fitted bezel uses (front, 30 mm corners, sides inside the door's outline)."""
    outline, sides = g.shell_plan(P)
    cs = g.CS([outline])
    ol = g.door_outline(P)
    if ol is not None:
        cs = cs ^ ol.offset(-P.outline_gap, g.m3d.JoinType.Round)
    q = max(cs.to_polygons(), key=lambda a: abs(g.CS([a]).area()))
    q = np.asarray(q, float)
    hood, fen = sides["hood"], sides["fender"]
    rim_h, rim_f = g.door_rim(P, "hood"), g.door_rim(P, "fender")

    def tip(s_, rim):
        yy = np.arange(s_["y_end"] - 15.0, s_["y_end"] + 12.0, 0.5)
        return float(yy[np.argmin(rim(yy))])
    yth, ytf = tip(hood, rim_h), tip(fen, rim_f)
    # walk the boundary, keeping only the front and sides (drop the far back)
    keep = [pt for pt in q if (pt[0] < 0 and pt[1] >= yth) or (pt[0] >= 0 and pt[1] >= ytf)]
    keep = np.asarray(keep)
    # order: start at the hood tip, go forward up the hood side, across the front, back down the fender side
    ang = np.arctan2(keep[:, 1] + 60.0, keep[:, 0])       # about a point behind the front
    o = np.argsort(-ang)[::-1]
    pts = keep[np.argsort(-(np.unwrap(np.arctan2(keep[:, 1] + 80.0, -keep[:, 0]))))]
    # simpler: sort by polar angle round (0, -80), from the hood side (angle ~ pi) to the fender side (~0)
    a2 = np.arctan2(keep[:, 1] + 80.0, keep[:, 0])
    a2 = np.where(a2 < -np.pi / 2, a2 + 2 * np.pi, a2)
    pts = keep[np.argsort(-a2)]
    # resample evenly and smooth a little into one fair curve
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    s = np.arange(0, d[-1], 1.0)
    x = np.interp(s, d, pts[:, 0])
    y = np.interp(s, d, pts[:, 1])
    x, y = smooth(x, 3), smooth(y, 3)
    return np.c_[x, y], sides, (yth, ytf)


def rounded_poly(corners, radii, n_arc=8):
    """Polyline of a closed polygon with each corner rounded by its radius."""
    out = []
    m = len(corners)
    for i in range(m):
        p0, p1, p2 = np.asarray(corners[i - 1]), np.asarray(corners[i]), np.asarray(corners[(i + 1) % m])
        r = radii[i]
        a, b = p0 - p1, p2 - p1
        la, lb = np.linalg.norm(a), np.linalg.norm(b)
        a, b = a / la, b / lb
        ang = math.acos(np.clip(a @ b, -1, 1))
        t = r / math.tan(ang / 2)
        t = min(t, 0.45 * la, 0.45 * lb)
        r = t * math.tan(ang / 2)
        s0, s1 = p1 + a * t, p1 + b * t
        bis = (a + b) / np.linalg.norm(a + b)
        c = p1 + bis * (r / math.sin(ang / 2))
        a0 = math.atan2(*(s0 - c)[::-1])
        a1 = math.atan2(*(s1 - c)[::-1])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n_arc + 1):
            th = a0 + da * k / n_arc
            out.append(c + r * np.array([math.cos(th), math.sin(th)]))
    return np.asarray(out)


def _corner_arc(p0, p1, p2, r, n_arc):
    """Points of the round of radius r at corner p1 (between p0 and p2), and its two ends."""
    p0, p1, p2 = map(np.asarray, (p0, p1, p2))
    a, b = p0 - p1, p2 - p1
    la, lb = np.linalg.norm(a), np.linalg.norm(b)
    a, b = a / la, b / lb
    ang = math.acos(np.clip(a @ b, -1, 1))
    t = min(r / math.tan(ang / 2), 0.45 * la, 0.45 * lb)
    r = t * math.tan(ang / 2)
    s0, s1 = p1 + a * t, p1 + b * t
    bis = (a + b) / np.linalg.norm(a + b)
    c = p1 + bis * (r / math.sin(ang / 2))
    a0 = math.atan2(*(s0 - c)[::-1])
    a1 = math.atan2(*(s1 - c)[::-1])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    return [c + r * np.array([math.cos(a0 + da * k / n_arc), math.sin(a0 + da * k / n_arc)]) for k in range(n_arc + 1)]


def section(T, B, Dr, Df, rb, R_lip, n_arc=4, n_edge=3, n_bead=8):
    """The cross-section in (n, z): n = 0 at the outside face, negative inward. A thin C:
    rail on top (depth Dr), 3 mm front wall, floor at the bottom (depth Df), the front bottom
    corner rolled round R_lip, and a bead of radius rb along the rail's front edge. Every
    corner and edge always gets the same number of points, so from one section to the next each
    point stays on the same feature and the loft can't twist."""
    t = T_WALL
    C = [(-Dr, T - t), (-t, T - t), (-t, B + t), (-Df, B + t), (-Df, B), (0.0, B), (0.0, T), (-Dr, T)]
    R = [0.9, 1.5, 1.5, 0.9, 0.9, R_lip, 1.2, 0.9]
    m = len(C)
    arcs = [_corner_arc(C[i - 1], C[i], C[(i + 1) % m], R[i], n_arc) for i in range(m)]
    pts = []
    for i in range(m):
        pts += arcs[i]
        e0, e1 = np.asarray(arcs[i][-1]), np.asarray(arcs[(i + 1) % m][0])
        if i == 6:                                       # the rail's top, G -> H: the bead sits on it
            # the bead's points always span most of the flat, so they stay spread out; where the
            # bead fades away toward the ears only its height drops
            room = e0[0] - e1[0]
            wb = min(2 * rb, 0.6 * room) if rb > 0.3 else 0.6 * room
            hb = min(rb, wb / 2)
            nc = e0[0] - 0.2 * room - wb / 2
            b0, b1 = np.array([nc + wb / 2, T]), np.array([nc - wb / 2, T])
            for k in range(1, 3):
                pts.append(e0 + (b0 - e0) * k / 3)
            for k in range(n_bead + 1):
                th = math.pi * k / n_bead
                pts.append(np.array([nc + wb / 2 * math.cos(th), T + hb * math.sin(th)]))
            for k in range(1, n_edge):
                pts.append(b1 + (e1 - b1) * k / n_edge)
        else:
            for k in range(1, n_edge):
                pts.append(e0 + (e1 - e0) * k / n_edge)
    return np.asarray(pts)


def sew_runs(wires, cuts_):
    """Loft the sections in runs (OpenCascade won't do the whole U in one go), as surfaces only,
    then sew the runs together along the section curves they share, cap the two ear tips and
    close it into one solid."""
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeSolid
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SHELL, TopAbs_FACE
    from OCP.TopoDS import TopoDS
    from OCP.ShapeFix import ShapeFix_Solid
    sew = BRepBuilderAPI_Sewing(1e-3)

    def run(a, b):                                       # loft a..b, halving it until it goes
        lb = BRepOffsetAPI_ThruSections(False, False, 1e-4)
        for w in wires[a:b + 1]:
            lb.AddWire(w.wrapped)
        try:
            lb.Build()
            shp = lb.Shape()
        except Exception:
            if b - a < 2:
                raise
            m = (a + b) // 2
            run(a, m)
            run(m, b)
            return
        print("  run", a, b)
        ex = TopExp_Explorer(shp, TopAbs_FACE)
        while ex.More():
            sew.Add(ex.Current())
            ex.Next()
    for a, b in zip(cuts_, cuts_[1:]):
        run(a, b)
    for w in (wires[0], wires[-1]):                     # flat caps on the ear tips
        sew.Add(BRepBuilderAPI_MakeFace(w.wrapped, True).Face())
    sew.Perform()
    ex = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
    shell = TopoDS.Shell(ex.Current()) if hasattr(TopoDS, "Shell") else TopoDS.Shell_s(ex.Current())
    ms = BRepBuilderAPI_MakeSolid(shell)
    fix = ShapeFix_Solid(ms.Solid())
    fix.Perform()
    sol = Solid(fix.Solid())
    if sol.volume < 0:
        sol = Solid(sol.wrapped.Reversed())
    return sol


def build(skip_loft=False):
    path, sides, (yth, ytf) = plan_path()
    n = len(path)
    tang = np.gradient(path, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    nrm = np.c_[tang[:, 1], -tang[:, 0]]
    # make the normal point outward (away from a point inside the bezel)
    inside = np.array([0.0, -60.0])
    flip = np.sum((path - inside) * nrm, axis=1) < 0
    nrm[flip] *= -1

    hood, fen = sides["hood"], sides["fender"]
    rim_h, rim_f = g.door_rim(P, "hood"), g.door_rim(P, "fender")
    F = g.front_frame(P)
    z_top, z_bu, z_wb, z_fb, _ = g.shell_levels(P)
    floor_top = z_wb - 0.15
    B_front = floor_top - T_WALL

    # where each station is: 0 on the straight front, 1 once past the corner onto the side
    def side_w(pt):
        x, y = pt
        s_ = hood if x < 0 else fen
        y0, yc = float(s_["p0"][1]), float(s_["arc_end_y"])
        if abs(x) < abs(float(s_["p0"][0])) - 25:
            return 0.0
        w = np.clip((y0 - y) / max(y0 - yc, 1.0), 0, 1)
        wx = np.clip((abs(x) - (abs(float(s_["p0"][0])) - 25)) / 25.0, 0, 1)
        return float(max(w, 0.35 * wx))

    rows = []
    for i in range(n):
        x, y = path[i]
        s_ = hood if x < 0 else fen
        rim = rim_h if x < 0 else rim_f
        y_t = yth if x < 0 else ytf
        w = side_w(path[i])
        ws = w * w * (3 - 2 * w)
        u = float(g.front_uv(P, x, y))
        lip = z_top + float(g.top_rise(P, u))               # the door's lip along the front
        T_front = lip - 1.3                                  # rail top; the bead's top meets the lip
        T_side = float(rim(y)) - 0.05                        # the door's edge along the sides
        T = (1 - ws) * T_front + ws * T_side
        # bottom: level along the front, then a straight line back to the ear's tip
        yc = float(s_["arc_end_y"])
        z_tip = float(rim(y_t)) - 0.05
        B_side = B_front + (z_tip - B_front) * np.clip((yc - y) / max(yc - y_t, 1.0), 0, 1)
        B = B_front if y >= yc else B_side
        # rail and floor narrow toward the corners until the section is just the flange
        U = abs(u)
        U_c = abs(float(g.front_uv(P, float(s_["p0"][0]), float(s_["p0"][1]))))
        f_ = np.clip((U_c - 10 - U) / 60.0, 0, 1)            # 1 across the middle, 0 by the corner
        f_ = f_ * f_ * (3 - 2 * f_)
        f_ = f_ * (1 - ws)
        Dr = 3.6 + (P.blade_depth - 3.6) * f_
        Df = 3.6 + (P.floor_depth - 3.6) * f_
        rb = 1.2 * (1 - ws)                              # the bead fades out round the corners
        R_lip = 1.0 + 3.5 * (1 - ws)
        if T - B < 8.0:                                     # at the very tip keep a little height
            B = T - 8.0
        rows.append((x, y, nrm[i], T, B, Dr, Df, rb, R_lip))

    # stations: every 4 mm, finer round the corners
    idx = [0]
    for i in range(1, n - 1):
        dw = abs(side_w(path[i]) - side_w(path[idx[-1]]))
        if i - idx[-1] >= 7 or (dw > 0.12 and i - idx[-1] >= 3):
            idx.append(i)
    idx.append(n - 1)

    wires = []
    for i in idx:
        x, y, nv, T, B, Dr, Df, rb, R_lip = rows[i]
        sec = section(T, B, Dr, Df, rb, R_lip)
        pts3 = [Vector(x + nv[0] * a, y + nv[1] * a, b) for a, b in sec]
        wires.append(Wire([Spline(pts3 + [pts3[0]], periodic=False)]) if False else Wire([Edge.make_spline(pts3, periodic=True)]))
    # OpenCascade won't loft all the sections in one go round the whole U; loft it in runs that
    # share their end sections and join them (the runs meet on the same section curve)
    # loft it in short runs, each a light smooth surface, and glue them into one solid along the
    # sections they share. OpenCascade's compatibility pass is off: it re-aligns the sections'
    # start points and twists the corners, and the sections already correspond point for point
    if skip_loft:
        return None, path, rows, sides, (yth, ytf)
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

    def loft_run(ws):
        lb = BRepOffsetAPI_ThruSections(True, False, 1e-4)
        lb.CheckCompatibility(False)
        for w in ws:
            lb.AddWire(w.wrapped)
        lb.Build()
        s_ = Solid(lb.Shape())
        return s_ if s_.volume > 0 else Solid(s_.wrapped.Reversed())
    step = RUN_LEN
    ends = list(range(0, len(wires) - 1, step)) + [len(wires) - 1]
    runs = [loft_run(wires[a:b + 1]) for a, b in zip(ends, ends[1:])]
    print("  runs", len(runs), [round(r.volume) for r in runs], flush=True)
    # sew the runs' curved faces together (their end caps inside the U are dropped) with a cap
    # on each ear tip, and close it into one solid
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopoDS import TopoDS
    from OCP.ShapeFix import ShapeFix_Shell, ShapeFix_Solid
    sew = BRepBuilderAPI_Sewing(1e-3)
    c0 = np.asarray(tuple(wires[0].center()))
    c1 = np.asarray(tuple(wires[-1].center()))
    for k, r_ in enumerate(runs):
        for f in r_.faces():
            if f.geom_type.name == "PLANE":
                fc = np.asarray(tuple(f.center()))
                keep = (k == 0 and np.linalg.norm(fc - c0) < 5) or (k == len(runs) - 1 and np.linalg.norm(fc - c1) < 5)
                if not keep:
                    continue
            sew.Add(f.wrapped)
    sew.Perform()
    ex = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
    sh = TopoDS.Shell(ex.Current()) if hasattr(TopoDS, "Shell") else TopoDS.Shell_s(ex.Current())
    fs = ShapeFix_Shell(sh)
    fs.Perform()
    so = ShapeFix_Solid(BRepBuilderAPI_MakeSolid(fs.Shell()).Solid())
    so.Perform()
    body = Solid(so.Solid())
    if body.volume < 0:
        body = Solid(body.wrapped.Reversed())
    print("  sewn: free edges", sew.NbFreeEdges(), "volume", round(body.volume), flush=True)
    return body, path, rows, sides, (yth, ytf)


def rounded_bar(x0, x1, y0, y1, z0, z1, r, axis):
    """A box whose four edges along `axis` are rounded by r."""
    b = Solid.make_box(x1 - x0, y1 - y0, z1 - z0, Plane((x0, y0, z0)))
    ax = {"x": Axis.X, "y": Axis.Y, "z": Axis.Z}[axis]
    return b.fillet(r, b.edges().filter_by(ax))


def features(body, sides, tips):
    """Windows, tongue, screw holes and flange pockets, then the fillets."""
    zc = g.pod_zc(P)
    ww, wh = P.pod_face_w + 2 * P.window_clear_x, P.pod_face_h + 2 * P.window_clear_y
    wins = []
    for (px, py, _) in g.pod_poses(P):
        # through the front wall, straight ahead of the pod, centred on its lenses
        wins.append(rounded_bar(px - ww / 2, px + ww / 2, py - 0.5, py + 80.0, zc - wh / 2, zc + wh / 2, WIN_R, "y"))

    # the clip tongue: a thin tapered plate off the back of the rail, top level with the door's lip
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
    plan = [xy(ul, tb[0]), xy(ur, tb[1]), xy(ur, n_n), xy(P.clip_u + rw, n_r), xy(P.clip_u - rw, n_r), xy(ul, n_n)]
    tongue = extrude(make_face(Polyline(*[(float(a), float(b), lip_c - T_WALL) for a, b in plan], close=True)), T_WALL)
    tongue = tongue.fillet(1.0, tongue.edges().filter_by(Axis.Z))
    slot = rounded_bar(-P.tongue_slot_w / 2, P.tongue_slot_w / 2, 0, 1, 0, 1, 0.0 + 1e-3, "z") if False else None
    # slot along the middle and the groove the clip's bar drops into
    su0, su1 = P.clip_u - P.tongue_slot_w / 2, P.clip_u + P.tongue_slot_w / 2
    slot = extrude(make_face(Polyline(*[(float(a), float(b), lip_c - T_WALL - 1) for a, b in
                                        (xy(su0, n_n - 2), xy(su1, n_n - 2), xy(su1, n_r - 4), xy(su0, n_r - 4))], close=True)), T_WALL + 2)
    gr = [xy(ul - 1, g1[0] - P.clip_skew), xy(ur + 1, g1[1] + P.clip_skew), xy(ur + 1, g0[1] + P.clip_skew), xy(ul - 1, g0[0] - P.clip_skew)]
    groove = extrude(make_face(Polyline(*[(float(a), float(b), lip_c - P.groove_depth) for a, b in gr], close=True)), P.groove_depth + 2)
    tongue = tongue - slot - groove
    body = body.fuse(tongue).clean()
    print("  tongue", round(body.volume), flush=True)

    # screw holes on every hole in the door's flange, and pockets clear of the flange
    cutters = list(wins)
    for name in ("hood", "fender"):
        s_ = sides[name]
        sx = s_["sx"]
        for h in s_["holes"]:
            at, nrm = np.asarray(h["at"], float), np.asarray(h["normal"], float)
            o = at - 30 * nrm
            cutters.append(Solid.make_cylinder(P.ear_hole_d / 2, 60, Plane(tuple(o), z_dir=tuple(nrm))))
        fl = g.door_flange(P, name)
        if fl is None:
            continue
        fx, fy0, fz0, FX = fl
        sxf = s_["side_x"]
        rim = g.door_rim(P, name)
        y_t = tips[0] if sx < 0 else tips[1]
        seg, cur = [], []
        for y in np.arange(y_t - 5.0, s_["arc_end_y"] - 1.0, 1.0):
            col = np.nan_to_num(FX[int(round(y - fy0))], nan=0.0)
            hit = np.flatnonzero(col > float(sxf(y)) - 12.0)
            if len(hit):
                cur.append((y, fz0 + hit.min(), float(col.max())))
            elif cur:
                seg.append(cur)
                cur = []
        if cur:
            seg.append(cur)
        for sg in seg:
            ys = [a for a, _, _ in sg]
            ya, yb = min(ys) - 1.5, max(ys) + 1.5
            za = min(z for _, z, _ in sg) - 1.5
            zb = max(float(rim(y)) for y in ys) + 2.0
            yy = np.linspace(ya, yb, 20)
            reach = min(max(r_ for _, _, r_ in sg) + P.ear_gap, float(np.min(sxf(yy))) - P.min_wall)
            inner = float(np.min(sxf(yy))) - 16.0
            if sx > 0:
                cutters.append(rounded_bar(inner, reach, ya, yb, za, zb, 1.0, "x"))
            else:
                cutters.append(rounded_bar(-reach, -inner, ya, yb, za, zb, 1.0, "x"))
    print("  cutting", len(cutters), flush=True)
    body = body.cut(*cutters).clean()
    print("  cut", round(body.volume), flush=True)
    # fillets: the window openings' edges, then whatever else will take it
    for (px, py, _) in g.pod_poses(P):
        box_ = (px - ww / 2 - 2, px + ww / 2 + 2, zc - wh / 2 - 2, zc + wh / 2 + 2)
        es = [e for e in body.edges() if box_[0] < e.center().X < box_[1] and box_[2] < e.center().Z < box_[3]
              and e.center().Y > py - 1.0]
        for r_ in (1.5, 1.0, 0.6):
            try:
                body = body.fillet(r_, es)
                print("window fillet", r_)
                break
            except Exception:
                continue
    return body


WIN_R = 12.0
RUN_LEN = 8


if __name__ == "__main__":
    import time
    from build123d import export_brep, import_brep
    t0 = time.time()
    cache = os.path.join("/tmp/claude-0", "bezel_loft.brep")
    body, path, rows, sides, tips = build(skip_loft=os.path.exists(cache))
    if os.path.exists(cache):
        body = import_brep(cache)
    else:
        export_brep(body, cache)
    print("loft", round(time.time() - t0, 1), "s, volume", round(body.volume, 1), flush=True)
    body = features(body, sides, tips)
    print("features", round(time.time() - t0, 1), "s, valid", body.is_valid, "volume", round(body.volume, 1), flush=True)
    os.makedirs(os.path.join(HERE, "stl", "cad"), exist_ok=True)
    export_stl(body, os.path.join(HERE, "stl", "cad", "bezel_cad_passenger.stl"), tolerance=0.05, angular_tolerance=0.1)
    print("exported", round(time.time() - t0, 1), "s", flush=True)
