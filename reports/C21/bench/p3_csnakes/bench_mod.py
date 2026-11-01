C, S, TX, TY = 0.8660254037844387, 0.5, 10.0, -3.0

def noop() -> None:
    return None

def transform_tuples(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(C*x - S*y + TX, S*x + C*y + TY) for (x, y) in pts]

def transform_flat(v: list[float]) -> list[float]:
    xs = v[0::2]; ys = v[1::2]
    out = [0.0] * len(v)
    out[0::2] = [C*x - S*y + TX for x, y in zip(xs, ys)]
    out[1::2] = [S*x + C*y + TY for x, y in zip(xs, ys)]
    return out

def transform_bytes(b: bytes) -> bytes:
    # b: little-endian float64 pairs; pure Python transform, returns bytes of the same layout
    from array import array
    a = array('d'); a.frombytes(b)
    return array('d', transform_flat(a.tolist())).tobytes()

