# HMP-GSA Prototype

A small research prototype for comparing three guidance hypotheses against the
same simulated-annealing search loop.

The important design choice is separation of concerns:

- `HMPGSA` owns the SA loop, temperature, sampling, logging and lifecycle.
- `GSAAdapter` is the compatibility boundary with the existing HMP-SA code.
- `UnguidedGSA` / `PriorOnlyGSA` = controls (uniform vs static prior).
- `SuccessfulFeatureGSA` = A: reinforce features involved in improving moves.
- `GoodSolutionFrequencyGSA` = B: reinforce features appearing in good solutions.
- `MutationFeatureGSA` = C: learn operation + feature combinations.

The prototype deliberately does NOT implement the real HMP MDL evaluator. The
existing HMP implementation should be plugged in through `GSAAdapter`.

## Expected adapter contract

Implement:

1. `initial_prior()` -> `{feature: nonnegative_weight}`
2. `sample_moves(state, rng, pool_size)` -> iterable of `Move`
3. `apply_move(state, move)` -> new state
4. `evaluate(state)` -> scalar MDL score (lower is better)
5. `features_of(state)` -> iterable of features
6. `feature_of_move(move)` -> feature
7. `operation_of_move(move)` -> e.g. "add", "remove", "replace"

`sample_moves` is intentionally allowed to return only a small candidate pool.
GSA does NOT need to evaluate every possible neighbor.

## Research discipline

The three variants share exactly the same search machinery. Only the
definition of "what gets remembered" changes. This makes comparisons much
cleaner:

HMP-SA / unguided
    vs
prior-only
    vs
HMP-GSA-A
HMP-GSA-B
HMP-GSA-C

Keep the random seed, iteration budget, initial state and evaluator identical
when comparing variants.

## Important

The equations in the research notes are hypotheses, not validated claims.
This prototype is intended to make those hypotheses testable.
