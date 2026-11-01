// A small "user script" as a Studio user might write it in a C# script node: transform points in place.
// The variant number changes a constant so every compile is a fresh, uncached compile.
public static class UserScripts
{
    public static string Body(int variant) => $$"""
        const double C = 0.8660254037844387, S = 0.5;
        double tx = 10.0 + {{variant}} * 0.0, ty = -3.0;
        for (int i = 0; i < P.Length; i += 2)
        {
            double x = P[i], y = P[i + 1];
            P[i] = C * x - S * y + tx;
            P[i + 1] = S * x + C * y + ty;
        }
        """;

    // Same body wrapped as a class for CSharpCompilation (non-scripting) use.
    public static string AsClass(int variant) => $$"""
        using System;
        public static class UserScript
        {
            public static void Run(double[] P)
            {
        {{Body(variant)}}
            }
        }
        """;
}

public class ScriptGlobals { public double[] P = System.Array.Empty<double>(); }
