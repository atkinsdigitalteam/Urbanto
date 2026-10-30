using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

// Vendor side (would run on your licence server): sign a licence with ECDSA P-256.
using var vendorKey = ECDsa.Create(ECCurve.NamedCurves.nistP256);
var lic = new Licence("LIC-0001", "Test Co", DateTime.UtcNow.AddDays(365), 5,
    new[] { "core", "parking", "massing3d" }, "MACHINE-FINGERPRINT-HASH");
byte[] payload = JsonSerializer.SerializeToUtf8Bytes(lic, LicJson.Default.Licence);
byte[] sig = vendorKey.SignData(payload, HashAlgorithmName.SHA256);
string file = Convert.ToBase64String(payload) + "." + Convert.ToBase64String(sig);
string pubPem = vendorKey.ExportSubjectPublicKeyInfoPem();

// Client side (inside the app): verify offline with the embedded public key.
using var pub = ECDsa.Create(); pub.ImportFromPem(pubPem);
var parts = file.Split('.');
var p = Convert.FromBase64String(parts[0]);
bool valid = pub.VerifyData(p, Convert.FromBase64String(parts[1]), HashAlgorithmName.SHA256);
var back = JsonSerializer.Deserialize(p, LicJson.Default.Licence)!;
Console.WriteLine($"fileLen={file.Length} valid={valid} parking={back.Modules.Contains("parking")} expires={back.Expires:yyyy-MM-dd}");

record Licence(string Id, string Customer, DateTime Expires, int Seats, string[] Modules, string Fingerprint);
[JsonSerializable(typeof(Licence))] partial class LicJson : JsonSerializerContext {}
