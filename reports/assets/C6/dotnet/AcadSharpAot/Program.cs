// ACadSharp Native AOT smoke test: read every DXF in a folder, write it back as
// R2000 DXF and as AC1015 DWG, read the DWG back, then build a new drawing from code.
using System.Diagnostics;
using System.Text;
using ACadSharp;
using ACadSharp.Entities;
using ACadSharp.IO;
using CSMath;

string inDir = args.Length > 0 ? args[0] : ".";
string outDir = args.Length > 1 ? args[1] : "out";
Directory.CreateDirectory(outDir);

static string Counts(CadDocument d) =>
    string.Join(", ", d.Entities.GroupBy(e => e.ObjectName).OrderBy(g => g.Key).Select(g => $"{g.Key}={g.Count()}"));

static string Cps(string s) => string.Join(" ", s.Take(6).Select(c => $"U+{(int)c:X4}"));

foreach (var f in Directory.GetFiles(inDir, "*.dxf").OrderBy(x => x))
{
    var name = Path.GetFileNameWithoutExtension(f);
    var notes = new List<string>();
    NotificationEventHandler onNote = (s, e) => { if (e.NotificationType >= NotificationType.Warning) notes.Add($"{e.NotificationType}: {e.Message}"); };
    try
    {
        var sw = Stopwatch.StartNew();
        CadDocument doc = DxfReader.Read(f, onNote);
        Console.WriteLine($"READ  {name}.dxf  ver={doc.Header.Version}  [{Counts(doc)}]  warnings={notes.Count}  {sw.ElapsedMilliseconds} ms");
        foreach (var n in notes.Distinct().Take(4)) Console.WriteLine($"      {n}");
        foreach (var t in doc.Entities.OfType<TextEntity>().Take(2)) Console.WriteLine($"      TEXT  first chars {Cps(t.Value)}");
        foreach (var t in doc.Entities.OfType<MText>().Take(1)) Console.WriteLine($"      MTEXT first chars {Cps(t.Value)}");
        foreach (var d in doc.Entities.OfType<Dimension>()) Console.WriteLine($"      DIM {d.ObjectName} measurement={d.Measurement:0.###} block={(d.Block?.Name ?? "null")}");

        notes.Clear();
        var dxfOut = Path.Combine(outDir, name + ".acadsharp.dxf");
        DxfWriter.Write(dxfOut, doc, false, null, onNote);
        var dwgOut = Path.Combine(outDir, name + ".acadsharp.dwg");
        doc.Header.Version = ACadVersion.AC1015;
        DwgWriter.Write(dwgOut, doc, null, onNote);
        var back = DwgReader.Read(dwgOut, onNote);
        Console.WriteLine($"DWG   {name}.dwg  {new FileInfo(dwgOut).Length} bytes, read back [{Counts(back)}]  warnings={notes.Count}");
        foreach (var n in notes.Distinct().Take(4)) Console.WriteLine($"      {n}");
        var dwg2dxf = Path.Combine(outDir, name + ".dwg-roundtrip.dxf");
        DxfWriter.Write(dwg2dxf, back, false, null, null);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"FAIL  {name}: {ex.GetType().Name}: {ex.Message}");
    }
}

// New drawing from code: Arabic TEXT written to DWG in several versions / code pages
foreach (var (ver, cp) in new[] { (ACadVersion.AC1015, "ANSI_1252"), (ACadVersion.AC1015, "ANSI_1256"),
                                   (ACadVersion.AC1018, "ANSI_1256"), (ACadVersion.AC1024, "ANSI_1252") })
{
    try
    {
        var nd = new CadDocument(ver);
        nd.Header.CodePage = cp;
        nd.Entities.Add(new Line { StartPoint = new XYZ(0, 0, 0), EndPoint = new XYZ(25, 0, 0) });
        var lw = new LwPolyline();
        lw.Vertices.Add(new LwPolyline.Vertex(new XY(10, 0)) { Bulge = Math.Tan(Math.PI / 2 / 4) });
        lw.Vertices.Add(new LwPolyline.Vertex(new XY(0, 10)));
        nd.Entities.Add(lw);
        nd.Entities.Add(new TextEntity { Value = "\u0645\u062E\u0637\u0637 \u0631\u0626\u064A\u0633\u064A", InsertPoint = new XYZ(0, 20, 0), Height = 2.5 });
        var stem = Path.Combine(outDir, $"acadsharp-new-{ver}-{cp}");
        DxfWriter.Write(stem + ".dxf", nd, false, null, null);
        DwgWriter.Write(stem + ".dwg", nd, null, null);
        var rb = DwgReader.Read(stem + ".dwg");
        var rx = DxfReader.Read(stem + ".dxf");
        Console.WriteLine($"NEW   {Path.GetFileName(stem)}.dwg {new FileInfo(stem + ".dwg").Length} bytes -> [{Counts(rb)}]; " +
            $"DWG text {Cps(rb.Entities.OfType<TextEntity>().First().Value)}; DXF text {Cps(rx.Entities.OfType<TextEntity>().First().Value)}; " +
            $"bulge {rb.Entities.OfType<LwPolyline>().First().Vertices[0].Bulge:0.########}");
    }
    catch (Exception ex) { Console.WriteLine($"FAIL  new {ver} {cp}: {ex.GetType().Name}: {ex.Message}"); }
}
