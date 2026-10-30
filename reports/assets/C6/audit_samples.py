"""Audit every DXF in ./samples (and ./minimal if present) with ezdxf 1.4.5.

For each file:
  1. ezdxf.readfile()          strict loader (raises DXFStructureError on bad structure)
  2. ezdxf.recover.readfile()  tolerant loader; returns an Auditor with errors/fixes
  3. doc.audit()               the same checks the `ezdxf audit` CLI runs
ezdxf log warnings raised while loading are captured too, because the strict
loader silently repairs some structures (for example it creates missing tables)
and only logs that fact.

Run:  python3 audit_samples.py [folder ...]
"""
from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

import ezdxf
from ezdxf import recover

HERE = Path(__file__).resolve().parent


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.INFO)
        self.records: list[str] = []

    def emit(self, record):
        self.records.append(f"{record.levelname}: {record.getMessage()}")


def audit_file(p: Path) -> dict:
    cap = Capture()
    log = logging.getLogger("ezdxf")
    log.addHandler(cap)
    log.setLevel(logging.INFO)
    res: dict = {"file": p.name}
    try:
        doc = ezdxf.readfile(p)
        res["readfile"] = "ok"
        a = doc.audit()
        res["audit_errors"] = [f"{e.code}: {e.message}" for e in a.errors]
        res["audit_fixes"] = [f"{e.code}: {e.message}" for e in a.fixes]
    except Exception as exc:  # noqa: BLE001
        res["readfile"] = f"{type(exc).__name__}: {exc}"
    res["readfile_log"] = list(cap.records)
    cap.records.clear()
    try:
        doc, auditor = recover.readfile(p)
        res["recover_errors"] = [f"{e.code}: {e.message}" for e in auditor.errors]
        res["recover_fixes"] = [f"{e.code}: {e.message}" for e in auditor.fixes]
    except Exception as exc:  # noqa: BLE001
        res["recover_errors"] = [f"{type(exc).__name__}: {exc}"]
        res["recover_fixes"] = []
    res["recover_log"] = list(cap.records)
    log.removeHandler(cap)
    return res


def short(items: list[str], n: int = 3) -> str:
    if not items:
        return "none"
    extra = f" (+{len(items) - n} more)" if len(items) > n else ""
    return "; ".join(items[:n]) + extra


def main(folders: list[Path]):
    print(f"ezdxf {ezdxf.__version__}")
    for folder in folders:
        for p in sorted(folder.glob("*.dxf")):
            r = audit_file(p)
            print(f"\n{folder.name}/{r['file']}")
            print(f"  readfile        : {r['readfile']}")
            if "audit_errors" in r:
                print(f"  audit errors    : {len(r['audit_errors'])}  {short(r['audit_errors'])}")
                print(f"  audit fixes     : {len(r['audit_fixes'])}  {short(r['audit_fixes'])}")
            print(f"  readfile log    : {short(r['readfile_log'])}")
            print(f"  recover errors  : {len(r['recover_errors'])}  {short(r['recover_errors'])}")
            print(f"  recover fixes   : {len(r['recover_fixes'])}  {short(r['recover_fixes'])}")


if __name__ == "__main__":
    args = [Path(a) for a in sys.argv[1:]] or [HERE / "samples"]
    main(args)
