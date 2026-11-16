"""openpyxl round-trip test for report C7 (Excel live link robustness).

1. build_base(): make a workbook with the features a live-linked planning sheet tends to have
   (styles, number formats, merged cells, formulas, a defined name, data validation,
   conditional formatting, an Excel table, a comment, a hyperlink, a chart, an image,
   sheet protection, freeze panes, custom document properties).
2. excelify(): add what Excel itself writes but openpyxl cannot create: cached formula values
   (<v>), a calcChain part, an x14 sparkline group in <extLst>, and a customXml part.
3. Round-trip the file through openpyxl (default, data_only=True) and report, part by part,
   what survived.  Optionally inventory files produced by other tools (OpenXML SDK, ClosedXML).

Usage: python3 roundtrip.py <workdir> [extra.xlsx ...]
"""
import io, re, sys, zipfile, warnings
from pathlib import Path

import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.packaging.custom import StringProperty
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROWS = [("P-0001", 1200.0, 2.5, "Residential"), ("P-0002", 950.0, 3.0, "Mixed"),
        ("P-0003", 2100.0, 1.8, "Retail"), ("P-0004", 640.0, 4.0, "Office")]


def build_base(path: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Plots"
    ws.append(["PlotId", "Area_m2", "FAR", "Use", "GFA_m2"])
    for i, (pid, area, far, use) in enumerate(ROWS, start=2):
        ws.append([pid, area, far, use, f"=B{i}*C{i}"])
    n = len(ROWS) + 1
    ws[f"A{n + 2}"] = "Total GFA"
    ws[f"E{n + 2}"] = f"=SUM(E2:E{n})"
    ws.merge_cells(f"A{n + 2}:D{n + 2}")
    hdr = Font(bold=True, color="FFFFFF")
    for c in ws[1]:
        c.font = hdr
        c.fill = PatternFill("solid", fgColor="1F4E78")
        c.alignment = Alignment(horizontal="center")
        c.border = Border(bottom=Side(style="thin"))
    for r in range(2, n + 1):
        ws[f"B{r}"].number_format = "#,##0.0"
        ws[f"E{r}"].number_format = "#,##0"
    ws.column_dimensions["A"].width = 14
    ws.freeze_panes = "A2"
    ws.add_table(Table(displayName="PlotTable", ref=f"A1:E{n}",
                       tableStyleInfo=TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)))
    dv = DataValidation(type="list", formula1='"Residential,Mixed,Retail,Office"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"D2:D{n}")
    ws.conditional_formatting.add(f"C2:C{n}", CellIsRule(operator="greaterThan", formula=["3"], fill=PatternFill("solid", bgColor="FFC7CE")))
    ws.conditional_formatting.add(f"E2:E{n}", ColorScaleRule(start_type="min", start_color="F8696B", end_type="max", end_color="63BE7B"))
    ws["A2"].comment = Comment("Plot id is the row identity key", "planner")
    ws["A3"].hyperlink = "https://example.com/plots/P-0002"
    wb.defined_names["SiteArea"] = DefinedName("SiteArea", attr_text=f"Plots!$B$2:$B${n}")
    ch = BarChart()
    ch.title = "GFA by plot"
    ch.add_data(Reference(ws, min_col=5, min_row=1, max_row=n), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=n))
    ws.add_chart(ch, "H2")
    from PIL import Image as PILImage
    buf = io.BytesIO()
    PILImage.new("RGB", (40, 20), (31, 78, 120)).save(buf, "PNG")
    buf.seek(0)
    ws.add_image(XLImage(buf), "H20")
    ws.protection.sheet = True
    ws.protection.formatCells = False
    wb.custom_doc_props.append(StringProperty(name="StudioLinkId", value="link-42"))
    wb.save(path)


def excelify(src: Path, dst: Path):
    """Add Excel-only content: cached values, calcChain, sparklines (x14 extLst), customXml."""
    zin = zipfile.ZipFile(src)
    zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    n = len(ROWS) + 1
    gfa = {f"E{i}": a * f for i, (_, a, f, _) in enumerate(ROWS, start=2)}
    gfa[f"E{n + 2}"] = sum(gfa.values())
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "xl/worksheets/sheet1.xml":
            xml = data.decode()
            for ref, val in gfa.items():  # <c r="E2"><f>B2*C2</f><v></v></c> -> cached value
                xml = re.sub(rf'(<c r="{ref}"[^>]*>)(<f>[^<]*</f>)(<v>[^<]*</v>|<v\s*/>)?',
                             lambda m: f"{m.group(1)}{m.group(2)}<v>{val:g}</v>", xml)
            ext = ('<extLst><ext uri="{05C60535-1F16-4fd2-B633-F4F36F0B64E0}" '
                   'xmlns:x14="http://schemas.microsoft.com/office/spreadsheetml/2009/9/main">'
                   '<x14:sparklineGroups xmlns:xm="http://schemas.microsoft.com/office/excel/2006/main">'
                   '<x14:sparklineGroup displayEmptyCellsAs="gap"><x14:colorSeries rgb="FF376092"/>'
                   '<x14:sparklines><x14:sparkline><xm:f>Plots!B2:C2</xm:f><xm:sqref>F2</xm:sqref></x14:sparkline>'
                   '</x14:sparklines></x14:sparklineGroup></x14:sparklineGroups></ext></extLst>')
            xml = xml.replace("</worksheet>", ext + "</worksheet>")
            data = xml.encode()
        elif item.filename == "xl/workbook.xml":  # Excel writes its engine id and no fullCalcOnLoad flag
            data = re.sub(r"<calcPr[^>]*/>", '<calcPr calcId="191029"/>', data.decode()).encode()
        elif item.filename == "[Content_Types].xml":
            xml = data.decode().replace("</Types>",
                '<Override PartName="/xl/calcChain.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.calcChain+xml"/>'
                '<Override PartName="/customXml/itemProps1.xml" ContentType="application/vnd.openxmlformats-officedocument.customXmlProperties+xml"/></Types>')
            data = xml.encode()
        elif item.filename == "xl/_rels/workbook.xml.rels":
            xml = data.decode().replace("</Relationships>",
                '<Relationship Id="rIdCalc" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/calcChain" Target="calcChain.xml"/>'
                '<Relationship Id="rIdCx" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml" Target="../customXml/item1.xml"/></Relationships>')
            data = xml.encode()
        zout.writestr(item, data)
    cells = "".join(f'<c r="{r}" i="1"/>' for r in gfa)
    zout.writestr("xl/calcChain.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  f'<calcChain xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">{cells}</calcChain>')
    zout.writestr("customXml/item1.xml", '<studio xmlns="urn:example:studio"><link id="link-42" range="PlotTable"/></studio>')
    zout.writestr("customXml/itemProps1.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<ds:datastoreItem ds:itemID="{6E3F1A2B-0000-4000-8000-000000000042}" '
                  'xmlns:ds="http://schemas.openxmlformats.org/officeDocument/2006/customXml"/>')
    zout.writestr("customXml/_rels/item1.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXmlProps" Target="itemProps1.xml"/></Relationships>')
    zout.close()


def inventory(path: Path) -> dict:
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    def main_ns(xml):  # strip the prefix the writer bound to the SpreadsheetML namespace (SDK and ClosedXML use "x:")
        m = re.search(r'xmlns:(\w+)="http://schemas.openxmlformats.org/spreadsheetml/2006/main"', xml)
        return re.sub(rf"<(/?){m.group(1)}:", r"<\1", xml) if m else xml
    sheet = main_ns(z.read("xl/worksheets/sheet1.xml").decode("utf-8-sig"))
    styles = main_ns(z.read("xl/styles.xml").decode("utf-8-sig"))
    wbxml = main_ns(z.read("xl/workbook.xml").decode("utf-8-sig"))
    f_cells = re.findall(r"<c [^>]*>\s*<f[^>]*>[^<]*</f>\s*(<v>[^<]+</v>)?", sheet)
    m = re.search(r'<cellXfs count="(\d+)"', styles)
    def has(p): return any(n.startswith(p) for n in names)
    return {
        "formula cells": len(f_cells),
        "formula cells with a non-empty cached <v>": sum(1 for v in f_cells if v),
        "cellXfs (cell styles)": int(m.group(1)) if m else 0,
        "custom number formats": len(re.findall(r"<numFmt ", styles)),
        "merged ranges": len(re.findall(r"<mergeCell ", sheet)),
        "data validations": len(re.findall(r"<dataValidation ", sheet)),
        "conditional formats": len(re.findall(r"<conditionalFormatting", sheet)),
        "freeze pane": "<pane " in sheet,
        "sheet protection": "<sheetProtection" in sheet,
        "hyperlinks": len(re.findall(r"<hyperlink ", sheet)),
        "defined names": len(re.findall(r"<definedName ", wbxml)),
        "table part": has("xl/tables/"),
        "comments part": any("comments" in n for n in names),
        "chart part": has("xl/charts/"),
        "image (xl/media)": has("xl/media/"),
        "x14 sparklines (extLst)": "sparklineGroup" in sheet,
        "calcChain part": "xl/calcChain.xml" in names,
        "customXml part": has("customXml/"),
        "custom doc props": "docProps/custom.xml" in names,
        "calcPr fullCalcOnLoad": "fullCalcOnLoad" in wbxml,
        "zip parts": len(names),
    }


def main():
    wd = Path(sys.argv[1])
    wd.mkdir(parents=True, exist_ok=True)
    base, src = wd / "base_openpyxl.xlsx", wd / "excel_like.xlsx"
    build_base(base)
    excelify(base, src)
    results = {"source (Excel-like)": inventory(src)}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        wb = openpyxl.load_workbook(src)
        print("openpyxl warnings on load:", sorted({str(x.message) for x in w}) or "none")
    print("load_workbook(src)['Plots']['E2'].value ->", repr(wb["Plots"]["E2"].value))
    print("load_workbook(src, data_only=True)['Plots']['E2'].value ->",
          repr(openpyxl.load_workbook(src, data_only=True)["Plots"]["E2"].value))
    out_a = wd / "rt_openpyxl_default.xlsx"
    wb["Plots"]["B2"] = 5000.0  # the kind of edit a link writes back
    wb.save(out_a)
    results["openpyxl load+save"] = inventory(out_a)
    print("after openpyxl save, reload data_only=True E2 ->",
          repr(openpyxl.load_workbook(out_a, data_only=True)["Plots"]["E2"].value))

    out_b = wd / "rt_openpyxl_data_only.xlsx"
    openpyxl.load_workbook(src, data_only=True).save(out_b)
    results["openpyxl data_only load+save"] = inventory(out_b)
    print("after data_only save, E2 value ->", repr(openpyxl.load_workbook(out_b)["Plots"]["E2"].value))

    for extra in sys.argv[2:]:
        results[Path(extra).stem] = inventory(Path(extra))

    keys = list(results["source (Excel-like)"].keys())
    cols = list(results.keys())
    print("\n| Feature | " + " | ".join(cols) + " |")
    print("|---|" + "---|" * len(cols))
    for k in keys:
        print(f"| {k} | " + " | ".join(str(results[c][k]) for c in cols) + " |")


if __name__ == "__main__":
    main()
