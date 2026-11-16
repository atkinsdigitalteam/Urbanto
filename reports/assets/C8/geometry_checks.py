"""C8 measurement: detect the parcel defects municipal data most often carries, with shapely 2."""
import shapely
from shapely import Polygon, MultiPolygon
from shapely.validation import explain_validity
print("shapely", shapely.__version__, "GEOS", shapely.geos_version_string)

parcels = {
    # A and B should share the line x=494060; B starts 5 cm to the right (a gap/sliver)
    "A": Polygon([(494000, 2787850), (494060, 2787850), (494060, 2787920), (494000, 2787920)]),
    "B": Polygon([(494060.05, 2787850), (494120, 2787850), (494120, 2787920), (494060.05, 2787920)]),
    # C overlaps B by 0.3 m
    "C": Polygon([(494119.7, 2787850), (494180, 2787850), (494180, 2787920), (494119.7, 2787920)]),
    # D is a bow-tie (self-intersection), typical of a digitised parcel with two corners swapped
    "D": Polygon([(494000, 2787930), (494060, 2787990), (494060, 2787930), (494000, 2787990)]),
    # E has a repeated vertex and a 1 mm spike
    "E": Polygon([(494060, 2787930), (494120, 2787930), (494120, 2787930), (494120, 2787990),
                  (494090, 2787990), (494090.001, 2788010), (494090, 2787990), (494060, 2787990)]),
    # F is one plot number stored as two parts (multipart)
    "F": MultiPolygon([Polygon([(494130, 2787930), (494150, 2787930), (494150, 2787950), (494130, 2787950)]),
                       Polygon([(494160, 2787930), (494180, 2787930), (494180, 2787950), (494160, 2787950)])]),
}
print("\nValidity:")
for k, g in parcels.items():
    print(f"  {k}: valid={g.is_valid} reason={explain_validity(g)} parts={shapely.get_num_geometries(g)} "
          f"vertices={shapely.get_num_coordinates(g)} after remove_repeated_points={shapely.get_num_coordinates(shapely.remove_repeated_points(g))}")
fixed = shapely.make_valid(parcels["D"])
print(f"  D make_valid -> {fixed.geom_type} with {shapely.get_num_geometries(fixed)} parts, area {fixed.area:.1f} m2 (bow-tie 'area' before fix: {parcels['D'].area:.1f})")

print("\nGaps and overlaps between neighbours:")
names = list(parcels)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        ga, gb = shapely.make_valid(parcels[a]), shapely.make_valid(parcels[b])
        ov = ga.intersection(gb).area
        gap = ga.distance(gb)
        if ov > 0 or 0 < gap < 0.10:
            print(f"  {a}-{b}: overlap {ov:.3f} m2, gap {gap:.3f} m")

# Sliver detection: union the block, look for thin holes
block = shapely.union_all([shapely.make_valid(parcels[k]) for k in "ABC"])
print(f"\nUnion of A,B,C: {block.geom_type}, parts={shapely.get_num_geometries(block)}")
# Fix 1: round to a 0.10 m grid (does NOT reliably close gaps: 494060.05 rounds away from 494060)
snapped = [shapely.set_precision(parcels[k], 0.1) for k in "ABC"]
print(f"set_precision(0.1 m): A-B gap now {snapped[0].distance(snapped[1]):.3f} m, "
      f"B-C overlap now {snapped[1].intersection(snapped[2]).area:.3f} m2")
# Fix 2: snap B's vertices to A's within 0.10 m, then clip C by B to remove the overlap
b2 = shapely.snap(parcels["B"], parcels["A"], 0.10)
c2 = parcels["C"].difference(b2)
print(f"snap(B to A, 0.10 m) + C.difference(B): A-B gap now {parcels['A'].distance(b2):.3f} m, "
      f"B-C overlap now {b2.intersection(c2).area:.3f} m2, union parts={shapely.get_num_geometries(shapely.union_all([parcels['A'], b2, c2]))}")
