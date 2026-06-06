#!/usr/bin/env python3
"""Study A2 — live in-game cross-venue lead-lag analysis (public release).

Implements the locked pre-registration (A2_PREREG.md) §3–§10: the per-game lead
score over lags 1–3, the autocorrelation-preserving circular-shift permutation
null, the 70/30 sealed chronological holdout, the drop-top-N falsification, the
BH-FDR correction, and the P1–P7 decision rule (including the A2-specific P7
both-moved / update-rate-symmetry guard). The STATISTICS are identical to the
script that produced the published result; only the DATA INPUT differs — it is
repointed from the original collection tape to a documented, portable CSV schema.

Input schema (CSV; see sample_data/):
    game_id    grouping key for one game (chronologically sortable; or supply order)
    venue      which venue priced it; this study compares A_VENUE vs B_VENUE
    bin_min    integer 1-minute-bin index within the game (monotonic)
    price      venue's implied home-win probability in [0, 1] at that bin

Lead-lag needs no outcomes. NOT included here, by design: the cross-venue collector
and the entity-resolution layer that aligns each venue's market for the same game —
those are Oddvane's. No real market data is republished; only the method, the
aggregate result, and a synthetic sample.

Run:  python analysis.py [path/to/data.csv]   (defaults to sample_data/sample.csv)
"""
import csv
import math
import os
import random
import sys

# --- locked parameters (identical to the pre-registered run) ---------------
A, B = "kalshi", "polymarket"          # A vs B; pooled S<0 => A leads
LAGS = (1, 2, 3)
NPERM = 2000
SEED = 20260604
SPLIT = 0.70
SETTLED_LO, SETTLED_HI = 0.02, 0.98
MIN_OVERLAP, MIN_DISTINCT, MIN_CHANGED, CHG = 30, 15, 20, 0.005
P1_IN, P1_OUT = 30, 15
P3_FRAC = 0.60
rng = random.Random(SEED)


def corr(xs, ys):
    n = len(xs)
    if n < 10:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / math.sqrt(sxx * syy)


def lead_score(dA, dB, L, shift=0, mask=None):
    """S = sum_k [r(+k) - r(-k)]; shift -> dB; mask restricts anchor bins t."""
    S = 0.0
    for k in LAGS:
        xs = []; ys = []; x2 = []; y2 = []
        for t in range(k, L):
            if mask is not None and not mask[t]:
                continue
            a, b = dA[t], dB[(t - k - shift) % L]
            if a is not None and b is not None:
                xs.append(a); ys.append(b)
            a2, b2 = dA[t - k], dB[(t - shift) % L]
            if a2 is not None and b2 is not None:
                x2.append(a2); y2.append(b2)
        rp, rm = corr(xs, ys), corr(x2, y2)
        S += (rp or 0.0) - (rm or 0.0)
    return S


def perm_p(S_obs, S_perm):
    return (1 + sum(1 for s in S_perm if abs(s) >= abs(S_obs))) / (len(S_perm) + 1)


# --- data (CSV -> per-game first-difference grids) -------------------------
def load(path):
    games = {}
    for r in csv.DictReader(open(path, newline="")):
        if r.get("price") in (None, ""):
            continue
        gid, venue = r["game_id"], r["venue"]
        if venue not in (A, B):
            continue
        games.setdefault(gid, {A: {}, B: {}})[venue][int(r["bin_min"])] = float(r["price"])
    return games


def grids(gid, s):
    aligned = sorted(set(s[A]) & set(s[B]))
    if not aligned:
        return None
    rows = [(b, s[A][b], s[B][b]) for b in aligned]
    while rows:                                          # drop fully-settled tail
        _, ap, bp = rows[-1]
        if (ap <= SETTLED_LO and bp <= SETTLED_LO) or (ap >= SETTLED_HI and bp >= SETTLED_HI):
            rows.pop()
        else:
            break
    if not rows:
        return None
    b0, b1 = rows[0][0], rows[-1][0]; L = b1 - b0 + 1

    def filled(d):
        arr = [None] * L
        for i in range(L):
            b = b0 + i
            if b in d: arr[i] = d[b]
            elif (b - 1) in d: arr[i] = d[b - 1]      # forward-fill <=1 bin
        return arr
    Ag, Bg = filled(s[A]), filled(s[B])
    dA = [None] * L; dB = [None] * L
    for i in range(1, L):
        if Ag[i] is not None and Ag[i-1] is not None: dA[i] = Ag[i] - Ag[i-1]
        if Bg[i] is not None and Bg[i-1] is not None: dB[i] = Bg[i] - Bg[i-1]
    return {"gid": gid, "A": Ag, "B": Bg, "dA": dA, "dB": dB, "L": L}


def qualifies(g):
    L, Ag, Bg, dA, dB = g["L"], g["A"], g["B"], g["dA"], g["dB"]
    both = [i for i in range(L) if Ag[i] is not None and Bg[i] is not None]
    if len(both) < MIN_OVERLAP:
        return False
    for arr, dd in ((Ag, dA), (Bg, dB)):
        if len(set(round(arr[i], 4) for i in both)) < MIN_DISTINCT:
            return False
        if sum(1 for i in range(L) if dd[i] is not None and abs(dd[i]) >= CHG) < MIN_CHANGED:
            return False
    return True


def both_moved_mask(g):
    return [(g["dA"][t] is not None and g["dB"][t] is not None
             and abs(g["dA"][t]) >= CHG and abs(g["dB"][t]) >= CHG) for t in range(g["L"])]


def scenario(games, dB_key="dB", mask_key=None):
    per = []; perm_mat = []
    for g in games:
        dB = g[dB_key]; mask = g[mask_key] if mask_key else None
        S = lead_score(g["dA"], dB, g["L"], mask=mask)
        sp = []
        for _ in range(NPERM):
            sh = rng.randrange(6, g["L"] - 6) if g["L"] > 12 else 1
            sp.append(lead_score(g["dA"], dB, g["L"], shift=sh, mask=mask))
        per.append((g["gid"], S, perm_p(S, sp))); perm_mat.append(sp)
    Sbar = sum(p[1] for p in per) / len(per)
    Sbar_perm = [sum(perm_mat[i][j] for i in range(len(per))) / len(per) for j in range(NPERM)]
    return Sbar, perm_p(Sbar, Sbar_perm), per


def drop_variant(g, N):
    dB = list(g["dB"])
    idx = sorted(((abs(dB[i]), i) for i in range(g["L"]) if dB[i] is not None), reverse=True)
    for _, i in idx[:N]:
        dB[i] = None
    return dB


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sample_data", "sample.csv")
    raw = load(path)
    games = []
    for gid in sorted(raw):
        g = grids(gid, raw[gid])
        if g and qualifies(g):
            games.append(g)
    cut = int(SPLIT * len(games))
    insample, holdout = games[:cut], games[cut:]
    print(f"qualifying games: {len(games)}  (in-sample {len(insample)} / holdout {len(holdout)})", flush=True)

    if len(insample) < P1_IN or len(holdout) < P1_OUT:
        print(f"\n*** VERDICT: INCONCLUSIVE — UNDERPOWERED (P1: in={len(insample)}>={P1_IN}? "
              f"out={len(holdout)}>={P1_OUT}?). NOT a pass, NOT a disproof. ***")
        return

    Sbar, p_in, per_in = scenario(insample)
    Sbar_sign = 1 if Sbar > 0 else -1
    signs_frac = sum(1 for _, S, _ in per_in if (1 if S > 0 else -1) == Sbar_sign) / len(per_in)
    ps = sorted((p_i, gid) for (gid, _S, p_i) in per_in); M = len(ps); surv = []
    for rank, (p_i, gid) in enumerate(ps, 1):
        if p_i <= rank / M * 0.10:
            surv = ps[:rank]
    n_surv = len(surv)

    drops = {}
    for name, N in (("drop5", 5), ("drop10", 10), ("drop1pct", None)):
        for g in insample:
            nN = N if N is not None else max(1, round(0.01 * sum(1 for i in range(g["L"]) if g["dB"][i] is not None)))
            g["_drop"] = drop_variant(g, nN)
        drops[name] = scenario(insample, dB_key="_drop")

    for g in insample:
        g["_bm"] = both_moved_mask(g)
    Sbm, p_bm, _ = scenario(insample, mask_key="_bm")
    num = {A: 0, B: 0}; den = 0
    for g in insample:
        for i in range(g["L"]):
            if g["A"][i] is not None and g["B"][i] is not None:
                den += 1
                if g["dA"][i] is not None and abs(g["dA"][i]) >= CHG: num[A] += 1
                if g["dB"][i] is not None and abs(g["dB"][i]) >= CHG: num[B] += 1
    rate_K = num[A] / den if den else 0; rate_P = num[B] / den if den else 0
    R = max(rate_K, rate_P) / min(rate_K, rate_P) if min(rate_K, rate_P) > 0 else float("inf")

    Soos, p_oos, _ = scenario(holdout)

    P1 = True
    P2 = p_in < 0.05
    P3 = signs_frac >= P3_FRAC
    P4 = (n_surv >= 1) and P2
    P5 = ((1 if Soos > 0 else -1) == Sbar_sign) and (p_oos < 0.05)
    P6 = True; p6rows = {}
    for name in ("drop5", "drop10", "drop1pct"):
        Sd, pd, _ = drops[name]
        ok = ((1 if Sd > 0 else -1) == Sbar_sign) and (abs(Sd) / abs(Sbar) if Sbar else 0) >= 0.5 and pd < 0.05
        p6rows[name] = (Sd, pd, abs(Sd) / abs(Sbar) if Sbar else 0, ok)
        if not ok: P6 = False
    P7a = ((1 if Sbm > 0 else -1) == Sbar_sign) and (p_bm < 0.05)
    P7 = P7a and (R <= 2.00)

    leader = "Polymarket" if Sbar_sign > 0 else "Kalshi"
    checks = {"P1": P1, "P2": P2, "P3": P3, "P4": P4, "P5": P5, "P6": P6, "P7": P7}
    verdict = (f"ROBUST LEAD — {leader} leads" if all(checks.values())
               else "NO ROBUST LEAD — failed " + ", ".join(k for k, v in checks.items() if not v))

    print(f"\nin-sample S̄={Sbar:+.4f} (sign ⇒ {leader} leads)  pooled p={p_in:.4f}")
    print(f"sign-consistency: {100*signs_frac:.0f}%   BH-FDR survivors: {n_surv}/{M}")
    print("\nGATE TABLE (P1-P7):")
    print(f"  P1 power            in={len(insample)}(≥30) out={len(holdout)}(≥15)   {'PASS' if P1 else 'FAIL'}")
    print(f"  P2 in-sample sig    p={p_in:.4f} (<0.05)                {'PASS' if P2 else 'FAIL'}")
    print(f"  P3 sign-consistency {100*signs_frac:.0f}% (≥60%)                   {'PASS' if P3 else 'FAIL'}")
    print(f"  P4 BH-FDR q=0.10    {n_surv} survive (≥1) & P2            {'PASS' if P4 else 'FAIL'}")
    print(f"  P5 out-of-sample    S̄_oos={Soos:+.4f} p={p_oos:.4f}        {'PASS' if P5 else 'FAIL'}")
    print(f"  P6 drop-top-N       (rows below)                 {'PASS' if P6 else 'FAIL'}")
    print(f"  P7 update-asymmetry R={R:.3f} (≤2.00) & both-moved {'PASS' if P7 else 'FAIL'}")
    print("\nDROP-TOP-N (P6) — fraction of lead score left after dropping biggest |ΔB| bins:")
    print(f"  full       S̄={Sbar:+.4f}  ratio 1.00")
    for name in ("drop5", "drop10", "drop1pct"):
        Sd, pd, ratio, ok = p6rows[name]
        print(f"  {name:9s} S̄={Sd:+.4f}  |S̄|/|full|={ratio:.2f}  p={pd:.4f}  {'keep' if ok else 'FAIL'}")
    print(f"\nP7: both-moved S̄={Sbm:+.4f} p={p_bm:.4f} ({'PASS' if P7a else 'FAIL'}); "
          f"update rates {A}={rate_K:.3f} {B}={rate_P:.3f} R={R:.3f} (FAIL if R>2.00)")
    print(f"\nHOLDOUT: S̄_oos={Soos:+.4f} p={p_oos:.4f} -> "
          f"{'replicates in-sample sign' if (1 if Soos>0 else -1)==Sbar_sign else 'OPPOSITE sign to in-sample'}")
    print("\n" + "=" * 68)
    print(f"VERDICT: {verdict}")
    print("=" * 68)


if __name__ == "__main__":
    main()
