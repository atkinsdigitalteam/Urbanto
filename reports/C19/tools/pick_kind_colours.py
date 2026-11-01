"""Search data-kind colours that stay apart for normal vision and three colour-vision deficiencies.

Constraints: contrast >= 3:1 against node and canvas of the theme; each kind keeps a hue family.
Objective: maximise the smallest CAM02-UCS distance over normal, deutan, protan, tritan (severity 100).
"""
import colorsys, itertools, json, random, sys
import numpy as np
from colorspacious import cspace_convert
sys.path.insert(0, ".")
from build_tokens import contrast, DARK, LIGHT

HUES = {"shapes": (155, 185), "number": (205, 232), "text": (268, 300)}
CONDS = [None, "deuteranomaly", "protanomaly", "tritanomaly"]

def hexof(rgb):
    return "#%02X%02X%02X" % tuple(int(round(v * 255)) for v in rgb)

def candidates(theme, hue_range, n=400, seed=1):
    rnd = random.Random(seed)
    out = []
    while len(out) < n:
        h = rnd.uniform(*hue_range) / 360
        l = rnd.uniform(0.55, 0.80) if theme is DARK else rnd.uniform(0.28, 0.48)
        s = rnd.uniform(0.45, 0.85)
        rgb = colorsys.hls_to_rgb(h, l, s)
        hx = hexof(rgb)
        if contrast(hx, theme["node"]) >= 3 and contrast(hx, theme["canvas"]) >= 3:
            out.append(hx)
    return out

def sim_ucs(hexes):
    cols = np.array([[int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)] for h in hexes])
    res = []
    for c in CONDS:
        s = cols if c is None else np.clip(cspace_convert(cols, {"name": "sRGB1+CVD", "cvd_type": c, "severity": 100}, "sRGB1"), 0, 1)
        res.append(cspace_convert(s, "sRGB1", "CAM02-UCS"))
    return res

def score(hexes):
    best = 1e9
    for ucs in sim_ucs(hexes):
        for i, j in itertools.combinations(range(len(hexes)), 2):
            best = min(best, float(np.linalg.norm(ucs[i] - ucs[j])))
    return best

def search(theme, any_hex, iters=6000, seed=7):
    pools = {k: candidates(theme, r, seed=i + 1) for i, (k, r) in enumerate(HUES.items())}
    rnd = random.Random(seed)
    cur = {k: rnd.choice(v) for k, v in pools.items()}
    cur_s = score(list(cur.values()) + [any_hex])
    for _ in range(iters):
        k = rnd.choice(list(pools))
        trial = dict(cur, **{k: rnd.choice(pools[k])})
        s = score(list(trial.values()) + [any_hex])
        if s >= cur_s:
            cur, cur_s = trial, s
    return cur, cur_s

if __name__ == "__main__":
    out = {}
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        best, s = search(theme, theme["kind-any"])
        out[name] = {"colours": best, "min_distance_all_conditions": round(s, 1)}
        print(name, best, round(s, 1))
    json.dump(out, open("kind_colours_search.json", "w"), indent=1)
