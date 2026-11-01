using System.Diagnostics;
using System.Runtime.InteropServices;

// Benchmark 1: CPython embedded in a Native AOT .NET app through the C API.
unsafe
{
    string mode = args.Length > 0 ? args[0] : "full";
    long t0 = Stopwatch.GetTimestamp();
    // Linux only: load libpython with RTLD_GLOBAL so C extension modules (numpy etc.) can resolve Py* symbols.
    // .NET's own loader uses RTLD_LAZY without RTLD_GLOBAL. Pass "noglobal" to see what happens without this.
    if (mode != "noglobal")
    {
        nint h = Py.dlopen("libpython3.13.so.1.0", Py.RTLD_NOW | Py.RTLD_GLOBAL);
        if (h == 0) throw new InvalidOperationException("dlopen libpython failed");
    }
    int already = Py.Py_IsInitialized();               // first P/Invoke: dlopen + dlsym of libpython
    long t1 = Stopwatch.GetTimestamp();
    Py.Py_InitializeEx(0);                             // 0 = do not install Python signal handlers
    long t2 = Stopwatch.GetTimestamp();

    const string code = """
from array import array
C, S, TX, TY = 0.8660254037844387, 0.5, 10.0, -3.0

def noop():
    return None

def transform_tuples(pts):
    # pts: list of (x, y) tuples of Python floats; returns a new list of tuples
    return [(C*x - S*y + TX, S*x + C*y + TY) for (x, y) in pts]

def transform_buffer(mv):
    # mv: writable memoryview over the host's double[] (x0, y0, x1, y1, ...); transformed in place
    d = mv.cast('d')
    v = d.tolist()
    xs = v[0::2]; ys = v[1::2]
    out = array('d', v)
    out[0::2] = array('d', [C*x - S*y + TX for x, y in zip(xs, ys)])
    out[1::2] = array('d', [S*x + C*y + TY for x, y in zip(xs, ys)])
    d[:] = out
    return None
""";
    nint main = Py.Check(Py.PyImport_AddModule("__main__"), "AddModule");
    nint g = Py.PyModule_GetDict(main);
    nint r = Py.Check(Py.PyRun_StringFlags(code, Py.Py_file_input, g, g, 0), "module code");
    Py.Py_DecRef(r);
    long t3 = Stopwatch.GetTimestamp();

    // optional numpy path (numpy 2.x is installed system wide on this VM)
    bool haveNumpy = true;
    nint rn = Py.PyRun_StringFlags("""
import numpy as np
_R = np.array([[C, -S], [S, C]]); _T = np.array([TX, TY])
def transform_numpy(mv):
    a = np.frombuffer(mv, dtype=np.float64).reshape(-1, 2)
    a[:] = a @ _R.T + _T
""", Py.Py_file_input, g, g, 0);
    if (rn == 0) { Py.PyErr_Print(); haveNumpy = false; } else Py.Py_DecRef(rn);
    long t4 = Stopwatch.GetTimestamp();

    Stat.Line("p1 startup: first P/Invoke (dlopen libpython)", $"{Stat.Us(t1 - t0):F0} us (already={already})");
    Stat.Line("p1 startup: Py_InitializeEx(0)", $"{Stat.Us(t2 - t1):F0} us");
    Stat.Line("p1 startup: define module functions", $"{Stat.Us(t3 - t2):F0} us");
    Stat.Line("p1 startup: import numpy", haveNumpy ? $"{Stat.Us(t4 - t3):F0} us" : "numpy not available");
    Stat.Line("p1 startup: total to ready (no numpy)", $"{Stat.Us(t3 - t0):F0} us");
    if (mode != "full") { Py.Py_FinalizeEx(); return; }

    nint noop = Py.PyDict_GetItemString(g, "noop");            // borrowed
    nint fTuples = Py.PyDict_GetItemString(g, "transform_tuples");
    nint fBuffer = Py.PyDict_GetItemString(g, "transform_buffer");
    nint fNumpy = haveNumpy ? Py.PyDict_GetItemString(g, "transform_numpy") : 0;

    // ---- empty call, GIL already held by this thread
    Stat.Run("p1 empty call (GIL held)", 10_000, 200_000, () =>
    {
        nint res = Py.PyObject_CallNoArgs(noop);
        Py.Py_DecRef(res);
    }, "payload=0 B");
    // batched mean (removes Stopwatch overhead from the number)
    {
        const int N = 1_000_000;
        long a = Stopwatch.GetTimestamp();
        for (int i = 0; i < N; i++) { nint res = Py.PyObject_CallNoArgs(noop); Py.Py_DecRef(res); }
        Stat.Line("p1 empty call (GIL held), batched mean of 1e6", $"{Stat.Us(Stopwatch.GetTimestamp() - a) * 1000.0 / N:F1} ns per call");
    }

    // ---- point marshalling: list of N tuples of Python floats in, list of tuples out
    foreach (int n in new[] { 10_000, 100_000 })
    {
        double[] src = Pts.Make(n);
        double[] expect = Pts.Reference(src);
        double[] dst = new double[src.Length];
        int iters = n == 10_000 ? 500 : 100, warm = n == 10_000 ? 20 : 5;
        string payload = $"payload={n} points = {n * 16} B of float64 each way";

        Stat.Run($"p1 tuples round trip N={n} (build list + call + read back)", warm, iters, () =>
        {
            nint list = Py.PyList_New(n);
            for (int i = 0; i < n; i++)
            {
                nint t = Py.PyTuple_New(2);
                Py.PyTuple_SetItem(t, 0, Py.PyFloat_FromDouble(src[2 * i]));
                Py.PyTuple_SetItem(t, 1, Py.PyFloat_FromDouble(src[2 * i + 1]));
                Py.PyList_SetItem(list, i, t);
            }
            nint res = Py.Check(Py.PyObject_CallOneArg(fTuples, list), "transform_tuples");
            for (int i = 0; i < n; i++)
            {
                nint t = Py.PyList_GetItem(res, i);
                dst[2 * i] = Py.PyFloat_AsDouble(Py.PyTuple_GetItem(t, 0));
                dst[2 * i + 1] = Py.PyFloat_AsDouble(Py.PyTuple_GetItem(t, 1));
            }
            Py.Py_DecRef(res);
            Py.Py_DecRef(list);
        }, payload);
        Stat.Line($"p1 tuples N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");

        // split: marshal-in only, Python compute only (prebuilt list), marshal-out only
        Stat.Run($"p1 tuples N={n} part: build Python list only", warm, iters, () =>
        {
            nint list = Py.PyList_New(n);
            for (int i = 0; i < n; i++)
            {
                nint t = Py.PyTuple_New(2);
                Py.PyTuple_SetItem(t, 0, Py.PyFloat_FromDouble(src[2 * i]));
                Py.PyTuple_SetItem(t, 1, Py.PyFloat_FromDouble(src[2 * i + 1]));
                Py.PyList_SetItem(list, i, t);
            }
            Py.Py_DecRef(list);
        }, payload);
        {
            nint list = Py.PyList_New(n);
            for (int i = 0; i < n; i++)
            {
                nint t = Py.PyTuple_New(2);
                Py.PyTuple_SetItem(t, 0, Py.PyFloat_FromDouble(src[2 * i]));
                Py.PyTuple_SetItem(t, 1, Py.PyFloat_FromDouble(src[2 * i + 1]));
                Py.PyList_SetItem(list, i, t);
            }
            Stat.Run($"p1 tuples N={n} part: Python call only (list comprehension)", warm, iters, () =>
            {
                nint res = Py.PyObject_CallOneArg(fTuples, list);
                Py.Py_DecRef(res);
            }, payload);
            nint res2 = Py.PyObject_CallOneArg(fTuples, list);
            Stat.Run($"p1 tuples N={n} part: read result back only", warm, iters, () =>
            {
                for (int i = 0; i < n; i++)
                {
                    nint t = Py.PyList_GetItem(res2, i);
                    dst[2 * i] = Py.PyFloat_AsDouble(Py.PyTuple_GetItem(t, 0));
                    dst[2 * i + 1] = Py.PyFloat_AsDouble(Py.PyTuple_GetItem(t, 1));
                }
            }, payload);
            Py.Py_DecRef(res2);
            Py.Py_DecRef(list);
        }

        // ---- buffer path: memoryview over pinned double[], transformed in place by pure Python
        Stat.Run($"p1 buffer (memoryview, pure Python) N={n}", warm, iters, () =>
        {
            Array.Copy(src, dst, src.Length);
            fixed (double* p = dst)
            {
                nint mv = Py.PyMemoryView_FromMemory((byte*)p, dst.Length * 8, Py.PyBUF_WRITE);
                nint res = Py.Check(Py.PyObject_CallOneArg(fBuffer, mv), "transform_buffer");
                Py.Py_DecRef(res);
                Py.Py_DecRef(mv);
            }
        }, payload + ", zero copy across the boundary");
        Stat.Line($"p1 buffer N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");

        if (haveNumpy)
        {
            Stat.Run($"p1 buffer (memoryview, numpy) N={n}", warm, iters, () =>
            {
                Array.Copy(src, dst, src.Length);
                fixed (double* p = dst)
                {
                    nint mv = Py.PyMemoryView_FromMemory((byte*)p, dst.Length * 8, Py.PyBUF_WRITE);
                    nint res = Py.Check(Py.PyObject_CallOneArg(fNumpy, mv), "transform_numpy");
                    Py.Py_DecRef(res);
                    Py.Py_DecRef(mv);
                }
            }, payload + ", zero copy across the boundary");
            Stat.Line($"p1 numpy N={n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
        }
    }

    // ---- GIL released by the host thread; each call takes it with PyGILState_Ensure/Release (realistic for a UI app with worker threads)
    nint ts = Py.PyEval_SaveThread();
    Stat.Run("p1 empty call with PyGILState_Ensure/Release each call (same thread)", 10_000, 200_000, () =>
    {
        int st = Py.PyGILState_Ensure();
        nint res = Py.PyObject_CallNoArgs(noop);
        Py.Py_DecRef(res);
        Py.PyGILState_Release(st);
    }, "payload=0 B");
    {
        double[] times = new double[20_000];
        var th = new Thread(() =>
        {
            for (int i = 0; i < 1000; i++) { int s0 = Py.PyGILState_Ensure(); Py.Py_DecRef(Py.PyObject_CallNoArgs(noop)); Py.PyGILState_Release(s0); }
            for (int i = 0; i < times.Length; i++)
            {
                long a = Stopwatch.GetTimestamp();
                int st = Py.PyGILState_Ensure();
                nint res = Py.PyObject_CallNoArgs(noop);
                Py.Py_DecRef(res);
                Py.PyGILState_Release(st);
                times[i] = Stat.Us(Stopwatch.GetTimestamp() - a);
            }
        });
        th.Start(); th.Join();
        Stat.Print("p1 empty call with PyGILState_Ensure/Release from a .NET worker thread", times, "payload=0 B");
    }
    {
        double[] times = new double[200_000];
        var th = new Thread(() =>
        {
            int s0 = Py.PyGILState_Ensure();       // create this thread's PyThreadState once
            nint mine = Py.PyEval_SaveThread();     // release the GIL but keep the thread state alive
            for (int i = 0; i < 10_000; i++) { Py.PyEval_RestoreThread(mine); Py.Py_DecRef(Py.PyObject_CallNoArgs(noop)); mine = Py.PyEval_SaveThread(); }
            for (int i = 0; i < times.Length; i++)
            {
                long a = Stopwatch.GetTimestamp();
                Py.PyEval_RestoreThread(mine);
                nint res = Py.PyObject_CallNoArgs(noop);
                Py.Py_DecRef(res);
                mine = Py.PyEval_SaveThread();
                times[i] = Stat.Us(Stopwatch.GetTimestamp() - a);
            }
            Py.PyEval_RestoreThread(mine);
            Py.PyGILState_Release(s0);
        });
        th.Start(); th.Join();
        Stat.Print("p1 empty call from a .NET worker thread that keeps its PyThreadState (RestoreThread/SaveThread per call)", times, "payload=0 B");
    }
    Py.PyEval_RestoreThread(ts);

    long f0 = Stopwatch.GetTimestamp();
    Py.Py_FinalizeEx();
    Stat.Line("p1 Py_FinalizeEx", $"{Stat.Us(Stopwatch.GetTimestamp() - f0):F0} us");
}
