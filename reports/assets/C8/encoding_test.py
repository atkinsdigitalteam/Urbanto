"""C8 measurement: what happens to Arabic attributes in shapefile, GeoPackage and file geodatabase.
Run: PYTHONPATH=<pylib with pyogrio 0.13 / GDAL 3.12> python3 encoding_test.py <outdir>
"""
import os, sys, glob, shutil
import numpy as np
import pyogrio
from pyogrio.raw import read, write
import shapely

out = sys.argv[1] if len(sys.argv) > 1 else "out"
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
print("pyogrio", pyogrio.__version__, "GDAL", pyogrio.__gdal_version_string__)

# Two adjacent parcels in DLTM (EPSG:3997) near Burj Khalifa.
p1 = shapely.Polygon([(494000, 2787850), (494060, 2787850), (494060, 2787920), (494000, 2787920)])
p2 = shapely.Polygon([(494060, 2787850), (494120, 2787850), (494120, 2787920), (494060, 2787920)])
geom = np.array([shapely.to_wkb(p1), shapely.to_wkb(p2)], dtype=object)
fields = ["plot_number", "community_name_en", "community_name_ar", "land_use_code", "land_use_class"]
data = [np.array(["3450123", "3450124"], dtype=object),
        np.array(["Burj Khalifa", "Burj Khalifa"], dtype=object),
        np.array(["برج خليفة", "برج خليفة"], dtype=object),
        np.array(["R", "C"], dtype=object),
        np.array(["سكني", "تجاري"], dtype=object)]

def dbf_info(path):
    with open(path, "rb") as f: b = f.read()
    ldid = b[29]
    # field descriptors: 32-byte records from offset 32 until 0x0D
    names = []; i = 32
    while b[i] != 0x0D:
        names.append(b[i:i+11].split(b"\x00")[0]); i += 32
    return ldid, names

def show(path, **kw):
    meta, fids, g, fd = read(path, **kw)
    return dict(zip(meta["fields"], [v[0] for v in fd])), meta.get("crs"), meta.get("encoding")

# 1. Shapefile, pyogrio default (UTF-8 + .cpg)
s1 = f"{out}/utf8.shp"
write(s1, geom, data, fields, crs="EPSG:3997", geometry_type="Polygon", driver="ESRI Shapefile")
print("\n[1] default write: files", sorted(os.path.basename(p) for p in glob.glob(f"{out}/utf8.*")))
print("    .cpg =", open(f"{out}/utf8.cpg").read().strip(), "| DBF LDID byte =", dbf_info(f"{out}/utf8.dbf")[0])
print("    DBF field names:", dbf_info(f"{out}/utf8.dbf")[1])
print("    read back:", show(s1)[0])

# 2. Shapefile written as Windows-1256 (Arabic ANSI code page)
s2 = f"{out}/cp1256.shp"
write(s2, geom, data, fields, crs="EPSG:3997", geometry_type="Polygon", driver="ESRI Shapefile", encoding="cp1256")
cpg2 = f"{out}/cp1256.cpg"
print("\n[2] encoding=cp1256: .cpg =", open(cpg2).read().strip() if os.path.exists(cpg2) else "(none)",
      "| LDID =", dbf_info(f"{out}/cp1256.dbf")[0])
print("    read back with .cpg:", show(s2)[0])

# 3. Lose the .cpg (common when people email only .shp/.shx/.dbf/.prj)
for src, tag in [("utf8", "3a UTF-8 dbf"), ("cp1256", "3b CP1256 dbf")]:
    d = f"{out}/nocpg_{src}"; os.makedirs(d)
    for ext in ("shp", "shx", "dbf", "prj"): shutil.copy(f"{out}/{src}.{ext}", d)
    vals, crs, enc = show(f"{d}/{src}.shp")
    print(f"\n[{tag}, .cpg deleted] read: encoding reported={enc} ->", vals)
    for guess in ("cp1256", "utf-8"):
        try:
            print(f"     read with encoding={guess}:", show(f"{d}/{src}.shp", encoding=guess)[0])
        except Exception as e:
            print(f"     read with encoding={guess}: ERROR {e}")

# 4. Lose the .prj
d = f"{out}/noprj"; os.makedirs(d)
for ext in ("shp", "shx", "dbf", "cpg"): shutil.copy(f"{out}/utf8.{ext}", d)
print("\n[4] .prj deleted: CRS read =", show(f"{d}/utf8.shp")[1])
print("    .prj written by GDAL for EPSG:3997:\n    ", open(f"{out}/utf8.prj").read()[:400])
print("    CRS read back from .prj:", show(s1)[1])

# 5a. Arabic field names in a shapefile: DBF names are limited to 10 bytes, and UTF-8 Arabic uses 2 bytes per letter
s5 = f"{out}/arabic_names.shp"
write(s5, geom[:1], [np.array(["برج خليفة"], dtype=object), np.array(["x"], dtype=object)],
      ["اسم_المجتمع_العربي", "ملاحظات"], crs="EPSG:3997", geometry_type="Polygon", driver="ESRI Shapefile")
print("\n[5a] Arabic field names -> DBF names (raw bytes):", dbf_info(s5.replace(".shp", ".dbf"))[1])
try:
    print("     read back:", show(s5)[0])
except Exception as e:
    print("     read back FAILED:", type(e).__name__, e)

# 5b. Long Arabic text value in a shapefile (DBF character fields hold at most 254 bytes)
long_ar = "مخطط تفصيلي " * 20  # 240 characters, 440 bytes in UTF-8
s5b = f"{out}/long_text.shp"
write(s5b, geom[:1], [np.array([long_ar], dtype=object)], ["notes"], crs="EPSG:3997",
      geometry_type="Polygon", driver="ESRI Shapefile")
v = show(s5b)[0]["notes"]
print(f"[5b] wrote {len(long_ar)} chars / {len(long_ar.encode('utf-8'))} bytes; read back {len(v)} chars / {len(v.encode('utf-8'))} bytes")

# 6. Same data in GeoPackage and file geodatabase
for drv, path in [("GPKG", f"{out}/parcels.gpkg"), ("OpenFileGDB", f"{out}/parcels.gdb")]:
    write(path, geom, data + [np.array([long_ar, long_ar], dtype=object)], fields + ["ملاحظات_طويلة_جدا"],
          crs="EPSG:3997", geometry_type="Polygon", driver=drv, layer="parcels")
    vals, crs, enc = show(path)
    print(f"\n[6] {drv}: fields kept =", list(vals.keys()))
    print(f"    long Arabic note length after round trip = {len(vals['ملاحظات_طويلة_جدا'])} chars; CRS = {crs}")

# 7. GeoJSON: RFC 7946 output reprojects to WGS 84 lon/lat
for opt in ({}, {"RFC7946": "YES"}):
    path = f"{out}/parcels{'_rfc' if opt else ''}.geojson"
    write(path, geom, data, fields, crs="EPSG:3997", geometry_type="Polygon", driver="GeoJSON", layer_options=opt)
    txt = open(path, encoding="utf-8").read()
    i = txt.find('"coordinates"')
    print(f"\n[7] GeoJSON {opt or 'default'}: crs member present={'\"crs\"' in txt}; first coords:", txt[i:i+70])
