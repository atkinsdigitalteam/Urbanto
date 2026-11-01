using System.Buffers.Binary;
using System.Diagnostics;
using System.Runtime.InteropServices;

// Benchmark 5c: Native AOT host <-> JIT C# helper (Roslyn) over stdin/stdout pipes. args: <helper executable> <label>
string helper = args[0], label = args.Length > 1 ? args[1] : "helper";
if (args.Length > 2)
{
    // mode: helper only loads IL compiled by Roslyn inside the AOT host (file given as args[2]); Roslyn is never loaded in the helper
    byte[] il = File.ReadAllBytes(args[2]);
    double[] src0 = Pts.Make(10_000), dst0 = new double[src0.Length];
    var st = new double[8]; var ld = new double[8]; var fr = new double[8]; var ldIn = new double[8];
    for (int i = 0; i < st.Length + 1; i++)
    {
        long a = Stopwatch.GetTimestamp();
        using var h = Helper.Start(helper, "noroslyn");
        h.Ping();
        long b = Stopwatch.GetTimestamp();
        uint inside = h.LoadIl(il);
        long c = Stopwatch.GetTimestamp();
        h.Run(src0, dst0);
        long d = Stopwatch.GetTimestamp();
        h.Close();
        if (i == 0) continue;
        st[i - 1] = Stat.Us(b - a); ld[i - 1] = Stat.Us(c - b); ldIn[i - 1] = inside; fr[i - 1] = Stat.Us(d - c);
    }
    Stat.Print($"p5c [{label}] helper start to first ping", st, "");
    Stat.Print($"p5c [{label}] load precompiled IL in fresh helper (round trip)", ld, $"{il.Length} B of IL");
    Stat.Print($"p5c [{label}] first 10000-point run in fresh helper (includes JIT of user code)", fr, "");
    Stat.Line($"p5c [{label}] max abs error", $"{Pts.MaxErr(dst0, Pts.Reference(src0)):E2}");
    return;
}

// cold starts: process start -> first ping reply, then first compile (cold Roslyn in a fresh process)
var startT = new double[8]; var firstCompile = new double[8]; var firstCompileInside = new double[8];
for (int i = 0; i < startT.Length + 1; i++)
{
    long a = Stopwatch.GetTimestamp();
    using var h = Helper.Start(helper);
    h.Ping();
    long b = Stopwatch.GetTimestamp();
    uint inside = h.Compile(UserScripts.AsClass(i));
    long c = Stopwatch.GetTimestamp();
    h.Close();
    if (i == 0) continue;     // first spawn is a cache warm-up
    startT[i - 1] = Stat.Us(b - a); firstCompile[i - 1] = Stat.Us(c - b); firstCompileInside[i - 1] = inside;
}
Stat.Print($"p5c [{label}] helper process start to first ping reply", startT, "");
Stat.Print($"p5c [{label}] first compile in a fresh helper (round trip)", firstCompile, "small user script");
Stat.Print($"p5c [{label}] first compile in a fresh helper (inside helper)", firstCompileInside, "");

using var w = Helper.Start(helper);
w.Ping(); w.Compile(UserScripts.AsClass(0));
var next = new double[30];
for (int i = 0; i < next.Length; i++) { long a = Stopwatch.GetTimestamp(); w.Compile(UserScripts.AsClass(100 + i)); next[i] = Stat.Us(Stopwatch.GetTimestamp() - a); }
Stat.Print($"p5c [{label}] next compiles (each a new script, collectible ALC)", next, "");
Stat.Run($"p5c [{label}] empty round trip", 500, 5000, () => w.Ping(), "payload=5 B each way");
foreach (int n in new[] { 10_000, 100_000 })
{
    double[] src = Pts.Make(n), expect = Pts.Reference(src), dst = new double[src.Length];
    w.Run(src, dst);
    Stat.Run($"p5c [{label}] {n} points round trip", n == 10_000 ? 20 : 5, n == 10_000 ? 300 : 50, () => w.Run(src, dst), $"payload={1 + n * 16 + 4} B each way");
    Stat.Line($"p5c [{label}] {n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
}

sealed class Helper : IDisposable
{
    readonly Process p; readonly Stream inS, outS; byte[] rbuf = new byte[1 << 20]; byte[] wbuf = new byte[1 << 20];
    Helper(Process p) { this.p = p; inS = p.StandardInput.BaseStream; outS = p.StandardOutput.BaseStream; }
    public static Helper Start(string exe, string? arg = null)
    {
        var psi = new ProcessStartInfo(exe) { RedirectStandardInput = true, RedirectStandardOutput = true, UseShellExecute = false };
        if (arg != null) psi.ArgumentList.Add(arg);
        return new Helper(Process.Start(psi)!);
    }
    void Send(ReadOnlySpan<byte> body)
    {
        Span<byte> h = stackalloc byte[4];
        BinaryPrimitives.WriteUInt32LittleEndian(h, (uint)body.Length);
        inS.Write(h); inS.Write(body); inS.Flush();
    }
    ReadOnlySpan<byte> Receive()
    {
        Span<byte> h = stackalloc byte[4];
        outS.ReadExactly(h);
        int len = (int)BinaryPrimitives.ReadUInt32LittleEndian(h);
        if (rbuf.Length < len) rbuf = new byte[len];
        outS.ReadExactly(rbuf, 0, len);
        return rbuf.AsSpan(0, len);
    }
    public void Ping() { Send([0]); Receive(); }
    public uint Compile(string code)
    {
        var bytes = System.Text.Encoding.UTF8.GetBytes(code);
        var body = new byte[1 + bytes.Length]; body[0] = 2; bytes.CopyTo(body, 1);
        Send(body);
        var r = Receive();
        if (r[1] != 1) throw new Exception("compile failed");
        return BinaryPrimitives.ReadUInt32LittleEndian(r.Slice(2));
    }
    public uint LoadIl(byte[] il)
    {
        var body = new byte[1 + il.Length]; body[0] = 3; il.CopyTo(body, 1);
        Send(body);
        var r = Receive();
        return BinaryPrimitives.ReadUInt32LittleEndian(r.Slice(2));
    }
    public void Run(double[] src, double[] dst)
    {
        int len = 1 + src.Length * 8;
        if (wbuf.Length < len) wbuf = new byte[len];
        wbuf[0] = 1;
        MemoryMarshal.AsBytes(src.AsSpan()).CopyTo(wbuf.AsSpan(1));
        Send(wbuf.AsSpan(0, len));
        var r = Receive();
        MemoryMarshal.Cast<byte, double>(r.Slice(1)).CopyTo(dst);
    }
    public void Close() { try { inS.Close(); p.WaitForExit(5000); } catch { } }
    public void Dispose() { Close(); p.Dispose(); }
}
