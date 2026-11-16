import sys, numpy as np, scipy.sparse as sp, networkx as nx
d = sys.argv[1]
ip = np.fromfile(d+"/indptr.i32", np.int32); ix = np.fromfile(d+"/indices.i32", np.int32); w = np.fromfile(d+"/weights.f64")
G = sp.csr_matrix((w, ix, ip))
H = nx.from_scipy_sparse_array(G, edge_attribute="length")
bc = nx.betweenness_centrality(H, weight="length", normalized=False)
nxv = np.array([bc[i] for i in range(G.shape[0])]) * 2   # nx halves undirected pair counts
cs = np.loadtxt(d+"/bc_csharp.txt")
print("nodes", len(cs), "max abs diff", np.abs(nxv-cs).max(), "max value", cs.max())
