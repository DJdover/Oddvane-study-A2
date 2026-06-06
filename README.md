Live In-Game Cross-Venue Lead-Lag in Prediction Markets — Study A2

Result: no robust lead. On 871 live MLB games priced minute-by-minute on Kalshi and
Polymarket, we tested whether one venue's short-horizon price changes lead the
other's, beyond the shared-news co-movement of both watching the same game. The
in-sample lead score is essentially zero (S̄ = −0.0028, p = 0.68, 39% sign
consistency); the out-of-sample half is significant but with the *opposite* sign;
and the score fails every falsification guard. There is no consistent directional
lead. We report it as a non-finding.

Why publish a non-finding

Oddvane studies how prediction markets move. This is one of a series of
pre-registered studies we publish whether or not they find something — on purpose.
The value isn't the answer; it's the method: pre-registration with a timestamped
hash, a sealed out-of-sample holdout, a permutation null that preserves
autocorrelation, a drop-top-N falsification, and a study-specific guard against the
exact way a lead can be faked — all committed to before the data was examined.

This is the continuous-market companion to an earlier study (Study A), which found
no robust lead on slow championship futures and was thinly powered (three qualifying
outcomes). A2 is the better-powered, live-in-game version we said we'd run: 871
games, minute resolution, its own pre-registration.

What was pre-registered

Before any season tape was pulled, we locked the full method (A2_PREREG.md) and
timestamped its SHA-256 (A2_PREREG.sha256, with the OpenTimestamps proof
A2_PREREG.md.ots). Each guard defeats a specific failure mode:

    •    an equal-weight pooled lead score, so one game can't carry the result;
    •    a sealed chronological 70/30 holdout, scored once at the end;
    •    an autocorrelation-preserving circular-shift permutation null;
    •    a drop-top-N falsification (a lead living in a few big plays is an artifact);
    •    a Benjamini–Hochberg FDR correction across games;
    •    **P7**, a study-specific guard with two numeric sub-conditions: the lead must
         survive on the *both-moved* subset (bins where both venues moved ≥0.5¢), AND
         the two venues' update rates must be within 2× of each other — so a lead that
         is really just "one venue ticks more often" is rejected as a mechanism
         artifact, not information.

What happened

P1 (power) passed — 609 in-sample / 262 holdout games. Everything testing for an
actual lead failed: the in-sample score is ≈0 and non-significant (P2, P3, P4); the
holdout is significant but flips sign versus in-sample, so there is no consistent
direction (P5); dropping the largest moves flips the near-zero score around (P6);
and the P7 both-moved test is ≈0 (update rates were symmetric, R = 1.15). Full gate
table and numbers in A2_RESULTS.md.

A note on honesty: a last-trade lead, even had one survived, reflects which venue's
traders *trade* first — related to, but not the same as, which venue is *informed*
first. A2's claim is deliberately narrow, and here it is a clean null.

Reproduce it

`analysis.py` is the full analysis — the per-game lead score over lags 1–3, the
circular-shift permutation null, the sealed holdout, the drop-top-N falsification,
the BH-FDR correction, and the P1–P7 decision rule including P7 — the same logic that
produced the result, with its data input repointed to a documented CSV format.
`sample_data/` provides a small synthetic dataset (built with no lead either way) so
you can run it end-to-end without our data. Not included, by design: the cross-venue
collector and the entity-resolution layer that aligns each venue's market for the
same game — those are Oddvane's. No real market data is republished here; only the
method, the aggregate result, and a synthetic sample.

Provenance

A2_PREREG.md is published **byte-identical** to the pre-registration that was
OpenTimestamps-stamped on 2026-06-04, before any season tape was pulled — no
redaction was needed, as the file contains no private content. A2_PREREG.sha256
therefore equals the timestamped hash (61fc5784…), and the included
A2_PREREG.md.ots proof applies directly to this published file; it was verified
unchanged after the single run. A commit date does not establish pre-registration
ordering; the OpenTimestamps proof does.

License: MIT (see LICENSE).
