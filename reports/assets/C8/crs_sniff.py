"""C8 measurement: can a file with no .prj be assigned a GCC CRS from its coordinates alone?
For each candidate CRS, inverse-project the bounding-box centre and keep the CRS if the result
falls inside that CRS's EPSG area of use. Also checks Z handling in a shapefile."""
import sys
from pyproj import CRS, Transformer
CANDIDATES = [3997, 32639, 32640, 27039, 27040, 32637, 32638, 9357, 9358, 9359, 2932, 28600, 2318, 4326]

# Country extents taken from EPSG areas of use: UAE = Nahrwan 1967 (4270), Saudi = KSA-GRF17 (9333), Qatar = QND95 (4614)
COUNTRY = {"UAE": CRS.from_epsg(4270).area_of_use, "Saudi Arabia": CRS.from_epsg(9333).area_of_use,
           "Qatar": CRS.from_epsg(4614).area_of_use}

def in_country(lon, lat):
    return [k for k, a in COUNTRY.items() if a.west <= lon <= a.east and a.south <= lat <= a.north]

def candidates_for(x, y):
    hits = []
    for code in CANDIDATES:
        crs = CRS.from_epsg(code)
        if crs.is_geographic:
            lon, lat = x, y
        else:
            lon, lat = Transformer.from_crs(crs, 4326, always_xy=True).transform(x, y)
        a = crs.area_of_use
        if a and a.west <= lon <= a.east and a.south <= lat <= a.north:
            hits.append((code, crs.name, round(lon, 4), round(lat, 4), ",".join(in_country(lon, lat)) or "outside UAE/KSA/Qatar"))
    return hits

samples = {
    "Burj Khalifa in DLTM": (494040.047, 2787900.182),
    "Burj Khalifa in WGS 84 / UTM 40N": (326112.131, 2787898.865),
    "Kingdom Centre in KSA-GRF17 / UTM 38N": (669371.900, 2734016.029),
    "MIA Doha in QND95 / QNG": (232565.507, 393565.912),
    "Burj Khalifa lon/lat": (55.2742, 25.1972),
    "Burj Khalifa lat/lon (swapped)": (25.1972, 55.2742),
}
for label, (x, y) in samples.items():
    hits = candidates_for(x, y)
    inside = [h for h in hits if h[4] != "outside UAE/KSA/Qatar"]
    print(f"{label}: {len(hits)} CRS area-of-use hit(s), {len(inside)} land inside UAE/KSA/Qatar")
    for h in inside:
        print("    EPSG:%s %-36s -> lon %s, lat %s  [%s]" % h)

# Anchor method: the user drops one pin on the project site (here: Burj Khalifa, lon/lat) and the
# importer ranks candidate CRSs by how far the file's centre lands from that pin.
from pyproj import Geod
geod = Geod(ellps="WGS84")
anchor = (55.2742, 25.1972)
print("\nAnchor ranking for the DLTM sample (distance from the pin):")
ranked = []
for code, name, lon, lat, _ in candidates_for(494040.047, 2787900.182):
    ranked.append((geod.inv(anchor[0], anchor[1], lon, lat)[2], code, name))
for d, code, name in sorted(ranked)[:4]:
    print(f"    EPSG:{code:<6} {name:<36} {d/1000:9.3f} km")

# Z values: what a shapefile reader reports when a PolygonZ arrives
try:
    import numpy as np, shapely
    from pyogrio.raw import write, read
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    pz = shapely.Polygon([(494000, 2787850, 3.2), (494060, 2787850, 3.4), (494060, 2787920, 3.9), (494000, 2787920, 3.1)])
    write(f"{out}/z_test.shp", np.array([shapely.to_wkb(pz)], dtype=object), [np.array(["1"], dtype=object)], ["id"],
          crs="EPSG:3997", geometry_type="Polygon Z", driver="ESRI Shapefile")
    meta, _, geom, _ = read(f"{out}/z_test.shp")
    g = shapely.from_wkb(geom[0])
    print(f"\nShapefile written with Z: reported geometry_type={meta['geometry_type']}, has_z={g.has_z}, "
          f"z range {min(c[2] for c in g.exterior.coords)}..{max(c[2] for c in g.exterior.coords)}; "
          f"2D area unaffected: {g.area:.1f} m2")
    meta2, _, geom2, _ = read(f"{out}/z_test.shp", force_2d=True)
    print(f"Read with force_2d=True: has_z={shapely.from_wkb(geom2[0]).has_z}")
except ImportError as e:
    print("pyogrio not available:", e)
