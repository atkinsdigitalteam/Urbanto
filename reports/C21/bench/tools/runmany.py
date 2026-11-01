"""Run a command K times as separate processes; report wall-clock p50/p95 and aggregate
"RESULT | label | <number> us" lines printed by the child. Usage: runmany.py K label -- cmd args..."""
import subprocess, sys, time, re, statistics, math

def pct(v, q):
    s = sorted(v); return s[min(len(s) - 1, math.ceil(q * len(s)) - 1)]

k = int(sys.argv[1]); label = sys.argv[2]; cmd = sys.argv[sys.argv.index('--') + 1:]
walls = []; inner = {}
for i in range(k + 1):                      # first run is a discarded warm-up (file cache)
    t = time.perf_counter()
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    w = (time.perf_counter() - t) * 1000
    if p.returncode != 0:
        print(p.stdout[-2000:]); raise SystemExit(f"exit code {p.returncode}")
    if i == 0: continue
    walls.append(w)
    for m in re.finditer(r"RESULT \| ([^|]+) \| ([0-9.]+) us", p.stdout):
        inner.setdefault(m.group(1).strip(), []).append(float(m.group(2)) / 1000)
print(f"RESULT | {label} wall clock (process start to exit) | n={k} | p50_ms={pct(walls,.5):.1f} | p95_ms={pct(walls,.95):.1f} | min_ms={min(walls):.1f} | mean_ms={statistics.mean(walls):.1f}")
for name, v in inner.items():
    print(f"RESULT | {label} inner: {name} | n={len(v)} | p50_ms={pct(v,.5):.2f} | p95_ms={pct(v,.95):.2f} | min_ms={min(v):.2f}")
