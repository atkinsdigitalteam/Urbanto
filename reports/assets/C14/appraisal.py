"""C14 worked development appraisal: a sample Dubai residential tower.

Run:  python3 appraisal.py            (writes outputs/*.md next to this file)

Conventions follow what the report documents for ARGUS Developer-style residual
appraisals and the RICS "Valuation of development property" standard (2019):
  * monthly periods; costs and receipts booked in the month they fall;
  * 100 % debt on land and costs (RICS B1.2.8.3), interest at nominal annual
    rate / 12 on the balance brought forward, credit rate on positive balances;
  * interest compounding period configurable (1 = monthly, 3 = quarterly, as
    decoded from a published ARGUS Developer cash flow, see verify_argus());
  * residual land value (RLV) is the land price that leaves a target profit on
    cost (profit / total costs including finance);
  * project IRR is computed WITHOUT finance (as ARGUS prints "IRR% (without
    Interest)" and as RICS 7.2.4 describes).
All inputs are in AED. Every input carries a note: SOURCE (cited in the report)
or ASSUMPTION (a choice made for the example).
"""
from __future__ import annotations

import datetime as dt
import math
import os
from dataclasses import dataclass, replace

import numpy as np
import numpy_financial as npf
from scipy import optimize, stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT, exist_ok=True)

SQFT_PER_M2 = 10.7639  # 1 m2 = 10.7639 ft2 (exact definition 0.3048 m per ft)


# --------------------------------------------------------------------------
# S-curves: cumulative fraction F(x) of construction cost spent at time fraction x
# --------------------------------------------------------------------------
def s_linear(x):
    return np.clip(x, 0.0, 1.0)


def s_sine(x):
    """Sine-based S-curve: F(x) = (1 - cos(pi x)) / 2."""
    x = np.clip(x, 0.0, 1.0)
    return (1.0 - np.cos(np.pi * x)) / 2.0


def s_beta(x, a=2.0, b=2.0):
    """Beta-CDF S-curve. Beta(2,2) has the closed form F(x) = 3x^2 - 2x^3."""
    return stats.beta.cdf(np.clip(x, 0.0, 1.0), a, b)


def s_dhss(x, C=0.0, K=3.0):
    """DHSS (Hudson 1978) form: y = x + C x^2 - C x - (6x^3 - 9x^2 + 3x) / K.
    With C = 0 and K = 3 it reduces exactly to 3x^2 - 2x^3 (= Beta(2,2) CDF).
    Published C, K values by contract value band were NOT verified in this
    research; the parameters here are illustrative."""
    x = np.clip(x, 0.0, 1.0)
    return x + C * x**2 - C * x - (6 * x**3 - 9 * x**2 + 3 * x) / K


S_CURVES = {
    "straight line": s_linear,
    "sine (1-cos pi x)/2": s_sine,
    "Beta(2,2) = 3x^2-2x^3": s_beta,
    "Beta(2,3) front-loaded": lambda x: s_beta(x, 2.0, 3.0),
    "Beta(3,2) back-loaded": lambda x: s_beta(x, 3.0, 2.0),
    "DHSS C=0, K=3": lambda x: s_dhss(x, 0.0, 3.0),
    "DHSS C=-0.2, K=5": lambda x: s_dhss(x, -0.2, 5.0),
    "DHSS C=+0.2, K=5": lambda x: s_dhss(x, 0.2, 5.0),
}
# DHSS curve is monotone on [0,1] only if K >= 3 and |C| <= 1 - 3/K: F'(x) is a
# concave quadratic, so its minimum on [0,1] is at an end point, where
# F'(0) = 1 - C - 3/K and F'(1) = 1 + C - 3/K.


def spread(total, n, curve):
    """Monthly amounts over n months from a cumulative curve F."""
    edges = curve(np.arange(n + 1) / n)
    return total * np.diff(edges)


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Inputs:
    gfa_m2: float = 30_000.0              # ASSUMPTION: G+30 tower, 30,000 m2 GFA
    efficiency: float = 0.75              # ASSUMPTION: saleable / GFA (AECOM lists 75-80% net:gross for UAE offices)
    price_aed_sqft: float = 1_640.0       # SOURCE: Knight Frank, Dubai avg apartment price Q4 2024, AED 1,640 psf
    build_aed_m2: float = 5_500.0         # SOURCE: Turner & Townsend UAEMI 2025, Dubai apartments high rise, AED 5,500
    contingency: float = 0.05             # ASSUMPTION: 5 % of construction
    fees: float = 0.08                    # ASSUMPTION: 8 % of construction + contingency (UK ARGUS examples use 8-12 %)
    fees_precon_share: float = 0.20       # ASSUMPTION: 20 % of fees in pre-construction, rest follows the S-curve
    marketing: float = 0.03               # ASSUMPTION: 3 % of GDV (as in the Runnymede ARGUS example)
    agent: float = 0.015                  # ASSUMPTION: 1.5 % of GDV (as in the Broxbourne ARGUS example)
    acq_costs: float = 0.04               # ASSUMPTION: 4 % of land price (transfer fee; not verified)
    arrangement_fee: float = 0.01         # ASSUMPTION: 1 % of land + construction + contingency, paid month 0
    eibor_3m: float = 0.0434              # SOURCE: 3-month UAE interbank rate 4.34 % on 30 Oct 2026 (Trading Economics, citing CBUAE)
    margin: float = 0.03                  # ASSUMPTION: lender margin over EIBOR
    credit_rate: float = 0.0              # ASSUMPTION: no interest earned on positive balances
    compounding_months: int = 1           # 1 = monthly, 3 = quarterly
    precon_months: int = 6                # ASSUMPTION
    build_months: int = 30                # ASSUMPTION
    sales_months: int = 6                 # ASSUMPTION: sales receipts after completion
    target_poc: float = 0.20              # ASSUMPTION: target profit on cost 20 %
    curve: str = "Beta(2,2) = 3x^2-2x^3"
    offplan: bool = False                 # True: buyers pay 40 % during construction (illustrative)
    start: dt.date = dt.date(2027, 1, 1)  # ASSUMPTION: appraisal start date

    @property
    def debit_rate(self):
        return self.eibor_3m + self.margin

    @property
    def nsa_m2(self):
        return self.gfa_m2 * self.efficiency

    @property
    def gdv(self):
        return self.nsa_m2 * self.price_aed_sqft * SQFT_PER_M2

    @property
    def construction(self):
        return self.gfa_m2 * self.build_aed_m2

    @property
    def n_months(self):
        return self.precon_months + self.build_months + self.sales_months


BASE = Inputs()


# --------------------------------------------------------------------------
# Cash flow
# --------------------------------------------------------------------------
def cash_flow(p: Inputs, land: float):
    """Return dict of monthly arrays (index 0..T, month 0 = land purchase)."""
    T = p.n_months
    n = T + 1
    z = lambda: np.zeros(n)
    c0 = 1 + p.precon_months              # first construction month index
    c1 = c0 + p.build_months              # one past last construction month
    s0, s1 = c1, c1 + p.sales_months
    curve = S_CURVES[p.curve]

    land_cf, acq, build, cont, fees, mkt, agent, rev, arr = (z() for _ in range(9))
    land_cf[0] = land
    acq[0] = land * p.acq_costs
    build[c0:c1] = spread(p.construction, p.build_months, curve)
    cont[c0:c1] = spread(p.construction * p.contingency, p.build_months, curve)
    fee_total = (p.construction * (1 + p.contingency)) * p.fees
    fees[1:c0] = fee_total * p.fees_precon_share / p.precon_months
    fees[c0:c1] += spread(fee_total * (1 - p.fees_precon_share), p.build_months, curve)
    m0 = max(1, c1 - 12)                  # marketing from 12 months before completion to end of sales
    mkt[m0:s1] = p.gdv * p.marketing / (s1 - m0)
    arr[0] = p.arrangement_fee * (land + p.construction * (1 + p.contingency))
    if p.offplan:
        # Illustrative UAE-style payment plan (ASSUMPTION): 10 % at launch (first
        # construction month), 30 % spread evenly over construction, 60 % on handover
        # spread over the sales months. Escrow release rules are ignored.
        rev[c0] += 0.10 * p.gdv
        rev[c0:c1] += 0.30 * p.gdv / p.build_months
        rev[s0:s1] += 0.60 * p.gdv / p.sales_months
    else:
        rev[s0:s1] = p.gdv / p.sales_months
    agent[:] = rev * p.agent
    costs = land_cf + acq + build + cont + fees + mkt + agent + arr
    return dict(land=land_cf, acq=acq, build=build, cont=cont, fees=fees, mkt=mkt,
                agent=agent, arr=arr, rev=rev, costs=costs, net=rev - costs)


def finance(net, debit, credit, k=1):
    """ARGUS-style finance on a single account.
    Interest for month t = interest-bearing balance brought forward * rate / 12.
    Accrued interest is added to the interest-bearing balance every k months.
    Returns (interest array (positive = cost), closing cumulative balance array)."""
    n = len(net)
    interest = np.zeros(n)
    cum = np.zeros(n)          # cumulative balance including all interest
    ib = 0.0                   # interest-bearing balance (negative = debt)
    accrued = 0.0
    prev_cum = 0.0
    for t in range(n):
        if t > 0:
            rate = debit if ib < 0 else credit
            i_t = ib * rate / 12.0            # negative when debt
            interest[t] = -i_t
            accrued += i_t
        cum[t] = prev_cum + net[t] - interest[t]
        prev_cum = cum[t]
        # update interest-bearing balance for next month
        ib += net[t]
        if (t + 1) % k == 0:
            ib += accrued
            accrued = 0.0
    return interest, cum


def appraise(p: Inputs, land: float):
    cf = cash_flow(p, land)
    interest, cum = finance(cf["net"], p.debit_rate, p.credit_rate, p.compounding_months)
    fin = interest.sum()
    total_costs = cf["costs"].sum() + fin
    profit = cf["rev"].sum() - total_costs
    return dict(cf=cf, interest=interest, cum=cum, finance=fin, total_costs=total_costs,
                profit=profit, poc=profit / total_costs, pogdv=profit / p.gdv,
                peak_debt=-cum.min())


def residual_land(p: Inputs):
    def f(L):
        a = appraise(p, L)
        return a["profit"] - p.target_poc * a["total_costs"]
    return optimize.brentq(f, -p.gdv, p.gdv, xtol=1.0)


# --------------------------------------------------------------------------
# IRR, XIRR, NPV
# --------------------------------------------------------------------------
def month_dates(p: Inputs, n):
    d = []
    y, m = p.start.year, p.start.month
    for i in range(n):
        yy, mm = y + (m - 1 + i) // 12, (m - 1 + i) % 12 + 1
        d.append(dt.date(yy, mm, 1))
    return d


def xirr(values, dates, guess=0.1):
    """Excel-style XIRR: sum P_i / (1+r)^((d_i - d_0)/365) = 0."""
    d0 = dates[0]
    yrs = np.array([(d - d0).days / 365.0 for d in dates])
    f = lambda r: np.sum(values / (1.0 + r) ** yrs)
    return optimize.brentq(f, -0.99, 10.0)


def npv_monthly(values, annual_rate):
    """Discount monthly flows at an effective annual rate; month 0 undiscounted."""
    rm = (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0
    t = np.arange(len(values))
    return float(np.sum(values / (1.0 + rm) ** t))


def all_real_irrs(values):
    """All real IRRs > -100 %: roots g of sum v_t g^(N-t) with g = 1 + r."""
    roots = np.roots(values)
    real = roots[np.abs(roots.imag) < 1e-10].real
    return sorted(g - 1.0 for g in real if g > 0)


# --------------------------------------------------------------------------
# Reporting helpers
# --------------------------------------------------------------------------
def fm(x, d=0):
    return f"{x:,.{d}f}"


def mt(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(text.rstrip() + "\n")
    print(f"\n===== {name} =====\n{text}")


# --------------------------------------------------------------------------
# 0. Decode ARGUS Developer finance convention from a published cash flow
# --------------------------------------------------------------------------
def verify_argus():
    """Figures transcribed from the Broxbourne viability appraisal (ARGUS
    Developer 6.00.008, report date 06/08/2018), phased cash flow page A1:
    costs per month and printed 'Finance Costs (All Sets)', debit 6.50 %."""
    costs = np.array([1_750_298, 0, 0, 0, 10_442, 36_068, 462_806, 391_144, 558_966], float)
    printed_interest = np.array([0, 9_481, 9_481, 9_583, 9_583, 9_640, 9_991, 12_498, 14_617])
    printed_cum = np.array([1_750_298, 1_759_779, 1_769_260, 1_778_843, 1_798_868,
                            1_844_577, 2_317_374, 2_721_017, 3_294_600])
    rows = []
    for k in (1, 3):
        interest, cum = finance(-costs, 0.065, 0.001, k)
        rows.append((f"{k}-monthly", " ".join(fm(v) for v in interest),
                     int(np.max(np.abs(np.round(interest) - printed_interest))),
                     int(np.max(np.abs(np.round(-cum) - printed_cum)))))
    txt = ("Printed ARGUS interest, months 1-9: " + " ".join(fm(v) for v in printed_interest) + "\n\n")
    txt += mt(rows, ["compounding", "model interest months 1-9", "max abs diff vs printed interest",
                     "max abs diff vs printed cumulative"])
    txt += ("\n\nHand check: month 2 interest = 1,750,298 x 6.50 % / 12 = "
            f"{1_750_298 * 0.065 / 12:,.2f} (printed 9,481).")
    # Runnymede ARGUS Developer 8.20.003 summary (07/01/2025): ratios recomputed
    profit, tc, gdv = 999_886, 4_951_814, 5_951_700
    txt += (f"\n\nRunnymede summary check: profit on cost = 999,886 / 4,951,814 = {profit/tc*100:.2f} % "
            f"(printed 20.19 %); profit on GDV = 999,886 / 5,951,700 = {profit/gdv*100:.2f} % (printed 16.80 %). "
            "Total costs include the finance cost, so ARGUS profit on cost is profit / (costs + finance).")
    write("00_argus_decode.md", txt)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    verify_argus()
    p = BASE

    # 1. S-curve table
    xs = np.linspace(0, 1, 11)
    rows = [[f"{x:.1f}"] + [f"{float(S_CURVES[k](x)):.3f}" for k in S_CURVES] for x in xs]
    write("01_s_curves.md", mt(rows, ["time fraction x"] + list(S_CURVES)))

    # 2. Residual land value and base appraisal
    L = residual_land(p)
    a = appraise(p, L)
    cf = a["cf"]
    lines = [
        ("GFA", f"{fm(p.gfa_m2)} m2"),
        ("Saleable area (75 %)", f"{fm(p.nsa_m2)} m2 = {fm(p.nsa_m2 * SQFT_PER_M2)} ft2"),
        ("Sale price", f"AED {fm(p.price_aed_sqft)} per ft2 = AED {fm(p.price_aed_sqft * SQFT_PER_M2)} per m2"),
        ("GDV", f"AED {fm(p.gdv)}"),
        ("Construction (AED 5,500 x GFA)", f"AED {fm(cf['build'].sum())}"),
        ("Contingency 5 %", f"AED {fm(cf['cont'].sum())}"),
        ("Professional fees 8 %", f"AED {fm(cf['fees'].sum())}"),
        ("Marketing 3 % GDV", f"AED {fm(cf['mkt'].sum())}"),
        ("Sales agent 1.5 % GDV", f"AED {fm(cf['agent'].sum())}"),
        ("Arrangement fee 1 %", f"AED {fm(cf['arr'].sum())}"),
        ("Residualised land price", f"AED {fm(L)}"),
        ("Acquisition costs 4 %", f"AED {fm(cf['acq'].sum())}"),
        (f"Finance (debit {p.debit_rate*100:.2f} % nominal, credit 0 %, monthly)", f"AED {fm(a['finance'])}"),
        ("Total costs incl. finance", f"AED {fm(a['total_costs'])}"),
        ("Profit", f"AED {fm(a['profit'])}"),
        ("Profit on cost", f"{a['poc']*100:.2f} %"),
        ("Profit on GDV", f"{a['pogdv']*100:.2f} %"),
        ("Peak debt", f"AED {fm(a['peak_debt'])}"),
        ("Land per m2 GFA", f"AED {fm(L / p.gfa_m2)}  (AED {fm(L / p.gfa_m2 / SQFT_PER_M2)} per ft2 GFA)"),
        ("Land as % of GDV", f"{L / p.gdv * 100:.1f} %"),
    ]
    # project IRR without finance (land included at month 0)
    net = cf["net"]
    r_m = npf.irr(net)
    dates = month_dates(p, len(net))
    r_x = xirr(net, dates)
    lines += [
        ("Project IRR, monthly (periodic)", f"{r_m*100:.4f} % per month"),
        ("  annualised effective (1+r)^12-1", f"{((1+r_m)**12-1)*100:.2f} %"),
        ("  annualised nominal 12 r", f"{r_m*12*100:.2f} %"),
        ("Project XIRR (actual dates, 365-day)", f"{r_x*100:.4f} % (effective from monthly IRR: {((1+r_m)**12-1)*100:.4f} %)"),
    ]
    for dr in (0.10, 0.15, 0.20):
        lines.append((f"Project NPV at {dr*100:.0f} % p.a. effective (no finance)", f"AED {fm(npv_monthly(net, dr))}"))
    # RICS 6.2 DCF residual: land such that NPV (no finance lines) at a target rate = 0
    for dr in (0.15, 0.20):
        def g(Lx, dr=dr):
            c = cash_flow(p, Lx)
            return npv_monthly(c["net"], dr)
        Ld = optimize.brentq(g, -p.gdv, p.gdv, xtol=1.0)
        lines.append((f"DCF residual land value at target IRR {dr*100:.0f} % (no finance, RICS 6.2)", f"AED {fm(Ld)}"))
    write("02_base_appraisal.md", mt(lines, ["item", "value"]))

    # 3. Monthly cash flow (selected months) and hand checks
    c0 = 1 + p.precon_months
    show = [0, 1, 6, c0, c0 + 1, c0 + 14, c0 + 15, c0 + 29, c0 + 30, p.n_months]
    rows = []
    for t in show:
        rows.append([t, dates[t].isoformat()[:7], fm(cf["land"][t] + cf["acq"][t] + cf["arr"][t]),
                     fm(cf["build"][t] + cf["cont"][t]), fm(cf["fees"][t]), fm(cf["mkt"][t] + cf["agent"][t]),
                     fm(cf["rev"][t]), fm(a["interest"][t]), fm(a["cum"][t])])
    txt = mt(rows, ["month", "date", "land+acq+arr fee", "build+contingency", "fees", "marketing+agent",
                    "revenue", "interest", "cumulative balance"])
    F1 = 3 * (1 / 30) ** 2 - 2 * (1 / 30) ** 3
    bc = p.construction * (1 + p.contingency)
    txt += "\n\nHand checks\n\n"
    txt += (f"* S-curve, first construction month: F(1/30) = 3(1/30)^2 - 2(1/30)^3 = {F1:.7f}; "
            f"x AED {fm(bc)} (construction + contingency) = AED {fm(F1 * bc, 2)}; "
            f"model = AED {fm(cf['build'][c0] + cf['cont'][c0], 2)}\n")
    F_mid = (3 * 0.5**2 - 2 * 0.5**3) - (3 * (14 / 30) ** 2 - 2 * (14 / 30) ** 3)
    txt += (f"* S-curve, construction month 15: F(15/30) - F(14/30) = {F_mid:.7f}; x AED {fm(bc)} = "
            f"AED {fm(F_mid * bc, 2)}; model = AED {fm(cf['build'][c0+14] + cf['cont'][c0+14], 2)}\n")
    t = c0 + 1
    hand_i = -a["cum"][t - 1] * p.debit_rate / 12
    txt += (f"* Interest in month {t}: balance b/f AED {fm(-a['cum'][t-1], 2)} x {p.debit_rate*100:.2f} % / 12 = "
            f"AED {fm(hand_i, 2)}; model = AED {fm(a['interest'][t], 2)}\n")
    txt += (f"* Profit on cost: {fm(a['profit'])} / {fm(a['total_costs'])} = {a['profit']/a['total_costs']*100:.4f} %; "
            f"profit on GDV: {fm(a['profit'])} / {fm(p.gdv)} = {a['profit']/p.gdv*100:.4f} %\n")
    write("03_cashflow_and_hand_checks.md", txt)
    # full monthly cash flow as CSV
    keys = ["land", "acq", "arr", "build", "cont", "fees", "mkt", "agent", "rev", "net"]
    with open(os.path.join(OUT, "base_cashflow_monthly.csv"), "w", encoding="utf-8") as fh:
        fh.write("month,date," + ",".join(keys) + ",interest,cumulative_balance\n")
        for t in range(len(net)):
            fh.write(f"{t},{dates[t].isoformat()}," + ",".join(f"{cf[k][t]:.2f}" for k in keys)
                     + f",{a['interest'][t]:.2f},{a['cum'][t]:.2f}\n")

    # 4. Two-way sensitivity: RLV vs sale price and build cost
    steps = [-0.10, -0.05, 0.0, 0.05, 0.10]
    rows = []
    for dc in steps:
        row = [f"build {dc*100:+.0f} % (AED {fm(p.build_aed_m2*(1+dc))}/m2)"]
        for dpz in steps:
            q = replace(p, price_aed_sqft=p.price_aed_sqft * (1 + dpz), build_aed_m2=p.build_aed_m2 * (1 + dc))
            row.append(fm(residual_land(q) / 1e6, 1))
        rows.append(row)
    hdr = ["RLV, AED million"] + [f"price {d*100:+.0f} % ({fm(p.price_aed_sqft*(1+d))} psf)" for d in steps]
    txt = mt(rows, hdr)
    # profit on cost at fixed (base) land price
    rows = []
    for dc in steps:
        row = [f"build {dc*100:+.0f} %"]
        for dpz in steps:
            q = replace(p, price_aed_sqft=p.price_aed_sqft * (1 + dpz), build_aed_m2=p.build_aed_m2 * (1 + dc))
            row.append(f"{appraise(q, L)['poc']*100:.1f} %")
        rows.append(row)
    txt += "\n\nProfit on cost with land fixed at the base RLV\n\n" + mt(rows, ["profit on cost"] + [f"price {d*100:+.0f} %" for d in steps])
    write("04_two_way_sensitivity.md", txt)

    # 5. Tornado (one-way swings of RLV)
    base_rlv = L
    tests = [
        ("Sale price +/-10 %", dict(price_aed_sqft=p.price_aed_sqft * 0.9), dict(price_aed_sqft=p.price_aed_sqft * 1.1)),
        ("Build cost +/-10 %", dict(build_aed_m2=p.build_aed_m2 * 1.1), dict(build_aed_m2=p.build_aed_m2 * 0.9)),
        ("Efficiency 70 % / 80 %", dict(efficiency=0.70), dict(efficiency=0.80)),
        ("Target profit on cost 25 % / 15 %", dict(target_poc=0.25), dict(target_poc=0.15)),
        ("Construction 36 / 24 months", dict(build_months=36), dict(build_months=24)),
        ("Debit rate +2 / -2 points", dict(margin=p.margin + 0.02), dict(margin=p.margin - 0.02)),
        ("Sales period 12 / 3 months", dict(sales_months=12), dict(sales_months=3)),
        ("Fees 10 % / 6 %", dict(fees=0.10), dict(fees=0.06)),
        ("Contingency 10 % / 2.5 %", dict(contingency=0.10), dict(contingency=0.025)),
    ]
    res = []
    for name, lo, hi in tests:
        rl = residual_land(replace(p, **lo))
        rh = residual_land(replace(p, **hi))
        res.append((name, rl, rh, abs(rh - rl)))
    res.sort(key=lambda r: -r[3])
    mx = max(r[3] for r in res)
    rows = [[n, fm((a_ - base_rlv) / 1e6, 1), fm((b_ - base_rlv) / 1e6, 1), fm(s / 1e6, 1),
             "#" * max(1, round(30 * s / mx))] for n, a_, b_, s in res]
    write("05_tornado.md", f"Base RLV AED {fm(base_rlv/1e6,1)} million\n\n" +
          mt(rows, ["input (downside / upside)", "downside change, AED m", "upside change, AED m", "swing, AED m", "bar"]))

    # 6. S-curve and compounding effect on finance and RLV
    rows = []
    for name in S_CURVES:
        q = replace(p, curve=name)
        rl = residual_land(q)
        aa = appraise(q, rl)
        rows.append([name, fm(rl / 1e6, 2), fm(aa["finance"] / 1e6, 2), fm(aa["peak_debt"] / 1e6, 1)])
    for k in (3, 12):
        q = replace(p, compounding_months=k)
        rl = residual_land(q)
        aa = appraise(q, rl)
        rows.append([f"Beta(2,2), compounding every {k} months", fm(rl / 1e6, 2), fm(aa["finance"] / 1e6, 2), fm(aa["peak_debt"] / 1e6, 1)])
    q = replace(p, offplan=True)
    rl = residual_land(q)
    aa = appraise(q, rl)
    rows.append(["Beta(2,2), off-plan payment plan 10/30/60 (illustrative)", fm(rl / 1e6, 2), fm(aa["finance"] / 1e6, 2), fm(aa["peak_debt"] / 1e6, 1)])
    txt = mt(rows, ["case", "RLV, AED m", "finance cost, AED m", "peak debt, AED m"])
    # RICS crude approximations of construction interest (B2.2.2.3) vs cash flow
    fees_total = p.construction * (1 + p.contingency) * p.fees
    build_related = p.construction * (1 + p.contingency) + fees_total
    yrs = p.build_months / 12
    approx_half_costs = build_related / 2 * ((1 + p.debit_rate / 12) ** p.build_months - 1)
    approx_half_time = build_related * ((1 + p.debit_rate / 12) ** (p.build_months / 2) - 1)
    q = replace(p, acq_costs=0.0, arrangement_fee=0.0, marketing=0.0, agent=0.0)
    cfq = cash_flow(q, 0.0)
    only_build = -(cfq["build"] + cfq["cont"] + cfq["fees"])
    i_cf, _ = finance(only_build[: 1 + p.precon_months + p.build_months], p.debit_rate, 0.0, 1)
    txt += ("\n\nInterest on construction-related costs (construction + contingency + fees = AED "
            f"{fm(build_related)}) at {p.debit_rate*100:.2f} %. Cash-flow line: pre-construction fees from month 1, "
            f"interest to practical completion (month {p.precon_months + p.build_months}); approximations: "
            f"{p.build_months}-month construction period:\n\n")
    txt += mt([["Cash flow, Beta(2,2) S-curve, monthly compounding", fm(i_cf.sum())],
               ["RICS approximation 1: half the costs over the whole period", fm(approx_half_costs)],
               ["RICS approximation 2: all the costs over half the period", fm(approx_half_time)]],
              ["method", "interest, AED"])
    write("06_curve_compounding_offplan.md", txt)

    # 7. Benchmark-source sensitivity: RLV using each source's high-rise residential rate
    srcs = [
        ("T&T ICMS 2024, Dubai residential high rise USD 1,334 (secondary)", 1334 * 3.67),
        ("T&T UAEMI Q1 2024, apartments high-rise midpoint (4,410-5,390)", (4410 + 5390) / 2),
        ("T&T UAEMI 2025, Dubai apartments high rise (base)", 5500),
        ("T&T tall buildings 2025, residential 20-60 storeys midpoint, GIA shell & core", (5000 + 6450) / 2),
        ("Currie & Brown Q3 2025, high-rise midpoint (5,750-8,840)", (5750 + 8840) / 2),
        ("Stonehaven 2025, high-rise apartments G+40 midpoint (7,100-9,700)", (7100 + 9700) / 2),
        ("AECOM 2025 handbook (Q3 2024), high-rise midpoint USD 2,100-3,400 x 3.67", (2100 + 3400) / 2 * 3.67),
    ]
    rows = []
    for name, rate in srcs:
        rl = residual_land(replace(p, build_aed_m2=rate))
        rows.append([name, fm(rate), fm(rl / 1e6, 1), f"{rl / p.gdv * 100:.1f} %"])
    write("07_benchmark_source_sensitivity.md", mt(rows, ["cost source", "AED/m2 used", "RLV, AED m", "RLV % of GDV"]))

    # 8. Monte Carlo
    rng = np.random.default_rng(14)
    N = 2000
    pz = rng.triangular(-0.10, 0.0, 0.10, N)
    cz = rng.triangular(-0.05, 0.0, 0.15, N)
    rz = rng.triangular(-0.01, 0.0, 0.02, N)
    bm = rng.integers(27, 37, N)
    out = np.empty(N)
    for i in range(N):
        q = replace(p, price_aed_sqft=p.price_aed_sqft * (1 + pz[i]), build_aed_m2=p.build_aed_m2 * (1 + cz[i]),
                    margin=p.margin + rz[i], build_months=int(bm[i]))
        out[i] = residual_land(q)
    pct = np.percentile(out, [5, 10, 50, 90, 95])
    rows = [["P5", fm(pct[0] / 1e6, 1)], ["P10", fm(pct[1] / 1e6, 1)], ["P50", fm(pct[2] / 1e6, 1)],
            ["P90", fm(pct[3] / 1e6, 1)], ["P95", fm(pct[4] / 1e6, 1)],
            ["Mean", fm(out.mean() / 1e6, 1)], ["Share of runs below deterministic base RLV", f"{(out < base_rlv).mean()*100:.1f} %"]]
    txt = (f"{N} runs, seed 14. Price ~ Triangular(-10 %, 0, +10 %); build cost ~ Triangular(-5 %, 0, +15 %); "
           "debit-rate change ~ Triangular(-1, 0, +2) points; construction months ~ uniform integer 27-36. "
           "Inputs independent (no correlation).\n\n")
    txt += mt(rows, ["RLV statistic", "AED million"])
    hist, edges = np.histogram(out / 1e6, bins=12)
    hrows = [[f"{edges[i]:.0f} to {edges[i+1]:.0f}", int(hist[i]), "#" * max(0, round(40 * hist[i] / hist.max()))] for i in range(len(hist))]
    txt += "\n\nDistribution of RLV (AED million)\n\n" + mt(hrows, ["RLV band", "runs", "bar"])
    write("08_monte_carlo.md", txt)

    # 9. IRR conventions and multiple IRRs
    rows = []
    rows.append(["Monthly IRR of base project cash flow", f"{r_m*100:.4f} %"])
    rows.append(["x 12 (nominal annual)", f"{r_m*12*100:.2f} %"])
    rows.append(["(1+r)^12 - 1 (effective annual)", f"{((1+r_m)**12-1)*100:.4f} %"])
    rows.append(["XIRR on first-of-month dates, 365-day year", f"{r_x*100:.4f} %"])
    # Multiple-IRR example: buyer deposit, construction spend, balance on handover
    v = np.array([30.0, -120.0, 100.0])
    roots = all_real_irrs(v)
    rows.append(["Example flows (years 0,1,2): +30, -120, +100", ""])
    rows.append(["  all real IRRs (np.roots)", ", ".join(f"{r*100:.2f} %" for r in roots)])
    rows.append(["  numpy_financial.irr picks", f"{npf.irr(v)*100:.2f} %"])
    for r in (0.0, 0.10, 0.50, 2.50):
        rows.append([f"  NPV at {r*100:.0f} %", f"{npf.npv(r, v):.2f}"])
    write("09_irr_conventions.md", mt(rows, ["measure", "value"]))


if __name__ == "__main__":
    main()
