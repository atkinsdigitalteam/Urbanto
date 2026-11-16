"""Geoid undulation (EGM96 vs EGM2008) at four GCC landmarks, using PROJ CDN grids (network enabled)."""
import pyproj
from pyproj import Transformer
import os
if os.environ.get("PROJ_CA_BUNDLE"):  # needed behind a TLS-inspecting proxy
    pyproj.network.set_ca_bundle_path(os.environ["PROJ_CA_BUNDLE"])
pyproj.network.set_network_enabled(True)
print("network enabled:", pyproj.network.is_network_enabled(), "endpoint:", pyproj.network.get_network_endpoint() if hasattr(pyproj.network,'get_network_endpoint') else '')
pts = {"Burj Khalifa": (55.2742, 25.1972), "SZ Grand Mosque": (54.474, 24.412),
       "Kingdom Centre": (46.6744, 24.7113), "MIA Doha": (51.53926545, 25.2950187)}
for vname, comp in [("EGM96", "EPSG:4326+5773"), ("EGM2008", "EPSG:4326+3855")]:
    t = Transformer.from_crs("EPSG:4979", comp, always_xy=True)
    for n,(lon,lat) in pts.items():
        _,_,h = t.transform(lon, lat, 0.0)
        print(f"{vname:8} {n:16} ellipsoid h=0 -> orthometric H={h:8.3f} m  (N = {-h:7.3f} m) | op: {t.get_last_used_operation().description[:80]}")
# KSA-VRF14 and Ras Ghumays: does PROJ know a geoid model?
from pyproj.transformer import TransformerGroup
for comp in ["EPSG:9520", "EPSG:4326+5843"]:
    try:
        tg = TransformerGroup("EPSG:4979" if comp!="EPSG:9520" else "EPSG:9332", comp, always_xy=True)
        print(comp, "usable:", [x.description[:90] for x in tg.transformers], "unavailable:", [o.name for o in tg.unavailable_operations])
    except Exception as e:
        print(comp, "ERR", e)
