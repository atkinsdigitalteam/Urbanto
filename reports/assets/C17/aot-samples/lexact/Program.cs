using Cryptlex;
try { LexActivator.SetProductData("dummy"); } catch (Exception e) { Console.WriteLine("expected error: " + e.GetType().Name + " " + e.Message); }
