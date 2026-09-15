"""Kuhn poker — the smallest interesting imperfect-information poker game.

Three cards (J=0, Q=1, K=2), one dealt to each player, one betting round.
Antes of 1, bet size 1. The equilibrium game value to player 0 is exactly
-1/18, which makes it a precise correctness check for the solver.
"""
from __future__ import annotations
import itertools

CARDS = (0, 1, 2)
_TERMINAL = {"pp", "pbp", "pbb", "bp", "bb"}


class KuhnState:
    __slots__ = ("cards", "history")

    def __init__(self, cards=None, history=""):
        self.cards = cards            # None (undealt) or (c0, c1)
        self.history = history        # string over {'p','b'}

    def is_chance(self):
        return self.cards is None

    def chance_outcomes(self):
        deals = list(itertools.permutations(CARDS, 2))
        p = 1.0 / len(deals)
        return [(KuhnState(c, ""), p) for c in deals]

    def is_terminal(self):
        return self.history in _TERMINAL

    def current_player(self):
        return len(self.history) % 2

    def legal_actions(self):
        return ["p", "b"]             # pass/check, bet/call

    def next_state(self, action):
        return KuhnState(self.cards, self.history + action)

    def information_set(self):
        return (self.cards[self.current_player()], self.history)

    def returns(self):
        """Utility to player 0."""
        c0, c1 = self.cards
        high = 1 if c0 > c1 else -1
        h = self.history
        if h == "pp":
            return high * 1
        if h == "bp":
            return 1                  # player 1 folded
        if h == "pbp":
            return -1                 # player 0 folded
        if h in ("bb", "pbb"):
            return high * 2
        raise ValueError("not terminal: " + h)


def new_initial_state():
    return KuhnState()


NAME = "kuhn"
