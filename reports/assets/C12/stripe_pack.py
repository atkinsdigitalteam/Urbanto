"""
C12 stripe-packing parking layout test (Urbanto Studio research, 2026-10-30).

What it does
------------
Packs parking "modules" (stall row + aisle + stall row) as parallel stripes
inside a site polygon, for each parking angle, using the minimum dimensions of
Dubai Building Code (DBC) 2021 Table B.11. It searches the stripe direction and
the stripe offset (phase) and keeps the layout with the most stalls. It then
reports stalls, gross m2 per stall, stall-area efficiency, circulation length,
mean straight-line walk to an entrance, and the DBC accessible-bay count.

Model (deliberately simple; see the report for what it leaves out)
-------------------------------------------------------------------
* Circulation: a two-way perimeter loop of width RING_W (6.0 m, the DBC 90 deg
  two-way driveway) runs just inside the site edge. Every aisle is a straight
  stripe that ends on that loop at both ends, so there are no dead ends and
  one-way aisles always have an entry and an exit.
* Stalls are rectangles w x L (DBC 2.5 m x 5.5 m; parallel 2.5 m x 6.0 m) set
  at the stall angle with one corner on the aisle edge, as drawn in DBC Figures
  B.60 to B.63 (saw-tooth rows, no interlock between back-to-back rows).
  Row depth  d = L*sin(a) + w*cos(a);  pitch along aisle p = w / sin(a).
* A stall counts only if it lies wholly inside the interior (site minus loop)
  and the aisle strip in front of it is also inside the interior.
* 30 deg is not in DBC Table B.11. It is run with the DBC 2.5 x 5.5 m bay and
  the narrowest DBC one-way aisle (3.3 m, the 45 deg value) as an assumption.
* No accessible bays, landscape islands, columns, ramps or entrances are drawn.

Run:  python3 stripe_pack.py   (needs shapely >= 2, numpy, matplotlib)
"""
import json
import math
import time

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union

RING_W = 6.0          # DBC Table B.11: 90 deg two-way driveway, m
W, L = 2.5, 5.5       # DBC Table B.11 bay width and length, m

# name, angle (deg), bay width, bay length, aisle width, one-way?, note
CASES = [
    ("0 (parallel), one-way", 0, 2.5, 6.0, 3.0, True, "DBC B.11"),
    ("30, one-way*", 30, W, L, 3.3, True, "assumed: no DBC 30 deg row; 45 deg aisle used"),
    ("45, one-way", 45, W, L, 3.3, True, "DBC B.11"),
    ("60, one-way", 60, W, L, 3.8, True, "DBC B.11"),
    ("75, one-way", 75, W, L, 5.5, True, "DBC B.11"),
    ("90, one-way", 90, W, L, 5.5, True, "DBC B.11"),
    ("90, two-way", 90, W, L, 6.0, False, "DBC B.11"),
    # comparison only: US ULI/NPA values as quoted by Iowa SUDAS Table 8B-1.02
    # (8 ft 6 in stall, 18 ft projection, 24 ft two-way aisle)
    ("90, two-way, US ULI", 90, 2.591, 5.486, 7.315, False, "SUDAS 8B-1.02 (ULI/NPA), comparison"),
]

SITES = {
    "Rectangle 120 x 80 m": Polygon([(0, 0), (120, 0), (120, 80), (0, 80)]),
    "Irregular pentagon": Polygon([(0, 0), (110, 0), (135, 50), (80, 100), (8, 72)]),
}
# Building entrance used for the walking-distance score (on the site edge).
ENTRANCES = {"Rectangle 120 x 80 m": (60.0, 80.0), "Irregular pentagon": (44.0, 86.0)}


def row_geometry(angle, w, l):
    """Return (depth d, pitch p, template stall polygon with its aisle-side
    corner at x=0 and its far side at y=0, the aisle edge at y=d)."""
    if angle == 0:                       # parallel: long side along the aisle
        return w, l, box(0, 0, l, w)
    a = math.radians(angle)
    ax, ay = math.cos(a), math.sin(a)    # car axis
    nx, ny = -math.sin(a), math.cos(a)   # across the car
    pts = [(0, 0), (l * ax, l * ay), (l * ax + w * nx, l * ay + w * ny), (w * nx, w * ny)]
    poly = Polygon(pts)
    minx, miny, _, _ = poly.bounds
    poly = affinity.translate(poly, -minx, -miny)
    d = l * math.sin(a) + w * math.cos(a)
    p = w / math.sin(a)
    return d, p, poly


def pack(site, case, phi_step=2.0, phase_step=0.5, extra_dirs=()):
    """Search stripe direction phi and offset; return the best layout."""
    name, angle, w, l, aisle, one_way, _ = case
    interior = site.buffer(-RING_W, join_style="mitre")
    d, p, tmpl = row_geometry(angle, w, l)
    module = 2 * d + aisle
    tw = tmpl.bounds[2]                  # template x-extent
    # x of the stall corner that touches the aisle edge (the entry side)
    fx = 0.0 if angle == 0 else l * math.cos(math.radians(angle))
    phis = sorted(set([round(x, 3) for x in np.arange(0, 180, phi_step)] + list(extra_dirs)))
    tc = np.array(tmpl.exterior.coords)[:-1]          # 4 x 2 template corners
    tm = tc * np.array([1.0, -1.0])                   # mirrored (top row)
    best = None
    c = site.centroid
    for phi in phis:
        I = affinity.rotate(interior, -phi, origin=c)   # stripes run along x
        shapely.prepare(I)
        minx, miny, maxx, maxy = I.bounds
        xs = np.arange(minx - tw, maxx + tw, p)
        for s in np.arange(0, module, phase_step):
            stalls, aisles = [], []
            y0 = miny + s - module               # start one module early
            while y0 < maxy:
                ya0, ya1 = y0 + d, y0 + d + aisle    # aisle band
                band = box(minx - 1, ya0, maxx + 1, ya1)
                aisle_geom = band.intersection(I)
                if aisle_geom.is_empty:
                    y0 += module
                    continue
                # bottom row: stall corner touches aisle edge y=ya0;
                # top row: mirror of bottom row about the aisle centre line
                off_b = np.stack([xs, np.full_like(xs, y0)], 1)[:, None, :]
                off_t = np.stack([xs, np.full_like(xs, ya1 + d)], 1)[:, None, :]
                cand = np.concatenate([shapely.polygons(tc[None] + off_b),
                                       shapely.polygons(tm[None] + off_t)])
                fr = shapely.box(xs + fx, ya0, xs + fx + p, ya1)
                front = np.concatenate([fr, fr])
                ok = shapely.contains(I, cand) & shapely.contains(I, front)
                if ok.any():
                    stalls.extend(cand[ok].tolist())
                    aisles.append(aisle_geom)
                y0 += module
            n = len(stalls)
            if best is None or n > best["n"]:
                best = dict(n=n, phi=phi, phase=s, stalls=stalls, aisles=aisles)
    # rotate the winner back to site coordinates
    best["stalls"] = [affinity.rotate(g, best["phi"], origin=c) for g in best["stalls"]]
    best["aisles"] = [affinity.rotate(g, best["phi"], origin=c) for g in best["aisles"]]
    best.update(d=d, p=p, module=module, interior=interior)
    return best


def dbc_accessible(n):
    """DBC Table C.17 (all buildings except private housing)."""
    if n < 25:
        return None                      # table starts at 25 spaces
    if n <= 500:
        return max(1, math.ceil(0.02 * n))
    return 10 + math.ceil(0.01 * (n - 500))


def score(site, sname, case, best):
    name, angle, w, l, aisle, one_way, note = case
    n = best["n"]
    ring = site.difference(best["interior"])
    ring_len = site.buffer(-RING_W / 2, join_style="mitre").exterior.length
    aisle_len = sum(g.length / 2 - aisle for g in best["aisles"] if not g.is_empty)  # ~ centre-line length
    ent = Point(ENTRANCES[sname])
    walk = float(np.mean([g.centroid.distance(ent) for g in best["stalls"]])) if n else float("nan")
    stall_area = n * w * l
    used = unary_union(best["stalls"] + best["aisles"]).intersection(best["interior"])
    unused = best["interior"].area - used.area   # interior left unpaved/unused
    return {
        "site": sname, "case": name, "angle_deg": angle, "bay_w_m": w, "bay_l_m": l,
        "aisle_m": aisle, "row_depth_m": round(best["d"], 3), "pitch_m": round(best["p"], 3),
        "module_m": round(best["module"], 3),
        "theory_m2_per_stall": round(best["module"] * best["p"] / 2, 2),
        "site_m2": round(site.area, 1), "stalls": n,
        "gross_m2_per_stall": round(site.area / n, 2) if n else None,
        "stall_area_efficiency_pct": round(100 * stall_area / site.area, 1),
        "circulation_m": round(ring_len + aisle_len, 1),
        "loop_area_m2": round(ring.area, 1),
        "unused_interior_m2": round(unused, 1),
        "mean_walk_to_entrance_m": round(walk, 1),
        "dbc_accessible_bays": dbc_accessible(n),
        "best_direction_deg": float(best["phi"]), "best_phase_m": float(best["phase"]),
        "note": note,
    }


def main():
    t0 = time.time()
    results, layouts = [], {}
    for sname, site in SITES.items():
        # also try every site-edge direction so the optimum is not missed
        coords = list(site.exterior.coords)
        edge_dirs = [math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180
                     for a, b in zip(coords[:-1], coords[1:])]
        for case in CASES:
            best = pack(site, case, extra_dirs=edge_dirs)
            r = score(site, sname, case, best)
            results.append(r)
            layouts[(sname, case[0])] = best
            print(f"{sname:22s} {case[0]:24s} stalls={r['stalls']:4d} "
                  f"m2/stall={r['gross_m2_per_stall']:6.2f} eff={r['stall_area_efficiency_pct']:5.1f}% "
                  f"theory={r['theory_m2_per_stall']:6.2f} circ={r['circulation_m']:6.1f} m "
                  f"walk={r['mean_walk_to_entrance_m']:5.1f} m acc={r['dbc_accessible_bays']} "
                  f"loop={r['loop_area_m2']:.0f} unused={r['unused_interior_m2']:.0f} "
                  f"dir={r['best_direction_deg']:.1f}")
    print(f"elapsed {time.time() - t0:.1f} s")
    with open("results.json", "w") as f:
        json.dump(results, f, indent=1)
    draw(layouts, results)


def draw(layouts, results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    surface, ink, muted = "#fcfcfb", "#0b0b0b", "#52514e"
    stall_c, circ_c, aisle_c = "#2a78d6", "#d9d8d4", "#bdbcb7"
    fig, axs = plt.subplots(2, len(CASES), figsize=(3.0 * len(CASES), 6.6), facecolor=surface)
    for i, (sname, site) in enumerate(SITES.items()):
        for j, case in enumerate(CASES):
            ax = axs[i, j]
            ax.set_facecolor(surface)
            b = layouts[(sname, case[0])]
            r = [x for x in results if x["site"] == sname and x["case"] == case[0]][0]
            ring = site.difference(b["interior"])
            for g in getattr(ring, "geoms", [ring]):
                ax.fill(*g.exterior.xy, color=circ_c, lw=0)
                for h in g.interiors:
                    ax.fill(*h.xy, color=surface, lw=0)
            for g in b["aisles"]:
                for gg in getattr(g, "geoms", [g]):
                    if gg.geom_type == "Polygon":
                        ax.fill(*gg.exterior.xy, color=aisle_c, lw=0)
            for g in b["stalls"]:
                ax.fill(*g.exterior.xy, facecolor=stall_c, edgecolor=surface, lw=0.4)
            ax.plot(*site.exterior.xy, color=ink, lw=1.0)
            ex, ey = ENTRANCES[sname]
            ax.plot([ex], [ey], marker="v", color=ink, ms=6)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(f"{case[0]}\n{r['stalls']} stalls, {r['gross_m2_per_stall']:.1f} m²/stall",
                         fontsize=9, color=ink)
        axs[i, 0].text(-0.08, 0.5, sname, transform=axs[i, 0].transAxes, rotation=90,
                       va="center", ha="right", fontsize=10, color=muted)
    fig.suptitle("Stripe packing with DBC 2021 Table B.11 minimum dimensions "
                 "(blue = stall, light grey = 6 m loop, mid grey = aisle, ▼ = entrance)",
                 fontsize=11, color=ink)
    fig.tight_layout(rect=(0.01, 0, 1, 0.95))
    fig.savefig("C12-layouts.png", dpi=90, facecolor=surface)

    # m2/stall by angle, two sites (two series: slot 1 blue, slot 2 orange)
    fig2, ax = plt.subplots(figsize=(9.5, 3.8), facecolor=surface)
    ax.set_facecolor(surface)
    names = [c[0] for c in CASES]
    x = np.arange(len(names))
    colors = {"Rectangle 120 x 80 m": "#2a78d6", "Irregular pentagon": "#eb6834"}
    for k, sname in enumerate(SITES):
        vals = [[r for r in results if r["site"] == sname and r["case"] == nm][0]["gross_m2_per_stall"]
                for nm in names]
        bars = ax.bar(x + (k - 0.5) * 0.38, vals, width=0.36, color=colors[sname], label=sname,
                      edgecolor=surface, linewidth=2)
        for bx, v in zip(bars, vals):
            ax.text(bx.get_x() + bx.get_width() / 2, v + 0.6, f"{v:.1f}", ha="center",
                    fontsize=7.5, color=muted)
    theo = [[r for r in results if r["case"] == nm][0]["theory_m2_per_stall"] for nm in names]
    ax.plot(x, theo, ls="none", color=ink, marker="_", ms=22, mew=2.5,
            label="Module only (no loop, no row ends)")
    ax.set_xticks(x, [n.replace(", ", ",\n", 1) for n in names], fontsize=8, color=ink)
    ax.set_ylabel("Gross site m² per stall", color=ink)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(muted)
    ax.spines["bottom"].set_color(muted)
    ax.tick_params(colors=muted)
    ax.grid(axis="y", color="#e6e5e1", lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.set_title("Land take per stall by angle (lower is better)", fontsize=11, color=ink, loc="left")
    fig2.tight_layout()
    fig2.savefig("C12-m2-per-stall.png", dpi=110, facecolor=surface)


if __name__ == "__main__":
    main()
