"""Build the C20 mockups: a parametric object in the drawing, the window designer, and the custom window in use.

Uses the C19 tokens (tools/c19-tokens.json, mockups/tokens.css) and chrome (mockups/chrome.css), plus mockups/c20.css.
Run: python3 build_c20.py && node render.js
"""
import json, math, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "mockups"
TOK = json.loads((ROOT / "tools" / "c19-tokens.json").read_text(encoding="utf-8"))
ICONS = OUT / "icons"
MANIFEST = []

def esc(s):
    return html.escape(str(s), quote=True)

def rgba(hexstr, a):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"

def ic(name, size=16, color="currentColor", stroke=1.75):
    src = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    src = src.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    src = src.replace('stroke-width="2"', f'stroke-width="{stroke}"').replace('stroke="currentColor"', f'stroke="{color}"')
    return f'<span class="icon" style="width:{size}px;height:{size}px">{src}</span>'

def page(name, body, theme, w=1440, h=900, title=""):
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{esc(title or name)}</title>
<link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="chrome.css"><link rel="stylesheet" href="c20.css">
<style>html,body{{width:{w}px;height:{h}px;overflow:hidden}}</style></head>
<body class="theme-{theme}">{body}</body></html>
"""
    (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
    MANIFEST.append({"html": f"{name}.html", "png": f"png/{name}.png", "width": w, "height": h})

# ------------------------------------------------------------------ the site plan (SVG)
SCALE = 4.0  # px per metre in the plan

def poly(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

def inset_rect(x0, y0, x1, y1, d):
    return x0 + d, y0 + d, x1 - d, y1 - d

def chamfer_rect(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]

def courtyard(block, setback=6, depth=14, cham=6):
    x0, y0, x1, y1 = inset_rect(*block, setback * SCALE)
    outer = chamfer_rect(x0, y0, x1, y1, cham * SCALE)
    ix0, iy0, ix1, iy1 = inset_rect(x0, y0, x1, y1, depth * SCALE)
    inner = chamfer_rect(ix0, iy0, ix1, iy1, 2 * SCALE)
    return outer, inner, (x0, y0, x1, y1), (ix0, iy0, ix1, iy1)

def plan_svg(c, w, h, selected=True, handles=True, ghost_depth=None, hover_tip=True):
    road = c["control"]
    kerb = c["border-strong"]
    bfill = rgba(c["text-muted"], 0.10)
    bline = c["text-subtle"]
    pfill = rgba(c["cat-shape"], 0.13)
    pline = c["cat-shape"]
    sel = c["selection"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           f'<defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{c["canvas-dot"]}" stroke-width="1"/></pattern></defs>',
           f'<rect width="{w}" height="{h}" fill="{c["canvas"]}"/><rect width="{w}" height="{h}" fill="url(#grid)"/>']
    # roads
    xs = [(-10, 340), (380, 740), (780, 1100)]
    ys = [(-10, 300), (340, 620), (660, 900)]
    for rx in (340, 740):
        out.append(f'<rect x="{rx}" y="-10" width="40" height="{h + 20}" fill="{road}"/>')
        out.append(f'<line x1="{rx + 20}" y1="0" x2="{rx + 20}" y2="{h}" stroke="{c["text-subtle"]}" stroke-width="1" stroke-dasharray="10 10" opacity="0.5"/>')
    for ry in (300, 620):
        out.append(f'<rect x="-10" y="{ry}" width="{w + 20}" height="40" fill="{road}"/>')
        out.append(f'<line x1="0" y1="{ry + 20}" x2="{w}" y2="{ry + 20}" stroke="{c["text-subtle"]}" stroke-width="1" stroke-dasharray="10 10" opacity="0.5"/>')
    blocks = {}
    for i, (bx0, bx1) in enumerate(xs):
        for j, (by0, by1) in enumerate(ys):
            b = (bx0 + 8, by0 + 8, bx1 - 8, by1 - 8)
            blocks[(i, j)] = b
            out.append(f'<rect x="{b[0]}" y="{b[1]}" width="{b[2] - b[0]}" height="{b[3] - b[1]}" rx="4" fill="none" stroke="{kerb}" stroke-width="1"/>')
    # plain buildings (not parametric)
    plain = [(16, 16, 150, 120), (170, 16, 330, 120), (16, 150, 120, 290), (150, 170, 330, 290),
             (16, 350, 160, 470), (16, 500, 160, 610), (190, 350, 330, 610),
             (790, 670, 940, 790), (960, 670, 1080, 790), (16, 670, 330, 760)]
    for (x0, y0, x1, y1) in plain:
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="2" fill="{bfill}" stroke="{bline}" stroke-width="1"/>')
    # trees along roads
    for k in range(0, int(h), 46):
        for tx in (352, 368, 752, 768):
            pass
    for k in range(20, int(w), 52):
        for ty in (308, 332, 628, 652):
            out.append(f'<circle cx="{k}" cy="{ty}" r="4.5" fill="{rgba(c["cat-value"], 0.18)}" stroke="{c["cat-value"]}" stroke-width="1" opacity="0.8"/>')
    # parametric instances (same definition) in other blocks
    labels = {(1, 0): "A1", (2, 0): "A2", (2, 1): "A4", (1, 2): "A5"}
    for key, lab in labels.items():
        outer, inner, _, _ = courtyard(blocks[key], setback=5 if lab != "A5" else 6, depth=12 if lab in ("A1", "A5") else 14)
        out.append(f'<path d="M{poly(outer)} Z M{poly(inner)} Z" fill="{pfill}" fill-rule="evenodd" stroke="{pline}" stroke-width="1"/>')
        b = blocks[key]
        out.append(f'<text x="{b[0] + 10}" y="{b[1] + 18}" font-size="11" font-weight="600" fill="{pline}">{lab}</text>')
    # the selected instance A3 in block (1, 1)
    b = blocks[(1, 1)]
    outer, inner, orect, irect = courtyard(b, setback=6, depth=14)
    stroke = sel if selected else pline
    fill = rgba(c["accent-fill"], 0.07) if selected else pfill
    out.append(f'<path d="M{poly(outer)} Z M{poly(inner)} Z" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{1.75 if selected else 1}"/>')
    if ghost_depth:
        _, inner2, _, _ = courtyard(b, setback=6, depth=ghost_depth)
        out.append(f'<path d="M{poly(inner2)} Z" fill="none" stroke="{sel}" stroke-width="1.25" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{b[0] + 10}" y="{b[1] + 18}" font-size="11" font-weight="600" fill="{sel if selected else pline}">A3</text>')
    if selected and handles:
        hc = c["overlay"]
        x0, y0, x1, y1 = orect
        mx = (x0 + x1) / 2
        # setback dimension from plot edge to footprint edge (top)
        out.append(f'<line x1="{mx - 40}" y1="{b[1]}" x2="{mx - 40}" y2="{y0}" stroke="{sel}" stroke-width="1"/>')
        out += [f'<line x1="{mx - 44}" y1="{yy}" x2="{mx - 36}" y2="{yy}" stroke="{sel}" stroke-width="1"/>' for yy in (b[1], y0)]
        out.append(f'<rect x="{mx - 84}" y="{(b[1] + y0) / 2 - 9}" width="38" height="18" rx="4" fill="{hc}" stroke="{c["border-strong"]}"/><text x="{mx - 65}" y="{(b[1] + y0) / 2 + 4}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{c["text"]}">6.0 m</text>')
        # setback grip: arrow on the footprint edge
        out.append(f'<path d="M{mx} {y0 - 9} l7 9 h-14 Z" fill="{hc}" stroke="{sel}" stroke-width="1.5" stroke-linejoin="round"/>')
        # courtyard depth grip: diamond on the inner top edge
        ix0, iy0, ix1, iy1 = irect
        out.append(f'<path d="M{mx} {iy0 - 7} l7 7 l-7 7 l-7 -7 Z" fill="{hc}" stroke="{sel}" stroke-width="1.5"/>')
        out.append(f'<line x1="{mx + 14}" y1="{y0}" x2="{mx + 14}" y2="{iy0}" stroke="{sel}" stroke-width="1" stroke-dasharray="3 3"/>')
        out.append(f'<rect x="{mx + 20}" y="{(y0 + iy0) / 2 - 9}" width="44" height="18" rx="4" fill="{hc}" stroke="{c["border-strong"]}"/><text x="{mx + 42}" y="{(y0 + iy0) / 2 + 4}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{c["text"]}">14 m</text>')
        # chamfer grip on the top-left corner
        cx, cy = x0 + 3 * SCALE, y0 + 3 * SCALE
        out.append(f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="{hc}" stroke="{sel}" stroke-width="1.5"/>')
        # floors grip: vertical double arrow near the top-right corner
        fx, fy = x1 + 2, y0 + 30
        out.append(f'<rect x="{fx - 11}" y="{fy - 20}" width="22" height="40" rx="11" fill="{hc}" stroke="{sel}" stroke-width="1.5"/>')
        out.append(f'<path d="M{fx} {fy - 13} l-5 6 h10 Z M{fx} {fy + 13} l-5 -6 h10 Z" fill="{sel}"/>')
        out.append(f'<rect x="{fx + 16}" y="{fy - 9}" width="44" height="18" rx="4" fill="{hc}" stroke="{c["border-strong"]}"/><text x="{fx + 38}" y="{fy + 4}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{c["text"]}">8 fl</text>')
        # rotation grip: arc at the bottom-left corner
        rx, ry = x0 - 12, y1 + 12
        out.append(f'<path d="M{rx + 2} {ry - 22} A22 22 0 0 0 {rx + 22} {ry - 2}" fill="none" stroke="{sel}" stroke-width="1.25" stroke-dasharray="3 3"/>')
        out.append(f'<circle cx="{rx}" cy="{ry}" r="7" fill="{hc}" stroke="{sel}" stroke-width="1.5"/>')
        out.append(f'<path d="M{rx - 3} {ry + 1} a3.5 3.5 0 1 1 3 3" fill="none" stroke="{sel}" stroke-width="1.3" stroke-linecap="round"/>')
        if hover_tip:
            tx, ty = mx + 12, y0 - 42
            out.append(f'<rect x="{tx}" y="{ty}" width="196" height="24" rx="6" fill="{c["text"]}"/><text x="{tx + 10}" y="{ty + 16}" font-size="11" font-weight="600" fill="{c["canvas"]}">Front setback 6.0 m · drag or type</text>')
    out.append("</svg>")
    return "".join(out), b, orect

# ------------------------------------------------------------------ shared chrome
RAIL = ["vector", "vector-bezier-2", "line-dashed", "polygon", "box", "shape", "ruler-measure", "resize",
        "layout-grid", "route", "stack", "lasso", "crosshair", "tag", "table", "calculator", "typography",
        "building-community", "grid-dots", "selector", "versions", "database", "photo", "settings"]

def appbar(c, title):
    menus = "".join(f'<span class="menu">{m}</span>' for m in "File Edit View Map Draw Points Curves Regions Massing Transform Blocks Annotate Analyse Help".split())
    return f"""<div class="appbar"><span class="brand"><span class="dot">{ic('building-community', 13, c['text-on-accent'])}</span>Urbanto Studio</span>{menus}
    <span class="title"><b>{esc(title)}</b> · edited</span>
    <span class="appright"><span class="pill">{ic('layout-grid', 14)} Massing {ic('chevron-down', 14)}</span><span class="tb-btn">{ic('search', 16)}</span></span></div>"""

def rail(on=4):
    return '<div class="rail">' + "".join(f'<span class="tool {"on" if i == on else ""}">{ic(n, 18)}</span>' + ("<hr>" if i in (7, 15) else "") for i, n in enumerate(RAIL)) + "</div>"

def status(c, extra="Selected: Courtyard block A3"):
    return f"""<div class="status"><span class="t">E</span> 1,412.0 <span class="t">N</span> 3,861.5 <span class="t">m</span><span>{esc(extra)}</span><span class="spacer"></span>
    <span class="group"><span class="on">OSNAP</span><span>ORTHO</span><span>POLAR</span><span>SNAP</span><span class="on">TRACK</span></span>
    <span>Scale 1:500</span><span>Grid: north</span></div>"""

def kdot(c, kind):
    return f'<span class="k" style="background:{c["kind-" + kind]}"></span>'

def slider_ctl(val, frac, unit=""):
    return (f'<span class="ctl slider"><span class="mini"><i style="width:{frac * 100:.0f}%"></i><b style="left:{frac * 100:.0f}%"></b></span>'
            f'<span class="num">{esc(val)}</span>{f"<span class=unit>{esc(unit)}</span>" if unit else ""}</span>')

def inspector(c, depth=14):
    tile = f'<span class="tile" style="background:{rgba(c["cat-shape"], 0.18)}">{ic("cube", 16, c["cat-shape"])}</span>'
    return f"""<div class="right">
  <div class="insp-head">{tile}<div><div class="name">Courtyard block · A3</div><div class="kind">Parametric · v3 · 5 in drawing</div></div>
    <span style="margin-left:auto" class="tb-btn">{ic('dots', 16)}</span></div>
  <div class="tabs" style="padding-top:4px"><span class="on">Parameters</span><span>Outputs</span><span>Definition</span></div>
  <div class="panel-body" style="gap:8px">
    <div style="display:flex;gap:6px"><span class="select">{ic('bookmark', 14)} Mid-rise default <span style="color:var(--text-subtle);margin-left:6px">changed</span><span class="chev">{ic('chevron-down', 14)}</span></span><span class="tb-btn">{ic('device-floppy', 16)}</span><span class="tb-btn">{ic('refresh', 16)}</span></div>
    <div class="group-h">{ic('chevron-down', 14)} Massing <span class="count">3</span><span class="act">{ic('app-window', 14)}</span></div>
    <div class="prop2"><span class="mod"></span><label>Floors</label>{slider_ctl("8", 0.45)}</div>
    <div class="prop2"><span></span><label>Floor height</label><span class="ctl"><span class="num" style="text-align:left">3.2</span><span class="unit">m</span></span></div>
    <div class="prop2"><span></span><label>Roof</label><span class="ctl">Flat<span class="chev">{ic('chevron-down', 14)}</span></span></div>
    <div class="group-h">{ic('chevron-down', 14)} Setbacks <span class="count">3</span></div>
    <div class="prop2"><span class="mod"></span><label>Front</label><span class="ctl"><span class="num" style="text-align:left">6.0</span><span class="unit">m</span><span class="chev">{ic('link', 14)}</span></span></div>
    <div class="prop2"><span></span><label>Side, rear</label><span class="ctl"><span class="num" style="text-align:left">4.0</span><span class="unit">m</span></span></div>
    <div class="group-h">{ic('chevron-down', 14)} Courtyard <span class="count">2</span></div>
    <div class="prop2"><span class="{"mod" if depth != 14 else ""}"></span><label>Depth</label>{slider_ctl(str(depth), 0.55 if depth == 14 else 0.68, "m")}</div>
    <div class="prop2"><span></span><label>Corners</label><span class="segs" style="height:28px"><span>Square</span><span class="on">Chamfer</span><span>Round</span></span></div>
    <div class="group-h">{ic('chevron-right', 14)} Use mix <span class="count">4</span></div>
    <div class="group-h" style="margin-bottom:4px">{ic('chevron-down', 14)} Results <span class="count">live</span></div>
    <div class="outputs"><span>GFA</span><b>18,420 m²</b><span>Plot ratio</span><b>3.1</b><span>Homes</span><b>164</b><span>Run time</span><b>4 ms</b></div>
    <div style="display:flex;gap:8px;margin-top:6px"><span class="btn">{ic('app-window', 14)} Open window</span><span class="btn ghost">{ic('route', 14)} Edit flow</span></div>
    <div style="display:flex;gap:8px"><span class="btn ghost">{ic('box', 14)} Bake to shapes</span><span class="btn ghost">{ic('unlink', 14)} Make unique</span></div>
  </div></div>"""

def popover(c, x, y):
    tile = f'<span class="tile" style="background:{rgba(c["cat-shape"], 0.18)}">{ic("cube", 14, c["cat-shape"])}</span>'
    return f"""<div class="popover" style="left:{x}px;top:{y}px">
  <div class="ph">{tile}<div><div class="name">Courtyard block</div><div class="sub">A3 · 4 pinned parameters</div></div><span style="margin-left:auto" class="tb-btn">{ic('pin', 15)}</span></div>
  <div class="pb">
    <div class="prow"><label>Floors</label><span class="val">8</span><div class="track"><span class="rail"></span><span class="fill" style="width:45%"></span><span class="knob" style="left:45%"></span></div></div>
    <div class="prow"><label>Front setback</label><span class="stepper"><span>{ic('minus', 12)}</span><b>6.0 m</b><span>{ic('plus', 12)}</span></span></div>
    <div class="prow"><label>Courtyard depth</label><span class="val">14<span class="u">m</span></span><div class="track"><span class="rail"></span><span class="fill" style="width:55%"></span><span class="knob" style="left:55%"></span></div></div>
    <div class="field"><label>Use</label><span class="segs"><span class="on">Homes</span><span>Mixed</span><span>Office</span></span></div>
  </div>
  <div class="pf"><span class="select">{ic('bookmark', 13)} Mid-rise default<span class="chev">{ic('chevron-down', 13)}</span></span><span class="btn sm primary">{ic('app-window', 13, c['text-on-accent'])} Window</span></div>
</div>"""

def legend(c):
    return (f'<div class="legend"><span><svg width="18" height="12"><rect x="1" y="1" width="16" height="10" rx="2" fill="{rgba(c["cat-shape"], 0.13)}" stroke="{c["cat-shape"]}"/></svg>Parametric: Courtyard block (5)</span>'
            f'<span><svg width="18" height="12"><rect x="1" y="1" width="16" height="10" rx="2" fill="{rgba(c["text-muted"], 0.10)}" stroke="{c["text-subtle"]}"/></svg>Plain shapes</span>'
            f'<span><svg width="18" height="12"><rect x="1" y="1" width="16" height="10" rx="2" fill="{rgba(c["accent-fill"], 0.10)}" stroke="{c["selection"]}" stroke-width="1.5"/></svg>Selected</span></div>')

def viewbar(c, mode="Plan"):
    return f"""<div class="viewbar"><span class="crumb">{ic('map', 14)} <b>Site plan</b></span><span class="tb-sep"></span>
  <span class="seg" style="height:26px"><span class="on">{mode}</span><span>3D</span></span><span class="tb-sep"></span>
  <span class="tb-btn">{ic('arrows-move', 16)}</span><span class="tb-btn">{ic('rotate', 16)}</span><span class="tb-btn">{ic('focus-2', 16)}</span>
  <span class="spacer"></span><span class="tb-btn">{ic('stack-2', 16)} Layers</span><span class="zoom"><span>{ic('minus', 14)}</span><span class="val">1:500</span><span>{ic('plus', 14)}</span></span></div>"""

# ------------------------------------------------------------------ page 1: object selected in the drawing
def build_object(theme):
    c = TOK["color"][theme]
    vw, vh = 1440 - 72 - 300, 900 - 40 - 28 - 36
    svg, b, orect = plan_svg(c, vw, vh)
    pop = popover(c, 796, 352)
    body = f"""<div class="app wide">{appbar(c, "Site plan · Phase 1")}{rail(4)}
  <div class="view">{viewbar(c)}<div class="plan">{svg}{pop}{legend(c)}</div></div>
  {inspector(c)}{status(c)}</div>"""
    page(f"c20-object-{theme}", body, theme, title="Parametric object in the drawing")

# ------------------------------------------------------------------ the custom window
def custom_window(c, x, y, design=False, dragging=False):
    tile = f'<span class="tile" style="background:{rgba(c["cat-shape"], 0.18)}">{ic("cube", 14, c["cat-shape"])}</span>'
    bars = [("Homes", 0.78, c["kind-number"], "12,950 m²"), ("Retail", 0.22, c["cat-measure"], "2,610 m²"), ("Office", 0.0, c["cat-list"], "0 m²"), ("Parking", 0.24, c["text-subtle"], "2,860 m²")]
    bar_html = "".join(f'<div class="bar"><span>{l}</span><span class="b" style="width:{max(f, 0.02) * 100:.0f}%;background:{col}"></span><span class="n">{n}</span></div>' for l, f, col, n in bars)
    bound = lambda name, kind: (f'<span class="bound">{kdot(c, kind)}</span>' if design else "")
    chart = f"""<div class="chart"><div class="ttl"><span>GFA by use</span><b>18,420 m²</b></div><div class="bars">{bar_html}</div></div>"""
    if design:
        chart = (f'<div class="sel"><span class="tag">{ic("chart-bar", 11, c["text-on-accent"])} Chart · GFA by use</span>'
                 + "".join(f'<span class="h" style="{p}"></span>' for p in ("left:-9px;top:-9px", "right:-9px;top:-9px", "left:-9px;bottom:-9px", "right:-9px;bottom:-9px", "left:calc(50% - 4px);bottom:-9px"))
                 + chart + "</div>")
    drop = '<div class="dropline"></div>' if design else ""
    floors_frac = 0.52 if dragging else 0.45
    depth_val, depth_frac = ("16", 0.68) if dragging else ("14", 0.55)
    tip = (f'<span class="tip" style="left:calc({depth_frac * 100:.0f}% - 30px);top:-26px">Depth 16 m</span>' if dragging else "")
    return f"""<div class="cw" style="left:{x}px;top:{y}px">
  <div class="tbar">{tile}<div><div class="t">Courtyard block</div><div class="s">A3 · Mid-rise default, changed</div></div>
    <span class="r"><span class="tb-btn">{ic('pin', 15)}</span><span class="tb-btn">{ic('x', 15)}</span></span></div>
  <div class="tabs"><span class="on">Massing</span><span>Setbacks</span><span>Use mix</span><span>Report</span></div>
  <div class="body">
    <div class="sec">Building<span class="line"></span></div>
    <div class="prow"><label>Floors {bound('Floors', 'number')}</label><span class="val">8</span><div class="track"><span class="rail"></span><span class="fill" style="width:{floors_frac * 100:.0f}%"></span><span class="knob" style="left:{floors_frac * 100:.0f}%"></span><span class="ticks">{'<i></i>' * 13}</span></div></div>
    <div class="two">
      <div class="field"><label>Floor height {bound('Floor height', 'number')}</label><span class="stepper"><span>{ic('minus', 12)}</span><b>3.2 m</b><span>{ic('plus', 12)}</span></span></div>
      <div class="field"><label>Roof {bound('Roof', 'text')}</label><span class="select">Flat<span class="chev">{ic('chevron-down', 13)}</span></span></div>
    </div>
    {drop}
    <div class="sec">Courtyard<span class="line"></span></div>
    <div class="prow"><label>Depth {bound('Depth', 'number')}</label><span class="val">{depth_val}<span class="u">m</span></span><div class="track"><span class="rail"></span><span class="fill" style="width:{depth_frac * 100:.0f}%"></span><span class="knob" style="left:{depth_frac * 100:.0f}%"></span>{tip}</div></div>
    <div class="field"><label>Corners {bound('Corners', 'text')}</label><span class="segs"><span>Square</span><span class="on">Chamfer</span><span>Round</span></span></div>
    {chart}
    <div class="mini-table"><div><span>Floor</span><span>Use</span><span>Area</span></div><div><span>Ground</span><span>Retail</span><span>2,610 m²</span></div><div><span>1 to 7</span><span>Homes</span><span>12,950 m²</span></div><div><span>Basement</span><span>Parking</span><span>2,860 m²</span></div></div>
  </div>
  <div class="foot"><span class="select" style="flex:none;width:150px">{ic('bookmark', 13)} Presets<span class="chev">{ic('chevron-down', 13)}</span></span><span class="btn sm ghost">{ic('refresh', 13)} Reset</span><span class="spacer"></span><span class="btn sm primary">{ic('box', 13, c['text-on-accent'])} Bake</span></div>
</div>"""

# ------------------------------------------------------------------ page 2: the window designer
def build_designer(theme):
    c = TOK["color"][theme]
    tiles = [("Input", [("adjustments-horizontal", "Slider"), ("hash", "Number"), ("selector", "Choice"), ("toggle-right", "Toggle"), ("palette", "Colour"),
                        ("typography", "Text"), ("vector-bezier-2", "Curve"), ("table", "Table"), ("crosshair", "Pick in drawing")]),
             ("Show", [("variable", "Value"), ("chart-bar", "Chart"), ("photo", "Image"), ("text-size", "Note")]),
             ("Layout", [("section", "Section"), ("layout-columns", "Columns"), ("app-window", "Tabs"), ("box-model-2", "Group")]),
             ("Action", [("click", "Button"), ("bookmark", "Presets"), ("box", "Bake")])]
    groups = "".join(f'<div class="section-label">{g}</div><div class="tiles">' + "".join(
        f'<span class="tilebtn{" drag" if n == "Toggle" else ""}">{ic(i, 18)}{n}</span>' for i, n in items) + "</div>" for g, items in tiles)
    unbound = f'<div class="section-label">Flow inputs not on the window</div><div class="chipline"><span class="kchip missing">{kdot(c, "text")} Corner radius</span><span class="kchip missing">{kdot(c, "number")} Rear setback</span></div>'
    palette = f"""<div class="palette"><div class="tabs"><span class="on">Controls</span><span>Bindings</span><span>Outline</span></div>
      <div class="panel-body" style="gap:8px"><div class="search">{ic('search', 14)} Find a control</div>{groups}{unbound}</div></div>"""
    surface = f"""<div class="surface"><div class="dots"></div>
      {custom_window(c, 196, 34, design=True)}
      <div class="dragghost" style="left:640px;top:262px">{ic('toggle-right', 16, c['accent'])} Toggle <span style="color:var(--text-subtle);font-weight:400">drop to add below Roof</span></div>
      <div class="callout" style="left:640px;top:58px"><i>1</i> Drag controls in; they snap to a 2-column grid</div>
      <div class="callout" style="left:640px;top:96px"><i>2</i> Each control binds to one flow input or output</div>
      <div class="callout" style="left:640px;top:134px"><i>3</i> Rules show or enable a control from other values</div>
    </div>"""
    props = f"""<div class="props"><div class="insp-head"><span class="tile" style="background:{rgba(c['cat-measure'], 0.18)}">{ic('chart-bar', 16, c['cat-measure'])}</span>
      <div><div class="name">Chart</div><div class="kind">In section Courtyard · row 4</div></div></div>
      <div class="tabs" style="padding-top:4px"><span class="on">Setup</span><span>Rules</span><span>Style</span></div>
      <div class="panel-body" style="gap:10px">
        <div class="section-label">Bound to</div>
        <div class="binding">{kdot(c, 'number')}<b>GFA by use</b><span class="src">output · list of 4</span></div>
        <div class="prop"><label>Label</label><span class="ctl">GFA by use</span></div>
        <div class="prop"><label>Chart</label><span class="segs" style="height:28px"><span class="on">Bars</span><span>Stacked</span><span>Pie</span></span></div>
        <div class="prop"><label>Width</label><span class="segs" style="height:28px"><span>1 column</span><span class="on">2 columns</span></span></div>
        <div class="prop"><label>Height</label><span class="ctl"><span class="num" style="text-align:left">auto</span><span class="chev">{ic('chevron-down', 14)}</span></span></div>
        <div class="section-label" style="margin-top:6px">Show when</div>
        <div class="rule"><span class="select">{kdot(c, 'text')} Use<span class="chev">{ic('chevron-down', 12)}</span></span><span class="select">is not<span class="chev">{ic('chevron-down', 12)}</span></span><span class="select">Office<span class="chev">{ic('chevron-down', 12)}</span></span><span class="tb-btn">{ic('x', 13)}</span></div>
        <span class="btn ghost sm" style="align-self:flex-start">{ic('plus', 13)} Add rule</span>
        <div class="section-label">Enable when</div>
        <span class="ctl">Always<span class="chev">{ic('chevron-down', 14)}</span></span>
        <div class="section-label">Help</div>
        <span class="ctl" style="height:52px;align-items:flex-start;padding-top:6px;color:var(--text-muted)">Gross floor area per use, from the flow's GFA output.</span>
      </div></div>"""
    toolbar = f"""<div class="toolbar"><span class="tb-btn">{ic('arrow-back-up', 16)}</span><span class="flowname">{ic('cube', 16, c['cat-shape'])} Courtyard block <span class="muted">›</span> Window</span>
      <span class="tb-sep"></span><span class="seg"><span class="on">Design</span><span>Preview</span></span>
      <span class="tb-btn">{ic('arrow-back-up', 16)}</span><span class="tb-btn">{ic('arrow-forward-up', 16)}</span><span class="tb-sep"></span>
      <span class="pill">{ic('device-desktop', 14)} 420 × auto {ic('chevron-down', 14)}</span><span class="seg"><span class="{'on' if theme == 'dark' else ''}">{ic('moon', 14)} Dark</span><span class="{'on' if theme == 'light' else ''}">{ic('sun', 14)} Light</span></span>
      <span class="spacer"></span><span class="tb-btn">{ic('crosshair', 16)} Test on A3</span><span class="tb-btn primary">{ic('device-floppy', 16, c['text-on-accent'])} Save window</span></div>"""
    body = f"""<div class="app wide" style="grid-template-columns:1fr">{appbar(c, "Courtyard block · window designer")}
      <div class="designer">{toolbar}{palette}{surface}{props}</div>{status(c, "Designing the window for Courtyard block v3")}</div>"""
    body = body.replace('<div class="appbar">', '<div class="appbar" style="grid-column:1">').replace('<div class="status">', '<div class="status" style="grid-column:1">')
    page(f"c20-designer-{theme}", body, theme, title="Window designer")

# ------------------------------------------------------------------ page 3: the custom window in use
def build_in_use(theme):
    c = TOK["color"][theme]
    vw, vh = 1440 - 72 - 300, 900 - 40 - 28 - 36
    svg, b, orect = plan_svg(c, vw, vh, handles=True, ghost_depth=16, hover_tip=False)
    win = custom_window(c, 24, 16, design=False, dragging=True)
    body = f"""<div class="app wide">{appbar(c, "Site plan · Phase 1")}{rail(4)}
  <div class="view">{viewbar(c)}<div class="plan">{svg}{win}{legend(c)}</div></div>
  {inspector(c, depth=16)}{status(c, "Live preview: courtyard depth 16 m (release to apply as one undo step)")}</div>"""
    page(f"c20-window-in-use-{theme}", body, theme, title="Custom window in use")

if __name__ == "__main__":
    for t in ("dark", "light"):
        build_object(t)
        build_designer(t)
        build_in_use(t)
    (ROOT / "tools" / "manifest.json").write_text(json.dumps(MANIFEST, indent=1), encoding="utf-8")
    print(len(MANIFEST), "pages")
