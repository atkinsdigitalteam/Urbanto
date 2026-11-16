"""C11 worked examples: corner geometry and a DMRB CD 116 roundabout check.

Run:  python3 -I geometry_checks.py            (writes PNGs next to this file)

Part A  Corner of an Abu Dhabi USDM "Avenue" (City context) and "Street".
        For several kerb (corner) radii it measures, with shapely:
          * the kerb return arc length and the footway area given up,
          * the pedestrian crossing length on the footway desire line,
          * the set-back needed to keep the crossing at kerb-to-kerb width,
          * the effective turning radius (largest inner-edge turning circle that is
            tangent to the inner edges of the approach and receiving traffic lanes
            and does not cut the kerb return),
          * whether AASHTO design vehicles (min inside / outside turning radii
            quoted from TxDOT Roadway Design Manual Table 4-1) fit without
            encroaching into the opposing lane of the receiving street.
Part B  Compact roundabout checked against DMRB CD 116 v2.1.0 clauses 3.5 to 3.26,
        including an entry path radius measured on a constructed fastest path
        (2 m wide path => centreline 1 m from kerbs, islands and centre line,
        start 50 m before the give way line, best-fit circle over 25 m).
        The same checks are then run on a 20 m ICD one-lane roundabout of the size
        the Abu Dhabi USDM Table 5.10 allows.
Part C  Median U-turn: receiving width needed beyond the median edge for a 180-degree
        turn around a median nose, per vehicle and median width (steady-state annulus).

All dimensions in metres. Frames: Part A uses right-hand traffic (UAE).
Part B is drawn in the UK left-hand frame of CD 116; the geometry is mirror-symmetric,
so radii are the same for a right-hand-traffic (anticlockwise) roundabout.
"""
from __future__ import annotations

import math
import os

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
FT = 0.3048

# ----------------------------------------------------------------------------------
# Part A: corner geometry
# ----------------------------------------------------------------------------------
# Avenue, City context, USDM Table 5.2 (minimums): cycle lane 1.5, curb lane 3.3,
# travel lane 3.3, centre median 2.0 (USDM note 2: min 2 m refuge).
AV_CYCLE, AV_CURB, AV_LANE, AV_MEDIAN = 1.5, 3.3, 3.3, 2.0
AV_HALF = AV_CYCLE + AV_CURB + AV_LANE            # kerb to median edge, one direction
AV_W = 2 * AV_HALF + AV_MEDIAN                     # kerb to kerb
# Street, City context: parking 2.7, curb lane 3.0, no median. USDM 5.9.7: kerb
# extensions are 0.5 m narrower than the parking lane -> 2.2 m extension at corners.
ST_PARK, ST_CURB = 2.7, 3.0
ST_EXT = ST_PARK - 0.5
ST_W_CORNER = 2 * (ST_PARK + ST_CURB) - 2 * ST_EXT  # kerb to kerb at the extensions
# Footway on the Avenue (City, minimums): edge 0.2, furnishing 1.0, through 2.4,
# frontage 0.5. Desire line = centre of the through zone.
FW_EDGE, FW_FURN, FW_THRU = 0.2, 1.0, 2.4
DESIRE = FW_EDGE + FW_FURN + FW_THRU / 2

# AASHTO design vehicles (TxDOT RDM Table 4-1, ft): min design turning radius (outer
# front corner), min inside radius (inner rear wheel).
VEHICLES = {
    "P (car)": (23.8 * FT, 14.4 * FT),
    "CITY-BUS": (41.6 * FT, 24.5 * FT),
    "SU-30": (41.8 * FT, 28.4 * FT),
    "WB-40": (39.9 * FT, 19.3 * FT),
}


def footway_corner(R: float, size: float = 60.0) -> Polygon:
    """South-west footway block with its corner at (0, 0) rounded to radius R."""
    blk = box(-size, -size, 0.0, 0.0)
    if R <= 0:
        return blk
    return blk.buffer(-R, join_style="round").buffer(R, join_style="round")


def effective_radius(R: float, a: float, b: float) -> float:
    """Largest inner-edge turning radius Re for a right turn (RHT) from a road whose
    kerb is y=0 into a road whose kerb is x=0, when the vehicle's inner edge must stay
    on the lane edges y>=a (approach) and x>=b (receiving) and outside the kerb return.
    Circle centre (b-Re, a-Re). Solved by bisection on a shapely test."""
    fw_interior = footway_corner(R).buffer(-1e-6)

    def ok(re: float) -> bool:
        # inner-edge arc of the turn, from the approach tangent point to the receiving one
        cx, cy = b - re, a - re
        t = np.linspace(math.pi / 2, 0.0, 721)
        arc = LineString(np.c_[cx + re * np.cos(t), cy + re * np.sin(t)])
        return not arc.intersects(fw_interior)

    lo, hi = 0.0, 200.0
    if not ok(1e-3):
        return 0.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def effective_radius_closed_form(R: float, a: float, b: float) -> float:
    """Same quantity in closed form: dist(centres) + R <= Re, centres (b-Re,a-Re), (-R,-R)."""
    # solve sqrt((b+R-Re)^2 + (a+R-Re)^2) + R = Re for Re > max(a,b)+R
    # feasible (inner disk contains the kerb-return disk) while f <= 0; f grows with Re
    f = lambda re: math.hypot(b + R - re, a + R - re) + R - re
    lo, hi = max(a, b) + R, 500.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) <= 0:
            lo = mid
        else:
            hi = mid
    return lo


def crossing_length(R: float, y_line: float) -> float:
    """Length of a crossing of the Street along y = y_line (footway desire line) between
    the two kerb returns (corner at x=0 and mirrored corner at x=ST_W_CORNER)."""
    left = footway_corner(R)
    right = footway_corner(R)
    # mirror right block about x = ST_W_CORNER/2
    from shapely import affinity
    right = affinity.scale(right, xfact=-1, yfact=1, origin=(ST_W_CORNER / 2, 0))
    line = LineString([(-50, y_line), (ST_W_CORNER + 50, y_line)])
    gap = line.difference(unary_union([left, right]))
    # keep the segment that spans the carriageway
    segs = [g for g in getattr(gap, "geoms", [gap]) if g.bounds[0] > -50 and g.bounds[2] < ST_W_CORNER + 50]
    return max((s.length for s in segs), default=0.0)


def part_a(lines: list[str]) -> list[dict]:
    a = AV_CYCLE                      # approach: inner edge of Avenue curb lane
    b = ST_PARK - ST_EXT              # receiving: 0.5 m from extension kerb to travel lane
    lines.append("PART A  Corner: USDM Avenue (City) x Street (City), right turn, RHT")
    lines.append(f"  Avenue kerb-to-kerb {AV_W:.1f} m (2 x [{AV_CYCLE}+{AV_CURB}+{AV_LANE}] + median {AV_MEDIAN})")
    lines.append(f"  Street kerb-to-kerb at kerb extensions {ST_W_CORNER:.1f} m; offsets a={a:.1f} m, b={b:.1f} m")
    lines.append(f"  Footway desire line {DESIRE:.1f} m behind the Avenue kerb")
    lines.append("")
    hdr = (f"  {'R kerb':>6} {'arc':>6} {'area':>6} {'cross':>6} {'setback':>7} {'Re':>6} {'Re(cf)':>6}  "
           + "  ".join(f"{k:>11}" for k in VEHICLES))
    lines.append(hdr)
    rows = []
    for R in (0.5, 2.0, 5.0, 10.0, 15.0):
        fw0 = footway_corner(0.0).intersection(box(-30, -30, 0, 0))
        fwR = footway_corner(R).intersection(box(-30, -30, 0, 0))
        area = fw0.area - fwR.area                     # footway given to carriageway
        arc = math.pi * R / 2                          # 90 deg kerb return
        # measured arc: boundary length change (two straights of R replaced by arc)
        arc_meas = fwR.exterior.length - (fw0.exterior.length - 2 * R)
        cross = crossing_length(R, -DESIRE)
        setback = max(0.0, R - DESIRE)                 # move crossing to y=-R to keep kerb-to-kerb
        re = effective_radius(R, a, b)
        re_cf = effective_radius_closed_form(R, a, b)
        fits = {}
        for name, (r_out, r_in) in VEHICLES.items():
            kerb_ok = re >= r_in
            swept = r_out - r_in
            enc_design = max(0.0, swept - ST_CURB)       # into the opposing lane of the Street
            enc_control = max(0.0, swept - 2 * ST_CURB)  # beyond both Street lanes
            if not kerb_ok:
                fits[name] = "kerb"
            elif enc_design <= 1e-9:
                fits[name] = "OK"
            elif enc_control <= 1e-9:
                fits[name] = f"+{enc_design:.2f}/ok"
            else:
                fits[name] = f"+{enc_design:.2f}/+{enc_control:.2f}"
        rows.append(dict(R=R, arc=arc, arc_meas=arc_meas, area=area, cross=cross, setback=setback,
                         re=re, re_cf=re_cf, fits=fits))
        lines.append(f"  {R:6.1f} {arc_meas:6.2f} {area:6.2f} {cross:6.2f} {setback:7.2f} {re:6.2f} {re_cf:6.2f}  "
                     + "  ".join(f"{fits[k]:>11}" for k in VEHICLES))
    lines.append("  arc = kerb return length (m, measured); area = footway lost (m2); cross = crossing length")
    lines.append("  on the desire line (m); setback = distance to move the crossing so it stays kerb-to-kerb;")
    lines.append("  Re = effective inner turning radius (m; shapely bisection / closed form).")
    lines.append("  Vehicle: OK = inner edge clears the kerb and the steady-state swept width fits the 3.0 m")
    lines.append("  receiving lane; 'kerb' = inner edge would cut the kerb; '+x/ok' = x m into the opposing lane")
    lines.append("  but inside both Street lanes (acceptable only for a control vehicle); '+x/+y' = beyond both.")
    lines.append("")
    for name, (r_out, r_in) in VEHICLES.items():
        lines.append(f"  {name:9}: outer {r_out:5.2f} m, inner {r_in:5.2f} m, steady-state swept width {r_out - r_in:4.2f} m")
    lines.append("")
    # Avenue crossing: two stages with a 2.0 m refuge
    lines.append(f"  Crossing the Avenue: single stage {AV_W:.1f} m; with refuge two stages of {AV_HALF:.1f} m"
                 f" (USDM max crossing distance 13 m)")
    lines.append("")
    return rows


# ----------------------------------------------------------------------------------
# Part B: roundabout
# ----------------------------------------------------------------------------------
CD116_T38 = [  # central island diameter, R1, R2, min ICD (CD 116 Table 3.8)
    (4.0, 3.0, 13.0, 28.0), (6.0, 4.0, 13.4, 28.8), (8.0, 5.0, 13.9, 29.8), (10.0, 6.0, 14.4, 30.8),
    (12.0, 7.0, 15.0, 32.0), (14.0, 8.0, 15.6, 33.2), (16.0, 9.0, 16.3, 34.6), (18.0, 10.0, 17.0, 36.0)]


def t38_min_icd(island_d: float) -> float:
    xs = [r[0] for r in CD116_T38]
    ys = [r[3] for r in CD116_T38]
    if island_d < xs[0]:
        return ys[0]
    if island_d > xs[-1]:
        return float("nan")
    return float(np.interp(island_d, xs, ys))


class Roundabout:
    def __init__(self, name, icd, island_d, entry_w, circ_w, approach_half=3.65, splitter_w=3.0,
                 splitter_len=20.0, kerb_r=15.0, flare_len=25.0, compact=True, urban_40mph=True):
        self.__dict__.update(locals())
        del self.__dict__["self"]
        self.r_out = icd / 2
        self.r_in = self.r_out - circ_w            # overrun / central island perimeter
        self.build()

    def build(self):
        ro = self.r_out
        e, v, s = self.entry_w, self.approach_half, self.splitter_w
        arms = []
        for ang in (0, 90, 180, 270):
            # south arm in local frame; LHT: entry on the west (x<0), exit on the east (x>0)
            y_far = -(ro + 120)
            y_flare0 = -(ro + self.flare_len)
            pts_w = [(-(s / 2 + e), 0.0), (-(s / 2 + e), -(ro + 2)), (-v, y_flare0), (-v, y_far)]
            pts_e = [(v, y_far), (v, y_flare0), (s / 2 + e, -(ro + 2)), (s / 2 + e, 0.0)]
            arm = Polygon(pts_w + pts_e)
            arms.append(self._rot(arm, ang))
        cw = unary_union([Point(0, 0).buffer(ro, 512)] + arms)
        # kerb radii where the arm kerbs meet the ICD circle (rounds concave corners)
        self.carriageway = cw.buffer(self.kerb_r, 256, join_style="round").buffer(-self.kerb_r, 256, join_style="round")
        self.carriageway = self.carriageway.intersection(Point(0, 0).buffer(ro + 110))
        obst = [Point(0, 0).buffer(self.r_in, 512)]
        for ang in (0, 90, 180, 270):
            spl = Polygon([(-s / 2, -(ro + 0.5)), (0.0, -(ro + self.splitter_len)), (s / 2, -(ro + 0.5))])
            cl = LineString([(0.0, -(ro + self.splitter_len)), (0.0, -(ro + 110))])  # centre line
            obst.append(self._rot(spl, ang))
            obst.append(self._rot(cl, ang).buffer(0.01))
        self.obstacles = unary_union(obst)
        self.free = self.carriageway.buffer(-1.0).difference(self.obstacles.buffer(1.0))

    @staticmethod
    def _rot(g, ang):
        from shapely import affinity
        return affinity.rotate(g, ang, origin=(0, 0))

    # ---- fastest through path (south arm to north arm) -----------------------------
    def fastest_path(self):
        ro = self.r_out
        Y0 = ro + 50.0                                   # 50 m before the give way line
        knots = np.array([0.0, 0.4 * ro, 0.8 * ro, ro, ro + 6, ro + 14, ro + 24, ro + 36, Y0, Y0 + 15])
        x_start = -1.02                                  # 1 m (+2 cm tolerance) from the centre line

        def make(xk):
            xs = np.concatenate([xk, [x_start, x_start]])
            yy = np.concatenate([-knots[::-1], knots[1:]])
            xx = np.concatenate([xs[::-1], xs[1:]])
            return CubicSpline(yy, xx, bc_type="clamped")

        ys = np.linspace(-Y0, Y0, 1201)

        def curv(sp):
            d1, d2 = sp(ys, 1), sp(ys, 2)
            return d2 / (1 + d1 ** 2) ** 1.5, np.sqrt(1 + d1 ** 2)

        def energy(xk):
            sp = make(xk)
            k, ds = curv(sp)
            return float(np.sum(k ** 2 * ds) * (ys[1] - ys[0]))

        free = self.free
        bnd = free.boundary

        import shapely
        shapely.prepare(free)
        yc = ys[::4]

        def clearance(xk):
            xc = make(xk)(yc)
            d = shapely.distance(bnd, shapely.points(xc, yc))
            inside = shapely.contains_xy(free, xc, yc)
            return np.where(inside, d, -d)

        # initial guess: pass west of the island at r_in + 1.5
        x0 = np.array([-(self.r_in + 1.5), -(self.r_in + 1.2), -0.5 * (self.r_in + ro), -(self.s_w() - 1.5),
                       -(self.s_w() - 2.0), -3.0, -2.0, -1.5])
        res = minimize(energy, x0, method="SLSQP",
                       constraints=[{"type": "ineq", "fun": clearance}],
                       options={"maxiter": 400, "ftol": 1e-9})
        sp = make(res.x)
        xs = sp(ys)
        self.min_clear = float(min(clearance(res.x))) + 1.0   # +1: free region is already offset by 1 m
        return ys, xs, res

    def s_w(self):
        return self.splitter_w / 2 + self.entry_w

    @staticmethod
    def best_fit_radius(px, py):
        """Kasa least-squares circle fit."""
        A = np.c_[2 * px, 2 * py, np.ones_like(px)]
        bb = px ** 2 + py ** 2
        cx, cy, c = np.linalg.lstsq(A, bb, rcond=None)[0]
        return math.sqrt(c + cx ** 2 + cy ** 2)

    @staticmethod
    def three_point_radius(p1, p2, p3):
        a = math.dist(p1, p2); b = math.dist(p2, p3); c = math.dist(p1, p3)
        area2 = abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1]))
        return float("inf") if area2 < 1e-9 else a * b * c / (2 * area2)

    def entry_path_radius(self, ys, xs, window=25.0):
        """Entry path radius per CD 116 3.20 Note 1 / A1.2: smallest radius of a circular
        curve fitted over 25 m of path in the entry (left-hand) curve, windows between
        50 m before and 10 m after the give way line. Three estimators are returned:
        least-squares circle (Kasa) on windows lying wholly in the left-hand curve,
        the equivalent-arc radius 25 m / heading change, and the 3-point radius
        (start, middle, end) that Civil 3D's fastest-path tool uses."""
        ro = self.r_out
        d1 = np.gradient(xs, ys); d2 = np.gradient(d1, ys)
        head = np.arctan2(1.0, d1)                    # heading of a path parametrised by y
        s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(xs), np.diff(ys)))])
        out = dict(ls=float("inf"), arc=float("inf"), p3=float("inf"), at=None, circ=float("inf"))
        for m in range(len(ys)):
            i = np.searchsorted(s, s[m] - window / 2); j = np.searchsorted(s, s[m] + window / 2)
            if i <= 0 or j >= len(ys) - 1:
                continue
            r_arc = (s[j] - s[i]) / max(abs(head[j] - head[i]), 1e-12)
            if -(ro + 50) <= ys[m] <= -(ro - 10) and d2[m] < 0:      # entry, left-hand curve
                if r_arc < out["arc"]:
                    out["arc"], out["at"] = r_arc, ys[m]
                    out["p3"] = self.three_point_radius((xs[i], ys[i]), (xs[m], ys[m]), (xs[j], ys[j]))
                if (d2[i:j] < 0).all():
                    out["ls"] = min(out["ls"], self.best_fit_radius(xs[i:j], ys[i:j]))
            if abs(ys[m]) <= 2 and d2[m] > 0:                          # around the central island
                out["circ"] = min(out["circ"], r_arc)
        return out

    def check(self, lines):
        L = lines.append
        L(f"PART B  {self.name}")
        L(f"  ICD {self.icd} m, central island {self.island_d} m, entry width e {self.entry_w} m, "
          f"circulatory width {self.circ_w} m, overrun ring {self.r_in - self.island_d / 2:.2f} m, kerb radius {self.kerb_r} m")
        res = []

        def chk(cl, ok, txt):
            res.append(ok)
            L(f"  [{'PASS' if ok else 'FAIL'}] CD 116 {cl}: {txt}")

        chk("3.5", self.icd >= 28.0, f"ICD {self.icd} >= 28 m")
        if self.compact:
            chk("3.5.1", self.icd <= 36.0, f"compact ICD {self.icd} <= 36 m")
        chk("3.7", self.island_d >= 4.0, f"central island {self.island_d} >= 4 m")
        m = t38_min_icd(self.island_d)
        chk("3.8/T3.8", self.icd >= m, f"ICD {self.icd} >= Table 3.8 minimum {m:.1f} m for a {self.island_d} m island")
        ratio = self.circ_w / self.entry_w
        chk("3.6", 1.0 - 1e-9 <= ratio <= 1.2 + 1e-9, f"circulatory/entry = {ratio:.2f} (1.0 to 1.2)")
        if self.compact:
            chk("3.6.7", self.circ_w <= 6.0, f"compact circulatory width {self.circ_w} <= 6 m")
        else:
            chk("3.6.5", self.circ_w <= 15.0, f"normal circulatory width {self.circ_w} <= 15 m")
        chk("3.14", 3.0 <= self.entry_w <= 4.5, f"single-lane entry width {self.entry_w} within 3.0 to 4.5 m")
        chk("3.19.1/.2", 10.0 <= self.kerb_r <= 100.0, f"entry kerb radius {self.kerb_r} within 10 to 100 m")
        ys, xs, opt = self.fastest_path()
        r = self.entry_path_radius(ys, xs)
        lim = 70.0 if (self.compact and self.urban_40mph) else 100.0
        clause = "3.24" if (self.compact and self.urban_40mph) else ("3.25" if self.compact else "3.26")
        chk(clause, r["arc"] <= lim, f"entry path radius {r['arc']:.1f} m (25 m equivalent arc; 3-point {r['p3']:.1f} m;"
            f" least-squares on wholly-left windows {r['ls']:.1f} m) <= {lim:.0f} m")
        at, r_circ = r["at"], r["circ"]
        L(f"  fastest path: optimiser success={opt.success}, min centreline clearance {self.min_clear:.2f} m"
          f" (target 1.0); smallest entry radius centred {(-self.r_out - at):.1f} m before the ICD;"
          f" radius around the island ~{r_circ:.1f} m")
        # US comparison: FHWA-RD-00-067 Exhibit 6-13 (single-lane): ICD -> max R1 (m), and the
        # R1 radius/speed pairs printed there (e = +0.02), used here only to interpolate.
        icd_r1 = [(30, 54), (35, 61), (40, 69), (45, 73)]
        r1_speed = [(54, 41), (61, 43), (65, 44), (69, 45), (73, 46), (78, 47), (83, 48), (88, 49), (93, 50)]
        if self.icd >= icd_r1[0][0]:
            r1max = float(np.interp(self.icd, *zip(*icd_r1)))
            v = float(np.interp(r["arc"], *zip(*r1_speed)))
            L(f"  [info] FHWA 2000 Exhibit 6-13: max R1 at ICD {self.icd:.0f} m ~ {r1max:.0f} m; measured "
              f"{r['arc']:.0f} m -> ~{v:.0f} km/h (FHWA Exhibit 6-4 urban single-lane max entry speed 35 km/h)")
        else:
            L(f"  [info] FHWA 2000 Exhibit 6-13 starts at ICD 30 m; Exhibit 6-19 urban compact range is 25 to 30 m")
        L("")
        self.path = (xs, ys)
        return all(res)


def draw(rb: Roundabout, fname: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(5, 6), dpi=90)
    for g in getattr(rb.carriageway, "geoms", [rb.carriageway]):
        ax.fill(*g.exterior.xy, color="#d9d9d9", lw=0)
    for g in getattr(rb.obstacles, "geoms", [rb.obstacles]):
        if g.geom_type == "Polygon":
            ax.fill(*g.exterior.xy, color="#8fbf8f", lw=0)
    ax.add_patch(plt.Circle((0, 0), rb.island_d / 2, color="#4f8f4f"))
    xs, ys = rb.path
    ax.plot(xs, ys, color="#c0392b", lw=1.5, label="fastest through path (centreline)")
    ax.set_xlim(-45, 45); ax.set_ylim(-rb.r_out - 52, rb.r_out + 52)
    ax.set_aspect("equal"); ax.set_title(rb.name, fontsize=9); ax.legend(fontsize=7, loc="upper right")
    ax.tick_params(labelsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, fname)); plt.close(fig)


def part_c(lines: list[str]) -> None:
    """Median U-turn (GCC practice): steady-state check of a 180-degree turn around a median
    nose of width M, turn centre on the median centre line. The inner edge must clear the
    nose (r_in >= M/2); the outer edge must stay inside the receiving carriageway, so the
    receiving width needed from the median edge is max(M/2, r_in) + swept - M/2."""
    recv = 2 * AV_LANE                    # USDM Avenue: two 3.3 m lanes (cycle lane not used)
    lines.append("PART C  Median U-turn on a USDM Avenue (receiving lanes 2 x 3.3 = 6.6 m, cycle lane excluded)")
    lines.append(f"  {'median M':>9} " + "  ".join(f"{k:>10}" for k in VEHICLES))
    for M in (2.0, 5.0, 6.0, 8.0, 12.0):
        cells = []
        for name, (r_out, r_in) in VEHICLES.items():
            need = max(M / 2, r_in) + (r_out - r_in) - M / 2
            cells.append(f"{need:5.2f} {'ok' if need <= recv else 'X '}")
        lines.append(f"  {M:9.1f} " + "  ".join(f"{c:>10}" for c in cells))
    lines.append("  value = receiving width needed beyond the median edge (m); X = needs a loon or a wider median")
    lines.append("")


def main():
    lines: list[str] = []
    part_a(lines)
    part_c(lines)
    rb1 = Roundabout("Compact roundabout to CD 116 (ICD 32 m)", icd=32.0, island_d=12.0, entry_w=4.5,
                     circ_w=5.4, kerb_r=15.0)
    rb1.check(lines)
    draw(rb1, "roundabout_cd116_compact.png")
    rb2 = Roundabout("USDM-size one-lane roundabout (ICD 20 m)", icd=20.0, island_d=10.0, entry_w=4.5,
                     circ_w=5.0, kerb_r=10.0)
    rb2.check(lines)
    draw(rb2, "roundabout_usdm_20m.png")
    out = "\n".join(lines)
    print(out)
    with open(os.path.join(HERE, "geometry_checks_output.txt"), "w", encoding="utf-8") as f:
        f.write(out + "\n")


if __name__ == "__main__":
    main()
