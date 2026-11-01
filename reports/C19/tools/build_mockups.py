"""Build the C19 mockup pages (HTML with inline SVG) and a render manifest for render.js.

Run: python3 build_mockups.py && node render.js
"""
import json, math, pathlib, random
import flowsvg as F
from flowsvg import Theme, S, T, Z, TOK, icon, esc, rgba

ROOT = F.ROOT
OUT = ROOT / "mockups"
DARK, LIGHT = Theme("dark"), Theme("light")
MANIFEST = []

def page(name, body, width, height, theme=DARK, title="", scale=1):
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{esc(title or name)}</title>
<meta name="viewport" content="width={width}">
<link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="chrome.css">
<style>html,body{{width:{width}px;height:{height}px;overflow:hidden}}</style></head>
<body class="theme-{theme.name}">{body}</body></html>
"""
    (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
    MANIFEST.append({"html": f"{name}.html", "png": f"png/{name}.png", "width": width, "height": height, "scale": scale})

def ic(name, size=16, color="currentColor"):
    src = (F.ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
    src = src.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    src = src.replace('stroke-width="2"', 'stroke-width="1.75"').replace('stroke="currentColor"', f'stroke="{color}"')
    return f'<span class="icon" style="width:{size}px;height:{size}px">{src}</span>'

# ------------------------------------------------------------------ the small flow (b)
def small_flow(error=True, selected="offset", focus_floors=True, compact=False):
    c2, c3 = (320, 592) if compact else (352, 656)
    nodes = [
        dict(id="layer", x=64, y=104, w=192, title="Layer", cat="source", icon="stack-2",
             outputs=[dict(name="Shapes", kind="shapes", count="24")],
             inputs=[dict(name="Layer", kind="text", value="Plots")]),
        dict(id="setback", x=64, y=216, w=192, title="Setback", cat="value", icon="adjustments-horizontal",
             outputs=[dict(name="Value", kind="number", count="1")],
             inputs=[dict(name="Metres", kind="number", slider=dict(min=0, max=20, value=6, unit="m"))]),
        dict(id="floors", x=64, y=328, w=192, title="Floors", cat="value", icon="hash",
             outputs=[dict(name="Value", kind="number", count="1")],
             inputs=[dict(name="Number", kind="number", value="4", focus=focus_floors)]),
        dict(id="offset", x=c2, y=104, w=208, title="Offset", subtitle="Simple", cat="shape", icon="vector-bezier-2",
             outputs=[dict(name="Shapes", kind="shapes", count="24"), dict(name="Area", kind="number", count="24", wired=True)],
             inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Distance", kind="number", wired=True),
                     dict(name="Sides", kind="text", value="Inside"), dict(name="Join", kind="text", value="Mitre")],
             selected=(selected == "offset")),
        dict(id="multiply", x=c2, y=344, w=208, title="Multiply", cat="value", icon="math-function",
             outputs=[dict(name="Result", kind="number", count="1")],
             inputs=[dict(name="A", kind="number", wired=True), dict(name="B", kind="number", value="3.2", unit="m")]),
        dict(id="extrude", x=c3, y=152, w=208, title="Extrude", cat="shape", icon="box",
             outputs=[dict(name="Solids", kind="shapes", count="21", failed=error)],
             inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Height", kind="number", wired=True, error=error)],
             state="error" if error else None,
             message=["3 of 24 plots got a height of 0 m.", "Height must be above 0."] if error else None,
             action="Select the 3 plots" if error else None),
        dict(id="area", x=c3, y=376, w=192, title="Total area", cat="measure", icon="ruler-measure",
             outputs=[dict(name="Sum", kind="number", count="1")],
             inputs=[dict(name="Values", kind="number", wired=True)]),
    ]
    wires = [
        dict(**{"from": ("layer", 0), "to": ("offset", 0)}, structure="list"),
        dict(**{"from": ("setback", 0), "to": ("offset", 1)}, structure="item"),
        dict(**{"from": ("floors", 0), "to": ("multiply", 0)}, structure="item"),
        dict(**{"from": ("offset", 0), "to": ("extrude", 0)}, structure="list"),
        dict(**{"from": ("multiply", 0), "to": ("extrude", 1)}, structure="item"),
        dict(**{"from": ("offset", 1), "to": ("area", 0)}, structure="list"),
    ]
    if selected == "offset":
        for w in wires:
            if "offset" in (w["from"][0], w["to"][0]):
                w["state"] = "selected"
    groups = [
        dict(title="Inputs", color="group-2", x=40, y=64, w=240, h=376),
        dict(title="Massing", color="group-3", x=c2 - 24, y=64, w=c3 + 208 + 24 - (c2 - 24), h=432),
    ]
    return dict(nodes=nodes, wires=wires, groups=groups)

def toolbar_html(theme, zoom="100%", running=False):
    return f"""<div class="toolbar">
  <span class="flowname">{ic('route', 16, theme['text-muted'])} Offset the plots by a slider <span class="muted">{ic('chevron-down', 14, theme['text-subtle'])}</span></span>
  <span class="tb-sep"></span>
  <span class="tb-btn primary">{ic('player-play', 16, theme['text-on-accent'])} Run</span>
  <span class="tb-btn {'disabled' if not running else ''}">{ic('player-stop', 16)}</span>
  <span class="seg"><span class="on">Auto</span><span>Manual</span><span>Delay</span></span>
  <span class="tb-sep"></span>
  <span class="tb-btn">{ic('arrow-back-up', 16)}</span><span class="tb-btn">{ic('arrow-forward-up', 16)}</span>
  <span class="spacer"></span>
  <span class="tb-btn">{ic('search', 16)}</span>
  <span class="zoom"><span>{ic('minus', 14)}</span><span class="val">{zoom}</span><span>{ic('plus', 14)}</span></span>
  <span class="tb-btn">{ic('focus-2', 16)}</span>
  <span class="tb-sep"></span>
  <span class="tb-btn">{ic('map', 16)}</span><span class="tb-btn">{ic('layout-sidebar-right', 16)}</span><span class="tb-btn">{ic('dots', 16)}</span>
</div>"""

def flow_canvas_svg(model, theme, w, h, zoom=1.0, origin=(0, 0), minimap=True, view=None, fade=False, extra=""):
    svg = F.canvas(model, theme, w, h, zoom=zoom, origin=origin, fade_unrelated=fade, extra_top=extra)
    if minimap:
        mx = w - S["minimap-width"] - S["minimap-margin"]
        my = h - S["minimap-height"] - S["minimap-margin"]
        view = view or (origin[0], origin[1], w / zoom, h / zoom)
        mm = F.minimap(model, theme, view, mx, my)
        svg = svg.replace("</svg>", mm + "</svg>")
    return svg

def problem_chip(errors=1, warnings=0):
    parts = []
    if errors:
        parts.append(f'<span class="d"></span>{errors} error' + ("s" if errors > 1 else ""))
    if warnings:
        parts.append(f'<span class="w"></span>{warnings} warning' + ("s" if warnings > 1 else ""))
    return f'<div class="problem">{" ".join(parts)}</div>'

# ------------------------------------------------------------------ (b) small flow, dark and light
def build_small_flow(theme, name):
    W, H = 1200, 760
    model = small_flow()
    canvas = flow_canvas_svg(model, theme, W, H - 40, origin=(0, 0))
    body = f"""<div class="solo" style="width:{W}px;height:{H}px;display:grid;grid-template-rows:40px 1fr">
{toolbar_html(theme)}
<div class="canvas" style="grid-row:2">{canvas}{problem_chip(1, 0)}</div></div>"""
    page(name, body, W, H, theme, "Small flow, " + theme.name)

# ------------------------------------------------------------------ (a) whole window
RAIL = ["vector", "vector-bezier-2", "line-dashed", "polygon", "box", "shape", "ruler-measure", "resize",
        "layout-grid", "route", "stack", "lasso", "crosshair", "tag", "table", "calculator", "typography",
        "building-community", "grid-dots", "selector", "versions", "database", "photo", "settings"]

def build_window(theme, name):
    model = small_flow(compact=True)
    cw, ch = 1440 - 72 - 300 - 248, 900 - 40 - 28 - 40 - 32
    canvas = flow_canvas_svg(model, theme, cw, ch, zoom=1.0, origin=(28, 44))
    rail = "".join(f'<span class="tool {"on" if i == 9 else ""}">{ic(n, 18)}</span>' + ("<hr>" if i in (7, 15) else "") for i, n in enumerate(RAIL))
    cats = [("Sources", "source", "stack-2", 6), ("Values", "value", "adjustments-horizontal", 5), ("Shapes", "shape", "vector-bezier-2", 18),
            ("Measure", "measure", "ruler-measure", 9), ("Lists", "list", "list-details", 11), ("Flow", "flow", "repeat", 4), ("Output", "output", "file-spreadsheet", 3)]
    cat_rows = "".join(f'<div class="row"><span class="tile" style="background:{rgba(theme["cat-" + c], 0.18)}">{ic(i, 14, theme["cat-" + c])}</span>{t}<span class="meta">{n}</span></div>' for t, c, i, n in cats)
    start = "".join(f'<div class="row"><span class="tile" style="background:{rgba(theme["cat-" + c], 0.18)}">{ic(i, 14, theme["cat-" + c])}</span>{t}</div>' for t, c, i in
                    [("Layer", "source", "stack-2"), ("Slider", "value", "adjustments-horizontal"), ("Offset", "shape", "vector-bezier-2"), ("Area", "measure", "ruler-measure")])
    left = f"""<div class="left">
  <div class="tabs"><span>Flows</span><span class="on">Nodes</span><span>Library</span><span>Variants</span></div>
  <div class="panel-body">
    <div class="search">{ic('search', 14)} Search nodes <kbd>Tab</kbd></div>
    <div class="chips"><span class="chip on">Start here</span><span class="chip">Recent</span><span class="chip">Starred</span></div>
    <div class="list">{start}</div>
    <div class="section-label">All nodes</div>
    <div class="list">{cat_rows}</div>
  </div></div>"""
    dot = lambda k: f'<span class="kind" style="background:{theme["kind-" + k]}"></span>'
    right = f"""<div class="right">
  <div class="insp-head"><span class="tile" style="background:{rgba(theme['cat-shape'], 0.18)}">{ic('vector-bezier-2', 16, theme['cat-shape'])}</span>
    <div><div class="name">Offset</div><div class="kind">Shape command · 24 shapes · 0.1 ms</div></div>
    <span style="margin-left:auto" class="tb-btn">{ic('dots', 16)}</span></div>
  <div class="tabs" style="padding-top:4px"><span class="on">Inputs</span><span>Outputs</span><span>Info</span></div>
  <div class="panel-body" style="gap:8px">
    <div class="prop"><label>Shapes</label><span class="ctl wired">{dot('shapes')} from Layer</span></div>
    <div class="prop"><label>Distance</label><span class="ctl wired">{dot('number')} from Setback</span></div>
    <div class="prop"><label>Mode</label><span class="ctl">Simple<span class="chev">{ic('chevron-down', 14)}</span></span></div>
    <div class="prop"><label>Sides</label><span class="ctl">Inside<span class="chev">{ic('chevron-down', 14)}</span></span></div>
    <div class="prop"><label>Join</label><span class="ctl">Mitre<span class="chev">{ic('chevron-down', 14)}</span></span></div>
    <div class="prop"><label>Ends</label><span class="ctl">Square<span class="chev">{ic('chevron-down', 14)}</span></span></div>
    <div class="prop"><label>Merge</label><span><span class="toggle"></span></span></div>
    <div class="section-label" style="margin-top:12px">Last run</div>
    <div class="facts"><span>Shapes out</span><b>24</b><span>Total area</span><b>3,412 m²</b><span>Time</span><b>0.1 ms</b></div>
    <div style="display:flex;gap:8px;margin-top:8px"><span class="btn">{ic('route', 14)} Explain</span><span class="btn ghost">{ic('eye', 14)} Preview</span></div>
  </div></div>"""
    menus = "".join(f'<span class="menu">{m}</span>' for m in "File Edit View Map Draw Points Curves Regions Massing Transform Blocks Annotate Analyse Help".split())
    body = f"""<div class="app">
  <div class="appbar"><span class="brand"><span class="dot">{ic('building-community', 13, theme['text-on-accent'])}</span>Urbanto Studio</span>{menus}
    <span class="title"><b>Flow offset by slider</b> · edited</span>
    <span class="appright"><span class="pill">{ic('layout-grid', 14)} Drafting {ic('chevron-down', 14)}</span><span class="tb-btn">{ic('search', 16)}</span></span></div>
  <div class="rail">{rail}</div>
  <div class="doc">
    {toolbar_html(theme)}
    {left}
    <div class="canvas">{canvas}{problem_chip(1, 0)}</div>
    <div class="doctabs"><span>{ic('map', 14)} Model</span><span class="on">{ic('route', 14)} Offset the plots by a slider</span><span>{ic('plus', 14)}</span></div>
  </div>
  {right}
  <div class="status"><span class="t">E</span> 1,204.5 <span class="t">N</span> 3,880.2 <span class="t">m</span><span class="spacer"></span>
    <span class="group"><span class="on">OSNAP</span><span>ORTHO</span><span>POLAR</span><span>SNAP</span><span class="on">TRACK</span></span>
    <span>Show: Both</span><span>Select: Drawing</span><span>Grid: north</span><span>{ic('bell', 14) if (F.ICON_DIR / 'bell.svg').exists() else ''}</span></div>
</div>"""
    page(name, body, 1440, 900, theme, "Whole window")

# ------------------------------------------------------------------ direct "after" views at screenshot size
def build_error_pair(theme):
    """Same content as 02: Layer, Slider, two Offset nodes, one in error, hover thumbnail hidden."""
    nodes = [
        dict(id="layer", x=24, y=96, w=176, title="Layer", cat="source", icon="stack-2",
             outputs=[dict(name="Shapes", kind="shapes", count="2×1"), dict(name="Layer", kind="text", count="1")],
             inputs=[dict(name="Name", kind="text", value="Plots")]),
        dict(id="slider", x=24, y=232, w=176, title="Slider", cat="value", icon="adjustments-horizontal",
             outputs=[dict(name="Value", kind="number", count="1")],
             inputs=[dict(name="Value", kind="number", slider=dict(min=0, max=10, value=1, unit=""))]),
        dict(id="o1", x=264, y=96, w=208, title="Offset", subtitle="Simple", cat="shape", icon="vector-bezier-2",
             outputs=[dict(name="Created", kind="shapes", count="2×1"), dict(name="Area", kind="number", count="2")],
             inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Distance", kind="number", wired=True),
                     dict(name="Sides", kind="text", value="Left"), dict(name="Join", kind="text", value="Mitre")]),
        dict(id="o2", x=264, y=328, w=208, title="Offset", subtitle="Simple", cat="shape", icon="vector-bezier-2",
             outputs=[dict(name="Created", kind="shapes", failed=True)],
             inputs=[dict(name="Shapes", kind="shapes", wired=False, error=True), dict(name="Distance", kind="number", wired=True),
                     dict(name="Sides", kind="text", value="Left")],
             state="error", message=["Shapes is not connected.", "Connect a layer or a selection."], action="Connect from Layer"),
    ]
    wires = [dict(**{"from": ("layer", 0), "to": ("o1", 0)}, structure="list"),
             dict(**{"from": ("slider", 0), "to": ("o1", 1)}), dict(**{"from": ("slider", 0), "to": ("o2", 1)})]
    model = dict(nodes=nodes, wires=wires, groups=[])
    svg = flow_canvas_svg(model, theme, 600, 723, origin=(0, 0), minimap=False)
    page("after-02-error", f'<div class="canvas" style="width:600px;height:723px">{svg}{problem_chip(1)}</div>', 600, 723, theme, "Error node, after")
    return model

def build_zoomed_pair(theme):
    model = build_error_pair_model()
    svg = flow_canvas_svg(model, theme, 600, 723, zoom=0.5, origin=(-280, -300), minimap=False)
    page("after-03-zoomed-out", f'<div class="canvas" style="width:600px;height:723px">{svg}{problem_chip(1)}</div>', 600, 723, theme, "Zoomed out, after")

def build_error_pair_model():
    nodes = [
        dict(id="layer", x=24, y=96, w=176, title="Layer", cat="source", icon="stack-2",
             outputs=[dict(name="Shapes", kind="shapes", count="2×1"), dict(name="Layer", kind="text", count="1")],
             inputs=[dict(name="Name", kind="text", value="Plots")]),
        dict(id="slider", x=24, y=232, w=176, title="Slider", cat="value", icon="adjustments-horizontal",
             outputs=[dict(name="Value", kind="number", count="1")],
             inputs=[dict(name="Value", kind="number", slider=dict(min=0, max=10, value=1, unit=""))]),
        dict(id="o1", x=264, y=96, w=208, title="Offset", subtitle="Simple", cat="shape", icon="vector-bezier-2",
             outputs=[dict(name="Created", kind="shapes", count="2×1"), dict(name="Area", kind="number", count="2")],
             inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Distance", kind="number", wired=True),
                     dict(name="Sides", kind="text", value="Left"), dict(name="Join", kind="text", value="Mitre")]),
        dict(id="o2", x=264, y=360, w=208, title="Offset", subtitle="Simple", cat="shape", icon="vector-bezier-2",
             outputs=[dict(name="Created", kind="shapes", failed=True)],
             inputs=[dict(name="Shapes", kind="shapes", wired=False, error=True), dict(name="Distance", kind="number", wired=True),
                     dict(name="Sides", kind="text", value="Left")],
             state="error", message=["Shapes is not connected."], action="Connect from Layer"),
    ]
    wires = [dict(**{"from": ("layer", 0), "to": ("o1", 0)}, structure="list"),
             dict(**{"from": ("slider", 0), "to": ("o1", 1)}), dict(**{"from": ("slider", 0), "to": ("o2", 1)})]
    return dict(nodes=nodes, wires=wires, groups=[])

def build_paused_pair(theme):
    model = build_error_pair_model()
    model["nodes"] = [n for n in model["nodes"] if n["id"] != "o2"]
    for n in model["nodes"]:
        if n["id"] in ("layer", "slider"):
            n["badges"] = ["ran"]
        if n["id"] == "o1":
            n["state"] = "paused"
            n["badges"] = ["breakpoint"]
            n["selected"] = False
            n["y"] = 200
    for w in model["wires"]:
        w["state"] = None
    model["wires"] = [w for w in model["wires"] if w["to"][0] != "o2"]
    o1 = next(n for n in model["nodes"] if n["id"] == "o1")
    th = theme
    bar_y = o1["y"] - 44
    label = "Paused before Offset"
    lw = F.text_width(label, 11, 500)
    bw = 8 + 8 + 10 + lw + 12 + 40 + 6 + 46 + 4
    bx = o1["x"] + o1["w"] - bw + 8
    bar = (f'<g><rect x="{bx}" y="{bar_y}" width="{bw}" height="32" rx="8" fill="{th["overlay"]}" stroke="{th["border-strong"]}" filter="url(#shadow-{th.name})"/>'
           f'<circle cx="{bx + 14}" cy="{bar_y + 16}" r="4" fill="{th["paused"]}"/>'
           f'<text x="{bx + 26}" y="{bar_y + 20}" class="t-small" fill="{th["text"]}">{label}</text>'
           f'<rect x="{bx + bw - 94}" y="{bar_y + 4}" width="40" height="24" rx="6" fill="{th["accent-fill"]}"/>'
           + icon("player-play", bx + bw - 82, bar_y + 8, 16, th["text-on-accent"]) +
           f'<rect x="{bx + bw - 50}" y="{bar_y + 4}" width="46" height="24" rx="6" fill="{th["control"]}"/>'
           f'<text x="{bx + bw - 27}" y="{bar_y + 20}" text-anchor="middle" class="t-small" fill="{th["text"]}">Step</text></g>')
    svg = flow_canvas_svg(model, theme, 600, 721, origin=(0, 0), extra=bar, minimap=False)
    page("after-04-paused", f'<div class="canvas" style="width:600px;height:721px">{svg}</div>', 600, 721, theme, "Paused, after")

def build_one_node(theme, name="after-06-one-node", w=600, h=728):
    n = dict(id="num", x=196, y=320, w=208, title="Number", cat="value", icon="hash",
             outputs=[dict(name="Value", kind="number", count="1")],
             inputs=[dict(name="Value", kind="number", value="12.5", unit="m")], selected=True)
    model = dict(nodes=[n], wires=[], groups=[])
    svg = flow_canvas_svg(model, theme, w, h, origin=(0, 0), minimap=False)
    page(name, f'<div class="canvas" style="width:{w}px;height:{h}px">{svg}</div>', w, h, theme, "One node, after")

def build_hover_pair(theme):
    model = build_error_pair_model()
    model["nodes"] = [n for n in model["nodes"] if n["id"] != "o2"]
    model["wires"] = [w for w in model["wires"] if w["to"][0] != "o2"]
    o1 = next(n for n in model["nodes"] if n["id"] == "o1")
    o1["y"] = 300
    for n in model["nodes"]:
        if n["id"] != "o1":
            n["y"] += 204
    plots = [dict(pts=[(0, 0), (40, 0), (40, 30), (0, 30)], muted=True, dashed=True),
             dict(pts=[(4, 4), (36, 4), (36, 26), (4, 26)], fill=True),
             dict(pts=[(60, 2), (98, 2), (98, 32), (60, 32)], muted=True, dashed=True),
             dict(pts=[(64, 6), (94, 6), (94, 28), (64, 28)], fill=True)]
    card = F.hover_card(o1, theme, plots, "Offset · 2 shapes", "Area 2,184 m²  ·  ran in 0.1 ms")
    svg = flow_canvas_svg(model, theme, 600, 728, origin=(0, 0), extra=card, minimap=False)
    page("after-07-hover", f'<div class="canvas" style="width:600px;height:728px">{svg}</div>', 600, 728, theme, "Hover card, after")

# ------------------------------------------------------------------ 500 nodes
def big_model(cols=25, rows=20, seed=3):
    rnd = random.Random(seed)
    templates = [
        ("Layer", "source", "stack-2", [("Shapes", "shapes")], [("Name", "text", "Plots")]),
        ("Offset", "shape", "vector-bezier-2", [("Shapes", "shapes"), ("Area", "number")], [("Shapes", "shapes", None), ("Distance", "number", None), ("Sides", "text", "Inside")]),
        ("Divide", "shape", "layout-grid", [("Parts", "shapes")], [("Shapes", "shapes", None), ("Count", "number", "6")]),
        ("Extrude", "shape", "box", [("Solids", "shapes")], [("Shapes", "shapes", None), ("Height", "number", None)]),
        ("Area", "measure", "ruler-measure", [("Sum", "number")], [("Shapes", "shapes", None)]),
        ("Count", "measure", "hash", [("Count", "number")], [("Items", "any", None)]),
    ]
    nodes, wires, groups = [], [], []
    colw, gapx, gapy = 208, 88, 40
    col_x = [64 + c * (colw + gapx) for c in range(cols)]
    for c in range(cols):
        y = 96
        kind = 0 if c == 0 else 1 + (c - 1) % (len(templates) - 1)
        for r in range(rows):
            t = templates[kind if c else 0]
            title, cat, icn, outs, ins = t
            nid = f"n{c}_{r}"
            n = dict(id=nid, x=col_x[c], y=y, w=colw, title=title, cat=cat, icon=icn,
                     outputs=[dict(name=o, kind=k, count=rnd.choice(["24", "12", "2×6", "1", "48"])) for o, k in outs],
                     inputs=[dict(name=i[0], kind=i[1], **({"value": i[2]} if i[2] else {"wired": True})) for i in ins])
            if rnd.random() < 0.012:
                n["state"] = "error"; n["message"] = ["Height must be above 0."]
            elif rnd.random() < 0.015:
                n["state"] = "warning"
            nodes.append(n)
            y += F.node_height(n) + gapy + (40 if n.get("state") == "error" else 0)
    by = {n["id"]: n for n in nodes}
    for c in range(1, cols):
        for r in range(rows):
            dst = by[f"n{c}_{r}"]
            srcs = [by[f"n{c-1}_{rr}"] for rr in (r, max(0, r - 1)) if f"n{c-1}_{rr}" in by]
            for k, src in enumerate(srcs[:1 + (r % 2)]):
                oi = 0
                ii = next((i for i, p in enumerate(dst["inputs"]) if p.get("wired") and p["kind"] in (src["outputs"][oi]["kind"], "any")), None)
                if ii is None:
                    continue
                if any(w["to"] == (dst["id"], ii) for w in wires):
                    continue
                wires.append({"from": (src["id"], oi), "to": (dst["id"], ii), "structure": "list" if src["outputs"][oi]["kind"] == "shapes" else "item"})
    for g in range(0, cols, 5):
        x0 = col_x[g] - 24
        x1 = col_x[min(g + 4, cols - 1)] + colw + 24
        ys = [n["y"] for n in nodes if n["x"] >= x0 and n["x"] <= x1]
        ye = [n["y"] + F.node_height(n) for n in nodes if n["x"] >= x0 and n["x"] <= x1]
        groups.append(dict(title=["Site inputs", "Plot setbacks", "Massing", "Measures", "Reports"][g // 5 % 5],
                           color=f"group-{1 + (g // 5) % 8}", x=x0, y=min(ys) - 48, w=x1 - x0, h=max(ye) - min(ys) + 72))
    return dict(nodes=nodes, wires=wires, groups=groups)

def build_500(theme):
    model = big_model()
    assert len(model["nodes"]) == 500, len(model["nodes"])
    # normal zoom, matching 05 (600 x 723)
    svg = flow_canvas_svg(model, theme, 600, 723, zoom=1.0, origin=(580, 520))
    page("after-05-500-nodes-100", f'<div class="canvas" style="width:600px;height:723px">{svg}{problem_chip(4, 6)}</div>', 600, 723, theme, "500 nodes at 100 percent")
    # 30 percent
    svg = flow_canvas_svg(model, theme, 600, 723, zoom=0.30, origin=(20, -60))
    page("after-05-500-nodes-30", f'<div class="canvas" style="width:600px;height:723px">{svg}{problem_chip(4, 6)}</div>', 600, 723, theme, "500 nodes at 30 percent")
    # large versions
    svg = flow_canvas_svg(model, theme, 1200, 760, zoom=1.0, origin=(580, 520))
    page("mock-500-nodes-100", f'<div class="canvas" style="width:1200px;height:760px">{svg}{problem_chip(4, 6)}</div>', 1200, 760, theme, "500 nodes at 100 percent")
    svg = flow_canvas_svg(model, theme, 1200, 760, zoom=0.30, origin=(0, -60))
    page("mock-500-nodes-30", f'<div class="canvas" style="width:1200px;height:760px">{svg}{problem_chip(4, 6)}</div>', 1200, 760, theme, "500 nodes at 30 percent")
    return model

# ------------------------------------------------------------------ zoom sheet (100, 60, 30)
def build_zoom_sheet(theme):
    model = small_flow(focus_floors=False)
    cells = []
    for z, label in ((1.0, "100 percent: everything"), (0.6, "60 percent: no port labels, titles 12 px on screen"), (0.3, "30 percent: blocks with state glyphs")):
        w, h = 560, 400
        svg = F.canvas(model, theme, w, h, zoom=z * 0.62, origin=(24, 40)) if False else F.canvas(model, theme, w, h, zoom=z, origin=(24, 40) if z == 1.0 else (-40, -20))
        cells.append(f'<figure style="display:flex;flex-direction:column;gap:8px"><figcaption class="ui" style="font:600 13px/18px IBM Plex Sans;color:{theme["text"]}">{label}</figcaption>'
                     f'<div style="width:{w}px;height:{h}px;overflow:hidden;border-radius:8px;border:1px solid {theme["border"]}">{svg}</div></figure>')
    body = f'<div class="sheet"><h1>Zoom levels</h1><p>The same flow at 100, 60 and 30 percent. Thresholds: full detail at 65 percent and above, blocks below 35 percent (tokens.json, zoom).</p><div style="display:flex;gap:24px;margin-top:20px">{"".join(cells)}</div></div>'
    page(f"mock-zoom-levels-{theme.name}", body, 1800, 560, theme, "Zoom levels")

# ------------------------------------------------------------------ anatomy sheet
def dim(x1, y1, x2, y2, label, theme, side="top", off=14):
    col = theme["accent"]
    out = []
    if side in ("top", "bottom"):
        yy = y1 - off if side == "top" else y1 + off
        out.append(f'<line x1="{x1}" y1="{yy}" x2="{x2}" y2="{yy}" stroke="{col}" stroke-width="1"/>')
        out += [f'<line x1="{x}" y1="{yy - 4}" x2="{x}" y2="{yy + 4}" stroke="{col}" stroke-width="1"/>' for x in (x1, x2)]
        out.append(f'<text x="{(x1 + x2) / 2}" y="{yy - 5 if side == "top" else yy + 14}" text-anchor="middle" font-size="11" font-weight="600" fill="{col}">{esc(label)}</text>')
    else:
        xx = x1 - off if side == "left" else x1 + off
        out.append(f'<line x1="{xx}" y1="{y1}" x2="{xx}" y2="{y2}" stroke="{col}" stroke-width="1"/>')
        out += [f'<line x1="{xx - 4}" y1="{y}" x2="{xx + 4}" y2="{y}" stroke="{col}" stroke-width="1"/>' for y in (y1, y2)]
        anchor = "end" if side == "left" else "start"
        out.append(f'<text x="{xx - 7 if side == "left" else xx + 7}" y="{(y1 + y2) / 2 + 4}" text-anchor="{anchor}" font-size="11" font-weight="600" fill="{col}">{esc(label)}</text>')
    return "".join(out)

def build_anatomy(theme):
    k = 2.5  # drawing scale for the big node
    n = dict(id="offset", x=0, y=0, w=208, title="Offset", subtitle="Simple", cat="shape", icon="vector-bezier-2",
             outputs=[dict(name="Shapes", kind="shapes", count="24"), dict(name="Area", kind="number", count="24")],
             inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Distance", kind="number", wired=True),
                     dict(name="Sides", kind="text", value="Inside")], badges=["warning"])
    big = F.node(n, theme, 1.0)
    h = F.node_height(n)
    ox, oy = 250, 120
    ann = []
    s = lambda v: v * k
    ann.append(dim(ox, oy, ox + s(208), oy, "208 px wide (26 grid units of 8)", theme, "top", 22))
    ann.append(dim(ox + s(208), oy, ox + s(208), oy + s(32), "header 32", theme, "right", 26))
    ann.append(dim(ox + s(208), oy + s(36), ox + s(208), oy + s(60), "row 24", theme, "right", 26))
    ann.append(dim(ox + s(208), oy + s(32), ox + s(208), oy + s(36), "pad 4", theme, "right", 90))
    ann.append(dim(ox, oy, ox, oy + s(h), f"{h} px = 32 + 4 + 5 × 24 + 4", theme, "left", 22))
    ann.append(dim(ox + s(10), oy + s(32) + 30, ox + s(30), oy + s(32) + 30, "icon tile 20", theme, "bottom", -36))
    notes = [
        ("Corner radius 8, border 1 px node-border, shadow 0 2 6 black 35 percent", 0),
        ("Header: node-header fill, 1 px divider; icon tile 20 at x 10 (category colour 18 percent, icon 14, stroke 1.75)", 1),
        ("Title IBM Plex Sans 13/16 semibold; subtitle 11 regular, text-subtle", 2),
        ("State badges 16 px at the header's right edge, 4 px apart", 3),
        ("Outputs first, then inputs: one port per 24 px row; labels 11 px, 12 px from the edge", 4),
        ("Count badge: 16 px pill, radius 8, padding 6, 10 px tabular numbers, inside the node", 5),
        ("Inline field: 20 px tall, radius 4, control fill, value 11 medium", 6),
        ("Ports: 10 px glyph on the edge with a 2 px ring in the node colour; hollow when unwired", 7),
    ]
    note_svg = "".join(f'<text x="{ox + s(208) + 130}" y="{oy + 30 + i * 26}" font-size="12" fill="{theme["text-muted"]}"><tspan font-weight="600" fill="{theme["text"]}">{j + 1}. </tspan>{esc(t)}</text>' for i, (t, j) in enumerate(notes))
    # legend: ports, wires, states
    ly = oy + s(h) + 110
    ox = 120
    legend = [f'<text x="{ox}" y="{ly}" font-size="13" font-weight="600" fill="{theme["text"]}">Ports by data kind (shape and colour)</text>']
    for i, (kind, label) in enumerate([("shapes", "Shapes: circle"), ("number", "Number: diamond"), ("text", "Text, choice, true/false: square"), ("any", "Any: ring")]):
        x = ox + 8 + i * 230
        legend.append(F.port_glyph(kind, x, ly + 28, theme, True, size=14))
        legend.append(F.port_glyph(kind, x + 26, ly + 28, theme, False, size=14))
        legend.append(f'<text x="{x + 44}" y="{ly + 32}" font-size="12" fill="{theme["text-muted"]}">{esc(label)}</text>')
    legend.append(f'<text x="{ox}" y="{ly + 78}" font-size="13" font-weight="600" fill="{theme["text"]}">Wires by structure (colour from the source port)</text>')
    for i, (st, label) in enumerate([("item", "One item 1.75 px"), ("list", "List 3 px"), ("nested", "List of lists: double line 5.5 px with 2.5 px gap"), ("lazy", "Lazy: dashed 6 4")]):
        x = ox + i * 260
        y = ly + 106
        d = f"M{x} {y} C{x + 60} {y}, {x + 60} {y + 24}, {x + 120} {y + 24}"
        col = theme["kind-shapes"]
        if st == "item":
            legend.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.75"/>')
        elif st == "list":
            legend.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3"/>')
        elif st == "nested":
            legend.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="5.5"/><path d="{d}" fill="none" stroke="{theme["canvas"]}" stroke-width="2.5"/>')
        else:
            legend.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.75" stroke-dasharray="6 4"/>')
        legend.append(f'<text x="{x}" y="{y + 50}" font-size="12" fill="{theme["text-muted"]}">{esc(label)}</text>')
    legend.append(f'<text x="{ox}" y="{ly + 200}" font-size="13" font-weight="600" fill="{theme["text"]}">State badges (16 px, in the header)</text>')
    for i, (st, label) in enumerate([("error", "Error"), ("warning", "Warning"), ("running", "Running"), ("paused", "Paused"), ("stale", "Out of date"), ("disabled", "Disabled"), ("bypass", "Bypassed"), ("ran", "Ran"), ("breakpoint", "Breakpoint")]):
        x = ox + i * 116
        legend.append(F.badge_state(st, x, ly + 214, theme, size=20))
        legend.append(f'<text x="{x + 28}" y="{ly + 229}" font-size="12" fill="{theme["text-muted"]}">{label}</text>')
    W, H = 1600, 1040
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H - 80}" class="flow">{F.defs(theme)}'
           f'<g transform="translate({ox},{oy}) scale({k})">{big}</g>{"".join(ann)}{note_svg}{"".join(legend)}</svg>')
    body = f'<div class="sheet" style="padding:24px 32px 0"><h1>Node anatomy</h1><p>Offset node drawn at 250 percent. All sizes are px at 100 percent zoom, from tokens.json.</p>{svg}</div>'
    page(f"mock-anatomy-{theme.name}", body, W, H, theme, "Node anatomy", scale=1)

# ------------------------------------------------------------------ states sheet
def build_states(theme):
    base = lambda **kw: dict(dict(w=192, title="Extrude", cat="shape", icon="box",
                                  outputs=[dict(name="Solids", kind="shapes", count="24")],
                                  inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Height", kind="number", value="12", unit="m")]), **kw)
    items = [("Normal", base(id="a")), ("Selected", base(id="b", selected=True)), ("Error", base(id="c", state="error", message=["Height must be above 0."], action="Show the 3 plots")),
             ("Warning", base(id="d", state="warning")), ("Running", base(id="e", state="running")), ("Paused", base(id="f", state="paused", badges=["breakpoint"])),
             ("Out of date", base(id="g", state="stale")), ("Disabled", base(id="h", state="disabled")), ("Bypassed", base(id="i", state="bypass"))]
    parts = []
    for i, (label, n) in enumerate(items):
        n["x"] = 40 + (i % 5) * 240
        n["y"] = 70 + (i // 5) * 230
        parts.append(f'<text x="{n["x"]}" y="{n["y"] - 14}" font-size="12" font-weight="600" fill="{theme["text-muted"]}">{label}</text>')
    model = dict(nodes=[n for _, n in items], wires=[], groups=[])
    svg = F.canvas(model, theme, 1240, 560, extra_top="".join(parts))
    page(f"mock-states-{theme.name}", f'<div style="width:1240px;height:560px">{svg}</div>', 1240, 560, theme, "Node states")

# ------------------------------------------------------------------ before / after pairs
def pair(name, before, afters, caption, heights=None):
    figs = [f'<figure><figcaption><span class="tag">Before</span>{esc(caption[0])}</figcaption><img src="../../../briefs/C19-images/{before}"></figure>']
    for png, cap in afters:
        figs.append(f'<figure><figcaption><span class="tag after">After</span>{esc(cap)}</figcaption><img src="{png}"></figure>')
    body = f'<div class="pair">{"".join(figs)}</div>'
    return body

def build_pairs():
    specs = [
        ("pair-01-whole-window", "01-whole-window.png", [("png/after-01-whole-window.png", "Whole window")], "Whole window", True),
        ("pair-02-error-node", "02-error-node.png", [("png/after-02-error.png", "Error node, same content")], "Error node", False),
        ("pair-02b-small-flow", "02-error-node.png", [("png/mock-small-flow-dark.png", "Small flow: 7 nodes, one error, one typed value")], "Error node", False),
        ("pair-03-zoomed-out", "03-zoomed-out-overlap.png", [("png/after-03-zoomed-out.png", "Same nodes at 50 percent")], "Zoomed out", False),
        ("pair-04-paused", "04-breakpoint-paused.png", [("png/after-04-paused.png", "Paused at a breakpoint")], "Paused", False),
        ("pair-05-500-nodes", "05-500-nodes.png", [("png/after-05-500-nodes-100.png", "500 nodes at 100 percent"), ("png/after-05-500-nodes-30.png", "500 nodes at 30 percent")], "500 nodes", False),
        ("pair-06-one-node", "06-one-node.png", [("png/after-06-one-node.png", "One Number node, typed value")], "One node", False),
        ("pair-07-hover", "07-hover-thumbnail.png", [("png/after-07-hover.png", "Hover card")], "Hover thumbnail", False),
    ]
    sizes = {"01-whole-window.png": (1440, 900)}
    for name, before, afters, cap, vertical in specs:
        body = pair(name, before, afters, (cap,))
        if vertical:
            body = body.replace('class="pair"', 'class="pair pairs-col"')
            w, h = 1440 + 48, 900 * 2 + 24 + 48 + 56
        else:
            w = 24 + (600 + 24) * (1 + len(afters)) + (600 if "small-flow" in name else 0)
            h = 760 + 48 + 28 + 10 if "small-flow" in name else 728 + 48 + 28 + 10
        page(name, body, w, h, DARK, cap)

def build_light_pair():
    body = ('<div class="pair"><figure><figcaption><span class="tag after">Dark</span>Small flow</figcaption><img src="png/mock-small-flow-dark.png"></figure>'
            '<figure><figcaption><span class="tag after">Light</span>Same flow, light theme</figcaption><img src="png/mock-small-flow-light.png"></figure></div>')
    page("pair-dark-light", body, 24 + 2 * (1200 + 24), 760 + 48 + 38, DARK, "Dark and light")

if __name__ == "__main__":
    build_small_flow(DARK, "mock-small-flow-dark")
    build_small_flow(LIGHT, "mock-small-flow-light")
    build_window(DARK, "after-01-whole-window")
    build_window(LIGHT, "mock-whole-window-light")
    build_error_pair(DARK)
    build_zoomed_pair(DARK)
    build_paused_pair(DARK)
    build_one_node(DARK)
    build_hover_pair(DARK)
    build_500(DARK)
    build_zoom_sheet(DARK)
    build_zoom_sheet(LIGHT)
    build_anatomy(DARK)
    build_anatomy(LIGHT)
    build_states(DARK)
    build_states(LIGHT)
    # pairs must render after their parts
    build_pairs()
    build_light_pair()
    (ROOT / "tools" / "manifest.json").write_text(json.dumps(MANIFEST, indent=1), encoding="utf-8")
    print(len(MANIFEST), "pages")
