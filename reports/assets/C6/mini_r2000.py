"""A tiny hand-written DXF R2000 (AC1015) writer, no library.

It writes the smallest file the ezdxf documentation lists as required for DXF
R13 and later (HEADER $ACADVER + $HANDSEED, empty CLASSES, nine TABLES with the
required entries, *Model_Space / *Paper_Space blocks, ENTITIES, OBJECTS with
the root dictionary and ACAD_GROUP), then one variant per missing piece, so
each piece can be checked with ezdxf (audit_samples.py) and the .NET readers.

Run: python3 mini_r2000.py   -> ./minimal/*.dxf
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent / "minimal"
OUT.mkdir(exist_ok=True)

# Fixed handles (hex strings). $HANDSEED must be larger than all of them.
H = dict(
    VPORT_T="1", LTYPE_T="2", LAYER_T="3", STYLE_T="4", VIEW_T="5", UCS_T="6",
    APPID_T="7", DIMSTYLE_T="8", BLOCK_RECORD_T="9",
    LT_BYBLOCK="10", LT_BYLAYER="11", LT_CONT="12", LAYER0="13", STD_STYLE="14",
    APPID_ACAD="15", STD_DIMSTYLE="16", BR_MS="17", BR_PS="18",
    BLK_MS="19", END_MS="1A", BLK_PS="1B", END_PS="1C",
    LINE="1D", ROOT="1E", GROUP_D="1F",
)
SEED = "20"


def tags(*pairs) -> list[tuple[int, str]]:
    return list(pairs)


def table(name: str, handle: str, entries: list[list[tuple[int, str]]], extra=()) -> list:
    out = [(0, "TABLE"), (2, name), (5, handle), (330, "0"), (100, "AcDbSymbolTable"),
           (70, str(len(entries)))]
    out += list(extra)
    for e in entries:
        out += e
    out.append((0, "ENDTAB"))
    return out


def record(kind: str, handle: str, owner: str, subclass: str, body, handle_code: int = 5):
    return [(0, kind), (handle_code, handle), (330, owner), (100, "AcDbSymbolTableRecord"),
            (100, subclass)] + list(body)


def ltype(handle, name, desc):
    return record("LTYPE", handle, H["LTYPE_T"], "AcDbLinetypeTableRecord",
                  [(2, name), (70, "0"), (3, desc), (72, "65"), (73, "0"), (40, "0.0")])


def build(drop: set[str]) -> list[tuple[int, str]]:
    """Return the tag list; `drop` names the pieces to leave out."""
    t: list = []
    # HEADER
    if "HEADER" not in drop:
        t += [(0, "SECTION"), (2, "HEADER"), (9, "$ACADVER"), (1, "AC1015")]
        if "HANDSEED" not in drop:
            t += [(9, "$HANDSEED"), (5, "1A" if "HANDSEED_LOW" in drop else SEED)]
        t += [(0, "ENDSEC")]
    if "CLASSES" not in drop:
        t += [(0, "SECTION"), (2, "CLASSES"), (0, "ENDSEC")]
    if "TABLES" not in drop:
        t += [(0, "SECTION"), (2, "TABLES")]
        t += table("VPORT", H["VPORT_T"], [])
        lts = [] if "LTYPES" in drop else [ltype(H["LT_BYBLOCK"], "ByBlock", ""),
                                           ltype(H["LT_BYLAYER"], "ByLayer", ""),
                                           ltype(H["LT_CONT"], "Continuous", "Solid line")]
        t += table("LTYPE", H["LTYPE_T"], lts)
        layers = [] if "LAYER0" in drop else [record(
            "LAYER", H["LAYER0"], H["LAYER_T"], "AcDbLayerTableRecord",
            [(2, "0"), (70, "0"), (62, "7"), (6, "Continuous"), (370, "-3")])]
        t += table("LAYER", H["LAYER_T"], layers)
        styles = [] if "STYLE" in drop else [record(
            "STYLE", H["STD_STYLE"], H["STYLE_T"], "AcDbTextStyleTableRecord",
            [(2, "Standard"), (70, "0"), (40, "0.0"), (41, "1.0"), (50, "0.0"), (71, "0"),
             (42, "2.5"), (3, "txt"), (4, "")])]
        t += table("STYLE", H["STYLE_T"], styles)
        t += table("VIEW", H["VIEW_T"], [])
        t += table("UCS", H["UCS_T"], [])
        appids = [] if "APPID" in drop else [record(
            "APPID", H["APPID_ACAD"], H["APPID_T"], "AcDbRegAppTableRecord",
            [(2, "ACAD"), (70, "0")])]
        t += table("APPID", H["APPID_T"], appids)
        dims = [] if "DIMSTYLE" in drop else [record(
            "DIMSTYLE", H["STD_DIMSTYLE"], H["DIMSTYLE_T"], "AcDbDimStyleTableRecord",
            [(2, "Standard"), (70, "0")], handle_code=105)]  # DIMSTYLE uses 105, not 5
        t += table("DIMSTYLE", H["DIMSTYLE_T"], dims, extra=[(100, "AcDbDimStyleTable")])
        if "BLOCK_RECORD" not in drop:
            brs = [record("BLOCK_RECORD", H["BR_MS"], H["BLOCK_RECORD_T"], "AcDbBlockTableRecord",
                          [(2, "*Model_Space")]),
                   record("BLOCK_RECORD", H["BR_PS"], H["BLOCK_RECORD_T"], "AcDbBlockTableRecord",
                          [(2, "*Paper_Space")])]
            t += table("BLOCK_RECORD", H["BLOCK_RECORD_T"], brs)
        t += [(0, "ENDSEC")]
    if "BLOCKS" not in drop:
        t += [(0, "SECTION"), (2, "BLOCKS")]
        for blk, end, br, name, ps in (("BLK_MS", "END_MS", "BR_MS", "*Model_Space", False),
                                       ("BLK_PS", "END_PS", "BR_PS", "*Paper_Space", True)):
            t += [(0, "BLOCK"), (5, H[blk]), (330, H[br]), (100, "AcDbEntity")]
            t += [(67, "1")] if ps else []
            t += [(8, "0"), (100, "AcDbBlockBegin"), (2, name), (70, "0"),
                  (10, "0.0"), (20, "0.0"), (30, "0.0"), (3, name), (1, "")]
            t += [(0, "ENDBLK"), (5, H[end]), (330, H[br]), (100, "AcDbEntity")]
            t += [(67, "1")] if ps else []
            t += [(8, "0"), (100, "AcDbBlockEnd")]
        t += [(0, "ENDSEC")]
    # ENTITIES: one LINE, 25 m long
    t += [(0, "SECTION"), (2, "ENTITIES"), (0, "LINE")]
    if "LINE_HANDLE" not in drop:
        t += [(5, H["ROOT"] if "LINE_DUP_HANDLE" in drop else H["LINE"])]
    if "LINE_OWNER" not in drop:
        t += [(330, H["BR_MS"])]
    if "LINE_SUBCLASS" not in drop:
        t += [(100, "AcDbEntity")]
    t += [(8, "0")]
    if "LINE_SUBCLASS" not in drop:
        t += [(100, "AcDbLine")]
    t += [(10, "0.0"), (20, "0.0"), (30, "0.0"), (11, "25.0"), (21, "0.0"), (31, "0.0")]
    t += [(0, "ENDSEC")]
    if "OBJECTS" not in drop:
        t += [(0, "SECTION"), (2, "OBJECTS"),
              (0, "DICTIONARY"), (5, H["ROOT"]), (330, "0"), (100, "AcDbDictionary"), (281, "1")]
        if "ACAD_GROUP" not in drop:
            t += [(3, "ACAD_GROUP"), (350, H["GROUP_D"]),
                  (0, "DICTIONARY"), (5, H["GROUP_D"]), (330, H["ROOT"]),
                  (100, "AcDbDictionary"), (281, "1")]
        t += [(0, "ENDSEC")]
    t += [(0, "EOF")]
    return t


def write(name: str, t: list) -> Path:
    p = OUT / name
    with open(p, "w", encoding="ascii", newline="\r\n") as f:
        for code, value in t:
            f.write(f"{code:>3}\n{value}\n")
    return p


VARIANTS = {
    "00-full-minimum": set(),
    "01-no-objects-section": {"OBJECTS"},
    "02-no-acad-group-dict": {"ACAD_GROUP"},
    "03-no-classes-section": {"CLASSES"},
    "04-no-blocks-section": {"BLOCKS"},
    "05-no-block-record-table": {"BLOCK_RECORD"},
    "06-no-layer-0": {"LAYER0"},
    "07-no-ltypes": {"LTYPES"},
    "08-no-standard-style": {"STYLE"},
    "09-no-appid-acad": {"APPID"},
    "10-no-standard-dimstyle": {"DIMSTYLE"},
    "11-no-handseed": {"HANDSEED"},
    "12-handseed-too-low": {"HANDSEED_LOW"},
    "13-line-without-handle": {"LINE_HANDLE"},
    "14-line-without-owner": {"LINE_OWNER"},
    "15-line-without-subclass-markers": {"LINE_SUBCLASS"},
    "16-line-duplicate-handle": {"LINE_DUP_HANDLE"},
    "17-no-header-section": {"HEADER"},
    "18-entities-only-ac1015": {"HEADER", "CLASSES", "TABLES", "BLOCKS", "OBJECTS"},
}

if __name__ == "__main__":
    for name, drop in VARIANTS.items():
        p = write(f"{name}.dxf", build(drop))
        print(f"{p.name:42s} {p.stat().st_size:6,d} bytes  dropped: {', '.join(sorted(drop)) or '-'}")
