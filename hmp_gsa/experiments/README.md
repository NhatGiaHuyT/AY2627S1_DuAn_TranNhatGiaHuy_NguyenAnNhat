# HMP-GSA Experiment Harness

A reproducible harness for testing the three proposed guidance hypotheses
against unguided and prior-only controls, before connecting them to the real
HMP/MDL implementation.

The search engine is `hmp_gsa.core.HMPGSA`. Neighborhood sampling is
`hmp_gsa.subset.SubsetSelectionAdapter`, shared with `hmp_gsa.demo`.
Hyperparameters are `hmp_gsa.settings` / `configs/baseline.json`.

- unguided = uniform sampling, no memory
- prior_only = static prior, no online updates
- A = Successful Feature
- B = Good-Solution Frequency
- C = Mutation + Feature

## Run

Python 3.10+:

    python -m experiments.run

or:

    python -m experiments.run --config configs/baseline.json

Results are written to results/<timestamp>/:
- runs.csv       full per-iteration traces
- summary.csv    aggregate comparison
- config.json    exact configuration used

These synthetic landscapes are NOT MDL. They isolate properties of the
memory hypotheses. Replace `SyntheticLandscape` with an HMP adapter to
test the real evaluator without changing A/B/C or the controls.
