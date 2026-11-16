"""Check GCC CRS codes against pyproj's bundled EPSG database."""
import pyproj
from pyproj import CRS
from pyproj.database import get_database_metadata
print("pyproj", pyproj.__version__, "PROJ", pyproj.proj_version_str,
      "EPSG db", get_database_metadata("EPSG.VERSION"), get_database_metadata("EPSG.DATE"))
codes = [4326, 32636, 32637, 32638, 32639, 32640, 3997, 4270, 27039, 27040, 4303, 30339, 30340, 5843,
         4204, 2318, 20436, 20437, 20438, 20439, 20440, 8818, 8836, 8837, 8838, 8839, 8840,
         9333, 9356, 9357, 9358, 9359, 9360, 9335, 9520,
         4614, 2932, 4285, 28600, 4286, 2099, 3857]
for c in codes:
    crs = CRS.from_epsg(c)
    aou = crs.area_of_use
    d = crs.datum.name if crs.datum else (crs.geodetic_crs.datum.name if crs.geodetic_crs else '')
    ell = crs.ellipsoid.name if crs.ellipsoid else ''
    proj = ''
    if crs.coordinate_operation:
        op = crs.coordinate_operation
        params = {p.name: round(p.value, 9) for p in op.params}
        proj = f"{op.method_name} {params}"
    units = ",".join(sorted({a.unit_name for a in crs.axis_info}))
    axes = ",".join(f"{a.abbrev}({a.direction})" for a in crs.axis_info)
    print(f"\nEPSG:{c} | {crs.name} | type={crs.type_name} | deprecated={crs.is_deprecated}")
    print(f"  datum={d} | ellipsoid={ell} | units={units} | axes={axes}")
    if proj: print(f"  projection={proj}")
    if aou: print(f"  area={aou.name} | bounds W{aou.west} S{aou.south} E{aou.east} N{aou.north}")
