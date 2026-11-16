"""C12: arithmetic sensitivity for accessible bays and landscape on the
120 x 80 m rectangle, 90 deg two-way DBC layout (344 stalls, 22 m2 spare).
Inputs are the quoted values in the report; nothing here is a code value
except where the comment names the clause."""
import math
n = 344
bay = 2.5 * 5.5
# DBC Table C.17 (2 %, min 1, for 25-500), van 10 % of accessible (min 1),
# Table C.18 car 2.5 x 5.5, van 3.35 x 5.5; access aisle >= 1.2 m, may be shared
acc = max(1, math.ceil(0.02 * n)); van = max(1, math.ceil(0.10 * acc)); car = acc - van
w = car * 2.5 + math.ceil(car / 2) * 1.2 + van * 3.35 + 1.2
print("DBC:", acc, "accessible (van", van, ") row width", round(w, 2), "m vs", acc * 2.5,
      "m -> extra", round(w - acc * 2.5, 2), "m =", round((w - acc * 2.5) / 2.5, 2), "bays")
# ADA Table 208.2 (301-400 -> 8), 208.2.4 (1 van per 6 -> 2), 502.2/502.3 widths
acc, van, car = 8, 2, 6
w = car * 2.44 + math.ceil(car / 2) * 1.525 + van * (3.35 + 1.525)
print("ADA:", acc, "bays row width", round(w, 2), "vs", acc * 2.5, "-> extra", round(w - acc * 2.5, 2),
      "m =", round((w - acc * 2.5) / 2.5, 2), "DBC bays")
# KSA UABE 2010 / Riyadh code: 301-500 -> 6 accessible + 4 limited mobility
acc, lm = 6, 4
w = acc * 2.4 + math.ceil(acc / 2) * 2.1 + lm * 2.4 + math.ceil(lm / 2) * 1.2
print("KSA:", acc, "+", lm, "LM row width", round(w, 2), "vs", (acc + lm) * 2.5, "-> extra",
      round(w - (acc + lm) * 2.5, 2), "m =", round((w - (acc + lm) * 2.5) / 2.5, 2),
      "DBC bays (and 6.1 m long, not 5.5 m)")
# Landscape: if islands replace bays one for one (13.75 m2 each)
site = 9600.0
req = 0.10 * site                                   # SUDAS: 10 % of paved area
k = math.ceil(max(0, req - 22) / bay)
print("SUDAS 10 %:", round(req), "m2 ->", k, "bays lost =", round(100 * k / n, 1), "%")
a = 45 * 0.09290304                                 # Portland: 45 ft2 per space
k = math.ceil((a * n - 22) / (bay + a))
print("Portland 45 ft2/space (", round(a, 2), "m2 ) ->", k, "bays lost =", round(100 * k / n, 1), "%")
