using System.Diagnostics;
using CSnakes.Runtime;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

// Benchmark 3: CSnakes (source-generated bindings) under Native AOT.
// args: <python folder laid out as bin/python3, lib/libpython3.13.so, lib/python3.13>
long t0 = Stopwatch.GetTimestamp();
var builder = Host.CreateApplicationBuilder(args.Length > 1 ? args[1..] : Array.Empty<string>());
builder.Services
    .WithPython()
    .WithHome(AppContext.BaseDirectory)          // folder holding bench_mod.py
    .FromFolder(args[0], "3.13");
var app = builder.Build();
long tb = Stopwatch.GetTimestamp();
var env = app.Services.GetRequiredService<IPythonEnvironment>();
long t1 = Stopwatch.GetTimestamp();
var mod = env.BenchMod();                        // generated from bench_mod.py
long t2 = Stopwatch.GetTimestamp();
Stat.Line("p3 startup: generic host build (no Python yet)", $"{Stat.Us(tb - t0):F0} us");
Stat.Line("p3 startup: Python environment ready (locate + Py_Initialize)", $"{Stat.Us(t1 - tb):F0} us");
Stat.Line("p3 startup: import bench_mod", $"{Stat.Us(t2 - t1):F0} us");
if (args.Length > 1 && args[1] == "startup") return;

Stat.Run("p3 CSnakes empty call", 10_000, 200_000, () => mod.Noop(), "payload=0 B");
foreach (int n in new[] { 10_000, 100_000 })
{
    double[] src = Pts.Make(n), expect = Pts.Reference(src), dst = new double[src.Length];
    int iters = n == 10_000 ? 300 : 50, warm = n == 10_000 ? 20 : 5;
    Stat.Run($"p3 CSnakes list[tuple[float,float]] N={n} round trip", warm, iters, () =>
    {
        var input = new (double, double)[n];
        for (int i = 0; i < n; i++) input[i] = (src[2 * i], src[2 * i + 1]);
        var res = mod.TransformTuples(input);
        for (int i = 0; i < n; i++) { var (x, y) = res[i]; dst[2 * i] = x; dst[2 * i + 1] = y; }
    }, $"payload={n} points = {n * 16} B of float64 each way");
    Stat.Line($"p3 tuples N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
    Stat.Run($"p3 CSnakes list[float] (flat) N={n} round trip", warm, iters, () =>
    {
        var res = mod.TransformFlat(src);
        for (int i = 0; i < res.Count; i++) dst[i] = res[i];
    }, $"payload={n} points = {n * 16} B of float64 each way");
    Stat.Line($"p3 flat N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
    Stat.Run($"p3 CSnakes bytes in/out (array module, pure Python) N={n} round trip", warm, iters, () =>
    {
        byte[] b = new byte[src.Length * 8];
        Buffer.BlockCopy(src, 0, b, 0, b.Length);
        byte[] r = mod.TransformBytes(b);
        Buffer.BlockCopy(r, 0, dst, 0, r.Length);
    }, $"payload={n * 16} B each way");
    Stat.Line($"p3 bytes N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
}
