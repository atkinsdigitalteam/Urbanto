"""C8 measurement: what GDAL does with CRS when writing KML and DXF from DLTM data."""
import os, sys, numpy as np, shapely
from pyogrio.raw import write, read
out = sys.argv[1] if len(sys.argv) > 1 else "."
p = shapely.Polygon([(494000, 2787850), (494060, 2787850), (494060, 2787920), (494000, 2787920)])
geom = np.array([shapely.to_wkb(p)], dtype=object)
for drv, ext in [("KML", "kml"), ("LIBKML", "kmz"), ("DXF", "dxf")]:
    path = f"{out}/parcel_{drv}.{ext}"
    try:
        if os.path.exists(path): os.remove(path)
        fname = "Layer" if drv == "DXF" else "Name"  # DXF only has fixed fields such as Layer
        write(path, geom, [np.array(["برج خليفة"], dtype=object)], [fname], crs="EPSG:3997",
              geometry_type="Polygon", driver=drv)
        meta, _, g, fd = read(path)
        c = shapely.from_wkb(g[0]).exterior.coords[0]
        print(f"{drv}: CRS read back = {meta['crs']}; first vertex = ({c[0]:.6f}, {c[1]:.6f}); fields = {list(meta['fields'])}; "
              f"values = {[v[0] for v in fd][:3]}; size = {os.path.getsize(path)} bytes")
    except Exception as e:
        print(f"{drv}: ERROR {type(e).__name__}: {e}")
