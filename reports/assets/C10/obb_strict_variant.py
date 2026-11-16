# Variant of the OBB split: never accept a split that landlocks a child of a parent that has frontage.
# If neither orientation works, keep the parent (it may exceed A_MAX).
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # parcel_bench.py sits next to this file
import parcel_bench as pb
from shapely.geometry import Polygon
import numpy as np
from shapely.geometry import LineString
from shapely.ops import split

def subdivide_obb_strict(block):
    ring = block.exterior.buffer(0.01)
    out = []
    def ts(poly, along):
        c, ld, L, S = pb.obb_info(poly)
        d = ld if along else np.array([-ld[1], ld[0]])
        big = 4 * (L + S)
        pieces = pb.as_polys(split(poly, LineString([tuple(c - d * big), tuple(c + d * big)])))
        if len(pieces) < 2 or any(pb.obb_info(q)[3] < pb.W_MIN for q in pieces):
            return None
        return pieces
    def ok(pieces, parent):
        if pb.frontage(parent, ring) < pb.ACCESS_MIN:
            return True
        return all(pb.frontage(q, ring) >= pb.ACCESS_MIN for q in pieces)
    def rec(poly):
        if poly.area <= pb.A_MAX:
            out.append(poly); return
        for along in (False, True):
            p = ts(poly, along)
            if p is not None and ok(p, poly):
                for q in p: rec(q)
                return
        out.append(poly)
    rec(block)
    return out

for name, fn in (("a_rectangle", pb.block_rect), ("b_L", pb.block_L), ("b_U", pb.block_U), ("c_arc_10deg", lambda: pb.block_arc(10)), ("d_thin", pb.block_thin)):
    v, _ = fn(); b = Polygon(v)
    m = pb.metrics(b, subdivide_obb_strict(b))
    print(name, {k: m[k] for k in ("plots", "no_access", "above_max", "area_max", "in_band", "slivers")})
