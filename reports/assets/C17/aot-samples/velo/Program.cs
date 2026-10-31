using Velopack;
using Velopack.Sources;
VelopackApp.Build().Run();
var mgr = new UpdateManager(new SimpleWebSource("https://example.invalid/releases"));
Console.WriteLine($"installed={mgr.IsInstalled} version={mgr.CurrentVersion?.ToString() ?? "none"}");
if (args.Length > 0 && mgr.IsInstalled) {
    var info = await mgr.CheckForUpdatesAsync();
    if (info != null) { await mgr.DownloadUpdatesAsync(info); mgr.ApplyUpdatesAndRestart(info); }
}
