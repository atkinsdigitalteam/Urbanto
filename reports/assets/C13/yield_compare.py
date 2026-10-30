"""C13 worked example: one plot, one building, five rule sets.

Computes GFA, FAR/plot ratio, efficiency, population and parking for a
5,000 m2 mixed-use plot under the rules read for report C13
(Dubai, Abu Dhabi, Saudi Arabia, London, Singapore). Every rule below cites
the source number used in reports/C13-development-yield-and-density-rules.md.

Run:  python3 yield_compare.py            (prints markdown tables)
      python3 yield_compare.py --json out.json

All areas are m2. Component areas are INTERNAL areas (to the inside face of
the external wall); the external wall band is added per rule. This is an
illustrative design, not a real scheme.
"""
import json
import math
import sys
from dataclasses import dataclass, field

PLOT = 5000.0          # m2 (100 m x 50 m)
WALL_T = 0.30          # m, external wall thickness (assumption)
BAY_GROSS = 30.0       # m2 per car bay incl. aisles, ramps, columns (assumption)
# DBC Table B.11 minimum geometry for 90 deg two-way parking, for reference:
BAY_NET_DBC = 2.5 * 5.5 + 2.5 * 6.0 / 2   # = 21.25 m2 (bay + half aisle)


@dataclass
class Comp:
    cat: str            # rule category (see RULES)
    area: float         # internal m2
    use: str = "common"  # res / office / retail / common / parking


@dataclass
class Floor:
    name: str
    level: str          # basement / ground / podium_parking / podium / amenity / tower / mep / roof
    perimeter: float    # external perimeter, m
    comps: list = field(default_factory=list)
    balconies: dict = field(default_factory=dict)  # {"projecting": m2, "recessed": m2}

    @property
    def wall_band(self):
        return self.perimeter * WALL_T - 4 * WALL_T ** 2

    def internal(self, exclude=("void",)):
        return sum(c.area for c in self.comps if c.cat not in exclude)


def C(cat, area, use="common"):
    return Comp(cat, area, use)


# ---------------------------------------------------------------- building
def build():
    floors = []
    for name in ("B2", "B1"):                       # 90 x 50 m basement
        floors.append(Floor(name, "basement", 280, [
            C("parking", 3760, "parking"), C("parking_lobby", 40), C("stairs", 80),
            C("lift_shaft", 40), C("service_shaft", 50), C("plant", 300),
            C("storage", 100, "res"), C("waste_room", 40)]))
    floors.append(Floor("G", "ground", 240, [           # 70 x 50 m podium
        C("retail", 2200, "retail"), C("lobby", 250, "res"), C("lobby", 200, "office"),
        C("loading", 300, "retail"), C("boh", 150, "retail"), C("stairs", 80),
        C("lift_shaft", 40), C("service_shaft", 50), C("statutory_room", 100),
        C("toilets", 50, "retail")]))
    floors.append(Floor("L1", "podium_parking", 240, [
        C("parking", 2900, "parking"), C("parking_lobby", 40), C("stairs", 80),
        C("lift_shaft", 40), C("service_shaft", 50), C("plant", 110),
        C("void", 200)]))                            # void over double-height office lobby
    for name in ("L2", "L3"):
        floors.append(Floor(name, "podium_parking", 240, [
            C("parking", 3100, "parking"), C("parking_lobby", 40), C("stairs", 80),
            C("lift_shaft", 40), C("service_shaft", 50), C("plant", 110)]))
    for name in ("L4", "L5"):
        floors.append(Floor(name, "podium", 240, [
            C("office", 2850, "office"), C("corridor", 100, "office"),
            C("toilets", 150, "office"), C("stairs", 80), C("lift_shaft", 40),
            C("service_shaft", 50), C("plant", 150, "office")]))
    floors.append(Floor("L6", "amenity", 128, [         # enclosure on podium roof
        C("gym", 600, "res"), C("pool_services", 150, "res"), C("corridor", 50, "res"),
        C("stairs", 80), C("lift_shaft", 40), C("service_shaft", 50)]))
    for n in range(7, 37):                            # 40 x 27.5 m tower plate
        if n == 22:
            floors.append(Floor(f"L{n}", "mep", 135, [
                C("mep_floor", 935), C("stairs", 40), C("lift_shaft", 25),
                C("service_shaft", 20), C("lobby", 20), C("refuse_chute", 5),
                C("corridor", 15)]))
        else:
            floors.append(Floor(f"L{n}", "tower", 135, [
                C("apartment", 860, "res"), C("corridor", 80, "res"), C("stairs", 40),
                C("lift_shaft", 25), C("service_shaft", 20), C("lobby", 20, "res"),
                C("refuse_chute", 5), C("elec_cupboard", 10, "res")],
                balconies={"projecting": 80, "recessed": 40}))
    floors.append(Floor("Roof", "roof", 52, [
        C("roof_plant", 150), C("stairs", 20)]))
    return floors


UNIT_MIX = {"studio": (58, 40), "1BR": (116, 65), "2BR": (116, 100), "3BR": (29, 120)}
TOWER_ROOF = 40 * 27.5          # m2, for the Abu Dhabi 25 % rooftop rule
PODIUM_ROOF = 70 * 50           # m2, for the Dubai gym <= 50 % of roof rule
ONCE = {"lift_shaft", "service_shaft", "refuse_chute"}


# ---------------------------------------------------------------- rule sets
# Each rule returns the included fraction (0..1) of a component on a floor.
# "once" handling (count a vertical shaft on one floor only) is done in gfa().

def dubai_dbc(c, f, ctx):
    """DBC 2021 Table A.3 [1]; measured to exterior face of external wall."""
    if f.level == "basement":
        return 0.0          # only habitable/occupiable + sanitary basement space counts
    if c.cat == "lift_shaft":
        return 1.0 if f.name == "G" else 0.0   # recall floor assumed = G
    if c.cat == "gym":
        return 0.0 if c.area <= 0.5 * PODIUM_ROOF else 1.0
    excluded = {"parking", "parking_lobby", "loading", "plant", "mep_floor",
                "roof_plant", "service_shaft", "refuse_chute", "waste_room",
                "statutory_room", "elec_cupboard", "pool_services", "void"}
    if f.level == "mep":
        return 0.0          # MEP plant floor excluded (whole floor, see report)
    if f.level == "roof":
        return 0.0          # elevator machine room / mechanical
    return 0.0 if c.cat in excluded else 1.0


def abu_dhabi(variant):
    """Abu Dhabi Capital Development Code 2022, s.603.02 [8]."""
    def rule(c, f, ctx):
        if f.level == "basement":
            return 0.0      # 'areas below grade are not counted except habitable'
        if f.level == "podium_parking":
            if variant == "N-25":
                return 0.0  # note N-25: podium parking floor not counted
            return 0.0 if c.cat == "void" else 1.0   # A.8 serviced parking structure
        if c.cat in ("statutory_room", "void"):
            return 0.0
        if f.level == "mep":
            return 0.0      # B.8 mechanical floor
        if f.level == "roof":
            share = sum(x.area for x in f.comps) / TOWER_ROOF
            return 0.0 if share <= 0.25 else 1.0     # B.5 / A.9
        return 1.0          # incl. loading at grade, plant/equipment (A.3), gym (A.6)
    return rule


def singapore_ura(c, f, ctx):
    """URA GFA handbook pages [24]-[36], harmonised definition from 1 Jun 2023 [25]."""
    if c.cat in ("parking", "void", "refuse_chute"):
        return 0.0          # parking lots handled via LTA upper bound in gfa()
    if f.level == "basement" and c.cat in ("plant", "waste_room"):
        return 0.0          # M&E / refuse chambers in fully sunken basement car park
    if c.cat == "loading":
        return 0.0          # loading bay on same level as driveway
    return 1.0              # incl. full-height MEP floor, roof plant, lift motor room


def saudi_momrah(c, f, ctx):
    """MOMRAH 2024 residential requirements, 'total building area' [12]."""
    if f.level == "basement":
        return 0.0          # underground car-park floors excluded (whole level, see report)
    if c.cat == "void":
        return 0.0
    return 1.0              # all roofed floor area above ground


def london_gea(c, f, ctx):
    """RICS Code of Measuring Practice 6th ed. GEA [19]; London Plan FAR = GEA/site [17]."""
    return 0.0 if c.cat == "void" else 1.0


RULESETS = {
    "Dubai (DBC)": dict(rule=dubai_dbc, wall=1.0, once=False,
                        balconies={"projecting": 0, "recessed": 0}),
    "Abu Dhabi (N-25 reading)": dict(rule=abu_dhabi("N-25"), wall=1.0, once=True,
                                     balconies={"projecting": 0, "recessed": 1}),
    "Abu Dhabi (A.8 reading)": dict(rule=abu_dhabi("A.8"), wall=1.0, once=True,
                                    balconies={"projecting": 0, "recessed": 1}),
    "Saudi (MOMRAH)": dict(rule=saudi_momrah, wall=1.0, once=False,
                           balconies={"projecting": 1, "recessed": 1}),
    "London (GEA)": dict(rule=london_gea, wall=1.0, once=False,
                         balconies={"projecting": 0, "recessed": 0}),
    "Singapore (URA)": dict(rule=singapore_ura, wall=0.5, once=True,
                            balconies={"projecting": 1, "recessed": 1}),
}


def gfa(floors, rs):
    """Return total GFA, per-use breakdown and balcony area for one rule set.

    rs["once"] True: lift shafts, service shafts and refuse chutes are counted
    once only, on the first (lowest) floor where the rule includes them
    (Abu Dhabi 603.02 A.1 [8]; URA lift shaft / service duct pages [29][30]).
    The external wall band is added in proportion to the included share of
    each floor (full band = exterior face; 0.5 = middle of wall).
    """
    rule, wall_k, balc, once = rs["rule"], rs["wall"], rs["balconies"], rs.get("once")
    seen_once = set()
    total, by_use, balcony_total = 0.0, {}, 0.0
    for f in floors:
        parts = []
        for c in f.comps:
            k = rule(c, f, None)
            if once and c.cat in ONCE and k > 0:
                if c.cat in seen_once:
                    k = 0.0
                else:
                    seen_once.add(c.cat)
            parts.append((c, c.area * k))
        inc_floor = sum(a for _, a in parts)
        interior = f.internal()
        wall = f.wall_band * wall_k * (inc_floor / interior if interior else 0.0)
        for c, a in parts:
            share = a + (wall * a / inc_floor if inc_floor else 0.0)
            by_use[c.use] = by_use.get(c.use, 0.0) + share
        b = sum(f.balconies.get(t, 0) * balc[t] for t in balc)
        balcony_total += b
        by_use["res"] = by_use.get("res", 0.0) + b
        total += inc_floor + wall + b
    return total, by_use, balcony_total


def typical_floor_gfa(floors, rs):
    f = next(x for x in floors if x.level == "tower")
    rule, wall_k, balc = rs["rule"], rs["wall"], rs["balconies"]
    inc = 0.0
    for c in f.comps:
        k = rule(c, f, None)
        if c.cat in ONCE and rs.get("once"):
            k = 0.0     # shafts counted once on a lower floor (AD, SG)
        inc += c.area * k
    wall = f.wall_band * wall_k * inc / f.internal()
    b = sum(f.balconies.get(t, 0) * balc[t] for t in balc)
    return inc + wall + b


def gea_gia(floors):
    gea = sum(f.internal() + f.wall_band for f in floors)
    gia = sum(f.internal() for f in floors)
    balconies = sum(sum(f.balconies.values()) for f in floors)
    return gea, gia, balconies


# ---------------------------------------------------------------- population
def population():
    dbc = {"studio": 1.5, "1BR": 1.8, "2BR": 3, "3BR": 4}       # DBC Table D.5 [1]
    ndss = {"studio": (1, 39), "1BR": (2, 50), "2BR": (4, 70), "3BR": (6, 95)}  # NDSS [18]
    pop_dbc = sum(UNIT_MIX[t][0] * dbc[t] for t in UNIT_MIX)
    bedspaces = sum(UNIT_MIX[t][0] * ndss[t][0] for t in UNIT_MIX)
    ndss_ok = {t: UNIT_MIX[t][1] >= ndss[t][1] for t in UNIT_MIX}
    return pop_dbc, bedspaces, ndss_ok


# ---------------------------------------------------------------- parking
def parking(uses_gfa_ad, office_gia, retail_gia, sg_gfa_use, units):
    n = {t: UNIT_MIX[t][0] for t in UNIT_MIX}
    office_na, retail_na = 5700.0, 2200.0
    out = {}
    # Dubai DBC Table B.13 [1] - minimum, net area basis, rounding up per use (assumption)
    res = n["studio"] * 1 + n["1BR"] * 1 + n["2BR"] * 1 + n["3BR"] * 2
    out["Dubai (DBC)"] = dict(kind="minimum", res=res, office=math.ceil(office_na / 50),
                              retail=math.ceil(retail_na / 70))
    # Abu Dhabi Technical Circular 2009-TIS-0001 [9] - GFA = BUA minus parking
    for zone, r2, r3, off in (("CBD", 1.1, 1.75, 2.4), ("non-CBD", 1.25, 2.0, 2.6)):
        res = n["studio"] + n["1BR"] + n["2BR"] * r2 + n["3BR"] * r3
        out[f"Abu Dhabi ({zone})"] = dict(kind="rate (DoT)", res=math.ceil(res),
                                          office=math.ceil(uses_gfa_ad["office"] * off / 100),
                                          retail=math.ceil(uses_gfa_ad["retail"] * 2.15 / 100))
    # Saudi MOMRAH 2024 [12]: 1.5 per apartment (round up), 1 per 45 m2 shops/offices
    out["Saudi (MOMRAH)"] = dict(kind="minimum", res=math.ceil(units * 1.5),
                                 office=math.ceil(office_na / 45), retail=math.ceil(retail_na / 45))
    # London Plan T6.1-T6.3 [17] - maximums, GIA basis, round down
    out["London (CAZ / PTAL 5-6)"] = dict(kind="maximum", res=0, office=0, retail=0,
                                          note=f"disabled bays >= {math.ceil(0.03 * units)} now, "
                                               f"+{math.ceil(0.07 * units)} later")
    small = n["studio"] + n["1BR"] + n["2BR"]
    out["London (Outer, PTAL 2-3)"] = dict(kind="maximum",
                                           res=math.floor(small * 0.75 + n["3BR"] * 1.0),
                                           office=math.floor(office_gia / 100),
                                           retail=math.floor(retail_gia / 50))
    # Singapore LTA RPPS 2019 Appendix A [40] - range, GFA basis, nearest integer per use
    for zone, (rl, ru, ol, ou, sl, su) in {
            "Zone 2": (1 / 1.25, 1.0, 530, 330, 420, 210),
            "Zone 3": (1 / 1.25, 1.0, 260, 210, 200, 160)}.items():
        lo = round(units * rl) + round(sg_gfa_use["office"] / ol) + round(sg_gfa_use["retail"] / sl)
        hi = round(units * ru) + round(sg_gfa_use["office"] / ou) + round(sg_gfa_use["retail"] / su)
        out[f"Singapore ({zone})"] = dict(kind="range", lower=lo, upper=hi)
    for v in out.values():
        if "res" in v:
            v["total"] = v["res"] + v["office"] + v["retail"]
    return out


# ---------------------------------------------------------------- Dubai DM facilities
DM_HIGH = [  # Dubai Municipality DM-PD-P1-Wi2 (2019), high density > 220 p/ha [4]
    ("Daily mosque", 4000, 0.3), ("Family park", 4000, 0.75), ("Friday mosque", 12000, 0.23),
    ("Kindergarten", 12000, 0.25), ("Primary school", 12000, 0.65),
    ("District park", 12000, 0.7), ("Intermediate school", 20000, 0.42),
    ("Secondary school", 30000, 0.33), ("Government health centre", 30000, 0.22),
    ("Hayy (quarter) park", 30000, 0.4)]


def main():
    floors = build()
    for name, rs in RULESETS.items():
        rs["name"] = name
    gea, gia, balc = gea_gia(floors)
    sla = 24940 + 5700 + 2200   # apartments internal + office NIA + retail NLA
    rows = []
    results = {}
    for name, rs in RULESETS.items():
        total, by_use, b = gfa(floors, rs)
        tf = typical_floor_gfa(floors, rs)
        results[name] = dict(gfa=total, far=total / PLOT, eff=sla / total,
                             typ_floor=tf, typ_eff=860 / tf, by_use=by_use, balconies=b)
    # London GIA based efficiency and IPMS 1 reference
    results["London (GEA)"]["gia"] = gia
    ipms1 = gea + balc

    # Singapore extras: balcony bonus cap and excess parking counted as GFA
    sg = results["Singapore (URA)"]
    sg_res_ex_balc = sg["by_use"]["res"] - sg["balconies"]
    bonus_cap = 0.07 * sg_res_ex_balc
    balcony_in_gpr = max(0.0, sg["balconies"] - bonus_cap)

    # per-use GFA for parking bases
    ad_circ = {}   # Abu Dhabi circular: GFA = BUA - parking; use GEA of use floors
    podium_band = build()[2].wall_band
    ad_circ["office"] = 2 * (3420 + podium_band)
    ground = [f for f in floors if f.name == "G"][0]
    retail_int = sum(c.area for c in ground.comps if c.use == "retail")
    ad_circ["retail"] = retail_int + podium_band * retail_int / ground.internal()
    office_gia, retail_gia = 2 * 3420, retail_int
    units = sum(v[0] for v in UNIT_MIX.values())
    sg_use = {"office": sg["by_use"]["office"], "retail": sg["by_use"]["retail"]}
    park = parking(ad_circ, office_gia, retail_gia, sg_use, units)

    parking_area = sum(c.area for f in floors for c in f.comps if c.cat == "parking")
    bays = math.floor(parking_area / BAY_GROSS)
    sg_upper = park["Singapore (Zone 2)"]["upper"]
    sg_excess_gfa = max(0, bays - sg_upper) * BAY_GROSS

    pop_dbc, bedspaces, ndss_ok = population()

    if "--json" in sys.argv:
        out = dict(results=results, gea=gea, gia=gia, ipms1=ipms1, parking=park,
                   bays=bays, parking_area=parking_area, pop_dbc=pop_dbc,
                   bedspaces=bedspaces, sg_excess_gfa=sg_excess_gfa,
                   sg_balcony_cap=bonus_cap, sg_balcony_in_gpr=balcony_in_gpr)
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as fh:
            json.dump(out, fh, indent=1, default=float)

    # Dubai built-up area (DBC A.5.2.2 [1]): everything constructed incl.
    # balconies, covered parking, basements, service floors; excluding shafts
    # (MEP shafts, refuse chutes 'and similar' - lift shafts treated as shafts).
    shafts = sum(c.area for f in floors for c in f.comps if c.cat in ONCE)
    bua = gea + balc - shafts

    # ------------------------------------------------------------ print
    if "--floors" in sys.argv:
        print("| Floor(s) | Level | Internal components (m2) | Wall band m2 | Balconies m2 |")
        print("|---|---|---|---:|---:|")
        seen = set()
        for f in floors:
            key = (f.level, tuple((c.cat, c.area) for c in f.comps))
            if key in seen:
                continue
            seen.add(key)
            same = [x.name for x in floors if (x.level, tuple((c.cat, c.area) for c in x.comps)) == key]
            label = same[0] if len(same) == 1 else f"{same[0]}-{same[-1]} ({len(same)} floors)"
            comp = ", ".join(f"{c.cat} {c.area:,.0f}" for c in f.comps)
            bal = "+".join(str(v) for v in f.balconies.values()) or "0"
            print(f"| {label} | {f.level} | {comp} | {f.wall_band:.2f} | {bal} |")
        print()
    print("## Inputs")
    print(f"Plot {PLOT:,.0f} m2; {len(floors)} floor records; units {units}; "
          f"GEA {gea:,.1f}; GIA {gia:,.1f}; balconies {balc:,.0f}; "
          f"parking area {parking_area:,.0f} m2 -> {bays} bays at {BAY_GROSS} m2 "
          f"(DBC net geometry {BAY_NET_DBC} m2)")
    print()
    print("| Rule set | GFA m2 | FAR | Efficiency (32,840 / GFA) | Typical tower floor GFA | Typical floor efficiency (860 / floor) |")
    print("|---|---:|---:|---:|---:|---:|")
    for name, r in results.items():
        print(f"| {name} | {r['gfa']:,.0f} | {r['far']:.2f} | {r['eff']:.1%} | "
              f"{r['typ_floor']:,.1f} | {r['typ_eff']:.1%} |")
    print(f"| London GIA (reference) | {gia:,.0f} | {gia/PLOT:.2f} | {sla/gia:.1%} | 1,060.0 | {860/1060:.1%} |")
    print(f"| IPMS 1 (reference) | {ipms1:,.0f} | {ipms1/PLOT:.2f} | {sla/ipms1:.1%} | - | - |")
    print(f"| Dubai built-up area (DBC A.5.2.2, reference) | {bua:,.0f} | {bua/PLOT:.2f} | {sla/bua:.1%} | - | - |")
    print()
    print(f"Singapore: balconies {sg['balconies']:,.0f} m2; 7% bonus cap {bonus_cap:,.0f} m2; "
          f"balcony GFA beyond cap {balcony_in_gpr:,.0f} m2; "
          f"excess parking over Zone 2 upper bound ({sg_upper}) counted as GFA: "
          f"{sg_excess_gfa:,.0f} m2 -> GPR incl. excess "
          f"{(sg['gfa'] + sg_excess_gfa)/PLOT:.2f}")
    print()
    print("| Parking rule set | Type | Residential | Office | Retail | Total | Provided bays | Gap | Note |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for name, p in park.items():
        if p["kind"] == "range":
            print(f"| {name} | range | - | - | - | {p['lower']}-{p['upper']} | {bays} | "
                  f"{bays - p['upper']:+d} over upper bound | |")
        else:
            gap = bays - p["total"]
            print(f"| {name} | {p['kind']} | {p['res']} | {p['office']} | {p['retail']} | "
                  f"{p['total']} | {bays} | {gap:+d} | " + p.get('note', '') + " |")
    print()
    print(f"Population: DBC Table D.5 rates -> {pop_dbc:.1f} persons; "
          f"NDSS bedspaces -> {bedspaces}; NDSS minimum sizes met: {ndss_ok}")
    dens = pop_dbc / (PLOT / 10000)
    print(f"Density {dens:,.0f} persons/ha (plot basis) -> Dubai DM high-density table")
    print("| Facility (Dubai DM, >220 p/ha) | Population threshold | Share of one facility | Land at m2/person |")
    print("|---|---:|---:|---:|")
    for fac, thr, m2p in DM_HIGH:
        print(f"| {fac} | {thr:,} | {pop_dbc/thr:.1%} | {pop_dbc*m2p:,.0f} m2 |")
    w = 0.35 * pop_dbc
    print(f"Abu Dhabi mosque regs with the Dubai population as proxy: worshippers {w:.0f}, "
          f"min GFA {1.8*w:,.0f} m2, parking {math.ceil(w/30)} (1 per 30 worshippers)")
    # Saudi coverage check (65 % ground, 75 % upper floors)
    g_cov = (ground.internal() + ground.wall_band) / PLOT
    print(f"Saudi coverage check: ground {g_cov:.1%} vs 65 % max; podium upper floors {g_cov:.1%} vs 75 % max")
    # Singapore DU check (inference from page text: 85 m2 divisor outside Central Area)
    print(f"Singapore DU check (inferred): residential GFA excl. bonus {sg_res_ex_balc:,.0f} / 85 = "
          f"{sg_res_ex_balc/85:.0f} DU allowed vs {units}")


if __name__ == "__main__":
    main()
