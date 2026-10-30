"""List candidate datum transformations pyproj knows for each GCC local datum -> WGS 84."""
from pyproj.transformer import TransformerGroup
from pyproj import Transformer
import pyproj
pyproj.network.set_network_enabled(False)
pairs = [(4270,"Nahrwan 1967"),(4303,"TC(1948)"),(4204,"Ain el Abd"),(8818,"MTRF-2000"),(9333,"KSA-GRF17"),
         (4614,"QND95"),(4285,"Qatar 1974"),(4286,"Qatar 1948")]
for code,name in pairs:
    tg = TransformerGroup(f"EPSG:{code}", "EPSG:4326", always_xy=True)
    print(f"\n== EPSG:{code} {name} -> WGS 84: {len(tg.transformers)} usable, {len(tg.unavailable_operations)} unavailable")
    for t in tg.transformers:
        print(f"   acc={t.accuracy} m | {t.description}")
    for op in tg.unavailable_operations:
        print(f"   UNAVAILABLE (grid missing) | {op.name}")
    best = Transformer.from_crs(f"EPSG:{code}", "EPSG:4326", always_xy=True)
    print(f"   from_crs picks: {best.description} (acc={best.accuracy})")
