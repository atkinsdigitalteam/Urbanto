"""C10 parcel subdivision benchmark: OBB recursive split vs straight-skeleton strips.

Measures plot count, area statistics, street frontage, slivers and arc-discretisation
effects on synthetic test blocks. Units are metres and square metres.

Requirements: Python 3.12+, shapely >= 2.1, numpy, matplotlib, and (for the skeleton
method) compas_cgal 0.10 (CGAL straight skeleton bindings, LGPL-3.0):
    pip install --target ./pylib --no-deps compas_cgal "compas>=2.15,<3"
    PYTHONPATH=./pylib python3 parcel_bench.py <out_dir>

The OBB method follows Algorithm 2 of Vanegas et al. 2012 and the CityEngine
"Recursive" parameters (lotAreaMax, lotWidthMin, irregularity, forceStreetAccess).
The skeleton method is a simplified version of their Algorithm 1 (skeleton faces ->
strips merged per logical street -> diagonal-edge fix -> ray slicing -> merge of small
or triangular lots). Simplifications are listed in the report (C10, "Measured failure cases").
"""
import json
import math
import random
import sys
import time

import numpy as np
import shapely
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.ops import split, unary_union

try:
    from compas_cgal.straight_skeleton_2 import interior_straight_skeleton
    HAVE_SKELETON = True
except Exception:  # pragma: no cover
    HAVE_SKELETON = False

# ---------------------------------------------------------------- parameters
A_MIN = 450.0      # lotAreaMin (m2)
A_MAX = 900.0      # lotAreaMax (m2): OBB splits while area > A_MAX
W_MIN = 15.0       # lotWidthMin (m): reject a split if a child's OBB short side < W_MIN
SKEL_FRONT = 20.0  # skeleton target street frontage per lot (m)
ACCESS_MIN = 1.0   # a lot "has street access" if it shares >= 1 m with the block boundary
SLIVER_ASPECT = 4.0          # sliver if OBB long/short > 4 ...
SLIVER_INSCRIBED = 0.5 * W_MIN  # ... or inscribed-circle diameter < 7.5 m


# ---------------------------------------------------------------- test blocks
def arc_points(r, a0, a1, step_deg):
    """Points on a circular arc centred at the origin from angle a0 to a1 (degrees)."""
    n = max(1, math.ceil(abs(a1 - a0) / step_deg - 1e-9))
    return [(r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def block_rect():
    v = [(0, 0), (240, 0), (240, 80), (0, 80)]
    return v, [0, 1, 2, 3]


def block_L():
    v = [(0, 0), (200, 0), (200, 80), (80, 80), (80, 200), (0, 200)]
    return v, list(range(6))


def block_U():
    v = [(0, 0), (240, 0), (240, 200), (160, 200), (160, 80), (80, 80), (80, 200), (0, 200)]
    return v, list(range(8))


def block_arc(step_deg, merge_arc=True):
    """Annular sector: inner radius 220 m, outer 300 m, 60 degrees. Both long sides are arcs.
    merge_arc=True labels every chord of an arc with one street id (one logical street);
    False gives each chord its own id (what you get if the arc is exported as a polyline
    and nothing remembers it was one curve)."""
    outer = arc_points(300, 0, 60, step_deg)
    inner = arc_points(220, 60, 0, step_deg)
    v = [(220.0, 0.0)] + outer + inner[:-1]
    # edges: (220,0)->(300,0) radial; outer chords; outer end -> inner start radial; inner chords
    streets = [0]
    nid = 1
    for _ in range(len(outer) - 1):
        streets.append(1 if merge_arc else nid)
        nid += 1
    streets.append(1000)
    for _ in range(len(inner) - 1):
        streets.append(2000 if merge_arc else 2000 + nid)
        nid += 1
    assert len(streets) == len(v)
    return v, streets


def block_thin():
    v = [(0, 0), (160, -6), (330, 4), (430, 40), (320, 38), (170, 40), (40, 30)]
    return v, list(range(7))


# ---------------------------------------------------------------- helpers
def obb_info(poly):
    r = shapely.oriented_envelope(poly)
    c = np.array(r.exterior.coords[:4])
    e0, e1 = c[1] - c[0], c[2] - c[1]
    l0, l1 = np.linalg.norm(e0), np.linalg.norm(e1)
    center = c.mean(axis=0)
    if l0 >= l1:
        return center, e0 / max(l0, 1e-12), l0, l1
    return center, e1 / max(l1, 1e-12), l1, l0


def frontage(p, ring_buf):
    return p.exterior.intersection(ring_buf).length


def as_polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [x for x in getattr(g, "geoms", []) if isinstance(x, Polygon) and x.area > 1e-6]


# ---------------------------------------------------------------- OBB recursive split
def subdivide_obb(block, xi=1.0, omega=0.0, seed=0):
    rng = random.Random(seed)
    ring_buf = block.exterior.buffer(0.01)
    out = []

    def try_split(poly, along_long):
        center, ld, L, S = obb_info(poly)
        perp = np.array([-ld[1], ld[0]])
        shift = (rng.uniform(-1, 1) * omega * 0.25) * (L if not along_long else S)
        if not along_long:      # cut perpendicular to the long axis (default, Vanegas Alg. 2)
            p = center + ld * shift
            d = perp
        else:                   # rotated 90 degrees
            p = center + perp * shift
            d = ld
        big = 4 * (L + S)
        line = LineString([tuple(p - d * big), tuple(p + d * big)])
        pieces = as_polys(split(poly, line))
        if len(pieces) < 2:
            return None
        if any(obb_info(q)[3] < W_MIN for q in pieces):  # CityEngine lotWidthMin rule
            return None
        return pieces

    def rec(poly):
        if poly.area <= A_MAX:
            out.append(poly)
            return
        first = try_split(poly, False)
        chosen = first
        if first is not None and any(frontage(q, ring_buf) < ACCESS_MIN for q in first) \
                and rng.random() < xi:
            second = try_split(poly, True)
            if second is not None:
                chosen = second
        if chosen is None:
            chosen = try_split(poly, True)
        if chosen is None:
            out.append(poly)  # cannot split without breaking lotWidthMin: lot stays > A_MAX
            return
        for q in chosen:
            rec(q)

    rec(block)
    return out


# ---------------------------------------------------------------- skeleton subdivision
def skeleton_faces(verts):
    pts = [(x, y, 0.0) for x, y in verts]
    P, idx, E, _T = interior_straight_skeleton(pts, as_graph=False)
    id2pt = {int(i): (float(P[k][0]), float(P[k][1])) for k, i in enumerate(idx)}
    lines = [LineString([id2pt[int(a)], id2pt[int(b)]]) for a, b in E]
    noded = unary_union(lines)  # CGAL edges can meet mid-edge; node them or faces go missing
    faces = as_polys(shapely.polygonize(list(getattr(noded, "geoms", [noded]))))
    n = len(verts)
    edge_face = {}
    for i in range(n):
        a, b = verts[i], verts[(i + 1) % n]
        mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        cands = [f for f in faces if f.exterior.distance(mid) < 1e-6]
        edge_face[i] = cands[0] if cands else None
    return faces, edge_face, len(id2pt)


def group_edges(streets):
    """Cyclic runs of equal street ids -> list of lists of edge indices, CCW order."""
    n = len(streets)
    start = next((i for i in range(n) if streets[i] != streets[i - 1]), 0)
    groups, cur = [], [start]
    for k in range(1, n):
        i = (start + k) % n
        if streets[i] == streets[cur[-1]]:
            cur.append(i)
        else:
            groups.append(cur)
            cur = [i]
    groups.append(cur)
    return groups


def support_coords(verts, edges):
    n = len(verts)
    return [verts[edges[0]]] + [verts[(e + 1) % n] for e in edges]


def fix_diagonals(block, verts, groups, strips, supports):
    """Vanegas 4.2.2 (StreetLength scheme): at convex corners give the near-triangular
    corner region to the strip with the longer supporting street."""
    ext = block.exterior
    m = len(groups)
    for gi in range(m):
        gj = (gi + 1) % m
        a, b = groups[gi][-1], groups[gj][0]
        n = len(verts)
        v_prev, v, v_next = np.array(verts[a]), np.array(verts[b]), np.array(verts[(b + 1) % n])
        e_in, e_out = v - v_prev, v_next - v
        if e_in[0] * e_out[1] - e_in[1] * e_out[0] <= 0:  # reflex or straight: T(v) = None
            continue
        len_i, len_j = LineString(supports[gi]).length, LineString(supports[gj]).length
        x, y = (gi, gj) if len_i < len_j else (gj, gi)  # x loses, y gains
        if strips[x].is_empty or strips[y].is_empty:
            continue
        shared = strips[x].boundary.intersection(strips[y].boundary)
        cs = [c for g in getattr(shared, "geoms", [shared]) for c in getattr(g, "coords", [])]
        if not cs:
            continue
        q = max(cs, key=lambda c: ext.distance(Point(c)))
        psi = LineString(supports[x])
        f = psi.interpolate(psi.project(Point(q)))
        if Point(q).distance(f) < 0.01:
            continue
        qa, fa = np.array(q), np.array(f.coords[0])
        d = (fa - qa) / np.linalg.norm(fa - qa)
        if not LineString([q, f]).within(strips[x].buffer(1e-6)):
            continue
        cut = LineString([tuple(qa - d * 0.05), tuple(fa + d * 0.05)])
        pieces = as_polys(split(strips[x], cut))
        vpt = Point(v)
        moved = [p for p in pieces if p.distance(vpt) < 1e-6]
        keep = [p for p in pieces if p.distance(vpt) >= 1e-6]
        if moved:
            strips[y] = unary_union([strips[y]] + moved)
            strips[x] = unary_union(keep) if keep else Polygon()
    return strips


def slice_strip(strip, support, width):
    psi = LineString(support)
    L = psi.length
    n = max(1, int(round(L / width)))
    cuts = []
    for k in range(1, n):
        s = k * L / n
        p = np.array(psi.interpolate(s).coords[0])
        t = np.array(psi.interpolate(min(L, s + 0.5)).coords[0]) - np.array(psi.interpolate(max(0, s - 0.5)).coords[0])
        t /= np.linalg.norm(t)
        nrm = np.array([-t[1], t[0]])  # left normal = inward for a CCW block
        ray = LineString([tuple(p - nrm * 0.05), tuple(p + nrm * 2000)])
        inter = ray.intersection(strip)
        segs = [g for g in getattr(inter, "geoms", [inter]) if isinstance(g, LineString) and not g.is_empty]
        if not segs:
            continue
        seg = min(segs, key=lambda g: g.distance(Point(p)))
        c = np.array(seg.coords)
        dd = c[-1] - c[0]
        if np.linalg.norm(dd) < 1e-6:
            continue
        dd /= np.linalg.norm(dd)
        cuts.append(LineString([tuple(c[0] - dd * 0.05), tuple(c[-1] + dd * 0.05)]))
    if not cuts:
        return as_polys(strip)
    net = unary_union([strip.boundary] + cuts)
    faces = as_polys(shapely.polygonize(list(getattr(net, "geoms", [net]))))
    return [f for f in faces if strip.buffer(1e-6).contains(f.representative_point())]


def is_triangular(p):
    s = p.simplify(0.5)
    return len(s.exterior.coords) <= 4


def merge_small(parcels, a_min):
    parcels = list(parcels)
    changed = True
    while changed and len(parcels) > 1:
        changed = False
        order = sorted(range(len(parcels)), key=lambda i: parcels[i].area)
        for i in order:
            p = parcels[i]
            if p.area >= a_min and not is_triangular(p):
                continue
            best, best_len = None, 0.5
            for j, q in enumerate(parcels):
                if j == i:
                    continue
                sl = p.boundary.intersection(q.boundary).length
                if sl > best_len:
                    best, best_len = j, sl
            if best is None:
                continue
            merged = unary_union([p, parcels[best]])
            if not isinstance(merged, Polygon):
                continue
            parcels = [r for k, r in enumerate(parcels) if k not in (i, best)] + [merged]
            changed = True
            break
    return parcels


def subdivide_skeleton(block, verts, streets, width=SKEL_FRONT, fix=True, merge=True):
    faces, edge_face, n_nodes = skeleton_faces(verts)
    groups = group_edges(streets)
    strips, supports = [], []
    for g in groups:
        fs = [edge_face[e] for e in g if edge_face[e] is not None]
        strips.append(unary_union(fs) if fs else Polygon())
        supports.append(support_coords(verts, g))
    if fix:
        strips = fix_diagonals(block, verts, groups, strips, supports)
    parcels = []
    for s, sup in zip(strips, supports):
        if s.is_empty or s.area < 1e-3:
            continue
        parcels += slice_strip(s, sup, width)
    if merge:
        parcels = merge_small(parcels, A_MIN)
    return parcels, {"skeleton_nodes": n_nodes, "skeleton_faces": len(faces), "strips": sum(1 for s in strips if s.area > 1e-3)}


# ---------------------------------------------------------------- metrics
def metrics(block, parcels):
    ring_buf = block.exterior.buffer(0.01)
    areas = np.array([p.area for p in parcels])
    fr = np.array([frontage(p, ring_buf) for p in parcels])
    shorts, aspects, insc, rect, nverts = [], [], [], [], []
    for p in parcels:
        _, _, L, S = obb_info(p)
        shorts.append(S)
        aspects.append(L / max(S, 1e-9))
        insc.append(2 * shapely.maximum_inscribed_circle(p, 0.05).length)
        rect.append(p.area / max(shapely.oriented_envelope(p).area, 1e-9))
        nverts.append(len(p.exterior.coords) - 1)
    shorts, aspects, insc = np.array(shorts), np.array(aspects), np.array(insc)
    sliver = (aspects > SLIVER_ASPECT) | (insc < SLIVER_INSCRIBED)
    union_area = unary_union(parcels).area
    return {
        "plots": int(len(parcels)),
        "area_mean": round(float(areas.mean()), 1),
        "area_min": round(float(areas.min()), 1),
        "area_max": round(float(areas.max()), 1),
        "area_cv_pct": round(float(100 * areas.std() / areas.mean()), 1),
        "in_band": int(((areas >= A_MIN) & (areas <= A_MAX)).sum()),
        "below_min": int((areas < A_MIN).sum()),
        "above_max": int((areas > A_MAX).sum()),
        "no_access": int((fr < ACCESS_MIN).sum()),
        "frontage_lt_wmin": int((fr < W_MIN).sum()),
        "obb_short_lt_wmin": int((shorts < W_MIN).sum()),
        "slivers": int(sliver.sum()),
        "rectangularity_mean": round(float(np.mean(rect)), 3),
        "vertices_mean": round(float(np.mean(nverts)), 1),
        "vertices_max": int(np.max(nverts)),
        "coverage_pct": round(100 * union_area / block.area, 3),
        "overlap_m2": round(float(areas.sum() - union_area), 3),
    }


def match_iou(a, b):
    """For each parcel in a, best IoU with any parcel in b."""
    res = []
    for p in a:
        best = 0.0
        for q in b:
            if not p.intersects(q):
                continue
            inter = p.intersection(q).area
            if inter <= 0:
                continue
            best = max(best, inter / p.union(q).area)
        res.append(best)
    return np.array(res)


# ---------------------------------------------------------------- run
def run_case(name, verts, streets, results, store):
    block = Polygon(verts)
    assert block.is_valid and block.exterior.is_ccw, name
    row = {"case": name, "block_area": round(block.area, 1), "block_vertices": len(verts)}
    t0 = time.perf_counter()
    obb1 = subdivide_obb(block, xi=1.0)
    t1 = time.perf_counter()
    obb0 = subdivide_obb(block, xi=0.0)
    results.append({**row, "method": "OBB xi=1", "ms": round(1000 * (t1 - t0), 1), **metrics(block, obb1)})
    results.append({**row, "method": "OBB xi=0", **metrics(block, obb0)})
    store[(name, "OBB xi=1")] = obb1
    store[(name, "OBB xi=0")] = obb0
    # irregularity sweep: 20 seeds at omega = 0.3
    cnt, slv, noacc = [], [], []
    for sd in range(20):
        ps = subdivide_obb(block, xi=1.0, omega=0.3, seed=sd)
        m = metrics(block, ps)
        cnt.append(m["plots"]); slv.append(m["slivers"]); noacc.append(m["no_access"])
    results.append({**row, "method": "OBB xi=1 omega=0.3 (20 seeds)",
                    "plots_range": [min(cnt), max(cnt)], "slivers_range": [min(slv), max(slv)],
                    "no_access_range": [min(noacc), max(noacc)]})
    if HAVE_SKELETON:
        t0 = time.perf_counter()
        sk, info = subdivide_skeleton(block, verts, streets)
        t1 = time.perf_counter()
        results.append({**row, "method": "Skeleton", "ms": round(1000 * (t1 - t0), 1), **info, **metrics(block, sk)})
        store[(name, "Skeleton")] = sk
        raw, info2 = subdivide_skeleton(block, verts, streets, fix=False, merge=False)
        results.append({**row, "method": "Skeleton raw (no diagonal fix, no merge)", **info2, **metrics(block, raw)})
        store[(name, "Skeleton raw")] = raw


def main(out_dir):
    results, store = [], {}
    run_case("a_rectangle", *block_rect(), results, store)
    run_case("b_L", *block_L(), results, store)
    run_case("b_U", *block_U(), results, store)
    run_case("c_arc_10deg", *block_arc(10.0), results, store)
    run_case("c_arc_1deg", *block_arc(1.0), results, store)
    run_case("c_arc_1deg_chords_as_streets", *block_arc(1.0, merge_arc=False), results, store)
    run_case("d_thin", *block_thin(), results, store)

    # arc discretisation: how many plots survive a change from 10 to 1 degree chords
    stability = {}
    for meth in ("OBB xi=1", "Skeleton"):
        a, b = store.get(("c_arc_10deg", meth)), store.get(("c_arc_1deg", meth))
        if a is None or b is None:
            continue
        iou = match_iou(a, b)
        stability[meth] = {"plots_10deg": len(a), "plots_1deg": len(b),
                           "share_of_10deg_plots_with_IoU_ge_0.9": round(float((iou >= 0.9).mean()), 3),
                           "median_IoU": round(float(np.median(iou)), 3)}

    # arc sweep: chord angle vs result
    sweep = []
    for step in (20, 10, 5, 2, 1, 0.5, 0.25):
        v, s = block_arc(step)
        block = Polygon(v)
        sag = 300 * (1 - math.cos(math.radians(step / 2)))
        area_err = 100 * (1 - block.area / (0.5 * (300**2 - 220**2) * math.pi / 3))
        t0 = time.perf_counter(); o = subdivide_obb(block); t1 = time.perf_counter()
        row = {"chord_deg": step, "vertices": len(v), "outer_sagitta_m": round(sag, 3),
               "area_error_pct": round(area_err, 3), "obb_ms": round(1000 * (t1 - t0), 1)}
        mo = metrics(block, o)
        row.update({"obb_plots": mo["plots"], "obb_slivers": mo["slivers"], "obb_no_access": mo["no_access"],
                    "obb_vertices_max": mo["vertices_max"]})
        if HAVE_SKELETON:
            t0 = time.perf_counter(); interior_straight_skeleton([(x, y, 0.0) for x, y in v], as_graph=False)
            row["cgal_skeleton_ms"] = round(1000 * (time.perf_counter() - t0), 2)
            t0 = time.perf_counter(); k, info = subdivide_skeleton(block, v, s); t1 = time.perf_counter()
            mk = metrics(block, k)
            row.update({"skel_ms": round(1000 * (t1 - t0), 1), "skel_nodes": info["skeleton_nodes"],
                        "skel_plots": mk["plots"], "skel_slivers": mk["slivers"],
                        "skel_no_access": mk["no_access"], "skel_vertices_max": mk["vertices_max"]})
            v2, s2 = block_arc(step, merge_arc=False)
            k2, _ = subdivide_skeleton(Polygon(v2), v2, s2)
            mk2 = metrics(Polygon(v2), k2)
            row.update({"skel_chords_as_streets_plots": mk2["plots"], "skel_chords_as_streets_slivers": mk2["slivers"],
                        "skel_chords_as_streets_area_min": mk2["area_min"]})
        sweep.append(row)

    # lotWidthMin vs forceStreetAccess trade-off on the concave blocks (OBB, xi = 1)
    global W_MIN
    width_sweep = []
    w_saved = W_MIN
    for cname, fn in (("b_L", block_L), ("b_U", block_U)):
        v, _s = fn()
        block = Polygon(v)
        for w in (15.0, 10.0, 5.0):
            W_MIN = w
            m = metrics(block, subdivide_obb(block, xi=1.0))
            width_sweep.append({"case": cname, "lotWidthMin": w, "plots": m["plots"], "no_access": m["no_access"],
                                "slivers": m["slivers"], "area_min": m["area_min"], "area_max": m["area_max"]})
    W_MIN = w_saved

    out = {"parameters": {"A_MIN": A_MIN, "A_MAX": A_MAX, "W_MIN": W_MIN, "SKEL_FRONT": SKEL_FRONT,
                          "ACCESS_MIN": ACCESS_MIN, "SLIVER_ASPECT": SLIVER_ASPECT,
                          "SLIVER_INSCRIBED": SLIVER_INSCRIBED},
           "versions": {"shapely": shapely.__version__, "numpy": np.__version__, "python": sys.version.split()[0]},
           "results": results, "arc_stability": stability, "arc_sweep": sweep, "width_sweep": width_sweep}
    with open(f"{out_dir}/results.json", "w") as fh:
        json.dump(out, fh, indent=1)
    make_figure(store, f"{out_dir}/c10_subdivision.png")
    return out


def make_figure(store, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPoly

    cases = [("a_rectangle", "(a) rectangle 240 x 80 m"), ("b_L", "(b) L block"), ("b_U", "(b) U block"),
             ("c_arc_10deg", "(c) arc block, 10 deg chords"), ("c_arc_1deg", "(c) arc block, 1 deg chords"),
             ("c_arc_1deg_chords_as_streets", "(c) 1 deg, each chord = own street"), ("d_thin", "(d) thin irregular block")]
    methods = ["OBB xi=0", "OBB xi=1", "Skeleton"]
    fig, axes = plt.subplots(len(cases), len(methods), figsize=(12, 2.9 * len(cases)))
    ok, bad_area, noacc_c, sliv_c = "#9ecae1", "#fdd49e", "#bdbdbd", "#d62728"
    for r, (cname, ctitle) in enumerate(cases):
        for c, meth in enumerate(methods):
            ax = axes[r][c]
            ax.set_aspect("equal"); ax.axis("off")
            parcels = store.get((cname, meth))
            if parcels is None:
                continue
            block = unary_union(parcels)
            ring_buf = block.exterior.buffer(0.01) if isinstance(block, Polygon) else None
            for p in parcels:
                _, _, L, S = obb_info(p)
                insc = 2 * shapely.maximum_inscribed_circle(p, 0.05).length
                sliver = (L / max(S, 1e-9) > SLIVER_ASPECT) or insc < SLIVER_INSCRIBED
                acc = ring_buf is None or frontage(p, ring_buf) >= ACCESS_MIN
                face = ok if A_MIN <= p.area <= A_MAX else bad_area
                if not acc:
                    face = noacc_c
                ax.add_patch(MplPoly(np.array(p.exterior.coords), closed=True, fc=face,
                                     ec=sliv_c if sliver else "#333333", lw=1.6 if sliver else 0.5,
                                     hatch="///" if not acc else None))
            minx, miny, maxx, maxy = block.bounds
            ax.set_xlim(minx - 5, maxx + 5); ax.set_ylim(miny - 5, maxy + 5)
            ax.set_title(f"{ctitle}\n{meth}: {len(parcels)} plots", fontsize=8)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(fc=ok, ec="#333", label="area within 450-900 m2"),
                        Patch(fc=bad_area, ec="#333", label="area outside band"),
                        Patch(fc=noacc_c, ec="#333", hatch="///", label="no street frontage"),
                        Patch(fc="white", ec=sliv_c, lw=1.6, label="sliver (aspect > 4 or inscribed diameter < 7.5 m)")],
               loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path, dpi=80)


if __name__ == "__main__":
    res = main(sys.argv[1] if len(sys.argv) > 1 else ".")
    for row in res["results"]:
        print(row)
    print("arc stability", res["arc_stability"])
    for row in res["width_sweep"]:
        print(row)
    for row in res["arc_sweep"]:
        print(row)
