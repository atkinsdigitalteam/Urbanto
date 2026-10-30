"""Write a tiny Abu Dhabi (ADM SDD v1.18.2) style plot DXF with ezdxf and self-check it.

What it shows:
  * DXF R2010 header ($ACADVER AC1024) = the AutoCAD 2010-2012 file generation, i.e.
    "not later than 2012" as the SDD spec asks (the spec asks for DWG; converting DXF to
    DWG needs an external converter such as ODA File Converter, not tested here).
  * SDD layer names, ACI colours and lineweights for the PLOT file (Table 5).
  * 1 drawing unit = 1 metre, coordinates in WGS 84 / UTM 40N (EPSG:32640).
  * A mini QC for a few SDD data-capturing rules: closed LWPOLYLINE only, no arcs /
    splines / ellipses / hatches, attribute-block insertion point inside its polygon,
    and the SDD file-name pattern.
Run: python3 adm_sdd_check.py   (ezdxf 1.4.5, shapely, pyproj)
"""
import re
from pathlib import Path

import ezdxf
from pyproj import Transformer
from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent
NAME = "P11_20261030_AP_Plot_ADM.dxf"  # <ProjectID>_<YYYYMMDD>_<AP/MP>_<theme>_<ADM/DOT>
NAME_RE = re.compile(r"^[A-Za-z0-9]+_\d{8}_(AP|MP)_(Plot|Roads|Services|additional)_(ADM|DOT)\.dwg$",
                     re.IGNORECASE)

# SDD Table 5 (PLOT drawing layers): name -> (ACI colour, lineweight in 1/100 mm)
SDD_PLOT_LAYERS = {
    "Plot": (51, 25), "PlotDetail": (51, 25), "Sector": (3, 30), "SectorDetail": (3, 25),
    "Zone": (7, 40), "ZoneDetail": (7, 25), "DimensionLine": (7, 25), "Title": (7, 25),
}


def build():
    doc = ezdxf.new("R2010", setup=False)
    doc.header["$INSUNITS"] = 6  # metres
    doc.header["$MEASUREMENT"] = 1  # metric
    for name, (aci, lw) in SDD_PLOT_LAYERS.items():
        doc.layers.add(name, color=aci, lineweight=lw, linetype="Continuous")
    blk = doc.blocks.new("PlotDetail")
    for i, tag in enumerate(("PlotNumber", "SectorNumber", "UsageCategoryType", "UsageType")):
        blk.add_attdef(tag, insert=(0, -i * 1.5), dxfattribs={"height": 1.0})
    msp = doc.modelspace()
    # Sample plot origin in Abu Dhabi city (24.4539 N, 54.3773 E) -> UTM 40N metres
    e, n = Transformer.from_crs(4326, 32640, always_xy=True).transform(54.3773, 24.4539)
    pts = [(e, n), (e + 30, n), (e + 30, n + 25), (e, n + 25)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "Plot"})
    ref = msp.add_blockref("PlotDetail", (e + 15, n + 12.5), dxfattribs={"layer": "PlotDetail"})
    ref.add_auto_attribs({"PlotNumber": "C2-0001", "SectorNumber": "C2",
                          "UsageCategoryType": "Residential", "UsageType": "Villa"})
    path = HERE / "sample_adm_plot.dxf"
    doc.saveas(path)
    return path, (e, n)


def qc(path):
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    errors = []
    print("ACADVER:", doc.dxfversion, "| INSUNITS:", doc.header.get("$INSUNITS"))
    banned = msp.query("ARC CIRCLE ELLIPSE SPLINE HATCH SOLID LINE XLINE 3DPOLYLINE")
    if len(banned):
        errors.append(f"{len(banned)} banned entities")
    polys = {}
    for pl in msp.query("LWPOLYLINE"):
        if not pl.closed:
            errors.append(f"open polyline on {pl.dxf.layer}")
        if pl.dxf.layer not in SDD_PLOT_LAYERS:
            errors.append(f"unknown layer {pl.dxf.layer}")
        polys.setdefault(pl.dxf.layer, []).append(Polygon([p[:2] for p in pl.get_points()]))
    for ins in msp.query("INSERT"):
        geom_layer = ins.dxf.layer.removesuffix("Detail")
        p = Point(ins.dxf.insert.x, ins.dxf.insert.y)
        if not any(poly.contains(p) for poly in polys.get(geom_layer, [])):
            errors.append(f"{ins.dxf.name} insertion point not inside a {geom_layer} polygon")
    auditor = doc.audit()
    print("ezdxf audit errors:", len(auditor.errors), "fixes:", len(auditor.fixes))
    dwg_name = NAME.replace(".dxf", ".dwg")
    print("file name", dwg_name, "matches SDD pattern:", bool(NAME_RE.match(dwg_name)))
    print("bad name 'Plot_P11.dwg' matches:", bool(NAME_RE.match("Plot_P11.dwg")))
    print("SDD QC errors:", errors or "none")


if __name__ == "__main__":
    p, (e, n) = build()
    print(f"origin UTM40N E {e:.3f} N {n:.3f}; wrote {p.name} ({p.stat().st_size} bytes)")
    qc(p)
