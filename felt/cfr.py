"""CFR+ engine.

A generic counterfactual-regret-minimization-plus solver that operates over
any game exposing the small state interface in ``felt.games`` (is_terminal /
is_chance / chance_outcomes / current_player / legal_actions / next_state /
information_set / returns, where ``returns`` is the utility to player 0).

CFR+ = regret matching with regrets floored at zero, alternating player
updates, and linear (iteration-weighted) strategy averaging. In self-play the
*average* strategy converges to a Nash equilibrium; the per-iteration strategy
does not — which is why we accumulate ``strategy_sum``.
"""
from __future__ import annotations


class CFRSolver:
    def __init__(self, new_initial_state):
        self._root = new_initial_state
        self.regret_sum = {}     # infoset -> list[float]
        self.strategy_sum = {}   # infoset -> list[float]
        self.actions = {}        # infoset -> list[action]
        self.iterations = 0
        self.nodes_visited = 0

    # -- node bookkeeping -------------------------------------------------
    def _ensure(self, infoset, legal):
        if infoset not in self.regret_sum:
            n = len(legal)
            self.regret_sum[infoset] = [0.0] * n
            self.strategy_sum[infoset] = [0.0] * n
            self.actions[infoset] = list(legal)

    def _current_strategy(self, infoset):
        r = self.regret_sum[infoset]
        pos = [x if x > 0.0 else 0.0 for x in r]
        s = sum(pos)
        if s > 0.0:
            return [x / s for x in pos]
        n = len(r)
        return [1.0 / n] * n

    def average_strategy(self, infoset):
        if infoset not in self.strategy_sum:
            return None
        s = self.strategy_sum[infoset]
        tot = sum(s)
        if tot > 0.0:
            return [x / tot for x in s]
        n = len(s)
        return [1.0 / n] * n

    # -- training ---------------------------------------------------------
    def train(self, iterations):
        for _ in range(iterations):
            self.iterations += 1
            for player in (0, 1):
                self._cfr(self._root(), player, 1.0, 1.0, 1.0, self.iterations)

    def _cfr(self, state, player, reach0, reach1, reach_ch, t):
        self.nodes_visited += 1
        if state.is_terminal():
            return state.returns()
        if state.is_chance():
            v = 0.0
            for child, p in state.chance_outcomes():
                v += p * self._cfr(child, player, reach0, reach1, reach_ch * p, t)
            return v

        cur = state.current_player()
        infoset = state.information_set()
        legal = state.legal_actions()
        self._ensure(infoset, legal)
        strat = self._current_strategy(infoset)
        acts = self.actions[infoset]

        util = [0.0] * len(acts)
        node_util = 0.0
        for i, a in enumerate(acts):
            child = state.next_state(a)
            if cur == 0:
                u = self._cfr(child, player, reach0 * strat[i], reach1, reach_ch, t)
            else:
                u = self._cfr(child, player, reach0, reach1 * strat[i], reach_ch, t)
            util[i] = u
            node_util += strat[i] * u

        if cur == player:
            # counterfactual reach = everyone except the acting player
            if player == 0:
                cf, own, sign = reach1 * reach_ch, reach0, 1.0
            else:
                cf, own, sign = reach0 * reach_ch, reach1, -1.0  # utils are P0's
            r = self.regret_sum[infoset]
            s = self.strategy_sum[infoset]
            for i in range(len(acts)):
                regret = cf * sign * (util[i] - node_util)
                r[i] = max(r[i] + regret, 0.0)          # CFR+ flooring
                s[i] += own * strat[i] * t              # linear averaging
        return node_util

    # -- evaluation -------------------------------------------------------
    def game_value(self):
        """Expected value to player 0 when both play the average strategy."""
        return self._value_under_average(self._root())

    def _value_under_average(self, state):
        if state.is_terminal():
            return state.returns()
        if state.is_chance():
            return sum(p * self._value_under_average(c) for c, p in state.chance_outcomes())
        infoset = state.information_set()
        avg = self.average_strategy(infoset)
        acts = self.actions.get(infoset) or state.legal_actions()
        if avg is None:
            n = len(acts)
            avg = [1.0 / n] * n
        v = 0.0
        for i, a in enumerate(acts):
            v += avg[i] * self._value_under_average(state.next_state(a))
        return v
