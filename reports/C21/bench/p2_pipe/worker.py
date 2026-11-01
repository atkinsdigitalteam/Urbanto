"""Python side of benchmark 2: a child process that answers requests on stdin/stdout.
Usage: python3 -I worker.py <json|bin|msgpack|binnp> [extra sys.path entry]
json:    one UTF-8 JSON object per line, flat list of floats [x0, y0, x1, y1, ...]
bin:     frame = <u32 little-endian length><u8 op><float64 little-endian array>, decoded with array('d')
msgpack: frame = <u32 little-endian length><msgpack map {"op": str, "pts": [float64...]}>
binnp:   like bin, but the transform is done with numpy instead of a Python loop"""
import sys, struct
from array import array

mode = sys.argv[1]
if len(sys.argv) > 2:
    sys.path.insert(0, sys.argv[2])

C, S, TX, TY = 0.8660254037844387, 0.5, 10.0, -3.0

def transform_flat(v):
    xs = v[0::2]; ys = v[1::2]
    out = [0.0] * len(v)
    out[0::2] = [C*x - S*y + TX for x, y in zip(xs, ys)]
    out[1::2] = [S*x + C*y + TY for x, y in zip(xs, ys)]
    return out

inp = sys.stdin.buffer
outp = sys.stdout.buffer

if mode == "json":
    import json
    while True:
        line = inp.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg["op"] == "noop":
            reply = '{"ok":true}'
        else:
            reply = json.dumps({"pts": transform_flat(msg["pts"])}, separators=(",", ":"))
        outp.write(reply.encode("utf-8") + b"\n")
        outp.flush()
else:
    if mode == "msgpack":
        import msgpack
    if mode == "binnp":
        import numpy as np
        R = np.array([[C, -S], [S, C]]); T = np.array([TX, TY])
    hdr = struct.Struct("<I")
    while True:
        h = inp.read(4)
        if len(h) < 4:
            break
        (n,) = hdr.unpack(h)
        payload = inp.read(n)
        if mode == "msgpack":
            msg = msgpack.unpackb(payload)
            if msg["op"] == "noop":
                body = msgpack.packb({"ok": True})
            else:
                body = msgpack.packb({"pts": transform_flat(msg["pts"])})
        else:
            op = payload[0]
            if op == 0:
                body = b"\x00"
            elif mode == "bin":
                a = array("d"); a.frombytes(memoryview(payload)[1:])
                body = b"\x01" + array("d", transform_flat(a.tolist())).tobytes()
            else:
                a = np.frombuffer(payload, dtype=np.float64, offset=1).reshape(-1, 2)
                body = b"\x01" + (a @ R.T + T).tobytes()
        outp.write(hdr.pack(len(body)) + body)
        outp.flush()
