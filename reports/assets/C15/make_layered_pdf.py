"""Build small layered (Optional Content Group) PDF sheets by hand with pikepdf.

Outputs (written next to this script):
  layered_pdfa2b.pdf         A1 sheet, 7 OCGs, PDF 1.7, PDF/A-2b metadata + sRGB output intent
  layered_pdfa2b_noname.pdf  same file but the default OC configuration has no /Name
                             (a PDF/A-2 rule; shows a typical layer-export pitfall)
  layered_pdfa4.pdf          same drawing as PDF 2.0 with PDF/A-4 metadata, no Info dict

Run:  PYTHONPATH=<dir with pikepdf, Pillow> python3 make_layered_pdf.py
Needs: pikepdf (tested 10.17.0), Pillow (ImageCms for the sRGB ICC profile),
       fontTools, pyproj, and DejaVuSans.ttf (embedded as a subset).
"""
import io
import sys
from pathlib import Path

import pikepdf
from pikepdf import Array, Dictionary, Name, Stream, String
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import ImageCms
from pyproj import Transformer

HERE = Path(__file__).resolve().parent
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
MM = 72.0 / 25.4  # PDF points per millimetre

# A1 landscape (ISO 216): 841 x 594 mm. DDA Circular 400 asks for A1 sheets.
SHEET_W, SHEET_H = 841.0, 594.0
SCALE = 200  # 1:200 -> 1 m on site = 5 mm on paper
M_TO_MM = 1000.0 / SCALE

# Layers: (OCG name, default ON?, print?) -- names follow the AIA/NCS format.
LAYERS = [
    ("G-ANNO-TTLB", True, True),   # border and title block
    ("C-PROP-LINE", True, True),   # plot (property) boundary from the site/affection plan
    ("A-WALL", True, True),        # building footprint
    ("A-AREA-PATT", True, True),   # shaded area diagram (GFA polygons), semi-transparent
    ("A-ANNO-DIMS", True, True),   # dimensions
    ("A-ANNO-TEXT", True, True),   # labels, plot coordinates
    ("G-ANNO-NPLT", False, False), # construction lines: hidden and not printed
]

# ISO 128 line-width series values used here (mm): 0.25 thin, 0.35, 0.5 wide, 0.7.
LW = {"thin": 0.25, "med": 0.35, "wide": 0.5, "xwide": 0.7}


def subset_font(text: str) -> tuple[bytes, TTFont]:
    font = TTFont(str(FONT_PATH))
    opts = subset.Options()
    opts.layout_features = []
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["GSUB", "GPOS", "GDEF", "kern"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    data = buf.getvalue()
    return data, TTFont(io.BytesIO(data))


def font_objects(pdf: pikepdf.Pdf, text: str) -> pikepdf.Object:
    data, tt = subset_font(text)
    upm = tt["head"].unitsPerEm
    k = 1000.0 / upm
    cmap = tt.getBestCmap()
    hmtx = tt["hmtx"]
    widths = []
    for code in range(32, 127):
        g = cmap.get(code)
        widths.append(round(hmtx[g][0] * k) if g else 0)
    head, hhea = tt["head"], tt["hhea"]
    cap = tt["glyf"]["H"].yMax if "H" in tt["glyf"].keys() else hhea.ascent
    fontfile = Stream(pdf, data)
    fontfile.Length1 = len(data)
    desc = pdf.make_indirect(Dictionary(
        Type=Name.FontDescriptor,
        FontName=Name("/ABCDEF+DejaVuSans"),
        Flags=32,  # nonsymbolic
        FontBBox=Array([round(head.xMin * k), round(head.yMin * k),
                        round(head.xMax * k), round(head.yMax * k)]),
        ItalicAngle=0,
        Ascent=round(hhea.ascent * k),
        Descent=round(hhea.descent * k),
        CapHeight=round(cap * k),
        StemV=80,
        FontFile2=pdf.make_indirect(fontfile),
    ))
    return pdf.make_indirect(Dictionary(
        Type=Name.Font, Subtype=Name.TrueType,
        BaseFont=Name("/ABCDEF+DejaVuSans"),
        FirstChar=32, LastChar=126, Widths=Array(widths),
        Encoding=Name.WinAnsiEncoding, FontDescriptor=desc,
    ))


class Ops:
    """Tiny content-stream writer. Coordinates in mm on the sheet."""

    def __init__(self):
        self.out = []

    def raw(self, s):
        self.out.append(s)

    def layer(self, tag):
        self.raw(f"/OC /{tag} BDC")

    def end(self):
        self.raw("EMC")

    def stroke(self, rgb=(0, 0, 0), width_mm=0.25, dash=None):
        self.raw(f"{rgb[0]} {rgb[1]} {rgb[2]} RG {width_mm * MM:.3f} w")
        self.raw(f"[{' '.join(f'{d * MM:.2f}' for d in dash)}] 0 d" if dash else "[] 0 d")

    def poly(self, pts, close=True, fill=False):
        x0, y0 = pts[0]
        self.raw(f"{x0 * MM:.3f} {y0 * MM:.3f} m")
        for x, y in pts[1:]:
            self.raw(f"{x * MM:.3f} {y * MM:.3f} l")
        self.raw(("h " if close else "") + ("B" if fill else "S"))

    def rect(self, x, y, w, h):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])

    def text(self, x, y, s, size_mm=2.5):
        s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        # ISO 3098 style heights: 2.5, 3.5, 5, 7 mm; font size in pt ~ cap height / 0.73
        pt = size_mm * MM / 0.73
        self.raw(f"BT /F1 {pt:.2f} Tf 0 0 0 rg {x * MM:.3f} {y * MM:.3f} Td ({s}) Tj ET")

    def bytes(self):
        return ("\n".join(self.out) + "\n").encode("latin-1")


def build_drawing():
    # Sample plot: 40 m x 30 m, building 26 m x 18 m with 5/6 m setbacks.
    # Plot origin placed at a sample point near Dubai Marina (25.0800 N, 55.1400 E),
    # converted to DLTM (EPSG:3997) and UTM 40N (EPSG:32640) for the coordinate labels.
    to_dltm = Transformer.from_crs(4326, 3997, always_xy=True)
    to_utm = Transformer.from_crs(4326, 32640, always_xy=True)
    e0, n0 = to_dltm.transform(55.1400, 25.0800)
    ue, un = to_utm.transform(55.1400, 25.0800)
    ox, oy = 120.0, 180.0  # sheet position (mm) of the plot origin
    plot = [(0, 0), (40, 0), (40, 30), (0, 30)]
    bldg = [(5, 6), (31, 6), (31, 24), (5, 24)]
    s = lambda p: (ox + p[0] * M_TO_MM, oy + p[1] * M_TO_MM)

    o = Ops()
    # Title block and border
    o.layer("oc0")
    o.stroke(width_mm=LW["xwide"]); o.rect(10, 10, SHEET_W - 20, SHEET_H - 20)
    tb_x, tb_y, tb_w, tb_h = SHEET_W - 10 - 180, 10, 180, 70
    o.stroke(width_mm=LW["wide"]); o.rect(tb_x, tb_y, tb_w, tb_h)
    o.stroke(width_mm=LW["thin"])
    for dy in (14, 28, 42, 56):
        o.poly([(tb_x, tb_y + dy), (tb_x + tb_w, tb_y + dy)], close=False)
    rows = [
        "PROJECT: Sample plot (illustrative)    PLOT No.: 000-0000",
        "DRAWING: A-06-001 Setting-out plan    SCALE 1:200 @ A1",
        "CRS: WGS 84 / Dubai Local TM (EPSG:3997)    UNITS: m",
        "FILE: 7001-URB-ZZ-00-DR-A-06001    STATUS S3  REV P01",
        "CONSULTANT: <name, licence no.>   SIGN/STAMP: <digital>",
    ]
    for i, r in enumerate(reversed(rows)):
        o.text(tb_x + 4, tb_y + 4.5 + 14 * i, r, 3.5)
    o.end()
    # Plot boundary
    o.layer("oc1")
    o.stroke(rgb=(0.8, 0, 0), width_mm=LW["xwide"], dash=(12, 3, 1.5, 3))
    o.poly([s(p) for p in plot])
    o.end()
    # Building footprint
    o.layer("oc2")
    o.stroke(width_mm=LW["wide"]); o.poly([s(p) for p in bldg])
    o.end()
    # Shaded area diagram: semi-transparent fill (transparency = PDF/A-2+ only)
    o.layer("oc3")
    o.raw("q /GS1 gs 0.2 0.5 0.9 rg")
    o.stroke(rgb=(0.2, 0.5, 0.9), width_mm=LW["thin"])
    o.poly([s(p) for p in bldg], fill=True)
    o.raw("Q")
    o.end()
    # Dimensions
    o.layer("oc4")
    o.stroke(width_mm=LW["thin"])
    a, b = s((0, -3)), s((40, -3))
    o.poly([a, b], close=False)
    for p in (a, b):
        o.poly([(p[0], p[1] - 2), (p[0], p[1] + 2)], close=False)
    o.text((a[0] + b[0]) / 2 - 6, a[1] + 1.5, "40.00", 3.5)
    o.end()
    # Text: plot corner coordinates in DLTM
    o.layer("oc5")
    for (x, y), lab in zip(plot, ("P1", "P2", "P3", "P4")):
        px, py = s((x, y))
        o.text(px + 1.5, py + 1.5, f"{lab} E {e0 + x:.3f} N {n0 + y:.3f}", 2.5)
    o.text(ox, oy + 30 * M_TO_MM + 12, "GFA (sample): 26.00 x 18.00 = 468.00 m2", 5)
    o.end()
    # Non-plot construction lines
    o.layer("oc6")
    o.stroke(rgb=(0, 0.6, 0), width_mm=LW["thin"], dash=(3, 2))
    o.poly([s((-5, 15)), s((45, 15))], close=False)
    o.poly([s((20, -5)), s((20, 35))], close=False)
    o.end()
    used = "".join(sorted(set("".join(rows) + "40.00P1234EN.0123456789 GFA(sample):x=m2")))
    return o.bytes(), used, (e0, n0, ue, un)


def build(path: Path, *, pdfa_part: int, d_name: bool):
    content, used_text, coords = build_drawing()
    pdf = pikepdf.new()
    font = font_objects(pdf, used_text + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz<>/,.-_:@0123456789() ")
    ocgs = []
    props = Dictionary()
    for i, (nm, on, prints) in enumerate(LAYERS):
        ocg = Dictionary(Type=Name.OCG, Name=String(nm))
        if not prints:
            ocg.Usage = Dictionary(Print=Dictionary(PrintState=Name.OFF),
                                   View=Dictionary(ViewState=Name.OFF))
        ref = pdf.make_indirect(ocg)
        ocgs.append(ref)
        props[f"/oc{i}"] = ref
    gs = Dictionary(Type=Name.ExtGState, ca=0.35, CA=1.0)
    page = pikepdf.Page(Dictionary(
        Type=Name.Page,
        MediaBox=Array([0, 0, round(SHEET_W * MM, 2), round(SHEET_H * MM, 2)]),
        Resources=Dictionary(Font=Dictionary(F1=font), Properties=props,
                             ExtGState=Dictionary(GS1=gs)),
        Contents=pdf.make_stream(content),
    ))
    pdf.pages.append(page)
    # Layer panel order: grouped with non-selectable text labels (ISO 32000-1 8.11.4.3)
    order = Array([
        Array([String("General"), ocgs[0], ocgs[6]]),
        Array([String("Civil"), ocgs[1]]),
        Array([String("Architectural"), ocgs[2], ocgs[3], ocgs[4], ocgs[5]]),
    ])
    d = Dictionary(Order=order, ON=Array([o for o, l in zip(ocgs, LAYERS) if l[1]]),
                   OFF=Array([o for o, l in zip(ocgs, LAYERS) if not l[1]]),
                   Locked=Array([ocgs[0]]))
    if d_name:
        d.Name = String("Default (plot set)")
    pdf.Root.OCProperties = Dictionary(OCGs=Array(ocgs), D=d)
    pdf.Root.PageMode = Name.UseOC  # open the layers panel
    # Output intent with an sRGB ICC profile (Pillow/littleCMS built-in sRGB)
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    icc_stream = pdf.make_stream(icc)
    icc_stream.N = 3
    pdf.Root.OutputIntents = Array([Dictionary(
        Type=Name.OutputIntent, S=Name.GTS_PDFA1,
        OutputConditionIdentifier=String("sRGB IEC61966-2.1"),
        Info=String("sRGB"), DestOutputProfile=icc_stream)])
    with pdf.open_metadata(set_pikepdf_as_editor=False,
                           update_docinfo=(pdfa_part != 4)) as meta:
        meta["dc:title"] = "Layered sheet sample (C15)"
        meta["xmp:CreatorTool"] = "make_layered_pdf.py (Urbanto C15)"
        meta["pdfaid:part"] = str(pdfa_part)
        if pdfa_part == 4:
            meta["pdfaid:rev"] = "2020"
        else:
            meta["pdfaid:conformance"] = "B"
    if pdfa_part == 4:
        if "/Info" in pdf.trailer:
            del pdf.trailer["/Info"]
        pdf.save(path, force_version="2.0", fix_metadata_version=False,
                 deterministic_id=True)
    else:
        pdf.save(path, force_version="1.7", fix_metadata_version=False,
                 deterministic_id=True)
    return coords


if __name__ == "__main__":
    c = build(HERE / "layered_pdfa2b.pdf", pdfa_part=2, d_name=True)
    build(HERE / "layered_pdfa2b_noname.pdf", pdfa_part=2, d_name=False)
    build(HERE / "layered_pdfa4.pdf", pdfa_part=4, d_name=True)
    e0, n0, ue, un = c
    print(f"Sample origin 25.0800N 55.1400E -> DLTM E {e0:.3f} N {n0:.3f}; "
          f"UTM40N E {ue:.3f} N {un:.3f}")
    for f in ("layered_pdfa2b.pdf", "layered_pdfa2b_noname.pdf", "layered_pdfa4.pdf"):
        print(f, (HERE / f).stat().st_size, "bytes")
