# R21M: measured cost of Python and C# script hosting for a .NET 10 Native AOT desktop app

Agent R21M for report C21. Measured on 2026-11-01.

**Read this first: these are Linux x64 numbers from a shared 4-core VM. Windows will differ.** Process start, pipe latency, DLL loading and
file sizes all behave differently on Windows. Treat the numbers as relative costs (which option is 10x slower than which), not as absolute
Windows timings. Where a number is a quote from a web page, it has a link. Where it is measured, the method and the result file in
`bench/` are named. All raw outputs are in `bench/**/run_*.txt`, build logs in `bench/**/build_*.log`, sizes in `bench/sizes.txt`.

## Setup and method (applies to every table below)

| item | value | source |
|---|---|---|
| Machine | 4 vCPU shared VM, 16 GB RAM, Linux 6.18 x86_64, Ubuntu 24.04 | measured: `nproc`, `free -m`, `uname -a` |
| .NET | SDK 10.0.403, runtime 10.0.14, installed into my folder with [dotnet-install.sh](https://dot.net/v1/dotnet-install.sh) `--channel 10.0`. The .NET 10 install worked, so .NET 8 was not used. | measured: `dotnet --info` |
| Native AOT toolchain | clang + lld on linux-x64, `PublishAot=true`, `RuntimeIdentifier=linux-x64`, Release | `bench/*/build_publish*.log` |
| Python | CPython 3.13.17 (Ubuntu package `libpython3.13 3.13.17-1+noble1`), `/usr/lib/x86_64-linux-gnu/libpython3.13.so.1.0`; numpy 2.5.3 preinstalled; msgpack 1.2.4 via `pip install --target` | measured: `dpkg -l`, `python3 -c "import numpy"` |
| Workload | "transform N points": rotate 30 degrees and translate (10, -3); N = 0 (empty call), 10,000 and 100,000 points; points are float64 (x, y) pairs, so 160,000 B and 1,600,000 B of raw data each way | `bench/common/Bench.cs` |
| Correctness | every run compares the result to a C# reference: max abs error 0 (pure Python) or 1.1e-13 (numpy) | `max abs error` lines in every `run_*.txt` |
| In-process timing | `Stopwatch.GetTimestamp()` around each call, warm-up first (10,000 calls for empty, 20 or 5 for points), then 200,000 / 500 / 100 timed calls; p50 and p95 are nearest-rank percentiles | `bench/common/Bench.cs` (`Stat.Run`) |
| Process start timing | `bench/tools/runmany.py`: starts the process K times (first run discarded as cache warm-up), wall clock with `time.perf_counter`, plus inner timestamps printed by the child | `bench/tools/runmany.py` |
| Noise | p95 is often 1.3x to 3x p50 on this shared VM; GC-heavy paths (CSnakes, pythonnet) have much larger p95 | all `run_*.txt` |

### Headline table (option | metric | value | method)

All values are p50 unless marked. "Round trip" means: points leave C#, Python or C# user code transforms them, points are back in a C# `double[]`.

| option | metric | value | method |
|---|---|---|---|
| CPython C API in AOT host ([LibraryImport]) | builds under Native AOT | yes, 0 warnings, 0 errors, 1.2 MiB exe | `bench/p1_cpython_aot/build_publish.log` |
| CPython C API in AOT host | startup: dlopen + Py_InitializeEx + define functions | 16.6 ms (p95 22.2) | 30 process runs, `bench/p1_cpython_aot/run_startup.txt` |
| CPython C API in AOT host | `import numpy` on top | +83.8 ms (p95 106.5) | same 30 runs |
| CPython C API in AOT host | empty call, GIL held | 0.07 us (p95 0.13); 52 ns batched mean of 1e6 | `run_full.txt` |
| CPython C API in AOT host | 10k points as list of tuples of Python floats | 4.32 ms (p95 5.08) | `run_full.txt` |
| CPython C API in AOT host | 10k points as zero-copy memoryview, numpy transform | 0.120 ms (p95 0.205) | `run_full.txt` |
| CPython C API in AOT host | 100k points tuples / memoryview+numpy | 65.7 ms / 2.69 ms | `run_full.txt` |
| python3 child over pipes | process start to first reply | 18.3 to 24.2 ms (no numpy), 99.6 ms (with numpy) | 20 spawns per format, `bench/p2_pipe/run_full.txt` |
| python3 child over pipes | empty round trip | 27.6 to 37.5 us (idle cores); 5.9 us when cores are kept busy | `run_full.txt`, `run_binnp_blas1.txt` |
| python3 child over pipes | 10k points: JSON / struct float64 / msgpack / float64+numpy | 30.1 ms / 3.15 ms / 2.87 ms / 0.49 ms | `run_full.txt` |
| python3 child over pipes | 100k points: JSON / struct float64 / msgpack / float64+numpy | 270.9 ms / 37.6 ms / 32.5 ms / 4.42 ms | `run_full.txt` |
| CSnakes 2.0.0-beta.350 | builds and runs under Native AOT | yes, 3 warnings (IL2067 x2, IL3050 x1, all inside CSnakes.Runtime) | `bench/p3_csnakes/build_publish_2.0.0-beta.350_detail.log` |
| CSnakes 1.2.1 (latest stable) | builds and runs under Native AOT | yes, 0 warnings | `build_publish_1.2.1_detail.log` |
| CSnakes | startup to Python ready | 86.2 ms (p95 115.7), most of it `import asyncio` | 20 runs, `run_startup_2.0.0-beta.350.txt`, `importtime_csnakes_vs_raw.txt` |
| CSnakes | empty call | 0.24 us (p95 0.27) | `run_full_2.0.0-beta.350.txt` |
| CSnakes | 10k points `list[tuple[float,float]]` / `bytes` | 15.6 ms (p95 36.1) / 2.83 ms | `run_full_2.0.0-beta.350.txt` |
| pythonnet 3.2.1 | Native AOT | builds with 219 warnings, crashes at `PythonEngine.Initialize()`: `PlatformNotSupportedException: Dynamic code generation is not supported on this platform` | `bench/p4_pythonnet/build_publish_aot.log`, `run_aot.txt` |
| Roslyn scripting 5.9.0, JIT process | first compile of a 10-line script, fresh process | 1,567 ms (IL-only NuGet DLLs); 654 ms with ReadyToRun | 10 process runs, `bench/p5a_roslyn_jit/run_first_x10.txt` |
| Roslyn scripting, JIT process | next compiles (new script text each time) | 143 ms (p95 441) with `CSharpScript`; 6.9 ms with `CSharpCompilation.Emit` + collectible ALC | `run_full.txt` |
| Roslyn scripting, JIT process | memory: 200 more `CSharpScript` compiles | working set +210.9 MB, never released; collectible ALC path: no growth | `run_full.txt` |
| Roslyn inside Native AOT | `CSharpScript` / `Assembly.Load` of emitted IL | both fail (`NotSupportedException`, `PlatformNotSupportedException`); `CSharpCompilation.Emit` itself works (19.8 ms first, 2.2 ms next); 30 warnings; 34.6 MiB exe | `bench/p5b_roslyn_aot/run_aot.txt`, `build_publish_aot.log` |
| AOT host + JIT C# helper over pipes | helper start / first compile / next compile | 71 ms / 1,401 ms / 6.7 ms (IL-only); 57 ms / 575 ms / 4.7 ms (ReadyToRun) | 8 spawns, `bench/p5c_host/run_fdd.txt`, `run_r2r.txt` |
| AOT host + JIT C# helper over pipes | empty / 10k / 100k round trip | 30.5 us / 0.263 ms / 3.41 ms | `run_fdd.txt` |
| Install size | libpython + trimmed stdlib (Linux) / python.org embeddable zip 3.13.17 | 19.7 MiB / 10.9 MiB zip, 21.6 MiB extracted | `bench/sizes.txt` |
| Install size | Roslyn compiler DLLs (en only) / with 13 satellite languages / ReadyToRun | 9.9 MiB / +7.0 MiB / 27.2 MiB | `bench/sizes.txt` |
| Install size | JIT helper: framework-dependent / self-contained linux-x64 / self-contained win-x64 / trimmed self-contained | 9.8 MiB (+ 78.8 MiB shared runtime) / 88.6 MiB / 86.6 MiB / 33.5 MiB | `bench/sizes.txt` |

---

### Option 1: CPython embedded through the C API with [LibraryImport] (Python 3.13.17, .NET 10.0.14, measured 2026-11-01)

**How it works:**
- `[LibraryImport]` generates the P/Invoke marshalling at compile time, so no IL stub is generated at run time; the docs say the runtime IL stub "isn't available for ahead-of-time (AOT) compiler or IL trimming scenarios" ([Microsoft Learn, P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation)).
- The host binds about 30 C API functions (`Py_InitializeEx`, `PyRun_StringFlags`, `PyObject_CallOneArg`, `PyList_New`, `PyFloat_FromDouble`, `PyMemoryView_FromMemory`, `PyGILState_Ensure`, ...) in `bench/p1_cpython_aot/Py.cs`; all are exported by `libpython3.13.so.1.0` (checked with `nm -D`).
- Two ways to pass points: build Python objects (a list of N tuples, 3N C API calls each way), or hand Python a zero-copy writable `memoryview` over the pinned `double[]` (`PyMemoryView_FromMemory`, 1 call). Python then works on the buffer with pure Python or numpy.
- Python's embedding guide notes that "Python needs to load library modules implemented as C dynamic extensions (.so files) linked against it" ([docs.python.org, Embedding Python](https://docs.python.org/3/extending/embedding.html)). On Linux, .NET's loader does not load libpython with `RTLD_GLOBAL`, so numpy failed with `undefined symbol: PyObject_SelfIter` until the host first called `dlopen("libpython3.13.so.1.0", RTLD_NOW | RTLD_GLOBAL)` (measured, `bench/p1_cpython_aot/run_noglobal.txt`). This is a Linux and macOS issue; on Windows `.pyd` files link `python313.dll` by name (not measured here).
- Threads: the Python docs say `PyGILState_Ensure()` does "not guarantee a persistent thread state ... a matched acquire/release pair may create and destroy a thread state each time", and recommend `PyThreadState_New` plus `PyEval_RestoreThread`/`PyEval_SaveThread` for a thread that calls in many times ([docs.python.org, Thread states and the GIL, 3.15 docs](https://docs.python.org/3/c-api/threads.html)). The measurement matches this (table below).

**Good to use because:**
- Builds under Native AOT with 0 warnings and a 1.2 MiB exe (measured, `build_publish.log`, `sizes.txt`); Native AOT forbids runtime code generation and dynamic loading ([Microsoft Learn, Native AOT limitations](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)), and this path needs neither.
- Lowest call overhead of everything measured: 52 ns per empty call.
- Zero-copy buffers make large point sets cheap: 10k points through numpy in 0.12 ms, 100k in 2.7 ms.

**Bad to use because:**
- You own refcounting, error handling, GIL rules and Python home discovery yourself (all visible in `Program.cs`). A bug crashes the whole CAD process; a Python crash or hang is an app crash or hang.
- The Linux RTLD_GLOBAL trap above (measured). Windows has its own discovery issues (not measured here).
- One interpreter per process: a runaway user script can only be stopped cooperatively; there is no safe kill without killing the app (design reasoning, not measured).
- Object marshalling is slow: list of tuples costs 4.3 ms for 10k points, about 36x the buffer+numpy path.

**Numbers:**

| property | value | source |
|---|---|---|
| AOT build | 0 warnings, 0 errors; exe 1,247,240 B (1.2 MiB) | measured: `dotnet publish -c Release`, `bench/p1_cpython_aot/build_publish.log`, `bench/sizes.txt` |
| first P/Invoke (dlopen libpython) | 1.04 ms (p95 1.21) | measured: 30 process runs, `run_startup.txt` |
| `Py_InitializeEx(0)` | 12.8 ms (p95 17.6) | same |
| startup to ready (no numpy) | 16.6 ms (p95 22.2) | same |
| `import numpy` | 83.8 ms (p95 106.5) | same |
| `Py_FinalizeEx` | 20.0 ms | measured: `run_full.txt` |
| empty call, GIL held | p50 0.07 us, p95 0.13 us; batched mean 52.1 ns | measured: 200,000 timed calls; 1e6 batched, `run_full.txt` |
| empty call with `PyGILState_Ensure/Release`, same thread | 0.16 us (p95 0.25) | same |
| empty call from a .NET worker thread, `PyGILState_Ensure/Release` per call | 6.64 us (p95 11.0) | measured: 20,000 calls on a new `Thread`, `run_full.txt` |
| empty call from a worker thread that keeps its thread state (`PyEval_RestoreThread/SaveThread`) | 0.18 us (p95 0.26) | measured: 200,000 calls, `run_full.txt` |
| 10k points, list of tuples, full round trip | 4.32 ms (p95 5.08); split: build list 1.56, Python list comprehension 1.93, read back 0.46 | measured: 500 calls each, `run_full.txt` |
| 10k points, memoryview, pure Python (`tolist` + `array`) | 3.17 ms (p95 3.68) | same |
| 10k points, memoryview, numpy | 0.120 ms (p95 0.205) | same |
| 100k points, tuples / memoryview pure Python / memoryview numpy | 65.7 ms (p95 81.0) / 41.8 ms (p95 62.4) / 2.69 ms (p95 3.50) | measured: 100 calls each, `run_full.txt` |
| payload | 10k points = 160,000 B float64 each way; 100k = 1,600,000 B | `bench/common/Bench.cs` |

**Take for Studio:**
- If Python must run in-process in the AOT app, the raw C API via `[LibraryImport]` is the only measured option that is both AOT clean and fast. Pass points as flat float64 buffers (memoryview), never as lists of tuples.
- Keep one long-lived Python thread state per worker thread; do not call `PyGILState_Ensure` per call from pool threads (about 37x slower in this test: 6.64 us vs 0.18 us).

### Option 2: separate python3 child process over stdin/stdout pipes (measured 2026-11-01)

**How it works:**
- The Native AOT host (`bench/p2_pipe/Program.cs`, `System.Diagnostics.Process`, 0 AOT warnings) starts `python3 -I worker.py <format>` and writes requests to its stdin, reads replies from stdout.
- Formats: (a) JSON, one object per line, flat list of numbers, written with `Utf8JsonWriter` and read with `Utf8JsonReader` (no reflection); (b) "bin": `<u32 length><u8 op><float64 little-endian array>`, decoded in Python with `array('d').frombytes` (equivalent to `struct` unpacking); (c) msgpack 1.2.4 on the Python side, a hand-written msgpack subset (array of float64) on the C# side; (d) "binnp": like bin but the transform uses numpy.
- The child is a normal Python with its own site-packages; a crash or hang in the child does not take the app down, and the host can kill and restart it (design reasoning, not measured).

**Good to use because:**
- No in-process risk and no AOT constraints at all: the host is plain .NET code (0 warnings, `bench/p2_pipe/build_publish.log`).
- With a binary float64 format the cost over in-process is small for 10k points: 3.15 ms vs 3.17 ms (pure Python memoryview in-process), and 0.49 ms vs 0.12 ms with numpy.
- A user's Python can be any version and any packages; a separate venv per library flow is possible.

**Bad to use because:**
- Fixed overhead per call: 27 to 37 us per empty round trip when cores are idle, about 400x the in-process C API call. Fine for one call per node evaluation, bad for one call per point.
- Pipe latency depends on CPU idle state on this VM: when numpy's OpenBLAS worker threads were spinning, the empty round trip fell to 5.9 us; with `OPENBLAS_NUM_THREADS=1` it went back to 27.0 us (measured, `run_binnp_blas1.txt`). Expect different numbers on Windows.
- JSON is 10x slower than binary: 30.1 ms for 10k points, 271 ms for 100k. Python's `json.loads` + `json.dumps` alone take 14.4 ms for 10k (measured, `run_py_parts.txt`), and C# `Utf8JsonWriter` takes 3.9 ms to write 20,000 doubles.
- Start cost 18 to 24 ms per child, about 100 ms if the child imports numpy.

**Numbers:**

| property | value | source |
|---|---|---|
| `python3 -I -c pass` / `-I -S` / `-I -c "import numpy"` | 16.0 / 10.8 / 100.9 ms (p95 21.9 / 15.3 / 124.6) | measured: 30 runs each, `bench/p2_pipe/run_python_start.txt` |
| process start to first reply: json / bin / msgpack / binnp | 24.2 / 18.7 / 18.3 / 99.6 ms (p95 33.4 / 22.2 / 23.8 / 132.0) | measured: 20 spawns each, `run_full.txt` |
| empty round trip: json / bin / msgpack | 31.4 / 27.6 / 37.5 us (p95 64.8 / 53.3 / 63.4) | measured: 5,000 round trips, `run_full.txt` |
| empty round trip, binnp (OpenBLAS threads spinning) / with `OPENBLAS_NUM_THREADS=1` | 5.9 us (p95 9.0) / 27.0 us (p95 40.8) | measured: `run_full.txt`, `run_binnp_blas1.txt` |
| 10k points: json | 30.1 ms (p95 43.2); 378,690 B out, 378,044 B back | measured: 300 round trips, `run_full.txt` |
| 10k points: bin (float64) | 3.15 ms (p95 4.48); 160,005 B each way | same |
| 10k points: msgpack | 2.87 ms (p95 3.43); 180,019 B out, 180,012 B back | same |
| 10k points: binnp | 0.487 ms (p95 0.769); with 1 BLAS thread 0.463 ms (p95 0.646) | same |
| 100k points: json / bin / msgpack / binnp | 270.9 / 37.6 / 32.5 / 4.42 ms (p95 349.7 / 55.3 / 37.5 / 5.20); json payload 3,787,471 B out | measured: 50 round trips, `run_full.txt` |
| C# side encode only, 10k points: json / bin / msgpack | 3,902 / 4.1 / 23.1 us | measured: `run_full.txt` (`host-side encode only`) |
| Python side only, 10k: transform / json loads+dumps / array decode+encode / msgpack unpack+pack | 1.27 / 14.4 / 0.54 / 0.92 ms | measured: `timeit`, 50 repeats, `run_py_parts.txt` |

**Take for Studio:**
- A child process with a binary float64 frame is the robust default for user Python: about 3 ms per 10k points with pure Python, 0.5 ms with numpy, and the app survives a bad script.
- Never use JSON for geometry arrays. Use raw float64 frames (or msgpack if you need structure).
- Keep the child alive between evaluations (start costs 18 to 100 ms); batch whole lists per call.

### Option 3: CSnakes (CSnakes.Runtime 2.0.0-beta.350 and 1.2.1, measured 2026-11-01)

**How it works:**
- CSnakes is "a .NET Source Generator and Runtime that you can use to embed Python code and libraries into your C#.NET Solution", calling Python through the CPython C API in-process ([CSnakes README on GitHub](https://github.com/tonybaloney/CSnakes)). NuGet owners are aaron.powell, raboof and anthonyshaw ([nuget.org CSnakes.Runtime](https://www.nuget.org/packages/CSnakes.Runtime)). I did not find a page that states Microsoft backing, so "Microsoft-backed" is not verified.
- Python functions with type hints in `.py` files (added as `AdditionalFiles` with `SourceItemType="Python"`) become typed C# methods: `list[tuple[float, float]]` maps to `IReadOnlyList<(double, double)>`, `bytes` to `byte[]` (`bench/p3_csnakes/bench_mod.py`).
- Its docs say Native AOT "only works with source generated bindings" because dynamic conversion "requires reflection when done dynamically, which is not supported in Native AOT" ([CSnakes docs, Native AOT](https://tonybaloney.github.io/CSnakes/v1/advanced/native-aot/), [doc source](https://raw.githubusercontent.com/tonybaloney/CSnakes/main/docs/advanced/native-aot.md)).
- Python is found by locators; `FromFolder(folder, version)` expects `lib/libpython3.13.so` and `lib/python3.13` under the folder on Linux ([PythonLocator.cs](https://raw.githubusercontent.com/tonybaloney/CSnakes/main/src/CSnakes.Runtime/Locators/PythonLocator.cs), [ServiceCollectionExtensions.cs](https://raw.githubusercontent.com/tonybaloney/CSnakes/main/src/CSnakes.Runtime/ServiceCollectionExtensions.cs)). I made a folder of symlinks to the Ubuntu Python. The host is `Microsoft.Extensions.Hosting`.

**Good to use because:**
- It builds and runs under Native AOT on .NET 10: 2.0.0-beta.350 with 3 warnings, 1.2.1 with 0 warnings (measured). Calls are typed and generated, so no hand-written refcounting.
- Empty call 0.24 us, still in the sub-microsecond range.
- With `bytes` arguments the 10k-point round trip (2.83 ms) is as fast as the raw C API with pure Python.

**Bad to use because:**
- Collection conversion is slow: 10k points as `list[tuple[float,float]]` take 15.6 ms (p95 36.1), 3.6x the raw C API tuple path (4.32 ms); 100k take 213 ms with p95 607 ms (measured). Large p95 suggests heavy GC of wrapper objects (inference, not profiled).
- Startup is 86 ms to "Python ready" vs 16.6 ms for the raw C API, because CSnakes imports `asyncio` at start (66 ms cumulative under `PYTHONPROFILEIMPORTTIME`, `importtime_csnakes_vs_raw.txt`).
- `FromFolder` puts only the stdlib and the home folder on `sys.path`: system numpy was not importable (`ModuleNotFoundError`, `run_full_2.0.0-beta.350.txt`); you must manage a venv (`WithVirtualEnvironment`) or redistributable Python.
- The 2.x line is still beta (2.0.0-beta.350, 2026-07-15) while the last stable is 1.2.1 from 2025-08-08 ([NuGet registration](https://api.nuget.org/v3/registration5-gz-semver2/csnakes.runtime/index.json)). Its packaged README still says "Supports .NET 8 and 9" and "Python 3.9-3.13" (README.md inside the 2.0.0-beta.350 nupkg).
- Same in-process risk as option 1 (a Python crash is an app crash).

**Numbers:**

| property | value | source |
|---|---|---|
| AOT build, 2.0.0-beta.350 | 3 warnings: IL2067 x2 in `PyObject.As(Type)`, IL3050 x1 in `PyObjectImporters.Runtime<T>.BareImport` ("Calls 'System.Type.MakeGenericType'... Use methods generated by the source generator instead"); 0 errors | measured: `dotnet publish -p:TrimmerSingleWarn=false`, `bench/p3_csnakes/build_publish_2.0.0-beta.350_detail.log` |
| AOT build, 1.2.1 | 0 warnings, 0 errors | measured: `build_publish_1.2.1_detail.log` |
| exe size | 4.79 MB (beta.350), 4.73 MB (1.2.1) vs 1.25 MB raw C API | measured: `ls -l`, `sizes.txt` |
| startup: host build / Python ready / import module | 8.95 / 86.2 / 0.44 ms (p95 12.0 / 115.7 / 0.88); wall to exit 112 ms | measured: 20 runs, `run_startup_2.0.0-beta.350.txt` |
| empty call | 0.24 us (p95 0.27) beta.350; 0.24 us (p95 0.47) 1.2.1 | measured: 200,000 calls, `run_full_*.txt` |
| 10k points `list[tuple[float,float]]` | 15.6 ms (p95 36.1) beta.350; 19.1 ms (p95 37.6) 1.2.1 | measured: 300 calls |
| 10k points `list[float]` flat | 18.1 ms (p95 25.2); 17.8 ms (p95 24.3) | same |
| 10k points `bytes` in and out (Python uses `array('d')`) | 2.83 ms (p95 3.76); 2.87 ms (p95 4.06) | same |
| 100k points tuples / flat / bytes | 212.7 / 172.6 / 38.1 ms (p95 606.9 / 275.2 / 55.8) beta.350 | measured: 50 calls |

**Take for Studio:**
- CSnakes is usable under Native AOT, but only pass geometry as `bytes` (or buffers); typed lists of tuples cost 3.6x the raw C API and have bad tail latency.
- Its startup (86 ms, `asyncio`) and hosting dependency are a cost for a desktop app that may never use Python in a session; load it lazily.

### Option 4: pythonnet under Native AOT (pythonnet 3.2.1, measured 2026-11-01)

**How it works:**
- pythonnet embeds CPython in-process; its README says "You must set `Runtime.PythonDLL` property or `PYTHONNET_PYDLL` environment variable starting with version 3.0" and "Then call `PythonEngine.Initialize()`" ([pythonnet README](https://github.com/pythonnet/pythonnet)).
- Its runtime builds delegates and types at run time (stack trace: `Python.Runtime.CodeGenerator..ctor` called from `DelegateManager..ctor` in `PythonEngine.Initialize`), which is `System.Reflection.Emit`; Native AOT has "No runtime code generation, for example, System.Reflection.Emit" ([Microsoft Learn, Native AOT limitations](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).

**Good to use because:**
- In a normal JIT process it works: empty call 0.46 us, 10k tuples 15.3 ms (measured, `run_jit.txt`). Not relevant for an AOT host.

**Bad to use because:**
- Native AOT publish succeeds with 219 warnings (103 unique lines; IL2026, IL2046, IL2055, IL2060, IL2065, IL2067, IL2070, IL2072, IL2075, IL2080, IL2111, IL3000, IL3050, IL3051), then the exe aborts at start: `System.PlatformNotSupportedException: Dynamic code generation is not supported on this platform. at System.Reflection.Emit.ReflectionEmitThrower.ThrowPlatformNotSupportedException() at Python.Runtime.CodeGenerator..ctor() at Python.Runtime.DelegateManager..ctor() at Python.Runtime.PythonEngine.Initialize(...)`, exit code 134 (measured, `bench/p4_pythonnet/run_aot.txt`).
- Even under JIT: without `PythonEngine.Shutdown()` the process printed its last line and did not exit until killed by a 600 s timeout; with `Shutdown()` (411 ms) it exited (measured, `run_jit.txt`, `run_jit_shutdown.txt`). Initialize took 215 to 295 ms.

**Numbers:**

| property | value | source |
|---|---|---|
| AOT publish | 219 warnings, 0 errors, exe 5.07 MB | measured: `build_publish_aot.log`, `aot_warnings_unique.txt` |
| AOT run | crash in `PythonEngine.Initialize`, `PlatformNotSupportedException`, exit 134 | measured: `run_aot.txt` |
| JIT: Initialize / empty call / 10k tuples / 100k tuples | 215 ms / 0.46 us / 15.3 ms (p95 75.7) / 144 ms (p95 795) | measured: `run_jit.txt` (second run in `run_jit_shutdown.txt`: 295 ms / 0.78 us / 19.3 ms / 158 ms) |

**Take for Studio:**
- pythonnet cannot be used in the Native AOT app. It could only live in a JIT helper process, where a plain python3 child (option 2) is simpler.

### Option 5a: Roslyn scripting in a normal JIT process (Microsoft.CodeAnalysis.CSharp.Scripting 5.9.0, measured 2026-11-01)

**How it works:**
- `CSharpScript.Create(code, options, typeof(Globals)).CreateDelegate()` parses, compiles and loads a script assembly; the user script here is a 10-line loop over `double[] P` (`bench/common/UserScripts.cs`).
- Alternative: `CSharpCompilation.Create(...).Emit(stream)` and load the bytes into a collectible `AssemblyLoadContext`, which can be unloaded later: "You can load a set of assemblies into a collectible AssemblyLoadContext, execute methods in them ... and finally unload" ([Microsoft Learn, assembly unloadability](https://learn.microsoft.com/en-us/dotnet/standard/assembly/unloadability)).
- ReadyToRun precompiles assemblies so less JIT work happens at first use; "R2R binaries are larger" and "the size of an assembly will grow to between two to three times larger" ([Microsoft Learn, ReadyToRun](https://learn.microsoft.com/en-us/dotnet/core/deploying/ready-to-run), page dated 2021-08-23, updated 2026-07-27).

**Good to use because:**
- Once compiled, user C# runs at JIT speed: 10k points in 53 us in-process, vs 2.83 ms for the fastest pure Python round trip measured (CSnakes `bytes`), about 50x.
- Recompiles with `CSharpCompilation` + collectible ALC take 6.9 ms and do not leak.

**Bad to use because:**
- Cold first compile is 1.57 s with the NuGet DLLs (IL only), 0.65 s after ReadyToRun publish (measured, 10 runs).
- `CSharpScript` recompiles are 143 ms (p95 441) and leak: 200 more scripts added 210.9 MB of working set and 200 loaded assemblies that are never unloaded (measured).
- Roslyn needs the JIT, so it cannot run user code inside the Native AOT app (option 5b).

**Numbers:**

| property | value | source |
|---|---|---|
| process start to Main | 44 ms (p95 53) | measured: OS start time vs `DateTime.UtcNow`, 10 runs, `run_first_x10.txt` |
| first compile, IL-only DLLs | 1,567 ms (p95 1,684); first run on 10k points 7.5 ms; process wall 1,683 ms | measured: 10 process runs, `run_first_x10.txt` |
| first compile, ReadyToRun publish | 654 ms (p95 757); first run 2.9 ms; process wall 748 ms | same |
| next compiles, `CSharpScript` (30 new scripts) | 143 ms (p95 441, min 91) | measured: `run_full.txt` |
| next compiles, `CSharpCompilation.Emit` + collectible ALC (30) | 6.9 ms (p95 10.9) | same |
| run compiled script on 10k points | 53 us (p95 75) | measured: 500 runs, `run_full.txt` |
| empty script delegate call | 0.29 us (p95 0.70) | measured: 100,000 calls |
| memory after first compile | working set 134.0 MB, private 158.7 MB, managed heap 8.2 MB | measured: `Process.WorkingSet64`, `PrivateMemorySize64`, `GC.GetTotalMemory(true)` |
| memory growth, 200 more `CSharpScript` compiles | managed heap +9.9 MB, working set +210.9 MB, 262 assemblies loaded | measured: `run_full.txt` |
| memory growth, 200 Emit + collectible ALC compiles, unloaded | managed heap +0.2 MB, working set -3.4 MB | same |
| Roslyn scripting DLLs on disk (4 DLLs) | 10,354,376 B (9.9 MiB) IL only; 28,557,312 B (27.2 MiB) ReadyToRun | measured: `bench/sizes.txt` |
| satellite resource folders | 13 languages, 7.0 MiB (avoid with `SatelliteResourceLanguages=en`) | same |
| nupkg sizes | Microsoft.CodeAnalysis.Common 4.3 MiB, .CSharp 11.6 MiB, .Scripting.Common 0.5 MiB, .CSharp.Scripting 0.3 MiB | same; versions from [NuGet registration](https://api.nuget.org/v3/registration5-gz-semver2/microsoft.codeanalysis.csharp.scripting/page/4.7.0/5.9.0.json) (5.9.0 published 2026-08-17) |

**Take for Studio:**
- Use `CSharpCompilation` + collectible `AssemblyLoadContext`, not `CSharpScript`, for a C# script node that users edit many times.
- Publish the Roslyn side with ReadyToRun if first-compile latency matters (1.57 s to 0.65 s for +17 MiB).

### Option 5b: Roslyn inside the Native AOT executable (measured 2026-11-01)

**How it works:**
- Same Roslyn 5.9.0 packages, `PublishAot=true`. Each step was tried separately (`bench/p5b_roslyn_aot/Program.cs`).

**Good to use because:**
- The compiler itself runs AOT-compiled and is fast: `CSharpCompilation.Emit` succeeded, first compile 19.8 ms (1 reference) or 43 ms (167 references), next compiles 2.2 ms (p95 3.3) (measured, `run_aot.txt`). This only produces IL bytes.

**Bad to use because:**
- `CSharpScript.EvaluateAsync("1 + 2")` fails: `System.NotSupportedException: Can't create a metadata reference to an assembly without location.` because `typeof(object).Assembly.Location` is `''` in AOT (measured).
- Loading the emitted IL fails: `Assembly.Load(byte[])` throws `System.PlatformNotSupportedException: Operation is not supported on this platform.` (measured). This matches "No dynamic loading, for example, Assembly.LoadFile" ([Microsoft Learn, Native AOT limitations](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/)).
- Reference assemblies must be shipped on disk (System.Runtime.dll from the ref pack is 862,504 B).
- 30 warnings (26 from Roslyn: IL2026, IL2050, IL2072, IL2075, IL2091, IL3000), publish took 1 min 37 s, exe 36,281,552 B (34.6 MiB) vs 1.2 MiB for option 1 (measured).

**Numbers:**

| property | value | source |
|---|---|---|
| AOT publish | 30 warnings, 0 errors, 1 min 37 s, exe 36,281,552 B (34.6 MiB) | measured: `build_publish_aot.log`, `aot_warnings_unique.txt` |
| `CSharpScript.EvaluateAsync` | fails, `NotSupportedException` | measured: `run_aot.txt` |
| `CSharpCompilation.Emit` | works; first 19.8 ms, next 2.2 ms (p95 3.3), 2,048 B of IL | measured: `run_aot.txt` |
| `Assembly.Load(bytes)` | fails, `PlatformNotSupportedException` | measured: `run_aot.txt` |

**Take for Studio:**
- User C# can never execute inside the AOT process. It needs a JIT process (option 5c).

### Option 5c: Native AOT host + JIT C# helper process with Roslyn, binary pipe (measured 2026-11-01)

**How it works:**
- `bench/p5c_helper` is a framework-dependent .NET 10 console app with Microsoft.CodeAnalysis.CSharp 5.9.0. It reads frames `<u32 length><u8 op><payload>` on stdin: op 2 = compile C# source (Emit + collectible ALC + `CreateDelegate<Action<double[]>>`), op 1 = run on a float64 array, op 3 = load IL that was compiled elsewhere.
- `bench/p5c_host` is the Native AOT host (0 warnings, 2.0 MiB exe) that starts the helper and exchanges frames.
- Variant "IL compiled in the AOT host": Roslyn runs in the AOT host (option 5b), the helper only loads the 2 KB of IL (op 3). The helper binary still references Roslyn, so its assemblies are mapped for type resolution, but no Roslyn code runs in it.

**Good to use because:**
- Steady state is very cheap: 10k points round trip 0.26 ms, 100k 3.4 ms, empty 30 us, each recompile 4.7 to 6.7 ms (measured).
- The helper is isolated: an infinite loop or crash in user C# can be handled by killing the helper (design reasoning, not measured).

**Bad to use because:**
- Cold path: helper start 57 to 71 ms plus first compile 0.58 s (ReadyToRun) to 1.40 s (IL only).
- Needs a .NET runtime: a framework-dependent helper failed with "You must install .NET to run this application." when no runtime was found (measured, `run_missing_runtime.txt`). Self-contained avoids this but costs 87 to 89 MiB.
- Trimming the self-contained helper gave 24 trim warnings (IL2026, IL2050, IL2072, IL2075, IL2091; `bench/p5c_helper/build_publish_sc_trimmed.log`), and made it slower: start 111.5 ms vs 68.5 ms and first compile 1.65 s vs 1.27 s (measured). Trimming also removes framework APIs that user scripts might call (reasoning, not measured).

**Numbers:**

| property | value | source |
|---|---|---|
| helper start to first ping: framework-dependent IL / ReadyToRun / self-contained / self-contained trimmed | 71.0 / 57.0 / 68.5 / 111.5 ms (p95 89.1 / 72.6 / 76.6 / 129.2) | measured: 8 spawns each, `bench/p5c_host/run_fdd.txt`, `run_r2r.txt`, `run_sc_helper.txt`, `run_trimmed_helper.txt` |
| first compile in a fresh helper | 1,401 / 575 / 1,268 / 1,655 ms | same |
| next compiles (30 new scripts) | 6.7 / 4.7 / 6.7 / 7.7 ms | same |
| empty round trip | 30.5 us (p95 49.6) IL; 30.2 us (p95 48.4) R2R | measured: 5,000 round trips |
| 10k points round trip | 0.263 ms (p95 0.432) IL; 0.215 ms (p95 0.332) R2R; payload 160,005 B each way | measured: 300 round trips |
| 100k points round trip | 3.41 ms (p95 4.62) IL; 3.42 ms (p95 5.00) R2R | measured: 50 round trips |
| IL compiled in AOT host: helper start / load IL / first 10k run incl. JIT | 59.5 / 12.1 / 2.6 ms (framework-dependent); 41.2 / 15.4 / 2.8 ms (R2R) | measured: 8 spawns, `run_precompiled_il.txt` |

**Take for Studio:**
- This is the realistic C# script path for an AOT app: start one helper lazily, keep it alive, recompile on edit (5 to 7 ms) and send whole point lists as float64 frames.
- Compiling in the AOT host (19.8 ms cold) and shipping IL to a helper that does not run Roslyn cuts the cold path from about 1.5 s (71 + 1,401 ms) to about 80 to 95 ms (19.8 + 41 to 60 + 12 to 15 + 3 ms), at the cost of a 34.6 MiB AOT exe; worth a design spike.

### Option 6: install sizes on disk (measured 2026-11-01)

**How it works:**
- Apparent file sizes in bytes, summed with `bench/tools/sizes.py` (MiB = 1,048,576 B). Linux numbers are from this VM; Windows numbers come from cross-publishing `-r win-x64` here, from the python.org zip downloaded here, or from HTTP `Content-Length` of Microsoft download URLs listed in [.NET 10 releases.json](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json).
- The embeddable package "is a ZIP file containing a minimal Python environment. It is intended for acting as part of another application"; "Tcl/Tk (including all dependents, such as IDLE), pip and the Python documentation are not included" ([docs.python.org, Using Python on Windows, 3.15 docs](https://docs.python.org/3/using/windows.html#the-embeddable-package)).

**Numbers:**

| property | value | source |
|---|---|---|
| python.org Windows embeddable package 3.13.17 (64-bit), quoted | 10.9 MB, SHA-256 9e35319b... | [python.org 3.13.17 release page](https://www.python.org/downloads/release/python-31317/) (the page says 3.13.17 "has been superseded by Python 3.13.18") |
| same zip, measured | 11,441,267 B download (SHA-256 matched), 22,640,861 B (21.6 MiB) extracted; largest files python313.dll 6.1 MB, libcrypto-3.dll 6.0 MB, python313.zip (stdlib) 3.8 MB | measured: `curl`, `sha256sum`, `zipfile`, `bench/sizes.txt` |
| Linux libpython3.13.so.1.0 | 7,400,496 B (7.1 MiB) | measured |
| Linux stdlib `/usr/lib/python3.13`, all | 49.1 MiB (of which `__pycache__` 11.0, static lib/config 22.7, lib-dynload 3.4) | measured |
| Linux stdlib trimmed (no tests, idle, tkinter, ensurepip, pydoc_data, config, `__pycache__`) + libpython | 12.6 + 7.1 = 19.7 MiB | measured |
| numpy 2.5.3 installed (numpy + numpy.libs) | 57.1 MiB | measured |
| Roslyn DLLs as deployed: compiler only (helper, en) / scripting (4 DLLs) / scripting ReadyToRun | 9.8 MiB (whole helper folder) / 9.9 MiB / 27.2 MiB | measured |
| .NET 10.0.14 shared runtime on Linux (Microsoft.NETCore.App + host) | 82,612,136 B (78.8 MiB) | measured |
| JIT helper, framework-dependent: linux-x64 / win-x64 / win-x64 ReadyToRun | 9.8 / 9.9 / 26.4 MiB | measured: `dotnet publish -r <rid> --self-contained false` |
| JIT helper, self-contained: linux-x64 / win-x64 / linux-x64 trimmed | 88.6 / 86.6 / 33.5 MiB | measured: `--self-contained true`, `-p:PublishTrimmed=true` |
| .NET 10.0.14 runtime downloads for Windows x64: `dotnet-runtime` exe / zip, `windowsdesktop-runtime` exe / zip | 29.2 / 35.3 / 57.3 / 37.4 MiB | measured: `curl -I` Content-Length of URLs in [releases.json](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json) |
| Native AOT exes (linux-x64): raw C API / pipe host / CSnakes / pythonnet / Roslyn inside / helper host | 1.2 / 2.2 / 4.5 / 4.8 / 34.6 / 2.0 MiB | measured: `bench/sizes.txt` |

**Take for Studio:**
- Bundling Python for Windows costs about 11 MB download and 22 MB on disk (embeddable zip), before any packages; numpy alone is far bigger than the interpreter (57 MiB here, Linux).
- A C# script helper costs about 10 MiB (framework-dependent, needs the 29 to 57 MiB .NET runtime installer) or about 87 MiB self-contained.

## What I could not verify
- Windows timings: nothing was run on Windows. Process creation, pipe latency and DLL loading on Windows were not measured.
- Whether CSnakes is "Microsoft-backed": no opened page says so.
- The numpy-in-CSnakes path: not measured (system numpy not on CSnakes' `sys.path` with `FromFolder`).
- Script timeouts / killing runaway scripts: designed in reasoning only, not measured.

## How to rerun
- `source env.sh` (sets `DOTNET_ROOT` to `dotnet10/` and `NUGET_PACKAGES` to `nuget/`), then `cd bench/<project> && dotnet publish -c Release`. Build output goes to `artifacts/` (set in `bench/Directory.Build.props`); it was deleted after the runs to keep the folder small.
- Run commands used: `p1_cpython_aot [full|startup|noglobal]`; `p2_pipe <worker.py> <pylib dir> [json,bin,msgpack,binnp]`; `p3_csnakes <pyhome> [startup]` (`pyhome/` holds symlinks to the system Python in the layout CSnakes expects); `p5b_roslyn_aot <ref pack dir>`; `p5c_host <helper exe> <label> [precompiled.dll]`; process repeats with `python3 bench/tools/runmany.py K label -- cmd`; sizes with `python3 bench/tools/sizes.py <R21M dir>`.
