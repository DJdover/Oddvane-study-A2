# Study A2 — RESULTS: live in-game cross-venue lead-lag (MLB)

**Ran once on 2026-06-05 against the LOCKED, OTS-stamped `A2_PREREG.md`
(SHA-256 `61fc5784…0796788d`, verified UNCHANGED post-run; stamped 2026-06-04
before the tape was pulled). Tape read-only; one run; no bets. Numbers only.**

## VERDICT (per §10 decision rule): NO ROBUST LEAD — failed P2, P3, P4, P5, P6, P7

Qualifying games: **871** (in-sample **609** / holdout **262**).
In-sample pooled lead score **S̄ = −0.0028** (sign ⇒ Kalshi) · pooled **p = 0.6762**
· sign-consistency **39%** · BH-FDR survivors **27/609**.

## Gate table (P1–P7)
| gate | number | result |
|---|---|---|
| P1 power | in 609 (≥30), out 262 (≥15) | PASS |
| P2 in-sample sig | p = 0.6762 (<0.05) | FAIL |
| P3 sign-consistency | 39% (≥60%) | FAIL |
| P4 BH-FDR q=0.10 | 27 survive (≥1) AND P2 | FAIL |
| P5 out-of-sample | S̄_oos = +0.0738, p = 0.0005, **opposite sign** | FAIL |
| P6 drop-top-N | (rows below) | FAIL |
| P7 update-asymmetry | R = 1.150 (≤2.00), both-moved fails | FAIL |

## P6 drop-top-N — fraction of lead score remaining after dropping biggest |ΔB| bins
| scenario | S̄ | \|S̄\|/\|full\| | p |
|---|---|---|---|
| full | −0.0028 | 1.00 | — |
| drop top-5 | +0.0446 | 15.91 | 0.0005 |
| drop top-10 | +0.0525 | 18.70 | 0.0005 |
| drop top-1% | +0.0245 | 8.73 | 0.0025 |

Ratios exceed 1 and the sign flips positive because full S̄ ≈ 0 (denominator
~0.0028); removing a handful of bins moves it by more than its whole value.

## P7 — shared-news / update-asymmetry
- both-moved subset: S̄ = −0.0028, p = 0.8341 (need same sign & p<0.05) → FAIL.
- update rates: kalshi 0.585, poly 0.509, R = max/min = **1.150** (FAIL only if
  R>2.00 → this sub-condition passes; P7 fails on the both-moved sub-condition).

## Holdout on its own
S̄_oos = +0.0738, p = 0.0005 → **opposite sign** to in-sample (−0.0028), significant.

## Summary of the numbers
- In-sample lead score is ≈ 0 (−0.0028) and not significant (p = 0.68); 39% sign
  consistency (≈ half). No directional lead in-sample.
- Out-of-sample is positive and significant but **opposite sign** to in-sample —
  no consistent direction across the split.
- Drop-top-N flips the near-zero in-sample score; P6 fails on all three drops.
- Update rates are symmetric (R = 1.150 ≤ 2.00); the P7 both-moved test is ≈ 0.

## Deviation (logged)
§2.3 Kalshi bid/ask spread-sanity not computable — the tape stores last-trade only
(no quotes). The §2.2 activity proxies (≥15 distinct, ≥20 changed bins/venue) were
applied; this is the only deviation from §1–§10.

## Provenance / integrity
- `A2_PREREG.md` SHA-256 `61fc5784…0796788d`, OTS-stamped 2026-06-04 before the
  tape was pulled (proof `A2_PREREG.md.ots`), **verified unchanged post-run.**
- Internal-only; no bets; A2 tape read-only (455,289 rows).
- Reproduce the method: `python analysis.py` (runs on the synthetic sample in
  `sample_data/`; the real numbers above came from the single locked run on
  Oddvane's private cross-venue tape, which is not republished).
