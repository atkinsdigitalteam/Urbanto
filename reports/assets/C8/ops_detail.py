from pyproj.transformer import TransformerGroup
import json
for code in [4270,4204,4285,8818,9333,4614]:
    tg = TransformerGroup(f"EPSG:{code}", "EPSG:4326", always_xy=True)
    print(f"\n== EPSG:{code}")
    for t in tg.transformers:
        j = t.to_json_dict()
        # find the concatenated / helmert step id
        def ids(d, out):
            if isinstance(d, dict):
                if 'id' in d and d.get('type') in ('Transformation','ConcatenatedOperation'):
                    out.append(f"{d['id']['authority']}:{d['id']['code']}")
                for v in d.values(): ids(v, out)
            elif isinstance(d, list):
                for v in d: ids(v, out)
            return out
        idl = ids(j, [])
        params = []
        def pr(d):
            if isinstance(d, dict):
                if d.get('type')=='Transformation':
                    params.append((d['method']['name'], [(p['name'].split(' ')[0][:6], p['value']) for p in d.get('parameters',[])]))
                for v in d.values(): pr(v)
            elif isinstance(d, list):
                for v in d: pr(v)
        pr(j)
        a = t.area_of_use
        print(f" {idl} acc={t.accuracy} | {t.name} | area={a.name[:100] if a else ''}")
        for m,p in params: print("     ", m, p)
