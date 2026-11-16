// C8 measurement: decoding a Windows-1256 shapefile DBF string in .NET 8.
using System.Text;

string cpgPath = args[0];          // e.g. cp1256.cpg
string dbfPath = args[1];          // e.g. cp1256.dbf
string cpg = File.Exists(cpgPath) ? File.ReadAllText(cpgPath).Trim() : "";
Console.WriteLine($".cpg says: '{cpg}'");

try { Encoding.GetEncoding(1256); Console.WriteLine("GetEncoding(1256) without provider: OK"); }
catch (Exception e) { Console.WriteLine($"GetEncoding(1256) without provider: {e.GetType().Name}"); }

Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
Encoding enc = cpg.ToUpperInvariant() switch
{
    "UTF-8" or "UTF8" or "65001" => new UTF8Encoding(false),
    "CP1256" or "1256" or "WINDOWS-1256" => Encoding.GetEncoding(1256),
    _ => Encoding.Latin1 // what GDAL assumes when nothing is declared
};
Console.WriteLine($"Using {enc.WebName}");

// Minimal DBF reader: header length at byte 8, record length at byte 10, fields from byte 32.
byte[] b = File.ReadAllBytes(dbfPath);
int headerLen = BitConverter.ToUInt16(b, 8);
var fields = new List<(string name, int len)>();
for (int i = 32; b[i] != 0x0D; i += 32)
    fields.Add((Encoding.ASCII.GetString(b, i, 11).TrimEnd('\0'), b[i + 16]));
int pos = headerLen + 1; // skip deletion flag of record 1
foreach (var (name, len) in fields)
{
    Console.WriteLine($"  {name,-10} = {enc.GetString(b, pos, len).Trim()}");
    pos += len;
}
