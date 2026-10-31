// Read every DWG in a folder with ACadSharp and print version, entity counts, first text code points.
using ACadSharp; using ACadSharp.Entities; using ACadSharp.IO;
foreach (var f in Directory.GetFiles(args[0], "*.dwg").OrderBy(x => x))
{
    try
    {
        var notes = 0;
        var doc = DwgReader.Read(f, (s, e) => { if (e.NotificationType >= NotificationType.Warning) notes++; });
        var counts = string.Join(", ", doc.Entities.GroupBy(e => e.ObjectName).OrderBy(g => g.Key).Select(g => $"{g.Key}={g.Count()}"));
        var t = doc.Entities.OfType<TextEntity>().FirstOrDefault()?.Value;
        Console.WriteLine($"{Path.GetFileName(f)}: {doc.Header.Version} [{counts}] warnings={notes}" + (t == null ? "" : $" text {string.Join(" ", t.Take(4).Select(c => $"U+{(int)c:X4}"))}"));
    }
    catch (Exception ex) { Console.WriteLine($"{Path.GetFileName(f)}: FAIL {ex.GetType().Name}: {ex.Message}"); }
}
