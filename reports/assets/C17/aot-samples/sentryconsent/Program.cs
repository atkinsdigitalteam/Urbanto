using Sentry;

// Consent-gated, privacy-trimmed Sentry setup (sample; consent would come from a first-run dialog or settings file).
bool userConsented = args.Length > 1 && args[1] == "--consent";
if (!userConsented) { Console.WriteLine("no consent: Sentry not initialised"); return; }

using (SentrySdk.Init(o =>
{
    o.Dsn = args[0];
    o.SendDefaultPii = false;            // SDK default; stated explicitly
    o.AutoSessionTracking = false;       // no session pings unless the user also agrees to usage stats
    o.Release = "studio@1.0.0";
    o.SetBeforeSend(e =>
    {
        e.ServerName = null;             // never send the machine name
        e.User = new SentryUser { Id = e.User?.Id }; // keep only the random installation id
        foreach (var img in e.DebugImages ?? new())
            if (img.CodeFile is { } p) img.CodeFile = Path.GetFileName(p); // drop C:\Users\<name>\... prefix
        return e;
    });
}))
{
    try { throw new InvalidOperationException("test crash"); }
    catch (Exception ex) { Console.WriteLine($"captured {SentrySdk.CaptureException(ex)}"); }
    SentrySdk.Flush(TimeSpan.FromSeconds(5));
}
