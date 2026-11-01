"""Draw Flow mockups as SVG from tokens.json, using only rounded rectangles, lines, curves, text and
small outline icons (Tabler). Every number comes from tokens.json so the mockups match the spec.

Used by build_mockups.py. Coordinates are canvas units; `zoom` scales them to screen pixels.
"""
import json, math, pathlib, re, html
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "tokens.json").read_text(encoding="utf-8"))
S = TOK["size"]
T = TOK["type"]
Z = TOK["zoom"]
ICON_DIR = ROOT / "mockups" / "icons"

# ---------------------------------------------------------------- text measuring (IBM Plex Sans metrics)
_FONTS = {}
def _font(weight):
    if weight not in _FONTS:
        f = TTFont(str(ROOT / "mockups" / "fonts" / f"ibm-plex-sans-{weight}.woff2"))
        _FONTS[weight] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _FONTS[weight]

def text_width(s, size, weight=400):
    cmap, hm, upm = _font(weight)
    w = 0
    for ch in s:
        g = cmap.get(ord(ch)) or cmap.get(ord("n"))
        w += hm[g][0]
    return w / upm * size

def fit(s, size, weight, max_w):
    if text_width(s, size, weight) <= max_w:
        return s
    while s and text_width(s + "…", size, weight) > max_w:
        s = s[:-1]
    return s.rstrip() + "…"

def esc(s):
    return html.escape(str(s), quote=True)

# ---------------------------------------------------------------- colours
def rgba(hexstr, alpha=None):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    if alpha is not None:
        a = alpha
    return f"rgba({r},{g},{b},{a:.3f})"

# ---------------------------------------------------------------- icons
_ICON_CACHE = {}
def icon(name, x, y, size, color, stroke=1.75):
    """Tabler outline icon, scaled so that the 24 unit box becomes `size`."""
    if name not in _ICON_CACHE:
        src = (ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
        body = "".join(re.findall(r"<(?:path|circle|rect|line|polyline|polygon|ellipse)\b[^>]*/>", src))
        body = body.replace('<path stroke="none" d="M0 0h24v24H0z" fill="none"/>', "")
        _ICON_CACHE[name] = body
    k = size / 24
    sw = stroke / k
    return (f'<g transform="translate({x:.2f},{y:.2f}) scale({k:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{sw:.3f}" stroke-linecap="round" stroke-linejoin="round">{_ICON_CACHE[name]}</g>')

# ---------------------------------------------------------------- model helpers
class Theme:
    def __init__(self, name):
        self.name = name
        self.c = TOK["color"][name]
    def __getitem__(self, k):
        return self.c[k]

def node_height(n):
    rows = len(n.get("outputs", [])) + len(n.get("inputs", []))
    return S["node-header-height"] + 2 * S["node-body-padding-y"] + rows * S["node-row-height"]

def port_pos(n, side, i):
    """Canvas position of port i on side 'out' or 'in'. Outputs come first, then inputs."""
    rh, top = S["node-row-height"], S["node-header-height"] + S["node-body-padding-y"]
    if side == "out":
        return n["x"] + n["w"], n["y"] + top + i * rh + rh / 2
    row = len(n.get("outputs", [])) + i
    return n["x"], n["y"] + top + row * rh + rh / 2

# ---------------------------------------------------------------- primitives
def port_glyph(kind, cx, cy, theme, wired=True, size=None, ring=True):
    size = size or S["port-size"]
    col = theme[f"kind-{kind}"]
    fill = col if wired else theme["node"]
    sw = 1.5
    r = size / 2
    ring_el = ""
    out = []
    if kind == "shapes":
        if ring:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r + S["port-ring"]}" fill="{theme["node"]}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - (0 if wired else sw / 2)}" fill="{fill}" stroke="{col}" stroke-width="{0 if wired else sw}"/>')
    elif kind == "number":
        d = r * 1.18
        if ring:
            e = d + S["port-ring"] * 1.3
            out.append(f'<path d="M{cx} {cy - e} L{cx + e} {cy} L{cx} {cy + e} L{cx - e} {cy} Z" fill="{theme["node"]}"/>')
        dd = d - (0 if wired else sw / 2)
        out.append(f'<path d="M{cx} {cy - dd} L{cx + dd} {cy} L{cx} {cy + dd} L{cx - dd} {cy} Z" fill="{fill}" stroke="{col}" stroke-width="{0 if wired else sw}" stroke-linejoin="round"/>')
    elif kind == "text":
        s = size * 0.9
        if ring:
            e = s + S["port-ring"] * 2
            out.append(f'<rect x="{cx - e / 2}" y="{cy - e / 2}" width="{e}" height="{e}" rx="3" fill="{theme["node"]}"/>')
        ss = s - (0 if wired else sw)
        out.append(f'<rect x="{cx - ss / 2}" y="{cy - ss / 2}" width="{ss}" height="{ss}" rx="2" fill="{fill}" stroke="{col}" stroke-width="{0 if wired else sw}"/>')
    else:  # any: ring
        if ring:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r + S["port-ring"]}" fill="{theme["node"]}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 1}" fill="{theme["node"] if not wired else theme["node"]}" stroke="{col}" stroke-width="2"/>')
        if wired:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 3.2}" fill="{col}"/>')
    return "".join(out)

def wire_path(sx, sy, tx, ty):
    dx = tx - sx
    if dx >= 0:
        c = min(max(S["wire-curve-factor"] * abs(dx), S["wire-curve-min"]), S["wire-curve-max"])
    else:
        c = 80 + 0.25 * abs(ty - sy)
    return f"M{sx:.1f} {sy:.1f} C{sx + c:.1f} {sy:.1f}, {tx - c:.1f} {ty:.1f}, {tx:.1f} {ty:.1f}"

def wire(w, nodes, theme, zoom=1.0, faded=False):
    a, b = nodes[w["from"][0]], nodes[w["to"][0]]
    sx, sy = port_pos(a, "out", w["from"][1])
    tx, ty = port_pos(b, "in", w["to"][1])
    kind = a["outputs"][w["from"][1]]["kind"]
    col = theme[f"kind-{kind}"]
    d = wire_path(sx, sy, tx, ty)
    structure = w.get("structure", "item")
    state = w.get("state")
    minw = Z["wire-min-screen-width"] / zoom
    opacity = S["wire-opacity-dark"] if theme.name == "dark" else S["wire-opacity-light"]
    if zoom < Z["block-mode-below"]:
        return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{minw:.2f}" opacity="{Z["wire-opacity-below-30"]}"/>'
    if faded:
        opacity = S["wire-fade-opacity"]
    out = []
    if state == "selected":
        out.append(f'<path d="{d}" fill="none" stroke="{theme["selection"]}" stroke-width="{S["wire-selected-underlay"]}" opacity="0.28" stroke-linecap="round"/>')
        opacity = 1
    if state == "hover":
        opacity = 1
    extra = S["wire-hover-extra"] if state in ("hover", "selected") else 0
    if structure == "item":
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{max(S["wire-item"] + extra, minw):.2f}" opacity="{opacity}"/>')
    elif structure == "list":
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{max(S["wire-list"] + extra, minw):.2f}" opacity="{opacity}"/>')
    elif structure == "nested":
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{S["wire-nested-outer"] + extra}" opacity="{opacity}"/>')
        out.append(f'<path d="{d}" fill="none" stroke="{theme["canvas"]}" stroke-width="{S["wire-nested-gap"]}"/>')
    elif structure == "lazy":
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{S["wire-item"] + extra}" stroke-dasharray="{S["wire-lazy-dash"]}" opacity="{opacity}"/>')
    if state == "flowing":
        out.append(f'<path d="{d}" fill="none" stroke="{theme["text"]}" stroke-width="1.5" stroke-dasharray="{S["wire-flow-dash"]}" opacity="0.9"/>')
    return "".join(out)

def badge_state(kind, x, y, theme, size=None):
    s = size or S["state-badge"]
    g = S["state-badge-glyph"] * s / S["state-badge"]
    cx, cy = x + s / 2, y + s / 2
    spec = {
        "error": (theme["danger"], "alert-circle", theme["node"], True),
        "warning": (theme["warning"], "alert-triangle", theme["node"], True),
        "running": (theme["control"], "loader-2", theme["running"], False),
        "paused": (theme["accent-soft"], "player-pause", theme["paused"], False),
        "stale": (theme["control"], "clock-hour-4", theme["stale"], False),
        "disabled": (theme["control"], "ban", theme["text-muted"], False),
        "bypass": (theme["control"], "arrows-split", theme["text-muted"], False),
        "ran": (theme["control"], "check", theme["text-muted"], False),
        "breakpoint": (theme["danger"], None, None, True),
        "lineage": (theme["control"], "route", theme["text-muted"], False),
    }[kind]
    bg, ic, fg, solid = spec
    out = [f'<circle cx="{cx}" cy="{cy}" r="{s / 2}" fill="{bg}"/>']
    if kind == "breakpoint":
        out = [f'<circle cx="{cx}" cy="{cy}" r="{s / 2}" fill="{theme["control"]}"/>',
               f'<circle cx="{cx}" cy="{cy}" r="{s * 0.26}" fill="{theme["danger"]}"/>']
    elif kind == "error":
        out.append(f'<rect x="{cx - 0.9}" y="{cy - g * 0.38}" width="1.8" height="{g * 0.46}" rx="0.9" fill="{fg}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy + g * 0.3}" r="1.05" fill="{fg}"/>')
    elif kind == "warning":
        out.append(f'<rect x="{cx - 0.9}" y="{cy - g * 0.36}" width="1.8" height="{g * 0.42}" rx="0.9" fill="{fg}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy + g * 0.3}" r="1.05" fill="{fg}"/>')
    else:
        out.append(icon(ic, cx - g / 2, cy - g / 2, g, fg, 1.75))
    return "".join(out)

def count_badge_width(text):
    return text_width(text, T["badge"]["size"], 500) + 2 * S["count-badge-padding-x"]

def count_badge(text, right, cy, theme):
    w = count_badge_width(text)
    h = S["count-badge-height"]
    x = right - w
    return (f'<rect x="{x:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h}" rx="{S["count-badge-radius"]}" fill="{theme["badge"]}"/>'
            f'<text x="{x + w / 2:.1f}" y="{cy + 3.6:.1f}" text-anchor="middle" class="t-badge" fill="{theme["badge-text"]}">{esc(text)}</text>'), w

# ---------------------------------------------------------------- node
def node(n, theme, zoom=1.0):
    x, y, w = n["x"], n["y"], n["w"]
    h = node_height(n)
    R = S["node-radius"]
    HH = S["node-header-height"]
    state = n.get("state")
    states = n.get("badges", []) + ([state] if state and state not in ("selected",) else [])
    cat = theme[f"cat-{n.get('cat', 'shape')}"]
    out = [f'<g class="node" data-id="{esc(n["id"])}">']
    op = ""
    if state == "disabled":
        op = f' opacity="{theme["disabled-opacity"]}"'
    elif state == "bypass":
        op = f' opacity="{theme["bypass-opacity"]}"'
    out.append(f"<g{op}>")

    # ---- block mode (below 30 percent)
    if zoom < Z["block-mode-below"]:
        rr = max(R, 3 / zoom)
        border = theme["danger"] if state == "error" else rgba(cat, 0.55)
        bw = (2 if state in ("error", "selected") else 1) / zoom
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rr}" fill="{theme["node"]}" stroke="{border}" stroke-width="{bw}"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rr}" fill="{rgba(cat, 0.14)}"/>')
        strip = 4 / zoom
        out.append(f'<path d="M{x} {y + rr} a{rr} {rr} 0 0 1 {rr} {-rr} h{w - 2 * rr} a{rr} {rr} 0 0 1 {rr} {rr} v{strip - rr} h{-w} Z" fill="{cat}"/>')
        if n.get("selected"):
            o = 3 / zoom
            out.append(f'<rect x="{x - o}" y="{y - o}" width="{w + 2 * o}" height="{h + 2 * o}" rx="{rr + o}" fill="none" stroke="{theme["selection"]}" stroke-width="{2 / zoom}"/>')
        main = next((s for s in ("error", "warning", "running", "paused", "stale") if s in states), None)
        if main:
            gs = Z["state-glyph-screen-size"] / zoom
            out.append(badge_state(main, x + w / 2 - gs / 2, y + h / 2 - gs / 2, theme, size=gs))
        out.append("</g></g>")
        return "".join(out)

    full = zoom >= Z["full-detail-min"]
    # ---- shadow, body, header
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{R}" fill="{theme["node"]}" filter="url(#shadow-{theme.name})"/>')
    out.append(f'<path d="M{x} {y + R} a{R} {R} 0 0 1 {R} {-R} h{w - 2 * R} a{R} {R} 0 0 1 {R} {R} v{HH - R} h{-w} Z" fill="{theme["node-header"]}"/>')
    out.append(f'<line x1="{x}" y1="{y + HH}" x2="{x + w}" y2="{y + HH}" stroke="{theme["divider"]}" stroke-width="{S["node-divider"]}"/>')
    border = theme["node-border"]
    bw = S["node-border"]
    dash = ""
    if state == "error":
        border, bw = theme["danger"], 1.5
    elif state == "paused":
        border, bw, dash = theme["paused"], 1.5, ' stroke-dasharray="5 3"'
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{R}" fill="none" stroke="{border}" stroke-width="{bw}"{dash}/>')
    if state == "running":
        out.append(f'<rect x="{x + 1}" y="{y + HH - 1}" width="{(w - 2) * 0.62:.1f}" height="2" fill="{theme["accent-line"]}"/>')

    # ---- header content
    px = S["node-header-padding-x"]
    tile = S["node-icon-tile"]
    ty = y + (HH - tile) / 2
    title_size = T["node-title"]["size"] if full else Z["title-fixed-screen-size"] / zoom
    badges_w = len(states) * (S["state-badge"] + S["state-badge-gap"])
    if full:
        out.append(f'<rect x="{x + px}" y="{ty}" width="{tile}" height="{tile}" rx="{S["node-icon-tile-radius"]}" fill="{rgba(cat, 0.18)}"/>')
        out.append(icon(n.get("icon", "box"), x + px + (tile - S["node-icon"]) / 2, ty + (tile - S["node-icon"]) / 2, S["node-icon"], cat, S["node-icon-stroke"]))
        tx = x + px + tile + S["node-title-gap"]
        max_title = w - (tx - x) - px - badges_w
        title = fit(n["title"], title_size, 600, max_title)
        out.append(f'<text x="{tx}" y="{y + HH / 2 + 4.6}" class="t-title" fill="{theme["text-muted"] if state == "stale" else theme["text"]}">{esc(title)}'
                   + (f'<tspan class="t-sub" fill="{theme["text-subtle"]}" dx="6">{esc(n["subtitle"])}</tspan>' if n.get("subtitle") and text_width(title + "  " + n["subtitle"], 13, 600) < max_title else "")
                   + "</text>")
    else:
        # mid zoom: title at fixed screen size, no icon tile, category as small square
        sq = 8
        out.append(f'<rect x="{x + px}" y="{y + HH / 2 - sq / 2}" width="{sq}" height="{sq}" rx="2" fill="{cat}"/>')
        tx = x + px + sq + 6
        title = fit(n["title"], title_size, 600, w - (tx - x) - px - badges_w)
        out.append(f'<text x="{tx}" y="{y + HH / 2 + title_size * 0.36}" font-family="IBM Plex Sans" font-weight="600" font-size="{title_size:.2f}" fill="{theme["text"]}">{esc(title)}</text>')
    bx = x + w - px - S["state-badge"]
    for s in reversed(states):
        out.append(badge_state(s, bx, y + (HH - S["state-badge"]) / 2, theme))
        bx -= S["state-badge"] + S["state-badge-gap"]

    # ---- rows
    rh = S["node-row-height"]
    top = y + HH + S["node-body-padding-y"]
    inset = S["node-port-label-inset"]
    for i, p in enumerate(n.get("outputs", [])):
        cy = top + i * rh + rh / 2
        if full:
            right = x + w - inset
            if p.get("count"):
                b, bwid = count_badge(p["count"], right, cy, theme)
                out.append(b)
                right -= bwid + 6
            col = theme["danger"] if p.get("failed") else theme["text-muted"]
            out.append(f'<text x="{right}" y="{cy + 3.8}" text-anchor="end" class="t-port" fill="{col}">{esc(p["name"])}</text>')
        out.append(port_glyph(p["kind"], x + w, cy, theme, wired=p.get("wired", True), size=None if full else 6 / zoom, ring=full))
    n_out = len(n.get("outputs", []))
    for i, p in enumerate(n.get("inputs", [])):
        cy = top + (n_out + i) * rh + rh / 2
        if full:
            label = p["name"]
            lx = x + inset
            lw = text_width(label, 11, 400)
            err = p.get("error")
            out.append(f'<text x="{lx}" y="{cy + 3.8}" class="t-port" fill="{theme["danger"] if err else theme["text-muted"]}">{esc(label)}</text>')
            if p.get("slider") and not p.get("wired"):
                sl = p["slider"]
                fx = lx + lw + 10
                vtxt = f'{sl["value"]:g} {sl.get("unit", "")}'.strip()
                vw = text_width(vtxt, 11, 500)
                tx1 = x + w - inset - vw - 10
                frac = (sl["value"] - sl["min"]) / (sl["max"] - sl["min"])
                kx = fx + (tx1 - fx) * frac
                out.append(f'<rect x="{fx}" y="{cy - 1.5}" width="{tx1 - fx}" height="3" rx="1.5" fill="{theme["control-hover"]}"/>')
                out.append(f'<rect x="{fx}" y="{cy - 1.5}" width="{kx - fx}" height="3" rx="1.5" fill="{theme["accent-line"]}"/>')
                out.append(f'<circle cx="{kx}" cy="{cy}" r="5.5" fill="{theme["text"]}" stroke="{theme["node"]}" stroke-width="2"/>')
                out.append(f'<text x="{x + w - inset}" y="{cy + 3.8}" text-anchor="end" class="t-value" fill="{theme["text"]}">{esc(vtxt)}</text>')
            elif "value" in p and not p.get("wired"):
                fx = lx + lw + 8
                fw = x + w - inset - fx
                fh = S["inline-field-height"]
                focus = p.get("focus")
                out.append(f'<rect x="{fx}" y="{cy - fh / 2}" width="{fw}" height="{fh}" rx="{S["inline-field-radius"]}" fill="{theme["control"]}"'
                           + (f' stroke="{theme["focus-ring"]}" stroke-width="1.5"' if focus else "") + "/>")
                val = fit(str(p["value"]), 11, 500, fw - 14)
                anchor = "start" if p.get("kind") == "text" else "end"
                vx = fx + 7 if anchor == "start" else fx + fw - 7
                out.append(f'<text x="{vx}" y="{cy + 3.8}" text-anchor="{anchor}" class="t-value" fill="{theme["text"]}">{esc(val)}</text>')
                if p.get("unit"):
                    out.append(f'<text x="{fx + 7}" y="{cy + 3.8}" class="t-port" fill="{theme["text-subtle"]}">{esc(p["unit"])}</text>')
                if focus:
                    cxp = vx + 1.5
                    out.append(f'<line x1="{cxp}" y1="{cy - 6}" x2="{cxp}" y2="{cy + 6}" stroke="{theme["accent-line"]}" stroke-width="1.2"/>')
        out.append(port_glyph(p["kind"], x, cy, theme, wired=p.get("wired", False), size=None if full else 6 / zoom, ring=full))
    out.append("</g>")

    # ---- selection outline
    if n.get("selected"):
        o = S["selection-offset"] + 1
        out.append(f'<rect x="{x - o}" y="{y - o}" width="{w + 2 * o}" height="{h + 2 * o}" rx="{R + o}" fill="none" stroke="{theme["selection"]}" stroke-width="{S["selection-width"]}"/>')

    # ---- error tray
    if state == "error" and n.get("message") and full:
        lines = n["message"] if isinstance(n["message"], list) else [n["message"]]
        pad = S["error-tray-padding"]
        lh = T["error-message"]["line"]
        th = pad * 2 + lh * len(lines) + (lh if n.get("action") else 0)
        ty0 = y + h + 4
        out.append(f'<rect x="{x}" y="{ty0}" width="{w}" height="{th}" rx="{R}" fill="{theme["node"]}"/>')
        out.append(f'<rect x="{x}" y="{ty0}" width="{w}" height="{th}" rx="{R}" fill="{theme["danger-soft"]}" stroke="{rgba(theme["danger"], 0.55)}" stroke-width="1"/>')
        out.append(icon("alert-circle", x + pad, ty0 + pad + 1, 13, theme["danger"], 1.75))
        for k, line in enumerate(lines):
            out.append(f'<text x="{x + pad + 19}" y="{ty0 + pad + 11 + k * lh}" class="t-msg" fill="{theme["text"]}">{esc(fit(line, 11, 400, w - pad * 2 - 19))}</text>')
        if n.get("action"):
            out.append(f'<text x="{x + pad + 19}" y="{ty0 + pad + 11 + len(lines) * lh}" class="t-msg-link" fill="{theme["accent"]}">{esc(n["action"])}</text>')
    out.append("</g>")
    return "".join(out)

def group(g, theme, zoom=1.0):
    col = theme[g.get("color", "group-2")]
    R = S["group-radius"]
    out = [f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" rx="{R}" fill="{rgba(col, 0.08 if theme.name == "dark" else 0.10)}" stroke="{rgba(col, 0.35)}" stroke-width="{S["group-border"] / max(zoom, 0.5)}"/>']
    size = T["group-title"]["size"] if zoom >= Z["full-detail-min"] else Z["group-title-fixed-screen-size"] / zoom
    k = 1 if zoom >= Z["full-detail-min"] else 1 / zoom
    if zoom < Z["block-mode-below"]:
        # blocks: the title sits just above the frame so it never covers nodes
        ty, tx = g["y"] - 5 * k, g["x"] + 2 * k
    else:
        ty, tx = g["y"] + 6 * k + size * 0.95, g["x"] + S["group-padding"] * (1 if k == 1 else 0.75 * k)
    out.append(f'<text x="{tx}" y="{ty}" font-family="IBM Plex Sans" font-weight="600" font-size="{size:.2f}" fill="{col}">{esc(g["title"])}</text>')
    return "".join(out)

def defs(theme):
    sh = theme["shadow-node"].split()
    dy = float(sh[1].rstrip("px")); blur = float(sh[2].rstrip("px")); color = sh[3]
    return (f'<defs><filter id="shadow-{theme.name}" x="-20%" y="-20%" width="140%" height="160%">'
            f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur / 2}" flood-color="{rgba(color)}"/></filter>'
            f'<pattern id="dots-{theme.name}" width="{S["canvas-dot-spacing"]}" height="{S["canvas-dot-spacing"]}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{S["canvas-dot-spacing"] / 2}" cy="{S["canvas-dot-spacing"] / 2}" r="{S["canvas-dot-size"] / 2 + 0.25}" fill="{theme["canvas-dot"]}"/></pattern></defs>')

def canvas(model, theme, width, height, zoom=1.0, origin=(0, 0), dots=True, extra_top="", fade_unrelated=False):
    """Full canvas SVG: background dots, groups, wires (under nodes), nodes."""
    nodes = {n["id"]: n for n in model["nodes"]}
    ox, oy = origin
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" class="flow theme-{theme.name}">',
           defs(theme), f'<rect width="{width}" height="{height}" fill="{theme["canvas"]}"/>']
    if dots and zoom >= Z["dots-hidden-below"]:
        sp = S["canvas-dot-spacing"] * zoom
        out.append(f'<pattern id="dz-{theme.name}-{int(zoom*100)}" width="{sp}" height="{sp}" patternUnits="userSpaceOnUse" x="{(-ox * zoom) % sp}" y="{(-oy * zoom) % sp}">'
                   f'<circle cx="{sp / 2}" cy="{sp / 2}" r="{max(S["canvas-dot-size"] / 2 * zoom, 0.6) + 0.2}" fill="{theme["canvas-dot"]}"/></pattern>')
        out.append(f'<rect width="{width}" height="{height}" fill="url(#dz-{theme.name}-{int(zoom*100)})"/>')
    elif dots:
        sp = S["canvas-dot-spacing"] * S["canvas-dot-major-every"] * zoom
        out.append(f'<pattern id="dM-{theme.name}" width="{sp}" height="{sp}" patternUnits="userSpaceOnUse"><circle cx="{sp / 2}" cy="{sp / 2}" r="0.9" fill="{theme["canvas-dot-major"]}"/></pattern>')
        out.append(f'<rect width="{width}" height="{height}" fill="url(#dM-{theme.name})"/>')
    out.append(f'<g transform="scale({zoom}) translate({-ox},{-oy})">')
    for g in model.get("groups", []):
        out.append(group(g, theme, zoom))
    sel = {n["id"] for n in model["nodes"] if n.get("selected")}
    for w in model.get("wires", []):
        related = w["from"][0] in sel or w["to"][0] in sel
        out.append(wire(w, nodes, theme, zoom, faded=fade_unrelated and not related))
    for n in model["nodes"]:
        out.append(node(n, theme, zoom))
    out.append(extra_top)
    out.append("</g></svg>")
    return "".join(out)

def minimap(model, theme, view_rect, x, y, w=None, h=None):
    w = w or S["minimap-width"]; h = h or S["minimap-height"]
    xs = [n["x"] for n in model["nodes"]] + [n["x"] + n["w"] for n in model["nodes"]]
    ys = [n["y"] for n in model["nodes"]] + [n["y"] + node_height(n) for n in model["nodes"]]
    vx, vy, vw, vh = view_rect
    x0, x1 = min(xs + [vx]) - 40, max(xs + [vx + vw]) + 40
    y0, y1 = min(ys + [vy]) - 40, max(ys + [vy + vh]) + 40
    pad = 10
    k = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad - 14) / (y1 - y0))
    ox = x + pad + ((w - 2 * pad) - (x1 - x0) * k) / 2
    oy = y + pad + 14 + ((h - 2 * pad - 14) - (y1 - y0) * k) / 2
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{S["minimap-radius"]}" fill="{theme["minimap"]}" stroke="{theme["border"]}" filter="url(#shadow-{theme.name})"/>',
           f'<text x="{x + 10}" y="{y + 16}" class="t-small" fill="{theme["text-subtle"]}">Map</text>',
           icon("x", x + w - 22, y + 5, 14, theme["text-subtle"], 1.75)]
    for g in model.get("groups", []):
        col = theme[g.get("color", "group-2")]
        out.append(f'<rect x="{ox + (g["x"] - x0) * k:.1f}" y="{oy + (g["y"] - y0) * k:.1f}" width="{g["w"] * k:.1f}" height="{g["h"] * k:.1f}" rx="2" fill="{rgba(col, 0.12)}"/>')
    for n in model["nodes"]:
        col = theme["danger"] if n.get("state") == "error" else (theme["selection"] if n.get("selected") else theme["minimap-node"])
        out.append(f'<rect x="{ox + (n["x"] - x0) * k:.1f}" y="{oy + (n["y"] - y0) * k:.1f}" width="{max(n["w"] * k, 1.5):.1f}" height="{max(node_height(n) * k, 1.5):.1f}" rx="1" fill="{col}"/>')
    out.append(f'<rect x="{ox + (vx - x0) * k:.1f}" y="{oy + (vy - y0) * k:.1f}" width="{vw * k:.1f}" height="{vh * k:.1f}" rx="2" fill="{theme["minimap-viewport-fill"]}" stroke="{theme["minimap-viewport"]}" stroke-width="1"/>')
    return "".join(out)

STYLE = """
@font-face { font-family: 'IBM Plex Sans'; font-weight: 400; src: url('fonts/ibm-plex-sans-400.woff2') format('woff2'); }
@font-face { font-family: 'IBM Plex Sans'; font-weight: 500; src: url('fonts/ibm-plex-sans-500.woff2') format('woff2'); }
@font-face { font-family: 'IBM Plex Sans'; font-weight: 600; src: url('fonts/ibm-plex-sans-600.woff2') format('woff2'); }
@font-face { font-family: 'Cascadia Mono'; font-weight: 400; src: url('fonts/cascadia-mono-400.woff2') format('woff2'); }
svg.flow text, .ui { font-family: 'IBM Plex Sans', sans-serif; }
.t-title { font-size: 13px; font-weight: 600; }
.t-sub { font-size: 11px; font-weight: 400; }
.t-port { font-size: 11px; font-weight: 400; }
.t-value { font-size: 11px; font-weight: 500; font-variant-numeric: tabular-nums; }
.t-badge { font-size: 10px; font-weight: 500; font-variant-numeric: tabular-nums; }
.t-msg { font-size: 11px; font-weight: 400; }
.t-msg-link { font-size: 11px; font-weight: 500; }
.t-small { font-size: 11px; font-weight: 500; }
"""


def hover_card(n, theme, shapes, caption, footer):
    """Card shown above a node on hover: title, plan thumbnail, one line of facts. Drawn in canvas units."""
    W, R = S["hover-card-width"], S["hover-card-radius"]
    TH = S["hover-card-thumb-height"]
    x = n["x"] + n["w"] / 2 - W / 2
    h = 30 + TH + 30
    y = n["y"] - h - 10
    out = [f'<g filter="url(#shadow-{theme.name})"><rect x="{x}" y="{y}" width="{W}" height="{h}" rx="{R}" fill="{theme["overlay"]}" stroke="{theme["border-strong"]}"/>',
           f'<path d="M{x + W / 2 - 7} {y + h - 0.5} L{x + W / 2} {y + h + 7} L{x + W / 2 + 7} {y + h - 0.5} Z" fill="{theme["overlay"]}" stroke="{theme["border-strong"]}"/>',
           f'<rect x="{x + W / 2 - 8}" y="{y + h - 2}" width="16" height="2.5" fill="{theme["overlay"]}"/></g>',
           f'<text x="{x + 10}" y="{y + 19}" class="t-title" fill="{theme["text"]}">{esc(caption)}</text>',
           f'<rect x="{x + 8}" y="{y + 28}" width="{W - 16}" height="{TH}" rx="6" fill="{theme["canvas"]}"/>']
    # fit shapes into the thumbnail
    pts = [p for poly in shapes for p in poly["pts"]]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = min((W - 40) / (x1 - x0), (TH - 20) / (y1 - y0))
    ox = x + 8 + (W - 16 - (x1 - x0) * k) / 2
    oy = y + 28 + (TH - (y1 - y0) * k) / 2
    for poly in shapes:
        d = " ".join(f"{'M' if i == 0 else 'L'}{ox + (px - x0) * k:.1f} {oy + (py - y0) * k:.1f}" for i, (px, py) in enumerate(poly["pts"])) + " Z"
        col = theme[poly.get("color", "kind-shapes")]
        fill = rgba(col, 0.16) if poly.get("fill") else "none"
        dash = ' stroke-dasharray="3 3"' if poly.get("dashed") else ""
        out.append(f'<path d="{d}" fill="{fill}" stroke="{col if not poly.get("muted") else theme["text-subtle"]}" stroke-width="1.25"{dash}/>')
    out.append(f'<text x="{x + 10}" y="{y + 28 + TH + 19}" class="t-port" fill="{theme["text-muted"]}">{esc(footer)}</text>')
    return "".join(out)
