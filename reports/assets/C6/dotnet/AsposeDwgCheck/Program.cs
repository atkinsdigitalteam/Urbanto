// Independent check: open DWG files written by ACadSharp with Aspose.CAD (evaluation mode) and list entity types.
using Aspose.CAD; using Aspose.CAD.FileFormats.Cad;
foreach (var f in Directory.GetFiles(args[0], "*.dwg").OrderBy(x => x))
{
    try
    {
        using var img = Image.Load(f);
        var cad = (CadImage)img;
        var kinds = string.Join(", ", cad.Entities.GroupBy(e => e.TypeName.ToString()).OrderBy(g => g.Key).Select(g => $"{g.Key}={g.Count()}"));
        Console.WriteLine($"{Path.GetFileName(f)}: [{kinds}]");
    }
    catch (Exception ex) { Console.WriteLine($"{Path.GetFileName(f)}: FAIL {ex.GetType().Name}: {ex.Message}"); }
}
