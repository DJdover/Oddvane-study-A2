# A2 — PRE-REGISTRATION: Live in-game cross-venue lead-lag (MLB)

**Status: LOCKED. The full season tape has NOT been pulled or examined. This file
is hashed (`A2_PREREG.sha256`) and the hash is to be timestamped publicly BEFORE
any tape pull, so the criteria provably predate the data. After approval the
analysis runs EXACTLY ONCE; the verdict is reported as-is — including "no robust
lead" or "inconclusive."** A2 is a NEW study; A's null stays banked and untouched.

---

## 0. Prior-exposure / contamination disclosure

To build and validate the collector and to settle the price-definition question,
I examined **one game** — the probe game **SF @ Milwaukee, 2026-06-04** — at the
level of price *semantics* and series alignment. **I computed NO lead-lag
statistic on it.** To remove any doubt, **that game is EXCLUDED** from both the
in-sample and out-of-sample sets. No other game has been examined.

---

## 1. Question and hypotheses

On a single **live MLB game** priced on **Kalshi (A)** and **Polymarket (B)**,
do one venue's short-horizon (1–3 min) **last-trade** price changes lead the
other's, **beyond the shared-news co-movement** of both venues watching the same
game?

- **H0:** No lead — the directional lead score S (§5) is 0 in expectation.
- **H1 (two-sided):** One venue leads — pooled S is reliably non-zero and robust
  under all checks in §10.

Internal-only research (Kalshi never republished). Manifold excluded (play-money).

---

## 2. Data and universe (LOCKED)

- **Venues:** Kalshi + Polymarket, **keyless public** market data only.
- **Outcome:** **home-team win probability** per game.
- **Price definition (LOCKED — the apples-to-apples decision):** **last-trade,
  forward-filled ≤1 bin to the 1-minute grid, on BOTH venues.** Kalshi:
  candlesticks `price.close_dollars` (carry `previous_dollars` when no trade in a
  minute). Polymarket: `prices-history` `p` (its single trade-based series).
  **Midpoint was rejected:** Polymarket exposes no *historical* midpoint (live
  only), so a mid-vs-trade mix across venues was impossible to avoid and would
  itself fake/hide a lead. Last-trade is the one definition constructible
  symmetrically from both history endpoints.
- **Games:** all MLB regular-season games from the 2026 season opening through
  the pull date, discovered via **MLB StatsAPI** schedule (`detailedState`,
  teams, start/end), that carry a game-winner market on **both** venues.
  **EXCLUDE** the plumbing game (SF@MIL 2026-06-04).
- **In-game window:** first pitch → final (per StatsAPI). Drop the fully-settled
  tail (consecutive end-of-game bins where BOTH venues are ≤0.02 or ≥0.98).
- **Qualifying filter (selection uses only coverage/liquidity, never the lead) —
  computed on the IN-SAMPLE portion:** a game qualifies iff
  1. present on both venues with **≥30** overlapping in-game 1-min bins;
  2. **LIQUIDITY floor (proxied by activity, NOT reported volume — which was
     null/unreliable in the probe):** each venue shows **≥15 distinct prices**
     AND **≥20 bins with a ≥0.5¢ change** in-game (the market actually traded/
     moved); and
  3. **spread sanity (where available):** Kalshi median in-game
     (`yes_ask−yes_bid`) **≤ 0.05** (wide spread ⇒ thin ⇒ flag & exclude).
     Polymarket has no historical spread → rely on (2). Thin games are flagged
     and excluded, not silently kept.

---

## 3. Preprocessing (LOCKED)

1-minute bins; last-trade forward-filled ≤1 bin per §2; first differences
Δp_t = p_t − p_{t−1} per venue per game; pairwise-complete alignment (a lag pair
counts only if both referenced bins exist on both venues).

## 4. Lags (LOCKED)
k ∈ {1, 2, 3} bins (= 1, 2, 3 min). Primary statistic aggregates k=1..3; per-lag
values are descriptive only. No wide-grid lag scan.

## 5. Primary metric (LOCKED)
Pearson corr of first differences, pairwise-complete. A=Kalshi, B=Polymarket:
- `r(+k)=corr(ΔA_t, ΔB_{t−k})` → Polymarket leads;
- `r(−k)=corr(ΔA_{t−k}, ΔB_t)` → Kalshi leads.
**Per-game** `S_i = Σ_{k=1}^{3}[r_i(+k) − r_i(−k)]` (S<0 ⇒ Kalshi leads game i).
**Pooled** `S̄ = mean_i(S_i)` over qualifying games, **equal-weight** (so one game
can't carry the result).

## 6. Significance / null (LOCKED)
Autocorrelation-preserving **circular-shift permutation**: per game, circularly
shift ΔB by a uniform offset in [6, n−6], recompute S_i. **2000 perms, seed
20260604.** Per-game two-sided `p_i=(1+#{|S_perm|≥|S_obs|})/2001`; pooled
likewise on the averaged S̄.

## 7. Out-of-sample SEALED holdout (LOCKED)
Because the whole season is retrievable at once, the holdout is sealed by
*construction + commitment*: qualifying games are split **chronologically** —
in-sample = earliest **70%** by game date, holdout = latest **30%**. Qualification,
all threshold application, the discovery test, AND the §10 guards run on
**in-sample only**; the holdout is loaded and scored in the **single final
confirmatory step** and never before. The timestamped hash is the proof this
split + these criteria predate any data examination.

## 8. Drop-top-N falsification (LOCKED)
Per game, drop the bins with the largest **|ΔB_t|** (Polymarket move) — **N=5,
N=10, and top-1%** — recompute S_i and pooled S̄. A lead that lives in a few big
plays is an artifact.

## 9. Multiple-comparisons correction (LOCKED)
Across qualifying games' per-game p_i, **Benjamini–Hochberg FDR at q=0.10**.
Report family size and survivors.

## 10. PASS / FAIL decision rule (LOCKED — ALL must hold)
- **P1 power:** ≥ **30** qualifying in-sample games (and ≥ **15** in the holdout).
- **P2 in-sample sig:** pooled `p` < 0.05.
- **P3 sign consistency:** ≥ **60%** of qualifying games share the sign of S̄.
- **P4 multiple-comparisons:** ≥ **1** game survives BH-FDR q=0.10 AND P2.
- **P5 out-of-sample:** holdout S̄ same sign as in-sample AND holdout `p` < 0.05.
- **P6 drop-top-N:** for all three drops — sign kept, `|S̄_drop| ≥ 0.5·|S̄_full|`,
  pooled `p` < 0.05.
- **P7 shared-news / update-asymmetry guard (A2-specific) — FULLY NUMERIC, both
  sub-conditions required to PASS:**
  - **(a) Both-moved survival.** Define the *both-moved subset* as anchor bins t
    with |ΔA_t| ≥ 0.005 AND |ΔB_t| ≥ 0.005 (both venues moved ≥0.5¢ in bin t).
    Recompute the pooled lead score S̄ using only those anchor bins (in-sample);
    require **same sign** as the full in-sample S̄ **and** permutation **p < 0.05**.
  - **(b) Update-rate symmetry (hard number).** For each venue v, define
    `rate_v = (# in-sample in-game aligned bins with |Δp_v| ≥ 0.005) / (# in-sample
    in-game aligned bins)`. Let `R = max(rate_K, rate_P) / min(rate_K, rate_P)`.
    **P7 FAILS if R > 2.00.** (One venue updating >2× as often ⇒ the lead is
    treated as an update-mechanism artifact, not information.)
  - **P7 PASSES iff (a) holds AND R ≤ 2.00.** Otherwise P7 FAILS. This is the
    guard against "continuous-vs-staircase fakes a lead" and "same play, one venue
    ticks first." `R` and both rates are reported regardless of outcome.

**Verdict (locked):** **ROBUST LEAD** only if P1–P7 all hold (name the venue);
**NO ROBUST LEAD** if P1 holds but any of P2–P7 fails (state which, incl. if it
died on drop-top-N or the update-asymmetry guard); **INCONCLUSIVE —
UNDERPOWERED** if P1 fails.

## 11. Anti-tuning commitments
Runs **exactly once**. No criterion in §1–§10 edited after results. Equal-weight
pooling, two-sided test, drop-top-N, and the P7 guard are chosen so a result from
one game, a few big plays, or update-mechanism asymmetry cannot pass. Reporting
faithful regardless of outcome; the plumbing game is excluded.

## 12. Known limitation (stated up front, not a loophole)
Even a surviving lead is a **last-trade** lead: it reflects which venue's traders
*trade* first, which is related to but not identical to which venue is *informed*
first. A book/quote-level test (order-book mid, sub-minute) would be a stronger
instrument but requires live collection (deferred). A2's claim is therefore
deliberately narrow: a last-trade, 1-minute-resolution lead surviving all guards.

## Deviations log
(none yet)
