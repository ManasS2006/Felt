"""Command-line interface:  python -m felt <command>

    solve <game> [--iters N]   solve a game, print value + exploitability
    test                       run correctness self-tests (Kuhn, Leduc)
    bench [--game G] [--iters N]   time the solver for machine comparison
"""
from __future__ import annotations
import argparse
import platform
import time

from .cfr import CFRSolver
from .games import GAMES
from .exploitability import exploitability


def _solve(game, iters):
    root = GAMES[game]
    solver = CFRSolver(root)
    t0 = time.perf_counter()
    solver.train(iters)
    dt = time.perf_counter() - t0
    val = solver.game_value()
    expl, v0, v1 = exploitability(solver, root)
    print(f"game        : {game}")
    print(f"iterations  : {iters}")
    print(f"train time  : {dt:.3f} s  ({iters / dt:,.0f} iters/s)")
    print(f"infosets    : {len(solver.regret_sum):,}")
    print(f"game value  : {val:+.6f}  (to player 0, both playing average)")
    print(f"exploitab.  : {expl:.6f}  per hand   [BR0 {v0:+.4f}, BR1 {v1:+.4f}]")
    return solver


def _test():
    ok = True

    # Kuhn: game value must be exactly -1/18.
    root = GAMES["kuhn"]
    s = CFRSolver(root)
    s.train(20000)
    val = s.game_value()
    expl, _, _ = exploitability(s, root)
    target = -1.0 / 18.0
    kuhn_val_ok = abs(val - target) < 1e-3
    kuhn_expl_ok = expl < 5e-3
    print(f"[Kuhn ] value {val:+.6f} (target {target:+.6f})  "
          f"{'PASS' if kuhn_val_ok else 'FAIL'}")
    print(f"[Kuhn ] exploitability {expl:.6f}  "
          f"{'PASS' if kuhn_expl_ok else 'FAIL'}")
    ok = ok and kuhn_val_ok and kuhn_expl_ok

    # Leduc: exploitability must fall well below the ante with enough CFR+.
    root = GAMES["leduc"]
    s = CFRSolver(root)
    s.train(500)
    expl, _, _ = exploitability(s, root)
    leduc_ok = expl < 0.1
    print(f"[Leduc] exploitability {expl:.6f} after 500 iters  "
          f"{'PASS' if leduc_ok else 'FAIL'}")
    ok = ok and leduc_ok

    print("=" * 40)
    print("ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
    return 0 if ok else 1


def _bench(game, iters):
    root = GAMES[game]
    solver = CFRSolver(root)
    t0 = time.perf_counter()
    solver.train(iters)
    dt = time.perf_counter() - t0
    print(f"machine     : {platform.machine()} / {platform.processor() or 'cpu'}")
    print(f"python      : {platform.python_version()} ({platform.system()})")
    print(f"game        : {game}")
    print(f"iterations  : {iters}")
    print(f"wall time   : {dt:.3f} s")
    print(f"throughput  : {iters / dt:,.0f} iterations/s")
    print(f"node visits : {solver.nodes_visited:,}  "
          f"({solver.nodes_visited / dt:,.0f} nodes/s)")


def main(argv=None):
    p = argparse.ArgumentParser(prog="felt", description="Felt poker CFR+ solver")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("solve", help="solve a game")
    ps.add_argument("game", choices=list(GAMES))
    ps.add_argument("--iters", type=int, default=2000)

    sub.add_parser("test", help="run correctness self-tests")

    pb = sub.add_parser("bench", help="benchmark for machine comparison")
    pb.add_argument("--game", choices=list(GAMES), default="leduc")
    pb.add_argument("--iters", type=int, default=1000)

    args = p.parse_args(argv)
    if args.cmd == "solve":
        _solve(args.game, args.iters)
    elif args.cmd == "test":
        return _test()
    elif args.cmd == "bench":
        _bench(args.game, args.iters)
    return 0
