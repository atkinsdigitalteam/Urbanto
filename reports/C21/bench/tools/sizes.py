"""Measure install sizes on disk (apparent size, bytes; MiB = 1024*1024 B). Usage: sizes.py <R21M folder>"""
import os, sys, glob
R = sys.argv[1]
def size(p, skip=lambda d: False):
    if os.path.isfile(p): return os.path.getsize(p)
    t = 0
    for root, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if not skip(os.path.join(root, d))]
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp): t += os.path.getsize(fp)
    return t
def out(label, b, note=""):
    print(f"RESULT | size | {label} | {b} B | {b/1048576:.1f} MiB | {note}")

# --- Python runtime on this Linux VM (Ubuntu 24.04 deadsnakes-style packages, Python 3.13.17)
lib = "/usr/lib/x86_64-linux-gnu/libpython3.13.so.1.0"
std = "/usr/lib/python3.13"
out("libpython3.13.so.1.0", size(lib))
out("stdlib /usr/lib/python3.13 (all, incl. __pycache__ and lib-dynload)", size(std))
out("  of which __pycache__ dirs", sum(size(d) for d in glob.glob(std + "/**/__pycache__", recursive=True)))
out("  of which lib-dynload (C extension modules)", size(std + "/lib-dynload"))
for d in ("test", "idlelib", "tkinter", "turtledemo", "ensurepip", "pydoc_data", "config-3.13-x86_64-linux-gnu", "lib2to3"):
    if os.path.exists(os.path.join(std, d)): out(f"  of which {d}/", size(os.path.join(std, d)))
drop = {"test", "idlelib", "tkinter", "turtledemo", "ensurepip", "pydoc_data", "config-3.13-x86_64-linux-gnu", "__pycache__", "site-packages", "dist-packages"}
trim = size(std, skip=lambda d: os.path.basename(d) in drop)
out("stdlib trimmed (no tests, idle, tkinter, ensurepip, pydoc_data, config/static lib, __pycache__)", trim)
out("libpython + trimmed stdlib (embedding set, Linux)", trim + size(lib))
out("numpy 2.x installed here (/usr/local/lib/python3.13/dist-packages/numpy + numpy.libs)", size("/usr/local/lib/python3.13/dist-packages/numpy") + size("/usr/local/lib/python3.13/dist-packages/numpy.libs"))
out("msgpack 1.2.4 (pip --target)", size(R + "/pylib"))

# --- python.org Windows embeddable package 3.13.17 (downloaded, sha256 checked)
z = R + "/downloads/pyembed31317/zip/python-3.13.17-embed-amd64.zip"
out("python-3.13.17-embed-amd64.zip (download)", size(z))
out("python-3.13.17-embed-amd64 extracted", size(R + "/downloads/pyembed31317/x"))

# --- Roslyn packages (NuGet cache)
N = R + "/nuget"
for pkg in ("microsoft.codeanalysis.common", "microsoft.codeanalysis.csharp", "microsoft.codeanalysis.scripting.common", "microsoft.codeanalysis.csharp.scripting"):
    for nup in glob.glob(f"{N}/{pkg}/5.9.0/*.nupkg"):
        out(f"nupkg {os.path.basename(nup)}", size(nup))
P = R + "/artifacts/publish/p5a_roslyn_jit/release_linux-x64"
dlls = [f for f in glob.glob(P + "/Microsoft.CodeAnalysis*.dll")]
out("Roslyn scripting DLLs as deployed (4 DLLs, IL only)", sum(size(f) for f in dlls))
sat = [d for d in os.listdir(P) if os.path.isdir(os.path.join(P, d))]
out(f"Roslyn satellite resource folders ({len(sat)} languages)", sum(size(os.path.join(P, d)) for d in sat))
out("Roslyn scripting DLLs ReadyToRun (crossgen) as deployed", sum(size(f) for f in glob.glob(R + "/artifacts/p5a_r2r/Microsoft.CodeAnalysis*.dll")))

# --- .NET runtime and helper deployments
rt = glob.glob(R + "/dotnet10/shared/Microsoft.NETCore.App/*")[0]
out(f"shared .NET runtime Microsoft.NETCore.App {os.path.basename(rt)} (linux-x64, needed by framework-dependent helper)", size(rt) + size(R + "/dotnet10/host"))
for n in ("p5c_helper",):
    out("helper framework-dependent linux-x64 (helper + Roslyn compiler DLLs, en only)", size(R + "/artifacts/publish/p5c_helper/release_linux-x64"))
for d in sorted(glob.glob(R + "/artifacts/sizes/*")):
    out(f"helper publish {os.path.basename(d)}", size(d))
rp = glob.glob(N + "/microsoft.netcore.app.runtime.win-x64/*")
for d in rp: out(f"win-x64 runtime pack (NuGet cache folder) {os.path.basename(d)}", size(d), "includes .nupkg and extracted files")

# --- AOT host binaries
for proj in ("p1_cpython_aot", "p2_pipe", "p3_csnakes", "p4_pythonnet", "p5b_roslyn_aot", "p5c_host"):
    for f in glob.glob(f"{R}/artifacts/publish/{proj}/release_linux-x64/{proj}"):
        out(f"Native AOT executable {proj} (linux-x64, stripped .dbg kept separately)", size(f))
