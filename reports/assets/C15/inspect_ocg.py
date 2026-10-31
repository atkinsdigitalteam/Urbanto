"""Print the Optional Content (layer) structure of a PDF and check BDC/EMC balance.

Usage: PYTHONPATH=<dir with pikepdf> python3 -I inspect_ocg.py file.pdf
"""
import re
import sys

import pikepdf


def name_of(o):
    return str(o.get("/Name", "?"))


def walk_order(arr, depth=0):
    for item in arr:
        if isinstance(item, pikepdf.Array):
            walk_order(item, depth + 1)
        elif isinstance(item, pikepdf.String):
            print("  " * depth + f"[label] {item}")
        else:
            print("  " * depth + f"- {name_of(item)}")


def main(path):
    pdf = pikepdf.open(path)
    print(f"file: {path}  PDF version {pdf.pdf_version}  pages {len(pdf.pages)}")
    ocp = pdf.Root.get("/OCProperties")
    if ocp is None:
        print("no /OCProperties: not a layered PDF")
        return
    ocgs = list(ocp.OCGs)
    print(f"/OCProperties /OCGs: {len(ocgs)} groups")
    for g in ocgs:
        usage = g.get("/Usage")
        extra = ""
        if usage is not None:
            ps = usage.get("/Print", {}).get("/PrintState")
            vs = usage.get("/View", {}).get("/ViewState")
            extra = f"  Usage: PrintState={ps} ViewState={vs}"
        print(f"  obj {g.objgen[0]:>3}  /Name ({name_of(g)}){extra}")
    d = ocp.D
    print(f"/D default config: /Name={d.get('/Name', '<missing>')}")
    for key in ("/ON", "/OFF", "/Locked"):
        if key in d:
            print(f"  {key}: {[name_of(x) for x in d[key]]}")
    if "/Order" in d:
        print("  /Order (layer panel tree):")
        walk_order(d.Order, 2)
    for i, page in enumerate(pdf.pages):
        props = page.Resources.get("/Properties", {})
        print(f"page {i + 1} /Resources /Properties:")
        for k, v in props.items():
            print(f"  {k} -> {name_of(v)}")
        c = page.Contents
        streams = list(c) if isinstance(c, pikepdf.Array) else [c]
        data = "\n".join(x.read_bytes().decode("latin-1") for x in streams)
        print(f"  /Contents: {len(streams)} stream(s)")
        bdc = re.findall(r"/OC\s+/(\w+)\s+BDC", data)
        print(f"  content stream: {len(data)} bytes, {len(bdc)} '/OC ... BDC', "
              f"{data.count('EMC')} 'EMC' (balanced={len(bdc) == data.count('EMC')})")
        m = re.search(r"/OC /oc1 BDC.*?EMC", data, re.S)
        if m:
            print("  excerpt:\n    " + m.group(0).replace("\n", "\n    "))


if __name__ == "__main__":
    main(sys.argv[1])
