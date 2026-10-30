"""C9: time cityseer 5.8 (Rust core, AGPL-3.0) on the same synthetic network as bench_walk.py.

Street network = intersections of the perturbed grid (bench_walk.build), optionally decomposed
into ~50 m segments (cityseer's usual practice), plus N plot centroids as a data layer
(1 % 'amenity', the rest 'home'). Times:
  centrality_shortest at 800 m (closeness + betweenness, all nodes, no sampling)
  compute_accessibilities for 'amenity' and 'home' at 800 m (home count = reach metric)
  betweenness_demand at 1600 m (homes -> amenities, origin-constrained gravity split)
Usage: PYTHONPATH=<pylib> python3 bench_cityseer.py --plots 100000 --decompose 50
"""
import argparse, json, os, resource, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import networkx as nx
import geopandas as gpd
from shapely import geometry
from cityseer.tools import io, graphs
from cityseer.metrics import networks, layers
import bench_walk

ap = argparse.ArgumentParser()
ap.add_argument("--plots", type=int, default=100000)
ap.add_argument("--decompose", type=float, default=0)
ap.add_argument("--dist", type=int, default=800)
a = ap.parse_args()

X0, Y0 = 300000.0, 2700000.0   # shift into UTM 40N (EPSG:32640) range; geometry is synthetic
t0 = time.perf_counter()
net = bench_walk.build(a.plots)
G = nx.MultiGraph(); G.graph["crs"] = "EPSG:32640"
for i, (x, y) in enumerate(net["xy"]):
    G.add_node(str(i), x=x + X0, y=y + Y0)
for u, v in net["edges"]:
    pu, pv = net["xy"][u] + (X0, Y0), net["xy"][v] + (X0, Y0)
    G.add_edge(str(u), str(v), geom=geometry.LineString([pu, pv]))
if a.decompose:
    G = graphs.nx_decompose(G, a.decompose)
nodes_gdf, edges_gdf, ns = io.network_structure_from_nx(G)
c = net["centroid"] + (X0, Y0)
lu = np.full(a.plots, "home", dtype=object); lu[net["amen"]] = "amenity"
data_gdf = gpd.GeoDataFrame({"uid": np.arange(a.plots), "landuse": lu},
                            geometry=gpd.points_from_xy(c[:, 0], c[:, 1]), crs="EPSG:32640").set_index("uid")
t_build = time.perf_counter() - t0
out = dict(tool="cityseer 5.8.0", plots=a.plots, decompose_m=a.decompose, network_nodes=len(nodes_gdf),
           build_s=round(t_build, 1), dist_m=a.dist)
t = time.perf_counter()
nodes_gdf = networks.centrality_shortest(ns, nodes_gdf, distances=[a.dist])
out["centrality_s"] = round(time.perf_counter() - t, 2)
t = time.perf_counter()
nodes_gdf = layers.compute_accessibilities(data_gdf, "landuse", ["amenity", "home"], nodes_gdf, ns,
                                           distances=[a.dist])
out["accessibility_s"] = round(time.perf_counter() - t, 2)
# macroscopic flow: demand-weighted betweenness (homes -> amenities, gravity split, routed on
# shortest paths) = link pedestrian volumes from a spatial-interaction model
homes = data_gdf[data_gdf.landuse == "home"].assign(w=1.0)
amen = data_gdf[data_gdf.landuse == "amenity"].assign(w=1.0)
t = time.perf_counter()
nodes_gdf = networks.betweenness_demand(ns, nodes_gdf, homes, amen, "w", "w", distances=[1600])
out["betweenness_demand_1600_s"] = round(time.perf_counter() - t, 2)
out["columns_sample"] = [col for col in nodes_gdf.columns if "800" in col or "1600" in col][-4:]
out["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
out["loadavg_1m"] = round(os.getloadavg()[0], 2)
out["threads_available"] = os.cpu_count()
print(json.dumps(out))
