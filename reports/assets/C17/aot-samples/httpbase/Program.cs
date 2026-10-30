using System.Text.Json;
using var http = new HttpClient();
Console.WriteLine("hello");
if (args.Length > 0) {
    var s = await http.GetStringAsync(args[0]);
    using var doc = JsonDocument.Parse(s);
    Console.WriteLine(doc.RootElement.ValueKind);
}
