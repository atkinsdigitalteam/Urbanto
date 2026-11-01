using System.Buffers.Binary;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Runtime.Loader;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

// JIT helper process: compiles user C# with Roslyn and runs it on point buffers sent over stdin/stdout.
// Frame: <u32 LE length><u8 op><payload>. op 0 = ping, op 2 = compile (UTF-8 source), op 1 = run on float64 array.
var stdin = Console.OpenStandardInput();
var stdout = Console.OpenStandardOutput();
var refs = args.Length > 0 && args[0] == "noroslyn" ? Array.Empty<MetadataReference>() : ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")!).Split(Path.PathSeparator)
    .Where(p => Path.GetFileName(p) is "System.Runtime.dll" or "System.Private.CoreLib.dll" or "System.Math.dll")
    .Select(p => MetadataReference.CreateFromFile(p)).ToArray();
Action<double[]>? user = null;
AssemblyLoadContext? alc = null;
byte[] buf = new byte[1 << 20];
byte[] hdr = new byte[4];
double[] pts = Array.Empty<double>();
while (true)
{
    if (!ReadExactly(stdin, hdr, 4)) break;
    int len = (int)BinaryPrimitives.ReadUInt32LittleEndian(hdr);
    if (buf.Length < len) buf = new byte[len];
    if (!ReadExactly(stdin, buf, len)) break;
    byte op = buf[0];
    if (op == 0) { Reply(stdout, [0]); continue; }
    if (op == 2)
    {
        long t = Stopwatch.GetTimestamp();
        string code = System.Text.Encoding.UTF8.GetString(buf, 1, len - 1);
        var comp = CSharpCompilation.Create("u" + Guid.NewGuid().ToString("N"), [CSharpSyntaxTree.ParseText(code)], refs,
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, optimizationLevel: OptimizationLevel.Release));
        using var ms = new MemoryStream();
        var res = comp.Emit(ms);
        byte ok = 0;
        if (res.Success)
        {
            ms.Position = 0;
            alc?.Unload();
            alc = new AssemblyLoadContext(null, isCollectible: true);
            user = alc.LoadFromStream(ms).GetType("UserScript")!.GetMethod("Run")!.CreateDelegate<Action<double[]>>();
            ok = 1;
        }
        uint us = (uint)((Stopwatch.GetTimestamp() - t) * 1_000_000 / Stopwatch.Frequency);
        byte[] r = new byte[6]; r[0] = 2; r[1] = ok; BinaryPrimitives.WriteUInt32LittleEndian(r.AsSpan(2), us);
        Reply(stdout, r);
        continue;
    }
    if (op == 3)
    {
        // load an assembly that was compiled elsewhere (for example by Roslyn inside the AOT host): no Roslyn needed here
        long t = Stopwatch.GetTimestamp();
        alc?.Unload();
        alc = new AssemblyLoadContext(null, isCollectible: true);
        user = alc.LoadFromStream(new MemoryStream(buf, 1, len - 1)).GetType("UserScript")!.GetMethod("Run")!.CreateDelegate<Action<double[]>>();
        uint us = (uint)((Stopwatch.GetTimestamp() - t) * 1_000_000 / Stopwatch.Frequency);
        byte[] r = new byte[6]; r[0] = 3; r[1] = 1; BinaryPrimitives.WriteUInt32LittleEndian(r.AsSpan(2), us);
        Reply(stdout, r);
        continue;
    }
    // op 1: run user code in place on the float64 array, send it back
    int n = (len - 1) / 8;
    if (pts.Length != n) pts = new double[n];
    MemoryMarshal.Cast<byte, double>(buf.AsSpan(1, len - 1)).CopyTo(pts);
    user!(pts);
    MemoryMarshal.AsBytes(pts.AsSpan()).CopyTo(buf.AsSpan(1));
    Reply(stdout, buf.AsSpan(0, len));
}

static bool ReadExactly(Stream s, byte[] b, int n)
{
    int o = 0;
    while (o < n) { int k = s.Read(b, o, n - o); if (k == 0) return false; o += k; }
    return true;
}
static void Reply(Stream s, ReadOnlySpan<byte> body)
{
    Span<byte> h = stackalloc byte[4];
    BinaryPrimitives.WriteUInt32LittleEndian(h, (uint)body.Length);
    s.Write(h); s.Write(body); s.Flush();
}
