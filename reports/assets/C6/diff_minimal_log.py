"""For each hand-written minimal variant, list the ezdxf log messages (loader repairs)
and audit results that differ from the full minimum file 00-full-minimum.dxf."""
from pathlib import Path
from audit_samples import audit_file

HERE = Path(__file__).resolve().parent / "minimal"
base = audit_file(HERE / "00-full-minimum.dxf")
print("00-full-minimum.dxf ezdxf loader log (what ezdxf adds to a bare minimum file):")
for m in base["readfile_log"]:
    print("   ", m)
base_set = set(base["readfile_log"])
for p in sorted(HERE.glob("*.dxf"))[1:]:
    r = audit_file(p)
    extra = [m for m in r["readfile_log"] if m not in base_set]
    fixes = r.get("audit_fixes", []) + [f"recover: {x}" for x in r["recover_fixes"]]
    print(f"{p.name}: readfile={r['readfile']}")
    for m in extra:
        print("    log  :", m)
    for f in dict.fromkeys(fixes):
        print("    fix  :", f)
