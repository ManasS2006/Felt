"""Game registry.

Each game module exposes ``new_initial_state()`` returning a state object with
this duck-typed interface used by the CFR engine:

    is_terminal() -> bool
    is_chance() -> bool
    chance_outcomes() -> list[(state, prob)]      # chance nodes only
    current_player() -> 0 | 1                      # decision nodes only
    legal_actions() -> list[action]
    next_state(action) -> state
    information_set() -> hashable                   # key for the acting player
    returns() -> float                             # utility to player 0 (terminal)
"""
from . import kuhn, leduc

GAMES = {
    "kuhn": kuhn.new_initial_state,
    "leduc": leduc.new_initial_state,
}

__all__ = ["GAMES", "kuhn", "leduc"]
