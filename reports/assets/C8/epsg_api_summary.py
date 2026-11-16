import json, sys, glob, os
d = sys.argv[1]
for f in sorted(glob.glob(os.path.join(d, "*.json")), key=lambda p: int(os.path.basename(p)[:-5])):
    try:
        j = json.load(open(f))
    except Exception as e:
        print(os.path.basename(f), "ERR", e); continue
    dep = "DEPRECATED" if j.get("Deprecations") else "valid"
    sup = [s.get("SupersededBy", s) for s in j.get("Supersessions", [])]
    print(f"{j.get('Code')} | {j.get('Name')} | {dep} | src={j.get('InformationSource')} | rev={str(j.get('RevisionDate'))[:10]} | remark={ (j.get('Remark') or '')[:160]} | supersessions={sup}")
