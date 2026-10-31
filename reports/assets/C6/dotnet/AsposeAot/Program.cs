// Aspose.CAD Native AOT smoke test (evaluation mode, no licence): read each DXF, save DXF and DWG.
using Aspose.CAD;
using Aspose.CAD.FileFormats.Cad;
using Aspose.CAD.ImageOptions;

string inDir = args.Length > 0 ? args[0] : ".";
string outDir = args.Length > 1 ? args[1] : "out";
Directory.CreateDirectory(outDir);
foreach (var f in Directory.GetFiles(inDir, "*.dxf").OrderBy(x => x))
{
    var name = Path.GetFileNameWithoutExtension(f);
    try
    {
        using var img = Image.Load(f);
        var cad = img as CadImage;
        Console.WriteLine($"READ  {name}.dxf  entities={cad?.Entities?.Count()}");
        img.Save(Path.Combine(outDir, name + ".aspose.dwg"), new DwgOptions());
        img.Save(Path.Combine(outDir, name + ".aspose.dxf"), new DxfOptions());
        Console.WriteLine($"SAVE  {name}: dwg {new FileInfo(Path.Combine(outDir, name + ".aspose.dwg")).Length} bytes");
    }
    catch (Exception ex) { Console.WriteLine($"FAIL  {name}: {ex.GetType().Name}: {ex.Message}"); }
}
