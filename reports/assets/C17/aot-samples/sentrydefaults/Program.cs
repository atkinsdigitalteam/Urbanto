using Sentry;
// Default options apart from DSN: shows what the .NET SDK sends with SendDefaultPii left at its default (false).
using (SentrySdk.Init(o => { o.Dsn = args[0]; o.AutoSessionTracking = false; }))
{
    try { throw new InvalidOperationException("test crash from AOT sample"); }
    catch (Exception ex) { Console.WriteLine($"captured {SentrySdk.CaptureException(ex)}"); }
    SentrySdk.Flush(TimeSpan.FromSeconds(5));
}
