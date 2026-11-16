using Standard.Licensing;
using Standard.Licensing.Security.Cryptography;
using Standard.Licensing.Validation;
var keys = KeyGenerator.Create().GenerateKeyPair();
var priv = keys.ToEncryptedPrivateKeyString("pass"); var pub = keys.ToPublicKeyString();
var lic = License.New().WithUniqueIdentifier(Guid.NewGuid()).As(LicenseType.Standard)
  .ExpiresAt(DateTime.UtcNow.AddDays(365)).WithMaximumUtilization(5)
  .WithProductFeatures(new Dictionary<string,string>{{"Parking","true"},{"Massing3D","true"},{"ExcelLink","false"}})
  .LicensedTo("Test Co", "test@example.com").CreateAndSignWithPrivateKey(priv, "pass");
var xml = lic.ToString();
var back = License.Load(xml);
var fails = back.Validate().ExpirationDate(DateTime.UtcNow).And().Signature(pub).AssertValidLicense().ToList();
Console.WriteLine($"len={xml.Length} failures={fails.Count} parking={back.ProductFeatures.Get("Parking")}");
