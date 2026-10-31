// Drives the state machine through a scripted session and prints every transition.
using ExcelLinkSketch;

var sm = new ExcelLinkStateMachine(seed: 7);
var clock = TimeSpan.Zero;
sm.Transitioned += (from, e, to, delay) =>
{
    Console.WriteLine($"| {clock.TotalSeconds,6:F2} | {from} | {e} | {to} | {(delay is null ? "-" : $"{delay.Value.TotalMilliseconds:F0} ms")} |");
};
void F(LinkEvent e) { var d = sm.Fire(e); if (d is not null) clock += d.Value; }

Console.WriteLine("| t (s) | From | Event | To | Next action after |");
Console.WriteLine("|---|---|---|---|---|");
F(LinkEvent.Link);
for (int i = 0; i < 4; i++) F(LinkEvent.NotRunning);         // Excel not running -> fallback after 3 retries
F(LinkEvent.FileChanged);                                     // user saved in another tool
F(LinkEvent.FileUnreadable); F(LinkEvent.FileUnreadable);     // torn read while a save is in progress
F(LinkEvent.ExcelAppeared); F(LinkEvent.Bound);
while (sm.State != LinkState.SuspendedByUser) F(LinkEvent.Busy); // user typing in a cell
for (int i = 0; i < 13; i++) F(LinkEvent.Busy);
Console.WriteLine($"busy notice due: {sm.ShouldShowBusyNotice} after {sm.TimeBusy.TotalSeconds:F1} s");
F(LinkEvent.CallOk);
F(LinkEvent.BeforeSave); F(LinkEvent.PathChanged);           // Save As
F(LinkEvent.ServerGone); F(LinkEvent.NotRunning); F(LinkEvent.Bound); // Excel crashed and was restarted
F(LinkEvent.WriteBlocked); F(LinkEvent.CallOk);              // protected sheet, then unprotected
F(LinkEvent.ConflictFound); F(LinkEvent.ConflictResolved);
F(LinkEvent.ServerGone); for (int i = 0; i < 4; i++) F(LinkEvent.NotRunning);   // Excel quit: fall back to the file
F(LinkEvent.ConflictFound); F(LinkEvent.ConflictResolved);                       // conflict found while in fallback
F(LinkEvent.Unlink);

Console.WriteLine();
Console.WriteLine("| Base | Studio | Excel | Owner | Decision |");
Console.WriteLine("|---|---|---|---|---|");
foreach (var (b, s, x, o) in new (object?, object?, object?, string?)[] {
    (2.5, 2.5, 3.0, null), (2.5, 3.2, 2.5, null), (2.5, 3.2, 3.2, null), (2.5, 3.2, 3.0, null),
    (2.5, 3.2, 3.0, "studio"), (2.5, 3.2, 3.0, "excel") })
    Console.WriteLine($"| {b} | {s} | {x} | {o ?? "none"} | {CellMerge.Decide(b, s, x, o)} |");

Console.WriteLine();
Console.WriteLine($"transition table rows: {ExcelLinkStateMachine.Table.Count}");
var reachable = new HashSet<LinkState> { LinkState.Disconnected };
bool grew = true;
while (grew) { grew = false; foreach (var kv in ExcelLinkStateMachine.Table) if (reachable.Contains(kv.Key.Item1) && reachable.Add(kv.Value)) grew = true; }
reachable.Add(LinkState.FileFallback); // entered through the NotRunning attempt counter, not a table row
Console.WriteLine($"states reachable: {reachable.Count} of {Enum.GetValues<LinkState>().Length}");
