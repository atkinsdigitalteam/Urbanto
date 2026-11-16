// Layered (OCG) A1 sheet written with PDFsharp 6.2.2 (MIT licence; 6.5.0 is AGPL-3.0-only)
// using only its low-level object API for the layers. Tested on .NET 8 / Linux.
// Project: dotnet new console; dotnet add package PDFsharp --version 6.2.2
// Run:     dotnet run -- out.pdf /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf [srgb.icc]
// If an ICC profile path is given, the file also gets an sRGB output intent and an XMP packet.
// MEASURED (veraPDF 1.30.3, profile 2b): 143 of 144 rules pass. The one failure is clause
// 6.6.4 (no pdfaid identification) because PDFsharp 6.2.2 regenerates the XMP packet on
// Save() and drops the one written below. PDFsharp's own SetPdfA() writes pdfaid:part 1
// (PDF/A-1 forbids layers) and threw "DrawString issued outside of document structure in
// PDF/UA document" here. So: add the PDF/A-2 identification in a post-processing step,
// or use a library with PDF/A-2 output.
using System.Globalization;
using System.Text;
using PdfSharp.Drawing;
using PdfSharp.Fonts;
using PdfSharp.Pdf;
using PdfSharp.Pdf.Advanced;

var outPath = args[0];
GlobalFontSettings.FontResolver = new FileFontResolver(args[1]);
var iccPath = args.Length > 2 ? args[2] : null;

const double MM = 72.0 / 25.4;
var doc = new PdfDocument();
doc.Info.Title = "Layered sheet sample (C15, PDFsharp)";
doc.Info.CreationDate = new DateTime(2026, 10, 30, 12, 0, 0, DateTimeKind.Utc);
var page = doc.AddPage();
page.Width = XUnit.FromMillimeter(841);   // A1 landscape
page.Height = XUnit.FromMillimeter(594);

// 1) Title text through the normal drawing API (embeds a TrueType subset).
using (var gfx = XGraphics.FromPdfPage(page))
{
    var font = new XFont("DejaVu Sans", 10);
    gfx.DrawString("A-06-001 Setting-out plan  1:200 @ A1  EPSG:3997  S3 P01", font,
        XBrushes.Black, new XPoint(600 * MM, 580 * MM - 560 * MM));
}

// 2) Optional content groups (ISO 32000-1, 8.11).
string[] names = { "C-PROP-LINE", "A-WALL", "G-ANNO-NPLT" };
var ocgs = new List<PdfDictionary>();
var props = new PdfDictionary(doc);
for (int i = 0; i < names.Length; i++)
{
    var ocg = new PdfDictionary(doc);
    ocg.Elements.SetName("/Type", "/OCG");
    ocg.Elements.SetString("/Name", names[i]);
    doc.Internals.AddObject(ocg);              // OCGs must be indirect objects
    ocgs.Add(ocg);
    props.Elements.SetReference($"/oc{i}", ocg);
}
page.Resources.Elements["/Properties"] = props;

var ocgArray = new PdfArray(doc);
foreach (var g in ocgs) ocgArray.Elements.Add(g.Reference!);
var off = new PdfArray(doc); off.Elements.Add(ocgs[2].Reference!);
var order = new PdfArray(doc); foreach (var g in ocgs) order.Elements.Add(g.Reference!);
var d = new PdfDictionary(doc);
d.Elements.SetString("/Name", "Default");     // PDF/A-2 clause 6.9 requires a Name
d.Elements["/OFF"] = off;
d.Elements["/Order"] = order;                 // PDF/A-2: Order must list every OCG
var ocProps = new PdfDictionary(doc);
ocProps.Elements["/OCGs"] = ocgArray;
ocProps.Elements["/D"] = d;
doc.Internals.Catalog.Elements["/OCProperties"] = ocProps;

// 3) Geometry in a second content stream, each layer wrapped in /OC /ocN BDC ... EMC.
string F(double v) => v.ToString("0.###", CultureInfo.InvariantCulture);
var sb = new StringBuilder();
void Rect(string tag, double x, double y, double w, double h, double lwMm, string rgb)
{
    sb.Append($"/OC /{tag} BDC q {rgb} RG {F(lwMm * MM)} w ");
    sb.Append($"{F(x * MM)} {F(y * MM)} {F(w * MM)} {F(h * MM)} re S Q EMC\n");
}
Rect("oc0", 120, 180, 200, 150, 0.7, "0.8 0 0");   // plot 40 x 30 m at 1:200
Rect("oc1", 145, 210, 130, 90, 0.5, "0 0 0");      // building 26 x 18 m
Rect("oc2", 100, 160, 240, 190, 0.25, "0 0.6 0");  // construction box, OFF by default
var content = page.Contents.AppendContent();
content.CreateStream(Encoding.ASCII.GetBytes(sb.ToString()));

// 4) Optional PDF/A-2b identification: XMP + sRGB output intent.
if (iccPath != null)
{
    var icc = new PdfDictionary(doc);
    icc.CreateStream(File.ReadAllBytes(iccPath));
    icc.Elements.SetInteger("/N", 3);
    doc.Internals.AddObject(icc);
    var oi = new PdfDictionary(doc);
    oi.Elements.SetName("/Type", "/OutputIntent");
    oi.Elements.SetName("/S", "/GTS_PDFA1");
    oi.Elements.SetString("/OutputConditionIdentifier", "sRGB IEC61966-2.1");
    oi.Elements.SetReference("/DestOutputProfile", icc);
    var ois = new PdfArray(doc); ois.Elements.Add(oi);
    doc.Internals.Catalog.Elements["/OutputIntents"] = ois;

    // XMP with PDF/A identification; values must match the Info dictionary.
    string xmp = $$"""
        <?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
         <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
          <rdf:Description rdf:about=""
            xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
            xmlns:xmp="http://ns.adobe.com/xap/1.0/">
           <pdfaid:part>2</pdfaid:part>
           <pdfaid:conformance>B</pdfaid:conformance>
           <dc:title><rdf:Alt><rdf:li xml:lang="x-default">{{doc.Info.Title}}</rdf:li></rdf:Alt></dc:title>
           <pdf:Producer>{{doc.Info.Producer}}</pdf:Producer>
           <xmp:CreatorTool>{{doc.Info.Creator}}</xmp:CreatorTool>
           <xmp:CreateDate>2026-10-30T12:00:00Z</xmp:CreateDate>
          </rdf:Description>
         </rdf:RDF>
        </x:xmpmeta>
        <?xpacket end="w"?>
        """;
    var meta = new PdfDictionary(doc);
    meta.Elements.SetName("/Type", "/Metadata");
    meta.Elements.SetName("/Subtype", "/XML");
    meta.CreateStream(Encoding.UTF8.GetBytes(xmp));
    doc.Internals.AddObject(meta);
    doc.Internals.Catalog.Elements.SetReference("/Metadata", meta);
    Console.WriteLine($"Info Producer='{doc.Info.Producer}' Creator='{doc.Info.Creator}'");
}

doc.Save(outPath);
Console.WriteLine($"wrote {outPath} ({new FileInfo(outPath).Length} bytes)");

sealed class FileFontResolver(string path) : IFontResolver
{
    public FontResolverInfo ResolveTypeface(string familyName, bool bold, bool italic) => new("DejaVuSans");
    public byte[] GetFont(string faceName) => File.ReadAllBytes(path);
}
