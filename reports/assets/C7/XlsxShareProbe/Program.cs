// XlsxShareProbe: what happens when .NET Excel libraries open an .xlsx that another
// process is holding open. General example code for report C7 (not Studio code).
// Usage:
//   make <path>                     create a small workbook with formulas and cached values
//   hold <path> <None|Read|ReadWrite> <seconds>   hold the file open (FileAccess.ReadWrite)
//   probe <path>                    try every open strategy and print one line per try
//   torn <path>                     open a half-written copy and report the exception
//   excelsave <path>                Excel-style save (temp file, delete original, rename) while a reader holds a handle
//   stale <path>                    write an input cell with the SDK and show the dependent cached value
//   timing <rows>                   time a full read with each library
using System.Diagnostics;
using ClosedXML.Excel;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Spreadsheet;
using ExcelDataReader;
using MiniExcelLibs;

static class P
{
    static int Main(string[] a)
    {
        System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance); // ExcelDataReader needs this
        switch (a[0])
        {
            case "make": Make(a[1], 3); return 0;
            case "hold": Hold(a[1], Enum.Parse<FileShare>(a[2]), int.Parse(a[3])); return 0;
            case "probe": Probe(a[1]); return 0;
            case "torn": Torn(a[1]); return 0;
            case "excelsave": ExcelSave(a[1]); return 0;
            case "stale": Stale(a[1]); return 0;
            case "timing": Timing(int.Parse(a[1])); return 0;
            case "sdkedit": // copy, then change one cell in place with the Open XML SDK
                File.Copy(a[1], a[2], true);
                using (var d = SpreadsheetDocument.Open(a[2], true))
                {
                    var c = d.WorkbookPart!.WorksheetParts.First().Worksheet.Descendants<Cell>().First(x => x.CellReference == "B2");
                    c.CellValue = new CellValue(5000); c.DataType = null; d.Save();
                }
                return 0;
            case "cxedit": // load, change one cell, save with ClosedXML
                using (var wb = new XLWorkbook(a[1])) { wb.Worksheet(1).Cell("B2").Value = 5000; wb.SaveAs(a[2]); }
                return 0;
        }
        return 1;
    }

    // ---------- sample workbook: PlotId | Area_m2 | FAR | GFA (=B*C, with cached value) ----------
    public static void Make(string path, int rows, int extraCols = 0)
    {
        using var doc = SpreadsheetDocument.Create(path, SpreadsheetDocumentType.Workbook);
        var wbp = doc.AddWorkbookPart();
        wbp.Workbook = new Workbook();
        var wsp = wbp.AddNewPart<WorksheetPart>();
        var data = new SheetData();
        string[] head = ["PlotId", "Area_m2", "FAR", "GFA"];
        var hr = new Row { RowIndex = 1 };
        for (int c = 0; c < head.Length + extraCols; c++)
            hr.Append(new Cell { CellReference = Col(c) + "1", DataType = CellValues.InlineString,
                InlineString = new InlineString(new Text(c < head.Length ? head[c] : $"X{c}")) });
        data.Append(hr);
        for (int r = 2; r <= rows + 1; r++)
        {
            double area = 1000 + r, far = 2.5;
            var row = new Row { RowIndex = (uint)r };
            row.Append(new Cell { CellReference = $"A{r}", DataType = CellValues.InlineString, InlineString = new InlineString(new Text($"P-{r - 1:D4}")) });
            row.Append(new Cell { CellReference = $"B{r}", CellValue = new CellValue(area) });
            row.Append(new Cell { CellReference = $"C{r}", CellValue = new CellValue(far) });
            // formula plus the cached value Excel would have written
            row.Append(new Cell { CellReference = $"D{r}", CellFormula = new CellFormula($"B{r}*C{r}"), CellValue = new CellValue(area * far) });
            for (int c = 0; c < extraCols; c++)
                row.Append(new Cell { CellReference = Col(4 + c) + r, CellValue = new CellValue(r * 10 + c) });
            data.Append(row);
        }
        wsp.Worksheet = new Worksheet(data);
        wbp.Workbook.AppendChild(new Sheets(new Sheet { Id = wbp.GetIdOfPart(wsp), SheetId = 1, Name = "Plots" }));
    }

    static string Col(int i) { string s = ""; i++; while (i > 0) { int m = (i - 1) % 26; s = (char)('A' + m) + s; i = (i - 1) / 26; } return s; }

    static void Hold(string path, FileShare share, int seconds)
    {
        using var fs = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, share);
        Console.WriteLine($"HOLDING share={share}");
        Console.Out.Flush();
        Thread.Sleep(seconds * 1000);
    }

    static void Try(string name, Func<string> f)
    {
        try { Console.WriteLine($"  OK    {name}: {f()}"); }
        catch (Exception e)
        {
            var inner = e.InnerException is null ? "" : $" <- {e.InnerException.GetType().Name}";
            Console.WriteLine($"  FAIL  {name}: {e.GetType().Name} HResult=0x{e.HResult:X8}{inner}: {e.Message.Split('\n')[0]}");
        }
    }

    static string ReadA2(SpreadsheetDocument d)
    {
        var ws = d.WorkbookPart!.WorksheetParts.First().Worksheet;
        var c = ws.Descendants<Cell>().First(x => x.CellReference == "D2");
        return $"D2 formula={c.CellFormula?.Text} cached={c.CellValue?.Text}";
    }

    static void Probe(string path)
    {
        Try("OpenXml SpreadsheetDocument.Open(path, isEditable:false)", () => { using var d = SpreadsheetDocument.Open(path, false); return ReadA2(d); });
        Try("OpenXml Open(FileStream Read, FileShare.ReadWrite)", () =>
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            using var d = SpreadsheetDocument.Open(fs, false); return ReadA2(d);
        });
        Try("OpenXml Open(FileStream Read, FileShare.ReadWrite|Delete)", () =>
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
            using var d = SpreadsheetDocument.Open(fs, false); return ReadA2(d);
        });
        Try("Copy to MemoryStream via FileShare.ReadWrite, then OpenXml", () =>
        {
            var ms = new MemoryStream();
            using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete)) fs.CopyTo(ms);
            ms.Position = 0; using var d = SpreadsheetDocument.Open(ms, false); return ReadA2(d) + $" ({ms.Length} bytes)";
        });
        Try("File.Copy to temp, then OpenXml", () =>
        {
            var tmp = Path.GetTempFileName(); File.Copy(path, tmp, true);
            using var d = SpreadsheetDocument.Open(tmp, false); return ReadA2(d);
        });
        Try("OpenXml SpreadsheetDocument.Open(path, isEditable:true) + save", () =>
        {
            using var d = SpreadsheetDocument.Open(path, true);
            var c = d.WorkbookPart!.WorksheetParts.First().Worksheet.Descendants<Cell>().First(x => x.CellReference == "B2");
            c.CellValue = new CellValue(1234); d.Save(); return "wrote B2=1234";
        });
        Try("ClosedXML new XLWorkbook(path)", () => { using var wb = new XLWorkbook(path); return $"D2={wb.Worksheet(1).Cell("D2").FormulaA1} cachedValue={wb.Worksheet(1).Cell("D2").CachedValue}"; });
        Try("ClosedXML new XLWorkbook(FileStream FileShare.ReadWrite)", () =>
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            using var wb = new XLWorkbook(fs); return $"D2 value={wb.Worksheet(1).Cell("D2").Value}";
        });
        Try("ExcelDataReader on File.Open(path, Open, Read) [default share]", () =>
        {
            using var fs = File.Open(path, FileMode.Open, FileAccess.Read);
            using var r = ExcelReaderFactory.CreateReader(fs); r.Read(); r.Read(); return $"D2={r.GetValue(3)}";
        });
        Try("ExcelDataReader on FileStream FileShare.ReadWrite", () =>
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            using var r = ExcelReaderFactory.CreateReader(fs); r.Read(); r.Read(); return $"D2={r.GetValue(3)}";
        });
        Try("MiniExcel.Query(path)", () => { var row = MiniExcel.Query(path, useHeaderRow: true).Cast<IDictionary<string, object>>().First(); return $"GFA={row["GFA"]}"; });
    }

    static void Torn(string path)
    {
        var bytes = File.ReadAllBytes(path);
        foreach (var frac in new[] { 0.5, 0.95 })
        {
            var cut = Path.Combine(Path.GetTempPath(), $"torn_{frac}.xlsx");
            File.WriteAllBytes(cut, bytes.AsSpan(0, (int)(bytes.Length * frac)).ToArray());
            Console.WriteLine($"-- file truncated to {frac:P0} of {bytes.Length} bytes");
            Try("OpenXml", () => { using var d = SpreadsheetDocument.Open(cut, false); return ReadA2(d); });
            Try("ClosedXML", () => { using var wb = new XLWorkbook(cut); return "opened"; });
            Try("ExcelDataReader", () => { using var fs = File.OpenRead(cut); using var r = ExcelReaderFactory.CreateReader(fs); r.Read(); return "opened"; });
            Try("MiniExcel", () => { var n = MiniExcel.Query(cut).Count(); return $"{n} rows"; });
        }
    }

    // Excel's documented save: write a temp file in the same folder, delete the original, rename the temp.
    static void ExcelSave(string path)
    {
        var dir = Path.GetDirectoryName(Path.GetFullPath(path))!;
        var events = new List<string>();
        using var w = new FileSystemWatcher(dir) { IncludeSubdirectories = false, EnableRaisingEvents = true };
        var sw = Stopwatch.StartNew();
        void Log(string s) { lock (events) events.Add($"{sw.ElapsedMilliseconds,4} ms {s}"); }
        w.Created += (_, e) => Log($"Created {e.Name}");
        w.Changed += (_, e) => Log($"Changed {e.Name}");
        w.Deleted += (_, e) => Log($"Deleted {e.Name}");
        w.Renamed += (_, e) => Log($"Renamed {e.OldName} -> {e.Name}");

        // reader keeps a handle open the whole time (Read, ReadWrite|Delete share)
        using var reader = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
        var beforeLen = reader.Length;

        var tmp = Path.Combine(dir, "A1B2C3D4"); // Excel uses a random 8-character name with no extension
        Make(tmp, 50);
        Log("--- temp written");
        File.Delete(path);
        File.Move(tmp, path);
        Log("--- original deleted, temp renamed");
        Thread.Sleep(500);
        using var d = SpreadsheetDocument.Open(reader, false); // still the old file through the old handle
        var oldRows = d.WorkbookPart!.WorksheetParts.First().Worksheet.Descendants<Row>().Count();
        using var fresh = SpreadsheetDocument.Open(new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite), false);
        var newRows = fresh.WorkbookPart!.WorksheetParts.First().Worksheet.Descendants<Row>().Count();
        foreach (var e in events) Console.WriteLine(e);
        Console.WriteLine($"old handle: length {beforeLen} bytes, {oldRows} rows; reopened by path: {newRows} rows");
    }

    static void Stale(string path)
    {
        using (var d = SpreadsheetDocument.Open(path, true))
        {
            var ws = d.WorkbookPart!.WorksheetParts.First().Worksheet;
            ws.Descendants<Cell>().First(x => x.CellReference == "B2").CellValue = new CellValue(5000);
            d.Save();
        }
        using (var d = SpreadsheetDocument.Open(path, false))
            Console.WriteLine("after writing B2=5000 with the SDK: " + ReadA2(d) + "  (true value 12500)");
        using (var d = SpreadsheetDocument.Open(path, true))
        {
            // Fix 1: drop cached values of formulas; Fix 2: ask Excel to recalculate on load.
            foreach (var c in d.WorkbookPart!.WorksheetParts.First().Worksheet.Descendants<Cell>().Where(c => c.CellFormula != null)) c.CellValue?.Remove();
            var wb = d.WorkbookPart.Workbook;
            wb.CalculationProperties ??= new CalculationProperties();
            wb.CalculationProperties.FullCalculationOnLoad = true;
            d.Save();
        }
        using (var d = SpreadsheetDocument.Open(path, false))
            Console.WriteLine("after clearing <v> and setting fullCalcOnLoad: " + ReadA2(d) + $" fullCalcOnLoad={d.WorkbookPart!.Workbook.CalculationProperties?.FullCalculationOnLoad?.Value}");
    }

    static void Timing(int rows)
    {
        var path = Path.Combine(Path.GetTempPath(), $"timing_{rows}.xlsx");
        Make(path, rows, extraCols: 6); // 10 columns
        Console.WriteLine($"file: {rows} rows x 10 cols, {new FileInfo(path).Length / 1024} KiB");
        Bench("OpenXml DOM (Worksheet.Descendants<Cell>)", () => { using var d = SpreadsheetDocument.Open(path, false); return d.WorkbookPart!.WorksheetParts.First().Worksheet.Descendants<Cell>().Count(); });
        Bench("OpenXml SAX (OpenXmlReader)", () =>
        {
            using var d = SpreadsheetDocument.Open(path, false); int n = 0;
            using var r = OpenXmlReader.Create(d.WorkbookPart!.WorksheetParts.First());
            while (r.Read()) if (r.ElementType == typeof(Cell) && r.IsStartElement) n++;
            return n;
        });
        Bench("ClosedXML (load workbook, enumerate used cells)", () => { using var wb = new XLWorkbook(path); return wb.Worksheet(1).CellsUsed().Count(); });
        Bench("ExcelDataReader (stream rows)", () =>
        {
            using var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            using var r = ExcelReaderFactory.CreateReader(fs); int n = 0;
            while (r.Read()) n += r.FieldCount; return n;
        });
        Bench("MiniExcel (Query, stream rows)", () => MiniExcel.Query(path).Sum(x => ((IDictionary<string, object>)x).Count));
    }

    static void Bench(string name, Func<int> f)
    {
        f(); // warm-up (JIT)
        var times = new List<double>(); int n = 0;
        for (int i = 0; i < 5; i++) { var sw = Stopwatch.StartNew(); n = f(); times.Add(sw.Elapsed.TotalMilliseconds); }
        times.Sort();
        Console.WriteLine($"  {name,-50} median {times[2],7:F0} ms  (min {times[0]:F0}, max {times[4]:F0})  cells={n}");
    }
}
