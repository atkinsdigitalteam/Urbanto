"""C9: time pandana 0.8 (UDST, AGPL-3.0-or-later, C++ contraction hierarchies) on the fine graph
of bench_walk.py (one access node per plot). Times network build (CH preprocessing), the
800 m count aggregation for every node (= reach), an exponential-decay sum at --grav m (gravity-like; default 2400)
and nearest-amenity (nearest_pois).
Usage: PYTHONPATH=<pylib> python3 bench_pandana.py --plots 100000
"""
import argparse, json, os, resource, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import pandana
import bench_walk

ap = argparse.ArgumentParser(); ap.add_argument("--plots", type=int, default=100000)
ap.add_argument("--grav", type=int, default=2400)  # decay-sum radius; precompute memory grows with it
a = ap.parse_args()
net = bench_walk.build(a.plots)
G, plot_node, _ = bench_walk.fine_graph(net)
coo = G.tocoo(); m = coo.row < coo.col                      # one record per undirected edge
N = G.shape[0]
# node coordinates: intersections from xy, plot access nodes from acc
xy = np.zeros((N, 2)); xy[:len(net["xy"])] = net["xy"]; xy[plot_node] = net["acc"]
out = dict(tool="pandana " + pandana.__version__ if hasattr(pandana, "__version__") else "pandana",
           plots=a.plots, nodes=N)
t = time.perf_counter()
nw = pandana.Network(pd.Series(xy[:, 0]), pd.Series(xy[:, 1]), pd.Series(coo.row[m]), pd.Series(coo.col[m]),
                     pd.DataFrame({"len": coo.data[m]}), twoway=True)
out["build_ch_s"] = round(time.perf_counter() - t, 2)
pre = max(800, a.grav)
t = time.perf_counter(); nw.precompute(pre); out[f"precompute_{pre}_s"] = round(time.perf_counter() - t, 2)
nw.set(pd.Series(plot_node), variable=pd.Series(np.ones(a.plots)), name="plots")
t = time.perf_counter(); r = nw.aggregate(800, type="count", decay="flat", name="plots")
out["reach_800_count_s"] = round(time.perf_counter() - t, 2)
out["median_plots_within_800m"] = float(np.median(r.values[plot_node]))
amen = plot_node[net["amen"]]
nw.set(pd.Series(amen), variable=pd.Series(np.ones(len(amen))), name="amen")
t = time.perf_counter(); g = nw.aggregate(a.grav, type="sum", decay="exp", name="amen")
out[f"decay_sum_{a.grav}_s"] = round(time.perf_counter() - t, 2)
nw.set_pois("amen", 3000, 1, pd.Series(xy[amen, 0]), pd.Series(xy[amen, 1]))
t = time.perf_counter(); near = nw.nearest_pois(3000, "amen", num_pois=1)
out["nearest_poi_s"] = round(time.perf_counter() - t, 2)
out["median_to_nearest_m"] = float(np.median(near.values[plot_node, 0]))
out["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
out["loadavg_1m"] = round(os.getloadavg()[0], 2)
print(json.dumps(out))
