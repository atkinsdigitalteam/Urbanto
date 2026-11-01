using System.Buffers;
using System.Buffers.Binary;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.Json;

// Benchmark 2: Native AOT host <-> separate python3 child over stdin/stdout pipes.
// args: <path to worker.py> <pylib dir for msgpack> [python exe]
string worker = args[0], pylib = args[1], python = "python3";
string[] modes = args.Length > 2 ? args[2].Split(',') : new[] { "json", "bin", "msgpack", "binnp" };

foreach (var mode in modes)
{
    // ---- process start: Process.Start until the first empty request is answered
    var starts = new double[20];
    for (int i = 0; i < starts.Length + 1; i++)
    {
        long a = Stopwatch.GetTimestamp();
        using var w = Worker.Start(python, worker, mode, pylib);
        w.Noop();
        double us = Stat.Us(Stopwatch.GetTimestamp() - a);
        w.Close();
        if (i > 0) starts[i - 1] = us;   // drop the very first (cold cache)
    }
    Stat.Print($"p2 [{mode}] process start to first reply", starts, "python3 -I worker.py");

    using var wk = Worker.Start(python, worker, mode, pylib);
    wk.Noop();
    Stat.Run($"p2 [{mode}] empty round trip", 500, 5000, () => wk.Noop(), $"payload={wk.LastReqBytes} B out, {wk.LastRespBytes} B back");
    foreach (int n in new[] { 10_000, 100_000 })
    {
        double[] src = Pts.Make(n), expect = Pts.Reference(src), dst = new double[src.Length];
        int iters = n == 10_000 ? 300 : 50, warm = n == 10_000 ? 20 : 5;
        wk.Transform(src, dst);
        Stat.Run($"p2 [{mode}] {n} points round trip", warm, iters, () => wk.Transform(src, dst),
            $"payload={wk.LastReqBytes} B out, {wk.LastRespBytes} B back");
        Stat.Line($"p2 [{mode}] {n} max abs error vs C#", $"{Pts.MaxErr(dst, expect):E2}");
        // host side encode/decode cost alone (no pipe, no Python)
        Stat.Run($"p2 [{mode}] {n} host-side encode only", 5, 50, () => wk.EncodeOnly(src), "");
    }
    wk.Close();
}

sealed class Worker : IDisposable
{
    readonly Process p; readonly Stream inS, outS; readonly string mode;
    readonly ArrayBufferWriter<byte> buf = new(1 << 20);
    byte[] rbuf = new byte[1 << 20];
    public int LastReqBytes, LastRespBytes;

    Worker(Process p, string mode) { this.p = p; this.mode = mode; inS = p.StandardInput.BaseStream; outS = p.StandardOutput.BaseStream; }

    public static Worker Start(string python, string script, string mode, string pylib)
    {
        var psi = new ProcessStartInfo(python) { RedirectStandardInput = true, RedirectStandardOutput = true, UseShellExecute = false };
        psi.ArgumentList.Add("-I"); psi.ArgumentList.Add(script); psi.ArgumentList.Add(mode); psi.ArgumentList.Add(pylib);
        return new Worker(Process.Start(psi)!, mode);
    }

    public void Noop()
    {
        buf.ResetWrittenCount();
        if (mode == "json") { "{\"op\":\"noop\"}\n"u8.CopyTo(buf.GetSpan(16)); buf.Advance(14); }
        else if (mode == "msgpack") { MsgPack.WriteNoop(buf); }
        else { buf.GetSpan(1)[0] = 0; buf.Advance(1); }
        Send(); var resp = Receive();
        if (resp.Length == 0) throw new Exception("no reply");
    }

    public void EncodeOnly(double[] src) { buf.ResetWrittenCount(); Encode(src); }

    void Encode(double[] src)
    {
        if (mode == "json")
        {
            using (var jw = new Utf8JsonWriter(buf))
            {
                jw.WriteStartObject(); jw.WriteString("op", "t"); jw.WriteStartArray("pts");
                foreach (var d in src) jw.WriteNumberValue(d);
                jw.WriteEndArray(); jw.WriteEndObject();
            }
            buf.GetSpan(1)[0] = (byte)'\n'; buf.Advance(1);
        }
        else if (mode == "msgpack") MsgPack.WritePoints(buf, src);
        else
        {
            var span = buf.GetSpan(1 + src.Length * 8);
            span[0] = 1;
            MemoryMarshal.AsBytes(src.AsSpan()).CopyTo(span.Slice(1));   // little-endian on x64 and arm64
            buf.Advance(1 + src.Length * 8);
        }
    }

    public void Transform(double[] src, double[] dst)
    {
        buf.ResetWrittenCount();
        Encode(src);
        Send();
        var r = Receive();
        if (mode == "json")
        {
            var rd = new Utf8JsonReader(r);
            int i = 0;
            while (rd.Read()) if (rd.TokenType == JsonTokenType.Number) dst[i++] = rd.GetDouble();
            if (i != dst.Length) throw new Exception("bad count " + i);
        }
        else if (mode == "msgpack") MsgPack.ReadPoints(r, dst);
        else MemoryMarshal.Cast<byte, double>(r.Slice(1)).CopyTo(dst);
    }

    void Send()
    {
        var data = buf.WrittenSpan;
        LastReqBytes = data.Length;
        if (mode != "json")
        {
            Span<byte> h = stackalloc byte[4];
            BinaryPrimitives.WriteUInt32LittleEndian(h, (uint)data.Length);
            inS.Write(h); LastReqBytes += 4;
        }
        inS.Write(data);
        inS.Flush();
    }

    ReadOnlySpan<byte> Receive()
    {
        if (mode == "json")
        {
            int n = 0;
            while (true)
            {
                if (n == rbuf.Length) Array.Resize(ref rbuf, rbuf.Length * 2);
                int k = outS.Read(rbuf, n, rbuf.Length - n);
                if (k == 0) throw new EndOfStreamException();
                n += k;
                if (rbuf[n - 1] == (byte)'\n') break;
            }
            LastRespBytes = n;
            return rbuf.AsSpan(0, n - 1);
        }
        Span<byte> h = stackalloc byte[4];
        outS.ReadExactly(h);
        int len = (int)BinaryPrimitives.ReadUInt32LittleEndian(h);
        if (rbuf.Length < len) rbuf = new byte[len];
        outS.ReadExactly(rbuf, 0, len);
        LastRespBytes = len + 4;
        return rbuf.AsSpan(0, len);
    }

    public void Close() { try { inS.Close(); p.WaitForExit(5000); } catch { } }
    public void Dispose() { Close(); p.Dispose(); }
}

// Hand-written MessagePack subset (map with "op" and "pts": array of float64), no reflection, AOT safe.
static class MsgPack
{
    public static void WriteNoop(ArrayBufferWriter<byte> w)
    {
        var s = w.GetSpan(16);
        s[0] = 0x81; s[1] = 0xA2; s[2] = (byte)'o'; s[3] = (byte)'p'; s[4] = 0xA4; "noop"u8.CopyTo(s.Slice(5));
        w.Advance(9);
    }
    public static void WritePoints(ArrayBufferWriter<byte> w, double[] src)
    {
        var s = w.GetSpan(32 + src.Length * 9);
        int o = 0;
        s[o++] = 0x82;
        s[o++] = 0xA2; s[o++] = (byte)'o'; s[o++] = (byte)'p'; s[o++] = 0xA1; s[o++] = (byte)'t';
        s[o++] = 0xA3; s[o++] = (byte)'p'; s[o++] = (byte)'t'; s[o++] = (byte)'s';
        s[o++] = 0xDD; BinaryPrimitives.WriteUInt32BigEndian(s.Slice(o), (uint)src.Length); o += 4;
        foreach (var d in src) { s[o++] = 0xCB; BinaryPrimitives.WriteDoubleBigEndian(s.Slice(o), d); o += 8; }
        w.Advance(o);
    }
    public static void ReadPoints(ReadOnlySpan<byte> r, double[] dst)
    {
        // expects {"pts": [float64...]} as written by msgpack-python
        int o = 0;
        if (r[o++] != 0x81) throw new Exception("map");
        int kl = r[o++] & 0x1F; o += kl;
        int count;
        if (r[o] == 0xDD) { count = (int)BinaryPrimitives.ReadUInt32BigEndian(r.Slice(o + 1)); o += 5; }
        else if (r[o] == 0xDC) { count = BinaryPrimitives.ReadUInt16BigEndian(r.Slice(o + 1)); o += 3; }
        else throw new Exception("array");
        if (count != dst.Length) throw new Exception("count");
        for (int i = 0; i < count; i++)
        {
            if (r[o] != 0xCB) throw new Exception("float64 expected");
            dst[i] = BinaryPrimitives.ReadDoubleBigEndian(r.Slice(o + 1)); o += 9;
        }
    }
}
