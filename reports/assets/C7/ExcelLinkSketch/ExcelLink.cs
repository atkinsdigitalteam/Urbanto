// ExcelLink.cs: general example code for report C7 "Excel live link robustness".
// Not Studio code. Shows (1) a retrying COM message filter and (2) a reconnection state
// machine that is independent of COM so it can be unit-tested anywhere.
// Built-in COM interop ([ComImport], RCWs) is Windows-only and not supported by Native AOT.
using System.Runtime.InteropServices;
using System.Runtime.Versioning;

namespace ExcelLinkSketch;

// ---------------------------------------------------------------------------------------
// 1. Message filter. Register it on the STA thread that makes the Excel calls.
//    COM calls RetryRejectedCall when Excel answers SERVERCALL_RETRYLATER (busy) or
//    SERVERCALL_REJECTED. Return -1 to cancel (caller gets RPC_E_CALL_REJECTED 0x80010001),
//    0..99 to retry at once, >=100 to wait that many milliseconds and retry.
// ---------------------------------------------------------------------------------------
[ComImport, Guid("00000016-0000-0000-C000-000000000046"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
internal interface IOleMessageFilter
{
    [PreserveSig] int HandleInComingCall(int dwCallType, IntPtr hTaskCaller, int dwTickCount, IntPtr lpInterfaceInfo);
    [PreserveSig] int RetryRejectedCall(IntPtr hTaskCallee, int dwTickCount, int dwRejectType);
    [PreserveSig] int MessagePending(IntPtr hTaskCallee, int dwTickCount, int dwPendingType);
}

[SupportedOSPlatform("windows")]
internal sealed class RetryMessageFilter : IOleMessageFilter
{
    const int SERVERCALL_ISHANDLED = 0, SERVERCALL_REJECTED = 1, SERVERCALL_RETRYLATER = 2;
    const int PENDINGMSG_WAITDEFPROCESS = 2;

    // Short per-call budget: keep the STA responsive and let the state machine own long waits.
    public static int PerCallBudgetMs { get; set; } = 2000;

    [DllImport("ole32.dll")]
    static extern int CoRegisterMessageFilter(IOleMessageFilter? newFilter, out IOleMessageFilter? oldFilter);

    /// <summary>Call on the STA thread that talks to Excel. MTA threads cannot have message filters.</summary>
    public static IDisposable Register()
    {
        if (Thread.CurrentThread.GetApartmentState() != ApartmentState.STA)
            throw new InvalidOperationException("Message filters work only on STA threads.");
        CoRegisterMessageFilter(new RetryMessageFilter(), out var old);
        return new Revoker(old);
    }

    sealed class Revoker(IOleMessageFilter? old) : IDisposable
    {
        public void Dispose() => CoRegisterMessageFilter(old, out _);
    }

    int IOleMessageFilter.HandleInComingCall(int t, IntPtr caller, int ticks, IntPtr info) => SERVERCALL_ISHANDLED;

    int IOleMessageFilter.RetryRejectedCall(IntPtr callee, int elapsedMs, int rejectType)
    {
        if (rejectType == SERVERCALL_REJECTED) return -1;           // definite refusal
        if (rejectType != SERVERCALL_RETRYLATER) return -1;
        if (elapsedMs >= PerCallBudgetMs) return -1;                // hand over to the state machine
        // 100, 200, 400 ms ... capped at 500 ms. Never return 0..99: that retries immediately
        // and spins a core while Excel is in a modal state.
        int step = Math.Min(500, 100 << Math.Min(3, elapsedMs / 250));
        return step;
    }

    int IOleMessageFilter.MessagePending(IntPtr callee, int ticks, int pendingType) => PENDINGMSG_WAITDEFPROCESS;
}

// ---------------------------------------------------------------------------------------
// 2. HRESULT classification. Values from winerror.h (Microsoft COM error code pages).
// ---------------------------------------------------------------------------------------
public enum LinkEvent
{
    Link, Unlink,                 // user intent
    Bound, NotRunning,            // discovery results
    CallOk, Busy, BusyTooLong,    // call outcomes and Busy timer
    BeforeSave, AfterSave, PathChanged, BeforeClose, WorkbookGone,
    ServerGone, ReadOnly, WriteBlocked, RemoteChange,
    FileChanged, FileUnreadable, ExcelAppeared,
    ConflictFound, ConflictResolved,
}

public static class HResult
{
    public const int RPC_E_CALL_REJECTED = unchecked((int)0x80010001);
    public const int RPC_E_SERVERCALL_RETRYLATER = unchecked((int)0x8001010A);
    public const int RPC_E_DISCONNECTED = unchecked((int)0x80010108);
    public const int RPC_E_SERVER_DIED = unchecked((int)0x80010007);
    public const int RPC_E_SERVER_DIED_DNE = unchecked((int)0x80010012);
    public const int RPC_S_SERVER_UNAVAILABLE = unchecked((int)0x800706BA);
    public const int RPC_S_CALL_FAILED = unchecked((int)0x800706BE);
    public const int MK_E_UNAVAILABLE = unchecked((int)0x800401E3);
    public const int VBA_E_IGNORE = unchecked((int)0x800AC472);   // Excel: busy with user input / dialog
    public const int SHARING_VIOLATION = unchecked((int)0x80070020);

    public static LinkEvent Classify(int hr) => hr switch
    {
        RPC_E_CALL_REJECTED or RPC_E_SERVERCALL_RETRYLATER or VBA_E_IGNORE => LinkEvent.Busy,
        RPC_E_DISCONNECTED or RPC_E_SERVER_DIED or RPC_E_SERVER_DIED_DNE
            or RPC_S_SERVER_UNAVAILABLE or RPC_S_CALL_FAILED => LinkEvent.ServerGone,
        MK_E_UNAVAILABLE => LinkEvent.NotRunning,
        _ => LinkEvent.WriteBlocked,   // e.g. protected sheet: stop writing, keep reading, tell the user
    };
}

// ---------------------------------------------------------------------------------------
// 3. States, transition table, backoff.
// ---------------------------------------------------------------------------------------
public enum LinkState
{
    Disconnected, Discovering, Linked, Busy, SuspendedByUser, Saving,
    ReadOnlyLinked, Conflict, Lost, FileFallback,
}

public sealed record Backoff(TimeSpan First, TimeSpan Max, double Jitter = 0.2)
{
    public TimeSpan Delay(int attempt, Random rng)
    {
        double ms = Math.Min(Max.TotalMilliseconds, First.TotalMilliseconds * Math.Pow(2, attempt));
        return TimeSpan.FromMilliseconds(ms * (1 + Jitter * (2 * rng.NextDouble() - 1)));
    }
}

public static class Policy
{
    public static readonly Backoff BusyRetry = new(TimeSpan.FromMilliseconds(250), TimeSpan.FromSeconds(2));
    public static readonly TimeSpan BusyToSuspended = TimeSpan.FromSeconds(5);
    public static readonly TimeSpan SuspendedPoll = TimeSpan.FromSeconds(2);
    public static readonly TimeSpan SuspendedNotice = TimeSpan.FromSeconds(30);   // ~30 s, as Microsoft suggests for the busy dialog
    public static readonly Backoff Rediscover = new(TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(8), Jitter: 0);
    public static readonly int RediscoverAttemptsBeforeFallback = 3;
    public static readonly TimeSpan FallbackRotPoll = TimeSpan.FromSeconds(5);
    public static readonly TimeSpan FileDebounce = TimeSpan.FromMilliseconds(500);
    public static readonly Backoff TornFileRetry = new(TimeSpan.FromMilliseconds(250), TimeSpan.FromSeconds(2), Jitter: 0);
}

public sealed class ExcelLinkStateMachine
{
    // (from, event) -> to. Anything missing is ignored (logged) rather than thrown.
    public static readonly Dictionary<(LinkState, LinkEvent), LinkState> Table = new()
    {
        [(LinkState.Disconnected, LinkEvent.Link)] = LinkState.Discovering,
        [(LinkState.Discovering, LinkEvent.Bound)] = LinkState.Linked,
        [(LinkState.Discovering, LinkEvent.NotRunning)] = LinkState.Discovering,      // retry with backoff, then fallback
        [(LinkState.Discovering, LinkEvent.ReadOnly)] = LinkState.ReadOnlyLinked,
        [(LinkState.Linked, LinkEvent.Busy)] = LinkState.Busy,
        [(LinkState.Linked, LinkEvent.BeforeSave)] = LinkState.Saving,
        [(LinkState.Linked, LinkEvent.BeforeClose)] = LinkState.Linked,                // closing is not certain yet
        [(LinkState.Linked, LinkEvent.WorkbookGone)] = LinkState.Lost,
        [(LinkState.Linked, LinkEvent.ServerGone)] = LinkState.Lost,
        [(LinkState.Linked, LinkEvent.ReadOnly)] = LinkState.ReadOnlyLinked,
        [(LinkState.Linked, LinkEvent.WriteBlocked)] = LinkState.ReadOnlyLinked,
        [(LinkState.Linked, LinkEvent.RemoteChange)] = LinkState.Linked,               // re-read keyed rows
        [(LinkState.Linked, LinkEvent.ConflictFound)] = LinkState.Conflict,
        [(LinkState.Busy, LinkEvent.CallOk)] = LinkState.Linked,
        [(LinkState.Busy, LinkEvent.Busy)] = LinkState.Busy,
        [(LinkState.Busy, LinkEvent.BusyTooLong)] = LinkState.SuspendedByUser,
        [(LinkState.Busy, LinkEvent.ServerGone)] = LinkState.Lost,
        [(LinkState.SuspendedByUser, LinkEvent.CallOk)] = LinkState.Linked,            // flush queued writes
        [(LinkState.SuspendedByUser, LinkEvent.Busy)] = LinkState.SuspendedByUser,
        [(LinkState.SuspendedByUser, LinkEvent.ServerGone)] = LinkState.Lost,
        [(LinkState.Saving, LinkEvent.AfterSave)] = LinkState.Linked,
        [(LinkState.Saving, LinkEvent.PathChanged)] = LinkState.Linked,                // Save As: rebind to new FullName
        [(LinkState.Saving, LinkEvent.Busy)] = LinkState.Saving,
        [(LinkState.Saving, LinkEvent.ServerGone)] = LinkState.Lost,
        [(LinkState.ReadOnlyLinked, LinkEvent.CallOk)] = LinkState.Linked,             // user enabled editing / unprotected
        [(LinkState.ReadOnlyLinked, LinkEvent.ServerGone)] = LinkState.Lost,
        [(LinkState.ReadOnlyLinked, LinkEvent.WorkbookGone)] = LinkState.Lost,
        [(LinkState.Conflict, LinkEvent.ConflictResolved)] = LinkState.Linked,
        [(LinkState.Conflict, LinkEvent.ServerGone)] = LinkState.Lost,
        [(LinkState.Lost, LinkEvent.Bound)] = LinkState.Linked,
        [(LinkState.Lost, LinkEvent.NotRunning)] = LinkState.Lost,                     // count attempts
        [(LinkState.FileFallback, LinkEvent.FileChanged)] = LinkState.FileFallback,     // debounce, then read
        [(LinkState.FileFallback, LinkEvent.FileUnreadable)] = LinkState.FileFallback,  // torn read: retry
        [(LinkState.FileFallback, LinkEvent.ExcelAppeared)] = LinkState.Discovering,
        [(LinkState.FileFallback, LinkEvent.ConflictFound)] = LinkState.Conflict,
    };

    readonly Random _rng;
    int _attempt;
    LinkState _beforeConflict = LinkState.Linked;
    TimeSpan _busyFor;
    public LinkState State { get; private set; } = LinkState.Disconnected;
    public Queue<(string key, string field, object value)> PendingWrites { get; } = new();
    public event Action<LinkState, LinkEvent, LinkState, TimeSpan?>? Transitioned;

    public ExcelLinkStateMachine(int seed = 1) => _rng = new Random(seed);

    /// <summary>Feeds one event. Returns the delay before the caller should act again (null = no timer).</summary>
    public TimeSpan? Fire(LinkEvent e)
    {
        var from = State;
        if (!Table.TryGetValue((from, e), out var to))
        {
            // Unlink works from every state; losing Excel always leads to Lost.
            if (e == LinkEvent.Unlink) to = LinkState.Disconnected;
            else if (e == LinkEvent.ServerGone || e == LinkEvent.WorkbookGone) to = LinkState.Lost;
            else return null;
        }
        if (to == LinkState.Conflict && from != LinkState.Conflict) _beforeConflict = from;
        if (from == LinkState.Conflict && e == LinkEvent.ConflictResolved) to = _beforeConflict; // back to Linked or FileFallback
        TimeSpan? delay = null;
        if (to != from) { _attempt = 0; if (to != LinkState.SuspendedByUser) _busyFor = TimeSpan.Zero; }

        switch (to)
        {
            case LinkState.Busy:
                delay = Policy.BusyRetry.Delay(_attempt++, _rng);
                _busyFor += delay.Value;
                if (_busyFor >= Policy.BusyToSuspended) { State = to; return Fire(LinkEvent.BusyTooLong); }
                break;
            case LinkState.SuspendedByUser:
                delay = Policy.SuspendedPoll;
                _busyFor += delay.Value;
                break;
            case LinkState.Discovering when e == LinkEvent.NotRunning:
            case LinkState.Lost when e == LinkEvent.NotRunning:
                if (_attempt >= Policy.RediscoverAttemptsBeforeFallback) { to = LinkState.FileFallback; _attempt = 0; delay = Policy.FallbackRotPoll; break; }
                delay = Policy.Rediscover.Delay(_attempt++, _rng);
                break;
            case LinkState.Lost:
                delay = TimeSpan.Zero;                       // try the ROT at once: Excel may only have closed the workbook
                break;
            case LinkState.FileFallback when e == LinkEvent.FileChanged:
                delay = Policy.FileDebounce;
                break;
            case LinkState.FileFallback when e == LinkEvent.FileUnreadable:
                delay = Policy.TornFileRetry.Delay(_attempt++, _rng);
                break;
        }
        State = to;
        Transitioned?.Invoke(from, e, to, delay);
        return delay;
    }

    public bool CanWrite => State is LinkState.Linked or LinkState.FileFallback;
    public TimeSpan TimeBusy => _busyFor;
    public bool ShouldShowBusyNotice => State == LinkState.SuspendedByUser && _busyFor >= Policy.SuspendedNotice;
}

// ---------------------------------------------------------------------------------------
// 4. Three-way merge per keyed cell (row identity key + field), used on every sync.
// ---------------------------------------------------------------------------------------
public enum MergeOutcome { NoChange, TakeExcel, PushStudio, Conflict }

public static class CellMerge
{
    public static MergeOutcome Decide(object? baseValue, object? studio, object? excel, string? owner = null)
    {
        bool sChanged = !Equals(studio, baseValue), eChanged = !Equals(excel, baseValue);
        if (!sChanged && !eChanged) return MergeOutcome.NoChange;
        if (sChanged && !eChanged) return MergeOutcome.PushStudio;
        if (!sChanged && eChanged) return MergeOutcome.TakeExcel;
        if (Equals(studio, excel)) return MergeOutcome.NoChange;      // both made the same edit
        return owner switch                                            // column ownership settles most clashes
        {
            "studio" => MergeOutcome.PushStudio,
            "excel" => MergeOutcome.TakeExcel,
            _ => MergeOutcome.Conflict,
        };
    }
}
