using Velopack;
using Velopack.Sources;
using Sentry;
using Standard.Licensing;
using Standard.Licensing.Security.Cryptography;
using Standard.Licensing.Validation;

VelopackApp.Build().Run();
using var _ = SentrySdk.Init(o => { o.Dsn = "https://public@example.invalid/1"; o.SendDefaultPii = false; });
var mgr = new UpdateManager(new SimpleWebSource("https://example.invalid/releases"));
var keys = KeyGenerator.Create().GenerateKeyPair();
var lic = License.New().WithUniqueIdentifier(Guid.NewGuid()).As(LicenseType.Standard)
  .ExpiresAt(DateTime.UtcNow.AddDays(365))
  .WithProductFeatures(new Dictionary<string,string>{{"Parking","true"}})
  .LicensedTo("Test Co", "test@example.com").CreateAndSignWithPrivateKey(keys.ToEncryptedPrivateKeyString("p"), "p");
var ok = !License.Load(lic.ToString()).Validate().Signature(keys.ToPublicKeyString()).AssertValidLicense().Any();
Console.WriteLine($"installed={mgr.IsInstalled} licenceValid={ok}");
