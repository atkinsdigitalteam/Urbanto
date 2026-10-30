"""Build the C6 sample DXF R2000 (AC1015) files with ezdxf 1.4.5 and print the
worked numbers used in the report.

Run:  python3 make_samples.py            (writes ./samples/*.dxf, prints a log)
Then: python3 audit_samples.py           (ezdxf recover + audit on every file)

Units: metres ($INSUNITS = 6, $MEASUREMENT = 1).
"""
from __future__ import annotations

import math
from pathlib import Path

import ezdxf
from ezdxf import path as ezpath
from ezdxf.math import Vec2, arc_to_bulge, bulge_to_arc
from ezdxf.enums import TextEntityAlignment, MTextEntityAlignment

OUT = Path(__file__).resolve().parent / "samples"
OUT.mkdir(exist_ok=True)

# A 30 m x 20 m plot with a 6 m corner splay arc at the street corner.
BULGE_90 = math.tan(math.radians(90) / 4)  # quarter circle, counter-clockwise
PLOT = [(0, 0, 0), (30, 0, 0), (30, 14, BULGE_90), (24, 20, 0), (0, 20, 0)]  # (x, y, bulge)


def new_doc(**kw) -> ezdxf.document.Drawing:
    doc = ezdxf.new("R2000", units=6, **kw)  # AC1015, metres
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LUNITS"] = 2  # decimal
    doc.header["$LUPREC"] = 2
    # ezdxf 1.4.5 writes $DIMSTYLE = "ISO-25" although only "Standard" exists in the
    # DIMSTYLE table; ezdxf audit does not flag it, ACadSharp's writer throws on it.
    doc.header["$DIMSTYLE"] = "Standard"
    return doc


def save(doc, name: str) -> Path:
    p = OUT / name
    doc.saveas(p)
    print(f"  wrote {p.name} ({p.stat().st_size:,} bytes, {doc.dxfversion})")
    return p


# ---------------------------------------------------------------- 01 minimum
def sample_01_minimum():
    print("01 minimum file written by ezdxf.new('R2000')")
    raw = ezdxf.new("R2000")
    print(f"  ezdxf.new('R2000') defaults: $DIMSTYLE = {raw.header['$DIMSTYLE']!r}, "
          f"DIMSTYLE table = {[d.dxf.name for d in raw.dimstyles]}")
    doc = new_doc()
    doc.modelspace().add_line((0, 0), (25, 0))
    save(doc, "01-minimum-ezdxf-R2000.dxf")
    print("  tables:", {t: len(getattr(doc, t)) for t in
                        ("layers", "linetypes", "styles", "dimstyles", "appids",
                         "ucs", "views", "viewports", "block_records")})
    print("  root dictionary keys:", list(doc.rootdict.keys()))
    print("  header variables written:", len(list(doc.header.varnames())))


# ---------------------------------------------------------------- 02 bulges
def sample_02_bulges():
    print("02 LWPOLYLINE bulges")
    # Worked arc: quarter circle radius 10 about (0,0), from (10,0) to (0,10), CCW.
    theta = math.radians(90)
    b = math.tan(theta / 4)
    centre, sa, ea, r = bulge_to_arc((10, 0), (0, 10), b)
    chord = math.dist((10, 0), (0, 10))
    sagitta = r - r * math.cos(theta / 2)
    print(f"  bulge = tan(90 deg / 4) = tan(22.5 deg) = {b:.9f}")
    print(f"  bulge_to_arc -> centre {centre}, start {math.degrees(sa):.3f} deg, "
          f"end {math.degrees(ea):.3f} deg, radius {r:.6f}")
    print(f"  check via sagitta: chord {chord:.6f}, sagitta {sagitta:.6f}, "
          f"2*s/c = {2 * sagitta / chord:.9f}")
    s, e, b2 = arc_to_bulge((0, 0), 0, math.pi / 2, 10)
    print(f"  arc_to_bulge(centre (0,0), 0..90 deg, r 10) -> {s}, {e}, bulge {b2:.9f}")
    # Semicircles: +1 counter-clockwise, -1 clockwise.
    for bb in (1.0, -1.0):
        c, a0, a1, rr = bulge_to_arc((40, 0), (50, 0), bb)
        # independent check: flatten the one-segment polyline and take its middle point
        tmp = ezdxf.new("R2000").modelspace().add_lwpolyline([(40, 0, bb), (50, 0, 0)], format="xyb")
        pts = list(ezpath.make_path(tmp).flattening(0.001))
        print(f"  bulge {bb:+.0f} from (40,0) to (50,0): centre {Vec2(c).round(6)}, r {rr}, "
              f"arc passes through {Vec2(pts[len(pts) // 2]).round(3)}")

    doc = new_doc()
    msp = doc.modelspace()
    doc.layers.add("PLOT", color=7)
    doc.layers.add("WORKED-ARC", color=1)
    msp.add_lwpolyline([(10, 0, b), (0, 10, 0)], format="xyb", dxfattribs={"layer": "WORKED-ARC"})
    msp.add_lwpolyline([(40, 0, 1.0), (50, 0, 0)], format="xyb", dxfattribs={"layer": "WORKED-ARC"})
    msp.add_lwpolyline([(40, -5, -1.0), (50, -5, 0)], format="xyb", dxfattribs={"layer": "WORKED-ARC"})
    plot = msp.add_lwpolyline(PLOT, format="xyb", close=True, dxfattribs={"layer": "PLOT"})
    save(doc, "02-lwpolyline-bulges.dxf")

    # Area of the plot: analytic vs flattened polyline.
    analytic = 30 * 20 - (6 * 6 - math.pi * 6 * 6 / 4)
    pts = list(ezpath.make_path(plot).flattening(0.0005))
    shoelace = 0.5 * abs(sum(p.x * q.y - q.x * p.y for p, q in zip(pts, pts[1:] + pts[:1])))
    print(f"  plot area analytic 600 - (36 - 9*pi) = {analytic:.4f} m2; "
          f"flattened ({len(pts)} pts, 0.5 mm sagitta) = {shoelace:.4f} m2")


# ---------------------------------------------------------------- 03 hatch
def sample_03_hatch():
    print("03 HATCH")
    doc = new_doc()
    msp = doc.modelspace()
    doc.layers.add("HATCH-PLOT", color=3)
    doc.layers.add("HATCH-PLAZA", color=1)
    # 1. Solid fill, polyline boundary path with a bulge (the plot).
    h1 = msp.add_hatch(color=256, dxfattribs={"layer": "HATCH-PLOT"})
    h1.set_solid_fill(color=256, style=0)
    h1.paths.add_polyline_path([(x, y, b) for x, y, b in PLOT], is_closed=True, flags=1 | 16)
    # 2. Pattern fill, edge boundary path (lines + arc) with a circular hole (island).
    h2 = msp.add_hatch(color=256, dxfattribs={"layer": "HATCH-PLAZA"})
    h2.set_pattern_fill("ANSI31", color=256, scale=0.5, angle=0, style=0)  # style 0 = normal (odd parity)
    outer = h2.paths.add_edge_path(flags=1)  # external
    outer.add_line((40, 0), (60, 0))
    outer.add_line((60, 0), (60, 10))
    outer.add_arc(center=(50, 10), radius=10, start_angle=0, end_angle=180, ccw=True)
    outer.add_line((40, 10), (40, 0))
    hole = h2.paths.add_edge_path(flags=0)  # default = inner loop
    hole.add_arc(center=(50, 8), radius=3, start_angle=0, end_angle=360, ccw=True)
    h2.set_seed_points([(42, 2)])
    save(doc, "03-hatch.dxf")
    print(f"  plaza net area analytic 20*10 + pi*10^2/2 - pi*3^2 = "
          f"{200 + math.pi * 100 / 2 - math.pi * 9:.4f} m2")
    print(f"  ANSI31 pattern definition lines written: {len(h2.pattern.lines)}")


# ---------------------------------------------------------------- 04 dimensions
def urb500(doc):
    """Metric dimension style for a 1:500 plan drawn in metres.
    Paper sizes in mm; DIMSCALE 0.5 turns 2.5 mm text into 1.25 m in the model."""
    ds = doc.dimstyles.new("URB500")
    ds.dxf.dimscale = 0.5
    ds.dxf.dimtxt = 2.5
    ds.dxf.dimasz = 2.5
    ds.dxf.dimexe = 1.25
    ds.dxf.dimexo = 0.625
    ds.dxf.dimgap = 0.625
    ds.dxf.dimdec = 2       # 2 decimals
    ds.dxf.dimadec = 2      # angular decimals
    ds.dxf.dimlunit = 2     # decimal
    ds.dxf.dimaunit = 0     # decimal degrees
    ds.dxf.dimzin = 0       # keep trailing zeros: 30.00
    ds.dxf.dimdsep = ord(".")  # decimal point, not comma
    ds.dxf.dimtad = 1       # text above the dimension line
    ds.dxf.dimtih = 0       # text aligned with the dimension line
    ds.dxf.dimtoh = 0
    ds.dxf.dimtxsty = "Standard"
    ds.dxf.dimclrd = 256
    ds.dxf.dimclre = 256
    ds.dxf.dimclrt = 256
    return ds


def sample_04_dimensions():
    print("04 DIMENSION")
    doc = new_doc(setup=False)
    urb500(doc)
    doc.header["$DIMSTYLE"] = "URB500"
    msp = doc.modelspace()
    doc.layers.add("PLOT", color=7)
    doc.layers.add("DIM", color=2)
    msp.add_lwpolyline(PLOT, format="xyb", close=True, dxfattribs={"layer": "PLOT"})
    msp.add_line((40, 0), (55, 0), dxfattribs={"layer": "PLOT"})
    msp.add_line((40, 0), (52, 9), dxfattribs={"layer": "PLOT"})
    msp.add_circle((50, 30), 3, dxfattribs={"layer": "PLOT"})
    a = {"layer": "DIM"}
    dims = [
        ("linear horizontal (frontage)", msp.add_linear_dim(base=(15, -5), p1=(0, 0), p2=(30, 0), dimstyle="URB500", dxfattribs=a)),
        ("linear vertical (depth)", msp.add_linear_dim(base=(-5, 10), p1=(0, 0), p2=(0, 20), angle=90, dimstyle="URB500", dxfattribs=a)),
        ("aligned (12 m by 9 m boundary)", msp.add_aligned_dim(p1=(40, 0), p2=(52, 9), distance=3, dimstyle="URB500", dxfattribs=a)),
        ("radius (corner splay)", msp.add_radius_dim(center=(24, 14), radius=6, angle=45, dimstyle="URB500", dxfattribs=a)),
        ("diameter (fountain)", msp.add_diameter_dim(center=(50, 30), radius=3, angle=30, dimstyle="URB500", dxfattribs=a)),
        ("angular 2-line", msp.add_angular_dim_2l(base=(40 + 8 * math.cos(math.radians(18)), 8 * math.sin(math.radians(18))),
                                                  # ezdxf 1.4.5 draws the acute arc and "36.87" text
                                                  # with the skew leg as line1 (tested: the other
                                                  # order draws the 323.13 deg reflex angle)
                                                  line1=((40, 0), (52, 9)), line2=((40, 0), (55, 0)),
                                                  dimstyle="URB500", dxfattribs=a)),
        ("angular 3-point", msp.add_angular_dim_3p(base=(4, 4), center=(0, 0), p1=(30, 0), p2=(0, 20),
                                                   dimstyle="URB500", dxfattribs=a)),
    ]
    for label, ov in dims:
        ov.render()
        d = ov.dimension
        blk = doc.blocks.get(d.dxf.geometry)
        kinds = {}
        for e in blk:
            kinds[e.dxftype()] = kinds.get(e.dxftype(), 0) + 1
        text = next((e.text for e in blk if e.dxftype() == "MTEXT"), "")
        print(f"  {label:32s} code70={d.dxf.dimtype:3d} measurement={d.get_measurement() if not isinstance(d.get_measurement(), Vec2) else d.get_measurement()!s:>12} "
              f"block={d.dxf.geometry} {kinds} text='{text}'")
    # Hand check of the aligned dimension: direction (12,9)/15, normal (-0.6, 0.8).
    al = dims[2][1].dimension
    print(f"  aligned defpoint 10 = {Vec2(al.dxf.defpoint).round(4)} (hand: p1 + 3*(-0.6,0.8) = (38.2, 2.4)); "
          f"13 = {Vec2(al.dxf.defpoint2)}, 14 = {Vec2(al.dxf.defpoint3)}; length sqrt(12^2+9^2) = {math.hypot(12, 9)}")
    ang = dims[5][1].dimension
    arc = next(e for e in doc.blocks.get(ang.dxf.geometry) if e.dxftype() == "ARC")
    print(f"  angular 2-line: atan2(9,12) = {math.degrees(math.atan2(9, 12)):.4f} deg; "
          f"block ARC {arc.dxf.start_angle:.2f}..{arc.dxf.end_angle:.2f} deg r {arc.dxf.radius:.3f}; "
          f"get_measurement() = {ang.get_measurement():.4f} (ezdxf API quirk, see report)")
    for code, attr in ((10, "defpoint"), (13, "defpoint2"), (14, "defpoint3"), (15, "defpoint4"), (16, "defpoint5")):
        print(f"    angular code {code}: {Vec2(ang.dxf.get(attr)).round(3)}")
    save(doc, "04-dimensions.dxf")

    # Negative test: same linear dimension, but the block is never rendered.
    doc2 = new_doc()
    urb500(doc2)
    ov = doc2.modelspace().add_linear_dim(base=(15, -5), p1=(0, 0), p2=(30, 0), dimstyle="URB500")
    # no ov.render(): the DIMENSION has no geometry block
    print(f"  unrendered dimension: geometry block name = {ov.dimension.dxf.get('geometry')!r}")
    save(doc2, "04b-dimension-without-block.dxf")


# ---------------------------------------------------------------- 05 Arabic
AR_TEXT = "مخطط رئيسي - قطعة 12"         # "Masterplan - plot 12": RTL with LTR digits
AR_MTEXT = "المنطقة السكنية\\Pمساحة القطعة: 592.27 م²"  # "Residential zone / Plot area: 592.27 m2"


def arabic_doc(codepage: str, version: str = "R2000"):
    doc = ezdxf.new(version, units=6)
    # ezdxf rewrites $DWGCODEPAGE from doc.encoding on save, so set the encoding:
    doc.encoding = {"ANSI_1256": "cp1256", "ANSI_1252": "cp1252"}[codepage]
    doc.header["$DIMSTYLE"] = "Standard"
    st = doc.styles.new("ARABIC", dxfattribs={"font": "arial.ttf"})
    st.set_extended_font_data(family="Arial", italic=False, bold=False)
    return doc


def add_arabic(doc, text: str, mtext: str):
    msp = doc.modelspace()
    t = msp.add_text(text, height=2.5, dxfattribs={"style": "ARABIC"})
    t.set_placement((30, 0), align=TextEntityAlignment.BOTTOM_RIGHT)  # right-aligned
    m = msp.add_mtext(mtext, dxfattribs={"style": "ARABIC", "char_height": 2.0, "width": 40})
    m.set_location((30, -5), attachment_point=MTextEntityAlignment.TOP_RIGHT)


def raw_line(p: Path, needle_code: str, after: str):
    """Return the raw bytes of the first value line for group code needle_code
    found after the line `after`."""
    lines = p.read_bytes().split(b"\r\n") if b"\r\n" in p.read_bytes() else p.read_bytes().split(b"\n")
    seen = False
    for i, ln in enumerate(lines):
        if ln.strip() == after.encode():
            seen = True
        if seen and ln.strip() == needle_code.encode():
            return lines[i + 1]
    return b""


def sample_05_arabic():
    print("05 Arabic TEXT / MTEXT")
    import arabic_reshaper
    from bidi.algorithm import get_display

    variants = [
        ("05a-arabic-ansi1256.dxf", "ANSI_1256", "R2000", AR_TEXT, AR_MTEXT),
        ("05b-arabic-ansi1252-uplus.dxf", "ANSI_1252", "R2000", AR_TEXT, AR_MTEXT),
        ("05c-arabic-preshaped-visual.dxf", "ANSI_1256", "R2000",
         get_display(arabic_reshaper.reshape(AR_TEXT)), AR_MTEXT),
        ("05d-arabic-R2007-utf8.dxf", "ANSI_1256", "R2007", AR_TEXT, AR_MTEXT),
    ]
    for name, cp, ver, text, mtext in variants:
        doc = arabic_doc(cp, ver)
        add_arabic(doc, text, mtext)
        p = save(doc, name)
        raw = raw_line(p, "1", "TEXT")
        print(f"    $DWGCODEPAGE={cp}; TEXT code 1 raw bytes: {raw[:60]!r}{'...' if len(raw) > 60 else ''}")
        cp_written = raw_line(p, "3", "$DWGCODEPAGE")
        print(f"    $DWGCODEPAGE in file: {cp_written!r}")
        from ezdxf import recover
        for label, back in (("readfile", ezdxf.readfile(p)), ("recover.readfile", recover.readfile(p)[0])):
            t = back.modelspace().query("TEXT").first
            print(f"    {label:16s} TEXT equals written: {t.dxf.text == text}; first code points: "
                  f"{' '.join(f'U+{ord(c):04X}' for c in t.dxf.text[:4])}")
    print(f"  logical order (stored):  {' '.join(f'U+{ord(c):04X}' for c in AR_TEXT[:5])} ...")
    shaped = get_display(arabic_reshaper.reshape(AR_TEXT))
    print(f"  pre-shaped visual order: {' '.join(f'U+{ord(c):04X}' for c in shaped[:5])} ...")
    enc_ok = all(c.encode("cp1256", errors="strict") for c in AR_TEXT)
    try:
        shaped.encode("cp1256")
        print("  presentation forms fit cp1256: yes")
    except UnicodeEncodeError as exc:
        print(f"  presentation forms fit cp1256: no ({exc.reason} at U+{ord(shaped[exc.start]):04X})")
    print(f"  logical Arabic fits cp1256: {enc_ok}")


# ---------------------------------------------------------------- 06 plot styles
def plot_layers(doc):
    msp = doc.modelspace()
    doc.layers.add("PLOT-BOUNDARY", color=7, lineweight=50)
    doc.layers.add("ROADS", color=8, lineweight=25)
    msp.add_lwpolyline(PLOT, format="xyb", close=True, dxfattribs={"layer": "PLOT-BOUNDARY"})
    msp.add_line((-10, -6), (40, -6), dxfattribs={"layer": "ROADS"})
    msp.add_line((-10, -12), (40, -12), dxfattribs={"layer": "ROADS", "color": 1})


def set_style_sheet(doc, sheet: str):
    for name in ("Model", "Layout1"):
        lay = doc.layouts.get(name)
        lay.dxf_layout.dxf.current_style_sheet = sheet
        lay.dxf_layout.dxf.plot_layout_flags |= 32  # PlotPlotStyles


def sample_06_plotstyles():
    print("06 plot styles")
    # CTB: colour-dependent. Pen settings come from the ACI colour of each object.
    doc = new_doc()
    doc.header["$PSTYLEMODE"] = 1
    plot_layers(doc)
    set_style_sheet(doc, "monochrome.ctb")
    save(doc, "06a-plotstyles-ctb.dxf")

    # STB: named plot styles held in the ACAD_PLOTSTYLENAME dictionary.
    doc = new_doc()
    doc.header["$PSTYLEMODE"] = 0
    plot_layers(doc)
    psd = doc.rootdict["ACAD_PLOTSTYLENAME"]  # ACDBDICTIONARYWDFLT, default entry "Normal"
    handles = {}
    for name in ("Road-Edge", "Plot-Boundary"):
        ph = doc.objects.add_placeholder(owner=psd.dxf.handle)
        psd[name] = ph
        handles[name] = ph.dxf.handle
    doc.layers.get("ROADS").dxf.plotstyle_handle = handles["Road-Edge"]
    doc.layers.get("PLOT-BOUNDARY").dxf.plotstyle_handle = handles["Plot-Boundary"]
    set_style_sheet(doc, "acad.stb")
    p = save(doc, "06b-plotstyles-stb.dxf")
    print(f"  ACAD_PLOTSTYLENAME entries: { {k: v.dxf.handle for k, v in psd.items()} }, default -> {psd.dxf.default}")
    for lay in doc.layers:
        print(f"    layer {lay.dxf.name!r:16} code 390 -> {lay.dxf.get('plotstyle_handle')}")

    # Same drawing saved as R2007: ezdxf writes entity-level 380/390 only for AC1021+.
    doc.dxfversion = "AC1021"
    ln = doc.modelspace().query("LINE[color==1]").first
    ln.dxf.plotstyle_enum = 3  # 3 = by object handle
    ln.dxf.plotstyle_handle = handles["Plot-Boundary"]
    save(doc, "06c-plotstyles-stb-entity390-R2007.dxf")


if __name__ == "__main__":
    print(f"ezdxf {ezdxf.__version__}")
    sample_01_minimum()
    sample_02_bulges()
    sample_03_hatch()
    sample_04_dimensions()
    sample_05_arabic()
    sample_06_plotstyles()
