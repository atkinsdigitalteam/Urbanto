using System.Diagnostics;
using Python.Runtime;

// Benchmark 4: pythonnet. Same code is published once with Native AOT and once as a normal JIT app.
long t0 = Stopwatch.GetTimestamp();
Runtime.PythonDLL = "/usr/lib/x86_64-linux-gnu/libpython3.13.so.1.0";
PythonEngine.Initialize();
long t1 = Stopwatch.GetTimestamp();
Stat.Line("p4 pythonnet PythonEngine.Initialize", $"{Stat.Us(t1 - t0):F0} us");
nint ts = PythonEngine.BeginAllowThreads();
using (Py.GIL())
{
    using var scope = Py.CreateScope();
    scope.Exec("""
C, S, TX, TY = 0.8660254037844387, 0.5, 10.0, -3.0
def noop():
    return None
def transform_tuples(pts):
    return [(C*x - S*y + TX, S*x + C*y + TY) for (x, y) in pts]
""");
    using PyObject noop = scope.Get("noop");
    using PyObject tf = scope.Get("transform_tuples");
    Stat.Run("p4 pythonnet empty call (GIL held)", 10_000, 100_000, () => { using var r = noop.Invoke(); }, "payload=0 B");
    foreach (int n in new[] { 10_000, 100_000 })
    {
        double[] src = Pts.Make(n), expect = Pts.Reference(src), dst = new double[src.Length];
        Stat.Run($"p4 pythonnet tuples N={n} round trip", n == 10_000 ? 10 : 3, n == 10_000 ? 100 : 20, () =>
        {
            var items = new PyObject[n];
            for (int i = 0; i < n; i++) items[i] = new PyTuple(new PyObject[] { new PyFloat(src[2 * i]), new PyFloat(src[2 * i + 1]) });
            using var list = new PyList(items);
            using var res = tf.Invoke(list);
            using var rl = new PyList(res);
            long cnt = rl.Length();
            for (int i = 0; i < cnt; i++)
            {
                using var t = rl[i];
                dst[2 * i] = t[0].As<double>(); dst[2 * i + 1] = t[1].As<double>();
            }
            foreach (var it in items) it.Dispose();
        }, $"payload={n} points");
        Stat.Line($"p4 tuples N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
    }
}
PythonEngine.EndAllowThreads(ts);
Console.WriteLine("p4 done");
if (args.Length > 0 && args[0] == "shutdown") { long s0 = Stopwatch.GetTimestamp(); PythonEngine.Shutdown(); Stat.Line("p4 PythonEngine.Shutdown", $"{Stat.Us(Stopwatch.GetTimestamp() - s0):F0} us"); }
