using LicenseSpring;
var cfg = new Configuration(apiKey: "x", sharedKey: "y", productCode: "p", appName: "a", appVersion: "1.0");
var mgr = LicenseManager.GetInstance(); try { mgr.Initialize(cfg); Console.WriteLine("init ok, current=" + (mgr.CurrentLicense()?.Key() ?? "none")); } catch (Exception e) { Console.WriteLine("err " + e.GetType().Name); }
