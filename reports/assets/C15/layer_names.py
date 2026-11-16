"""Validate CAD layer names against ISO 13567 and AIA / US NCS V6 patterns.

Field rules used (see report C15, sections ISO 13567 and AIA CAD Layer Guidelines):
  ISO 13567-2: Agent(2) Element(6) Presentation(2) are mandatory, then optional,
  positional fields Status(1) Sector(4) Phase(1) Projection(1) Scale(1)
  WorkPackage(2) UserDefined(any). '-' = all / not subdivided, '_' = unused.
  NCS V6 CLG: Discipline(1-2)-Major(4)[-Minor(4)][-Minor(4)][-Status(1)].
Run: python3 layer_names.py
"""
import re

ISO_FIELD = r"[A-Z0-9_\-]"
ISO13567 = re.compile(
    r"^(?P<agent>[A-Z][A-Z0-9_\-])"
    r"(?P<element>" + ISO_FIELD + r"{6})"
    r"(?P<presentation>[ETHDJKGUBVI_\-]" + ISO_FIELD + r")"
    r"(?:(?P<status>[NERTOF_\-])"
    r"(?:(?P<sector>" + ISO_FIELD + r"{4})"
    r"(?:(?P<phase>[PDRCO1-9_\-])"
    r"(?:(?P<projection>[0-3_\-])"
    r"(?:(?P<scale>[A-K1-7_\-])"
    r"(?:(?P<workpackage>" + ISO_FIELD + r"{2})"
    r"(?P<user>[A-Za-z0-9_\-]*)"
    r")?)?)?)?)?)?$"
)

NCS_DISCIPLINES = "ABCDEFGHILMOPQRSTVWXZ"
AIA_NCS = re.compile(
    r"^(?P<discipline>[" + NCS_DISCIPLINES + r"][A-Z]?)"
    r"-(?P<major>[A-Z0-9~]{4})"
    r"(?:-(?P<minor1>[A-Z0-9~]{4}))?"
    r"(?:-(?P<minor2>[A-Z0-9~]{4}))?"
    r"(?:-(?P<status>[ADEFMNTX1-9]))?$"
)

# Abu Dhabi (ADM SDD v1.18.2) uses its own fixed list; exact match only (subset shown).
ADM_SDD_PLOT = {"Plot", "PlotDetail", "Sector", "SectorDetail", "Zone", "ZoneDetail",
                "DimensionLine", "Title"}


def check(name):
    out = []
    m = ISO13567.match(name)
    out.append(("ISO 13567", "ok " + ",".join(f"{k}={v}" for k, v in m.groupdict().items() if v)
                if m else "FAIL"))
    m = AIA_NCS.match(name)
    if m:
        note = " (warn: ANNO not allowed for ISO 13567 conformance)" if m["major"] == "ANNO" else ""
        out.append(("AIA/NCS", "ok " + ",".join(f"{k}={v}" for k, v in m.groupdict().items() if v) + note))
    else:
        out.append(("AIA/NCS", "FAIL"))
    out.append(("ADM SDD plot", "ok" if name in ADM_SDD_PLOT else "-"))
    return out


SAMPLES = [
    # AIA / NCS samples (first four are the NCS V6 document's own examples)
    "A-WALL", "AD-WALL", "A-WALL-FULL-TEXT", "AI-WALL-FULL-DIMS-N",
    "C-PROP-LINE", "G-ANNO-TTLB", "A-AREA-PATT", "A-WALL-N",
    "A_WALL", "A-WAL", "Y-WALL", "A-WALL-Q", "a-wall", "A-WALL-FULL-TEXT-DIMS",
    # ISO 13567 samples (from Wikipedia ISO 13567 and Tse & Wong 2004)
    "A-B374--T-", "A-37420-T2N01B113B23pro", "SF5821AAE-NI---13C23USER",
    "A-------E-N", "A-------E1", "A-------Z-", "A-------E-Q", "A-B374-T-",
    # Authority-specific (Abu Dhabi SDD)
    "Plot", "PlotDetail", "RoadCenterLine",
]

if __name__ == "__main__":
    w = max(map(len, SAMPLES))
    for s in SAMPLES:
        res = check(s)
        print(f"{s:<{w}}  " + " | ".join(f"{k}: {v}" for k, v in res))
