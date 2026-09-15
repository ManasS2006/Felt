"""Leduc Hold'em — a small but non-trivial poker research testbed.

Deck of 6 cards: ranks J=0, Q=1, K=2, two suits each. Each player is dealt
one private card; after the first betting round one public card is revealed;
then a second betting round. Antes of 1, bet size 2 on round 1 and 4 on
round 2, at most two bets/raises per round. Showdown: pairing the public card
wins, otherwise the higher private rank wins, equal ranks split.

Infosets are keyed by *rank* (suits are strategically irrelevant in Leduc, so
merging suit-equivalent states is lossless), plus the public card and the full
betting history.
"""
from __future__ import annotations
import copy

NUM_CARDS = 6           # cards 0..5, rank = card // 2
ANTE = 1
BET = (2, 4)            # bet/raise size per round
CAP = 2                 # max bets+raises per round


class LeducState:
    __slots__ = ("priv", "public", "round", "committed", "bet_level",
                 "raises", "to_move", "round_actions", "history", "phase",
                 "fold_winner")

    def __init__(self):
        self.priv = None
        self.public = None
        self.round = 0
        self.committed = [ANTE, ANTE]
        self.bet_level = ANTE
        self.raises = 0
        self.to_move = 0
        self.round_actions = []
        self.history = ()
        self.phase = "deal_priv"      # deal_priv | bet | deal_pub | terminal
        self.fold_winner = None

    def _clone(self):
        s = LeducState.__new__(LeducState)
        s.priv = self.priv
        s.public = self.public
        s.round = self.round
        s.committed = list(self.committed)
        s.bet_level = self.bet_level
        s.raises = self.raises
        s.to_move = self.to_move
        s.round_actions = list(self.round_actions)
        s.history = self.history
        s.phase = self.phase
        s.fold_winner = self.fold_winner
        return s

    # -- node type --------------------------------------------------------
    def is_chance(self):
        return self.phase in ("deal_priv", "deal_pub")

    def is_terminal(self):
        return self.phase == "terminal"

    def current_player(self):
        return self.to_move

    def chance_outcomes(self):
        if self.phase == "deal_priv":
            outs = []
            for c0 in range(NUM_CARDS):
                for c1 in range(NUM_CARDS):
                    if c1 == c0:
                        continue
                    s = self._clone()
                    s.priv = (c0, c1)
                    s.phase = "bet"
                    outs.append((s, 1.0))
            p = 1.0 / len(outs)
            return [(s, p) for s, _ in outs]
        # deal_pub
        used = {self.priv[0], self.priv[1]}
        remaining = [c for c in range(NUM_CARDS) if c not in used]
        p = 1.0 / len(remaining)
        outs = []
        for c in remaining:
            s = self._clone()
            s.public = c
            s.round = 1
            s.to_move = 0
            s.bet_level = s.committed[0]      # both matched -> equal
            s.raises = 0
            s.round_actions = []
            s.history = s.history + ("/",)
            s.phase = "bet"
            outs.append((s, p))
        return outs

    # -- betting ----------------------------------------------------------
    def _facing_bet(self):
        return self.committed[self.to_move] < self.bet_level

    def legal_actions(self):
        if self._facing_bet():
            acts = ["f", "c"]                 # fold, call
            if self.raises < CAP:
                acts.append("r")              # raise
            return acts
        acts = ["c"]                          # check
        if self.raises < CAP:
            acts.append("r")                  # bet
        return acts

    def next_state(self, action):
        s = self._clone()
        me = s.to_move
        opp = 1 - me
        b = BET[s.round]
        s.round_actions.append(action)
        s.history = s.history + (action,)

        if action == "f":
            s.phase = "terminal"
            s.fold_winner = opp
            return s
        if action == "c":
            if s._facing_bet():               # call
                s.committed[me] = s.bet_level
                s._end_round()
            else:                             # check
                if len(s.round_actions) >= 2 and s.round_actions[-2] == "c":
                    s._end_round()
                else:
                    s.to_move = opp
            return s
        if action == "r":
            if s._facing_bet():               # raise: match then add b
                s.committed[me] = s.bet_level + b
            else:                             # bet
                s.committed[me] = s.committed[me] + b
            s.bet_level = s.committed[me]
            s.raises += 1
            s.to_move = opp
            return s
        raise ValueError("illegal action: " + action)

    def _end_round(self):
        if self.round == 0:
            self.phase = "deal_pub"
        else:
            self.phase = "terminal"

    # -- info / payoff ----------------------------------------------------
    def information_set(self):
        own_rank = self.priv[self.to_move] // 2
        pub_rank = self.public // 2 if self.public is not None else -1
        return (own_rank, pub_rank, self.history)

    def returns(self):
        """Utility to player 0."""
        if self.fold_winner is not None:
            w = self.fold_winner
            return self.committed[1] if w == 0 else -self.committed[0]
        # showdown
        r0 = self.priv[0] // 2
        r1 = self.priv[1] // 2
        rp = self.public // 2
        p0_pair = (r0 == rp)
        p1_pair = (r1 == rp)
        if p0_pair and not p1_pair:
            winner = 0
        elif p1_pair and not p0_pair:
            winner = 1
        elif r0 > r1:
            winner = 0
        elif r1 > r0:
            winner = 1
        else:
            return 0.0                        # tie (equal contributions)
        return self.committed[1] if winner == 0 else -self.committed[0]


def new_initial_state():
    return LeducState()


NAME = "leduc"
