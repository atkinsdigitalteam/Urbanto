"""Per-capita community-facility land from Dubai Municipality's public facility standards list
(DM-PD-P1-Wi2, issue 2, 2019-07-18, page 1: low-density areas < 70 persons/ha), read from the PDF at
https://dmpmedia.dm.gov.ae/uploads/2021/09/قائمة-المعايير-التخطيطية-للخدمات-العامة.pdf
Columns: level, facility, population served, minimum site area m2, minimum m2 per person, flag
flag: '*' may be inside mixed-use buildings, '**' optional, '^' not required inside development projects."""
ROWS = [
    ("neighbourhood", "daily mosque", 2000, 1800, 0.9, ""),
    ("neighbourhood", "shops", 2000, 400, 0.2, "*"),
    ("neighbourhood", "post-box complex", 2000, 35, 0.0, "^"),
    ("neighbourhood", "public square", 2000, 1500, 0.75, "^"),
    ("neighbourhood", "family square", 2000, 1500, 0.75, "**"),
    ("neighbourhood", "family park", 2000, 4000, 2.0, ""),
    ("residential area", "Friday mosque", 6000, 4500, 0.75, ""),
    ("residential area", "commercial centre", 6000, 6000, 1.0, "*"),
    ("residential area", "nursery", 6000, 600, 0.1, "*"),
    ("residential area", "kindergarten", 6000, 3000, 0.5, ""),
    ("residential area", "primary school", 6000, 8000, 1.3, ""),
    ("residential area", "private general clinic", 6000, 650, 0.11, "*"),
    ("residential area", "private specialist clinic", 6000, 650, 0.11, "*"),
    ("residential area", "private medical centre", 6000, 650, 0.11, "*"),
    ("residential area", "sports fields", 6000, 3500, 0.6, "**"),
    ("residential area", "area park", 6000, 12000, 2.0, ""),
    ("district", "intermediate school", 10000, 9000, 0.9, ""),
    ("district", "secondary school", 20000, 12000, 0.6, ""),
    ("district", "private surgical centre", 15000, 1200, 0.08, "*"),
    ("district", "post office", 20000, 2000, 0.1, "*^"),
    ("district", "government health centre", 30000, 7500, 0.25, ""),
    ("district", "ambulance point", 20000, 1000, 0.05, "*"),
    ("district", "district park", 20000, 20000, 1.0, ""),
    ("sector", "civil defence centre", 50000, 4000, 0.08, ""),
    ("sector", "Eid prayer ground", 70000, 14000, 0.2, "^"),
    ("sector", "public library", 70000, 6000, 0.09, "^"),
    ("sector", "police station", 70000, 5000, 0.07, ""),
    ("sector", "elderly rest house", 50000, 2500, 0.05, ""),
    ("sector", "municipality office", 50000, 1500, 0.03, ""),
    ("sector", "municipality centre", 150000, 4500, 0.03, "^"),
    ("sector", "private hospital", 35000, 5000, 0.14, ""),
    ("sector", "government hospital", 80000, 12000, 0.15, ""),
    ("sector", "sector park", 70000, 500000, 7.0, ""),
]
allr = sum(r[4] for r in ROWS)
req = sum(r[4] for r in ROWS if "^" not in r[5] and "**" not in r[5])
parks = sum(r[4] for r in ROWS if "park" in r[1])
print(f"sum of per-person minima, all rows: {allr:.2f} m2/person")
print(f"excluding optional (**) and not-required-in-projects (^): {req:.2f} m2/person")
print(f"of which parks: {parks:.2f} m2/person")
for dens in (40, 70):
    print(f"at {dens} persons/ha: facility land >= {req*dens:.0f} m2/ha = {req*dens/100:.1f}% of gross land")
