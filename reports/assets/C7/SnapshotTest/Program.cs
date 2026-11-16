using System.IO.Compression;
using DocumentFormat.OpenXml.Packaging;

static MemoryStream SnapshotWorkbook(string path)
{
    for (int attempt = 0; ; attempt++)
    {
        try
        {
            var before = File.GetLastWriteTimeUtc(path);
            var ms = new MemoryStream();
            using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read,
                       FileShare.ReadWrite | FileShare.Delete, 1 << 16, FileOptions.SequentialScan))
                fs.CopyTo(ms);                                    // handle closed before Excel's next save
            if (File.GetLastWriteTimeUtc(path) != before) throw new IOException("changed during copy");
            ms.Position = 0;
            using (SpreadsheetDocument.Open(ms, false)) { }       // throws FileFormatException if torn
            ms.Position = 0;
            return ms;
        }
        catch (Exception e) when (attempt < 5 &&
            e is IOException or FileFormatException or InvalidDataException or OpenXmlPackageException)
        {
            Console.WriteLine($"attempt {attempt}: {e.GetType().Name}, sleeping {250 << Math.Min(attempt, 3)} ms");
            Thread.Sleep(250 << Math.Min(attempt, 3));            // 250, 500, 1000, 2000, 2000 ms
        }
    }
}

// Test: start with a torn file, repair it after ~600 ms from another thread.
var good = args[0]; var path = Path.Combine(Path.GetTempPath(), "snap_test.xlsx");
var bytes = File.ReadAllBytes(good);
File.WriteAllBytes(path, bytes.AsSpan(0, bytes.Length / 2).ToArray());
var t = Task.Run(async () => { await Task.Delay(600); File.WriteAllBytes(path + ".tmp", bytes); File.Move(path + ".tmp", path, true); });
var sw = System.Diagnostics.Stopwatch.StartNew();
using var snap = SnapshotWorkbook(path);
Console.WriteLine($"snapshot ok: {snap.Length} bytes after {sw.ElapsedMilliseconds} ms");
await t;
