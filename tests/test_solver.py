"""Correctness tests. Run with `pytest` or `python tests/test_solver.py`.

The Kuhn game value is analytically -1/18, which pins down the solver; the
Leduc exploitability check confirms the exact best-response calculation and
that CFR+ is converging toward equilibrium.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from felt.cfr import CFRSolver
from felt.games import GAMES
from felt.exploitability import exploitability


def test_kuhn_game_value():
    s = CFRSolver(GAMES["kuhn"])
    s.train(20000)
    assert abs(s.game_value() - (-1.0 / 18.0)) < 1e-3


def test_kuhn_exploitability():
    s = CFRSolver(GAMES["kuhn"])
    s.train(20000)
    expl, _, _ = exploitability(s, GAMES["kuhn"])
    assert expl < 5e-3


def test_leduc_converges():
    s = CFRSolver(GAMES["leduc"])
    s.train(500)
    expl, _, _ = exploitability(s, GAMES["leduc"])
    assert expl < 0.1


if __name__ == "__main__":
    test_kuhn_game_value()
    test_kuhn_exploitability()
    test_leduc_converges()
    print("all tests passed")
