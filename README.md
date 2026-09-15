# Felt

A from-scratch **counterfactual-regret (CFR+) poker solver**, built over ~2 years
of chipping away at imperfect-information game solving — and the DeepStack line of
research in particular.

Poker is a game of *imperfect information*: you can't evaluate a spot in isolation,
because its value depends on the hidden cards your opponent might hold and how they'd
play each one. That rules out the search techniques behind chess and Go engines and
calls for a different family of algorithms — CFR and its descendants. This repo is
the honest, verifiable core of that story.

> **Two implementations.** This repository is the **reference implementation**: a
> clean, dependency-free Python CFR+ engine that *provably converges* to the Nash
> equilibrium of small poker games. It is the algorithmic heart that the separate
> **C++ / LibTorch build** scales up to heads-up no-limit hold'em with depth-limited
> continual re-solving and learned value networks (the version that solves a
> BTN-vs-BB flop in ~95 s on an M4 MacBook Air).

---

## What's here

- **`felt/cfr.py`** — a generic CFR+ engine (regret matching with zero-floored
  regrets, alternating updates, linear strategy averaging). The average strategy
  converges to equilibrium; the current strategy does not — so we average it.
- **`felt/games/`** — two exact game models: **Kuhn** poker and **Leduc** hold'em.
- **`felt/exploitability.py`** — an *exact* best-response / exploitability
  calculator (the real convergence metric, with correct information-set tying).
- **`bench.py`** — a zero-install cross-machine benchmark.
- **`docs/`** — three explainer visuals (open the HTML files in a browser):
  - `how-it-works.html` — the whole system in plain language
  - `lineage-map.html` — where Felt sits among the CFR → CFR-D → DeepStack papers
  - `project-card.html` — the one-page project summary

## Quick start

Requires only **Python 3.8+** — no dependencies, no build step.

```bash
# verify correctness (Kuhn value = -1/18, Leduc exploitability -> 0)
python -m felt test

# solve a game and print its value + exploitability
python -m felt solve kuhn  --iters 20000
python -m felt solve leduc --iters 2000

# benchmark this machine (run on each box to compare)
python bench.py
```

## Correctness

| Game  | Metric | Result | Reference |
|-------|--------|--------|-----------|
| Kuhn  | game value to P0 (average strategy) | **-0.05565** | exact **-1/18 = -0.05556** |
| Kuhn  | exploitability @ 20k iters | **~0.001** /hand | 0 at equilibrium |
| Leduc | exploitability @ 500 iters | **~0.067** /hand | 0 at equilibrium |

Kuhn's analytic game value pins the solver down; Leduc's falling exploitability
confirms both CFR+ convergence and the exact best-response code.

## Benchmark

Same command (`python bench.py`), one row per machine — fill in as you run it:

| Machine | CPU | Leduc 1000 iters | node-visits/s |
|---------|-----|------------------|---------------|
| Laptop  | Snapdragon ARM64 (Windows) | 36.4 s | ~519k |
| Desktop | _(run it)_ | _–_ | _–_ |
| M4 Air  | _(run it)_ | _–_ | _–_ |

The pure-Python reference is deliberately simple, not fast — its job is to be
*correct and portable*. Speed is the C++/LibTorch engine's job.

## How it works (short version)

1. **Study once (offline).** Solve the last betting round exactly (its leaves are
   real showdowns) to train a value network; then bootstrap up one street at a time,
   using the trained network as the leaf estimate for the street above (à la DeepStack).
2. **Re-solve live.** On every decision, build a small depth-limited lookahead of the
   current spot and run CFR+; past the depth limit, the value network stands in for
   solving to the end. A re-solve gadget keeps each subgame safe (CFR-D).

This repo implements step-2 CFR+ end-to-end on full small games (no depth limit
needed — they're solvable outright). The value-network + depth-limit layer is the
C++ engine's domain.

## Roadmap

- [ ] Bindings to the C++/LibTorch HUNL engine
- [ ] Depth-limited solving with a learned value network at the leaves
- [ ] Value target: **EV × matchup** (DEVN) rather than raw counterfactual values
- [ ] Postflop CFR+ for a single real board (bridge between toy games and HUNL)

## Background

- Zinkevich et al., *Regret Minimization in Games with Incomplete Information* (NIPS 2007)
- Burch, Johanson, Bowling, *Solving Imperfect Information Games Using Decomposition* — CFR-D (2014)
- Moravčík et al., *DeepStack* (Science 2017)
- Wołosiuk et al., *Don't Predict Counterfactual Values, Predict Expected Values Instead* (AAAI 2023)
