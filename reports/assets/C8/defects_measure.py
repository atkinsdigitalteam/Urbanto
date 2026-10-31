"""Measure the size of common CRS mistakes at real GCC locations."""
import pyproj
from pyproj import Transformer, CRS, Proj, Geod
from pyproj.transformer import TransformerGroup
pyproj.network.set_network_enabled(False)
g = Geod(ellps="WGS84")
bk = (55.2742, 25.1972); szgm = (54.474, 24.412); kc=(46.6744,24.7113); mia=(51.53926545,25.2950187)

print("1) Spread of every Nahrwan 1967 -> WGS 84 candidate at Sheikh Zayed Grand Mosque (WGS84 -> Nahrwan geographic):")
tg = TransformerGroup("EPSG:4326","EPSG:4270",always_xy=True)
ref=None
for t in tg.transformers:
    lon,lat = t.transform(*szgm)
    if ref is None: ref=(lon,lat)
    _,_,d = g.inv(ref[0],ref[1],lon,lat)
    print(f"   {t.description.replace(' (with axis order normalized for visualization)',''):<55} acc={t.accuracy:>5} -> lon {lon:.7f} lat {lat:.7f}  ({d:6.2f} m from first)")

print("\n2) Nahrwan 1967 / UTM 40N labelled as WGS 84 / UTM 40N (Burj Khalifa):")
x,y = Transformer.from_crs(4326,27040,always_xy=True).transform(*bk)
lon,lat = Transformer.from_crs(32640,4326,always_xy=True).transform(x,y)
_,_,d=g.inv(*bk,lon,lat); print(f"   lands at {lon:.6f},{lat:.6f}: {d:.1f} m from the true position")

print("\n3) DLTM (EPSG:3997) coordinates read as WGS 84 / UTM 40N (Burj Khalifa):")
x,y = Transformer.from_crs(4326,3997,always_xy=True).transform(*bk)
lon,lat = Transformer.from_crs(32640,4326,always_xy=True).transform(x,y)
_,_,d=g.inv(*bk,lon,lat); print(f"   DLTM E={x:.1f} N={y:.1f} -> read as UTM40N lands at {lon:.5f},{lat:.5f}: {d/1000:.1f} km away")
print("   UTM40N read as DLTM:")
x,y = Transformer.from_crs(4326,32640,always_xy=True).transform(*bk)
lon,lat = Transformer.from_crs(3997,4326,always_xy=True).transform(x,y)
_,_,d=g.inv(*bk,lon,lat); print(f"   lands at {lon:.5f},{lat:.5f}: {d/1000:.1f} km away")

print("\n4) Lat/lon swapped (axis order) for Burj Khalifa:")
lon,lat = bk[1],bk[0]
print(f"   point read as lon={lon}, lat={lat} -> {'valid' if -90<=lat<=90 else 'invalid'}; distance:", round(g.inv(*bk,lon,lat)[2]/1000), "km")
t_auth = Transformer.from_crs("EPSG:4326","EPSG:32640")  # authority axis order: lat, lon
print("   EPSG:4326 authority order (lat,lon) input (25.1972,55.2742) ->", tuple(round(v,3) for v in t_auth.transform(25.1972,55.2742)))
print("   same numbers passed as (lon,lat) without always_xy ->", tuple(round(v,3) for v in t_auth.transform(55.2742,25.1972)))

print("\n5) Grid scale factor (point scale k) - grid vs ground distance:")
for name,pt,codes in [("Burj Khalifa",bk,[3997,32640,32639]),("SZ Grand Mosque",szgm,[32640,32639]),("Kingdom Centre",kc,[32638,9358,32637]),("MIA Doha",mia,[2932,32639])]:
    for c in codes:
        f = Proj(CRS.from_epsg(c)).get_factors(*pt)
        k = f.meridional_scale
        print(f"   {name:<16} EPSG:{c:<6} k={k:.7f}  -> {abs(k-1)*1e6:7.1f} mm per km ({'longer' if k>1 else 'shorter'} on grid)")

print("\n6) Ground height effect: elevation factor at 300 m above ellipsoid (R=6371 km): ", round(300/6371000*1e6,1), "mm per km")
