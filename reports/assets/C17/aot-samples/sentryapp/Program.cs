using Sentry;
using (SentrySdk.Init(o => {
    o.Dsn = "https://public@example.invalid/1";
    o.SendDefaultPii = false; o.Debug = true; o.DiagnosticLevel = SentryLevel.Debug;
    o.AutoSessionTracking = true;
    o.SetBeforeSend((e, h) => { e.User = new SentryUser(); e.ServerName = null; return e; });
}))
{
    try { throw new InvalidOperationException("test"); }
    catch (Exception ex) { var id = SentrySdk.CaptureException(ex); Console.WriteLine($"captured {id}"); }
}
