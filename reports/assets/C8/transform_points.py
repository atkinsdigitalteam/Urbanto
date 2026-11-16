"""Transform four published landmark coordinates from WGS 84 into GCC local grids with pyproj.
Shows the operation PROJ actually used and its stated accuracy, plus round-trip error."""
import pyproj
from pyproj import Transformer, CRS
from pyproj.transformer import TransformerGroup
pyproj.network.set_network_enabled(False)
pts = {  # lon, lat (published, Wikipedia infobox, read 2026-10-30)
 "Burj Khalifa, Dubai": (55.2742, 25.1972),
 "Sheikh Zayed Grand Mosque, Abu Dhabi": (54.474000, 24.412000),
 "Kingdom Centre, Riyadh": (46.6744, 24.7113),
 "Museum of Islamic Art, Doha": (51.53926545, 25.2950187),
}
targets = {
 "Burj Khalifa, Dubai": [3997, 32640, 27040, 30340],
 "Sheikh Zayed Grand Mosque, Abu Dhabi": [32640, 27040, 30340],
 "Kingdom Centre, Riyadh": [32638, 9358, 8838, 20438, 2318],
 "Museum of Islamic Art, Doha": [2932, 28600, 2099, 32639, 27039],
}
for name,(lon,lat) in pts.items():
    print(f"\n### {name}: lon {lon}, lat {lat}")
    for code in targets[name]:
        t = Transformer.from_crs("EPSG:4326", f"EPSG:{code}", always_xy=True)
        x,y = t.transform(lon,lat)
        op = t.get_last_used_operation()
        back = Transformer.from_crs(f"EPSG:{code}", "EPSG:4326", always_xy=True)
        lon2,lat2 = back.transform(x,y)
        geod = pyproj.Geod(ellps="WGS84")
        _,_,rt = geod.inv(lon,lat,lon2,lat2)
        # strip axis-order boilerplate from the description
        desc = op.description.replace(" (with axis order normalized for visualization)","")
        print(f"  EPSG:{code:<6} {CRS.from_epsg(code).name:<36} E={x:14.3f} N={y:14.3f} | op: {desc} | acc={op.accuracy} m | round-trip {rt*1000:.3f} mm")
