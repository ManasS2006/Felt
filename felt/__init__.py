"""Felt — a from-scratch counterfactual-regret poker solver.

This package is the *reference* implementation: a clean, dependency-free
CFR+ engine that provably converges to the Nash equilibrium of small
poker games (Kuhn, Leduc). It is the algorithmic core that the C++/LibTorch
build scales up to heads-up no-limit with learned value networks.

Public API:
    from felt import CFRSolver, GAMES
"""
from .cfr import CFRSolver
from .games import GAMES

__all__ = ["CFRSolver", "GAMES"]
__version__ = "0.1.0"
