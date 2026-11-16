"""C8 measurement: how far apart competing datum transformations land, at Abu Dhabi and Riyadh."""
import pyproj
from pyproj import Transformer, Geod
from pyproj.transformer import TransformerGroup
pyproj.network.set_network_enabled(False)
g = Geod(ellps="WGS84")
szgm = (54.474, 24.412); kc = (46.6744, 24.7113)
clean = lambda s: s.replace(" (with axis order normalized for visualization)", "").replace("Inverse of ", "")

# Abu Dhabi: ADCO transformation (12) that PROJ picks vs the AD-SDI ones (13, 14, 15) and Dubai (10)
res = {clean(t.description): t.transform(*szgm) for t in TransformerGroup("EPSG:4326", "EPSG:4270", always_xy=True).transformers}
a = res["Nahrwan 1967 to WGS 84 (12)"]
for k in ["Nahrwan 1967 to WGS 84 (13)", "Nahrwan 1967 to WGS 84 (14)", "Nahrwan 1967 to WGS 84 (15)", "Nahrwan 1967 to WGS 84 (10)"]:
    b = res[k]; print(f"SZ Grand Mosque: (12) vs {k}: {g.inv(a[0], a[1], b[0], b[1])[2]:.2f} m")

# Saudi: which operations exist between the legacy frames and KSA-GRF17
for s, t in [(4204, 9333), (8818, 9333), (4204, 8818)]:
    tg = TransformerGroup(f"EPSG:{s}", f"EPSG:{t}", always_xy=True)
    print(f"EPSG:{s} -> EPSG:{t}: usable {[ (clean(x.description), x.accuracy) for x in tg.transformers]}; "
          f"unavailable {[ (o.name, [gr.short_name for gr in o.grids]) for o in tg.unavailable_operations]}")
x1, y1 = Transformer.from_crs(4326, 32638, always_xy=True).transform(*kc)
x2, y2 = Transformer.from_crs(4326, 9358, always_xy=True).transform(*kc)
print(f"Riyadh WGS 84/UTM 38N vs KSA-GRF17/UTM 38N: dE={x2-x1:.3f} dN={y2-y1:.3f} ({((x2-x1)**2+(y2-y1)**2)**0.5:.3f} m)")
x3, y3 = Transformer.from_crs(4326, 8838, always_xy=True).transform(*kc)
t = Transformer.from_crs(8838, 9358, always_xy=True); x4, y4 = t.transform(x3, y3)
print(f"Riyadh MTRF-2000 -> KSA-GRF17 (UTM 38N): dE={x4-x3:.3f} dN={y4-y3:.3f} via {clean(t.get_last_used_operation().description)}")
x5, y5 = Transformer.from_crs(4326, 20438, always_xy=True).transform(*kc)
x6, y6 = Transformer.from_crs(20438, 9358, always_xy=True).transform(x5, y5)
print(f"Riyadh Ain el Abd -> KSA-GRF17 direct (EPSG:9362) vs via WGS 84 (EPSG:1111): {((x6-x2)**2+(y6-y2)**2)**0.5:.2f} m apart")
