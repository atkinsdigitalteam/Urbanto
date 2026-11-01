using System.Diagnostics;
using System.Reflection;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Scripting;
using Microsoft.CodeAnalysis.Scripting;

// Benchmark 5b: try Roslyn inside a Native AOT executable. Each step is tried separately and its outcome printed.
Step("1 CSharpScript.EvaluateAsync(\"1 + 2\")", () =>
{
    var r = CSharpScript.EvaluateAsync<int>("1 + 2").GetAwaiter().GetResult();
    return "result " + r;
});
Step("2 typeof(object).Assembly.Location (needed for MetadataReference.CreateFromFile)", () =>
    "'" + typeof(object).Assembly.Location + "'");
Step("3 CSharpCompilation.Emit with references from the reference pack on disk", () =>
{
    // In AOT there are no framework assemblies on disk next to the app; point at the SDK's reference pack instead.
    string refDir = args.Length > 0 ? args[0] : "";
    var refs = Directory.GetFiles(refDir, "*.dll").Select(p => MetadataReference.CreateFromFile(p)).ToArray();
    long t = Stopwatch.GetTimestamp();
    var comp = CSharpCompilation.Create("u1", new[] { CSharpSyntaxTree.ParseText(UserScripts.AsClass(1)) }, refs,
        new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
    var ms = new MemoryStream();
    var res = comp.Emit(ms);
    string s = $"success={res.Success}, {ms.Length} bytes IL, {Stat.Us(Stopwatch.GetTimestamp() - t) / 1000:F0} ms, refs={refs.Length}";
    File.WriteAllBytes(Path.Combine(AppContext.BaseDirectory, "u1.dll"), ms.ToArray());
    return s;
});
Step("4 Assembly.Load(bytes) of the emitted user assembly", () =>
{
    var asm = Assembly.Load(File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory, "u1.dll")));
    return "loaded " + asm.FullName;
});

Step("5 compile timings inside AOT (refs: System.Runtime.dll from the reference pack only)", () =>
{
    string refDir = args.Length > 0 ? args[0] : "";
    var refs = new[] { MetadataReference.CreateFromFile(Path.Combine(refDir, "System.Runtime.dll")) };
    double Compile(int v)
    {
        long t = Stopwatch.GetTimestamp();
        var comp = CSharpCompilation.Create("u" + v, new[] { CSharpSyntaxTree.ParseText(UserScripts.AsClass(v)) }, refs,
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, optimizationLevel: OptimizationLevel.Release));
        var ms = new MemoryStream();
        var res = comp.Emit(ms);
        if (!res.Success) throw new Exception(string.Join("; ", res.Diagnostics));
        if (v == 7) File.WriteAllBytes(Path.Combine(AppContext.BaseDirectory, "u7.dll"), ms.ToArray());
        return Stat.Us(Stopwatch.GetTimestamp() - t);
    }
    double first = Compile(7);
    var next = Enumerable.Range(8, 30).Select(Compile).ToArray();
    Stat.Print("p5b AOT Roslyn next compiles (30 new scripts)", next, "");
    return $"first compile {first / 1000:F1} ms";
});

static void Step(string name, Func<string> f)
{
    try { Console.WriteLine($"RESULT | p5b step {name} | OK: {f()}"); }
    catch (Exception e)
    {
        var inner = e; while (inner.InnerException != null) inner = inner.InnerException;
        Console.WriteLine($"RESULT | p5b step {name} | FAILED: {e.GetType().FullName}: {e.Message.Split('\n')[0]} | innermost: {inner.GetType().FullName}: {inner.Message.Split('\n')[0]}");
        Console.WriteLine("    at " + string.Join("\n    at ", (inner.StackTrace ?? "").Split('\n').Take(6).Select(l => l.Trim())));
    }
}
