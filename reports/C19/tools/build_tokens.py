"""Single source of the C19 Flow tokens.

Writes ../tokens.json, ../mockups/tokens.css and ../tools/contrast.md (measured contrast ratios and
colour-vision checks). Run: python3 build_tokens.py
"""
import json, pathlib, itertools

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent

# ---------------------------------------------------------------- colours
DARK = {
    # surfaces, darkest to lightest
    "canvas": "#0F151F",
    "canvas-dot": "#1F2A3A",
    "canvas-dot-major": "#2A374B",
    "panel": "#141B27",
    "panel-raised": "#1A2231",
    "control": "#1F2838",
    "control-hover": "#263042",
    "node": "#1A2232",
    "node-header": "#1F2839",
    "node-hover": "#1E2737",
    "overlay": "#1C2434",
    # lines
    "divider": "#252F40",
    "border": "#273142",
    "border-strong": "#364258",
    "node-border": "#2C3749",
    "node-border-hover": "#3D4A62",
    # text
    "text": "#E6EAF1",
    "text-muted": "#9AA5B8",
    "text-subtle": "#6E7A8E",
    "text-on-accent": "#1C1406",
    # brand accent
    "accent": "#E9AB4C",
    "accent-hover": "#F0BA66",
    "accent-fill": "#E9AB4C",
    "accent-soft": "#E9AB4C29",
    "accent-line": "#E9AB4C",
    "selection": "#E9AB4C",
    "selection-fill": "#E9AB4C14",
    "focus-ring": "#E9AB4C",
    # data kinds (ports and wires)
    "kind-shapes": "#6AF0CB",
    "kind-number": "#5F9BF1",
    "kind-text": "#8D46D5",
    "kind-any": "#98A3B5",
    # states
    "danger": "#F2777C",
    "danger-soft": "#F2777C24",
    "warning": "#F3CF63",
    "warning-soft": "#F3CF6324",
    "success": "#6FD98F",
    "running": "#E6EAF1",
    "paused": "#E9AB4C",
    "stale": "#9AA5B8",
    "disabled-opacity": "0.45",
    "bypass-opacity": "0.60",
    # badges
    "badge": "#263044",
    "badge-text": "#B9C2D2",
    # groups (frame colour; fill uses group-fill-alpha)
    "group-1": "#E9AB4C", "group-2": "#5BB8F5", "group-3": "#9C83F2", "group-4": "#4CC6B4",
    "group-5": "#F2777C", "group-6": "#C984D8", "group-7": "#8BC97A", "group-8": "#D9A0BE",
    # node categories (icon tile)
    "cat-source": "#5BB8F5", "cat-value": "#8BC97A", "cat-shape": "#4CC6B4", "cat-measure": "#D9A0BE",
    "cat-list": "#9C83F2", "cat-flow": "#C984D8", "cat-output": "#A3B1C6",
    # minimap
    "minimap": "#141B27F0",
    "minimap-node": "#3A465C",
    "minimap-viewport": "#E9AB4C",
    "minimap-viewport-fill": "#E9AB4C14",
    # shadows
    "shadow-node": "0 2px 6px #00000059",
    "shadow-node-selected": "0 4px 14px #00000073",
    "shadow-overlay": "0 8px 24px #00000080",
}

LIGHT = {
    "canvas": "#F3F5F8",
    "canvas-dot": "#D5DBE4",
    "canvas-dot-major": "#C2CAD6",
    "panel": "#FFFFFF",
    "panel-raised": "#F7F8FA",
    "control": "#F1F3F6",
    "control-hover": "#E7EBF0",
    "node": "#FFFFFF",
    "node-header": "#F8F9FB",
    "node-hover": "#FBFCFD",
    "overlay": "#FFFFFF",
    "divider": "#E5E9EF",
    "border": "#E1E5EB",
    "border-strong": "#C6CEDA",
    "node-border": "#CDD4DF",
    "node-border-hover": "#B3BDCC",
    "text": "#172B45",
    "text-muted": "#55657D",
    "text-subtle": "#7E8CA2",
    "text-on-accent": "#1C1406",
    "accent": "#955700",
    "accent-hover": "#7E4A00",
    "accent-fill": "#E9AB4C",
    "accent-soft": "#E9AB4C33",
    "accent-line": "#C98216",
    "selection": "#B06F0C",
    "selection-fill": "#E9AB4C1F",
    "focus-ring": "#B06F0C",
    "kind-shapes": "#18A174",
    "kind-number": "#1735DB",
    "kind-text": "#48256F",
    "kind-any": "#6B778A",
    "danger": "#C9343C",
    "danger-soft": "#C9343C1A",
    "warning": "#9A6B00",
    "warning-soft": "#F3CF6338",
    "success": "#1E8A4C",
    "running": "#172B45",
    "paused": "#955700",
    "stale": "#55657D",
    "disabled-opacity": "0.45",
    "bypass-opacity": "0.60",
    "badge": "#EEF1F5",
    "badge-text": "#46566E",
    "group-1": "#C98216", "group-2": "#2F86C8", "group-3": "#6C55D8", "group-4": "#0E8A7D",
    "group-5": "#C9343C", "group-6": "#A04FB5", "group-7": "#4C8C3B", "group-8": "#B0567F",
    "cat-source": "#2F86C8", "cat-value": "#4C8C3B", "cat-shape": "#0E8A7D", "cat-measure": "#B0567F",
    "cat-list": "#6C55D8", "cat-flow": "#A04FB5", "cat-output": "#5E6E86",
    "minimap": "#FFFFFFF2",
    "minimap-node": "#C3CBD7",
    "minimap-viewport": "#C98216",
    "minimap-viewport-fill": "#E9AB4C1F",
    "shadow-node": "0 1px 3px #1018281F",
    "shadow-node-selected": "0 4px 12px #10182829",
    "shadow-overlay": "0 8px 24px #10182833",
}

# ---------------------------------------------------------------- sizes (px at 100 percent zoom)
SIZE = {
    "grid": 8,
    "canvas-dot-spacing": 24,
    "canvas-dot-size": 1.5,
    "canvas-dot-major-every": 4,
    "node-width-s": 160, "node-width-m": 208, "node-width-l": 256,
    "node-radius": 8,
    "node-border": 1,
    "node-header-height": 32,
    "node-header-padding-x": 10,
    "node-icon-tile": 20,
    "node-icon-tile-radius": 5,
    "node-icon": 14,
    "node-icon-stroke": 1.75,
    "node-title-gap": 8,
    "node-row-height": 24,
    "node-body-padding-y": 4,
    "node-port-label-inset": 12,
    "node-divider": 1,
    "port-size": 10,
    "port-ring": 2,
    "port-hit-width": 20,
    "inline-field-height": 20,
    "inline-field-radius": 4,
    "inline-field-min-width": 56,
    "count-badge-height": 16,
    "count-badge-radius": 8,
    "count-badge-padding-x": 6,
    "state-badge": 16,
    "state-badge-glyph": 10,
    "state-badge-gap": 4,
    "selection-width": 2,
    "selection-offset": 2,
    "error-tray-padding": 8,
    "error-tray-max-lines": 2,
    "wire-item": 1.75,
    "wire-list": 3,
    "wire-nested-outer": 5.5,
    "wire-nested-gap": 2.5,
    "wire-lazy-dash": "6 4",
    "wire-hover-extra": 1,
    "wire-selected-underlay": 6,
    "wire-flow-dash": "4 8",
    "wire-flow-speed-px-per-s": 40,
    "wire-curve-min": 24,
    "wire-curve-max": 120,
    "wire-curve-factor": 0.5,
    "wire-fade-selected-threshold": 40,
    "wire-fade-global-threshold": 400,
    "wire-fade-opacity": 0.25,
    "wire-opacity-dark": 0.85,
    "wire-opacity-light": 0.75,
    "group-radius": 12,
    "group-padding": 16,
    "group-title-height": 28,
    "group-border": 1,
    "minimap-width": 200,
    "minimap-height": 136,
    "minimap-radius": 8,
    "minimap-margin": 12,
    "toolbar-height": 40,
    "toolbar-button": 28,
    "toolbar-button-radius": 6,
    "toolbar-icon": 16,
    "toolbar-gap": 4,
    "toolbar-group-gap": 12,
    "panel-left-width": 248,
    "panel-right-width": 300,
    "panel-padding": 12,
    "panel-row-height": 28,
    "panel-section-gap": 16,
    "control-height": 28,
    "control-radius": 6,
    "problem-chip-height": 24,
    "hover-card-width": 220,
    "hover-card-radius": 8,
    "hover-card-thumb-height": 120,
}

TYPE = {
    "family-ui": "IBM Plex Sans",
    "family-mono": "Cascadia Mono",
    "node-title": {"size": 13, "line": 16, "weight": 600},
    "node-subtitle": {"size": 11, "line": 14, "weight": 400},
    "port-label": {"size": 11, "line": 14, "weight": 400},
    "inline-value": {"size": 11, "line": 14, "weight": 500, "numbers": "tabular"},
    "badge": {"size": 10, "line": 12, "weight": 500, "numbers": "tabular"},
    "error-message": {"size": 11, "line": 15, "weight": 400},
    "group-title": {"size": 13, "line": 16, "weight": 600},
    "panel-title": {"size": 13, "line": 18, "weight": 600},
    "section-label": {"size": 11, "line": 16, "weight": 600},
    "body": {"size": 12, "line": 16, "weight": 400},
    "body-strong": {"size": 12, "line": 16, "weight": 500},
    "small": {"size": 11, "line": 14, "weight": 400},
    "toolbar": {"size": 12, "line": 16, "weight": 500},
}

ZOOM = {
    "full-detail-min": 0.65,
    "block-mode-below": 0.35,
    "title-fixed-screen-size": 12,
    "state-glyph-screen-size": 16,
    "group-title-fixed-screen-size": 13,
    "wire-min-screen-width": 1,
    "wire-opacity-below-30": 0.35,
    "dots-hidden-below": 0.40,
    "levels": {
        "100": "Everything: titles 13 px, port labels 11 px, inline fields, count badges, state badges, wires by structure.",
        "60": "Port labels and inline fields hidden; ports drawn as 6 px dots; titles drawn at 12 px screen size; count and state badges kept; wires keep colour, item and list widths scale but never below 1 px.",
        "30": "Node is a block: node fill plus a 4 px category strip at the top, state glyph 16 px screen size in the centre, no title; group titles at 13 px screen size; wires 1 px at 35 percent opacity; minor dots hidden.",
    },
}

KINDS = {
    "shapes": {"port-shape": "circle", "label": "Shapes"},
    "number": {"port-shape": "diamond", "label": "Number"},
    "text": {"port-shape": "rounded-square", "label": "Text, choice and true/false"},
    "any": {"port-shape": "ring", "label": "Any"},
}

# ---------------------------------------------------------------- checks
def hex_rgb(h):
    h = h.lstrip("#")[:6]
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def lum(h):
    def c(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in hex_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

CHECKS = [
    ("text", "canvas", 4.5), ("text", "node", 4.5), ("text", "panel", 4.5),
    ("text-muted", "node", 4.5), ("text-muted", "panel", 4.5), ("text-subtle", "panel", 3.0),
    ("accent", "panel", 3.0), ("text-on-accent", "accent-fill", 4.5),
    ("node-border", "canvas", 1.3), ("border-strong", "panel", 1.5),
    ("kind-shapes", "node", 3.0), ("kind-number", "node", 3.0), ("kind-text", "node", 3.0),
    ("kind-any", "node", 3.0),
    ("kind-shapes", "canvas", 3.0), ("kind-number", "canvas", 3.0), ("kind-text", "canvas", 3.0),
    ("kind-any", "canvas", 3.0),
    ("danger", "node", 3.0), ("warning", "node", 3.0), ("success", "node", 3.0),
    ("badge-text", "badge", 4.5), ("selection", "canvas", 3.0),
    ("cat-source", "node-header", 3.0), ("cat-value", "node-header", 3.0), ("cat-shape", "node-header", 3.0),
    ("cat-measure", "node-header", 3.0), ("cat-list", "node-header", 3.0), ("cat-flow", "node-header", 3.0),
    ("cat-output", "node-header", 3.0), ("paused", "node", 3.0), ("stale", "node", 3.0),
]

def run_checks(theme, name):
    rows = []
    for fg, bg, need in CHECKS:
        bg_hex = theme[bg]
        r = contrast(theme[fg], bg_hex)
        rows.append((name, fg, theme[fg], bg, bg_hex, round(r, 2), need, "pass" if r >= need else "FAIL"))
    return rows

def cvd_rows(theme, name):
    try:
        from colorspacious import cspace_convert
    except ImportError:
        return []
    import numpy as np
    keys = ["kind-shapes", "kind-number", "kind-text", "kind-any"]
    cols = np.array([hex_rgb(theme[k]) for k in keys])
    out = []
    for cond, sev in (("normal", 0), ("deuteranomaly", 100), ("protanomaly", 100), ("tritanomaly", 100)):
        if sev:
            sim = np.clip(cspace_convert(cols, {"name": "sRGB1+CVD", "cvd_type": cond, "severity": sev}, "sRGB1"), 0, 1)
        else:
            sim = cols
        ucs = cspace_convert(sim, "sRGB1", "CAM02-UCS")
        best = min(((float(np.linalg.norm(ucs[i] - ucs[j])), keys[i], keys[j])
                    for i, j in itertools.combinations(range(len(keys)), 2)))
        out.append((name, cond, round(best[0], 1), best[1], best[2]))
    return out

def main():
    tokens = {
        "$schema-note": "C19 Flow visual tokens. Colours as hex (8-digit hex = alpha). Sizes in px at 100 percent zoom.",
        "version": "1.0.0",
        "date": "2026-11-01",
        "color": {"dark": DARK, "light": LIGHT},
        "size": SIZE,
        "type": TYPE,
        "zoom": ZOOM,
        "kinds": KINDS,
    }
    (ROOT / "tokens.json").write_text(json.dumps(tokens, indent=2) + "\n", encoding="utf-8")

    css = ["/* Generated from tokens.json by tools/build_tokens.py. Do not edit by hand. */"]
    for theme, sel in ((DARK, ":root, .theme-dark"), (LIGHT, ".theme-light")):
        css.append(sel + " {")
        css += [f"  --{k}: {v};" for k, v in theme.items()]
        css.append("}")
    css.append(":root {")
    css += [f"  --{k}: {v}{'px' if isinstance(v, (int, float)) and not k.endswith(('opacity', 'factor', 'every', 'threshold', 'speed-px-per-s')) else ''};"
            for k, v in SIZE.items()]
    css.append("}")
    (ROOT / "mockups" / "tokens.css").write_text("\n".join(css) + "\n", encoding="utf-8")

    rows = run_checks(DARK, "dark") + run_checks(LIGHT, "light")
    md = ["| Theme | Foreground | | Background | | Ratio | Needed | Result |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {t} | {fg} | `{fh}` | {bg} | `{bh}` | {r} | {n} | {ok} |" for t, fg, fh, bg, bh, r, n, ok in rows]
    cv = cvd_rows(DARK, "dark") + cvd_rows(LIGHT, "light")
    md += ["", "| Theme | Vision | Smallest distance between data-kind colours (CAM02-UCS) | Closest pair |", "|---|---|---|---|"]
    md += [f"| {t} | {c} | {d} | {a} / {b} |" for t, c, d, a, b in cv]
    (HERE / "contrast.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    fails = [r for r in rows if r[-1] == "FAIL"]
    print(f"checks: {len(rows)}, fails: {len(fails)}")
    for f in fails:
        print("  FAIL", f)
    for c in cv:
        print("  cvd", c)

if __name__ == "__main__":
    main()
