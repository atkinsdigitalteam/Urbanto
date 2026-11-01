"""Build the C21 mockups: the script node with its editor (Python dark, C# light) and the text-and-blocks editor (dark, light).

Uses the C19 tokens (tools/c19-tokens.json, mockups/tokens.css), chrome (mockups/chrome.css), flowsvg.py, plus mockups/c21.css.
Run: python3 build_c21.py && node render.js
"""
import json, pathlib, html, re
import flowsvg as F

ROOT = F.ROOT
OUT = ROOT / "mockups"
TOK = F.TOK
MANIFEST = []

def esc(s):
    return html.escape(str(s), quote=False)

def rgba(h, a):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"

def ic(name, size=16, color="currentColor", stroke=1.75):
    src = (F.ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
    src = src.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')
    src = src.replace('stroke-width="2"', f'stroke-width="{stroke}"').replace('stroke="currentColor"', f'stroke="{color}"')
    return f'<span class="icon" style="width:{size}px;height:{size}px">{src}</span>'

def page(name, body, theme, w=1440, h=900, title=""):
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{esc(title or name)}</title>
<link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="chrome.css"><link rel="stylesheet" href="c21.css">
<style>html,body{{width:{w}px;height:{h}px;overflow:hidden}}
.seg span.icon,.tabs span.icon,.doctabs span.icon{{padding:0!important;background:none!important;box-shadow:none!important}} .seg > span{{gap:6px}}</style></head>
<body class="theme-{theme}">{body}</body></html>
"""
    (OUT / f"{name}.html").write_text(doc, encoding="utf-8")
    MANIFEST.append({"html": f"{name}.html", "png": f"png/{name}.png", "width": w, "height": h})

RAIL = ["vector", "vector-bezier-2", "line-dashed", "polygon", "box", "shape", "ruler-measure", "resize",
        "layout-grid", "route", "stack", "lasso", "crosshair", "tag", "table", "calculator", "typography",
        "building-community", "grid-dots", "selector", "versions", "database", "photo", "settings"]

def appbar(c, title):
    menus = "".join(f'<span class="menu">{m}</span>' for m in "File Edit View Map Draw Points Curves Regions Massing Transform Blocks Annotate Analyse Help".split())
    return f"""<div class="appbar"><span class="brand"><span class="dot">{ic('building-community', 13, c['text-on-accent'])}</span>Urbanto Studio</span>{menus}
    <span class="title"><b>{esc(title)}</b> · edited</span>
    <span class="appright"><span class="pill">{ic('layout-grid', 14)} Drafting {ic('chevron-down', 14)}</span><span class="tb-btn">{ic('search', 16)}</span></span></div>"""

def rail(on=9):
    return '<div class="rail">' + "".join(f'<span class="tool {"on" if i == on else ""}">{ic(n, 18)}</span>' + ("<hr>" if i in (7, 15) else "") for i, n in enumerate(RAIL)) + "</div>"

def status(c, text):
    return f"""<div class="status"><span>{esc(text)}</span><span class="spacer"></span><span class="group"><span class="on">OSNAP</span><span>ORTHO</span><span>SNAP</span></span><span>Scale 1:500</span></div>"""

# ------------------------------------------------------------------ tiny highlighter for the mockups
PY_KW = {"import", "as", "for", "in", "if", "else", "return", "def", "while", "not", "and", "or", "from", "None", "True", "False"}
CS_KW = {"var", "foreach", "in", "for", "int", "double", "new", "return", "if", "else", "using", "while"}
URB_KW = {"let", "repeat", "until", "max", "time", "state", "next", "end", "for", "each", "in", "yield", "if", "else", "fn", "collect", "times"}

def highlight(line, lang, inputs=()):
    if lang == "py" and line.lstrip().startswith("#") or lang == "cs" and line.lstrip().startswith("//") or lang == "urb" and line.lstrip().startswith("#"):
        return f'<span class="com">{esc(line)}</span>'
    kws = {"py": PY_KW, "cs": CS_KW, "urb": URB_KW}[lang]
    out = []
    for tok in re.findall(r'f?"[^"]*"|\$"[^"]*"|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|\s+|.', line):
        if tok.startswith(('"', 'f"', '$"')):
            out.append(f'<span class="str">{esc(tok)}</span>')
        elif re.fullmatch(r"\d+(?:\.\d+)?", tok):
            out.append(f'<span class="num">{esc(tok)}</span>')
        elif tok in kws:
            out.append(f'<span class="kw">{esc(tok)}</span>')
        elif tok in inputs:
            out.append(f'<span class="inp">{esc(tok)}</span>')
        elif re.fullmatch(r"[A-Z][A-Za-z0-9]*", tok) and lang == "cs" and tok in ("List", "Point", "Math", "Curve"):
            out.append(f'<span class="ty">{esc(tok)}</span>')
        elif re.fullmatch(r"[A-Za-z_]\w*", tok):
            out.append(f'<span class="nm">{esc(tok)}</span>')
        elif tok.strip():
            out.append(f'<span class="op">{esc(tok)}</span>')
        else:
            out.append(tok)
    s = "".join(out)
    # function calls: name followed by "("
    s = re.sub(r'<span class="nm">(\w+)</span>(<span class="op">\(</span>)', r'<span class="fn">\1</span>\2', s)
    return s

def code_lines(lines, lang, inputs, cur=None, marks=None):
    marks = marks or {}
    rows = []
    i = 0
    for ln in lines:
        if ln.startswith("<err>"):
            rows.append(f'<div class="ln errrow"><span class="no"></span><span class="gut"></span><span>{ln[5:]}</span></div>')
            continue
        i += 1
        body = ln if isinstance(ln, str) and ln.startswith("<raw>") else None
        content = ln[5:] if body else highlight(ln, lang, inputs)
        gut = marks.get(i, "")
        rows.append(f'<div class="ln{" cur" if i == cur else ""}"><span class="no">{i}</span><span class="gut">{gut}</span><span>{content}</span></div>')
    return "".join(rows)

# ------------------------------------------------------------------ the Flow canvas with the script node
def script_flow(lang):
    py = lang == "py"
    names = ("curves", "spacing", "offset", "points", "count", "log") if py else ("Curves", "Spacing", "Offset", "Points", "Count", "Log")
    nodes = [
        dict(id="edges", x=24, y=72, w=192, title="Street edges", cat="source", icon="stack-2",
             outputs=[dict(name="Curves", kind="shapes", count="24")], inputs=[dict(name="Layer", kind="text", value="Kerb lines")]),
        dict(id="spacing", x=24, y=184, w=192, title="Spacing", cat="value", icon="adjustments-horizontal",
             outputs=[dict(name="Value", kind="number", count="1")], inputs=[dict(name="Metres", kind="number", slider=dict(min=4, max=20, value=8, unit="m"))]),
        dict(id="script", x=256, y=96, w=216, title="Spread trees", subtitle="Python" if py else "C#", cat="flow", icon="brand-python" if py else "brand-c-sharp",
             outputs=[dict(name=names[3], kind="shapes", count="312"), dict(name=names[4], kind="number", count="1"), dict(name=names[5], kind="text", count="1")],
             inputs=[dict(name=names[0], kind="shapes", wired=True), dict(name=names[1], kind="number", wired=True), dict(name=names[2], kind="number", value="2.5", unit="m")],
             selected=True, badges=["ran"]),
        dict(id="place", x=512, y=120, w=192, title="Place symbol", cat="shape", icon="trees",
             outputs=[dict(name="Blocks", kind="shapes", count="312")], inputs=[dict(name="Points", kind="shapes", wired=True), dict(name="Symbol", kind="text", value="Tree 6 m")]),
    ]
    wires = [dict(**{"from": ("edges", 0), "to": ("script", 0)}, structure="list", state="selected"),
             dict(**{"from": ("spacing", 0), "to": ("script", 1)}, state="selected"),
             dict(**{"from": ("script", 0), "to": ("place", 0)}, structure="list", state="selected")]
    return dict(nodes=nodes, wires=wires, groups=[])

def editor_pane(c, lang):
    py = lang == "py"
    if py:
        lines = [
            "# Spread trees along street edges",
            "import studio as st",
            "",
            "points = []",
            "for edge in curves:",
            "    inner = edge.offset(-offset)       # stay off the kerb",
            "<raw>" + highlight("    n = max(1, int(inner.length // ", "py", ("curves", "spacing", "offset")) + '<span class="squig"><span class="nm">spacng</span></span>' + highlight("))", "py", ()),
            "<err>" + '<span class="inline-err">' + ic("alert-circle", 12, c["danger"]) + "NameError: 'spacng' is not defined. Did you mean 'spacing'?</span>",
            "    for t in st.steps(n, ends=False):",
            "<raw>" + highlight("        points.append(inner.po", "py", ("curves", "spacing", "offset")) + '<span class="caret"></span>',
            "",
            "count = len(points)",
            'log = f"{count} trees on {len(curves)} edges"',
            "print(log)",
        ]
        inputs = ("curves", "spacing", "offset")
        comp = [("ƒ", "point_at(t)", "Point", True), ("ƒ", "points(count)", "list[Point]", False), ("ƒ", "position_at_length(d)", "Point", False), ("ƒ", "polyline()", "Curve", False), ("p", "portion(t0, t1)", "Curve", False)]
        doc = "<code>point_at(t: float) -> Point</code><br>Point at parameter t from 0 to 1 along the curve. Arcs stay exact."
        env = [("Python", "3.13 embedded"), ("env", "studio-default"), ("", "shapely 2.1"), ("", "numpy 2.3")]
        title_icon = "brand-python"
        cons = [('<span class="t">14:02:11</span> <span class="ok">run 6.1 ms</span> points 312, count 1', ""), ("312 trees on 24 edges", ""),
                ('<span class="t">14:02:40</span> <span class="err">not run: 1 problem (line 7)</span>', "")]
        status_text = "Ln 9, Col 31   Python 3.13   Spaces: 4   UTF-8   Last run 6.1 ms"
        err_line = 7
    else:
        lines = [
            "// Spread trees along street edges",
            "var points = new List<Point>();",
            "foreach (var edge in Curves)",
            "{",
            "    var inner = edge.Offset(-Offset);   // stay off the kerb",
            "<raw>" + highlight("    int n = Math.Max(1, (int)(inner.Length / ", "cs", ("Curves", "Spacing", "Offset")) + '<span class="squig"><span class="nm">Spacng</span></span>' + highlight("));", "cs", ()),
            "<err>" + '<span class="inline-err">' + ic("alert-circle", 12, c["danger"]) + "CS0103: 'Spacng' does not exist. Did you mean 'Spacing'?</span>",
            "    for (int i = 0; i < n; i++)",
            "<raw>" + highlight("        points.Add(inner.Po", "cs", ("Curves", "Spacing", "Offset")) + '<span class="caret"></span>',
            "}",
            "Points = points;",
            "Count = points.Count;",
            'Log = $"{Count} trees on {Curves.Count} edges";',
        ]
        inputs = ("Curves", "Spacing", "Offset")
        comp = [("M", "PointAt(double t)", "Point", True), ("M", "PointsAlong(int count)", "List<Point>", False), ("M", "PositionAtLength(double d)", "Point", False), ("M", "ToPolyline()", "Curve", False), ("M", "Portion(double t0, double t1)", "Curve", False)]
        doc = "<code>Point PointAt(double t)</code><br>Point at parameter t from 0 to 1 along the curve. Arcs stay exact."
        env = [("C#", "14"), ("host", ".NET 10 helper"), ("", "Studio.Api 1.0")]
        title_icon = "brand-c-sharp"
        cons = [('<span class="t">14:02:11</span> <span class="ok">compiled 410 ms, run 3.8 ms</span> Points 312, Count 1', ""), ("312 trees on 24 edges", ""),
                ('<span class="t">14:02:40</span> <span class="err">not run: 1 error (line 6)</span>', "")]
        status_text = "Ln 8, Col 28   C# 14   Spaces: 4   UTF-8   Last run 3.8 ms"
        err_line = 6
    marks = {err_line: ic("alert-circle", 13, c["danger"])}
    comp_html = "".join(f'<div class="it{" on" if on else ""}"><span class="kindglyph" style="background:{rgba(c["cat-flow"], 0.2)};color:{c["cat-flow"]}">{k}</span><span class="mono">{esc(n)}</span><span class="sig">{esc(t)}</span></div>' for k, n, t, on in comp)
    ports = [("in", "shapes", inputs[0], "Shapes", "list"), ("in", "number", inputs[1], "Number (m)", "item"), ("in", "number", inputs[2], "Number (m)", "item"),
             ("out", "shapes", "points" if py else "Points", "Shapes", "list"), ("out", "number", "count" if py else "Count", "Number", "item"), ("out", "text", "log" if py else "Log", "Text", "item")]
    port_rows = "".join(f'<span class="k" style="background:{c["kind-" + k]}"></span><span class="n">{"→ " if d == "out" else ""}{esc(n)}</span><span class="t">{t}</span><span class="a">{a}</span>' for d, k, n, t, a in ports)
    env_html = "".join(f'<span class="envchip">{(f"<b>{a}</b> " if a else "")}{esc(b)}</span>' for a, b in env)
    tile = f'<span class="tile" style="width:22px;height:22px;border-radius:6px;display:grid;place-items:center;background:{rgba(c["cat-flow"], 0.18)}">{ic(title_icon, 14, c["cat-flow"])}</span>'
    return f"""<div class="pane">
  <div class="pane-h"><span class="ttl">{tile}Spread trees <span class="muted">script node</span></span>
    <span class="seg" style="margin-left:8px"><span class="{'on' if py else ''}">Python</span><span class="{'' if py else 'on'}">C#</span></span>
    <span class="spacer"></span><span style="display:inline-flex;align-items:center;gap:6px;color:var(--text-muted);font-size:11px"><span class="toggle"></span>Run on change</span>
    <span class="tb-btn plain">{ic('player-play', 15)} Run node</span><span class="tb-btn">{ic('dots', 16)}</span></div>
  <div class="subbar">{env_html}<span class="envchip">{ic('plus', 12)} Package</span></div>
  <div class="ports"><span></span><span class="h">Port</span><span class="h">Kind</span><span class="h" style="text-align:right">Access</span>{port_rows}</div>
  <div class="code">{code_lines(lines, lang, inputs, cur=9 if py else 8, marks=marks)}
    <div class="complete" style="left:{286 if py else 250}px;top:{8 + 22 + 20 * (9 if py else 8)}px">{comp_html}<div class="doc">{doc}</div></div></div>
  <div class="console"><div class="tabs"><span class="on">Console</span><span>Problems <span class="badge-n">1</span></span><span>Runs</span></div>
    <div class="lines">{"<br>".join(a for a, _ in cons)}</div></div>
  <div class="statusline">{esc(status_text)}</div>
</div>"""

def flow_toolbar(c, name):
    return f"""<div class="toolbar"><span class="flowname">{ic('route', 16, c['text-muted'])} {esc(name)} <span class="muted">{ic('chevron-down', 14)}</span></span>
  <span class="tb-sep"></span><span class="tb-btn primary">{ic('player-play', 16, c['text-on-accent'])} Run</span>
  <span class="seg"><span class="on">Auto</span><span>Manual</span></span><span class="spacer"></span>
  <span class="zoom"><span>{ic('minus', 14)}</span><span class="val">100%</span><span>{ic('plus', 14)}</span></span><span class="tb-btn">{ic('focus-2', 16)}</span></div>"""

def build_script(theme, lang):
    c = TOK["color"][theme]
    T = F.Theme(theme)
    model = script_flow(lang)
    cw, ch = 1440 - 72 - 660, 900 - 40 - 28 - 40
    svg = F.canvas(model, T, cw, ch, zoom=1.0, origin=(0, 0))
    body = f"""<div class="app" style="grid-template-columns:72px 1fr 660px">{appbar(c, "Street trees")}{rail()}
  <div class="split" style="grid-template-rows:40px 1fr;background:var(--canvas)">{flow_toolbar(c, "Street trees")}<div class="canvas" style="position:relative">{svg}</div></div>
  {editor_pane(c, lang)}{status(c, "Script node Spread trees selected")}</div>"""
    body = body.replace('<div class="pane">', '<div class="pane" style="grid-row:2">', 1)
    page(f"c21-script-node-{'python' if lang == 'py' else 'csharp'}-{theme}", body, theme, title="Script node")

# ------------------------------------------------------------------ text and blocks
TEXT = [
    "# Find the number of floors that reaches the target area",
    'let plot = pick("Plot A3")',
    "let target = 18000 m2",
    "",
    "repeat until gfa >= target, max 50, time 5 s",
    "  state floors = 3",
    "  let block = extrude(plot, floors * 3.2 m)",
    "  let gfa = area(plot) * floors",
    "  next floors = floors + 1",
    "end",
    "",
    'report("Floors needed", floors)',
    "<raw>" + highlight("if floors > ", "urb") + '<span class="caret"></span>',
]

def blocks_pane(c):
    gfas = [6300, 8400, 10500, 12600, 14700, 16800, 18900]
    spark = "".join(f'<i class="{"on" if i == 7 else ""}" style="height:{g / 18900 * 16:.0f}px"></i>' for i, g in enumerate(gfas, 1))
    hl = lambda s: f'<div class="bline">{highlight(s, "urb")}</div>'
    hint = lambda s, v: f'<div class="bline">{highlight(s, "urb")}<span class="hint">pass 7 <b>{v}</b></span></div>'
    return f"""<div class="blocks">
  {hl("# Find the number of floors that reaches the target area")}
  {hl('let plot = pick("Plot A3")')}
  {hl("let target = 18000 m2")}
  <div class="container loop">
    <div class="chead">{ic('repeat', 15, c['cat-flow'])}<span class="kwd">repeat</span><span class="lab">until</span><span class="fieldbox expr">gfa &gt;= target</span>
      <span class="lab">max</span><span class="fieldbox">50 <span class="u">passes</span></span><span class="lab">time</span><span class="fieldbox">5 <span class="u">s</span></span>
      <span class="spacer"></span><span class="lab" style="display:inline-flex;gap:6px;align-items:center"><span class="toggle"></span>Show values</span></div>
    <div class="cbody">
      <div class="bline"><span class="kw">state</span> <span class="nm">floors</span> <span class="op">=</span> <span class="num">3</span><span class="hint">pass 7 <b>9</b></span></div>
      {hint("let block = extrude(plot, floors * 3.2 m)", "1 solid, 28.8 m")}
      {hint("let gfa = area(plot) * floors", "18,900 m²")}
      <div class="bline"><span class="kw">next</span> <span class="nm">floors</span> <span class="op">=</span> <span class="nm">floors</span> <span class="op">+</span> <span class="num">1</span><span class="hint">pass 7 <b>10</b></span></div>
    </div>
    <div class="scrub"><span>Pass</span><div class="bar"><div class="spark">{spark}</div><span class="tgt" style="top:{16 - 18000 / 18900 * 16:.0f}px"></span><span class="rail"></span><span class="fill" style="width:100%"></span><span class="knob" style="left:100%"></span></div>
      <span><b>7 of 7</b> · stopped: gfa 18,900 m² ≥ target · 2.1 ms</span></div>
  </div>
  {hl('report("Floors needed", floors)')}
  <div class="container" style="margin-top:8px">
    <div class="chead"><span class="kwd">if</span><span class="fieldbox expr">floors &gt; <span class="caret"></span></span><span class="lab">typed as text, shown as a container</span></div>
    <div class="cbody" style="border-left-color:var(--border-strong)"><span class="hole">then: type a statement</span></div>
  </div>
</div>"""

def text_pane(c):
    rows = code_lines(TEXT, "urb", (), cur=13)
    return f'<div class="code" style="padding-top:12px">{rows}<div class="complete" style="left:206px;top:{12 + 20 * 13}px;width:300px"><div class="it on"><span class="kindglyph" style="background:{rgba(c["cat-value"], 0.2)};color:{c["cat-value"]}">x</span><span class="mono">target</span><span class="sig">area, 18,000 m²</span></div><div class="it"><span class="kindglyph" style="background:{rgba(c["cat-value"], 0.2)};color:{c["cat-value"]}">x</span><span class="mono">floors</span><span class="sig">number, 9</span></div><div class="it"><span class="kindglyph" style="background:{rgba(c["cat-value"], 0.2)};color:{c["cat-value"]}">x</span><span class="mono">gfa</span><span class="sig">area, 18,900 m²</span></div></div></div>'

def loop_flow_svg(c, theme, w, h):
    T = F.Theme(theme)
    gx, gy, gw, gh = 268, 40, 660, 176
    nodes = [
        dict(id="plot", x=24, y=56, w=176, title="Pick plot", cat="source", icon="crosshair", outputs=[dict(name="Plot", kind="shapes", count="1")], inputs=[]),
        dict(id="target", x=24, y=140, w=176, title="target", cat="value", icon="hash", outputs=[dict(name="Value", kind="number", count="1")], inputs=[dict(name="m²", kind="number", value="18000")]),
        dict(id="mul1", x=gx + 24, y=gy + 40, w=176, title="floors × 3.2 m", cat="value", icon="math-function", outputs=[dict(name="Height", kind="number")], inputs=[dict(name="floors", kind="number", wired=True)]),
        dict(id="ext", x=gx + 236, y=gy + 40, w=176, title="Extrude", cat="shape", icon="box", outputs=[dict(name="Block", kind="shapes")], inputs=[dict(name="Shapes", kind="shapes", wired=True), dict(name="Height", kind="number", wired=True)]),
        dict(id="gfa", x=gx + 448, y=gy + 40, w=188, title="area × floors", cat="measure", icon="ruler-measure", outputs=[dict(name="gfa", kind="number")], inputs=[dict(name="Plot", kind="shapes", wired=True), dict(name="floors", kind="number", wired=True)]),
        dict(id="report", x=gx + gw + 48, y=72, w=176, title="Report", cat="output", icon="file-spreadsheet", outputs=[], inputs=[dict(name="floors", kind="number", wired=True)]),
    ]
    wires = [dict(**{"from": ("plot", 0), "to": ("ext", 0)}), dict(**{"from": ("mul1", 0), "to": ("ext", 1)}),
             dict(**{"from": ("plot", 0), "to": ("gfa", 0)})]
    groups = [dict(title="", color="group-6", x=gx, y=gy, w=gw, h=gh)]
    model = dict(nodes=nodes, wires=wires, groups=groups)
    col = T["cat-flow"]
    num = T["kind-number"]
    fy = gy + 40 + 32 + 4 + 24 + 12          # floors input row of mul1
    ry = 72 + 32 + 4 + 12                    # report input row
    ty = 140 + 32 + 4 + 12                   # target output row
    extra = (f'<text x="{gx + 14}" y="{gy + 20}" font-size="12" font-weight="600" fill="{col}">Loop</text>'
             f'<text x="{gx + 50}" y="{gy + 20}" font-size="11" fill="{T["text-muted"]}">until gfa ≥ target · max 50 passes · 5 s · state floors = 3 · next floors + 1</text>'
             # state input on the loop's left edge feeding floors
             f'<circle cx="{gx}" cy="{fy}" r="5" fill="{num}"/><path d="M{gx} {fy} L{gx + 24} {fy}" stroke="{num}" stroke-width="1.75"/>'
             # feedback: next floors leaves the right edge and returns along the bottom to the state input
             f'<path d="M{gx + gw} {gy + 150} C{gx + gw + 30} {gy + 150}, {gx + gw + 30} {gy + gh + 22}, {gx + gw - 40} {gy + gh + 22} L{gx + 40} {gy + gh + 22} C{gx - 30} {gy + gh + 22}, {gx - 30} {fy}, {gx} {fy}" fill="none" stroke="{num}" stroke-width="1.75" stroke-dasharray="6 4" opacity="0.85"/>'
             f'<text x="{gx + gw / 2}" y="{gy + gh + 18}" text-anchor="middle" font-size="10.5" fill="{T["text-subtle"]}">next floors: fed back to the next pass</text>'
             # loop output floors to Report
             f'<circle cx="{gx + gw}" cy="{ry}" r="5" fill="{num}"/><path d="M{gx + gw} {ry} C{gx + gw + 30} {ry}, {gx + gw + 18} {ry}, {gx + gw + 48} {ry}" fill="none" stroke="{num}" stroke-width="1.75"/>'
             # target feeds the stop condition on the header
             f'<path d="M200 {ty} C 240 {ty}, {gx - 40} {gy + 16}, {gx} {gy + 16}" fill="none" stroke="{num}" stroke-width="1.5" stroke-dasharray="2 4" opacity="0.8"/>'
             f'<circle cx="{gx}" cy="{gy + 16}" r="4" fill="{T["canvas"]}" stroke="{num}" stroke-width="1.5"/>')
    return F.canvas(model, T, w, h, zoom=1.0, origin=(0, 0), extra_top=extra)

def build_blocks(theme):
    c = TOK["color"][theme]
    toolbar = f"""<div class="toolbar"><span class="flowname">{ic('code', 16, c['text-muted'])} massing-search.urbs <span class="muted">Flow Script</span></span>
      <span class="tb-sep"></span><span class="seg"><span>Text</span><span class="on">Text and blocks</span><span>Blocks</span></span>
      <span class="tb-sep"></span><span class="tb-btn primary">{ic('player-play', 16, c['text-on-accent'])} Run</span><span class="spacer"></span>
      <span class="envchip"><span class="syncdot"></span> Text, blocks and Flow in sync</span><span class="tb-btn">{ic('route', 16)} Open as Flow</span></div>"""
    body = f"""<div class="app" style="grid-template-columns:72px 1fr">{appbar(c, "Massing search")}{rail(16)}
  <div class="split" style="grid-template-rows:40px 1fr 268px">{toolbar}
    <div style="display:grid;grid-template-columns:1fr 1fr;min-height:0">
      <div class="pane" style="border-left:0"><div class="pane-h"><span class="ttl">{ic('code', 15)} Text <span class="muted">what you type</span></span></div>{text_pane(c)}</div>
      <div class="pane"><div class="pane-h"><span class="ttl">{ic('layout-rows', 15)} Blocks <span class="muted">the same code, loops as containers</span></span></div>{blocks_pane(c)}</div>
    </div>
    <div class="flowstrip"><span class="lbl">{ic('route', 14)} Flow <span style="font-weight:400;color:var(--text-subtle)">the same code as nodes: the loop is a Loop container</span></span>{loop_flow_svg(c, theme, 1368, 268)}</div>
  </div>{status(c, "Flow Script · 13 lines · last run 2.1 ms")}</div>"""
    page(f"c21-text-and-blocks-{theme}", body, theme, title="Text and blocks")

if __name__ == "__main__":
    build_script("dark", "py")
    build_script("light", "cs")
    build_script("light", "py")
    build_script("dark", "cs")
    build_blocks("dark")
    build_blocks("light")
    (ROOT / "tools" / "manifest.json").write_text(json.dumps(MANIFEST, indent=1), encoding="utf-8")
    print(len(MANIFEST), "pages")
