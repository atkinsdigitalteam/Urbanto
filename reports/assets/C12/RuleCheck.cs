using System;
using System.IO;
using System.Linq;
using System.Text.Json;

// Load a parking rule pack (dubai-dbc-2021-parking-rules.json) and derive
// row depth, pitch, module width and module-only m2 per stall per row type.
var json = File.ReadAllText(args.Length > 0 ? args[0] : "dubai-dbc-2021-parking-rules.json");
var pack = JsonSerializer.Deserialize<RulePack>(json, new JsonSerializerOptions { PropertyNameCaseInsensitive = true })!;
Console.WriteLine($"{pack.Id}: {pack.Rows.Length} row types");
foreach (var r in pack.Rows)
{
    var g = RowGeometry.From(r);
    Console.WriteLine($"{r.AngleDeg,3} deg {r.Flow,-8} depth {g.Depth,5:F2} m  pitch {g.Pitch,5:F2} m  " +
                      $"module {g.Module,5:F2} m  {g.Module * g.Pitch / 2,5:F2} m2/stall");
}
Console.WriteLine($"DBC accessible bays for 344 stalls: {Accessible.Dbc(344)}");

public sealed record RowRule(double AngleDeg, string Flow, double BayWidth, double BayLength, double Aisle, string Clause);
public sealed record RulePack(string Id, string Title, RowRule[] Rows);

public readonly record struct RowGeometry(double Depth, double Pitch, double Module)
{
    // Rectangle bay with one corner on the aisle edge (DBC Figures B.60 to B.63).
    public static RowGeometry From(RowRule r)
    {
        if (r.AngleDeg == 0)   // parallel: long side along the aisle
            return new(r.BayWidth, r.BayLength, 2 * r.BayWidth + r.Aisle);
        double a = r.AngleDeg * Math.PI / 180.0;
        double depth = r.BayLength * Math.Sin(a) + r.BayWidth * Math.Cos(a);
        double pitch = r.BayWidth / Math.Sin(a);
        return new(depth, pitch, 2 * depth + r.Aisle);
    }
}

public static class Accessible
{
    // DBC Table C.17, all buildings except private housing.
    public static int? Dbc(int total) => total switch
    {
        < 25 => null,
        <= 500 => Math.Max(1, (int)Math.Ceiling(0.02 * total)),
        _ => 10 + (int)Math.Ceiling(0.01 * (total - 500)),
    };
}
