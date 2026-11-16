using System;
using System.Linq;

static class DevFinance
{
    // ARGUS-style single-account finance. net[t]: receipts minus costs in month t.
    // Interest for month t = interest-bearing balance b/f * annual nominal rate / 12.
    // Accrued interest joins the interest-bearing balance every k months.
    public static (double[] Interest, double[] Cumulative) Run(
        double[] net, double debit, double credit, int k = 1)
    {
        int n = net.Length;
        var interest = new double[n];
        var cum = new double[n];
        double ib = 0, accrued = 0, prev = 0;
        for (int t = 0; t < n; t++)
        {
            if (t > 0)
            {
                double i = ib * (ib < 0 ? debit : credit) / 12.0; // negative when in debt
                interest[t] = -i;
                accrued += i;
            }
            cum[t] = prev + net[t] - interest[t];
            prev = cum[t];
            ib += net[t];
            if ((t + 1) % k == 0) { ib += accrued; accrued = 0; }
        }
        return (interest, cum);
    }
}

class Program
{
    static void Main()
    {
        double[] costs = { 1_750_298, 0, 0, 0, 10_442, 36_068, 462_806, 391_144, 558_966 };
        double[] printed = { 0, 9_481, 9_481, 9_583, 9_583, 9_640, 9_991, 12_498, 14_617 };
        foreach (int k in new[] { 1, 3 })
        {
            var (i, c) = DevFinance.Run(costs.Select(x => -x).ToArray(), 0.065, 0.001, k);
            double maxDiff = i.Zip(printed, (a, b) => Math.Abs(Math.Round(a) - b)).Max();
            Console.WriteLine($"k={k}: interest = {string.Join(" ", i.Select(x => x.ToString("N0")))}; max |diff| vs ARGUS = {maxDiff}");
        }
    }
}
