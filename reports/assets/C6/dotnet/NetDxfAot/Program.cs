// netDxf Native AOT smoke test: read every DXF in a folder, save as R2000, build a new drawing.
using System.Diagnostics;
using netDxf;
using netDxf.Entities;
using netDxf.Header;

string inDir = args.Length > 0 ? args[0] : ".";
string outDir = args.Length > 1 ? args[1] : "out";
Directory.CreateDirectory(outDir);
static string Cps(string s) => string.Join(" ", s.Take(6).Select(c => $"U+{(int)c:X4}"));

foreach (var f in Directory.GetFiles(inDir, "*.dxf").OrderBy(x => x))
{
    var name = Path.GetFileNameWithoutExtension(f);
    try
    {
        var sw = Stopwatch.StartNew();
        var doc = DxfDocument.Load(f);
        if (doc == null) { Console.WriteLine($"FAIL  {name}: Load returned null"); continue; }
        var counts = string.Join(", ", doc.Entities.All.GroupBy(e => e.CodeName).OrderBy(g => g.Key).Select(g => $"{g.Key}={g.Count()}"));
        Console.WriteLine($"READ  {name}.dxf  ver={doc.DrawingVariables.AcadVer}  [{counts}]  {sw.ElapsedMilliseconds} ms");
        foreach (var t in doc.Entities.Texts.Take(2)) Console.WriteLine($"      TEXT  first chars {Cps(t.Value)}");
        foreach (var t in doc.Entities.MTexts.Take(1)) Console.WriteLine($"      MTEXT first chars {Cps(t.Value)}");
        doc.DrawingVariables.AcadVer = DxfVersion.AutoCad2000;
        doc.Save(Path.Combine(outDir, name + ".netdxf.dxf"));
    }
    catch (Exception ex)
    {
        Console.WriteLine($"FAIL  {name}: {ex.GetType().Name}: {ex.Message}");
    }
}

var d = new DxfDocument(DxfVersion.AutoCad2000);
d.Entities.Add(new Line(new Vector2(0, 0), new Vector2(25, 0)));
d.Entities.Add(new Polyline2D(new[] { new Polyline2DVertex(10, 0, Math.Tan(Math.PI / 2 / 4)), new Polyline2DVertex(0, 10) }));
d.Entities.Add(new Text("مخطط رئيسي", new Vector2(0, 20), 2.5));
var p = Path.Combine(outDir, "netdxf-new.dxf");
d.Save(p);
var back = DxfDocument.Load(p);
Console.WriteLine($"NEW   netdxf-new.dxf {new FileInfo(p).Length} bytes -> {back.Entities.All.Count()} entities; text {Cps(back.Entities.Texts.First().Value)}");
