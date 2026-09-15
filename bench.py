#!/usr/bin/env python3
"""Cross-machine benchmark for Felt's CFR+ core.

Run the same command on each machine and compare — this is how we measure the
laptop-vs-desktop speed difference without any build step:

    python bench.py

Pure Python and stdlib-only, so it runs anywhere Python 3.8+ is installed.
"""
import platform
import time

from felt.cfr import CFRSolver
from felt.games import GAMES


def run(game, iters):
    solver = CFRSolver(GAMES[game])
    t0 = time.perf_counter()
    solver.train(iters)
    dt = time.perf_counter() - t0
    return dt, solver.nodes_visited


def main():
    print("=" * 56)
    print(" Felt CFR+ benchmark")
    print("=" * 56)
    print(f" machine : {platform.machine()}  {platform.processor() or ''}".rstrip())
    print(f" system  : {platform.system()} {platform.release()}")
    print(f" python  : {platform.python_version()}")
    print("-" * 56)
    for game, iters in (("kuhn", 20000), ("leduc", 1000)):
        dt, nodes = run(game, iters)
        print(f" {game:<6} {iters:>6} iters   {dt:8.3f} s   "
              f"{iters / dt:>9,.0f} it/s   {nodes / dt:>12,.0f} nodes/s")
    print("=" * 56)


if __name__ == "__main__":
    main()
