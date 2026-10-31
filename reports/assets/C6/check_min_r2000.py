"""Raw-tag lint for DXF R2000 (AC1015) files, independent of ezdxf's loader.

ezdxf's loader silently creates missing tables, layer "0", line types and
dictionaries, so `ezdxf audit` passing does not prove the file on disk has
them. This script reads the raw group-code/value pairs and checks the list
the ezdxf documentation gives as required for DXF R13+ (filestructure.html),
plus Autodesk's "not omitted" common entity codes (5, 330, 100 AcDbEntity, 8),
handle uniqueness and $HANDSEED.

Run: python3 check_min_r2000.py file.dxf [...]
"""
from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_SECTIONS = ["HEADER", "CLASSES", "TABLES", "BLOCKS", "ENTITIES", "OBJECTS"]
REQUIRED_TABLES = {
    "VPORT": [], "VIEW": [], "UCS": [],
    "LTYPE": ["BYBLOCK", "BYLAYER", "CONTINUOUS"],
    "LAYER": ["0"],
    "STYLE": ["STANDARD"],
    "APPID": ["ACAD"],
    "DIMSTYLE": ["STANDARD"],
    "BLOCK_RECORD": ["*MODEL_SPACE", "*PAPER_SPACE"],
}
STRUCTURE = {"SECTION", "ENDSEC", "TABLE", "ENDTAB", "EOF", "SEQEND"}


def read_tags(p: Path) -> list[tuple[int, str]]:
    raw = p.read_bytes().decode("cp1252", errors="replace").splitlines()
    return [(int(raw[i].strip()), raw[i + 1].strip()) for i in range(0, len(raw) - 1, 2)]


def split_sections(tags):
    sections, cur, name = {}, None, None
    for i, (c, v) in enumerate(tags):
        if c == 0 and v == "SECTION":
            name = tags[i + 1][1]
            cur = []
            sections[name] = cur
        elif c == 0 and v == "ENDSEC":
            cur = None
        elif cur is not None:
            cur.append((c, v))
    return sections


def records(tags):
    """Split a tag list into records starting at each group code 0."""
    out, cur = [], None
    for c, v in tags:
        if c == 0:
            cur = [(c, v)]
            out.append(cur)
        elif cur is not None:
            cur.append((c, v))
    return out


def check(p: Path) -> list[str]:
    problems: list[str] = []
    tags = read_tags(p)
    secs = split_sections(tags)
    for s in REQUIRED_SECTIONS:
        if s not in secs:
            problems.append(f"missing section {s}")
    hdr = dict()
    h = secs.get("HEADER", [])
    for i, (c, v) in enumerate(h):
        if c == 9 and i + 1 < len(h):
            hdr[v] = h[i + 1][1]
    if hdr.get("$ACADVER") != "AC1015":
        problems.append(f"$ACADVER is {hdr.get('$ACADVER')!r}, expected 'AC1015'")
    if "$HANDSEED" not in hdr:
        problems.append("missing $HANDSEED")
    # tables
    tbl_recs = records(secs.get("TABLES", []))
    tables: dict[str, list[str]] = {}
    current = None
    for r in tbl_recs:
        kind = r[0][1]
        if kind == "TABLE":
            current = dict(r[1:]).get(2)
            tables[current] = []
        elif kind == "ENDTAB":
            current = None
        elif current:
            tables[current].append(dict(r[1:]).get(2, "").upper())
    for t, entries in REQUIRED_TABLES.items():
        if t not in tables:
            problems.append(f"missing table {t}")
            continue
        for e in entries:
            if e not in tables[t]:
                problems.append(f"table {t} lacks entry {e}")
    # header variables that name table entries must point at existing entries
    for var, table_name, extra in (("$DIMSTYLE", "DIMSTYLE", ()), ("$TEXTSTYLE", "STYLE", ()),
                                   ("$DIMTXSTY", "STYLE", ()), ("$CLAYER", "LAYER", ()),
                                   ("$CELTYPE", "LTYPE", ("BYLAYER", "BYBLOCK"))):
        val = hdr.get(var)
        if val and table_name in tables and val.upper() not in tables[table_name] + list(extra):
            problems.append(f"header {var} = {val!r} but table {table_name} has no such entry")
    # blocks
    blk_names = [dict(r[1:]).get(2, "").upper() for r in records(secs.get("BLOCKS", [])) if r[0][1] == "BLOCK"]
    for b in ("*MODEL_SPACE", "*PAPER_SPACE"):
        if b not in blk_names:
            problems.append(f"BLOCKS lacks {b}")
    # objects: first object must be the root DICTIONARY containing ACAD_GROUP
    objs = records(secs.get("OBJECTS", []))
    if objs:
        root = objs[0]
        if root[0][1] != "DICTIONARY":
            problems.append("first object in OBJECTS is not the root DICTIONARY")
        if ("ACAD_GROUP" not in [v for c, v in root if c == 3]):
            problems.append("root DICTIONARY lacks ACAD_GROUP")
    # handles and common entity codes
    handles: dict[str, str] = {}
    for sec in ("TABLES", "BLOCKS", "ENTITIES", "OBJECTS"):
        for r in records(secs.get(sec, [])):
            kind = r[0][1]
            if kind in STRUCTURE or kind == "ENDTAB":
                continue
            codes = [c for c, _ in r]
            hcode = 105 if kind == "DIMSTYLE" else 5
            hv = next((v for c, v in r if c == hcode), None)
            if hv is None:
                problems.append(f"{sec}: {kind} without handle (group {hcode})")
            elif hv.upper() in handles:
                problems.append(f"{sec}: duplicate handle {hv} ({kind} and {handles[hv.upper()]})")
            else:
                handles[hv.upper()] = kind
            if kind == "DIMENSION":
                geom = next((v for c, v in r if c == 2), "").upper()
                if not geom or geom not in blk_names:
                    problems.append(f"{sec}: DIMENSION {hv} has no geometry block (group 2 "
                                    f"{geom or 'missing'}); AutoCAD refuses such files")
            if sec in ("ENTITIES", "BLOCKS"):
                if 330 not in codes:
                    problems.append(f"{sec}: {kind} {hv} without owner (330)")
                if (100, "AcDbEntity") not in r:
                    problems.append(f"{sec}: {kind} {hv} without subclass marker AcDbEntity")
                if 8 not in codes:
                    problems.append(f"{sec}: {kind} {hv} without layer (8)")
    if "$HANDSEED" in hdr and handles:
        try:
            if int(hdr["$HANDSEED"], 16) <= max(int(h, 16) for h in handles):
                problems.append(f"$HANDSEED {hdr['$HANDSEED']} is not above the largest handle "
                                f"{max(handles, key=lambda x: int(x, 16))}")
        except ValueError:
            problems.append("unparsable handle")
    return problems


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        probs = check(p)
        print(f"{p.name}: {'OK' if not probs else '; '.join(probs)}")
