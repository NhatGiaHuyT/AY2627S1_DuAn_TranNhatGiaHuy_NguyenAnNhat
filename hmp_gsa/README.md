# HMP-GSA Prototype

A research prototype for comparing three guidance hypotheses against the same
simulated-annealing search loop on configurable transaction datasets.

The important design choice is separation of concerns:

- `HMPGSA` owns the SA loop, temperature, sampling, logging and lifecycle.
- `GSAAdapter` is the compatibility boundary with the existing HMP-SA code.
- `UnguidedGSA` / `PriorOnlyGSA` = controls (uniform vs static prior).
- `SuccessfulFeatureGSA` = A: reinforce features involved in improving moves.
- `GoodSolutionFrequencyGSA` = B: reinforce features appearing in good solutions.
- `MutationFeatureGSA` = C: learn operation + feature combinations.

The repository includes a conservative MDL-like dataset adapter in
`hmp_gsa.modules.mdl`. It mirrors the Java runner's residual-plus-code-table
compression idea, but it is not yet a paper-exact replacement for the full HMP
code-table state. The complete existing HMP implementation remains the
reference to plug in through `GSAAdapter` for matched experiments.

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

The synthetic landscape implementation remains in
`hmp_gsa.experiments.landscapes` for regression/reference purposes, but it is
not used by the experiment runner.

## Run real-dataset experiments

Edit `hmp_gsa/configs/baseline.json` and add any number of dataset entries:

```json
{
    "name": "my_dataset",
    "path": "datasets/my_dataset.txt",
    "candidate_sizes": [1, 2],
    "max_pattern_size": 2,
    "max_candidates": 5000
}
```

Then run:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

The runner writes `dataset`-keyed `runs.csv` and `summary.csv` files under
`results/<timestamp>/`. Dataset files are whitespace-separated transactions;
each non-empty line is one transaction.

Progress is enabled by default and reports completed runs, current dataset /
variant / seed, elapsed time, and an estimated remaining time. Set
`"progress": false` in the config for quiet execution.

## Important

The equations in the research notes are hypotheses, not validated claims.
This prototype is intended to make those hypotheses testable.
