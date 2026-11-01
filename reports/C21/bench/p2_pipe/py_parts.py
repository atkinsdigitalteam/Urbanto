"""Time the Python-side pieces of benchmark 2 in isolation (no pipe): transform, decode, encode.
Usage: python3 -I py_parts.py <pylib dir>"""
import sys, json, random, timeit, statistics
from array import array
sys.path.insert(0, sys.argv[1])
import msgpack
C, S, TX, TY = 0.8660254037844387, 0.5, 10.0, -3.0
def transform_flat(v):
    xs = v[0::2]; ys = v[1::2]
    out = [0.0] * len(v)
    out[0::2] = [C*x - S*y + TX for x, y in zip(xs, ys)]
    out[1::2] = [S*x + C*y + TY for x, y in zip(xs, ys)]
    return out
for n in (10_000, 100_000):
    v = [random.uniform(-500, 500) for _ in range(2 * n)]
    js = json.dumps({"op": "t", "pts": v}).encode()
    raw = array("d", v).tobytes()
    mp = msgpack.packb({"op": "t", "pts": v})
    reps = 50 if n == 10_000 else 10
    def t(f):
        r = timeit.repeat(f, number=1, repeat=reps)
        return f"p50_ms={statistics.median(r)*1000:.2f}"
    print(f"RESULT | py_parts N={n} transform_flat (pure Python list comprehension) | {t(lambda: transform_flat(v))}")
    print(f"RESULT | py_parts N={n} json.loads + json.dumps | {t(lambda: json.dumps(json.loads(js)))}")
    print(f"RESULT | py_parts N={n} array('d').frombytes + tolist + array(list).tobytes | {t(lambda: array('d', (lambda a: (a.frombytes(raw), a)[1])(array('d')).tolist()).tobytes())}")
    print(f"RESULT | py_parts N={n} msgpack.unpackb + packb | {t(lambda: msgpack.packb(msgpack.unpackb(mp)))}")
