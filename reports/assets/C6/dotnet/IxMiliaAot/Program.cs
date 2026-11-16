// IxMilia.Dxf Native AOT smoke test: read every DXF in a folder, save as R2000, build a new drawing.
using System.Diagnostics;
using IxMilia.Dxf;
using IxMilia.Dxf.Entities;

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
        var file = DxfFile.Load(f);
        var counts = string.Join(", ", file.Entities.GroupBy(e => e.EntityTypeString).OrderBy(g => g.Key).Select(g => $"{g.Key}={g.Count()}"));
        Console.WriteLine($"READ  {name}.dxf  ver={file.Header.Version}  [{counts}]  {sw.ElapsedMilliseconds} ms");
        foreach (var t in file.Entities.OfType<DxfText>().Take(2)) Console.WriteLine($"      TEXT  first chars {Cps(t.Value)}");
        foreach (var t in file.Entities.OfType<DxfMText>().Take(1)) Console.WriteLine($"      MTEXT first chars {Cps(t.Text)}");
        file.Header.Version = DxfAcadVersion.R2000;
        using (var fs = File.Create(Path.Combine(outDir, name + ".ixmilia.dxf"))) file.Save(fs);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"FAIL  {name}: {ex.GetType().Name}: {ex.Message}");
    }
}

var d = new DxfFile();
d.Header.Version = DxfAcadVersion.R2000;
d.Entities.Add(new DxfLine(new DxfPoint(0, 0, 0), new DxfPoint(25, 0, 0)));
var lw = new DxfLwPolyline(new[] {
    new DxfLwPolylineVertex { X = 10, Y = 0, Bulge = Math.Tan(Math.PI / 2 / 4) },
    new DxfLwPolylineVertex { X = 0, Y = 10 } });
d.Entities.Add(lw);
d.Entities.Add(new DxfText(new DxfPoint(0, 20, 0), 2.5, "مخطط رئيسي"));
var p = Path.Combine(outDir, "ixmilia-new.dxf");
using (var fs = File.Create(p)) d.Save(fs);
var back = DxfFile.Load(p);
Console.WriteLine($"NEW   ixmilia-new.dxf {new FileInfo(p).Length} bytes -> {back.Entities.Count} entities; text {Cps(back.Entities.OfType<DxfText>().First().Value)}");
