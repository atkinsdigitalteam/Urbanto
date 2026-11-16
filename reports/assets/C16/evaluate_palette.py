"""C16: evaluate candidate palettes and render swatches.

Measures, for each palette:
  - WCAG 2.2 contrast ratio against #FFFFFF and #1E1E1E (normal vision), and the same
    ratio after simulating both colour and background for each colour-vision deficiency;
  - minimum pairwise CAM02-UCS deltaE' (colorspacious) for normal vision and for
    deuteranopia, protanopia and tritanopia (Machado et al. 2009, severity 100), the worst
    pair, and the minimum over severities 10, 20, ..., 100 (anomalous trichromacy);
  - minimum pairwise CIEDE2000 (colour-science 0.4.7) as a cross-check;
  - a slot order in which every prefix (first k colours) keeps the largest minimum distance.
Renders PNG swatches (fills, 2 px lines with dash patterns, markers) on both backgrounds
under normal vision and the three simulations.

Usage: PYTHONPATH=<dir with colour-science> python3 evaluate_palette.py <out_dir>
"""
import itertools
import json
import os
import sys

import numpy as np
import colorspacious as cs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.style as mstyle

try:
    import colour  # colour-science, only for the CIEDE2000 cross-check
except ImportError:  # pragma: no cover
    colour = None

BG = {"light": "#FFFFFF", "dark": "#1E1E1E"}
VISIONS = ["normal", "deutan", "protan", "tritan"]
CVD_NAME = {"deutan": "deuteranomaly", "protan": "protanomaly", "tritan": "tritanomaly"}
LABEL = {"normal": "Normal vision", "deutan": "Deuteranopia (sim.)",
         "protan": "Protanopia (sim.)", "tritan": "Tritanopia (sim.)"}

PALETTES = {
    # Shared palette chosen in C16 (palette_search.py shared --hue-gap 30 --with-tritan),
    # listed in assignment order (every prefix keeps the largest minimum distance)
    "shared": ["#EB7300", "#1E96FF", "#7837FF", "#147869",
               "#D20528", "#8C55A0", "#64A06E", "#BE78A0"],
    # Strict: 3:1 also after simulating colour and background (--sim-contrast)
    "shared_strict": ["#FF2D41", "#5F7800", "#5A9B6E", "#057D78",
                      "#2387FF", "#7837FF", "#9650AA", "#CD6EA5"],
    # Best distance found without the hue-diversity rule (normal + deutan + protan only)
    "shared_maxdist": ["#969B00", "#646E1E", "#00AA73", "#007869",
                       "#50A0AA", "#286EA0", "#788CFF", "#6941FF"],
    # Baselines taken from matplotlib (installed version), not from memory
    "tab10_first8": [matplotlib.colors.to_hex(c).upper()
                     for c in matplotlib.colormaps["tab10"].colors[:8]],
    "petroff8": [c.upper() for c in mstyle.library["petroff8"]["axes.prop_cycle"].by_key()["color"]],
}

DASHES = [(None, None), (6, 3), (1.5, 2), (6, 2, 1.5, 2), (10, 3), (6, 2, 1.5, 2, 1.5, 2),
          (3, 3), (12, 2, 3, 2)]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]


def rgb255(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def rel_lum(c255):
    c = np.asarray(c255, float) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(lin @ np.array([0.2126, 0.7152, 0.0722]))


def contrast(a255, b255):
    la, lb = rel_lum(a255), rel_lum(b255)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def space(vision, severity=100):
    if vision == "normal":
        return "sRGB1"
    return {"name": "sRGB1+CVD", "cvd_type": CVD_NAME[vision], "severity": severity}


def sim255(c255, vision, severity=100):
    if vision == "normal":
        return np.asarray(c255, float)
    out = cs.cspace_convert(np.asarray(c255, float) / 255, space(vision, severity), "sRGB1")
    return np.clip(out, 0, 1) * 255


def ucs(hexes, vision, severity=100):
    rgb = np.array([rgb255(h) for h in hexes]) / 255
    return cs.cspace_convert(rgb, space(vision, severity), "CAM02-UCS")


def pairwise_min(points):
    best = (np.inf, None)
    for a, b in itertools.combinations(range(len(points)), 2):
        d = float(np.linalg.norm(points[a] - points[b]))
        if d < best[0]:
            best = (d, (a, b))
    return best


def ciede2000_min(hexes, vision):
    if colour is None:
        return None
    rgb = np.array([sim255(rgb255(h), vision) for h in hexes]) / 255
    lab = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))  # D65, L* in 0..100
    return min(float(colour.delta_E(lab[a], lab[b], method="CIE 2000"))
               for a, b in itertools.combinations(range(len(hexes)), 2))


def prefix_order(hexes):
    """Order slots so that every prefix keeps the largest possible minimum distance."""
    pts = [np.stack([ucs([h], v)[0] for v in VISIONS]) for h in hexes]

    def d(i, j):
        return float(np.min(np.linalg.norm(pts[i] - pts[j], axis=1)))
    n = len(hexes)
    a, b = max(itertools.combinations(range(n), 2), key=lambda p: d(*p))
    order = [a, b]
    while len(order) < n:
        rest = [k for k in range(n) if k not in order]
        order.append(max(rest, key=lambda k: min(d(k, o) for o in order)))
    prefix = [round(min(d(i, j) for i, j in itertools.combinations(order[:k], 2)), 2)
              for k in range(2, n + 1)]
    return [hexes[i] for i in order], prefix


def evaluate(name, hexes):
    res = {"name": name, "palette": hexes, "contrast": {}, "dE": {}, "dE_worst_pair": {},
           "dE_min_over_severity": {}, "ciede2000_min": {}}
    for bgname, bg in BG.items():
        for v in VISIONS:
            bgs = sim255(rgb255(bg), v)
            res["contrast"][f"{bgname}/{v}"] = [round(contrast(sim255(rgb255(h), v), bgs), 2)
                                               for h in hexes]
    for v in VISIONS:
        dmin, pair = pairwise_min(ucs(hexes, v))
        res["dE"][v] = round(dmin, 2)
        res["dE_worst_pair"][v] = [hexes[pair[0]], hexes[pair[1]]]
        if v != "normal":
            res["dE_min_over_severity"][v] = round(min(
                pairwise_min(ucs(hexes, v, s))[0] for s in range(10, 101, 10)), 2)
        c = ciede2000_min(hexes, v)
        res["ciede2000_min"][v] = None if c is None else round(c, 2)
    res["J_prime"] = [round(float(x), 1) for x in ucs(hexes, "normal")[:, 0]]
    u = ucs(hexes, "normal")
    res["chroma_M_prime"] = [round(float(np.hypot(x[1], x[2])), 1) for x in u]
    res["hue_h_prime"] = [round(float(np.degrees(np.arctan2(x[2], x[1])) % 360), 1) for x in u]
    res["prefix_order"], res["prefix_min_dE_all4"] = prefix_order(hexes)
    return res


def render(hexes_by_bg, path, title):
    """hexes_by_bg: {'light': [...], 'dark': [...]} (same list twice for a shared palette)."""
    fig, axes = plt.subplots(len(VISIONS), 2, figsize=(12, 10.5), dpi=100)
    for col, bgname in enumerate(["light", "dark"]):
        hexes = hexes_by_bg[bgname]
        for row, v in enumerate(VISIONS):
            ax = axes[row, col]
            bg = sim255(rgb255(BG[bgname]), v) / 255
            ink = "#000000" if bgname == "light" else "#FFFFFF"
            ax.set_facecolor(bg)
            for i, h in enumerate(hexes):
                c = sim255(rgb255(h), v) / 255
                x = i * 1.25
                ax.add_patch(plt.Rectangle((x, 2.2), 1.0, 1.0, color=c))
                dash = DASHES[i]
                ln, = ax.plot([x, x + 1.0], [1.6, 1.6], color=c, lw=2)
                if dash[0] is not None:
                    ln.set_dashes(dash)
                ax.plot([x + 0.5], [0.9], marker=MARKERS[i], color=c, ms=9, mew=0)
                ax.text(x + 0.5, 0.25, str(i + 1), ha="center", va="center", color=ink, fontsize=9)
            ax.set_xlim(-0.2, 8 * 1.25)
            ax.set_ylim(0, 3.5)
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(False)
            ax.set_title(f"{LABEL[v]} on {BG[bgname]}", fontsize=10, loc="left")
    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, facecolor="#F4F4F4")
    plt.close(fig)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    pals = dict(PALETTES)
    extra = os.path.join(out, "per_theme.json")
    if os.path.exists(extra):  # per-theme variants written by palette_search.py runs
        pt = json.load(open(extra))
        pals["light_variant"] = pt["light"]
        pals["dark_variant"] = pt["dark"]
    results = {k: evaluate(k, v) for k, v in pals.items()}
    json.dump(results, open(os.path.join(out, "palette_results.json"), "w"), indent=1)
    render({"light": pals["shared"], "dark": pals["shared"]},
           os.path.join(out, "swatch_shared.png"),
           "Shared palette: fill, 2 px line with dash pattern, marker; slots 1-8")
    if "light_variant" in pals:
        render({"light": pals["light_variant"], "dark": pals["dark_variant"]},
               os.path.join(out, "swatch_per_theme.png"),
               "Per-theme variants (same hues): light set on #FFFFFF, dark set on #1E1E1E")
    for k, r in results.items():
        print(k, "dE'", r["dE"], "sev-min", r["dE_min_over_severity"],
              "CIEDE2000", r["ciede2000_min"])
        print("   min contrast light", min(r["contrast"]["light/normal"]),
              "dark", min(r["contrast"]["dark/normal"]))


if __name__ == "__main__":
    main()
