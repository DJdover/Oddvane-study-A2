#!/usr/bin/env python3
"""Generate a small SYNTHETIC dataset matching analysis.py's input schema.

This is FAKE data — for each toy "game", venue A walks a home-win random walk and
venue B loosely follows A plus its own noise and a few injected large moves, with
NO built-in lead in either direction. The analysis run on this sample will produce
NO ROBUST LEAD; whatever per-run noise appears is an artifact of this toy generator,
NOT a finding. The prices are NOT real market data from any venue.

Run:  python generate_sample.py   ->  writes sample.csv
"""
import csv
import os
import random

rng = random.Random(20260604)
N_GAMES = 55
BINS = 80


def clamp(x):
    return min(0.97, max(0.03, x))


def main():
    rows = []
    for gi in range(N_GAMES):
        gid = f"g{gi:04d}"
        a = rng.uniform(0.35, 0.65)
        big = set(rng.sample(range(1, BINS), 5))          # a few large discrete moves on B
        for b in range(BINS):
            a = clamp(a + rng.gauss(0, 0.02))             # venue A in-game walk
            bp = clamp(a + rng.gauss(0, 0.012)            # B tracks A CONTEMPORANEOUSLY (no lead either way)
                       + (rng.choice([-0.06, 0.06]) if b in big else 0.0))
            rows.append((gid, "kalshi", b, round(a, 4)))
            rows.append((gid, "polymarket", b, round(bp, 4)))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["game_id", "venue", "bin_min", "price"])
        w.writerows(rows)
    print(f"wrote {out}  ({len(rows)} rows, {N_GAMES} games, synthetic)")


if __name__ == "__main__":
    main()
