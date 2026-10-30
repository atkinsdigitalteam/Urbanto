"""C16: search for an eight-colour categorical palette for Urbanto Studio.

Constraints (all measured, nothing eyeballed):
  1. WCAG 2.x contrast ratio >= 3:1 (SC 1.4.11) against #FFFFFF and against #1E1E1E.
  2. Pairwise perceptual distance in CAM02-UCS (colorspacious deltaE, Euclidean J'a'b')
     under normal vision AND simulated deuteranopia AND simulated protanopia
     (Machado et al. 2009, severity 100, via colorspacious "sRGB1+CVD").
     Tritanopia is reported, and optionally added to the objective (--with-tritan).
  3. A chroma floor (CAM02-UCS M' >= 20) so no slot is a near-grey.

Method: candidate grid of 8-bit sRGB colours (step 5 per channel = 140,608 colours),
filtered by constraint 1 and 3, then maximin search: many random restarts of greedy
farthest-point selection followed by coordinate ascent (replace one slot at a time with
the candidate that maximises its minimum distance to the other seven) until no slot
improves. The objective is the minimum over all 28 pairs of
min(dE_normal, dE_deutan, dE_protan [, dE_tritan]).

Usage:
  python3 palette_search.py shared            # one palette valid on both backgrounds
  python3 palette_search.py shared --hue-gap 30   # at least 30 degrees of hue between any two slots
  python3 palette_search.py shared --with-tritan
  python3 palette_search.py light             # light-theme-only palette (>= 3:1 on #FFFFFF)
  python3 palette_search.py dark --hues '<json list of hex>' --jmax 85
        # per-theme variant: slot k kept within +-12 degrees of hue of the given palette
  python3 palette_search.py shared --hue-gap 30 --with-tritan --sim-contrast
        # strict: 3:1 must also hold for simulated colour on simulated background
  Other options: --jmin/--jmax (CAM02-UCS J' limits), --seed N, --restarts N
Writes JSON to stdout.
"""
import json
import sys

import numpy as np
import colorspacious as cs

BG = {"light": "#FFFFFF", "dark": "#1E1E1E"}
STEP = 5
CHROMA_FLOOR = 20.0      # CAM02-UCS M'
SEED = 20261030
RESTARTS = 400


def hex_to_rgb255(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def rgb255_to_hex(c):
    return "#%02X%02X%02X" % tuple(int(round(v)) for v in c)


def rel_lum(rgb255):
    """WCAG 2.2 relative luminance (sRGB, 0.04045 threshold)."""
    c = np.asarray(rgb255, dtype=float) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return lin @ np.array([0.2126, 0.7152, 0.0722])


def contrast(l1, l2):
    hi, lo = np.maximum(l1, l2), np.minimum(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


CVD = {
    "deutan": {"name": "sRGB1+CVD", "cvd_type": "deuteranomaly", "severity": 100},
    "protan": {"name": "sRGB1+CVD", "cvd_type": "protanomaly", "severity": 100},
    "tritan": {"name": "sRGB1+CVD", "cvd_type": "tritanomaly", "severity": 100},
}


def to_ucs(rgb255, vision="normal", severity=100):
    rgb1 = np.asarray(rgb255, dtype=float) / 255.0
    if vision == "normal":
        return cs.cspace_convert(rgb1, "sRGB1", "CAM02-UCS")
    space = dict(CVD[vision])
    space["severity"] = severity
    return cs.cspace_convert(rgb1, space, "CAM02-UCS")


def simulate_rgb255(rgb255, vision, severity=100):
    if vision == "normal":
        return np.asarray(rgb255, dtype=float)
    space = dict(CVD[vision])
    space["severity"] = severity
    out = cs.cspace_convert(np.asarray(rgb255, dtype=float) / 255.0, space, "sRGB1")
    return np.clip(out, 0, 1) * 255.0


def candidates(mode, jmin=0.0, jmax=100.0, sim_contrast=False):
    v = np.arange(0, 256, STEP, dtype=float)
    grid = np.stack(np.meshgrid(v, v, v, indexing="ij"), -1).reshape(-1, 3)
    ok = np.ones(len(grid), bool)
    # --sim-contrast: also require 3:1 after simulating colour AND background for each CVD
    for vision in (["normal", "deutan", "protan", "tritan"] if sim_contrast else ["normal"]):
        L = rel_lum(simulate_rgb255(grid, vision))
        for bgname in (["light", "dark"] if mode == "shared" else [mode]):
            Lbg = rel_lum(simulate_rgb255(hex_to_rgb255(BG[bgname]), vision))
            ok &= contrast(L, Lbg) >= 3.0
    grid = grid[ok]
    ucs = to_ucs(grid)
    chroma = np.hypot(ucs[:, 1], ucs[:, 2])
    keep = (chroma >= CHROMA_FLOOR) & (ucs[:, 0] >= jmin) & (ucs[:, 0] <= jmax)
    return grid[keep], ucs[keep]


def maximin(spaces, n=8, restarts=RESTARTS, seed=SEED, allowed=None, hue=None, hue_gap=0.0):
    """Maximise the minimum pairwise distance of an n-colour set.

    spaces : list of (N,3) CAM02-UCS arrays, one per vision type; the pair distance is
             the minimum over these vision types.
    allowed: optional list of n index arrays; slot k may only use allowed[k].
    hue, hue_gap: optional (N,) hue angles in degrees; any two chosen colours must differ
             in hue by at least hue_gap degrees (forces one colour per hue family).
    """
    rng = np.random.default_rng(seed)
    N = spaces[0].shape[0]
    cache = {}

    def d_to(idx):
        if idx not in cache:
            cache[idx] = np.min([np.linalg.norm(S - S[idx], axis=1) for S in spaces], axis=0)
        return cache[idx]

    def mask_for(slot, others):
        m = np.zeros(N)
        if allowed is not None:
            m[:] = -np.inf
            m[allowed[slot]] = 0
        if hue is not None and hue_gap > 0:
            for o in others:
                dh = np.abs((hue - hue[o] + 180) % 360 - 180)
                m[dh < hue_gap] = -np.inf
        return m

    def pair_min(sel):
        return min(min(np.linalg.norm(S[sel[a]] - S[sel[b]]) for S in spaces)
                   for a in range(len(sel)) for b in range(a + 1, len(sel)))

    best, best_score = None, -1.0
    for _ in range(restarts):
        first = int(rng.choice(allowed[0])) if allowed is not None else int(rng.integers(N))
        sel = [first]
        dmin = d_to(first).copy()
        for k in range(1, n):
            cand = dmin + mask_for(k, sel)
            j = int(np.argmax(cand))
            if not np.isfinite(cand[j]):
                break
            sel.append(j)
            dmin = np.minimum(dmin, d_to(j))
        if len(sel) < n:
            continue
        improved = True
        while improved:  # coordinate ascent; never decreases the objective
            improved = False
            for i in range(n):
                others = [s for t, s in enumerate(sel) if t != i]
                dm = np.min([d_to(o) for o in others], axis=0) + mask_for(i, others)
                j = int(np.argmax(dm))
                cur = float(np.min([d_to(o)[sel[i]] for o in others]))
                if dm[j] > cur + 1e-9:
                    sel[i] = j
                    improved = True
        score = pair_min(sel)
        if score > best_score:
            best, best_score = list(sel), score
    return best, best_score


def order_by_hue(rgbs):
    ucs = to_ucs(np.array(rgbs))
    h = np.degrees(np.arctan2(ucs[:, 2], ucs[:, 1])) % 360
    return [rgbs[i] for i in np.argsort(h)]


def main():
    mode = sys.argv[1]
    with_tritan = "--with-tritan" in sys.argv
    def opt(name, default):
        return float(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default
    grid, ucs_n = candidates(mode, opt("--jmin", 0.0), opt("--jmax", 100.0),
                             "--sim-contrast" in sys.argv)
    visions = ["deutan", "protan"] + (["tritan"] if with_tritan else [])
    spaces = [ucs_n] + [to_ucs(grid, v) for v in visions]
    allowed = None
    if "--hues" in sys.argv:  # hue-matched variant: slot k restricted to +-HUE_TOL of target hue
        target = json.loads(sys.argv[sys.argv.index("--hues") + 1])
        tol = 12.0
        h = np.degrees(np.arctan2(ucs_n[:, 2], ucs_n[:, 1])) % 360
        allowed = []
        for t in target:
            th = np.degrees(np.arctan2(*to_ucs(hex_to_rgb255(t))[[2, 1]])) % 360
            dh = np.abs((h - th + 180) % 360 - 180)
            allowed.append(np.where(dh <= tol)[0])
    gap = float(sys.argv[sys.argv.index("--hue-gap") + 1]) if "--hue-gap" in sys.argv else 0.0
    hue = np.degrees(np.arctan2(ucs_n[:, 2], ucs_n[:, 1])) % 360
    sel, score = maximin(spaces, allowed=allowed, hue=hue, hue_gap=gap,
                         seed=int(opt("--seed", SEED)), restarts=int(opt("--restarts", RESTARTS)))
    rgbs = [grid[i] for i in sel]
    if allowed is None:
        rgbs = order_by_hue(rgbs)
    print(json.dumps({
        "mode": mode, "objective_visions": ["normal"] + visions, "hue_gap_deg": gap,
        "candidates_after_filters": int(len(grid)),
        "min_pairwise_dE_objective": round(float(score), 2),
        "palette": [rgb255_to_hex(c) for c in rgbs],
    }, indent=1))


if __name__ == "__main__":
    main()
