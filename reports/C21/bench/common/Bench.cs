using System.Diagnostics;

// Shared helpers: point generation, reference transform, timing statistics.
public static class Pts
{
    // Affine transform used by every option: rotate 30 degrees, then translate (10, -3).
    public const double C = 0.8660254037844387, S = 0.5, TX = 10.0, TY = -3.0;

    public static double[] Make(int n)
    {
        var a = new double[n * 2];
        var r = new Random(42);
        for (int i = 0; i < a.Length; i++) a[i] = r.NextDouble() * 1000.0 - 500.0;
        return a;
    }

    public static double[] Reference(double[] src)
    {
        var d = new double[src.Length];
        for (int i = 0; i < src.Length; i += 2)
        {
            double x = src[i], y = src[i + 1];
            d[i] = C * x - S * y + TX;
            d[i + 1] = S * x + C * y + TY;
        }
        return d;
    }

    public static double MaxErr(double[] a, double[] b)
    {
        if (a.Length != b.Length) return double.PositiveInfinity;
        double m = 0;
        for (int i = 0; i < a.Length; i++) m = Math.Max(m, Math.Abs(a[i] - b[i]));
        return m;
    }
}

public static class Stat
{
    public static double Us(long ticks) => ticks * 1_000_000.0 / Stopwatch.Frequency;

    // Runs warmup + iters calls of f, timing each one, and prints one summary line.
    public static double[] Run(string label, int warmup, int iters, Action f, string payload = "")
    {
        for (int i = 0; i < warmup; i++) f();
        var t = new double[iters];
        for (int i = 0; i < iters; i++)
        {
            long a = Stopwatch.GetTimestamp();
            f();
            t[i] = Us(Stopwatch.GetTimestamp() - a);
        }
        Print(label, t, payload);
        return t;
    }

    public static void Print(string label, double[] us, string payload = "")
    {
        var s = (double[])us.Clone();
        Array.Sort(s);
        double P(double q) => s[Math.Min(s.Length - 1, (int)Math.Ceiling(q * s.Length) - 1)];
        Console.WriteLine($"RESULT | {label} | n={s.Length} | p50_us={P(0.50):F2} | p95_us={P(0.95):F2} | min_us={s[0]:F2} | mean_us={s.Average():F2} | {payload}");
    }

    public static void Line(string label, string value) => Console.WriteLine($"RESULT | {label} | {value}");
}
