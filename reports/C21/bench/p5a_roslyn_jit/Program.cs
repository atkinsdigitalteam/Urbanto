using System.Diagnostics;
using System.Reflection;
using System.Runtime.Loader;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Scripting;
using Microsoft.CodeAnalysis.Scripting;

// Benchmark 5a: Roslyn in a normal JIT process. Modes: full (default), first (one compile, then exit), leak.
string mode = args.Length > 0 ? args[0] : "full";
long procStart = Process.GetCurrentProcess().StartTime.ToUniversalTime().Ticks;
double msToMain = (DateTime.UtcNow.Ticks - procStart) / 10_000.0;
var opts = ScriptOptions.Default.WithOptimizationLevel(OptimizationLevel.Release);
double[] src = Pts.Make(10_000), expect = Pts.Reference(src);

long a = Stopwatch.GetTimestamp();
var script = CSharpScript.Create(UserScripts.Body(0), opts, typeof(ScriptGlobals));
var runner = script.CreateDelegate();           // forces compile + load
long b = Stopwatch.GetTimestamp();
var g = new ScriptGlobals { P = (double[])src.Clone() };
runner(g).GetAwaiter().GetResult();
long c = Stopwatch.GetTimestamp();
Stat.Line("p5a process start to Main (approx, from OS start time)", $"{msToMain * 1000:F0} us");
Stat.Line("p5a CSharpScript first compile (Create + CreateDelegate)", $"{Stat.Us(b - a):F0} us");
Stat.Line("p5a CSharpScript first run on 10000 points", $"{Stat.Us(c - b):F0} us");
Stat.Line("p5a first script result max abs error", $"{Pts.MaxErr(g.P, expect):E2}");
GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
var pr = Process.GetCurrentProcess(); pr.Refresh();
Stat.Line("p5a memory after first compile", $"working set {pr.WorkingSet64 / 1048576.0:F1} MB, private {pr.PrivateMemorySize64 / 1048576.0:F1} MB, managed heap {GC.GetTotalMemory(true) / 1048576.0:F1} MB");
if (mode == "first") return;

// next compiles: each is a different script text (no cache hit)
var times = new double[30];
for (int i = 0; i < times.Length; i++)
{
    long t = Stopwatch.GetTimestamp();
    var r = CSharpScript.Create(UserScripts.Body(i + 1), opts, typeof(ScriptGlobals)).CreateDelegate();
    times[i] = Stat.Us(Stopwatch.GetTimestamp() - t);
}
Stat.Print("p5a CSharpScript next compiles (2nd to 31st, each a new script)", times, "small script, 10 lines");

// running an already compiled script delegate
var g2 = new ScriptGlobals { P = (double[])src.Clone() };
Stat.Run("p5a run compiled script delegate on 10000 points", 20, 500, () => { Array.Copy(src, g2.P, src.Length); runner(g2).GetAwaiter().GetResult(); }, "in-process, no marshalling");
Stat.Run("p5a empty call of compiled script delegate (empty script)", 1000, 100_000, MakeEmpty(opts), "");

// CSharpCompilation + Emit + collectible AssemblyLoadContext (what a helper would use; unloadable)
var refs = ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")!).Split(Path.PathSeparator)
    .Where(p => Path.GetFileName(p) is "System.Runtime.dll" or "System.Private.CoreLib.dll" or "System.Math.dll")
    .Select(p => MetadataReference.CreateFromFile(p)).ToArray();
var ctimes = new double[30];
for (int i = 0; i < ctimes.Length; i++)
{
    long t = Stopwatch.GetTimestamp();
    var run = CompileAndLoad(UserScripts.AsClass(100 + i), refs, out var alc);
    ctimes[i] = Stat.Us(Stopwatch.GetTimestamp() - t);
    alc.Unload();
}
Stat.Print("p5a CSharpCompilation.Emit + collectible ALC load (warm, 30 compiles)", ctimes, "");

// memory growth: 200 more CSharpScript compiles (script assemblies are not collectible) vs 200 collectible ALC compiles
long before = GC.GetTotalMemory(true); pr.Refresh(); long wsBefore = pr.WorkingSet64;
for (int i = 0; i < 200; i++) CSharpScript.Create(UserScripts.Body(1000 + i), opts, typeof(ScriptGlobals)).CreateDelegate();
GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
long after = GC.GetTotalMemory(true); pr.Refresh();
Stat.Line("p5a memory growth after 200 CSharpScript compiles", $"managed heap +{(after - before) / 1048576.0:F1} MB, working set +{(pr.WorkingSet64 - wsBefore) / 1048576.0:F1} MB, loaded assemblies now {AppDomain.CurrentDomain.GetAssemblies().Length}");
before = GC.GetTotalMemory(true); pr.Refresh(); wsBefore = pr.WorkingSet64;
for (int i = 0; i < 200; i++) { CompileAndLoad(UserScripts.AsClass(5000 + i), refs, out var alc)(new double[2]); alc.Unload(); }
for (int k = 0; k < 5; k++) { GC.Collect(); GC.WaitForPendingFinalizers(); }
after = GC.GetTotalMemory(true); pr.Refresh();
Stat.Line("p5a memory growth after 200 Emit + collectible ALC compiles (unloaded)", $"managed heap +{(after - before) / 1048576.0:F1} MB, working set +{(pr.WorkingSet64 - wsBefore) / 1048576.0:F1} MB, loaded assemblies now {AppDomain.CurrentDomain.GetAssemblies().Length}");

static Action<double[]> CompileAndLoad(string code, MetadataReference[] refs, out AssemblyLoadContext alc)
{
    var comp = CSharpCompilation.Create("u" + Guid.NewGuid().ToString("N"), new[] { CSharpSyntaxTree.ParseText(code) }, refs,
        new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, optimizationLevel: OptimizationLevel.Release));
    using var ms = new MemoryStream();
    var res = comp.Emit(ms);
    if (!res.Success) throw new Exception(string.Join("\n", res.Diagnostics));
    ms.Position = 0;
    alc = new AssemblyLoadContext(null, isCollectible: true);
    var asm = alc.LoadFromStream(ms);
    return asm.GetType("UserScript")!.GetMethod("Run")!.CreateDelegate<Action<double[]>>();
}

static Action MakeEmpty(ScriptOptions opts)
{
    var d = CSharpScript.Create("", opts, typeof(ScriptGlobals)).CreateDelegate();
    var gl = new ScriptGlobals();
    return () => d(gl).GetAwaiter().GetResult();
}
