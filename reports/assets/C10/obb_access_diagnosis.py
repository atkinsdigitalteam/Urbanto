# Counts why OBB + forceStreetAccess = 1 still landlocks plots: the rotated split fails lotWidthMin, or also landlocks.
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # parcel_bench.py sits next to this file
import parcel_bench as pb
from shapely.geometry import Polygon, LineString
from shapely.ops import split
import numpy as np
for name, fn in (("L", pb.block_L), ("U", pb.block_U), ("rect", pb.block_rect)):
    v, s = fn()
    block = Polygon(v)
    ring = block.exterior.buffer(0.01)
    stats = {"rot_needed": 0, "rot_width_fail": 0, "rot_still_noaccess": 0, "parent_noaccess_splits": 0}
    def ts(poly, along):
        c, ld, L, S = pb.obb_info(poly)
        perp = np.array([-ld[1], ld[0]])
        d = perp if not along else ld
        big = 4 * (L + S)
        line = LineString([tuple(c - d * big), tuple(c + d * big)])
        pieces = pb.as_polys(split(poly, line))
        if len(pieces) < 2: return None, "nosplit"
        if any(pb.obb_info(q)[3] < pb.W_MIN for q in pieces): return None, "width"
        return pieces, "ok"
    def rec(poly):
        if poly.area <= pb.A_MAX: return
        if pb.frontage(poly, ring) < pb.ACCESS_MIN: stats["parent_noaccess_splits"] += 1
        first, _ = ts(poly, False)
        chosen = first
        if first is not None and any(pb.frontage(q, ring) < 1 for q in first):
            if pb.frontage(poly, ring) >= 1:
                stats["rot_needed"] += 1
            second, why = ts(poly, True)
            if second is None:
                if pb.frontage(poly, ring) >= 1: stats["rot_width_fail"] += 1
            else:
                chosen = second
                if any(pb.frontage(q, ring) < 1 for q in second) and pb.frontage(poly, ring) >= 1:
                    stats["rot_still_noaccess"] += 1
        if chosen is None:
            chosen, _ = ts(poly, True)
        if chosen is None: return
        for q in chosen: rec(q)
    rec(block)
    print(name, stats)
