// C9 benchmark, C# port: the same metrics as bench_walk.py, in-process, on the same graph.
// Input: CSR binaries written by `python3 bench_walk.py --export <dir> --plots N`.
// Usage: dotnet run -c Release -- <dir> <threads>
using System.Diagnostics;
using System.Runtime.InteropServices;

static T[] Load<T>(string path) where T : struct =>
    MemoryMarshal.Cast<byte, T>(File.ReadAllBytes(path)).ToArray();

var dir = args[0];
int threads = args.Length > 1 ? int.Parse(args[1]) : Environment.ProcessorCount;
var indptr = Load<int>(Path.Combine(dir, "indptr.i32"));
var indices = Load<int>(Path.Combine(dir, "indices.i32"));
var w = Load<double>(Path.Combine(dir, "weights.f64"));
var plotNode = Load<int>(Path.Combine(dir, "plot_node.i32"));
var amenNode = Load<int>(Path.Combine(dir, "amen_node.i32"));
int n = indptr.Length - 1;
var plotsAt = new int[n];
foreach (var p in plotNode) plotsAt[p]++;
var po = new ParallelOptions { MaxDegreeOfParallelism = threads };
Console.WriteLine($"nodes={n} arcs={indices.Length} plots={plotNode.Length} amenities={amenNode.Length} threads={threads}");

void Report(string name, Stopwatch sw, string extra = "") =>
    Console.WriteLine($"{name,-38} {sw.Elapsed.TotalSeconds,9:F3} s  peakWS={Process.GetCurrentProcess().PeakWorkingSet64 / 1048576} MB {extra}");

// Dijkstra from a set of sources, stopping at `limit`. Uses caller-owned dist array and
// touched list so a bounded search costs only what it reaches (no O(n) reset per source).
void Dijkstra(ReadOnlySpan<int> sources, double limit, double[] dist, List<int> touched,
              PriorityQueue<int, double> pq, Action<int, double>? visit = null)
{
    foreach (var s in sources) { dist[s] = 0; touched.Add(s); pq.Enqueue(s, 0); }
    while (pq.TryDequeue(out int u, out double du))
    {
        if (du > dist[u]) continue;            // stale entry
        visit?.Invoke(u, du);
        for (int e = indptr[u]; e < indptr[u + 1]; e++)
        {
            int v = indices[e]; double dv = du + w[e];
            if (dv <= limit && dv < dist[v])
            {
                if (double.IsPositiveInfinity(dist[v])) touched.Add(v);
                dist[v] = dv; pq.Enqueue(v, dv);
            }
        }
    }
}
double[] NewDist() { var d = new double[n]; Array.Fill(d, double.PositiveInfinity); return d; }
void Reset(double[] d, List<int> t) { foreach (var i in t) d[i] = double.PositiveInfinity; t.Clear(); }

// (a1) single source
{
    var sw = Stopwatch.StartNew();
    var d = NewDist(); var t = new List<int>(); var pq = new PriorityQueue<int, double>();
    Dijkstra(new[] { plotNode[0] }, double.PositiveInfinity, d, t, pq);
    Report("a1 single-source, whole network", sw, $"max={d.Where(double.IsFinite).Max():F0} m");
}
// (a2) all plots to nearest amenity: one multi-source Dijkstra
{
    var sw = Stopwatch.StartNew();
    var d = NewDist(); var t = new List<int>(); var pq = new PriorityQueue<int, double>();
    Dijkstra(amenNode, double.PositiveInfinity, d, t, pq);
    var near = plotNode.Select(p => d[p]).OrderBy(x => x).ToArray();
    Report("a2 all plots -> nearest amenity", sw, $"median={near[near.Length / 2]:F0} m");
}
// (b) reach: plots within 800 m of every plot (one bounded Dijkstra per plot)
{
    var sw = Stopwatch.StartNew();
    var reach = new int[plotNode.Length];
    Parallel.For(0, plotNode.Length, po,
        () => (NewDist(), new List<int>(4096), new PriorityQueue<int, double>()),
        (i, _, st) =>
        {
            var (d, t, pq) = st; int c = 0;
            Dijkstra(new[] { plotNode[i] }, 800.0, d, t, pq, (u, du) => c += plotsAt[u]);
            reach[i] = c; Reset(d, t); return st;
        }, _ => { });
    var s = reach.OrderBy(x => x).ToArray();
    Report("b  reach: plots within 800 m, all plots", sw, $"median={s[s.Length / 2]}");
}
// (d) gravity: A_i = sum_j W_j exp(-beta d_ij), d_ij <= 2400 m, one bounded search per amenity
{
    double beta = Math.Log(2) / 400.0;
    var sw = Stopwatch.StartNew();
    var acc = new double[n]; var gate = new object();
    Parallel.For(0, amenNode.Length, po,
        () => (NewDist(), new List<int>(65536), new PriorityQueue<int, double>(), new double[n]),
        (j, _, st) =>
        {
            var (d, t, pq, a) = st;
            Dijkstra(new[] { amenNode[j] }, 2400.0, d, t, pq, (u, du) => a[u] += Math.Exp(-beta * du));
            Reset(d, t); return st;
        },
        st => { lock (gate) for (int i = 0; i < n; i++) acc[i] += st.Item4[i]; });
    var g = plotNode.Select(p => acc[p]).OrderBy(x => x).ToArray();
    Report("d  gravity score, all plots", sw, $"median={g[g.Length / 2]:F3}");
}
// (c) betweenness, Brandes (weighted). Global with k sampled sources, and local with radius.
double[] Betweenness(int[] sources, double radius)
{
    var bc = new double[n]; var gate = new object();
    Parallel.For(0, sources.Length, po,
        () => (NewDist(), new List<int>(4096), new PriorityQueue<int, double>(),
               new double[n], new double[n], new List<int>(4096), new double[n]),
        (k, _, st) =>
        {
            var (d, t, pq, sigma, delta, order, local) = st;
            int s = sources[k];
            sigma[s] = 1;
            Dijkstra(new[] { s }, radius, d, t, pq, (u, du) => order.Add(u));
            // sigma in settle order: predecessors are neighbours v with d[v] + w == d[u]
            foreach (var u in order)
                for (int e = indptr[u]; e < indptr[u + 1]; e++)
                {
                    int v = indices[e];
                    if (Math.Abs(d[v] + w[e] - d[u]) < 1e-9 && v != u) sigma[u] += sigma[v];
                }
            for (int i = order.Count - 1; i >= 0; i--)
            {
                int u = order[i];
                for (int e = indptr[u]; e < indptr[u + 1]; e++)
                {
                    int v = indices[e];
                    if (Math.Abs(d[v] + w[e] - d[u]) < 1e-9 && sigma[u] > 0)
                        delta[v] += sigma[v] / sigma[u] * (1 + delta[u]);
                }
                if (u != s) local[u] += delta[u];
            }
            foreach (var u in order) { sigma[u] = 0; delta[u] = 0; }
            order.Clear(); Reset(d, t); return st;
        },
        st => { lock (gate) for (int i = 0; i < n; i++) bc[i] += st.Item7[i]; });
    return bc;
}
if (args.Length > 2 && args[2] == "validate")
{   // exact global betweenness to a text file, to check against networkx on a small graph
    File.WriteAllLines(Path.Combine(dir, "bc_csharp.txt"),
        Betweenness(Enumerable.Range(0, n).ToArray(), double.PositiveInfinity).Select(x => x.ToString("R")));
    return;
}
{
    var rng = new Random(7);
    var sample = Enumerable.Range(0, n).OrderBy(_ => rng.Next()).Take(100).ToArray();
    var sw = Stopwatch.StartNew();
    Betweenness(sample, double.PositiveInfinity);
    Report("c  betweenness global, k=100 sources", sw, $"per-source={sw.Elapsed.TotalSeconds / 100:F4} s");
    sw.Restart();
    Betweenness(Enumerable.Range(0, n).ToArray(), 800.0);
    Report("c' betweenness local r=800 m, all nodes", sw);
}
