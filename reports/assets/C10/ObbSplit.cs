// C10 sample: OBB recursive parcel split (Vanegas et al. 2012, Algorithm 2; CityEngine "Recursive")
// in C# with NetTopologySuite 2.6.0. Deterministic (irregularity = 0, forceStreetAccess = 1).
// Build: dotnet new console; dotnet add package NetTopologySuite --version 2.6.0; replace Program.cs.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using NetTopologySuite.Algorithm;
using NetTopologySuite.Geometries;
using NetTopologySuite.Operation.Polygonize;

public static class ObbSplit
{
    static readonly GeometryFactory F = new GeometryFactory();

    public sealed record Options(double AreaMax = 900, double WidthMin = 15, double AccessMin = 1.0);

    public static List<Polygon> Subdivide(Polygon block, Options o)
    {
        var ringBuf = block.ExteriorRing.Buffer(0.01);
        double Frontage(Polygon p) => p.ExteriorRing.Intersection(ringBuf).Length;
        var output = new List<Polygon>();
        var stack = new Stack<Polygon>();
        stack.Push(block);
        while (stack.Count > 0)
        {
            var poly = stack.Pop();
            if (poly.Area <= o.AreaMax) { output.Add(poly); continue; }
            var first = TrySplit(poly, alongLong: false, o);
            var chosen = first;
            if (first != null && first.Any(q => Frontage(q) < o.AccessMin))
                chosen = TrySplit(poly, alongLong: true, o) ?? first;   // rotate 90 degrees (xi = 1)
            chosen ??= TrySplit(poly, alongLong: true, o);
            if (chosen == null) { output.Add(poly); continue; }      // lotWidthMin blocks every split
            foreach (var q in chosen) stack.Push(q);
        }
        return output;
    }

    static List<Polygon>? TrySplit(Polygon poly, bool alongLong, Options o)
    {
        var (cx, cy, ux, uy, len, wid) = Obb(poly);
        // default: cut perpendicular to the long axis through the OBB centre
        double dx = alongLong ? ux : -uy, dy = alongLong ? uy : ux;
        double big = 4 * (len + wid);
        var cut = F.CreateLineString(new[] {
            new Coordinate(cx - dx * big, cy - dy * big), new Coordinate(cx + dx * big, cy + dy * big) });
        var pieces = Split(poly, cut);
        if (pieces.Count < 2) return null;
        if (pieces.Any(p => Obb(p).wid < o.WidthMin)) return null;   // CityEngine lotWidthMin rule
        return pieces;
    }

    static (double cx, double cy, double ux, double uy, double len, double wid) Obb(Geometry g)
    {
        var r = MinimumAreaRectangle.GetMinimumRectangle(g);
        var c = r.Coordinates;
        double e0x = c[1].X - c[0].X, e0y = c[1].Y - c[0].Y, e1x = c[2].X - c[1].X, e1y = c[2].Y - c[1].Y;
        double l0 = Math.Sqrt(e0x * e0x + e0y * e0y), l1 = Math.Sqrt(e1x * e1x + e1y * e1y);
        double cx = (c[0].X + c[1].X + c[2].X + c[3].X) / 4, cy = (c[0].Y + c[1].Y + c[2].Y + c[3].Y) / 4;
        return l0 >= l1 ? (cx, cy, e0x / l0, e0y / l0, l0, l1) : (cx, cy, e1x / l1, e1y / l1, l1, l0);
    }

    static List<Polygon> Split(Polygon poly, LineString line)
    {
        var pz = new Polygonizer();
        pz.Add(poly.Boundary.Union(line));            // node the boundary with the cut line
        return pz.GetPolygons().OfType<Polygon>()
                 .Where(p => p.Area > 1e-6 && poly.Contains(p.InteriorPoint)).ToList();
    }

    static Polygon Poly(params (double x, double y)[] pts) =>
        F.CreatePolygon(pts.Append(pts[0]).Select(p => new Coordinate(p.x, p.y)).ToArray());

    static Polygon ArcBlock(double stepDeg)
    {
        IEnumerable<(double, double)> Arc(double r, double a0, double a1)
        {
            int n = (int)Math.Ceiling(Math.Abs(a1 - a0) / stepDeg - 1e-9);
            for (int k = 0; k <= n; k++)
            {
                double a = (a0 + (a1 - a0) * k / n) * Math.PI / 180;
                yield return (r * Math.Cos(a), r * Math.Sin(a));
            }
        }
        var inner = Arc(220, 60, 0).ToList();
        var pts = new List<(double, double)> { (220, 0) };
        pts.AddRange(Arc(300, 0, 60));
        pts.AddRange(inner.Take(inner.Count - 1));
        return Poly(pts.ToArray());
    }

    public static void Main()
    {
        var cases = new (string, Polygon)[] {
            ("a_rectangle", Poly((0,0),(240,0),(240,80),(0,80))),
            ("b_L", Poly((0,0),(200,0),(200,80),(80,80),(80,200),(0,200))),
            ("b_U", Poly((0,0),(240,0),(240,200),(160,200),(160,80),(80,80),(80,200),(0,200))),
            ("c_arc_10deg", ArcBlock(10)), ("c_arc_1deg", ArcBlock(1)),
            ("d_thin", Poly((0,0),(160,-6),(330,4),(430,40),(320,38),(170,40),(40,30))) };
        var o = new Options();
        foreach (var (name, block) in cases)
        {
            var sw = Stopwatch.StartNew();
            var lots = Subdivide(block, o);
            sw.Stop();
            var ringBuf = block.ExteriorRing.Buffer(0.01);
            int noAccess = lots.Count(p => p.ExteriorRing.Intersection(ringBuf).Length < o.AccessMin);
            Console.WriteLine($"{name,-12} plots={lots.Count,3} noAccess={noAccess,2} " +
                $"areaMin={lots.Min(p => p.Area),6:F1} areaMax={lots.Max(p => p.Area),6:F1} " +
                $"coverage={100 * lots.Sum(p => p.Area) / block.Area:F3}% ms={sw.Elapsed.TotalMilliseconds:F1}");
        }
    }
}
