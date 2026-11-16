"""C9 benchmark: walkability metrics on a synthetic street network with N plots.

Builds a perturbed-grid street network (100 m blocks, +-15 m jitter, 8 % of
street segments removed, largest connected component kept), drops N plots on
the street segments (random position along the segment, random side), and
builds two graphs:

  fine   : every plot gets its own access node spliced into its street segment
           (nodes = intersections + plots). Exact plot-to-plot distances.
  coarse : plots are attached to the nearest intersection (KD-tree) with a
           straight-line offset. Graph = intersections only (about N/9 nodes).

Metrics timed (one per subprocess so peak RSS is per metric):
  a1  single-source shortest paths (one origin to every node)
  a2  all plots to nearest amenity (multi-source Dijkstra, 1 % of plots are amenities)
  b   reach: number of plots within 800 m network distance, for every plot
  c   betweenness, sampled (Brandes with k random sources, networkx)
  d   gravity accessibility: sum_j W_j * exp(-beta * d_ij), d_ij <= 2400 m

Usage:
  python3 bench_walk.py --plots 100000 --graph fine --metric b [--workers 4]
  python3 bench_walk.py --export out_dir --plots 100000   (writes CSR binaries for the C# port)
Prints one JSON line.
"""
import argparse, json, os, resource, sys, time
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import dijkstra, connected_components
from scipy.spatial import cKDTree

SPACING = 100.0      # m between intersections
JITTER = 15.0        # m uniform jitter on intersection positions
DROP = 0.08          # share of street segments removed
PLOTS_PER_EDGE = 5.0 # target mean plots per street segment (both sides)
SETBACK = 20.0       # m from street centreline to plot centroid (coarse offset only)
REACH_R = 800.0      # m
GRAV_R = 2400.0      # m cut-off for gravity score
GRAV_BETA = np.log(2) / 400.0  # illustrative: weight halves every 400 m
AMENITY_SHARE = 0.01


def build(n_plots, seed=1):
    rng = np.random.default_rng(seed)
    n_edges_target = n_plots / PLOTS_PER_EDGE
    side = int(round(np.sqrt(n_edges_target / (2 * (1 - DROP))))) + 1
    ii, jj = np.meshgrid(np.arange(side), np.arange(side), indexing="ij")
    xy = np.c_[ii.ravel() * SPACING, jj.ravel() * SPACING].astype(float)
    xy += rng.uniform(-JITTER, JITTER, xy.shape)
    idx = (ii * side + jj)
    h = np.c_[idx[:-1, :].ravel(), idx[1:, :].ravel()]
    v = np.c_[idx[:, :-1].ravel(), idx[:, 1:].ravel()]
    edges = np.vstack([h, v])
    edges = edges[rng.random(len(edges)) > DROP]
    # keep largest connected component
    n0 = len(xy)
    A = sp.coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(n0, n0))
    _, lab = connected_components(A, directed=False)
    big = np.bincount(lab).argmax()
    keep = lab == big
    remap = -np.ones(n0, int); remap[keep] = np.arange(keep.sum())
    edges = edges[keep[edges[:, 0]] & keep[edges[:, 1]]]
    edges = remap[edges]; xy = xy[keep]
    E = len(edges)
    # plots on segments
    pe = rng.integers(0, E, n_plots)
    pt = rng.uniform(0.05, 0.95, n_plots)
    ps = rng.choice([-1.0, 1.0], n_plots)
    p0 = xy[edges[pe, 0]]; p1 = xy[edges[pe, 1]]
    acc = p0 + (p1 - p0) * pt[:, None]
    d = p1 - p0; nrm = np.c_[-d[:, 1], d[:, 0]] / np.linalg.norm(d, axis=1)[:, None]
    centroid = acc + nrm * ps[:, None] * SETBACK
    amen = rng.choice(n_plots, max(1, int(n_plots * AMENITY_SHARE)), replace=False)
    return dict(xy=xy, edges=edges, pe=pe, pt=pt, acc=acc, centroid=centroid, amen=amen,
                side=side)


def fine_graph(net):
    """Splice one access node per plot into its street segment."""
    xy, edges, pe, pt = net["xy"], net["edges"], net["pe"], net["pt"]
    n_i = len(xy); P = len(pe)
    order = np.lexsort((pt, pe))            # plots sorted by edge then t
    plot_node = np.empty(P, int); plot_node[order] = n_i + np.arange(P)
    rows, cols, w = [], [], []
    pe_s, pt_s = pe[order], pt[order]
    starts = np.searchsorted(pe_s, np.arange(len(edges)))
    ends = np.searchsorted(pe_s, np.arange(len(edges)), side="right")
    L = np.linalg.norm(xy[edges[:, 1]] - xy[edges[:, 0]], axis=1)
    for e in range(len(edges)):
        a, b = edges[e]
        s, t = starts[e], ends[e]
        chain = [a] + list(n_i + np.arange(s, t)) + [b]
        ts = np.r_[0.0, pt_s[s:t], 1.0]
        seg = np.diff(ts) * L[e]
        rows.extend(chain[:-1]); cols.extend(chain[1:]); w.extend(np.maximum(seg, 1e-3))
    N = n_i + P
    G = sp.coo_matrix((w, (rows, cols)), shape=(N, N)).tocsr()
    G = (G + G.T).tocsr()
    return G, plot_node, np.zeros(P)


def coarse_graph(net):
    xy, edges = net["xy"], net["edges"]
    L = np.linalg.norm(xy[edges[:, 1]] - xy[edges[:, 0]], axis=1)
    N = len(xy)
    G = sp.coo_matrix((L, (edges[:, 0], edges[:, 1])), shape=(N, N)).tocsr()
    G = (G + G.T).tocsr()
    d, node = cKDTree(xy).query(net["centroid"])
    return G, node, d


def peak_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _reach_chunk(args):
    G, src, is_plot_w, radius = args
    D = dijkstra(G, directed=False, indices=src, limit=radius)
    return (np.isfinite(D) * is_plot_w).sum(axis=1)


def run(metric, graph, n_plots, workers, k):
    t0 = time.perf_counter()
    net = build(n_plots)
    G, plot_node, off = fine_graph(net) if graph == "fine" else coarse_graph(net)
    t_build = time.perf_counter() - t0
    N = G.shape[0]
    plot_w = np.bincount(plot_node, minlength=N).astype(float)  # plots per node
    amen_nodes = np.unique(plot_node[net["amen"]])
    out = dict(metric=metric, graph=graph, plots=n_plots, nodes=N, edges=G.nnz // 2,
               area_km2=round((net["side"] * SPACING / 1000) ** 2, 1), build_s=round(t_build, 2))
    t = time.perf_counter()
    if metric == "a1":
        D = dijkstra(G, directed=False, indices=int(plot_node[0]))
        out["check_max_m"] = float(D[np.isfinite(D)].max())
    elif metric == "a1nx":
        import networkx as nx
        H = nx.from_scipy_sparse_array(G, edge_attribute="length")
        t = time.perf_counter()
        D = nx.single_source_dijkstra_path_length(H, int(plot_node[0]), weight="length")
        out["check_max_m"] = float(max(D.values()))
    elif metric == "a2":
        D = dijkstra(G, directed=False, indices=amen_nodes, min_only=True)
        dp = D[plot_node] + off
        out["amenities"] = int(len(amen_nodes))
        out["median_to_nearest_m"] = float(np.median(dp))
        out["p95_to_nearest_m"] = float(np.percentile(dp, 95))
    elif metric == "a2nx":
        import networkx as nx
        H = nx.from_scipy_sparse_array(G, edge_attribute="length")
        t = time.perf_counter()
        D = nx.multi_source_dijkstra_path_length(H, set(amen_nodes.tolist()), weight="length")
        out["median_to_nearest_m"] = float(np.median([D[int(p)] for p in plot_node]))
    elif metric == "b":
        # sources: every node that carries a plot (fine: one per plot; coarse: intersections)
        src_nodes = np.unique(plot_node) if graph == "coarse" else plot_node
        chunk = 256 if graph == "fine" else 1024
        chunks = [src_nodes[i:i + chunk] for i in range(0, len(src_nodes), chunk)]
        if workers > 1:
            from multiprocessing import get_context
            with get_context("fork").Pool(workers) as pool:
                parts = pool.map(_reach_chunk, [(G, c, plot_w, REACH_R) for c in chunks])
        else:
            parts = [_reach_chunk((G, c, plot_w, REACH_R)) for c in chunks]
        node_count = np.zeros(N); node_count[src_nodes] = np.concatenate(parts)
        reach = node_count[plot_node]
        out["median_plots_within_800m"] = float(np.median(reach))
    elif metric == "c":
        import networkx as nx
        H = nx.from_scipy_sparse_array(G, edge_attribute="length")
        t = time.perf_counter()
        bc = nx.betweenness_centrality(H, k=k, weight="length", seed=7, normalized=True)
        out["k"] = k
        out["per_source_s"] = None  # filled below
    elif metric == "d":
        W = np.ones(len(amen_nodes))  # amenity weights (e.g. floor area); 1 here
        acc = np.zeros(N)
        for i in range(0, len(amen_nodes), 64):
            D = dijkstra(G, directed=False, indices=amen_nodes[i:i + 64], limit=GRAV_R)
            E = np.exp(-GRAV_BETA * D)          # exp(-inf) = 0 outside cut-off
            acc += W[i:i + 64] @ E
        score = acc[plot_node] * np.exp(-GRAV_BETA * off)
        out["median_gravity"] = float(np.median(score))
    else:
        raise SystemExit("unknown metric")
    out["time_s"] = round(time.perf_counter() - t, 3)
    if metric == "c":
        out["per_source_s"] = round(out["time_s"] / k, 4)
        out["exact_extrapolated_s"] = round(out["per_source_s"] * N, 0)
    out["workers"] = workers
    out["peak_rss_mb"] = round(peak_mb(), 0)
    out["loadavg_1m"] = round(os.getloadavg()[0], 2)  # other jobs share this VM
    return out


def export(dirname, n_plots):
    os.makedirs(dirname, exist_ok=True)
    net = build(n_plots)
    G, plot_node, _ = fine_graph(net)
    G.sort_indices()
    G.indptr.astype(np.int32).tofile(os.path.join(dirname, "indptr.i32"))
    G.indices.astype(np.int32).tofile(os.path.join(dirname, "indices.i32"))
    G.data.astype(np.float64).tofile(os.path.join(dirname, "weights.f64"))
    plot_node.astype(np.int32).tofile(os.path.join(dirname, "plot_node.i32"))
    np.unique(plot_node[net["amen"]]).astype(np.int32).tofile(os.path.join(dirname, "amen_node.i32"))
    print(json.dumps(dict(nodes=G.shape[0], directed_arcs=G.nnz, plots=n_plots)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plots", type=int, default=100000)
    ap.add_argument("--graph", choices=["fine", "coarse"], default="fine")
    ap.add_argument("--metric", default="a1")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--k", type=int, default=100)
    ap.add_argument("--export")
    a = ap.parse_args()
    if a.export:
        export(a.export, a.plots)
    else:
        print(json.dumps(run(a.metric, a.graph, a.plots, a.workers, a.k)))
