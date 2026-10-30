// CadLib.NET (trial package, no licence key) Native AOT smoke test: read each DXF, write DXF and DWG.
using WW.Cad.IO;
using WW.Cad.Model;

string inDir = args.Length > 0 ? args[0] : ".";
string outDir = args.Length > 1 ? args[1] : "out";
Directory.CreateDirectory(outDir);
foreach (var f in Directory.GetFiles(inDir, "*.dxf").OrderBy(x => x))
{
    var name = Path.GetFileNameWithoutExtension(f);
    try
    {
        DxfModel model = CadReader.Read(f);
        Console.WriteLine($"READ  {name}.dxf  entities={model.Entities.Count}");
        DwgWriter.Write(Path.Combine(outDir, name + ".cadlib.dwg"), model, null);
        DxfWriter.Write(Path.Combine(outDir, name + ".cadlib.dxf"), model, false, null);
    }
    catch (Exception ex) { Console.WriteLine($"FAIL  {name}: {ex.GetType().Name}: {ex.Message}"); }
}
